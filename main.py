import streamlit as st
import pandas as pd
import ccxt

st.set_page_config(layout="wide")

st.title("🧪 API TEST MODE")

try:
    # Coba pake Binance dulu buat test koneksi
    ex = ccxt.binance({'timeout': 20000, 'enableRateLimit': True})
    tickers = ex.fetch_tickers()
    
    data = []
    for sym, v in tickers.items():
        if '/USDT' in sym:
            data.append({
                "COIN": sym,
                "PRICE": v['last'],
                "VOLUME": v['quoteVolume']
            })
    
    df = pd.DataFrame(data).sort_values("VOLUME", ascending=False).head(20)
    st.success("✅ API BERHASIL NARIK DATA!")
    st.table(df) # Pake table biasa biar gak ada error render

except Exception as e:
    st.error(f"❌ API GAGAL: {e}")
    st.info("Saran: Cek apakah library 'ccxt' sudah ada di requirements.txt")
