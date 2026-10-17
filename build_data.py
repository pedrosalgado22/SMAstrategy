# Downloads the prices, calculates the SMAs and saves everything the page needs in docs/data.json.
# Run it with:  python build_data.py

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

from config import TICKERS, OPTIMAL_N, BAND, SHOW_DAYS

output_path = Path(__file__).parent / "docs" / "data.json"
output_path.parent.mkdir(exist_ok=True)   # create the docs folder if it does not exist


def to_list(series):
    # pandas series -> plain list. Empty values (NaN) become None, which is null in JSON.
    result = []
    for value in series:
        if pd.isna(value):
            result.append(None)
        else:
            result.append(round(float(value), 2))
    return result


def download_prices(ticker):
    # 5 years of daily prices: enough for a 200 day SMA plus a year of chart
    df = yf.download(ticker, period="5y", progress=False)
    if df.empty:
        raise ValueError("Yahoo returned no data")
    df.columns = df.columns.get_level_values(0)   # keep only the first column layer, the plain names
    df = df.dropna(subset=["Close"])              # drop days without a price
    return df


def build_entry(name, ticker, n):
    df = download_prices(ticker)

    low = max(1, n - BAND)
    high = n + BAND
    if len(df) < max(200, high):
        raise ValueError("not enough price history")

    # 1. every SMA we need: column name -> length. Calculated on all the rows we downloaded.
    lengths = {"sma_50": 50, "sma_100": 100, "sma_200": 200,
               "sma_n": n, "sma_low": low, "sma_high": high}
    for column, length in lengths.items():
        df[column] = df["Close"].rolling(window=length).mean()

    # 2. is the window open? Open means the close is at or below the optimal SMA (the buy rule of the backtest)
    valid = df.dropna(subset=["sma_n"])               # only days where the optimal SMA exists
    below = (valid["Close"] <= valid["sma_n"]).tolist()   # True on days the close was at or below it
    is_open = below[-1]

    days_in_state = 0                 # how many days in a row it has been open (or closed)
    for value in reversed(below):     # walk back from the latest day
        if value == is_open:
            days_in_state += 1
        else:
            break

    # 3. the latest numbers, shown in the table
    last = df.iloc[-1]
    latest = {
        "date": df.index[-1].strftime("%Y-%m-%d"),
        "close": round(float(last["Close"]), 2),
        "distance_pct": round(float((last["Close"] / last["sma_n"] - 1) * 100), 2),
        "is_open": is_open,
        "days_in_state": days_in_state,
    }
    for column in lengths:
        latest[column] = round(float(last[column]), 2)

    # 4. the last SHOW_DAYS days, drawn on the chart
    shown = df.tail(SHOW_DAYS)
    series = {
        "dates": shown.index.strftime("%Y-%m-%d").tolist(),
        "close": to_list(shown["Close"]),
    }
    for column in lengths:
        series[column] = to_list(shown[column])

    return {"name": name, "ticker": ticker, "n": n, "low_n": low, "high_n": high,
            "latest": latest, "series": series}


entries = []
skipped = []   # tickers that failed, shown as a note on the page
for name, ticker in TICKERS.items():
    if name not in OPTIMAL_N:
        skipped.append(f"{name} (no optimal n in config.py)")
        print("skipped", name, "- no optimal n in config.py")
        continue
    try:
        entries.append(build_entry(name, ticker, OPTIMAL_N[name]))
        print("ok     ", name)
    except Exception as error:   # one bad ticker should not stop the others
        skipped.append(f"{name} ({error})")
        print("skipped", name, "-", error)

if len(entries) == 0:
    raise SystemExit("Nothing was downloaded, so data.json was not changed.")

output = {
    "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "entries": entries,
    "skipped": skipped,
}
with open(output_path, "w") as file:
    json.dump(output, file, allow_nan=False)   # allow_nan=False: crash instead of writing broken JSON
print("saved", output_path)