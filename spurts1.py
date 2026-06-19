# ... (Baaki imports wahi rahen)
import math

def fetch_and_append():
    try:
        session = requests.Session(impersonate="chrome124")
        # Referer aur Headers ko optimize kiya
        session.headers.update(headers)
        session.get("https://www.nseindia.com", timeout=15)
        
        response = session.get(API_URL, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ API Error: {response.status_code}")
            return

        data = response.json()
        # Data extraction logic (Safe handling)
        rows = next((block.get("Rise-in-OI-Rise", []) for block in data.get("data", []) if "Rise-in-OI-Rise" in block), [])

        if not rows:
            print("ℹ️ No data in 'Rise-in-OI-Rise'.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = []

        for sno, row in enumerate(rows, start=1):
            symbol = row.get("symbol", "")
            current_oi = float(row.get("latestOI", 0))
            
            # Trend calculation
            oi_trend = "NEW"
            if symbol in previous_oi:
                old_oi = previous_oi[symbol]
                oi_trend = "🟢↑ UP" if current_oi > old_oi else ("🔴↓ DOWN" if current_oi < old_oi else "➖ SAME")
            previous_oi[symbol] = current_oi

            output.append([
                sno, timestamp, symbol, row.get("instrument", ""),
                row.get("expiryDate", ""), row.get("strikePrice", ""),
                row.get("optionType", ""), oi_trend, current_oi,
                row.get("prevOI", ""), row.get("changeInOI", ""),
                row.get("pChangeInOI", ""), row.get("ltp", ""),
                row.get("prevClose", ""), row.get("pChange", ""),
                row.get("volume", ""), row.get("turnover", ""),
                row.get("underlyingValue", "")
            ])

        # Batch append optimization: 
        # Agar append_rows error de, toh gspread v6+ ke liye 'value_input_option' zaruri hai
        sheet.append_rows(output, value_input_option="USER_ENTERED")
        print(f"✅ {timestamp} : {len(output)} rows added.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")