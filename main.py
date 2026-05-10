import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. INITIAL CONFIG
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=30000, key="freshengine")

# 2. CSS STYLING (The Pro Vibe)
st.markdown(r'''
<style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #05080f; color: #e2e8f0; font-family: sans-serif; }
    .glass-card {
        background: rgba(23, 32, 53, 0.45);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    .title-text { color: #10b981; font-weight: 800; font-size: 32px; letter-spacing: -1.5px; margin: 0; }
    [data-testid="stMetric"] { background: rgba(15, 23, 42, 0.9); border-left: 5px solid #10b981; padding: 15px !important; border-radius: 10px; }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE (COINGECKO - HIGH RELIABILITY)
@st.cache_data(ttl=30)
def fetch_verified_market():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 50, 'page': 1, 'price_change_percentage': '24h'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            btc = next((x for x in data if x['symbol'] == 'btc'), None)
            
            rows = []
            for item in data:
                change = item['price_change_percentage_24h']
                # --- LOGIKA WARNA INDIKATOR ---
                indicator = "🟢" if change >= 0 else "🔴"
                
                rows.append({
                    "ASSET": item['symbol'].upper(),
                    "PRICE": item['current_price'],
                    "CHANGE (%)": change,
                    "TREND": indicator
                })
            
            df = pd.DataFrame(rows).head(12)
            # Formatting (Warna indikator tetap di kolom TREND)
            df['PRICE'] = df['PRICE'].apply(lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}")
            df['CHANGE (%)'] = df['CHANGE (%)'].apply(lambda x: f"{x:+.2f}%")
            
            p_btc = float(btc['current_price']) if btc else 0.0
            c_btc = float(btc['price_change_percentage_24h']) if btc else 0.0
            return df, p_btc, c_btc
    except: pass
    return pd.DataFrame(), 0.0, 0.0

# 4. RENDER UI
df_data, btc_val, btc_chg = fetch_verified_market()
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# --- HEADER (FIXED PARAMETERS) ---
h1, h2 = st.columns(2)
with h1:
    st.markdown('<p class="title-text">METAVERSEINDO_</p>', unsafe_allow_html=True)
with h2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:15px;font-family:monospace;'>{time_now} WIB</div>", unsafe_allow_html=True)

st.write("---")

# --- METRICS (FIXED PARAMETERS) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC / USD", f"${btc_val:,.0f}" if btc_val > 0 else "---", f"{btc_chg:+.2f}%")
m2.metric("STATUS", "LIVE", "STABLE")
m3.metric("FEED", "COINGECKO", "V3")
m4.metric("LOGIC", "TREND-ON", "ACTIVE")

st.write("")

# --- MAIN WORKSPACE (FIXED RATIO) ---
left_col, right_col = st.columns([1, 1.8])

with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📊
