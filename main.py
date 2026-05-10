import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime

# 1. CONFIG (Wajib paling atas)
st.set_page_config(page_title="META INDO", layout="wide", initial_sidebar_state="collapsed")

# 2. INJECT TAILWIND & CLEAN UI
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    /* Sembunyikan Header GitHub/Edit & Footer */
    header, footer, #MainMenu {visibility: hidden;}
    
    .stApp {
        background-color: #020617;
        scroll-behavior: smooth;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 5px; }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #34d399 !important;
        font-family: 'ui-monospace', monospace;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI AMBIL DATA
def get_data():
    try:
        # Pake Kucoin biar stabil
        ex = ccxt.kucoin({'enableRateLimit': True})
        tickers = ex.fetch_tickers()
        return [{"Koin": s.split('/'), "Harga": v['last'], "Vol": v['quoteVolume'], "Change": v['percentage'] or 0.0} 
                for s, v in tickers.items() if '/USDT' in s]
    except Exception as e:
        return []

# 4. HEADER META INDO - LOGO 📊
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/80 p-6 rounded-2xl border border-slate-800 mb-8">
        <div>
            <h1 class="text-4xl font-black text-emerald-400 tracking-tighter">📊 META INDO</h1>
            <p class="text-slate-400 text-sm font-medium uppercase tracking-widest">Crypto Analytics Terminal</p>
        </div>
        <div class="text-right">
            <p class="text-slate-500 text-xs font-mono">DATA STREAM</p>
            <p class="text-emerald-500 text-xs font-mono">ACTIVE</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tombol Refresh
col_btn = st.columns()
with col_btn:
    if st.button("🔄 SYNC DATA"):
        st.cache_data.clear()
        st.rerun()

# 5. ENGINE UTAMA
data = get_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS
    m_cols = st.columns(3)
    coins = ["BTC", "ETH", "SOL"]
    
    for i, sym in enumerate(coins):
        row = df[df['Koin'] == sym]
        if not row.empty:
            with m_cols[i]:
                st.metric(
                    label=f"{sym} Market", 
                    value=f"${row.iloc['Harga']:,.2f}", 
                    delta=f"{row.iloc['Change']:+.2f}%"
                )

    st.markdown("<div class='my-8 border-b border-slate-800'></div>", unsafe_allow_html=True)

    # 6. DATA TABLE
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>📊 Market Movement</h2>", unsafe_allow_html=True)
    
    st.dataframe(
        df.head(50),
        use_container_width=True,
        height=550,
        hide_index=True
    )
    
    # Footer info
    st.caption(f"Last Synchronization: {datetime.now().strftime('%H:%M:%S')} WIB")

else:
    st.warning("Menunggu data dari provider... Coba klik Sync Data.")
