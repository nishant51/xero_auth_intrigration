import json
import hmac
import hashlib
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
NAME = os.getenv("B12_NAME", "Nishant Timsina")
EMAIL = os.getenv("B12_EMAIL", "timsinanisant51@gmail.com")
RESUME_LINK = os.getenv("B12_RESUME_LINK", "https://linkedin.com/in/nishant-timsina")
REPO_LINK = os.getenv("B12_REPO_LINK", "https://github.com/nishant51/xero_auth_intrigration")
ACTION_RUN_LINK = os.getenv("B12_ACTION_RUN_LINK", "https://github.com/nishant51/xero_auth_intrigration/actions/runs/your_run_id")
SIGNING_SECRET = os.getenv("B12_SIGNING_SECRET", "hello-there-from-b12").encode()
SUBMISSION_URL = "https://b12.io/apply/submission"
timestamp = datetime.utcnow().isoformat() + "Z"

payload = {
    "action_run_link": ACTION_RUN_LINK,
    "email": EMAIL,
    "name": NAME,
    "repository_link": REPO_LINK,
    "resume_link": RESUME_LINK,
    "timestamp": timestamp,
}

payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
signature = hmac.new(SIGNING_SECRET, payload_json.encode('utf-8'), hashlib.sha256).hexdigest()
headers = {
    "X-Signature-256": f"sha256={signature}",
    "Content-Type": "application/json"
}

response = requests.post(SUBMISSION_URL, headers=headers, data=payload_json)
if response.status_code == 200:
    try:
        resp_json = response.json()
        if resp_json.get("success"):
            print("Submission successful!")
            print("Receipt:", resp_json.get("receipt"))
        else:
            print("Submission failed:", resp_json)
    except Exception as e:
        print("Error parsing response:", e)
else:
    print("HTTP Error:", response.status_code, response.text)
