import streamlit as st
import streamlit.components.v1 as components

# 1. INITIAL SETUP
st.set_page_config(page_title="metaverseindo", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS CUSTOM (STABILIZED)
st.markdown(r'''
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #020617; color: #eaecef; }
    .nav-bar-top {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        border-bottom: 2px solid #10b981;
        padding: 15px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-radius: 0 0 15px 15px;
    }
    .brand-id { 
        color: #10b981; font-weight: 900; font-size: 28px; letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
    }
    .card-panel { 
        background-color: rgba(30, 41, 59, 0.5); 
        border: 1px solid #334155; 
        border-radius: 12px; padding: 15px;
        backdrop-filter: blur(10px);
    }
    </style>
    ''', unsafe_allow_html=True)

# 3. NAVBAR
st.markdown('''
    <div class="nav-bar-top">
        <div class="brand-id">METAVERSEINDO_</div>
        <div style="color:#10b981; font-weight:bold; font-family:monospace;">STABLE TERMINAL v.99</div>
    </div>
    ''', unsafe_allow_html=True)

# 4. MAIN LAYOUT
col_left, col_right = st.columns([1.2, 2.8])

with col_left:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("<h5 style='color:#10b981;'>📊 Market Monitor</h5>", unsafe_allow_html=True)
    
    # MARKET OVERVIEW DENGAN CLICK-TO-VIEW
    market_overview = '''
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {
      "colorTheme": "dark",
      "dateRange": "12M",
      "showChart": false,
      "locale": "en",
      "width": "100%",
      "height": "800",
      "isTransparent": true,
      "showSymbolLogo": true,
      "tabs": [
        {
          "title": "Crypto",
          "symbols": [
            {"s": "BINANCE:BTCUSDT"},
            {"s": "BINANCE:ETHUSDT"},
            {"s": "BINANCE:SOLUSDT"},
            {"s": "BINANCE:BNBUSDT"},
            {"s": "BINANCE:XRPUSDT"},
            {"s": "BINANCE:DOGEUSDT"},
            {"s": "BINANCE:ADAUSDT"}
          ]
        }
      ]
    }
      </script>
    </div>
    '''
    components.html(market_overview, height=810)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # CHART UTAMA
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("<h5 style='color:#10b981;'>📈 Analysis Chart</h5>", unsafe_allow_html=True)
    
    # Widget Chart yang mendukung "Symbol Change"
    tv_chart = '''
    <div id="tradingview_locked"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "width": "100%",
      "height": 500,
      "symbol": "BINANCE:BTCUSDT",
      "interval": "1",
      "timezone": "Asia/Jakarta",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_locked"
    });
    </script>
    '''
    components.html(tv_chart, height=510)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")

    # TECHNICAL GAUGE (Ikut ter-update)
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("<h5 style='color:#10b981;'>🛡️ Technical Indicators</h5>", unsafe_allow_html=True)
    
    technical_gauge = '''
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {
      "interval": "1m",
      "width": "100%",
      "isTransparent": true,
      "height": "280",
      "symbol": "BINANCE:BTCUSDT",
      "showIntervalTabs": true,
      "locale": "en",
      "colorTheme": "dark"
    }
      </script>
    </div>
    '''
    components.html(technical_gauge, height=290)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#475569; font-size:12px; margin-top:20px;'>FIXED VERSION - READY TO TRADE</div>", unsafe_allow_html=True)
