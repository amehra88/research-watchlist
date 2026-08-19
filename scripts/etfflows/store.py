"""
store — append-only JSONL state for fetched FactSet series.

One record per (series, ticker, date):
    {"series": "flows"|"prices"|"aum", "ticker": "XLK", "date": "2026-08-18",
     "value": 47558761.75, "shares_outstanding": null, "fetched_at": "..."}

IDEMPOTENT ON (series, ticker, date). Re-running a fetch for a day already stored is a
no-op, and a later fetch of the SAME key overwrites the earlier one on load — which is what
makes it safe to re-run a partially-failed backfill without curating what already landed.
Last-write-wins matters for a real case: today's flow arrives as null at 05:30 and as a real
number the next morning, and the number must win.

Append-only on disk (never rewritten in place) so a crash mid-write costs at most the
trailing line rather than the whole history.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

SERIES = ("flows", "prices", "aum")


def append(path: str, records, series: str, now: datetime | None = None) -> int:
    """Append records for one series. Returns the number of lines written."""
    if series not in SERIES:
        raise ValueError(f"unknown series {series!r}")
    if not records:
        return 0
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    n = 0
    with open(path, "a") as fh:
        for r in records:
            if not r.get("ticker") or not r.get("date"):
                continue
            fh.write(json.dumps({
                "series": series,
                "ticker": r["ticker"],
                "date": r["date"],
                "value": r.get("value"),
                "shares_outstanding": r.get("shares_outstanding"),
                "fetched_at": stamp,
            }) + "\n")
            n += 1
    return n


def load(path: str) -> dict:
    """Read the ledger into {series: {ticker: {date: record}}}, last write winning.

    A malformed line is skipped rather than fatal — a torn trailing line from an interrupted
    write must not make three years of history unreadable.
    """
    out: dict[str, dict[str, dict[str, dict]]] = {s: {} for s in SERIES}
    if not os.path.exists(path):
        return out
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            s, t, d = rec.get("series"), rec.get("ticker"), rec.get("date")
            if s not in out or not t or not d:
                continue
            out[s].setdefault(t, {})[d] = rec
    return out


def series_for(state: dict, series: str, ticker: str) -> tuple[list[str], list]:
    """(dates, values) for one ticker, ascending by date. None values are preserved."""
    by_date = state.get(series, {}).get(ticker, {})
    dates = sorted(by_date)
    return dates, [by_date[d].get("value") for d in dates]


def month_end_aum(state: dict, ticker: str) -> dict[str, float]:
    """{date: shareClassAUMReported} for the AUM anchors, dropping nulls."""
    return {d: rec["value"]
            for d, rec in sorted(state.get("aum", {}).get(ticker, {}).items())
            if rec.get("value") is not None}


def latest_date(state: dict, series: str, require_value: bool = True) -> str | None:
    """Newest date present across all tickers for a series.

    `require_value=True` ignores dates whose value is null everywhere — which is exactly
    today's row at a 05:30 fetch. This is what lets the report PRINT its as-of date instead
    of assuming T-1; the spec requires that, and the assumption is genuinely wrong some days.
    """
    best = None
    for _, by_date in state.get(series, {}).items():
        for d, rec in by_date.items():
            if require_value and rec.get("value") is None:
                continue
            if best is None or d > best:
                best = d
    return best


def coverage(state: dict, series: str) -> dict[str, int]:
    """{ticker: count of non-null observations} — used by the backfill progress report."""
    return {t: sum(1 for r in by_date.values() if r.get("value") is not None)
            for t, by_date in state.get(series, {}).items()}
