import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE CONFIG
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STYLING (Glassmorphism Pro)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;800&display=swap');

    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: 'Plus Jakarta Sans', sans-serif; }

    .glass-card {
        background: rgba(23, 32, 53, 0.6);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }

    .title-text {
        font-family: 'JetBrains Mono', monospace;
        color: #10b981;
        font-weight: 800;
        font-size: 32px;
        letter-spacing: -1px;
        margin: 0;
    }

    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.8);
        border-left: 4px solid #10b981;
        padding: 10px 15px;
        border-radius: 8px;
    }
    
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_market_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if res.status_code == 200:
            data = res.json()
            btc = next(i for i in data if i['symbol'] == "BTCUSDT")
            coins = []
            for i in data:
                if i['symbol'].endswith('USDT') and float(i.get('quoteVolume', 0)) > 30000000:
                    coins.append({
                        "SYMBOL": i['symbol'].replace('USDT',''),
                        "PRICE": f"{float(i['lastPrice']):,.2f}",
                        "CHANGE": f"{float(i['priceChangePercent'])}%"
                    })
            return pd.DataFrame(coins).head(12), float(btc['lastPrice']), float(btc['priceChangePercent'])
    except:
        pass
    return pd.DataFrame(), 0.0, 0.0

# 4. DATA FETCH & HEADER (BARIS 80 FIX)
df, btc_p, btc_c = get_market_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# FIX DISINI: Tambahkan ratio agar tidak TypeError
c_title, c_clock = st.columns()

with c_title:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
    st.caption("Terminal v.72 | Secure Connection Established")

with c_clock:
    st.markdown(f"<div style='text-align: right; color: #64748b; font-family: JetBrains Mono; padding-top: 15px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("") 

# 5. KEY METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC/USDT", f"${btc_p:,.0f}", f"{btc_c}%")
m2.metric("STATUS", "STABLE", "100%")
m3.metric("FEED", "BINANCE", "SPOT")
m4.metric("VOL", "> 30M", "HIGH")

st.write("") 

# 6. MAIN WORKSPACE
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Snapshot")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=480)
    else:
        st.error("Synchronizing Data...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Technical Analysis")
    tv_widget = """
    <div id="tv_pro"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "width": "100%", "height": 480, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_pro", "allow_symbol_change": true,
      "hide_side_toolbar": false
    });
    </script>
    """
    components.html(tv_widget, height=490)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #334155; font-size: 10px; margin-top: 30px;'>© 2026 METAVERSEINDO | TERMINAL ENCRYPTED</div>", unsafe_allow_html=True)
