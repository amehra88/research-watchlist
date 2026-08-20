#!/usr/bin/env python3
"""Composite ranking: most AI-forward to least.

Combines the JUDGMENT layer (delete-the-model centrality, from the memo) with
the EVIDENCE layers (EDGAR language, senior AI officer, MCP filings, GitHub
traction, engineering-blog register).

THE TRAP THIS AVOIDS: naive summing ranks Cloudflare above iRhythm, because
Cloudflare has 5,742 GitHub stars and iRhythm has no repos at all. That is not
a finding about AI-centrality -- it is a finding that one is a software company
and the other is a medical device company. Practitioner evidence (GitHub, eng
blog) is only MEANINGFUL for firms whose product surface is developer-facing.

So each name is scored on the dimensions that APPLY to it, and the total is
rescaled to a common 0-100. `evidence_basis` records which dimensions were used,
so a high score on a narrow basis is visible rather than hidden.

DIMENSIONS
  centrality  0-5  delete the model -- does the product still exist and sell?
                   (judgment, from docs/ai-application-layer-screen.md)
  product     0-3  named product + does the model do the work + priced separately
  disclosure  0-2  EDGAR revenue/data language (audited claim)
  org         0-2  senior AI officer named in a filing
  practitioner 0-3 GitHub MCP traction + eng-blog operator register
                   (developer-surface firms only)
"""
import json, os, glob, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

# --- JUDGMENT LAYER -------------------------------------------------------
# (centrality 0-5, product 0-3, dev_surface, one-line basis)
# centrality 5 = delete the model and there is no product at all
#            3 = model is the premium/most of the equity story
#            2 = product survives; AI is a real compounding overlay
#            1 = AI is a feature
J = {
 "HTFL": (5,3,False,"FFR-CT is an inference on a CT scan; reimbursed per analysis"),
 "IRTC": (5,3,False,"classifier reads 14 days of ECG; FDA + CPT code; no model, no report"),
 "UPST": (5,2,False,"the credit decision IS the model"),
 "RXRX": (5,1,False,"company is a model; output unproven"),
 "AUR":  (5,1,False,"driving policy is the entire product; pre-revenue"),
 "KDK":  (5,1,False,"driverless trucking; same shape as AUR"),
 "HNGE": (5,3,False,"CV motion tracking replaces the therapist's labor"),
 "NTRA": (5,3,False,"personalized ctDNA panel; detection is statistical inference"),
 "GH":   (5,3,False,"blood-based classifier; weaker business than NTRA"),
 "APP":  (5,3,False,"auction-time ranking model IS the P&L"),
 "FICO": (5,3,False,"the score is a model sold as inference"),
 "EVLV": (4,3,False,"weapons-vs-benign discrimination in a live physical stream"),
 "TEM":  (4,2,False,"clinical-molecular linkage; licensing mix is the diligence question"),
 "ADPT": (4,3,False,"immune-repertoire classifier; Natera-shaped"),
 "RDNT": (4,3,False,"owns the scans AND the distribution; AI upsell is cash-pay"),
 "AXON": (4,3,False,"system of record converting to model-native product"),
 "DE":   (4,3,False,"See & Spray decides per plant, priced on outcome"),
 "TSLA": (4,2,False,"fleet collects training data at a profit; FSD is the premium"),
 "PL":   (4,2,False,"temporal Earth corpus; product is inference over it. ~35x sales"),
 "CLBT": (3,2,False,"extraction is engineering; the paid job is AI triage"),
 "MBLY": (3,2,False,"perception across an OEM-funded fleet"),
 "RELX": (3,3,True, "owns the legal/scientific ground truth; sells the answer"),
 "TRI":  (3,3,True, "same as RELX, narrower"),
 "SPGI": (3,2,True, "ratings/index corpus + CAIO + MCP surface"),
 "GEHC": (3,2,False,"largest imaging-AI installed base"),
 "ISRG": (3,1,False,"best unconverted corpus in med-tech; no AI revenue yet"),
 "CHRW": (3,2,False,"substitution is publicly auditable via shipments/employee"),
 "PLTR": (3,3,True, "AIP wires models into operational decisions"),
 "CRWD": (3,3,True, "Charlotte AI compresses analyst labor"),
 "NET":  (3,2,True, "inference at the edge; deepest MCP traction of any filer"),
 "MDB":  (3,2,True, "vector search; strongest operator-register blog by far"),
 "INOD": (3,2,True, "sells training data to the labs; supplier TO the app layer"),
 "WLY":  (3,2,False,"licenses its corpus and prints the AI revenue number"),
 "TEAM": (2,3,True, "huge work corpus + Rovo + Head of AI + 1,038-star MCP server"),
 "SHOP": (2,2,True, "merchant data + AI-forward CEO; monetized via retention"),
 "FDS":  (2,2,True, "financial corpus going agent-addressable; CAIO; 3/3 screens"),
 "MORN": (2,2,True, "same move as FDS; filing claim not matched by repo traction"),
 "INTU": (2,2,False,"owns returns and ledgers; attacks the services line"),
 "NU":   (2,2,False,"behavioral underwriting where no bureau file exists"),
 "V":    (2,2,True, "transaction graph; agentic commerce surface"),
 "KVYO": (2,2,True, "cross-merchant behavioral prediction; thin repo traction"),
 "DOCU": (2,2,True, "largest executed-agreement corpus; near-zero repo traction"),
 "WAY":  (2,2,False,"denial prediction on a proprietary claims corpus"),
 "VRSK": (2,2,False,"pooled claims monopoly; imagery is the genuinely new part"),
 "SPOT": (2,2,True, "AI DJ programs the stream; retention not revenue"),
 "ESTC": (2,2,True, "retrieval/vector infrastructure; 765-star MCP server"),
 "FIG":  (2,2,True, "1,910-star MCP server; design corpus"),
 "S":    (2,2,True, "AI-native detection; losing to CRWD"),
 "RBLX": (2,2,False,"safety ML is a licence to operate; generative creation"),
 "OPEN": (3,2,False,"the pricing model IS the business"),
 "NP":   (3,2,False,"flood underwriting model is the company"),
 "QXO":  (2,1,False,"named a CAIO at founding; AI-transformation playbook, unproven"),
 "CGNX": (2,2,False,"deep-learning inspection; commoditizing from above"),
 "SYM":  (1,1,False,"largely optimization and controls, not learned policy"),
 "TYL":  (1,1,False,"records company; watch-for-conversion only"),
 "ALGN": (2,2,False,"orthodontic outcomes corpus; centrality claim walked back"),
 "TOST": (1,1,False,"payments company with an analytics layer"),
 "IQV":  (2,1,False,"health data at scale"),
 "MCO":  (2,1,True, "ratings corpus; CAIO"),
 "MA":   (2,1,False,"transaction graph fraud scoring; network survives without it"),
}


