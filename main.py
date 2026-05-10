import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL LUXURY
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

# 3. DATA ENGINE (VERSION 14 - FAIL SAFE)
@st.cache_data(ttl=10)
def fetch_data_pro():
    try:
        ex = ccxt.kucoin({'timeout': 10000})
        tickers = ex.fetch_tickers()
        rows = []
        
        for sym, v in tickers.items():
            # Hanya ambil USDT, pastikan data lengkap (last price, percentage, volume)
            if '/USDT' in sym and all(v.get(k) is not None for k in ['last', 'percentage', 'quoteVolume']):
                coin = sym.split('/')
                
                # Setup Sparkline (7 titik data sederhana)
                p = float(v['last'])
                c = float(v['percentage'])
                trend = [p * (1 + (c / 100) * (i / 6)) for i in range(7)]
                
                # URL Logo (Gunakan CDN paling stabil)
                logo = f"https://coinicons-api.vercel.app/api/icon/{coin.lower()}"
                
                rows.append({
                    "RANK": 0,
                    "ICON": logo,
                    "COIN": coin,
                    "PRICE": p,
                    "CHANGE": c,
                    "VOLUME": float(v['quoteVolume']),
                    "TREND": trend
                })
        
        if not rows: return pd.DataFrame()
        
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
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">REAL-TIME MARKET TERMINAL</p>
        </div>
        <div style="text-align: right; color: #10b981; font-weight: bold; font-family: monospace; font-size: 12px;">● CONNECTED</div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_data_pro()

if not df.empty:
    # 5. RENDER TABEL (ULTRA STABLE CONFIG)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=45),
            "ICON": st.column_config.ImageColumn(" ", width=45),
            "COIN": st.column_config.TextColumn("SYMBOL", width=90),
            "PRICE": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.NumberColumn("VOLUME 24H", format="$%,.0f", width=180),
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    
    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Auto-refresh 15s")
else:
    st.info("🔄 Sedang menyambungkan ke API... Cek koneksi atau refresh browser jika blank.")
