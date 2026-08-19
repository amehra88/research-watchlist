# Topic Vocabulary & US Evidence Side — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the shared topic vocabulary (`topic_map.py`, spec P2) and the US evidence stream (`mdna_evidence.py`, spec P3b), so that analyst questions and company disclosures land in the *same* topic namespace and the §6.2 evidence-without-question gap becomes computable.

**Architecture:** Two producers write into one namespace. `mdna_evidence.py` diffs consecutive 10-Q/10-K MD&A sections already on disk in `notes/sec/` and emits *added* prose as evidence claims. `topic_map.py` consumes both registers — analyst exchanges from `exchanges.jsonl` (question side) and claims from `claims.jsonl` (evidence side) — extracts short topic phrases, embeds them against the 62 `config/watchlist.yaml` theme slugs as anchors, and assigns each unit either an existing theme (cosine ≥ threshold) or a new-theme candidate. Candidates cluster and surface for operator naming; the system never writes to `watchlist.yaml`.

**Tech Stack:** Python 3 stdlib, `PyYAML`, `scripts/chunking/embed.py` (Gemini `gemini-embedding-001`, dim 3072, content-hash cached), `claude -p` with `--output-format stream-json` for phrase extraction. No pytest — tests are plain-assert modules run directly.

**Spec:** `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` (§4.2, §4.4, §5, §6.2). Read it alongside this plan.

## Global Constraints

- **The vocabulary is 62 slugs, not 61.** The spec says 61; `space_supply_chain` was added in commit `0a703b9a`. Always count them at runtime from `config/watchlist.yaml` → `themes:` (5 groups: `demand`, `supply`, `margins_pricing`, `strategic`, `macro_policy`). **Never hardcode the count.**
- **The system never writes to `config/watchlist.yaml`.** New themes are proposed to a review file only. Vocabulary and tier changes are operator-only (spec §4.2).
- **No pytest in this environment.** Tests are modules of `test_*` functions with a `__main__` runner that prints `✓`/`✗` and exits non-zero on failure — copy the runner block from `scripts/v3_ingest/test_transcript_ingest.py` verbatim.
- **Absolute paths.** `REPO_ROOT = Path("/root/research-watchlist")`, matching `transcript_ingest.py:72`. Scripts must behave identically when run from a worktree.
- **Cross-sectional metrics only.** No velocity, slope fitting, smoothing, or seasonal adjustment anywhere in this plan's output (spec §5, "Prohibited by design").
- **Every claim carries `first_evidence_date`.** Without it §6.3 lifecycle staging has no clock. A claim record missing it is a bug, not a degraded record.
- **`empty` ≠ `failed` in any ledger.** `empty` is answered-and-done; `failed` is unknown-and-retried. This is the `b1c351aa` lesson already encoded in `transcript_ingest.py:428`.
- **Run `python3 scripts/check.py` before every commit.** It must report 0 issues.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/v3_ingest/evidence_store.py` | **Create.** Claim record shape, id derivation, append-with-dedup writer. Shared by `mdna_evidence.py` (this plan) and `foreign_evidence.py` (later plan). |
| `scripts/v3_ingest/test_evidence_store.py` | **Create.** Unit tests for the above. |
| `scripts/v3_ingest/mdna_evidence.py` | **Create.** Parse `notes/sec/` MD&A notes, group by ticker, QoQ diff, emit added blocks as claims. |
| `scripts/v3_ingest/test_mdna_evidence.py` | **Create.** Unit tests, incl. boilerplate-suppression regression. |
| `scripts/v3_ingest/topic_map.py` | **Create.** Anchor loading, phrase extraction, embedding + cosine assignment, candidate clustering, CLI. |
| `scripts/v3_ingest/test_topic_map.py` | **Create.** Unit tests with an injected fake embedder (no network in tests). |
| `state/evidence/claims.jsonl` | **Runtime output.** Not committed. |
| `state/topics/topics.jsonl` | **Runtime output.** Not committed. |
| `state/topics/_candidates.json` | **Runtime output.** Operator review queue. Not committed. |

`topic_map.py` is the largest unit. It is kept as one file because its four stages share the anchor matrix and the vocabulary loader, and splitting them would mean passing a 62×3072 float matrix across module boundaries for no gain. It stays under ~450 lines.

---

## Task 1: Claim record shape and writer

The shared contract between both evidence producers. Built first so `mdna_evidence.py` and the later `foreign_evidence.py` cannot drift apart.

**Files:**
- Create: `scripts/v3_ingest/evidence_store.py`
- Test: `scripts/v3_ingest/test_evidence_store.py`

**Interfaces:**
- Consumes: nothing (leaf module).
- Produces:
  - `CLAIM_FIELDS: tuple[str, ...]`
  - `claim_id(source: str, document_id: str, text: str) -> str` — 16-hex sha1
  - `make_claim(*, source, document_id, ticker, affects, first_evidence_date, period_key, text, source_phrase=None) -> dict`
  - `calendar_quarter(date_iso: str) -> str` — `"2026Q3"`
  - `append_claims(path: Path, claims: list[dict]) -> dict` — returns `{"written": int, "dupes": int}`
  - `existing_claim_ids(path: Path) -> set[str]`

- [ ] **Step 1: Write the failing test**

Create `scripts/v3_ingest/test_evidence_store.py`:

```python
"""
Unit tests for evidence_store (spec §4.3, §4.4 — the shared claim record).

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_evidence_store.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_store as es  # noqa: E402


def test_calendar_quarter_maps_month_to_quarter():
    assert es.calendar_quarter("2026-08-19") == "2026Q3"
    assert es.calendar_quarter("2026-01-01") == "2026Q1"
    assert es.calendar_quarter("2025-12-31") == "2025Q4"


def test_claim_id_is_stable_and_text_sensitive():
    a = es.claim_id("mdna", "doc1", "capacity rose 34%")
    b = es.claim_id("mdna", "doc1", "capacity rose 34%")
    c = es.claim_id("mdna", "doc1", "capacity rose 35%")
    assert a == b, "same inputs must give same id"
    assert a != c, "text change must change the id"
    assert len(a) == 16


def test_make_claim_requires_first_evidence_date():
    """The lifecycle clock (spec §6.3). A claim without it is a bug."""
    try:
        es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="",
                      period_key="2026Q3", text="x")
    except ValueError as e:
        assert "first_evidence_date" in str(e)
    else:
        raise AssertionError("empty first_evidence_date must raise")


def test_make_claim_derives_period_key_when_absent():
    c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="2026-08-19",
                      period_key=None, text="x")
    assert c["period_key"] == "2026Q3"


def test_make_claim_has_exactly_the_declared_fields():
    c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="2026-08-19",
                      period_key="2026Q3", text="x")
    assert set(c) == set(es.CLAIM_FIELDS)
    assert c["verified"] is False, "claims are leads, never established fact"


def test_append_claims_dedupes_across_runs():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"
        c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                          affects=["ADI"], first_evidence_date="2026-08-19",
                          period_key="2026Q3", text="capacity rose")
        first = es.append_claims(p, [c])
        second = es.append_claims(p, [c])
        assert first == {"written": 1, "dupes": 0}
        assert second == {"written": 0, "dupes": 1}, "re-run must not duplicate"
        assert len(p.read_text().strip().splitlines()) == 1


def test_existing_claim_ids_tolerates_missing_file():
    with tempfile.TemporaryDirectory() as d:
        assert es.existing_claim_ids(Path(d) / "nope.jsonl") == set()


# ───────────────────────── runner ─────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_evidence_store.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'evidence_store'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/v3_ingest/evidence_store.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_evidence_store.py`
Expected: PASS — `7/7 pass`

- [ ] **Step 5: Lint and commit**

```bash
python3 scripts/check.py
git add scripts/v3_ingest/evidence_store.py scripts/v3_ingest/test_evidence_store.py
git commit -m "P3b: shared claim record for the evidence side"
```

---

## Task 2: MD&A QoQ diff → claims

The cheapest work in the project: 7,222 notes are already on disk in `notes/sec/`, no external API, no `claude -p`, no new auth.

The diff is what makes this work. An MD&A section is ~80% boilerplate that is byte-identical quarter to quarter (the safe-harbor paragraph in `notes/sec/2026-08-19-ADI-10-Q-2-3.md` runs to four screens). Diffing consecutive filings from the same ticker deletes all of it for free and leaves what management *newly chose to say* — which is exactly the evidence signal.

**Files:**
- Create: `scripts/v3_ingest/mdna_evidence.py`
- Test: `scripts/v3_ingest/test_mdna_evidence.py`

**Interfaces:**
- Consumes: `evidence_store.make_claim`, `evidence_store.append_claims` (Task 1).
- Produces:
  - `parse_note(path: Path) -> dict | None` — `{"ticker", "filed_date", "form_type", "mdna", "document_id"}`; `None` when the note has no MD&A body.
  - `MDNA_HEADING_RE: re.Pattern`
  - `split_blocks(text: str) -> list[str]`
  - `added_blocks(prev: str, curr: str, *, min_words: int = 25) -> list[str]`
  - `claims_for_ticker(notes: list[dict]) -> list[dict]`
  - `main(argv=None) -> int`

- [ ] **Step 1: Write the failing test**

Create `scripts/v3_ingest/test_mdna_evidence.py`:

```python
"""
Unit tests for mdna_evidence (spec §4.4 — the US evidence side).

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_mdna_evidence.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mdna_evidence as me  # noqa: E402

