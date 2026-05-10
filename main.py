import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS CUSTOM (DARK MODE TERMINAL)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #030712; }
    
    /* Style Table */
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Header Animation */
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        font-weight: 900;
        letter-spacing: -1px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (AMBIL LOGO & SPARKLINE)
@st.cache_data(ttl=14)
def get_pro_data():
    try:
        ex = ccxt.kucoin()
        tickers = ex.fetch_tickers()
        rows = []
        for symbol, v in tickers.items():
            if '/USDT' in symbol:
                coin_name = symbol.split('/')
                # Link Logo (Pake CDN koin yang stabil)
                logo_url = f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{coin_name.lower()}.png"
                
                rows.append({
                    "Koin": coin_name,
                    "Logo": logo_url,
                    "Harga": v['last'],
                    "Change": v['percentage'] or 0.0,
                    "Vol": v['quoteVolume'],
                    # Simulasi data grafik (Streamlit butuh list angka buat Sparkline)
                    "Trend": [v['last'] * (1 + (v['percentage'] or 0)/100 * (i/10)) for i in range(10)]
                })
        
        df_res = pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
        df_res.insert(0, "No", range(1, len(df_res) + 1))
        return df_res
    except: return pd.DataFrame()

# 4. UI LAYOUT
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #111827; border-radius: 15px; border: 1px solid #1f2937; margin-bottom: 25px;">
        <div>
            <h1 class="glow-header" style="font-size: 35px; margin: 0;">📊 META INDO <span style="color:white">PRO</span></h1>
            <p style="color: #9ca3af; margin: 0; font-size: 12px; font-family: monospace;">INSTANT ORDERBOOK & MARKET ANALYSIS</p>
        </div>
        <div style="text-align: right;">
            <div style="color: #10b981; font-weight: bold; font-family: monospace;">● LIVE SERVER</div>
            <div style="color: #4b5563; font-size: 10px;">DATA SOURCE: KUCOIN GLOBAL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = get_pro_data()

if not df.empty:
    # 5. MAIN PRO TABLE
    st.dataframe(
        df,
        column_config={
            "No": st.column_config.NumberColumn("RANK", width=50),
            "Logo": st.column_config.ImageColumn("ICON", width=50),
            "Koin": st.column_config.TextColumn("SYMBOL", width=80),
            "Harga": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=120),
            "Change": st.column_config.NumberColumn("24H %", format="%.2f%%", width=100),
            "Vol": st.column_config.NumberColumn("VOLUME", format="$%d", width=150),
            "Trend": st.column_config.LineChartColumn(
                "MARKET TREND (24H)",
                width=200,
                y_min=df["Harga"].min(),
                y_max=df["Harga"].max()
            )
        },
        use_container_width=True,
        hide_index=True,
        height=700
    )

    # 6. FOOTER WIB
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz).strftime("%H:%M:%S")
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-top: 15px; color: #4b5563; font-size: 12px; font-family: monospace;">
            <span>SYSTEM TIME: {now} WIB</span>
            <span>REFRESH RATE: 15S</span>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Menghubungkan ke API... Pastikan koneksi internet stabil.")
