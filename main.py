import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP (Kunci Layout)
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (CUSTOM TABLE & FONT)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    /* Memaksa font monospace dan warna teks agar rapi */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        color: #f1f5f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (VERSION 19 - ULTRA STABLE)
@st.cache_data(ttl=12)
def fetch_final_data():
    try:
        # Gunakan KuCoin API dengan timeout 12 detik
        ex = ccxt.kucoin({'timeout': 12000})
        tickers = ex.fetch_tickers()
        rows = []
        
        for sym, v in tickers.items():
            try:
                # Hanya ambil pasangan USDT dengan data yang valid
                if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                    coin = sym.split('/')
                    
                    # Sparkline super ringan (5 titik data)
                    p = float(v['last'])
                    c = float(v.get('percentage', 0) or 0)
                    # Pastikan data trend murni float
                    trend = [float(p * (1 + (c / 100) * (i / 4))) for i in range(5)]
                    
                    # Logo via Google Proxy (Jauh lebih stabil dibanding CDN lain)
                    logo = f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32"
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": logo,
                        "SYMBOL": coin,
                        "PRICE": p,
                        "CHANGE": c,
                        "VOLUME": float(v['quoteVolume']),
                        "TREND": trend
                    })
            except:
                continue
        
        if not rows: return pd.DataFrame()
        
        # Ambil Top 40 biar gak berat pas proses render di browser
        df = pd.DataFrame(rows).sort_values("VOLUME", ascending=False).head(40)
        df["RANK"] = range(1, len(df) + 1)
        return df
    except:
        return pd.DataFrame()

# 4. UI HEADER
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-header" style="font-size: 28px; margin: 0;">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">BLOCKCHAIN TERMINAL v4.5</p>
        </div>
        <div style="color: #10b981; font-family: monospace; font-size: 12px; font-weight: bold;">● LIVE FEED</div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_final_data()

if not df.empty:
    # 5. RENDER TABEL (KUNCI FORMAT SULTAN)
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("SYMBOL", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "CHANGE": st.column_config.NumberColumn("CHANGE", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.NumberColumn("VOLUME 24H", format="$%,.0f", width=180),
            "TREND": st.column_config.LineChartColumn("MARKET TREND", width=150)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    
    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Source: KuCoin | Refresh: 15s")
else:
    st.warning("🔄 Connecting to API... Jika blank, silakan refresh browser lu sekali lagi.")
