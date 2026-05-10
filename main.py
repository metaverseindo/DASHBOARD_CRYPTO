import streamlit as st
import pandas as pd
import ccxt

# 1. CONFIG (Wajib di paling atas)
st.set_page_config(page_title="Neon Crypto", layout="wide", initial_sidebar_state="collapsed")

# 2. INJECT TAILWIND & CUSTOM CSS
# Kita panggil script Tailwind dari CDN biar class-nya aktif
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    /* Sembunyikan Header & Footer Streamlit agar bersih */
    header, footer, #MainMenu {visibility: hidden;}
    
    /* Paksa Background Deep Dark ala Tailwind Slate-950 */
    .stApp {
        background-color: #020617;
        scroll-behavior: smooth;
    }

    /* Custom Scrollbar Neon */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 5px; }
    
    /* Styling Metric Streamlit agar sinkron dengan Tailwind */
    [data-testid="stMetricValue"] {
        color: #34d399 !important; /* Emerald 400 */
        font-family: 'ui-monospace', monospace;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI AMBIL DATA
def get_data():
    try:
        ex = ccxt.kucoin()
        tickers = ex.fetch_tickers()
        return [{"Koin": s.split('/'), "Harga": v['last'], "Vol": v['quoteVolume'], "Change": v['percentage'] or 0.0} 
                for s, v in tickers.items() if '/USDT' in s]
    except: return []

# 4. HEADER PAKE TAILWIND CLASSES
# Kita bungkus title pake div Tailwind biar makin cakep
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/50 p-6 rounded-2xl border border-slate-800 mb-8">
        <div>
            <h1 class="text-3xl font-black text-emerald-400 tracking-tighter">⚡ NEON TERMINAL</h1>
            <p class="text-slate-400 text-sm font-medium">Real-time Crypto Analytics Engine</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.button("🔄 Sync Blockchain Data"):
    st.rerun()

# 5. ENGINE & DISPLAY
data = get_data()
if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS SECTION (FIXED FOR PYTHON 3.14)
    m_cols = st.columns(3)
    top_3 = ["BTC", "ETH", "SOL"]
    for i, sym in enumerate(top_3):
        row = df[df['Koin'] == sym]
        if not row.empty:
            with m_cols[i]:
                st.metric(label=f"{sym} / USDT", 
                          value=f"${row.iloc['Harga']:,.2f}", 
                          delta=f"{row.iloc['Change']:+.2f}%")

    st.markdown("<div class='my-8'></div>", unsafe_allow_html=True)

    # 6. MARKET TABLE
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>🔥 Top Volume Movers</h2>", unsafe_allow_html=True)
    
    # Styling DataFrame
    st.dataframe(
        df.head(50),
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    # FOOTER DENGAN TAILWIND
    st.markdown("""
        <div class="mt-12 text-center pb-10">
            <a href="#top" class="text-emerald-500 hover:text-emerald-400 transition-colors text-sm font-bold tracking-widest uppercase">
                ↑ Back to Top
            </a>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("Koneksi API Gagal. Sila Refresh.")
