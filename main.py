import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=20000, key="freshengine") # Update tiap 20 detik

# 2. CSS STYLING (Tetap Dark & Pro)
st.markdown(r'''
<style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: sans-serif; }
    .glass-card {
        background: rgba(23, 32, 53, 0.45);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .title-text { color: #10b981; font-weight: 800; font-size: 32px; margin: 0; }
    [data-testid="stMetric"] { background: #0f172a; border-left: 5px solid #10b981; padding: 15px !important; border-radius: 10px; }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE (REALTIME FEED)
@st.cache_data(ttl=10)
def get_realtime_data():
    try:
        # Pake CryptoCompare buat kestabilan tingkat tinggi
        symbols = "BTC,ETH,BNB,SOL,XRP,ADA,DOGE,AVAX,TRX,DOT,LINK,MATIC"
        url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols}&tsyms=USD"
        r = requests.get(url, timeout=10)
        
        if r.status_code == 200:
            raw = r.json()['RAW']
            rows = []
            for coin in raw:
                data = raw[coin]['USD']
                change = float(data['CHANGEPCT24HOUR'])
                rows.append({
                    "ASSET": coin,
                    "PRICE": float(data['PRICE']),
                    "24H %": change,
                    "TREND": "🟢" if change >= 0 else "🔴"
                })
            
            df = pd.DataFrame(rows)
            # Ambil BTC secara spesifik buat metrik
            btc_price = raw['BTC']['USD']['PRICE']
            btc_change = raw['BTC']['USD']['CHANGEPCT24HOUR']
            
            # Format tampilan tabel
            df_display = df.copy()
            df_display['PRICE'] = df_display['PRICE'].apply(lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}")
            df_display['24H %'] = df_display['24H %'].apply(lambda x: f"{x:+.2f}%")
            
            return df_display, float(btc_price), float(btc_change)
    except:
        pass
    return pd.DataFrame(), 0.0, 0.0

# 4. EXECUTE
df_market, btc_p, btc_c = get_realtime_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# --- HEADER ---
h1, h2 = st.columns(2)
with h1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
with h2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:15px;font-family:monospace;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# --- METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC / USD", f"${btc_p:,.0f}" if btc_p > 0 else "CONNECTING...", f"{btc_c:+.2f}%")
m2.metric("STATUS", "LIVE", "STABLE")
m3.metric("FEED", "CRYPTOCOMPARE", "REALTIME")
m4.metric("LOGIC", "TREND-ON", "ACTIVE")

st.write("")

# --- WORKSPACE ---
l_col, r_col = st.columns([1, 1.8])

with l_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Snapshot")
    if not df_market.empty:
        # Indikator warna teks
        def color_logic(val):
            color = '#10b981' if '+' in val else '#ef4444'
            return f'color: {color}'
        st.dataframe(df_market.style.map(color_logic, subset=['24H %']), use_container_width=True, hide_index=True, height=450)
    else:
        st.warning("Fetching data stream... Please wait.")
    st.markdown('</div>', unsafe_allow_html=True)

with r_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Chart")
    tv_code = f'''
    <div id="tv_v94"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_v94", "allow_symbol_change": true
    }});
    </script>
    '''
    components.html(tv_code, height=460)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#1e293b;font-size:10px;margin-top:20px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
