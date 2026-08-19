#!/usr/bin/env python3
"""
etf_flows — ETF flow & crowding monitor.

Spec: docs/specs/2026-08-19-etf-flow-crowding-monitor.md

FETCH AND RENDER ARE DECOUPLED ON PURPOSE. run_daily.sh records that on 2026-08-13 two
`claude -p`-heavy jobs inside one rolling 5-hour window exhausted the subscription and the
news digest shipped 40 of 256 stories. So:

    --fetch    05:30 ET weekdays, a handful of `claude -p` calls, appends to the ledger
    --report   inside run_daily.sh at 07:00, ZERO LLM calls, pure computation over state

Never add `claude -p` work to the 06:45-08:15 window.

    --backfill  ONE-SHOT, ~95 `claude -p` calls. Prints the estimate and refuses to run
                without --yes. Run it well outside the morning window.

Usage:
    python3 scripts/etf_flows.py --fetch
    python3 scripts/etf_flows.py --report
    python3 scripts/etf_flows.py --dry-run --report
    python3 scripts/etf_flows.py --backfill --start 2023-08-19 --yes
    python3 scripts/etf_flows.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etfflows import build, factset_flows, fear_greed, render, store  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEDGER = os.path.join(REPO_ROOT, "state", "etf_flows.jsonl")
TRIGGER_STATE = os.path.join(REPO_ROOT, "state", "etf_flows_triggers.json")
FG_CACHE = os.path.join(REPO_ROOT, "state", "fear_greed.json")
UNIVERSE = os.path.join(REPO_ROOT, "config", "etf_universe.yaml")
LOG_DIR = os.path.join(REPO_ROOT, "logs")
NOTES_DIR = os.path.join(REPO_ROOT, "notes", "flows")


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)


def _load_json(path, default):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def _save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
    os.replace(tmp, path)


# ── fetch ─────────────────────────────────────────────────────────────────────

def do_fetch(args) -> int:
    """Incremental daily pull. Small by construction: a short lookback, not a re-backfill."""
    uni = build.load_universe(UNIVERSE)
    tickers = uni.tickers
    end = args.end or date.today().isoformat()
    start = args.start or (date.fromisoformat(end) - timedelta(days=args.lookback)).isoformat()

    runner = factset_flows.make_runner(REPO_ROOT)
    total_failed: set[str] = set()

    for series in ("flows", "prices", "aum"):
        calls = factset_flows.estimate_calls(len(tickers), start, end, series)
        log(f"{series}: {len(tickers)} tickers {start}..{end} (~{calls} calls)")
        if args.dry_run:
            continue
        recs, failed = factset_flows.fetch_range(tickers, series, start, end, runner,
                                                 on_progress=log)
        n = store.append(LEDGER, recs, series)
        log(f"{series}: stored {n} rows, {len(failed)} failed tickers")
        total_failed.update(failed)

    if total_failed:
        # Reported, never silent — a partial fetch that looks clean is how a section quietly
        # starts under-reporting.
        log(f"WARNING: {len(total_failed)} tickers failed: {', '.join(sorted(total_failed))}")
    return 0


# ── backfill ──────────────────────────────────────────────────────────────────

def do_backfill(args) -> int:
    """The one-shot. Loud about cost, because that cost is the known failure mode."""
    uni = build.load_universe(UNIVERSE)
    end = args.end or date.today().isoformat()
    trig, ctx = uni.trigger_tickers(), uni.context_tickers()

    trig_start = args.start or (date.fromisoformat(end) - timedelta(days=365 * 3)).isoformat()
    ctx_start = (date.fromisoformat(end) - timedelta(days=365)).isoformat()
    price_start = (date.fromisoformat(end) - timedelta(days=365)).isoformat()
    all_t = uni.tickers

    plan = [
        ("flows", trig, trig_start, end),
        ("flows", ctx, ctx_start, end),
        ("aum", all_t, trig_start, end),
        ("prices", all_t, price_start, end),
    ]

    print("\nBACKFILL PLAN")
    print("=" * 68)
    total = 0
    for series, tks, s, e in plan:
        c = factset_flows.estimate_calls(len(tks), s, e, series)
        total += c
        print(f"  {series:<7} {len(tks):>3} tickers  {s}..{e}  ~{c:>3} calls")
    print("=" * 68)
    print(f"  TOTAL ~{total} `claude -p` calls.")
    print("  Each carries ~29.7K fixed cache-creation tokens (docs/cost-model.md).")
    print("  Do NOT run this in the 06:45-08:15 window — see run_daily.sh, 2026-08-13.\n")

    if not args.yes:
        print("Refusing to run without --yes. Re-run with --yes to proceed.")
        return 2

    runner = factset_flows.make_runner(REPO_ROOT)
    failed: set[str] = set()
    for series, tks, s, e in plan:
        log(f"=== {series} {len(tks)} tickers {s}..{e} ===")
        recs, f = factset_flows.fetch_range(tks, series, s, e, runner, on_progress=log)
        n = store.append(LEDGER, recs, series)
        log(f"{series}: stored {n} rows, {len(f)} failed")
        failed.update(f)

    state = store.load(LEDGER)
    for series in ("flows", "prices", "aum"):
        cov = store.coverage(state, series)
        if cov:
            lo = min(cov.values())
            log(f"{series}: {len(cov)} tickers, min {lo} obs, max {max(cov.values())} obs")
    if failed:
        log(f"WARNING: failed tickers: {', '.join(sorted(failed))}")
    return 0


# ── report ────────────────────────────────────────────────────────────────────

def do_report(args) -> int:
    """Zero LLM calls. Pure computation over stored state."""
    uni = build.load_universe(UNIVERSE)
    state = store.load(LEDGER)

    as_of = args.as_of or store.latest_date(state, "flows")
    if not as_of:
        log("ERROR: no flow data in the ledger. Run --backfill or --fetch first.")
        return 1

    fg, fg_status = fear_greed.get(FG_CACHE)
    fg_line = fear_greed.render_line(fg, fg_status)

    trig_state = _load_json(TRIGGER_STATE, {})
    report, new_trig = build.build_report(state, uni, as_of, trig_state, fg_line)

    main = render.render_main(report)
    table = render.render_table(report)

    if args.dry_run:
        print(main)
        print("=" * 86)
        print(table)
        log(f"DRY RUN — nothing written. as_of={as_of}, "
            f"{len(report['alerts'])} alerts, {len(report['rows'])} rows")
        return 0

    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)
    main_path = os.path.join(LOG_DIR, f"report_etfflows_{as_of}.txt")
    table_path = os.path.join(LOG_DIR, f"report_etfflows_table_{as_of}.txt")
    note_path = os.path.join(NOTES_DIR, f"{as_of}-flows.md")

    with open(main_path, "w") as fh:
        fh.write(main)
    with open(table_path, "w") as fh:
        fh.write(table)
    with open(note_path, "w") as fh:
        fh.write(render.render_note(report))

    # Persist hysteresis state ONLY on a real run — a dry run must not consume an alert.
    _save_json(TRIGGER_STATE, new_trig)

    log(f"wrote {main_path}")
    log(f"wrote {table_path}")
    log(f"wrote {note_path}")
    log(f"as_of={as_of}, {len(report['alerts'])} alerts, "
        f"{report['suppressed']} suppressed, {len(report['rows'])} rows")
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────

def do_selftest(args) -> int:
    """Cheap live checks that touch no LLM: CNN reachability and universe integrity."""
    ok = True

    uni = build.load_universe(UNIVERSE)
    trig, ctx = uni.trigger_tickers(), uni.context_tickers()
    print(f"universe: {len(trig)} trigger + {len(ctx)} context = {len(uni.tickers)}")
    if set(trig) & set(ctx):
        print(f"  FAIL overlapping tiers: {set(trig) & set(ctx)}")
        ok = False
    if len(uni.tickers) != len(trig) + len(ctx):
        print("  FAIL duplicate tickers across sleeves")
        ok = False

    fg, status = fear_greed.get(FG_CACHE)
    print(f"fear&greed: status={status}")
    print(f"  {fear_greed.render_line(fg, status)}")
    if status == "none":
        print("  FAIL no reading and no cache")
        ok = False

    state = store.load(LEDGER)
    latest = store.latest_date(state, "flows")
    cov = store.coverage(state, "flows")
    print(f"ledger: {len(cov)} tickers with flow data, latest={latest}")
    if not cov:
        print("  NOTE ledger is empty — run --backfill (see the plan it prints first)")

    print("OK" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fetch", action="store_true", help="incremental daily pull (05:30)")
    p.add_argument("--report", action="store_true", help="render from state (07:00, no LLM)")
    p.add_argument("--backfill", action="store_true", help="one-shot history pull (~95 calls)")
    p.add_argument("--selftest", action="store_true", help="offline/cheap integrity checks")
    p.add_argument("--dry-run", action="store_true", help="compute and print, write nothing")
    p.add_argument("--yes", action="store_true", help="confirm an expensive backfill")
    p.add_argument("--start", help="YYYY-MM-DD")
    p.add_argument("--end", help="YYYY-MM-DD")
    p.add_argument("--as-of", help="report for this flow date instead of the newest")
    p.add_argument("--lookback", type=int, default=10,
                   help="days of history for --fetch (default 10, covers a long weekend)")
    args = p.parse_args()

    if args.backfill:
        return do_backfill(args)
    if args.fetch:
        return do_fetch(args)
    if args.report:
        return do_report(args)
    if args.selftest:
        return do_selftest(args)
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
