
=============================================================
GLOBAL STOCK SCREENER — Méthode Buffet / Lynch / Greenblatt
=============================================================
Scanne ~1700 actions sur 5 marchés mondiaux et détecte
les meilleures opportunités selon 10 critères.

Marchés couverts :
    - S&P500        (503 actions — USA grandes caps)
    - NASDAQ100     (100 actions — USA tech)
    - Europe        (CAC40, DAX, FTSE100)
    - Asie          (Nikkei225, Hang Seng)
    - Small Caps    (Russell 2000 — sélection)

Critères analysés (score /10) :
    1. Croissance CA          +15%/an minimum
    2. Marge Nette            >15%
    3. PEG Ratio              <2.0 (Lynch)
    4. Avantage Compétitif    Marge brute >40%
    5. Dette/Capitaux         <1.0
    6. ROE                    >15% (Buffet)
    7. ROIC                   >15% (Munger)
    8. FCF Yield              >5% (Hedge Funds)
    9. Magic Formula          Top 30% (Greenblatt)
    10. Short Interest         <10% (pas de pression vendeuse)

Installation :
    pip3 install yfinance pandas requests beautifulsoup4 lxml

Usage :
    python3 global_screener.py                    → scan complet
    python3 global_screener.py --min-score 7      → score minimum 7/10
    python3 global_screener.py --market sp500     → un seul marché
    python3 global_screener.py --export           → export CSV
    python3 global_screener.py --fast             → top 500 actions seulement
