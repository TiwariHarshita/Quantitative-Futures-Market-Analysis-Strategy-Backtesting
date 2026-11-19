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
2. Add walk-forward evaluation and transaction-cost sensitivity (e.g. 2, 5, 10 bps).
3. Compare performance across assets and disjoint economic regimes.
4. Test a null/randomized strategy to reduce false discoveries.
5. Compute contract-level P&L using exchange multipliers, ticks, expiry and margin rules.

## Resume guidance

Only describe analyses you completed. Run on real datasets and inspect `REPORT.md` before making claims about market behavior or performance. Do not label synthetic-data results as real backtesting.
