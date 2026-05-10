import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETUP
st.set_page_config(page_title="META INDO PRO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=15000, key="datarefresh")

# 2. CSS SULTAN (Kunci Format)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        font-weight: 900;
        font-size: 28px;
    }
    [data-testid="stDataFrame"] td { 
        vertical-align: middle !important; 
        font-family: 'ui-monospace', monospace !important;
        color: #f1f5f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DATA (AUTO-SWITCH EXCHANGE)
@st.cache_data(ttl=10)
def fetch_data_robust():
    # Coba KuCoin, kalau gagal pindah ke Binance
    exchanges = [ccxt.kucoin({'timeout': 10000}), ccxt.binance({'timeout': 10000})]
    
    for ex in exchanges:
        try:
            tickers = ex.fetch_tickers()
            rows = []
            for sym, v in tickers.items():
                if '/USDT' in sym and v.get('last') and v.get('quoteVolume'):
                    coin = sym.split('/')
                    p = float(v['last'])
                    c = float(v.get('percentage', 0) or 0)
                    
                    # FORMAT VOLUME SULTAN (String manipulation agar pasti muncul $)
                    vol_val = float(v['quoteVolume'])
                    vol_str = f"${vol_val:,.0f}"
                    
                    rows.append({
                        "RANK": 0,
                        "ICON": f"https://www.google.com/s2/favicons?domain=https://coinmarketcap.com/currencies/{coin.lower()}/&sz=32",
                        "SYMBOL": coin,
                        "PRICE": p,
                        "24H %": c,
                        "VOLUME": vol_str,
                        "TREND": [p * (1 + (c / 100) * (i / 5)) for i in range(6)]
                    })
            
            df = pd.DataFrame(rows)
            # Urutkan berdasarkan volume (tapi bersihkan dulu $ dan komanya buat sorting)
            df['sort_vol'] = df['VOLUME'].replace('[\$,]', '', regex=True).astype(float)
            df = df.sort_values("sort_vol", ascending=False).head(40).drop(columns=['sort_vol'])
            df["RANK"] = range(1, len(df) + 1)
            return df
        except:
            continue # Coba exchange berikutnya kalau exchange ini gagal/blokir
    return pd.DataFrame()

# 4. UI HEADER
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0f172a; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="glow-header">📊 META INDO PRO</h1>
            <p style="color: #64748b; margin: 0; font-size: 11px; font-family: monospace;">STABLE TERMINAL v8.0</p>
        </div>
        <div style="color: #10b981; font-weight: bold; font-family: monospace;">● LIVE FEED</div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_data_robust()

if not df.empty:
    # 5. RENDER TABEL
    st.dataframe(
        df,
        column_config={
            "RANK": st.column_config.NumberColumn("RANK", width=40),
            "ICON": st.column_config.ImageColumn(" ", width=40),
            "SYMBOL": st.column_config.TextColumn("COIN", width=80),
            "PRICE": st.column_config.NumberColumn("PRICE", format="$%.4f", width=120),
            "24H %": st.column_config.NumberColumn("CHANGE", format="%+.2f%%", width=100),
            "VOLUME": st.column_config.TextColumn("VOLUME 24H", width=200),
            "TREND": st.column_config.LineChartColumn("TREND", width=160)
        },
        use_container_width=True,
        hide_index=True,
        height=680
    )
    st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')} WIB | Exchange: Multi-Cloud Connect")
else:
    st.error("⚠️ Semua jalur API (KuCoin/Binance) sedang sibuk. Tunggu 15 detik atau refresh manual.")
