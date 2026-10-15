import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf

original_data_path = Path("/home/pedrosalgado22/Documents/Github Repositories/SMAstrategy/data/raw")

processed_data_path = Path("/home/pedrosalgado22/Documents/Github Repositories/SMAstrategy/data/processed")



original_data_path.mkdir(parents=True, exist_ok=True) # exists is if does not exist create else ignore parents is the same for folders above it so in this case data

processed_data_path.mkdir(parents=True, exist_ok=True)


SMA_LENGTHS = list(range(1, 201))  # list for all values



indices = {    # dictionary in Python. Each entry has a key : value:
    "sp500": "^GSPC",
    "nasdaq_comp": "^IXIC",
    "nasdaq100": "^NDX",
    "ftse100": "^FTSE",
    "nikkei": "^N225",
    "dax": "^GDAXI",
    "cac40": "^FCHI",
    "hang_seng": "^HSI",
    "shanghai": "000001.SS",
    "euro_stoxx": "^STOXX50E",
    "nifty": "^NSEI",
    "Dow Jones": "^DJI"
}

def sma_calc(df):
    for length in SMA_LENGTHS:
        df[f"sma_{length}"] = df["Close"].rolling(window=length).mean() # calculates mean of rolling window of length and adds it as a new column to the dataframe
    return df

for name, ticker in indices.items(): # .items() is specifically for dictionaries. gives you key + value
    df = yf.download(ticker, start="1950-01-01", progress=False) # progress is a progress bar that shows the download progress

    df.columns = df.columns.get_level_values(0)  # df.columns.get_level_values(0) keeps only the first layer, so the columns become plain names basically nested we want the first layer which is the name of the columns
    df.to_csv(original_data_path / f"{name}_raw.csv")

    gaps = df.index.to_series().diff().dt.days # calculates gap . index is date series turns it to list of values diff subtracts previous row and dt days keeps number of days between the two dates

    print(name, df.index.min().date(), df.index.max().date(), len(df),
          " - duplicates:", df.index.duplicated().sum(),
          " - NaN cells:", df.isna().sum().sum(),
          " - longest gap (in days):", gaps.max())

    df = sma_calc(df)

    df.to_csv(processed_data_path / f"{name}_processed.csv")