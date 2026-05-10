import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30000, key="freshengine")

# 2. BOOTSTRAP ENGINE & CSS
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #0b0e11; color: #eaecef; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #1e2329; border-right: 1px solid #f0b90b; }
    
    /* Navbar Custom */
    .navbar-custom { background-color: #1e2329; border-bottom: 2px solid #f0b90b; padding: 15px 25px; margin-bottom: 20px; }
    .brand-text { font-family: 'Orbitron', sans-serif; color: #f0b90b; font-weight: 900; font-size: 22px; }
    
    /* Card Exchange */
    .card-exchange { background-color: #161a1e; border: 1px solid #2b3139; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .badge-live { background-color: #02c076; color: white; padding: 4px 8px; border-radius: 4px; font-size: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR MENU (PENGATUR HALAMAN)
with st.sidebar:
    st.markdown('<p class="brand-text">META INDO</p>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio(
        "NAVIGASI MENU",
        ["📊 Terminal Market", "🚀 Trade & Portfolio", "⚙️ System Settings"],
        index=0
    )
    st.markdown("---")
    st.caption("v.45 | Built with Bootstrap 5")

# 4. DATA ENGINE (FAILOVER)
@st.cache_data(ttl=20)
def get_live_data():
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
                            rows.append({"SYMBOL": item['symbol'].replace('USDT', ''), "PRICE": float(item['lastPrice']), "CHANGE": float(item['priceChangePercent']), "VOL_RAW": vol})
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(15)
                return df, f"🟢 VVIP ({base.split('//')})"
        except: continue
    return pd.DataFrame([{"SYMBOL": "BTC", "PRICE": 0, "CHANGE": 0, "VOL_RAW": 0}]), "🔴 OFFLINE"

# 5. LOGIKA HALAMAN
tz = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz).strftime("%H:%M:%S")

# NAVBAR ATAS (Statis di semua menu)
st.markdown(f"""
    <nav class="navbar navbar-custom">
        <div class="container-fluid">
            <span class="brand-text">META INDO PRO</span>
            <div class="d-flex align-items-center">
                <span class="badge-live me-3">LIVE</span>
                <span class="text-secondary" style="font-size: 13px;">{now} WIB</span>
            </div>
        </div>
    </nav>
    """, unsafe_allow_html=True)

if menu == "📊 Terminal Market":
    df, status = get_live_data()
    col_l, col_r = st.columns([1.2, 2.8])
    
    with col_l:
        st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
        st.write("##### 📊 Top Assets")
        st.dataframe(df.drop(columns=['VOL_RAW']), column_config={"PRICE": st.column_config.NumberColumn("PRICE", format="$%.2f"), "CHANGE": st.column_config.NumberColumn("24H%", format="%+.2f%%")}, use_container_width=True, hide_index=True, height=500)
        st.caption(f"Status: {status}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
        st.write("##### 📈 Analysis Chart")
        components.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "H", "timezone": "Asia/Jakarta", "theme": "dark", "style": "1", "locale": "en", "toolbar_bg": "#f1f3f6", "enable_publishing": false, "allow_symbol_change": true, "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚀 Trade & Portfolio":
    st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
    st.write("## 🚀 Trading Hub")
    st.write("Menu ini sedang disiapkan untuk integrasi Trade Order langsung ke Binance.")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Estimated Balance", "$ 0.00", "0%")
    with c2:
        st.metric("Active Trades", "0 Pairs", "Stable")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ System Settings":
    st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
    st.write("## ⚙️ System Settings")
    st.write("### API Connection Info")
    if "BINANCE_API_KEY" in st.secrets:
        st.success("API Key Detected: [PROTECTED]")
    else:
        st.error("API Key Not Found! Please check Streamlit Secrets.")
    st.write("---")
    st.write("### Theme Preference")
    st.toggle("High Contrast Mode (Coming Soon)")
    st.markdown('</div>', unsafe_allow_html=True)