NOTE = """---
doc_type: sec_filing
ticker: ADI
form_type: 10-Q
filed_date: '2026-08-19'
themes:
- semiconductor_cycle
---

# ADI 10-Q — filed 2026-08-19

## Item 2. Management's Discussion and Analysis

Revenue increased forty percent driven by demand across the industrial and
automotive end markets, with particular strength in datacenter power.
"""

NOTE_NO_MDNA = """---
doc_type: sec_filing
ticker: ADI
form_type: 8-K
filed_date: '2026-08-19'
---

# ADI 8-K — filed 2026-08-19

## Item 2.02 Results of Operations

Press release furnished herewith.
"""


def _write(d, name, body):
    p = Path(d) / name
    p.write_text(body)
    return p


def test_parse_note_extracts_frontmatter_and_mdna_body():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "2026-08-19-ADI-10-Q-2-3.md", NOTE)
        got = me.parse_note(p)
        assert got["ticker"] == "ADI"
        assert got["filed_date"] == "2026-08-19"
        assert got["form_type"] == "10-Q"
        assert "Revenue increased forty percent" in got["mdna"]
        assert "doc_type" not in got["mdna"], "frontmatter must not leak in"


def test_parse_note_returns_none_without_an_mdna_section():
    """8-Ks dominate the SEC corpus (spec §1.2). They carry no MD&A and must
    be skipped silently rather than producing empty claims."""
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "2026-08-19-ADI-8-K-2.02.md", NOTE_NO_MDNA)
        assert me.parse_note(p) is None


def test_added_blocks_suppresses_unchanged_boilerplate():
    """The regression that matters: safe-harbor text is byte-identical QoQ and
    must never surface as new evidence."""
    boiler = ("This report contains forward-looking statements subject to the "
              "safe harbor created under the Private Securities Litigation "
              "Reform Act of 1995 and other safe harbors, and actual results "
              "could differ materially from those anticipated herein for many "
              "reasons including the risk factors described in Item 1A.")
    prev = boiler
    curr = boiler + "\n\n" + (
        "We began qualifying a second source for high-power lasers during the "
        "quarter, and we now expect that supplier to carry a meaningful share "
        "of datacenter interconnect volume in the coming fiscal year.")
    got = me.added_blocks(prev, curr)
    assert len(got) == 1, f"expected only the new block, got {len(got)}"
    assert "second source for high-power lasers" in got[0]
    assert "safe harbor" not in got[0]


def test_added_blocks_drops_short_fragments():
    """Table rows and page numbers survive the diff as noise. A claim needs
    enough prose to carry a topic."""
    got = me.added_blocks("alpha beta", "alpha beta\n\n17\n\nRevenue $ 4,021")
    assert got == []


def test_claims_for_ticker_orders_by_filed_date_and_sets_the_clock():
    notes = [
        {"ticker": "ADI", "filed_date": "2026-08-19", "form_type": "10-Q",
         "document_id": "notes/sec/b.md", "mdna": "shared prose here. " * 5 +
         "We qualified a second laser source this quarter across our "
         "datacenter interconnect product family and expect volume."},
        {"ticker": "ADI", "filed_date": "2026-05-14", "form_type": "10-Q",
         "document_id": "notes/sec/a.md", "mdna": "shared prose here. " * 5},
    ]
    claims = me.claims_for_ticker(notes)
    assert len(claims) == 1
    c = claims[0]
    assert c["first_evidence_date"] == "2026-08-19", "clock = the LATER filing"
    assert c["document_id"] == "notes/sec/b.md"
    assert c["period_key"] == "2026Q3"
    assert c["source"] == "mdna"
    assert c["affects"] == ["ADI"]
    assert c["verified"] is False


def test_claims_for_ticker_emits_nothing_for_a_single_filing():
    """With one filing there is no prior to diff against, so there is no
    'newly said' — emitting the whole MD&A would flood the evidence side."""
    notes = [{"ticker": "ADI", "filed_date": "2026-08-19", "form_type": "10-Q",
              "document_id": "notes/sec/b.md", "mdna": "prose " * 60}]
    assert me.claims_for_ticker(notes) == []


