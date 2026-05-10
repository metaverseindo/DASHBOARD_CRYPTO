import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. SETUP WAJIB
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STABLE (Raw String)
st.markdown(r'''
<style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: sans-serif; }
    .glass-card {
        background: rgba(23, 32, 53, 0.5);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .title-text { color: #10b981; font-weight: 800; font-size: 28px; margin: 0; }
    [data-testid="stMetric"] { background: #0f172a; border-left: 5px solid #10b981; padding: 10px !important; border-radius: 8px; }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if r.status_code == 200:
            data = r.json()
            btc = next((i for i in data if i['symbol'] == "BTCUSDT"), None)
            rows = []
            for i in data:
                if i['symbol'].endswith('USDT') and float(i.get('quoteVolume', 0)) > 30000000:
                    rows.append({
                        "ASSET": i['symbol'].replace('USDT',''),
                        "PRICE": f"{float(i['lastPrice']):,.2f}",
                        "24H": f"{float(i['priceChangePercent'])}%"
                    })
            return pd.DataFrame(rows).head(10), float(btc['lastPrice']), float(btc['priceChangePercent'])
    except: pass
    return pd.DataFrame(), 0.0, 0.0

# 4. RENDER UI
df, btc_p, btc_c = get_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# --- FIX TOTAL BARIS 79 (Dikasih angka 2) ---
col_head1, col_head2 = st.columns(2) 

with col_head1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
    st.caption("v.83 | FINAL STABLE")

with col_head2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:10px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# --- FIX METRICS (Dikasih angka 4) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC", f"${btc_p:,.0f}", f"{btc_c}%")
m2.metric("STATUS", "LIVE", "OK")
m3.metric("FEED", "BINANCE", "SPOT")
m4.metric("VOL", ">30M", "HIGH")

st.write("")

# --- FIX WORKSPACE (Dikasih List Rasio) ---
left, right = st.columns([1, 1.5])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market")
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Chart")
    chart_code = f'''
    <div id="tv_v83"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 400, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_v83", "allow_symbol_change": true
    }});
    </script>
    '''
    components.html(chart_code, height=410)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#334155;font-size:10px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
