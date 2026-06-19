# =====================================================
# MULTIBAGGER FUNDAMENTAL SCANNER V3.0
# PART 1 / 5
# GOOGLE CONNECTION + ULTIMATE ANTI BLOCK ENGINE
# =====================================================


import gspread
import requests
import time
import random
import traceback

from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from oauth2client.service_account import (
    ServiceAccountCredentials
)


# =====================================================
# GOOGLE SHEET CONFIGURATION
# =====================================================

JSON_FILE = (
    "oi-analysis-496406-0cd8eaad9bc1.json"
)

SPREADSHEET_NAME = (
    "OI_ANALYSIS"
)

WORKSHEET_NAME = (
    "MULTIBAGGER"
)


# =====================================================
# GOOGLE AUTHENTICATION
# =====================================================

SCOPE = [

    "https://spreadsheets.google.com/feeds",

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive"

]


credentials = (
    ServiceAccountCredentials
    .from_json_keyfile_name(
        JSON_FILE,
        SCOPE
    )
)


client = gspread.authorize(
    credentials
)


sheet = (
    client
    .open(SPREADSHEET_NAME)
    .worksheet(WORKSHEET_NAME)
)


print("\n" + "="*60)

print(
    "GOOGLE SHEET CONNECTED SUCCESSFULLY"
)

print(
    "SPREADSHEET :",
    SPREADSHEET_NAME
)

print(
    "WORKSHEET   :",
    WORKSHEET_NAME
)

print("="*60)


# =====================================================
# ADVANCED HTTP SESSION
# =====================================================


session = requests.Session()


retry_strategy = Retry(

    total=5,

    connect=5,

    read=5,

    backoff_factor=3,

    status_forcelist=[

        429,
        500,
        502,
        503,
        504

    ]
)


adapter = HTTPAdapter(

    max_retries=retry_strategy

)


session.mount(
    "https://",
    adapter
)

session.mount(
    "http://",
    adapter
)


# =====================================================
# ROTATING USER AGENTS
# =====================================================


USER_AGENTS = [

    # Chrome Windows

    (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    ),


    # Edge

    (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Edge/137.0 Safari/537.36"
    ),


    # Linux Chrome

    (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/136.0 Safari/537.36"
    ),


    # Firefox

    (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64; rv:140.0) "
        "Gecko/20100101 Firefox/140.0"
    )

]


# =====================================================
# FAILED STOCK STORAGE
# =====================================================


FAILED_SYMBOLS = []


SUCCESS_SYMBOLS = []


# =====================================================
# RANDOM HUMAN DELAY
# =====================================================


def human_delay():

    delay = random.uniform(
        5,
        10
    )

    print(
        f"Waiting {delay:.1f} seconds..."
    )

    time.sleep(delay)


# =====================================================
# EXTRA COOLING DELAY
# =====================================================


def cooling_break(stock_number):

    if stock_number % 10 == 0:

        print(
            "\nCOOLING BREAK 30 SECONDS"
        )

        time.sleep(30)


# =====================================================
# RANDOM HEADER CREATOR
# =====================================================


def get_headers():

    return {

        "User-Agent":
            random.choice(USER_AGENTS),


        "Accept":
            (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "*/*;q=0.8"
            ),


        "Accept-Language":
            "en-US,en;q=0.9",


        "Cache-Control":
            "no-cache",


        "Pragma":
            "no-cache",


        "Connection":
            "keep-alive"

    }


# =====================================================
# ADVANCED SCREENER FETCHER
# =====================================================


def fetch_screener_page(symbol):

    url = (
        "https://www.screener.in/company/"
        f"{symbol}/"
    )


    for attempt in range(1, 6):

        try:

            print(
                f"{symbol} | Attempt {attempt}"
            )


            response = session.get(

                url,

                headers=get_headers(),

                timeout=30

            )


            if response.status_code == 200:

                print(
                    f"{symbol} : DATA DOWNLOADED"
                )


                return BeautifulSoup(

                    response.text,

                    "html.parser"

                )


            elif response.status_code == 404:

                print(
                    f"{symbol} : COMPANY NOT FOUND"
                )

                break


            elif response.status_code == 429:

                wait = attempt * 30

                print(
                    f"{symbol} : BLOCKED "
                    f"WAITING {wait} SEC"
                )

                time.sleep(wait)


            else:

                print(
                    f"{symbol} : HTTP ERROR",
                    response.status_code
                )

                time.sleep(10)


        except Exception as error:


            print(
                f"{symbol} NETWORK ERROR:"
            )

            print(error)


            traceback.print_exc()


            time.sleep(
                attempt * 10
            )


    FAILED_SYMBOLS.append(symbol)


    print(
        f"{symbol} : FAILED AFTER ALL RETRIES"
    )


    return None


