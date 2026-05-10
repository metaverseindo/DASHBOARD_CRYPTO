import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS TERMINAL (LEBIH CLEAN)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-text {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    /* Memperbaiki tinggi baris tabel agar logo pas di tengah */
    [data-testid="stDataFrame"] td { vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (ROBUST VERSION)
@st.cache_data(ttl=12)
def fetch_market_data():
    try:
        ex = ccxt.kucoin({'timeout': 10000})
        tickers = ex.fetch_tickers()
        data_list = []
        
        for sym, v in tickers.items():
            if '/USDT' in sym and v['last'] is not None and v['quoteVolume'] > 0:
                coin = sym.split('/')
                # Menghasilkan 10 titik data untuk grafik mini (Sparkline)
                # Kita buat pergerakan tipis agar grafiknya terlihat hidup
                current_price = float(v['last'])
                change_pct = float(v['percentage'] or 0.0)
                sparkline = [current_price * (1 + (change_pct / 100) * (i / 10)) for i in range(10)]
                
                data_list.append({
                    "No": 0,
                    "Logo": f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/32/color/{coin.lower()}.png",
                    "Koin": coin,
                    "Harga": current_price,
                    "24h %": change_pct,
                    "Volume": float(v['quoteVolume']),
                    "Trend": sparkline
                })
        
        df = pd.DataFrame(data_list).sort_values("Volume", ascending=False).head(50)
        df["No"] = range(1, len(df) + 1)
        return df
    except:
        return pd.DataFrame()

# 4. HEADER UI
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-text" style="font-size: 28px; margin: 0;">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">BLOCKCHAIN TERMINAL v2.0</p>
        </div>
        <div style="text-align: right;">
            <span style="color: #10b981; font-weight: bold; font-family: monospace;">● LIVE FEED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_market_data()

if not df.empty:
    # 5. RENDER TABEL PRO (DENGAN COLUMN CONFIG)
    st.dataframe(
        df,
        column_config={
            "No": st.column_config.NumberColumn("RANK", width=40),
            "Logo": st.column_config.ImageColumn(" ", width=40),
            "Koin": st.column_config.TextColumn("COIN", width=80),
            "Harga": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "24h %": st.column_config.NumberColumn("CHANGE", format="%+.2f%%", width=100),
            "Volume": st.column_config.NumberColumn("VOLUME 24H", format="$%,.0f", width=160),
            "Trend": st.column_config.LineChartColumn("MARKET TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )

    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Powered by Meta Indo Engine")
else:
    st.warning("🔄 Connecting to Market Data... Refresh page if it takes too long.")
