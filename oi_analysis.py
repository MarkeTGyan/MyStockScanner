# =========================================================
# INSTALL REQUIRED LIBRARIES
# =========================================================
# pip install requests pandas gspread oauth2client gspread-formatting

import requests
import pandas as pd
import gspread
import time
import json

from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from gspread_formatting import *

# =========================================================
# GOOGLE SHEETS AUTH
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

spreadsheet = client.open("OI_ANALYSIS")

sheet_main = spreadsheet.worksheet("OI_DATA")
sheet_record = spreadsheet.worksheet("OI_DATA1")
sheet_top7 = spreadsheet.worksheet("DAILY_TOP5")
sheet_incr = spreadsheet.worksheet("OI_INCR")

# =========================================================
# NEW TOP SHEET
# =========================================================

sheet_top = spreadsheet.worksheet("TOP")

# =========================================================
# NSE URL
# =========================================================

URL = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"

# =========================================================
# HEADERS
# =========================================================

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

# =========================================================
# SESSION
# =========================================================

session = requests.Session()

# =========================================================
# GLOBAL STORAGE
# =========================================================

previous_oi = {}

# sudden spike tracking
previous_full_oi = {}

# =========================================================
# SAFE FLOAT
# =========================================================

def safe_float(x):

    try:

        if x is None:
            return 0

        return float(str(x).replace(",", ""))

    except:

        return 0

# =========================================================
# REFRESH COOKIE
# =========================================================

def refresh_cookie():

    global session

    try:

        session = requests.Session()

        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=15
        )

        print("NSE Cookies Refreshed")

    except Exception as e:

        print("Cookie Error :", e)

# =========================================================
# COLOR FORMAT
# =========================================================

green_format = CellFormat(
    backgroundColor=Color(0.75, 1, 0.75)
)

red_format = CellFormat(
    backgroundColor=Color(1, 0.75, 0.75)
)

# =========================================================
# FETCH FUNCTION
# =========================================================

