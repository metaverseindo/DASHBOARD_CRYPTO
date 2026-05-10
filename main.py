import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & REFRESH (15 detik)
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (SULTAN STYLE)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
        font-weight: 900;
        text-align: center;
        padding: 15px;
        font-size: 30px;
    }
    [data-testid="stDataFrame"] td:nth-child(6) { 
        text-align: right !important; 
        color: #fbbf24 !important; 
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ROBUST DATA ENGINE (ROTASI EXCHANGE)
@st.cache_data(ttl=12)
def fetch_robust_data():
    # Daftar exchange buat rotasi kalau satu overload
    exchanges = [
        ccxt.binance({'timeout': 7000, 'enableRateLimit': True}),
        ccxt.kucoin({'timeout': 7000, 'enableRateLimit': True}),
        ccxt.gateio({'timeout': 7000, 'enableRateLimit': True})
    ]
    
    for ex in exchanges:
        try:
            tickers = ex.fetch_tickers()
            rows = []
            for sym, v in tickers.items():
                if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                    # Filter koin dengan volume di atas $1M biar gak berat
                    if float(v['quoteVolume']) > 1000000:
                        coin = sym.split('/')
                        p = float(v['last'])
                        c = float(v.get('percentage', 0) or 0)
                        vol_val = float(v['quoteVolume'])
                        
                        rows.append({
                            "RANK": 0,
                            "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                            "SYMBOL": coin,
                            "PRICE": p,
                            "CHANGE": c,
                            "VOL_RAW": vol_val,
                            "VOLUME 24H": f"$ {vol_val:,.0f}", # Format Sultan
                            "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                        })
            
            df = pd.DataFrame(rows)
            if not df.empty:
                df = df.sort_values("VOL_RAW", ascending=False).head(35)
                df["RANK"] = range(1, len(df) + 1)
                return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME 24H", "TREND"]]
        except:
            continue # Kalau satu error/overload, coba exchange berikutnya
    return pd.DataFrame()

# 4. HEADER UI
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df = fetch_robust_data()

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
            "VOLUME 24H": st.column_config.TextColumn("VOLUME 24H", width=200),
            "TREND": st.column_config.LineChartColumn("TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')} WIB | Meta Indo Pro v33.0")
else:
    st.error("⚠️ Semua API (Binance/KuCoin/Gate) sedang Limit. Refresh browser dalam 10 detik.")
