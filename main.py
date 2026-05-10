import streamlit as st
import pandas as pd
import ccxt

# 1. KONFIGURASI
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# 2. AMBIL DATA
def get_crypto_data():
    try:
        exchange = ccxt.kucoin()
        tickers = exchange.fetch_tickers()
        return [{"Koin": s.split('/'), "Harga": v['last'], "Vol": v['quoteVolume']} 
                for s, v in tickers.items() if '/USDT' in s]
    except:
        return []

# 3. HEADER (Tanpa 'with' biar gak error lagi)
st.title("📈 CRYPTO DASHBOARD")
if st.button("🔄 REFRESH DATA"):
    st.rerun()

# 4. ENGINE UTAMA
data = get_crypto_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS (Gue pake cara manual, paling aman dari error 'spec')
    col1, col2, col3 = st.columns(3)
    
    # Filter Koin
    btc = df[df['Koin'] == 'BTC']
    eth = df[df['Koin'] == 'ETH']
    sol = df[df['Koin'] == 'SOL']
    
    if not btc.empty:
        col1.metric("BTC/USDT", f"${btc.iloc['Harga']:,.2f}")
    if not eth.empty:
        col2.metric("ETH/USDT", f"${eth.iloc['Harga']:,.2f}")
    if not sol.empty:
        col3.metric("SOL/USDT", f"${sol.iloc['Harga']:,.2f}")

    st.divider()

    # TABEL (Langsung tampil, gak pake kolom-koloman ribet)
    st.subheader("📊 Market Overview (Top 50 Volume)")
    st.dataframe(df.head(50), use_container_width=True, height=600)

else:
    st.error("Gagal koneksi ke API. Klik Refresh.")
