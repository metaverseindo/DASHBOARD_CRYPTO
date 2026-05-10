import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG & REFRESH (15 detik biar stabil)
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS SULTAN (TERMINAL STYLE)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #030712; }
    
    /* Bikin angka sejajar & font rapi */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', 'Cascadia Code', monospace !important;
    }
    
    /* Animasi Glow Header */
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    
    .stAlert { background-color: #111827; border: 1px solid #1f2937; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# 3. PRO DATA ENGINE
@st.cache_data(ttl=14)
def get_meta_pro_data():
    try:
        ex = ccxt.kucoin()
        tickers = ex.fetch_tickers()
        rows = []
        for symbol, v in tickers.items():
            if '/USDT' in symbol:
                coin = symbol.split('/')
                # Filter koin-koin sampah, ambil yang volumenya masuk akal aja
                if v['quoteVolume'] > 0:
                    rows.append({
                        "Koin": coin,
                        "Logo": f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{coin.lower()}.png",
                        "Harga": v['last'],
                        "Change": v['percentage'] or 0.0,
                        "Vol": v['quoteVolume'],
                        # Simulasi trend 24 jam (pake data dummy yang proporsional dengan harga)
                        "Trend": [v['last'] * (1 + (v['percentage'] or 0)/200 * i) for i in range(-5, 6)]
                    })
        
        df = pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
        df.insert(0, "No", range(1, len(df) + 1))
        return df
    except: return pd.DataFrame()

# 4. HEADER LAYOUT
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 25px; background: #0f172a; border-radius: 20px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-header" style="font-size: 38px; margin: 0;">📊 META INDO <span style="color:white">PRO</span></h1>
            <p style="color: #64748b; margin: 0; font-size: 13px; font-family: monospace; letter-spacing: 2px;">REAL-TIME MARKET INTELLIGENCE</p>
        </div>
        <div style="text-align: right;">
            <div style="color: #10b981; font-weight: bold; font-family: monospace; display: flex; align-items: center; gap: 8px;">
                <span style="height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #10b981;"></span>
                LIVE SERVER
            </div>
            <div style="color: #475569; font-size: 11px; margin-top: 5px;">SOURCE: KUCOIN GLOBAL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = get_meta_pro_data()

if not df.empty:
    # 5. ULTIMATE DATAFRAME CONFIG
    st.dataframe(
        df,
        column_config={
            "No": st.column_config.NumberColumn("RANK", width=40),
            "Logo": st.column_config.ImageColumn("ICON", width=50),
            "Koin": st.column_config.TextColumn("SYMBOL", width=90),
            "Harga": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=140),
            "Change": st.column_config.NumberColumn("24H %", format="%.2f%%", width=100),
            "Vol": st.column_config.NumberColumn("24H VOLUME", format="$%d", width=180),
            "Trend": st.column_config.LineChartColumn(
                "TREND (24H)", 
                width=180,
                y_min=df["Harga"].min(),
                y_max=df["Harga"].max()
            )
        },
        use_container_width=True,
        hide_index=True,
        height=750
    )

    # 6. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; padding: 10px; color: #475569; font-size: 12px; font-family: monospace;">
            <span>SINKRONISASI: {datetime.now(tz).strftime('%H:%M:%S')} WIB</span>
            <span>META INDO v2.0.1 - PRO LICENSE</span>
        </div>
    """, unsafe_allow_html=True)

else:
    st.info("🔄 Sedang memuat data dan logo koin... Mohon tunggu.")
