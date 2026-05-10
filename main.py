import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG (Harus paling atas)
st.set_page_config(page_title="META INDO", layout="wide", initial_sidebar_state="collapsed")

# 2. AUTO-REFRESH (Set tiap 10 detik biar gak terlalu pusing tapi tetep Live)
st_autorefresh(interval=10000, key="datarefresh")

# 3. STYLE & UI CUSTOMIZATION
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    
    /* Bikin angka di tabel rata kanan & font monospace biar rapi sejajar */
    [data-testid="stDataFrame"] td { 
        text-align: right !important; 
        font-family: 'ui-monospace', 'Cascadia Code', monospace !important; 
    }
    
    /* Glow effect buat nama Meta Indo */
    .glow-text { text-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA ENGINE (Ambil data dari KuCoin via CCXT)
@st.cache_data(ttl=9) # Cache dikit di bawah durasi refresh biar gak berat
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
        # Sort berdasarkan Volume terbesar (biar koin rame di atas)
        return pd.DataFrame(rows).sort_values("Vol", ascending=False).head(50)
    except Exception as e:
        return pd.DataFrame()

# 5. HEADER META INDO
st.markdown("""
    <div class="flex justify-between items-center bg-slate-900/80 p-6 rounded-2xl border border-slate-800 mb-6">
        <div>
            <h1 class="text-4xl font-black text-emerald-400 tracking-tighter glow-text">📊 META INDO</h1>
            <p class="text-slate-400 text-sm font-medium uppercase tracking-widest">Crypto Analytics Terminal</p>
        </div>
        <div class="flex items-center gap-3 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <p class="text-emerald-500 font-mono text-xs font-bold">LIVE FEED ACTIVE</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Eksekusi ambil data
df = get_crypto_data()

if not df.empty:
    # 6. TOP METRICS (BTC, ETH, SOL)
    m1, m2, m3 = st.columns(3)
    important_coins = ["BTC", "ETH", "SOL"]
    cols = [m1, m2, m3]
    
    for i, sym in enumerate(important_coins):
        row = df[df['Koin'] == sym]
        if not row.empty:
            cols[i].metric(
                label=f"{sym} / USDT", 
                value=f"${row.iloc['Harga']:,.2f}", 
                delta=f"{row.iloc['Change']:+.2f}%"
            )

    st.markdown("<div class='my-6 border-b border-slate-800'></div>", unsafe_allow_html=True)

    # 7. MAIN TABLE (FORMAT TITIK/KOMA & WARNA)
    st.markdown("<h2 class='text-xl font-bold text-slate-200 mb-4 px-2'>📊 Market Movement (Top 50 Vol)</h2>", unsafe_allow_html=True)

    # Fungsi styling warna teks
    def style_rows(row):
        # Change Positif = Ijo, Negatif = Merah
        change_color = '#10b981' if row['Change'] >= 0 else '#ef4444'
        styles = []
        for name in row.index:
            if name == 'Change':
                styles.append(f'color: {change_color}; font-weight: 800;')
            else:
                styles.append('color: #cbd5e1;') # Warna abu-abu terang buat angka lain biar gak pusing
        return styles

    # Apply Format Ribuan & Desimal
    styled_df = df.style.format({
        "Harga": "${:,.4f}", # Pake koma untuk ribuan, 4 desimal
        "Vol": "{:,.0f}",    # Pake koma untuk ribuan, tanpa desimal (Volume)
        "Change": "{:+.2f}%" # Sinyal + atau - dengan persen
    }).apply(style_rows, axis=1)

    # Tampilkan Tabel
    st.dataframe(
        styled_df,
        use_container_width=True, 
        height=650, 
        hide_index=True
    )

    # 8. FOOTER WIB
    tz_jkt = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz_jkt).strftime('%H:%M:%S')
    st.markdown(f"""
        <div class="flex justify-between items-center mt-4 px-2">
            <p class="text-slate-500 text-xs font-mono">ID: {waktu_skrg} WIB | Update: Auto (10s)</p>
            <a href="#top" class="text-emerald-500 text-xs no-underline hover:underline">↑ Back to Top</a>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("Gagal terhubung ke server exchange. Mencoba kembali...")
