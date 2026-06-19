# =========================================================
# GAIN_V2.py (FIXED VERSION)
# =========================================================

import time
import hashlib
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

JSON_FILE = "oi-analysis-496406-0cd8eaad9bc1.json"
WORKBOOK = "OI_ANALYSIS"
SOURCE_SHEET = "DAILY_TOP5"
GAIN_SHEET = "GAIN"
HISTORY_SHEET = "GAIN_HISTORY"
SLEEP_SECONDS = 60

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- HELPERS ---
def extract_price(v):
    try:
        s = str(v).strip()
        if "|" in s: s = s.split("|")[0].strip()
        return float(s)
    except: return None

def oi_direction(v):
    s = str(v)
    if "▲" in s: return 1
    if "▼" in s: return -1
    return 0

def price_direction(v):
    s = str(v)
    if "🟢" in s: return 1
    if "🔴" in s: return -1
    return 0

def signal_name(oi, price):
    if oi == 1 and price == 1: return "LONG BUILDUP (BUY)"
    if oi == 1 and price == -1: return "SHORT BUILDUP (SELL)"
    if oi == -1 and price == -1: return "LONG UNWINDING (SELL)"
    if oi == -1 and price == 1: return "SHORT COVERING (BUY)"
    return None

# --- AUTH & SETUP ---
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
client = gspread.authorize(creds)
book = client.open(WORKBOOK)
src = book.worksheet(SOURCE_SHEET)

try: gain = book.worksheet(GAIN_SHEET)
except: gain = book.add_worksheet(title=GAIN_SHEET, rows=5000, cols=20)

try: hist = book.worksheet(HISTORY_SHEET)
except: 
    hist = book.add_worksheet(title=HISTORY_SHEET, rows=5000, cols=10)
    hist.update(values=[["SYMBOL", "FIRST_SEEN"]], range_name="A1:B1")

known_symbols = set()
try:
    hist_data = hist.get_all_records()
    for r in hist_data: known_symbols.add(str(r.get("SYMBOL", "")).strip())
except: pass

last_hash = ""
print("GAIN ENGINE STARTED...")

# --- MAIN LOOP ---
while True:
    try:
        records = src.get_all_records()
        if not records:
            time.sleep(SLEEP_SECONDS)
            continue

        df = pd.DataFrame(records)
        df["TIME"] = pd.to_datetime(df["TIME"], errors="coerce")
        df["PRICE_VALUE"] = df["CURRENT PRICE"].apply(extract_price)
        df["OI_DIR"] = df["% Change in OI"].apply(oi_direction)
        df["PRICE_DIR"] = df["CURRENT PRICE"].apply(price_direction)
        df = df[df["Symbol"].astype(str) != "-"]

        results = []
        new_rows_for_history = []
        symbols = sorted(list(set(df["Symbol"].dropna().astype(str))))

        for symbol in symbols:
            sdf = df[df["Symbol"].astype(str) == symbol].sort_values("TIME").tail(10)
            if len(sdf) < 5: continue

            signal_count = {}
            for _, row in sdf.iterrows():
                sig = signal_name(row["OI_DIR"], row["PRICE_DIR"])
                if sig: signal_count[sig] = signal_count.get(sig, 0) + 1
            
            if not signal_count: continue
            best_signal = max(signal_count, key=signal_count.get)
            confidence = round(signal_count[best_signal] * 100 / len(sdf), 2)
            if confidence < 60: continue

            status = "ACTIVE"
            if symbol not in known_symbols:
                status = "NEW"
                known_symbols.add(symbol)
                new_rows_for_history.append([symbol, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

            results.append([0, symbol, best_signal, status, confidence, len(sdf), 
                            sdf["PRICE_VALUE"].dropna().iloc[-1] if not sdf["PRICE_VALUE"].dropna().empty else None, 
                            datetime.now().strftime("%H:%M:%S")])

        # Formatting results
        results = sorted(results, key=lambda x: x[4], reverse=True)
        for i, row in enumerate(results, start=1): row[0] = i
        
        final_data = [["RANK", "SYMBOL", "SIGNAL", "STATUS", "CONFIDENCE", "FETCH_COUNT", "LAST_PRICE", "LAST_UPDATE"]]
        final_data.extend(results)

        # Update Sheet
        current_hash = hashlib.md5(str(final_data).encode()).hexdigest()
        if current_hash != last_hash:
            gain.clear()
            gain.update(values=final_data, range_name=f"A1:H{len(final_data)}")
            if new_rows_for_history: hist.append_rows(new_rows_for_history)
            last_hash = current_hash
            
            # --- FIXED SUMMARY PRINT ---
            gain_df = pd.DataFrame(results, columns=["RANK", "SYMBOL", "SIGNAL", "STATUS", "CONFIDENCE", "COUNT", "PRICE", "TIME"])
            print(f"\n--- SUMMARY {datetime.now().strftime('%H:%M:%S')} ---")
            print(f"LONG BUILDUP (BUY)    : {gain_df['SIGNAL'].str.contains('LONG BUILDUP', na=False).sum()}")
            print(f"SHORT BUILDUP (SELL)  : {gain_df['SIGNAL'].str.contains('SHORT BUILDUP', na=False).sum()}")
            print(f"LONG UNWINDING (SELL) : {gain_df['SIGNAL'].str.contains('LONG UNWINDING', na=False).sum()}")
            print(f"SHORT COVERING (BUY)  : {gain_df['SIGNAL'].str.contains('SHORT COVERING', na=False).sum()}")
            print("------------------------------------------")

    except Exception as e:
        print(datetime.now(), "ERROR :", str(e))

    time.sleep(SLEEP_SECONDS)