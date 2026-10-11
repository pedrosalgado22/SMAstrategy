# SMAstrategy

Does buying when the market touches its moving average (SMA) beat buying every week (DCA)?

A data science / analysis project on major stock indices over ~40 years. It is **not** price prediction. It studies what happens when people buy at the SMA (50, 100 or 200 days).

---

## 1. Question

With identical contributions, does deploying cash only when the index is at or below its SMA end with more wealth than DCA?

- Each index is analysed **alone**, against its own DCA. Indices are not compared with each other.
- Earlier definition of "beat the market": outperform the S&P 500.
- Only **buying** is tested. No selling.
- Untested prior from the literature (e.g. Faber 2007): trend filters mostly cut drawdown and keep returns similar. They may not raise returns in strong bull markets.

---

## 2. The experiment: 4 scenarios per index

| Scenario | Rule |
|---|---|
| DCA | Buys with the cash as soon as it arrives |
| SMA50 | Holds cash until `close <= SMA50`, then buys with all of it |
| SMA100 | Same, with SMA100 |
| SMA200 | Same, with SMA200 |

All four run over the same period. They differ only in the buy rule.

**One-sentence version:** if money is available and `close <= SMA`, buy with all the available money.

### Rules

- **Payments:** 250 units arrive every Monday (+7 days), for all four scenarios.
- **First payment:** the first Monday on or after the start day.
- **Holiday Monday:** the payment still arrives. The purchase happens on the next trading day. That payment misses one day of interest (tiny simplification).
- **Buy condition:** checked every trading day, not only on Mondays.
- **Signal:** uses the **previous trading day's** `Close` and SMA. Today's close is only the purchase price (no look-ahead).
- **No SMA yet:** if the previous day's SMA is missing, there is no signal that day.
- **Buy size:** the whole pile of cash.
- **Fractional units:** allowed.
- **Costs and taxes:** none.
- **Inflation:** ignored for now.
- **Start day:** the first row on or after 1986-01-01 with SMA200 available. That means Jan 1986 for indices with enough older history. Others wait for a buffer of the first 200 `Close` rows. All four scenarios of an index share the same start.
- **End day:** each index's own last close.
- **Rule type:** `close <= SMA`, not a cross event.

### Money model

- **Interest:** uninvested cash earns 2% a year, compounded over the calendar days since the previous row: `cash *= 1.02 ** (days / 365)`.
- **Dividends:** the indices are treated as accumulating. Units grow by a yearly dividend yield in the same step: `units *= (1 + yield) ** (days / 365)`.
- **Dividend yields:** one constant per index, set manually. These are placeholders.

