# Walk-forward evaluation and transaction-cost sensitivity

Rolling training: **504 observations**; test: **126 observations**; roll step: **126 observations**. No overlapping held-out days. Only complete test folds are included.

Parameters selected using **training net Sharpe** at **5 bps**; the next test window is evaluated once without retuning.

## Concatenated out-of-sample results

| strategy       |   test_days |   test_folds |   assumed_cost_bps |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|------------:|-------------:|-------------------:|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Mean Reversion |        1386 |           11 |                  5 |           1386 |            13.8259 |                     27.4519 |                  0.2224 |           -38.919  |             17.9654 |
| Momentum       |        1386 |           11 |                  5 |           1386 |           -20.4128 |                     39.8928 |                  0.0959 |           -71.2367 |             49.4949 |

## Transaction-cost stress test

| strategy       |   cost_bps |   turnover_units |   observations |   total_return_pct |   annualized_volatility_pct |   sharpe_zero_risk_free |   max_drawdown_pct |   positive_days_pct |
|:---------------|-----------:|-----------------:|---------------:|-------------------:|----------------------------:|------------------------:|-------------------:|--------------------:|
| Mean Reversion |          0 |              301 |           1386 |            32.3258 |                     27.4458 |                  0.3222 |           -38.7312 |             18.1818 |
| Mean Reversion |          2 |              301 |           1386 |            24.5912 |                     27.4478 |                  0.2823 |           -38.8064 |             18.0375 |
| Mean Reversion |          5 |              301 |           1386 |            13.8259 |                     27.4519 |                  0.2224 |           -38.919  |             17.9654 |
| Mean Reversion |         10 |              301 |           1386 |            -2.095  |                     27.4619 |                  0.1227 |           -39.1064 |             17.8211 |
| Mean Reversion |         20 |              301 |           1386 |           -27.5843 |                     27.4938 |                 -0.0765 |           -45.4553 |             17.8211 |
| Momentum       |          0 |               73 |           1386 |           -17.4601 |                     39.8967 |                  0.1125 |           -70.4496 |             49.5671 |
| Momentum       |          2 |               73 |           1386 |           -18.6538 |                     39.895  |                  0.1059 |           -70.7669 |             49.5671 |
| Momentum       |          5 |               73 |           1386 |           -20.4128 |                     39.8928 |                  0.0959 |           -71.2367 |             49.4949 |
| Momentum       |         10 |               73 |           1386 |           -23.2625 |                     39.8904 |                  0.0793 |           -72.0035 |             49.4228 |
| Momentum       |         20 |               73 |           1386 |           -28.6666 |                     39.89   |                  0.046  |           -73.4784 |             49.3506 |

## Fold-specific parameters and evaluation

