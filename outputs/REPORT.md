# Futures Market Strategy Research

**Data source:** synthetic (ARTIFICIAL DATA; not real market evidence)

**Instrument:** synthetic illustrative series

**Observations:** 1500; **out-of-sample begins:** 2023-01-10

**Methods:** SMA 20/60 momentum; 20-day z-score mean reversion at ±1; signals shifted one trading bar; assumed proportional cost = 5.0 bps per unit turnover.

## Results

| strategy       | period        |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|:--------------|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Momentum       | Development   |           1050 |            -51.08  |                      22.122 |                  -0.665 |            -58.796 |              46.952 |
| Momentum       | Out-of-Sample |            450 |             -8.11  |                      18.284 |                  -0.168 |            -18.604 |              50.222 |
| Mean Reversion | Development   |           1050 |            -63.891 |                      17.077 |                  -1.345 |            -64.901 |              24.19  |
| Mean Reversion | Out-of-Sample |            450 |             19.386 |                      13.366 |                   0.809 |            -11.39  |              29.333 |
| Buy and Hold   | Development   |           1050 |            -45.901 |                      22.216 |                  -0.552 |            -56.757 |              50     |
| Buy and Hold   | Out-of-Sample |            450 |              3.058 |                      18.273 |                   0.184 |            -20.977 |              50.222 |

## Interpretation

Compare out-of-sample returns, drawdowns and stability across volatility regimes. A higher in-sample Sharpe alone is not evidence of predictive skill.

## Limitations

- Educational **percentage-return proxy**, not a tradable futures contract P&L. No margin, contract multipliers, bid/ask execution, funding, collateral interest, market impact, contract-specific expiry, or roll P&L.
- Yahoo `=F` price histories may be stitched across contracts. Verify continuous-series construction, adjustments and roll rules against exchange/contract data before making claims.
- Daily closes are an approximate execution model. Signals are lagged to avoid same-bar look-ahead; next-open execution could differ significantly.
- Static strategies were not optimized; the 70/30 split is chronological, not randomized.
- Risk-free rate assumed zero for Sharpe. This is research, not financial advice.
