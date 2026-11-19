# Quantitative Futures Market Analysis & Strategy Backtesting

A Python-based quantitative research project for analyzing historical futures market data, developing rule-based trading strategies, and evaluating their performance using statistical methods, backtesting, and risk analysis.

The project implements **momentum** and **mean-reversion** strategies, compares their performance across different market conditions, and uses walk-forward validation to assess out-of-sample results. It also examines how transaction costs affect strategy profitability.

## Features

- **Market Data Analysis:** Historical price processing, daily returns, moving averages, rolling volatility, and statistical indicators.
- **Trading Strategies:** Moving-average momentum and Z-score-based mean reversion.
- **Strategy Backtesting:** Historical simulation with position tracking, transaction costs, and performance evaluation.
- **Risk Analysis:** Sharpe ratio, cumulative returns, maximum drawdown, and volatility-regime analysis.
- **Out-of-Sample Testing:** Chronological training and testing splits to evaluate performance on unseen observations.
- **Walk-Forward Optimization:** Rolling training and testing windows with parameter selection performed independently for each fold.
- **Transaction-Cost Sensitivity:** Evaluation of strategy performance under different trading-cost assumptions.
- **Data Visualization:** Price indicators, equity curves, volatility trends, and strategy comparisons.
- **Automated Reporting:** CSV results, performance summaries, and Markdown research reports.

## Tech Stack

