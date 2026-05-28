import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="StockIQ Pro — Screener IA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.stApp { background: #050810 !important; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px !important; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99,179,237,0.2); }
    50% { box-shadow: 0 0 40px rgba(99,179,237,0.5); }
}
@keyframes countUp {
    from { opacity: 0; transform: scale(0.5); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes borderFlow {
    0% { border-color: #1e3a5f; }
    50% { border-color: #3182ce; }
    100% { border-color: #1e3a5f; }
}
@keyframes floatBadge {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}

.hero-wrapper {
    background: linear-gradient(160deg, #050810 0%, #0a1628 40%, #050d1f 100%);
    border: 1px solid #1a2f50;
    border-radius: 24px;
    padding: 60px 48px;
    margin: 20px 0 32px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
    animation: fadeInDown 0.8s ease-out;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -100px; left: -100px; right: -100px; bottom: -100px;
    background: radial-gradient(ellipse at 50% 0%, rgba(49,130,206,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #3182ce, transparent);
    animation: shimmer 3s infinite;
    background-size: 200% auto;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(49,130,206,0.1);
    border: 1px solid rgba(49,130,206,0.35);
    color: #63b3ed;
    padding: 8px 20px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 28px;
    animation: floatBadge 3s ease-in-out infinite;
}
.badge-dot {
    width: 6px; height: 6px;
    background: #63b3ed;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

.hero-title {
    font-size: 64px;
    font-weight: 900;
    background: linear-gradient(135deg, #fff 0%, #90cdf4 40%, #4299e1 70%, #2b6cb0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 16px 0;
    line-height: 1.05;
    letter-spacing: -2px;
}
.hero-title span {
    background: linear-gradient(135deg, #63b3ed, #4299e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    color: #4a6080;
    font-size: 18px;
    font-weight: 400;
    margin: 0 0 40px 0;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

.hero-stats {
    display: flex;
    justify-content: center;
    gap: 48px;
    flex-wrap: wrap;
    padding-top: 32px;
    border-top: 1px solid #0f1e35;
}
.hero-stat { text-align: center; }
.hero-stat-value {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #4299e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: countUp 0.6s ease-out backwards;
}
.hero-stat-label {
    font-size: 11px;
    color: #2d3f5a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
    font-weight: 600;
}

.glass-card {
    background: rgba(10,20,40,0.8);
    backdrop-filter: blur(20px);
    border: 1px solid #1a2f50;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    animation: fadeInUp 0.6s ease-out backwards;
    transition: border-color 0.3s, transform 0.2s;
}
.glass-card:hover {
    border-color: #2b4a7a;
    transform: translateY(-1px);
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 24px 0;
}
.metric-item {
    background: #080f1e;
    border: 1px solid #1a2f50;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    animation: fadeInUp 0.5s ease-out backwards;
    transition: all 0.3s;
}
.metric-item:hover {
    border-color: #3182ce;
    animation: glow 2s infinite;
}
.metric-num {
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 8px;
}
.metric-lbl {
    font-size: 12px;
    color: #2d4a6a;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

.stock-row {
    background: #070d1a;
    border: 1px solid #111d30;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 10px;
    transition: all 0.25s;
    animation: fadeInUp 0.4s ease-out backwards;
    cursor: pointer;
}
.stock-row:hover {
    background: #0a1525;
    border-color: #2563a8;
    transform: translateX(4px);
}

.verdict-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.v-green { background: rgba(72,187,120,0.12); color: #68d391; border: 1px solid rgba(72,187,120,0.25); }
.v-yellow { background: rgba(246,173,85,0.12); color: #f6ad55; border: 1px solid rgba(246,173,85,0.25); }
.v-orange { background: rgba(237,100,74,0.12); color: #fc8181; border: 1px solid rgba(237,100,74,0.25); }

.score-bar-bg {
    background: #0f1a2e;
    border-radius: 6px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.score-bar-fill {
    height: 8px;
    border-radius: 6px;
    background: linear-gradient(90deg, #2b6cb0, #63b3ed, #90cdf4);
    transition: width 1s ease-out;
    box-shadow: 0 0 10px rgba(99,179,237,0.4);
}

.insight-box {
    background: linear-gradient(135deg, rgba(43,108,176,0.06), rgba(99,179,237,0.03));
    border: 1px solid rgba(43,108,176,0.2);
    border-left: 3px solid #3182ce;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
}
.insight-title { color: #63b3ed; font-weight: 700; font-size: 13px; margin-bottom: 4px; }
.insight-text { color: #3a5070; font-size: 13px; line-height: 1.5; }

.tag {
    display: inline-block;
    background: rgba(30,58,100,0.5);
    color: #4a7aaa;
    border: 1px solid #1e3a64;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1a4080 0%, #2563ab 50%, #3182ce 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 32px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    width: 100% !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(49,130,206,0.3) !important;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #2563ab 0%, #3182ce 50%, #4299e1 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(49,130,206,0.5) !important;
}

div[data-testid="stExpander"] summary { padding-left: 16px !important; }
div[data-testid="stExpander"] {
    background: #070d1a !important;
    border: 1px solid #111d30 !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"]:hover { border-color: #2563a8 !important; }

.stProgress > div > div > div { background: linear-gradient(90deg, #1a4080, #3182ce, #63b3ed) !important; }
.stProgress > div > div { background: #0a1525 !important; }

header, footer, #MainMenu { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
  <div class="hero-badge"><span class="badge-dot"></span> Intelligence Artificielle Financière · v2.0</div>
  <div class="hero-title">Stock<span>IQ</span> Pro</div>
  <p class="hero-sub">Le screener institutionnel propulsé par l'IA — analyse 500+ actions selon les méthodes des plus grands investisseurs mondiaux</p>
  <div class="hero-stats">
    <div class="hero-stat"><div class="hero-stat-value">10</div><div class="hero-stat-label">Critères IA</div></div>
    <div class="hero-stat"><div class="hero-stat-value">500+</div><div class="hero-stat-label">Actions scannées</div></div>
    <div class="hero-stat"><div class="hero-stat-value">5</div><div class="hero-stat-label">Marchés mondiaux</div></div>
    <div class="hero-stat"><div class="hero-stat-value">4</div><div class="hero-stat-label">Légendes de l'invest.</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ACCÈS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col_l, col_m, col_r = st.columns([1,2,1])
with col_m:
    st.markdown("### 🔐 Accès Premium")
    code = st.text_input("", placeholder="••••••••••••  Entrez votre code d'accès", type="password", label_visibility="collapsed")
    if code != "MONCODE123":
        if code: st.error("❌ Code incorrect.")
        else: st.info("🔒 Entrez votre code pour accéder au screener.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    st.success("✅ Accès Premium activé — Bienvenue !")
st.markdown('</div>', unsafe_allow_html=True)

# ── GUIDE ─────────────────────────────────────────────────────────────────
with st.expander("📚 Guide d'utilisation & Méthodologie"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""**🎯 Les 10 critères analysés**
1. 📈 Croissance CA >15%/an
2. 💰 Marge Nette >15%
3. 📊 PEG Ratio <2.0 (Lynch)
4. 🛡️ Marge Brute >40%
5. 🏦 Dette/Capitaux <1.0
6. ⭐ ROE >15% (Buffet)
7. 🔮 ROIC >15% (Munger)
8. 💵 FCF Yield >5%
9. ✨ Magic Formula (Greenblatt)
10. 📉 Short Interest <10%""")
    with c2:
        st.markdown("""**📊 Légende des verdicts**

🟢 **FORT POTENTIEL** (8-10/10)
→ Action exceptionnelle à étudier

🟡 **À SURVEILLER** (6-7/10)
→ Bonnes bases, surveiller le prix

🟠 **INTÉRESSANT** (4-5/10)
→ Qualités mais faiblesses notables

🔴 **ÉVITER** (0-3/10)
→ Ne passe pas les filtres""")
    with c3:
        st.markdown("""**⚡ Conseils d'utilisation**

• Lance un scan par marché pour plus de précision
• Score ≥ 7 = action à analyser sérieusement
• Exporte le CSV et croise avec d'autres sources
• Relance chaque semaine pour voir les nouveaux signaux
• ⚠️ Toujours faire ses propres recherches
• Ce n'est pas un conseil financier""")

st.divider()

# ── PARAMÈTRES ────────────────────────────────────────────────────────────
st.markdown("### ⚙️ Paramètres de l'analyse")
col1, col2, col3, col4 = st.columns(4)
with col1:
    market_choice = st.selectbox("🌍 Marché", ["🌐 Tous", "🇺🇸 S&P500", "💻 NASDAQ", "🇪🇺 Europe", "🌏 Asie", "📈 Small Caps"])
with col2:
    min_score = st.slider("🎯 Score min", 1, 10, 5)
with col3:
    speed = st.selectbox("⚡ Profondeur", ["🚀 Rapide (25/marché)", "🔄 Standard (50/marché)", "🔍 Complet (80/marché)"])
with col4:
    sort_by = st.selectbox("📊 Trier par", ["Score (↓)", "Prix (↑)", "Capitalisation (↓)"])

speed_map = {"🚀 Rapide (25/marché)": 25, "🔄 Standard (50/marché)": 50, "🔍 Complet (80/marché)": 80}
limit = speed_map[speed]
market_map = {"🌐 Tous": None, "🇺🇸 S&P500": "sp500", "💻 NASDAQ": "nasdaq",
              "🇪🇺 Europe": "europe", "🌏 Asie": "asia", "📈 Small Caps": "smallcaps"}

THRESHOLDS = {"revenue_growth": 0.15, "net_margin": 0.15, "peg_ratio": 2.0,
              "gross_margin": 0.40, "debt_to_equity": 1.0, "roe": 0.15,
              "roic": 0.15, "fcf_yield": 0.05, "short_interest": 0.10}

def get_tickers(mf, lim):
    sp500 = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","V","UNH","XOM","MA","JNJ",
             "PG","HD","COST","MRK","ABBV","CVX","CRM","WMT","BAC","KO","PEP","AMD","NFLX","ADBE",
             "TMO","LLY","AVGO","ORCL","ACN","IBM","QCOM","TXN","INTU","ISRG","AMAT","LRCX","ADI",
             "REGN","VRTX","GILD","MDLZ","BKNG","ADP","PANW","SNPS","CDNS","MELI","NOW","DDOG",
             "ZS","CRWD","NET","MDB","HUBS","SHOP","SQ","ROKU","ABNB","RBLX","COIN","PLTR","UBER",
             "LYFT","DOCU","ZM","OKTA","TWLO","VEEV","COUP","BILL","GTLB","SMAR","FRSH","BRZE"]
    nasdaq = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","COST","NFLX","AMD","ADBE",
              "QCOM","TXN","INTC","INTU","AMGN","ISRG","SBUX","PYPL","REGN","VRTX","GILD","MDLZ",
              "BKNG","ADP","LULU","PANW","SNPS","CDNS","MELI","ASML","ABNB","WDAY","TEAM","DXCM",
              "IDXX","ILMN","ALGN","SGEN","PCAR","ODFL","FAST","CTAS","PAYX","CPRT","VRSK","ANSS",
              "ZBRA","MPWR","ENTG","LSCC","FORM","CRUS","SWKS","QRVO","MCHP","KLAC","ANET","CDNS"]
    europe = ["AI.PA","AIR.PA","BNP.PA","MC.PA","OR.PA","SAN.PA","TTE.PA","SU.PA","RMS.PA","KER.PA",
              "CAP.PA","ATO.PA","DSY.PA","ENGI.PA","EL.PA","AXA.PA","SGO.PA","VIE.PA","SEB.PA",
              "AZN.L","SHEL.L","HSBA.L","BP.L","GSK.L","RIO.L","ULVR.L","DGE.L","LSEG.L","REL.L",
              "BARC.L","LLOY.L","STAN.L","NWG.L","VOD.L","BT-A.L","TSCO.L","SBRY.L","MKS.L",
              "SAP.DE","SIE.DE","ALV.DE","BMW.DE","BAYN.DE","BAS.DE","VOW3.DE","ADS.DE","LIN.DE",
              "MRK.DE","DTE.DE","RWE.DE","EON.DE","HEN3.DE","MUV2.DE","CBK.DE","DBK.DE","BEI.DE"]
    asia = ["7203.T","9984.T","6861.T","8306.T","7974.T","6758.T","4502.T","6954.T","8035.T",
            "4063.T","9432.T","9433.T","6501.T","6752.T","7267.T","7751.T","4519.T","2914.T",
            "0700.HK","0941.HK","1299.HK","0005.HK","2318.HK","0939.HK","1398.HK","0388.HK",
            "0016.HK","0012.HK","3690.HK","9988.HK","1810.HK","0883.HK","0762.HK","2382.HK"]
    smallcaps = ["CELH","BOOT","TREX","MEDP","AAON","CSWI","ATKR","SPSC","AEIS","KTOS","HLNE",
                 "TGTX","SMAR","YETI","APPF","STEP","BCPC","MGEE","LANC","CRVL","UFPI","FELE",
                 "EXPO","MSGS","GSHD","HALO","VCEL","ACVA","NARI","PRCT","DOMO","ALRM","IIIV",
                 "AMSF","FCFS","COOP","HCKT","MGRC","LKFN","BANF","BOKF","STBA","NBTB","TRMK"]
    markets = []
    if mf in [None,"sp500"]: markets.append((sp500,"S&P500 🇺🇸"))
    if mf in [None,"nasdaq"]: markets.append((nasdaq,"NASDAQ 💻"))
    if mf in [None,"europe"]: markets.append((europe,"EUROPE 🇪🇺"))
    if mf in [None,"asia"]: markets.append((asia,"ASIE 🌏"))
    if mf in [None,"smallcaps"]: markets.append((smallcaps,"SMALL CAPS 📈"))
    return [(t[:lim], m) for t, m in markets]

def get_price(info):
    for k in ["currentPrice","regularMarketPrice","previousClose","open"]:
        v = info.get(k)
        if v and v > 0: return v
    return None

def analyze_stock(ticker, market):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5: return None
        price = get_price(info)
        if not price: return None
        r = {"ticker": ticker, "name": (info.get("longName") or info.get("shortName") or ticker)[:45],
             "market": market, "sector": info.get("sector","N/A"), "industry": info.get("industry","N/A"),
             "price": price, "market_cap": info.get("marketCap"), "pe": info.get("trailingPE"),
             "criteria": {}, "score": 0}
        s = 0
        def c(k, lbl, val, passed, thr):
            r["criteria"][k] = {"label":lbl,"value":val,"passed":passed,"threshold":thr}
            return 1 if passed else 0

        # 1
        try:
            fin = stock.financials
            if fin is not None and not fin.empty and "Total Revenue" in fin.index:
                rev = fin.loc["Total Revenue"].dropna()
                if len(rev)>=2 and rev.iloc[-1]>0:
                    cagr=(rev.iloc[0]/rev.iloc[-1])**(1/max(len(rev)-1,1))-1
                    s+=c("rv","📈 Croissance CA",f"{cagr*100:.1f}%",cagr>=0.15,">15%/an")
                else: s+=c("rv","📈 Croissance CA","N/A",False,">15%/an")
            else: s+=c("rv","📈 Croissance CA","N/A",False,">15%/an")
        except: s+=c("rv","📈 Croissance CA","N/A",False,">15%/an")

        # 2
        try:
            nm=info.get("profitMargins")
            if nm is not None: s+=c("nm","💰 Marge Nette",f"{nm*100:.1f}%",nm>=0.15,">15%")
            else: s+=c("nm","💰 Marge Nette","N/A",False,">15%")
        except: s+=c("nm","💰 Marge Nette","N/A",False,">15%")

        # 3
        try:
            peg=info.get("pegRatio")
            if peg and peg>0: s+=c("peg","📊 PEG (Lynch)",f"{peg:.2f}",peg<2.0,"<2.0")
            else: s+=c("peg","📊 PEG (Lynch)","N/A",False,"<2.0")
        except: s+=c("peg","📊 PEG (Lynch)","N/A",False,"<2.0")

        # 4
        try:
            gm=info.get("grossMargins")
            if gm is not None: s+=c("gm","🛡️ Avantage Compétitif",f"{gm*100:.1f}%",gm>=0.40,">40%")
            else: s+=c("gm","🛡️ Avantage Compétitif","N/A",False,">40%")
        except: s+=c("gm","🛡️ Avantage Compétitif","N/A",False,">40%")

        # 5
        try:
            de=info.get("debtToEquity")
            if de is not None:
                der=de/100
                s+=c("de","🏦 Dette/Capitaux",f"{der:.2f}",der<1.0,"<1.0")
            else: s+=c("de","🏦 Dette/Capitaux","N/A",False,"<1.0")
        except: s+=c("de","🏦 Dette/Capitaux","N/A",False,"<1.0")

        # 6
        try:
            roe=info.get("returnOnEquity")
            if roe is not None: s+=c("roe","⭐ ROE (Buffet)",f"{roe*100:.1f}%",roe>=0.15,">15%")
            else: s+=c("roe","⭐ ROE (Buffet)","N/A",False,">15%")
        except: s+=c("roe","⭐ ROE (Buffet)","N/A",False,">15%")

        # 7
        try:
            roa=info.get("returnOnAssets")
            if roa is not None: s+=c("roic","🔮 ROIC (Munger)",f"{roa*100:.1f}%",roa>=0.15,">15%")
            else: s+=c("roic","🔮 ROIC (Munger)","N/A",False,">15%")
        except: s+=c("roic","🔮 ROIC (Munger)","N/A",False,">15%")

        # 8
        try:
            fcf=info.get("freeCashflow"); cap=info.get("marketCap")
            if fcf and cap and cap>0:
                fy=fcf/cap
                s+=c("fcf","💵 FCF Yield",f"{fy*100:.1f}%",fy>=0.05,">5%")
            else: s+=c("fcf","💵 FCF Yield","N/A",False,">5%")
        except: s+=c("fcf","💵 FCF Yield","N/A",False,">5%")

        # 9
        try:
            pe=info.get("trailingPE"); roe_v=info.get("returnOnEquity")
            if pe and pe>0 and roe_v:
                magic=(1/pe*100)+(roe_v*100)
                s+=c("mf","✨ Magic Formula",f"Score {magic:.1f}",magic>=25,"Score >25")
            else: s+=c("mf","✨ Magic Formula","N/A",False,"Score >25")
        except: s+=c("mf","✨ Magic Formula","N/A",False,"Score >25")

        # 10
        try:
            so=info.get("sharesOutstanding"); ss=info.get("sharesShort")
            if so and ss and so>0:
                sp_pct=ss/so
                s+=c("si","📉 Short Interest",f"{sp_pct*100:.1f}%",sp_pct<0.10,"<10%")
            else: s+=c("si","📉 Short Interest","N/A",False,"<10%")
        except: s+=c("si","📉 Short Interest","N/A",False,"<10%")

        r["score"]=s
        if s>=8: r["verdict"]="🟢 FORT POTENTIEL"
        elif s>=6: r["verdict"]="🟡 À SURVEILLER"
        elif s>=4: r["verdict"]="🟠 INTÉRESSANT"
        else: r["verdict"]="🔴 ÉVITER"
        return r
    except: return None

def fmt_cap(c):
    if not c: return "N/A"
    if c>=1e12: return f"${c/1e12:.1f}T"
    if c>=1e9: return f"${c/1e9:.1f}B"
    return f"${c/1e6:.0f}M"

if st.button("🚀 Lancer l'analyse IA", use_container_width=True):
    mf = market_map[market_choice]
    markets_data = get_tickers(mf, limit)
    total = sum(len(t) for t,_ in markets_data)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">🤖 Analyse IA en cours</div>
        <div class="insight-text">Scan de {total} actions · Méthodes Buffet · Lynch · Munger · Greenblatt</div>
    </div>""", unsafe_allow_html=True)

    progress = st.progress(0)
    status = st.empty()
    all_results = []
    counter = 0

    for tickers, market_name in markets_data:
        for ticker in tickers:
            counter += 1
            pct = counter/total
            status.markdown(f"**⏳ `{ticker}`** — {counter}/{total} actions analysées &nbsp;&nbsp; `{'█'*int(pct*20)}{'░'*(20-int(pct*20))}`")
            progress.progress(pct)
            result = analyze_stock(ticker, market_name)
            if result: all_results.append(result)
            time.sleep(0.4)

    progress.empty()
    status.empty()

    qualified = [r for r in all_results if r["score"] >= min_score]
    strong = [r for r in all_results if r["score"] >= 8]
    perfect = [r for r in all_results if r["score"] == 10]

    if sort_by == "Score (↓)": qualified.sort(key=lambda x: x["score"], reverse=True)
    elif sort_by == "Prix (↑)": qualified.sort(key=lambda x: x["price"])
    elif sort_by == "Capitalisation (↓)": qualified.sort(key=lambda x: x.get("market_cap") or 0, reverse=True)

    st.divider()
    st.markdown(f"## 📊 Résultats · {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-item"><div class="metric-num" style="color:#4a7aaa">{len(all_results)}</div><div class="metric-lbl">Analysées</div></div>
        <div class="metric-item"><div class="metric-num" style="color:#f6ad55">{len(qualified)}</div><div class="metric-lbl">Score ≥ {min_score}/10</div></div>
        <div class="metric-item"><div class="metric-num" style="color:#68d391">{len(strong)}</div><div class="metric-lbl">FORT POTENTIEL 🔥</div></div>
        <div class="metric-item"><div class="metric-num" style="color:#fc8181">{len(perfect)}</div><div class="metric-lbl">Score Parfait ⭐</div></div>
    </div>
    """, unsafe_allow_html=True)

    # GRAPHIQUES
    if all_results:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            scores = [r["score"] for r in all_results]
            fig1 = go.Figure()
            fig1.add_trace(go.Histogram(
                x=scores, nbinsx=10,
                marker=dict(
                    color=scores,
                    colorscale=[[0,'#1a3a6a'],[0.5,'#2563ab'],[1,'#63b3ed']],
                    line=dict(color='#050810', width=1)
                ),
                hovertemplate='Score %{x}: %{y} actions<extra></extra>'
            ))
            fig1.update_layout(
                title=dict(text="Distribution des scores", font=dict(color='#63b3ed', size=14)),
                paper_bgcolor='#070d1a', plot_bgcolor='#070d1a',
                font=dict(color='#4a6080'),
                xaxis=dict(title="Score /10", gridcolor='#0f1e35', color='#4a6080'),
                yaxis=dict(title="Nombre d'actions", gridcolor='#0f1e35', color='#4a6080'),
                height=280, margin=dict(t=40, b=40, l=40, r=20)
            )
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        with col_g2:
            if qualified:
                top10 = sorted(qualified, key=lambda x: x["score"], reverse=True)[:10]
                colors = ['#68d391' if r["score"]>=8 else '#f6ad55' if r["score"]>=6 else '#fc8181' for r in top10]
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=[r["ticker"] for r in top10],
                    y=[r["score"] for r in top10],
                    marker=dict(color=colors, line=dict(color='#050810', width=1)),
                    text=[f"{r['score']}/10" for r in top10],
                    textposition='outside',
                    textfont=dict(color='#63b3ed', size=11),
                    hovertemplate='%{x}: %{y}/10<extra></extra>'
                ))
                fig2.update_layout(
                    title=dict(text="Top 10 actions qualifiées", font=dict(color='#63b3ed', size=14)),
                    paper_bgcolor='#070d1a', plot_bgcolor='#070d1a',
                    font=dict(color='#4a6080'),
                    xaxis=dict(gridcolor='#0f1e35', color='#4a6080'),
                    yaxis=dict(range=[0,11], gridcolor='#0f1e35', color='#4a6080'),
                    height=280, margin=dict(t=40, b=40, l=40, r=20)
                )
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        # Répartition par secteur
        if qualified:
            sectors = {}
            for r in qualified:
                s = r.get("sector","N/A")
                sectors[s] = sectors.get(s, 0) + 1
            fig3 = go.Figure(go.Pie(
                labels=list(sectors.keys()),
                values=list(sectors.values()),
                hole=0.6,
                marker=dict(colors=px.colors.sequential.Blues_r[:len(sectors)],
                            line=dict(color='#050810', width=2)),
                hovertemplate='%{label}: %{value} actions (%{percent})<extra></extra>'
            ))
            fig3.update_layout(
                title=dict(text="Répartition par secteur", font=dict(color='#63b3ed', size=14)),
                paper_bgcolor='#070d1a', font=dict(color='#4a6080'),
                height=260, margin=dict(t=40, b=20, l=0, r=0),
                showlegend=True,
                legend=dict(font=dict(color='#4a6080', size=11))
            )
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    # RÉSULTATS
    if qualified:
        st.divider()
        st.markdown(f"## 🏆 {len(qualified)} Actions qualifiées")

        for i, r in enumerate(qualified):
            score_pct = r["score"] * 10
            vc = "v-green" if r["score"]>=8 else "v-yellow" if r["score"]>=6 else "v-orange"

            with st.expander(f"{r['verdict']}  ·  {r['ticker']}  ·  {r['name']}  ·  {r['score']}/10"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prix", f"${r['price']:.2f}")
                c2.metric("Capitalisation", fmt_cap(r.get("market_cap")))
                c3.metric("Secteur", r.get("sector","N/A")[:20])
                c4.metric("Score", f"{r['score']}/10 ⭐")

                st.markdown(f"""
                <div style="margin: 12px 0 4px 0; color: #2d4a6a; font-size:12px; font-weight:600">SCORE GLOBAL</div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width:{score_pct}%"></div>
                </div>
                <div style="color:#2d4a6a;font-size:11px;margin-top:6px">{r['score']}/10 critères validés · {score_pct}% de conformité</div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                crit_data = []
                for crit in r["criteria"].values():
                    crit_data.append({"": "✅" if crit["passed"] else "❌",
                                      "Critère": crit["label"],
                                      "Valeur": crit["value"],
                                      "Seuil requis": crit["threshold"]})
                st.dataframe(pd.DataFrame(crit_data), use_container_width=True, hide_index=True)

                insight = ("🔥 Action exceptionnelle selon nos 10 critères institutionnels. À analyser en priorité avec une étude fondamentale approfondie avant tout investissement." if r['score']>=8 else
                           "💡 Bonnes fondamentales. Surveille cette action et attends un point d'entrée optimal (pullback ou consolidation)." if r['score']>=6 else
                           "⚠️ Qualités intéressantes mais quelques faiblesses. À surveiller sur le long terme.")
                st.markdown(f"""<div class="insight-box"><div class="insight-title">💡 Analyse IA</div><div class="insight-text">{insight}</div></div>""", unsafe_allow_html=True)

        st.divider()
        rows = [{"Verdict":r["verdict"],"Ticker":r["ticker"],"Nom":r["name"],"Marché":r["market"],
                 "Secteur":r.get("sector","N/A"),"Prix":f"${r['price']:.2f}",
                 "Cap":fmt_cap(r.get("market_cap")),"Score":f"{r['score']}/10"}
                for r in qualified]
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        st.download_button("📁 Exporter tous les résultats (CSV)", csv,
                          f"stockiq_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                          "text/csv", use_container_width=True)
    else:
        st.warning(f"Aucune action avec un score ≥ {min_score}/10. Baisse le score minimum ou change de marché.")

    st.markdown("""<div style="text-align:center;color:#1a2f4a;font-size:11px;margin-top:48px;padding:20px 0;border-top:1px solid #0a1525">
    ⚠️ StockIQ Pro est un outil d'analyse informatif uniquement — Pas un conseil en investissement financier<br>
    Les performances passées ne garantissent pas les résultats futurs · Investir comporte des risques de perte
    </div>""", unsafe_allow_html=True)
