"""Rolling training windows, strictly chronological tests and fixed-trade cost stress tests.

Educational percentage-return proxy; not an executable futures-contract simulator.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from market_research import indicators, metrics, TRADING_DAYS


def candidate_signals(prices: pd.DataFrame) -> dict[str, dict[str, pd.DataFrame]]:
    """Candidate indicators use trailing price observations only (no future data)."""
    out = {'Momentum': {}, 'Mean Reversion': {}}
    for fast, slow in [(10, 40), (20, 60), (30, 90)]:
        d = indicators(prices, fast=fast, slow=slow)
        out['Momentum'][f'SMA_{fast}_{slow}'] = d[['return', 'momentum_signal']].rename(columns={'momentum_signal': 'signal'})
    for window in [15, 20, 30]:
        d = indicators(prices, zwindow=window)
        for z in [0.75, 1.0, 1.5]:
            v = d[['return']].copy()
            v['signal'] = np.select([d['zscore'] < -z, d['zscore'] > z], [1., -1.], default=0.)
            out['Mean Reversion'][f'Z_{window}_{z:g}'] = v
    return out


def window_backtest(candidate: pd.DataFrame, start: int, stop: int, cost_bps: float) -> pd.DataFrame:
    """Reinitialize to flat at start; first exposure uses prior CLOSE signal.

    A first-day entry is charged even if the previous window held a position.
    Independent windows assume liquidation/position reset between windows; exit
    cost at previous window's end is NOT charged (stated limitation).
    """
    if cost_bps < 0 or not np.isfinite(cost_bps):
        raise ValueError('cost_bps must be finite and nonnegative')
    if not (0 <= start < stop <= len(candidate)):
        raise ValueError('Invalid window bounds')
    s = candidate.iloc[start:stop].copy()
    s['position'] = candidate['signal'].shift(1).iloc[start:stop].fillna(0.).to_numpy()
    s['turnover'] = s['position'].diff().abs()
    s.iloc[0, s.columns.get_loc('turnover')] = abs(s['position'].iloc[0])
    s['gross_return'] = s['position'] * s['return']
    s['trading_cost'] = s['turnover'] * cost_bps / 10_000
    s['net_return'] = s['gross_return'] - s['trading_cost']
    s['equity'] = (1+s['net_return']).cumprod()
    return s


def walk_forward(prices: pd.DataFrame, train_bars: int = 504, test_bars: int = 126,
                 step_bars: int | None = None, base_cost_bps: float = 5.,
                 costs_bps: tuple[float, ...] = (0., 2., 5., 10., 20.)) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Optimize on each trailing training set, deploy once on next held-out block.

    Candidate selection is training-only, net Sharpe-maximizing. No optimization
    uses a held-out return. Cost grid is applied *after* selecting trades at base
    cost: transaction-cost stress tests do not retune the strategy.
    """
    if step_bars is None:
        step_bars = test_bars
    if train_bars < 100 or test_bars < 20 or step_bars != test_bars:
        raise ValueError('Use train_bars>=100, test_bars>=20, step_bars=test_bars (nonoverlapping).')
    if len(prices) < train_bars + test_bars:
        raise ValueError('Need at least one full training and test window.')
    if not costs_bps or any(c < 0 or not np.isfinite(c) for c in costs_bps):
        raise ValueError('Cost grid must contain finite nonnegative values.')
    if base_cost_bps < 0 or not np.isfinite(base_cost_bps):
        raise ValueError('Invalid base trading cost.')
    candidates = candidate_signals(prices)
    folds, daily = [], []
    fold = 0
    for test_start in range(train_bars, len(prices), step_bars):
        test_stop = min(test_start+test_bars, len(prices))
        if test_stop-test_start < test_bars:  # Discard final incomplete held-out fold
            break
        train_start = test_start-train_bars
        fold += 1
        for strategy, choices in candidates.items():
            training = []
            for key, series in choices.items():
                fitted = window_backtest(series, train_start, test_start, base_cost_bps)
                met = metrics(fitted['net_return'])
                score = met['sharpe_zero_risk_free']
                score = float(score) if np.isfinite(score) else -1e9
                training.append((score, key))
            best_score, best_key = max(training, key=lambda x: (x[0], x[1]))
            tested = window_backtest(choices[best_key], test_start, test_stop, base_cost_bps)
            observed = metrics(tested['net_return'])
            folds.append({
                'fold':fold,'strategy':strategy,'train_start':prices.index[train_start].date().isoformat(),
                'train_end':prices.index[test_start-1].date().isoformat(),
                'test_start':prices.index[test_start].date().isoformat(),
                'test_end':prices.index[test_stop-1].date().isoformat(),
                'chosen_parameters':best_key, 'training_sharpe':best_score,
                'test_return_pct':observed['total_return_pct'],
                'test_sharpe':observed['sharpe_zero_risk_free'],
                'test_max_drawdown_pct':observed['max_drawdown_pct'],
                'test_turnover':float(tested['turnover'].sum()),
            })
            recorded = tested[['return','position','turnover','gross_return','trading_cost','net_return']].copy()
            recorded['fold'] = fold
            recorded['strategy'] = strategy
            recorded['parameters'] = best_key
            recorded.index.name = 'Date'
            daily.append(recorded.reset_index())
    if not folds:
        raise ValueError('No completed test folds found.')
    folds_df = pd.DataFrame(folds)
    daily_df = pd.concat(daily, ignore_index=True)
    summary, sensitivity = [], []
    for strategy, df in daily_df.groupby('strategy', sort=True):
        df = df.sort_values('Date').copy()
        summary.append({'strategy':strategy,'test_days':len(df),'test_folds':df['fold'].nunique(),
                        'assumed_cost_bps':base_cost_bps,
                        **metrics(df['net_return'])})
        for cost in sorted(set(costs_bps) | {base_cost_bps}):
            stressed = df['gross_return'] - df['turnover'] * cost / 10000.
            sensitivity.append({'strategy':strategy,'cost_bps':cost,
                                'turnover_units':float(df['turnover'].sum()),
                                **metrics(stressed)})
    return folds_df, daily_df, pd.DataFrame(summary), pd.DataFrame(sensitivity)