| Index | Placeholder yield |
|---|---|
| sp500 | 2% |
| nasdaq_comp | 1% |
| nasdaq100 | 1% |
| ftse100 | 4% |
| nikkei | 1% |
| dax | 0% (Yahoo's DAX is already a total-return index) |
| cac40 | 3% |
| hang_seng | 3% |
| shanghai | 2% |

A constant yield is crude. Real yields moved a lot over 40 years (S&P 500: roughly 3%+ in the late 1980s, about 1.5% recently). It can favour whichever strategy holds the most units for the longest, probably DCA.

### Daily loop (same function for all four)

For each trading day from the start to the end:

1. Add interest to cash and dividends to units, for the days since the previous row.
2. Add any payments due on or before today.
3. Buy if cash > 0 and (DCA, or yesterday's close <= yesterday's SMA).
4. After the last row, compute the metrics.

### Output metrics (per index and scenario)

`start_date`, `end_date`, `total_invested`, `final_value` (units x last close + leftover cash), `total_return_pct` (final / invested - 1), `units`, `avg_price` (money spent on purchases / units purchased, dividend units excluded), `leftover_cash`, `n_buys`.

- `avg_price` is `None` if a strategy never buys.
- `total_invested` must be identical across the four scenarios of an index.

---

## 3. Indices and data

Source: Yahoo Finance via `yfinance` (unofficial, can break). Stooq is a backup option.

| Index | Ticker | First date | Last date | Rows | Longest gap (days) |
|---|---|---|---|---|---|
| sp500 | ^GSPC | 1950-01-03 | 2026-10-07 | 19313 | 7 |
| nasdaq_comp | ^IXIC | 1971-02-05 | 2026-10-07 | 14035 | 7 |
| nasdaq100 | ^NDX | 1985-10-01 | 2026-10-07 | 10334 | 7 |
| ftse100 | ^FTSE | 1984-01-03 | 2026-10-07 | 10803 | 5 |
| nikkei | ^N225 | 1965-01-05 | 2026-10-06 | 15180 | 11 |
| dax | ^GDAXI | 1987-12-30 | 2026-10-07 | 9805 | 6 |
| cac40 | ^FCHI | 1990-03-01 | 2026-10-07 | 9297 | 6 |
| hang_seng | ^HSI | 1986-12-31 | 2026-10-06 | 9813 | 7 |
| shanghai | 000001.SS | 1997-07-02 | 2026-09-30 | 7087 | 20 |

### Data checks done

- No duplicate dates and no NaN in any index.
- Gaps have real-world causes (inferred from size): US 7 days is the post-9/11 closure, Nikkei 11 days is a Japanese holiday stretch.
- **Open item:** Shanghai's 20-day gap looks too long for holidays. Find it with `gaps.nlargest(5)`. Gaps in late Jan/Feb or early Oct are holidays. Gaps elsewhere may be missing data.
- Shanghai ends 2026-09-30, probably the National Day holiday (unverified).
- The columns are `Close, High, Low, Open, Volume`. Volume is 0 for these indices.
- Early DAX rows have `Open = High = Low = Close`. Only closes were recorded then, so only `Close` is used.

### Start dates (estimates; the code computes the real ones)

- Jan 1986 (first trading day Jan 2): sp500, nasdaq_comp, ftse100, nikkei.
- About July 1986: nasdaq100 (starts Oct 1985, too short for SMA200 in Jan 1986).
- Others, 200 rows after their first data point: hang_seng (about Oct 1987), dax (about late 1988), cac40 (about late 1990), shanghai (about mid-1998).

### Notes on the data

- All indices except the DAX are **price** indices. The DAX is a **performance** (total return) index. This does not matter for stand-alone analysis. It would matter only when comparing against an external benchmark (cash, S&P 500).
- Price-only data would slightly favour the timed strategies (cash misses dividends). The dividend model fixes that.

---

## 4. Data we cannot easily get (free)

### All World and Emerging Markets

- MSCI ACWI and EM launched at the end of 1987, MSCI World in 1969. The history is licensed, so there is no ticker-level fix.
- Yahoo's MSCI World series appears to cover only about 2012-2026 (one aggregator, unconfirmed).
- MSCI's site has an end-of-day data search. Free download depth is unconfirmed.
- Practical route: ETFs with shorter windows, labelled as short-window. VT/ACWI start about 2008, EEM about 2003, VWO about 2005 (unverified). Check each start date.
- Optional long-history EM stand-in: country indices (Brazil, India, Korea, Taiwan, Mexico, Shanghai). It is cap-unweighted with mixed currencies, so label it clearly.
- China has two reasonable indices (Shanghai mainland-only, Hang Seng Hong Kong-listed). Both are included.

### FirstRate Data (paid vendor, evaluated, not bought)

- Stocks start Jan 2000. 16,314 tickers, over 7,000 delisted, including former S&P 500, Nasdaq-100, Dow and Russell 3000 members.
- Adjusted for splits and dividends. Intraday-focused, with daily bars. Only a 2-week free sample per ticker. No price on the page.
- US index bars only from 2005, international from 2007, so it is too short for the indices.
- No market-cap rankings.
- Check before paying: whether its daily close includes out-of-hours trades, and how delisted tickers are named.
- Plan: try Yahoo first, measure coverage, then buy only the missing tickers (per-ticker purchase appears to be offered; pricing and licensing unknown).

### Individual companies (parked for now)

Goal: the biggest companies over the longest history (first "top 25 in the world", settling for the 50 biggest in the S&P 500 or All World, then 25 every 5 years over 30 years).

- **Survivorship bias:** today's biggest companies are today's winners. Evaluate each cohort **only forward** from its selection date. Use earlier history only to warm up the SMA.
- The bias tilts toward DCA: strong uptrenders stay above their SMA and the timed buyer sits in cash.
- Yahoo lacks delisted and merged companies.
- **Ticker reuse trap:** Yahoo's "T" is today's AT&T (the former SBC), so its pre-2005 history is not the original AT&T's.
- The 1989 global top 20 was mostly Japanese, and several of those banks later merged into Mizuho, so there are no free prices. A global top 25 is not achievable free beyond roughly the 2000s.
- Free lists: finhacker.cz (top 20 US S&P 500 by market cap per year, 1989-2026, a blog, so cross-check it), CNBC snapshots (1989, 1999, 2009, 2014), Visual Capitalist (top 10 every 5 years from 1999, plus a current top 25), a free GitHub list of S&P 500 membership from 1996 (no market caps).
- **Proposed design:** US top 20 per year from 1989. Cohorts at 1989, 1994, 1999, 2004, 2009, 2014, 2019, each tracked for 5 years. Report a **coverage rate** per cohort (companies with continuous history / 20). Require at least 10 years of history per stock.
- Report the share of stocks where timed beats DCA and the median difference. The 20 stocks are correlated, so they are not independent tests.

---

## 5. Folder and code conventions

```
SMAstrategy/
  data/raw/         raw CSVs from Yahoo (git-ignored; .gitignore is written manually)
  data/processed/   CSVs with SMA columns
  results/          results.csv
```

- **Names used in code:** `original_data_path`, `processed_data_path`, `SMA_LENGTHS = [50, 100, 200]`, function `sma_calc`, columns `sma_50`, `sma_100`, `sma_200`.
- **SMA:** mean of the last N `Close` rows (trading days), computed on the full file so pre-1986 data warms it up.
- **Style:** elementary code. for loops, function calls, basic tools. Minimal, no extras that were not asked for. Don't reprint unchanged code. Use names actually defined in the notebook. No gitignore code in scripts.
- **Environment:** VS Code. The `.py` file uses the selected Python interpreter, while a notebook uses its own selected kernel. They can differ. Check with `import sys; print(sys.executable)` and set the same venv in both.

### Download script (one loop per index)

Download from Yahoo, flatten the columns (`df.columns.get_level_values(0)`), save the raw CSV, print the check (start, end, rows, duplicates, NaN, longest gap), add the SMA columns, and save the processed CSV.

---

## 6. Notebook plan

| Cell | Content |
|---|---|
| 1 | Parameters: `PAYMENT = 250`, `INTEREST_RATE = 0.02`, `START_DATE`, `DIV_YIELD`, `STRATEGIES` |
| 2 | `simulate(df, sma_col, dividend_yield)`: one strategy on one index. `sma_col=None` means DCA |
| 3 | Test on the S&P 500: run the four strategies and check `total_invested` is equal in all four rows |
| 4 | Loop over all 9 indices x 4 strategies, build the results table, save `results/results.csv` |

Cell 4 loops over the names in `DIV_YIELD`. It needs `processed_data_path` to be a `Path`.

### Testing done (synthetic data only)

- Hand calculation on an 8-row dataset matched exactly for DCA and SMA50.
- An independent calendar-day implementation matched all 36 results (`final_value` within 0.0003%).
- Money conservation (0% interest and dividends: spent + leftover = invested).
- Dividend formula check.
- Blanking the last row's SMA changes nothing (no look-ahead).
- A never-buys strategy crashed with a division by zero, which led to the `avg_price` guard.
- All 36 simulations run in about 2 seconds.
- Tested on Python 3.12 and pandas 3.0.2. **Real Yahoo data has not been run yet.**

---

## 7. Visualization ideas

Rule for every chart: compare against DCA within the same index (the indices differ hugely in scale).

### From `results.csv` only

1. **Heatmap vs DCA:** 9 indices x SMA50/100/200, cell = % difference in `final_value` vs DCA, diverging colors centered on 0.
2. **Cheaper entry vs outcome (scatter):** x = % difference in `avg_price` vs DCA, y = % difference in `final_value` vs DCA, one dot per index x strategy, colored by strategy. Left but below zero means cash drag beat the cheaper entries.
3. **Win count:** how many of the 9 indices each strategy ranks first on `final_value`, or the average rank.
4. **Buying behaviour:** bars of `n_buys`, `leftover_cash` as % of `final_value`, and money per buy (`total_invested / n_buys`).

### Needs daily tracking

These need `simulate` to also record each day's portfolio value, cash and total invested, plus a log of purchase dates and amounts.

5. **Value relative to DCA over time:** 3x3 grid (one panel per index), one line per strategy, flat line at 1.0.
6. **Money multiple over time:** `value / total_invested` for all four strategies, showing time under water.
7. **Cash drag over time:** cash as % of portfolio value per strategy.
8. **Buy timeline (one index, e.g. S&P 500):** price and SMA line, with dots on purchase dates sized by amount, SMA50 vs SMA200.

### Robustness

9. **Different start years:** run from each start year (1986 ... 2006) and show a boxplot of `final_value` vs DCA per strategy. Needs `START_DATE` passed into `simulate`. Takes about a minute.
10. **Sensitivity to assumptions:** for one index, a grid of interest rate (0-5%) x dividend yield (0-4%), colored by SMA200 minus DCA.

Tools: plain `matplotlib` (`imshow` for heatmaps). Suggested start: ideas 1, 2 and 5.

---

## 8. Next steps

1. **Finish the notebook** for DCA and SMA50/100/200: run cells 3 and 4 on the real data, then build the charts one cell at a time.
2. **Single `.py` script:** scraping + SMA computing + final results.
3. **SMA sweep from 1 to 200** (see below).
4. **Company cohorts** (section 4).
5. **All World and EM** via ETFs, with shorter windows.

### SMA sweep (1 to 200)

- Loop `n` over `range(1, 201)` for each index. Each pass computes SMA(n) into one temporary column, calls `simulate` unchanged, and stores a row with `sma_length = n`.
- **`n = 1` is DCA.** SMA(1) is the close, so `close <= SMA` is always true. This was checked on synthetic data and gives an identical result, which makes it a built-in check. `n = 200` reproduces the earlier `sma_200` run.
- All 200 strategies share the start date set by `sma_200`.
- Don't save 200 SMA columns. Compute on the fly.
- Output: 9 x 200 = 1,800 rows. `sma_length` replaces `strategy`. About 13 seconds per index on synthetic data, so about 2 minutes in total.
- Plot `sma_length` on the x-axis against `final_value`, `total_return_pct`, `n_buys` or `leftover_cash`, with `n = 1` as the DCA baseline.
- **Caution:** neighbouring lengths give similar results, so the curve will look smooth. The best `n` of 200 partly reflects luck. Trust the shape and whether it repeats across indices.

---

## 9. Earlier ideas kept for later

- **Event study:** event = close crosses below SMA(n) for n = 50, 100, 200, with events at least 20 trading days apart. Measure forward returns after 1, 3, 6, 12 and 36 months (21, 63, 126, 252 trading days), entering at the next close. Compare with every other day (median and win rate). Possibly also how much further price falls first.
- **ML layer (exploratory):** features at each event (distance below SMA, SMA slope, 1-year return, volatility, drawdown from high). Target is the forward 12-month return. Use time-based walk-forward validation, never random splits. There is little data, so pool assets.
- **Robustness:** sub-periods (1987, 2000-02, 2008, 2020, 2022), block bootstrap, out-of-sample holdout (e.g. the S&P 500's 1950-1988 history), SMA length sensitivity, and counting how many combinations were tried (multiple testing).
- **Other variations:** costs (0, 10, 25 bps), a T-bill series from FRED as the cash rate, USD as base currency with FX from FRED, a common window (about Oct 1988 onward) if a cross-index comparison is ever needed.
- **Original rule families:** (A) trend filter (hold above the SMA, cash below), (B) dip buy, (C) cross-up entry. Selling was dropped, so only buying is tested.

---

## 10. Limitations

- One historical path per index, not independent samples.
- Dividend yields are placeholders and constant. The 2% cash rate is an assumption.
- Free data only. There is survivorship bias in any company list built from today's tickers.
- Price indices (all except the DAX) ignore dividends unless the dividend model is applied.
- Results depend on the start date (hence the start-year robustness idea).
- Real-data results are not available yet. Everything tested so far used synthetic data.
