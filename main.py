import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (ULTRA CLEAN)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-text {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    /* Rapiin tabel agar icon dan chart pas di tengah baris */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        color: #f1f5f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (VERSION 10 - THE TANK)
@st.cache_data(ttl=12)
def fetch_pro_data():
    try:
        # Hubungkan ke KuCoin
        ex = ccxt.kucoin({'timeout': 15000})
        tickers = ex.fetch_tickers()
        data_list = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v['last'] is not None and v['quoteVolume'] > 0:
                coin = sym.split('/')
                
                # Setup Sparkline yang super enteng (6 titik data)
                p = float(v['last'])
                c = float(v['percentage'] or 0.0)
                # Bikin list angka murni untuk trend
                sparkline = [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                
                data_list.append({
                    "RANK": 0,
                    "ICON": f"https://coinicons-api.vercel.app/api/icon/{coin.lower()}",
                    "SYMBOL": coin,
                    "PRICE": p,
                    "CHANGE": c,
                    "VOLUME": float(v['quoteVolume']),
                    "TREND": sparkline
                })
        
        # Sort & Ambil Top 50
        df = pd.DataFrame(data_list).sort_values("VOLUME", ascending=False).head(50)
        df["RANK"] = range(1, len(df) + 1)
        return df
    except:
        return pd.DataFrame()

# 4. HEADER
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-text" style="font-size: 28px; margin: 0;">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">REAL-TIME MARKET INTELLIGENCE</p>
        </div>
        <div style="text-align: right; color: #10b981; font-weight: bold; font-family: monospace; font-size: 12px;">
            ● TERMINAL ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_pro_data()

if not df.empty:
    # 5. RENDER TABEL (CONFIG PALING STABIL)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.NumberColumn("24H VOLUME", format="$%,.0f", width=180),
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=150)
        },
        use_container_width=True,
        hide_index=True,
        height=700
    )

    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Auto-refresh active")
else:
    st.info("🔄 Connecting to server... Jika data tidak muncul dalam 10 detik, silakan refresh halaman.")
