#!/usr/bin/env python3
"""
Lifecycle staging and the Tier 0 lag measurement (spec §6.3).

    lag = first_question_date - first_evidence_date

`first_evidence_date` comes from claims.jsonl; `first_question_date` is the
earliest `event_date` of an ANALYST exchange on the same (topic, company).
Positive lag means the company disclosed it before the street asked — which is
the entire premise of the system.

**Tier 0 is a test of that premise, not a demonstration of it.** The spec rests
the claim on one anecdote (Innolight FY2025 → the 2026-06-09 question). This
module computes the distribution over every (topic, company) pair that has
both registers, and it deliberately KEEPS pairs where the question came first:
those are the counter-evidence, and dropping or clamping them would rig the
measurement.

It is not a returns backtest, and it must not be read as one. Only ~32 tickers
carry both registers today, the 62 themes were authored in 2026 with the
answers known, and the watchlist is survivorship-selected. Relative timing is
still fair game — topic selection does not bias whether evidence or the
question came first — which is exactly why this is the measurement worth
having now.

`append_detections` writes the append-only stage-1 log. In three years the
question will be "when did the system FIRST flag this", and only a value that
never moves can answer it.
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
TOPICS_PATH = REPO_ROOT / "state" / "topics" / "topics.jsonl"
EXCHANGES_PATH = REPO_ROOT / "state" / "transcripts" / "exchanges.jsonl"
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


def question_dates(path: Path = EXCHANGES_PATH) -> dict:
    """vector_id -> event_date.

    Topic rows carry period_key but not the exchange's date, so the exact
    question date is recovered here by joining back on unit_id. A quarter
    label would blur a lag the whole point of which is measured in days."""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("vector_id") and r.get("event_date"):
            out[r["vector_id"]] = str(r["event_date"])[:10]
    return out


def build_index(rows, qdates: dict) -> dict:
    """-> {(theme, ticker): {first_evidence_date, first_question_date, ...}}

    Rows with no theme are skipped: a below-threshold phrase is a CANDIDATE,
    not a topic, and counting un-named clusters here would quietly pad the
    distribution with things the operator has never approved."""
    idx: dict = {}
    for r in rows:
        theme, ticker = r.get("theme"), r.get("ticker")
        if not theme or not ticker:
            continue
        p = idx.setdefault((theme, ticker), {
            "theme": theme, "ticker": ticker,
            "first_evidence_date": None, "first_question_date": None,
            "n_evidence": 0, "n_question": 0, "banks": set(),
        })
        if r.get("register") == "evidence":
            p["n_evidence"] += 1
            d = r.get("first_evidence_date")
            if d and (p["first_evidence_date"] is None
                      or str(d)[:10] < p["first_evidence_date"]):
                p["first_evidence_date"] = str(d)[:10]
        elif r.get("register") == "question":
            p["n_question"] += 1
            if r.get("speaker_firm"):
                p["banks"].add(r["speaker_firm"])
            d = qdates.get(r.get("unit_id"))
            if d and (p["first_question_date"] is None
                      or d < p["first_question_date"]):
                p["first_question_date"] = d
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

def append_detections(path: Path, entries: list, as_of: str) -> int:
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
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return len(new)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tier 0 lag + §6.3 staging")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--no-log", action="store_true",
                    help="report only; do not append to the detection log")
    args = ap.parse_args(argv)

    rows = list(iter_rows())
    if not rows:
        log(f"no topic rows at {TOPICS_PATH} — run topic_map.py first")
        return 1
    qd = question_dates()
    idx = build_index(rows, qd)
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
                "open_lag_days": open_lag_days(p, args.as_of),
            })
    log("§6.3 stages: " + ", ".join(
        f"{k}={by_stage[k]}" for k in sorted(by_stage) if k))

    stage1.sort(key=lambda e: -(e["open_lag_days"] or 0))
    log(f"{len(stage1)} stage-1 (topic, company) pairs — evidence, no question")
    for e in stage1[:15]:
        log(f"    {e['ticker']:<6} {e['theme']:<44} "
            f"{e['open_lag_days']:>4}d open since {e['first_evidence_date']}")

    if not args.no_log:
        n = append_detections(DETECTIONS_PATH, stage1, args.as_of)
        log(f"{n} new detections appended -> {DETECTIONS_PATH} "
            f"(first-seen dates are never restamped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
