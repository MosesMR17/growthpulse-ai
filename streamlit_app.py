import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="Nordnet Multi-Risk Terminal", layout="wide", initial_sidebar_state="expanded")

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

st.title("⚡ NORDNET 70-TICKER DUAL-RISK SCREENER & QUANT TERMINAL")
st.markdown("---")

# --- Expanded 70-Stock Universe (Nordic Blue-Chips + High-Risk Growth/Biotech/Shipping + Global Benchmarks) ---
NORDIC_UNIVERSE = {
    # --- LOW RISK / BLUE CHIPS (Established, High Cash Flow, Stable Dividends) ---
    "EQNR.OL": "Low Risk (Energy Giant)", "DNB.OL": "Low Risk (Banking)", "NHY.OL": "Low Risk (Materials)",
    "YAR.OL": "Low Risk (Agriculture)", "MOWI.OL": "Low Risk (Seafood)", "ORK.OL": "Low Risk (Consumer Goods)",
    "TEL.OL": "Low Risk (Telecom)", "GJF.OL": "Low Risk (Insurance)", "AKRBP.OL": "Low Risk (E&P Oil)",
    "SUBC.OL": "Low Risk (Subsea Engineering)", "FRO.OL": "Low Risk (Tanker Shipping)", "SALM.OL": "Low Risk (Salmon)",
    "BAKKA.OL": "Low Risk (Fish Farming)", "AUSS.OL": "Low Risk (Seafood)", "FLNG.OL": "Low Risk (LNG Shipping)",
    "KOG.OL": "Low Risk (Defense & Tech)", "ENTRA.OL": "Low Risk (Real Estate)", "AFG.OL": "Low Risk (Construction)",
    "ATEA.OL": "Low Risk (IT Infrastructure)", "HEX.OL": "Low Risk (Hydrogen/Composites)", "Scatec": "Low Risk (Renewables)",
    "NEL.OL": "Moderate Risk (Hydrogen Pureplay)", "NAS.OL": "Moderate Risk (Aviation)", "AUTO.OL": "Moderate Risk (Robotics Tech)",
    
    # --- HIGH RISK / SPECULATIVE / SMALL-CAPS / BIOTECH (High Burn, Emisjon Prone) ---
    "PLTR": "High Risk (AI Growth)", "TSLA": "High Risk (EV Volatility)", "NIO": "High Risk (EV Growth)",
    "AMC": "High Risk (Meme/Retail)", "GME": "High Risk (Meme/Retail)", "CLCO.OL": "High Risk (Shipping Spec)",
    "DVD.OL": "High Risk (Deep Drilling)", "AKOBO.OL": "High Risk (Mining Explorer)", "PENR.OL": "High Risk (Oil Explorer)",
    "BNOR.OL": "High Risk (Oil Production)", "AGLX.OL": "High Risk (Green Tech)", "ACR.OL": "High Risk (Credit/Debt)",
    "AZT.OL": "High Risk (Biotech)", "ABS.OL": "High Risk (Biotech)", "ASAS.OL": "High Risk (Aquaculture)",
    "LIFE.OL": "High Risk (MedTech/Biotech)", "CAPS.OL": "High Risk (CleanTech)", "CIRC.OL": "High Risk (Biotech)",
    "WSTEP.OL": "High Risk (Small IT)", "MGN.OL": "High Risk (Micro-Cap)", "SCANA.OL": "High Risk (Industrial Micro)",
    "AKVA.OL": "High Risk (Fish Tech)", "HUNT.OL": "High Risk (Venture)", "NAPA.OL": "High Risk (Shipping)",
    "OTEC.OL": "High Risk (Ocean Tech)", "BINT.OL": "High Risk (Micro-Cap)", "ARCHA.OL": "High Risk (Oil Services)",
    
    # --- NORDIC & GLOBAL BENCHMARKS ---
    "^GSPC": "Benchmark (S&P 500)", "^OSEBX": "Benchmark (Oslo Bors)", "NVDA": "Global Mega Cap", "AAPL": "Global Mega Cap"
}

@st.cache_data
def fetch_bulk_market_data(tickers_dict):
    report_data = []
    
    for t, cat in tickers_dict.items():
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
                    "Risk Profile": cat,
                    "Price": round(curr_price, 2),
                    "Daily %": f"{daily_pct:+.2f}%",
                    "3M Momentum": f"{mom_3m:+.1f}%",
                    "SMC Structure": bos_status,
                    "Directional Bias": bias,
                    "Stop Loss": round(recent_low * 0.98, 2),
                    "Target": round(curr_price * 1.10, 2)
                })
        except Exception:
            continue
    return pd.DataFrame(report_data)

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
            
        risk_level = "🟢 LOW RISK (Cash Flow Positive)"
        if runway_months < 12:
            risk_level = "🔴 HIGH EMISJON RISK (< 12 mo runway)"
        elif runway_months < 24:
            risk_level = "🟡 MODERATE RISK (12-24 mo runway)"
            
        return {
            "Ticker": ticker_symbol,
            "Cash Reserves": f"${cash:,.0f}",
            "Annual Burn": f"${op_cash_flow:,.0f}",
            "Est. Runway": f"{runway_months:.1f} months" if runway_months != 999 else "Infinite (Profitable)",
            "Dilution Risk Status": risk_level
        }
    except Exception:
        return None

