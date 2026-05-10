import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG
st.set_page_config(page_title="META INDO", layout="wide", initial_sidebar_state="collapsed")

# 2. AUTO-REFRESH (Refresh tiap 10 detik)
st_autorefresh(interval=10000, key="datarefresh")

# 3. STYLE & UI CUSTOMIZATION
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    
    /* Perbaikan: Rata Kanan untuk angka & Monospace agar titik sejajar */
    [data-testid="stDataFrame"] td { 
        text-align: right !important; 
        font-family: 'ui-monospace', monospace !important; 
    }
    
    .glow-text { text-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA ENGINE (Update: Menambahkan Kolom No)
@st.cache_data(ttl=9)
def get_crypto_data():
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
        
        # Sort by Volume & Ambil Top 50
        df_res = pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
        
        # INSERT KOLOM NOMOR DI AWAL
        df_res.insert(0, "No", range(1, len(df_res) + 1))
        
        return df_res
    except:
        return pd.DataFrame()

# 5. HEADER
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/80 p-6 rounded-2xl border border-slate-800 mb-6">
        <div>
            <h1 class="text-4xl font-black text-emerald-400 tracking-tighter glow-text">📊 META INDO</h1>
            <p class="text-slate-400 text-sm font-medium uppercase tracking-widest">Live Market Pulse</p>
        </div>
        <div class="flex items-center gap-3 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <p class="text-emerald-500 font-mono text-xs font-bold">LIVE FEED</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = get_crypto_data()

if not df.empty:
    # 6. METRICS (BTC, ETH, SOL)
    m1, m2, m3 = st.columns(3)
    for i, sym in enumerate(["BTC", "ETH", "SOL"]):
        row = df[df['Koin'] == sym]
        if not row.empty:
            [m1, m2, m3][i].metric(f"{sym}/USDT", f"${row.iloc['Harga']:,.2f}", f"{row.iloc['Change']:+.2f}%")

    st.markdown("<div class='my-6 border-b border-slate-800'></div>", unsafe_allow_html=True)

    # 7. MAIN TABLE (Update: Style Kolom Nomor)
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>📊 Market Movement</h2>", unsafe_allow_html=True)

    def style_rows(row):
        # Change Ijo/Merah
        change_color = '#10b981' if row['Change'] >= 0 else '#ef4444'
        styles = []
        for name in row.index:
            if name == 'Change':
                styles.append(f'color: {change_color}; font-weight: 800;')
            elif name == 'No':
                styles.append('color: #64748b; text-align: center;') # Nomor abu-abu & tengah
            else:
                styles.append('color: #cbd5e1;') # Angka lain abu-abu terang
        return styles

    styled_df = df.style.format({
        "No": "{:02d}",     # Format 01, 02, dst
        "Harga": "${:,.4f}", # Koma ribuan, titik desimal
        "Vol": "{:,.0f}",    # Koma ribuan, tanpa desimal
        "Change": "{:+.2f}%" 
    }).apply(style_rows, axis=1)

    st.dataframe(styled_df, use_container_width=True, height=650, hide_index=True)

    # 8. FOOTER
    tz = pytz.timezone('Asia/Jakarta')
    st.markdown(f'<p class="text-slate-500 text-xs font-mono mt-4">ID: {datetime.now(tz).strftime("%H:%M:%S")} WIB | Auto-Refresh: 10s</p>', unsafe_allow_html=True)
else:
    st.error("API Error. Memperbaiki koneksi...")
