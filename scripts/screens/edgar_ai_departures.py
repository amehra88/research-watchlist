#!/usr/bin/env python3
"""Senior technical DEPARTURES -- the negative signal the officer screen misses.

Operator's point (2026-08-20, prompted by CrowdStrike's CTO leaving): the
appointment screen is structurally optimistic. It counts companies naming a
Chief AI Officer and never counts the ones losing their technical leadership.
Technical leadership is one of the three original criteria, so churn at the top
of engineering is real evidence against a thesis -- and 8-K Item 5.02 covers
departures exactly as it covers appointments.

Read as a NEGATIVE overlay on the officer screen. A company that appears in
both within a short window has a revolving door, which is worse than never
having named anyone.

CAVEAT, same as the appointment screen: Section 16 officers only. A VP of ML
leaving with half the research team is invisible here.
"""
import json, time, urllib.request, urllib.parse, gzip, collections, sys, os, datetime

UA = "Ashim Mehra ashimmehra@gmail.com"
BASE = "https://efts.sec.gov/LATEST/search-index"

# Departure language paired with a technical role. Weighted by seniority.
PHRASES = [
    ("Chief Technology Officer will depart", 5),
    ("Chief Technology Officer resigned", 5),
    ("Chief Technology Officer, resigned", 5),
    ("resignation of the Company's Chief Technology Officer", 5),
    ("Chief AI Officer resigned", 5),
    ("Chief Artificial Intelligence Officer resigned", 5),
    ("Chief Information Officer resigned", 3),
    ("Chief Product Officer resigned", 3),
    ("Chief Science Officer resigned", 4),
    ("Chief Scientific Officer resigned", 4),
    ("transition from his role as Chief Technology Officer", 4),
    ("transition from her role as Chief Technology Officer", 4),
    ("stepping down as Chief Technology Officer", 5),
]
FORMS = ["8-K", "DEF 14A"]
START, END = "2025-01-01", "2026-08-20"


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
    return None


hits = collections.defaultdict(dict)
for phrase, w in PHRASES:
    for form in FORMS:
        frm, total = 0, None
        while frm < 100:
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
                nm = (h["_source"].get("display_names") or [None])[0]
                if nm:
                    hits[nm][phrase] = w
            frm += len(rows)
            if total is not None and frm >= total:
                break
        print("%-52r %-8s total=%s" % (phrase, form, total), file=sys.stderr)

out = [{"score": sum(v.values()), "n": len(v), "filer": k,
        "phrases": sorted(v, key=lambda x: -v[x])} for k, v in hits.items()]
out.sort(key=lambda r: -r["score"])
stamp = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
outdir = os.environ.get("SCREEN_OUTDIR", os.path.dirname(os.path.abspath(__file__)))
dest = os.path.join(outdir, "edgar_ai_departures_%s.json" % stamp)
json.dump(out, open(dest, "w"), indent=1)
print("wrote " + dest, file=sys.stderr)

print("## Senior technical departures — negative overlay\n")
print("The officer screen counts hires and never counts losses, which makes it")
print("structurally optimistic. This is the other half. A company appearing in both")
print("within a short window has a revolving door — worse than never having hired.\n")
print("| Score | Filer | Departure language |")
print("|---|---|---|")
for r in out[:40]:
    print("| %d | %s | %s |" % (r["score"], r["filer"][:52], "; ".join(r["phrases"][:2])[:60]))
