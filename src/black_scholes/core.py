from __future__ import annotations

from math import erf, exp, log, pi, sqrt
from typing import Literal

import numpy as np

OptionType = Literal['call', 'put']
_EPS = 1e-12


def _to_array(x: float | np.ndarray) -> np.ndarray:
    return np.asarray(x, dtype=float)


def _norm_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x**2) / sqrt(2 * pi)


def _norm_cdf(x: np.ndarray) -> np.ndarray:
    vec_erf = np.vectorize(erf)
    return 0.5 * (1.0 + vec_erf(x / sqrt(2.0)))


def _validate_inputs(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
) -> tuple[np.ndarray, float, float, float, float]:
    s = np.maximum(_to_array(spot), _EPS)
    k = max(float(strike), _EPS)
    t = max(float(time_to_maturity), _EPS)
    r = float(rate)
    sigma = max(float(volatility), _EPS)
    return s, k, t, r, sigma


def _d1_d2(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float, float, float]:
    s, k, t, r, sigma = _validate_inputs(spot, strike, time_to_maturity, rate, volatility)
    sqrt_t = sqrt(t)
    d1 = (np.log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return d1, d2, s, k, t, r, sigma


def black_scholes_price(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = 'call',
) -> np.ndarray:
    d1, d2, s, k, t, r, _ = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    disc_k = k * exp(-r * t)
    if option_type == 'call':
        return s * _norm_cdf(d1) - disc_k * _norm_cdf(d2)
    if option_type == 'put':
        return disc_k * _norm_cdf(-d2) - s * _norm_cdf(-d1)
    raise ValueError("option_type must be 'call' or 'put'")


def delta(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = 'call',
) -> np.ndarray:
    d1, _, *_ = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    if option_type == 'call':
        return _norm_cdf(d1)
    if option_type == 'put':
        return _norm_cdf(d1) - 1.0
    raise ValueError("option_type must be 'call' or 'put'")


def gamma(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
) -> np.ndarray:
    d1, _, s, _, t, _, sigma = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    return _norm_pdf(d1) / (s * sigma * sqrt(t))


def vega(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
) -> np.ndarray:
    d1, _, s, _, t, _, _ = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    return s * _norm_pdf(d1) * sqrt(t)


def theta(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = 'call',
) -> np.ndarray:
    d1, d2, s, k, t, r, sigma = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    first_term = -(s * _norm_pdf(d1) * sigma) / (2.0 * sqrt(t))
    if option_type == 'call':
        return first_term - r * k * exp(-r * t) * _norm_cdf(d2)
    if option_type == 'put':
        return first_term + r * k * exp(-r * t) * _norm_cdf(-d2)
    raise ValueError("option_type must be 'call' or 'put'")


def rho(
    spot: float | np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = 'call',
) -> np.ndarray:
    _, d2, _, k, t, r, _ = _d1_d2(spot, strike, time_to_maturity, rate, volatility)
    if option_type == 'call':
        return k * t * exp(-r * t) * _norm_cdf(d2)
    if option_type == 'put':
        return -k * t * exp(-r * t) * _norm_cdf(-d2)
    raise ValueError("option_type must be 'call' or 'put'")
