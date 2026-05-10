import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG & REFRESH
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS CUSTOM (FIXED LAYOUT)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #030712; }
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
    }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE (WITH ERROR HANDLING)
@st.cache_data(ttl=10)
def get_meta_data():
    try:
        # Pake exchange yang paling stabil
        ex = ccxt.kucoin({'timeout': 10000})
        tickers = ex.fetch_tickers()
        rows = []
        
        for symbol, v in tickers.items():
            if '/USDT' in symbol and v['last'] is not None:
                coin = symbol.split('/')
                # Filter koin dengan volume yang valid
                if v['quoteVolume'] and v['quoteVolume'] > 0:
                    rows.append({
                        "No": 0, # Placeholder
                        "Icon": f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{coin.lower()}.png",
                        "Koin": coin,
                        "Harga": float(v['last']),
                        "Change": float(v['percentage'] or 0.0),
                        "Vol": float(v['quoteVolume']),
                        "Trend": [float(v['last']) * (1 + (i/100)) for i in range(-5, 5)] # Sparkline data
                    })
        
        df = pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
        df["No"] = range(1, len(df) + 1)
        return df
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        return pd.DataFrame()

# 4. HEADER
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-header" style="font-size: 30px; margin: 0;">📊 META INDO <span style="color:white">PRO</span></h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">REAL-TIME TERMINAL</p>
        </div>
        <div style="text-align: right; color: #10b981; font-weight: bold; font-family: monospace; font-size: 12px;">
            ● LIVE FEED
        </div>
    </div>
    """, unsafe_allow_html=True)

df = get_meta_data()

if not df.empty:
    # 5. ULTIMATE DATAFRAME RENDERER
    # Kita pisahkan antara data display dan data styling agar tidak berat
    st.dataframe(
        df,
        column_config={
            "No": st.column_config.NumberColumn("RANK", width=40),
            "Icon": st.column_config.ImageColumn(" ", width=40),
            "Koin": st.column_config.TextColumn("SYMBOL", width=80),
            "Harga": st.column_config.NumberColumn("PRICE ($)", format="$%.4f", width=120),
            "Change": st.column_config.NumberColumn("24H %", format="%+.2f%%", width=100),
            "Vol": st.column_config.NumberColumn("VOLUME", format="$%,.0f", width=160),
            "Trend": st.column_config.LineChartColumn("TREND", width=150)
        },
        use_container_width=True,
        hide_index=True,
        height=650
    )

    # 6. FOOTER WIB
    tz = pytz.timezone('Asia/Jakarta')
    st.markdown(f"""<p style="color: #475569; font-size: 11px; font-family: monospace;">
        LAST SYNC: {datetime.now(tz).strftime('%H:%M:%S')} WIB | AUTO-REFRESH ACTIVE</p>""", 
        unsafe_allow_html=True)
else:
    st.info("🔄 Sedang menyambungkan ke API KuCoin... Silakan refresh halaman jika lama.")
