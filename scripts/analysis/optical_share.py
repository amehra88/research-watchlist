#!/usr/bin/env python3
"""Quarterly datacom-module share — COHR/LITE/AAOI vs Innolight/Eoptolink.

The operator's test is SHARE (2026-08-21: "if they take material share, yes it could be a
thesis breaker"), and the route does not matter — silicon photonics counts the same as InP.

THREE CORRECTIONS over the first version, all from operator review:

1. "you can't just look at headline revenue." Companies are now classified by ROLE and only
   like is compared with like:
     module_maker  competes head-to-head -> IN the share math
     contract_mfr  BUILDS modules for the module makers; its revenue OVERLAPS theirs, so
                   including it double-counts. Fabrinet is excluded for exactly this reason.
     component     sells INTO module makers (Accelink) — a different layer
     diversified   material non-optical revenue (HG Genuine) — totals mislead
   What is still NOT fixed: within module_maker, these are COMPANY TOTALS. COHR carries
   lasers/industrial and LITE legacy telecom, so US share is overstated. FactSet exposes
   GEOGRAPHIC segments (FF_SALES_GEO_SEG) but not business segments, so a true datacom-only
   split needs extraction from the filings. Every run says so.

2. "there are other chinese companies." Eoptolink joins Innolight in the panel; Accelink and
   HG Genuine are tracked but classified out. Still missing: TFC Optical, Broadex, Dongshan,
   Hisense Broadband, Source Photonics. The Chinese side is therefore UNDERCOUNTED and the
   share below is a FLOOR.

3. "i want it by quarter." Full quarterly series from FactSet FF_SALES in USD — no FX
   assumption, no cumulative/standalone confusion from Chinese H1 and 9M reporting.

BALANCED PANEL. Share is only comparable across quarters if the same companies appear in
every one. An earlier version compared 4 US + 2 CN in one quarter against 2 US + 1 CN in the
next and reported a 14-point "gain" that was pure composition artefact.

  python3 scripts/analysis/optical_share.py
  python3 scripts/analysis/optical_share.py --since 2024-01-01 --csv share.csv
"""
from __future__ import annotations

import textwrap

import argparse
import datetime as dt
from pathlib import Path

import yaml

CFG = Path("/root/research-watchlist/config/optical_revenue.yaml")


def load() -> dict:
    return yaml.safe_load(CFG.read_text()) or {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Quarterly datacom-module revenue share")
    ap.add_argument("--since", default="2024-01-01")
    ap.add_argument("--csv")
    ap.add_argument("--include-all", action="store_true",
                    help="also show a variant including component/diversified names "
                         "(never the contract manufacturer — that always double-counts)")
    args = ap.parse_args()
    since = dt.date.fromisoformat(args.since)

    cfg = load()
    comps = cfg["companies"]
    roles = ("module_maker",) if not args.include_all else ("module_maker", "component", "diversified")
    panel = {k: v for k, v in comps.items() if v["role"] in roles}
    excluded = {k: v for k, v in comps.items() if k not in panel}

    # A company can belong in the panel but have no obtainable data (O-Net was taken
    # private). Exclude it from the maths but SAY SO — silently dropping it would hide a
    # real hole, and blocking on it would refuse to produce any number at all.
    no_data = {k: v for k, v in panel.items() if not v.get("quarters")}
    panel = {k: v for k, v in panel.items() if v.get("quarters")}

    print(f"PANEL ({', '.join(roles)}):")
    for k, v in sorted(panel.items(), key=lambda kv: kv[1]["bloc"]):
        print(f"   {v['bloc']}  {k:<16}{v['name']}")
    for k, v in no_data.items():
        why = " ".join((v.get("note") or "no data").split())[:78]
        print(f"   !! {v['bloc']}  {k:<13}{v['name']} — IN SCOPE BUT NO DATA: {why}")
    print("EXCLUDED:")
    for k, v in excluded.items():
        why = " ".join((v.get("note") or "").split())[:88]
        print(f"   {v['role']:<14}{k:<16}{why}")

    # quarters where EVERY panel company reported — the balanced panel
    per = {k: {dt.date.fromisoformat(str(q)) if not isinstance(q, dt.date) else q: val
               for q, val in v["quarters"].items()} for k, v in panel.items()}
    common = sorted(set.intersection(*(set(d) for d in per.values())))
    common = [q for q in common if q >= since]
    if not common:
        print("\nno quarter has every panel company reporting")
        return 1

    rows = []
    print(f"\n{'quarter':<12}{'US $mn':>10}{'China $mn':>12}{'total':>11}{'China share':>13}")
    for q in common:
        us = sum(per[k][q] for k, v in panel.items() if v["bloc"] == "US")
        cn = sum(per[k][q] for k, v in panel.items() if v["bloc"] == "CN")
        tot = us + cn
        sh = cn / tot * 100
        rows.append({"quarter": q.isoformat(), "us_usd_mn": round(us, 1),
                     "china_usd_mn": round(cn, 1), "total_usd_mn": round(tot, 1),
                     "china_share_pct": round(sh, 1)})
        print(f"{q!s:<12}{us:>10,.0f}{cn:>12,.0f}{tot:>11,.0f}{sh:>12.1f}%")

    if len(rows) >= 2:
        a, b = rows[0], rows[-1]
        print(f"\nChina share {a['quarter']} -> {b['quarter']}: "
              f"{a['china_share_pct']}% -> {b['china_share_pct']}% "
              f"({b['china_share_pct'] - a['china_share_pct']:+.1f} pts)")

    print(textwrap.dedent("""
        READ WITH THESE LIMITS
          * COMPANY TOTALS, not datacom segment. COHR carries lasers/industrial, LITE legacy
            telecom, AAOI CATV. US revenue here is therefore OVERSTATED as datacom, so the
            China share below is a FLOOR on that count too.
          * The Chinese side is UNDERCOUNTED: TFC Optical, Broadex, Dongshan, Hisense
            Broadband and Source Photonics are not in the panel.
          * Fabrinet is excluded because it BUILDS modules for the module makers — counting
            it would double-count the same product.
          * Revenue share is not unit share. If Chinese ASPs are lower, unit share is HIGHER
            than shown.
        """).rstrip())

    if args.csv and rows:
        import csv
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
        print(f"\nwrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
