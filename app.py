from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from black_scholes.analytics import all_greeks, greek_curve, make_spot_grid, payoff_at_expiry, price_curve, price_heatmap


st.set_page_config(page_title='Black-Scholes Visualizer', page_icon='📈', layout='wide')

st.markdown("""
<style>
[data-testid="stToolbar"] {visibility: hidden; height: 0; position: fixed;}
[data-testid="stDecoration"] {visibility: hidden; height: 0; position: fixed;}
[data-testid="stStatusWidget"] {visibility: hidden; height: 0;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def format_metric(value: float, decimals: int = 4) -> str:
    return f'{value:,.{decimals}f}'


def metric_card(label: str, value: float, help_text: str) -> None:
    st.metric(label, format_metric(value), help=help_text)


st.title('Black-Scholes Visualizer')
st.caption('Interactive option pricing dashboard for exploring European call and put prices, Greeks, payoff, and sensitivity.')

with st.sidebar:
    st.header('Parameters')
    option_type = st.segmented_control('Option Type', options=['call', 'put'], default='call')
    spot = st.slider('Spot Price (S)', min_value=20.0, max_value=300.0, value=100.0, step=1.0)
    strike = st.slider('Strike (K)', min_value=20.0, max_value=300.0, value=100.0, step=1.0)
    time_to_maturity = st.slider('Time to Maturity (years)', min_value=0.05, max_value=3.0, value=1.0, step=0.05)
    rate = st.slider('Risk-Free Rate (r)', min_value=0.0, max_value=0.15, value=0.05, step=0.005)
    volatility = st.slider('Volatility (σ)', min_value=0.05, max_value=1.0, value=0.20, step=0.01)
    selected_greek = st.selectbox('Highlighted Greek', ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho'], index=0)
    st.divider()
    st.markdown('### Model Assumptions')
    st.markdown(
        '- European exercise only  \n'
        '- Constant volatility and rates  \n'
        '- No dividends  \n'
        '- Lognormal price dynamics'
    )

spot_grid = make_spot_grid(spot, width=0.7, points=260)
metrics = all_greeks(spot, strike, time_to_maturity, rate, volatility, option_type)
price_values = price_curve(spot_grid, strike, time_to_maturity, rate, volatility, option_type)
highlighted_greek_values = greek_curve(selected_greek, spot_grid, strike, time_to_maturity, rate, volatility, option_type)
payoff_values = payoff_at_expiry(spot_grid, strike, metrics['Price'], option_type)

metric_cols = st.columns(6)
metric_help = {
    'Price': 'Black-Scholes present value for the selected option.',
    'Delta': 'Sensitivity of option price to a $1 change in spot.',
    'Gamma': 'Rate of change of delta with respect to spot.',
    'Vega': 'Sensitivity of option price to a 1.00 change in volatility.',
    'Theta': 'Sensitivity of option price to time decay, in years.',
    'Rho': 'Sensitivity of option price to a 1.00 change in the rate.',
}
for col, label in zip(metric_cols, ['Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']):
    with col:
        metric_card(label, metrics[label], metric_help[label])

left, right = st.columns([1.8, 1.2])
with left:
    tab1, tab2, tab3 = st.tabs(['Price Curve', 'Greek Surface', 'Payoff'])

    with tab1:
        price_df = pd.DataFrame({'Spot': spot_grid, 'Option Price': price_values})
        fig_price = px.line(price_df, x='Spot', y='Option Price', title='Option Value vs Spot Price')
        fig_price.add_trace(
            go.Scatter(
                x=[spot],
                y=[metrics['Price']],
                mode='markers',
                marker=dict(size=12),
                name='Current Selection',
            )
        )
        fig_price.add_vline(x=strike, line_dash='dash', annotation_text='Strike')
        fig_price.update_layout(height=470, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        greek_df = pd.DataFrame({'Spot': spot_grid, selected_greek: highlighted_greek_values})
        fig_greek = px.line(greek_df, x='Spot', y=selected_greek, title=f'{selected_greek} vs Spot Price')
        fig_greek.add_trace(
            go.Scatter(
                x=[spot],
                y=[metrics[selected_greek]],
                mode='markers',
                marker=dict(size=12),
                name='Current Selection',
            )
        )
        fig_greek.add_hline(y=0.0, line_dash='dot')
        fig_greek.update_layout(height=470, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_greek, use_container_width=True)

    with tab3:
        payoff_df = pd.DataFrame({'Spot at Expiry': spot_grid, 'PnL at Expiry': payoff_values})
        fig_payoff = px.line(payoff_df, x='Spot at Expiry', y='PnL at Expiry', title='Expiration Payoff (Long Option)')
        fig_payoff.add_hline(y=0.0, line_dash='dot')
        fig_payoff.add_vline(x=strike, line_dash='dash', annotation_text='Strike')
        fig_payoff.update_layout(height=470, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_payoff, use_container_width=True)

with right:
    st.subheader('Sensitivity Heatmap')
    heatmap_spots = make_spot_grid(spot, width=0.7, points=35)
    heatmap_vols = pd.Series(np.linspace(0.05, 1.0, 28).round(3))
    heatmap_matrix = price_heatmap(heatmap_spots, heatmap_vols.to_numpy(), strike, time_to_maturity, rate, option_type)
    fig_heatmap = px.imshow(
        heatmap_matrix,
        x=[round(v, 1) for v in heatmap_spots],
        y=[round(v, 2) for v in heatmap_vols],
        aspect='auto',
        labels={'x': 'Spot Price', 'y': 'Volatility', 'color': 'Option Price'},
        title='Option Price across Spot × Volatility',
        color_continuous_scale=[
            [0.0, '#b22222'],
            [0.5, '#ffd84d'],
            [1.0, '#228b22'],
        ],
    )
    fig_heatmap.update_traces(
        hovertemplate='Spot: %{x}<br>Volatility: %{y}<br>Option Price: %{z:.4f}<extra></extra>',
        xgap=1,
        ygap=1,
        hoverongaps=False,
    )
    fig_heatmap.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig_heatmap.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig_heatmap.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20), hovermode='closest')
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader('Interpretation')
    moneyness = spot / strike
    stance = 'in the money' if ((option_type == 'call' and spot > strike) or (option_type == 'put' and spot < strike)) else 'out of the money'
    st.markdown(
        f'- Current option is **{stance}** with spot/strike ratio **{moneyness:.3f}**.\n'
        f'- Premium is **{metrics["Price"]:.4f}** under the selected volatility and rate assumptions.\n'
        f'- The highlighted Greek, **{selected_greek}**, updates across the full spot range so you can inspect curvature and nonlinear exposure.\n'
        '- The payoff chart treats the option as a **long position** and subtracts the current premium from intrinsic value at expiry.'
    )
