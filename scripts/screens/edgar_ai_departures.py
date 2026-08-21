#!/usr/bin/env python3
"""Senior technical DEPARTURES -- the negative signal the officer screen misses.

Operator's point (2026-08-20, prompted by CrowdStrike's CTO leaving): the
appointment screen is structurally optimistic. It counts companies naming a
Chief AI Officer and never counts the ones losing their technical leadership.
Technical leadership is one of the three original criteria, so churn at the top
of engineering is real evidence against a thesis.

WHY THIS IS A TWO-STAGE SCREEN (rewritten 2026-08-21)
-----------------------------------------------------
The first build phrase-matched strings like "Chief Technology Officer resigned"
and returned FIVE companies in fourteen months -- and missed CrowdStrike, the
case that prompted it. That is not a thin signal, it is a broken method.
Measured against EDGAR full-text search, 8-K Item 5.02 does not talk that way:

    "Chief Technology Officer resigned"                2 filings
    "no longer serve as Chief Technology Officer"      0
    "will step down as Chief Technology Officer"       0
    "notified the Company of his intention to resign"  40
    "notified the Company of her intention to resign"  10
    "separation from the Company"                     313

The departure verb and the ROLE sit in different sentences. Counsel writes
"On [date], Jane Doe notified the Company of her intention to resign" in one
paragraph and identifies her as CTO in another. A phrase screen cannot span
that gap, so it only ever catches the rare filing that collapses both into one
clause -- which is why the first build found noise and missed the real case.

So: STAGE 1 searches the departure boilerplate (high recall, no role filter).
STAGE 2 fetches each filing and scores it only if a technical role appears
within PROXIMITY characters of the departure language. That is what lets the
role and the verb resolve across sentence boundaries.

CAVEAT, unchanged: Section 16 officers only. A VP of ML leaving with half the
research team is invisible here. Read as a NEGATIVE overlay on the officer
screen -- a company in both within a short window has a revolving door, which
is worse than never having named anyone.
"""
import json, time, urllib.request, urllib.parse, gzip, collections, re, os, datetime

UA = "Ashim Mehra ashimmehra@gmail.com"
FTS = "https://efts.sec.gov/LATEST/search-index"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"

# STAGE 1: how counsel actually writes a departure. No role words here on
# purpose -- these are deliberately high-recall and filtered in stage 2.
DEPARTURE_CUES = [
    "notified the Company of his intention to resign",
    "notified the Company of her intention to resign",
    "notified the Company of his decision to resign",
    "notified the Company of her decision to resign",
    "tendered his resignation",
    "tendered her resignation",
    "will depart the Company",
    "stepping down from his role",
    "stepping down from her role",
    "transition from his role",
    "transition from her role",
    "mutually agreed to separate",
    "separation from the Company",
]

# STAGE 2: technical roles, weighted by how much the departure damages a
# "technical leadership" claim. A CTO leaving is the signal; a CIO runs IT.
ROLES = [
    (r"Chief Technology Officer", 5),
    (r"Chief Technical Officer", 5),
    (r"Chief AI Officer", 5),
    (r"Chief Artificial Intelligence Officer", 5),
    (r"Chief Data (?:and|&) AI Officer", 5),
    (r"Chief Scientific Officer", 4),
    (r"Chief Science Officer", 4),
    (r"Chief Data Officer", 4),
    (r"Chief Engineering Officer", 4),
    (r"Head of (?:AI|Artificial Intelligence|Machine Learning)", 4),
    (r"Chief Product Officer", 3),
    (r"Chief Information Officer", 2),
]
PROXIMITY = 1200   # chars between the departure cue and the role
FORMS = "8-K"
START, END = "2025-01-01", "2026-08-21"


def get(url, tries=4):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(r, timeout=45) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw
        except Exception:
            time.sleep(1.5 * (a + 1))
    return None


def search(cue, frm=0):
    p = {"q": '"%s"' % cue, "forms": FORMS, "startdt": START, "enddt": END, "from": frm}
    raw = get(FTS + "?" + urllib.parse.urlencode(p))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


# ---------------------------------------------------------------- stage 1
print("[departures] stage 1: locating 8-K departure language", flush=True)
candidates = {}          # (accession, cik) -> {"filer":..., "cues": set()}
for cue in DEPARTURE_CUES:
    frm, seen, total = 0, 0, 0
    while frm < 200:
        j = search(cue, frm)
        if not j:
            break
        hs = j.get("hits", {}).get("hits", [])
        total = j.get("hits", {}).get("total", {}).get("value", 0)
        if not hs:
            break
        for h in hs:
            src = h.get("_source", {})
            adsh = h.get("_id", "").split(":")[0]
            ciks = src.get("ciks") or []
            if not ciks:
                continue
            cik = str(int(ciks[0]))
            names = src.get("display_names") or ["?"]
            key = (adsh, cik)
            candidates.setdefault(key, {"filer": names[0], "cues": set()})
            candidates[key]["cues"].add(cue)
        seen += len(hs)
        frm += 10
        if seen >= total:
            break
        time.sleep(0.12)
    print("  %-52s %d" % (cue[:52], total), flush=True)

print("[departures] stage 1 found %d candidate filings" % len(candidates), flush=True)

# ---------------------------------------------------------------- stage 2
print("[departures] stage 2: fetching filings, proximity-matching role", flush=True)
ROLE_RE = [(re.compile(p, re.I), w, p) for p, w in ROLES]
CUE_RE = re.compile("|".join(re.escape(c) for c in DEPARTURE_CUES), re.I)
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def clean_label(p):
    return (p.replace("(?:", "").replace(")", "").replace("|", "/"))


results = collections.defaultdict(
    lambda: {"score": 0, "filer": "", "roles": set(), "filings": set()})

for n, ((adsh, cik), meta) in enumerate(sorted(candidates.items()), 1):
    acc = adsh.replace("-", "")
    raw = get("%s/%s/%s/%s.txt" % (ARCHIVE, cik, acc, adsh))
    if raw:
        txt = WS.sub(" ", TAG.sub(" ", raw.decode("utf-8", "ignore")))
        for m in CUE_RE.finditer(txt):
            lo = max(0, m.start() - PROXIMITY)
            window = txt[lo:m.end() + PROXIMITY]
            for rx, w, label in ROLE_RE:
                if rx.search(window):
                    r = results[cik]
                    r["filer"] = meta["filer"]
                    r["score"] = max(r["score"], w)
                    r["roles"].add(clean_label(label))
                    r["filings"].add(adsh)
    if n % 25 == 0:
        print("  ...%d/%d fetched" % (n, len(candidates)), flush=True)
    time.sleep(0.11)

out = [{"score": v["score"], "filer": v["filer"], "cik": k,
        "roles": sorted(v["roles"]), "n_filings": len(v["filings"]),
        "filings": sorted(v["filings"])[:5]}
       for k, v in results.items()]
out.sort(key=lambda r: (-r["score"], -r["n_filings"], r["filer"]))

HERE = os.environ.get("SCREEN_OUTDIR") or os.path.dirname(os.path.abspath(__file__))
STAMP = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
path = os.path.join(HERE, "edgar_ai_departures_%s.json" % STAMP)
json.dump(out, open(path, "w"), indent=1)

print("\n[departures] %d companies with a senior TECHNICAL departure" % len(out))
print("[departures] wrote %s\n" % path)
for r in out[:40]:
    print("%2d  %-52s %s" % (r["score"], r["filer"][:52], "; ".join(r["roles"])[:60]))