def fetch_oi_data():

    global previous_oi
    global previous_full_oi

    print("Fetching OI Data...")

    refresh_cookie()

    try:

        response = session.get(
            URL,
            headers=headers,
            timeout=20
        )

        text_data = response.text.strip()

        if text_data == "":
            print("Empty Response")
            return

        try:

            data_json = json.loads(text_data)

        except:

            print("JSON Decode Failed")
            return

        if "data" not in data_json:
            print("No data key")
            return

        data = data_json["data"]

        if len(data) == 0:
            print("No data received")
            return

        rows = []

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        time_header = datetime.now().strftime("%H:%M")

        # =================================================
        # PROCESS DATA
        # =================================================

        for item in data:

            symbol = item.get("symbol", "")

            oi_today = int(
                safe_float(item.get("latestOI"))
            )

            oi_prev = int(
                safe_float(item.get("prevOI"))
            )

            change_oi = oi_today - oi_prev

            percent_change = 0

            if oi_prev > 0:

                percent_change = round(
                    (change_oi / oi_prev) * 100,
                    2
                )

            volume = int(
                safe_float(item.get("volume"))
            )

            fut_value = safe_float(
                item.get("futValue")
            )

            opt_value = safe_float(
                item.get("optValue")
            )

            total_value = fut_value + opt_value

            # =============================================
            # GOOGLE SYMBOL FIX
            # =============================================

            if symbol == "NIFTY":

                google_symbol = "INDEXNSE:NIFTY_50"

            elif symbol == "BANKNIFTY":

                google_symbol = "INDEXNSE:NIFTY_BANK"

            else:

                google_symbol = f"NSE:{symbol}"

            # =============================================
            # GOOGLEFINANCE FORMULA
            # =============================================

            price_formula = f'''=IFERROR(
ROUND(GOOGLEFINANCE("{google_symbol}","price"),2)
&" | "&
IF(
GOOGLEFINANCE("{google_symbol}","price")>
GOOGLEFINANCE("{google_symbol}","closeyest"),
"🟢 "&ROUND(
GOOGLEFINANCE("{google_symbol}","price")-
GOOGLEFINANCE("{google_symbol}","closeyest"),2)
&" ("&
ROUND(
(
(GOOGLEFINANCE("{google_symbol}","price")-
GOOGLEFINANCE("{google_symbol}","closeyest"))/
GOOGLEFINANCE("{google_symbol}","closeyest")
)*100,2)
&"%)",
"🔴 "&ROUND(
GOOGLEFINANCE("{google_symbol}","price")-
GOOGLEFINANCE("{google_symbol}","closeyest"),2)
&" ("&
ROUND(
(
(GOOGLEFINANCE("{google_symbol}","price")-
GOOGLEFINANCE("{google_symbol}","closeyest"))/
GOOGLEFINANCE("{google_symbol}","closeyest")
)*100,2)
&"%)"
),"")'''

            rows.append([

                symbol,
                oi_today,
                oi_prev,
                change_oi,
                percent_change,
                volume,
                fut_value,
                opt_value,
                total_value,
                price_formula

            ])

        # =================================================
        # DATAFRAME
        # =================================================

        df = pd.DataFrame(rows, columns=[

            "Symbol",
            "OI Today",
            "OI Previous",
            "OI Change",
            "% OI Change",
            "Volume",
            "Futures Value",
            "Options Value",
            "Total Value",
            "Price Change"

        ])

        # =================================================
        # SORT
        # =================================================

        df = df.sort_values(
            by="OI Change",
            ascending=False
        )

        # =================================================
        # MAIN SHEET
        # =================================================

        main_data = [df.columns.tolist()] + df.values.tolist()

        sheet_main.clear()

        sheet_main.update(
            "A1",
            main_data,
            value_input_option="USER_ENTERED"
        )

        # =================================================
        # DAILY_TOP5 (TOP 11)
        # =================================================

        top11 = df.head(11)

        top_rows = []

        rank = 1

        for _, row in top11.iterrows():

            symbol = row["Symbol"]

            current_change = int(row["OI Change"])

            old_change = previous_oi.get(symbol, current_change)

            incr = current_change - old_change

            # =============================================
            # ARROW
            # =============================================

            if incr > 0:
                incr_text = f"🟢 ▲ {incr} OI"

            elif incr < 0:
                incr_text = f"🔴 ▼ {incr} OI"

            else:
                incr_text = f"• {incr} OI"

            previous_oi[symbol] = current_change

            live_price_text = sheet_main.acell(
                f"J{df.index.get_loc(row.name)+2}"
            ).value

            top_rows.append([

                current_time,
                rank,
                symbol,
                current_change,
                incr_text,
                row["% OI Change"],
                row["Volume"],
                row["Total Value"],
                live_price_text

            ])

            rank += 1

        sheet_top7.append_rows(
            top_rows,
            value_input_option="USER_ENTERED"
        )

        # =================================================
        # TOP SHEET
        # SUDDEN OI SPIKE DETECTION
        # =================================================

        top_sheet_rows = []

        for _, row in df.iterrows():

            symbol = row["Symbol"]

            current_oi = int(row["OI Change"])

            old_oi = previous_full_oi.get(symbol, current_oi)

            oi_jump = current_oi - old_oi

            # =============================================
            # SUDDEN SPIKE CONDITION
            # =============================================

            # sudden jump threshold
            if abs(oi_jump) >= 2000:

                if oi_jump > 0:
                    jump_text = f"🟢 BIG OI SPIKE +{oi_jump}"

                else:
                    jump_text = f"🔴 OI DROP {oi_jump}"

                live_price_text = sheet_main.acell(
                    f"J{df.index.get_loc(row.name)+2}"
                ).value

                top_sheet_rows.append([

                    current_time,
                    symbol,
                    current_oi,
                    old_oi,
                    oi_jump,
                    row["% OI Change"],
                    row["Volume"],
                    row["Total Value"],
                    jump_text,
                    live_price_text

                ])

            previous_full_oi[symbol] = current_oi

        # =============================================
        # APPEND TO TOP SHEET
        # =============================================

        if len(top_sheet_rows) > 0:

            sheet_top.append_rows(
                top_sheet_rows,
                value_input_option="USER_ENTERED"
            )

        # =================================================
        # OI_INCR SHEET
        # =================================================

        all_values = sheet_incr.get_all_values()

        if len(all_values) == 0:

            bulk_data = [["Symbol", time_header]]

            for _, row in df.iterrows():

                bulk_data.append([
                    row["Symbol"],
                    row["OI Change"]
                ])

            sheet_incr.update(
                "A1",
                bulk_data
            )

        else:

            headers_row = all_values[0]

            next_col = len(headers_row) + 1

            sheet_incr.update_cell(
                1,
                next_col,
                time_header
            )

            symbols_sheet = sheet_incr.col_values(1)

            symbol_row_map = {}

            for idx, sym in enumerate(symbols_sheet):

                symbol_row_map[sym] = idx + 1

            update_range = []

            for _, row in df.iterrows():

                symbol = row["Symbol"]

                oi_val = int(row["OI Change"])

                if symbol not in symbol_row_map:

                    new_row = len(symbols_sheet) + 1

                    sheet_incr.update_cell(
                        new_row,
                        1,
                        symbol
                    )

                    symbol_row_map[symbol] = new_row

                    symbols_sheet.append(symbol)

                row_no = symbol_row_map[symbol]

                update_range.append({
                    "range": gspread.utils.rowcol_to_a1(
                        row_no,
                        next_col
                    ),
                    "values": [[oi_val]]
                })

            if len(update_range) > 0:

                sheet_incr.batch_update(update_range)

            # =============================================
            # SORT LAST COLUMN DESCENDING
            # =============================================

            sheet_incr.sort(
                (next_col, 'des')
            )

        print("SUCCESS : DATA UPDATED")

    except Exception as e:

        print("ERROR :", e)

# =========================================================
# MAIN LOOP
# =========================================================

# =========================================================
# SMART MARKET TIME LOOP
# =========================================================

while True:

    now = datetime.now()

    current_time = now.strftime("%H:%M")

    weekday = now.weekday()

    # =============================================
    # WEEKDAY CHECK
    # Monday = 0
    # Friday = 4
    # =============================================

    if weekday <= 4:

        # =========================================
        # MARKET TIME CHECK
        # =========================================

        if "09:15" <= current_time <= "15:35":

            print(f"MARKET ACTIVE : {current_time}")

            try:

                fetch_oi_data()

            except Exception as e:

                print("MAIN LOOP ERROR :", e)

            print("Waiting 5 Minutes...\n")

            time.sleep(300)

        else:

            print(f"MARKET CLOSED : {current_time}")

            # check every 1 minute
            time.sleep(60)

    else:

        print("WEEKEND - MARKET CLOSED")

        # weekend sleep
        time.sleep(300)