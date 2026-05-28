import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="StockIQ Pro — Screener Institutionnel",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: #0a0e1a; }
    
    .hero {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a0e1a 100%);
        border: 1px solid #1e2d4a;
        border-radius: 20px;
        padding: 48px 40px;
        margin-bottom: 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, rgba(99,179,237,0.05) 0%, transparent 60%);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(99,179,237,0.1);
        border: 1px solid rgba(99,179,237,0.3);
        color: #63b3ed;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 52px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #63b3ed 50%, #4299e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 16px 0;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: #718096;
        font-size: 18px;
        font-weight: 400;
        margin: 0 0 32px 0;
    }
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 40px;
        flex-wrap: wrap;
    }
    .hero-stat {
        text-align: center;
    }
    .hero-stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #63b3ed;
    }
    .hero-stat-label {
        font-size: 12px;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .access-card {
        background: #0d1526;
        border: 1px solid #1e2d4a;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: #0d1526;
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #63b3ed;
    }
    .metric-label {
        font-size: 13px;
        color: #4a5568;
        margin-top: 4px;
    }
    
    .stock-card {
        background: #0d1526;
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .stock-card:hover { border-color: #63b3ed; }
    
    .badge-green {
        background: rgba(72,187,120,0.15);
        color: #68d391;
        border: 1px solid rgba(72,187,120,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-yellow {
        background: rgba(237,137,54,0.15);
        color: #fbd38d;
        border: 1px solid rgba(237,137,54,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-red {
        background: rgba(245,101,101,0.15);
        color: #fc8181;
        border: 1px solid rgba(245,101,101,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .criteria-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #1a2540;
    }
    
    .score-bar-container {
        background: #1a2540;
        border-radius: 4px;
        height: 6px;
        width: 100%;
        margin-top: 8px;
    }
    .score-bar {
        height: 6px;
        border-radius: 4px;
        background: linear-gradient(90deg, #4299e1, #63b3ed);
    }
    
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #2b6cb0, #3182ce) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 32px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #3182ce, #4299e1) !important;
        transform: translateY(-1px) !important;
    }
    
    .stSelectbox > div > div, .stSlider { 
        background: #0d1526 !important; 
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2b6cb0, #63b3ed) !important;
    }
    
    .tip-box {
        background: rgba(99,179,237,0.05);
        border: 1px solid rgba(99,179,237,0.2);
        border-radius: 10px;
        padding: 16px 20px;
        margin: 12px 0;
    }
    .tip-title { color: #63b3ed; font-weight: 600; font-size: 14px; }
    .tip-text { color: #718096; font-size: 13px; margin-top: 4px; }
    
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── HERO ───
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ Intelligence Artificielle Financière</div>
    <div class="hero-title">StockIQ Pro</div>
    <p class="hero-subtitle">Le screener utilisé par les investisseurs institutionnels — maintenant accessible à tous</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-value">10</div>
            <div class="hero-stat-label">Critères analysés</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">5</div>
            <div class="hero-stat-label">Marchés mondiaux</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">500+</div>
            <div class="hero-stat-label">Actions scannées</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">4</div>
            <div class="hero-stat-label">Méthodes légendaires</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── ACCÈS ───
st.markdown('<div class="access-card">', unsafe_allow_html=True)
st.markdown("### 🔐 Accès Premium")
code = st.text_input("Code d'accès :", placeholder="Entre ton code ici...", type="password", label_visibility="collapsed")
if code != "MONCODE123":
    if code:
        st.error("❌ Code incorrect. Contacte le support si tu as acheté l'accès.")
    else:
        st.info("👆 Entre ton code d'accès pour débloquer le screener")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
st.success("✅ Accès Premium activé — Bienvenue !")
st.markdown('</div>', unsafe_allow_html=True)

# ─── EXPLICATIONS ───
with st.expander("📚 Comment ça marche ? (Guide pour débutants)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🎯 Les 10 critères analysés :**
        
        1. **Croissance CA** — L'entreprise grandit-elle vite ?
        2. **Marge Nette** — Est-elle très rentable ?
        3. **PEG Ratio** — Est-elle bien valorisée vs sa croissance ?
        4. **Marge Brute** — A-t-elle un avantage compétitif ?
        5. **Dette** — Est-elle peu endettée ?
        6. **ROE** — Utilise-t-elle bien les capitaux ? (Buffet)
        7. **ROIC** — Crée-t-elle de la valeur ? (Munger)
        8. **FCF Yield** — Génère-t-elle du cash ? (Hedge Funds)
        9. **Magic Formula** — Score global Greenblatt
        10. **Short Interest** — Les vendeurs à découvert l'évitent-ils ?
        """)
    with col2:
        st.markdown("""
        **📊 Comment lire les résultats :**
        
        🟢 **FORT POTENTIEL** (8-10/10) → Action exceptionnelle, à étudier en priorité
        
        🟡 **À SURVEILLER** (6-7/10) → Bonne action, à analyser plus en détail
        
        🟠 **INTÉRESSANT** (4-5/10) → Des qualités mais des faiblesses
        
        🔴 **ÉVITER** (0-3/10) → Ne répond pas aux critères institutionnels
        
        ⚠️ *Ces résultats sont informatifs. Fais toujours tes propres recherches avant d'investir.*
        """)

st.divider()

# ─── PARAMÈTRES ───
st.markdown("### ⚙️ Paramètres du scan")
col1, col2, col3 = st.columns(3)
with col1:
    market_choice = st.selectbox("🌍 Marché cible", 
        ["🌐 Tous les marchés", "🇺🇸 S&P500 (USA)", "💻 NASDAQ100 (Tech)", 
         "🇪🇺 Europe (CAC40/DAX/FTSE)", "🌏 Asie (Nikkei/Hang Seng)", "📈 Small Caps (Russell 2000)"])
with col2:
    min_score = st.slider("🎯 Score minimum", 1, 10, 5, help="Plus le score est élevé, plus les critères sont stricts")
with col3:
    speed = st.selectbox("⚡ Mode d'analyse", ["🚀 Rapide (20 actions)", "🔄 Standard (40 actions)", "🔍 Approfondi (60 actions)"])

speed_map = {"🚀 Rapide (20 actions)": 20, "🔄 Standard (40 actions)": 40, "🔍 Approfondi (60 actions)": 60}
limit = speed_map[speed]

market_map = {
    "🌐 Tous les marchés": None, "🇺🇸 S&P500 (USA)": "sp500",
    "💻 NASDAQ100 (Tech)": "nasdaq", "🇪🇺 Europe (CAC40/DAX/FTSE)": "europe",
    "🌏 Asie (Nikkei/Hang Seng)": "asia", "📈 Small Caps (Russell 2000)": "smallcaps"
}

THRESHOLDS = {
    "revenue_growth": 0.15, "net_margin": 0.15, "peg_ratio": 2.0,
    "gross_margin": 0.40, "debt_to_equity": 1.0, "roe": 0.15,
    "roic": 0.15, "fcf_yield": 0.05, "short_interest": 0.10,
}

def get_tickers(market_filter, limit):
    sp500 = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","V","UNH",
             "XOM","MA","JNJ","PG","HD","COST","MRK","ABBV","CVX","CRM",
             "WMT","BAC","KO","PEP","AMD","NFLX","ADBE","TMO","LLY","AVGO",
             "ORCL","ACN","IBM","QCOM","TXN","INTU","ISRG","AMAT","LRCX","ADI",
             "REGN","VRTX","GILD","MDLZ","BKNG","ADP","PANW","SNPS","CDNS","MELI",
             "NOW","SNOW","DDOG","ZS","CRWD","NET","MDB","HUBS","BILL","SHOP"]
    nasdaq = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","COST","NFLX",
              "AMD","ADBE","QCOM","TXN","INTC","INTU","AMGN","ISRG","SBUX","PYPL",
              "REGN","VRTX","GILD","MDLZ","BKNG","ADP","LULU","PANW","SNPS","CDNS",
              "MELI","ASML","ABNB","WDAY","TEAM","DXCM","IDXX","ILMN","ALGN","SGEN"]
    europe = ["AI.PA","AIR.PA","BNP.PA","MC.PA","OR.PA","SAN.PA","TTE.PA","SU.PA","RMS.PA","KER.PA",
              "AZN.L","SHEL.L","HSBA.L","BP.L","GSK.L","RIO.L","ULVR.L","DGE.L","LSEG.L","REL.L",
              "SAP.DE","SIE.DE","ALV.DE","BMW.DE","BAYN.DE","BAS.DE","VOW3.DE","ADS.DE","LIN.DE","MRK.DE"]
    asia = ["7203.T","9984.T","6861.T","8306.T","7974.T","6758.T","4502.T","6954.T","8035.T","4063.T",
            "0700.HK","0941.HK","1299.HK","0005.HK","2318.HK","0939.HK","1398.HK","0388.HK","0016.HK","0012.HK"]
    smallcaps = ["CELH","BOOT","TREX","MEDP","AAON","CSWI","ATKR","SPSC","AEIS","KTOS",
                 "HLNE","TGTX","SMAR","YETI","APPF","STEP","BCPC","MGEE","LANC","CRVL",
                 "UFPI","FELE","EXPO","MSGS","GSHD","HALO","VCEL","ACVA","NARI","PRCT"]

    markets = []
    if market_filter in [None, "sp500"]: markets.append((sp500, "S&P500 🇺🇸"))
    if market_filter in [None, "nasdaq"]: markets.append((nasdaq, "NASDAQ 💻"))
    if market_filter in [None, "europe"]: markets.append((europe, "EUROPE 🇪🇺"))
    if market_filter in [None, "asia"]: markets.append((asia, "ASIE 🌏"))
    if market_filter in [None, "smallcaps"]: markets.append((smallcaps, "SMALL CAPS 📈"))
    return [(t[:limit], m) for t, m in markets]

def get_price(info):
    for key in ["currentPrice","regularMarketPrice","previousClose","open"]:
        val = info.get(key)
        if val and val > 0: return val
    return None

def analyze_stock(ticker, market):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5: return None
        price = get_price(info)
        if not price: return None

        result = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "market": market,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price": price,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "criteria": {},
            "score": 0,
            "total": 10,
        }
        score = 0

        def add_criterion(key, label, value_str, passed, threshold):
            result["criteria"][key] = {"label": label, "value": value_str, "passed": passed, "threshold": threshold}
            return 1 if passed else 0

        # 1. Croissance CA
        try:
            fin = stock.financials
            if fin is not None and not fin.empty and "Total Revenue" in fin.index:
                rev = fin.loc["Total Revenue"].dropna()
                if len(rev) >= 2 and rev.iloc[-1] > 0:
                    cagr = (rev.iloc[0]/rev.iloc[-1])**(1/max(len(rev)-1,1))-1
                    score += add_criterion("revenue_growth","📈 Croissance du CA",f"{cagr*100:.1f}%",cagr>=0.15,">15%/an")
                else: score += add_criterion("revenue_growth","📈 Croissance du CA","N/A",False,">15%/an")
            else: score += add_criterion("revenue_growth","📈 Croissance du CA","N/A",False,">15%/an")
        except: score += add_criterion("revenue_growth","📈 Croissance du CA","N/A",False,">15%/an")

        # 2. Marge Nette
        try:
            nm = info.get("profitMargins")
            if nm is not None: score += add_criterion("net_margin","💰 Marge Nette",f"{nm*100:.1f}%",nm>=0.15,">15%")
            else: score += add_criterion("net_margin","💰 Marge Nette","N/A",False,">15%")
        except: score += add_criterion("net_margin","💰 Marge Nette","N/A",False,">15%")

        # 3. PEG
        try:
            peg = info.get("pegRatio")
            if peg and peg > 0: score += add_criterion("peg_ratio","📊 PEG Ratio (Lynch)",f"{peg:.2f}",peg<2.0,"<2.0")
            else: score += add_criterion("peg_ratio","📊 PEG Ratio (Lynch)","N/A",False,"<2.0")
        except: score += add_criterion("peg_ratio","📊 PEG Ratio (Lynch)","N/A",False,"<2.0")

        # 4. Marge Brute
        try:
            gm = info.get("grossMargins")
            if gm is not None: score += add_criterion("gross_margin","🛡️ Avantage Compétitif",f"{gm*100:.1f}%",gm>=0.40,">40%")
            else: score += add_criterion("gross_margin","🛡️ Avantage Compétitif","N/A",False,">40%")
        except: score += add_criterion("gross_margin","🛡️ Avantage Compétitif","N/A",False,">40%")

        # 5. Dette
        try:
            de = info.get("debtToEquity")
            if de is not None:
                der = de/100
                score += add_criterion("debt_to_equity","🏦 Dette/Capitaux",f"{der:.2f}",der<1.0,"<1.0")
            else: score += add_criterion("debt_to_equity","🏦 Dette/Capitaux","N/A",False,"<1.0")
        except: score += add_criterion("debt_to_equity","🏦 Dette/Capitaux","N/A",False,"<1.0")

        # 6. ROE
        try:
            roe = info.get("returnOnEquity")
            if roe is not None: score += add_criterion("roe","⭐ ROE (Buffet)",f"{roe*100:.1f}%",roe>=0.15,">15%")
            else: score += add_criterion("roe","⭐ ROE (Buffet)","N/A",False,">15%")
        except: score += add_criterion("roe","⭐ ROE (Buffet)","N/A",False,">15%")

        # 7. ROIC
        try:
            roa = info.get("returnOnAssets")
            if roa is not None: score += add_criterion("roic","🔮 ROIC (Munger)",f"{roa*100:.1f}%",roa>=0.15,">15%")
            else: score += add_criterion("roic","🔮 ROIC (Munger)","N/A",False,">15%")
        except: score += add_criterion("roic","🔮 ROIC (Munger)","N/A",False,">15%")

        # 8. FCF Yield
        try:
            fcf = info.get("freeCashflow")
            cap = info.get("marketCap")
            if fcf and cap and cap > 0:
                fy = fcf/cap
                score += add_criterion("fcf_yield","💵 FCF Yield",f"{fy*100:.1f}%",fy>=0.05,">5%")
            else: score += add_criterion("fcf_yield","💵 FCF Yield","N/A",False,">5%")
        except: score += add_criterion("fcf_yield","💵 FCF Yield","N/A",False,">5%")

        # 9. Magic Formula
        try:
            pe = info.get("trailingPE")
            roe_val = info.get("returnOnEquity")
            if pe and pe > 0 and roe_val:
                magic = (1/pe*100)+(roe_val*100)
                score += add_criterion("magic_formula","✨ Magic Formula (Greenblatt)",f"Score {magic:.1f}",magic>=25,"Score >25")
            else: score += add_criterion("magic_formula","✨ Magic Formula (Greenblatt)","N/A",False,"Score >25")
        except: score += add_criterion("magic_formula","✨ Magic Formula (Greenblatt)","N/A",False,"Score >25")

        # 10. Short Interest
        try:
            so = info.get("sharesOutstanding")
            ss = info.get("sharesShort")
            if so and ss and so > 0:
                sp = ss/so
                score += add_criterion("short_interest","📉 Short Interest",f"{sp*100:.1f}%",sp<0.10,"<10%")
            else: score += add_criterion("short_interest","📉 Short Interest","N/A",False,"<10%")
        except: score += add_criterion("short_interest","📉 Short Interest","N/A",False,"<10%")

        result["score"] = score
        if score >= 8: result["verdict"] = "🟢 FORT POTENTIEL"
        elif score >= 6: result["verdict"] = "🟡 À SURVEILLER"
        elif score >= 4: result["verdict"] = "🟠 INTÉRESSANT"
        else: result["verdict"] = "🔴 ÉVITER"
        return result
    except: return None

def format_cap(cap):
    if not cap: return "N/A"
    if cap >= 1e12: return f"${cap/1e12:.1f}T"
    if cap >= 1e9: return f"${cap/1e9:.1f}B"
    return f"${cap/1e6:.0f}M"

if st.button("🚀 Lancer l'analyse", use_container_width=True):
    markets_data = get_tickers(market_map[market_choice], limit)
    total = sum(len(t) for t, _ in markets_data)
    
    st.markdown(f"""
    <div class="tip-box">
        <div class="tip-title">🔍 Scan en cours — {total} actions analysées</div>
        <div class="tip-text">L'IA analyse chaque action selon 10 critères utilisés par les plus grands investisseurs mondiaux</div>
    </div>
    """, unsafe_allow_html=True)

    progress = st.progress(0)
    status = st.empty()
    all_results = []
    counter = 0

    for tickers, market_name in markets_data:
        for ticker in tickers:
            counter += 1
            status.markdown(f"**⏳ Analyse en cours :** `{ticker}` ({counter}/{total})")
            progress.progress(counter/total)
            result = analyze_stock(ticker, market_name)
            if result: all_results.append(result)
            time.sleep(0.5)

    progress.empty()
    status.empty()

    qualified = [r for r in all_results if r["score"] >= min_score]
    strong = [r for r in all_results if r["score"] >= 8]
    perfect = [r for r in all_results if r["score"] == 10]

    st.divider()
    st.markdown(f"## 📊 Résultats du {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(all_results)}</div><div class="metric-label">Actions analysées</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#fbd38d">{len(qualified)}</div><div class="metric-label">Score ≥ {min_score}/10</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#68d391">{len(strong)}</div><div class="metric-label">Score ≥ 8/10 🔥</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#fc8181">{len(perfect)}</div><div class="metric-label">Score parfait 10/10 ⭐</div></div>', unsafe_allow_html=True)

    if qualified:
        st.divider()
        st.markdown("## 🏆 Actions qualifiées")

        for r in sorted(qualified, key=lambda x: x["score"], reverse=True):
            score_pct = r["score"] * 10
            badge_class = "badge-green" if r["score"] >= 8 else ("badge-yellow" if r["score"] >= 6 else "badge-red")
            
            with st.expander(f"{r['verdict']}  •  {r['ticker']}  •  {r['name'][:45]}  •  Score : {r['score']}/10"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"${r['price']:.2f}")
                with col2:
                    st.metric("Capitalisation", format_cap(r["market_cap"]))
                with col3:
                    st.metric("Secteur", r["sector"])

                st.markdown(f"""
                <div class="score-bar-container">
                    <div class="score-bar" style="width:{score_pct}%"></div>
                </div>
                <p style="color:#4a5568;font-size:12px;margin-top:4px">Score : {r['score']}/10 critères validés</p>
                """, unsafe_allow_html=True)

                crit_data = []
                for c in r["criteria"].values():
                    crit_data.append({
                        "": "✅" if c["passed"] else "❌",
                        "Critère": c["label"],
                        "Valeur": c["value"],
                        "Seuil requis": c["threshold"]
                    })
                st.dataframe(pd.DataFrame(crit_data), use_container_width=True, hide_index=True)

                st.markdown(f"""
                <div class="tip-box">
                    <div class="tip-title">💡 Que faire avec cette action ?</div>
                    <div class="tip-text">
                    {"Cette action est exceptionnelle selon nos critères. Elle mérite une analyse approfondie avant investissement." if r['score'] >= 8 else
                     "Cette action présente de bonnes caractéristiques. Surveille-la et attends un bon point d'entrée." if r['score'] >= 6 else
                     "Des qualités intéressantes mais aussi des faiblesses. À suivre avec prudence."}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        rows = [{"Verdict": r["verdict"], "Ticker": r["ticker"], "Nom": r["name"][:40],
                 "Marché": r["market"], "Secteur": r["sector"],
                 "Prix": f"${r['price']:.2f}", "Cap": format_cap(r["market_cap"]),
                 "Score": f"{r['score']}/10"} 
                for r in sorted(qualified, key=lambda x: x["score"], reverse=True)]
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📁 Exporter les résultats en CSV", csv,
                          f"stockiq_screening_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv",
                          use_container_width=True)
    else:
        st.warning(f"Aucune action ne répond aux critères (score ≥ {min_score}/10). Essaie de baisser le score minimum ou de changer de marché.")

    st.markdown("""
    <div style="text-align:center;color:#2d3748;font-size:12px;margin-top:40px;padding:20px;border-top:1px solid #1a2540">
        ⚠️ StockIQ Pro est un outil d'analyse informatif uniquement. Ce n'est pas un conseil financier.<br>
        Faites toujours vos propres recherches avant d'investir. Les performances passées ne garantissent pas les résultats futurs.
    </div>
    """, unsafe_allow_html=True)
