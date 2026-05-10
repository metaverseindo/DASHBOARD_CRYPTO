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

# 2. CSS & BOOTSTRAP (RAW STRING)
st.markdown(r'''
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; }
    .nav-bar-top {
        background-color: #0f172a;
        border-bottom: 2px solid #10b981;
        padding: 15px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    .brand-id { font-family: 'Orbitron', sans-serif; color: #10b981; font-weight: 900; font-size: 24px; letter-spacing: 1px; }
    .card-panel {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .dot-live { height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    ''', unsafe_allow_html=True)

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown('<div class="brand-id" style="font-size: 18px;">metaverseindo</div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #10b981;'>", unsafe_allow_html=True)
    nav_choice = st.radio(
        "NAVIGASI",
        ["📊 Terminal Market", "🚀 Trading Hub", "⚙️ System Settings"],
        index=0
    )
    st.markdown("---")
    st.caption("v.52 | Stable Build")

# 4. DATA ENGINE
@st.cache_data(ttl=20)
def get_master_data():
    key = st.secrets.get("BINANCE_API_KEY", None)
    endpoints = ["https://api.binance.com", "https://api1.binance.com", "https://api2.binance.com"]
    headers = {"User-Agent": "Mozilla/5.0"}
    if key: headers["X-MBX-APIKEY"] = key
    
    for base in endpoints:
        try:
            res = requests.get(f"{base}/api/v3/ticker/24hr", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                rows = []
                for item in data:
                    if item.get('symbol', '').endswith('USDT'):
                        vol = float(item.get('quoteVolume', 0))
                        if vol > 5000000:
                            rows.append({
                                "SYMBOL": item['symbol'].replace('USDT', ''),
                                "PRICE": float(item['lastPrice']),
                                "CHANGE": float(item['priceChangePercent']),
                                "VOL_RAW": vol,
                                "VOLUME 24H": f"$ {vol:,.0f}"
                            })
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(15)
                return df.drop(columns=['VOL_RAW']), f"🟢 {base.split('//')}"
        except: continue
    
    backup_df = pd.DataFrame([{"SYMBOL": "BTC", "PRICE": 0.0, "CHANGE": 0.0, "VOLUME 24H": "BUSY"}])
    return backup_df, "🔴 BUSY"

# 5. RENDER LOGIC
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# Global Navbar
st.markdown(f'''
    <div class="nav-bar-top">
        <div class="brand-id">metaverseindo</div>
        <div class="d-flex align-items-center">
            <span class="dot-live"></span>
            <span style="color: #10b981; font-size: 14px; font-weight: bold; margin-right: 20px;">LIVE MARKET</span>
            <span class="text-secondary" style="font-size: 13px;">{time_now} WIB</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

if nav_choice == "📊 Terminal Market":
    df, net_status = get_master_data()
    col_l, col_r = st.columns([1.3, 2.7])
    
    with col_l:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📊 Top Market")
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
        st.caption(f"Status: {net_status}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.write("##### 📈 Analysis Chart")
        # FIXED HTML STRING
        tv_html = '''
        <div id="tv-metaverse" style="height:500px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>
        new TradingView.widget({
            "autosize": true,
            "symbol": "BINANCE:BTCUSDT",
            "interval": "60",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tv-metaverse"
        });
        </script>
        '''
        components.html(tv_html, height=510)
        st.markdown('</div>', unsafe_allow_html=True)

elif nav_choice == "🚀 Trading Hub":
    st.markdown('<div class="card-panel"><h3>🚀 Trading Terminal</h3><p>Fasilitas trading metaverseindo sedang disiapkan.</p></div>', unsafe_allow_html=True)

elif nav_choice == "⚙️ System Settings":
    st.markdown('<div class="card-panel"><h3>⚙️ Dashboard Diagnostics</h3>', unsafe_allow_html=True)
    if "BINANCE_API_KEY" in st.secrets:
        st.success("API Connection: ENCRYPTED")
    else:
        st.warning("API Connection: PUBLIC")
    st.markdown('</div>', unsafe
