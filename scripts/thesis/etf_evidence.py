#!/usr/bin/env python3
"""etf_evidence.py — peer-ETF trim/exit clusters as thesis evidence (RIS5 A3, amendment v1.1).

Carried over from A4: task-4-report.md deferred this item because
`state/etf_trades/<date>.json` did not exist anywhere in the repo and "building a consumer
would mean inventing a producer contract nobody has specified." A3 now owns and builds
BOTH the producer (`scripts/portal/etf_trades_archive.py`) and this consumer.

Rule (amendment v1.1): when >= MIN_PEER_ETFS DISTINCT peer ETFs trimmed or exited a name in
the archived window with ZERO adds/new positions, attach a CHALLENGE strength-1 evidence
row (source `peer_etf`, family `"other managers"`) to that ticker's competitive-advantage
assumptions, via the SAME route insider clusters use:
`thesis.insider_pull.investor_assumptions(fm, direction="challenge")` (routes (a)
competitive-advantage-derived, (b) `competition_slugs`, (c) bearish-polarity themes — see
A4's fix 0 in task-4-report.md).

DISTINCT ETFS, not entries: the archive's `by_ticker` list has one row per (date, etf,
action) inside the window, so the same ETF trimming on three separate archived days must
count as ONE manager, not three — the single likeliest bug in a naive implementation
(flagged explicitly during this task's own pre-build review; see test_distinct_etfs_not_
entries_counted below).

Challenge-only, no symmetric confirm for >= N adds: A4's ORIGINAL brief bullet asked for
both directions, but THIS task's amendment v1.1 (the actual governing spec for A3) only
specifies the challenge half. That is the scope actually built here — noted for the
coordinator to request the confirm half separately if wanted.

Evidence pipeline (identical to insider_pull.py's own main(), just a different source):
write is idempotent per (ticker, source_id, assumption_id) via
thesis.match_evidence.LOG's existing dedup key, so re-running against the same day's
archive adds nothing new.

    python3 scripts/thesis/etf_evidence.py                       # today's archive, live write
    python3 scripts/thesis/etf_evidence.py --date 2026-09-17 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))
from thesis import thesis_io as tio                             # noqa: E402
from thesis.insider_pull import investor_assumptions             # noqa: E402

ARCHIVE_DIR = REPO / "state" / "etf_trades"

# "config" per the amendment -- a module constant, mirroring insider_pull.py's own
# MIN_INSIDERS convention (that module's docstring/tests use the identical pattern).
# ACCEPTED as-is by coordinator review (fix round 1) -- no change needed here.
MIN_PEER_ETFS = 3

TRIM_ACTIONS = {"trimmed", "exit"}     # etf_trades._ACTION_LABEL values
ADD_ACTIONS = {"added", "new"}


def load_archive(d: str, archive_dir: Path = ARCHIVE_DIR) -> dict:
    """{} (not an error) when no archive exists for `d` yet -- a missing archive day
    (weekend, or the archiver hasn't run yet) is routine, not a failure."""
    p = Path(archive_dir) / f"{d}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _cluster_start(rows: list[dict], min_peer_etfs: int) -> str | None:
    """The earliest date, walking the ticker's trim rows in chronological order, at which
    the CUMULATIVE distinct-trimmer count first reaches min_peer_etfs -- the cluster's own
    identity, independent of which day the archive happens to be read on. None if the rows
    never cross the bar (caller only calls this once they already know they do)."""
    trims = sorted((r for r in rows if r.get("action") in TRIM_ACTIONS),
                   key=lambda r: r.get("date") or "")
    seen: set[str] = set()
    for r in trims:
        seen.add(r["etf"])
        if len(seen) >= min_peer_etfs:
            return r["date"]
    return None


def peer_trim_clusters(by_ticker: dict[str, list[dict]],
                       min_peer_etfs: int = MIN_PEER_ETFS) -> dict[str, dict]:
    """{ticker: {trimmers: [etf,...] sorted, n: int, cluster_start: date}} for tickers with
    >= min_peer_etfs DISTINCT ETFs trimming/exiting and ZERO ETFs adding/opening new, over
    the archive's own window. `n` is len(trimmers) -- a set, so a repeat-trimming ETF
    counts once. `cluster_start` (fix round 1, coordinator review) is the date the
    min_peer_etfs-th DISTINCT trimmer first appeared -- the cluster's stable identity, used
    downstream as the evidence row's dedup key instead of the run's own as_of date. A 4th+
    trimmer joining later does NOT move cluster_start (see
    test_cluster_start_unaffected_by_a_4th_trimmer_joining_later): the cluster's identity
    is when it first qualified, not its current size."""
    out: dict[str, dict] = {}
    for tk, rows in (by_ticker or {}).items():
        trimmers = {r["etf"] for r in rows if r.get("action") in TRIM_ACTIONS}
        adders = {r["etf"] for r in rows if r.get("action") in ADD_ACTIONS}
        if len(trimmers) >= min_peer_etfs and not adders:
            out[tk] = {"trimmers": sorted(trimmers), "n": len(trimmers),
                      "cluster_start": _cluster_start(rows, min_peer_etfs)}
    return out


def evidence_rows(clusters: dict[str, dict], theses: dict[str, dict], as_of: str,
                  covered_days: int) -> list[dict]:
    """`source_id` is keyed on the CLUSTER's own start date (`cluster_start`), not `as_of`
    (fix round 1, coordinator review) -- a daily cron over a 14-day trailing window would
    otherwise re-key the same persisting cluster on every run's own as_of date and
    re-attach it daily, inflating pressure.challenge without any new information. Keying on
    cluster_start makes thesis.match_evidence's existing ticker|source_id|assumption_id
    dedup treat day 2..14 of the SAME cluster as a no-op, while a cluster that later lapses
    and re-forms (its old trims aged out of the window, a wholly new set crosses the bar)
    naturally gets a new, later cluster_start and is correctly treated as a new episode.
    `date` (the evidence row's own observed-on date) stays `as_of` -- only the dedup key
    changed, not when the evidence is recorded as having been seen."""
    rows = []
    for t, c in sorted(clusters.items()):
        fm = theses.get(t)
        if not fm:
            continue
        start = c["cluster_start"]
        why = (f"{c['n']} peer ETFs ({', '.join(c['trimmers'])}) trimmed/exited {t} with "
              f"0 adds, since {start} (through {as_of}, {covered_days} archived report day(s))")
        for aid in investor_assumptions(fm, direction="challenge"):
            rows.append({
                "source": "peer_etf", "source_id": f"peer_etf:{t}:{start}",
                "ref": "portal.etf_trades (ws ETF-holdings-change report)",
                "date": as_of, "title": "peer ETF trim cluster", "assumption_id": aid,
                "direction": "challenge", "strength": 1, "why": why, "quote": "",
                "cross_ticker": False, "ticker": t, "family": "other managers",
            })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="archive date to read (default: today)")
    ap.add_argument("--archive-dir", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    as_of = a.date or date.today().isoformat()
    archive_dir = Path(a.archive_dir) if a.archive_dir else ARCHIVE_DIR
    archived = load_archive(as_of, archive_dir)
    if not archived:
        print(f"no archive for {as_of} at {archive_dir} -- nothing to do")
        return 0

    clusters = peer_trim_clusters(archived.get("by_ticker") or {})
    covered_days = len(archived.get("days") or [])
    tickers = sorted(clusters)
    theses = {t: fm for t in tickers if (fm := tio.load(t))}
    ev = evidence_rows(clusters, theses, as_of, covered_days)

    print(f"clusters: {len(clusters)} ticker(s) with >= {MIN_PEER_ETFS} distinct peer trims, "
         f"0 adds ({sum(1 for t in clusters if t not in theses)} skipped, no _thesis.md)")

    if a.dry_run:
        print(json.dumps({"clusters": clusters, "evidence": ev}, indent=1, default=str))
        return 0

    from thesis.match_evidence import CHANGES, LOG, _append, _read_log
    log = _read_log()
    existing = {f"{r['ticker']}|{r['source_id']}|{r.get('assumption_id')}" for r in log}
    ts = datetime.now(timezone.utc).isoformat()
    new = [dict(r, ts=ts) for r in ev
          if f"{r['ticker']}|{r['source_id']}|{r['assumption_id']}" not in existing]
    _append(LOG, new)
    log += new
    for t in sorted({r["ticker"] for r in new}):
        fm = theses[t]
        tio.recompute_pressure(fm, [r for r in log if r["ticker"] == t], date.today())
        if fm["_changes"]:
            _append(CHANGES, [dict(c, ts=ts, ticker=t, kind="status") for c in fm["_changes"]])
        tio.save(t, fm)
    print(f"DONE clusters={len(clusters)} evidence_rows={len(new)} "
         f"tickers_updated={len({r['ticker'] for r in new})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
