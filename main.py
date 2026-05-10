import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="META INDO PRO", layout="wide")
st_autorefresh(interval=30000, key="freshengine")

# --- KONEKSI VVIP (BINANCE API KEY) ---
# Ambil dari Streamlit Secrets (Dashboard Streamlit > Settings > Secrets)
api_key = st.secrets.get("BINANCE_API_KEY", "")
api_secret = st.secrets.get("BINANCE_SECRET_KEY", "")

@st.cache_data(ttl=20)
def get_vvip_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Kalau API Key ada, kita kirim lewat header biar diprioritaskan Binance
    if api_key:
        headers["X-MBX-APIKEY"] = api_key

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        rows = []
        for item in data:
            if item['symbol'].endswith('USDT'):
                v = float(item['quoteVolume'])
                if v > 5000000:
                    rows.append({
                        "SYMBOL": item['symbol'].replace('USDT', ''),
                        "PRICE": float(item['lastPrice']),
                        "CHANGE": float(item['priceChangePercent']),
                        "VOL_RAW": v,
                        "VOLUME": f"$ {v:,.0f}"
                    })
        df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
        return df.drop(columns=['VOL_RAW']), "VVIP LIVE"
    except:
        backup = [
            {"SYMBOL": "BTC", "PRICE": 65000.0, "CHANGE": 1.5, "VOLUME": "$ 30B+"},
            {"SYMBOL": "ETH", "PRICE": 3500.0, "CHANGE": -0.5, "VOLUME": "$ 15B+"}
        ]
        return pd.DataFrame(backup), "STANDBY"

st.markdown('<h2 style="text-align:center;color:#10b981;">📊 META INDO PRO TERMINAL</h2>', unsafe_allow_html=True)

df, mode = get_vvip_data()

st.dataframe(
    df,
    column_config={
        "PRICE": st.column_config.NumberColumn("PRICE", format="$%.2f"),
        "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%"),
    },
    use_container_width=True,
    hide_index=True
)

st.caption(f"Status: {mode} | Sync: {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')} WIB")
