# SMA Strategy 

An ETL and data analysis repo that tests buying stocks and indexes at a simple moving average target (SMA) versus plain monthly investing (DCA) on 12 stock indexes and 35+ large companies up to about 40 years.

The financial topic at hand is meant to serve only as context for a data project and not necessarily the implication that there is any advantage to be gained from simple SMA trends. Past trends do not represent future ones and if there was any significant advantage to be found in SMA strategies it would have been found and erased immediately decades ago since quant models degrade incredibly quickly. Also the answer to this hypotesis can be found with a quick Google search. It just serves as a subject for a data project.


<img width="1216" height="684" alt="The-Simple-Moving-Average_png" src="https://github.com/user-attachments/assets/54891358-71ff-41af-b000-3601b0c8493a" />



---

## What is an SMA?

The **simple moving average** of length `n` is the average of the last `n` daily closing prices. It is a smoothed price line.

```
SMA(n) on day t = (close of day t + close of day t-1 + ... + close of day t-n+1) / n
```

- **DCA** (dollar cost averaging) means investing a fixed amount on a fixed schedule. It is the baseline here.

---

## Repository Contents

| File | Description |
|---|---|
| `smaparsing_indexes.py` | Fetches index histories from Yahoo Finance |
| `smaparsing_individualstocks.py` | Same for the individual companies  |
| `smanalysis_50_100_200.ipynb` | DCA vs SMA 50, 100 and 200 on the indexes |
| `smanalysis_50_100_200_ind.ipynb` | Same on the individual companies |
| `smanalysis_simulation.ipynb` | The SMA 1 to 200 sweep on the indexes: results, charts, cross-validated smoothing and White's Reality Check |
| `smanalysis_simulation_ind.ipynb` | Same on the individual companies |
| `config.py` | Dashboard settings |
| `build_data.py` | Downloads fresh prices, recalculates the SMAs and writes `docs/data.json` |
| `data/results/` | Saved full results |
| `docs/` | The dashboard served by GitHub Pages (`index.html` and `data.json`) |
| `.github/workflows/` | Scheduled GitHub Actions workflow |
| `requirements.txt` | Python dependencies |
| `LICENSE`, `.gitignore` | License and ignored files |


---

## Hypotesis

**Question:** with identical contributions and holding assets long-term, does purchasing only when the market is below a certain SMA end with a higher value than DCA?

- Each asset is compared only with **its own DCA**, so results are shown as **% vs DCA**. Assets are not compared with each other (different starts, currencies and circumstances).
- Only buying and holding is tested.
- Every length from 1 to 200 is simulated per asset (DCA plus SMA 2 to 200) and the 200 results are compared, with the 50,100 and 200 windows analysed further.

### Rules (same for all 200 simulations, for all stocks)

- **Signal for purchasing:** the previous trading day's close must be below the previous day's SMA. The purchase is priced at that same close.
- **Buy size:** all cash available, with fractional units of a share allowed.
- **Start:** the first day on or after 1986-01-01 with 200 closes available. All 200 strategies of an asset share the same start and end.
- **Payments:** All simulations get 500 to invest each month since the starting date, with DCA purchasing immediately and all SMA strategies holding cash until the analysed asset falls below threshold, triggering the signal to purchase.
- **Interest:** cash earns 3% a year, compounded over the calendar days between prices.
- **Dividends:** all assets are treated as accumulating. Units grow by a yearly dividend yield. The yields are manually set constant approximations.


- **Final amount** = units purchased x last close + leftover cash. It includes all the money invested plus any cash still waiting.

---

## Data

Source: Yahoo Finance. The final run ends on 2026-10-20.

