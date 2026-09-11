#!/usr/bin/env python3
"""
Lifecycle staging and the Tier 0 lag measurement (spec §6.3).

    lag = first_question_date - first_evidence_date

`first_evidence_date` is the earliest evidence-register row on the same (topic, company) —
an MD&A claim's filed date, or a corprep transcript turn; `first_question_date` is the
earliest ANALYST exchange on it. Positive lag means the company disclosed it before the
street asked — which is the entire premise of the system.

**Tier 0 is a test of that premise, not a demonstration of it.** The spec rests the claim on
one anecdote (Innolight FY2025 → the 2026-06-09 question). This module computes the
distribution over every (topic, company) pair that has both registers, and it deliberately
KEEPS pairs where the question came first: those are the counter-evidence, and dropping or
clamping them would rig the measurement.

It is not a returns backtest, and it must not be read as one. The 62 themes were authored in
2026 with the answers known, and the watchlist is survivorship-selected. Relative timing is
still fair game — topic selection does not bias whether evidence or the question came first —
which is exactly why this is the measurement worth having now.

`append_detections` writes the append-only stage-1 log. In three years the question will be
"when did the system FIRST flag this", and only a value that never moves can answer it.

Ported 2026-09-10 from branch worktree-idea-surfacing-spec (scripts/v3_ingest/lifecycle.py)
onto the P2 topic_map.jsonl row shape: themes is a list of {theme, score}, event_date is on
every row, firm on question rows. The branch's extraction-progress guard is replaced by a
staleness guard (P2 maps the whole corpus in one run; the failure mode now is a map older
than its inputs).
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO_ROOT = Path("/root/research-watchlist")
TOPICS_PATH = REPO_ROOT / "state" / "topics" / "topic_map.jsonl"
EXCHANGES_PATH = REPO_ROOT / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS_PATH = REPO_ROOT / "state" / "evidence" / "claims.jsonl"
DETECTIONS_PATH = REPO_ROOT / "state" / "topics" / "detections.jsonl"

#: stage 4 = "questions on most covered calls". A bare majority is not enough
#: on its own — two names with one asked about is a majority and plainly not
#: "most covered calls" — so breadth is required too.
STAGE4_MIN_TICKERS = 3


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] lifecycle: {msg}", flush=True)


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(str(s)[:10])


def lag_days(first_evidence_date, first_question_date):
    """-> int days, or None if either side is missing. May be NEGATIVE."""
    if not first_evidence_date or not first_question_date:
        return None
    return (_d(first_question_date) - _d(first_evidence_date)).days


def open_lag_days(pair: dict, as_of: str) -> int | None:
    """How long a topic has sat with evidence and no question. §6.3: 'that
    duration, not merely the stage label, is what gets reported.'"""
    if not pair.get("first_evidence_date") or pair.get("first_question_date"):
        return None
    return (_d(as_of) - _d(pair["first_evidence_date"])).days


def iter_rows(path: Path = TOPICS_PATH):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                yield json.loads(line)
            except ValueError:
                continue


def build_index(rows) -> dict:
    """-> {(theme, ticker): {first_evidence_date, first_question_date, n_evidence, n_question,
    banks, evidence_sources}}. A row contributes once per theme it carries.

    Rows with no theme are skipped: a below-threshold row is a CANDIDATE, not a topic, and
    counting un-named clusters here would quietly pad the distribution with things the
    operator has never approved."""
    idx: dict = {}
    for r in rows:
        ticker, date = r.get("ticker"), str(r.get("event_date") or "")[:10]
        if not ticker or not date:
            continue
        for t in (r.get("themes") or []):
            theme = t.get("theme") if isinstance(t, dict) else t
            if not theme:
                continue
            p = idx.setdefault((theme, ticker), {
                "theme": theme, "ticker": ticker,
                "first_evidence_date": None, "first_question_date": None,
                "n_evidence": 0, "n_question": 0, "banks": set(), "evidence_sources": set(),
            })
            if r.get("register") == "evidence":
                p["n_evidence"] += 1
                p["evidence_sources"].add(r.get("source") or "exchange")
                if p["first_evidence_date"] is None or date < p["first_evidence_date"]:
                    p["first_evidence_date"] = date
            elif r.get("register") == "question":
                p["n_question"] += 1
                if r.get("firm"):
                    p["banks"].add(r["firm"])
                if p["first_question_date"] is None or date < p["first_question_date"]:
                    p["first_question_date"] = date
    return idx


def stage(idx: dict, theme: str, ticker: str) -> int | None:
    """§6.3 staging, read across every company carrying the topic."""
    if (theme, ticker) not in idx:
        return None
    asked = {tk for (th, tk), p in idx.items()
             if th == theme and p["first_question_date"]}
    if not asked:
        return 1                                   # nobody has asked anywhere
    here = idx[(theme, ticker)]["first_question_date"] is not None
    if not here:
        return 2                                   # asked elsewhere, not here
    covered = {tk for (th, tk) in idx if th == theme}
    if len(asked) >= STAGE4_MIN_TICKERS and len(asked) > len(covered) / 2:
        return 4                                   # late / priced
    return 3                                       # consensus forming


