import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="🌍 Global Stock Screener", layout="wide")

# ─── ACCÈS ───
st.title("🌍 Global Stock Screener")
st.caption("Méthode Buffet · Lynch · Munger · Greenblatt — 10 critères · 5 marchés mondiaux")

code = st.text_input("🔑 Entre ton code d'accès :", type="password")
if code != "MONCODE123":
    st.warning("Code incorrect. Accès refusé.")
    st.stop()

st.success("✅ Accès autorisé !")
st.divider()

# ─── CONFIGURATION ───
THRESHOLDS = {
    "revenue_growth": 0.15,
    "net_margin": 0.15,
    "peg_ratio": 2.0,
    "gross_margin": 0.40,
    "debt_to_equity": 1.0,
    "roe": 0.15,
    "roic": 0.15,
    "fcf_yield": 0.05,
    "short_interest": 0.10,
}

# ─── TICKERS ───
def get_sp500():
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        tickers = tables[0]["Symbol"].tolist()
        return [t.replace(".", "-") for t in tickers], "S&P500"
    except:
        return ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","V","UNH",
                "XOM","MA","JNJ","PG","HD","COST","MRK","ABBV","CVX","CRM"], "S&P500"

def get_nasdaq100():
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for t in tables:
            if "Ticker" in t.columns or "Symbol" in t.columns:
                col = "Ticker" if "Ticker" in t.columns else "Symbol"
                return t[col].tolist(), "NASDAQ100"
    except:
        pass
    return ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","COST","NFLX",
            "AMD","ADBE","QCOM","TXN","INTC","INTU","AMGN","ISRG","SBUX","PYPL"], "NASDAQ100"

def get_europe():
    cac40 = ["AI.PA","AIR.PA","ALO.PA","MT.AS","ATO.PA","CS.PA","BNP.PA","EN.PA",
             "CAP.PA","CA.PA","ACA.PA","BN.PA","DSY.PA","ENGI.PA","EL.PA","RMS.PA",
             "KER.PA","MC.PA","OR.PA","ORA.PA","RI.PA","SAN.PA","SU.PA","GLE.PA","TTE.PA"]
    dax = ["ADS.DE","AIR.DE","ALV.DE","BAS.DE","BAYN.DE","BMW.DE","SAP.DE","SIE.DE",
           "VOW3.DE","MRK.DE","LIN.DE","RWE.DE","DTE.DE","EOAN.DE","FRE.DE"]
    ftse = ["AZN.L","SHEL.L","HSBA.L","ULVR.L","BP.L","RIO.L","GSK.L","BATS.L",
            "LSEG.L","NG.L","LLOY.L","BARC.L","GLEN.L","VOD.L","DGE.L"]
    return cac40 + dax + ftse, "EUROPE"

def get_asia():
    nikkei = ["7203.T","9984.T","6861.T","8306.T","7974.T","4063.T","9433.T",
              "6758.T","4502.T","9432.T","7267.T","6954.T","8035.T","6501.T"]
    hangseng = ["0700.HK","0941.HK","1299.HK","0005.HK","2318.HK","0939.HK",
                "1398.HK","3988.HK","0883.HK","0388.HK","0016.HK","0012.HK"]
    return nikkei + hangseng, "ASIE"

def get_smallcaps():
    return ["SMAR","YETI","APPF","CELH","BOOT","COKE","TREX","MEDP","STEP","AAON",
            "BCPC","MGEE","LANC","CRVL","UFPI","FELE","EXPO","MSGS","CSWI","ATKR",
            "PRCT","GSHD","HALO","VCEL","ACVA","NARI","SPSC","AEIS","KTOS","HLNE"], "SMALL CAPS"

