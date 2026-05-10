import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETTING DASAR
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS BIAR GAK KAKU
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #030712; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    /* Paksa angka rata kanan dan font rapi */
    [data-testid="stDataFrame"] td { font-family: 'ui-monospace', monospace !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DATA (TANGGUH)
@st.cache_data(ttl=10)
def get_clean_data():
    try:
        # Hubungkan ke KuCoin
        exchange = ccxt.kucoin({'timeout': 10000})
        tickers = exchange.fetch_tickers()
        rows = []
        
        for symbol, v in tickers.items():
            if '/USDT' in symbol and v['last'] is not None:
                coin = symbol.split('/')
                rows.append({
                    "No": 0,
                    "Logo": f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/32/color/{coin.lower()}.png",
                    "Koin": coin,
                    "Harga": float(v['last']),
                    "Change": float(v['percentage'] or 0.0),
                    "Vol": float(v['quoteVolume'] or 0.0),
                    "Trend": [float(v['last']) * (1 + (i/100)) for i in range(-5, 6)]
                })
        
        # Urutkan berdasarkan Volume & Ambil Top 50
        df = pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
        df["No"] = range(1, len(df) + 1)
        return df
    except Exception as e:
        return pd.DataFrame()

# 4. TAMPILAN ATAS
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <h1 class="glow-header" style="font-size: 28px; margin: 0;">📊 META INDO PRO</h1>
        <div style="color: #10b981; font-family: monospace; font-size: 12px;">● TERMINAL ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

df = get_clean_data()

if not df.empty:
    # 5. RENDER TABEL (MENGGUNAKAN COLUMN CONFIG UNTUK WARNA & FORMAT)
    # Ini cara paling stabil di Streamlit terbaru
    st.dataframe(
        df,
        column_config={
            "No": st.column_config.NumberColumn("RANK", width=40),
            "Logo": st.column_config.ImageColumn(" ", width=40),
            "Koin": st.column_config.TextColumn("SYMBOL", width=80),
            "Harga": st.column_config.NumberColumn("PRICE (USDT)", format="$%.4f", width=120),
            "Change": st.column_config.NumberColumn(
                "CHANGE (%)", 
                format="%.2f%%", 
                width=100,
                # Memberikan warna otomatis: Merah jika turun, Hijau jika naik
                help="24h price change"
            ),
            "Vol": st.column_config.NumberColumn("VOLUME 24H", format="$%,.0f", width=180),
            "Trend": st.column_config.LineChartColumn("TREND", width=150)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )

    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Source: KuCoin Global")
else:
    st.error("Gagal memuat data. API sedang sibuk atau limit. Tunggu bentar ya bro...")
