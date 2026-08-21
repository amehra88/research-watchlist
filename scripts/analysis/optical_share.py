#!/usr/bin/env python3
"""Quarterly datacom-optics share tracker — COHR/LITE vs the Chinese transceiver makers.

WHY. The operator's test for the Chinese-competition thesis is SHARE, not technology route
(2026-08-21: "if they take material share, yes it could be a thesis breaker"). Silicon
photonics counts the same as indium phosphide. So the question needs a number, tracked, not
a judgement re-litigated each quarter.

WHY NOT TAM. The obvious route is to triangulate the TAM everyone quotes and back into share.
The corpus does hold that language, but it is sparse for optical names, inconsistently scoped
(LITE's undefined "optical TAM" vs Credo's component-level "SiPho PIC market"), and usually
sourced to a third party. Instead this uses a BOTTOM-UP denominator: total revenue across the
tracked set, from primary disclosure on both sides. No third-party estimate, no definitional
argument — at the cost of measuring share OF THE TRACKED SET rather than of the true market.

SOURCES
  US names   : Store B `metrics` table (metric='SALES'), already in pg, FactSet-sourced.
  Chinese    : config/optical_share_foreign.yaml, every point carrying its provenance.
  FX         : yfinance CNY=X, quarter-end close, cached to state/.

CALENDAR ALIGNMENT. COHR and LITE already land on calendar quarter ends. CIEN and CRDO do not
(Jan-31 / Oct-31 / Jul-31 fiscal ends), so every fiscal_end is mapped to the NEAREST calendar
quarter end. That is an approximation and it is labelled in the output.

HONEST LIMITS — read before quoting a number:
  * Company TOTALS, not datacom segment. COHR and CIEN carry large non-datacom businesses
    (lasers, industrial, telecom systems), so their share here OVERSTATES their datacom
    position and correspondingly understates the Chinese share. The `pure_play` column says
    which is which. Fixing this properly needs segment revenue, which Store B does not hold.
  * Chinese A-shares report cumulative H1 and 9M figures. Points flagged `cumulative: true`
    are EXCLUDED from the quarterly series rather than silently mixed in.
  * AAOI and FN are absent from Store B, so the tracked set is incomplete on the US side too.

  python3 scripts/analysis/optical_share.py
  python3 scripts/analysis/optical_share.py --since 2025-01-01 --csv out.csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path("/root/research-watchlist")
FOREIGN_CFG = REPO_ROOT / "config" / "optical_share_foreign.yaml"
FX_CACHE = REPO_ROOT / "state" / "fx_cny_quarter_end.json"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))

# US tracked set. Store B holds SALES for these; AAOI/FN are missing (see config `missing`).
US_NAMES = {
    "COHR": {"pure_play": False, "note": "includes lasers + industrial"},
    "LITE": {"pure_play": False, "note": "includes legacy telecom"},
    "CIEN": {"pure_play": False, "note": "telecom systems, not modules"},
    "CRDO": {"pure_play": False, "note": "connectivity ICs + optical DSP"},
}


def quarter_end(d: dt.date) -> dt.date:
    """Nearest calendar quarter end. CIEN/CRDO file Jan-31, Oct-31, Jul-31, Apr-30."""
    ends = [dt.date(y, m, day)
            for y in (d.year - 1, d.year, d.year + 1)
            for m, day in ((3, 31), (6, 30), (9, 30), (12, 31))]
    return min(ends, key=lambda e: abs((e - d).days))


def us_quarters(since: dt.date) -> dict[dt.date, dict[str, float]]:
    from pgconn import connect
    cur = connect().cursor()
    cur.execute(
        """SELECT ticker, fiscal_end, actual FROM metrics
            WHERE metric='SALES' AND actual IS NOT NULL
              AND ticker = ANY(%s) AND fiscal_end >= %s
            ORDER BY fiscal_end""",
        (list(US_NAMES), since - dt.timedelta(days=120)))
    out: dict[dt.date, dict[str, float]] = {}
    for tk, fe, actual in cur.fetchall():
        q = quarter_end(fe)
        if q < since:
            continue
        out.setdefault(q, {})[tk] = float(actual)      # already USD millions
    return out


def fx_rate(q: dt.date) -> float | None:
    """CNY per USD at quarter end, cached. Returns None if unavailable — the caller must
    then skip the quarter rather than invent a rate."""
    cache = {}
    if FX_CACHE.exists():
        try:
            cache = json.loads(FX_CACHE.read_text())
        except (json.JSONDecodeError, OSError):
            cache = {}
    key = q.isoformat()
    if key in cache:
        return cache[key]
    try:
        import yfinance as yf
        hist = yf.Ticker("CNY=X").history(
            start=(q - dt.timedelta(days=10)).isoformat(),
            end=(q + dt.timedelta(days=4)).isoformat())
        if hist.empty:
            return None
        rate = float(hist["Close"].iloc[-1])
    except Exception:                                   # noqa: BLE001 — offline / API change
        return None
    cache[key] = rate
    FX_CACHE.parent.mkdir(parents=True, exist_ok=True)
    FX_CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    return rate


def foreign_quarters(since: dt.date) -> tuple[dict[dt.date, dict[str, float]], list[str]]:
    cfg = yaml.safe_load(FOREIGN_CFG.read_text()) or {}
    out: dict[dt.date, dict[str, float]] = {}
    skipped: list[str] = []
    for cid, c in (cfg.get("companies") or {}).items():
        for row in (c.get("quarters") or []):
            q = row["calendar_quarter"]
            if isinstance(q, str):
                q = dt.date.fromisoformat(q)
            if q < since:
                continue
            if row.get("cumulative"):
                skipped.append(f"{cid} {q}: cumulative ({row.get('note','')[:48]})")
                continue
            rate = fx_rate(q)
            if rate is None:
                skipped.append(f"{cid} {q}: no FX rate available")
                continue
            out.setdefault(q, {})[cid] = row["revenue_mn"] / rate     # CNY mn -> USD mn
    return out, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="Quarterly datacom-optics revenue share")
    ap.add_argument("--since", default="2025-01-01")
    ap.add_argument("--csv", help="also write the series to this path")
    args = ap.parse_args()
    since = dt.date.fromisoformat(args.since)

    us = us_quarters(since)
    fg, skipped = foreign_quarters(since)
    quarters = sorted(set(us) | set(fg))
    if not quarters:
        print("no data in range")
        return 1

    # BALANCED PANEL. Share is only comparable across quarters if the SAME companies are in
    # every quarter. The first version of this compared 4 US + 2 China in one quarter against
    # 2 US + 1 China in another and reported a 14-point "share gain" that was pure composition
    # artefact. Restrict to companies present in EVERY quarter that has both sides.
    both = [q for q in quarters if us.get(q) and fg.get(q)]
    if not both:
        print("no quarter has both US and Chinese reporters — cannot compute share")
        return 1
    panel_us = set.intersection(*(set(us[q]) for q in both))
    panel_fg = set.intersection(*(set(fg[q]) for q in both))
    if not panel_us or not panel_fg:
        print("no company reports in every comparable quarter — panel is empty")
        return 1
    dropped = (set().union(*(set(us[q]) for q in both)) - panel_us) | \
              (set().union(*(set(fg[q]) for q in both)) - panel_fg)
    print(f"BALANCED PANEL: {','.join(sorted(panel_us))} vs "
          f"{','.join(c.split('.')[0] for c in sorted(panel_fg))}")
    if dropped:
        print(f"  dropped (not in every quarter): {', '.join(sorted(dropped))}")
    print()

    rows = []
    print(f"{'quarter':<12}{'US $mn':>10}{'China $mn':>12}{'total':>10}{'China share':>13}")
    for q in both:
        u = {k: v for k, v in us[q].items() if k in panel_us}
        f = {k: v for k, v in fg[q].items() if k in panel_fg}
        us_t, fg_t = sum(u.values()), sum(f.values())
        tot = us_t + fg_t
        share = fg_t / tot * 100
        rows.append({"quarter": q.isoformat(), "us_usd_mn": round(us_t, 1),
                     "china_usd_mn": round(fg_t, 1), "total_usd_mn": round(tot, 1),
                     "china_share_pct": round(share, 1)})
        print(f"{q!s:<12}{us_t:>10,.0f}{fg_t:>12,.0f}{tot:>10,.0f}{share:>12.1f}%")

    if len(rows) >= 2:
        d = rows[-1]["china_share_pct"] - rows[0]["china_share_pct"]
        print(f"\nChina share {rows[0]['quarter']} -> {rows[-1]['quarter']}: "
              f"{rows[0]['china_share_pct']}% -> {rows[-1]['china_share_pct']}%  ({d:+.1f} pts)")

    if skipped:
        print("\nEXCLUDED (not silently mixed in):")
        for s in skipped:
            print(f"  - {s}")

    print("\nLIMITS: company TOTALS, not datacom segment — COHR/CIEN/LITE carry large "
          "non-datacom\n  businesses, so US share here is OVERSTATED and China share "
          "UNDERSTATED.\n  AAOI and FN are absent from Store B, so the US set is incomplete "
          "too.\n  CIEN/CRDO fiscal ends are mapped to the nearest calendar quarter.")

    if args.csv and rows:
        import csv
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