def export_walk_forward(prices: pd.DataFrame, output: Path, train_bars: int = 504,
                        test_bars: int = 126, cost_bps: float = 5.,
                        cost_grid: tuple[float, ...] = (0.,2.,5.,10.,20.)) -> None:
    output.mkdir(parents=True, exist_ok=True)
    folds, daily, summary, stress = walk_forward(prices, train_bars, test_bars, test_bars, cost_bps, cost_grid)
    folds.to_csv(output/'walk_forward_folds.csv', index=False)
    daily.to_csv(output/'walk_forward_daily.csv', index=False)
    summary.to_csv(output/'walk_forward_summary.csv', index=False)
    stress.to_csv(output/'transaction_cost_sensitivity.csv', index=False)

    plt.figure(figsize=(11,5))
    for strategy, group in daily.groupby('strategy'):
        group = group.sort_values('Date')
        plt.plot(group['Date'], (1+group['net_return']).cumprod(), label=strategy)
    for date in folds.query('strategy == "Momentum"')['test_start'].iloc[1:]:
        plt.axvline(pd.Timestamp(date), alpha=.12, color='grey')
    plt.title(f'Walk-forward held-out equity curves ({cost_bps:g} bps/unit turnover)')
    plt.ylabel('Growth of 1 unit'); plt.legend(); plt.tight_layout()
    plt.savefig(output/'walk_forward_equity.png', dpi=145); plt.close()

    plt.figure(figsize=(9,5))
    for strategy, group in stress.groupby('strategy'):
        plt.plot(group['cost_bps'], group['total_return_pct'], marker='o', label=strategy)
    plt.axhline(0, color='grey', linewidth=.8)
    plt.xlabel('Trading cost (basis points per unit turnover)')
    plt.ylabel('Total held-out net return (%)')
    plt.title('Cost sensitivity: same trades, no retuning'); plt.legend(); plt.tight_layout()
    plt.savefig(output/'transaction_cost_sensitivity.png', dpi=145); plt.close()

    with (output/'WALK_FORWARD_REPORT.md').open('w', encoding='utf-8') as f:
        f.write('# Walk-forward evaluation and transaction-cost sensitivity\n\n'
                f'Rolling training: **{train_bars} observations**; test: **{test_bars} observations**; '
                f'roll step: **{test_bars} observations**. No overlapping held-out days. '
                f'Only complete test folds are included.\n\n'
                f'Parameters selected using **training net Sharpe** at **{cost_bps:g} bps**; '
                'the next test window is evaluated once without retuning.\n\n'
                '## Concatenated out-of-sample results\n\n'+summary.round(4).to_markdown(index=False)+'\n\n'
                '## Transaction-cost stress test\n\n'+stress.round(4).to_markdown(index=False)+'\n\n'
                '## Fold-specific parameters and evaluation\n\n'+folds.round(4).to_markdown(index=False)+'\n\n'
                '## Assumptions and limitations\n\n'
                '- **Educational return proxy, not contract-level futures P&L.** No expiry/roll P&L, tick multipliers, realistic fills, margin, funding, or market impact.\n'
                '- All indicators are trailing; positions at each date use the previous observation’s closing signal.\n'
                '- Fold tests start flat and charge first-day entry turnover; an explicit exit cost after the final day of a fold is not modeled.\n'
                '- Selected parameter sets use ONLY their corresponding training windows; no test returns enter selection.\n'
                '- Transaction-cost comparisons reuse identical positions (no cost-specific optimization).\n'
                '- Percentage-based position return model; trading near daily close may not achieve these hypothetical fills.\n'
                '- Repeatedly reviewing holdout results to invent new rules can still introduce researcher overfitting.\n'
                '- Artificial input is NOT evidence of real financial market behavior. Sharpe uses zero risk-free rate.\n')
    print('\nWALK-FORWARD OUT-OF-SAMPLE SUMMARY\n',summary.round(3).to_string(index=False))
    print('\nCOST SENSITIVITY\n',stress[['strategy','cost_bps','total_return_pct','max_drawdown_pct']].round(3).to_string(index=False))
