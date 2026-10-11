# SMAstrategy

Does buying when the market touches its moving average (SMA) beat buying on a fixed schedule (DCA)?

A data science / analysis project on major stock indices over ~40 years. It is **not** price prediction. It studies what happens when people buy at the SMA (any length from 1 to 200 days).

**Headline result:** buying at the SMA almost never beat plain DCA. Gaps are small (mostly within about 2%), DCA wins about 80% of the cases, and no SMA length works across indices. Details in section 7.

---

## 1. Question

With identical contributions, does deploying cash only when the index is at or below its SMA end with more wealth than DCA?

- Each index is analysed **alone**, against its own DCA. Indices are not compared with each other.
- Earlier definition of "beat the market": outperform the S&P 500.
- Only **buying** is tested. No selling.
- Untested prior from the literature (e.g. Faber 2007): trend filters mostly cut drawdown and keep returns similar. They may not raise returns in strong bull markets.

---

## 2. Experiment and rules

### Scenarios per index

| Scenario | Rule |
|---|---|
| DCA | Buys with the cash as soon as it arrives |
| SMA(n) | Holds cash until `close <= SMA(n)`, then buys with all of it |

Notebook runs use n = 50, 100, 200 plus DCA (4 scenarios). The sweep uses every n from 1 to 200.

**One-sentence version:** if money is available and `close <= SMA`, buy with all the available money.

### Rules (same for every scenario)

- **Buy condition:** checked every trading day.
- **Signal:** uses the **previous trading day's** `Close` and SMA. Today's close is only the purchase price (no look-ahead).
- **No SMA yet:** if the previous day's SMA is missing, there is no signal that day.
- **Buy size:** the whole pile of cash. Fractional units allowed.
- **Rule type:** `close <= SMA`, not a cross event.
- **Costs, taxes, inflation:** none / ignored.
- **SMA:** mean of the last N `Close` rows (trading days), computed on the full file so pre-1986 data warms it up.
- **Start day:** the first row on or after 1986-01-01 with SMA200 available. Indices with older data start in Jan 1986. Others wait for a buffer of the first 200 `Close` rows. All scenarios of an index share the same start.
- **End day:** each index's last close (all ended 2026-10-09).

### Payment schedules (three runs were made)

| Run | Payment | Per year | Used for |
|---|---|---|---|
| Weekly | 250 every Monday (+7 days) | about 13,045 | Section 7.2 |
| Monthly | 1,087 on the 1st of each month | about 13,044 | Section 7.3 (equal total money to weekly) |
| Monthly | 1,000 on the 1st of each month | 12,000 | The sweep script (percentages are scale-free) |

- **Weekly:** first payment is the first Monday on or after the start. A holiday Monday still pays, and the purchase happens on the next trading day.
- **Monthly:** first payment is the first 1st-of-month on or after the start (a Jan 2 start pays first on Feb 1). A weekend or holiday 1st is paid on the next trading day.
- **Why total invested differs:** 250 per week is more than 1,000 per month, because a year has about 52.2 weeks and 12 months. 1,087 makes the two equal.
- Payments on a non-trading day miss one day of interest (tiny simplification).

### Money model

- **Interest:** uninvested cash earns 2% a year, compounded over the calendar days since the previous row: `cash *= 1.02 ** (days / 365)`.
- **Dividends:** indices are treated as accumulating. Units grow by a yearly dividend yield in the same step: `units *= (1 + yield) ** (days / 365)`.
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

### Daily loop (one function for all scenarios)

For each trading day from the start to the end:

1. Add interest to cash and dividends to units, for the days since the previous row.
2. Add any payments due on or before today.
3. Buy if cash > 0 and yesterday's close <= yesterday's SMA.
4. After the last row, compute the result.

### Final amount

`final amount = units x last Close + leftover cash`

- Units hold everything that was invested (plus reinvested dividends). Leftover cash is money not yet invested, plus its interest.
- So the final amount includes all the money invested plus the leftover cash.
- Verified: with 0% interest and dividends, a flat price gives a final amount equal to total invested, and a rising price (never buys, all stays cash) also equals total invested.

### Output metrics in the notebook results table

`start_date`, `end_date`, `total_invested`, `final_value`, `total_return_pct` (final / invested - 1), `units`, `avg_price` (money spent on purchases / units purchased, dividend units excluded), `leftover_cash`, `n_buys`.

- `avg_price` is `None` if a strategy never buys.
- `total_invested` is identical across the scenarios of an index (check).

