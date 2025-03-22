from django.db import models
from django.utils import timezone

class XeroAccount(models.Model):
    account_id = models.CharField(max_length=36, unique=True, help_text="Xero Account UUID")
    code = models.CharField(max_length=10, blank=True, null=True, help_text="Customer defined alpha numeric account code e.g., 200 or SALES")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the account")
    account_type = models.CharField(max_length=50, blank=True, null=True, help_text="Account type (e.g., BANK, REVENUE)")
    bank_account_number = models.CharField(max_length=50, blank=True, null=True, help_text="Bank account number (for BANK accounts only)")
    status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')],
        blank=True,
        null=True,
        help_text="Account status in Xero (ACTIVE or ARCHIVED)"
    )
    description = models.TextField(blank=True, null=True, help_text="Description of the account (not for bank accounts)")
    bank_account_type = models.CharField(max_length=50, blank=True, null=True, help_text="Bank account type (for BANK accounts only)")
    currency_code = models.CharField(max_length=3, blank=True, null=True, help_text="Currency code (for BANK accounts only)")
    tax_type = models.CharField(max_length=50, blank=True, null=True, help_text="Tax type associated with the account")
    enable_payments_to_account = models.BooleanField(default=False, help_text="Whether payments can be applied to this account")
    show_in_expense_claims = models.BooleanField(default=False, help_text="Whether account is available for expense claims")
    account_class = models.CharField(max_length=50, blank=True, null=True, help_text="Account class (ASSET, LIABILITY, etc.)")
    system_account = models.CharField(max_length=50, blank=True, null=True, help_text="System account type if applicable (e.g., DEBTORS)")
    reporting_code = models.CharField(max_length=50, blank=True, null=True, help_text="Reporting code if set")
    reporting_code_name = models.CharField(max_length=255, blank=True, null=True, help_text="Reporting code name if set")
    has_attachments = models.BooleanField(default=False, help_text="Indicates if the account has attachments")
    updated_date_utc = models.DateTimeField(blank=True, null=True, help_text="Last modified date in UTC format")
    add_to_watchlist = models.BooleanField(default=False, help_text="Whether account is shown in Xero dashboard watchlist")

    # Metadata for tracking
    fetch_status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('ERROR', 'Error')],
        default='SUCCESS',
        help_text="Status of the fetch operation"
    )
    error_message = models.TextField(blank=True, null=True, help_text="Error details if fetch failed")
    fetched_at = models.DateTimeField(default=timezone.now, help_text="When the data was fetched")

    class Meta:
        verbose_name = "Xero Chart of Account"
        verbose_name_plural = "Xero Chart of Accounts"

    def __str__(self):
        return f"{self.name} ({self.account_id})"