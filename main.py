import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz # Tambahin ini buat urusan timezone

# 1. CONFIG
st.set_page_config(page_title="META INDO", layout="wide", initial_sidebar_state="collapsed")

# 2. STYLE & TAILWIND
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; scroll-behavior: smooth; }
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 5px; }
    [data-testid="stMetricValue"] { color: #34d399 !important; font-family: 'monospace'; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE
def get_data():
    try:
        ex = ccxt.kucoin({'enableRateLimit': True})
        t = ex.fetch_tickers()
        rows = []
        for s, v in t.items():
            if '/USDT' in s:
                rows.append({
                    "Koin": s.split('/'),
                    "Harga": v['last'],
                    "Vol": v['quoteVolume'],
                    "Change": v['percentage'] or 0.0
                })
        return rows
    except: return []

# 4. HEADER
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/80 p-6 rounded-2xl border border-slate-800 mb-8">
        <div>
            <h1 class="text-4xl font-black text-emerald-400 tracking-tighter">📊 META INDO</h1>
            <p class="text-slate-400 text-sm font-medium uppercase tracking-widest">Crypto Analytics Terminal</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. BUTTON REFRESH
if st.button("🔄 SYNC DATA SEKARANG"):
    st.cache_data.clear()
    st.rerun()

# 6. MAIN ENGINE
data = get_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS
    col1, col2, col3 = st.columns(3)
    
    btc_row = df[df['Koin'] == 'BTC']
    if not btc_row.empty:
        col1.metric("BTC Market", f"${btc_row.iloc['Harga']:,.2f}", f"{btc_row.iloc['Change']:+.2f}%")
    
    eth_row = df[df['Koin'] == 'ETH']
    if not eth_row.empty:
        col2.metric("ETH Market", f"${eth_row.iloc['Harga']:,.2f}", f"{eth_row.iloc['Change']:+.2f}%")
        
    sol_row = df[df['Koin'] == 'SOL']
    if not sol_row.empty:
        col3.metric("SOL Market", f"${sol_row.iloc['Harga']:,.2f}", f"{sol_row.iloc['Change']:+.2f}%")

    st.divider()

  # 7. TABLE DENGAN SINYAL WARNA & PEMISAH RIBUAN
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>📊 Market Movement</h2>", unsafe_allow_html=True)
    
    st.data_editor(
        df.head(50),
        column_config={
            # Harga tetap dengan 4 desimal
            "Harga": st.column_config.NumberColumn(
                "Harga ($)", 
                format="$%.4f"
            ),
            # Volume sekarang pake pemisah ribuan (1,234,567)
            "Vol": st.column_config.NumberColumn(
                "Volume 24h", 
                format="%d" 
            ),
            # SINYAL WARNA: Ijo buat naik, Merah buat turun
            "Change": st.column_config.ProgressColumn(
                "Change (%)",
                help="Persentase perubahan harga 24 jam",
                format="%.2f%%",
                min_value=-15, # Batas bawah warna merah
                max_value=15,  # Batas atas warna ijo
            )
        },
        use_container_width=True,
        height=550,
        hide_index=True,
        disabled=True
    )
    
    # Tambahan CSS biar warna Change makin kontras (opsional tapi bagus)
    st.markdown("""
        <style>
        /* Mewarnai text di kolom Change berdasarkan value */
        [data-testid="stTableSummary"] { font-family: monospace; }
        </style>
    """, unsafe_allow_html=True)

    # --- INFO JAM WIB ---
    tz_jakarta = pytz.timezone('Asia/Jakarta')
    waktu_sekarang = datetime.now(tz_jakarta).strftime('%H:%M:%S')
    st.caption(f"Last sync: {waktu_sekarang} WIB")
