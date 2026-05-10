import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. SETUP & REFRESH
st.set_page_config(page_title="metaverseindo", layout="wide")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS PREMIUM (Responsive & No Leaking)
st.markdown(r'''
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
    /* Global Reset */
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; font-family: 'Inter', sans-serif; }
    
    /* Brand Header */
    .brand-container {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        border-bottom: 2px solid #10b981;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    .brand-name { font-family: 'Orbitron', sans-serif; color: #10b981; font-size: 28px; letter-spacing: 2px; }
    
    /* Card Panel */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; }
    .metric-value { font-size: 20px; color: #10b981; font-weight: bold; }

    /* Hide Column Gap on Mobile */
    [data-testid="column"] { padding: 0px 5px !important; }
    
    @media (max-width: 768px) {
        .brand-name { font-size: 20px; }
        .metric-value { font-size: 16px; }
    }
    </style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=15)
def get_crypto_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        data = res.json()
        btc = next(i for i in data if i['symbol'] == "BTCUSDT")
        rows = []
        for i in data:
            if i['symbol'].endswith('USDT') and float(i.get('quoteVolume', 0)) > 20000000:
                rows.append({
                    "ASSET": i['symbol'].replace('USDT',''),
                    "PRICE": f"{float(i['lastPrice']):,.2f}",
                    "24H %": f"{float(i['priceChangePercent'])}%"
                })
        return pd.DataFrame(rows).head(15), float(btc['lastPrice'])
    except:
        return pd.DataFrame(), 0

# 4. RENDER UI
df, btc_price = get_crypto_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M")

# Header
st.markdown(f'''
    <div class="brand-container">
        <div class="brand-name">METAVERSEINDO</div>
        <div style="font-size: 12px; color: #64748b;">Terminal v.68 • {time_now} WIB</div>
    </div>
''', unsafe_allow_html=True)

# Metrics bar
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Bitcoin</div><div class="metric-value">${btc_price:,.0f}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value">ONLINE</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Market</div><div class="metric-value">SPOT</div></div>', unsafe_allow_html=True)

# Table Area
st.markdown('<div style="background-color: #0f172a; padding: 15px; border-radius: 12px; border: 1px solid #334155;">', unsafe_allow_html=True)
st.write("### 📊 Top Assets")
st.dataframe(df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Chart Area (Full Width di Desktop & Mobile)
with st.expander("🔍 ANALYSIS CHART", expanded=True):
    tv_html = '''
    <div id="tradingview_meta"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "toolbar_bg": "#f1f3f6", "enable_publishing": false,
      "allow_symbol_change": true, "container_id": "tradingview_meta"
    });
    </script>
    '''
    components.html(tv_html, height=460)

# Sidebar (Minimalist)
st.sidebar.markdown('<p style="font-family:Orbitron; color:#10b981;">metaverseindo</p>', unsafe_allow_html=True)
st.sidebar.caption("Stable Pro Dashboard")
