import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="Nordic Universal Dilution & Emisjon Screener", layout="wide", initial_sidebar_state="expanded")

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
    .safe-box {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #34d399;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ NORDIC UNIVERSE DILUTION & EMISJON SCANNER")
st.markdown("Automated balance sheet runway analysis and disclosure keyword tracking across an expanded array of small-cap, growth, and micro-cap equities.")

# --- Comprehensive Universe of Norwegian Small-Caps, Micro-Caps, Biotech, & Explorers ---
EXPANDED_UNIVERSE = {
    # --- Energy, Oil Services & Shipping Speculation ---
    "AKOBO.OL": "Mining Explorer", "CLCO.OL": "Shipping Spec", "DVD.OL": "Deep Drilling", 
    "PENR.OL": "Oil Explorer", "BNOR.OL": "Oil Production", "ARCHA.OL": "Oil Services",
    "FLNG.OL": "LNG Shipping", "FRO.OL": "Tanker Shipping", "NAPA.OL": "Shipping", "OTEC.OL": "Ocean Tech",
    
    # --- Biotech, MedTech & CleanTech / Hydrogen High Burn ---
    "AZT.OL": "Biotech", "ABS.OL": "Biotech", "CIRC.OL": "Biotech", "LIFE.OL": "MedTech",
    "NEL.OL": "Hydrogen Pureplay", "AGLX.OL": "Green Tech", "HEX.OL": "Hydrogen/Composites", 
    "CAPS.OL": "CleanTech", "Scatec": "Renewables",
    
    # --- Seafood, Aquaculture Tech & Micro Industrials ---
    "MOWI.OL": "Seafood", "SALM.OL": "Salmon", "BAKKA.OL": "Fish Farming", "AUSS.OL": "Seafood",
    "AKVA.OL": "Fish Tech", "ASAS.OL": "Aquaculture", "SCANA.OL": "Industrial Micro",
    
    # --- IT, Venture & Small-Cap Tech ---
    "WSTEP.OL": "Small IT", "MGN.OL": "Micro-Cap", "HUNT.OL": "Venture", "BINT.OL": "Micro-Cap",
    "ATEA.OL": "IT Infrastructure", "AUTO.OL": "Robotics Tech", "ACR.OL": "Credit/Debt",
    
    # --- Large Caps / Benchmarks for Baseline Comparison ---
    "EQNR.OL": "Energy Giant", "DNB.OL": "Banking", "NHY.OL": "Materials", "YAR.OL": "Agriculture",
    "OSEBX.OL": "Oslo Benchmark"
}

def analyze_company_burn(ticker):
    try:
        t = yf.Ticker(ticker)
        bs = t.balance_sheet
        cf = t.cashflow
        
        if bs.empty or cf.empty:
            return None
            
        # Extract Cash and Operating Cash Flow
        cash_keys = ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments', 'Cash']
        cash = 0
        for k in cash_keys:
            if k in bs.index:
                val = bs.loc[k].iloc[0]
                if not pd.isna(val):
                    cash = float(val)
                    break
                    
        cf_keys = ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities']
        op_cf = 0
        for k in cf_keys:
            if k in cf.index:
                val = cf.loc[k].iloc[0]
                if not pd.isna(val):
                    op_cf = float(val)
                    break
                    
        # Calculate runway
        if op_cf < 0:
            monthly_burn = abs(op_cf) / 12
            runway_months = cash / monthly_burn if monthly_burn > 0 else 0
        else:
            runway_months = 999.0 # Positive cash flow
            
        # Risk classification
        if runway_months == 999.0:
            status = "🟢 Safe (Cash Flow Positive)"
        elif runway_months < 6:
            status = "🚨 CRITICAL (<6 Mo Runway - Emisjon Imminent)"
        elif runway_months < 12:
            status = "🔴 High Risk (<12 Mo Runway)"
        elif runway_months < 24:
            status = "🟡 Moderate Risk (12-24 Mo Runway)"
        else:
            status = "🟢 Adequate Runway (>24 Mo)"
            
        # Get latest stock price
        hist = t.history(period="5d")
        price = float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else price
        daily_change = ((price / prev_price) - 1) * 100 if prev_price > 0 else 0.0

        return {
            "Ticker": ticker,
            "Category": EXPANDED_UNIVERSE.get(ticker, "General Equity"),
            "Price (NOK/USD)": round(price, 2),
            "Daily Change %": round(daily_change, 2),
            "Cash Reserves": round(cash, 0),
            "Annual Cash Flow": round(op_cf, 0),
            "Est. Runway (Months)": round(runway_months, 1) if runway_months != 999.0 else "Profitable / Infinite",
            "Dilution Status": status
        }
    except Exception:
        return None

# --- Main Interface Layout ---
tab1, tab2 = st.tabs([
    "📊 Universal Burn & Emisjon Screener", 
    "📰 Real-Time Dilution & Capital Raise Feed"
])

with tab1:
    st.subheader("Mass Balance Sheet Runway & Cash Burn Matrix")
    st.write("Scanning all configured small-caps, micro-caps, biotechs, and explorers simultaneously to identify companies burning through cash reserves.")

    if st.button("RUN FULL UNIVERSE DILUTION SCAN", type="primary"):
        results = []
        progress_bar = st.progress(0)
        total_tickers = len(EXPANDED_UNIVERSE)
        
        for i, ticker in enumerate(EXPANDED_UNIVERSE.keys()):
            res = analyze_company_burn(ticker)
            if res:
                results.append(res)
            progress_bar.progress((i + 1) / total_tickers)
            
        progress_bar.empty()
        
        if results:
            df_res = pd.DataFrame(results)
            
            # Sort by runway ascending to put high dilution risk at the top
            df_res['sort_val'] = df_res['Est. Runway (Months)'].apply(lambda x: 9999 if x == "Profitable / Infinite" else float(x))
            df_res = df_res.sort_values(by='sort_val').drop(columns=['sort_val'])
            
            def color_dilution(row):
                if "CRITICAL" in row['Dilution Status'] or "High Risk" in row['Dilution Status']:
                    return ['background-color: rgba(239, 68, 68, 0.15); color: #fca5a5;'] * len(row)
                elif "Safe" in row['Dilution Status'] or "Adequate" in row['Dilution Status']:
                    return ['background-color: rgba(16, 185, 129, 0.10); color: #34d399;'] * len(row)
                return ['color: #cbd5e1;'] * len(row)

            st.dataframe(df_res.style.apply(color_dilution, axis=1), use_container_width=True)
        else:
            st.warning("Could not retrieve financial statements for the screening array.")

with tab2:
    st.subheader("🚨 Live Corporate Disclosures & Emisjon Keyword Radar")
    st.write("Automatically scans news wires and filings across the entire watchlist for capital actions, private placements, and equity offerings.")
    
    custom_input = st.text_input("Enter Tickers to Scan (Comma Separated)", "AKOBO.OL, AZT.OL, CLCO.OL, NEL.OL, NAS.OL, PENR.OL, CIRC.OL")
    
    if st.button("SCAN NEWS & FILINGS FOR EMISJONER"):
        tickers_to_check = [t.strip().upper() for t in custom_input.split(",")]
        emission_keywords = [
            'emisjon', 'rettet emisjon', 'reparasjonsemisjon', 'private placement', 
            'tegningsretter', 'subscription rights', 'dilution', 'capital raise', 
            'share issue', 'bookbuilding', 'offering', 'shares', 'sluttet'
        ]
        
        found_events = 0
        for ticker in tickers_to_check:
            try:
                t_obj = yf.Ticker(ticker)
                news = t_obj.news
                if news:
                    for item in news:
                        content = item.get('content', item)
                        title = content.get('title', '')
                        publisher = content.get('publisher', 'Market Wire')
                        link = content.get('link', '#')
                        
                        if any(kw in title.lower() for kw in emission_keywords):
                            found_events += 1
                            st.markdown(f"""
                            <div class="alert-box">
                                <b>🚨 EMISJON / CAPITAL EVENT FLAG [{ticker}]</b><br>
                                <a href="{link}" target="_blank" style="color: #fca5a5; font-size: 15px; text-decoration: underline; font-weight: 600;">{title}</a>
                                <p style="font-size: 11px; color: #cbd5e1; margin-top: 5px;">Source: {publisher}</p>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception:
                continue
                
        if found_events == 0:
            st.info("No active filing keyword matches found in recent wire feeds for these specific tickers. Try adding other micro-caps or check back when new company disclosures hit the market wire.")
