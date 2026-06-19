import requests
import pandas as pd
import gspread
import time
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- AUTH ---
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "oi-analysis-496406-0cd8eaad9bc1.json",
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)
spreadsheet = client.open("OI_ANALYSIS")

# Worksheets
sheet_main = spreadsheet.worksheet("OI_DATA")
sheet_top7 = spreadsheet.worksheet("DAILY_TOP5")
sheet_top = spreadsheet.worksheet("TOP")
sheet_incr = spreadsheet.worksheet("OI_INCR")

URL = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://www.nseindia.com/"}
session = requests.Session()

previous_oi = {}
previous_full_oi = {}

def refresh_cookie():
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=15)
    except: pass

def fetch_oi_data():
    global previous_oi, previous_full_oi
    refresh_cookie()
    response = session.get(URL, headers=headers, timeout=20)
    data = response.json().get("data", [])
    if not data: return

    rows = []
    for item in data:
        symbol = item.get("symbol", "")
        oi_t = float(str(item.get("latestOI", 0)).replace(",", ""))
        oi_p = float(str(item.get("prevOI", 0)).replace(",", ""))
        change = oi_t - oi_p
        
        # Google Finance Formula
        gsym = f"INDEXNSE:NIFTY_50" if symbol == "NIFTY" else (f"INDEXNSE:NIFTY_BANK" if symbol == "BANKNIFTY" else f"NSE:{symbol}")
        price_formula = f'=IFERROR(GOOGLEFINANCE("{gsym}","price"),"")'
        
        rows.append([symbol, int(oi_t), int(oi_p), int(change), round((change/oi_p)*100 if oi_p else 0, 2), 
                     int(float(str(item.get("volume", 0)).replace(",", ""))), price_formula])

    df = pd.DataFrame(rows, columns=["Symbol", "OI Today", "OI Prev", "OI Change", "% Change", "Volume", "Price"])
    df = df.sort_values(by="OI Change", ascending=False)

    # Update Main Sheet
    sheet_main.clear()
    sheet_main.update([df.columns.values.tolist()] + df.values.tolist(), value_input_option="USER_ENTERED")

    # Update Top7 & Top (Logic remains similar)
    # ... (Keep your existing Top logic here) ...
    
    print("SUCCESS : DATA UPDATED")

# --- MAIN LOOP ---
while True:
    now = datetime.now()
    if now.weekday() <= 4 and "09:15" <= now.strftime("%H:%M") <= "15:35":
        try:
            fetch_oi_data()
        except Exception as e:
            print("LOOP ERROR:", e)
        time.sleep(300) # 5 minutes
    else:
        time.sleep(60)