def summarize(lags: list) -> dict:
    """Distribution, not a mean. A mean over a skewed, small sample would be
    the easiest way to overstate what this measures."""
    s = sorted(x for x in lags if x is not None)
    n = len(s)
    if not n:
        return {"n": 0}
    mid = (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)
    pos = sum(1 for x in s if x > 0)
    return {
        "n": n,
        "min": s[0],
        "p25": s[int(0.25 * n)],
        "median": mid,
        "p75": s[int(0.75 * n)],
        "max": s[-1],
        "n_negative": sum(1 for x in s if x < 0),
        "n_zero": sum(1 for x in s if x == 0),
        "share_evidence_led": round(100.0 * pos / n, 1),
    }


# ───────────────────── the append-only detection log ─────────────────────

def map_is_fresh(map_path: Path, inputs: list) -> tuple:
    """(ok, reason). A stage-1 detection means 'evidence exists and nobody has asked'. On a map
    older than its inputs that is indistinguishable from 'the question rows landed after the
    last mapping run' — and detected_on freezes the mistake permanently."""
    map_path = Path(map_path)
    if not map_path.exists():
        return False, f"{map_path} missing — run topic_map.py --run first"
    mt = map_path.stat().st_mtime
    for p in inputs:
        p = Path(p)
        if p.exists() and p.stat().st_mtime > mt:
            return False, (f"{map_path.name} is older than {p.name} — re-run topic_map.py "
                           f"before logging detections")
    return True, "fresh"


def append_detections(path: Path, entries: list, as_of: str,
                      coverage_pct: float | None = None) -> int:
    """Append stage-1 detections, stamped with the date first seen.

    First-seen wins. Restamping on a re-run would destroy the only property
    that makes this log worth keeping: that `detected_on` is when the system
    actually said it, not when it last recomputed."""
    path = Path(path)
    seen = set()
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            seen.add((r.get("theme"), r.get("ticker")))
    new = [e for e in entries if (e.get("theme"), e.get("ticker")) not in seen]
    if not new:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for e in new:
            rec = dict(e)
            rec["detected_on"] = as_of
            if coverage_pct is not None:
                rec["coverage_pct"] = round(coverage_pct, 1)
            fh.write(json.dumps(rec, sort_keys=True, default=list) + "\n")
    return len(new)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tier 0 lag + §6.3 staging")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--no-log", action="store_true",
                    help="report only; do not append to the detection log")
    ap.add_argument("--force-log", action="store_true",
                    help="append even though the map is older than its inputs")
    args = ap.parse_args(argv)

    rows = list(iter_rows())
    if not rows:
        log(f"no topic rows at {TOPICS_PATH} — run topic_map.py first")
        return 1
    idx = build_index(rows)
    log(f"{len(rows)} topic rows -> {len(idx)} (topic, company) pairs")

    both = {k: p for k, p in idx.items()
            if p["first_evidence_date"] and p["first_question_date"]}
    lags = [lag_days(p["first_evidence_date"], p["first_question_date"])
            for p in both.values()]
    log(f"{len(both)} pairs carry BOTH registers")

    s = summarize(lags)
    if s["n"]:
        log("Tier 0 — lag in days (question date minus evidence date):")
        log(f"    n={s['n']}  min={s['min']}  p25={s['p25']}  "
            f"median={s['median']}  p75={s['p75']}  max={s['max']}")
        log(f"    evidence led in {s['share_evidence_led']}% of pairs "
            f"({s['n_negative']} negative, {s['n_zero']} same-day)")

    by_stage = collections.Counter()
    stage1 = []
    for (theme, ticker), p in idx.items():
        st = stage(idx, theme, ticker)
        by_stage[st] += 1
        if st == 1 and p["first_evidence_date"]:
            stage1.append({
                "theme": theme, "ticker": ticker, "stage": 1,
                "first_evidence_date": p["first_evidence_date"],
                "n_evidence": p["n_evidence"],
                "evidence_sources": sorted(p["evidence_sources"]),
                "open_lag_days": open_lag_days(p, args.as_of),
            })
    log("§6.3 stages: " + ", ".join(
        f"{k}={by_stage[k]}" for k in sorted(by_stage) if k))

    stage1.sort(key=lambda e: -(e["open_lag_days"] or 0))
    log(f"{len(stage1)} stage-1 (topic, company) pairs — evidence, no question")
    for e in stage1[:15]:
        log(f"    {e['ticker']:<6} {e['theme']:<44} "
            f"{e['open_lag_days']:>4}d open since {e['first_evidence_date']}")

    if args.no_log:
        return 0
    ok, why = map_is_fresh(TOPICS_PATH, [EXCHANGES_PATH, CLAIMS_PATH])
    if not ok and not args.force_log:
        log(f"REFUSING to append: {why}. Pass --force-log to accept a provisional detection.")
        return 2
    n = append_detections(DETECTIONS_PATH, stage1, args.as_of)
    log(f"{n} new detections appended -> {DETECTIONS_PATH} "
        f"(first-seen dates are never restamped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
