import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS TERMINAL
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow { color: #10b981; text-shadow: 0 0 15px #10b981; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE (PASTI JALAN)
@st.cache_data(ttl=30)
def get_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        rows = []
        for item in data:
            if item['symbol'].endswith('USDT'):
                v = float(item['quoteVolume'])
                if v > 10000000: # Cuma ambil koin volume $10M+
                    rows.append({
                        "SYMBOL": item['symbol'].replace('USDT', ''),
                        "PRICE": float(item['lastPrice']),
                        "24H %": float(item['priceChangePercent']),
                        "VOL_RAW": v,
                        "VOLUME": f"$ {v:,.0f}"
                    })
        df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
        return df.drop(columns=['VOL_RAW']), "LIVE"
    except:
        # DATA STANDBY - Gue rapihin total biar GAK ADA ERROR LAGI
        backup = [
            {"SYMBOL": "BTC", "PRICE": 65000.0, "24H %": 1.5, "VOLUME": "$ 30,000,000,000"},
            {"SYMBOL": "ETH", "PRICE": 3500.0, "24H %": -0.5, "VOLUME": "$ 15,000,000,000"},
            {"SYMBOL": "SOL", "PRICE": 145.0, "24H %": 4.0, "VOLUME": "$ 5,000,000,000"}
        ]
        return pd.DataFrame(backup), "STANDBY"

# 4. TAMPILAN
st.markdown('<h1 class="glow">📊 META INDO TERMINAL</h1>', unsafe_allow_html=True)

df, mode = get_data()

st.dataframe(
    df,
    column_config={
        "PRICE": st.column_config.NumberColumn("PRICE", format="$%.2f"),
        "24H %": st.column_config.NumberColumn("CHANGE", format="%+.2f%%"),
    },
    use_container_width=True,
    hide_index=True
)

st.caption(f"Status: {mode} | {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')} WIB")
