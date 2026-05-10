import streamlit as st
import pandas as pd
import ccxt

# 1. Pastikan config di paling atas
st.set_page_config(page_title="Crypto Neon", layout="wide")

# 2. Fungsi ambil data yang simpel
def ambil_data():
    try:
        ex = ccxt.kucoin()
        tickers = ex.fetch_tickers()
        return [{"Coin": s.split('/'), "Price": v['last'], "Vol": v['quoteVolume']} 
                for s, v in tickers.items() if '/USDT' in s]
    except:
        return []

# 3. Baris 57 (Yang sering error) - Gue isi angka 2
c1, c2 = st.columns(2) 
with c1:
    st.title("⚡ CRYPTO DASHBOARD")
with c2:
    if st.button("🔄 Refresh Data"):
        st.rerun()

# 4. Engine utama
data = ambil_data()
if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # Metrics - Gue isi angka 3
    cols = st.columns(3)
    top_coins = ["BTC", "ETH", "SOL"]
    for i, coin in enumerate(top_coins):
        row = df[df['Coin'] == coin]
        if not row.empty:
            cols[i].metric(coin, f"${row.iloc['Price']}")

    st.divider()

    # Layout bawah - Gue isi list biar aman
    full_col = st.columns()
    with full_col:
        st.subheader("📊 Market Top 20")
        st.dataframe(df.head(20), use_container_width=True)
else:
    st.error("Gagal ambil data API. Coba lagi nanti.")
