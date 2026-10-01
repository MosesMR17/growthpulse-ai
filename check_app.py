import os
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

from modules.backtest.engine import run_momentum_backtest

# --- Page Config ---
st.set_page_config(page_title="Quantitative Momentum Dashboard", layout="wide")

st.title("📈 Quantitative Momentum & Backtest Engine")
st.write("Welcome to your institutional-grade momentum screening and backtesting platform.")

# --- Backtest Section ---
st.header("📊 Strategy Backtest Engine")
ticker_input = st.text_input("Enter Ticker for Backtest", value="AAPL").upper()
lookback = st.slider("Momentum Lookback Window (Days)", min_value=5, max_value=100, value=20)

if st.button("Run Backtest"):
    with st.spinner(f"Fetching data and running backtest for {ticker_input}..."):
        try:
            # Fetch 1 year of historical daily data safely
            data = yf.download(ticker_input, period="1y", interval="1d", progress=False)
        except Exception as e:
            data = pd.DataFrame()

        if not data.empty:
            # Handle multi-index columns if returned by newer yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                prices = data['Close'].iloc[:, 0]
            else:
                prices = data['Close']
                
            # Run simulation
            results = run_momentum_backtest(prices, lookback_window=lookback)
            
            # Plot performance using Plotly
            fig = px.line(
                results, 
                y=['Buy_Hold_Cum', 'Strategy_Cum'],
                labels={'value': 'Growth of $1', 'index': 'Date', 'variable': 'Strategy'},
                title=f"Momentum Strategy vs Buy & Hold ({ticker_input})"
            )
            fig.update_layout(legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1})
            st.plotly_chart(fig, use_container_width=True)
            
            # Show final metrics
            final_bh = results['Buy_Hold_Cum'].iloc[-1] - 1
            final_strat = results['Strategy_Cum'].iloc[-1] - 1
            
            col1, col2 = st.columns(2)
            col1.metric("Buy & Hold Return", f"{final_bh:.2%}")
            col2.metric("Momentum Strategy Return", f"{final_strat:.2%}")
        else:
            st.error(f"Could not retrieve data for '{ticker_input}'. Please check the ticker symbol or try another one.")
