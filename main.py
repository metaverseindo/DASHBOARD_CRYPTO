import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG
st.set_page_config(page_title="META INDO", layout="wide", initial_sidebar_state="collapsed")

# Ganti dari 5000 (5 detik) ke 30000 (30 detik)
st_autorefresh(interval=30000, key="datarefresh")

# 3. STYLE & TAILWIND
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    [data-testid="stMetricValue"] { color: #34d399 !important; font-family: 'monospace'; font-weight: 800; }
    /* Animasi Fade In buat tabel */
    .stDataFrame { animation: fadeIn 0.5s; }
    @keyframes fadeIn { from { opacity: 0.5; } to { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA ENGINE (Pake Cache buat bandingin harga lama & baru)
@st.cache_data(ttl=4)
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
        return pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
    except: return pd.DataFrame()

# 5. HEADER
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/80 p-6 rounded-2xl border border-slate-800 mb-6">
        <div>
            <h1 class="text-4xl font-black text-emerald-400 tracking-tighter">📊 META INDO</h1>
            <p class="text-slate-400 text-sm font-medium uppercase tracking-widest">Live Market Pulse</p>
        </div>
        <div class="flex items-center gap-2">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <p class="text-emerald-500 font-mono text-xs">LIVE STREAMING</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = get_crypto_data()

if not df.empty:
    # 6. METRICS
    c1, c2, c3 = st.columns(3)
    for i, sym in enumerate(["BTC", "ETH", "SOL"]):
        row = df[df['Koin'] == sym]
        if not row.empty:
            [c1, c2, c3][i].metric(f"{sym} / USDT", f"${row.iloc['Harga']:,.2f}", f"{row.iloc['Change']:+.2f}%")

    # 7. STYLED TABLE (FORMAT RAPIH & WARNA)
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4'>📊 Market Movement</h2>", unsafe_allow_html=True)

    def style_row(row):
        # Logika warna: Change > 0 (Ijo/Beli), Change < 0 (Merah/Jual)
        color = '#4ade80' if row['Change'] >= 0 else '#f87171'
        return [f'color: {color}; font-weight: bold' if name == 'Change' else '' for name in row.index]

    styled_df = df.style.format({
        "Harga": "${:,.4f}",
        "Vol": "{:,.0f}",
        "Change": "{:+.2f}%"
    }).apply(style_row, axis=1)

    st.dataframe(styled_df, use_container_width=True, height=600, hide_index=True)

    # 8. FOOTER WIB
    tz = pytz.timezone('Asia/Jakarta')
    st.caption(f"Last Auto-Sync: {datetime.now(tz).strftime('%H:%M:%S')} WIB | Refresh rate: 5s")

else:
    st.error("Koneksi API putus. Reconnecting...")
