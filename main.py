# 1. Interval 10 detik biar gak terlalu "grabak-grubuk"
st_autorefresh(interval=10000, key="datarefresh")

# 2. CSS tambahan biar angka rapi sejajar (rata kanan)
st.markdown("""
    <style>
    /* Bikin angka di tabel rata kanan & font monospace biar sejajar titiknya */
    [data-testid="stDataFrame"] td { text-align: right !important; font-family: 'ui-monospace', monospace; }
    /* Efek glow dikit buat header META INDO */
    .stMarkdown h1 { text-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# 3. Logika warna yang lebih tajam (Ijo Emerald vs Merah Rose)
def style_row(row):
    color = '#10b981' if row['Change'] >= 0 else '#ef4444'
    return [f'color: {color}; font-weight: bold;' if name == 'Change' else 'color: #cbd5e1;' for name in row.index]

# 4. Format Angka (Titik & Koma)
styled_df = df.style.format({
    "Harga": "${:,.2f}", # 2 desimal biar gak kepanjangan
    "Vol": "{:,.0f}",    # Pemisah ribuan buat Volume
    "Change": "{:+.2f}%" # Sinyal + atau -
}).apply(style_row, axis=1)