### SMA sweep (1 to 200)

- For each index, loop `n` over `range(1, 201)`. Each pass computes SMA(n) into one temporary column and runs the same simulation.
- **`n = 1` is DCA.** SMA(1) is the close, so `close <= SMA` is always true. Checked: identical to the DCA run.
- All 200 strategies share the start date set by `sma_200`.
- SMA(50), SMA(100) and SMA(200) from the sweep match the notebook table (percentages are scale-free).
- Console block prints, per index: DCA final amount, SMA50/100/200 vs DCA, average of n = 2-200, best and worst n, how many of the 199 lengths beat DCA, and 10 group means.
- **Groups for the bars:** 1-20, 21-40, ..., 181-200 (non-overlapping), mean final amount of each group.

---

## 3. Indices and data

Source: Yahoo Finance via `yfinance` (unofficial, can break). Stooq is a backup option.

| Index | Ticker | First date | Last date | Rows | Longest gap (days) |
|---|---|---|---|---|---|
| sp500 | ^GSPC | 1950-01-03 | 2026-10-09 | 19315 | 7 |
| nasdaq_comp | ^IXIC | 1971-02-05 | 2026-10-09 | 14037 | 7 |
| nasdaq100 | ^NDX | 1985-10-01 | 2026-10-09 | 10336 | 7 |
| ftse100 | ^FTSE | 1984-01-03 | 2026-10-09 | 10805 | 5 |
| nikkei | ^N225 | 1965-01-05 | 2026-10-09 | 15183 | 11 |
| dax | ^GDAXI | 1987-12-30 | 2026-10-09 | 9807 | 6 |
| cac40 | ^FCHI | 1990-03-01 | 2026-10-09 | 9299 | 6 |
| hang_seng | ^HSI | 1986-12-31 | 2026-10-09 | 9816 | 7 |
| shanghai | 000001.SS | 1997-07-02 | 2026-10-09 | 7089 | 20 |

### Actual experiment start dates

| Index | Start |
|---|---|
| sp500, nasdaq_comp, ftse100 | 1986-01-02 |
| nikkei | 1986-01-06 |
| nasdaq100 | 1986-07-16 (starts Oct 1985, too short for SMA200 in Jan 1986) |
| hang_seng | 1987-10-26 |
| dax | 1988-10-14 |
| cac40 | 1990-12-17 |
| shanghai | 1998-04-29 |

### Data checks done

- No duplicate dates and no NaN in any index on the final download.
- An earlier download had an empty last Shanghai row (NaN `Close`), which made its `final_value` NaN. Fixed by dropping rows with no `Close` after saving the raw file.
- Gaps have real-world causes (inferred from size): US 7 days is the post-9/11 closure, Nikkei 11 days is a Japanese holiday stretch.
- **Open item:** Shanghai's 20-day gap looks too long for holidays. Find it with `gaps.nlargest(5)`. Gaps in late Jan/Feb or early Oct are holidays. Gaps elsewhere may be missing data.
- Columns are `Close, High, Low, Open, Volume`. Volume is 0 for these indices. Early DAX rows have `Open = High = Low = Close`, so only `Close` is used.

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

## 5. Code, files and conventions

```
SMAstrategy/
  data/raw/         {name}_raw.csv        raw CSVs from Yahoo (git-ignored; .gitignore is written manually)
  data/processed/   {name}_processed.csv  CSVs with sma_50, sma_100, sma_200
```

### Final script: `sma_sweep.py`

One loop per index:

1. Download from Yahoo and flatten the columns (`df.columns.get_level_values(0)`).
2. Save the raw CSV and print the check (start, end, rows, duplicates, NaN, longest gap).
3. Drop rows with no `Close`, add the SMA columns, save the processed CSV.
4. Run 200 simulations (SMA 1 to 200). Print the console block.
5. Draw one figure per index: a line chart of final amount by SMA length (200 points) and a bar chart of the 10 group means (different colors, final amount in thousands above each bar, y-axis not starting at 0).
6. After the loop, `plt.show()` opens all 9 figures.

- `simulate` in the script returns only the final amount (the graphs need nothing else). It needs the `sma_200` column for the start date.
- Runtime about 2 minutes plus downloads (about 98 seconds on synthetic data).

### Notebook (earlier version)