| Index              | Ticker    | Experiment start |
| ------------------ | --------- | ---------------- |
| S&P 500            | ^GSPC     | 1986-01-02       |
| Nasdaq Composite   | ^IXIC     | 1986-01-02       |
| Nasdaq 100         | ^NDX      | 1986-07-16       |
| FTSE 100           | ^FTSE     | 1986-01-02       |
| Nikkei 225         | ^N225     | 1986-01-06       |
| DAX                | ^GDAXI    | 1988-10-14       |
| CAC 40             | ^FCHI     | 1990-12-17       |
| Hang Seng          | ^HSI      | 1987-10-26       |
| Shanghai Composite | 000001.SS | 1998-04-29       |
| Euro Stoxx 50      | ^STOXX50E | 2008-01-18       |
| Nifty 50           | ^NSEI     | 2008-07-07       |
| Dow Jones          | ^DJI      | 1992-10-14       |


- Coherence checks done, with no duplicate dates and no missing values in the final download.

### Companies

| Group | Companies |
|---|---|
| Hindsight winners | Microsoft, Apple, Amazon, Nvidia, Alphabet, Meta, Broadcom, Tesla, Netflix, Visa, Mastercard |
| Long-time US giants | Exxon Mobil, IBM, General Electric, Coca-Cola, Johnson & Johnson, Procter & Gamble, Walmart, JPMorgan, Berkshire Hathaway, Eli Lilly, Costco, Oracle |
| Fell hard but still trade | Citigroup, AIG, Intel, Cisco, Boeing, Nokia |
| Based outside the US | Nestlé, BP, Siemens, Toyota, TSMC, Tencent, Samsung, Alibaba, ASML, Saudi Aramco |

- Companies that started after 1986 are included from their first usable day.
- The sample is chosen with hindsight and has survivorship bias (Enron or Bear Stearns would once be in that list), which tilts results toward DCA. In general, only testing companies with hindsight and never selling is a clear advantage to DCA, but since the scope is to test long-term passive investments and focused on indexes with companies being an extra, it is not an issue.


## Results ( Indexes ) 

<img width="1789" height="1590" alt="image" src="https://github.com/user-attachments/assets/f80499fe-9527-43e8-b3a2-ccb82d98b177" />

---

<img width="1790" height="1590" alt="image" src="https://github.com/user-attachments/assets/9d1ecd9a-9933-4279-8272-b0a1b821b439" />

---

- All indexes other than the Euro Zone, French and Japanese markets seem to heavily favour DCA over long-term lump sum investments at first sight, having their higher peaks in the earlier windows.
- US indexes are particularly penalizing in this aspect, strongly favouring DCA.
- The EURO stock index has by far the most anti-DCA graph of all, apparently strongly penalizing early buying.
- There is a heavy correlation between the US and Chinese indexes themselves inside their holding positions as well as between CAC40 and Euro Stoxx, with 16 of the 40 companies in CAC also included in the Euro index, which helps to explain the similar visible trends between them.

---

<img width="1389" height="590" alt="image" src="https://github.com/user-attachments/assets/343e95ee-d5fd-4ca7-91e9-4ec21a7f8143" />

---

<img width="1281" height="690" alt="image" src="https://github.com/user-attachments/assets/0f66ef84-216b-4273-940d-3861ee223c64" />

---

- The Chinese markets are the most penalizing when comparing the mean final mean for each SMA strategy bin (10 bins) to the DCA, representing a greater Chinese market trend.
- Although there seems to be a clear initial advantage displayed in regards to DCA over longer SMA strategies differences, there is not a significant difference in the overall final value between them (for non-Chinese markets), with no bin oscillating more than 2.4 pp in difference. A key finding in itself which suggests that even the investor that would choose the literal worse performing SMA strategy would not lose that significantly to the best ones for the same asset.


## Results ( Individual Stocks ) 

<img width="1790" height="5189" alt="image" src="https://github.com/user-attachments/assets/e8ef6dbb-d637-4e58-9ff7-218c8c66a2fc" />

---

<img width="1389" height="590" alt="image" src="https://github.com/user-attachments/assets/3acadf2b-bd53-4480-9ebf-2bfd4ff52bcf" />

---