# =====================================================
# SAFE GAP BETWEEN STOCKS
# =====================================================


def wait_between_stocks(stock_number):

    human_delay()

    cooling_break(
        stock_number
    )


# =====================================================
# PART 1 COMPLETED
# =====================================================


print("\n" + "="*60)

print(
    "PART 1 LOADED SUCCESSFULLY"
)

print(
    "ULTIMATE ANTI BLOCK ENGINE READY"
)

print("="*60)



# =====================================================
# PART 2 / 5
# ADVANCED UNIVERSAL SCREENER DATA EXTRACTOR
# =====================================================


# =====================================================
# NORMALIZE DIFFERENT SCREENER FIELD NAMES
# =====================================================

def normalize_key(key):

    k = (
        str(key)
        .lower()
        .replace("\n", " ")
        .replace(":", "")
        .strip()
    )


    mapping = {


        # =================================================
        # TOP RATIOS
        # =================================================

        "market cap": "Market Cap",

        "current price": "Current Price",

        "high / low": "High / Low",

        "stock p/e": "Stock P/E",

        "book value": "Book Value",

        "dividend yield": "Dividend Yield",

        "roe": "ROE",

        "roce": "ROCE",

        "face value": "Face Value",


        # =================================================
        # BALANCE SHEET
        # =================================================

        "reserves": "Reserves",

        "borrowings": "Debt",

        "debt": "Debt",

        "total debt": "Debt",

        "debtors": "Debtors",

        "debtor days": "Debtor Days",

        "interest coverage": "Interest Coverage",

        "interest coverage ratio":
            "Interest Coverage",


        # =================================================
        # SALES & PROFIT
        # =================================================

        "sales": "Sales",

        "revenue": "Sales",

        "turnover": "Sales",

        "sales growth":
            "Sales Growth",

        "sales cagr 3 years":
            "Sales CAGR 3 Years",

        "sales cagr 3yrs":
            "Sales CAGR 3 Years",

        "profit after tax":
            "Profit After Tax",

        "net profit":
            "Profit After Tax",

        "pat":
            "Profit After Tax",

        "profit growth":
            "Profit Growth",

        "profit cagr 3 years":
            "Profit CAGR 3 Years",

        "profit cagr 5 years":
            "Profit CAGR 5 Years",


        # =================================================
        # RATIOS
        # =================================================

        "eps":
            "EPS",

        "debt to equity":
            "Debt to Equity",

        "price to book":
            "Price to Book Value",

        "price to book value":
            "Price to Book Value",

        "p/b":
            "Price to Book Value",

        "ev/ebitda":
            "EV/EBITDA",

        "ev ebitda":
            "EV/EBITDA",

        "industry pe":
            "Industry PE",

        "industry p/e":
            "Industry PE",


        # =================================================
        # RETURNS
        # =================================================

        "return over 3 years":
            "Return over 3 years",

        "return over 5 years":
            "Return over 5 years",


        # =================================================
        # SHARE HOLDING
        # =================================================

        "promoters":
            "Promoter Holding",

        "promoter holding":
            "Promoter Holding",

        "promoter":
            "Promoter Holding",

        "fiis":
            "FII Holding",

        "fii holding":
            "FII Holding",

        "foreign institutions":
            "FII Holding",

        "diis":
            "DII Holding",

        "dii holding":
            "DII Holding",

        "domestic institutions":
            "DII Holding",


        # =================================================
        # HOLDING CHANGE
        # =================================================

        "chg in fii hold":
            "Change in FII Holding",

        "change in fii holding":
            "Change in FII Holding",

        "chg in dii hold":
            "Change in DII Holding",

        "change in dii holding":
            "Change in DII Holding",

        "change in promoter holding":
            "Change in Promoter Holding",

        "chg in promoter holding":
            "Change in Promoter Holding",


        # =================================================
        # OTHER
        # =================================================

        "pledged percentage":
            "Pledged Percentage",

        "pledged %":
            "Pledged Percentage",

    }


    return mapping.get(
        k,
        str(key).strip()
    )


