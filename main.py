import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. INITIAL SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="expanded")

# 2. CSS CUSTOM
st.markdown(r'''
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 2px solid #10b981; }
    .nav-bar-top {
        background-color: #0f172a; border-bottom: 2px solid #10b981;
        padding: 15px; display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 20px; border-radius: 10px;
    }
    .brand-id { color: #10b981; font-weight: 900; font-size: 24px; font-family: 'Orbitron', sans-serif; }
    .card-panel { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 10px; }
    </style>
    ''', unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown('<div class="brand-id">metaverseindo</div>', unsafe_allow_html=True)
    st.info("Terminal integrated with TradingView Real-Time Data.")

# 4. NAVBAR
st.markdown(f'''<div class="nav-bar-top"><div class="brand-id">metaverseindo</div><div style="color:#10b981; font-weight:bold;">LIVE TERMINAL</div></div>''', unsafe_allow_html=True)

# 5. MAIN LAYOUT
col_left, col_right = st.columns([1.5, 2.5])

with col_left:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.write("##### Market Monitor")
    # INTEGRASI SCREENER REAL-TIME
    screener_html = '''
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {
      "colorTheme": "dark",
      "dateRange": "12M",
      "showChart": false,
      "locale": "en",
      "width": "100%",
      "height": "600",
      "largeChartUrl": "",
      "isTransparent": true,
      "showSymbolLogo": true,
      "showFloatingTooltip": false,
      "tabs": [
        {
          "title": "Crypto",
          "symbols": [
            {"s": "BINANCE:BTCUSDT"},
            {"s": "BINANCE:ETHUSDT"},
            {"s": "BINANCE:BNBUSDT"},
            {"s": "BINANCE:SOLUSDT"},
            {"s": "BINANCE:XRPUSDT"},
            {"s": "BINANCE:ADAUSDT"}
          ]
        }
      ]
    }
      </script>
    </div>
    '''
    components.html(screener_html, height=610)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.write("##### Analysis Chart")
    # CHART YANG BISA DIGANTI PAIRNYA
    tv_chart = '''
    <div id="tradingview_chart"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%",
      "height": 600,
      "symbol": "BINANCE:BTCUSDT",
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
    });
    </script>
    '''
    components.html(tv_chart, height=610)
    st.markdown('</div>', unsafe_allow_html=True)
