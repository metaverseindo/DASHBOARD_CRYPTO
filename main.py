import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# 1. INITIAL SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")

# 2. JAM REAL-TIME (WIB)
tz = pytz.timezone('Asia/Jakarta')
time_now = datetime.now(tz).strftime("%H:%M:%S")

# 3. CSS CUSTOM
st.markdown(r'''
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; }
    .nav-bar-top {
        background: #0f172a;
        border-bottom: 2px solid #10b981;
        padding: 15px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .brand-id { color: #10b981; font-weight: 900; font-size: 28px; letter-spacing: 1px; }
    .live-clock { color: #10b981; font-family: monospace; font-weight: bold; font-size: 22px; }
    .card-panel { 
        background-color: rgba(15, 23, 42, 0.8); 
        border: 1px solid #1e293b; 
        border-radius: 8px; padding: 10px;
    }
    </style>
    ''', unsafe_allow_html=True)

# 4. NAVBAR
st.markdown(f'''
    <div class="nav-bar-top">
        <div class="brand-id">METAVERSEINDO_</div>
        <div class="live-clock">{time_now} WIB</div>
    </div>
    ''', unsafe_allow_html=True)

# 5. MAIN LAYOUT (AUDITED & FIXED)
# Baris ini SANGAT PENTING: Harus ada agar Python 3.14 tidak error
c_left, c_right = st.columns()

with c_left:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    # WIDGET KIRI: Market Quotes
    market_quotes = '''
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
      {
      "width": "100%", "height": "750",
      "symbolsGroups": [
        {
          "name": "Crypto",
          "symbols": [
            {"name": "BINANCE:BTCUSDT"},
            {"name": "BINANCE:ETHUSDT"},
            {"name": "BINANCE:SOLUSDT"},
            {"name": "BINANCE:BNBUSDT"},
            {"name": "BINANCE:XRPUSDT"},
            {"name": "BINANCE:ADAUSDT"},
            {"name": "BINANCE:DOGEUSDT"}
          ]
        }
      ],
      "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "locale": "en"
    }
      </script>
    </div>
    '''
    components.html(market_quotes, height=760)
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    # WIDGET KANAN: Advanced Chart
    tv_chart = '''
    <div id="tradingview_final"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%", "height": "750",
      "symbol": "BINANCE:BTCUSDT",
      "interval": "1",
      "timezone": "Asia/Jakarta",
      "theme": "dark",
      "style": "1", "locale": "en",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "hide_side_toolbar": false,
      "container_id": "tradingview_final"
    });
    </script>
    '''
    components.html(tv_chart, height=760)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. FOOTER
st.markdown("<div style='text-align:center; color:#334155; font-size:10px; margin-top:10px;'>METAVERSEINDO TERMINAL | 2026</div>", unsafe_allow_html=True)
