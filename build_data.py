import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import yfinance as yf
from config import GROUPS, OPTIMAL_N, BEAT_DCA_PCT, DISPLAY_NAMES, BAND, SHOW_DAYS
from zoneinfo import ZoneInfo

output_path = Path(__file__).parent / "docs" / "data.json"   # .parent creates folder in which json goes in
output_path.parent.mkdir(parents=True, exist_ok=True)


def to_list(series):
    result = []
    for value in series:
        if pd.isna(value):
            result.append(None)  # Empty values (NaN) become None, which is null in JSON.
        else:
            result.append(round(float(value), 2))
    return result


def download_prices(ticker, name):
    df = yf.download(ticker, period="10y", progress=False) # yahoo download

    if df.empty:
        print(f"{name} ({ticker}) failed to download")

    if df.empty: raise ValueError("No data returned") # prevent corrupt

    df.columns = df.columns.get_level_values(0)   #  same as for parsing

    if df["Close"].isna().any():
        print(f"{name} ({ticker}) has missing closing prices")

    df = df.dropna(subset=["Close"])              # corrupted days or days that have not finished yet
    return df


def calculate_smas(df, lengths):
    for column, length in lengths.items():
        df[column] = df["Close"].rolling(window=length).mean()  # creates the sma for all distances in the dict


def get_current_state(df):
    below = (df["Close"] <= df["sma_n"]).tolist()   # creates bool series to list
    is_open = below[-1] # check if window open based on last value

    days_in_state = 0
    for value in reversed(below):     # reversed since starting from the below[-1] backwards
        if value == is_open:
            days_in_state += 1  # counts days in same status either closed or open
        else:
            break  # STOP THE COUNT!

    return is_open, days_in_state


def build_latest(df, lengths, is_open, days_in_state):  # recieves values from above
    # numbers table

    last = df.iloc[-1] # last row

    latest = {
        "date": df.index[-1].strftime("%Y-%m-%d"),
        "close": round(float(last["Close"]), 2),
        "distance_pct": round(float((last["Close"] / last["sma_n"] - 1) * 100), 2),
        "is_open": is_open,
        "days_in_state": days_in_state,
    }

    for column in lengths:
        latest[column] = round(float(last[column]), 2)   # gets the sma value based on last day for all distances and places it inside dict
        # loops cant be inside dicts

    return latest


def build_series(df, lengths):
    # chart
    shown = df.tail(SHOW_DAYS) # tail is opposite of head creates subset with days for graph

    series = {
        "dates": shown.index.strftime("%Y-%m-%d").tolist(), # converts index which will be dates to strings to list
        "close": to_list(shown["Close"]),
    }

    for column in lengths:
        series[column] = to_list(shown[column])  # converts all sma values already computed above to a list

    return series


def build_entry(name, ticker, opt_SMA, beat_dca_pct): # putting evberything together
    df = download_prices(ticker, name)

    low = max(1, opt_SMA - BAND)  # creating a band 
    high = opt_SMA + BAND

    if len(df) < 200:
        raise ValueError("not enough price history, at least 200 rows are needed for the SMA calculations. Only include stocks with a 200 market day history.")

    lengths = {
        "sma_50": 50,
        "sma_100": 100,
        "sma_200": 200,
        "sma_n": opt_SMA,
        "sma_low": low,
        "sma_high": high
    }

    calculate_smas(df, lengths)

    is_open, days_in_state = get_current_state(df)
    latest = build_latest(df, lengths, is_open, days_in_state)
    series = build_series(df, lengths)

    return {
        "name": name,
        "ticker": ticker,
        "opt_SMA": opt_SMA,
        "low_n": low,
        "high_n": high,
        "beat_dca_pct": beat_dca_pct,
        "latest": latest,
        "series": series
    }


def build_group():  # divides into indexes and stocks for the dash
    groups = []

    for title, tickers in GROUPS.items(): # for "Indexes", "sp500":"^GSPC",

        entries = []
        skipped = []

        for key, ticker in tickers.items():  # for "sp500": "^GSPC" in ticket dict
            if key in DISPLAY_NAMES:  # if sp500 in the display names dict
                name = DISPLAY_NAMES[key] # name is its corresponding
            else:
                name = key   # name is sp500

            if key not in OPTIMAL_N: # if sp500 does not have an optimal dca attribuited in the dict
                skipped.append(f"{name} no optimal opt_SMA in config.py") # append to corrupted list
                print("skipped", name, " no optimal opt_SMA in config.py") # warn
                continue  # if one stock sma is not avaliable it proceeds to others

            elif key not in BEAT_DCA_PCT:  # same for pct dca
                skipped.append(f"{name} no  BEAT_DCA_PCT in config.py")
                print("skipped", name, " no  BEAT_DCA_PCT in config.py")
                continue  # if one stock sma is not avaliable it proceeds to others

            # checks if dictionaries have the needed data else itll alert that some smas are missing,

            entry = build_entry(name, ticker, OPTIMAL_N[key], BEAT_DCA_PCT[key])
            entries.append(entry)
            print(f"{name} added")

        groups.append({"title": title, "entries": entries})

    return groups


def save_data(groups):
    output = {
        "updated": datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d %H:%M Lisbon/London time"), 
        "groups": groups,
    }

    with open(output_path, "w") as file:
        json.dump(output, file, allow_nan=False)   # crash instead of writing broken JSON

    print("saved", output_path)


groups = build_group()
save_data(groups)