# =====================================================
# EXTRACT TOP RATIO BOX
# =====================================================

def extract_top_ratios(soup, data):

    ratios = soup.select(
        "ul#top-ratios li"
    )


    for item in ratios:

        name = item.select_one(".name")

        value = item.select_one(".number")


        if name and value:

            key = normalize_key(
                name.get_text(
                    " ",
                    strip=True
                )
            )


            data[key] = value.get_text(
                " ",
                strip=True
            )


# =====================================================
# UNIVERSAL TABLE SCANNER
# YOUR ORIGINAL LOGIC IMPROVED
# =====================================================

def extract_all_tables(soup, data):

    tables = soup.find_all("table")


    for table in tables:

        rows = table.find_all("tr")


        for row in rows:

            cols = row.find_all(
                ["th", "td"]
            )


            if len(cols) < 2:
                continue


            key = cols[0].get_text(
                " ",
                strip=True
            )


            value = cols[-1].get_text(
                " ",
                strip=True
            )


            key = normalize_key(key)


            if key and value:

                data[key] = value


# =====================================================
# SPECIAL SHAREHOLDING RECOVERY
# =====================================================

def extract_shareholding_special(
    soup,
    data
):

    for table in soup.find_all("table"):

        for row in table.find_all("tr"):

            cols = row.find_all(
                ["td", "th"]
            )


            if len(cols) < 2:
                continue


            title = (
                cols[0]
                .get_text(
                    " ",
                    strip=True
                )
                .lower()
            )


            value = cols[-1].get_text(
                " ",
                strip=True
            )


            if "promoter" in title:

                data["Promoter Holding"] = value


            elif (
                "fii" in title
                or
                "foreign institution"
                in title
            ):

                data["FII Holding"] = value


            elif (
                "dii" in title
                or
                "domestic institution"
                in title
            ):

                data["DII Holding"] = value


# =====================================================
# COMPLETE DATA EXTRACTION MASTER
# =====================================================

def extract_complete_data(soup):

    data = {}


    # 1. Top Ratios
    extract_top_ratios(
        soup,
        data
    )


    # 2. Every Table
    extract_all_tables(
        soup,
        data
    )


    # 3. Extra Shareholding Safety
    extract_shareholding_special(
        soup,
        data
    )


    return data


# =====================================================
# DEBUG MODE
# =====================================================

def print_all_found_data(data):

    print("\nFOUND DATA")
    print("=" * 60)


    for key, value in sorted(data.items()):

        print(
            key,
            " : ",
            value
        )


# =====================================================
# PART 2 COMPLETED
# =====================================================

print("\n" + "=" * 60)

print(
    "PART 2 LOADED SUCCESSFULLY"
)

print(
    "ADVANCED SCREENER EXTRACTOR READY"
)

print("=" * 60)




# =====================================================
# PART 3 / 5
# SMART FIELD MAPPING ENGINE
# =====================================================


# =====================================================
# SAFE FIELD FETCHER
# Different names ko ek field me convert karega
# =====================================================

def get_field(data, names):

    for name in names:

        if name in data:

            value = str(data[name]).strip()

            if value and value != "-":
                return value

    return "-"


# =====================================================
# COMPLETE FUNDAMENTAL HEADERS
# Google Sheet J Column se start honge
# =====================================================

