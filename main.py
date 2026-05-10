import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide")
st_autorefresh(interval=30000, key="freshengine")

# 2. STYLE SULTAN
st.markdown("""<style>header, footer, #MainMenu {visibility: hidden;} .stApp { background-color: #020617; } .glow-header { color: #10b981; text-shadow: 0 0 15px #10b981; font-weight: 900; text-align: center; padding: 15px; font-size: 35px; }</style>""", unsafe_allow_html=True)

# 3. ENGINE NYAWA CADANGAN
@st.cache_data(ttl=20)
def fetch_data_safe():
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

    # JIKA SEMUA GAGAL, TAMPILKAN DATA STANDBY BIAR GAK KOSONG
    backup = [
        {"SYMBOL": "BTC", "PRICE": 65432.10, "CHANGE": 1.25, "VOLUME 24H": "$ 35,000,000,000"},
        {"SYMBOL": "ETH", "PRICE": 3456.78, "CHANGE": -0.45, "VOLUME 24H": "$ 18,000,000,000"},
        {"SYMBOL": "SOL", "PRICE": 145.20, "CHANGE": 3.10, "VOLUME 24H": "$ 6,000,000,000"}
    ]
    return pd.DataFrame(backup), "🔴 SERVERS BUSY (SHOWING STANDBY DATA)"

# 4. RENDER
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

# Indikator Key
if "BINANCE_API_KEY" in st.secrets:
    st.success("✅ API KEY TERDETEKSI: Menggunakan jalur VVIP.")
else:
    st.warning("⚠️ API KEY TIDAK ADA: Menggunakan jalur Publik.")

df, status_label = fetch_data_safe()

# TABLE TAMPIL DISINI
st.dataframe(
    df,
    column_config={
        "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.2f"),
        "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%"),
    },
    use_container_width=True, 
    hide_index=True
)

tz = pytz.timezone('Asia/Jakarta')
st.caption(f"**STATUS:** {status_label} | **SYNC:** {datetime.now(tz).strftime('%H:%M:%S')} WIB")
