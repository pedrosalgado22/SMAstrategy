import pandas as pd
from pathlib import Path
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

original_data_path = Path("/home/pedrosalgado22/Documents/Github Repositories/SMAstrategy/data/raw")

processed_data_path = Path("/home/pedrosalgado22/Documents/Github Repositories/SMAstrategy/data/processed")


original_data_path.mkdir(parents=True, exist_ok=True) # exists is if does not exist create else ignore parents is the same for folders above it so in this case data

processed_data_path.mkdir(parents=True, exist_ok=True)


SMA_LENGTHS = [50, 100, 200]

indices = {
    "sp500": "^GSPC",
    "nasdaq_comp": "^IXIC",
    "nasdaq100": "^NDX",
    "ftse100": "^FTSE",
    "nikkei": "^N225",
    "dax": "^GDAXI",
    "cac40": "^FCHI",
    "hang_seng": "^HSI",
    "shanghai": "000001.SS",
}

PAYMENT = 1000
INTEREST_RATE = 0.02
START_DATE = "1986-01-01"

DIV_YIELD = {  # placeholders, adjust manually; dax is 0 because it is already total return
    "sp500": 0.02, "nasdaq_comp": 0.01, "nasdaq100": 0.01, "ftse100": 0.04,
    "nikkei": 0.01, "dax": 0.0, "cac40": 0.03, "hang_seng": 0.03, "shanghai": 0.02,
}

colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
          "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]

def sma_calc(df):
    for length in SMA_LENGTHS:
        df[f"sma_{length}"] = df["Close"].rolling(window=length).mean()
    return df

def simulate(df, sma_col, dividend_yield):
    dates = df.index.tolist()
    closes = df["Close"].tolist()
    smas = df[sma_col].tolist()

    valid = df[(df.index >= START_DATE) & df["sma_200"].notna()]  # first day with sma_200 available
    start = df.index.get_loc(valid.index[0])

    cash = 0
    units = 0
    next_payment = dates[start].replace(day=1)  # payments on the 1st of each month
    if next_payment < dates[start]:
        next_payment += pd.DateOffset(months=1)

    for i in range(start, len(df)):
        days = (dates[i] - dates[i - 1]).days
        cash *= (1 + INTEREST_RATE) ** (days / 365)
        units *= (1 + dividend_yield) ** (days / 365)

        while next_payment <= dates[i]:
            cash += PAYMENT
            next_payment += pd.DateOffset(months=1)

        if cash > 0 and closes[i - 1] <= smas[i - 1]:
            units += cash / closes[i]
            cash = 0

    return units * closes[-1] + cash  # final amount = everything invested + leftover cash

for name, ticker in indices.items():
    df = yf.download(ticker, start="1950-01-01", progress=False) # progress is a progress bar that shows the download progress

    df.columns = df.columns.get_level_values(0)  # df.columns.get_level_values(0) keeps only the first layer, so the columns become plain names basically nested we want the first layer which is the name of the columns
    df.to_csv(original_data_path / f"{name}_raw.csv")

    gaps = df.index.to_series().diff().dt.days # calculates gap . index is date series turns it to list of values diff subtracts previous row and dt days keeps number of days between the two dates

    print(name, df.index.min().date(), df.index.max().date(), len(df),
          "// duplicates:", df.index.duplicated().sum(),
          "// NaN cells:", df.isna().sum().sum(),
          "// longest gap (in days):", gaps.max())

    df = df.dropna(subset=["Close"])  # drops rows with no price (Yahoo can add an empty last row)
    df = sma_calc(df)

    df.to_csv(processed_data_path / f"{name}_processed.csv")

    final_values = []
    for n in range(1, 201):
        df["sma_n"] = df["Close"].rolling(window=n).mean()
        final_values.append(simulate(df, "sma_n", DIV_YIELD[name]))

    group_names = []
    group_means = []
    group_labels = []
    for first in range(1, 200, 20):
        group = final_values[first - 1:first + 19]
        mean = sum(group) / len(group)
        group_names.append(f"{first}-{first + 19}")
        group_means.append(mean)
        group_labels.append(f"{mean / 1000:,.0f}k")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    ax1.plot(range(1, 201), final_values)
    ax1.set_title(f"{name}: final amount by SMA length")
    ax1.set_xlabel("SMA length")
    ax1.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    bars = ax2.bar(group_names, group_means, color=colors)
    ax2.bar_label(bars, labels=group_labels)
    ax2.set_ylim(bottom=min(group_means) * 0.97)
    ax2.set_title(f"{name}: mean final amount per 20 SMA lengths")
    ax2.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

plt.show()