=============================================================
"""

import yfinance as yf
import pandas as pd
import requests
import time
import argparse
import os
import json
from datetime import datetime


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

REQUEST_DELAY = 0.8  # secondes entre chaque requête

THRESHOLDS = {
    "revenue_growth":   0.15,
    "net_margin":       0.15,
    "peg_ratio":        2.0,
    "gross_margin":     0.40,
    "debt_to_equity":   1.0,
    "roe":              0.15,
    "roic":             0.15,
    "fcf_yield":        0.05,
    "short_interest":   0.10,
}


# ─────────────────────────────────────────────
# RÉCUPÉRATION DES TICKERS PAR MARCHÉ
# ─────────────────────────────────────────────

def get_sp500():
    print("  📋 Récupération S&P500...")
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        tickers = tables[0]["Symbol"].tolist()
        return [t.replace(".", "-") for t in tickers], "S&P500"
    except Exception as e:
        print(f"  ⚠️  Erreur S&P500: {e}")
        return ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","V","UNH",
                "XOM","MA","JNJ","PG","HD","COST","MRK","ABBV","CVX","CRM",
                "WMT","BAC","KO","PEP","AMD","NFLX","ADBE","TMO","LLY","AVGO"], "S&P500"


def get_nasdaq100():
    print("  📋 Récupération NASDAQ100...")
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for t in tables:
            if "Ticker" in t.columns or "Symbol" in t.columns:
                col = "Ticker" if "Ticker" in t.columns else "Symbol"
                return t[col].tolist(), "NASDAQ100"
    except Exception as e:
        print(f"  ⚠️  Erreur NASDAQ100: {e}")
    return ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","COST","NFLX",
            "AMD","ADBE","QCOM","TXN","INTC","INTU","AMGN","ISRG","SBUX","PYPL"], "NASDAQ100"


def get_europe():
    print("  📋 Récupération Europe (CAC40 + DAX + FTSE100)...")
    cac40 = [
        "AI.PA","AIR.PA","ALO.PA","MT.AS","ATO.PA","CS.PA","BNP.PA","EN.PA",
        "CAP.PA","CA.PA","ACA.PA","BN.PA","DSY.PA","ENGI.PA","EL.PA","ERF.PA",
        "RMS.PA","KER.PA","LR.PA","MC.PA","ML.PA","OR.PA","ORA.PA","RI.PA",
        "PUB.PA","RNO.PA","SAF.PA","SGO.PA","SAN.PA","SU.PA","GLE.PA","STLA.PA",
        "STM.PA","TEP.PA","HO.PA","TTE.PA","URW.AS","VIE.PA","DG.PA","WLN.PA"
    ]
    dax = [
        "ADS.DE","AIR.DE","ALV.DE","BAS.DE","BAYN.DE","BMW.DE","BEI.DE","CON.DE",
        "1COV.DE","DTEn.DE","DB1.DE","DPW.DE","DTE.DE","EOAN.DE","FRE.DE","FME.DE",
        "HEI.DE","HFG.DE","HNR1.DE","IFX.DE","LIN.DE","MRK.DE","MTX.DE","MUV2.DE",
        "RWE.DE","SAP.DE","SIE.DE","ENR.DE","VOW3.DE","VNA.DE"
    ]
    ftse = [
        "AZN.L","SHEL.L","HSBA.L","ULVR.L","BP.L","RIO.L","GSK.L","BATS.L",
        "LSEG.L","NG.L","LLOY.L","BARC.L","GLEN.L","AAL.L","WPP.L","PRU.L",
        "IMB.L","BT-A.L","VOD.L","REL.L","CPG.L","NWG.L","MNG.L","SGRO.L",
        "TSCO.L","DGE.L","EXPN.L","AUTO.L","ABF.L","JD.L"
    ]
    return cac40 + dax + ftse, "EUROPE"


def get_asia():
    print("  📋 Récupération Asie (Nikkei + Hang Seng)...")
    nikkei = [
        "7203.T","9984.T","6861.T","8306.T","7974.T","4063.T","9433.T","8316.T",
        "6758.T","4502.T","9432.T","7267.T","8411.T","4661.T","6367.T","6954.T",
        "9020.T","7751.T","4507.T","5108.T","6902.T","8035.T","7011.T","6501.T",
        "4519.T","2914.T","8801.T","4568.T","5401.T","3382.T"
    ]
    hangseng = [
        "0700.HK","0941.HK","1299.HK","0005.HK","2318.HK","0939.HK","1398.HK",
        "3988.HK","0883.HK","2628.HK","0011.HK","0388.HK","1109.HK","0016.HK",
        "0688.HK","2388.HK","0003.HK","0006.HK","0002.HK","1038.HK","0012.HK",
        "0066.HK","0823.HK","1044.HK","0101.HK","0027.HK","0175.HK","0762.HK"
    ]
    return nikkei + hangseng, "ASIE"


def get_smallcaps():
    print("  📋 Récupération Small Caps (Russell 2000 — sélection)...")
    return [
        "SMAR","YETI","APPF","CELH","BOOT","COKE","TREX","MEDP","STEP","AAON",
        "PLAY","BCPC","MGEE","LANC","CRVL","UFPI","FELE","ASTE","EXPO","DSGX",
        "MSGS","MGPI","HIMS","CSWI","PTCT","INVA","ADUS","ATKR","TMDX","AMBA",
        "PRCT","GSHD","HALO","IMVT","VCEL","FTDR","ACVA","NARI","VCTR","SPSC",
        "AEIS","KTOS","ANGI","DNLI","NTRA","ICFI","HLNE","TGTX","COOP","ACLX"
    ], "SMALL CAPS"


def get_all_tickers(market_filter=None):
    markets = []

    if market_filter is None or market_filter == "sp500":
        markets.append(get_sp500())
    if market_filter is None or market_filter == "nasdaq":
        markets.append(get_nasdaq100())
    if market_filter is None or market_filter == "europe":
        markets.append(get_europe())
    if market_filter is None or market_filter == "asia":
        markets.append(get_asia())
    if market_filter is None or market_filter == "smallcaps":
        markets.append(get_smallcaps())

    return markets


# ─────────────────────────────────────────────
# ANALYSE D'UNE ACTION
# ─────────────────────────────────────────────

def analyze_stock(ticker, market):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or not info.get("regularMarketPrice") and not info.get("currentPrice"):
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

        # ── 1. Croissance CA ──
        try:
            financials = stock.financials
            if financials is not None and not financials.empty and "Total Revenue" in financials.index:
                rev = financials.loc["Total Revenue"].dropna()
                if len(rev) >= 2:
                    cagr = (rev.iloc[0] / rev.iloc[-1]) ** (1 / (len(rev) - 1)) - 1
                    passed = cagr >= THRESHOLDS["revenue_growth"]
                    result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": f"+{cagr*100:.1f}%/an", "passed": passed, "threshold": "+15%/an"}
                    if passed: score += 1
                else:
                    result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": "+15%/an"}
            else:
                result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": "+15%/an"}
        except:
            result["criteria"]["revenue_growth"] = {"label": "Croissance CA", "value": "N/A", "passed": False, "threshold": "+15%/an"}

        # ── 2. Marge Nette ──
        try:
            nm = info.get("profitMargins")
            if nm is not None:
                passed = nm >= THRESHOLDS["net_margin"]
                result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": f"{nm*100:.1f}%", "passed": passed, "threshold": ">15%"}
                if passed: score += 1
            else:
                result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["net_margin"] = {"label": "Marge Nette", "value": "N/A", "passed": False, "threshold": ">15%"}

        # ── 3. PEG Ratio ──
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

        # ── 4. Avantage Compétitif (Marge Brute) ──
        try:
            gm = info.get("grossMargins")
            if gm is not None:
                passed = gm >= THRESHOLDS["gross_margin"]
                result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": f"Marge brute {gm*100:.1f}%", "passed": passed, "threshold": ">40%"}
                if passed: score += 1
            else:
                result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": "N/A", "passed": False, "threshold": ">40%"}
        except:
            result["criteria"]["gross_margin"] = {"label": "Avantage Compétitif", "value": "N/A", "passed": False, "threshold": ">40%"}

        # ── 5. Dette / Capitaux ──
        try:
            d2e = info.get("debtToEquity")
            if d2e is not None:
                d2e_n = d2e / 100
                passed = d2e_n < THRESHOLDS["debt_to_equity"]
                result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": f"{d2e_n:.2f}", "passed": passed, "threshold": "<1.0"}
                if passed: score += 1
            else:
                result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": "N/A", "passed": False, "threshold": "<1.0"}
        except:
            result["criteria"]["debt_to_equity"] = {"label": "Dette/Capitaux", "value": "N/A", "passed": False, "threshold": "<1.0"}

        # ── 6. ROE (Buffet) ──
        try:
            roe = info.get("returnOnEquity")
            if roe is not None:
                passed = roe >= THRESHOLDS["roe"]
                result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": f"{roe*100:.1f}%", "passed": passed, "threshold": ">15%"}
                if passed: score += 1
            else:
                result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["roe"] = {"label": "ROE (Buffet)", "value": "N/A", "passed": False, "threshold": ">15%"}

        # ── 7. ROIC (Munger) ──
        try:
            ebit = info.get("ebitda")
            total_assets = info.get("totalAssets")
            total_debt = info.get("totalDebt", 0)
            current_liabilities = info.get("totalCurrentLiabilities", 0)
            if ebit and total_assets and total_assets > 0:
                invested_capital = total_assets - current_liabilities
                roic = ebit / invested_capital if invested_capital > 0 else None
                if roic is not None:
                    passed = roic >= THRESHOLDS["roic"]
                    result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": f"{roic*100:.1f}%", "passed": passed, "threshold": ">15%"}
                    if passed: score += 1
                else:
                    result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": "N/A", "passed": False, "threshold": ">15%"}
            else:
                result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": "N/A", "passed": False, "threshold": ">15%"}
        except:
            result["criteria"]["roic"] = {"label": "ROIC (Munger)", "value": "N/A", "passed": False, "threshold": ">15%"}

        # ── 8. FCF Yield (Hedge Funds) ──
        try:
            fcf = info.get("freeCashflow")
            mktcap = info.get("marketCap")
            if fcf and mktcap and mktcap > 0:
                fcf_yield = fcf / mktcap
                passed = fcf_yield >= THRESHOLDS["fcf_yield"]
                result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": f"{fcf_yield*100:.1f}%", "passed": passed, "threshold": ">5%"}
                if passed: score += 1
            else:
                result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": "N/A", "passed": False, "threshold": ">5%"}
        except:
            result["criteria"]["fcf_yield"] = {"label": "FCF Yield", "value": "N/A", "passed": False, "threshold": ">5%"}

        # ── 9. Magic Formula (Greenblatt) ──
        try:
            earnings_yield = info.get("earningsYield") or (1 / info.get("trailingPE", 100) if info.get("trailingPE") else None)
            roe_val = info.get("returnOnEquity")
            if earnings_yield and roe_val:
                magic_score = (earnings_yield * 100) + (roe_val * 100)
                passed = magic_score >= 25
                result["criteria"]["magic_formula"] = {"label": "Magic Formula (Greenblatt)", "value": f"Score {magic_score:.1f}", "passed": passed, "threshold": "Score >25"}
                if passed: score += 1
            else:
                result["criteria"]["magic_formula"] = {"label": "Magic Formula (Greenblatt)", "value": "N/A", "passed": False, "threshold": "Score >25"}
        except:
            result["criteria"]["magic_formula"] = {"label": "Magic Formula (Greenblatt)", "value": "N/A", "passed": False, "threshold": "Score >25"}

        # ── 10. Short Interest ──
        try:
            shares_outstanding = info.get("sharesOutstanding")
            shares_short = info.get("sharesShort")
            if shares_outstanding and shares_short and shares_outstanding > 0:
                short_pct = shares_short / shares_outstanding
                passed = short_pct < THRESHOLDS["short_interest"]
                result["criteria"]["short_interest"] = {"label": "Short Interest", "value": f"{short_pct*100:.1f}%", "passed": passed, "threshold": "<10%"}
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

    except Exception as e:
        return None


# ─────────────────────────────────────────────
# AFFICHAGE
# ─────────────────────────────────────────────

def format_cap(cap):
    if not cap: return "N/A"
    if cap >= 1e12: return f"${cap/1e12:.1f}T"
    if cap >= 1e9: return f"${cap/1e9:.1f}B"
    return f"${cap/1e6:.0f}M"


def print_result(r):
    print(f"\n{'─'*60}")
    print(f"  {r['verdict']}  {r['ticker']} — {r['name']}")
    print(f"  {r['market']} · {r['sector']} · {format_cap(r['market_cap'])} · ${r['price']}")
    print(f"  Score: {r['score']}/{r['total']}")
    print(f"{'─'*60}")
    for key, c in r["criteria"].items():
        icon = "✅" if c["passed"] else "❌"
        print(f"  {icon} {c['label']:<30} {c['value']:<18} (seuil: {c['threshold']})")


def print_summary(all_results, min_score):
    qualified = [r for r in all_results if r["score"] >= min_score]
    perfect = [r for r in all_results if r["score"] == 10]
    strong = [r for r in all_results if r["score"] >= 8]

    print(f"\n{'═'*60}")
    print(f"  🌍 RÉSULTATS GLOBAUX — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'═'*60}")
    print(f"  Actions analysées    : {len(all_results)}")
    print(f"  Score ≥ {min_score}/10         : {len(qualified)}")
    print(f"  Score ≥ 8/10         : {len(strong)}")
    print(f"  Score = 10/10        : {len(perfect)}")
    print(f"{'═'*60}\n")

    # Par marché
    markets = list(set(r["market"] for r in all_results))
    print("  PAR MARCHÉ :")
    for m in markets:
        m_results = [r for r in all_results if r["market"] == m]
        m_qualified = [r for r in m_results if r["score"] >= min_score]
        print(f"  {m:<15} {len(m_results)} analysées → {len(m_qualified)} qualifiées")

    print(f"\n{'─'*60}")
    print(f"  TOP ACTIONS (score ≥ {min_score}/10) :\n")

    if not qualified:
        print("  Aucune action ne répond aux critères aujourd'hui.")
        return

    for r in sorted(qualified, key=lambda x: x["score"], reverse=True):
        bar = "█" * r["score"] + "░" * (10 - r["score"])
        print(f"  {r['ticker']:<8} [{bar}] {r['score']}/10  {r['verdict']}")
        print(f"           {r['name'][:45]}")
        print(f"           {r['market']} · {r['sector']}")
        print()


def export_csv(results, min_score=0):
    filename = f"screening_global_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    rows = []
    for r in results:
        if r["score"] >= min_score:
            row = {
                "ticker": r["ticker"],
                "name": r["name"],
                "market": r["market"],
                "sector": r["sector"],
                "price": r["price"],
                "market_cap": r["market_cap"],
                "score": r["score"],
                "verdict": r["verdict"],
            }
            for key, c in r["criteria"].items():
                row[key] = c.get("value", "N/A")
                row[f"{key}_pass"] = c.get("passed", False)
            rows.append(row)

    if rows:
        df = pd.DataFrame(rows)
        df = df.sort_values("score", ascending=False)
        df.to_csv(filename, index=False)
        print(f"\n  📁 Résultats exportés → {filename}")
    return filename


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Global Stock Screener — Buffet/Lynch/Greenblatt")
    parser.add_argument("--min-score", type=int, default=6, help="Score minimum sur 10 (défaut: 6)")
    parser.add_argument("--market", type=str, choices=["sp500","nasdaq","europe","asia","smallcaps"], help="Marché spécifique")
    parser.add_argument("--export", action="store_true", help="Exporter en CSV")
    parser.add_argument("--fast", action="store_true", help="Mode rapide — top 500 actions seulement")
    parser.add_argument("--verbose", action="store_true", help="Afficher toutes les actions")
    args = parser.parse_args()

    print("\n" + "═"*60)
    print("  🌍 GLOBAL STOCK SCREENER")
    print("  Méthode Buffet · Lynch · Munger · Greenblatt")
    print("  10 critères · 5 marchés mondiaux")
    print("═"*60 + "\n")

    markets_data = get_all_tickers(args.market)
    print()

    all_results = []
    total_tickers = sum(len(t) for t, _ in markets_data)
    print(f"  🔍 {total_tickers} actions à analyser\n")

    counter = 0
    for tickers, market_name in markets_data:
        print(f"\n  ── Scan {market_name} ({len(tickers)} actions) ──\n")

        if args.fast and len(tickers) > 100:
            tickers = tickers[:100]
            print(f"  ⚡ Mode rapide : limité à 100 actions\n")

        for i, ticker in enumerate(tickers):
            counter += 1
            print(f"  [{counter}/{total_tickers}] {ticker:<12}", end="\r")

            result = analyze_stock(ticker, market_name)

            if result:
                all_results.append(result)
                if args.verbose or result["score"] >= args.min_score:
                    print_result(result)

            time.sleep(REQUEST_DELAY)

    print_summary(all_results, args.min_score)

    qualified = [r for r in all_results if r["score"] >= args.min_score]
    if qualified and not args.verbose:
        print(f"\n{'─'*60}")
        print("  DÉTAIL DES ACTIONS QUALIFIÉES :\n")
        for r in sorted(qualified, key=lambda x: x["score"], reverse=True):
            print_result(r)

    if args.export:
        export_csv(all_results, min_score=args.min_score)

    print(f"\n  ⚠️  Ceci n'est pas un conseil financier.")
    print(f"  Faites toujours vos propres recherches.\n")


if __name__ == "__main__":
    main()