| Cell | Content |
|---|---|
| 1 | Parameters: payment, `INTEREST_RATE = 0.02`, `START_DATE`, `DIV_YIELD`, `STRATEGIES` |
| 2 | `simulate(df, sma_col, dividend_yield, values=None)`: full metrics. `sma_col=None` is DCA. `values` optional list of daily portfolio values for line charts |
| 3 | Test on the S&P 500 (check `total_invested` is equal in all rows) |
| 4 | Loop over 9 indices x 4 strategies, build the results table |

### Style rules

- Elementary code: for loops, function calls, basic tools. Minimal, no extras that were not asked for.
- Don't reprint unchanged code. Use names actually defined in the code. No gitignore code in scripts.
- Names: `original_data_path`, `processed_data_path`, `SMA_LENGTHS = [50, 100, 200]`, function `sma_calc`, columns `sma_{length}`.

### Environment

VS Code. A `.py` file uses the selected Python interpreter, while a notebook uses its own selected kernel. They can differ. Check with `import sys; print(sys.executable)` and set the same venv in both.

---

## 6. Testing done

- Hand calculation on small datasets matched exactly (weekly DCA and SMA50, monthly DCA).
- An independent calendar-day implementation matched all 36 results (`final_value` within 0.0003%).
- Money conservation (0% interest and dividends: spent + leftover = invested). Dividend formula check.
- Blanking the last row's SMA changes nothing (no look-ahead).
- A never-buys strategy crashed with a division by zero, which led to the `avg_price` guard.
- Final script: ran end to end with a stand-in for `yfinance` on synthetic data (9 figures). Its `simulate` matched the tested one exactly. `n = 1` equals DCA. The final amount equals total invested for flat and rising prices.
- The empty-last-row bug (Shanghai NaN) was reproduced and fixed.
- The real-data results below come from the user's own runs.

---

## 7. Results

### 7.1 How to read

- Every gap is **% vs the same index's DCA** (the indices differ hugely in scale).
- `DCA x` is the DCA final amount divided by total invested.
- A positive number means timing beat DCA.

### 7.2 Weekly run (250 every Monday)

| Index | Invested | DCA final | DCA x | SMA50 | SMA100 | SMA200 |
|---|---|---|---|---|---|---|
| sp500 | 531,750 | 9,136,301 | 17.2 | -0.29% | -0.95% | -1.33% |
| nasdaq_comp | 531,750 | 14,958,705 | 28.1 | -0.94% | -1.06% | -0.52% |
| nasdaq100 | 524,750 | 28,981,730 | 55.2 | -0.95% | -1.27% | **+0.74%** |
| ftse100 | 531,750 | 3,990,222 | 7.5 | **+0.05%** | -1.35% | -0.31% |
| nikkei | 531,750 | 2,728,705 | 5.1 | -0.45% | -0.20% | **+0.20%** |
| dax | 495,500 | 2,883,331 | 5.8 | -0.51% | -0.33% | -2.48% |
| cac40 | 467,250 | 1,967,391 | 4.2 | -0.01% | -0.09% | -1.43% |
| hang_seng | 508,250 | 2,807,144 | 5.5 | -0.40% | -1.42% | -2.57% |
| shanghai | 371,000 | 881,918 | 2.4 | -1.47% | -4.38% | -2.83% |

### 7.3 Monthly run (1,087 on the 1st, equal total money)

| Index | Invested | DCA final | DCA x | SMA50 | SMA100 | SMA200 |
|---|---|---|---|---|---|---|
| sp500 | 531,543 | 9,075,036 | 17.1 | -0.21% | -0.87% | -1.37% |
| nasdaq_comp | 531,543 | 14,867,339 | 28.0 | -0.78% | -0.91% | -0.57% |
| nasdaq100 | 525,021 | 28,903,328 | 55.1 | -0.83% | -1.17% | **+0.92%** |
| ftse100 | 531,543 | 3,967,990 | 7.5 | **+0.08%** | -1.21% | -0.09% |
| nikkei | 531,543 | 2,720,627 | 5.1 | -0.34% | -0.20% | **+0.30%** |
| dax | 495,672 | 2,880,885 | 5.8 | -0.48% | -0.25% | -2.56% |
| cac40 | 467,410 | 1,960,657 | 4.2 | **+0.16%** | **+0.19%** | -1.23% |
| hang_seng | 508,716 | 2,812,165 | 5.5 | -0.25% | -1.44% | -2.59% |
| shanghai | 371,754 | 885,524 | 2.4 | -1.53% | -4.55% | -2.90% |

### 7.4 Buying behaviour (weekly run)

Average purchase price vs DCA, and number of buys as % of DCA's number of buys.

