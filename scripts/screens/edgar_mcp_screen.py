#!/usr/bin/env python3
"""MCP-adoption screen: who is making their proprietary data agent-addressable.

Operator's thesis (2026-08-19): MCP adoption is a KPI. A company that ships a
Model Context Protocol server is deliberately exposing its corpus to AI agents --
positioning its proprietary data as substrate for the application layer rather
than defending a UI. FactSet is the worked example.

Why this is a GOOD screen right now: the phrase is rare in filings, and rarity is
precision (same logic as "AI revenue" hitting 5 of 4,194 AI-mentioning 10-Ks).
Early filers are making a deliberate architectural bet, not following a trend.

KNOWN LIMITATION -- read before trusting a null result: MCP adoption lives in
product docs, developer portals, and GitHub, NOT in SEC filings. A company can
ship a well-used MCP server and never mention it in a 10-K. This screen therefore
has HIGH precision and POOR recall, the same shape as the officer screen. Absence
here is not evidence of absence. Pairing it with a developer-surface source
(registry listings, GitHub org activity) is the real version of this signal.

Only multi-word phrases are used: bare "MCP" collides with unrelated usages
(Master Control Program, managed care, MCP ticker references).
"""
import json, time, urllib.request, urllib.parse, gzip, collections, sys, os, datetime

UA = "Ashim Mehra ashimmehra@gmail.com"
BASE = "https://efts.sec.gov/LATEST/search-index"

# (phrase, weight) -- weight = strength of the agent-addressability claim
PHRASES = [
    ("Model Context Protocol", 5),
    ("MCP server", 5),
    ("MCP servers", 5),
    ("our MCP", 4),
    ("agentic access", 3),
    ("AI agents to access", 3),
    ("agent-ready", 3),
    ("AI-ready data", 2),
    ("agentic workflows", 1),
    # "AI agents" deliberately excluded: 874 hits across forms. Too generic to
    # carry signal, and paging it triples runtime for a weight-1 phrase.
]
FORMS = ["10-K", "10-Q", "8-K"]
START, END = "2024-06-01", "2026-08-19"


def fetch(q, forms, frm=0, tries=4):
    p = {"q": '"%s"' % q, "forms": forms, "startdt": START, "enddt": END, "from": frm}
    url = BASE + "?" + urllib.parse.urlencode(p)
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except Exception:
            time.sleep(1.5 * (a + 1))
    print("  !! failed %r %s from=%d" % (q, forms, frm), file=sys.stderr)
    return None


hits = collections.defaultdict(dict)
sic = {}

for phrase, w in PHRASES:
    for form in FORMS:
        frm, total = 0, None
        while frm < 200:
            d = fetch(phrase, form, frm)
            time.sleep(0.4)
            if not d or "hits" not in d:
                break
            if total is None:
                total = d["hits"]["total"]["value"]
            rows = d["hits"]["hits"]
            if not rows:
                break
            for h in rows:
                s = h["_source"]
                names = s.get("display_names") or []
                if not names:
                    continue
                nm = names[0]
                hits[nm][phrase] = w
                sic[nm] = (s.get("sics") or [None])[0]
            frm += len(rows)
            if total is not None and frm >= total:
                break
        print("%-34r %-6s total=%s" % (phrase, form, total), file=sys.stderr)

out = []
for nm, ph in hits.items():
    out.append({"score": sum(ph.values()), "n": len(ph), "filer": nm,
                "sic": sic.get(nm), "phrases": sorted(ph, key=lambda p: -ph[p])})
out.sort(key=lambda r: (-r["score"], -r["n"]))

OUTDIR = os.environ.get("SCREEN_OUTDIR", os.path.dirname(os.path.abspath(__file__)))
STAMP = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
dest = os.path.join(OUTDIR, "edgar_mcp_screen_%s.json" % STAMP)
json.dump(out, open(dest, "w"), indent=1)
print("wrote " + dest, file=sys.stderr)
print("\n%d filers" % len(out), file=sys.stderr)