# ───────────────────────── runner ─────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_mdna_evidence.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'mdna_evidence'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/v3_ingest/mdna_evidence.py`:

```python
#!/usr/bin/env python3
"""MD&A QoQ diff -> claims.jsonl (spec §4.4, the US evidence side).

WHY A DIFF AND NOT A SUMMARY. An MD&A section is mostly boilerplate that is
byte-identical quarter to quarter — the safe-harbor paragraph alone runs to four
screens. Diffing consecutive filings from the same filer deletes all of it for
free, and what survives is what management NEWLY chose to say. That is the
evidence signal, and getting it costs no API call at all.

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
    rest = body[m.end():]
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
    """Blank-line-separated paragraphs, whitespace-normalised so that a
    reflowed but unchanged paragraph does not read as new."""
    out = []
    for blk in re.split(r"\n\s*\n", text):
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
    for blk in b:
        if blk in seen:
            continue
        if len(blk.split()) < min_words:
            continue
        # near-duplicate guard: a one-number edit to an otherwise identical
        # paragraph is a restatement, not a new disclosure.
        if any(difflib.SequenceMatcher(None, blk, old).ratio() > 0.95
               for old in a):
            continue
        out.append(blk)
    return out


def claims_for_ticker(notes: list) -> list:
    """Diff each filing against the previous one from the same filer."""
    ordered = sorted(notes, key=lambda n: n["filed_date"])
    claims = []
    for prev, curr in zip(ordered, ordered[1:]):
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
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    paths = sorted(Path(args.notes_dir).glob("*.md"))
    log(f"scanning {len(paths)} notes in {args.notes_dir}")

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
        claims.extend(claims_for_ticker(notes))
    log(f"{len(claims)} added-prose blocks became claims")

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_mdna_evidence.py`
Expected: PASS — `6/6 pass`

- [ ] **Step 5: Verify against the real corpus**

Run: `python3 scripts/v3_ingest/mdna_evidence.py --dry-run`

Expected: a scan of ~7,222 notes reporting how many carry MD&A, how many filers have only one filing on disk, and up to 20 sample claims. **Read the samples.** If they are dominated by numeric table rows, raise `MIN_WORDS` and re-run — do not proceed with a claims file that is mostly financial tables.

- [ ] **Step 6: Populate claims.jsonl**

```bash
python3 scripts/v3_ingest/mdna_evidence.py
```

- [ ] **Step 7: Lint and commit**

```bash
python3 scripts/check.py
git add scripts/v3_ingest/mdna_evidence.py scripts/v3_ingest/test_mdna_evidence.py
git commit -m "P3b: MD&A QoQ diff -> claims.jsonl"
```

---

## Task 3: Theme anchors and cosine assignment

The pure, deterministic core of `topic_map.py`. Built and tested with an injected fake embedder so the test suite never touches the network.

**Files:**
- Create: `scripts/v3_ingest/topic_map.py`
- Test: `scripts/v3_ingest/test_topic_map.py`

**Interfaces:**
- Consumes: `scripts/chunking/embed.py` → `embed(texts: list[str], task_type: str, *, use_cache: bool = True) -> list[list[float]]`. Task types are `"retrieval_document"` and `"retrieval_query"`; anchors and phrases both use `"retrieval_document"` so the comparison is symmetric.
- Produces:
  - `SIM_THRESHOLD: float`
  - `load_themes(watchlist_path: Path) -> list[str]`
  - `anchor_text(slug: str) -> str`
  - `cosine(a: list[float], b: list[float]) -> float`
  - `assign(phrase_vecs: list[list[float]], anchor_vecs: list[list[float]], anchors: list[str], threshold: float = SIM_THRESHOLD) -> list[tuple]` — one `(theme_or_None, similarity)` per phrase

- [ ] **Step 1: Write the failing test**

Create `scripts/v3_ingest/test_topic_map.py`:

```python
"""
Unit tests for topic_map (spec §4.2 — the shared topic vocabulary).

Embeddings are FAKED here. The real path is Gemini gemini-embedding-001 via
scripts/chunking/embed.py; a unit test must not spend API calls or need a key.

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_topic_map.py
"""
import math
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_map as tm  # noqa: E402

WATCHLIST = """
themes:
  demand:
    - ai_infrastructure_capex
    - china_ai_infrastructure_demand
  supply:
    - optical_component_supply
  strategic:
    - space_supply_chain
"""


def test_load_themes_flattens_every_group():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "watchlist.yaml"
        p.write_text(WATCHLIST)
        got = tm.load_themes(p)
        assert got == sorted([
            "ai_infrastructure_capex", "china_ai_infrastructure_demand",
            "optical_component_supply", "space_supply_chain"])


def test_load_themes_does_not_hardcode_a_count():
    """The spec says 61; space_supply_chain made it 62 and it will move
    again. Count at runtime, never in source."""
    src = Path(tm.__file__).read_text()
    assert " 61" not in src and "== 61" not in src


def test_anchor_text_turns_a_slug_into_a_phrase():
    assert tm.anchor_text("china_ai_infrastructure_demand") == \
        "china ai infrastructure demand"


def test_cosine_is_one_for_identical_and_zero_for_orthogonal():
    assert math.isclose(tm.cosine([1.0, 0.0], [1.0, 0.0]), 1.0, abs_tol=1e-9)
    assert math.isclose(tm.cosine([1.0, 0.0], [0.0, 1.0]), 0.0, abs_tol=1e-9)


def test_cosine_handles_a_zero_vector_without_dividing_by_zero():
    assert tm.cosine([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_assign_inherits_the_nearest_theme_above_threshold():
    anchors = ["ai_infrastructure_capex", "optical_component_supply"]
    anchor_vecs = [[1.0, 0.0], [0.0, 1.0]]
    phrases = [[0.99, 0.14]]                 # clearly the first anchor
    got = tm.assign(phrases, anchor_vecs, anchors, threshold=0.7)
    assert got[0][0] == "ai_infrastructure_capex"
    assert got[0][1] > 0.7


def test_assign_returns_none_below_threshold_as_a_new_theme_candidate():
    """Below threshold is the whole point: it is how the vocabulary grows
    (spec §4.2 step 4) instead of forcing everything into 62 boxes."""
    anchors = ["ai_infrastructure_capex"]
    anchor_vecs = [[1.0, 0.0]]
    phrases = [[0.0, 1.0]]
    got = tm.assign(phrases, anchor_vecs, anchors, threshold=0.7)
    assert got[0][0] is None
    assert got[0][1] < 0.7, "the near-miss score must still be reported"


# ───────────────────────── runner ─────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'topic_map'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/v3_ingest/topic_map.py`:

