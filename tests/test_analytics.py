from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'src'))

from black_scholes.analytics import all_greeks, greek_curve, make_spot_grid, payoff_at_expiry, price_heatmap


def test_make_spot_grid_is_positive_and_sorted():
    grid = make_spot_grid(100.0, width=0.5, points=11)
    assert len(grid) == 11
    assert np.all(grid > 0)
    assert np.all(np.diff(grid) > 0)


def test_all_greeks_contains_expected_fields():
    metrics = all_greeks(100.0, 100.0, 1.0, 0.05, 0.2, 'call')
    assert set(metrics.keys()) == {'Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'}
    assert metrics['Price'] > 0


def test_payoff_matches_intrinsic_minus_premium_for_call():
    spots = np.array([80.0, 100.0, 120.0])
    payoff = payoff_at_expiry(spots, 100.0, premium=10.0, option_type='call')
    assert np.allclose(payoff, np.array([-10.0, -10.0, 10.0]))


def test_greek_curve_and_heatmap_shapes():
    spots = np.linspace(80.0, 120.0, 7)
    vols = np.array([0.1, 0.2, 0.3])
    delta_curve = greek_curve('Delta', spots, 100.0, 1.0, 0.05, 0.2, 'call')
    matrix = price_heatmap(spots, vols, 100.0, 1.0, 0.05, 'call')
    assert delta_curve.shape == spots.shape
    assert matrix.shape == (len(vols), len(spots))
