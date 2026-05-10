import streamlit as st
import pandas as pd
import ccxt
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIG
st.set_page_config(page_title="Crypto Neon", layout="wide")

# 2. DATA
def get_data():
    try:
        ex = ccxt.kucoin()
        t = ex.fetch_tickers()
        return [{"Koin": s.split('/'), "Harga": v['last'], "Change": v['percentage'] or 0.0, "Vol": v['quoteVolume']} 
                for s, v in t.items() if '/USDT' in s]
    except: return []

# 3. HEADER - PERHATIKAN ANGKA 2 DI DALAM KURUNG
c1, c2 = st.columns(2) 
with c1:
    st.title("📈 CRYPTO NEON")
with c2:
    if st.button("🔄 Refresh"): st.rerun()

# 4. ENGINE
data = get_data()
if data:
    df = pd.DataFrame(data).sort_values("Vol", ascending=False)
    
    # METRICS - PERHATIKAN ANGKA 3 DI DALAM KURUNG
    m = st.columns(3)
    coins = ["BTC", "ETH", "SOL"]
    for i, sym in enumerate(coins):
        row = df[df['Koin'] == sym]
        if not row.empty:
            m[i].metric(sym, f"${row.iloc['Harga']}", f"{row.iloc['Change']}%")

    st.divider()

    # TABLE & CHART - PERHATIKAN LIST DI DALAM KURUNG
    left, right = st.columns()
    with left:
        st.dataframe(df.head(20), use_container_width=True)
    with right:
        top10 = df.head(10)
        fig = go.Figure(go.Bar(x=top10['Vol'], y=top10['Koin'], orientation='h'))
        st.plotly_chart(fig, use_container_width=True)
