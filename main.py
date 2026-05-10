import streamlit as st
import pandas as pd
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="META INDO PRO TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. AUTO REFRESH (TIAP 30 DETIK)
st_autorefresh(interval=30000, key="freshengine")

# 3. CSS CUSTOM (DARK MODE SULTAN)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; }
    .glow-header {
        color: #10b981; 
        text-shadow: 0 0 15px #10b981;
        font-weight: 900; 
        text-align: center; 
        padding: 20px; 
        font-size: 35px;
        font-family: 'Courier New', Courier, monospace;
    }
    .stDataFrame {
        border: 1px solid #1e293b;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. ENGINE VVIP DENGAN SISTEM FAILOVER (4 ENDPOINTS)
@st.cache_data(ttl=20)
def fetch_ultimate_data():
    # Ambil key dari Secrets Dashboard Streamlit
    key = st.secrets.get("BINANCE_API_KEY", None)
    
    # List pintu masuk Binance (Redundansi)
    endpoints = [
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    if key:
        headers["X-MBX-APIKEY"] = key

    # Mencoba satu per satu endpoint jika gagal
    for base_url in endpoints:
        try:
            url = f"{base_url}/api/v3/ticker/24hr"
            res = requests.get(url, headers=headers, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                rows = []
                for item in data:
                    # Filter hanya USDT dan Volume > 5 Juta USD
                    if item.get('symbol', '').endswith('USDT'):
                        coin = item['symbol'].replace('USDT', '')
                        vol = float(item.get('quoteVolume', 0))
                        if vol > 5000000:
                            rows.append({
                                "SYMBOL": coin,
                                "PRICE": float(item.get('lastPrice', 0)),
                                "CHANGE": float(item.get('priceChangePercent', 0)),
                                "VOL_RAW": vol,
                                "VOLUME 24H": f"$ {vol:,.0f}"
                            })
                
                df = pd.DataFrame(rows).sort_values("VOL_RAW", ascending=False).head(25)
                
                # Info server mana yang tembus
                server_host = base_url.split("//")
                status_label = f"🟢 VVIP LIVE ({server_host})" if key else f"🟡 LIVE ({server_host})"
                return df.drop(columns=['VOL_RAW']), status_label
        except:
            continue
            
    # Jika semua jalur diblokir
    backup_data = [
        {"SYMBOL": "BTC", "PRICE": 0.0, "CHANGE": 0.0, "VOLUME 24H": "ALL SERVERS BUSY"},
        {"SYMBOL": "ETH", "PRICE": 0.0, "CHANGE": 0.0, "VOLUME 24H": "PLEASE WAIT..."}
    ]
    return pd.DataFrame(backup_data), "🔴 ALL ENDPOINTS BLOCKED"

# 5. TAMPILAN UTAMA
st.markdown('<h1 class="glow-header">📊 META INDO PRO TERMINAL</h1>', unsafe_allow_html=True)

# Cek apakah Secrets terbaca (Indikator Debug)
if "BINANCE_API_KEY" not in st.secrets:
    st.error("❌ API KEY TIDAK TERDETEKSI: Pastikan sudah input di Dashboard Streamlit > Settings > Secrets")
else:
    st.success("✅ API KEY TERDETEKSI: Menggunakan jalur VVIP.")

# Ambil Data
df, status = fetch_ultimate_data()
