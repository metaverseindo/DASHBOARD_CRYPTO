import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (DARK LUXURY)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        font-weight: 900;
        text-align: center;
        padding: 10px;
    }
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (SUPER FAST & LIGHT)
@st.cache_data(ttl=12)
def fetch_top_data():
    try:
        # Pake Binance karena API-nya paling stabil buat server Cloud
        ex = ccxt.binance({'timeout': 10000, 'enableRateLimit': True})
        tickers = ex.fetch_tickers()
        rows = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                coin = sym.split('/')
                # Filter koin sampah, cuma ambil yang volumenya signifikan (biar enteng)
                if float(v['quoteVolume']) > 100000:
                    p = float(v['last'])
                    c = float(v.get('percentage', 0) or 0)
                    
                    # FORMAT VOLUME SULTAN (String)
                    vol_val = float(v['quoteVolume'])
                    vol_str = f"${vol_val:,.0f}"
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                        "SYMBOL": coin,
                        "PRICE": p,
                        "CHANGE": c,
                        "VOLUME_RAW": vol_val,
                        "VOLUME": vol_str,
                        "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                    })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            # Sort berdasarkan angka asli, ambil top 30
            df = df.sort_values("VOLUME_RAW", ascending=False).head(30)
            df["RANK"] = range(1, len(df) + 1)
            return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME", "TREND"]]
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# 4. UI HEADER
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df = fetch_top_data()

if not df.empty:
    # 5. RENDER TABEL
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.TextColumn("VOLUME 24H", width=180), # Teks biar rata kanan & koma muncul
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=650
    )
    
    # FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Meta Indo Engine v30.0")
else:
    st.info("🔄 Connecting to API... Jika tetap blank, pastikan file 'requirements.txt' sudah benar.")
