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
 "HTFL": (5,3,2,False,"FFR-CT is an inference on a CT scan; reimbursed per analysis"),
 "IRTC": (5,3,3,False,"classifier reads 14 days of ECG; FDA + CPT code; no model, no report"),
 "UPST": (5,2,3,False,"the credit decision IS the model"),
 "RXRX": (5,1,3,False,"company is a model; output unproven"),
 "AUR": (5,1,3,False,"driving policy is the entire product; pre-revenue"),
 "KDK": (5,1,3,False,"driverless trucking; same shape as AUR"),
 "HNGE": (5,3,3,False,"CV motion tracking replaces the therapist's labor"),
 "NTRA": (5,3,1,False,"tumor-informed: tracks known variants. Statistics, not learned models"),
 "GH": (5,3,3,False,"tumor-naive + screening REQUIRE learned classifiers (methylation, fragmentomics)"),
 "APP": (5,3,3,False,"auction-time ranking model IS the P&L"),
 "FICO": (3,3,1,False,"score is a REGULATED logistic scorecard, not modern ML; contradicts UPST"),
 "EVLV": (4,3,3,False,"model-native, but FTC settlement over detection-efficacy claims"),
 "TEM": (4,2,2,False,"clinical-molecular linkage; licensing mix is the diligence question"),
 "ADPT": (4,3,1,False,"clonoSEQ counts a known clone; the real ML (TCR-antigen map) is unproven"),
 "RDNT": (4,3,3,False,"owns the scans AND the distribution; AI upsell is cash-pay"),
 "AXON": (4,3,3,False,"system of record converting to model-native product"),
 "DE": (4,3,3,False,"See & Spray decides per plant, priced on outcome"),
 "TSLA": (4,2,3,False,"fleet collects training data at a profit; FSD is the premium"),
 "PL": (3,2,2,False,"DOWNGRADED: much of revenue is imagery ACCESS, not inference. ~35x sales"),
 "CLBT": (3,2,2,False,"extraction is engineering; the paid job is AI triage"),
 "MBLY": (3,2,3,False,"perception across an OEM-funded fleet"),
 "RELX": (3,3,2,True,"owns the legal/scientific ground truth; sells the answer"),
 "TRI": (3,3,2,True,"same as RELX, narrower"),
 "SPGI": (3,2,2,True,"ratings/index corpus + CAIO + MCP surface"),
 "GEHC": (3,2,3,False,"largest imaging-AI installed base"),
 "ISRG": (3,1,2,False,"best unconverted corpus in med-tech; no AI revenue yet"),
 "CHRW": (3,2,2,False,"substitution is publicly auditable via shipments/employee"),
 "PLTR": (4,3,2,True,"ontology is the scarce asset LLMs need to ACT; very few have solved it"),
 "CRWD": (3,3,3,True,"services drag sits in COGS at ~75% GM and margin STILL expands -- flywheel pays for itself"),
 "NET": (3,2,3,True,"inference at the edge; deepest MCP traction of any filer"),
 "MDB": (3,2,2,True,"vector search; strongest operator-register blog by far"),
 "INOD": (3,2,1,True,"sells training data to the labs; supplier TO the app layer"),
 "WLY": (3,2,1,False,"licenses its corpus and prints the AI revenue number"),
 "TEAM": (2,3,2,True,"huge work corpus + Rovo + Head of AI + 1,038-star MCP server"),
 "SHOP": (2,2,2,True,"merchant data + AI-forward CEO; monetized via retention"),
 "FDS": (2,2,2,True,"financial corpus going agent-addressable; CAIO; 3/3 screens"),
 "MORN": (2,2,1,True,"same move as FDS; filing claim not matched by repo traction"),
 "INTU": (2,2,2,False,"owns returns and ledgers; attacks the services line"),
 "NU": (2,2,2,False,"behavioral underwriting where no bureau file exists"),
 "V": (2,2,2,True,"transaction graph; agentic commerce surface"),
 "KVYO": (2,2,2,True,"cross-merchant behavioral prediction; thin repo traction"),
 "DOCU": (2,2,2,True,"largest executed-agreement corpus; near-zero repo traction"),
 "WAY": (2,2,2,False,"denial prediction on a proprietary claims corpus"),
 "VRSK": (2,2,2,False,"pooled claims monopoly; imagery is the genuinely new part"),
 "SPOT": (2,2,3,True,"AI DJ programs the stream; retention not revenue"),
 "ESTC": (2,2,2,True,"retrieval/vector infrastructure; 765-star MCP server"),
 "FIG": (2,2,2,True,"1,910-star MCP server; design corpus"),
 "S": (2,1,3,True,"CONFIRMED LOSING: CRWD 5x larger AND faster; S margin -350bps vs CRWD +150bps"),
 "RBLX": (2,2,3,False,"safety ML is a licence to operate; generative creation"),
 "OPEN": (3,2,2,False,"AVM works (GM 7.2->9.7%) but revenue -44% from peak; a rates trade, not an AI trade"),
 "NP": (3,2,2,False,"flood underwriting model is the company"),
 "QXO": (2,1,1,False,"named a CAIO at founding; AI-transformation playbook, unproven"),
 "CGNX": (2,2,2,False,"deep-learning inspection; commoditizing from above"),
 "SYM": (1,1,1,False,"largely optimization and controls, not learned policy"),
 "TYL": (1,1,1,False,"records company; watch-for-conversion only"),
 "ALGN": (2,2,1,False,"orthodontic outcomes corpus; centrality claim walked back"),
 "TOST": (1,1,1,False,"payments company with an analytics layer"),
 "IQV": (2,1,1,False,"health data at scale"),
 "MCO": (2,1,1,True,"ratings corpus; CAIO"),
 "MA": (2,1,2,False,"transaction graph fraud scoring; network survives without it"),
}


