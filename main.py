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

# --- 2. CUSTOM CSS (STYLE NEON CYBERPUNK) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    [data-testid="stMetricValue"] {
        color: #deff9a !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    div.element-container {
        color: #f5f5f5;
    }
    .stDataFrame {
        border: 1px solid #deff9a;
        border-radius: 10px;
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR SETTINGS ---
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
                    "High": t['high'],
                    "Low": t['low'],
                    "Volume": t['quoteVolume']
                })
        return rows
    except Exception as e:
        st.error(f"Error fetching from {ex_name}: {e}")
        return []

# --- 5. HEADER DASHBOARD ---
# Ganti ini:
col_h1, col_h2 = st.columns() # Angka artinya kolom kiri lebih lebar dari kolom kanan
# Menjadi ini (Isi angka 2 untuk dua kolom):
col_h1, col_h2 = st.columns()

# ATAU kalau mau kolom kiri lebih lebar (seperti kode gue sebelumnya):
col_h1, col_h2 = st.columns()

with col_h1:
    st.title("📈 CRYPTO NEON DASHBOARD")
    st.caption(f"Data Source: {exchange_choice} API | Real-time Analysis")
with col_h2:
    if st.button("🔄 Refresh Sekarang"):
        st.rerun()

# --- 6. MAIN ENGINE (DATA PROCESSING) ---
with st.spinner("🚀 Sinkronisasi dengan Blockchain..."):
    data = fetch_crypto_data(exchange_choice)

# Cek apakah data tersedia
if len(data) > 0:
    df = pd.DataFrame(data)
    df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

    # --- TOP 3 METRICS ---
    top_symbols = ["BTC", "ETH", "SOL"]
    m_cols = st.columns(3)
    
    for i, sym in enumerate(top_symbols):
        row = df[df['Koin'] == sym]
        if not row.empty:
            price = row.iloc['Harga']
            change = row.iloc['Change']
            m_cols[i].metric(
                label=f"{sym}/USDT", 
                value=f"${price:,.2f}", 
                delta=f"{change:+.2f}%"
            )
        else:
            m_cols[i].metric(label=sym, value="N/A")

    st.markdown("---")

    # --- LAYOUT: TABLE & CHART ---
    col_table, col_chart = st.columns()

    with col_table:
        st.subheader("📊 Market Overview")
        search = st.text_input("🔍 Cari Koin...", "").upper()
        
        if search:
            df_display = df[df['Koin'].str.contains(search)]
        else:
            df_display = df.head(50)

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
            height=500,
            hide_index=True
        )

    with col_chart:
        st.subheader("🔥 Top 10 Volume")
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
            height=500,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.caption(f"🕒 Terakhir diperbarui: {datetime.now().strftime('%H:%M:%S')} | Total koin aktif: {len(df)}")

else:
    # --- BARIS DI BAWAH INI HARUS MENJOROK (Indentasi) ---
    st.warning("⚠️ Menunggu data dari Exchange... Pastikan koneksi stabil.")
    st.info("Jika error berlanjut, coba ganti Exchange ke KuCoin melalui Sidebar.")

# --- 7. AUTO REFRESH ---
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
