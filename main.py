import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (KUNCI MATI)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
        font-weight: 900;
        text-align: center;
        padding: 20px;
        font-size: 32px;
    }
    /* Memaksa kolom volume rata kanan dan berwarna emas */
    [data-testid="stDataFrame"] td:nth-child(6) { 
        text-align: right !important; 
        color: #fbbf24 !important; 
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (VERSION 32 - PRE-FORMATTED)
@st.cache_data(ttl=12)
def fetch_emperor_data():
    try:
        # Gunakan Binance (API paling jarang maintenance)
        ex = ccxt.binance({'timeout': 10000, 'enableRateLimit': True})
        tickers = ex.fetch_tickers()
        rows = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                if float(v['quoteVolume']) > 1000000: # Cuma koin yang volumenya di atas $1M
                    coin = sym.split('/')
                    p = float(v['last'])
                    c = float(v.get('percentage', 0) or 0)
                    vol_val = float(v['quoteVolume'])
                    
                    # FORMAT SULTAN: Kita rakit manual string-nya
                    # Contoh: $ 1,540,232
                    vol_sultan = f"$ {vol_val:,.0f}"
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                        "SYMBOL": coin,
                        "PRICE": p,
                        "CHANGE": c,
                        "VOL_RAW": vol_val,
                        "VOLUME 24H": vol_sultan,
                        "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                    })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("VOL_RAW", ascending=False).head(35)
            df["RANK"] = range(1, len(df) + 1)
            return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME 24H", "TREND"]]
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# 4. HEADER UI
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df = fetch_emperor_data()

if not df.empty:
    # 5. RENDER TABEL (KUNCI TIPE DATA)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME 24H": st.column_config.TextColumn("VOLUME 24H (SULTAN)", width=200), # Pakai TEXT agar format manual kita aman
            "TREND": st.column_config.LineChartColumn("TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    
    # FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Source: Binance Global | Refresh: 15s")
else:
    st.warning("⚠️ API sedang overload. Tunggu 10 detik atau refresh manual.")
