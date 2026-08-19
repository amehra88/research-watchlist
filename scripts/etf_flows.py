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

from etfflows import build, factset_flows, fear_greed, lookthrough, render, store  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEDGER = os.path.join(REPO_ROOT, "state", "etf_flows.jsonl")
TRIGGER_STATE = os.path.join(REPO_ROOT, "state", "etf_flows_triggers.json")
FG_CACHE = os.path.join(REPO_ROOT, "state", "fear_greed.json")
LOOKTHROUGH_CACHE = os.path.join(REPO_ROOT, "state", "etf_lookthrough.json")
# The /root/ws scraper's daily holdings, which supply the BCTK side of the intersection.
WS_HOLDINGS_DB = "/root/ws/data/etf_holdings.db"
UNIVERSE = os.path.join(REPO_ROOT, "config", "etf_universe.yaml")
LOG_DIR = os.path.join(REPO_ROOT, "logs")
NOTES_DIR = os.path.join(REPO_ROOT, "notes", "flows")


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)


def ledger_path(args) -> str:
    return args.ledger or LEDGER


def wanted(args, uni) -> set[str] | None:
    """Parse --tickers once, validating against the WHOLE universe.

    Validation must not happen per tier sublist: a trigger-tier name is legitimately absent
    from the context list, and checking against that sublist would reject it as unknown.
    A typo'd ticker still fails loudly, because silently fetching nothing looks exactly like
    an ETF with no flows.
    """
    if not args.tickers:
        return None
    want = {t.strip().upper() for t in args.tickers.split(",") if t.strip()}
    unknown = sorted(want - set(uni.tickers))
    if unknown:
        raise SystemExit(f"ERROR: not in the universe: {', '.join(unknown)}")
    return want


def subset(want: set[str] | None, tickers: list[str]) -> list[str]:
    """Filter one list by an already-validated selection, preserving universe order."""
    return tickers if want is None else [t for t in tickers if t in want]


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
    tickers = subset(wanted(args, uni), uni.tickers)
    end = args.end or date.today().isoformat()

    runner = factset_flows.make_runner(REPO_ROOT)
    total_failed: set[str] = set()

    for series in ("flows", "prices", "aum"):
        # AUM NEEDS ITS OWN, WIDER WINDOW. Anchors exist only on month-end dates, so a 10-day
        # lookback returns zero rows on the ~19 trading days a month that are not near a month
        # boundary — a wasted `claude -p` call — and worse, a new month's anchor is missed
        # entirely unless a fetch happens to straddle it. A missing anchor silently degrades
        # the flow/AUM denominator for every subsequent day, so this window must always
        # contain at least one month end.
        lookback = args.aum_lookback if series == "aum" else args.lookback
        start = args.start or (date.fromisoformat(end) - timedelta(days=lookback)).isoformat()
        calls = factset_flows.estimate_calls(len(tickers), start, end, series)
        log(f"{series}: {len(tickers)} tickers {start}..{end} (~{calls} calls)")
        if args.dry_run:
            continue
        recs, failed = factset_flows.fetch_range(tickers, series, start, end, runner,
                                                 on_progress=log)
        n = store.append(ledger_path(args), recs, series)
        log(f"{series}: stored {n} rows, {len(failed)} failed tickers")
        total_failed.update(failed)

    if total_failed:
        # Reported, never silent — a partial fetch that looks clean is how a section quietly
        # starts under-reporting.
        log(f"WARNING: {len(total_failed)} tickers failed: {', '.join(sorted(total_failed))}")

    if not args.dry_run and not args.no_lookthrough:
        do_fetch_lookthrough(args, uni)
    return 0


def do_fetch_lookthrough(args, uni) -> None:
    """Pre-fetch Phase 2 inputs for whatever alerted, during the 05:30 window.

    WHY HERE AND NOT IN --report: look-through needs holdings and volume, which are
    `claude -p` calls, and --report runs at 07:00 inside run_daily.sh where LLM work is
    forbidden (the 2026-08-13 quota incident). So the fetch stage resolves which ETFs alerted
    and caches the RAW inputs; --report re-derives the decomposition from that cache with no
    LLM calls at all.

    The alert evaluation here is throwaway — it runs against a COPY of the hysteresis state
    and the result is discarded, so a fetch can never consume an alert that --report should
    still be able to fire.
    """
    state = store.load(ledger_path(args))
    as_of = store.latest_date(state, "flows")
    if not as_of:
        return

    trig_state = _load_json(TRIGGER_STATE, {})
    probe, _discarded = build.build_report(state, uni, as_of, dict(trig_state), "")
    etfs = lookthrough.etfs_to_decompose(probe["alerts"], uni)
    if not etfs:
        log("look-through: no alerting ETF to decompose")
        _save_json(LOOKTHROUGH_CACHE, {"as_of": as_of, "holdings": [], "adv": []})
        return

    log(f"look-through: decomposing {', '.join(etfs)}")
    try:
        h_runner = lookthrough.make_holdings_runner(REPO_ROOT)
        holdings_raw = h_runner(etfs[:10], topn=25)
    except Exception as exc:                       # noqa: BLE001 — degrade, never fail the fetch
        log(f"look-through: holdings fetch failed: {exc}")
        return

    parsed = lookthrough.parse_holdings(holdings_raw)
    names: list[str] = []
    for entry in parsed.values():
        for h in entry["holdings"][:lookthrough.MAX_NAMES]:
            if h["ticker"] not in names:
                names.append(h["ticker"])

    adv_raw: list[dict] = []
    if names:
        end = args.end or date.today().isoformat()
        start = (date.fromisoformat(end)
                 - timedelta(days=lookthrough.ADV_WINDOW_DAYS)).isoformat()
        try:
            a_runner = lookthrough.make_adv_runner(REPO_ROOT)
            for i in range(0, len(names), lookthrough.MAX_ADV_IDS):
                adv_raw.extend(a_runner(names[i:i + lookthrough.MAX_ADV_IDS], start, end))
        except Exception as exc:                   # noqa: BLE001
            # Without ADV the decomposition still renders — days-of-ADV shows '?' rather
            # than a fabricated 0.
            log(f"look-through: ADV fetch failed, days-of-ADV will be unavailable: {exc}")

    _save_json(LOOKTHROUGH_CACHE,
               {"as_of": as_of, "holdings": holdings_raw, "adv": adv_raw})
    log(f"look-through: cached {len(holdings_raw)} holding rows, {len(adv_raw)} price rows")


