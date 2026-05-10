import streamlit as st
import pandas as pd
import ccxt
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(
    page_title="Crypto Neon Dashboard",
    page_icon="⚡",
    layout="wide",
)

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #deff9a !important; font-family: 'Courier New', monospace; font-weight: bold; }
    div.element-container { color: #f5f5f5; }
    .stDataFrame { border: 1px solid #deff9a; border-radius: 10px; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚡ Settings 2.0")
    st.markdown("---")
    exchange_choice = st.selectbox("Pilih Exchange:", ["KuCoin", "Binance"])
    auto_refresh = st.toggle("Auto-refresh (30s)", value=True)
    st.markdown("---")
    st.info("Tips: Gunakan KuCoin jika Binance sedang memblokir IP server.")

# --- 4. FUNGSI AMBIL DATA ---
def fetch_crypto_data(ex_name):
    try:
        if ex_name == "KuCoin":
            exchange = ccxt.kucoin({'enableRateLimit': True})
        else:
            exchange = ccxt.binance({'enableRateLimit': True})
        tickers = exchange.fetch_tickers()
        rows = []
        for symbol, t in tickers.items():
            if '/USDT' in symbol:
                rows.append({
                    "Koin": symbol.split('/'),
                    "Harga": t['last'],
                    "Change": t['percentage'] if t['percentage'] is not None else 0.0,
                    "Volume": t['quoteVolume']
                })
        return rows
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# --- 5. HEADER (FIXED: Dikasih angka 2) ---
col_h1, col_h2 = st.columns(2) 
with col_h1:
    st.title("📈 CRYPTO NEON")
    st.caption(f"Source: {exchange_choice} | Python 3.14 Stable")
with col_h2:
    if st.button("🔄 Force Refresh"):
        st.rerun()

# --- 6. MAIN ENGINE ---
with st.spinner("🚀 Syncing..."):
    data = fetch_crypto_data(exchange_choice)

if len(data) > 0:
    df = pd.DataFrame(data)
    df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

    # --- TOP METRICS (FIXED: Dikasih angka 3) ---
    m_cols = st.columns(3)
    for i, sym in enumerate(["BTC", "ETH", "SOL"]):
        row = df[df['Koin'] == sym]
        if not row.empty:
            m_cols[i].metric(
                label=f"{sym}/USDT", 
                value=f"${row.iloc['Harga']:,.2f}", 
                delta=f"{row.iloc['Change']:+.2f}%"
            )

    st.markdown("---")

    # --- TABLE & CHART (FIXED: Baris 87 lu sekarang ada isinya!) ---
    col_table, col_chart = st.columns()
    
    with col_table:
        st.subheader("📊 Market Overview")
        search = st.text_input("🔍 Search Coin...", "").upper()
        df_display = df[df['Koin'].str.contains(search)] if search else df.head(50)
        
        def color_change(val):
            return f"color: {'#deff9a' if val >= 0 else '#ff4b4b'}; font-weight: bold"

        st.dataframe(
            df_display.style.format({
                "Harga": "${:,.4f}", 
                "Change": "{:+.2f}%", 
                "Volume": "${:,.0f}"
            }).map(color_change, subset=["Change"]),
            use_container_width=True, 
            height=450, 
            hide_index=True
        )

    with col_chart:
        st.subheader("🔥 Top 10 Vol")
        top_10 = df.head(10)
        fig = go.Figure(go.Bar(
            x=top_10['Volume'], 
            y=top_10['Koin'], 
            orientation='h', 
            marker=dict(color='#deff9a')
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='white', 
            height=450, 
            margin=dict(l=0, r=0, t=20, b=0), 
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")

else:
    st.warning("⚠️ Gagal narik data. Coba ganti exchange di sidebar.")

# --- 7. AUTO REFRESH ---
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