| Index | Avg price SMA50 / 100 / 200 | Buys % SMA50 / 100 / 200 |
|---|---|---|
| sp500 | +0.19 / -0.11 / +0.45 | 42 / 34 / 28 |
| nasdaq_comp | +0.88 / +1.16 / -0.07 | 43 / 36 / 30 |
| nasdaq100 | +0.92 / +1.30 / -1.17 | 44 / 36 / 29 |
| ftse100 | -0.18 / +0.75 / +0.23 | 50 / 43 / 37 |
| nikkei | +0.47 / +0.25 / -2.47 | 53 / 48 / 46 |
| dax | +0.67 / +0.62 / +3.25 | 45 / 40 / 33 |
| cac40 | -0.07 / -0.06 / +1.09 | 50 / 45 / 40 |
| hang_seng | +0.34 / +1.08 / +2.05 | 51 / 48 / 43 |
| shanghai | +1.42 / +4.44 / +2.85 | 55 / 53 / 51 |

### 7.5 SMA sweep (monthly 1,000, SMA 1 to 200)

| Index | DCA final | SMA50 | SMA100 | SMA200 | Average n=2-200 | Best n | Worst n | Lengths beating DCA |
|---|---|---|---|---|---|---|---|---|
| sp500 | 8,348,699 | -0.21% | -0.87% | -1.37% | -0.75% | 10 (+0.13%) | 182 (-1.89%) | 11 of 199 |
| nasdaq_comp | 13,677,404 | -0.78% | -0.91% | -0.57% | -0.99% | 2 (-0.23%) | 67 (-1.69%) | 0 |
| nasdaq100 | 26,589,998 | -0.83% | -1.17% | +0.92% | -0.56% | 200 (+0.92%) | 158 (-1.98%) | 38 |
| ftse100 | 3,650,405 | +0.08% | -1.21% | -0.09% | -0.05% | 184 (+1.03%) | 92 (-1.42%) | 96 |
| nikkei | 2,502,876 | -0.34% | -0.20% | +0.30% | -0.15% | 194 (+0.43%) | 38 (-0.73%) | 59 |
| dax | 2,650,308 | -0.48% | -0.25% | -2.56% | -0.90% | 3 (-0.03%) | 180 (-2.74%) | 0 |
| cac40 | 1,803,733 | +0.16% | +0.19% | -1.23% | -0.04% | 94 (+0.45%) | 197 (-1.32%) | 136 |
| hang_seng | 2,587,088 | -0.25% | -1.44% | -2.59% | -1.63% | 31 (-0.07%) | 158 (-3.49%) | 0 |
| shanghai | 814,650 | -1.53% | -4.55% | -2.90% | -2.58% | 4 (-0.05%) | 98 (-4.72%) | 0 |

Group means vs DCA (% of final amount):

| Index | 1-20 | 21-40 | 41-60 | 61-80 | 81-100 | 101-120 | 121-140 | 141-160 | 161-180 | 181-200 |
|---|---|---|---|---|---|---|---|---|---|---|
| sp500 | 0.00 | -0.14 | -0.16 | -0.58 | -0.95 | -1.13 | -0.91 | -0.78 | -1.28 | -1.49 |
| nasdaq_comp | -0.36 | -0.90 | -0.83 | -1.37 | -0.81 | -1.04 | -1.28 | -1.18 | -1.24 | -0.88 |
| nasdaq100 | -0.19 | -0.15 | -0.67 | -0.80 | -1.25 | -0.58 | -0.81 | -1.77 | 0.00 | +0.61 |
| ftse100 | -0.35 | -0.46 | -0.03 | -0.43 | -1.15 | -0.37 | +0.39 | +0.59 | +0.75 | +0.58 |
| nikkei | +0.02 | -0.41 | -0.42 | -0.38 | -0.29 | -0.12 | +0.03 | -0.30 | +0.07 | +0.30 |
| dax | -0.18 | -0.35 | -0.67 | -0.76 | -0.33 | -0.40 | -0.47 | -0.84 | -2.43 | -2.50 |
| cac40 | +0.10 | +0.20 | +0.13 | +0.08 | +0.21 | +0.11 | -0.10 | +0.06 | -0.25 | -0.96 |
| hang_seng | -0.48 | -0.23 | -0.35 | -0.90 | -1.33 | -1.60 | -2.47 | -3.35 | -2.95 | -2.58 |
| shanghai | -0.38 | -0.73 | -1.54 | -1.89 | -2.82 | -4.03 | -3.88 | -3.55 | -3.57 | -3.24 |

