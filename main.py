import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (DARK MODE LUXURY)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-text {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    /* Memastikan tabel rapi & angka monospace agar titik sejajar */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (ROBUST & FAST)
@st.cache_data(ttl=12)
def fetch_market_data():
    try:
        # Pake KuCoin dengan timeout 15 detik
        ex = ccxt.kucoin({'timeout': 15000})
        tickers = ex.fetch_tickers()
        data_list = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v['last'] is not None and v['quoteVolume'] > 0:
                coin = sym.split('/')
                
                # Setup Sparkline (Trend) - 7 titik data biar enteng
                p = float(v['last'])
                c = float(v['percentage'] or 0.0)
                sparkline = [p * (1 + (c / 100) * (i / 6)) for i in range(7)]
                
                data_list.append({
                    "RANK": 0,
                    "ICON": f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/32/color/{coin.lower()}.png",
                    "COIN": coin,
                    "PRICE": p,
                    "24H %": c,
                    "VOLUME": float(v['quoteVolume']),
                    "TREND": sparkline
                })
        
        # Sort by Volume terbesar
        df = pd.DataFrame(data_list).sort_values("VOLUME", ascending=False).head(50)
        df["RANK"] = range(1, len(df) + 1)
        return df
    except:
        return pd.DataFrame()

# 4. HEADER UI
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-text" style="font-size: 30px; margin: 0;">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">REAL-TIME MARKET ANALYSIS</p>
        </div>
        <div style="text-align: right; color: #10b981; font-weight: bold; font-family: monospace; font-size: 12px;">
            ● TERMINAL ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_market_data()

if not df.empty:
    # 5. RENDER TABEL (Pake Column Config Biar Rapi)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "COIN": st.column_config.TextColumn("SYMBOL", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=120),
            "24H %": st.column_config.NumberColumn("CHANGE", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.NumberColumn("24H VOL", format="$%,.0f", width=160),
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=720
    )

    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Updated: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Auto-refresh active")
else:
    st.info("🔄 Connecting to market data... Silakan refresh halaman jika data tidak muncul.")
