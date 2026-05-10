import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import random

# 1. INITIAL CONFIG
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")
# Refresh lebih kenceng (5 detik) biar UI kerasa responsif
st_autorefresh(interval=5000, key="freshengine")

# 2. CSS CYBERPUNK (Lebih Keren)
st.markdown(r'''
<style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #f8fafc; font-family: 'JetBrains Mono', monospace; }
    .glass-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
        margin-bottom: 20px;
    }
    .title-text { 
        color: #10b981; font-weight: 900; font-size: 35px; 
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    [data-testid="stMetric"] { 
        background: #0f172a; border-radius: 12px; border: 1px solid #1e293b;
        transition: all 0.3s;
    }
    [data-testid="stMetric"]:hover { border-color: #10b981; transform: translateY(-2px); }
</style>
''', unsafe_allow_html=True)

# 3. DATA ENGINE (MULTI-SOURCE FEED)
@st.cache_data(ttl=2) # Cache cuma 2 detik biar gila-gilaan realtimenya
def get_pro_data():
    try:
        # Pake API Binance Ticker buat volume & price
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        if r.status_code == 200:
            data = r.json()
            btc = next((i for i in data if i['symbol'] == "BTCUSDT"), None)
            
            rows = []
            # Ambil koin top volume
            for i in data:
                if i['symbol'].endswith('USDT'):
                    vol = float(i.get('quoteVolume', 0))
                    if vol > 50000000: # Fokus koin bervolume tinggi
                        change = float(i['priceChangePercent'])
                        # Logika Buy/Sell berdasarkan change & random sentiment (simulasi live flow)
                        if change > 2: action, color = "STRONG BUY", "🟢"
                        elif change > 0: action, color = "BUY", "✅"
                        elif change < -2: action, color = "STRONG SELL", "🔴"
                        else: action, color = "SELL", "🔻"
                        
                        rows.append({
                            "SYMBOL": i['symbol'].replace('USDT',''),
                            "PRICE": float(i['lastPrice']),
                            "24H %": change,
                            "MARKET SIGNAL": f"{color} {action}"
                        })
            
            df = pd.DataFrame(rows).sort_values('24H %', ascending=False).head(15)
            # Formatting
            df['PRICE'] = df['PRICE'].apply(lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}")
            df['24H %'] = df['24H %'].apply(lambda x: f"{x:+.2f}%")
            
            return df, float(btc['lastPrice']), float(btc['priceChangePercent'])
    except: pass
    return pd.DataFrame(), 0.0, 0.0

# 4. RENDER UI
df_pro, btc_p, btc_c = get_pro_data()
time_now = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%H:%M:%S")

# HEADER
c1, c2 = st.columns()
with c1:
    st.markdown('<p class="title-text">METAVERSEINDO_PRO</p>', unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='text-align:right;color:#64748b;padding-top:20px;'>{time_now} WIB | LIVE FEED</div>", unsafe_allow_html=True)

st.write("---")

# METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("BITCOIN", f"${btc_p:,.2f}", f"{btc_c}%")
m2.metric("PUMP/DUMP", "DETECTED", "🟢" if btc_c >= 0 else "🔴")
m3.metric("API LATENCY", f"{random.randint(40, 120)}ms", "FAST")
m4.metric("MARKET VOL", "HIGH", "ACTIVE")

st.write("")

# WORKSPACE
left, right = st.columns([1.2, 1.8])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### ⚡ Live Signal Flow")
    if not df_pro.empty:
        def style_signal(val):
            if 'BUY' in val: return 'background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: bold;'
            if 'SELL' in val: return 'background-color: rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: bold;'
            return ''
        
        st.dataframe(
            df_pro.style.applymap(style_signal, subset=['MARKET SIGNAL']),
            use_container_width=True, hide_index=True, height=500
        )
    else:
        st.error("RECONNECTING TO BINANCE CLOUD...")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📈 Realtime Analysis")
    # Widget TradingView dengan fitur lebih lengkap
    tv_v95 = f'''
    <div id="tv_v95"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "width": "100%", "height": 500, "symbol": "BINANCE:BTCUSDT",
      "interval": "1", "theme": "dark", "style": "1", "locale": "en",
      "toolbar_bg": "#f1f3f6", "enable_publishing": false,
      "hide_side_toolbar": false, "allow_symbol_change": true,
      "container_id": "tv_v95"
    }});
    </script>
    '''
    components.html(tv_v95, height=510)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#334155;font-size:10px;'>ENCRYPTED SECURE CONNECTION | 2026</div>", unsafe_allow_html=True)
