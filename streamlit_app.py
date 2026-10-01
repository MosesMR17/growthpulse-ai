import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="Nordic Universal Dilution, Buyback & Volume Radar", layout="wide", initial_sidebar_state="expanded")

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
    .buyback-box {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #34d399;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ NORDIC UNIVERSE: DILUTION, BUYBACK & VOLUME RADAR")
st.markdown("Advanced balance sheet runway analysis, volume anomaly tracking, share buyback detection, and specific corporate news parsing.")

# --- Comprehensive Universe ---
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
    
    # --- Large Caps / Benchmarks ---
    "EQNR.OL": "Energy Giant", "DNB.OL": "Banking", "NHY.OL": "Materials", "YAR.OL": "Agriculture",
    "OSEBX.OL": "Oslo Benchmark"
}

def analyze_company_comprehensive(ticker):
    try:
        t = yf.Ticker(ticker)
        bs = t.balance_sheet
        cf = t.cashflow
        
        if bs.empty or cf.empty:
            return None
            
        # Cash & Cash Flow
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
                    
        runway_months = (cash / (abs(op_cf) / 12)) if op_cf < 0 else 999.0
        
        if runway_months == 999.0:
            status = "🟢 Safe (Cash Flow Positive)"
        elif runway_months < 6:
            status = "🚨 CRITICAL (<6 Mo Runway - Emisjon Imminent)"
        elif runway_months < 12:
            status = "🔴 High Risk (<12 Mo Runway)"
        elif runway_months < 24:
            status = "🟡 Moderate Risk (12-24 Mo)"
        else:
            status = "🟢 Adequate Runway (>24 Mo)"
            
        # Price, Volume Spike & Volatility Check
        hist = t.history(period="30d")
        if hist.empty:
            return None
            
        price = float(hist['Close'].iloc[-1])
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else price
        daily_change = ((price / prev_price) - 1) * 100 if prev_price > 0 else 0.0
        
        recent_volume = float(hist['Volume'].iloc[-1])
        avg_volume_20 = float(hist['Volume'].iloc[-20:].mean()) if len(hist) >= 20 else recent_volume
        volume_ratio = (recent_volume / avg_volume_20) if avg_volume_20 > 0 else 1.0
        
        volume_status = "NORMAL"
        if volume_ratio >= 3.0:
            volume_status = "🔥 MASSIVE VOLUME SURGE (3x+ Avg)"
        elif volume_ratio >= 1.8:
            volume_status = "⚡ High Volume Activity"

        return {
            "Ticker": ticker,
            "Category": EXPANDED_UNIVERSE.get(ticker, "General Equity"),
            "Price": round(price, 2),
            "Daily Change %": round(daily_change, 2),
            "Volume Ratio": round(volume_ratio, 2),
            "Volume Flag": volume_status,
            "Est. Runway (Mo)": round(runway_months, 1) if runway_months != 999.0 else "Infinite",
            "Dilution / Burn Status": status
        }
    except Exception:
        return None

# --- Main Navigation Tabs ---
tab1, tab2 = st.tabs([
    "📊 Universal Runway, Buyback & Volume Screener", 
    "📰 Deep-Dive News & Event Inspector"
])

with tab1:
    st.subheader("Mass Balance Sheet Runway, Volume Spikes & Capital Action Screener")
    st.write("Scans all configured assets simultaneously for cash runways, unusual volume surges (signaling hidden accumulation, capital raising, or block trades), and status flags.")

    if st.button("RUN FULL UNIVERSE SCAN", type="primary"):
        results = []
        progress_bar = st.progress(0)
        total_tickers = len(EXPANDED_UNIVERSE)
        
        for i, ticker in enumerate(EXPANDED_UNIVERSE.keys()):
            res = analyze_company_comprehensive(ticker)
            if res:
                results.append(res)
            progress_bar.progress((i + 1) / total_tickers)
            
        progress_bar.empty()
        
        if results:
            df_res = pd.DataFrame(results)
            
            # Sort by volume ratio or risk level
            df_res['sort_val'] = df_res['Est. Runway (Mo)'].apply(lambda x: 9999 if x == "Infinite" else float(x))
            df_res = df_res.sort_values(by=['Volume Ratio'], ascending=False)
            
            def color_rows(row):
                if "CRITICAL" in row['Dilution / Burn Status'] or "High Risk" in row['Dilution / Burn Status']:
                    return ['background-color: rgba(239, 68, 68, 0.12); color: #fca5a5;'] * len(row)
                elif "MASSIVE VOLUME" in row['Volume Flag']:
                    return ['background-color: rgba(59, 130, 246, 0.15); color: #93c5fd;'] * len(row)
                return ['color: #cbd5e1;'] * len(row)

            st.dataframe(df_res.style.apply(color_rows, axis=1), use_container_width=True)
        else:
            st.warning("Could not pull market feed datasets.")

