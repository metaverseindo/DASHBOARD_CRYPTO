import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STYLING (V.63 Style)
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

# 3. DATA ENGINE (Original Binance Feed)
@st.cache_data(ttl=15)
def get_crypto_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if r.status_code == 200:
            data = r.json()
            btc = next((i for i in data if i['symbol'] == "BTCUSDT"), None)
            rows = []
            for i in data:
                if i['symbol'].endswith('USDT') and float(i.get('quoteVolume', 0)) > 30000000:
                    change = float(i['priceChangePercent'])
                    # Indikator Jual/Beli (Warna)
                    indicator = "🟢" if change >= 0 else "🔴"
                    rows.append({
                        "ASSET": i['symbol'].replace('USDT',''),
                        "PRICE": float(i['lastPrice']),
                        "24H %": change,
                        "SIGNAL": indicator
                    })
            df = pd.DataFrame(rows).head(12)
            # Formatting
            df['PRICE'] = df['PRICE'].apply(lambda x: f"{x:,.2f}" if x >= 1 else f"{x:.6f}")
            df['24H %'] = df['24H %'].apply(lambda x: f"{x:+.2f}%")
            return df, float(btc['lastPrice']), float(btc['priceChangePercent'])
    except: pass
    return pd.DataFrame(), 0.0, 0.0

# 4. RENDER UI
df, btc_p, btc_c = get_crypto_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# HEADER
c1, c2 = st.columns(2)
with c1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='text-align:right; color:#64748b; padding-top:10px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC", f"${btc_p:,.0f}", f"{btc_c}%")
m2.metric("STATUS", "LIVE", "OK")
m3.metric("FEED", "BINANCE", "SPOT")
m4.metric("VOL", ">30M", "STABLE")

st.write("")

# WORKSPACE
left, right = st.columns([1, 1.8])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Snapshot")
    if not df.empty:
        # Balikin Logika Warna Merah/Hijau di Tabel
        def color_pick(val):
            color = '#10b981' if '+' in val else '#ef4444'
            return f'color: {color}'
        st.dataframe(df.style.map(color_pick, subset=['24H %']), use_container_width=True, hide_index=True, height=450)
    else:
        st.info("Awaiting connection...")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Chart")
    tv_v63 = f'''
    <div id="tv_v63"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_v63", "allow_symbol_change": true
    }});
    </script>
    '''
    components.html(tv_v63, height=460)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#1e293b; font-size:10px; margin-top:20px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