```python
#!/usr/bin/env python3
"""Shared topic vocabulary over both registers (spec §4.2).

ONE VOCABULARY, TWO REGISTERS. Analyst exchanges (exchanges.jsonl) are the
question side; MD&A diffs and foreign claims (claims.jsonl) are the evidence
side. Both map into the SAME topic namespace — otherwise §6.2's two-count
comparison has no way to know that a disclosure and a question concern the same
topic, and the gap metric is simply not computable.

THEMES ARE ANCHORS, NOT BOXES. The config/watchlist.yaml slugs seed the space
and preserve continuity with the existing labelled history. A phrase that lands
near one inherits it; a phrase that lands far from all of them becomes a
new-theme CANDIDATE. That is how the vocabulary grows.

THE OPERATOR OWNS THE VOCABULARY. Candidates are written to a review file. This
module NEVER writes to config/watchlist.yaml — the same rule that governs tier
promotion.
"""
from __future__ import annotations

import datetime as dt
import math
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

REPO_ROOT = Path("/root/research-watchlist")
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"

# Cosine on gemini-embedding-001. Calibrated in Task 6 against the real
# corpus; this is the starting point, not a tuned value.
SIM_THRESHOLD = 0.72


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] topic_map: {msg}", flush=True)


def load_themes(watchlist_path: Path = WATCHLIST_YAML) -> list:
    """Every slug across every theme group, sorted. The count is whatever the
    file says today — it has already changed once and will change again."""
    data = yaml.safe_load(watchlist_path.read_text()) or {}
    slugs = set()
    for group in (data.get("themes") or {}).values():
        for slug in group or []:
            slugs.add(str(slug))
    return sorted(slugs)


def anchor_text(slug: str) -> str:
    """A slug is not a sentence. Embedding `china_ai_infrastructure_demand`
    raw wastes the model's language prior; the spaced phrase does not."""
    return slug.replace("_", " ")


def cosine(a: list, b: list) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def assign(phrase_vecs: list, anchor_vecs: list, anchors: list,
           threshold: float = SIM_THRESHOLD) -> list:
    """-> [(theme_or_None, similarity)] aligned to phrase_vecs.

    The similarity is reported even on a miss: a phrase that scored 0.71
    against an existing theme is a different kind of candidate from one that
    scored 0.2, and the operator review in §4.2 needs to see which."""
    out = []
    for pv in phrase_vecs:
        best_i, best_s = -1, -1.0
        for i, av in enumerate(anchor_vecs):
            s = cosine(pv, av)
            if s > best_s:
                best_i, best_s = i, s
        out.append((anchors[best_i] if best_s >= threshold else None, best_s))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: PASS — `7/7 pass`

- [ ] **Step 5: Lint and commit**

```bash
python3 scripts/check.py
git add scripts/v3_ingest/topic_map.py scripts/v3_ingest/test_topic_map.py
git commit -m "P2: theme anchors and cosine assignment"
```

---

## Task 4: Phrase extraction from both registers

Turns a raw analyst question or MD&A block into short topic phrases. This is the only `claude -p` call in the plan.

Per memory `claude-p-bulk-data-transport`: **never ask `claude -p` to echo bulk data back.** Send one unit's text, get back a short JSON array of phrases. The failure signature to fail fast on is `duration_api_ms: 0` with `total_cost_usd: 0` — the usage-limit cliff that killed the P1 backfill on 2026-08-11.

**Files:**
- Modify: `scripts/v3_ingest/topic_map.py` (append)
- Modify: `scripts/v3_ingest/test_topic_map.py` (append tests before the runner block)

**Interfaces:**
- Consumes: `assign`, `load_themes`, `anchor_text` (Task 3).
- Produces:
  - `iter_question_units(path: Path) -> Iterator[dict]` — `{"unit_id","register","ticker","period_key","speaker_firm","text"}`
  - `iter_evidence_units(path: Path) -> Iterator[dict]` — same keys, `speaker_firm=None`
  - `extract_prompt(text: str) -> str`
  - `parse_phrases(envelope: dict) -> tuple[list[str], str]` — `(phrases, status)`
  - `is_limit_cliff(envelope: dict) -> bool`

- [ ] **Step 1: Write the failing test**

Append to `scripts/v3_ingest/test_topic_map.py`, immediately **before** the `# ─── runner ───` block:

```python
import json  # noqa: E402  (appended with the Task 4 tests)


def test_iter_question_units_keeps_only_analyst_speech():
    """The question side is analysts. corprep speech is the company talking
    about itself — that is evidence, and it arrives via claims.jsonl."""
    rows = [
        {"vector_id": "v1", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "analyst", "speaker_firm": "Wolfe Research LLC",
         "text": "I wanted to ask about the Chinese transceivers"},
        {"vector_id": "v2", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "corprep", "speaker_firm": None, "text": "Thanks"},
        {"vector_id": "v3", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "operator", "speaker_firm": None, "text": "Next"},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exchanges.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows))
        got = list(tm.iter_question_units(p))
        assert [u["unit_id"] for u in got] == ["v1"]
        assert got[0]["register"] == "question"
        assert got[0]["speaker_firm"] == "Wolfe Research LLC"
        assert got[0]["period_key"] == "2026Q3"


def test_iter_evidence_units_reads_claims_and_carries_the_clock():
    rows = [{"claim_id": "c1", "ticker": "ADI", "period_key": "2026Q3",
             "first_evidence_date": "2026-08-19", "text": "second source"}]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"
        p.write_text(json.dumps(rows[0]))
        got = list(tm.iter_evidence_units(p))
        assert got[0]["unit_id"] == "c1"
        assert got[0]["register"] == "evidence"
        assert got[0]["speaker_firm"] is None
        assert got[0]["first_evidence_date"] == "2026-08-19"


def test_parse_phrases_reads_a_json_array_from_the_envelope():
    env = {"is_error": False, "result": '["chinese transceiver competition", '
                                        '"800g ramp timing"]'}
    phrases, status = tm.parse_phrases(env)
    assert status == "ok"
    assert phrases == ["chinese transceiver competition", "800g ramp timing"]


def test_parse_phrases_reports_failed_not_empty_on_a_bad_envelope():
    """empty is answered-and-done; failed is unknown-and-retried. Conflating
    them is the b1c351aa lesson."""
    _, status = tm.parse_phrases({"is_error": True, "result": "boom"})
    assert status.startswith("failed"), status


def test_parse_phrases_treats_an_empty_array_as_answered():
    phrases, status = tm.parse_phrases({"is_error": False, "result": "[]"})
    assert phrases == []
    assert status == "empty"


def test_is_limit_cliff_matches_the_2026_08_11_signature():
    """267 pages died this way: instant return, one turn, zero cost. Detecting
    it is the difference between a resumable pause and an hour of burnt clock."""
    assert tm.is_limit_cliff({"is_error": True, "duration_api_ms": 0,
                              "num_turns": 1, "total_cost_usd": 0})
    assert not tm.is_limit_cliff({"is_error": True, "duration_api_ms": 3507,
                                  "num_turns": 2, "total_cost_usd": 0.07})
    assert not tm.is_limit_cliff({"is_error": False, "duration_api_ms": 0,
                                  "num_turns": 1, "total_cost_usd": 0})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: FAIL — `AttributeError: module 'topic_map' has no attribute 'iter_question_units'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/v3_ingest/topic_map.py`:

```python
# ───────────────────── input units, both registers ─────────────────────