### 7.6 What the results show

**DCA wins most of the time**
- Of 27 comparisons (9 indices x SMA50/100/200), timing won 3 weekly and 5 monthly. Mean gap: -0.98% weekly, -0.91% monthly.
- In the sweep, 340 of 1,791 lengths (19%) beat DCA. The mean of the per-index averages is -0.85%.
- In 4 of 9 indices (nasdaq_comp, dax, hang_seng, shanghai) **no** length beat DCA. Their best lengths are n = 2, 3, 4 and 31, which is almost DCA itself.
- The S&P 500 has 11 lengths above DCA. The best is n = 10 at only +0.13%, and the 1-20 group averages +0.00%.

**The gaps are small**
- Almost everything is within about 2%. The best case is +1.03% (FTSE, n = 184), roughly 0.03% a year if spread over 40 years. The worst is -4.72% (Shanghai, n = 98).
- All indices grew 2.4x to 55x their invested money, which dwarfs these gaps.
- Gaps within +-0.3% are noise: 6 of 27 weekly, 8 of 27 monthly. CAC 40 flips sign between weekly (-0.01%, -0.09%) and monthly (+0.16%, +0.19%) for SMA50 and SMA100. The other 25 pairs keep their sign.

**Weekly vs monthly give the same conclusions**
- The DCA money multiple differs by under 0.7% between runs (S&P 17.18x weekly vs 17.07x monthly). Strategy gaps move by at most 0.28 points between runs.

**No best SMA length**
- Averages over the 9 indices: SMA50 loses least (-0.55% weekly, -0.46% monthly), SMA100 loses most (-1.23%, -1.16%), SMA200 is in between (-1.17%, -1.12%).
- Best n by index: 10, 2, 200, 184, 194, 3, 94, 31, 4. Worst n: 182, 67, 158, 92, 38, 180, 197, 158, 98. There is no common length.

**Shape of the curves**
- Lengths 1-20 are close to DCA in every index (-0.48% to +0.10%, mean -0.20%).
- For S&P, Nasdaq composite, DAX, Hang Seng and Shanghai the loss generally widens with length. DAX has a cliff from about -0.8% (141-160) to about -2.4% (161-200). Hang Seng worsens steadily to -3.35%. Shanghai is worst at 101-120 (-4.03%).
- In four indices long lengths do best: Nasdaq-100 (181-200: +0.61%), FTSE (121-200 all positive, best +0.75%), Nikkei (181-200: +0.30%), and CAC 40 (positive up to about 120, best 81-100: +0.21%, then negative).
- Nasdaq-100, Nikkei and FTSE have their best n at 200, 194 and 184, at the edge of the tested range. Lengths above 200 were not tested.

**SMA buyers do not buy cheaper**
- Their average purchase price was above DCA's in 20 of 27 weekly runs and 21 of 27 monthly runs. Weekly means: +0.52% (SMA50), +1.05% (SMA100), +0.69% (SMA200).
- The gap in average price and the gap in final amount are strongly linked (correlation -0.92 in both runs).
- Every win had an average price at least 0.18% lower than DCA's. But a lower price does not guarantee a win (monthly S&P SMA100: price -0.18%, final -0.87%).
- Biggest price penalties: Shanghai (+1.4%, +4.4%, +2.9%) and DAX SMA200 (+3.25%).

**SMA buyers buy less often, in bigger lumps**
- Buys are 28-55% of DCA's weekly and 36-73% monthly. Means for SMA50/100/200: 48/43/37% weekly, 69/57/46% monthly. A longer SMA means fewer buys.

**Leftover cash is small, but shows where markets are**
- At most 0.07% of the final amount, except Nikkei SMA200 (0.63-0.65%), about 1.3 years of payments with no buy signal.
- S&P (SMA100 and SMA200) and both Nasdaqs (SMA200) hold about 26 weeks (6 months) of payments. SMA50 for all three, and SMA100 for both Nasdaqs, hold about 3 weeks (1 month). Identical leftover amounts across these indices mean they last bought on the same days. These markets were above their long SMAs at the end of the data.

**Sweep matches the notebook**
- SMA50/100/200 values in the sweep equal the monthly table (for example Nasdaq-100 SMA200 +0.92%).

**Shanghai is the weakest case for timing**
- SMA50, SMA100 and SMA200 each lose between 1.5% and 4.6%, and Shanghai has the lowest DCA multiple (2.4x).

