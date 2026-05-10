import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & AUTO REFRESH
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=20000, key="datarefresh") # Interval agak dilonggarin ke 20s biar gak gampang limit

# 2. CSS SULTAN STYLE
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
        font-weight: 900; text-align: center; padding: 15px; font-size: 30px;
    }
    [data-testid="stDataFrame"] td:nth-child(6) { 
        text-align: right !important; color: #fbbf24 !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE V34 (INFINITY CACHE)
@st.cache_data(ttl=60, show_spinner=False) # Simpan data 60 detik buat jaga-jaga kalau limit
def fetch_infinity_data():
    # Daftar exchange cadangan
    exchange_list = [
        ('Binance', ccxt.binance({'timeout': 5000, 'enableRateLimit': True})),
        ('KuCoin', ccxt.kucoin({'timeout': 5000, 'enableRateLimit': True})),
        ('Gate.io', ccxt.gateio({'timeout': 5000, 'enableRateLimit': True}))
    ]
    
    for name, ex in exchange_list:
        try:
            tickers = ex.fetch_tickers()
            rows = []
            for sym, v in tickers.items():
                if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                    # Hanya ambil koin raksasa (Volume > 2M) biar stabil
                    if float(v['quoteVolume']) > 2000000:
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
                            "VOLUME 24H": f"$ {vol_val:,.0f}",
                            "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                        })
            
            if rows:
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(25)
                df["RANK"] = range(1, len(df) + 1)
                return df[["RANK", "ICON", "SYMBOL", "PRICE", "CHANGE", "VOLUME 24H", "TREND"]], name
        except:
            continue
    return pd.DataFrame(), None

# 4. UI RENDER
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

df, source = fetch_infinity_data()

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
        use_container_width=True, hide_index=True, height=600
    )
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"✅ Data Active ({source}) | Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB")
else:
    # Jika bener-bener mentok, tampilin pesan yang lebih "Sultan"
    st.warning("🔄 Terminal sedang melakukan sinkronisasi ulang dengan satelit bursa... Mohon tunggu sebentar.")
    st.info("Tips: Jika layar ini tidak berubah dalam 30 detik, silakan klik 'R' di keyboard atau refresh browser.")
