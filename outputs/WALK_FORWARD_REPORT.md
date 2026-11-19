# Walk-forward evaluation and transaction-cost sensitivity

Rolling training: **504 observations**; test: **126 observations**; roll step: **126 observations**. No overlapping held-out days. Only complete test folds are included.

Parameters selected using **training net Sharpe** at **5 bps**; the next test window is evaluated once without retuning.

## Concatenated out-of-sample results

| strategy       |   test_days |   test_folds |   assumed_cost_bps |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|------------:|-------------:|-------------------:|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Mean Reversion |         882 |            7 |                  5 |            882 |           -28.5035 |                     16.7311 |                 -0.4891 |           -41.6451 |             24.263  |
| Momentum       |         882 |            7 |                  5 |            882 |           -65.3996 |                     25.2729 |                 -1.0727 |           -72.8853 |             45.4649 |

## Transaction-cost stress test

| strategy       |   cost_bps |   turnover_units |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|-----------:|-----------------:|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Mean Reversion |          0 |              162 |            882 |           -22.4557 |                     16.7031 |                 -0.3514 |           -40.1864 |             24.4898 |
| Mean Reversion |          2 |              162 |            882 |           -24.9335 |                     16.7136 |                 -0.4065 |           -40.7741 |             24.3764 |
| Mean Reversion |          5 |              162 |            882 |           -28.5035 |                     16.7311 |                 -0.4891 |           -41.6451 |             24.263  |
| Mean Reversion |         10 |              162 |            882 |           -34.0823 |                     16.7647 |                 -0.6262 |           -43.6356 |             24.1497 |
| Mean Reversion |         20 |              162 |            882 |           -43.9749 |                     16.8489 |                 -0.8978 |           -49.5326 |             23.9229 |
| Momentum       |          0 |               55 |            882 |           -64.4304 |                     25.2629 |                 -1.042  |           -72.3076 |             45.6916 |
| Momentum       |          2 |               55 |            882 |           -64.8212 |                     25.2665 |                 -1.0543 |           -72.5401 |             45.5782 |
| Momentum       |          5 |               55 |            882 |           -65.3996 |                     25.2729 |                 -1.0727 |           -72.8853 |             45.4649 |
| Momentum       |         10 |               55 |            882 |           -66.3433 |                     25.2857 |                 -1.1032 |           -73.4514 |             45.4649 |
| Momentum       |         20 |               55 |            882 |           -68.1567 |                     25.3197 |                 -1.1638 |           -74.55   |             45.2381 |

## Fold-specific parameters and evaluation

|   fold | strategy       | train_start   | train_end   | test_start   | test_end   | chosen_parameters   |   training_sharpe |   test_return_pct |   test_sharpe |   test_max_drawdown_pct |   test_turnover |
|-------:|:---------------|:--------------|:------------|:-------------|:-----------|:--------------------|------------------:|------------------:|--------------:|------------------------:|----------------:|
|      1 | Momentum       | 2019-01-01    | 2020-12-04  | 2020-12-07   | 2021-05-31 | SMA_20_60           |           -0.2637 |          -14.0484 |       -0.91   |                -30.8589 |               7 |
|      1 | Mean Reversion | 2019-01-01    | 2020-12-04  | 2020-12-07   | 2021-05-31 | Z_30_0.75           |           -0.4603 |           -5.1118 |       -0.3261 |                 -9.0521 |              20 |
|      2 | Momentum       | 2019-06-26    | 2021-05-31  | 2021-06-01   | 2021-11-23 | SMA_30_90           |           -0.0901 |           28.8557 |        1.7627 |                -15.5668 |               1 |
|      2 | Mean Reversion | 2019-06-26    | 2021-05-31  | 2021-06-01   | 2021-11-23 | Z_30_1.5            |           -0.0162 |            9.9341 |        1.2089 |                -10.9738 |              26 |
|      3 | Momentum       | 2019-12-19    | 2021-11-23  | 2021-11-24   | 2022-05-18 | SMA_30_90           |            0.6498 |          -49.3974 |       -4.7073 |                -48.7253 |               7 |
|      3 | Mean Reversion | 2019-12-19    | 2021-11-23  | 2021-11-24   | 2022-05-18 | Z_30_1.5            |            0.3759 |          -24.4456 |       -3.2011 |                -23.4421 |              15 |
|      4 | Momentum       | 2020-06-12    | 2022-05-18  | 2022-05-19   | 2022-11-10 | SMA_30_90           |           -0.7695 |          -17.4128 |       -1.1613 |                -30.2313 |               9 |
|      4 | Mean Reversion | 2020-06-12    | 2022-05-18  | 2022-05-19   | 2022-11-10 | Z_30_1.5            |           -0.4557 |          -17.2287 |       -2.218  |                -19.6556 |              18 |
|      5 | Momentum       | 2020-12-07    | 2022-11-10  | 2022-11-11   | 2023-05-05 | SMA_10_40           |           -0.4995 |          -11.8275 |       -1.4767 |                -15.3598 |              13 |
|      5 | Mean Reversion | 2020-12-07    | 2022-11-10  | 2022-11-11   | 2023-05-05 | Z_30_1.5            |           -0.973  |            0.2381 |        0.1019 |                 -4.0598 |              19 |
|      6 | Momentum       | 2021-06-01    | 2023-05-05  | 2023-05-08   | 2023-10-30 | SMA_10_40           |           -0.5223 |          -16.257  |       -1.8451 |                -21.8715 |              13 |
|      6 | Mean Reversion | 2021-06-01    | 2023-05-05  | 2023-05-08   | 2023-10-30 | Z_30_0.75           |           -1.1505 |            9.6008 |        1.2789 |                 -6.3243 |              32 |
|      7 | Momentum       | 2021-11-24    | 2023-10-30  | 2023-10-31   | 2024-04-23 | SMA_10_40           |           -0.4094 |            1.2408 |        0.224  |                 -7.7911 |               5 |
|      7 | Mean Reversion | 2021-11-24    | 2023-10-30  | 2023-10-31   | 2024-04-23 | Z_30_0.75           |           -0.8949 |           -0.2405 |        0.0517 |                -10.6752 |              32 |

## Assumptions and limitations

- **Educational return proxy, not contract-level futures P&L.** No expiry/roll P&L, tick multipliers, realistic fills, margin, funding, or market impact.
- All indicators are trailing; positions at each date use the previous observation’s closing signal.
- Fold tests start flat and charge first-day entry turnover; an explicit exit cost after the final day of a fold is not modeled.
- Selected parameter sets use ONLY their corresponding training windows; no test returns enter selection.
- Transaction-cost comparisons reuse identical positions (no cost-specific optimization).
- Percentage-based position return model; trading near daily close may not achieve these hypothetical fills.
- Repeatedly reviewing holdout results to invent new rules can still introduce researcher overfitting.
- Artificial input is NOT evidence of real financial market behavior. Sharpe uses zero risk-free rate.