# LABEL FLYWHEEL (operator insight 2026-08-20, from CrowdStrike): a services arm
# staffed by experts is a LABELLING OPERATION. Every intrusion OverWatch hunts,
# every scan a RadNet radiologist reads, every case a forward-deployed engineer
# works becomes labelled training data a pure-software competitor cannot buy.
# This is the cheapest durable data moat in the market and nothing else on the
# scorecard was capturing it -- the corpus looks identical from outside, but one
# is annotated by domain experts at the company's own expense and the other is not.
LABEL_FLYWHEEL = {
    "CRWD": "OverWatch/Falcon Complete analysts label every investigated intrusion",
    "RDNT": "owns the radiologists whose reads label the images",
    "TEM":  "clinical abstraction staff structure the notes behind the corpus",
    "PLTR": "forward-deployed engineers encode each customer's ontology by hand",
    "ISRG": "case review annotates surgical video against outcomes",
    "IQV":  "clinical operations staff curate the trial data",
}

# LEADERSHIP CHURN: technical leadership is one of the operator's three original
# criteria, so senior technical departure is a genuine negative -- and the officer
# screen only sees APPOINTMENTS, which biases it optimistic. Tracked by hand until
# the 8-K departure screen backfills it.
LEADERSHIP_CHURN = {
    "CRWD": "CTO departed 2026 -- watch whether the detection-engineering bench holds",
}

# LAB ENCROACHMENT RISK (operator 2026-08-20: "I don't trust Claude not to compete
# with them in time"). The deepest risk to this entire thesis. Frontier labs are
# moving up the stack, and an application-layer company whose only asset is a
# licensed corpus plus a good prompt is a feature waiting to be shipped.
#
# The test is NOT capability -- assume the labs can do the reasoning. The test is:
# WHAT DOES THIS COMPANY HAVE THAT A LAB CANNOT ACQUIRE BY WRITING A CHECK OR
# SHIPPING A FEATURE?
#
#   Cannot be bought: FDA clearance and reimbursement codes (labs will not run
#   clinical trials); physical data-collection fleets; a regulated balance sheet;
#   government procurement and evidentiary standards; distribution to buyers who
#   will never touch a chat box.
#
#   Can be taken: anything that is text-in / text-out over a corpus the lab can
#   license on the same terms you did. Legal research, contract review, financial
#   summarisation, generic enterprise search.
#
# 0 = structurally protected, 3 = a lab could ship this
LAB_RISK = {
 "RELX":3,"TRI":3,"DOCU":3,"INOD":3,
 "MORN":2,"FDS":2,"SPGI":2,"WLY":2,"TEAM":2,"INTU":2,"CHRW":2,"WAY":2,"S":2,
 "FIG":2,"KVYO":2,"MCO":2,"IQV":1,"MDB":1,"ESTC":1,"NET":1,"PLTR":1,"APP":1,
 "UPST":1,"NU":1,"NP":1,"OPEN":1,"VRSK":1,"SPOT":1,"RBLX":1,"CLBT":1,"TEM":1,
 "QXO":1,"TYL":1,"TOST":1,"SYM":1,"CGNX":1,"MBLY":0,"AXON":0,"FICO":0,"EVLV":0,
 "IRTC":0,"HTFL":0,"GH":0,"NTRA":0,"ADPT":0,"RDNT":0,"GEHC":0,"ISRG":0,
 "DE":0,"TSLA":0,"AUR":0,"KDK":0,"RXRX":0,"PL":0,"HNGE":0,"V":0,"MA":0,"SHOP":1,
}

