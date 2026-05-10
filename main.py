import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE SETUP
st.set_page_config(
    page_title="META INDO PRO", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Refresh otomatis tiap 30 detik
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS SULTAN (EXCHANGE PROFESSIONAL LOOK)
st.markdown("""
    <style>
    /* Reset & Background */
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { 
        background-color: #0b0e11; 
        color: #eaecef; 
        font-family: 'Inter', sans-serif;
    }
    .block-container { padding: 1rem 2rem; }

    /* Custom Header Bar */
    .exchange-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 25px;
        background-color: #1e2329;
        border-bottom: 2px solid #2b3139;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    .brand-id {
        color: #f0b90b;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(240, 185, 11, 0.4);
    }
    .live-dot {
        height: 10px;
        width: 10px;
        background-color: #02c076;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2, 192, 118, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(2, 192, 118, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2, 192, 118, 0); }
    }

    /* DataFrame / Table UI */
    [data-testid="stDataFrame"] {
        background-color: #161a1e;
        border: 1px solid #2b3139;
        border-radius: 12px;
    }
    
    /* Typography & Headers */
    h3 {
        color: #848e9c !important;
        font-size: 16px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #474d57; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (TRIPLE FAILOVER)
@st.cache_data(ttl=20)
def fetch_exchange_master():
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
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
                return df.drop(columns=['VOL_RAW']), f"🟢 VVIP LIVE ({base.split('//')})"
        except:
            continue
    
    # Data Cadangan biar gak zonk
    backup = [{"SYMBOL": "BTC", "PRICE": 65432.1, "CHANGE": 1.2, "VOLUME 24H": "$ 30B+"}]
    return pd.DataFrame(backup), "🔴 SYNCING..."

# 4. NAVBAR RENDER
tz = pytz.timezone('Asia/Jakarta')
st.markdown(f"""
    <div class="exchange-navbar">
        <div class="brand-id">META INDO PRO</div>
        <div>
            <span class="live-dot"></span>
            <span style="color: #02c076; font-size: 14px; font-weight: bold;">MARKET ACTIVE</span>
        </div>
        <div style="color: #848e9c; font-size: 13px;">{datetime.now(tz).strftime('%H:%M:%S')} WIB</div>
    </div>
    """, unsafe_allow_html=True)

# 5. MAIN INTERFACE (COLUMNS)
col_market, col_chart = st.columns([1.2, 2.8])

df, status_label = fetch_exchange_master()

with col_market:
    st.markdown("### 🏦 Market Overview")
    st.dataframe(
        df,
        column_config={
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.2f"),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%"),
        },
        use_container_width=True,
        hide_index=True,
        height=550
    )
    st.caption(f"Network Status: {status_label}")

with col_chart:
    st.markdown("### 📈 Live Technical Analysis")
    # INTEGRASI TRADINGVIEW CHART (PRO FEATURES)
    tv_widget = """
    <div class="tradingview-widget-container" style="height:550px;">
      <div id="tradingview_full"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true,
        "symbol": "BINANCE:BTCUSDT",
        "interval": "60",
        "timezone": "Asia/Jakarta",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_full"
      });
      </script>
    </div>
    """
    components.html(tv_widget, height=560)

# 6. FOOTER STATS
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1:
    if "BINANCE_API_KEY" in st.secrets:
        st.success("🔒 API Connection: Encrypted VVIP")
    else:
        st.warning("🔓 API Connection: Public Path")
with f2:
    st.info("💡 Pro Tip: Use the chart sidebar to draw your own technical analysis.")
with f3:
    st.write(f"**Last Data Refresh:** {datetime.now(tz).strftime('%d %b %Y | %H:%M:%S')}")
