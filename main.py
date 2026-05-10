import streamlit as st
import pandas as pd
import requests
import pytz
# Cek apakah key kebaca (ini bakal muncul di layar app lu)
if "BINANCE_API_KEY" in st.secrets:
    st.write("✅ Sistem mendeteksi API Key di Secrets!")
else:
    st.write("❌ Sistem TIDAK menemukan API Key di Secrets.")
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="META INDO PRO", layout="wide")
st_autorefresh(interval=30000, key="freshengine")

# 1. CSS SULTAN
st.markdown("""<style>header, footer, #MainMenu {visibility: hidden;} .stApp { background-color: #020617; } .glow-header { color: #10b981; text-shadow: 0 0 15px #10b981; font-weight: 900; text-align: center; padding: 15px; font-size: 30px; }</style>""", unsafe_allow_html=True)

# 2. ENGINE VVIP SENSOR
@st.cache_data(ttl=20)
def fetch_vvip_data():
    # CEK APAKAH KEY KEBACA DARI SECRETS
    key = st.secrets.get("BINANCE_API_KEY", None)
    
    url = "https://api.binance.com/api/v3/ticker/24hr"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    if key:
        headers["X-MBX-APIKEY"] = key
        label = "🟢 VVIP LIVE"
    else:
        label = "🟡 LIVE (NO KEY DETECTED)"

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            rows = []
            for item in data:
                if item.get('symbol', '').endswith('USDT'):
                    coin = item['symbol'].replace('USDT', '')
                    vol = float(item.get('quoteVolume', 0))
                    if vol > 5000000:
                        rows.append({
                            "SYMBOL": coin,
                            "PRICE": float(item.get('lastPrice', 0)),
                            "CHANGE": float(item.get('priceChangePercent', 0)),
                            "VOL_RAW": vol,
                            "VOLUME 24H": f"$ {vol:,.0f}"
                        })
            df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(25)
            return df.drop(columns=['VOL_RAW']), label
    except:
        pass
        
    return pd.DataFrame([{"SYMBOL": "BTC", "PRICE": 65000, "CHANGE": 1.5, "VOLUME 24H": "$ 30B+"}]), "🔴 STANDBY (OFFLINE)"

# 3. TAMPILAN
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df, status = fetch_vvip_data()

# PESAN DEBUG (LU BISA HAPUS KALAU UDAH LIVE)
if "NO KEY" in status:
    st.info("💡 Tips: API Key belum terdeteksi. Pastikan lu udah Save di menu 'Secrets' di dashboard Streamlit.")

st.dataframe(df, use_container_width=True, hide_index=True)

tz = pytz.timezone('Asia/Jakarta')
st.caption(f"Status: {status} | {datetime.now(tz).strftime('%H:%M:%S')} WIB")
