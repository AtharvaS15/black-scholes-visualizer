from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'src'))

from black_scholes.core import black_scholes_price, delta, gamma, rho, theta, vega


def test_call_put_prices_are_positive():
    call = float(black_scholes_price(100, 100, 1.0, 0.05, 0.2, 'call'))
    put = float(black_scholes_price(100, 100, 1.0, 0.05, 0.2, 'put'))
    assert call > 0
    assert put > 0


def test_put_call_parity():
    s = 100
    k = 100
    t = 1.0
    r = 0.05
    sigma = 0.2
    call = float(black_scholes_price(s, k, t, r, sigma, 'call'))
    put = float(black_scholes_price(s, k, t, r, sigma, 'put'))
    lhs = call - put
    rhs = s - k * (2.718281828459045 ** (-r * t))
    assert abs(lhs - rhs) < 1e-4


def test_greeks_have_expected_signs_for_call():
    s = 100
    k = 100
    t = 1.0
    r = 0.05
    sigma = 0.2
    assert float(delta(s, k, t, r, sigma, 'call')) > 0
    assert float(gamma(s, k, t, r, sigma)) > 0
    assert float(vega(s, k, t, r, sigma)) > 0
    assert float(theta(s, k, t, r, sigma, 'call')) < 0
    assert float(rho(s, k, t, r, sigma, 'call')) > 0
