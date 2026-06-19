import pandas as pd
import yfinance as yf
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# --- SETTINGS ---
LOOKBACK = 1000
MAX_WORKERS = 10  # Workers badha diye hain speed ke liye
JSON_FILE = "oi-analysis-496406-0cd8eaad9bc1.json"

# --- AUTH ---
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)
spreadsheet = client.open("OI_ANALYSIS")

try:
    MULTIBAGGER = spreadsheet.worksheet("MULTIBAGGER")
except:
    MULTIBAGGER = spreadsheet.add_worksheet(title="MULTIBAGGER", rows=5000, cols=20)

def get_nse_symbols():
    # URL Error handling
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df = pd.read_csv(url)
        return df["SYMBOL"].dropna().astype(str).unique().tolist()
    except:
        return []

def scan_stock(symbol):
    try:
        # Ticker modification for better fetching
        ticker = f"{symbol}.NS"
        data = yf.download(ticker, period="5y", interval="1d", progress=False, threads=False)
        
        if data.empty or len(data) < LOOKBACK + 20:
            return None

        highs = data["High"].squeeze()
        today_high = float(highs.iloc[-1])
        # Previous 1000 high excluding today
        previous_1000_high = float(highs.iloc[-LOOKBACK-1:-1].max())

        if today_high < previous_1000_high:
            return None

        # Breakout Math
        breakout_pct = round(((today_high - previous_1000_high) / previous_1000_high) * 100, 2)

        # Optimization: Sirf breakout wale stocks ka hi count nikalein
        # (Ye loop bahut heavy tha, ab sirf valid stocks pe chalega)
        breakout_dates = highs[highs >= highs.rolling(window=LOOKBACK).max().shift(1)].index
        temp_df = pd.DataFrame({"DATE": breakout_dates})
        temp_df["MONTH"] = temp_df["DATE"].dt.strftime("%Y-%m")
        counts = temp_df["MONTH"].value_counts().to_dict()

        row = [datetime.now().strftime("%d-%b-%Y"), symbol, round(today_high, 2), 
               round(previous_1000_high, 2), breakout_pct]

        curr = datetime.now()
        for i in range(6):
            m_key = (curr - pd.DateOffset(months=i)).strftime("%Y-%m")
            row.append(counts.get(m_key, 0))

        return row
    except Exception:
        return None

def update_sheet(results):
    try:
        MULTIBAGGER.clear()
        headers = ["DATE", "SYMBOL", "TODAY_HIGH", "PREV_1000_HIGH", "BREAKOUT_%", 
                   "CURRENT_MONTH", "M1", "M2", "M3", "M4", "M5"]
        
        # Batch update is faster
        if results:
            data = [headers] + results
            MULTIBAGGER.update(f"A1:K{len(data)}", data)
        else:
            MULTIBAGGER.update("A1", [headers])
    except Exception as e:
        print(f"Sheet Error: {e}")

def main():
    print("SCANNING STARTED...")
    symbols = get_nse_symbols()
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scan_stock, s): s for s in symbols}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                print(f"Found: {res[1]}")

    results.sort(key=lambda x: x[4], reverse=True)
    update_sheet(results)
    print(f"TOTAL FOUND: {len(results)}")

if __name__ == "__main__":
    main()