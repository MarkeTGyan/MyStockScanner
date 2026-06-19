import requests
import gspread
import time
import json

from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =========================================================
# GOOGLE SHEETS
# =========================================================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "oi-analysis-496406-0cd8eaad9bc1.json",
    scope
)

client = gspread.authorize(creds)
sheet = client.open("OI_ANALYSIS").worksheet("TOPGAIN")

# =========================================================
# NSE URL
# =========================================================

GAINER_URL = "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
LOSER_URL  = "https://www.nseindia.com/api/live-analysis-variations?index=loosers"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

session = requests.Session()

# =========================================================
# INIT SESSION (VERY IMPORTANT)
# =========================================================

def init():
    session.get("https://www.nseindia.com", headers=headers, timeout=10)

# =========================================================
# SAFE JSON PARSER (CRITICAL FIX)
# =========================================================

def safe_json(response):

    try:
        return response.json()
    except:

        print("BLOCKED RESPONSE DETECTED")
        return {}

# =========================================================
# EXTRACT DATA (ALL STRUCTURES FIXED)
# =========================================================

def extract(data):

    if not isinstance(data, dict):
        return []

    if "data" in data:
        return data["data"]

    if "NIFTY" in data and "data" in data["NIFTY"]:
        return data["NIFTY"]["data"]

    for k in data:
        try:
            if isinstance(data[k], dict) and "data" in data[k]:
                return data[k]["data"]
        except:
            pass

    return []

# =========================================================
# VALUE GETTER (YOUR NEW FORMAT)
# =========================================================

def val(x, key):
    return x.get(key, 0)

# =========================================================
# FETCH
# =========================================================

def fetch():

    init()

    g = session.get(GAINER_URL, headers=headers, timeout=20)
    l = session.get(LOSER_URL, headers=headers, timeout=20)

    g_data = extract(safe_json(g))[:10]
    l_data = extract(safe_json(l))[:10]

    print("GAINERS:", len(g_data), "LOSERS:", len(l_data))

    return g_data, l_data

# =========================================================
# MAIN
# =========================================================

def run():

    gainers, losers = fetch()

    if not gainers or not losers:
        print("NO DATA (BLOCKED OR EMPTY)")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.clear()

    header = [[
        "TIME",

        "GAINER SYMBOL","OPEN","HIGH","LOW","PREV CLOSE","LTP","% CHANGE","VOLUME","VALUE",
        "",
        "LOSER SYMBOL","OPEN","HIGH","LOW","PREV CLOSE","LTP","% CHANGE","VOLUME","VALUE"
    ]]

    sheet.update("A1", header)

    rows = []

    for i in range(10):

        g = gainers[i] if i < len(gainers) else {}
        l = losers[i] if i < len(losers) else {}

        rows.append([

            now,

            # ================= GAINER =================
            val(g, "symbol"),
            val(g, "open_price"),
            val(g, "high_price"),
            val(g, "low_price"),

            val(g, "prev_price"),
            val(g, "ltp"),
            val(g, "perChange"),
            val(g, "trade_quantity"),
            val(g, "turnover"),

            "",

            # ================= LOSER =================
            val(l, "symbol"),
            val(l, "open_price"),
            val(l, "high_price"),
            val(l, "low_price"),

            val(l, "prev_price"),
            val(l, "ltp"),
            val(l, "perChange"),
            val(l, "trade_quantity"),
            val(l, "turnover")

        ])

    sheet.update("A2", rows)

    print("UPDATED:", now)

# =========================================================
# LOOP
# =========================================================

#while True:
   # run()
   # time.sleep(60)


#===========================================================

# =========================================================
# MARKET TIME CONTROLLER
# =========================================================

def is_market_time():

    now = datetime.now()

    weekday = now.weekday()   # Monday=0 ... Sunday=6

    if weekday >= 5:
        return False, "WEEKEND - MARKET CLOSED"

    current_time = now.time()

    start_time = datetime.strptime(
        "09:15:00",
        "%H:%M:%S"
    ).time()

    end_time = datetime.strptime(
        "15:35:00",
        "%H:%M:%S"
    ).time()

    if current_time < start_time:
        return False, (
            f"MARKET NOT STARTED : "
            f"{now.strftime('%H:%M:%S')}"
        )

    if current_time > end_time:
        return False, (
            f"MARKET CLOSED : "
            f"{now.strftime('%H:%M:%S')}"
        )

    return True, "ACTIVE"


# =========================================================
# LOOP
# =========================================================

print("TOP GAINER / LOSER SYSTEM STARTED")

while True:

    market_active, msg = is_market_time()

    if market_active:

        try:

            run()

        except Exception as e:

            print("RUN ERROR :", e)

        time.sleep(60)

    else:

        print(msg)

        # Market बंद होने पर हर 5 मिनट बाद चेक करेगा
        time.sleep(300)