# ─── ANALYSE ───
def analyze_stock(ticker, market):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            return None
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not price:
            return None

        result = {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "market": market,
            "sector": info.get("sector", "N/A"),
            "price": price,
            "market_cap": info.get("marketCap"),
            "criteria": {},
            "score": 0,
            "total": 10,
        }
        score = 0

        # 1. Croissance CA
        try:
            financials = stock.financials
            if financials is not None and not financials.empty and "Total Revenue" in financials.index:
                rev = financials.loc["Total Revenue"].dropna()
                if len(rev) >= 2:
                    cagr = (rev.iloc[0] / rev.iloc[-1]) ** (1 / (len(rev) - 1)) - 1
                    passed = cagr >= THRESHOLDS["revenue_growth"]
                    result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": f"{cagr*100:.1f}%", "passed": passed, "threshold": ">15%"}
                    if passed: score += 1
                else:
                    result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": ">15%"}
            else:
                result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": ">15%"}

        # 2. Marge Nette
        try:
            nm = info.get("profitMargins")
            if nm:
                passed = nm >= THRESHOLDS["net_margin"]
                result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": f"{nm*100:.1f}%", "passed": passed, "threshold": ">15%"}
                if passed: score += 1
            else:
                result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": "N/A", "passed": False, "threshold": ">15%"}

        # 3. PEG Ratio
        try:
            peg = info.get("pegRatio")
            if peg and peg > 0:
                passed = peg < THRESHOLDS["peg_ratio"]
                result["criteria"]["peg_ratio"] = {"label": "PEG Ratio (Lynch)", "value": f"{peg:.2f}", "passed": passed, "threshold": "<2.0"}
                if passed: score += 1
            else:
                result["criteria"]["peg_ratio"] = {"label": "PEG Ratio (Lynch)", "value": "N/A", "passed": False, "threshold": "<2.0"}
        except:
            result["criteria"]["peg_ratio"] = {"label": "PEG Ratio (Lynch)", "value": "N/A", "passed": False, "threshold": "<2.0"}

        # 4. Marge Brute
        try:
            gm = info.get("grossMargins")
            if gm:
                passed = gm >= THRESHOLDS["gross_margin"]
                result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": f"{gm*100:.1f}%", "passed": passed, "threshold": ">40%"}
                if passed: score += 1
            else:
                result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": "N/A", "passed": False, "threshold": ">40%"}
        except:
            result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": "N/A", "passed": False, "threshold": ">40%"}

        # 5. Dette/Capitaux
        try:
            de = info.get("debtToEquity")
            if de is not None:
                de_ratio = de / 100
                passed = de_ratio < THRESHOLDS["debt_to_equity"]
                result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": f"{de_ratio:.2f}", "passed": passed, "threshold": "<1.0"}
                if passed: score += 1
            else:
                result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": "N/A", "passed": False, "threshold": "<1.0"}
        except:
            result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": "N/A", "passed": False, "threshold": "<1.0"}

        # 6. ROE
        try:
            roe = info.get("returnOnEquity")
            if roe:
                passed = roe >= THRESHOLDS["roe"]
                result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": f"{roe*100:.1f}%", "passed": passed, "threshold": ">15%"}
                if passed: score += 1
            else:
                result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": "N/A", "passed": False, "threshold": ">15%"}

        # 7. ROIC
        try:
            roa = info.get("returnOnAssets")
            if roa:
                passed = roa >= THRESHOLDS["roic"]
                result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": f"{roa*100:.1f}%", "passed": passed, "threshold": ">15%"}
                if passed: score += 1
            else:
                result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": "N/A", "passed": False, "threshold": ">15%"}

        # 8. FCF Yield
        try:
            fcf = info.get("freeCashflow")
            cap = info.get("marketCap")
            if fcf and cap and cap > 0:
                fcf_yield = fcf / cap
                passed = fcf_yield >= THRESHOLDS["fcf_yield"]
                result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": f"{fcf_yield*100:.1f}%", "passed": passed, "threshold": ">5%"}
                if passed: score += 1
            else:
                result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": "N/A", "passed": False, "threshold": ">5%"}
        except:
            result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": "N/A", "passed": False, "threshold": ">5%"}

        # 9. Magic Formula
        try:
            ey = info.get("earningsYield") or (1 / info.get("trailingPE", 100) if info.get("trailingPE") else None)
            roe_val = info.get("returnOnEquity")
            if ey and roe_val:
                magic = (ey * 100) + (roe_val * 100)
                passed = magic >= 25
                result["criteria"]["magic_formula"] = {"label": "Magic Formula", "value": f"Score {magic:.1f}", "passed": passed, "threshold": "Score >25"}
                if passed: score += 1
            else:
                result["criteria"]["magic_formula"] = {"label": "Magic Formula", "value": "N/A", "passed": False, "threshold": "Score >25"}
        except:
            result["criteria"]["magic_formula"] = {"label": "Magic Formula", "value": "N/A", "passed": False, "threshold": "Score >25"}

        # 10. Short Interest
        try:
            so = info.get("sharesOutstanding")
            ss = info.get("sharesShort")
            if so and ss and so > 0:
                sp = ss / so
                passed = sp < THRESHOLDS["short_interest"]
                result["criteria"]["short_interest"] = {"label": "Short Interest", "value": f"{sp*100:.1f}%", "passed": passed, "threshold": "<10%"}
                if passed: score += 1
            else:
                result["criteria"]["short_interest"] = {"label": "Short Interest", "value": "N/A", "passed": False, "threshold": "<10%"}
        except:
            result["criteria"]["short_interest"] = {"label": "Short Interest", "value": "N/A", "passed": False, "threshold": "<10%"}

        result["score"] = score
        if score >= 8:
            result["verdict"] = "🟢 FORT POTENTIEL"
        elif score >= 6:
            result["verdict"] = "🟡 À SURVEILLER"
        elif score >= 4:
            result["verdict"] = "🟠 INTÉRESSANT"
        else:
            result["verdict"] = "🔴 ÉVITER"

        return result
    except:
        return None


