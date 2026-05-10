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

# 2. CSS
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

# 3. DATA ENGINE (Optimized)
@st.cache_data(ttl=15)
def get_data():
    try:
        # Panggil API Binance
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if r.status_code == 200:
            all_data = r.json()
            
            # Ambil BTC buat metrik atas
            btc = next((i for i in all_data if i['symbol'] == "BTCUSDT"), None)
            
            # Filter Koin
            processed_rows = []
            for i in all_data:
                symbol = i['symbol']
                # Cuma ambil pasangan USDT
                if symbol.endswith('USDT') and not symbol.startswith('BTC'):
                    vol = float(i.get('quoteVolume', 0))
                    # FILTER: Kita turunkan ke 10jt USDT biar data pasti muncul
                    if vol > 10000000: 
                        processed_rows.append({
                            "SYMBOL": symbol.replace('USDT',''),
                            "PRICE": float(i['lastPrice']),
                            "CHANGE": float(i['priceChangePercent']),
                            "VOLUME_RAW": vol # Buat sorting
                        })
            
            # Sortir berdasarkan volume terbesar
            df = pd.DataFrame(processed_rows)
            if not df.empty:
                df = df.sort_values(by="VOLUME_RAW", ascending=False).head(12)
                # Format angka setelah disortir
                df['PRICE'] = df['PRICE'].apply(lambda x: f"{x:,.2f}")
                df['CHANGE'] = df['CHANGE'].apply(lambda x: f"{x}%")
                # Buang kolom volume raw biar gak menuhin tabel
                df = df[["SYMBOL", "PRICE", "CHANGE"]]
            
            btc_p = float(btc['lastPrice']) if btc else 0.0
            btc_c = float(btc['priceChangePercent']) if btc else 0.0
            
            return df, btc_p, btc_c
    except Exception as e:
        print(f"Error: {e}")
    return pd.DataFrame(), 0.0, 0.0

# 4. UI RENDER
df, btc_p, btc_c = get_data()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# HEADER
c1, c2 = st.columns(2)
with c1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:10px;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC", f"${btc_p:,.0f}", f"{btc_c}%")
m2.metric("STATUS", "LIVE", "OK")
m3.metric("FEED", "BINANCE", "SPOT")
m4.metric("VOL FILTER", ">10M", "ACTIVE")

st.write("")

# 5. WORKSPACE
left, right = st.columns([1, 1.8])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊 Market Snapshot")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=450)
    else:
        # Pesan jika data kosong
        st.warning("No high volume coins found. Try refreshing.")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Live Chart")
    tv = f'''
    <div id="tv_v85"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_v85", "allow_symbol_change": true
    }});
    </script>
    '''
    components.html(tv, height=460)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#334155;font-size:10px;'>© 2026 METAVERSEINDO</div>", unsafe_allow_html=True)
