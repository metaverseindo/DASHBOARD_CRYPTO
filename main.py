import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime

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
        return [{"Koin": s.split('/'), "Harga": v['last'], "Vol": v['quoteVolume'], "Change": v['percentage'] or 0.0} 
                for s, v in t.items() if '/USDT' in s]
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

# 5. BUTTON REFRESH (Pake cara paling basic biar gak error)
if st.button("🔄 SYNC DATA SEKARANG"):
    st.cache_data.clear()
    st.rerun()

# 6. MAIN ENGINE
data = get_data()

if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS - Langsung buat 3 kolom dan isi satu-satu
    c1, c2, c3 = st.columns(3)
    
    coins = ["BTC", "ETH", "SOL"]
    for i, sym in enumerate(coins):
        row = df[df['Koin'] == sym]
        if not row.empty:
            target_col = [c1, c2, c3][i]
            target_col.metric(
                label=f"{sym} Market", 
                value=f"${row.iloc['Harga']:,.2f}", 
                delta=f"{row.iloc['Change']:+.2f}%"
            )

    st.divider()

    # 7. TABLE
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>📊 Market Movement</h2>", unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True, height=550, hide_index=True)
    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')} WIB")

else:
    st.warning("Data belum masuk. Klik Sync Data.")
