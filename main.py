import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. INITIAL SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS CUSTOM
st.markdown(r'''
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; }
    .nav-bar-top {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 15px 25px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 20px; border-radius: 12px;
    }
    .brand-id { font-family: 'Orbitron', sans-serif; color: #10b981; font-weight: 900; font-size: 24px; }
    .card-panel { background-color: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .metric-box { text-align: center; padding: 10px; border-right: 1px solid #334155; }
    .metric-box:last-child { border-right: none; }
    .dot-live { height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_crypto_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        if res.status_code == 200:
            data = res.json()
            btc_price = 0
            rows = []
            for i in data:
                symbol = i.get('symbol', '')
                if symbol == "BTCUSDT": btc_price = float(i['lastPrice'])
                if symbol.endswith('USDT'):
                    vol = float(i.get('quoteVolume', 0))
                    if vol > 10000000:
                        rows.append({"SYMBOL": symbol.replace('USDT',''), "PRICE": float(i['lastPrice']), "CHANGE": float(i['priceChangePercent']), "VOL": vol})
            df = pd.DataFrame(rows).sort_values("VOL", ascending=False).head(15)
            return df.drop(columns=['VOL']), btc_price, "🟢 ONLINE"
    except: pass
    return pd.DataFrame(), 0, "🔴 DELAY"

# 4. SIDEBAR
with st.sidebar:
    st.markdown('<div class="brand-id" style="font-size: 18px;">metaverseindo</div>', unsafe_allow_html=True)
    st.markdown("---")
    nav_choice = st.radio("NAVIGASI", ["📊 Terminal Market", "🚀 Trading Hub", "⚙️ System Settings"])
    st.markdown("---")
    st.caption("v.56 | metaverseindo Stable")

# 5. HEADER & NAVBAR
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

st.markdown(f'''
    <div class="nav-bar-top">
        <div class="brand-id">metaverseindo</div>
        <div class="d-flex align-items-center">
            <span class="dot-live"></span>
            <span style="color: #10b981; font-size: 14px; font-weight: bold; margin-right: 20px;">LIVE MARKET</span>
            <span class="text-secondary" style="font-size: 13px;">{time_now} WIB</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

#
