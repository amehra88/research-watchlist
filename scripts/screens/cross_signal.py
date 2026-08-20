#!/usr/bin/env python3
"""Cross-signal: companies appearing in MORE THAN ONE screen.

Any single screen is weak on its own -- filings language can be IR polish, an
officer title can be a defensive hire, and an MCP server can be a weekend
project. A company clearing two or three independent thresholds is making a
costly, consistent bet in public.

This is the section to read first.
"""
import json, os, re, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

SCREENS = [
    ("edgar_ai_language_screen", "revenue/data language"),
    ("edgar_ai_officer_screen", "senior AI officer"),
    ("edgar_mcp_screen", "MCP / agent-addressable"),
]


def cik(f):
    m = re.search(r"CIK (\d+)", f)
    return m.group(1) if m else f


def label(f):
    t = re.search(r"\(([^)]*)\)\s*\(CIK", f)
    tk = t.group(1).split(",")[0].strip() if t else "?"
    nm = re.sub(r"\s*\([^)]*\)\s*\(CIK.*$", "", f).strip()
    return tk, nm


def covered():
    try:
        import yaml
        data = yaml.safe_load(open(os.path.join(REPO, "config", "watchlist.yaml")))
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


def main():
    COV = covered()
    seen = collections.defaultdict(dict)
    meta = {}
    for prefix, lab in SCREENS:
        runs = sorted(glob.glob(os.path.join(HERE, prefix + "_*.json")))
        if not runs:
            continue
        for r in json.load(open(runs[-1])):
            k = cik(r["filer"])
            if r["score"] > seen[k].get(lab, -1):
                seen[k][lab] = r["score"]
            meta[k] = r["filer"]

    multi = [(k, v) for k, v in seen.items() if len(v) >= 2]
    multi.sort(key=lambda kv: (-len(kv[1]), -sum(kv[1].values())))

    print("## Cross-signal — companies clearing more than one screen\n")
    print("Any one screen is weak alone: language can be IR polish, a title can be a")
    print("defensive hire, an MCP server can be a side project. Two or three independent")
    print("thresholds is a costly, consistent public bet. **Read this section first.**\n")
    if not multi:
        print("_No company appears in more than one screen._\n")
        return
    print("%d companies clear 2+ screens.\n" % len(multi))
    print("| # | Ticker | Name | Screens cleared | |")
    print("|---|---|---|---|---|")
    for k, v in multi[:50]:
        tk, nm = label(meta[k])
        scr = "; ".join("%s (%d)" % (lab, sc) for lab, sc in sorted(v.items(), key=lambda x: -x[1]))
        mark = "*tracked*" if tk in COV else ""
        print("| %d | %s | %s | %s | %s |" % (len(v), tk, nm[:38], scr[:78], mark))
    print()


if __name__ == "__main__":
    main()