HEADERS = [

    # =================================================
    # BASIC VALUATION
    # =================================================

    "Market Cap",
    "Current Price",
    "High / Low",
    "Stock P/E",
    "Book Value",
    "Dividend Yield",


    # =================================================
    # PROFITABILITY
    # =================================================

    "ROCE",
    "ROE",
    "Face Value",


    # =================================================
    # BALANCE SHEET
    # =================================================

    "Reserves",
    "Debt",
    "Debt to Equity",
    "Interest Coverage",


    # =================================================
    # SALES & PROFIT
    # =================================================

    "Sales",
    "Sales Growth",
    "Sales CAGR 3 Years",

    "Profit After Tax",
    "Profit Growth",
    "Profit CAGR 3 Years",
    "Profit CAGR 5 Years",


    # =================================================
    # SHARE DATA
    # =================================================

    "EPS",
    "Price to Book Value",
    "Industry PE",
    "EV/EBITDA",


    # =================================================
    # SHAREHOLDING
    # =================================================

    "Promoter Holding",
    "FII Holding",
    "DII Holding",

    "Change in FII Holding",
    "Change in DII Holding",
    "Change in Promoter Holding",

    "Pledged Percentage",


    # =================================================
    # MARKET RETURNS
    # =================================================

    "Return over 3 years",
    "Return over 5 years",


    # =================================================
    # EXTRA ANALYSIS
    # =================================================

    "Debtor Days"

]


# =====================================================
# TOTAL COLUMNS CHECK
# =====================================================

TOTAL_FIELDS = len(HEADERS)


print("\n" + "=" * 60)

print(
    "TOTAL FUNDAMENTAL COLUMNS :",
    TOTAL_FIELDS
)

print("=" * 60)



# =====================================================
# CREATE SINGLE COMPANY FUNDAMENTAL ROW
# =====================================================

def create_fundamental_row(data):

    row = [

        # BASIC
        get_field(data, [
            "Market Cap"
        ]),

        get_field(data, [
            "Current Price"
        ]),

        get_field(data, [
            "High / Low"
        ]),

        get_field(data, [
            "Stock P/E"
        ]),

        get_field(data, [
            "Book Value"
        ]),

        get_field(data, [
            "Dividend Yield"
        ]),


        # QUALITY
        get_field(data, [
            "ROCE"
        ]),

        get_field(data, [
            "ROE"
        ]),

        get_field(data, [
            "Face Value"
        ]),


        # BALANCE SHEET
        get_field(data, [
            "Reserves"
        ]),

        get_field(data, [
            "Debt",
            "Borrowings",
            "Total Debt"
        ]),

        get_field(data, [
            "Debt to Equity",
            "Debt/Equity"
        ]),

        get_field(data, [
            "Interest Coverage",
            "Interest Coverage Ratio"
        ]),


        # SALES
        get_field(data, [
            "Sales",
            "Revenue",
            "Turnover"
        ]),

        get_field(data, [
            "Sales Growth",
            "Sales growth"
        ]),

        get_field(data, [
            "Sales CAGR 3 Years",
            "Sales CAGR 3Yrs"
        ]),


        # PROFIT
        get_field(data, [
            "Profit After Tax",
            "Net Profit",
            "PAT"
        ]),

        get_field(data, [
            "Profit Growth"
        ]),

        get_field(data, [
            "Profit CAGR 3 Years"
        ]),

        get_field(data, [
            "Profit CAGR 5 Years"
        ]),


        # RATIOS
        get_field(data, [
            "EPS"
        ]),

        get_field(data, [
            "Price to Book Value",
            "P/B"
        ]),

        get_field(data, [
            "Industry PE",
            "Industry P/E"
        ]),

        get_field(data, [
            "EV/EBITDA",
            "EV EBITDA"
        ]),


        # SHARE HOLDING
        get_field(data, [
            "Promoter Holding",
            "Promoters"
        ]),

        get_field(data, [
            "FII Holding",
            "FIIs",
            "Foreign Institutions"
        ]),

        get_field(data, [
            "DII Holding",
            "DIIs",
            "Domestic Institutions"
        ]),


        # HOLDING CHANGES
        get_field(data, [
            "Change in FII Holding",
            "Chg in FII Hold"
        ]),

        get_field(data, [
            "Change in DII Holding",
            "Chg in DII Hold"
        ]),

        get_field(data, [
            "Change in Promoter Holding",
            "Change in Prom Hold"
        ]),


        # PLEDGE
        get_field(data, [
            "Pledged Percentage",
            "Pledged %"
        ]),


        # RETURNS
        get_field(data, [
            "Return over 3 years"
        ]),

        get_field(data, [
            "Return over 5 years"
        ]),


        # WORKING CAPITAL
        get_field(data, [
            "Debtor Days"
        ])

    ]


    return row


# =====================================================
# DEBUG COLUMN COUNT
# =====================================================

