#!/usr/bin/env python3
"""High-precision pass: pull the actual filers behind the RARE phrases.

Rarity == precision. 'artificial intelligence' hits 4194 10-Ks (noise).
'AI revenue' hits 5 (signal). We screen on the rare tail only.
"""
import json, time, urllib.request, urllib.parse, gzip, collections, re, sys, os, datetime

UA = "Ashim Mehra ashimmehra@gmail.com"
BASE = "https://efts.sec.gov/LATEST/search-index"

# (phrase, weight) -- weight = how costly it is to say falsely
PHRASES = [
    ("AI revenue", 5),
    ("revenue from AI", 5),
    ("AI-driven revenue", 5),
    ("AI monetization", 4),
    ("monetize AI", 4),
    ("cost of AI", 3),
    ("AI infrastructure costs", 3),
    ("trained on proprietary", 3),
    ("proprietary datasets", 2),
    ("proprietary dataset", 2),
    ("our proprietary AI models", 3),
    ("our machine learning models", 2),
    ("inference costs", 3),
    ("our own models", 2),
    ("foundation models", 1),
]
FORMS = ["10-K", "10-Q"]

def fetch(q, forms, frm=0, tries=4):
    p = {"q": f'"{q}"', "forms": forms, "startdt": "2025-06-01", "enddt": "2026-08-19", "from": frm}
    url = BASE + "?" + urllib.parse.urlencode(p)
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except Exception as e:
            time.sleep(1.5 * (a + 1))
    print(f"  !! failed {q!r} {forms} from={frm}", file=sys.stderr)
    return None

hits = collections.defaultdict(dict)   # filer -> phrase -> weight
sic = {}

for phrase, w in PHRASES:
    for form in FORMS:
        frm, total = 0, None
        while frm < 400:
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
                if not nm:
                    continue
                hits[nm][phrase] = w
                sic[nm] = (s.get("sics") or [None])[0]
            frm += len(rows)
            if total is not None and frm >= total:
                break
        print(f"{phrase!r:32s} {form}  total={total}", file=sys.stderr)

out = []
for nm, ph in hits.items():
    out.append({"score": sum(ph.values()), "n": len(ph), "filer": nm,
                "sic": sic.get(nm), "phrases": sorted(ph, key=lambda p: -ph[p])})
out.sort(key=lambda r: (-r["score"], -r["n"]))
OUTDIR = os.environ.get("SCREEN_OUTDIR", os.path.dirname(os.path.abspath(__file__)))
STAMP = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
dest = os.path.join(OUTDIR, "edgar_ai_language_screen_%s.json" % STAMP)
json.dump(out, open(dest, "w"), indent=1)
print("wrote " + dest, file=sys.stderr)
print(f"\n{len(out)} filers", file=sys.stderr)
