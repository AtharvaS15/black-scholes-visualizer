from __future__ import annotations

from typing import Literal

import numpy as np

from .core import black_scholes_price, delta, gamma, rho, theta, vega

GreekName = Literal['Delta', 'Gamma', 'Vega', 'Theta', 'Rho']


GREEK_FUNCTIONS = {
    'Delta': delta,
    'Gamma': gamma,
    'Vega': vega,
    'Theta': theta,
    'Rho': rho,
}


def make_spot_grid(center: float, width: float = 0.6, points: int = 250) -> np.ndarray:
    """Build a spot-price grid centered around the current spot."""
    lower = max(1.0, center * (1.0 - width))
    upper = max(lower + 1.0, center * (1.0 + width))
    return np.linspace(lower, upper, points)


def price_curve(
    spot_grid: np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> np.ndarray:
    return black_scholes_price(spot_grid, strike, time_to_maturity, rate, volatility, option_type)


def greek_curve(
    greek_name: GreekName,
    spot_grid: np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> np.ndarray:
    greek_fn = GREEK_FUNCTIONS[greek_name]
    if greek_name in {'Delta', 'Theta', 'Rho'}:
        return greek_fn(spot_grid, strike, time_to_maturity, rate, volatility, option_type)
    return greek_fn(spot_grid, strike, time_to_maturity, rate, volatility)


def all_greeks(
    spot: float,
    strike: float,
    time_to_maturity: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> dict[str, float]:
    return {
        'Price': float(black_scholes_price(spot, strike, time_to_maturity, rate, volatility, option_type)),
        'Delta': float(delta(spot, strike, time_to_maturity, rate, volatility, option_type)),
        'Gamma': float(gamma(spot, strike, time_to_maturity, rate, volatility)),
        'Vega': float(vega(spot, strike, time_to_maturity, rate, volatility)),
        'Theta': float(theta(spot, strike, time_to_maturity, rate, volatility, option_type)),
        'Rho': float(rho(spot, strike, time_to_maturity, rate, volatility, option_type)),
    }


def payoff_at_expiry(
    spot_grid: np.ndarray,
    strike: float,
    premium: float,
    option_type: str,
) -> np.ndarray:
    intrinsic = np.maximum(spot_grid - strike, 0.0) if option_type == 'call' else np.maximum(strike - spot_grid, 0.0)
    return intrinsic - premium


def price_heatmap(
    spot_values: np.ndarray,
    vol_values: np.ndarray,
    strike: float,
    time_to_maturity: float,
    rate: float,
    option_type: str,
) -> np.ndarray:
    matrix = np.empty((len(vol_values), len(spot_values)), dtype=float)
    for i, sigma in enumerate(vol_values):
        matrix[i, :] = black_scholes_price(spot_values, strike, time_to_maturity, rate, float(sigma), option_type)
    return matrix
