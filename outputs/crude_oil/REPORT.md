# Futures Market Strategy Research

**Data source:** yahoo

**Instrument:** CL=F

**Observations:** 1970; **out-of-sample begins:** 2024-06-27

**Methods:** SMA 20/60 momentum; 20-day z-score mean reversion at ±1; signals shifted one trading bar; assumed proportional cost = 5.0 bps per unit turnover.

## Results

| strategy       | period        |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|:--------------|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Momentum       | Development   |           1379 |            -72.597 |                      55.818 |                  -0.138 |            -87.249 |              48.006 |
| Momentum       | Out-of-Sample |            591 |             37.209 |                      43.974 |                   0.528 |            -41.989 |              50.085 |
| Mean Reversion | Development   |           1379 |            -49.825 |                      44.176 |                  -0.049 |            -80.42  |              27.266 |
| Mean Reversion | Out-of-Sample |            591 |            -25.975 |                      33.799 |                  -0.211 |            -42.961 |              25.212 |
| Buy and Hold   | Development   |           1379 |             73.743 |                      56.083 |                   0.472 |            -84.902 |              54.17  |
| Buy and Hold   | Out-of-Sample |            591 |             28.702 |                      43.983 |                   0.466 |            -39.309 |              51.777 |

## Interpretation

Compare out-of-sample returns, drawdowns and stability across volatility regimes. A higher in-sample Sharpe alone is not evidence of predictive skill.

## Limitations

- Educational **percentage-return proxy**, not a tradable futures contract P&L. No margin, contract multipliers, bid/ask execution, funding, collateral interest, market impact, contract-specific expiry, or roll P&L.
- Yahoo `=F` price histories may be stitched across contracts. Verify continuous-series construction, adjustments and roll rules against exchange/contract data before making claims.
- Daily closes are an approximate execution model. Signals are lagged to avoid same-bar look-ahead; next-open execution could differ significantly.
- Static strategies were not optimized; the 70/30 split is chronological, not randomized.
- Risk-free rate assumed zero for Sharpe. This is research, not financial advice.