# ── backfill ──────────────────────────────────────────────────────────────────

def do_backfill(args) -> int:
    """The one-shot. Loud about cost, because that cost is the known failure mode."""
    uni = build.load_universe(UNIVERSE)
    end = args.end or date.today().isoformat()
    want = wanted(args, uni)
    trig = subset(want, uni.trigger_tickers())
    ctx = subset(want, uni.context_tickers())

    trig_start = args.start or (date.fromisoformat(end) - timedelta(days=365 * 3)).isoformat()
    ctx_start = (date.fromisoformat(end) - timedelta(days=365)).isoformat()
    price_start = (date.fromisoformat(end) - timedelta(days=365)).isoformat()
    all_t = subset(want, uni.tickers)

    plan = [(series, tks, s, e) for series, tks, s, e in (
        ("flows", trig, trig_start, end),
        ("flows", ctx, ctx_start, end),
        ("aum", all_t, trig_start, end),
        ("prices", all_t, price_start, end),
    ) if tks]

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
        n = store.append(ledger_path(args), recs, series)
        log(f"{series}: stored {n} rows, {len(f)} failed")
        failed.update(f)

    state = store.load(ledger_path(args))
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
    if args.tickers:
        uni = uni.restrict(subset(wanted(args, uni), uni.tickers))
    state = store.load(ledger_path(args))

    as_of = args.as_of or store.latest_date(state, "flows")
    if not as_of:
        log("ERROR: no flow data in the ledger. Run --backfill or --fetch first.")
        return 1

    fg, fg_status = fear_greed.get(FG_CACHE)
    fg_line = fear_greed.render_line(fg, fg_status)

    trig_state = _load_json(TRIGGER_STATE, {})
    report, new_trig = build.build_report(state, uni, as_of, trig_state, fg_line)

    # Phase 2, recomputed from the cache the fetch stage wrote. Pure computation — no LLM
    # calls in the 07:00 path. A cache from a different flow date is ignored rather than
    # rendered against today's alerts, which would attribute stale weights to a fresh move.
    cache = _load_json(LOOKTHROUGH_CACHE, {})
    if not report["alerts"]:
        report["lookthrough_note"] = "no alert today, nothing to decompose."
    elif not cache:
        report["lookthrough_note"] = ("not available — no cached holdings. Run --fetch "
                                      "(which pre-fetches it) before --report.")
    elif cache.get("as_of") != as_of:
        report["lookthrough_note"] = (f"skipped — cached holdings are for "
                                      f"{cache.get('as_of')}, not {as_of}.")
        log(f"look-through cache is for {cache.get('as_of')}, not {as_of} — skipping")
    else:
        report["lookthrough"] = lookthrough.analyse(
            report["alerts"], uni,
            lookthrough.parse_holdings(cache.get("holdings") or []),
            lookthrough.compute_adv(cache.get("adv") or []),
            lookthrough.bctk_holdings(WS_HOLDINGS_DB),
        )
        if not report["lookthrough"]:
            report["lookthrough_note"] = ("no alerting ETF was eligible (synthetic funds are "
                                          "never decomposed).")

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
    # notes/ convention is {YYYYMMDD}-..., not the ISO form used everywhere else here.
    # NOTE: notes/flows/ is a non-ticker directory, so indexing is subject to the open
    # chunker gap (memory: chunker-v3-awareness-gap) — this file is written to disk, but
    # do not assume it is searchable in pg until that is fixed.
    note_path = os.path.join(NOTES_DIR, f"{as_of.replace('-', '')}-flows.md")

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

    state = store.load(ledger_path(args))
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
    p.add_argument("--tickers",
                   help="comma-separated subset of the universe (smoke tests, or re-fetching "
                        "a failed subset without repeating a whole backfill)")
    p.add_argument("--ledger", help="alternate state ledger path (keeps a smoke test out of "
                                    "the production history)")
    p.add_argument("--no-lookthrough", action="store_true",
                   help="skip the Phase 2 pre-fetch during --fetch")
    p.add_argument("--lookback", type=int, default=10,
                   help="days of history for --fetch (default 10, covers a long weekend)")
    p.add_argument("--aum-lookback", type=int, default=45,
                   help="days of history for the AUM series (default 45 — must always span "
                        "a month end, since anchors exist only on month-end dates)")
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
