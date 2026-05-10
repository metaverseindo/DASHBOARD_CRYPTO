import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE CONFIG & AUTO-REFRESH
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STYLING (The Professional Web3 Vibe)
st.markdown(r'''
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;800&display=swap');
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .glass-card {
        background: rgba(23, 32, 53, 0.45);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    .title-text {
        font-family: 'JetBrains Mono', monospace;
        color: #10b981;
        font-weight: 800;
        font-size: 30px;
        letter-spacing: -1.5px;
        margin: 0;
    }
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.9);
        border-left: 5px solid #10b981;
        padding: 12px 15px !important;
        border-radius: 10px;
    }
    [data-testid="stMetricValue"] { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 24px !important; 
        color: #10b981 !important;
    }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE (Binance Feed)
@st.cache_data(ttl=15)
def get_verified_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if res.status_code == 200:
            data = res.json()
            btc = next((i for i in data if i['symbol'] == "BTCUSDT"), None)
            rows = []
            for i in data:
                if i['symbol'].endswith('USDT') and float(i.get('quoteVolume', 0)) > 30000000:
                    rows.append({
                        "SYMBOL": i['symbol'].replace('USDT',''),
                        "PRICE": f"{float(i['lastPrice']):,.2f}",
                        "CHANGE": f"{float(i['priceChangePercent'])}%"
                    })
            df = pd.DataFrame(rows).head(12)
            p = float(btc['lastPrice']) if btc else 0.0
            c = float(btc['priceChangePercent']) if btc else 0.0
            return df, p, c
    except: pass
    return pd.DataFrame(), 0.0, 0.0

# 4. FETCH & HEADER
df, btc_p, btc_c = get_verified_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# Fix baris columns (param)
c1, c2 = st.columns()
with c1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
    st.caption("TERMINAL v.82 | FIXED LAYOUT SECURE")
with c2:
    st.markdown(f"<div style='text-align:right;font-family:monospace;color:#64748b;padding-top:15px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("")

# 5. METRICS BAR
m_cols = st.columns(4)
m_cols.metric("BTC / USDT", f"${btc_p:,.0f}", f"{btc_c}%")
m_cols.metric("STABILITY", "OPTIMAL", "100%")
m_cols.metric("MARKET", "SPOT", "LIVE")
m_cols.metric("NETWORK", "ONLINE", "ACTIVE")

st.write("")

# 6. MAIN WORKSPACE (FIXED CHART INSIDE)
# Memberikan rasio yang seimbang
col_market, col_chart = st.columns([1, 1.3])

with col_market:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Snapshot")
    if not df.empty:
        # Dataframe dengan Container Width agar rapi
        st.dataframe(df, use_container_width=True, hide_index=True, height=480)
    else:
        st.error("Synchronizing with Binance...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Chart")
    
    # --- PENTING: TradingView sekarang terbungkus di dalam kolom st.columns ---
    tv_final = f'''
    <div id="tv_fixed"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 480, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_fixed", "allow_symbol_change": true
    }});
    </script>
    '''
    # Tinggi components.html harus sedikit lebih besar dari widget
    components.html(tv_final, height=495)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 7. FOOTER
st.markdown("<div style='text-align:center;color:#1e293b;font-size:10px;margin-top:30px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
