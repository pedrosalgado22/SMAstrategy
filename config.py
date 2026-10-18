# Settings for the dashboard.
# To add a stock or index:
#   1. add it to one of the groups below (key -> Yahoo Finance ticker)
#   2. add the same key to OPTIMAL_N and BEAT_DCA_PCT (paste the dictionaries your notebook prints)
#   3. optionally give it a nicer name in DISPLAY_NAMES (without one, the key is shown on the page)

# One dictionary per section of the page: key -> its Yahoo Finance ticker
GROUPS = {
    "Indexes": {
        "sp500": "^GSPC",
    },
    "Individual stocks": {
        "asml": "ASML",
    },
}

# key -> the optimal SMA length (the "averaged best sma" from the notebook)
OPTIMAL_N = {
    "sp500": 10,   # example value, replace it with your own result
    "asml": 50,    # example value, replace it with your own result
}

# key -> % of the SMA lengths from 2 to 200 that beat DCA (the "beat_pct" from the notebook)
BEAT_DCA_PCT = {
    "sp500": 5.5,   # example value, replace it with your own result
    "asml": 12.0,   # example value, replace it with your own result
}

# key -> the name shown on the page
DISPLAY_NAMES = {
    "sp500": "S&P 500",
    "asml": "ASML",
}

BAND = 5          # the chart also shows the SMA of (n - BAND) and (n + BAND)
SHOW_DAYS = 252   # trading days shown on the chart (about 1 year)