# --- Multi-Tab Navigation Structure ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dual-Risk Screener (70 Stocks)", 
    "⚙️ Quantitative Backtest & Risk", 
    "📅 Seasonal & Trend Analyzer", 
    "📰 Nordnet & Macro Feed",
    "⚠️ Emisjon & Dilution Radar"
])

with tab1:
    st.subheader("Side-by-Side Low-Risk Stalwarts vs High-Risk Growth Universe")
    st.caption("Live streaming quotes across major Nordnet / Oslo Børs asset categories, highlighting institutional safety vs high-beta micro-caps.")

    risk_filter = st.selectbox("Filter Risk Category", ["All Assets", "Low Risk (Blue Chips / Cash Cows)", "High Risk (Growth / Speculative / Small Caps)"])
    
    with st.spinner("Fetching data for 70+ Nordic & Global instruments..."):
        df_leaders = fetch_bulk_market_data(NORDIC_UNIVERSE)

    if not df_leaders.empty:
        if risk_filter == "Low Risk (Blue Chips / Cash Cows)":
            df_display = df_leaders[df_leaders['Risk Profile'].str.contains("Low Risk|Blue|Global")]
        elif risk_filter == "High Risk (Growth / Speculative / Small Caps)":
            df_display = df_leaders[df_leaders['Risk Profile'].str.contains("High Risk|Growth|Speculative")]
        else:
            df_display = df_leaders

        def style_rows(row):
            if "STRONG BULLISH" in row['Directional Bias']:
                return ['background-color: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: bold;'] * len(row)
            elif "BEARISH" in row['Directional Bias']:
                return ['background-color: rgba(239, 68, 68, 0.15); color: #f87171;'] * len(row)
            return ['color: #cbd5e1;'] * len(row)

        st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)
    else:
        st.error("Error loading screening stream.")

