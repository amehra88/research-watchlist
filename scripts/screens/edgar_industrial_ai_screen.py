#!/usr/bin/env python3
"""Industrial / defense / robotics AI screen -- the non-obvious names.

Operator (2026-08-20): "the list is of pretty well known companies... cast a
broader net... defense, robotics, industrials."

They were right, and mining the existing screens proved WHY. Only 65 of ~500
hits landed in industrial SICs, and none were LMT, RTX, NOC, GD, AVAV, KTOS,
HON, EMR, ROK or CAT. That is not because those companies do no AI. It is
because MY PHRASE SET WAS TUNED TO SOFTWARE. A SaaS company writes
"proprietary datasets" and "MCP server"; an aerospace prime writes "sensor
fusion", "autonomy", and "predictive maintenance" and never once says
"foundation model".

A screen inherits the vocabulary of whoever wrote it. This is the industrial
dialect of the same question.

Weighted, as always, by how costly the phrase is to say falsely:
  5 = a deployed autonomous/learned system doing physical work
  3 = a specific ML technique named
  1 = general vocabulary
"""
import json, time, urllib.request, urllib.parse, gzip, collections, sys, os, datetime

UA = "Ashim Mehra ashimmehra@gmail.com"
BASE = "https://efts.sec.gov/LATEST/search-index"

PHRASES = [
    ("autonomy stack", 5),
    ("autonomous systems", 4),
    ("sensor fusion", 5),
    ("perception system", 5),
    ("perception stack", 5),
    ("computer vision", 3),
    ("digital twin", 3),
    ("predictive maintenance", 3),
    ("machine vision", 3),
    ("neural network", 3),
    ("deep learning", 3),
    ("edge inference", 5),
    ("on-device inference", 5),
    ("autonomous navigation", 4),
    ("large language model", 1),
    ("machine learning algorithms", 1),
]
FORMS = ["10-K"]
START, END = "2025-06-01", "2026-08-20"

# Sectors we want to SURFACE (the point of the exercise). Software, semis and
# biotech are excluded not because they are uninteresting but because the other
# screens already cover them and they would drown the signal here.
KEEP = [(1000,1799),(2000,2799),(2900,3499),(3500,3599),(3600,3699),(3700,3799),
        (3800,3899),(4000,4799),(8710,8749)]
DROP = [(3674,3674),(3559,3559),(2836,2836),(2834,2836),(7370,7379),(6000,6799)]


def insector(s):
    try:
        s = int(s)
    except Exception:
        return False
    if any(a <= s <= b for a, b in DROP):
        return False
    return any(a <= s <= b for a, b in KEEP)


def fetch(q, form, frm=0, tries=4):
    p = {"q": '"%s"' % q, "forms": form, "startdt": START, "enddt": END, "from": frm}
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
    return None


hits = collections.defaultdict(dict)
sic = {}
for phrase, w in PHRASES:
    for form in FORMS:
        frm, total = 0, None
        while frm < 300:
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
                nm = (s.get("display_names") or [None])[0]
                sc = (s.get("sics") or [None])[0]
                if not nm or not insector(sc):
                    continue
                hits[nm][phrase] = w
                sic[nm] = sc
            frm += len(rows)
            if total is not None and frm >= total:
                break
        print("%-30r total=%s kept=%d" % (phrase, total, len(hits)), file=sys.stderr)

out = [{"score": sum(v.values()), "n": len(v), "filer": k, "sic": sic.get(k),
        "phrases": sorted(v, key=lambda x: -v[x])} for k, v in hits.items()]
out.sort(key=lambda r: (-r["score"], -r["n"]))
stamp = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
outdir = os.environ.get("SCREEN_OUTDIR", os.path.dirname(os.path.abspath(__file__)))
dest = os.path.join(outdir, "edgar_industrial_ai_screen_%s.json" % stamp)
json.dump(out, open(dest, "w"), indent=1)
print("wrote " + dest, file=sys.stderr)

print("## Industrial / defense / robotics AI — the non-obvious names\n")
print("Software, semis and biotech are excluded here; the other screens cover them.")
print("Phrases weighted by how costly they are to say falsely: a deployed autonomy")
print("stack or sensor-fusion system scores 5, a named technique 3, vocabulary 1.\n")
print("| Score | Ticker | Name | SIC | Evidence |")
print("|---|---|---|---|---|")
import re
for r in out[:60]:
    m = re.search(r"\(([^)]*)\)\s*\(CIK", r["filer"])
    tk = m.group(1).split(",")[0].strip() if m else "?"
    nm = re.sub(r"\s*\([^)]*\)\s*\(CIK.*$", "", r["filer"]).strip()
    print("| %d | %s | %s | %s | %s |" % (
        r["score"], tk, nm[:38], r["sic"], "; ".join(r["phrases"][:3])[:58]))
