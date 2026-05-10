import streamlit as st
import pandas as pd
import ccxt

# 1. KONFIGURASI (Cukup satu kali di paling atas)
st.set_page_config(
    page_title="Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS buat ngilangin header GitHub, Edit, dan Footer Streamlit
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. FUNGSI AMBIL DATA
def get_crypto_data():
    try:
        # Pake Kucoin karena lebih friendly buat server cloud
        exchange = ccxt.kucoin()
        tickers = exchange.fetch_tickers()
        rows = []
        for s, v in tickers.items():
            if '/USDT' in s:
                rows.append({
                    "Koin": s.split('/'), # Ambil nama koinnya aja
                    "Harga": v['last'],
                    "Vol": v['quoteVolume']
                })
        return rows
    except:
        return []

# 3. HEADER
st.title("📈 CRYPTO DASHBOARD")
if st.button("🔄 REFRESH DATA"):
    st.rerun()

# 4. ENGINE UTAMA
data = get_crypto_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS (Wajib isi angka 3 buat Python 3.14)
    c1, c2, c3 = st.columns(3)
    
    # Cara filter koin yang aman
    btc = df[df['Koin'] == 'BTC']
    eth = df[df['Koin'] == 'ETH']
    sol = df[df['Koin'] == 'SOL']
    
    if not btc.empty:
        c1.metric("BTC/USDT", f"${btc.iloc['Harga']:,.2f}")
    if not eth.empty:
        c2.metric("ETH/USDT", f"${eth.iloc['Harga']:,.2f}")
    if not sol.empty:
        c3.metric("SOL/USDT", f"${sol.iloc['Harga']:,.2f}")

    st.divider()

    # 5. TABEL MARKET
    st.subheader("📊 Market Overview (Top 50 Volume)")
    # Mempercantik tampilan tabel
    st.dataframe(
        df.head(50), 
        use_container_width=True, 
        height=600,
        hide_index=True
    )

else:
    st.error("Koneksi API Gagal. Pastikan internet aman atau klik Refresh.")
