import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# 1. SETTING DASAR (WAJIB PALING ATAS)
st.set_page_config(page_title="metaverseindo", layout="wide")

# 2. CSS SIMPEL (Gak bakal ngerusak layout mobile)
st.markdown("""
    <style>
    .main { background-color: #020617; }
    .stMetric { background-color: #0f172a; padding: 15px; border-radius: 10px; border: 1px solid #10b981; }
    div[data-testid="stExpander"] { border: 1px solid #10b981; background-color: #0f172a; }
    header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. FUNGSI AMBIL DATA
@st.cache_data(ttl=20)
def get_data():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        data = res.json()
        btc = next(i for i in data if i['symbol'] == "BTCUSDT")
        
        rows = []
        for i in data:
            if i['symbol'].endswith('USDT'):
                vol = float(i.get('quoteVolume', 0))
                if vol > 20000000: # Filter koin ramai aja
                    rows.append({
                        "COIN": i['symbol'].replace('USDT',''),
                        "PRICE": f"{float(i['lastPrice']):,.2f}",
                        "24h %": f"{float(i['priceChangePercent'])}%"
                    })
        return pd.DataFrame(rows).head(15), float(btc['lastPrice']), float(btc['priceChangePercent'])
    except:
        return pd.DataFrame(), 0, 0

# 4. HEADER
st.title("🟢 metaverseindo")
col1, col2 = st.columns(2)

df, btc_p, btc_c = get_data()

with col1:
    st.metric("BTC PRICE", f"${btc_p:,.0f}", f"{btc_c}%")
with col2:
    tz = pytz.timezone('Asia/Jakarta')
    st.metric("TIME (WIB)", datetime.now(tz).strftime("%H:%M"), "LIVE")

st.divider()

# 5. TABEL DATA (FULL WIDTH BIAR GAMPANG DIBACA DI HP)
st.subheader("📊 Top Market Volume")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.error("Koneksi API Binance sibuk. Refresh manual.")

st.divider()

# 6. TRADINGVIEW (DI TARUH DI BAWAH BIAR LEGA)
st.subheader("📈 Quick Analysis")
with st.expander("Klik untuk Buka Chart", expanded=True):
    tv_html = """
    <div id="tv_chart"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "width": "100%", "height": 450, "symbol": "BINANCE:BTCUSDT",
      "interval": "60", "theme": "dark", "style": "1", "locale": "en",
      "container_id": "tv_chart", "allow_symbol_change": true
    });
    </script>
    """
    components.html(tv_html, height=460)

# 7. SIDEBAR SIMPEL
st.sidebar.image("https://cryptologos.cc/logos/ethereum-eth-logo.png", width=50)
st.sidebar.title("metaverseindo")
st.sidebar.write("Terminal ini dioptimasi untuk tampilan Mobile & Desktop.")
