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
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; min-width: 350px !important; }
    .nav-bar-top {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 20px; border-radius: 10px;
    }
    .brand-id { color: #10b981; font-weight: 900; font-size: 24px; font-family: 'Orbitron', sans-serif; }
    .card-panel { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    </style>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_live_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        if res.status_code == 200:
            data = res.json()
            btc_p = next((float(i['lastPrice']) for i in data if i['symbol'] == "BTCUSDT"), 0)
            rows = [{"SYMBOL": i['symbol'].replace('USDT',''), "PRICE": f"{float(i['lastPrice']):,.2f}", "CHANGE": f"{float(i['priceChangePercent'])}%"} 
                    for i in data if i['symbol'].endswith('USDT') and float(i.get('quoteVolume',0)) > 15000000]
            df = pd.DataFrame(rows).head(20)
            return df, btc_p
    except: pass
    return pd.DataFrame(), 0

# 4. SIDEBAR (CHART & CONTROL)
with st.sidebar:
    st.markdown('<div class="brand-id">metaverseindo</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # TRADINGVIEW DI SIDEBAR (Bisa ganti koin sendiri)
    st.write("🔍 **Quick Analysis**")
    tv_sidebar = '''
    <div id="tv_side"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%", "height": 400, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_side",
      "allow_symbol_change": true,
      "enable_publishing": false,
      "hide_top_toolbar": false,
      "save_image": false
    });
    </script>
    '''
    components.html(tv_sidebar, height=410)
    
    df, btc_p = get_live_data()
    st.metric("BTC PRICE", f"${btc_p:,.0f}")

# 5. MAIN CONTENT
st.markdown(f'''<div class="nav-bar-top"><div class="brand-id">metaverseindo</div><div style="color:#10b981; font-weight:bold;">MARKET MONITOR</div></div>''', unsafe_allow_html=True)

st.markdown('<div class="card-panel">', unsafe_allow_html=True)
st.write("### 📊 Real-Time Spot Assets (USDT)")
if not df.empty:
    # Menampilkan tabel koin yang lebih banyak
    st.dataframe(df, use_container_width=True, hide_index=True, height=600)
else:
    st.warning("Fetching Market Data...")
st.markdown('</div>', unsafe_allow_html=True)
