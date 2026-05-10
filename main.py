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

# 2. CSS CUSTOM (STABLE)
st.markdown(r'''
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; }
    .nav-bar-top {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 10px 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 15px; border-radius: 10px;
    }
    .brand-id { font-family: 'Orbitron', sans-serif; color: #10b981; font-weight: 900; font-size: 20px; }
    .card-panel { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    @media (max-width: 768px) {
        .brand-id { font-size: 16px; }
        h6 { font-size: 10px !important; }
        h4 { font-size: 18px !important; }
    }
    </style>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_crypto_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        if res.status_code == 200:
            data = res.json()
            btc_p = next((float(i['lastPrice']) for i in data if i['symbol'] == "BTCUSDT"), 0)
            rows = [{"SYMBOL": i['symbol'].replace('USDT',''), "PRICE": float(i['lastPrice']), "CHANGE": float(i['priceChangePercent']), "VOL": float(i.get('quoteVolume',0))} 
                    for i in data if i.get('symbol','').endswith('USDT') and float(i.get('quoteVolume',0)) > 5000000]
            df = pd.DataFrame(rows).sort_values("VOL", ascending=False).head(10)
            return df.drop(columns=['VOL']), btc_p, "🟢 ONLINE"
    except: pass
    return pd.DataFrame(), 0, "🔴 RECONNECT"

# 4. SIDEBAR & NAVBAR
with st.sidebar:
    st.markdown('<div class="brand-id">metaverseindo</div>', unsafe_allow_html=True)
    nav = st.radio("MENU", ["📊 Market", "🚀 Hub"])

tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M")
st.markdown(f'''<div class="nav-bar-top"><div class="brand-id">metaverseindo</div><div style="font-size:12px;color:#10b981;">● {time_now} WIB</div></div>''', unsafe_allow_html=True)

# 5. MAIN CONTENT
if nav == "📊 Market":
    df, btc_p, net_status = get_crypto_data()

    # METRICS AREA
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="card-panel" style="text-align:center;"><h6>BTC</h6><h4 style="color:#10b981;">${btc_p:,.0f}</h4></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="card-panel" style="text-align:center;"><h6>NET</h6><h4 style="color:#10b981;">{net_status}</h4></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="card-panel" style="text-align:center;"><h6>TYPE</h6><h4 style="color:#10b981;">SPOT</h4></div>', unsafe_allow_html=True)

    # BARIS 71: SEKARANG UDAH ADA ISI NYA
    col_left, col_right = st.columns()
    
    with col_left:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📊 Top 10 Volume")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Loading data...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📈 Live Chart")
        tv_html = '<div id="tv" style="height:300px;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","interval":"60","theme":"dark","style":"1","locale":"en","container_id":"tv"});</script>'
        components.html(tv_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)
