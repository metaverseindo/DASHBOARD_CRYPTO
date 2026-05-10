import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Dashboard Crypto Real-Time")
st.caption("Semua pasangan USDT dari Binance API")

def fetch_all_usdt_tickers():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        all_tickers = resp.json()
        return [t for t in all_tickers if t["symbol"].endswith("USDT")]
    except Exception:
        return []

TOP_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

auto_refresh = st.toggle("Auto-refresh setiap 30 detik", value=True)
st.button("🔄 Refresh Sekarang")

with st.spinner("Mengambil data semua koin USDT dari Binance..."):
    tickers = fetch_all_usdt_tickers()

if not tickers:
    st.error("Gagal mengambil data dari Binance. Coba refresh kembali.")
    st.stop()

ticker_map = {t["symbol"]: t for t in tickers}

top_cols = st.columns(3)
for i, sym in enumerate(TOP_SYMBOLS):
    t = ticker_map.get(sym)
    with top_cols[i]:
        if t:
            price = float(t["lastPrice"])
            change = float(t["priceChangePercent"])
            label = sym.replace("USDT", "")
            st.metric(
                label=label,
                value=f"${price:,.2f}",
                delta=f"{change:+.2f}%",
            )
        else:
            st.metric(label=sym.replace("USDT", ""), value="N/A")

st.divider()

rows = []
for t in tickers:
    rows.append({
        "Koin": t["symbol"].replace("USDT", ""),
        "Harga (USDT)": float(t["lastPrice"]),
        "Perubahan 24j (%)": float(t["priceChangePercent"]),
        "Tertinggi 24j": float(t["highPrice"]),
        "Terendah 24j": float(t["lowPrice"]),
        "Volume 24j (USDT)": float(t["quoteVolume"]),
    })

df = pd.DataFrame(rows)
df = df.sort_values("Volume 24j (USDT)", ascending=False).reset_index(drop=True)

col_search, col_info = st.columns([2, 3])
with col_search:
    search = st.text_input("🔍 Cari koin...", placeholder="Contoh: BTC, ETH, SOL")
with col_info:
    st.markdown(f"<div style='padding-top:28px; color:gray'>Total koin: <b>{len(df)}</b> pasangan USDT</div>", unsafe_allow_html=True)

if search:
    mask = df["Koin"].str.contains(search.strip().upper(), na=False)
    df_filtered = df[mask]
else:
    df_filtered = df

def color_change(val):
    if pd.isna(val):
        return ""
    color = "#16a34a" if val >= 0 else "#dc2626"
    return f"color: {color}; font-weight: bold"

styled = (
    df_filtered.style
    .format({
        "Harga (USDT)": "${:,.6g}",
        "Perubahan 24j (%)": "{:+.2f}%",
        "Tertinggi 24j": "${:,.6g}",
        "Terendah 24j": "${:,.6g}",
        "Volume 24j (USDT)": "${:,.0f}",
    })
    .map(color_change, subset=["Perubahan 24j (%)"])
)

st.subheader(f"Tabel Semua Koin USDT — Diurutkan Volume Tertinggi")
st.dataframe(styled, use_container_width=True, hide_index=True, height=600)

st.caption(f"Terakhir diperbarui: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")
