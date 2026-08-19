#!/usr/bin/env python3
"""Senior-AI-hire screen: officer TITLES in SEC filings.

Rationale (operator's Welltower point): job postings are cheap; creating a
C-suite/EVP AI role and naming a person to it in an 8-K Item 5.02 or a proxy
is an expensive, board-level commitment. Screen the title, not the buzzword.
"""
import json, time, urllib.request, urllib.parse, gzip, collections, sys

UA = "Ashim Mehra ashimmehra@gmail.com"
BASE = "https://efts.sec.gov/LATEST/search-index"

TITLES = [
    ("Chief Artificial Intelligence Officer", 5),
    ("Chief AI Officer", 5),
    ("Chief AI and Data Officer", 5),
    ("Chief Data and AI Officer", 5),
    ("Chief Data and Analytics Officer", 3),
    ("Head of Artificial Intelligence", 4),
    ("Head of AI", 4),
    ("President of AI", 4),
    ("EVP of AI", 4),
    ("Executive Vice President, Artificial Intelligence", 4),
    ("SVP of Artificial Intelligence", 3),
    ("Vice President of Artificial Intelligence", 3),
    ("Global Head of AI", 4),
    ("Chief Technology and AI Officer", 5),
    ("AI officer", 3),
]
FORMS = ["8-K", "DEF 14A", "10-K"]

def fetch(q, forms, frm=0):
    p = {"q": f'"{q}"', "forms": forms, "startdt": "2024-01-01", "enddt": "2026-08-19", "from": frm}
    url = BASE + "?" + urllib.parse.urlencode(p)
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    for a in range(4):
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
sic, forms_seen = {}, collections.defaultdict(set)

for title, w in TITLES:
    for form in FORMS:
        frm, total = 0, None
        while frm < 200:
            d = fetch(title, form, frm)
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
                hits[nm][title] = w
                sic[nm] = (s.get("sics") or [None])[0]
                forms_seen[nm].add(form)
            frm += len(rows)
            if total is not None and frm >= total:
                break
        print(f"{title!r:52s} {form:8s} total={total}", file=sys.stderr)

out = []
for nm, th in hits.items():
    out.append({"score": sum(th.values()), "n": len(th), "filer": nm, "sic": sic.get(nm),
                "forms": sorted(forms_seen[nm]), "titles": sorted(th, key=lambda x: -th[x])})
out.sort(key=lambda r: (-r["score"], -r["n"]))
json.dump(out, open("/root/.claude/jobs/301fb645/tmp/hiring_results.json", "w"), indent=1)
print(f"\n{len(out)} filers with senior AI titles", file=sys.stderr)
