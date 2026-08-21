#!/usr/bin/env python3
"""MD&A QoQ diff -> claims.jsonl (spec §4.4, the US evidence side).

WHAT THE DIFF ACTUALLY BUYS — MEASURED, because the spec (§4.4) and the plan
both assumed more. The claim was "MD&A is largely carried-forward boilerplate,
so what changed is small and deliberate". Measured on COHR's consecutive 10-Qs
(2026-02-04 -> 2026-05-06), counting only prose blocks of >= MIN_WORDS words:

    prev 51 blocks | curr 53 blocks | exact carry-forward: 13

So ~75% of MD&A prose is REWRITTEN each quarter, not carried forward. The
overview paragraph is rewritten outright — its best match in the prior filing
scores 0.564. Number/date normalisation does not rescue it (48.2 blocks/pair vs
46.7 un-normalised), and neither does loosening the near-duplicate threshold to
0.75 (37.0/pair). The paragraphs genuinely differ; only the section scaffolding
(bullet lists, sub-headings) repeats verbatim, and MIN_WORDS already drops that.

Therefore: this module emits MD&A PROSE IN THE WINDOW, dated by filed_date. It
does NOT emit "what management newly chose to say" — that framing does not
survive contact with the corpus. The diff still earns its place by deleting the
verbatim scaffolding and the safe-harbor block, but it is a filter, not the
signal. Topic-level novelty ("this filer's MD&A raises topic T for the first
time in three quarters") belongs downstream in P4, where the comparison is
between stable topic slugs rather than between prose that is rewritten anyway.

WHY THE WINDOW. The spec sizes this component at 211 docs / 70 tickers inside
the 9-month window; notes/sec/ holds ~8 years. Without the window the evidence
side spans 2018-2026 while the question side (exchanges.jsonl) spans 9 months,
and §6.2's evidence-count-vs-question-count comparison is measuring two
different periods. The filing immediately BEFORE the window is still loaded, as
the diff baseline for the first in-window filing, but never emits claims itself.

WHY THE LATER FILING DATES THE CLAIM. first_evidence_date is when the market
could first have read the sentence, so it is the later filing's filed_date, not
the earlier one's. §6.3 measures lag from this date to the first analyst
question on the same topic.

  python3 scripts/v3_ingest/mdna_evidence.py --dry-run
  python3 scripts/v3_ingest/mdna_evidence.py --ticker ADI
  python3 scripts/v3_ingest/mdna_evidence.py
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import difflib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_store as es  # noqa: E402

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

REPO_ROOT = Path("/root/research-watchlist")
SEC_NOTES = REPO_ROOT / "notes" / "sec"
CLAIMS_PATH = REPO_ROOT / "state" / "evidence" / "claims.jsonl"

# 10-Q Item 2 and 10-K Item 7 are the same section under two numbers.
MDNA_HEADING_RE = re.compile(
    r"^##\s+Item\s+(?:2|7)[.\s].*Management.s\s+Discussion", re.I | re.M)
NEXT_HEADING_RE = re.compile(r"^##\s+", re.M)
MIN_WORDS = 25
WINDOW_MONTHS = 9          # matches transcript_ingest.py, so both registers
                           # cover the same period (spec §4.4)


def window_start(months: int = WINDOW_MONTHS, today: dt.date = None) -> str:
    """ISO date `months` back from today. Day-of-month is clamped so that e.g.
    the 31st does not fall off a 30-day month."""
    today = today or dt.date.today()
    m = today.month - months
    y = today.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    day = min(today.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0)
                          else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return f"{y:04d}-{m:02d}-{day:02d}"


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] mdna_evidence: {msg}", flush=True)


def _frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    raw = text[3:end]
    if yaml is None:                                  # pragma: no cover
        return {}
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}


def parse_note(path: Path):
    """-> {"ticker","filed_date","form_type","mdna","document_id"} or None."""
    text = path.read_text(errors="replace")
    fm = _frontmatter(text)
    if not fm.get("ticker") or not fm.get("filed_date"):
        return None

    body_start = text.find("\n---", 3)
    body = text[body_start + 4:] if body_start != -1 else text

    m = MDNA_HEADING_RE.search(body)
    if not m:
        return None
    # The regex stops at "Discussion"; real headings run on ("...and Analysis
    # of Financial Condition and Results of Operations"). Consume to end of
    # line so the tail of the heading does not open the body as a stray block.
    eol = body.find("\n", m.end())
    rest = body[eol + 1:] if eol != -1 else body[m.end():]
    nxt = NEXT_HEADING_RE.search(rest)
    mdna = (rest[:nxt.start()] if nxt else rest).strip()
    if not mdna:
        return None

    return {
        "ticker": str(fm["ticker"]),
        "filed_date": str(fm["filed_date"]),
        "form_type": str(fm.get("form_type", "")),
        "mdna": mdna,
        "document_id": str(path.relative_to(REPO_ROOT))
                       if str(path).startswith(str(REPO_ROOT)) else str(path),
    }


def split_blocks(text: str) -> list:
    """One block per line, whitespace-normalised so that a reflowed but
    unchanged paragraph does not read as new.

    NOT blank-line separated. The notes/sec/ writer emits one paragraph per
    line and almost never a blank line: a 1,200-note sample found 0 notes laid
    out in blank-line paragraphs and 254 laid out one-paragraph-per-line, and
    splitting on blank lines collapsed a 40,888-character MD&A into TWO blocks.
    A 40KB blob is not a claim — it carries every topic at once, so the
    downstream phrase extraction has nothing to bite on.

    Sub-headings ("Industry Conditions") are their own short lines and fall out
    at the min_words filter in added_blocks, which is where they belong."""
    out = []
    for blk in re.split(r"\n+", text):
        blk = " ".join(blk.split())
        if blk:
            out.append(blk)
    return out


def added_blocks(prev: str, curr: str, *, min_words: int = MIN_WORDS) -> list:
    """Paragraphs present in `curr` and absent from `prev`.

    Short fragments are dropped: financial tables survive the diff as rows of
    numbers and page markers, and they carry no topic to map."""
    a, b = split_blocks(prev), split_blocks(curr)
    seen = set(a)
    out = []
    # difflib caches the *second* sequence, so hold the candidate in seq2 and
    # swap the priors through seq1. real_quick_ratio (length bound) and
    # quick_ratio (multiset bound) are both upper bounds on ratio, so gating on
    # them skips the quadratic matching without changing a single verdict.
    # Measured: the naive form did not finish a full-corpus pass in 15 minutes.
    sm = difflib.SequenceMatcher()
    for blk in b:
        if blk in seen:
            continue
        if len(blk.split()) < min_words:
            continue
        # near-duplicate guard: a one-number edit to an otherwise identical
        # paragraph is a restatement, not a new disclosure.
        sm.set_seq2(blk)
        restated = False
        for old in a:
            sm.set_seq1(old)
            if (sm.real_quick_ratio() > 0.95 and sm.quick_ratio() > 0.95
                    and sm.ratio() > 0.95):
                restated = True
                break
        if restated:
            continue
        out.append(blk)
    return out


def claims_for_ticker(notes: list, *, since: str = None) -> list:
    """Diff each filing against the previous one from the same filer.

    `since` bounds which filings may EMIT, not which may be read: the filing
    immediately before the window is still needed as a diff baseline, or the
    first in-window quarter would diff against nothing and dump its whole MD&A.
    """
    ordered = sorted(notes, key=lambda n: n["filed_date"])
    claims = []
    for prev, curr in zip(ordered, ordered[1:]):
        if since and curr["filed_date"] < since:
            continue
        for blk in added_blocks(prev["mdna"], curr["mdna"]):
            claims.append(es.make_claim(
                source="mdna",
                document_id=curr["document_id"],
                ticker=curr["ticker"],
                affects=[curr["ticker"]],
                first_evidence_date=curr["filed_date"],
                period_key=None,
                text=blk,
            ))
    return claims


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P3b MD&A evidence (spec §4.4)")
    ap.add_argument("--ticker", action="append", help="restrict (repeatable)")
    ap.add_argument("--notes-dir", default=str(SEC_NOTES))
    ap.add_argument("--out", default=str(CLAIMS_PATH))
    ap.add_argument("--window-months", type=int, default=WINDOW_MONTHS,
                    help="0 disables the window and reads the whole corpus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    since = window_start(args.window_months) if args.window_months else None
    paths = sorted(Path(args.notes_dir).glob("*.md"))
    log(f"scanning {len(paths)} notes in {args.notes_dir}"
        + (f"; emitting for filings on/after {since}" if since else
           "; NO WINDOW (whole corpus)"))

    by_ticker = collections.defaultdict(list)
    parsed = skipped = 0
    for p in paths:
        note = parse_note(p)
        if note is None:
            skipped += 1
            continue
        if args.ticker and note["ticker"] not in set(args.ticker):
            continue
        by_ticker[note["ticker"]].append(note)
        parsed += 1

    log(f"{parsed} notes carry MD&A across {len(by_ticker)} filers "
        f"({skipped} without an MD&A section, mostly 8-K)")

    singles = [t for t, ns in by_ticker.items() if len(ns) < 2]
    if singles:
        log(f"{len(singles)} filers have only one MD&A on disk -> no diff "
            f"possible yet: {', '.join(sorted(singles)[:8])}"
            + (" ..." if len(singles) > 8 else ""))

    claims = []
    for ticker, notes in sorted(by_ticker.items()):
        claims.extend(claims_for_ticker(notes, since=since))
    in_window = {c["document_id"] for c in claims}
    log(f"{len(claims)} prose blocks became claims, from {len(in_window)} "
        f"filings across {len({c['ticker'] for c in claims})} filers")

    if args.dry_run:
        for c in claims[:20]:
            log(f"  DRY {c['ticker']} {c['first_evidence_date']} "
                f"{c['text'][:110]}")
        log(f"DRY: would append {len(claims)} claims to {args.out}")
        return 0

    stats = es.append_claims(Path(args.out), claims)
    log(f"done: {stats} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