|   fold | strategy       | train_start   | train_end   | test_start   | test_end   | chosen_parameters   |   training_sharpe |   test_return_pct |   test_sharpe |   test_max_drawdown_pct |   test_turnover |
|-------:|:---------------|:--------------|:------------|:-------------|:-----------|:--------------------|------------------:|------------------:|--------------:|------------------------:|----------------:|
|      1 | Momentum       | 2019-01-02    | 2020-12-31  | 2021-01-04   | 2021-07-02 | SMA_10_40           |            0.3137 |           45.6032 |        2.4806 |                -13.269  |               5 |
|      1 | Mean Reversion | 2019-01-02    | 2020-12-31  | 2021-01-04   | 2021-07-02 | Z_15_1.5            |            0.6463 |            6.3491 |        0.802  |                -12.4058 |              37 |
|      2 | Momentum       | 2019-07-03    | 2021-07-02  | 2021-07-06   | 2021-12-31 | SMA_10_40           |            0.4795 |            4.2559 |        0.4059 |                -15.6854 |               7 |
|      2 | Mean Reversion | 2019-07-03    | 2021-07-02  | 2021-07-06   | 2021-12-31 | Z_15_1.5            |            0.8092 |           13.1945 |        1.4263 |                 -9.0395 |              33 |
|      3 | Momentum       | 2020-01-02    | 2021-12-31  | 2022-01-03   | 2022-07-05 | SMA_10_40           |            0.6139 |           23.5711 |        1.0602 |                -36.6866 |               9 |
|      3 | Mean Reversion | 2020-01-02    | 2021-12-31  | 2022-01-03   | 2022-07-05 | Z_15_1.5            |            0.8193 |          -17.3233 |       -1.0539 |                -26.7403 |              22 |
|      4 | Momentum       | 2020-07-06    | 2022-07-05  | 2022-07-06   | 2023-01-03 | SMA_10_40           |            0.6449 |           -4.0678 |        0.0157 |                -25.6471 |               5 |
|      4 | Mean Reversion | 2020-07-06    | 2022-07-05  | 2022-07-06   | 2023-01-03 | Z_15_1              |            0.5053 |           24.4682 |        1.6235 |                -13.2958 |              39 |
|      5 | Momentum       | 2021-01-04    | 2023-01-03  | 2023-01-04   | 2023-07-06 | SMA_10_40           |            0.9094 |          -31.2548 |       -1.9523 |                -36.1561 |              13 |
|      5 | Mean Reversion | 2021-01-04    | 2023-01-03  | 2023-01-04   | 2023-07-06 | Z_15_1              |            0.6914 |            5.6531 |        0.5476 |                -23.9998 |              35 |
|      6 | Momentum       | 2021-07-06    | 2023-07-06  | 2023-07-07   | 2024-01-04 | SMA_30_90           |            0.0353 |          -11.137  |       -0.5784 |                -19.588  |               5 |
|      6 | Mean Reversion | 2021-07-06    | 2023-07-06  | 2023-07-07   | 2024-01-04 | Z_20_1.5            |            0.9889 |           10.8156 |        1.2243 |                 -5.6615 |              34 |
|      7 | Momentum       | 2022-01-03    | 2024-01-04  | 2024-01-05   | 2024-07-08 | SMA_30_90           |            0.3384 |          -17.3271 |       -1.512  |                -20.221  |               5 |
|      7 | Mean Reversion | 2022-01-03    | 2024-01-04  | 2024-01-05   | 2024-07-08 | Z_20_1.5            |            1.068  |           -7.3241 |       -1.1989 |                -14.3636 |              16 |
|      8 | Momentum       | 2022-07-06    | 2024-07-08  | 2024-07-09   | 2025-01-06 | SMA_30_90           |            0.0282 |            4.2535 |        0.4151 |                -15.543  |               5 |
|      8 | Mean Reversion | 2022-07-06    | 2024-07-08  | 2024-07-09   | 2025-01-06 | Z_30_1.5            |            1.6964 |            5.0905 |        0.6997 |                 -7.1876 |              15 |
|      9 | Momentum       | 2023-01-04    | 2025-01-06  | 2025-01-07   | 2025-07-08 | SMA_30_90           |           -0.0637 |           -8.9819 |       -0.3378 |                -28.3821 |               7 |
|      9 | Mean Reversion | 2023-01-04    | 2025-01-06  | 2025-01-07   | 2025-07-08 | Z_30_1.5            |            1.491  |           -0.2061 |        0.1157 |                -14.9891 |              16 |
|     10 | Momentum       | 2023-07-07    | 2025-07-08  | 2025-07-09   | 2026-01-06 | SMA_10_40           |           -0.1061 |           -8.3081 |       -0.5505 |                -16.6416 |               7 |
|     10 | Mean Reversion | 2023-07-07    | 2025-07-08  | 2025-07-09   | 2026-01-06 | Z_30_1.5            |            0.6666 |            0.841  |        0.2191 |                 -5.7364 |              14 |
|     11 | Momentum       | 2024-01-05    | 2026-01-06  | 2026-01-07   | 2026-07-09 | SMA_30_90           |           -0.3224 |            0.65   |        0.3593 |                -38.0851 |               5 |
|     11 | Mean Reversion | 2024-01-05    | 2026-01-06  | 2026-01-07   | 2026-07-09 | Z_15_0.75           |            0.8449 |          -19.927  |       -0.4471 |                -38.919  |              40 |

## Assumptions and limitations

- **Educational return proxy, not contract-level futures P&L.** No expiry/roll P&L, tick multipliers, realistic fills, margin, funding, or market impact.
- All indicators are trailing; positions at each date use the previous observation’s closing signal.
- Fold tests start flat and charge first-day entry turnover; an explicit exit cost after the final day of a fold is not modeled.
- Selected parameter sets use ONLY their corresponding training windows; no test returns enter selection.
- Transaction-cost comparisons reuse identical positions (no cost-specific optimization).
- Percentage-based position return model; trading near daily close may not achieve these hypothetical fills.
- Repeatedly reviewing holdout results to invent new rules can still introduce researcher overfitting.
- Artificial input is NOT evidence of real financial market behavior. Sharpe uses zero risk-free rate.
