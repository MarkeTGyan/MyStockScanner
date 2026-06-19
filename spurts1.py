import os
import time
import warnings
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from curl_cffi import requests

# Fills/Downcasting वार्निंग को छुपाने के लिए
warnings.filterwarnings("ignore", category=FutureWarning)

previous_oi = {}

# =====================================================
# GOOGLE SHEET LOGIN
# =====================================================
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
spreadsheet = client.open("OI_ANALYSIS")
sheet = spreadsheet.worksheet("SPURTS")

HEADERS_LIST = [
    "SNO", "TIME", "SYMBOL", "INSTRUMENT", "EXPIRY", "STRIKE_PRICE",
    "OPTION_TYPE", "OI_TREND", "LATEST_OI", "PREVIOUS_OI",
    "CHANGE_IN_OI", "PCHANGE_IN_OI", "LTP", "PREV_CLOSE",
    "PCHANGE_PRICE", "VOLUME", "TURNOVER", "UNDERLYING_VALUE"
]

# =====================================================
# 🗄️ AUTO BACKUP & NEW DAY CLEAR LOGIC
# =====================================================
def backup_and_clear_old_day():
    """शीट के पुराने डेटा का उसी फोल्डर में CSV बैकअप बनाता है और फिर शीट साफ़ करता है"""
    try:
        print("🔍 शीट के पुराने डेटा की तारीख जांची जा रही है...")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        first_entry_time = sheet.acell("B2").value
        
        if first_entry_time:
            entry_date = first_entry_time.split(" ")[0]
            
            if entry_date != today_str:
                print(f"📦 पुराना डेटा मिला ({entry_date})। बैकअप फ़ाइल बनाई जा रही है...")
                
                all_records = sheet.get_all_values()
                
                if len(all_records) > 1:
                    filename = f"backup_spurts_{entry_date}.csv"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        for row in all_records:
                            line = ",".join([f'"{str(item)}"' for item in row])
                            f.write(line + "\n")
                            
                    print(f"💾 बैकअप सफलतापूर्वक सेव हुआ: {os.path.abspath(filename)}")
                
                print("♻️ आज के नए सेशन के लिए शीट साफ़ की जा रही है...")
                sheet.clear()
                sheet.update(values=[HEADERS_LIST], range_name="A1:R1")
                print("✅ SHEET फ्रेश स्टार्ट के लिए रेडी है।")
            else:
                print("📈 आज का डेटा पहले से मौजूद है, उसी के आगे कंटिन्यू करेंगे।")
        else:
            if not sheet.acell("A1").value:
                sheet.update(values=[HEADERS_LIST], range_name="A1:R1")
                
    except Exception as e:
        print(f"⚠️ बैकअप या क्लियर करने में एरर (शायद शीट खाली थी): {e}")
        if not sheet.acell("A1").value:
            sheet.update(values=[HEADERS_LIST], range_name="A1:R1")

# =====================================================
# 🛡️ MARKET TIMING CONTROLLER
# =====================================================
def is_market_time():
    """चेक करता है कि क्या अभी वीक डे (Mon-Fri) है और समय सुबह 9:15 से दोपहर 3:35 के बीच है"""
    now = datetime.now()
    weekday = now.weekday()
    
    if weekday >= 5:
        return False, "💤 WEEKEND OFF: आज शनिवार/रविवार है। मार्केट बंद है।"
        
    current_time = now.time()
    start_time = datetime.strptime("09:15:00", "%H:%M:%S").time()
    end_time = datetime.strptime("15:35:00", "%H:%M:%S").time()
    
    if current_time < start_time:
        return False, f"⏳ MARKET NOT STARTED: सुबह के 9:15 का इंतजार है (करंट टाइम: {now.strftime('%H:%M:%S')})"
    elif current_time > end_time:
        return False, f"🛑 MARKET CLOSED: शाम के 3:35 हो चुके हैं, आज का ट्रेडिंग सेशन बंद है।"
        
    return True, "ACTIVE"

# =====================================================
# ADVANCED REAL BROWSER HEADERS & API
# =====================================================
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest"
}

API_URL = "https://www.nseindia.com/api/live-analysis-oi-spurts-contracts"

def fetch_and_append():
    try:
        session = requests.Session(impersonate="chrome124")
        session.get("https://www.nseindia.com", headers=headers, timeout=15)
        time.sleep(1) 
        
        response = session.get(API_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ सर्वर व्यस्त है (Status Code: {response.status_code})")
            return

        data = response.json()
        rows = []

        for block in data.get("data", []):
            if "Rise-in-OI-Rise" in block:
                rows = block["Rise-in-OI-Rise"]
                break

        if not rows:
            print("ℹ️ इस समय कोई 'Rise-in-OI-Rise' डेटा नहीं मिला।")
            return

        # 🔹 बदलाव: rows = rows[:10] लाइन को हटा दिया गया है ताकि पूरी टेबल का डेटा आ सके
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = []

        for sno, row in enumerate(rows, start=1):
            symbol = row.get("symbol", "")
            current_oi = float(row.get("latestOI", 0))

            oi_trend = "NEW"

            if symbol in previous_oi:
                old_oi = previous_oi[symbol]
                if current_oi > old_oi:
                    oi_trend = "🟢↑ OI UP"
                elif current_oi < old_oi:
                    oi_trend = "🔴↓ OI DOWN"
                else:
                    oi_trend = "➖ SAME"

            previous_oi[symbol] = current_oi

            output.append([
                sno, timestamp, symbol, row.get("instrument", ""),
                row.get("expiryDate", ""), row.get("strikePrice", ""),
                row.get("optionType", ""), oi_trend, row.get("latestOI", ""),
                row.get("prevOI", ""), row.get("changeInOI", ""),
                row.get("pChangeInOI", ""), row.get("ltp", ""),
                row.get("prevClose", ""), row.get("pChange", ""),
                row.get("volume", ""), row.get("turnover", ""),
                row.get("underlyingValue", "")
            ])

        sheet.append_rows(output, value_input_option="RAW")
        print(f"✅ {timestamp} : टेबल की सभी {len(output)} रो शीट में लाइव जोड़ दी गईं।")

    except Exception as e:
        print("❌ एरर :", str(e))

# =====================================================
# 🔄 MAIN LOOP SYSTEM WITH SLEEP-WAITING
# =====================================================
print("🤖 मार्केट टाइमिंग ऑटो-पायलट सिस्टम एक्टिवेटेड...")
backup_flag_done = False

while True:
    market_active, status_msg = is_market_time()
    
    if market_active:
        if not backup_flag_done:
            backup_and_clear_old_day()
            backup_flag_done = True
            
        fetch_and_append()
        time.sleep(60) 
    else:
        print(status_msg)
        if datetime.now().time() > datetime.strptime("15:35:00", "%H:%M:%S").time():
            backup_flag_done = False
            
        print("⏰ स्क्रिप्ट स्लीप मोड में है। 5 मिनट बाद दोबारा समय चेक करेगी...\n")
        time.sleep(300)