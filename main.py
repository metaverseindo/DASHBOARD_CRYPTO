import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS SULTAN UI
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981; text-shadow: 0 0 15px #10b981;
        font-weight: 900; text-align: center; padding: 15px; font-size: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE VVIP (STEALTH MODE)
@st.cache_data(ttl=20)
def fetch_vvip_data():
    # Mengambil key dari Secrets Dashboard
    api_key = st.secrets.get("BINANCE_API_KEY", "")
    
    url = "https://api.binance.com/api/v3/ticker/24hr"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Kirim identitas VVIP ke Binance
    if api_key:
        headers["X-MBX-APIKEY"] = api_key

    try:
        res = requests.get(url, headers=headers, timeout=10)
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
        if rows:
            df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
            return df.drop(columns=['VOL_RAW']), "VVIP LIVE"
    except:
        pass
        
    # BACKUP JIKA KONEKSI REWEL
    backup = [
        {"SYMBOL": "BTC", "PRICE": 65000.0, "CHANGE": 1.5, "VOLUME 24H": "$ 30B+"},
        {"SYMBOL": "ETH", "PRICE": 3500.0, "CHANGE": -0.5, "VOLUME 24H": "$ 15B+"},
        {"SYMBOL": "SOL", "PRICE": 145.0, "CHANGE": 4.2, "VOLUME 24H": "$ 5B+"}
    ]
    return pd.DataFrame(backup), "STANDBY (API LIMIT)"

# 4. RENDER TERMINAL
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df, mode = fetch_vvip_data()

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
st.caption(f"Status: {mode} | Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB")
