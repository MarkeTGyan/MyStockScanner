# Updated File: multi.py

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================================================
# UNIVERSAL AUTH FOR GITHUB SECRETS
# =========================================================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# GitHub Actions में 'GOOGLE_SHEETS_JSON' नाम का secret use करें
if 'GOOGLE_SHEETS_JSON' in os.environ:
    creds_dict = json.loads(os.environ['GOOGLE_SHEETS_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Local development ke liye (if json file exists)
    json_file = "oi-analysis-496406-0cd8eaad9bc1.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

client = gspread.authorize(creds)
spreadsheet = client.open("OI_ANALYSIS")

# ... Rest of the original code follows ...