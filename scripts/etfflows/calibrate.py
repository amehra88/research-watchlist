"""
calibrate — replay backfilled history through the REAL trigger logic and count what fires.

This exists because the shipped thresholds (STANDALONE_SIGMA, CORROBORATED_SIGMA) were chosen
a priori and the spec gates the email on measuring them. The target is ~1 alert per week
across the trigger tier: often enough to be worth reading, rare enough that the reader does
not learn to skip the section.

TWO THINGS THIS DELIBERATELY DOES NOT DO:

1. It does not re-implement the trigger rules. It calls triggers.evaluate() day by day with
   the same hysteresis state machine production uses, so what it counts is what would have
   shipped — including the re-arm band, the cooldown, and the one-alert-per-ticker collapse.
   A calibrator with its own copy of the rules calibrates a system nobody runs.

2. It does not count alert-DAYS. With hysteresis a sustained move fires once and then stays
   disarmed, so the number below is EPISODES. That is the honest unit: without hysteresis a
   single 63d crowding episode would count ~20 times and tempt you into raising the threshold
   until real events stop firing.

Usage:
    python3 scripts/etfflows/calibrate.py [--ledger PATH] [--days N]
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etfflows import HORIZONS, LONG_HORIZON, MIN_BASELINE_OBS, SHORT_HORIZON  # noqa: E402
from etfflows import build, metrics as m, store, triggers as tg  # noqa: E402

TRADING_DAYS_PER_WEEK = 5.0


def precompute(state, uni, horizons=HORIZONS) -> tuple[list[str], dict]:
    """Per-ticker, per-horizon readings at EVERY date, using the production pipeline.

    Returns (all_dates, {ticker: {horizon: {date: partial-Reading-kwargs}}}).

    The z-score at index i uses only data strictly before i, exactly as build.ticker_metrics
    does for a single day — so a replayed day cannot see its own future.
    """
    per: dict[str, dict[int, dict[str, dict]]] = {}
    all_dates: set[str] = set()

    for t in uni.tickers:
        dates, flows = store.series_for(state, "flows", t)
        if not dates:
            continue
        nav_by_date = dict(zip(*store.series_for(state, "prices", t)))
        navs = [nav_by_date.get(d) for d in dates]
        anchors = store.month_end_aum(state, t)
        all_dates.update(dates)
        per[t] = {}

        for h in horizons:
            sums = m.rolling_sums(flows, h)
            denom = m.step_aum_series(dates, anchors, h)
            bps = [m.to_bps(sums[i], denom[i]) for i in range(len(dates))]
            by_date: dict[str, dict] = {}

            baseline: list[float] = []
            for i, d in enumerate(dates):
                cur = bps[i]
                if cur is not None and len(baseline) >= MIN_BASELINE_OBS:
                    z = m.robust_z(cur, baseline)
                    ret = m.window_return(navs[: i + 1], h)
                    by_date[d] = {
                        "z": z.z, "percentile": z.percentile, "degraded": z.degraded,
                        "degrade_reason": z.reason, "flow_usd": sums[i], "flow_bps": cur,
                        "divergence": m.divergence(sums[i], ret),
                    }
                if cur is not None:
                    baseline.append(cur)      # grow AFTER use — never see your own value
            per[t][h] = by_date

    return sorted(all_dates), per


def replay(dates, per, uni, standalone, corroborated, max_alerts,
           pctile_gate: float | None = None) -> tuple[list, int]:
    """Walk the history day by day through the real evaluator. Returns (alerts, n_days).

    `pctile_gate` set -> percentile-gate mode at that percentile; None -> sigma mode.
    Module constants are patched and restored so the calibrator always exercises the shipped
    code path rather than a parallel implementation of the rules.
    """
    saved = (tg.STANDALONE_SIGMA, tg.CORROBORATED_SIGMA,
             tg.USE_PERCENTILE_GATE, tg.GATE_PERCENTILE)
    tg.STANDALONE_SIGMA, tg.CORROBORATED_SIGMA = standalone, corroborated
    tg.USE_PERCENTILE_GATE = pctile_gate is not None
    if pctile_gate is not None:
        tg.GATE_PERCENTILE = pctile_gate
    try:
        state: dict = {}
        fired = []
        counted = 0
        for d in dates:
            readings = []
            for t, by_h in per.items():
                for h, by_date in by_h.items():
                    r = by_date.get(d)
                    if r is None:
                        continue
                    readings.append(tg.Reading(
                        ticker=t, horizon=h, tier=uni.tier.get(t, "context"),
                        synthetic=uni.synthetic(t), min_history_ok=uni.min_history_ok(t), **r))
            if not readings:
                continue
            counted += 1
            alerts, state, _ = tg.evaluate(readings, state, d, max_alerts=max_alerts)
            fired.extend((d, a) for a in alerts)
        return fired, counted
    finally:
        (tg.STANDALONE_SIGMA, tg.CORROBORATED_SIGMA,
         tg.USE_PERCENTILE_GATE, tg.GATE_PERCENTILE) = saved


def main() -> int:
    ap = argparse.ArgumentParser()
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--ledger", default=os.path.join(repo, "state", "etf_flows.jsonl"))
    ap.add_argument("--universe", default=os.path.join(repo, "config", "etf_universe.yaml"))
    ap.add_argument("--max-alerts", type=int, default=6)
    args = ap.parse_args()

    state = store.load(args.ledger)
    uni = build.load_universe(args.universe)
    cov = store.coverage(state, "flows")
    print(f"ledger: {len(cov)} tickers with flow data")
    if not cov:
        print("EMPTY LEDGER — run --backfill first.")
        return 1

    dates, per = precompute(state, uni, HORIZONS)
    evaluable = {t for t, by_h in per.items() if any(by_h[h] for h in by_h)}
    trig = [t for t in uni.trigger_tickers() if t in evaluable]
    print(f"tickers with a usable baseline: {len(evaluable)} "
          f"({len(trig)} of {len(uni.trigger_tickers())} trigger-tier)")

    missing = sorted(set(uni.trigger_tickers()) - evaluable)
    if missing:
        # Never silent: a trigger name with no baseline can never alert, and if that is
        # unexpected it is a data bug, not a quiet non-event.
        print(f"  trigger-tier names with NO usable baseline: {', '.join(missing)}")

    print("\nEPISODES PER WEEK by threshold (target ~1.0)")
    print("=" * 62)
    print(f"{'standalone':>10} {'corrob':>8} {'episodes':>9} {'per week':>9}  {'span':>6}")
    print("-" * 62)

    results = []
    # corroborated == standalone disables the lower tier entirely (the elif can never fire),
    # so those rows measure a SINGLE-THRESHOLD design against the two-tier one.
    for standalone in (3.0, 4.0, 5.0, 6.0, 7.0, 8.0):
        # sorted(set(...)) so `standalone` appearing in the fixed list does not print the
        # single-threshold row twice.
        for corroborated in sorted({2.0, 3.0, 4.0, standalone}):
            if corroborated > standalone:
                continue
            fired, n_days = replay(dates, per, uni, standalone, corroborated, args.max_alerts)
            weeks = max(1e-9, n_days / TRADING_DAYS_PER_WEEK)
            per_week = len(fired) / weeks
            results.append((standalone, corroborated, len(fired), per_week, n_days))
            print(f"{standalone:>10.1f} {corroborated:>8.1f} {len(fired):>9} "
                  f"{per_week:>9.2f}  {n_days:>6}")

    best = min(results, key=lambda r: abs(r[3] - 1.0))
    print("-" * 62)
    print(f"closest to 1/week: standalone={best[0]}, corroborated={best[1]} "
          f"-> {best[3]:.2f}/week")

    # The alternative gate. A percentile is comparable across funds and directly readable
    # ("top 0.5% of this ETF's own history"), which a MAD-scaled sigma is not when the
    # underlying distribution is this heavy-tailed.
    print("\nPERCENTILE GATE (distribution-free, no corroboration tier)")
    print("=" * 62)
    print(f"{'pctile':>10} {'episodes':>9} {'per week':>9}")
    print("-" * 62)
    pct_results = []
    for gate in (99.0, 99.3, 99.5, 99.7, 99.8, 99.9):
        fired_p, n_days = replay(dates, per, uni, 3.0, 2.0, args.max_alerts, pctile_gate=gate)
        weeks = max(1e-9, n_days / TRADING_DAYS_PER_WEEK)
        pct_results.append((gate, len(fired_p), len(fired_p) / weeks))
        print(f"{gate:>10.2f} {len(fired_p):>9} {len(fired_p) / weeks:>9.2f}")
    best_p = min(pct_results, key=lambda r: abs(r[2] - 1.0))
    print("-" * 62)
    print(f"closest to 1/week: GATE_PERCENTILE={best_p[0]} -> {best_p[2]:.2f}/week")

    fired, _ = replay(dates, per, uni, best[0], best[1], args.max_alerts)
    by_ticker = Counter(a.ticker for _, a in fired)
    by_horizon = Counter(a.horizon for _, a in fired)

    # HOW alerts qualify matters as much as how many. If most fire via the corroborated path,
    # the effective threshold is the LOWER number, and the two corroborators are both weak:
    # the other horizon overlaps this one (5d sits inside 63d), and flow-vs-price divergence
    # is close to a coin flip. A design where the lower tier dominates is really a
    # single-threshold design wearing a disguise.
    by_basis = Counter(a.basis for _, a in fired)
    by_corro = Counter("other-horizon" if "also" in a.corroboration else "divergence"
                       for _, a in fired if a.basis == "corroborated")
    print(f"\nqualifying path: {dict(by_basis)}")
    if by_corro:
        print(f"  corroborated via: {dict(by_corro)}")
    print(f"\nAt that setting: {len(fired)} episodes across {len(by_ticker)} tickers")
    print("  most frequent:", ", ".join(f"{t}({n})" for t, n in by_ticker.most_common(8)))
    print(f"  by horizon: {SHORT_HORIZON}d={by_horizon.get(SHORT_HORIZON, 0)}, "
          f"{LONG_HORIZON}d={by_horizon.get(LONG_HORIZON, 0)}")
    print("\n  last 5 episodes:")
    for d, a in fired[-5:]:
        print(f"    {d}  {a.ticker:<5} {a.horizon:>2}d {a.direction:<7} "
              f"{a.z:+.1f}σ  [{a.basis}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
