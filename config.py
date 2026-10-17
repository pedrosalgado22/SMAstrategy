# Settings for the dashboard.
# To add a stock or index: add one line to TICKERS and one line to OPTIMAL_N (same name in both).

# name shown on the page -> its Yahoo Finance ticker
TICKERS = {
    "S&P 500": "^GSPC",
}

# name -> its optimal SMA length (the "averaged best sma" from the notebook)
OPTIMAL_N = {
    "S&P 500": 10,   # example value, replace it with your own result
}

BAND = 5          # the chart also shows the SMA of (n - BAND) and (n + BAND)
SHOW_DAYS = 252   # trading days shown on the chart (about 1 year)