- Almost all companies show DCA as the best strategy, either as the optimal purchase time or very close to it when compared to the optimal bin.
- By results, when companies have shown better performing strategies than DCA, it's by a little (2 pp max), similar to indexes. However, when other strategies lose to DCA, they lose by a lot. This displays the unfair penalization of this simulation towards individual companies and SMA windows, since individual stocks do not usually fall into the long term holding passive investments that the simulation analyses, as good performing companies fall into longer term SMAs territory much less often and anyone DCA-ing their salary into Apple since the beginning of the company's public listed history is obviously going to do fairly well.
- Unsurprisingly, a lot of the hindsight winners in the S&P show a very strong advantage to DCA and holding.
- Amazon and Google show the most interesting nuances as the only two Mag-7 companies that don't have an early optimal SMA and a very clear downward trend starting immediately in the first bins, with both hitting their optimums around the 70s mark.

---


<img width="1278" height="690" alt="image" src="https://github.com/user-attachments/assets/36d430b4-a72b-4141-a879-5c0140e68eb9" />

---



## Optimal SMA

The single best length will often be one lucky point, so the curve of 200 final amounts is smoothed and the highest smoothed point is taken as the optimal SMA. Three smoothers are compared. `y[n]` is the final amount for length `n` and `ŷ[n]` its smoothed value:

| Smoother | Definition |
|---|---|
| Average | `ŷ[n]` = mean of `y[j]` for all `j` with `abs(j - n) <= h` (the window shrinks at the ends) |
| Kernel regression | `ŷ[n]` = sum(`K((n-j)/b)` * `y[j]`) / sum(`K((n-j)/b)`), Gaussian `K(u) = exp(-u^2/2)` (statsmodels `KernelReg`) |
| LOESS | a straight line fitted to the closest share `f` of the lengths with weights `(1 - (distance/d)^3)^3`, and `ŷ[n]` is the line's value at `n` (statsmodels `lowess`, robustness iterations off) |


- All three are local weighted averages of neighbouring lengths. They differ in the weights and in the local fit.
- Settings chosen by cross-validation. Each length is predicted from the others with itself and its 3 closest lengths on each side hidden. The score is the mean of `(prediction - y)^2` and the smallest score wins.

## What the results show

- Share of lengths beating DCA is 1.5% for the median index (8 of 12 indexes are at 2% or less) and 8% for the median company (14 of 39 at 2% or less). For the Nasdaq Composite, FTSE 100, Shanghai Composite, Apple, Nvidia, Oracle, Cisco, Nokia, Tencent and ASML, none of the 199 lengths beat DCA.
- More than half of the lengths beat DCA for Euro Stoxx 50 (91%), Saudi Aramco (77%) (small sample size), Toyota (58%), Alibaba (57%) and CAC 40 (52%), with Costco at 50%. Strongly rising assets (Apple, Nvidia, Microsoft, Meta, Tesla) sit at or near 0%.
- Cross-validation chose the smallest setting almost everywhere (average 4, kernel 2, LOESS 0.05), so the smoothed optimum is usually within a few lengths of the raw best. The exceptions are Mastercard (58 to 71-72), IBM (111 to 84-85), Boeing (11 to 62), Cisco (1 to 21-22), Samsung (89 to 100-101), Aramco (116 to 118-151), and Oracle (1 to 12, average only) and Tencent (1 to 19, kernel only).
- SMA buyers do not buy cheaper, as the gap in average price and the gap in final amount are strongly linked , and every win had a lower average price.
- Idle cash earns 3% while the market earns more, so waiting costs more the longer the SMA. A dip to a long SMA in a rising market can still be above where DCA bought months earlier. Timing may help in long sideways or falling phases (Nikkei after 1990, FTSE and CAC 40 after 2000), but Shanghai is a counter-example.


## Significance: White's Reality Check

Although DCA looked like the best strategy overall throughout everything, there were instances that seemed to show SMA advantageous patterns.

