"""Educational futures-market strategy research. Not a contract-level trading simulator."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TRADING_DAYS = 252


def synthetic_prices(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Clearly artificial data with changing volatility and return patterns."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2019-01-01', periods=n)
    logret = np.empty(n)
    logret[0] = 0.0
    for i in range(1, n):
        vol = 0.007 if i < n//3 else (0.018 if i < 2*n//3 else 0.011)
        persistence = 0.18 if i < 2*n//3 else -0.15
        logret[i] = persistence*logret[i-1] + rng.normal(0, vol)
    close = 70 * np.exp(np.cumsum(logret))
    return pd.DataFrame({'Close': close}, index=dates)


def load_prices(source: str, ticker: str, start: str, end: str, csv_path: str | None) -> pd.DataFrame:
    if source == 'synthetic':
        return synthetic_prices()
    if source == 'csv':
        if not csv_path:
            raise ValueError('--csv is required when --source csv')
        raw = pd.read_csv(csv_path)
        norm = {c.lower().strip(): c for c in raw.columns}
        if not {'date', 'close'} <= set(norm):
            raise ValueError('CSV needs Date and Close columns (case-insensitive).')
        df = raw[[norm['date'], norm['close']]].copy()
        df.columns = ['Date', 'Close']
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        return clean_prices(df.set_index('Date'))
    if source == 'yahoo':
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError('Install dependencies: pip install -r requirements.txt') from exc
        raw = yf.download(ticker, start=start, end=end, interval='1d',
                          auto_adjust=False, progress=False, multi_level_index=False)
        if raw.empty:
            raise RuntimeError('No historical data returned. Check ticker/dates/network.')
        return clean_prices(raw[['Close']])
    raise ValueError(f'Unknown source: {source}')


def clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    x = df[['Close']].copy()
    x.index = pd.to_datetime(x.index, errors='coerce')
    if getattr(x.index, 'tz', None) is not None:
        x.index = x.index.tz_localize(None)
    x['Close'] = pd.to_numeric(x['Close'], errors='coerce')
    x = x.loc[~x.index.isna()].sort_index()
    if x.index.has_duplicates:
        raise ValueError('Duplicate timestamps found. Resolve them before backtesting.')
    x = x.dropna(subset=['Close'])
    x = x[x['Close'] > 0]
    if len(x) < 300:
        raise ValueError(f'Only {len(x)} usable rows. Need at least 300.')
    return x


def indicators(df: pd.DataFrame, fast: int = 20, slow: int = 60, zwindow: int = 20) -> pd.DataFrame:
    x = clean_prices(df)
    x['return'] = x['Close'].pct_change().fillna(0.0)
    x['vol20'] = x['return'].rolling(20, min_periods=20).std() * np.sqrt(TRADING_DAYS)
    x['sma_fast'] = x['Close'].rolling(fast, min_periods=fast).mean()
    x['sma_slow'] = x['Close'].rolling(slow, min_periods=slow).mean()
    mean = x['Close'].rolling(zwindow, min_periods=zwindow).mean()
    std = x['Close'].rolling(zwindow, min_periods=zwindow).std()
    x['zscore'] = ((x['Close'] - mean) / std.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    # Signals computed at close t, traded starting next bar t+1.
    x['momentum_signal'] = np.where(x['sma_fast'] > x['sma_slow'], 1.0, -1.0)
    x.loc[x['sma_slow'].isna(), 'momentum_signal'] = 0.0
    x['mean_reversion_signal'] = np.select([x['zscore'] < -1, x['zscore'] > 1], [1.0, -1.0], default=0.0)
    x.loc[x['zscore'].isna(), 'mean_reversion_signal'] = 0.0
    return x


def backtest(df: pd.DataFrame, signal_column: str, cost_bps: float = 5.0) -> pd.DataFrame:
    if cost_bps < 0:
        raise ValueError('Cost must be nonnegative.')
    x = df.copy()
    x['position'] = x[signal_column].shift(1).fillna(0.0)
    x['turnover'] = x['position'].diff().abs().fillna(x['position'].abs())
    x['gross_return'] = x['position'] * x['return']
    x['trading_cost'] = (cost_bps/10000.0) * x['turnover']
    x['net_return'] = x['gross_return'] - x['trading_cost']
    x['equity'] = (1 + x['net_return']).cumprod()
    return x


def metrics(returns: pd.Series) -> dict:
    r = returns.dropna().astype(float)
    if len(r) == 0:
        return {}
    eq = (1+r).cumprod()
    dd = eq / eq.cummax() - 1
    vol = float(r.std(ddof=1) * np.sqrt(TRADING_DAYS)) if len(r)>1 else 0.0
    sharpe = (float(r.mean()) * TRADING_DAYS / vol) if vol > 0 else np.nan
    return {
        'observations': len(r),
        'total_return_pct': float((eq.iloc[-1]-1)*100),
        'annualized_volatility_pct': vol*100,
        'sharpe_zero_risk_free': sharpe,
        'max_drawdown_pct': float(dd.min()*100),
        'positive_days_pct': float((r>0).mean()*100),
    }


def charts(data: pd.DataFrame, strategies: dict[str, pd.DataFrame], split_idx: int, output: Path) -> None:
    plt.figure(figsize=(12,5))
    plt.plot(data.index, data['Close'], label='Close', linewidth=1)
    plt.plot(data.index, data['sma_fast'], label='20-day SMA', alpha=.8)
    plt.plot(data.index, data['sma_slow'], label='60-day SMA', alpha=.8)
    plt.axvline(data.index[split_idx], linestyle='--', label='Test begins')
    plt.title('Price & Trend Indicators'); plt.legend(); plt.tight_layout()
    plt.savefig(output/'price_indicators.png', dpi=145); plt.close()

    plt.figure(figsize=(12,5))
    for name,x in strategies.items():
        plt.plot(x.index, x['equity'], label=name)
    plt.axvline(data.index[split_idx], linestyle='--', label='Test begins')
    plt.title('Cumulative Return (illustrative unit notional, net of assumed costs)')
    plt.ylabel('Growth of 1 unit'); plt.legend(); plt.tight_layout()
    plt.savefig(output/'equity_curves.png', dpi=145); plt.close()

    plt.figure(figsize=(12,4))
    plt.plot(data.index, data['vol20']*100, label='Annualized rolling 20-day volatility')
    plt.axvline(data.index[split_idx], linestyle='--', label='Test begins')
    plt.ylabel('Volatility (%)'); plt.title('Volatility Regimes'); plt.legend(); plt.tight_layout()
    plt.savefig(output/'volatility.png', dpi=145); plt.close()


def execute(source: str='synthetic', ticker: str='CL=F', start: str='2019-01-01',
            end: str='2026-11-01', csv_path: str|None=None, output_dir: str='outputs',
            cost_bps: float=5.0, run_walk_forward: bool=False,
            wf_train: int=504, wf_test: int=126,
            cost_grid: tuple[float, ...]=(0.,2.,5.,10.,20.)) -> pd.DataFrame:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    raw = load_prices(source, ticker, start, end, csv_path)
    data = indicators(raw)
    split_idx = int(len(data)*0.70)
    test_start = data.index[split_idx]
    strategies = {
        'Momentum': backtest(data, 'momentum_signal', cost_bps),
        'Mean Reversion': backtest(data, 'mean_reversion_signal', cost_bps),
    }
    benchmark = data.copy()
    benchmark['buy_hold_signal'] = 1.0
    strategies['Buy and Hold'] = backtest(benchmark, 'buy_hold_signal', cost_bps)
    rows = []
    for label, strategy in strategies.items():
        for period, sub in [('Development', strategy.iloc[:split_idx]), ('Out-of-Sample',strategy.iloc[split_idx:])]:
            rows.append({'strategy':label, 'period':period, **metrics(sub['net_return'])})
    table = pd.DataFrame(rows)
    table.to_csv(out/'strategy_metrics.csv', index=False)
    dataset = data[['Close','return','vol20','zscore','momentum_signal','mean_reversion_signal']]
    dataset.to_csv(out/'analyzed_data.csv', index_label='Date')
    charts(data, strategies, split_idx, out)
    # Regime classification on the entire historical dataset uses a fixed, descriptive
    # cutoff based on development data only (no future threshold leakage).
    threshold = float(data['vol20'].iloc[:split_idx].median())
    regime_rows = []
    for label, strategy in strategies.items():
        test = strategy.iloc[split_idx:].copy()
        test['regime'] = np.where(test['vol20'] > threshold, 'High volatility', 'Low volatility')
        for regime, subset in test.groupby('regime'):
            # Regime-conditioned days are nonconsecutive: risk metrics are descriptive only.
            regime_rows.append({'strategy':label,'regime':regime,
                                'observations':len(subset),
                                'average_daily_net_return_pct':subset['net_return'].mean()*100,
                                'positive_days_pct':(subset['net_return']>0).mean()*100})
    pd.DataFrame(regime_rows).to_csv(out/'volatility_regimes.csv', index=False)
    with (out/'REPORT.md').open('w') as f:
        f.write(f'# Futures Market Strategy Research\n\n'
                f'**Data source:** {source}'+ (' (ARTIFICIAL DATA; not real market evidence)' if source=='synthetic' else '') + '\n\n'
                f'**Instrument:** {ticker if source=="yahoo" else "user CSV" if source=="csv" else "synthetic illustrative series"}\n\n'
                f'**Observations:** {len(data)}; **out-of-sample begins:** {test_start.date()}\n\n'
                f'**Methods:** SMA 20/60 momentum; 20-day z-score mean reversion at ±1; '
                f'signals shifted one trading bar; assumed proportional cost = {cost_bps} bps per unit turnover.\n\n'
                '## Results\n\n'+table.round(3).to_markdown(index=False)+'\n\n'
                '## Interpretation\n\n'
                'Compare out-of-sample returns, drawdowns and stability across volatility regimes. '
                'A higher in-sample Sharpe alone is not evidence of predictive skill.\n\n'
                '## Limitations\n\n'
                '- Educational **percentage-return proxy**, not a tradable futures contract P&L. '
                'No margin, contract multipliers, bid/ask execution, funding, collateral interest, '
                'market impact, contract-specific expiry, or roll P&L.\n'
                '- Yahoo `=F` price histories may be stitched across contracts. Verify continuous-series '
                'construction, adjustments and roll rules against exchange/contract data before making claims.\n'
                '- Daily closes are an approximate execution model. Signals are lagged to avoid same-bar look-ahead; '
                'next-open execution could differ significantly.\n'
                '- Static strategies were not optimized; the 70/30 split is chronological, not randomized.\n'
                '- Risk-free rate assumed zero for Sharpe. This is research, not financial advice.\n')
    if run_walk_forward:
        from walk_forward import export_walk_forward
        export_walk_forward(raw, out, wf_train, wf_test, cost_bps, cost_grid)
    print('\n',table.round(3).to_string(index=False))
    print(f'\nSaved report/charts/CSVs to: {out.resolve()}')
    return table


def main():
    p = argparse.ArgumentParser(description='Educational futures market strategy research')
    p.add_argument('--source', choices=['synthetic','yahoo','csv'], default='synthetic')
    p.add_argument('--ticker', default='CL=F', help='Yahoo ticker, e.g. CL=F, GC=F, ES=F')
    p.add_argument('--start', default='2019-01-01')
    p.add_argument('--end', default='2026-11-01')
    p.add_argument('--csv', default=None, help='CSV with Date and Close columns')
    p.add_argument('--cost-bps', type=float, default=5.0)
    p.add_argument('--output', default='outputs')
    p.add_argument('--walk-forward', action='store_true', help='Run rolling training / held-out folds and transaction cost sensitivity')
    p.add_argument('--wf-train', type=int, default=504, help='Number of trailing observations for each training fold')
    p.add_argument('--wf-test', type=int, default=126, help='Number of held-out observations per fold')
    p.add_argument('--cost-grid', default='0,2,5,10,20', help='Comma-separated bps per turnover unit; never retunes holdout trades')
    args = p.parse_args()
    try:
        grid = tuple(float(v.strip()) for v in args.cost_grid.split(',') if v.strip())
    except ValueError as exc:
        p.error(f'Invalid --cost-grid: {exc}')
    execute(args.source,args.ticker,args.start,args.end,args.csv,args.output,args.cost_bps,
            args.walk_forward,args.wf_train,args.wf_test,grid)

if __name__ == '__main__':
    main()
