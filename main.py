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
    .dot-live { height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    ''', unsafe_allow_html=True)

# 3. DATA ENGINE (SMART FAILOVER)
@st.cache_data(ttl=15)
def get_crypto_data():
    # List endpoint cadangan kalau yang utama sibuk
    urls = [
        "https://api.binance.com/api/v3/ticker/24hr",
        "https://api1.binance.com/api/v3/ticker/24hr",
        "https://api2.binance.com/api/v3/ticker/24hr"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                btc_price = next((float(i['lastPrice']) for i in data if i['symbol'] == "BTCUSDT"), 0)
                rows = []
                for i in data:
                    symbol = i.get('symbol', '')
                    if symbol.endswith('USDT'):
                        vol = float(i.get('quoteVolume', 0))
                        if vol > 5000000: # Volume > 5jt biar data gak kosong
                            rows.append({"SYMBOL": symbol.replace('USDT',''), "PRICE": float(i['lastPrice']), "CHANGE": float(i['priceChangePercent']), "VOL": vol})
                
                if rows:
                    df = pd.DataFrame(rows).sort_values("VOL", ascending=False).head(15)
                    return df.drop(columns=['VOL']), btc_price, "🟢 ONLINE"
        except:
            continue
    return pd.DataFrame(), 0, "🔴 RECONNECTING"

# 4. SIDEBAR
with st.sidebar:
    st.markdown('<div class="brand-id" style="font-size: 18px;">metaverseindo</div>', unsafe_allow_html=True)
    st.markdown("---")
    nav_choice = st.radio("NAVIGASI", ["📊 Terminal Market", "🚀 Trading Hub", "⚙️ System Settings"])
    st.caption("v.57 | Stable Streamlit")

# 5. NAVBAR
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")
st.markdown(f'''<div class="nav-bar-top"><div class="brand-id">metaverseindo</div><div class="d-flex align-items-center"><span class="dot-live"></span><span style="color:#10b981;font-weight:bold;margin-right:20px;">LIVE</span><span class="text-secondary" style="font-size:13px;">{time_now} WIB</span></div></div>''', unsafe_allow_html=True)

# 6. MAIN CONTENT
if nav_choice == "📊 Terminal Market":
    df, btc_p, net_status = get_crypto_data()

    # METRICS AREA
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="card-panel" style="text-align:center;"><h6>BTC PRICE</h6><h4 style="color:#10b981;">${btc_p:,.2f}</h4></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="card-panel" style="text-align:center;"><h6>NETWORK</h6><h4 style="color:#10b981;">{net_status}</h4></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="card-panel" style="text-align:center;"><h6>ASSET TYPE</h6><h4 style="color:#10b981;">SPOT/USDT</h4></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.3, 2.7])
    with col_l:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📊 Market Volume")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        else:
            st.error("Gagal narik data. Coba Refresh browser.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📈 Live Chart")
        tv_html = '<div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","interval":"60","theme":"dark","style":"1","locale":"en","container_id":"tv"});</script>'
        components.html(tv_html, height=410)
        st.markdown('</div>', unsafe_allow_html=True)