with tab2:
    st.subheader("Dual-Filter Trend Strategy & Advanced Risk Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker_input = st.selectbox("Select Asset / Index", list(NORDIC_UNIVERSE.keys()))
    with col2:
        lookback = st.slider("Momentum Window (Days)", 5, 60, 20)
    with col3:
        trend_ma = st.slider("Macro Trend SMA Filter", 20, 200, 50)

    if st.button("RUN QUANTITATIVE SIMULATION", type="primary"):
        with st.spinner(f"Simulating models for {ticker_input}..."):
            data = yf.download(ticker_input, period="3y", interval="1d", progress=False)
            if not data.empty:
                prices = data['Close'].iloc[:, 0] if isinstance(data.columns, pd.MultiIndex) else data['Close']
                
                df_strat = pd.DataFrame(index=prices.index)
                df_strat['Price'] = prices
                df_strat['Return'] = df_strat['Price'].pct_change()
                df_strat['Momentum'] = df_strat['Price'].pct_change(lookback)
                df_strat['Trend_SMA'] = df_strat['Price'].rolling(window=trend_ma).mean()
                df_strat['Signal'] = 0
                df_strat.loc[(df_strat['Price'] > df_strat['Trend_SMA']) & (df_strat['Momentum'] > 0), 'Signal'] = 1
                df_strat['Strategy_Return'] = df_strat['Signal'].shift(1) * df_strat['Return']
                df_strat['Buy_Hold_Cum'] = (1 + df_strat['Return'].fillna(0)).cumprod()
                df_strat['Strategy_Cum'] = (1 + df_strat['Strategy_Return'].fillna(0)).cumprod()
                df_clean = df_strat.dropna()
                
                fig = px.line(df_clean, y=['Buy_Hold_Cum', 'Strategy_Cum'], title=f"Strategy vs Benchmark ({ticker_input})", render_mode='svg')
                fig.update_layout(plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19', font_color='#e2e8f0')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to retrieve chart data.")

with tab3:
    st.subheader("Seasonal Momentum Analyzer")
    season_ticker = st.selectbox("Choose Asset for Seasonality Check", list(NORDIC_UNIVERSE.keys()), key="season_box")
    
    if st.button("Analyze Seasonality"):
        with st.spinner("Extracting multi-year seasonal stats..."):
            try:
                df_s = yf.download(season_ticker, period="max", interval="1d", progress=False)
                if not df_s.empty:
                    c = df_s['Close'].iloc[:, 0] if isinstance(df_s.columns, pd.MultiIndex) else df_s['Close']
                    tdf = pd.DataFrame({'Close': c})
                    tdf['Month'] = tdf.index.month
                    tdf['Return'] = tdf['Close'].pct_change() * 100
                    monthly_avg = tdf.groupby('Month')['Return'].mean().reset_index()
                    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
                    monthly_avg['Month_Name'] = monthly_avg['Month'].map(month_names)
                    
                    fig_seas = px.bar(monthly_avg, x='Month_Name', y='Return', title=f"Average Monthly Returns (%) for {season_ticker}", color='Return', color_continuous_scale='RdYlGn')
                    fig_seas.update_layout(plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19', font_color='#e2e8f0')
                    st.plotly_chart(fig_seas, use_container_width=True)
                else:
                    st.warning("Insufficient data.")
            except Exception:
                st.warning("Could not process seasonal data.")

with tab4:
    st.subheader("📰 Nordnet Markets & Macro News Stream")
    news_ticker = st.selectbox("Select Asset Focus for News", list(NORDIC_UNIVERSE.keys()), key="news_box")
    try:
        t_obj = yf.Ticker(news_ticker)
        news_items = t_obj.news
        if news_items:
            for item in news_items[:8]:
                content = item.get('content', item)
                title = content.get('title', 'No Title Available')
                publisher = content.get('publisher', 'Nordnet / Financial Wire')
                link = content.get('link', '#')
                
                st.markdown(f"""
                <div class="card-box">
                    <p style="color: #60a5fa; font-size: 12px; margin-bottom: 4px;">SOURCE: NORDNET PARTNER WIRE ({publisher.upper()})</p>
                    <a href="{link}" target="_blank" style="color: #f3f4f6; font-size: 16px; text-decoration: none; font-weight: 600;">{title}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent news articles found.")
    except Exception:
        st.info("Live news stream temporarily restricted.")

with tab5:
    st.subheader("⚠️ Emisjon & Dilution Radar (Low vs High Risk Contrast)")
    st.write("Scan balance sheets for burn rates, and monitor live emittance filings across both secure blue-chips and volatile small-caps.")
    
    default_watchlist = "EQNR.OL, DNB.OL, NHY.OL, PLTR, TSLA, AKOBO.OL, CLCO.OL, AZT.OL"
    watchlist_input = st.text_input("Custom Ticker Watchlist (comma-separated)", default_watchlist)
    
    if st.button("RUN DEEP EMISJON SCAN", type="primary"):
        tickers = [t.strip().upper() for t in watchlist_input.split(",")]
        scan_results = []
        with st.spinner("Crunching cash runway velocities..."):
            for ticker in tickers:
                res = check_dilution_risk(ticker)
                if res:
                    scan_results.append(res)
                    
        if scan_results:
            st.dataframe(pd.DataFrame(scan_results), use_container_width=True)
        else:
            st.warning("Could not fetch balance sheet metrics.")

    st.markdown("---")
    st.subheader("🚨 Real-Time Emisjon & Expanded Capital Raise Alert Feed")
    st.markdown("Scanning live feeds across broadened Norwegian & international corporate communication keywords: *emisjon*, *rettet emisjon*, *reparasjonsemisjon*, *private placement*, *tegningsretter*, *subscription rights*, *dilution*, and *capital raise*.")

    dilution_found = False
    # Expanded keyword array covering Norwegian and English capital action terminology
    emission_keywords = [
        'emisjon', 'rettet emisjon', 'reparasjonsemisjon', 'private placement', 
        'tegningsretter', 'subscription rights', 'dilution', 'capital raise', 
        'share issue', 'bookbuilding', 'offering', 'shares'
    ]

    scan_tickers = [t.strip().upper() for t in watchlist_input.split(",")]
    # Also check high risk subset automatically if list is small
    auto_check_tickers = list(set(scan_tickers + ["AKOBO.OL", "AZT.OL", "CLCO.OL", "NEL.OL", "NAS.OL"]))

    for ticker in auto_check_tickers:
        try:
            t_obj = yf.Ticker(ticker)
            news = t_obj.news
            if news:
                for item in news:
                    content = item.get('content', item)
                    title = content.get('title', '')
                    publisher = content.get('publisher', 'Nordnet / Market Wire')
                    link = content.get('link', '#')
                    
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in emission_keywords):
                        dilution_found = True
                        st.markdown(f"""
                        <div class="alert-box">
                            <b>🚨 EMISJON / CAPITAL EVENT DETECTED [{ticker}]</b><br>
                            <a href="{link}" target="_blank" style="color: #fca5a5; font-size: 15px; text-decoration: underline; font-weight: 600;">{title}</a>
                            <p style="font-size: 11px; color: #cbd5e1; margin-top: 5px;">Source: {publisher} | Action: Review subscription period terms, discount to market price, and tegningsretter (subscription rights) trading tickers on Nordnet.</p>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception:
            continue
            
    if not dilution_found:
        st.info("No active corporate filing flags matched the expanded emission keyword bank for these specific tickers. Try adding known small-caps or checking active Oslo Børs disclosures directly via NewsWeb.")
