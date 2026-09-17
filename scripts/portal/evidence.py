"""Evidence index: scripts/portal/evidence.py (RIS4 slice 3, Task 1).

Loads state/thesis/evidence_log.jsonl (2,685 rows as of 2026-09-16; keys:
source, source_id, ref, date, title, assumption_id, direction ∈
confirm|challenge|neutral, strength 0-3, why, quote, cross_ticker, ts, ticker)
into an in-memory index keyed by (ticker, assumption_id), each row trimmed to
the fields a portal card/ticker bundle needs -- why/quote are truncated so one
long LLM-authored field can never balloon a card or a ticker bundle.

Read-only: this module never writes anywhere. Every path is overridable via
`Paths` (same dataclass-with-__post_init__-defaults pattern as reports.py's
own `Paths`) so tests run only against fixtures under
scripts/portal/fixtures/evidence/ -- the zero-arg default reads the live
REPO's state/thesis/evidence_log.jsonl.

Two other public functions build on the index:
  - `top(rows, n)` -- the ranking/cap rule shared by both consumers of this
    module (reports.py's thesis_alerts card and build_portal.py's per-ticker
    bundle attachment): sort by strength desc then date desc, drop strength-0
    rows when at least one row with strength >= 1 exists (an assumption with
    real signal shouldn't show a page of "strength 0, no real content" rows
    ahead of it), cap at `n`.
  - `attach_thesis(bundle, index)` -- sets `bundle["thesis"]["evidence"] =
    {assumption_id: top(rows)}` for every assumption in
    `bundle["thesis"]["fm_without_body"]["assumptions"]` (the ticker bundle's
    OWN key -- see vault.ticker_bundle's return shape; it is NOT called
    "fm"). A ticker with no thesis at all (empty/absent `fm_without_body`)
    gets no `evidence` key added -- `build_portal.py`'s `_stage_tickers_ingest`
    already treats an empty `fm_without_body` as "no thesis" for its own
    has-notes check, so this mirrors that convention. An assumption with no
    matching evidence rows still gets its own key, mapped to `[]` -- never
    silently dropped, so the frontend can render "no evidence yet" instead of
    treating a missing key as "not fetched".
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Bootstrap ONLY to make this package importable when this module is loaded as
# a bare `evidence` module (the no-pytest test harness convention, same as
# every other scripts/portal/*.py module -- see reports.py's own comment).
_here_parent = str(Path(__file__).resolve().parent.parent)
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402


def log(msg: str) -> None:
    print(f"[evidence] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Paths: overridable for tests, same pattern as reports.py's Paths
# ---------------------------------------------------------------------------
@dataclass
class Paths:
    repo: Path = REPO
    thesis_state: Path = None

    def __post_init__(self):
        self.thesis_state = self.thesis_state if self.thesis_state is not None \
            else (self.repo / "state" / "thesis")


DEFAULT_PATHS = Paths()

_ROW_FIELDS = ("date", "source", "source_id", "ref", "title", "direction",
               "strength", "why", "quote", "cross_ticker")
_WHY_CAP, _QUOTE_CAP = 200, 300


def _trim(row: dict) -> dict:
    out = {k: row.get(k) for k in _ROW_FIELDS}
    if out.get("why"):
        out["why"] = str(out["why"])[:_WHY_CAP]
    if out.get("quote"):
        out["quote"] = str(out["quote"])[:_QUOTE_CAP]
    return out


# ---------------------------------------------------------------------------
# load_index
# ---------------------------------------------------------------------------
def load_index(paths: Paths = None) -> dict:
    """{(ticker, assumption_id): [row, ...]} from evidence_log.jsonl, each row
    trimmed via `_trim`. Rows missing `ticker` or `assumption_id` (a row that
    never matched an assumption) are skipped -- they have no key to index
    under. A missing file returns {} plus one log line, never an error, same
    convention as reports.py's `news_digest_files`/`_digest_sections`.
    """
    paths = paths or DEFAULT_PATHS
    p = paths.thesis_state / "evidence_log.jsonl"
    if not p.exists():
        log(f"load_index: {p} missing -- returning {{}}")
        return {}
    index: dict = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ticker, aid = row.get("ticker"), row.get("assumption_id")
        if not ticker or not aid:
            continue
        index.setdefault((ticker, aid), []).append(_trim(row))
    return index


# ---------------------------------------------------------------------------
# top
# ---------------------------------------------------------------------------
def top(rows: list, n: int = 6) -> list:
    """Sort by strength desc, then date desc; drop strength==0 rows when at
    least one row with strength >= 1 exists (an all-zero-strength assumption
    keeps its rows -- there is no signal to prioritize over them); cap at `n`.
    Never filters by date/age -- that is the card-builder's job (reports.py
    applies its own 7-day window on top of this), not this module's.
    """
    if not rows:
        return []
    has_signal = any((r.get("strength") or 0) >= 1 for r in rows)
    pool = [r for r in rows if not (has_signal and (r.get("strength") or 0) == 0)]
    ordered = sorted(pool, key=lambda r: ((r.get("strength") or 0), str(r.get("date") or "")),
                      reverse=True)
    return ordered[:n]


# ---------------------------------------------------------------------------
# attach_thesis
# ---------------------------------------------------------------------------
def attach_thesis(bundle: dict, index: dict) -> None:
    """Mutates `bundle` in place: sets bundle["thesis"]["evidence"] =
    {assumption_id: top(rows)} for every assumption in
    bundle["thesis"]["fm_without_body"]["assumptions"]. Call this from
    build_portal.py's `_stage_tickers_ingest`, right after
    `vault.ticker_bundle(...)` returns and BEFORE the bundle is written to
    disk -- state_bundles.manifest() hashes files at the state stage (after
    this stage has already run), so the evidence key is safely inside every
    hash. A ticker with no thesis (`fm_without_body` empty/absent) is left
    completely alone -- no `evidence` key is added, matching
    `_stage_tickers_ingest`'s own "no thesis" test
    (`bool(b["thesis"]["fm_without_body"])`).
    """
    thesis = bundle.get("thesis")
    if not thesis:
        return
    fm = thesis.get("fm_without_body") or {}
    if not fm:
        return
    ticker = bundle.get("ticker")
    ev = {}
    for a in fm.get("assumptions") or []:
        aid = a.get("id")
        if not aid:
            continue
        ev[aid] = top(index.get((ticker, aid), []))
    thesis["evidence"] = ev