with tab2:
    st.subheader("📰 Targeted Stock News, Buyback & Emisjon Parser")
    st.write("Select or input any ticker to extract recent headlines specifically checking for **Emisjon / Dilution** events or **Share Buybacks (Tilbakekjøp)** alongside volume characteristics.")
    
    selected_target = st.text_input("Enter Ticker to Inspect (e.g. NEL.OL, AKOBO.OL, DNB.OL)", "AKOBO.OL")
    
    if st.button("FETCH TARGETED NEWS & BUYBACK ANALYSIS", type="primary"):
        target_clean = selected_target.strip().upper()
        st.markdown(f"### Analysis Report for: `{target_clean}`")
        
        try:
            t_obj = yf.Ticker(target_clean)
            
            # Volume profile check
            hist = t_obj.history(period="10d")
            if not hist.empty:
                cur_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[:-1].mean()
                v_mult = cur_vol / avg_vol if avg_vol > 0 else 1.0
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Latest Close Price", f"{hist['Close'].iloc[-1]:.2f}")
                col_b.metric("Latest Trading Volume", f"{cur_vol:,.0f}")
                col_c.metric("Volume vs 10D Average", f"{v_mult:.2f}x")
            
            st.markdown("---")
            st.subheader("Filing & News Feed Keyword Scanner")
            
            news_items = t_obj.news
            if news_items:
                emission_keywords = ['emisjon', 'rettet emisjon', 'reparasjonsemisjon', 'private placement', 'tegningsretter', 'subscription rights', 'dilution', 'capital raise', 'share issue', 'bookbuilding', 'offering', 'shares']
                buyback_keywords = ['buyback', 'tilbakekjøp', 'repurchase', 'acquire own shares', 'egne aksjer']
                
                matched_any = False
                for item in news_items:
                    content = item.get('content', item)
                    title = content.get('title', '')
                    publisher = content.get('publisher', 'Market Wire')
                    link = content.get('link', '#')
                    title_lower = title.lower()
                    
                    is_emission = any(kw in title_lower for kw in emission_keywords)
                    is_buyback = any(kw in title_lower for kw in buyback_keywords)
                    
                    if is_emission or is_buyback:
                        matched_any = True
                        box_class = "alert-box" if is_emission else "buyback-box"
                        tag_label = "🚨 DETECTED: EMISJON / DILUTION EVENT" if is_emission else "🟢 DETECTED: SHARE BUYBACK PROGRAM"
                        
                        st.markdown(f"""
                        <div class="{box_class}">
                            <b>{tag_label}</b><br>
                            <a href="{link}" target="_blank" style="color: #ffffff; font-size: 16px; text-decoration: underline; font-weight: 600;">{title}</a>
                            <p style="font-size: 11px; color: #cbd5e1; margin-top: 5px;">Source: {publisher} | Symbol: {target_clean}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if not matched_any:
                    st.info(f"No explicit Emisjon or Buyback keyword triggers found in the latest news feed for {target_clean}. Below are the most recent general news items:")
                    for item in news_items[:5]:
                        content = item.get('content', item)
                        title = content.get('title', 'No Title')
                        link = content.get('link', '#')
                        st.markdown(f"- [{title}]({link})")
            else:
                st.warning("No recent news feed items found for this ticker.")
        except Exception as e:
            st.error(f"Error retrieving data for {target_clean}: {e}")