- **Language:** Python
- **Libraries:** Pandas, NumPy, Matplotlib, SciPy
- **Data Sources:** Yahoo Finance or user-provided CSV datasets
- **Testing:** Pytest

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd futures_market_research
```

Alternatively, download and extract the project ZIP.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment.

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Usage

### 1. Run with synthetic data

The project includes a synthetic data generator for testing the analysis pipeline without requiring an internet connection.

```bash
python market_research.py --source synthetic
```

Synthetic data are intended for testing functionality and do not represent actual market performance.

### 2. Run with historical market data

Historical futures price series can be obtained through Yahoo Finance.

**Crude Oil Futures:**

```bash
python market_research.py --source yahoo --ticker CL=F --start 2019-01-01 --end 2026-11-01 --output outputs/crude_oil
```

Other example symbols include:

| Symbol | Market |
|---|---|
| `CL=F` | Crude Oil Futures |
| `GC=F` | Gold Futures |
| `ES=F` | E-mini S&P 500 Futures |

Data availability depends on the provider. Downloaded futures series may contain adjusted or stitched contract prices and should not automatically be treated as exchange-accurate continuous futures data.

### 3. Run with a custom dataset

The project supports importing historical prices through a CSV file.

**Required format:**

```csv
Date,Close
2024-01-02,72.5
2024-01-03,72.9
2024-01-04,73.1
```

The dataset should contain at least 300 valid daily observations.

Run:

```bash
python market_research.py --source csv --csv my_prices.csv --output outputs/my_study
```

For futures contract datasets, document contract identifiers, expiration and roll dates, price adjustment methods, and whether the observations represent settlement or last-traded prices.

---

## Trading Strategies

### 1. Moving-Average Momentum

The momentum strategy uses two simple moving averages to identify the direction of the market.

The moving average over a window of length \(n\) is:

\[
SMA_n(t)=\frac{1}{n}\sum_{i=0}^{n-1}P_{t-i}
\]

where \(P_t\) represents the closing price at time \(t\).

**Trading rules:**

- Long position when the short-term SMA exceeds the long-term SMA.
- Short position when the short-term SMA falls below the long-term SMA.
- No position before sufficient historical observations become available.

The default implementation uses a 20-day short-term moving average and a 60-day long-term moving average.

### 2. Z-Score Mean Reversion

The mean-reversion strategy identifies prices that deviate significantly from their recent average.

The rolling Z-score is calculated as:

\[
Z_t=\frac{P_t-\mu_t}{\sigma_t}
\]

where:

- \(P_t\): Current price
- \(\mu_t\): Rolling mean price
- \(\sigma_t\): Rolling standard deviation

**Trading rules:**

- Long position when \(Z_t\) is below −1.
- Short position when \(Z_t\) is above +1.
- Flat position when the Z-score is between the thresholds.

The default implementation uses a 20-day rolling window.

Both strategies generate signals using information available at the current close, with exposure applied to the following return observation to avoid same-observation look-ahead bias.

---

## Backtesting Methodology

The backtesting engine evaluates the performance of both strategies using historical percentage price returns and predefined position rules.

### Return calculation

Daily simple returns are calculated as:

\[
r_t=\frac{P_t-P_{t-1}}{P_{t-1}}
\]

Strategy gross returns are based on the position held over the corresponding return interval.

Trading costs are deducted according to changes in position:

\[
r_t^{net}=r_t^{gross}-c|w_t-w_{t-1}|
\]

where:

- \(w_t\): Trading position, ranging from −1 to +1
- \(c\): Transaction cost per unit change in exposure
- \(r_t^{net}\): Net daily strategy return

The default transaction cost is **5 basis points per unit of turnover**.

A direct change from long to short therefore incurs twice the cost of entering a long position from flat.

### Development and out-of-sample testing

For the standard backtest, the dataset is split chronologically:

| Dataset | Allocation | Purpose |
|---|---:|---|
| Development | 70% | Strategy development and analysis |
| Out-of-sample | 30% | Evaluation on later observations |

Test observations are not used for parameter selection.

## Walk-Forward Validation

Walk-forward validation provides a rolling framework for evaluating trading strategies under changing market conditions.

Instead of relying exclusively on a single development and test split, the algorithm repeatedly selects strategy parameters using historical training data and evaluates them on the subsequent unseen observations.

### Configuration

| Parameter | Default |
|---|---|
| Training window | 504 observations |
| Testing window | 126 observations |
| Window advancement | 126 observations |
| Optimization metric | Training net Sharpe ratio |
| Transaction cost | 5 basis points |

### Parameter Search

**Momentum strategy:**

The following short-term and long-term SMA combinations are evaluated:

- (10, 40)
- (20, 60)
- (30, 90)

**Mean-reversion strategy:**

Rolling windows:

- 15, 20, 30 observations

Z-score thresholds:

- 0.75, 1.0, 1.5

For each training fold, the parameter combination achieving the highest training-period net Sharpe ratio is selected.

The chosen parameters are then applied to the next test period without further adjustment.

### Run walk-forward analysis

Using synthetic data:

```bash
python market_research.py --source synthetic --walk-forward --output outputs/synthetic_walk_forward
```

Using historical crude oil futures proxy data:

```bash
python market_research.py \
  --source yahoo \
  --ticker CL=F \
  --start 2019-01-01 \
  --end 2026-11-01 \
  --walk-forward \
  --wf-train 504 \
  --wf-test 126 \
  --cost-bps 5 \
  --cost-grid 0,2,5,10,20 \
  --output outputs/crude_oil