import json          # noqa: E402  (appended with the Task 4 code)
import os            # noqa: E402
import re            # noqa: E402
import subprocess    # noqa: E402

EXCHANGES_PATH = REPO_ROOT / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS_PATH = REPO_ROOT / "state" / "evidence" / "claims.jsonl"

MODEL = "claude-sonnet-4-6"                # matches the other v3 wrappers
CLAUDE_TIMEOUT_S = 120
MIN_UNIT_WORDS = 8                         # below this there is no topic


def _calendar_quarter(date_iso: str) -> str:
    y, m, _ = date_iso.split("-")
    return f"{y}Q{(int(m) - 1) // 3 + 1}"


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue                       # torn line must not abort the run


def iter_question_units(path: Path = EXCHANGES_PATH):
    """Analyst speech only. corprep speech is the company describing itself,
    which is evidence and reaches us through claims.jsonl instead."""
    for r in _iter_jsonl(path):
        if r.get("speaker_type") != "analyst":
            continue
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        yield {
            "unit_id": r["vector_id"],
            "register": "question",
            "ticker": r.get("ticker"),
            "period_key": r.get("period_key")
                          or _calendar_quarter(r["event_date"]),
            "first_evidence_date": None,
            "speaker_firm": r.get("speaker_firm"),
            "text": text,
        }


def iter_evidence_units(path: Path = CLAIMS_PATH):
    for r in _iter_jsonl(path):
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        yield {
            "unit_id": r["claim_id"],
            "register": "evidence",
            "ticker": r.get("ticker"),
            "period_key": r.get("period_key"),
            "first_evidence_date": r.get("first_evidence_date"),
            "speaker_firm": None,
            "text": text,
        }


# ───────────────────────── phrase extraction ─────────────────────────

def extract_prompt(text: str) -> str:
    return (
        "Read the passage below from an earnings call or a company filing.\n"
        "List the distinct SUBJECT TOPICS it concerns — what it is about, not "
        "what it claims.\n\n"
        "Rules:\n"
        "- 2 to 5 words per topic, lowercase, no punctuation.\n"
        "- Name the subject matter, not the sentiment or direction. "
        "'chinese transceiver competition', not 'worry about china'.\n"
        "- At most 4 topics. Fewer is better. Return [] if it is small talk, "
        "an operator handoff, or pleasantries.\n"
        "- Do not name the company or the speaker.\n\n"
        "Reply with ONLY a JSON array of strings. No prose, no code fence.\n\n"
        "PASSAGE:\n" + text[:4000]
    )


def is_limit_cliff(envelope: dict) -> bool:
    """The 2026-08-11 signature: an error that returned instantly, took one
    turn and cost nothing. That is the usage limiter, not a bad prompt, and
    retrying into it just burns wall-clock. 267 pages died this way."""
    return bool(envelope.get("is_error")) \
        and envelope.get("duration_api_ms") == 0 \
        and envelope.get("num_turns") == 1 \
        and not envelope.get("total_cost_usd")


def parse_phrases(envelope: dict):
    """-> (phrases, status) where status is ok | empty | failed: <why>."""
    if envelope.get("is_error"):
        return [], f"failed: claude is_error {str(envelope.get('result'))[:120]}"
    raw = envelope.get("result") or ""
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return [], "failed: no JSON array in reply"
    try:
        items = json.loads(m.group(0))
    except ValueError as e:
        return [], f"failed: unparseable array ({e})"
    if not isinstance(items, list):
        return [], "failed: reply was not an array"
    phrases = [" ".join(str(x).lower().split()) for x in items
               if str(x).strip()]
    return (phrases, "ok") if phrases else ([], "empty")


def _claude_env() -> dict:
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)     # force subscription auth
    return env


def extract_phrases(text: str):
    """-> (phrases, status). Never raises; the caller records the status."""
    cmd = ["claude", "-p", extract_prompt(text),
           "--model", MODEL, "--output-format", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CLAUDE_TIMEOUT_S, env=_claude_env())
    except subprocess.TimeoutExpired:
        return [], "failed: timeout"
    except Exception as e:                            # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {e}"
    try:
        env = json.loads(proc.stdout)
    except ValueError:
        return [], f"failed: rc={proc.returncode} unparseable envelope"
    if is_limit_cliff(env):
        return [], "failed: usage-limit cliff"
    return parse_phrases(env)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: PASS — `13/13 pass`

- [ ] **Step 5: Lint and commit**

```bash
python3 scripts/check.py
git add scripts/v3_ingest/topic_map.py scripts/v3_ingest/test_topic_map.py
git commit -m "P2: phrase extraction over both registers, with cliff detection"
```

---

## Task 5: Candidate clustering and the operator review file

A phrase below threshold is one datapoint. A *cluster* of below-threshold phrases raised at several companies by several banks is a proposed theme. This is spec §4.2 step 4, and the gate that stops the review file being 4,000 one-off phrases.

**Files:**
- Modify: `scripts/v3_ingest/topic_map.py` (append)
- Modify: `scripts/v3_ingest/test_topic_map.py` (append before the runner)

**Interfaces:**
- Consumes: `cosine` (Task 3), unit dicts (Task 4).
- Produces:
  - `MIN_CANDIDATE_COMPANIES: int`, `MIN_CANDIDATE_BANKS: int`
  - `cluster_candidates(rows: list[dict], vecs: dict, threshold: float = 0.80) -> list[dict]`
  - `promotable(cluster: dict) -> bool`

- [ ] **Step 1: Write the failing test**

Append to `scripts/v3_ingest/test_topic_map.py` before the runner block:

