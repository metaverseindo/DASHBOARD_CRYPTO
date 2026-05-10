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
    .stApp { background-color: #020617; color: #eaecef; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; }
    .nav-bar-top {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 10px 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 15px; border-radius: 10px;
    }
    .brand-id { color: #10b981; font-weight: 900; font-size: 20px; }
    .card-panel { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    </style>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE DENGAN FAILSAFE
@st.cache_data(ttl=10)
def get_crypto_data():
    try:
        # Coba ambil data ticker 24 jam
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if res.status_code == 200:
            data = res.json()
            btc_p = next((float(i['lastPrice']) for i in data if i['symbol'] == "BTCUSDT"), 0)
            rows = []
            for i in data:
                if i['symbol'].endswith('USDT'):
                    vol = float(i.get('quoteVolume', 0))
                    if vol > 1000000: # Turunin filter ke 1jt biar data pasti masuk
                        rows.append({
                            "SYMBOL": i['symbol'].replace('USDT',''),
                            "PRICE": float(i['lastPrice']),
                            "CHANGE": float(i['priceChangePercent'])
                        })
            if rows:
                return pd.DataFrame(rows).head(10), btc_p, "ONLINE"
    except Exception as e:
        pass
    
    # DATA CADANGAN (Jika API Gagal agar tidak kosong)
    fallback_df = pd.DataFrame([
        {"SYMBOL": "BTC", "PRICE": 0.0, "CHANGE": 0.0},
        {"SYMBOL": "ETH", "PRICE": 0.0, "CHANGE": 0.0}
    ])
    return fallback_df, 0, "OFFLINE/RETRY"

# 4. RENDER UI
nav = st.sidebar.radio("MENU", ["Market", "Hub"])
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M")

st.markdown(f'''<div class="nav-bar-top"><div class="brand-id">metaverseindo</div><div style="color:#10b981;">{time_now} WIB</div></div>''', unsafe_allow_html=True)

if nav == "Market":
    df, btc_p, net_status = get_crypto_data()
    
    col_m = st.columns(3)
    col_m.markdown(f'<div class="card-panel" style="text-align:center;"><h6>BTC</h6><h4>${btc_p:,.0f}</h4></div>', unsafe_allow_html=True)
    col_m.markdown(f'<div class="card-panel" style="text-align:center;"><h6>STATUS</h6><h4>{net_status}</h4></div>', unsafe_allow_html=True)
    col_m.markdown(f'<div class="card-panel" style="text-align:center;"><h6>TYPE</h6><h4>SPOT</h4></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### Top Assets")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### Live Chart")
        tv_html = '<div id="tv" style="height:300px;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"tv"});</script>'
        components.html(tv_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)
