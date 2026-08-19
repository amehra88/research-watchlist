#!/usr/bin/env python3
"""Diff the two most recent runs of an EDGAR AI screen and report NEW entrants.

New filers crossing into the high-disclosure-cost tail are the leading indicator.
Usage: diff_screens.py <prefix>      e.g. diff_screens.py edgar_ai_language_screen
"""
import json, sys, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def covered_tickers():
    """Tickers already in watchlist.yaml, so known names don't read as discoveries."""
    path = os.path.join(REPO, "config", "watchlist.yaml")
    try:
        import yaml
    except ImportError:
        return set()
    try:
        data = yaml.safe_load(open(path))
    except Exception:
        return set()
    out = set()
    for v in (data or {}).values():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, dict):
                    for f in ("ticker", "id", "pvt_id"):
                        if e.get(f):
                            out.add(str(e[f]).upper())
    return out


COVERED = covered_tickers()


def cik(filer):
    m = re.search(r"CIK (\d+)", filer)
    return m.group(1) if m else filer


def label(filer):
    t = re.search(r"\(([^)]*)\)\s*\(CIK", filer)
    tk = t.group(1).split(",")[0].strip() if t else "?"
    nm = re.sub(r"\s*\([^)]*\)\s*\(CIK.*$", "", filer).strip()
    return tk, nm


def dedup(rows):
    """One row per company. EDGAR repeats a filer across documents/tickers."""
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: -r["score"]):
        k = cik(r["filer"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def emit(rows):
    print("| Score | Ticker | Name | Phrases | |")
    print("|---|---|---|---|---|")
    for r in rows:
        tk, nm = label(r["filer"])
        ph = "; ".join((r.get("phrases") or r.get("titles") or [])[:3])
        mark = "*tracked*" if tk in COVERED else ""
        print(f"| {r['score']} | {tk} | {nm[:44]} | {ph[:70]} | {mark} |")
    print()


def main(prefix):
    runs = sorted(glob.glob(os.path.join(HERE, f"{prefix}_*.json")))
    if len(runs) < 2:
        # First run: no baseline to diff against, so show the current top of the
        # list instead of an empty report. Every subsequent run diffs properly.
        print(f"## {prefix}")
        if not runs:
            print("\nNo runs on disk.\n")
            return
        raw = json.load(open(runs[-1]))
        cur = dedup(raw)
        print(f"\nFirst run (`{os.path.basename(runs[-1])}`) — no baseline yet, so this is the "
              f"current standing list, not a diff. {len(cur)} companies "
              f"({len(raw)} filing rows).\n")
        emit(cur[:40])
        return
    prev, cur = runs[-2], runs[-1]
    P = {cik(r["filer"]): r for r in json.load(open(prev))}
    C = {cik(r["filer"]): r for r in json.load(open(cur))}

    new = [C[k] for k in C if k not in P]
    gone = [P[k] for k in P if k not in C]
    rose = [(C[k], P[k]) for k in C if k in P and C[k]["score"] > P[k]["score"]]

    new.sort(key=lambda r: -r["score"])
    rose.sort(key=lambda t: -(t[0]["score"] - t[1]["score"]))

    print(f"## {prefix}")
    print(f"\n`{os.path.basename(prev)}` → `{os.path.basename(cur)}`")
    print(f"\n{len(P)} → {len(C)} filers | **{len(new)} new** | {len(rose)} increased | {len(gone)} dropped\n")

    if new:
        print("### New entrants (the signal)\n")
        emit(new[:40])
    if rose:
        print("### Increased conviction\n")
        for c, p in rose[:20]:
            tk, nm = label(c["filer"])
            print(f"- **{tk}** {nm[:44]} — {p['score']} → {c['score']}")
        print()
    if gone:
        print(f"### Dropped ({len(gone)})\n")
        print(", ".join(sorted(label(r['filer'])[0] for r in gone)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "edgar_ai_language_screen")
