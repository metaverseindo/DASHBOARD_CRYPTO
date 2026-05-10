import streamlit as st
import pandas as pd
import ccxt

# 1. KONFIGURASI (Harus paling atas sebelum markdown)
st.set_page_config(
    page_title="Crypto Metaverse Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS (Smooth Scroll + Hide GitHub UI + Metaverse Theme)
st.markdown("""
    <style>
    /* Smooth Scroll */
    html { scroll-behavior: smooth; }
    
    /* Hide Streamlit Elements (GitHub, Edit, Footer) */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Neon Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0e11; }
    ::-webkit-scrollbar-thumb { background: #00ffc8; border-radius: 10px; }
    
    /* Deep Dark Background */
    .stApp { background-color: #0b0e11; color: #eaecef; }
    
    /* Neon Metric */
    [data-testid="stMetricValue"] { color: #00ffc8 !important; font-family: 'monospace'; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATA
def get_crypto_data():
    try:
        exchange = ccxt.kucoin()
        tickers = exchange.fetch_tickers()
        rows = []
        for s, v in tickers.items():
            if '/USDT' in s:
                rows.append({
                    "Koin": s.split('/'), # FIX: Ambil index 0
                    "Harga": v['last'],
                    "Vol": v['quoteVolume']
                })
        return rows
    except:
        return []

# 4. HEADER
st.title("⚡ CRYPTO METAVERSEINDO")
if st.button("🔄 REFRESH DATA"):
    st.rerun()

# 5. ENGINE
data = get_crypto_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS (Fix: st.columns(3) biar gak error spec)
    c1, c2, c3 = st.columns(3)
    
    # Filter koin dengan cara yang bener
    btc = df[df['Koin'] == 'BTC']
    eth = df[df['Koin'] == 'ETH']
    sol = df[df['Koin'] == 'SOL']
    
    # FIX: Pake iloc bukan iloc['Harga']
    if not btc.empty:
        c1.metric("BTC/USDT", f"${btc.iloc['Harga']:,.2f}")
    if not eth.empty:
        c2.metric("ETH/USDT", f"${eth.iloc['Harga']:,.2f}")
    if not sol.empty:
        c3.metric("SOL/USDT", f"${sol.iloc['Harga']:,.2f}")

    st.divider()

    # 6. TABEL MARKET
    st.subheader("📊 Live Market Overview")
    st.dataframe(
        df.head(50), 
        use_container_width=True, 
        height=600,
        hide_index=True
    )
    
    # Tombol Back to Top (Manfaatin Smooth Scroll)
    st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)
    st.markdown("<a href='#top' style='color:#00ffc8; text-decoration:none;'>↑ Back to Top</a>", unsafe_allow_html=True)

else:
    st.error("Gagal ambil data API. Coba lagi.")