# MOMENTUM -- the competitive-position axis (operator 2026-08-20, prompted by
# "MBLY - I worry about competition"). The scorecard had NO measure of whether a
# company is winning or losing its market. That gap was papered over by hand-
# downgrading SentinelOne, which is a hack, not an algorithm.
#
# Growth and gross-margin DIRECTION together are the cleanest public read on
# competitive position: a company taking share grows fast AND holds or expands
# margin. Growing slowly while margin compresses means someone is out-competing
# you on both price and product, whatever the AI story says.
#
# (yoy_growth_pct, gm_delta_bps, score 0-3, evidence). FactSet actuals.
# TODO: auto-populate from FF_SALES/FF_GROSS_MGN for the full list; hand-entered
# for the names reviewed so far. Unmeasured names score neutral, never penalised.
MOMENTUM = {
 "IOT":  (30.5, -190, 3, "+30.5% YoY, GM ~75.4%; 7 straight sequential gains"),
 "NET":  (35.9, -600, 2, "+36% but GM 77.8->71.8%; growth is not the question, cost is"),
 "CRWD": (25.6, +150, 3, "+25.6% at 5x S's size AND margin expanding"),
 "MDB":  (25.2, +150, 3, "+25.2% with GM 70.6->72.2%"),
 "S":    (20.8, -350, 1, "slower than a competitor 5x its size, margin -350bps"),
 "OPEN": (-44.0, +250, 0, "revenue -44% from peak; margin up only because it stopped buying"),
 "MBLY": (5.0, -240, 0, "LTM +5.0%, GM 42.9% = series LOW. Competition confirmed"),
}

# (multiplier, reason). Efficacy contested by a regulator or independent testing.
CREDIBILITY = {
    "EVLV": (0.85, "FTC settlement re detection-efficacy claims; independent tests missed knives"),
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
    for tk, (cen, prod, ml, dev, basis) in J.items():
        # THESIS SCORE ranks the list: centrality x named-priced product x whether
        # the algorithm is actually LEARNED.
        #
        # ml_content added 2026-08-20 after the operator challenged FICO and NTRA.
        # Both were scoring 100 on centrality alone. But FICO's score is a regulated
        # logistic scorecard -- explainability rules under ECOA/Reg B actively CAP
        # its sophistication -- and Natera's Signatera tracks known variants with
        # Bayesian error models. "An algorithm is the product" is NOT the same claim
        # as "modern machine learning is the product", and collapsing the two is
        # exactly how a pretender reaches the top of an AI ranking.
        #
        # The tell this axis encodes: if regulation requires you to explain every
        # decision, you cannot deploy a model complex enough to be interesting.
        thesis = 100.0 * (cen + prod + ml) / 11.0

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

        # CREDIBILITY DISCOUNT: architecture can be genuinely model-native while the
        # evidence that it WORKS is contested. Different failure mode from AI-washing
        # and it needs its own penalty, not a lower centrality score.
        cred = CREDIBILITY.get(tk)
        mult = cred[0] if cred else 1.0
        flywheel = 3.0 if tk in LABEL_FLYWHEEL else 0.0
        lab = -1.8 * LAB_RISK.get(tk, 1)
        mom = MOMENTUM.get(tk)
        # centred on 1.5 so a measured-but-mediocre name is penalised and an
        # unmeasured name is neutral -- never punish a company for missing data
        momentum = (mom[2] - 1.5) * 1.5 if mom else 0.0
        churn = -2.0 if tk in LEADERSHIP_CHURN else 0.0

        rows.append({"ticker": tk,
                     "score": round((thesis + corrob + flywheel + churn + lab + momentum) * mult, 1),
                     "momentum": (mom[3] if mom else ""),
                     "lab_risk": LAB_RISK.get(tk, 1),
                     "ml": ml, "credibility": (cred[1] if cred else ""),
                     "flywheel": LABEL_FLYWHEEL.get(tk, ""),
                     "churn": LEADERSHIP_CHURN.get(tk, ""),
                     "thesis": round(thesis, 1), "corroboration": corrob,
                     "centrality": cen, "product": prod, "basis": basis,
                     "evidence": "; ".join(notes) or ("developer-facing, no data collected" if dev else "not developer-facing"),
                     "contradiction": contra})
    rows.sort(key=lambda r: (-r["score"], -r["centrality"]))

    print("| # | Ticker | Score | Cen | Prod | ML | Evidence | Why |")
    print("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        flag = "  !! " + r["contradiction"] if r["contradiction"] else ""
        if r["credibility"]:
            flag += "  !! credibility discount"
        if r["flywheel"]:
            flag += "  +label flywheel"
        if r["churn"]:
            flag += "  !! leadership churn"
        if r["lab_risk"] >= 2:
            flag += "  !! lab-encroachment %d/3" % r["lab_risk"]
        if r["momentum"]:
            flag += "  [mom: %s]" % r["momentum"]
        print("| %d | %s | %s | %d/5 | %d/3 | %d/3 | %s%s | %s |" % (
            i, r["ticker"], r["score"], r["centrality"], r["product"], r["ml"],
            r["evidence"], flag, r["basis"]))
    json.dump(rows, open(os.path.join(HERE, "ai_forward_ranking.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
