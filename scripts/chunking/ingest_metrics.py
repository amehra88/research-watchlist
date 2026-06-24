#!/usr/bin/env python3
"""
Store B ingest (multi-ticker x multi-metric). Reads raw FactSet JSON pulled by a
FactSet-MCP agent into state/chunk_store/factset_raw/, transforms via
store_b.build_metrics, and writes to the configured backend (file | pg, selected
by CHUNK_STORE_BACKEND through store_b.get_metrics_store()).

Raw layout — ONE combined file per (metric, kind) holding every ticker's rows,
keyed back to a ticker by FactSet `requestId` (== the id passed to the MCP, e.g.
"NVDA-US"):
    factset_raw/{METRIC}_{kind}.json        kind in {guidance, surprise}
e.g. factset_raw/SALES_guidance.json, factset_raw/INC_GROSS_surprise.json

PULL CONVENTION (the factset-pull-drop fix — do NOT change frequency):
The FactSet-MCP EstimatesConsensus pull MUST use periodicity='QTR' with
frequency='AM' (Actual Monthly). AM oversamples each fiscal period ~3x; the
redundant monthly rows collapse to one-per-period in store_b._dedupe_by_period
(keyed on fiscalEndDate). The original pull used frequency='AQ' (quarterly),
which lands in sampling gaps for off-calendar fiscal years and silently DROPS a
quarter (neighbors present, target absent, a few rows duplicated) — e.g. AVGO
lost FY22Q2 (2022-04-30) and FY23Q3 (2023-07-31). coverage_gaps() below is the
regression guard that catches a recurrence. Pull the full ids list in batches
(ids accepts ≤3000; ~10/call keeps each response under the MCP size cap) over a
window like 2020-06-01 → today.

The FY-label offset (note-label year - FactSet fiscalYear) is DERIVED per ticker
straight from FactSet's own fiscalEndDate via store_b.derive_fy_offset() — no
hand-coding — and cached to factset_raw/_fy_offsets.json. The legacy hand-coded
store_b._FY_LABEL_OFFSET is a defensive fallback only.

    python3 scripts/chunking/ingest_metrics.py                      # build + write + report
    python3 scripts/chunking/ingest_metrics.py --dry-run            # build + report, NO write
    python3 scripts/chunking/ingest_metrics.py --tickers NVDA,AMD --metrics SALES,EPS
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from store_b import (  # noqa: E402
    STORE_DIR, build_metrics, credibility_score, derive_fy_offset,
    get_metrics_store, _FY_LABEL_OFFSET,
)

RAW = STORE_DIR / "factset_raw"
OFFSETS_FILE = RAW / "_fy_offsets.json"
REPO = Path("/root/research-watchlist")
METRICS = ["SALES", "INC_GROSS", "EPS"]   # SALES + gross-income-$ + EPS (per operator decision)
KINDS = ("guidance", "surprise")


# ---------------------------------------------------------------------------
# Universe + identity (ticker <-> FactSet id)
# ---------------------------------------------------------------------------
def universe() -> list[str]:
    """T1 + T2 tickers from watchlist.yaml (dedup; drop the A000660 alias of
    000660.KS)."""
    w = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    out: list[str] = []
    for block in ("tier_1_bctk", "tier_2_active_candidates"):
        for it in (w.get(block) or []):
            tk = it if isinstance(it, str) else (it.get("ticker") or list(it.keys())[0])
            if tk and tk not in out:
                out.append(tk)
    return [t for t in out if t != "A000660"]


def id_maps(tickers: list[str]) -> tuple[dict, dict]:
    """(ticker -> factset_id, factset_id -> ticker) for the given tickers.
    factset_id from ticker_identity.yaml, else default TICKER-US."""
    idmap = yaml.safe_load((REPO / "config" / "ticker_identity.yaml").read_text())
    tk_to_fid, fid_to_tk = {}, {}
    for tk in tickers:
        fid = ((idmap.get(tk) or {}).get("factset_id")) or f"{tk}-US"
        tk_to_fid[tk] = fid
        fid_to_tk[fid] = tk
    return tk_to_fid, fid_to_tk


# ---------------------------------------------------------------------------
# Raw I/O — combined {metric}_{kind}.json grouped ticker -> [rows]
# ---------------------------------------------------------------------------
def rows_for(metric: str, kind: str, fid_to_tk: dict) -> dict[str, list[dict]]:
    p = RAW / f"{metric}_{kind}.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text()).get("data", [])
    grouped: dict[str, list[dict]] = {}
    for r in data:
        tk = fid_to_tk.get(r.get("requestId"))
        if tk:
            grouped.setdefault(tk, []).append(r)
    return grouped


# ---------------------------------------------------------------------------
# Coverage guard — interior fiscal-quarter gaps (the factset-pull-drop tell)
# ---------------------------------------------------------------------------
def coverage_gaps(tickers: list[str], fid_to_tk: dict) -> dict[str, list[dict]]:
    """Detect interior MISSING QUARTERS in each ticker's reported-actuals series.

    This is the guard for the pull-drop bug class (see the
    factset-pull-stage-drops-guidance note): a too-coarse FactSet sampling
    frequency (the original pull used frequency='AQ') lands in gaps for
    off-calendar fiscal years and silently omits a quarter — neighbors present,
    target absent, a couple of rows duplicated. The fix is frequency='AM'
    (monthly oversampling, collapsed by store_b._dedupe_by_period); this guard
    proves it took.

    Every fiscal quarter has an ACTUAL, so the surprise series is the dense
    reference: walk its sorted unique fiscalEndDates and flag any consecutive
    gap that is ~2x the ticker's own modal cadence (a skipped quarter) while
    that cadence is itself quarterly (≤130d) — which keeps genuine
    semi-annual/annual reporters from false-positiving. Returns
    {metric: [{ticker, gap_after, gap_before, days}]}; empty == clean.

    WARN, not raise: production ingest must not be wedged by one irregular name.
    The report prints it loudly; a non-empty result is the actionable signal.
    """
    from datetime import date as _d
    out: dict[str, list[dict]] = {}
    for metric in METRICS:
        s = rows_for(metric, "surprise", fid_to_tk)
        flagged = []
        for tk in tickers:
            fes = sorted({r["fiscalEndDate"] for r in s.get(tk, [])
                          if r.get("fiscalEndDate") and r.get("surpriseAfter") is not None})
            if len(fes) < 3:
                continue
            ds = [_d.fromisoformat(x) for x in fes]
            gaps = [(ds[i + 1] - ds[i]).days for i in range(len(ds) - 1)]
            modal = sorted(gaps)[len(gaps) // 2]          # median cadence
            if modal > 130:                               # not a quarterly reporter
                continue
            for i, g in enumerate(gaps):
                if g >= 1.6 * modal:                      # a skipped interior quarter
                    flagged.append({"ticker": tk, "gap_after": fes[i],
                                    "gap_before": fes[i + 1], "days": g})
        if flagged:
            out[metric] = flagged
    return out


# ---------------------------------------------------------------------------
# FY offsets — derived per ticker, cached
# ---------------------------------------------------------------------------
def derive_offsets(tickers: list[str], fid_to_tk: dict) -> dict[str, int]:
    """Union every ticker's raw rows across metric x kind, majority-vote the FY
    offset. Falls back to the hand-coded _FY_LABEL_OFFSET only when derivation
    yields nothing (no usable records)."""
    per_tk: dict[str, list[dict]] = {t: [] for t in tickers}
    for metric in METRICS:
        for kind in KINDS:
            for tk, rows in rows_for(metric, kind, fid_to_tk).items():
                per_tk.setdefault(tk, []).extend(rows)
    offsets, derived_flags = {}, {}
    for tk in tickers:
        d = derive_fy_offset(per_tk.get(tk, []))
        derived_flags[tk] = d is not None
        offsets[tk] = d if d is not None else _FY_LABEL_OFFSET.get(tk, 0)
    return offsets, derived_flags


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(tickers, metrics, fid_to_tk, offsets):
    as_of = date.today().isoformat()
    all_records, cred = [], {}
    for metric in metrics:
        g = rows_for(metric, "guidance", fid_to_tk)
        s = rows_for(metric, "surprise", fid_to_tk)
        for tk in tickers:
            recs = build_metrics(tk, g.get(tk, []), s.get(tk, []),
                                 metric=metric, as_of=as_of, fy_offset=offsets.get(tk))
            if not recs:
                continue
            all_records.extend(recs)
            c = credibility_score(recs)
            if c:
                cred[f"{tk}:{metric}"] = c
    return all_records, cred


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def _fmt(x, p="{:.1f}"):
    return "—" if x is None else p.format(x)


def report(records, cred, offsets, derived_flags, tickers, metrics):
    print(f"\n=== Store B build: {len(records)} metric rows, "
          f"{len(cred)} credibility (ticker:metric) pairs ===")

    print("\n--- derived FY offsets (note-label year − FactSet fiscalYear) ---")
    for tk in tickers:
        src = "derived" if derived_flags.get(tk) else "fallback"
        print(f"  {tk:>10}: {offsets.get(tk):+d}   ({src})")

    print("\n--- per (ticker, metric) coverage ---")
    by_pair = {}
    for r in records:
        by_pair.setdefault((r["ticker"], r["metric"]), []).append(r)
    for tk in tickers:
        for m in metrics:
            recs = by_pair.get((tk, m), [])
            c = cred.get(f"{tk}:{m}")
            if not recs:
                print(f"  {tk:>10} {m:<10}: no rows (not covered)")
                continue
            judged = [r for r in recs if r.get("beat_vs_guidance") is not None]
            if c and c.get("guides_quantitatively"):
                print(f"  {tk:>10} {m:<10}: {len(recs):>2} rows, {len(judged):>2} judged | "
                      f"hit={_fmt(c['guide_hit_rate'],'{:.0%}')} "
                      f"sandbag={_fmt(c['sandbag_index'],'{:+.3f}')} "
                      f"n={c['n_guided_periods']} {c.get('date_range')}")
            else:
                cb = c.get("consensus_beat_rate") if c else None
                n = c.get("n_consensus_periods") if c else 0
                print(f"  {tk:>10} {m:<10}: {len(recs):>2} rows, NO quant guidance → "
                      f"consensus-beat fallback (beat_rate={_fmt(cb,'{:.0%}')}, n={n})")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", help="comma list; default = T1+T2 universe")
    ap.add_argument("--metrics", help=f"comma list; default = {','.join(METRICS)}")
    ap.add_argument("--dry-run", action="store_true", help="build + report, do NOT write")
    args = ap.parse_args()

    tickers = args.tickers.split(",") if args.tickers else universe()
    metrics = args.metrics.split(",") if args.metrics else METRICS
    _, fid_to_tk = id_maps(tickers)

    offsets, derived_flags = derive_offsets(tickers, fid_to_tk)
    OFFSETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSETS_FILE.write_text(json.dumps(offsets, indent=2, sort_keys=True))

    records, cred = build(tickers, metrics, fid_to_tk, offsets)
    report(records, cred, offsets, derived_flags, tickers, metrics)

    # Coverage guard: interior missing-quarter detector (factset-pull-drop class).
    gaps = coverage_gaps(tickers, fid_to_tk)
    if gaps:
        print("\n⚠️  COVERAGE GAPS — interior missing quarters in the actuals series")
        print("    (pull-drop tell; re-pull the named ticker/metric with frequency='AM')")
        for metric, flagged in gaps.items():
            for f in flagged:
                print(f"    {f['ticker']:>10} {metric:<10}: "
                      f"{f['gap_after']} → {f['gap_before']} ({f['days']}d gap)")
    else:
        print("\n✓ coverage guard: no interior quarter gaps across "
              f"{len(tickers)} tickers × {len(METRICS)} metrics")

    if args.dry_run:
        print("\n[dry-run] no write performed.")
        return
    store = get_metrics_store()
    store.write(records, cred)
    print(f"\n=== wrote to {type(store).__name__} "
          f"(CHUNK_STORE_BACKEND): {len(records)} rows, {len(cred)} cred pairs ===")


if __name__ == "__main__":
    main()
