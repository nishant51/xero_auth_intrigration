from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json
import urllib.parse
import requests
import base64
import time
from django.utils import timezone
from datetime import datetime  # Added this import
import re
from account.models import XeroAccount
from django.shortcuts import render


def parse_xero_datetime(xero_timestamp):
    if not xero_timestamp or not isinstance(xero_timestamp, str):
        return None
    match = re.match(r"/Date\((\d+)([+-]\d{4})\)/", xero_timestamp)
    if not match:
        return None
    milliseconds, offset = match.groups()
    # Convert milliseconds to seconds
    timestamp_seconds = int(milliseconds) / 1000
    # Convert to datetime
    dt = datetime.fromtimestamp(timestamp_seconds)
    return dt

# Helper function to initialize Xero headers with token
def get_xero_headers(request):
    print("Entering get_xero_headers")
    token = request.session.get('xero_token')
    if not token:
        print("No token found in session")
        return None
    print(f"Found token in session: {token}")
    headers = {
        "Authorization": f"Bearer {token.get('access_token')}",
        "Accept": "application/json"
    }
    print("Xero headers initialized successfully")
    return headers

# Step 1: Redirect user to Xero login
def xero_login(request):
    print("Entering xero_login")
    auth_base_url = "https://login.xero.com/identity/connect/authorize"
    scopes = ["offline_access", "accounting.settings"]
    params = {
        "response_type": "code",
        "client_id": settings.XERO_CLIENT_ID,
        "redirect_uri": settings.XERO_REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": "xero_auth_state"
    }
    auth_url = f"{auth_base_url}?{urllib.parse.urlencode(params)}"
    print(f"Generated auth URL: {auth_url}")
    request.session['oauth_state'] = "xero_auth_state"
    print("Stored oauth_state in session")
    return redirect(auth_url)

# Step 2: Handle callback and exchange code for token
def xero_callback(request):
    print("Entering xero_callback")
    code = request.GET.get('code')
    state = request.GET.get('state')
    stored_state = request.session.get('oauth_state')
    print(f"Received code: {code}, state: {state}, stored_state: {stored_state}")
    
    if not code or state != stored_state:
        print("Validation failed: Invalid state or code")
        return JsonResponse({"error": "Invalid state or code"}, status=400)
    
    print("State validation passed")
    token_url = "https://identity.xero.com/connect/token"
    auth_string = f"{settings.XERO_CLIENT_ID}:{settings.XERO_CLIENT_SECRET}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.XERO_REDIRECT_URI
    }
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("Sending token exchange request")
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        token = response.json()
        token['expires_at'] = int(time.time()) + token['expires_in']
        print(f"Received token: {token}")
        request.session['xero_token'] = token
        print("Stored token in session")
        return redirect('home')
    except requests.RequestException as e:
        print(f"Token exchange failed: {str(e)}")
        error_details = e.response.text if e.response else str(e)
        return JsonResponse({"error": "Token exchange failed", "details": error_details}, status=e.response.status_code if e.response else 500)