```python
def test_cluster_candidates_groups_near_identical_phrasings():
    """Two analysts will never use the same words for the same idea. If the
    clusterer cannot see through that, no candidate ever reaches the gate."""
    rows = [
        {"unit_id": "u1", "phrase": "chinese transceiver competition",
         "ticker": "AAOI", "speaker_firm": "Wolfe", "register": "question"},
        {"unit_id": "u2", "phrase": "china transceiver competition",
         "ticker": "LITE", "speaker_firm": "Mizuho", "register": "question"},
        {"unit_id": "u3", "phrase": "silicon carbide pricing",
         "ticker": "ON", "speaker_firm": "Baird", "register": "question"},
    ]
    vecs = {"chinese transceiver competition": [1.0, 0.0],
            "china transceiver competition": [0.97, 0.24],
            "silicon carbide pricing": [0.0, 1.0]}
    got = tm.cluster_candidates(rows, vecs, threshold=0.80)
    sizes = sorted(len(c["unit_ids"]) for c in got)
    assert sizes == [1, 2], f"expected a 2-cluster and a singleton, got {sizes}"


def test_cluster_reports_distinct_companies_and_banks_not_raw_counts():
    """n_banks > n_companies > n_exchanges (spec §5). Forty mentions from one
    bank at one company is that company's marketing, not a diffusing idea."""
    rows = [
        {"unit_id": f"u{i}", "phrase": "chinese transceiver competition",
         "ticker": "AAOI", "speaker_firm": "Wolfe", "register": "question"}
        for i in range(40)
    ]
    vecs = {"chinese transceiver competition": [1.0, 0.0]}
    got = tm.cluster_candidates(rows, vecs, threshold=0.80)
    assert len(got) == 1
    assert got[0]["n_exchanges"] == 40
    assert got[0]["n_companies"] == 1
    assert got[0]["n_banks"] == 1


def test_promotable_requires_breadth_across_companies_and_banks():
    assert not tm.promotable({"n_companies": 1, "n_banks": 1})
    assert not tm.promotable({"n_companies": 5, "n_banks": 1})
    assert tm.promotable({"n_companies": tm.MIN_CANDIDATE_COMPANIES,
                          "n_banks": tm.MIN_CANDIDATE_BANKS})


def test_evidence_only_clusters_are_promotable_without_banks():
    """Stage 1 of §6.3 is evidence with NO questions. A gate that demands
    banks would discard exactly the earliest signal the system exists to find."""
    c = {"n_companies": tm.MIN_CANDIDATE_COMPANIES, "n_banks": 0,
         "registers": ["evidence"]}
    assert tm.promotable(c)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: FAIL — `AttributeError: module 'topic_map' has no attribute 'cluster_candidates'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/v3_ingest/topic_map.py`:

```python
# ───────────────────── new-theme candidate clustering ─────────────────────

MIN_CANDIDATE_COMPANIES = 3
MIN_CANDIDATE_BANKS = 2


def cluster_candidates(rows: list, vecs: dict, threshold: float = 0.80) -> list:
    """Greedy single-pass clustering of below-threshold phrases.

    Greedy, not k-means: the number of emergent topics is unknown by
    construction, and a centroid method needs that number up front. The cost
    is order-sensitivity, which is acceptable because the operator reads the
    clusters before anything is named.

    Reports n_banks / n_companies / n_exchanges separately — the §5 weighting
    is meaningless if they are collapsed into one count.
    """
    clusters = []
    for row in rows:
        v = vecs.get(row["phrase"])
        if v is None:
            continue
        placed = False
        for c in clusters:
            if cosine(v, c["_centroid"]) >= threshold:
                c["unit_ids"].append(row["unit_id"])
                c["phrases"].add(row["phrase"])
                c["_companies"].add(row.get("ticker"))
                if row.get("speaker_firm"):
                    c["_banks"].add(row["speaker_firm"])
                c["_registers"].add(row.get("register"))
                placed = True
                break
        if not placed:
            clusters.append({
                "_centroid": v,
                "unit_ids": [row["unit_id"]],
                "phrases": {row["phrase"]},
                "_companies": {row.get("ticker")},
                "_banks": ({row["speaker_firm"]}
                           if row.get("speaker_firm") else set()),
                "_registers": {row.get("register")},
            })

    out = []
    for c in clusters:
        out.append({
            "label_suggestion": sorted(c["phrases"])[0],
            "phrases": sorted(c["phrases"]),
            "unit_ids": c["unit_ids"],
            "registers": sorted(x for x in c["_registers"] if x),
            "n_exchanges": len(c["unit_ids"]),
            "n_companies": len({x for x in c["_companies"] if x}),
            "n_banks": len(c["_banks"]),
        })
    out.sort(key=lambda c: (c["n_banks"], c["n_companies"]), reverse=True)
    return out


def promotable(cluster: dict) -> bool:
    """Breadth gate before a cluster reaches the operator.

    Evidence-only clusters are exempt from the bank test: an analyst has by
    definition not asked about them yet, and that silence IS stage 1 of §6.3 —
    the earliest and most valuable state the system can report."""
    if cluster.get("registers") == ["evidence"]:
        return cluster.get("n_companies", 0) >= MIN_CANDIDATE_COMPANIES
    return (cluster.get("n_companies", 0) >= MIN_CANDIDATE_COMPANIES
            and cluster.get("n_banks", 0) >= MIN_CANDIDATE_BANKS)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: PASS — `17/17 pass`

- [ ] **Step 5: Lint and commit**

```bash
python3 scripts/check.py
git add scripts/v3_ingest/topic_map.py scripts/v3_ingest/test_topic_map.py
git commit -m "P2: new-theme candidate clustering behind a breadth gate"
```

---

## Task 6: CLI, resumable ledger, and the real run

Wires the stages together, adds the resume ledger, and runs against the real corpus. The threshold is calibrated here — against data, not by guess.

**Files:**
- Modify: `scripts/v3_ingest/topic_map.py` (append `main`)
- Modify: `scripts/v3_ingest/test_topic_map.py` (append before the runner)

**Interfaces:**
- Consumes: everything above; `scripts/chunking/embed.py::embed`.
- Produces:
  - `TOPICS_PATH`, `CANDIDATES_PATH`, `PROGRESS_PATH`
  - `main(argv=None) -> int`
  - Output row shape in `state/topics/topics.jsonl`:
    ```json
    {"unit_id": "3510330-t_..._qna_1_0", "register": "question",
     "ticker": "AAOI", "period_key": "2026Q3",
     "speaker_firm": "Wolfe Research LLC", "first_evidence_date": null,
     "phrase": "chinese transceiver competition",
     "theme": "china_ai_infrastructure_demand", "similarity": 0.81}
    ```

- [ ] **Step 1: Write the failing test**

Append to `scripts/v3_ingest/test_topic_map.py` before the runner block:

