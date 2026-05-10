import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE CONFIGURATION
st.set_page_config(
    page_title="metaverseindo", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Autorefresh setiap 30 detik
st_autorefresh(interval=30000, key="freshengine")

# 2. ULTRA-STABLE CSS (No-Leak & High Contrast)
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;800&display=swap');

    /* Hide Overlays */
    header, footer, #MainMenu {visibility: hidden;}
    
    /* Base App Styling */
    .stApp { 
        background-color: #05080f; 
        color: #e2e8f0; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }

    /* Glassmorphism Panels */
    .glass-card {
        background: rgba(23, 32, 53, 0.45);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }

    /* Brand Header */
    .title-text {
        font-family: 'JetBrains Mono', monospace;
        color: #10b981;
        font-weight: 800;
        font-size: 32px;
        letter-spacing: -1.5px;
        margin: 0;
    }

    /* Professional Metrics */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.9);
        border-left: 5px solid #10b981;
        padding: 15px !important;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricValue"] { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 26px !important; 
        color: #10b981 !important;
    }

    /* Dataframe Cleanup */
    .stDataFrame { border: none !important; }
    </style>
''', unsafe_allow_html=True)

# 3. ROBUST DATA ENGINE
@st.cache_data(ttl=15)
def get_verified_market_data():
    try:
        # Timeout 5 detik supaya aplikasi tidak gantung
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if res.status_code == 200:
            data = res.json()
            # Ambil Harga BTC Utama
            btc_data = next((i for i in data if i['symbol'] == "BTCUSDT"), None)
            
            # Filter Koin dengan Volume Tinggi (> $30jt)
            rows = []
            for i in data:
                if i['symbol'].endswith('USDT'):
                    vol = float(i.get('quoteVolume', 0))
                    if vol > 30000000:
                        rows.append({
                            "SYMBOL": i['symbol'].replace('USDT',''),
                            "PRICE": f"{float(i['lastPrice']):,.2f}",
                            "CHANGE": f"{float(i['priceChangePercent'])}%"
                        })
            
            df = pd.DataFrame(rows).head(12)
            btc_p = float(btc_data['lastPrice']) if btc_data else 0.0
            btc_c = float(btc_data['priceChangePercent']) if btc_data else 0.0
            return df, btc_p, btc_c
    except Exception:
        pass
    return pd.DataFrame(), 0.0, 0.0

# 4. EXECUTION
df, btc_p, btc_c = get_verified_market_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# HEADER - FIX TYPEERROR: Wajib isi list ratio
c_head_1, c_head_2 = st.columns([2.5, 1])

with c_head_1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
    st.caption("TERMINAL SECURE | VER 75.0.0 | BINANCE DATA FEED")

with c_head_2:
    st.markdown(f"""
        <div style='text-align: right; color: #64748b; font-family: JetBrains Mono; padding-top: 10px;'>
            {time_now} WIB
        </div>
    """, unsafe_allow_html=True)

st.write("") 

# METRICS - FIX: Wajib isi angka integer
m_cols = st.columns(4)
m_cols.metric("BTC / USDT", f"${btc_p:,.0f}", f"{btc_c}%")
m_cols.metric("STABILITY", "OPTIMAL", "100%")
m_cols.metric("MARKET", "SPOT", "LIVE")
m_cols.metric("NETWORK", "ONLINE", "ACTIVE")

st.write("") 

# 5. MAIN WORKSPACE - FIX: Wajib isi list ratio
col_left, col_right = st.columns([1.1, 1.4])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Flow")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("Synchronizing with Binance API...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Analysis")
    # TradingView Widget - High Performance
    tv_html = '''
    <div id="tv_final"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "width": "100%", "height": 500, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_final", 
      "allow_symbol_change": true,
      "hide_side_toolbar": false
    });
    </script>
    '''
    components.html(tv_html, height=510)
    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown(
    "<div style='text-align: center; color: #1e293b; font-size: 11px; margin-top: 40px;'>© 2026 METAVERSEINDO • ENCRYPTED TERMINAL SYSTEM</div>", 
    unsafe_allow_html=True
)
