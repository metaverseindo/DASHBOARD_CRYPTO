import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. SETTINGS & REFRESH
st.set_page_config(page_title="metaverseindo", layout="wide")
st_autorefresh(interval=20000, key="freshengine")

# 2. THEME & CSS
st.markdown(r'''
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; }
    .nav-bar {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 15px; margin-bottom: 20px; border-radius: 10px;
        text-align: center; font-family: 'Orbitron', sans-serif;
        color: #10b981; font-weight: 900; font-size: 22px;
    }
    .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; }
    </style>
    <div class="nav-bar">metaverseindo TERMINAL v.66</div>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE (INTEGRASI BINANCE)
@st.cache_data(ttl=15)
def get_live_market():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        data = res.json()
        watchlist = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'DOGEUSDT']
        rows = []
        for i in data:
            if i['symbol'] in watchlist:
                rows.append({
                    "SYMBOL": i['symbol'],
                    "PRICE": float(i['lastPrice']),
                    "CHANGE": float(i['priceChangePercent'])
                })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()

# 4. CONTROLLER (BIAR CHART & TABEL NYAMBUNG)
df = get_live_market()

with st.sidebar:
    st.markdown("### 🛰️ CONTROLLER")
    if not df.empty:
        # Pilih koin di sini buat ganti chart secara otomatis
        selected_coin = st.radio("SELECT ASSET:", df['SYMBOL'].tolist())
    else:
        selected_coin = "BTCUSDT"
    st.markdown("---")
    st.caption("Terminal by metaverseindo")

# 5. DISPLAY
col_l, col_r = st.columns([1, 2.5])

with col_l:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"##### Market Status")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error("API Limit. Wait 30s.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"##### Analysis: {selected_coin}")
    
    # JEMBATAN INTEGRASI: Chart bakal ngerespon selected_coin dari Radio Button
    tv_widget = f"""
    <div style="height:550px;">
        <div id="tv_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "autosize": true,
            "symbol": "BINANCE:{selected_coin}",
            "interval": "60",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "container_id": "tv_chart"
        }});
        </script>
    </div>
    """
    components.html(tv_widget, height=560)
    st.markdown('</div>', unsafe_allow_html=True)
