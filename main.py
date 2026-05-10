import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. CORE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. BOOTSTRAP & CUSTOM CSS INJECTION
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #0b0e11; color: #eaecef; font-family: 'Inter', sans-serif; }
    
    /* Bootstrap Override */
    .navbar-custom {
        background-color: #1e2329;
        border-bottom: 2px solid #f0b90b;
        padding: 15px 25px;
    }
    .brand-text {
        font-family: 'Orbitron', sans-serif;
        color: #f0b90b;
        font-weight: 900;
        font-size: 24px;
        text-transform: uppercase;
    }
    .card-exchange {
        background-color: #161a1e;
        border: 1px solid #2b3139;
        border-radius: 12px;
        padding: 15px;
    }
    .badge-live {
        background-color: #02c076;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 10px;
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(2, 192, 118, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(2, 192, 118, 0); }
        100% { box-shadow: 0 0 0 0 rgba(2, 192, 118, 0); }
    }
    /* DataFrame Styling */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    </style>
    
    <nav class="navbar navbar-custom mb-4">
        <div class="container-fluid">
            <span class="brand-text">META INDO PRO</span>
            <div class="d-flex align-items-center">
                <span class="badge-live me-3">LIVE MARKET</span>
                <span class="text-secondary" style="font-size: 12px;">v.Bootstrap 5.3</span>
            </div>
        </div>
    </nav>
    """, unsafe_allow_html=True)

# 3. ENGINE DATA (FAILOVER + VVIP)
@st.cache_data(ttl=20)
def get_market_data():
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
                return df.drop(columns=['VOL_RAW']), f"Connected: {base.split('//')}"
        except: continue
    return pd.DataFrame([{"SYMBOL": "BTC", "PRICE": 65000.0, "CHANGE": 0.0, "VOLUME 24H": "N/A"}]), "Offline"

# 4. RENDER CONTENT
tz = pytz.timezone('Asia/Jakarta')
df, status = get_market_data()

# Grid Layout Bootstrap (via Streamlit Columns)
col_left, col_right = st.columns([1.2, 2.8])

with col_left:
    st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
    st.write("##### 📊 Top Volume Assets")
    st.dataframe(
        df,
        column_config={
            "PRICE": st.column_config.NumberColumn("PRICE", format="$%.2f"),
            "CHANGE": st.column_config.NumberColumn("24H%", format="%+.2f%%"),
        },
        use_container_width=True, hide_index=True, height=520
    )
    st.markdown(f'<p class="text-secondary mt-2" style="font-size: 11px;">{status} | {datetime.now(tz).strftime("%H:%M:%S")} WIB</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card-exchange">', unsafe_allow_html=True)
    st.write("##### 📈 Analysis Terminal")
    tv_widget = """
    <div class="tradingview-widget-container" style="height:520px;">
      <div id="tradingview_bs5"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "60",
        "timezone": "Asia/Jakarta", "theme": "dark", "style": "1",
        "locale": "en", "toolbar_bg": "#f1f3f6", "enable_publishing": false,
        "allow_symbol_change": true, "container_id": "tradingview_bs5"
      });
      </script>
    </div>
    """
    components.html(tv_widget, height=530)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. FOOTER (Bootstrap Alert Style)
st.markdown(f"""
    <div class="container-fluid mt-4">
        <div class="alert alert-dark border-secondary text-light" role="alert" style="background-color: #1e2329;">
            <strong>Pro Mode:</strong> Jalur VVIP aktif. Gunakan chart di kanan untuk analisa teknikal mendalam.
        </div>
    </div>
    """, unsafe_allow_html=True)
