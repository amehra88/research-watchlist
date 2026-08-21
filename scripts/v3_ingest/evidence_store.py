#!/usr/bin/env python3
"""Shared claim record for the evidence side (spec §4.3, §4.4).

Both evidence producers — mdna_evidence.py (10-Q/10-K MD&A, US) and
foreign_evidence.py (CNINFO + StreetAccount) — write the SAME record shape into
one claims.jsonl, so §6.2 can compare a disclosure count against a question
count without caring which pipe the disclosure arrived through.

EVERY CLAIM CARRIES first_evidence_date. It is the publication date of the
document the claim came from, and it is the clock the §6.3 lifecycle staging
runs on: without it a detector can say "evidence exists, nobody is asking" but
not "and it has been sitting there for 50 days", which is the entire actionable
content of stage 1.

CLAIMS ARE LEADS, NOT FACTS. `verified` is False on write and only an operator
flips it. Figures here have not been checked against audited statements.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CLAIM_FIELDS = (
    "claim_id",
    "source",               # mdna | cninfo | streetaccount
    "document_id",          # repo-relative note path, or upstream doc id
    "ticker",               # the filer / speaker
    "affects",              # tickers whose thesis this bears on
    "first_evidence_date",  # publication date — the §6.3 clock
    "period_key",           # calendar quarter, e.g. 2026Q3
    "text",                 # the English claim
    "source_phrase",        # original-language phrase (CNINFO), else None
    "verified",             # always False on write
)


def calendar_quarter(date_iso: str) -> str:
    """Calendar quarter key. Deliberately calendar, not fiscal: filers'
    fiscal calendars disagree, and the denominator in §5 is cross-sectional."""
    y, m, _ = date_iso.split("-")
    return f"{y}Q{(int(m) - 1) // 3 + 1}"


def join_period_key(*, period_key, period_basis, event_date) -> str:
    """The key to join the QUESTION side to the EVIDENCE side on.

    THE TRAP: exchanges.jsonl `period_key` is not one thing. Measured on the
    corpus, 6,035 rows carry `period_basis: fiscal` and 4,086 carry `calendar`.
    LITE's fiscal 2026Q4 is calendar 2026Q2. Meanwhile every claim written by
    this module is calendar (see calendar_quarter). Joining the two registers on
    a raw `period_key` therefore lines up rows that are two quarters apart, and
    does it silently — the strings match, so nothing errors.

    That would corrupt both §6.2 (the evidence-count vs question-count
    comparison) and §6.3 (the lag from first evidence to first question), which
    are the two numbers the whole system exists to produce.

    So: always derive from the publication date, which is basis-independent.
    `period_key` is kept in the record for display, never for joining."""
    if event_date:
        return calendar_quarter(event_date)
    if period_basis == "calendar" and period_key:
        return str(period_key)
    raise ValueError(
        "cannot derive a calendar join key: no event_date, and period_key "
        f"{period_key!r} is basis {period_basis!r} rather than calendar")


def claim_id(source: str, document_id: str, text: str) -> str:
    h = hashlib.sha1(f"{source}|{document_id}|{text}".encode()).hexdigest()
    return h[:16]


def make_claim(*, source: str, document_id: str, ticker: str, affects: list,
               first_evidence_date: str, period_key, text: str,
               source_phrase=None) -> dict:
    if not first_evidence_date:
        raise ValueError(
            "first_evidence_date is required — it is the §6.3 lifecycle clock")
    return {
        "claim_id": claim_id(source, document_id, text),
        "source": source,
        "document_id": document_id,
        "ticker": ticker,
        "affects": list(affects),
        "first_evidence_date": first_evidence_date,
        "period_key": period_key or calendar_quarter(first_evidence_date),
        "text": text,
        "source_phrase": source_phrase,
        "verified": False,
    }


def existing_claim_ids(path: Path) -> set:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.add(json.loads(line)["claim_id"])
        except (ValueError, KeyError):
            continue          # a torn last line must not abort a resumed run
    return out


def append_claims(path: Path, claims: list) -> dict:
    """Append, skipping ids already on disk. Returns {"written", "dupes"}."""
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = existing_claim_ids(path)
    written = dupes = 0
    with path.open("a") as fh:
        for c in claims:
            if c["claim_id"] in seen:
                dupes += 1
                continue
            fh.write(json.dumps(c) + "\n")
            seen.add(c["claim_id"])
            written += 1
    return {"written": written, "dupes": dupes}
