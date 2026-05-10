import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS (Mencegah Melar & Rata Kanan)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        color: #f1f5f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE
@st.cache_data(ttl=10)
def fetch_data():
    try:
        ex = ccxt.kucoin({'timeout': 10000})
        tickers = ex.fetch_tickers()
        rows = []
        for sym, v in tickers.items():
            if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                coin = sym.split('/')
                p = float(v['last'])
                c = float(v.get('percentage', 0) or 0)
                # Trend data
                trend = [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                # Stable Logo
                logo = f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32"
                
                rows.append({
                    "RANK": 0,
                    "ICON": logo,
                    "COIN": coin,
                    "PRICE": p,
                    "CHANGE": c,
                    "VOLUME": float(v['quoteVolume']),
                    "TREND": trend
                })
        df = pd.DataFrame(rows).sort_values("VOLUME", ascending=False).head(40)
        df["RANK"] = range(1, len(df) + 1)
        return df
    except:
        return pd.DataFrame()

# 4. UI HEADER
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-header" style="font-size: 28px; margin: 0;">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">BLOCKCHAIN TERMINAL v6.0</p>
        </div>
        <div style="color: #10b981; font-weight: bold; font-family: monospace; font-size: 12px;">● LIVE</div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_data()

if not df.empty:
    # 5. RENDER TABEL (Urutan & Format Sultan)
    st.dataframe(
        df,
        column_order=("RANK", "ICON", "COIN", "PRICE", "CHANGE", "VOLUME", "TREND"),
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "COIN": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.NumberColumn("VOLUME 24H", format="$%,.0f", width=200),
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    
    # FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Auto-refresh Active")
else:
    st.warning("🔄 Sedang menyambungkan ke API... Refresh browser jika blank.")