def load_latest(prefix):
    runs = sorted(glob.glob(os.path.join(HERE, prefix + "_*.json")))
    return json.load(open(runs[-1])) if runs else []


def by_ticker(rows):
    out = {}
    for r in rows:
        m = re.search(r"\(([^)]*)\)\s*\(CIK", r.get("filer", ""))
        if not m:
            continue
        for t in m.group(1).split(","):
            t = t.strip().upper()
            if t and r.get("score", 0) > out.get(t, 0):
                out[t] = r["score"]
    return out


def main():
    lang = by_ticker(load_latest("edgar_ai_language_screen"))
    off = by_ticker(load_latest("edgar_ai_officer_screen"))
    gh = {r["ticker"]: r.get("traction", 0) for r in load_latest("github_mcp_usage")}
    try:
        blog = {r["ticker"]: (0 if r.get("insufficient_sample") else r["score"])
                for r in load_latest("eng_blog_proof")["rows"]}
    except Exception:
        blog = {}

    rows = []
    for tk, (cen, prod, dev, basis) in J.items():
        # THESIS SCORE ranks the list: how central is the model, and is there a
        # named product doing the work at a price. Nothing else moves the order.
        thesis = 100.0 * (cen + prod) / 8.0

        # CORROBORATION is reported separately and adjusts only modestly (+/-8).
        # Earlier version folded evidence into the denominator, which PENALISED
        # names that had more evidence measured -- FactSet cleared all three
        # screens and fell to 45th while HeartFlow scored 100 partly by being
        # measured on fewer dimensions. Backwards. Evidence now confirms or
        # contradicts a thesis; it never sets it.
        sig, notes = 0.0, []
        if tk in lang:
            sig += min(1.0, lang[tk] / 6.0); notes.append("filing-lang %d" % lang[tk])
        if tk in off:
            sig += min(1.0, off[tk] / 8.0); notes.append("AI officer %d" % off[tk])
        if dev:
            g, b = gh.get(tk), blog.get(tk)
            if g is not None:
                sig += min(1.0, g / 8.0); notes.append("gh-traction %s" % g)
            if b is not None:
                sig += min(1.0, b / 7.0); notes.append("blog-operator %d" % b)
        corrob = round(min(8.0, sig * 2.5), 1)

        # CONTRADICTION: loud in filings, silent where practitioners would see it.
        contra = ""
        if dev and lang.get(tk, 0) + off.get(tk, 0) >= 4 and \
           (gh.get(tk) or 0) < 4 and (blog.get(tk) or 0) < 2:
            contra = "claims > traction"

        rows.append({"ticker": tk, "score": round(thesis + corrob, 1),
                     "thesis": round(thesis, 1), "corroboration": corrob,
                     "centrality": cen, "product": prod, "basis": basis,
                     "evidence": "; ".join(notes) or ("developer-facing, no data collected" if dev else "not developer-facing"),
                     "contradiction": contra})
    rows.sort(key=lambda r: (-r["score"], -r["centrality"]))

    print("| # | Ticker | Score | Thesis | Corrob | Cen | Prod | Evidence | Why |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        flag = "  **" + r["contradiction"] + "**" if r["contradiction"] else ""
        print("| %d | %s | %s | %s | +%s | %d/5 | %d/3 | %s%s | %s |" % (
            i, r["ticker"], r["score"], r["thesis"], r["corroboration"],
            r["centrality"], r["product"], r["evidence"], flag, r["basis"]))
    json.dump(rows, open(os.path.join(HERE, "ai_forward_ranking.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
