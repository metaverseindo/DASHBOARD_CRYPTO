import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP (Kunci Layout)
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (ULTRA DARK & TIGHT)
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
    /* Memaksa font monospace agar angka sejajar dan rapi */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (VERSION 31 - LIGHTWEIGHT)
@st.cache_data(ttl=12)
def fetch_robust_data():
    try:
        # Pake Binance sebagai sumber utama (paling stabil buat server cloud)
        ex = ccxt.binance({'timeout': 10000, 'enableRateLimit': True})
        tickers = ex.fetch_tickers()
        rows = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                # Hanya koin dengan volume di atas $500k (Biar enteng & berkualitas)
                if float(v['quoteVolume']) > 500000:
                    coin = sym.split('/')
                    p = float(v['last'])
                    c = float(v.get('percentage', 0) or 0)
                    
                    # FORMAT VOLUME SULTAN (String manipulation)
                    vol_val = float(v['quoteVolume'])
                    vol_str = f"${vol_val:,.0f}"
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                        "SYMBOL": coin,
                        "PRICE": p,
                        "CHANGE": c,
                        "VOL_RAW": vol_val, # Buat sorting
                        "VOLUME": vol_str,  # Buat tampilan
                        "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                    })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            # Sorting berdasarkan volume asli, ambil Top 30 saja
            df = df.sort_values("VOL_RAW", ascending=False).head(30)
            df["RANK"] = range(1, len(df) + 1)
            return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME", "TREND"]]
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# 4. HEADER UI
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df = fetch_robust_data()

if not df.empty:
    # 5. RENDER TABEL (KUNCI FORMAT & LEBAR)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.TextColumn("VOLUME 24H", width=200), # Rata kanan & ada $ otomatis
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=650
    )
    
    # FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Meta Indo Stable v31.0")
else:
    st.info("🔄 Sedang narik data market... Tunggu 5 detik. Jika blank, cek requirements.txt lu.")
