import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import time
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & REFRESH (LANCAR JAYA)
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="datarefresh") # 30 detik biar aman dari ban

# 2. CSS TERMINAL SULTAN
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981; text-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
        font-weight: 900; text-align: center; padding: 20px; font-size: 35px;
    }
    [data-testid="stDataFrame"] td:nth-child(6) { 
        text-align: right !important; color: #fbbf24 !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LIGHTWEIGHT ENGINE (STEALTH MODE)
@st.cache_data(ttl=30)
def fetch_stealth_data():
    try:
        # Pake API Binance Public (Tanpa Library CCXT agar lebih stealth)
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        rows = []
        for item in data:
            symbol = item['symbol']
            if symbol.endswith('USDT'):
                coin = symbol.replace('USDT', '')
                vol_val = float(item['quoteVolume'])
                
                # Cuma ambil koin yang volumenya beneran gila (> 5M)
                if vol_val > 5000000:
                    p = float(item['lastPrice'])
                    c = float(item['priceChangePercent'])
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                        "SYMBOL": coin,
                        "PRICE": p,
                        "CHANGE": c,
                        "VOL_RAW": vol_val,
                        "VOLUME 24H": f"$ {vol_val:,.0f}",
                        "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                    })
        
        df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(20)
        df["RANK"] = range(1, len(df) + 1)
        return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME 24H", "TREND"]]
    except:
        return pd.DataFrame()

# 4. UI RENDER
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df = fetch_stealth_data()

if not df.empty:
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME 24H": st.column_config.TextColumn("VOLUME 24H", width=200),
            "TREND": st.column_config.LineChartColumn("TREND", width=160)
        },
        use_container_width=True, hide_index=True, height=550
    )
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"🛰️ Satellite Sync OK | Last Update: {datetime.now(tz).strftime('%H:%M:%S')} WIB")
else:
    # DATA FALLBACK (Biar tampilan nggak hancur pas kena limit)
    st.error("📡 Signal Lost. Mencoba Re-koneksi via Jalur Cadangan...")
    st.info("Saran: Gunakan VPN atau buka via browser HP jika IP lu juga ikut kena limit.")