def xero_data(request):
    print("Entering xero_data")
    headers = get_xero_headers(request)
    if not headers:
        print("No headers, redirecting to login")
        return redirect('xero_login')
    
    print("Headers obtained")
    # Refresh token if expired
    token = request.session['xero_token']
    if token['expires_at'] < int(time.time()):
        print("Token expired, refreshing")
        token_url = "https://identity.xero.com/connect/token"
        auth_string = f"{settings.XERO_CLIENT_ID}:{settings.XERO_CLIENT_SECRET}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": token['refresh_token']
        }
        headers_refresh = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            response = requests.post(token_url, data=payload, headers=headers_refresh)
            response.raise_for_status()
            new_token = response.json()
            new_token['expires_at'] = int(time.time()) + new_token['expires_in']
            request.session['xero_token'] = new_token
            headers["Authorization"] = f"Bearer {new_token['access_token']}"
            print(f"Token refreshed: {new_token}")
        except requests.RequestException as e:
            print(f"Token refresh failed: {str(e)}")
            error_details = e.response.text if e.response else str(e)
            status = e.response.status_code if e.response else 503
            if status == 400 and "invalid_grant" in error_details:
                request.session.flush()
                return redirect('xero_login')
            return JsonResponse({"error": "Token refresh failed", "details": error_details}, status=status)
    
    # Get all tenant connections
    print("Fetching connections")
    connections_url = "https://api.xero.com/connections"
    try:
        response = requests.get(connections_url, headers=headers)
        response.raise_for_status()
        connections = response.json()
        if not connections:
            print("No connections found")
            return JsonResponse({"error": "No Xero organizations connected"}, status=404)
    except requests.RequestException as e:
        print(f"Error fetching connections: {str(e)}")
        error_details = e.response.text if e.response else str(e)
        return JsonResponse({"error": "Failed to fetch connections", "details": error_details}, 
                          status=e.response.status_code if e.response else 500)
    
    # Fetch accounts for all tenants and save to model
    print("Fetching accounts for all tenants")
    all_accounts_data = {}
    
    for connection in connections:
        tenant_id = connection['tenantId']
        tenant_name = connection.get('tenantName', f"Tenant_{tenant_id}")
        print(f"Fetching accounts for tenant: {tenant_id} ({tenant_name})")
        
        accounts_url = "https://api.xero.com/api.xro/2.0/Accounts"
        headers["xero-tenant-id"] = tenant_id
        try:
            response = requests.get(accounts_url, headers=headers)
            response.raise_for_status()
            accounts_data = response.json()
            accounts_list = accounts_data.get("Accounts", [])
            print(f"Retrieved {len(accounts_list)} accounts for tenant {tenant_id}")
            
            # Save each account to the model using only defined fields
            for account in accounts_list:
                XeroAccount.objects.update_or_create(
                    account_id=account.get('AccountID'),
                    defaults={
                        'code': account.get('Code'),
                        'name': account.get('Name'),
                        'account_type': account.get('Type'),
                        'bank_account_number': account.get('BankAccountNumber'),
                        'status': account.get('Status'),
                        'description': account.get('Description'),
                        'bank_account_type': account.get('BankAccountType'),
                        'currency_code': account.get('CurrencyCode'),
                        'tax_type': account.get('TaxType'),
                        'enable_payments_to_account': account.get('EnablePaymentsToAccount', False),
                        'show_in_expense_claims': account.get('ShowInExpenseClaims', False),
                        'account_class': account.get('Class'),
                        'system_account': account.get('SystemAccount'),
                        'reporting_code': account.get('ReportingCode'),
                        'reporting_code_name': account.get('ReportingCodeName'),
                        'has_attachments': account.get('HasAttachments', False),
                        'updated_date_utc': parse_xero_datetime(account.get('UpdatedDateUTC')),
                        'add_to_watchlist': account.get('AddToWatchlist', False),
                        'fetch_status': 'SUCCESS',
                        'error_message': None,
                        'fetched_at': timezone.now()
                    }
                )
            
            all_accounts_data[tenant_name] = {
                "tenant_id": tenant_id,
                "account_count": len(accounts_list),
                "accounts": accounts_list
            }
        except requests.RequestException as e:
            print(f"Error fetching accounts for tenant {tenant_id}: {str(e)}")
            error_details = e.response.text if e.response else str(e)
            status = e.response.status_code if e.response else 500
            error_msg = f"API error: {error_details}"
            
            # Save error to model
            XeroAccount.objects.update_or_create(
                account_id=f"error_{tenant_id}",
                defaults={
                    'name': f"Error for {tenant_name}",
                    'fetch_status': 'ERROR',
                    'error_message': error_msg,
                    'fetched_at': timezone.now()
                }
            )
            
            all_accounts_data[tenant_name] = {
                "tenant_id": tenant_id,
                "error": error_msg,
                "accounts": []
            }
    
    # Structure the response
    response_data = {
        "tenant_count": len(connections),
        "tenants": all_accounts_data
    }
    print(f"Returning data for {len(connections)} tenants as JSON")
    return JsonResponse(response_data)


def home(request):
    return render(request, 'home.html')

# Add this view for account page
def account(request):
    return render(request, 'account.html')