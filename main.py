import streamlit as st
import pandas as pd
import ccxt
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG DASHBOARD ---
st.set_page_config(
    page_title="Crypto Neon Dashboard",
    page_icon="⚡",
    layout="wide",
)

# --- CUSTOM CSS (STYLE NEON) ---
st.markdown("""
    <style>
    /* Mengubah background utama */
    .stApp {
        background-color: #0e1117;
    }
    /* Style untuk card metric */
    [data-testid="stMetricValue"] {
        color: #deff9a !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    /* Container styling */
    div.element-container {
        color: #f5f5f5;
    }
    /* Neon border untuk tabel */
    .stDataFrame {
        border: 1px solid #deff9a;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚡ Settings 2.0")
    st.markdown("---")
    exchange_choice = st.selectbox("Pilih Exchange:", ["KuCoin", "Binance"])
    auto_refresh = st.toggle("Auto-refresh (30s)", value=True)
    st.markdown("---")
    st.info("Tips: Gunakan KuCoin jika Binance sedang memblokir IP Cloud.")

# --- FUNGSI AMBIL DATA ---
def fetch_crypto_data(ex_name):
    try:
        if ex_name == "KuCoin":
            exchange = ccxt.kucoin({'enableRateLimit': True})
        else:
            exchange = ccxt.binance({'enableRateLimit': True})
            
        tickers = exchange.fetch_tickers()
        
        rows = []
        for symbol, t in tickers.items():
            # Filter hanya pair USDT
            if '/USDT' in symbol:
                rows.append({
                    "Koin": symbol.split('/')[0],
                    "Harga": t['last'],
                    "Change": t['percentage'],
                    "High": t['high'],
                    "Low": t['low'],
                    "Volume": t['quoteVolume']
                })
        return rows
    except Exception as e:
        st.error(f"Error fetching from {ex_name}: {e}")
        return []

# --- HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("📈 CRYPTO NEON DASHBOARD")
    st.caption(f"Data Source: {exchange_choice} API | Real-time Analysis")
with col_h2:
    st.button("🔄 Force Refresh")

# --- DATA PROCESSING ---
with st.spinner("Menarik data dari blockchain..."):
    data = fetch_crypto_data(exchange_choice)

if data:
    df = pd.DataFrame(data)
    df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

    # --- TOP 3 METRICS ---
    top_symbols = ["BTC", "ETH", "SOL"]
    m_cols = st.columns(3)
    
    for i, sym in enumerate(top_symbols):
        row = df[df['Koin'] == sym]
        if not row.empty:
            price = row.iloc[0]['Harga']
            change = row.iloc[0]['Change']
            m_cols[i].metric(label=f"{sym}/USDT", value=f"${price:,.2f}", delta=f"{change:+.2f}%")

    st.markdown("---")

    # --- MAIN CONTENT: CHART & TABLE ---
    col_table, col_chart = st.columns([2, 1])

    with col_table:
        st.subheader("📊 Market Overview")
        search = st.text_input("🔍 Cari Koin (Contoh: XRP, DOGE)", "").upper()
        
        if search:
            df_display = df[df['Koin'].str.contains(search)]
        else:
            df_display = df.head(50) # Tampilkan 50 teratas saja biar cepat

        # Styling Tabel
        def color_change(val):
            color = '#deff9a' if val >= 0 else '#ff4b4b'
            return f'color: {color}; font-weight: bold'

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
        st.subheader("🔥 Top Volume (Visual)")
        # Simple Plotly Bar Chart
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
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')} | Total Pairs: {len(df)}")

if len(data) > 0: # Cek apakah datanya beneran ada isinya
    df = pd.DataFrame(data)
else:
st.warning("Menunggu data dari Exchange... Pastikan koneksi internet stabil.")

# --- AUTO REFRESH ---
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
