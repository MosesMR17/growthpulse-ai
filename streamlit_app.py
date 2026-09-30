import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="Quantitative Momentum & SMC Terminal", layout="wide", initial_sidebar_state="expanded")

# --- High-Tech Terminal CSS Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .stTextInput input, .stSlider, .stSelectbox {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }
    .card-box {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .alert-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #fca5a5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ QUANTITATIVE MOMENTUM & SMC INTELLIGENCE TERMINAL")
st.markdown("---")

# --- Helper Functions for Data & Analysis ---
@st.cache_data
def fetch_market_leaders():
    tickers = ["^GSPC", "^NDX", "SPY", "QQQ", "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD"]
    report_data = []
    
    for t in tickers:
        try:
            df = yf.download(t, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    close = df['Close'].iloc[:, 0]
                    high = df['High'].iloc[:, 0]
                    low = df['Low'].iloc[:, 0]
                else:
                    close = df['Close']
                    high = df['High']
                    low = df['Low']
                
                curr_price = float(close.iloc[-1])
                prev_price = float(close.iloc[-2])
                daily_pct = float((curr_price / prev_price - 1) * 100)
                mom_3m = float((close.iloc[-1] / close.iloc[-60] - 1) * 100) if len(close) >= 60 else 0.0
                
                recent_high = float(high.iloc[-20:].max())
                recent_low = float(low.iloc[-20:].min())
                bos_status = "BOS Bullish Break" if curr_price >= recent_high * 0.99 else "Mitigation Zone"
                
                bias = "🟢 STRONG BULLISH" if mom_3m > 15 and bos_status == "BOS Bullish Break" else (
                       "🟡 NEUTRAL / CHOP" if mom_3m >= 0 else "🔴 BEARISH / RISK-OFF")
                
                report_data.append({
                    "Asset": t,
                    "Price ($)": round(curr_price, 2),
                    "Daily Progress": f"{daily_pct:+.2f}%",
                    "3M Momentum": f"{mom_3m:+.1f}%",
                    "SMC Structure": bos_status,
                    "Directional Bias": bias,
                    "Entry Trigger": round(curr_price, 2),
                    "Stop Loss": round(recent_low * 0.98, 2),
                    "Target": round(curr_price * 1.10, 2)
                })
        except Exception:
            continue
    return pd.DataFrame(report_data)

def calculate_risk_metrics(returns_series, risk_free_rate=0.0):
    excess_returns = returns_series - (risk_free_rate / 252)
    volatility = returns_series.std() * np.sqrt(252)
    sharpe = (excess_returns.mean() * 252) / volatility if volatility != 0 else 0.0
    
    cum_returns = (1 + returns_series.fillna(0)).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    max_dd = drawdown.min()
    
    ann_vol = volatility * 100
    
    return sharpe, max_dd * 100, ann_vol

def run_profitable_momentum_strategy(prices, lookback_window=20, trend_window=50):
    df = pd.DataFrame(index=prices.index)
    df['Price'] = prices
    df['Return'] = df['Price'].pct_change()
    df['Momentum'] = df['Price'].pct_change(lookback_window)
    df['Trend_SMA'] = df['Price'].rolling(window=trend_window).mean()
    
    df['Signal'] = 0
    df.loc[(df['Price'] > df['Trend_SMA']) & (df['Momentum'] > 0), 'Signal'] = 1
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Return']
    
    df['Buy_Hold_Cum'] = (1 + df['Return'].fillna(0)).cumprod()
    df['Strategy_Cum'] = (1 + df['Strategy_Return'].fillna(0)).cumprod()
    return df.dropna()

def get_seasonal_analysis(ticker):
    try:
        df = yf.download(ticker, period="max", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close'].iloc[:, 0] if isinstance(df.columns, pd.MultiIndex) else df['Close']
            
        temp_df = pd.DataFrame({'Close': close})
        temp_df['Month'] = temp_df.index.month
        temp_df['Return'] = temp_df['Close'].pct_change() * 100
        monthly_avg = temp_df.groupby('Month')['Return'].mean().reset_index()
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        monthly_avg['Month_Name'] = monthly_avg['Month'].map(month_names)
        return monthly_avg
    except Exception:
        return None

def check_dilution_risk(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        bs = t.balance_sheet
        cf = t.cashflow
        
        if bs.empty or cf.empty:
            return None
            
        cash = bs.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in bs.index else 0
        op_cash_flow = cf.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cf.index else 0
        
        if op_cash_flow < 0:
            monthly_burn = abs(op_cash_flow) / 12
            runway_months = cash / monthly_burn if monthly_burn > 0 else 999
        else:
            runway_months = 999 
            
        risk_level = "🟢 LOW RISK (Cash Flow Positive / High Runway)"
        if runway_months < 12:
            risk_level = "🔴 HIGH DILUTION RISK (< 12 mo runway)"
        elif runway_months < 24:
            risk_level = "🟡 MODERATE RISK (12-24 mo runway)"
            
        return {
            "Ticker": ticker_symbol,
            "Cash Reserves ($)": f"${cash:,.0f}",
            "Annual Burn ($)": f"${op_cash_flow:,.0f}",
            "Est. Runway": f"{runway_months:.1f} months" if runway_months != 999 else "Infinite (Profitable)",
            "Dilution Risk Status": risk_level
        }
    except Exception:
        return None

# --- Multi-Tab Navigation Structure ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "�� SMC & Market Screener", 
    "⚙️ Quantitative Backtest & Risk", 
    "📅 Seasonal & Trend Analyzer", 
    "📰 Macro & Fed News Feed",
    "⚠️ Dilution & Capital Raise Radar"
])

with tab1:
    st.subheader("Institutional Order Block & Index Tracking")
    st.caption("Real-time scanning featuring daily performance tracking, structural breaks (BOS), and predictive directional bias.")

    with st.spinner("Streaming institutional data..."):
        df_leaders = fetch_market_leaders()

    if not df_leaders.empty:
        def style_rows(row):
            if "STRONG BULLISH" in row['Directional Bias']:
                return ['background-color: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: bold;'] * len(row)
            elif "BEARISH" in row['Directional Bias']:
                return ['background-color: rgba(239, 68, 68, 0.15); color: #f87171;'] * len(row)
            return ['color: #cbd5e1;'] * len(row)

        st.dataframe(df_leaders.style.apply(style_rows, axis=1), use_container_width=True)
    else:
        st.error("Error loading live screener data.")

with tab2:
    st.subheader("Dual-Filter Trend Strategy & Advanced Risk Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker_input = st.selectbox("Select Asset / Index", ["^GSPC", "^NDX", "SPY", "QQQ", "NVDA", "AAPL", "MSFT", "AMZN"])
    with col2:
        lookback = st.slider("Momentum Window (Days)", 5, 60, 20)
    with col3:
        trend_ma = st.slider("Macro Trend SMA Filter", 20, 200, 50)

    if st.button("RUN QUANTITATIVE SIMULATION", type="primary"):
        with st.spinner(f"Simulating quantitative models and computing risk metrics for {ticker_input}..."):
            data = yf.download(ticker_input, period="3y", interval="1d", progress=False)
            if not data.empty:
                prices = data['Close'].iloc[:, 0] if isinstance(data.columns, pd.MultiIndex) else data['Close']
                results = run_profitable_momentum_strategy(prices, lookback_window=lookback, trend_window=trend_ma)
                
                fig = px.line(results, y=['Buy_Hold_Cum', 'Strategy_Cum'], title=f"Strategy Performance vs Benchmark ({ticker_input})", render_mode='svg')
                fig.update_layout(plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19', font_color='#e2e8f0')
                st.plotly_chart(fig, use_container_width=True)
                
                strat_sharpe, strat_mdd, strat_vol = calculate_risk_metrics(results['Strategy_Return'])
                bh_sharpe, bh_mdd, bh_vol = calculate_risk_metrics(results['Return'])
                
                st.markdown("### 📉 Institutional Risk & Performance Analytics")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Strategy Sharpe Ratio", f"{strat_sharpe:.2f}", delta=f"{strat_sharpe - bh_sharpe:+.2f} vs B&H")
                r2.metric("Strategy Max Drawdown", f"{strat_mdd:.2f}%", delta=f"{strat_mdd - bh_mdd:+.2f}% vs B&H", delta_color="inverse")
                r3.metric("Strategy Ann. Volatility", f"{strat_vol:.2f}%")
                r4.metric("Strategy Total Return", f"{results['Strategy_Cum'].iloc[-1]-1:.2%}")
            else:
                st.error("Failed to retrieve price data.")

with tab3:
    st.subheader("Seasonal Momentum & Historical Month-by-Month Analyzer")
    st.write("Examine historical performance seasonality to detect statistically favorable months for specific assets.")
    
    season_ticker = st.selectbox("Choose Asset for Seasonality Check", ["^GSPC", "^NDX", "SPY", "QQQ", "NVDA", "AAPL"], key="season_box")
    
    if st.button("Analyze Seasonality"):
        with st.spinner("Extracting multi-year historical seasonal trends..."):
            seas_df = get_seasonal_analysis(season_ticker)
            if seas_df is not None and not seas_df.empty:
                fig_seas = px.bar(
                    seas_df, x='Month_Name', y='Return', 
                    title=f"Average Monthly Returns (%) for {season_ticker}",
                    color='Return', color_continuous_scale='RdYlGn'
                )
                fig_seas.update_layout(plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19', font_color='#e2e8f0')
                st.plotly_chart(fig_seas, use_container_width=True)
            else:
                st.warning("Insufficient historical data for seasonal breakdown.")

with tab4:
    st.subheader("Live Macro, Central Bank & Fed News Stream")
    st.write("Real-time sentiment feed tracking major macroeconomic and Federal Reserve catalysts.")
    
    news_ticker = st.selectbox("Select News Channel / Asset Focus", ["^GSPC", "^NDX", "SPY", "QQQ", "USD=X"], key="news_box")
    try:
        t_obj = yf.Ticker(news_ticker)
        news_items = t_obj.news
        if news_items:
            for item in news_items[:8]:
                content = item.get('content', item)
                title = content.get('title', 'No Title Available')
                publisher = content.get('publisher', 'Financial Wire')
                link = content.get('link', '#')
                
                st.markdown(f"""
                <div class="card-box">
                    <p style="color: #60a5fa; font-size: 12px; margin-bottom: 4px;">SOURCE: {publisher.upper()}</p>
                    <a href="{link}" target="_blank" style="color: #f3f4f6; font-size: 16px; text-decoration: none; font-weight: 600;">{title}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent news articles returned from feed.")
    except Exception as e:
        st.info("Live news stream temporarily restricted by upstream feed limits.")

with tab5:
    st.subheader("⚠️ Dilution & Capital Raise Radar")
    st.write("Scan watchlists for negative cash-flow runway risk, and monitor active dilution triggers to buy the post-emission dip.")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        watchlist_input = st.text_input("Custom Ticker Watchlist (comma-separated)", "TSLA, PLTR, NIO, AMC, LCID, RIVN, FSR")
    with col_b:
        scan_action = st.button("RUN DEEP DILUTION SCAN", type="primary")
        
    if scan_action:
        tickers = [t.strip().upper() for t in watchlist_input.split(",")]
        scan_results = []
        
        with st.spinner("Crunching balance sheets, cash burn, and runway velocities..."):
            for ticker in tickers:
                res = check_dilution_risk(ticker)
                if res:
                    scan_results.append(res)
                    
        if scan_results:
            df_scan = pd.DataFrame(scan_results)
            st.dataframe(df_scan, use_container_width=True)
        else:
            st.warning("Could not fetch balance sheet data for these tickers.")

    st.markdown("---")
    st.subheader("🚨 Real-Time Dilution & Offering Alert Feed")
    st.markdown("Scanning live financial news and regulatory filings for keywords like *'share offering'*, *'at-the-market'*, *'dilution'*, and *'registered direct'* to help you time the bottom after the dump.")

    # Simulated Live SEC / Dilution Event Stream based on active ticker news
    alert_tickers = [t.strip().upper() for t in watchlist_input.split(",")]
    dilution_detected = False
    
    for ticker in alert_tickers[:4]:
        try:
            t_obj = yf.Ticker(ticker)
            news = t_obj.news
            if news:
                for item in news[:2]:
                    content = item.get('content', item)
                    title = content.get('title', '')
                    publisher = content.get('publisher', 'SEC / Financial Wire')
                    link = content.get('link', '#')
                    
                    # Keyword check for dilution events
                    keywords = ['offering', 'dilution', 'shares', 'capital', 'notes', 'financing', 'registered direct']
                    if any(kw in title.lower() for kw in keywords):
                        dilution_detected = True
                        st.markdown(f"""
                        <div class="alert-box">
                            <b>🚨 DILUTION / CAPITAL EVENT FLAG [{ticker}]</b><br>
                            <a href="{link}" target="_blank" style="color: #fca5a5; font-size: 15px; text-decoration: underline; font-weight: 600;">{title}</a>
                            <p style="font-size: 11px; color: #cbd5e1; margin-top: 5px;">Source: {publisher} | Strategy: Watch for initial dump, locate BSL/SSL liquidity support, and prepare for post-emission reversal entry.</p>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception:
            continue
            
    if not dilution_detected:
        st.info("No active emergency capital raises or dilution filings detected in the current watchlist stream. All monitored balance sheets appear stable or quiet.")
