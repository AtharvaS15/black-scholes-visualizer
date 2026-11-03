![Dashboard Screenshot](./images/Black_Scholes_Visualizer_Dashboard.png)

# Options Market Visualizer — Pricing & Greeks

An interactive Streamlit dashboard for Black–Scholes pricing of European calls and puts. Change spot price, strike, volatility, time to expiration, and risk-free rate to see how theoretical option values, all five Greeks, payoff profiles, and spot–volatility sensitivity heatmaps respond. This is a model-driven visualizer, not a live market data feed.

## Features
- Adjustable parameters for spot, strike, time to maturity, rate, volatility, and option type
- Dashboard-style metric cards for price, Delta, Gamma, Vega, Theta, and Rho
- Interactive charts for price curves, Greek exposure, and expiration payoff
- Heatmap showing option price across spot–volatility scenarios
- Modular structure separating pricing logic, analytics, and UI

## Tech Stack
- Python
- NumPy
- Pandas
- Plotly
- Streamlit
- Pytest

## Project Structure
black_scholes_visualizer/
├── app.py
├── README.md
├── requirements.txt
├── src/
│   └── black_scholes/
│       ├── __init__.py
│       ├── analytics.py
│       └── core.py
└── tests/
    ├── test_analytics.py
    └── test_core.py

## Why I Built This
I built this project to better understand how option prices and Greeks behave across different scenarios, not just at a single point. Most explanations of Black-Scholes focus on the formula, but in practice what matters is how price and sensitivities change when volatility, time, or the underlying price changes. This dashboard was designed to make those relationships visual and interactive instead of purely theoretical.