print(
    "FIELD MAPPING ENGINE READY"
)

print(
    "TOTAL OUTPUT COLUMNS :",
    len(create_fundamental_row({}))
)


# =====================================================
# PART 3 COMPLETED
# =====================================================

print("\n" + "=" * 60)

print(
    "PART 3 LOADED SUCCESSFULLY"
)

print(
    "SMART FUNDAMENTAL MAPPING READY"
)

print("=" * 60)




# =====================================================
# PART 4 / 5
# MAIN MULTIBAGGER SCANNER ENGINE
# =====================================================


def update_fundamentals():

    print("\n" + "=" * 70)
    print("MULTIBAGGER FUNDAMENTAL SCANNER V3 STARTED")
    print("=" * 70)


    # =================================================
    # READ SYMBOLS FROM COLUMN B
    # =================================================

    symbols = sheet.col_values(2)[1:]


    symbols = [
        str(x).strip()
        for x in symbols
        if str(x).strip()
    ]


    total = len(symbols)


    print(
        f"TOTAL STOCKS FOUND : {total}"
    )


    # =================================================
    # WRITE HEADERS
    # New gspread format
    # =================================================

    try:

        sheet.update(
            range_name="J1",
            values=[HEADERS]
        )

        print(
            "HEADERS UPDATED SUCCESSFULLY"
        )


    except Exception as error:

        print(
            "HEADER UPDATE ERROR :",
            error
        )


    # =================================================
    # OUTPUT STORAGE
    # =================================================

    output = []


    # =================================================
    # START STOCK SCANNING
    # =================================================

    for count, symbol in enumerate(
        symbols,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"[{count}/{total}] SCANNING : {symbol}"
        )


        try:

            # -----------------------------------------
            # Download Screener Page
            # -----------------------------------------

            soup = fetch_screener_page(
                symbol
            )


            if soup:


                # -------------------------------------
                # Extract Complete Fundamental Data
                # -------------------------------------

                raw_data = extract_complete_data(
                    soup
                )


                # Debug Mode
                # print_all_found_data(raw_data)


                # -------------------------------------
                # Convert Data Into Final Row
                # -------------------------------------

                final_row = create_fundamental_row(
                    raw_data
                )


                output.append(
                    final_row
                )


                SUCCESS_SYMBOLS.append(
                    symbol
                )


                print(
                    f"{symbol} : SUCCESS"
                )


            else:

                error_row = (
                    ["ERROR"]
                    +
                    ["-"] *
                    (len(HEADERS) - 1)
                )


                output.append(
                    error_row
                )


                print(
                    f"{symbol} : NO DATA FOUND"
                )


        except Exception as error:


            print(
                f"{symbol} : ERROR ->",
                error
            )


            error_row = (
                ["ERROR"]
                +
                ["-"] *
                (len(HEADERS)-1)
            )


            output.append(
                error_row
            )


            if symbol not in FAILED_SYMBOLS:

                FAILED_SYMBOLS.append(
                    symbol
                )


        # =================================================
        # Anti Blocking Delay
        # =================================================

        wait_between_stocks(
            count
        )


    # =====================================================
    # GOOGLE SHEET UPDATE
    # =====================================================


    print("\n" + "=" * 70)
    print("WRITING DATA TO GOOGLE SHEET")
    print("=" * 70)


    try:


        # ---------------------------------------------
        # Clear Previous Data
        # ---------------------------------------------

        sheet.batch_clear(
            [
                "J2:AZ10000"
            ]
        )


        # ---------------------------------------------
        # Upload All Data In Single API Call
        # ---------------------------------------------

        if output:

            sheet.update(
                range_name="J2",
                values=output
            )


            print(
                "GOOGLE SHEET UPDATED SUCCESSFULLY"
            )


        else:

            print(
                "NO DATA AVAILABLE FOR UPDATE"
            )


    except Exception as error:


        print(
            "GOOGLE UPDATE FAILED :",
            error
        )


    # =====================================================
    # FINAL REPORT
    # =====================================================


    print("\n" + "=" * 70)
    print("SCANNING COMPLETED")
    print("=" * 70)


    failed_unique = list(
        set(FAILED_SYMBOLS)
    )


    success_count = len(
        SUCCESS_SYMBOLS
    )


    failed_count = len(
        failed_unique
    )


    print(
        f"TOTAL STOCKS     : {total}"
    )

    print(
        f"SUCCESSFUL       : {success_count}"
    )

    print(
        f"FAILED           : {failed_count}"
    )


    # ---------------------------------------------
    # Failed Stock List
    # ---------------------------------------------

    if failed_unique:


        print(
            "\nFAILED STOCK LIST"
        )


        for item in failed_unique:


            print(
                " -",
                item
            )


    # ---------------------------------------------
    # Success Stock List
    # ---------------------------------------------

    print(
        "\nMULTIBAGGER SCANNER V3 FINISHED"
    )


