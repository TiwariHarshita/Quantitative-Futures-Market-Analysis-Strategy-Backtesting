import numpy as np
import pandas as pd
import pytest
from market_research import synthetic_prices, indicators, backtest, metrics, clean_prices

def test_synthetic_and_indicators():
    data = indicators(synthetic_prices())
    assert len(data) == 1500
    assert data['momentum_signal'].iloc[:59].eq(0).all()
    assert data['mean_reversion_signal'].isin([-1,0,1]).all()

def test_lag_prevents_lookahead():
    idx = pd.bdate_range('2024-01-01', periods=3)
    data = pd.DataFrame({'return':[0.0, 0.10, -0.10], 'signal':[1, -1, 0]}, index=idx)
    result = backtest(data, 'signal', cost_bps=0)
    assert result['position'].tolist() == [0,1,-1]
    assert np.allclose(result['net_return'].to_numpy(), [0,.1,.1])

def test_cost_for_reversal():
    idx = pd.bdate_range('2024-01-01', periods=3)
    data = pd.DataFrame({'return':[0.,0.,0.], 'signal':[1.,-1.,0.]},index=idx)
    x = backtest(data,'signal',cost_bps=5)
    assert np.allclose(x['trading_cost'],[0,.0005,.001])

def test_metrics():
    result = metrics(pd.Series([0.01,-.02,.03]))
    assert result['observations'] == 3
    assert result['max_drawdown_pct'] < 0

def test_reject_duplicate_dates():
    d = pd.DataFrame({'Close':np.ones(320)}, index=[pd.Timestamp('2024-01-01')]*320)
    with pytest.raises(ValueError,match='Duplicate'):
        clean_prices(d)

from walk_forward import candidate_signals, window_backtest, walk_forward

def test_walk_forward_nonoverlap_and_oos_dates():
    raw = synthetic_prices(n=900)
    folds, daily, summary, sensitivity = walk_forward(raw, train_bars=300, test_bars=100)
    assert len(folds) == 12  # 6 folds x 2 strategies
    for strategy, subset in daily.groupby('strategy'):
        assert subset['Date'].is_unique
        assert len(subset) == 600
    assert (pd.to_datetime(folds['train_end']) < pd.to_datetime(folds['test_start'])).all()
    assert len(summary) == 2
    assert (sensitivity['cost_bps'] >= 0).all()

def test_cost_sensitivity_same_positions_and_monotonic_net_returns():
    _, daily, _, stress = walk_forward(synthetic_prices(n=850), 300, 100, costs_bps=(0,5,20))
    for _, sub in stress.groupby('strategy'):
        sub = sub.sort_values('cost_bps')
        assert sub['total_return_pct'].is_monotonic_decreasing
    assert (daily['turnover'] >= 0).all()

def test_first_day_charge_and_one_day_signal_lag():
    dates = pd.bdate_range('2024-01-01', periods=6)
    x = pd.DataFrame({'return':[0,.01,.02,.03,-.01,.02],
                      'signal':[1,1,-1,-1,0,0]}, index=dates)
    test = window_backtest(x,2,5,10)
    assert test['position'].tolist() == [1,-1,-1]
    assert test['turnover'].tolist() == [1,2,0]
    assert np.isclose(test['net_return'].iloc[0], .02 - .001)

def test_parameter_selection_independent_of_future_test_returns():
    raw = synthetic_prices(n=800)
    fold_a, _, _, _ = walk_forward(raw,train_bars=300,test_bars=100)
    changed = raw.copy()
    changed.iloc[310:400,0] *= np.linspace(1,2,90)
    fold_b, _, _, _ = walk_forward(changed,train_bars=300,test_bars=100)
    # The first test fold starts at index 300 and selection is based on rows 0:300.
    a = fold_a.loc[fold_a['fold']==1,'chosen_parameters'].tolist()
    b = fold_b.loc[fold_b['fold']==1,'chosen_parameters'].tolist()
    assert a == b


def test_invalid_walkforward_inputs():
    with pytest.raises(ValueError):
        walk_forward(synthetic_prices(n=300), train_bars=300, test_bars=100)