def format_cap(cap):
    if not cap: return "N/A"
    if cap >= 1e12: return f"${cap/1e12:.1f}T"
    if cap >= 1e9: return f"${cap/1e9:.1f}B"
    return f"${cap/1e6:.0f}M"


# ─── INTERFACE ───
col1, col2, col3 = st.columns(3)
with col1:
    market_choice = st.selectbox("📈 Marché", ["Tous", "S&P500", "NASDAQ100", "Europe", "Asie", "Small Caps"])
with col2:
    min_score = st.slider("🎯 Score minimum", 1, 10, 6)
with col3:
    fast_mode = st.checkbox("⚡ Mode rapide (100 actions max)", value=True)

market_map = {"Tous": None, "S&P500": "sp500", "NASDAQ100": "nasdaq", "Europe": "europe", "Asie": "asia", "Small Caps": "smallcaps"}

if st.button("🚀 Lancer le scan", type="primary"):
    market_filter = market_map[market_choice]

    markets_data = []
    if market_filter is None or market_filter == "sp500": markets_data.append(get_sp500())
    if market_filter is None or market_filter == "nasdaq": markets_data.append(get_nasdaq100())
    if market_filter is None or market_filter == "europe": markets_data.append(get_europe())
    if market_filter is None or market_filter == "asia": markets_data.append(get_asia())
    if market_filter is None or market_filter == "smallcaps": markets_data.append(get_smallcaps())

    if fast_mode:
        markets_data = [(t[:100], m) for t, m in markets_data]

    total = sum(len(t) for t, _ in markets_data)
    st.info(f"🔍 {total} actions à analyser...")

    progress = st.progress(0)
    status = st.empty()
    all_results = []
    counter = 0

    for tickers, market_name in markets_data:
        for ticker in tickers:
            counter += 1
            status.text(f"Analyse en cours : {ticker} ({counter}/{total})")
            progress.progress(counter / total)
            result = analyze_stock(ticker, market_name)
            if result:
                all_results.append(result)
            time.sleep(0.3)

    progress.empty()
    status.empty()

    qualified = [r for r in all_results if r["score"] >= min_score]
    strong = [r for r in all_results if r["score"] >= 8]

    st.divider()
    st.subheader(f"📊 Résultats — {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Actions analysées", len(all_results))
    c2.metric(f"Score ≥ {min_score}/10", len(qualified))
    c3.metric("Score ≥ 8/10", len(strong))
    c4.metric("Score = 10/10", len([r for r in all_results if r["score"] == 10]))

    if qualified:
        st.divider()
        st.subheader("🏆 Actions qualifiées")

        rows = []
        for r in sorted(qualified, key=lambda x: x["score"], reverse=True):
            rows.append({
                "Verdict": r["verdict"],
                "Ticker": r["ticker"],
                "Nom": r["name"][:40],
                "Marché": r["market"],
                "Secteur": r["sector"],
                "Prix": f"${r['price']:.2f}",
                "Cap": format_cap(r["market_cap"]),
                "Score": f"{r['score']}/10",
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🔍 Détail par action")
        for r in sorted(qualified, key=lambda x: x["score"], reverse=True):
            with st.expander(f"{r['verdict']}  {r['ticker']} — {r['name']} | Score: {r['score']}/10"):
                st.write(f"**Marché:** {r['market']} · **Secteur:** {r['sector']} · **Cap:** {format_cap(r['market_cap'])} · **Prix:** ${r['price']:.2f}")
                crit_data = []
                for key, c in r["criteria"].items():
                    crit_data.append({"Critère": c["label"], "Valeur": c["value"], "Seuil": c["threshold"], "Résultat": "✅" if c["passed"] else "❌"})
                st.dataframe(pd.DataFrame(crit_data), use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📁 Télécharger CSV", csv, f"screening_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
    else:
        st.warning("Aucune action ne répond aux critères. Essaie de baisser le score minimum.")

    st.caption("⚠️ Ceci n'est pas un conseil financier. Faites toujours vos propres recherches.")
