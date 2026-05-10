import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. INITIAL SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STYLESHEET (CLEAN & HIDDEN)
st.markdown("""
    <style>
    /* Sembunyikan elemen bawaan */
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    
    /* Container Header */
    .header-box {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        border-bottom: 3px solid #10b981;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .brand-title {
        font-family: 'Courier New', monospace;
        color: #10b981;
        font-weight: 900;
        font-size: 32px;
        letter-spacing: 4px;
        margin: 0;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def fetch_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        data = res.json()
        btc = next(i for i in data if i['symbol'] == "BTCUSDT")
        
        coins = []
        for i in data:
            if i['symbol'].endswith('USDT'):
                vol = float(i.get('quoteVolume', 0))
                if vol > 20000000: # Hanya koin dengan volume tinggi
                    coins.append({
                        "ASSET": i['symbol'].replace('USDT',''),
                        "PRICE": f"{float(i['lastPrice']):,.2f}",
                        "CHANGE": f"{float(i['priceChangePercent'])}%"
                    })
        return pd.DataFrame(coins).head(15), float(btc['lastPrice']), float(btc['priceChangePercent'])
    except:
        return pd.DataFrame(), 0.0, 0.0

# 4. RENDER HEADER
st.markdown('<div class="header-box"><p class="brand-title">METAVERSEINDO</p></div>', unsafe_allow_html=True)

# 5. DATA & METRICS
df, btc_p, btc_c = fetch_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# Metrik Utama (Gunakan Native Streamlit agar Responsive)
m1, m2, m3 = st.columns(3)
m1.metric("BITCOIN", f"${btc_p:,.0f}", f"{btc_c}%")
m2.metric("NETWORK", "ONLINE", delta_color="normal")
m3.metric("TIME (WIB)", time_now)

st.divider()

# 6. MAIN CONTENT LAYOUT
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.write("### 📊 Top Volume (USDT)")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=450)
    else:
        st.error("Data loading... please refresh.")

with col_right:
    st.write("### 📈 Live Chart")
    tv_widget = """
    <div id="tv_main"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "toolbar_bg": "#f1f3f6", "enable_publishing": false,
      "allow_symbol_change": true, "container_id": "tv_main"
    });
    </script>
    """
    components.html(tv_widget, height=460)
