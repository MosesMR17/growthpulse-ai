import streamlit as st

st.set_page_config(
    page_title="GrowthPulse AI | Nordic Business Growth Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .hero-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextInput input, .stSelectbox, .stTextArea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Public Marketing Landing Page ---
st.markdown("""
    <div class="hero-box">
        <h1>🇳🇴 GROWTHPULSE AI: NATIONWIDE NORDIC GROWTH SUITE</h1>
        <p style="font-size: 18px; color: #94a3b8;">
            The all-in-one AI reputation multiplier and short-form video repurposer built for local businesses across Norway.
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⭐ Smart Review Interceptor")
    st.write("Automatically filter negative feedback privately while driving 5-star reviews straight to Google Maps in Bokmål, Nynorsk, or Sami.")

with col2:
    st.markdown("### 🎬 AI Short-Form Video Studio")
    st.write("Upload raw long-form footage to instantly generate viral TikTok, Instagram Reels, and YouTube Shorts with burned-in captions.")

with col3:
    st.markdown("### 🏢 Nationwide Multi-Branch Hub")
    st.write("Manage multi-location franchise branches from Oslo to Stavanger, Sandnes, Trondheim, Bergen, and Tromsø under a single master dashboard.")

st.markdown("---")
st.subheader("🚀 Ready to grow your business?")
st.write("Use the **sidebar navigation** on the left to open the **Client Dashboard** or test out your active subscription and review tools!")

st.info("💡 **Founder Tip:** Check the sidebar pages menu (`Client_Dashboard`) to open your core SaaS workspace.")