### 7.7 Possible explanations (untested)

- **Waiting costs market returns.** Idle cash earns 2%, while the index earns more. The cost grows with SMA length because cash waits longer.
- **Dips are not cheap in rising markets.** A fall to a long SMA can still sit above where DCA bought months earlier, which explains the higher average prices.
- **Timing may help in long sideways or falling phases** (for example Nikkei after 1990, FTSE and CAC after 2000, Nasdaq-100 after 2000). This is untested, and Shanghai is a counter-example.
- **Assumptions matter most for FTSE (4% yield), CAC 40 and Hang Seng (3% yield).** Cash earns no dividends here, so a higher placeholder yield penalizes timing more.
- Hang Seng starts 1987-10-26, which is from memory the day it reopened after the 1987 crash, so its first purchases happen at crash prices.

### 7.8 Caveats on the results

- One historical path per index, with different start dates (1986 to 1998).
- Dividend yields are placeholders, and the 2% cash rate is an assumption. Neither was varied.
- 199 lengths are tested per index, so the best n partly reflects luck. No significance tests were run.
- Price indices (all except DAX) ignore dividends except through the placeholder model.
- Shanghai's 20-day data gap is unresolved.

---

## 8. Visualizations

### Done

- Line charts of portfolio value over time per strategy (3x3 grid, and one figure per index from a chosen year).
- Bar chart of final amount per strategy per index (thousands above bars, y-axis not starting at 0, so read the heights, not the proportions).
- Sweep figures: final amount by SMA length plus 10 group-mean bars (one image per index).

### Open ideas

Rule: compare against DCA within the same index.

1. **Heatmap vs DCA:** 9 indices x SMA50/100/200, cell = % difference in final amount, diverging colors centered on 0.
2. **Cheaper entry vs outcome (scatter):** x = % difference in `avg_price`, y = % difference in final amount, one dot per index x strategy.
3. **Win count:** how many indices each strategy ranks first, or the average rank.
4. **Buying behaviour:** bars of `n_buys`, leftover cash as % of final amount, money per buy.
5. **Value relative to DCA over time:** one panel per index, one line per strategy, flat line at 1.0.
6. **Money multiple over time:** value / total invested, showing time under water.
7. **Cash drag over time:** cash as % of portfolio value.
8. **Buy timeline (one index):** price and SMA with dots on purchase dates sized by amount.
9. **Different start years:** boxplot of final amount vs DCA per strategy for start years 1986 ... 2006.
10. **Sensitivity to assumptions:** grid of interest rate (0-5%) x dividend yield (0-4%), colored by SMA200 minus DCA.

---

## 9. Next steps

1. Resolve Shanghai's 20-day gap.
2. Decide what to do with the open questions from the results: lengths above 200, and the dependence on dividend yield and cash interest.
3. Open visualization ideas (section 8).
4. Company cohorts (section 4).
5. All World and EM via ETFs, with shorter windows.

---

## 10. Earlier ideas kept for later

- **Event study:** event = close crosses below SMA(n) for n = 50, 100, 200, with events at least 20 trading days apart. Measure forward returns after 1, 3, 6, 12 and 36 months (21, 63, 126, 252 trading days), entering at the next close. Compare with every other day (median and win rate). Possibly also how much further price falls first.
- **ML layer (exploratory):** features at each event (distance below SMA, SMA slope, 1-year return, volatility, drawdown from high). Target is the forward 12-month return. Use time-based walk-forward validation, never random splits. There is little data, so pool assets.
- **Robustness:** sub-periods (1987, 2000-02, 2008, 2020, 2022), block bootstrap, out-of-sample holdout (e.g. the S&P 500's 1950-1988 history), and counting how many combinations were tried (multiple testing).
- **Other variations:** costs (0, 10, 25 bps), a T-bill series from FRED as the cash rate, USD as base currency with FX from FRED, a common window (about Oct 1988 onward) if a cross-index comparison is ever needed.
- **Original rule families:** (A) trend filter (hold above the SMA, cash below), (B) dip buy, (C) cross-up entry. Selling was dropped, so only buying is tested.

---

## 11. Limitations

- One historical path per index, not independent samples.
- Dividend yields are placeholders and constant. The 2% cash rate is an assumption.
- Free data only. There is survivorship bias in any company list built from today's tickers.
- Price indices (all except the DAX) ignore dividends unless the dividend model is applied.
- Results depend on the start date (hence the start-year robustness idea).
- Differences below about 0.3% are not reliable.