# =====================================================
# PART 4 COMPLETED
# =====================================================


print("\n" + "=" * 70)

print(
    "PART 4 LOADED SUCCESSFULLY"
)

print(
    "MAIN SCANNER ENGINE READY"
)

print("=" * 70)



# =====================================================
# PART 5 / 5
# ADVANCED DATA RECOVERY MODULE
# =====================================================


def deep_data_recovery(data):

    """
    Agar kisi field ka naam alag format me aaye
    to usko standard field me convert karega.
    """

    recovery_map = {


        # Debt
        "Total Borrowings": "Debt",
        "Borrowing": "Debt",
        "Gross Debt": "Debt",


        # Sales
        "Revenue From Operations": "Sales",
        "Net Sales": "Sales",
        "Operating Revenue": "Sales",


        # Profit
        "Net Profit": "Profit After Tax",
        "PAT": "Profit After Tax",
        "Profit": "Profit After Tax",


        # Growth
        "Revenue Growth": "Sales Growth",
        "Sales CAGR": "Sales CAGR 3 Years",
        "PAT Growth": "Profit Growth",


        # Ratios
        "P/BV": "Price to Book Value",
        "P/B Ratio": "Price to Book Value",
        "EV EBITDA": "EV/EBITDA",
        "Industry P/E": "Industry PE",


        # Shareholding
        "Promoters Holding": "Promoter Holding",
        "FII Holding %": "FII Holding",
        "DII Holding %": "DII Holding",


        # Holding Change
        "FII Change": "Change in FII Holding",
        "DII Change": "Change in DII Holding",
        "Promoter Change":
            "Change in Promoter Holding",


        # CAGR & Returns
        "3Y Sales CAGR":
            "Sales CAGR 3 Years",

        "3Y Profit CAGR":
            "Profit CAGR 3 Years",

        "5Y Profit CAGR":
            "Profit CAGR 5 Years",

        "3Y Return":
            "Return over 3 years",

        "5Y Return":
            "Return over 5 years",


        # Others
        "Interest Cover":
            "Interest Coverage",

        "Pledged Shares":
            "Pledged Percentage"

    }


    for old_key, new_key in recovery_map.items():

        if (
            old_key in data
            and new_key not in data
        ):

            data[new_key] = data[old_key]


    return data



# =====================================================
# UPGRADE EXISTING EXTRACTOR
# =====================================================

old_extract_complete_data = extract_complete_data


def extract_complete_data(soup):

    """
    Original extraction +
    Deep recovery engine
    """

    data = old_extract_complete_data(
        soup
    )


    data = deep_data_recovery(
        data
    )


    return data


print("=" * 70)
print(
    "ADVANCED DATA RECOVERY MODULE LOADED"
)
print("=" * 70)



# =====================================================
# FINAL PROGRAM START POINT
# =====================================================


if __name__ == "__main__":


    start_time = time.time()


    print("\n" + "=" * 70)

    print(
        "MULTIBAGGER FUNDAMENTAL SCANNER V3 STARTING"
    )

    print("=" * 70)


    try:

        update_fundamentals()


    except Exception as error:


        print(
            "FATAL ERROR OCCURRED:"
        )

        print(error)


    finally:


        end_time = time.time()


        total_minutes = (
            end_time -
            start_time
        ) / 60


        print("\n" + "=" * 70)

        print(
            "MULTIBAGGER SCANNER FINISHED"
        )


        print(
            f"TOTAL EXECUTION TIME : "
            f"{total_minutes:.2f} MINUTES"
        )


        print("=" * 70)


# =====================================================
# V3.0 COMPLETE
# =====================================================