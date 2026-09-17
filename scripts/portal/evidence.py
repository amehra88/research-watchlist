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

Slice 3 Task 2 adds stage-alert enrichment. `reports.py`'s `_stage_alert_render_
inputs` loads state/topics/diffusion.json and state/topics/topic_map.jsonl
(`load_topic_map_rows` -- ~6 MB, ~18.7K rows, not scoped), then resolves the day's
cited tickers (via `_cite_target`, the SAME per-kind logic `stage_alert.render()`
itself uses -- see reports.py) and loads state/transcripts/exchanges.jsonl scoped
to JUST those tickers (`load_exchanges_by_ticker` -- see fix round 1 below), and
hands both loaded structures to `stage_alert.render()` AND to this module's own
functions:
  - `load_topic_map_rows(path)` / `load_exchanges_by_ticker(tickers, path)` --
    fix round 1 (reviewer-required): exchanges.jsonl (30 MB / ~16.4K rows in
    production) was previously loaded WHOLE via `theme_notes.load_sources()`
    regardless of which tickers the day's events could possibly cite.
    `load_exchanges_by_ticker` streams the file exactly once, line-at-a-time
    (never holding the whole 30 MB as one string), keeping only rows whose
    `ticker` is in the caller-supplied set -- typically 1-3 tickers on a live
    day, so the retained `ex` dict is a small fraction of the file (every row
    for one document shares that document's ticker, so this can never split a
    document's own question/answer rows across the keep/drop line). The SAME
    filtered `ex` is passed to `stage_alert.render()` too -- render() only ever
    cites the one ticker `_cite_target` already resolved for that event, so a
    ticker-scoped `ex` is sufficient for both callers, not just this module's.
  - `exchange_for(event, tm_rows, ex)` -- the analyst exchange stage_alert.render()
    itself would cite for `event = {theme, ticker, date}`, enriched with the
    management answer that immediately follows it in the same document. Deviates
    from the brief's `exchange_for(event, ex_rows)` shorthand by taking `tm_rows`
    too: stage_alert.first_question_cite() -- the rule this MUST replicate, not
    reinvent -- picks the cited analyst row by topic_map's own per-row theme
    score (see `stage_alert._score`), and that score lives only in topic_map
    rows, never in a raw exchange row. `ex` doubles as both the vector_id lookup
    first_question_cite() itself uses AND the source for the sibling-row scan
    (grouped once via `index_exchanges_by_document`).
  - `index_exchanges_by_document(ex)` -- {document_id: [row, ...]} from `ex`'s
    values, each document's rows ordered by transcript turn (see `_doc_num_key`
    -- `doc_num` values repeat across a split turn, e.g. two rows both
    "qna_19"; the trailing `_N` on `vector_id` breaks that tie). Built once per
    card and passed into `exchange_for` so a multi-event day doesn't re-group
    the (now ticker-scoped, much smaller) `ex` per event.
  - `breadth_trend(theme, diffusion)` -- the two most recent `cal_quarter` cells
    for `theme` in `diffusion["metrics"]` (string sort works: "CY2026-Q1" <
    "CY2026-Q2"). None when the theme has no metrics cells at all; a
    first-quarter theme still returns a dict with `prev_*` fields None -- there
    is legitimately no prior breadth to compare against, which is different
    from "diffusion.json itself is missing".
  - `tier_names_on_theme(theme, diffusion, universe)` -- every ticker paired
    with `theme` in `diffusion["pairs"]` (a stage means "on theme"; a bare
    mention in `metrics.companies` without a pair does not), split into
    `{tier_1: [...], tier_2: [...]}` by intersecting with `universe`'s
    (`identity.load_universe()`'s own shape) `tier_1_bctk`/
    `tier_2_active_candidates` tiers. `tier_3_watchlist` and orphan-notes
    entries are excluded by construction -- the output dict only ever has
    these two keys.
None of the three ever raises on a gap (empty/absent input) -- reports.py's own
try/except per-call still logs the one line the brief asks for; these
functions just return the "nothing to report" value (None/[]/{}) quietly.
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


# ---------------------------------------------------------------------------
# stage alert enrichment (Task 2): exchange citations, breadth trend, tiers
# ---------------------------------------------------------------------------
_QUESTION_CAP, _ANSWER_CAP = 400, 400


def _theme_score(row: dict, theme: str) -> float:
    """Identical to stage_alert._score -- replicated (not imported; stage_alert.py
    is out of scope for this task) because first_question_cite()'s candidate
    selection depends on it and this module needs the same tie-break."""
    return max((t.get("score", 0.0) for t in row.get("themes") or [] if t.get("theme") == theme),
               default=0.0)


def _cited_question_row(theme: str, ticker: str, date: str, tm_rows: list, ex: dict) -> dict | None:
    """The raw exchange row (document_id, doc_num, vector_id and all) for the analyst
    question stage_alert.first_question_cite() would cite -- the IDENTICAL candidate
    filter and highest-cosine tie-break, replicated here because first_question_cite()
    itself only returns {speaker, firm, event}, never the document_id/doc_num this
    module needs to find the paired answer. Returns None in exactly the same cases
    first_question_cite() would (no candidate rows, or the winning row's id isn't in
    `ex`)."""
    cands = [r for r in tm_rows if r.get("register") == "question" and r.get("ticker") == ticker
             and str(r.get("event_date") or "")[:10] == date and _theme_score(r, theme) > 0
             and r.get("id") in ex]
    if not cands:
        return None
    best = max(cands, key=lambda r: _theme_score(r, theme))
    return ex[best["id"]]


def _doc_num_key(row: dict) -> tuple:
    """Sort key for one document's transcript turns. `doc_num` (e.g. "qna_19") is not
    unique within a document -- a turn split across multiple vector rows repeats the
    same doc_num (observed live: 2,429 duplicate (document_id, doc_num) pairs in
    production exchanges.jsonl) -- so the trailing `_N` on `vector_id` (the split
    index FactSet assigns, e.g. "..._qna_19_0", "..._qna_19_1") is the tie-break, not
    file order (file order is NOT chronological -- verified against a live
    transcript)."""
    dn = row.get("doc_num") or ""
    sect, _, num = dn.rpartition("_")
    try:
        num = int(num)
    except ValueError:
        num = 0
    vid = row.get("vector_id") or ""
    try:
        idx = int(vid.rsplit("_", 1)[-1])
    except ValueError:
        idx = 0
    return (sect, num, idx)


def index_exchanges_by_document(ex: dict) -> dict:
    """{document_id: [row, ...]} from `ex`'s values (a vector_id -> raw-row map, e.g.
    `load_exchanges_by_ticker()`'s own return value), each document's rows ordered by
    `_doc_num_key`. Built once per card/build, not once per event -- see this
    module's docstring."""
    by_doc: dict = {}
    for r in (ex or {}).values():
        by_doc.setdefault(r.get("document_id"), []).append(r)
    for doc_id, rows in by_doc.items():
        rows.sort(key=_doc_num_key)
    return by_doc


def load_topic_map_rows(path: Path) -> list:
    """topic_map.jsonl's rows as a plain list -- no ticker filtering (it's ~6 MB in
    production, a fifth the size of exchanges.jsonl, and `_cited_question_row`'s own
    candidate filter already narrows by ticker/date/theme-score internally). Missing
    file -> [] + one log line, never an error; malformed lines are skipped."""
    path = Path(path)
    if not path.exists():
        log(f"load_topic_map_rows: {path} missing -- returning []")
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def load_exchanges_by_ticker(tickers: set, path: Path) -> dict:
    """{vector_id: row} from `path` (state/transcripts/exchanges.jsonl, ~30 MB / 16K
    rows in production), streamed ONCE and keeping only rows whose `ticker` is in
    `tickers` -- every row for a given document shares that document's ticker, so
    this never splits a document's own question/answer rows across the keep/drop
    line. `tickers` should be built from the day's fresh stage-alert events BEFORE
    calling this (see reports.py's `_stage_alert_render_inputs`), so the read only
    pays for what today's events could possibly cite -- not the whole universe.
    Missing file -> {} + one log line, never an error; malformed lines are skipped."""
    path = Path(path)
    if not path.exists():
        log(f"load_exchanges_by_ticker: {path} missing -- returning {{}}")
        return {}
    ex: dict = {}
    # Real line-at-a-time iteration (not read_text().splitlines()) -- the point of
    # streaming a 30 MB file is to never hold the whole thing as one string in
    # memory at once, only the filtered rows that survive.
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ticker") in tickers and r.get("vector_id"):
                ex[r["vector_id"]] = r
    return ex


_ANSWER_ROW_CAP = 3


def _management_answer(cited: dict, doc_rows: list, row_cap: int = _ANSWER_ROW_CAP) -> str | None:
    """Joins up to `row_cap` consecutive corprep ("management-side") rows immediately
    after `cited` within `doc_rows` (already sorted by `_doc_num_key`).

    A `speaker_type: None` row is ambiguous -- verified live, most are a genuine
    management-answer continuation with no recorded speaker_type at all (e.g.
    document 3449181-t), but the reviewer also reproduced a real transcript shape
    where a None-typed row is actually a SECOND analyst turn sitting between two
    unrelated answers (`[q1, ans1, None-typed follow-up, ans2, operator]`), and
    joining straight through it would splice ans2 onto q1's answer. Controller
    ruling: the join STOPS at the first `speaker_type: None` row UNLESS the row
    immediately after it is corprep AND has the SAME `speaker_name` as the last
    corprep row already joined (a real continuation never changes speaker) -- in
    that case the None row itself is skipped (never added to the answer) and the
    scan continues past it. The scan otherwise stops the instant it hits an
    unambiguous turn change (`analyst` or `operator`). None when the cited row
    isn't found in `doc_rows`, or nothing corprep follows it before a stop."""
    try:
        i = next(idx for idx, r in enumerate(doc_rows) if r.get("vector_id") == cited.get("vector_id"))
    except StopIteration:
        return None
    parts: list[str] = []
    last_speaker = None
    j, n = i + 1, len(doc_rows)
    while j < n and len(parts) < row_cap:
        r = doc_rows[j]
        st = r.get("speaker_type")
        if st == "corprep":
            if r.get("text"):
                parts.append(r["text"])
            last_speaker = r.get("speaker_name")
            j += 1
            continue
        if st in ("analyst", "operator"):
            break
        # st is None (or some other unrecorded value): ambiguous -- only a
        # continuation (see docstring) lets the scan pass through it.
        nxt = doc_rows[j + 1] if j + 1 < n else None
        if (last_speaker is not None and nxt is not None
                and nxt.get("speaker_type") == "corprep" and nxt.get("speaker_name") == last_speaker):
            j += 1  # skip the ambiguous row itself; its text is never joined
            continue
        break
    return " ".join(parts) if parts else None


def exchange_for(event: dict, tm_rows: list | None, ex: dict | None,
                  ex_by_doc: dict | None = None) -> dict | None:
    """{date, event_name, speaker_name, speaker_firm, question, answer, view_url} for
    `event = {theme, ticker, date}` -- `date` is the SAME first_question_date
    stage_alert.render() itself resolved for this event (see reports.py's
    `_cite_target`, which mirrors render()'s own per-kind picks; this function does
    not re-derive which ticker/date a stage2/stage3 event cites, only which exchange
    row that triple points at). `ex_by_doc` is `index_exchanges_by_document(ex)` --
    passed in so a multi-event build doesn't re-group `ex` per event; omitting it
    (the default) groups on the fly for standalone/test use.
    Returns None -- never raises -- when `tm_rows`/`ex` are absent (gap: no
    diffusion/exchanges data loaded), `theme`/`ticker`/`date` are incomplete (gate/
    stage4 events cite no single ticker), or no matching analyst row exists.
    """
    theme, ticker, edate = (event or {}).get("theme"), (event or {}).get("ticker"), (event or {}).get("date")
    if not theme or not ticker or not edate or tm_rows is None or ex is None:
        return None
    cited = _cited_question_row(theme, ticker, edate, tm_rows, ex)
    if cited is None:
        return None
    by_doc = ex_by_doc if ex_by_doc is not None else index_exchanges_by_document(ex)
    answer = _management_answer(cited, by_doc.get(cited.get("document_id"), []))
    return {
        "date": str(cited.get("event_date") or edate)[:10],
        "event_name": cited.get("event_name"),
        "speaker_name": cited.get("speaker_name"),
        "speaker_firm": cited.get("speaker_firm"),
        "question": str(cited.get("text") or "")[:_QUESTION_CAP],
        "answer": answer[:_ANSWER_CAP] if answer else None,
        "view_url": cited.get("view_url"),
    }


def breadth_trend(theme: str, diffusion: dict | None) -> dict | None:
    """{current_quarter, n_banks, n_companies, n_disclosing, prev_quarter,
    prev_n_banks, prev_n_companies} from the two most recent `cal_quarter` cells for
    `theme` in `diffusion["metrics"]`. None when `diffusion` is absent or the theme
    has zero cells -- never raises."""
    cells = sorted((m for m in (diffusion or {}).get("metrics", []) if m.get("theme") == theme),
                   key=lambda m: m.get("cal_quarter") or "")
    if not cells:
        return None
    cur, prev = cells[-1], (cells[-2] if len(cells) >= 2 else None)
    return {
        "current_quarter": cur.get("cal_quarter"),
        "n_banks": cur.get("n_banks", 0),
        "n_companies": cur.get("n_companies", 0),
        "n_disclosing": cur.get("n_disclosing", 0),
        "prev_quarter": prev.get("cal_quarter") if prev else None,
        "prev_n_banks": prev.get("n_banks") if prev else None,
        "prev_n_companies": prev.get("n_companies") if prev else None,
    }


def tier_names_on_theme(theme: str, diffusion: dict | None, universe: list | None) -> dict:
    """{tier_1: [ticker, ...], tier_2: [ticker, ...]} (sorted) -- every ticker paired
    with `theme` in `diffusion["pairs"]` that also appears in `universe`
    (`identity.load_universe()`'s own shape) under `tier_1_bctk`/
    `tier_2_active_candidates`. Both lists are empty when `diffusion`/`universe` is
    absent or nothing overlaps -- never raises, and the shape is always the same two
    keys (reports.py substitutes the brief's literal `{}` itself for the "snap never
    loaded at all" gap case, alongside `exchange`/`trend` going null -- see
    `_stage_alert_card`)."""
    out = {"tier_1": [], "tier_2": []}
    if not diffusion or not universe:
        return out
    tickers = {p.get("ticker") for p in diffusion.get("pairs", []) if p.get("theme") == theme}
    tier_key = {"tier_1_bctk": "tier_1", "tier_2_active_candidates": "tier_2"}
    for u in universe:
        tk, tier = u.get("ticker"), u.get("tier")
        if tk in tickers and tier in tier_key:
            out[tier_key[tier]].append(tk)
    out["tier_1"].sort()
    out["tier_2"].sort()
    return out