```python
def test_topic_row_carries_everything_the_metrics_need():
    """§5 needs speaker_firm for n_banks, ticker for n_companies, period_key
    for the quarter bucket, and first_evidence_date for the §6.3 clock. A row
    missing any of them silently breaks a metric downstream."""
    row = tm.topic_row(
        {"unit_id": "v1", "register": "question", "ticker": "AAOI",
         "period_key": "2026Q3", "speaker_firm": "Wolfe Research LLC",
         "first_evidence_date": None},
        "chinese transceiver competition", "china_ai_infrastructure_demand",
        0.81)
    for k in ("unit_id", "register", "ticker", "period_key", "speaker_firm",
              "first_evidence_date", "phrase", "theme", "similarity"):
        assert k in row, f"missing {k}"
    assert row["similarity"] == 0.81


def test_ledger_retries_failed_but_not_empty():
    """empty is answered-and-done; failed is unknown-and-retried."""
    with tempfile.TemporaryDirectory() as d:
        led = tm.Ledger(Path(d) / "_progress.json")
        led.record("u1", "ok", 2)
        led.record("u2", "empty", 0)
        led.record("u3", "failed: timeout", 0)
        assert led.done("u1") is True
        assert led.done("u2") is True
        assert led.done("u3") is False
        assert led.done("u4") is False


def test_ledger_survives_a_reload():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "_progress.json"
        tm.Ledger(p).record("u1", "ok", 2) or tm.Ledger(p).save()
        led = tm.Ledger(p)
        led.record("u1", "ok", 2)
        led.save()
        assert tm.Ledger(p).done("u1") is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: FAIL — `AttributeError: module 'topic_map' has no attribute 'topic_row'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/v3_ingest/topic_map.py`:

```python
# ───────────────────────── ledger, rows, CLI ─────────────────────────

import argparse  # noqa: E402  (appended with the Task 6 code)

STATE_DIR = REPO_ROOT / "state" / "topics"
TOPICS_PATH = STATE_DIR / "topics.jsonl"
CANDIDATES_PATH = STATE_DIR / "_candidates.json"
PROGRESS_PATH = STATE_DIR / "_progress.json"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))


class Ledger:
    """Three states per unit: ok / empty / failed. `empty` is
    answered-and-done, `failed` is unknown-and-retried."""

    def __init__(self, path: Path):
        self.path = path
        self.data = {"version": 1, "entries": {}}
        if path.exists():
            try:
                self.data = json.loads(path.read_text())
            except ValueError:
                pass
        self.data.setdefault("entries", {})

    def status(self, unit_id: str):
        e = self.data["entries"].get(unit_id)
        return e.get("status") if e else None

    def done(self, unit_id: str) -> bool:
        s = self.status(unit_id)
        return s in ("ok", "empty")

    def record(self, unit_id: str, status: str, n_phrases: int) -> None:
        self.data["entries"][unit_id] = {
            "status": status,
            "n_phrases": n_phrases,
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=1))


