from pathlib import Path
import yfinance as yf

original_data_path = Path("/home/pedrosalgado22/Documents/Github Repositories/SMAstrategy/data/raw")
original_data_path.mkdir(parents=True, exist_ok=True)

companies = {
    # hindsight winners
    "microsoft": "MSFT",
    "apple": "AAPL",
    "amazon": "AMZN",
    "nvidia": "NVDA",
    "alphabet": "GOOGL",
    "meta": "META",
    "broadcom": "AVGO",
    "tesla": "TSLA",
    "netflix": "NFLX",
    "visa": "V",
    "mastercard": "MA",
    # long-time US giants
    "exxon": "XOM",
    "ibm": "IBM",
    "ge": "GE",
    "coca_cola": "KO",
    "jnj": "JNJ",
    "pg": "PG",
    "walmart": "WMT",
    "jpmorgan": "JPM",
    "berkshire": "BRK-B",
    "eli_lilly": "LLY",
    "costco": "COST",
    "oracle": "ORCL",
    # fell hard but still trade
    "citigroup": "C",
    "aig": "AIG",
    "intel": "INTC",
    "cisco": "CSCO",
    "boeing": "BA",
    "nokia": "NOK",
    # based outside the US
    "nestle": "NESN.SW",
    "bp": "BP.L",
    "siemens": "SIE.DE",
    "toyota": "TM",
    "tsmc": "TSM",
    "tencent": "0700.HK",
    "samsung": "005930.KS",
    "alibaba": "BABA",
    "asml": "ASML",
    "aramco": "2222.SR",
}

for name, ticker in companies.items():
    df = yf.download(ticker, start="1950-01-01", auto_adjust=True, progress=False)  # auto_adjust=True: Close already includes splits and dividends

    if df.empty:  # Yahoo returned nothing for this ticker
        print(name, ticker, "// NO DATA")
        continue

    df.columns = df.columns.get_level_values(0)
    df.to_csv(original_data_path / f"{name}_raw.csv")

    gaps = df.index.to_series().diff().dt.days

    print(name, df.index.min().date(), df.index.max().date(), len(df),
          "// duplicates:", df.index.duplicated().sum(),
          "// NaN cells:", df.isna().sum().sum(),
          "// longest gap (in days):", gaps.max())