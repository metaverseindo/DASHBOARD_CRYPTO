import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. SETUP - WAJIB DI AWAL
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS (Dark Theme & Clean Layout)
st.markdown(r'''
<style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: sans-serif; }
    .glass-card {
        background: rgba(23, 32, 53, 0.5);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .title-text { color: #10b981; font-weight: 800; font-size: 28px; margin: 0; }
    [data-testid="stMetric"] { background: #0f172a; border-left: 5px solid #10b981; padding: 10px !important; border-radius: 8px; }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE (Provider: CoinGecko - High Stability)
@st.cache_data(ttl=30)
def fetch_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 50, 'page': 1}
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            btc = next((x for x in data if x['symbol'] == 'btc'), None)
            
            rows = []
            for item in data:
                if item['symbol'] != 'btc':
                    rows.append({
                        "ASSET": item['symbol'].upper(),
                        "PRICE": item['current_price'],
                        "CHANGE": item['price_change_percentage_24h']
                    })
            
            df = pd.DataFrame(rows).head(12)
            # Formatting Data
            df['PRICE'] = df['PRICE'].apply(lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}")
            df['CHANGE'] = df['CHANGE'].apply(lambda x: f"{x:+.2f}%")
            
            p_btc = float(btc['current_price']) if btc else 0.0
            c_btc = float(btc['price_change_percentage_24h']) if btc else 0.0
            return df, p_btc, c_btc
    except:
        pass
    return pd.DataFrame(), 0.0, 0.0

# 4. DATA PROCESSING
df_res, p_btc, c_btc = fetch_market_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# --- HEADER (Fix Baris 73: Dikasih angka 2) ---
col_1, col_2 = st.columns(2) 
with col_1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
with col_2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:10px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# --- METRICS (Fix Baris 92: Pecah variabel mandiri) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC / USD", f"${p_btc:,.0f}" if p_btc > 0 else "OFFLINE", f"{c_btc:+.2f}%")
m2.metric("STATUS", "LIVE", "STABLE")
m3.metric("FEED", "COINGECKO", "V3")
m4.metric("NETWORK", "ONLINE", "ACTIVE")

st.write("")

# --- WORKSPACE (Fix Baris 104: Pakai list rasio) ---
l_col, r_col = st.columns([1, 1.8])

with l_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Flow")
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True, hide_index=True, height=450)
    else:
        st.info("Synchronizing...")
    st.markdown('</div>', unsafe_allow_html=True)

with r_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Chart")
    tv_code = f'''
    <div id="tv_v90"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_v90", "allow_symbol_change": true
    }});
    </script>
    '''
    components.html(tv_code, height=460)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. FOOTER
st.markdown("<div style='text-align:center;color:#334155;font-size:10px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
