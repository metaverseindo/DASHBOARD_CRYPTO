import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. INITIAL SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30000, key="freshengine")

# 2. BOOTSTRAP 5 & CLEAN CSS
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #0b0e11; color: #eaecef; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1e2329; border-right: 1px solid #f0b90b; }
    .nav-bar-top {
        background-color: #1e2329;
        border-bottom: 2px solid #f0b90b;
        padding: 15px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border-radius: 8px;
    }
    .brand-id { font-family: 'Orbitron', sans-serif; color: #f0b90b; font-weight: 900; font-size: 22px; }
    .card-panel {
        background-color: #161a1e;
        border: 1px solid #2b3139;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .dot-live { height: 8px; width: 8px; background-color: #02c076; border-radius: 50%; display: inline-block; margin-right: 5px; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown('<div class="brand-id">META INDO</div>', unsafe_allow_html=True)
    st.markdown("---")
    nav_choice = st.radio(
        "NAVIGASI UTAMA",
        ["📊 Terminal Market", "🚀 Trading Hub", "⚙️ System Settings"],
        index=0
    )
    st.markdown("---")
    st.caption("v.46 | Stable Version")

# 4. DATA ENGINE
@st.cache_data(ttl=20)
def get_master_data():
    key = st.secrets.get("BINANCE_API_KEY", None)
    endpoints = ["https://api.binance.com", "https://api1.binance.com", "https://api2.binance.com"]
    headers = {"User-Agent": "Mozilla/5.0"}
    if key: headers["X-MBX-APIKEY"] = key
    
    for base in endpoints:
        try:
            res = requests.get(f"{base}/api/v3/ticker/24hr", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                rows = []
                for item in data:
                    if item.get('symbol', '').endswith('USDT'):
                        vol = float(item.get('quoteVolume', 0))
                        if vol > 5000000:
                            rows.append({
                                "SYMBOL": item['symbol'].replace('USDT', ''),
                                "PRICE": float(item['lastPrice']),
                                "CHANGE": float(item['priceChangePercent']),
                                "VOL_RAW": vol,
                                "VOLUME 24H": f"$ {vol:,.0f}"
                            })
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(15)
                return df.drop(columns=['VOL_RAW']), f"🟢 {base.split('//')}"
        except: continue
    return pd.DataFrame([{"SYMBOL": "BTC", "PRICE": 0.0, "CHANGE": 0.0, "VOLUME 24H": "BUSY"}]), "🔴 BUSY"

# 5. RENDER
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# Header Bar
st.markdown(f"""
    <div class="nav-bar-top">
        <div class="brand-id">META INDO PRO</div>
        <div class="d-flex align-items-center">
            <span class="dot-live"></span>
            <span