def topic_row(unit: dict, phrase: str, theme, similarity: float) -> dict:
    return {
        "unit_id": unit["unit_id"],
        "register": unit["register"],
        "ticker": unit.get("ticker"),
        "period_key": unit.get("period_key"),
        "speaker_firm": unit.get("speaker_firm"),
        "first_evidence_date": unit.get("first_evidence_date"),
        "phrase": phrase,
        "theme": theme,
        "similarity": round(float(similarity), 4),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P2 topic map (spec §4.2)")
    ap.add_argument("--threshold", type=float, default=SIM_THRESHOLD)
    ap.add_argument("--cluster-threshold", type=float, default=0.80)
    ap.add_argument("--limit", type=int, help="stop after N units (calibration)")
    ap.add_argument("--register", choices=["question", "evidence"],
                    action="append")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    import embed as emb                                # noqa: PLC0415

    themes = load_themes()
    log(f"{len(themes)} theme anchors from config/watchlist.yaml")

    want = set(args.register or ["question", "evidence"])
    units = []
    if "question" in want:
        units += list(iter_question_units())
    if "evidence" in want:
        units += list(iter_evidence_units())
    log(f"{len(units)} input units ({sorted(want)})")

    ledger = Ledger(PROGRESS_PATH)
    todo = [u for u in units if not ledger.done(u["unit_id"])]
    log(f"{len(todo)} units need phrase extraction "
        f"({len(units) - len(todo)} already done)")
    if args.limit:
        todo = todo[:args.limit]
        log(f"--limit {args.limit}: extracting {len(todo)}")

    if args.dry_run:
        for u in todo[:20]:
            log(f"  DRY {u['register']} {u['ticker']} {u['text'][:100]}")
        return 0

    emb.load_key()
    anchor_vecs = emb.embed([anchor_text(t) for t in themes],
                            "retrieval_document")

    extracted, cliff = [], False
    for i, u in enumerate(todo, 1):
        phrases, status = extract_phrases(u["text"])
        ledger.record(u["unit_id"], status, len(phrases))
        if status == "failed: usage-limit cliff":
            log(f"USAGE-LIMIT CLIFF after {i} units — stopping. Re-run later; "
                f"the ledger resumes without re-spending.")
            cliff = True
            break
        for p in phrases:
            extracted.append((u, p))
        if i % 50 == 0:
            ledger.save()
            log(f"  {i}/{len(todo)} units, {len(extracted)} phrases")
    ledger.save()
    log(f"extracted {len(extracted)} phrases from {len(todo)} units"
        + (" (stopped early)" if cliff else ""))

    if not extracted:
        log("nothing to map")
        return 1 if cliff else 0

    uniq = sorted({p for _, p in extracted})
    phrase_vecs = dict(zip(uniq, emb.embed(uniq, "retrieval_document")))
    log(f"embedded {len(uniq)} distinct phrases")

    assigned = assign([phrase_vecs[p] for _, p in extracted],
                      anchor_vecs, themes, threshold=args.threshold)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    rows, unmapped = [], []
    for (u, p), (theme, sim) in zip(extracted, assigned):
        rows.append(topic_row(u, p, theme, sim))
        if theme is None:
            unmapped.append({"unit_id": u["unit_id"], "phrase": p,
                             "ticker": u.get("ticker"),
                             "speaker_firm": u.get("speaker_firm"),
                             "register": u["register"]})

    with TOPICS_PATH.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    log(f"wrote {len(rows)} topic rows -> {TOPICS_PATH} "
        f"({len(rows) - len(unmapped)} inherited a theme, "
        f"{len(unmapped)} below threshold)")

    clusters = cluster_candidates(unmapped, phrase_vecs,
                                  threshold=args.cluster_threshold)
    ready = [c for c in clusters if promotable(c)]
    CANDIDATES_PATH.write_text(json.dumps({
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "threshold": args.threshold,
        "gate": {"min_companies": MIN_CANDIDATE_COMPANIES,
                 "min_banks": MIN_CANDIDATE_BANKS},
        "note": "Proposals only. The operator names or rejects each one; "
                "nothing here is written to config/watchlist.yaml.",
        "promotable": ready,
        "below_gate": len(clusters) - len(ready),
    }, indent=1))
    log(f"{len(ready)} candidate themes past the gate "
        f"({len(clusters) - len(ready)} below) -> {CANDIDATES_PATH}")
    return 1 if cliff else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/v3_ingest/test_topic_map.py`
Expected: PASS — `20/20 pass`

- [ ] **Step 5: Calibrate the threshold on a real sample**

Run: `python3 scripts/v3_ingest/topic_map.py --limit 150 --register question`

Read the reported inherited-vs-below-threshold split. Target roughly **60–80% inheriting an existing theme**. Then:
- **>90% inherit** → threshold too low; the vocabulary can never grow. Raise by 0.03 and re-run.
- **<40% inherit** → threshold too high; continuity with the 8,843 existing assignments is lost. Lower by 0.03 and re-run.

Update `SIM_THRESHOLD` in the source to the chosen value and record the observed split in a comment beside it. Re-running is cheap: the ledger skips extraction and `embed.py` caches by content hash, so only the assignment step repeats.

- [ ] **Step 6: Gold-test acceptance**

The spec's gold case is Chinese optical competition — a topic with **no** assigned theme in `config/watchlist.yaml`, which is precisely why it must arrive as a *candidate* rather than be forced into an existing box.

Run: `python3 scripts/v3_ingest/topic_map.py --register question`

Then verify both known exchanges produced a phrase, and that it did not get absorbed into an unrelated theme:

```bash
python3 - <<'PY'
import json
from pathlib import Path
rows = [json.loads(l) for l in
        Path("/root/research-watchlist/state/topics/topics.jsonl").read_text().splitlines() if l.strip()]
gold = [r for r in rows if r["unit_id"].startswith(("3510330-t", "3469684-t"))]
print(f"{len(gold)} topic rows from the two gold documents")
for r in gold:
    if any(w in r["phrase"] for w in ("china", "chinese", "laser", "transceiver")):
        print(f"  {r['ticker']:<6} {r['speaker_firm']} | {r['phrase']} -> "
              f"{r['theme']} ({r['similarity']})")
PY
```

**Pass condition:** at least one phrase from AAOI `3510330-t` mentioning Chinese transceivers/competition, and at least one from LITE `3469684-t` mentioning lasers. If either is absent, the phrase-extraction prompt is dropping the subject — fix `extract_prompt` and re-run those units (delete their ledger entries first). **Do not** hand-add the topic to make the test pass; that hardcodes the answer, which is the contamination the spec called out.

- [ ] **Step 7: Map the evidence side and confirm one namespace**

```bash
python3 scripts/v3_ingest/topic_map.py --register evidence
python3 - <<'PY'
import collections, json
from pathlib import Path
rows = [json.loads(l) for l in
        Path("/root/research-watchlist/state/topics/topics.jsonl").read_text().splitlines() if l.strip()]
by = collections.defaultdict(collections.Counter)
for r in rows:
    if r["theme"]:
        by[r["theme"]][r["register"]] += 1
both = {t: c for t, c in by.items() if len(c) == 2}
print(f"{len(by)} themes seen; {len(both)} carry BOTH registers")
for t, c in sorted(both.items(), key=lambda kv: -sum(kv[1].values()))[:10]:
    print(f"  {t:<40} question={c['question']:<5} evidence={c['evidence']}")
PY
```

**Pass condition:** at least one theme carries both registers. That is the proof §6.2's two-count gap is computable — a theme with `evidence > 0` and `question == 0` is a stage-1 topic, which is the whole point.

Note: `--register evidence` **overwrites** `topics.jsonl` as written. Before running Step 7, either extend `main` to merge registers instead of truncating, or run both registers in one invocation (`python3 scripts/v3_ingest/topic_map.py` with no `--register`). Prefer the single invocation — the ledger makes it resumable and it avoids the truncation trap entirely.

- [ ] **Step 8: Lint and commit**

```bash
python3 scripts/check.py
python3 scripts/v3_ingest/test_evidence_store.py
python3 scripts/v3_ingest/test_mdna_evidence.py
python3 scripts/v3_ingest/test_topic_map.py
git add scripts/v3_ingest/topic_map.py scripts/v3_ingest/test_topic_map.py
git commit -m "P2: topic_map CLI, resume ledger, calibrated threshold"
```

- [ ] **Step 9: Hand the candidates to the operator**

Print the promotable clusters for review. The operator names or rejects each one; nothing is written to `config/watchlist.yaml` by any script.

```bash
python3 - <<'PY'
import json
from pathlib import Path
d = json.loads(Path("/root/research-watchlist/state/topics/_candidates.json").read_text())
print(f"threshold {d['threshold']}, gate {d['gate']}, "
      f"{d['below_gate']} clusters below the gate\n")
for c in d["promotable"]:
    print(f"- {c['label_suggestion']}")
    print(f"    banks={c['n_banks']} companies={c['n_companies']} "
          f"exchanges={c['n_exchanges']} registers={','.join(c['registers'])}")
    print(f"    phrasings: {'; '.join(c['phrases'][:6])}")
PY
```

---

## Self-Review

**1. Spec coverage.**

| Spec section | Task |
|---|---|
| §4.2 anchors, embed, cosine inherit | Task 3 |
| §4.2 below-threshold → candidate, clustered, operator-reviewed | Tasks 5, 6 (Step 9) |
| §4.2 "operates over both registers, one vocabulary" | Task 4 (`iter_question_units` / `iter_evidence_units`), Task 6 Step 7 |
| §4.2 "never writes to watchlist.yaml" | Task 6 — candidates go to `_candidates.json`; asserted in the review note |
| §4.4 MD&A 10-Q Item 2 / 10-K Item 7 QoQ diff | Task 2 |
| §4.3/§4.4 `first_evidence_date` on every claim | Task 1 (raises without it), Task 2 (later filing dates it) |
| §5 `n_banks` > `n_companies` > `n_exchanges` reported separately | Task 5 |
| §5 no velocity/slope/smoothing | Global constraints; nothing in this plan computes a rate |
| §6.2 two-count gap computable | Task 6 Step 7 is the acceptance check |
| §6.3 lifecycle clock | `first_evidence_date` carried from claim → topic row |

**Not covered here, by design** — these belong to later plans: §4.3 `foreign_evidence.py` (P3; `cninfo_filings.py` exists but has never been run and `notes/foreign/` is empty), §4.5 `diffusion.py` (P4), §7 renderers and cadence (P5/P5b), §6.4 novel-name discovery.

**2. Placeholder scan.** No TBDs. Every code step carries runnable code; every verification step names the command and the pass condition. The two tuning steps (threshold, `MIN_WORDS`) give explicit numeric decision rules rather than "adjust as appropriate".

**3. Type consistency.** `claim_id` (Task 1) → `unit_id` (Task 4 `iter_evidence_units`) → `unit_ids` (Task 5 clusters) — the rename is deliberate and happens at one boundary. `period_key` is a calendar quarter string everywhere; `calendar_quarter` exists in both `evidence_store` and `topic_map` (as `_calendar_quarter`) because `topic_map` must not import the evidence module to read exchanges — a two-line duplication preferred over a dependency that would make the question side require the evidence side.

**One known wart, deliberately left in:** Task 6 Step 7 documents that `--register evidence` truncates `topics.jsonl`, and directs the executor to the single-invocation form. It is called out rather than silently fixed because an executor who runs the two registers separately will otherwise lose half the file and not notice.