```

All test folds are non-overlapping. Their returns are combined to calculate the overall held-out performance.

## Transaction-Cost Sensitivity Analysis

Transaction costs can significantly affect trading strategies, particularly those that frequently change positions.

The project evaluates strategy performance at the following assumed trading costs:

| Cost (basis points) | Cost per unit turnover |
|---|---:|
| 0 | 0.00% |
| 2 | 0.02% |
| 5 | 0.05% |
| 10 | 0.10% |
| 20 | 0.20% |

Previously selected trading positions remain unchanged across these experiments.

This allows the effect of transaction costs to be examined independently of strategy reoptimization.

The analysis generates a comparison of net returns and risk-adjusted performance under each cost assumption.

---

## Performance Metrics

The project evaluates strategies using several financial performance measures.

### Cumulative Return

Measures the compounded return over the evaluation period.

\[
R_{cum}=\prod_{t=1}^{T}(1+r_t)-1
\]

### Sharpe Ratio

Measures average excess return relative to return volatility.

\[
Sharpe=\frac{\bar r-r_f}{\sigma_r}\sqrt{252}
\]

The implementation assumes a zero risk-free rate and 252 trading observations per year.

### Maximum Drawdown

Measures the largest decline from a previous equity peak.

\[
MDD=\min_t\left(\frac{E_t}{\max_{s\leq t}E_s}-1\right)
\]

where \(E_t\) represents the cumulative equity value.

### Volatility Analysis

Rolling volatility is used to examine how market variability changes over time.

The project also compares performance across relatively high- and low-volatility conditions using a development-period volatility threshold.

---

## Generated Outputs

After execution, the project saves analysis results to the specified output directory.

### Standard Backtest

| File | Description |
|---|---|
| `REPORT.md` | Analysis methodology, results and limitations |
| `strategy_metrics.csv` | Development and out-of-sample performance |
| `volatility_regimes.csv` | Performance across volatility regimes |
| `analyzed_data.csv` | Cleaned prices, indicators, returns and signals |
| `price_indicators.png` | Price series with strategy indicators |
| `equity_curves.png` | Cumulative strategy performance |
| `volatility.png` | Historical rolling volatility |

### Walk-Forward Analysis

| File | Description |
|---|---|
| `WALK_FORWARD_REPORT.md` | Walk-forward methodology and results |
| `walk_forward_folds.csv` | Selected parameters and results for each fold |
| `walk_forward_daily.csv` | Held-out positions, turnover, gross and net returns |
| `walk_forward_summary.csv` | Aggregate out-of-sample performance |
| `transaction_cost_sensitivity.csv` | Performance under different transaction costs |
| `walk_forward_equity.png` | Walk-forward equity curves and fold boundaries |
| `transaction_cost_sensitivity.png` | Transaction-cost sensitivity visualization |

## Testing

The project includes automated tests for data processing, strategy calculations, backtesting behavior, and walk-forward analysis.

Run the test suite using:

```bash
python -m pytest -q
```

## Assumptions and Limitations

This project uses a simplified quantitative backtesting framework intended for historical strategy research.

The following assumptions apply:

- Strategy returns are modeled using percentage price changes rather than actual futures contract-level profit and loss.
- Positions are represented as normalized exposures of −1, 0, or +1.
- Transaction costs are approximated using a fixed basis-point model.
- Actual exchange fees, bid-ask spreads, slippage, margin requirements, contract multipliers, and variation margin are not individually modeled.
- Futures expiration and contract-roll economics are not explicitly simulated.
- Adjusted or combined historical contract series may differ from tradable futures prices.
- Walk-forward testing reduces some forms of look-ahead bias but does not eliminate overfitting or data-mining risk.
- Each walk-forward fold begins with an assumed flat position and pays the corresponding entry cost; an explicit end-of-fold liquidation cost is not modeled.
- Synthetic data are used only for testing and demonstration.

Backtested results are sensitive to market conditions, model assumptions, data quality, and transaction costs. Historical performance does not guarantee future results.

## Future Improvements

Potential extensions include:

1. **Contract-Level Futures Backtesting:** Incorporate tick sizes, contract multipliers, expiration dates, roll schedules, and margin requirements.
2. **Multi-Asset Analysis:** Compare strategy behavior across energy, metals, equity-index, and other futures markets.
3. **Market Regime Detection:** Investigate volatility clustering and changing market regimes using statistical models.
4. **Walk-Forward Window Sensitivity:** Compare different training and testing window lengths.
5. **Statistical Significance Testing:** Introduce bootstrap methods, randomized strategy benchmarks, and additional tests for false discoveries.
6. **Portfolio Risk Management:** Implement volatility targeting, position sizing, and portfolio-level exposure constraints.

## Disclaimer

This repository is intended for educational and research purposes. It does not provide investment advice or a production-ready trading system. All results should be interpreted in the context of the underlying data, methodology, and modeling assumptions.