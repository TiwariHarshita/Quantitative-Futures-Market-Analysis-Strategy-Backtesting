# Quantitative Futures Market Analysis & Strategy Backtesting

An **educational, reproducible quantitative research project** for a Trainee – International Markets application. It compares moving-average momentum and z-score mean reversion on daily price series, including a chronological out-of-sample test and explicit trading cost assumptions.

## Install and run

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python market_research.py --source synthetic
```

The default synthetic data requires no network and is **not evidence about actual markets**.

## Run on real historical prices

```bash
python market_research.py --source yahoo --ticker CL=F --start 2019-01-01 --end 2026-11-01 --output outputs/crude_oil
```

Use `GC=F` for gold or `ES=F` for E-mini S&P 500 futures **if available from the data provider**. Yahoo may block or fail downloads; source data is external and prices may be stitched/adjusted. This is *not* a production-quality historical futures feed.

## Run on your own verified contract/continuous series

Prepare `my_prices.csv` with two columns:

```csv
Date,Close
2024-01-02,72.5
2024-01-03,72.9
```

Use at least 300 valid daily rows. For authentic futures analysis, document contract identifiers, roll dates, adjustment conventions and whether prices are settlement or last trade.

```bash
python market_research.py --source csv --csv my_prices.csv --output outputs/my_study
```

## Outputs

- `REPORT.md`: methodology, results table, limitations
- `strategy_metrics.csv`: performance of each strategy for development and out-of-sample periods
- `volatility_regimes.csv`: conditional summary by volatility state
- `analyzed_data.csv`: cleaned prices, returns and signals
- `price_indicators.png`, `equity_curves.png`, `volatility.png`: plots

## Backtesting assumptions

- Momentum: long when 20-day SMA > 60-day SMA; otherwise short after warmup.
- Mean reversion: long if 20-day z-score < -1, short if > +1, otherwise flat.
- Signals are computed at day *t* close; exposure begins **on the next observation**, not the same close.
- 5 basis points per 1-unit change of notional exposure by default, i.e., long-to-short pays twice the cost of flat-to-long.
- 70% earliest observations for **development**, latest 30% as **out-of-sample**. No parameter selection uses test results.
- Percentage price returns with notional exposures ±1/0; **not a true futures contract simulation**. No multiplier, variation margin, collateral, explicit expiry/roll economics or accurate fill prices. Sharpe assumes zero risk-free rate.
- Volatility split uses the median rolling volatility of **development-only** observations.
- Data are daily; consider market holidays and missing sessions when interpreting signals.

## Run tests

```bash
python -m pytest -q
```

## Ideas to extend carefully

1. Use documented exchange-quality continuous contracts and add proper rolls.
2. Compare walk-forward sensitivity across training-window sizes, not just trading costs.
3. Compare performance across assets and disjoint economic regimes.
4. Test a null/randomized strategy to reduce false discoveries.
5. Compute contract-level P&L using exchange multipliers, ticks, expiry and margin rules.

## Resume guidance

Only describe analyses you completed. Run on real datasets and inspect `REPORT.md` before making claims about market behavior or performance. Do not label synthetic-data results as real backtesting.

## NEW: Walk-forward validation and transaction-cost sensitivity

Run the improved analysis on offline synthetic data:

```bash
python market_research.py --source synthetic --walk-forward --output outputs/synthetic_walk_forward
```

Run on historical crude-oil futures proxy data (requires internet):

```bash
python market_research.py --source yahoo --ticker CL=F --start 2019-01-01 --end 2026-11-01 --walk-forward --wf-train 504 --wf-test 126 --cost-bps 5 --cost-grid 0,2,5,10,20 --output outputs/crude_oil
```

Or bring a verified daily `Date,Close` CSV using `--source csv --csv data/my_prices.csv`.

**What the extension does:**

- Every fold uses the previous **504 daily observations** for parameter selection, then holds out the next **126 observations** for one test. It rolls forward by 126 and never overlaps test days.
- On each training fold, it chooses among momentum SMA pairs `(10,40), (20,60), (30,90)` and mean-reversion z-score windows `(15,20,30)` with thresholds `(0.75,1.0,1.5)` using *training net Sharpe* only.
- It records the parameters selected for every fold and the test-period results. No test results are used in that selection.
- It concatenates all disjoint held-out results to report out-of-sample equity growth and metrics.
- It recomputes returns at costs of **0, 2, 5, 10 and 20 basis points** per unit turnover, without changing previously selected positions, so cost sensitivity isn't distorted by retuning.

**New output files:**

| File | Description |
|---|---|
| `walk_forward_folds.csv` | Dates, selected parameters and fold-level held-out results |
| `walk_forward_daily.csv` | Held-out daily positions, turnover, gross/net returns |
| `walk_forward_summary.csv` | Concatenated held-out Sharpe, returns, drawdown |
| `transaction_cost_sensitivity.csv` | Held-out performance at each assumed trading cost |
| `walk_forward_equity.png` | Held-out equity charts, fold boundaries |
| `transaction_cost_sensitivity.png` | Net results vs trading-cost assumptions |
| `WALK_FORWARD_REPORT.md` | Reproducible experiment summary and limitations |

**Important limitations:** This remains an educational return proxy, not an exchange-accurate futures simulation. Fold start resets the assumed position to flat and pays entry cost; it does not model end-of-fold liquidation cost. Short positions, rolls and adjusted contract prices require additional attention. The sample synthetic results **must not be presented as live-market evidence**. Historical performance is not a profit guarantee.
