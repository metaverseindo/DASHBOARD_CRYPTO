import streamlit as st
import pandas as pd
import ccxt

# 1. KONFIGURASI AWAL
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# 2. AMBIL DATA DARI API
def get_crypto_data():
    try:
        # Pake Kucoin biar lebih stabil di cloud
        exchange = ccxt.kucoin()
        tickers = exchange.fetch_tickers()
        data_list = []
        for symbol, val in tickers.items():
            if '/USDT' in symbol:
                data_list.append({
                    "Koin": symbol.split('/'),
                    "Harga": val['last'],
                    "Volume": val['quoteVolume']
                })
        return data_list
    except:
        return []

# 3. HEADER (PAKAI ANGKA 1 BIAR GAK ERROR)
header_col = st.columns(1)
with header_col:
    st.title("📈 CRYPTO DASHBOARD")
    if st.button("🔄 REFRESH DATA"):
        st.rerun()

# 4. ENGINE UTAMA
data = get_crypto_data()

if data:
    df = pd.DataFrame(data).sort_values("Volume", ascending=False)
    
    # METRICS (PAKAI ANGKA 3 BIAR GAK ERROR)
    col1, col2, col3 = st.columns(3)
    
    # Cari data BTC, ETH, SOL
    btc = df[df['Koin'] == 'BTC']
    eth = df[df['Koin'] == 'ETH']
    sol = df[df['Koin'] == 'SOL']
    
    if not btc.empty: col1.metric("BTC/USDT", f"${btc.iloc['Harga']:,.2f}")
    if not eth.empty: col2.metric("ETH/USDT", f"${eth.iloc['Harga']:,.2f}")
    if not sol.empty: col3.metric("SOL/USDT", f"${sol.iloc['Harga']:,.2f}")

    st.divider()

    # TABEL (PAKAI ANGKA 1 BIAR GAK ERROR 'SPEC')
    st.subheader("📊 Market Overview (Top 50 Volume)")
    st.dataframe(df.head(50), use_container_width=True, height=600)

else:
    st.error("Gagal koneksi ke API Exchange. Coba klik refresh.")