I wanted to test for their statistical significance and see if results were enough to state that a clear trend has been happening in past performances. White’s Reality Check is a statistical test that accounts for testing many strategies and then selecting the best one. It compares the strategies against DCA and uses 1,000 bootstrap simulations, resampling returns in blocks, to estimate a p-value while accounting for the search across strategies.

- Test: Compare each SMA against DCA, accounting for the search across 199 alternatives. Repeat the same test for bins of 5, 10 and 20 SMA lengths.
- Bootstrap: Resample returns in blocks 1,000 times to account for dependence over time.
- Significance: A p-value below 0.05 is statistically significant.


Result: NONE of our tests was significant. No SMA or bin. There is insufficient statistical evidence that any SMA or bin has outperformed DCA.


## Dashboard

The dashboard is a static page that shows, for each asset, where the price stands relative to its optimal SMA today. It is updated every day by the scheduled job, and it is the practical end of the pipeline: data, sweep, optimal length, current state.

**How the findings feed it**
- **Optimal SMA:** the length per asset comes from the smoothed sweep curve (cross-validated average, kernel and LOESS), stored in `config.py`.
- **Status:** Open means the close is at or below the optimal SMA, which is the backtest's buy rule. It shows the rule's state, not a recommendation.

[**Live dashboard**](https://pedrosalgado22.github.io/SMAstrategy/)


A scheduled GitHub Actions workflow keeps the dashboard updated everyday on weekdays at 23:00 Lisbon time, after the main markets have closed for all companies/indexes present.


---

## Limitations

- Inflation not accounted for, with the avaliable money for purchasing staying stagnate. 
- Survivorship bias.
- Dividend yields are constant approximations and not their real life value at the time.
- The purchase is priced only at the close that triggered the signal. Does not account for in-day flutuations. 
- p-value is conservative and some sample sizes are small, so a non-significant result does not prove there is no edge. It just states that it is impossible to statistically confirm that it is. 
- The scheduled job runs on GitHub's servers, and Yahoo may block or rate-limit them. A failed run leaves the previous data in place.
- Including MSCI All World and Emerging Markets ETFs.

---

## Other Visualizations and Tables 

<img width="1789" height="1590" alt="image" src="https://github.com/user-attachments/assets/95e1f2ec-a0ef-4d36-9cd2-265cf2f8b1ea" />

---

<img width="1789" height="1589" alt="image" src="https://github.com/user-attachments/assets/2b3ffa52-1a2f-437b-8ac4-4d0649058ff4" />

---

<img width="1790" height="1590" alt="image" src="https://github.com/user-attachments/assets/8259a7cd-c678-4e4a-8d19-b6ec24889289" />

---
<img width="1789" height="5190" alt="image" src="https://github.com/user-attachments/assets/bf57a7d8-2cd5-4b8c-85c6-317d8b8f662d" />

---
<img width="1790" height="5189" alt="image" src="https://github.com/user-attachments/assets/7fa80645-b0db-4e0a-ac8f-c56136cac345" />

---

<img width="1784" height="5189" alt="image" src="https://github.com/user-attachments/assets/45923848-4765-40d8-986a-c0ea5f9d4dad" />

---

**Companies: best SMA and White's Reality Check**

| index | best SMA | best SMA final value | WRC p (all SMAs) | SMA significant | best bin (5) | mean final value (5) | WRC p (bins 5) | bins 5 significant | best bin (10) | mean final value (10) | WRC p (bins 10) | bins 10 significant | best bin (20) | mean final value (20) | WRC p (bins 20) | bins 20 significant |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| microsoft | 3 | 85,933,844.62 | 0.85 | False | 1-5 | 85,784,922.00 | 0.90 | False | 1-10 | 85,703,902.55 | 0.91 | False | 1-20 | 85,561,886.87 | 0.90 | False |
| apple | 10 | 188,035,006.74 | 0.95 | False | 6-10 | 187,783,382.52 | 0.98 | False | 1-10 | 187,775,678.87 | 0.99 | False | 1-20 | 187,501,519.37 | 0.96 | False |
| amazon | 73 | 14,225,509.53 | 0.92 | False | 71-75 | 14,188,722.84 | 0.89 | False | 61-70 | 14,030,421.86 | 0.94 | False | 61-80 | 13,992,193.68 | 0.92 | False |
| nvidia | 4 | 89,973,076.53 | 0.89 | False | 1-5 | 89,847,754.64 | 0.91 | False | 1-10 | 89,733,204.13 | 0.96 | False | 1-20 | 89,660,816.46 | 0.93 | False |
| alphabet | 69 | 1,858,004.15 | 0.66 | False | 66-70 | 1,856,568.98 | 0.64 | False | 61-70 | 1,854,964.20 | 0.64 | False | 41-60 | 1,850,136.87 | 0.63 | False |
| meta | 3 | 412,843.46 | 0.90 | False | 1-5 | 412,227.19 | 0.90 | False | 1-10 | 411,479.35 | 0.90 | False | 61-80 | 409,323.65 | 0.94 | False |
| broadcom | 29 | 5,120,422.81 | 0.92 | False | 31-35 | 5,107,819.37 | 0.91 | False | 21-30 | 5,102,738.10 | 0.94 | False | 1-20 | 5,097,983.96 | 0.93 | False |
| tesla | 2 | 3,320,148.61 | 0.65 | False | 1-5 | 3,312,544.96 | 0.65 | False | 1-10 | 3,296,213.35 | 0.62 | False | 1-20 | 3,266,747.98 | 0.61 | False |
| netflix | 4 | 10,534,811.99 | 0.85 | False | 1-5 | 10,520,971.15 | 0.87 | False | 1-10 | 10,512,172.14 | 0.88 | False | 1-20 | 10,474,064.40 | 0.86 | False |
| visa | 32 | 939,156.76 | 0.87 | False | 31-35 | 938,354.96 | 0.89 | False | 21-30 | 937,941.65 | 0.87 | False | 21-40 | 937,649.13 | 0.86 | False |
| mastercard | 58 | 1,505,817.97 | 0.92 | False | 71-75 | 1,502,778.73 | 0.87 | False | 51-60 | 1,499,130.42 | 0.87 | False | 1-20 | 1,497,388.40 | 0.85 | False |
| exxon | 14 | 13,774,710.53 | 0.78 | False | 11-15 | 13,762,638.02 | 0.80 | False | 11-20 | 13,755,629.68 | 0.80 | False | 1-20 | 13,753,564.46 | 0.80 | False |
| ibm | 111 | 5,187,763.53 | 0.60 | False | 81-85 | 5,181,777.75 | 0.53 | False | 81-90 | 5,180,519.19 | 0.49 | False | 81-100 | 5,179,400.25 | 0.56 | False |
| ge | 8 | 5,346,742.76 | 0.86 | False | 6-10 | 5,343,239.78 | 0.87 | False | 1-10 | 5,342,011.93 | 0.87 | False | 1-20 | 5,341,102.55 | 0.89 | False |
| coca_cola | 6 | 8,769,993.03 | 0.78 | False | 1-5 | 8,752,133.47 | 0.82 | False | 1-10 | 8,745,190.87 | 0.83 | False | 1-20 | 8,718,702.16 | 0.88 | False |
| jnj | 11 | 14,121,520.98 | 0.70 | False | 6-10 | 14,105,551.34 | 0.73 | False | 1-10 | 14,100,044.58 | 0.75 | False | 1-20 | 14,087,799.31 | 0.74 | False |
| pg | 16 | 9,383,020.07 | 0.80 | False | 16-20 | 9,378,346.18 | 0.80 | False | 11-20 | 9,376,665.55 | 0.80 | False | 1-20 | 9,373,387.17 | 0.76 | False |
| walmart | 181 | 11,401,375.27 | 0.88 | False | 176-180 | 11,399,477.08 | 0.88 | False | 171-180 | 11,380,662.40 | 0.89 | False | 161-180 | 11,299,472.20 | 0.90 | False |
| jpmorgan | 5 | 18,264,147.95 | 0.73 | False | 1-5 | 18,206,963.11 | 0.78 | False | 1-10 | 18,167,135.32 | 0.85 | False | 1-20 | 18,139,378.50 | 0.85 | False |
| berkshire | 6 | 1,177,062.67 | 0.95 | False | 1-5 | 1,175,789.59 | 0.94 | False | 1-10 | 1,175,480.07 | 0.94 | False | 1-20 | 1,174,094.20 | 0.91 | False |
| eli_lilly | 8 | 44,968,718.03 | 0.79 | False | 6-10 | 44,909,059.44 | 0.81 | False | 11-20 | 44,881,177.88 | 0.86 | False | 1-20 | 44,868,278.21 | 0.88 | False |
| costco | 61 | 16,167,833.59 | 0.60 | False | 56-60 | 16,161,784.29 | 0.60 | False | 51-60 | 16,147,787.41 | 0.60 | False | 41-60 | 16,121,363.34 | 0.58 | False |
| oracle | 12 | 34,277,134.77 | 0.88 | False | 11-15 | 34,224,275.71 | 0.88 | False | 1-10 | 34,054,489.73 | 0.87 | False | 1-20 | 33,973,906.37 | 0.87 | False |
| citigroup | 44 | 1,841,379.21 | 0.95 | False | 41-45 | 1,839,573.26 | 0.99 | False | 41-50 | 1,837,986.23 | 0.85 | False | 21-40 | 1,832,831.10 | 0.84 | False |
| aig | 126 | 395,920.24 | 0.89 | False | 121-125 | 395,773.84 | 0.82 | False | 121-130 | 395,214.70 | 0.85 | False | 101-120 | 394,660.70 | 0.83 | False |
| intel | 171 | 17,392,455.21 | 0.71 | False | 166-170 | 17,387,247.20 | 0.55 | False | 161-170 | 17,376,039.39 | 0.54 | False | 161-180 | 17,369,369.93 | 0.51 | False |
| cisco | 25 | 13,008,690.09 | 0.93 | False | 21-25 | 12,984,629.06 | 0.95 | False | 11-20 | 12,930,274.89 | 0.95 | False | 1-20 | 12,928,217.54 | 0.93 | False |
| boeing | 11 | 3,809,822.21 | 0.76 | False | 61-65 | 3,807,999.22 | 0.81 | False | 61-70 | 3,805,579.19 | 0.78 | False | 1-20 | 3,801,711.69 | 0.74 | False |
| nokia | 4 | 801,306.47 | 0.89 | False | 1-5 | 801,076.08 | 0.87 | False | 1-10 | 800,290.69 | 0.88 | False | 1-20 | 796,821.67 | 0.89 | False |
| nestle | 175 | 2,400,542.31 | 0.89 | False | 171-175 | 2,398,838.30 | 0.88 | False | 161-170 | 2,393,905.11 | 0.89 | False | 161-180 | 2,391,427.90 | 0.84 | False |
| bp | 70 | 2,133,223.12 | 0.63 | False | 66-70 | 2,131,888.09 | 0.61 | False | 61-70 | 2,131,080.01 | 0.59 | False | 61-80 | 2,128,843.13 | 0.64 | False |
| siemens | 49 | 2,344,160.46 | 0.87 | False | 46-50 | 2,342,719.90 | 0.96 | False | 41-50 | 2,341,768.84 | 0.95 | False | 41-60 | 2,340,285.03 | 0.90 | False |
| toyota | 135 | 2,572,436.03 | 0.85 | False | 131-135 | 2,568,625.49 | 0.87 | False | 131-140 | 2,568,489.93 | 0.85 | False | 121-140 | 2,566,867.52 | 0.88 | False |
| tsmc | 16 | 13,054,263.59 | 0.72 | False | 11-15 | 13,036,533.92 | 0.72 | False | 11-20 | 13,036,425.04 | 0.71 | False | 21-40 | 13,013,591.92 | 0.69 | False |
| tencent | 18 | 4,302,008.81 | 0.82 | False | 16-20 | 4,293,848.01 | 0.82 | False | 11-20 | 4,291,183.31 | 0.81 | False | 1-20 | 4,287,375.68 | 0.78 | False |
| samsung | 89 | 3,518,194.38 | 0.85 | False | 86-90 | 3,515,601.89 | 0.81 | False | 91-100 | 3,512,223.71 | 0.77 | False | 81-100 | 3,509,567.01 | 0.67 | False |
| alibaba | 200 | 67,468.40 | 0.81 | False | 196-200 | 67,408.91 | 0.79 | False | 191-200 | 67,399.90 | 0.69 | False | 181-200 | 67,338.60 | 0.60 | False |
| asml | 8 | 15,901,617.39 | 0.96 | False | 1-5 | 15,881,444.93 | 0.97 | False | 1-10 | 15,870,649.42 | 0.92 | False | 1-20 | 15,829,347.44 | 0.88 | False |
| aramco | 116 | 43,570.43 | 0.21 | False | 116-120 | 43,563.14 | 0.21 | False | 151-160 | 43,554.77 | 0.23 | False | 141-160 | 43,518.42 | 0.21 | False |

**Companies: raw best and smoothed best SMA**

| index | raw best | average | kernel | loess |
|---|---:|---:|---:|---:|
| microsoft | 3 | 1 | 1 | 1 |
| apple | 1 | 1 | 1 | 1 |
| amazon | 73 | 71 | 72 | 72 |
| nvidia | 1 | 1 | 1 | 1 |
| alphabet | 69 | 69 | 68 | 69 |
| meta | 3 | 1 | 1 | 1 |
| broadcom | 29 | 30 | 31 | 31 |
| tesla | 2 | 1 | 1 | 1 |
| netflix | 4 | 3 | 5 | 5 |
| visa | 32 | 31 | 32 | 33 |
| mastercard | 58 | 71 | 71 | 72 |
| exxon | 14 | 13 | 14 | 14 |
| ibm | 111 | 84 | 84 | 85 |
| ge | 8 | 5 | 8 | 7 |
| coca_cola | 6 | 3 | 5 | 1 |
| jnj | 11 | 7 | 9 | 9 |
| pg | 16 | 16 | 16 | 16 |
| walmart | 181 | 177 | 177 | 178 |
| jpmorgan | 5 | 1 | 1 | 1 |
| berkshire | 6 | 2 | 1 | 1 |
| eli_lilly | 8 | 12 | 9 | 9 |
| costco | 61 | 58 | 59 | 59 |
| oracle | 1 | 12 | 1 | 1 |
| citigroup | 44 | 43 | 43 | 42 |
| aig | 126 | 118 | 121 | 119 |
| intel | 171 | 168 | 169 | 169 |
| cisco | 1 | 21 | 22 | 22 |
| boeing | 11 | 62 | 62 | 62 |
| nokia | 1 | 1 | 1 | 1 |
| nestle | 175 | 173 | 173 | 173 |
| bp | 70 | 67 | 69 | 69 |
| siemens | 49 | 46 | 48 | 48 |
| toyota | 135 | 134 | 135 | 135 |
| tsmc | 16 | 16 | 15 | 15 |
| tencent | 1 | 1 | 19 | 1 |
| samsung | 89 | 100 | 101 | 101 |
| alibaba | 200 | 200 | 200 | 200 |
| asml | 1 | 2 | 1 | 1 |
| aramco | 116 | 151 | 118 | 118 |

**Indexes: best SMA and White's Reality Check**

| index | best SMA | best SMA final value | WRC p (all SMAs) | SMA significant | best bin (5) | mean final value (5) | WRC p (bins 5) | bins 5 significant | best bin (10) | mean final value (10) | WRC p (bins 10) | bins 10 significant | best bin (20) | mean final value (20) | WRC p (bins 20) | bins 20 significant |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sp500 | 10 | 4,116,748.50 | 0.92 | False | 11-15 | 4,114,193.20 | 0.84 | False | 11-20 | 4,113,480.11 | 0.83 | False | 1-20 | 4,113,100.27 | 0.85 | False |
| nasdaq_comp | 2 | 6,552,527.50 | 0.93 | False | 1-5 | 6,550,880.50 | 0.93 | False | 11-20 | 6,548,689.32 | 0.92 | False | 1-20 | 6,548,407.26 | 0.92 | False |
| nasdaq100 | 30 | 12,669,500.25 | 0.70 | False | 26-30 | 12,652,594.95 | 0.68 | False | 21-30 | 12,644,944.97 | 0.69 | False | 21-40 | 12,636,928.89 | 0.73 | False |
| ftse100 | 187 | 1,852,817.21 | 0.94 | False | 181-185 | 1,851,343.83 | 0.89 | False | 181-190 | 1,851,340.11 | 0.91 | False | 161-180 | 1,849,523.50 | 0.89 | False |
| nikkei | 200 | 1,166,537.88 | 0.92 | False | 196-200 | 1,166,283.25 | 0.91 | False | 191-200 | 1,165,660.00 | 0.91 | False | 181-200 | 1,165,092.24 | 0.91 | False |
| dax | 109 | 1,330,908.39 | 0.74 | False | 106-110 | 1,330,177.63 | 0.72 | False | 101-110 | 1,329,947.52 | 0.71 | False | 101-120 | 1,329,109.71 | 0.73 | False |
| cac40 | 58 | 906,486.34 | 0.62 | False | 56-60 | 905,462.10 | 0.59 | False | 51-60 | 905,040.53 | 0.59 | False | 41-60 | 904,957.22 | 0.59 | False |
| hang_seng | 36 | 1,277,796.87 | 0.93 | False | 66-70 | 1,276,203.60 | 0.93 | False | 31-40 | 1,275,384.81 | 0.93 | False | 41-60 | 1,274,609.98 | 0.91 | False |
| shanghai | 5 | 399,222.46 | 0.81 | False | 1-5 | 398,950.84 | 0.87 | False | 1-10 | 398,809.92 | 0.84 | False | 1-20 | 397,548.53 | 0.80 | False |
| euro_stoxx | 169 | 285,669.56 | 0.34 | False | 196-200 | 285,485.97 | 0.43 | False | 171-180 | 285,438.88 | 0.49 | False | 161-180 | 285,398.95 | 0.50 | False |
| nifty | 5 | 348,586.22 | 0.95 | False | 6-10 | 348,143.12 | 0.94 | False | 1-10 | 348,086.46 | 0.95 | False | 1-20 | 347,498.99 | 0.92 | False |
| dow_jones | 15 | 1,574,481.17 | 0.83 | False | 11-15 | 1,574,092.99 | 0.84 | False | 11-20 | 1,573,596.55 | 0.83 | False | 1-20 | 1,572,893.43 | 0.88 | False |

**Indexes: raw best and smoothed best SMA**

| index | raw best | average | kernel | loess |
|---|---:|---:|---:|---:|
| sp500 | 10 | 12 | 11 | 11 |
| nasdaq_comp | 1 | 1 | 1 | 1 |
| nasdaq100 | 30 | 31 | 30 | 30 |
| ftse100 | 1 | 185 | 186 | 1 |
| nikkei | 200 | 200 | 200 | 200 |
| dax | 109 | 111 | 106 | 106 |
| cac40 | 58 | 62 | 59 | 95 |
| hang_seng | 36 | 48 | 36 | 36 |
| shanghai | 1 | 2 | 1 | 1 |
| euro_stoxx | 169 | 172 | 200 | 200 |
| nifty | 5 | 7 | 6 | 7 |
| dow_jones | 15 | 13 | 14 | 14 |

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
