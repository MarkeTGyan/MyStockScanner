import requests
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- AUTH ---
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "oi-analysis-496406-0cd8eaad9bc1.json",
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)
sheet = client.open("OI_ANALYSIS").worksheet("TOPGAIN")

GAINER_URL = "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
LOSER_URL  = "https://www.nseindia.com/api/live-analysis-variations?index=loosers"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

session = requests.Session()

def init():
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except: pass

def fetch_data(url):
    try:
        resp = session.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # Nayi NSE response structure: 'data' key ke andar hi list hoti hai
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return []

def run():
    init()
    g_data = fetch_data(GAINER_URL)[:10]
    l_data = fetch_data(LOSER_URL)[:10]

    if not g_data and not l_data:
        print("Empty Response")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = ["TIME", "G_SYMBOL", "OPEN", "HIGH", "LOW", "PREV", "LTP", "%", "VOL", "VAL", "",
              "L_SYMBOL", "OPEN", "HIGH", "LOW", "PREV", "LTP", "%", "VOL", "VAL"]
    
    rows = [header]
    for i in range(10):
        g = g_data[i] if i < len(g_data) else {}
        l = l_data[i] if i < len(l_data) else {}
        rows.append([
            now,
            g.get("symbol"), g.get("openPrice"), g.get("highPrice"), g.get("lowPrice"), g.get("prevPrice"), g.get("ltp"), g.get("perChange"), g.get("tradeQuantity"), g.get("turnover"),
            "",
            l.get("symbol"), l.get("openPrice"), l.get("highPrice"), l.get("lowPrice"), l.get("prevPrice"), l.get("ltp"), l.get("perChange"), l.get("tradeQuantity"), l.get("turnover")
        ])

    # batch update is faster
    sheet.clear()
    sheet.update("A1", rows, value_input_option="USER_ENTERED")
    print(f"UPDATED: {now}")

# --- MARKET TIME LOGIC ---
def is_market_time():
    now = datetime.now()
    if now.weekday() >= 5: return False, "WEEKEND"
    current_time = now.time()
    if current_time < datetime.strptime("09:15:00", "%H:%M:%S").time(): return False, "WAITING FOR 09:15"
    if current_time > datetime.strptime("15:35:00", "%H:%M:%S").time(): return False, "MARKET CLOSED"
    return True, "ACTIVE"

print("SYSTEM STARTED")
while True:
    active, msg = is_market_time()
    if active:
        try: run()
        except Exception as e: print("RUN ERROR:", e)
        time.sleep(60)
    else:
        print(msg)
        time.sleep(300)