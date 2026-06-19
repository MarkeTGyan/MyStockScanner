import pandas as pd
import yfinance as yf
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# =====================================================
# GOOGLE SHEET AUTH
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

try:
    MULTIBAGGER = spreadsheet.worksheet("MULTIBAGGER")
except:
    MULTIBAGGER = spreadsheet.add_worksheet(
        title="MULTIBAGGER",
        rows=5000,
        cols=20
    )

# =====================================================
# SETTINGS
# =====================================================

LOOKBACK = 1000
MAX_WORKERS = 5

# =====================================================
# NSE STOCK LIST
# =====================================================

def get_nse_symbols():

    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    df = pd.read_csv(url)

    symbols = (
        df["SYMBOL"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return symbols

# =====================================================
# MONTHLY BREAKOUT COUNT
# =====================================================

def get_breakout_counts(highs):

    breakout_dates = []

    for i in range(LOOKBACK, len(highs)):

        prev_high = highs.iloc[i - LOOKBACK:i].max()

        if highs.iloc[i] >= prev_high:

            breakout_dates.append(highs.index[i])

    counts = {}

    if breakout_dates:

        temp = pd.DataFrame({
            "DATE": breakout_dates
        })

        temp["MONTH"] = temp["DATE"].dt.strftime("%Y-%m")

        counts = (
            temp["MONTH"]
            .value_counts()
            .to_dict()
        )

    return counts

# =====================================================
# SCAN STOCK
# =====================================================

def scan_stock(symbol):

    try:

        ticker = f"{symbol}.NS"

        data = yf.download(
            ticker,
            period="5y",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if data.empty:
            return None

        highs = data["High"].squeeze().dropna()

        if len(highs) < LOOKBACK + 1:
            return None

        today_high = float(highs.iloc[-1])

        previous_1000_high = float(
            highs.iloc[-LOOKBACK-1:-1].max()
        )

        # ==============================
        # BREAKOUT CONDITION
        # ==============================

        if today_high < previous_1000_high:
            return None

        breakout_pct = round(

            (
                (today_high - previous_1000_high)
                / previous_1000_high
            ) * 100,

            2

        )

        counts = get_breakout_counts(highs)

        row = [

            datetime.now().strftime("%d-%b-%Y"),

            symbol,

            round(today_high, 2),

            round(previous_1000_high, 2),

            breakout_pct

        ]

        current_month = pd.Timestamp.today()

        for i in range(6):

            month_name = (
                current_month -
                pd.DateOffset(months=i)
            ).strftime("%Y-%m")

            row.append(
                counts.get(month_name, 0)
            )

        print(f"BREAKOUT FOUND : {symbol}")

        return row

    except Exception as e:

        print(
            f"{symbol} : {str(e)}"
        )

        return None

# =====================================================
# UPDATE GOOGLE SHEET
# =====================================================

def update_sheet(results):

    MULTIBAGGER.clear()

    headers = [[

        "DATE",
        "SYMBOL",
        "TODAY_HIGH",
        "PREV_1000_HIGH",
        "BREAKOUT_%",
        "CURRENT_MONTH",
        "MONTH_1",
        "MONTH_2",
        "MONTH_3",
        "MONTH_4",
        "MONTH_5"

    ]]

    MULTIBAGGER.update(
        "A1",
        headers
    )

    if len(results) > 0:

        MULTIBAGGER.update(

            f"A2:K{len(results)+1}",

            results

        )

# =====================================================
# MAIN
# =====================================================

def main():

    print(
        "DOWNLOADING NSE SYMBOLS..."
    )

    symbols = get_nse_symbols()

    print(
        f"TOTAL NSE STOCKS : {len(symbols)}"
    )

    results = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {

            executor.submit(
                scan_stock,
                symbol
            ): symbol

            for symbol in symbols

        }

        for future in as_completed(futures):

            result = future.result()

            if result:

                results.append(result)

    results.sort(
        key=lambda x: x[4],
        reverse=True
    )

    update_sheet(results)

    print(
        f"TOTAL BREAKOUT STOCKS : {len(results)}"
    )

    print(
        "MULTIBAGGER SHEET UPDATED SUCCESSFULLY"
    )

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    main()