# SMA Strategy

An ETL and analysis project. It fetches daily prices from Yahoo Finance, tests buying at a simple moving average (SMA) against plain monthly investing (DCA) on 12 stock indexes and 39 large companies over up to about 40 years, picks an optimal SMA length for each asset, tests whether the best result is more than luck with White's Reality Check, and publishes the current state as an automatically updated dashboard.

[**Live dashboard**](https://pedrosalgado22.github.io/SMAstrategy/)

<!-- add a screenshot of the dashboard here, for example: ![Dashboard](docs/screenshot.png) -->

---

## Disclaimer

- **This is not financial advice.** Nothing here is a recommendation to buy or sell anything.
- I know I am not discovering gold or predicting the market. Past performance does not influence future performance, and a rule that worked or failed on past data proves nothing about the future.
- This is an ETL project, from fetching Yahoo data to deploying a dashboard, inspired by a trading theme. It is not a financial holy grail. It serves as a reference for how I build a data pipeline end to end.
- The main finding is modest: buying at the SMA usually did not beat plain DCA, and no statistically significant edge was found in any of the 51 assets.

---

## What is an SMA?

The **simple moving average** of length `n` is the average of the last `n` daily closing prices. It is a smoothed price line.

```
SMA(n) on day t = (close of day t + close of day t-1 + ... + close of day t-n+1) / n
```

- A short SMA (like 10) follows the price closely. A long SMA (like 200) moves slowly.
- **DCA** (dollar cost averaging) means investing a fixed amount on a fixed schedule. It is the baseline here.
- **DCA sits at position 1 of the sweep ("SMA 1").** It is coded as an always-buy strategy, the limit of a very short SMA. A literal SMA(1) is the close itself, so a strict "close below SMA" rule would never fire.
- **The strategy:** new money waits as cash. When the previous day's close is below the previous day's SMA(n), all the waiting cash is invested, priced at that close.
- The dashboard watches one length per asset, its optimal SMA (see [Optimal SMA per Asset](#optimal-sma-per-asset)).

---

## Repository Contents

| File | Description |
|---|---|
| `smaparsing_indexes.py` | Fetches the 12 index histories from Yahoo Finance and checks them (duplicates, missing values, gaps) |
| `smaparsing_individualstocks.py` | Same for the 39 companies |
| `smanalysis_50_100_200.ipynb` | DCA vs SMA 50, 100 and 200 on the indexes |
| `smanalysis_50_100_200_ind.ipynb` | Same on the individual companies |
| `smanalysis_simulation.ipynb` | The SMA 1 to 200 sweep on the indexes: results, charts, cross-validated smoothing and White's Reality Check |
| `smanalysis_simulation_ind.ipynb` | Same on the individual companies |
| `config.py` | Dashboard settings: which assets to show, each one's optimal SMA, and the share of lengths that beat DCA |
| `build_data.py` | Downloads fresh prices, recalculates the SMAs and writes `docs/data.json` |
| `data/results/` | Saved full results, one row per asset and strategy: `results_full200.parquet` (indexes) and `results_full200ind.parquet` (companies) |
| `docs/` | The dashboard served by GitHub Pages (`index.html` and `data.json`) |
| `.github/workflows/` | Scheduled GitHub Actions workflow that refreshes the data |
| `requirements.txt` | Python dependencies |
| `LICENSE`, `.gitignore` | License and ignored files |

The raw and processed CSVs (`<name>_processed.csv` for indexes, `<name>_indprocessed.csv` for companies) are created locally by the parsing scripts.

---

## Run It Yourself

1. `pip install -r requirements.txt`. The notebooks also need `matplotlib`, `statsmodels`, `arch` and `pyarrow`.
2. Run `smaparsing_indexes.py` and `smaparsing_individualstocks.py`. They download Yahoo Finance data, run the data checks and save raw and processed CSVs (with the SMA columns).
3. Open the notebooks to rerun the studies. Their folder paths start from your home folder (`Documents/Github Repositories/SMAstrategy`), so adjust them if the repository lives elsewhere.
4. Run `python build_data.py` to build `docs/data.json`. It downloads its own prices and does not use the notebook CSVs.
5. To view the page locally, run `python -m http.server` inside `docs/` and open `http://localhost:8000`. Opening `index.html` directly does not load the data.

---

## Automation

A scheduled GitHub Actions workflow keeps the dashboard current without manual work:

1. It runs `build_data.py` on weekdays at 23:00 UTC, after the main markets have closed. It can also be started by hand from the Actions tab.
2. `build_data.py` downloads 5 years of daily closes per asset and recalculates SMA 50/100/200 and the optimal SMA with its band. It writes `docs/data.json`: for each asset the last close, the optimal SMA and its band, the SMA value, the distance to it, the status, the days in that status, the SMAs, and the chart series (the last 252 trading days).
3. The workflow commits the updated file to this repository (commit message "Update data").
4. GitHub Pages serves `docs/`, and the page reads `data.json` in the browser.

- An asset that fails to download, or has too little history, is skipped and listed in its section as "Could not update". If nothing downloads, `data.json` is left unchanged and the run fails.
- No API keys or secrets are used.

---

## The Study

**Question:** with identical contributions, does investing only when the market is below its SMA end with more money than DCA?

- Each asset is compared only with **its own DCA**, so results are shown as **% vs DCA**. Assets are not compared with each other (different starts, currencies and circumstances).
- Only buying is tested. There is no selling.
- **Sweep:** every length from 1 to 200 is simulated per asset (DCA plus SMA 2 to 200), and the 200 results are compared.

### Rules (same for every strategy)

- **Signal:** the previous trading day's close must be below the previous day's SMA. The purchase is priced at that same close, so the rule assumes a fill at the close that triggered it (see Limitations). If the previous SMA does not exist yet, there is no signal.
- **Rule type:** `close < SMA`, checked every trading day. It is a state, not a cross event.
- **Buy size:** all the waiting cash, with fractional units allowed.
- **Costs, taxes and inflation:** ignored.
- **SMA:** the mean of the last `n` closes, computed on the full history so earlier data warms it up.
- **Start:** the first day on or after 1986-01-01 with 200 closes available. All 200 strategies of an asset share the same start and end.

### Money model (final run)

- **Payments:** 500 per month, paid on the first trading day on or after the 1st. The first payment arrives the month after the start. 500 is a figurative amount (no inflation adjustment); results are shown as %, so the amount does not matter.
- **Interest:** cash earns 3% a year, compounded over the calendar days between prices.
- **Dividends:** assets are treated as accumulating. Units grow by a yearly dividend yield. The yields are one constant per asset, set manually, and they are approximations.
  - Indexes: S&P 500 2%, Nasdaq Composite 1%, Nasdaq 100 1%, FTSE 100 4%, Nikkei 1%, DAX 0% (Yahoo's DAX already includes dividends), CAC 40 3%, Hang Seng 3%, Shanghai 2%, Euro Stoxx 50 3%, Nifty 50 1.3%, Dow Jones 2%.
  - Companies: see the list below.
- **Final amount** = units x last close + leftover cash. It includes all the money invested plus any cash still waiting.

<details>
<summary>Company dividend yields used</summary>

| Group | Yields |
|---|---|
| Hindsight winners | Microsoft 0.8%, Apple 0.5%, Amazon 0%, Nvidia 0.05%, Alphabet 0.03%, Meta 0.05%, Broadcom 0.9%, Tesla 0%, Netflix 0%, Visa 0.65%, Mastercard 0.45% |
| Long-time US giants | Exxon Mobil 3.7%, IBM 2.6%, General Electric 2.5%, Coca-Cola 2.4%, Johnson & Johnson 2.4%, Procter & Gamble 2.7%, Walmart 1.1%, JPMorgan 2.5%, Berkshire Hathaway 0%, Eli Lilly 2.4%, Costco 0.6%, Oracle 0.5% |
| Fell hard but still trade | Citigroup 2.5%, AIG 1.2%, Intel 1.8%, Cisco 0.9%, Boeing 2.2%, Nokia 4.0% |
| Based outside the US | Nestlé 2.7%, BP 6.5%, Siemens 3.5%, Toyota 1.8%, TSMC 2.0%, Tencent 0.4%, Samsung 1.1%, Alibaba 0.15%, ASML 0.7%, Saudi Aramco 4.8% |

</details>

---

## Data

Source: Yahoo Finance through `yfinance` (unofficial, so it can break). The final run ends on 2026-10-20.

| Index | Ticker | First date | Rows | Longest gap (days) | Experiment start |
|---|---|---|---|---|---|
| S&P 500 | ^GSPC | 1950-01-03 | 19318 | 7 | 1986-01-02 |
| Nasdaq Composite | ^IXIC | 1971-02-05 | 14040 | 7 | 1986-01-02 |
| Nasdaq 100 | ^NDX | 1985-10-01 | 10339 | 7 | 1986-07-16 |
| FTSE 100 | ^FTSE | 1984-01-03 | 10809 | 5 | 1986-01-02 |
| Nikkei 225 | ^N225 | 1965-01-05 | 15186 | 11 | 1986-01-06 |
| DAX | ^GDAXI | 1987-12-30 | 9811 | 6 | 1988-10-14 |
| CAC 40 | ^FCHI | 1990-03-01 | 9303 | 6 | 1990-12-17 |
| Hang Seng | ^HSI | 1986-12-31 | 9820 | 7 | 1987-10-26 |
| Shanghai Composite | 000001.SS | 1997-07-02 | 7093 | 20 | 1998-04-29 |
| Euro Stoxx 50 | ^STOXX50E | not listed | not listed | not listed | 2008-01-18 |
| Nifty 50 | ^NSEI | not listed | not listed | not listed | 2008-07-07 |
| Dow Jones | ^DJI | not listed | not listed | not listed | 1992-10-14 |

- The first date, rows and gap figures were recorded for the first nine indexes (from an earlier download). The three later additions (Euro Stoxx 50, Nifty 50, Dow Jones) only have their experiment start listed.
- Indexes without enough history before 1986 wait for 200 closes before starting.
- No duplicate dates and no missing values in the final download. An earlier download had an empty last Shanghai row, which was fixed by dropping rows with no close.
- Gaps have real-world causes (inferred from size): the 7-day US gap is the post-9/11 closure, and the 11-day Nikkei gap is a Japanese holiday stretch. **Open item:** Shanghai's 20-day gap looks too long for holidays and is not resolved.
- All indexes except the DAX are price indexes. The DAX is a total-return index.
- Yahoo's newest rows can change between downloads (an index's last day can appear or disappear), so results are only exactly comparable when they come from the same download.

### Companies (39, in four groups)

| Group | Companies |
|---|---|
| Hindsight winners (11) | Microsoft, Apple, Amazon, Nvidia, Alphabet, Meta, Broadcom, Tesla, Netflix, Visa, Mastercard |
| Long-time US giants (12) | Exxon Mobil, IBM, General Electric, Coca-Cola, Johnson & Johnson, Procter & Gamble, Walmart, JPMorgan, Berkshire Hathaway, Eli Lilly, Costco, Oracle |
| Fell hard but still trade (6) | Citigroup, AIG, Intel, Cisco, Boeing, Nokia |
| Based outside the US (10) | Nestlé, BP, Siemens, Toyota, TSMC, Tencent, Samsung, Alibaba, ASML, Saudi Aramco |

- Companies that started after 1986 are included from their first usable day (for example Saudi Aramco from 2020-09-30).
- Their dividend yields are the constants listed in the money model.
- **Enron and Bear Stearns are not included.** Yahoo drops companies that went bankrupt or were acquired, so the "flops" are giants that crashed but still trade.
- The sample is chosen with hindsight and has survivorship bias, which tilts results toward DCA.

### Data not easily available for free

- **MSCI All World and Emerging Markets:** the index history is licensed. ETFs (VT/ACWI about 2008, EEM about 2003) would give a shorter window.
- **Delisted companies:** a paid vendor such as FirstRate Data (stocks from 2000, over 7,000 delisted tickers) would cover them. It was evaluated and not bought.

---

## Optimal SMA per Asset

The dashboard watches one SMA length per asset. The single best length of the sweep is often one lucky point, so the curve of 200 final amounts is smoothed and the highest smoothed point is taken as the optimal SMA. Three smoothers are compared. `y[n]` is the final amount for length `n` and `ŷ[n]` its smoothed value:

| Smoother | Definition | Settings tried |
|---|---|---|
| Average | `ŷ[n]` = mean of `y[j]` for all `j` with `abs(j - n) <= h` (the window shrinks at the ends) | `h`: 4, 5, 8, 12, 20, 30 |
| Kernel regression | `ŷ[n]` = sum(`K((n-j)/b)` * `y[j]`) / sum(`K((n-j)/b)`), Gaussian `K(u) = exp(-u^2/2)` (statsmodels `KernelReg`) | `b`: 2, 3, 4, 6, 10, 15 |
| LOESS | a straight line fitted to the closest share `f` of the lengths with weights `(1 - (distance/d)^3)^3`, and `ŷ[n]` is the line's value at `n` (statsmodels `lowess`, robustness iterations off) | `f`: 0.05, 0.1, 0.15, 0.2, 0.3, 0.5 |

- All three are local weighted averages of neighbouring lengths. They differ in the weights and in the local fit (flat for the average and kernel, a straight line for LOESS, which is not pulled inward at the ends of the range).
- **Choosing the setting:** per asset and per smoother, by cross-validation. Each length is predicted from the others with itself and its 3 closest lengths on each side hidden (neighbouring lengths give nearly the same result, so leaving them in would reward the smallest window). The score is the mean of `(prediction - y)^2` and the smallest score wins. The smallest average window is 4 because 3 neighbours are hidden.
- Each asset uses only its own curve. Nothing is pooled across assets.
- An optimal length of 1 means DCA, so there is no line to watch. Such assets are normally left off the dashboard.
- The chosen values are stored in `config.py` (`OPTIMAL_N`, and `BEAT_DCA_PCT`, the share of lengths from 2 to 200 that beat DCA). The daily job does not recompute them. Rerun the sweep notebooks to refresh them.

**Limit:** smoothing removes jitter between neighbouring lengths. It cannot tell whether the whole curve is luck, which is what the next section tests.

---

## Significance: White's Reality Check

**Question:** is the best result among the 200 SMA settings (or among bins of them) genuinely unusual, or just the luckiest of the many tried? Picking the winner out of 199 alternatives inflates it, and White's Reality Check (White, 2000) adjusts for that.

- **Inputs:** the day-by-day return of every strategy and of DCA over the same dates. The final amounts alone are not enough, so the simulator was adapted to record a return per day: `r[t] = value[t] / (value[t-1] + payment[t]) - 1`, so new deposits count as capital, not profit.
- **Performance:** `f[k,t] = r[k,t] - r[DCA,t]` for candidate `k`, and the statistic is `V = max over k of sqrt(T) * mean(f[k,t])`.
- **Bootstrap:** days are resampled in random blocks (stationary bootstrap, which keeps the dependence over time; block length left at the `arch` default), 1,000 repetitions, seed 123. In each repetition the best centred result `max over k of sqrt(T) * (mean(f*) - mean(f))` is recorded.
- **p-value:** the share of repetitions at least as large as `V` (the `upper` p-value of `arch`, which is White's). Significant if `p < 0.05`.
- **Candidates:** (1) all SMA 2 to 200 (199 strategies), and bins of (2) 5, (3) 10 and (4) 20 lengths, where a bin's return is the average of the daily returns of its SMA strategies (the first bin has one strategy fewer because DCA is the benchmark). Each test asks whether the best candidate beats DCA by more than luck. DCA is the benchmark and the null hypothesis is that no candidate beats it.

---

## Results

Final run: 500 per month, 3% interest, constant dividend yields, 200 strategies per asset, data to 2026-10-20. Every figure compares an asset with its own DCA.

- **Lengths beating DCA:** the share of the 199 SMA lengths whose final amount is above DCA's.
- **Raw best, Average, Kernel, LOESS:** the best SMA length without and with each smoother (1 is DCA).
- **p:** White's Reality Check p-value for all SMAs and for bins of 5, 10 and 20 lengths. No value is below 0.05, so no test is significant.

### Indexes

| Index | Lengths beating DCA | Raw best | Average | Kernel | LOESS | p (all SMAs) | p (bins 5) | p (bins 10) | p (bins 20) |
|---|---|---|---|---|---|---|---|---|---|
| S&P 500 | 5% | 10 | 12 | 11 | 11 | 0.92 | 0.84 | 0.83 | 0.85 |
| Nasdaq Composite | 0% | 1 | 1 | 1 | 1 | 0.93 | 0.93 | 0.92 | 0.92 |
| Nasdaq 100 | 1% | 30 | 31 | 30 | 30 | 0.70 | 0.68 | 0.69 | 0.73 |
| FTSE 100 | 0% | 1 | 185 | 186 | 1 | 0.94 | 0.89 | 0.91 | 0.89 |
| Nikkei 225 | 24% | 200 | 200 | 200 | 200 | 0.92 | 0.91 | 0.91 | 0.91 |
| DAX | 1% | 109 | 111 | 106 | 106 | 0.74 | 0.72 | 0.71 | 0.73 |
| CAC 40 | 52% | 58 | 62 | 59 | 95 | 0.62 | 0.59 | 0.59 | 0.59 |
| Hang Seng | 1% | 36 | 48 | 36 | 36 | 0.93 | 0.93 | 0.93 | 0.91 |
| Shanghai Composite | 0% | 1 | 2 | 1 | 1 | 0.81 | 0.87 | 0.84 | 0.80 |
| Euro Stoxx 50 | 91% | 169 | 172 | 200 | 200 | 0.34 | 0.43 | 0.49 | 0.50 |
| Nifty 50 | 2% | 5 | 7 | 6 | 7 | 0.95 | 0.94 | 0.95 | 0.92 |
| Dow Jones | 2% | 15 | 13 | 14 | 14 | 0.83 | 0.84 | 0.83 | 0.88 |

<details>
<summary>Companies (39)</summary>

| Company | Lengths beating DCA | Raw best | Average | Kernel | LOESS | p (all SMAs) | p (bins 5) | p (bins 10) | p (bins 20) |
|---|---|---|---|---|---|---|---|---|---|
| Microsoft | 1% | 3 | 1 | 1 | 1 | 0.85 | 0.90 | 0.91 | 0.90 |
| Apple | 0% | 1 | 1 | 1 | 1 | 0.95 | 0.98 | 0.99 | 0.96 |
| Amazon | 25% | 73 | 71 | 72 | 72 | 0.92 | 0.89 | 0.94 | 0.92 |
| Nvidia | 0% | 1 | 1 | 1 | 1 | 0.89 | 0.91 | 0.96 | 0.93 |
| Alphabet | 14% | 69 | 69 | 68 | 69 | 0.66 | 0.64 | 0.64 | 0.63 |
| Meta | 1% | 3 | 1 | 1 | 1 | 0.90 | 0.90 | 0.90 | 0.94 |
| Broadcom | 17% | 29 | 30 | 31 | 31 | 0.92 | 0.91 | 0.94 | 0.93 |
| Tesla | 2% | 2 | 1 | 1 | 1 | 0.65 | 0.65 | 0.62 | 0.61 |
| Netflix | 4% | 4 | 3 | 5 | 5 | 0.85 | 0.87 | 0.88 | 0.86 |
| Visa | 10% | 32 | 31 | 32 | 33 | 0.87 | 0.89 | 0.87 | 0.86 |
| Mastercard | 11% | 58 | 71 | 71 | 72 | 0.92 | 0.87 | 0.87 | 0.85 |
| Exxon Mobil | 9% | 14 | 13 | 14 | 14 | 0.78 | 0.80 | 0.80 | 0.80 |
| IBM | 17% | 111 | 84 | 84 | 85 | 0.60 | 0.53 | 0.49 | 0.56 |
| General Electric | 8% | 8 | 5 | 8 | 7 | 0.86 | 0.87 | 0.87 | 0.89 |
| Coca-Cola | 2% | 6 | 3 | 5 | 1 | 0.78 | 0.82 | 0.83 | 0.88 |
| Johnson & Johnson | 16% | 11 | 7 | 9 | 9 | 0.70 | 0.73 | 0.75 | 0.74 |
| Procter & Gamble | 10% | 16 | 16 | 16 | 16 | 0.80 | 0.80 | 0.80 | 0.76 |
| Walmart | 5% | 181 | 177 | 177 | 178 | 0.88 | 0.88 | 0.89 | 0.90 |
| JPMorgan | 1% | 5 | 1 | 1 | 1 | 0.73 | 0.78 | 0.85 | 0.85 |
| Berkshire Hathaway | 1% | 6 | 2 | 1 | 1 | 0.95 | 0.94 | 0.94 | 0.91 |
| Eli Lilly | 8% | 8 | 12 | 9 | 9 | 0.79 | 0.81 | 0.86 | 0.88 |
| Costco | 50% | 61 | 58 | 59 | 59 | 0.60 | 0.60 | 0.60 | 0.58 |
| Oracle | 0% | 1 | 12 | 1 | 1 | 0.88 | 0.88 | 0.87 | 0.87 |
| Citigroup | 13% | 44 | 43 | 43 | 42 | 0.95 | 0.99 | 0.85 | 0.84 |
| AIG | 38% | 126 | 118 | 121 | 119 | 0.89 | 0.82 | 0.85 | 0.83 |
| Intel | 30% | 171 | 168 | 169 | 169 | 0.71 | 0.55 | 0.54 | 0.51 |
| Cisco | 0% | 1 | 21 | 22 | 22 | 0.93 | 0.95 | 0.95 | 0.93 |
| Boeing | 5% | 11 | 62 | 62 | 62 | 0.76 | 0.81 | 0.78 | 0.74 |
| Nokia | 0% | 1 | 1 | 1 | 1 | 0.89 | 0.87 | 0.88 | 0.89 |
| Nestlé | 6% | 175 | 173 | 173 | 173 | 0.89 | 0.88 | 0.89 | 0.84 |
| BP | 46% | 70 | 67 | 69 | 69 | 0.63 | 0.61 | 0.59 | 0.64 |
| Siemens | 1% | 49 | 46 | 48 | 48 | 0.87 | 0.96 | 0.95 | 0.90 |
| Toyota | 58% | 135 | 134 | 135 | 135 | 0.85 | 0.87 | 0.85 | 0.88 |
| TSMC | 25% | 16 | 16 | 15 | 15 | 0.72 | 0.72 | 0.71 | 0.69 |
| Tencent | 0% | 1 | 1 | 19 | 1 | 0.82 | 0.82 | 0.81 | 0.78 |
| Samsung | 14% | 89 | 100 | 101 | 101 | 0.85 | 0.81 | 0.77 | 0.67 |
| Alibaba | 57% | 200 | 200 | 200 | 200 | 0.81 | 0.79 | 0.69 | 0.60 |
| ASML | 0% | 1 | 2 | 1 | 1 | 0.96 | 0.97 | 0.92 | 0.88 |
| Saudi Aramco | 77% | 116 | 151 | 118 | 118 | 0.21 | 0.21 | 0.23 | 0.21 |

</details>

### What the results show

- **DCA usually wins.** The share of lengths beating DCA is 1.5% for the median index (8 of 12 indexes are at 2% or less) and 8% for the median company (14 of 39 at 2% or less). For the Nasdaq Composite, FTSE 100, Shanghai Composite, Apple, Nvidia, Oracle, Cisco, Nokia, Tencent and ASML, none of the 199 lengths beat DCA.
- **Exceptions.** More than half of the lengths beat DCA for Euro Stoxx 50 (91%), Saudi Aramco (77%), Toyota (58%), Alibaba (57%) and CAC 40 (52%), and Costco is at 50%. Euro Stoxx 50 starts in 2008 and Aramco in 2020. Strongly rising assets (Apple, Nvidia, Microsoft, Meta, Tesla) sit at or near 0%. An untested explanation is that cash waiting at 3% loses to a market that keeps rising.
- **Smoothing barely changes the answer.** Cross-validation chose the smallest setting almost everywhere (average 4, kernel 2, LOESS 0.05), so the smoothed optimum is usually within a few lengths of the raw best. The exceptions are Mastercard (58 to 71-72), IBM (111 to 84-85), Boeing (11 to 62), Cisco (1 to 21-22), Samsung (89 to 100-101), Aramco (116 to 118-151), and Oracle (1 to 12, average only) and Tencent (1 to 19, kernel only). Larger settings were chosen for Alphabet (kernel 3), Visa (average 5), IBM, Coca-Cola and Alibaba (LOESS 0.1), JPMorgan (average 8, kernel 3, LOESS 0.1), AIG (average 8, kernel 4, LOESS 0.15), Intel (average 8, kernel 4, LOESS 0.1), Nikkei (average 5), DAX (average 8, kernel 3) and CAC 40 (kernel 3). The smallest settings are the first values of each list, so smaller ones were not tested.
- **Many optima are 1 (DCA).** The raw best is 1 for 10 assets and all three smoothers give 1 for 8 (Nasdaq Composite, Microsoft, Apple, Nvidia, Meta, Tesla, JPMorgan, Nokia).
- **The smoothers disagree for a few assets.** FTSE 100 (average 185, kernel 186, LOESS 1), CAC 40 (LOESS 95 against 59-62 for the others) and Euro Stoxx 50 (average 172, kernel and LOESS 200).
- **Edge of the range.** The best length is 200 for the Nikkei 225 and Alibaba (and for the Euro Stoxx 50 with two smoothers), so lengths above 200 were not tested.
- **No significant result.** None of the 204 p-values (51 assets x 4 tests) is below 0.05. The lowest are Saudi Aramco (0.21 to 0.23, with data only from 2020) and Euro Stoxx 50 (0.34 to 0.50). All others are 0.49 or higher. The best SMA or bin of every asset is consistent with being the luckiest of the alternatives. The `upper` p-value is conservative when many strategies are poor, as here, so this means no evidence of an edge, not proof that none exists.

### Charts in the notebooks

Final amount by SMA length (best and worst marked), mean final amount per bin of 20 lengths, top 15 SMAs by final amount, % vs DCA by SMA length, % of lengths beating DCA per asset, and a heatmap of bin means vs DCA (color scale of plus or minus 5%).

<details>
<summary>Earlier run (9 indexes, superseded)</summary>

Earlier parameters: monthly payment of 1,000 (and two other payment runs below), 2% interest, rule `close <= SMA` with the purchase at the next day's close, 9 indexes. Kept for reference.

| Run | Payment | Per year | Used for |
|---|---|---|---|
| Weekly | 250 every Monday | about 13,045 | Weekly results |
| Monthly | 1,087 on the 1st | about 13,044 | Monthly results (equal total money to weekly) |
| Monthly | 1,000 on the 1st | 12,000 | The 1 to 200 sweep (percentages are scale-free) |

All results are % vs the same asset's DCA, so a positive number means timing beat DCA. The sweep used monthly payments of 1,000 with data to 2026-10-14/15. The weekly and monthly runs ended 2026-10-09, so a few numbers moved slightly (for example Nikkei SMA200 from +0.30% to +0.35%).

### SMA sweep (1 to 200)

| Index | DCA final amount | SMA50 | SMA100 | SMA200 | Average n=2-200 | Best n | Worst n | Lengths beating DCA |
|---|---|---|---|---|---|---|---|---|
| S&P 500 | 8,251,970 | -0.21% | -0.87% | -1.37% | -0.75% | 10 (+0.13%) | 182 (-1.89%) | 11 of 199 |
| Nasdaq Composite | 13,342,712 | -0.78% | -0.91% | -0.57% | -0.99% | 2 (-0.23%) | 67 (-1.69%) | 0 |
| Nasdaq 100 | 25,790,789 | -0.83% | -1.17% | +0.92% | -0.56% | 200 (+0.92%) | 158 (-1.98%) | 38 |
| FTSE 100 | 3,730,816 | +0.08% | -1.21% | -0.09% | -0.05% | 184 (+1.03%) | 92 (-1.42%) | 96 |
| Nikkei 225 | 2,336,295 | -0.34% | -0.20% | +0.35% | -0.13% | 194 (+0.47%) | 38 (-0.73%) | 68 |
| DAX | 2,666,950 | -0.48% | -0.25% | -2.56% | -0.90% | 3 (-0.03%) | 180 (-2.74%) | 0 |
| CAC 40 | 1,827,613 | +0.16% | +0.19% | -1.23% | -0.04% | 94 (+0.45%) | 197 (-1.32%) | 136 |
| Hang Seng | 2,572,456 | -0.25% | -1.44% | -2.59% | -1.63% | 31 (-0.07%) | 158 (-3.49%) | 0 |
| Shanghai Composite | 792,198 | -1.53% | -4.55% | -2.90% | -2.58% | 4 (-0.05%) | 98 (-4.72%) | 0 |

Mean result of each group of 20 lengths (the bars in the charts):

| Index | 1-20 | 21-40 | 41-60 | 61-80 | 81-100 | 101-120 | 121-140 | 141-160 | 161-180 | 181-200 |
|---|---|---|---|---|---|---|---|---|---|---|
| S&P 500 | 0.00 | -0.14 | -0.16 | -0.58 | -0.95 | -1.13 | -0.91 | -0.78 | -1.28 | -1.49 |
| Nasdaq Composite | -0.36 | -0.90 | -0.83 | -1.37 | -0.81 | -1.04 | -1.28 | -1.18 | -1.24 | -0.88 |
| Nasdaq 100 | -0.19 | -0.15 | -0.67 | -0.79 | -1.25 | -0.58 | -0.81 | -1.77 | 0.00 | +0.61 |
| FTSE 100 | -0.35 | -0.46 | -0.03 | -0.43 | -1.15 | -0.37 | +0.39 | +0.59 | +0.75 | +0.58 |
| Nikkei 225 | +0.03 | -0.41 | -0.41 | -0.37 | -0.29 | -0.12 | +0.05 | -0.26 | +0.12 | +0.34 |
| DAX | -0.18 | -0.35 | -0.67 | -0.76 | -0.33 | -0.40 | -0.47 | -0.84 | -2.43 | -2.50 |
| CAC 40 | +0.10 | +0.20 | +0.13 | +0.08 | +0.21 | +0.11 | -0.10 | +0.06 | -0.25 | -0.96 |
| Hang Seng | -0.48 | -0.23 | -0.35 | -0.90 | -1.33 | -1.60 | -2.47 | -3.35 | -2.95 | -2.58 |
| Shanghai Composite | -0.38 | -0.73 | -1.54 | -1.89 | -2.82 | -4.03 | -3.88 | -3.55 | -3.57 | -3.24 |

### What the results show

- **DCA wins most of the time.** Timing beat DCA in 3 of 27 weekly and 5 of 27 monthly comparisons (9 indexes x SMA 50/100/200). In the sweep, 349 of 1,791 lengths (19%) beat it. For 4 indexes (Nasdaq Composite, DAX, Hang Seng, Shanghai) none did.
- **The gaps are small.** Almost everything is within about 2%. The best is +1.03% (FTSE, n=184, roughly 0.03% a year) and the worst is -4.72% (Shanghai, n=98). Every index grew 2.4x to 55x its invested money, which dwarfs these gaps. Differences within +-0.3% are noise: CAC 40 flips sign between the weekly and monthly runs.
- **There is no best SMA length.** The best n by index is 10, 2, 200, 184, 194, 3, 94, 31 and 4, and some of these are single lucky points, which is why the dashboard uses a smoothed optimum (see Optimal SMA per Asset).
- **Shape of the curves.** Lengths 1-20 sit close to DCA everywhere (-0.48% to +0.10%). The loss grows with length for the S&P 500, Nasdaq Composite, DAX, Hang Seng and Shanghai. Nasdaq 100, FTSE and Nikkei do better at long lengths, and their best n sits at or near the edge of the range (200, 184, 194), so lengths above 200 were not tested. CAC 40 is above DCA up to about 120 and then falls below it.
- **SMA buyers do not buy cheaper.** Their average purchase price was above DCA's in 20 of 27 weekly and 21 of 27 monthly runs. The gap in average price and the gap in final amount are strongly linked (correlation -0.92), and every win had an average price at least 0.18% lower.
- **They buy less often, in bigger lumps:** 28-55% (weekly) and 36-73% (monthly) of DCA's number of buys, fewer for longer SMAs.
- **Leftover cash is small** (at most 0.07% of the final amount, except Nikkei SMA200 at 0.63-0.65%). At the end of the data the S&P 500 (SMA100 and SMA200) and both Nasdaqs (SMA200) had about 6 months of payments waiting, because they were above those SMAs.
- **Weekly and monthly runs agree.** The DCA multiple differs by under 0.7% between them. Shanghai is the weakest case for timing.

**Possible explanations (untested):** idle cash earns 2% while the market earns more, so waiting costs more the longer the SMA. A dip to a long SMA in a rising market can still be above where DCA bought months earlier. Timing may help in long sideways or falling phases (Nikkei after 1990, FTSE and CAC 40 after 2000), but Shanghai is a counter-example.

**Caveats:** one historical path per index with different start dates. Dividend yields are placeholders and the 2% cash rate is an assumption, and neither was varied. With 199 lengths tested per asset, the best length partly reflects luck (the final run tests this with White's Reality Check).

</details>

---

## Dashboard

A static page on GitHub Pages (`docs/index.html`) that reads `docs/data.json`. It has one section per group of assets (Indexes and Individual stocks), each with a table and a chart. It started with the S&P 500 and ASML as test assets.

- **Table:** name, last close, date, optimal SMA (band), SMA value, distance, status, days in status, and SMA 50/100/200.
- **Status:** **Open** means the last close is at or below the optimal SMA (the backtest buys when the close is below it). **Closed** means it is above. It displays the rule's state and is not an instruction to trade. In the backtest the purchase is priced at the close that triggered the signal.
- **Distance:** the last close relative to the optimal SMA, in %.
- **Chart (Plotly):** the close, SMA 50/100/200, the optimal SMA with a shaded band of nearby lengths, and a marker on the last close. Click a row or use the dropdown to switch.
- **Line under the chart:** "For <asset>, X% of the SMA lengths from 2 to 200 beat dollar cost averaging."
- **Layout:** uses up to 1,800 px on wide screens. On narrower screens the table hides its least important columns instead of scrolling (SMA 50/100/200 below 1,400 px, Date and SMA value below 1,100 px, band and days below 900 px). Colors follow the system light or dark mode, and the font is the system font (SF on Apple devices).
- Assets that could not be updated are listed in their section.

### Adding an asset

1. Add `key: ticker` to a group in `GROUPS` in `config.py`, for example `"asml": "ASML"` under "Individual stocks". A new group becomes a new section of the page.
2. Add the same key to `OPTIMAL_N` (optimal SMA length) and `BEAT_DCA_PCT` (% of lengths that beat DCA). The notebooks print both dictionaries.
3. Optionally add a nicer name in `DISPLAY_NAMES`. Without one, the key is shown.

`BAND` (default 5) sets the shaded band of nearby lengths, and `SHOW_DAYS` (default 252) the trading days on the chart.

---

## Testing

- Hand calculations matched exactly. An independent calendar-day implementation matched all 36 results (within 0.0003%). These checks were made on the earlier run.
- Money conservation: with 0% interest and dividends, money spent plus leftover cash equals the money invested.
- Blanking the last SMA value changes nothing, so the signal uses no future SMA data. With the earlier `<=` rule, SMA(1) reproduced DCA exactly. The final strict `<` rule codes DCA as its own always-buy strategy.
- Pricing the purchase at the signal day's close (the final rule) is more favourable than pricing it at the next close: in one test the next-close version gave DCA about 0.2% less final money (S&P 500 total return 1,590.81% against 1,594.27%). Every strategy, DCA included, uses the same pricing, and the effect on the comparison with DCA was not isolated.
- The dashboard build was checked on a synthetic price feed against a separate pandas calculation. The SMAs, distance, status and days in status matched, and an empty download, a short history and an empty last row were skipped or dropped. These were development checks and are not kept as automated tests.
- The dashboard layout was tested at 32 screen widths from 320 to 2560 px with no horizontal scrolling.
- The Reality Check code was adapted from the simulator with an AI assistant. Its p-values were not cross-checked against a second implementation.

---

## Limitations

- One historical path per asset, not independent samples. Results depend on the start date.
- Free data only. Yahoo is unofficial, and any list of companies built from today's tickers has survivorship bias.
- Dividend yields are constant approximations, and the 3% cash rate and the 500 monthly payment are assumptions. None was varied.
- The purchase is priced at the close that triggered the signal, which a real investor cannot know in advance.
- Final amounts and Reality Check returns measure different things (money at the end against average daily return), so the best SMA by final amount is not always the best by return.
- Differences below about 0.3% are not reliable.
- The Reality Check `upper` p-value is conservative when many candidates are poor, so a non-significant result does not prove there is no edge. Several assets have short histories (Euro Stoxx 50 from 2008, Saudi Aramco from 2020).
- The scheduled job runs on GitHub's servers, and Yahoo may block or rate-limit them. A failed run leaves the previous data in place.
- The dashboard's optimal lengths are fixed until the sweep is rerun.

---

## Ideas Not Done

- A more rigorous choice of the optimal length: walk-forward tests, a bootstrap of the optimum, Hansen's SPA (more powerful than the Reality Check when many strategies are poor) and the Model Confidence Set.
- Email alerts when an asset enters or leaves its window (designed and postponed).
- Robustness: start-year sweep, costs, sensitivity to the interest rate and dividend yield, pricing the purchase at the next close.
- An event study of what follows a cross below the SMA, and a small ML layer on those events.
- MSCI All World and Emerging Markets through ETFs, and company cohorts chosen without hindsight.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data fetching and analysis |
| `pandas`, `numpy` | Data processing |
| `yfinance` | Yahoo Finance prices |
| `matplotlib` | Charts in the analysis |
| `statsmodels` | Kernel regression and LOESS smoothing |
| `arch` | White's Reality Check (stationary bootstrap) |
| Parquet (via `pyarrow`) | Saved full results |
| HTML, CSS, JavaScript | The dashboard page (no framework, no server) |
| Plotly.js | Interactive dashboard charts |
| GitHub Actions | Scheduled data refresh |
| GitHub Pages | Dashboard hosting |

---

## License

See `LICENSE`.