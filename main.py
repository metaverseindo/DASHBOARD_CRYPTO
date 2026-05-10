import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP KUNCI
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="datarefresh")

# 2. CSS SULTAN (TERMINAL MODE)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981; text-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
        font-weight: 900; text-align: center; padding: 15px; font-size: 30px;
    }
    [data-testid="stDataFrame"] td:nth-child(6) { 
        text-align: right !important; color: #fbbf24 !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. PHANTOM ENGINE (DIRECT REQUEST)
@st.cache_data(ttl=30)
def fetch_phantom_data():
    # Nyoba berbagai pintu masuk (api1, api2, api3)
    endpoints = [
        "https://api1.binance.com/api/v3/ticker/24hr",
        "https://api2.binance.com/api/v3/ticker/24hr",
        "https://api3.binance.com/api/v3/ticker/24hr"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in endpoints:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                rows = []
                for item in data:
                    sym = item['symbol']
                    if sym.endswith('USDT'):
                        coin = sym.replace('USDT', '')
                        vol = float(item['quoteVolume'])
                        if vol > 5000000: # Filter volume Sultan
                            p = float(item['lastPrice'])
                            c = float(item['priceChangePercent'])
                            rows.append({
                                "RANK": 0,
                                "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                                "SYMBOL": coin,
                                "PRICE": p,
                                "CHANGE": c,
                                "VOL_RAW": vol,
                                "VOLUME 24H": f"$ {vol:,.0f}",
                                "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                            })
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
                df["RANK"] = range(1, len(df) + 1)
                return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME 24H", "TREND"]], "STABLE"
        except:
            continue
            
    # --- JALUR TERAKHIR: DATA STANDBY (ANTI-BLANK) ---
    # Jika semua API blokir, kita kasih data simulasi biar terminal tetep hidup
    mock_data = [
        {"RANK": 1, "ICON": "https://www.google.com/s2/favicons?domain=bitcoin.org", "SYMBOL": "BTC", "PRICE": 65432.10, "CHANGE": 1.5, "VOLUME 24H": "$ 32,450,120,000", "TREND":},
        {"RANK": 2, "ICON": "https://www.google.com/s2/favicons?domain=ethereum.org", "SYMBOL": "ETH", "PRICE": 3456.78, "CHANGE": -0.8, "VOLUME 24H": "$ 15,200,450,000", "TREND":}
    ]
    return pd.DataFrame(mock_data), "STANDBY"

# 4. RENDER
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df, status = fetch_phantom_data()

if not df.empty:
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.2f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME 24H": st.column_config.TextColumn("VOLUME 24H", width=200),
            "TREND": st.column_config.LineChartColumn("TREND", width=160)
        },
        use_container_width=True, hide_index=True, height=500
    )
    
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz).strftime('%H:%M:%S')
    if status == "STABLE":
        st.success(f"🟢 CONNECTION: SECURE | SYNC: {now} WIB")
    else:
        st.warning(f"🟡 CONNECTION: LIMITED (Standby Mode) | SYNC: {now} WIB")
else:
    st.error("📡 Signal Lost. Terminal in Emergency Lockdown.")
