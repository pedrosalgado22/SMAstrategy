# SMA Strategy

An ETL and analysis project. It fetches daily prices from Yahoo Finance, tests buying at a simple moving average (SMA) against plain monthly investing (DCA) on 9 stock indexes and 39 large companies over about 40 years, picks an optimal SMA length for each asset, and publishes the current state as an automatically updated dashboard.

[**Live dashboard**](https://pedrosalgado22.github.io/SMAstrategy/)

<!-- add a screenshot of the dashboard here, for example: ![Dashboard](docs/screenshot.png) -->

---

## Disclaimer

- **This is not financial advice.** Nothing here is a recommendation to buy or sell anything.
- I know I am not discovering gold or predicting the market. Past performance does not influence future performance, and a rule that worked or failed on past data proves nothing about the future.
- This is an ETL project, from fetching Yahoo data to deploying a dashboard, inspired by a trading theme. It is not a financial holy grail. It serves as a reference for how I build a data pipeline end to end.
- The main finding is modest: buying at the SMA usually did not beat plain DCA, and the gaps were small.

---

## What is an SMA?

The **simple moving average** of length `n` is the average of the last `n` daily closing prices. It is a smoothed price line.

```
SMA(n) on day t = (close of day t + close of day t-1 + ... + close of day t-n+1) / n
```

- A short SMA (like 10) follows the price closely. A long SMA (like 200) moves slowly.
- **DCA** (dollar cost averaging) means investing a fixed amount on a fixed schedule. It is the baseline here.
- **SMA(1) is the closing price itself, so SMA(1) is DCA.** DCA is just one of the 200 strategies tested.
- **The strategy:** new money waits as cash. When the previous day's close is at or below the previous day's SMA(n), all the waiting cash is invested.
- The dashboard watches one length per asset, its optimal SMA (see [Optimal SMA per Asset](#optimal-sma-per-asset)).

---

## Repository Contents

| File | Description |
|---|---|
| `smaparsing_indexes.py` | Fetches the 9 index histories from Yahoo Finance and checks them (duplicates, missing values, gaps) |
| `smaparsing_individualstocks.py` | Same for the 39 companies |
| `smanalysis_50_100_200.ipynb` | DCA vs SMA 50, 100 and 200 on the indexes |
| `smanalysis_50_100_200_ind.ipynb` | Same on the individual companies |
| `smanalysis_simulation.ipynb` | The SMA 1 to 200 sweep on the indexes |
| `smanalysis_simulation_ind.ipynb` | Same on the individual companies |
| `config.py` | Dashboard settings: which assets to show, each one's optimal SMA, and the share of lengths that beat DCA |
| `build_data.py` | Downloads fresh prices, recalculates the SMAs and writes `docs/data.json` |
| `data/results/` | Saved analysis results |
| `docs/` | The dashboard served by GitHub Pages (`index.html` and `data.json`) |
| `.github/workflows/` | Scheduled GitHub Actions workflow that refreshes the data |
| `requirements.txt` | Python dependencies |
| `LICENSE`, `.gitignore` | License and ignored files |

The raw and processed CSVs are created locally by the parsing scripts.

---

## Run It Yourself

1. `pip install -r requirements.txt`
2. Run `smaparsing_indexes.py` and `smaparsing_individualstocks.py`. They download Yahoo Finance data, run the data checks and save raw and processed CSVs (with the SMA columns).
3. Open the notebooks to rerun the studies. Their folder paths are absolute to the author's machine, so edit them first.
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

**Question:** with identical contributions, does investing only when the market is at or below its SMA end with more money than DCA?

- Each asset is compared only with **its own DCA**, so results are shown as **% vs DCA**. Assets are not compared with each other.
- Only buying is tested. There is no selling.
- **Sweep:** every length from 1 to 200 is simulated per asset, and the 200 results are compared.

### Rules (same for every strategy)

- **Signal:** the previous trading day's close and SMA decide, and today's close is the purchase price. This avoids using a price to decide on that same price. If the previous SMA does not exist yet, there is no signal.
- **Rule type:** `close <= SMA`, checked every trading day. It is a state, not a cross event.
- **Buy size:** all the waiting cash, with fractional units allowed.
- **Costs, taxes and inflation:** ignored.
- **SMA:** the mean of the last `n` closes, computed on the full history so earlier data warms it up.
- **Start:** the first day on or after 1986-01-01 with 200 closes available. All 200 strategies of an asset share the same start and end.

### Money model

- **Payments:** three runs were made.

| Run | Payment | Per year | Used for |
|---|---|---|---|
| Weekly | 250 every Monday | about 13,045 | Weekly results |
| Monthly | 1,087 on the 1st | about 13,044 | Monthly results (equal total money to weekly) |
| Monthly | 1,000 on the 1st | 12,000 | The 1 to 200 sweep (percentages are scale-free) |

- A weekend or holiday payment is paid on the next trading day. 250 per week is more money than 1,000 per month because a year has about 52.2 weeks and 12 months.
- **Interest:** cash earns 2% a year, compounded over the calendar days between prices.
- **Dividends:** assets are treated as accumulating. Units grow by a yearly dividend yield. The yields are one constant per asset, set manually, and they are placeholders: S&P 500 2%, Nasdaq Composite 1%, Nasdaq 100 1%, FTSE 100 4%, Nikkei 1%, DAX 0% (Yahoo's DAX already includes dividends), CAC 40 3%, Hang Seng 3%, Shanghai 2%.
- **Final amount** = units x last close + leftover cash. It includes all the money invested plus any cash still waiting.

---

## Data

Source: Yahoo Finance through `yfinance` (unofficial, so it can break).

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

- Companies that started after 1986 are included from their first usable day.
- Prices are dividend-adjusted (`auto_adjust=True`), so their dividend yield is 0.
- **Enron and Bear Stearns are not included.** Yahoo drops companies that went bankrupt or were acquired, so the "flops" are giants that crashed but still trade.
- The sample is chosen with hindsight and has survivorship bias, which tilts results toward DCA.

### Data not easily available for free

- **MSCI All World and Emerging Markets:** the index history is licensed. ETFs (VT/ACWI about 2008, EEM about 2003) would give a shorter window.
- **Delisted companies:** a paid vendor such as FirstRate Data (stocks from 2000, over 7,000 delisted tickers) would cover them. It was evaluated and not bought.

---

## Results

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
- **There is no best SMA length.** The best n by index is 10, 2, 200, 184, 194, 3, 94, 31 and 4, and some of these are single lucky points, which is why the dashboard uses a smoothed optimum (see below).
- **Shape of the curves.** Lengths 1-20 sit close to DCA everywhere (-0.48% to +0.10%). The loss grows with length for the S&P 500, Nasdaq Composite, DAX, Hang Seng and Shanghai. Nasdaq 100, FTSE and Nikkei do better at long lengths, and their best n sits at or near the edge of the range (200, 184, 194), so lengths above 200 were not tested. CAC 40 is above DCA up to about 120 and then falls below it.
- **SMA buyers do not buy cheaper.** Their average purchase price was above DCA's in 20 of 27 weekly and 21 of 27 monthly runs. The gap in average price and the gap in final amount are strongly linked (correlation -0.92), and every win had an average price at least 0.18% lower.
- **They buy less often, in bigger lumps:** 28-55% (weekly) and 36-73% (monthly) of DCA's number of buys, fewer for longer SMAs.
- **Leftover cash is small** (at most 0.07% of the final amount, except Nikkei SMA200 at 0.63-0.65%). At the end of the data the S&P 500 (SMA100 and SMA200) and both Nasdaqs (SMA200) had about 6 months of payments waiting, because they were above those SMAs.
- **Weekly and monthly runs agree.** The DCA multiple differs by under 0.7% between them. Shanghai is the weakest case for timing.

**Possible explanations (untested):** idle cash earns 2% while the market earns more, so waiting costs more the longer the SMA. A dip to a long SMA in a rising market can still be above where DCA bought months earlier. Timing may help in long sideways or falling phases (Nikkei after 1990, FTSE and CAC 40 after 2000), but Shanghai is a counter-example.

**Caveats:** one historical path per index with different start dates. Dividend yields are placeholders and the 2% cash rate is an assumption, and neither was varied. With 199 lengths tested per asset, the best length partly reflects luck and no significance tests were run.

---

## Optimal SMA per Asset

The dashboard watches one SMA length per asset. The single best length of the sweep is often one lucky point, so the curve is smoothed first:

1. The sweep gives 200 final amounts per asset (SMA 1, which is DCA, to SMA 200).
2. Each length is replaced by the average of its neighbours within `HALF` lengths (the window shrinks at the ends). The highest averaged point is the optimal SMA. Both the raw best and the averaged best are reported.
3. `HALF` is chosen per asset by cross-validation from 4, 5, 8, 12, 20 and 30. Each point is predicted from its neighbours while it and its 3 closest neighbours on each side are hidden (neighbouring lengths give nearly the same result, so leaving them in would let the test cheat). The `HALF` with the smallest squared error wins.
4. Each asset uses only its own curve. Nothing is pooled across assets.
5. An optimal length of 1 means DCA, so there is no line to watch. Such assets are normally left off the dashboard.

**Limit:** smoothing removes jitter between neighbouring lengths. It cannot tell whether the whole curve is luck, and no significance tests were run.

The results are stored in `config.py`: `OPTIMAL_N`, and `BEAT_DCA_PCT`, the share of lengths from 2 to 200 that beat DCA. The daily job does not recompute them. Rerun the sweep notebooks to refresh them.

---

## Dashboard

A static page on GitHub Pages (`docs/index.html`) that reads `docs/data.json`. It has one section per group of assets (Indexes and Individual stocks), each with a table and a chart. It started with the S&P 500 and ASML as test assets.

- **Table:** name, last close, date, optimal SMA (band), SMA value, distance, status, days in status, and SMA 50/100/200.
- **Status:** **Open** means the last close is at or below the optimal SMA, which is the backtest's buy rule. **Closed** means it is above. It displays the rule's state and is not an instruction to trade. In the backtest a signal on one day's close leads to a purchase at the next day's close.
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

- Hand calculations matched exactly. An independent calendar-day implementation matched all 36 results (within 0.0003%).
- Money conservation: with 0% interest and dividends, money spent plus leftover cash equals the money invested.
- Blanking the last SMA value changes nothing, so there is no look-ahead. SMA(1) reproduces DCA exactly.
- A variant that bought at the signal day's close (a look-ahead) raised DCA's return by about 0.2% with everything else equal (S&P 500: 1,590.81% to 1,594.27%). The final rules decide on the previous day's close and buy at today's close.
- The dashboard build was checked on a synthetic price feed against a separate pandas calculation. The SMAs, distance, status and days in status matched, and an empty download, a short history and an empty last row were skipped or dropped. These were development checks and are not kept as automated tests.
- The dashboard layout was tested at 32 screen widths from 320 to 2560 px with no horizontal scrolling.

---

## Limitations

- One historical path per asset, not independent samples. Results depend on the start date.
- Free data only. Yahoo is unofficial, and any list of companies built from today's tickers has survivorship bias.
- Price indexes ignore dividends except through the placeholder yields.
- Differences below about 0.3% are not reliable.
- The scheduled job runs on GitHub's servers, and Yahoo may block or rate-limit them. A failed run leaves the previous data in place.
- The dashboard's optimal lengths are fixed until the sweep is rerun.
- The notebooks use absolute paths from the author's machine.

---

## Ideas Not Done

- A more rigorous choice of the optimal length: a spline or Gaussian-process fit instead of the neighbour average, walk-forward tests, a bootstrap of the optimum, and tests for the best of 200 (White's Reality Check, Hansen's SPA, Model Confidence Set).
- Email alerts when an asset enters or leaves its window (designed and postponed).
- Robustness: start-year sweep, costs, sensitivity to the interest rate and dividend yield, bootstrap.
- An event study of what follows a cross below the SMA, and a small ML layer on those events.
- MSCI All World and Emerging Markets through ETFs, and company cohorts chosen without hindsight.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data fetching and analysis |
| `pandas` | Data processing |
| `yfinance` | Yahoo Finance prices |
| `matplotlib` | Charts in the analysis |
| HTML, CSS, JavaScript | The dashboard page (no framework, no server) |
| Plotly.js | Interactive dashboard charts |
| GitHub Actions | Scheduled data refresh |
| GitHub Pages | Dashboard hosting |

---

## License

See `LICENSE`.
