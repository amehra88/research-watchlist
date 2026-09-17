"""Code §5/§6/§7 analyst prose into structured JSON rows via a lean `claude -p` call.

`score_reads.py` (RIS5 A1) already isolates the verb/value in each section/sub-block's
explicit "Recommendation:" sentence. This module reuses its exact §-split and §6
sub-block isolation (`score_reads._sections`, `score_reads._SUBBLOCK_LABELS`) to grab the
FULL section/sub-block prose -- evidence + recommendation + reasoning -- and asks the
model to code it: a 1-5 score (or null), a direction (up/flat/down), a magnitude (0-2), a
short reason, and a verbatim supporting quote. The two modules join on (note_id, axis).

Model contract: one lean `claude -p` call per batch of BATCH_SIZE notes (all axes for
those notes combined into one prompt), Sonnet, a fixed system prompt, PROMPT_VERSION
"v1". Returns a JSON array; every element is validated against a schema (axis in
thesis_io.SCORE_KEYS, score 1-5 or null, direction/magnitude enums, reason/quote length
caps, and the quote must appear VERBATIM in the section text it was drawn from) --
anything that fails validation is dropped and logged, never silently coerced.

Failure handling (mirrors newsdigest/classify_llm.py's precheck-first pattern):
  - malformed/unparseable JSON, or a claude -p timeout, or a non-429 claude -p error ->
    retry the SAME batch once, then log and skip the whole batch (no split ladder --
    this job has no per-row fail-loud contract, unlike the news classifier).
  - a subscription 429 (SessionLimitError), or the lean-mode wrapper ceiling regressing
    (claude_p.ClaudeWrapperRegression) -> FAIL LOUD, propagates immediately, no retry, no
    split. `--backfill` aborts the run (rows already written stay written, since each
    batch is appended as it completes); the cron hook's caller catches it.
  - a batch that exhausts its retry and is skipped increments `batch_failures` in the
    summary dict (and process_notes()'s `omitted` count), and `main()` exits 1 -- so a
    100%-failed run (e.g. a lapsed subscription OAuth returning rc=1 on every call) is
    never indistinguishable from a clean zero-drop run.

Row id = sha1(note_id|axis|prompt_version) -- appends are idempotent across reruns of the
same prompt version.

CLI (run only inside the quota window -- see the module docstring in the task brief):
    python3 scripts/thesis/structure_reads.py --backfill --dry-run
    python3 scripts/thesis/structure_reads.py --backfill --ticker AMAT
    python3 scripts/thesis/structure_reads.py --backfill --since 2026-08-01
    python3 scripts/thesis/structure_reads.py --backfill --out /path/to/reads.jsonl

Hook (production, `scripts/cron_earnings_reviewer.py`, after a note is written):
    from thesis import structure_reads
    structure_reads.process_notes([note_path])   # caller wraps in try/except, never raises
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")   # canonical vault root -- for READING notes/state paths only
                                          # (see module docstring / task brief); NOT used for import
                                          # resolution below, since score_reads.py (RIS5 A1) is a
                                          # worktree-only sibling not yet merged into that checkout.
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]   # this file's own scripts/ dir -- resolves against
                                                      # wherever structure_reads.py actually lives (the
                                                      # worktree now, /root/research-watchlist after merge),
                                                      # so `thesis.score_reads` always resolves to a sibling
                                                      # that is actually on disk next to this file.
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "lib"))
from thesis import STATE_DIR, thesis_io as tio                       # noqa: E402
from thesis.score_reads import (                                     # noqa: E402
    NOTES, _sections, _SUBBLOCK_LABELS, parse_note_id, iter_note_paths,
)
import claude_p                                                      # noqa: E402

READS_PATH = STATE_DIR / "reads.jsonl"

MODEL = "sonnet"
PROMPT_VERSION = "v1"
BATCH_SIZE = 5                    # notes per claude -p call (up to 5 axes/note -> <=25 items)
CLAUDE_TIMEOUT_S = 600             # output-bound (25 quote+reason objects); no-margin 300s caused
                                   # rc=124 aborts elsewhere (see earnings_reviewer_calendar_timeout memory)
MAX_ATTEMPTS = 2                   # 1 try + 1 retry, then log and skip the batch
RETRY_BACKOFF_S = 15

# Fixed system prompt, used verbatim (per task brief) -- the full output contract lives in
# the user prompt (INSTRUCTIONS below), matching the lean-mode split classify_llm.py uses.
SYSTEM_PROMPT = "code this analyst paragraph as JSON, quote verbatim"

_VALID_DIRECTIONS = {"up", "flat", "down"}
_VALID_MAGNITUDES = {0, 1, 2}
_REASON_MAX = 160
_QUOTE_MAX = 240


class SessionLimitError(RuntimeError):
    """claude -p returned a 429 session/usage-limit result -- NON-RETRYABLE.

    Mirrors newsdigest/classify_llm.py's SessionLimitError: a 429 means the shared
    subscription quota is exhausted, not that this batch was bad. It must propagate
    immediately (fail loud) so the caller aborts instead of burning more quota."""
    def __init__(self, reset_hint: str = ""):
        self.reset_hint = reset_hint
        super().__init__("claude -p session limit reached (429)"
                         + (f" -- {reset_hint}" if reset_hint else ""))


_SESSION_LIMIT_RE = re.compile(r"session limit|usage limit", re.I)


def _detect_session_limit(stdout: str):
    """Reset hint string (may be '') if `stdout` carries a 429 session-limit result, else
    None. Same detection shape as classify_llm._detect_session_limit: handles both the
    parsed-JSON envelope and a raw-text fallback when stdout is truncated/unparseable."""
    if not stdout:
        return None
    try:
        env = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        env = None
    if isinstance(env, dict):
        body = str(env.get("result") or "")
        is_429 = env.get("api_error_status") == 429 or (env.get("is_error") and _SESSION_LIMIT_RE.search(body))
    else:
        body = stdout
        is_429 = ('"api_error_status":429' in stdout or '"api_error_status": 429' in stdout
                  or _SESSION_LIMIT_RE.search(stdout))
    if not is_429:
        return None
    m = re.search(r"resets[^\"'.}]*", body or "")
    return (m.group(0).strip() if m else "")


def _precheck_session_limit(stdout: str) -> None:
    """Passed to claude_p.run(precheck=...); ordering is load-bearing -- see claude_p.run's
    docstring. Raises SessionLimitError BEFORE the returncode/is_error envelope is examined."""
    hint = _detect_session_limit(stdout)
    if hint is not None:
        raise SessionLimitError(hint)


# ───────────────────────────── §-extraction (mirrors score_reads.parse_recs) ─────────────────────────────

def axis_texts(note_text: str) -> dict[str, str]:
    """{axis: full section/sub-block text} for every axis present in the note.

    Same §5/§6/§7 split (score_reads._sections) and §6 sub-block isolation
    (score_reads._SUBBLOCK_LABELS, same one-line regex score_reads.parse_recs uses
    inline) as A1's score_reads.py, in thesis_io.SCORE_KEYS order -- so the two modules
    join cleanly on (note_id, axis). Unlike parse_recs, this keeps the WHOLE block (not
    just the recommendation line): evidence + recommendation + reasoning, which is what
    the model needs to code a read.
    """
    sec = _sections(note_text)
    out: dict[str, str] = {}
    if "5" in sec:
        out["ai_positioning"] = sec["5"].strip()
    if "6" in sec:
        for label, key in _SUBBLOCK_LABELS:
            blk = re.search(rf"\*\*{label}\*\*.*?(?=\n- \*\*|\Z)", sec["6"], re.S)
            if blk:
                out[key] = blk.group(0).strip()
    if "7" in sec:
        out["potential_investor_interest.score"] = sec["7"].strip()
    return out


# ───────────────────────────── prompt construction ─────────────────────────────

INSTRUCTIONS = """\
You are coding analyst commentary from earnings/conference-call review notes into
structured JSON rows for a quantitative research pipeline. You are given a numbered list
of ITEMS. Each item is one excerpt of markdown prose -- an analyst's evidence,
recommendation and reasoning for ONE axis of ONE note.

For EACH item, return exactly one JSON object:
  "note_id": echo the item's note_id exactly.
  "axis": echo the item's axis exactly.
  "score": the analyst's numeric score for this axis as a plain integer 1-5 (drop any
    trailing +/- modifier, e.g. "4+" -> 4), or null if no score is stated or inferable.
  "direction": "up" if this read moves the axis higher than its prior/current score,
    "down" if lower, "flat" if unchanged, reaffirmed, or ambiguous.
  "magnitude": 0 (no real change / reaffirm), 1 (a modest revision), or 2 (a significant
    revision or a big swing in the underlying evidence).
  "reason": ONE short clause, in your own words, <=160 characters, explaining why.
  "quote": the single most load-bearing sentence or clause from the item's text, copied
    VERBATIM -- character-for-character, including any "**" markdown bold markers and
    exact punctuation, with no re-wrapping or paraphrasing -- from that item's text only.
    <=240 characters.

OUTPUT: ONLY a JSON array (no prose, no markdown, no code fences), one object per input
item, in this exact shape:
{"note_id": str, "axis": str, "score": int|null, "direction": "up"|"flat"|"down",
 "magnitude": 0|1|2, "reason": str, "quote": str}
Return exactly one object per input item -- never merge, split, or skip an item.
"""


def _item_block(items: list[tuple[str, str, str]]) -> str:
    out = ["ITEMS:"]
    for note_id, axis, text in items:
        out.append(f"\n[note_id: {note_id} | axis: {axis}]")
        out.append(text)
    return "\n".join(out)


def build_prompt(items: list[tuple[str, str, str]]) -> str:
    """The exact prompt sent to claude -p for one batch. Pure function."""
    return INSTRUCTIONS + "\n\n" + _item_block(items) + "\n"


# ───────────────────────────── validation ─────────────────────────────

def _normalize_loose(s: str) -> str:
    """Strip markdown bold markers and collapse whitespace -- used only for the diagnostic
    'would this quote have passed under a looser check' counter, never for acceptance."""
    return re.sub(r"\s+", " ", s.replace("**", "")).strip()


def _coerce_score(v):
    """(score_or_None, ok). ok=False means "drop, bad_score" -- None with ok=True is a
    legitimate null score. Tolerates a stray "4+"/"4-" idiom the model wasn't asked for."""
    if v is None:
        return None, True
    if isinstance(v, bool):
        return None, False
    if isinstance(v, int):
        return (v, True) if 1 <= v <= 5 else (None, False)
    if isinstance(v, float) and v.is_integer():
        iv = int(v)
        return (iv, True) if 1 <= iv <= 5 else (None, False)
    if isinstance(v, str):
        s = v.strip().rstrip("+-")
        if s.isdigit():
            iv = int(s)
            return (iv, True) if 1 <= iv <= 5 else (None, False)
    return None, False


def _validate_row(obj: dict, text_by_key: dict[tuple[str, str], str]) -> tuple[dict | None, str]:
    """(row, reason). row is None on any validation failure; reason is a short bucket key
    for the caller's drop-reason counters (see the module docstring: "bucket, don't just
    count" -- a bad_score drop must never look identical to a bad quote drop in the log)."""
    if not isinstance(obj, dict):
        return None, "not_a_dict"
    note_id = str(obj.get("note_id") or "")
    axis = str(obj.get("axis") or "")
    key = (note_id, axis)
    if key not in text_by_key:
        return None, "unknown_key"
    if axis not in tio.SCORE_KEYS:
        return None, "bad_axis"
    score, score_ok = _coerce_score(obj.get("score"))
    if not score_ok:
        return None, "bad_score"
    direction = obj.get("direction")
    if direction not in _VALID_DIRECTIONS:
        return None, "bad_direction"
    magnitude = obj.get("magnitude")
    if isinstance(magnitude, bool) or magnitude not in _VALID_MAGNITUDES:
        return None, "bad_magnitude"
    reason = obj.get("reason")
    if not isinstance(reason, str):
        return None, "bad_reason"
    if not reason:
        return None, "reason_empty"
    if len(reason) > _REASON_MAX:
        return None, "reason_too_long"
    quote = obj.get("quote")
    if not isinstance(quote, str):
        return None, "bad_quote"
    if not quote:
        return None, "quote_empty"
    if len(quote) > _QUOTE_MAX:
        return None, "quote_too_long"
    text = text_by_key[key]
    if quote not in text:
        if _normalize_loose(quote) in _normalize_loose(text):
            return None, "quote_not_verbatim_loose_match"   # diagnostic bucket, still dropped
        return None, "quote_not_verbatim"
    return ({"note_id": note_id, "axis": axis, "score": score, "direction": direction,
            "magnitude": int(magnitude), "reason": reason, "quote": quote}, "ok")


# ───────────────────────────── claude -p call ─────────────────────────────

def _run_claude(prompt: str, timeout: int = CLAUDE_TIMEOUT_S) -> tuple[str, float]:
    """Lean-mode `claude -p`. Monkeypatch seam for tests (same shape as
    newsdigest/classify_llm.py's `_run_claude`): tests stub `structure_reads._run_claude`
    so no real claude -p / network is touched."""
    text, cost, _env = claude_p.run(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL,
                                    cwd=str(REPO), timeout=timeout,
                                    precheck=_precheck_session_limit)
    return text, cost


def _extract_json_array(text: str):
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _call_batch(items: list[tuple[str, str, str]], logger=None,
                timeout: int = CLAUDE_TIMEOUT_S) -> tuple[list[dict], float, dict, bool]:
    """One claude -p call (with one retry) for `items` = [(note_id, axis, text)].

    Returns (validated_rows, cost, drop_reason_counts, batch_failed). A 429
    (SessionLimitError) or a ClaudeWrapperRegression propagates immediately -- never
    caught here. Malformed JSON, a timeout, or any other claude -p error retries the SAME
    batch once, then logs and returns ([], cost, {}, True) -- the whole batch is skipped,
    never partially recovered (no split ladder; see module docstring). `batch_failed`
    (distinct from a legitimate zero-drop clean batch) is what lets the caller tell "the
    model produced nothing worth keeping" apart from "claude -p never answered" -- the
    2026-07-08/claude_p_oauth_expiry_hygiene failure modes this job must not silently
    absorb (see module docstring)."""
    text_by_key = {(nid, ax): txt for nid, ax, txt in items}
    note_ids = sorted({nid for nid, _ax, _t in items})
    prompt = build_prompt(items)
    cost_total = 0.0
    arr = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        text = None
        try:
            text, cost = _run_claude(prompt, timeout=timeout)
            cost_total += cost
        except SessionLimitError:
            raise
        except claude_p.ClaudeWrapperRegression:
            # The harness-stripping flags stopped working -- a real claude -p call would
            # cost ~10x. Never retry/absorb this into a routine "batch skipped": propagate
            # so the run aborts loudly, same as a 429.
            raise
        except subprocess.TimeoutExpired:
            if logger:
                logger(f"STRUCTURE_READS timeout (attempt {attempt}/{MAX_ATTEMPTS}) notes={note_ids}")
        except RuntimeError as e:
            if logger:
                logger(f"STRUCTURE_READS claude -p error (attempt {attempt}/{MAX_ATTEMPTS}) "
                       f"notes={note_ids}: {type(e).__name__}: {e}")
        if text is not None:
            arr = _extract_json_array(text)
            if arr is not None:
                break
            if logger:
                logger(f"STRUCTURE_READS malformed JSON (attempt {attempt}/{MAX_ATTEMPTS}) "
                       f"notes={note_ids}: {text[:200]!r}")
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_BACKOFF_S)

    if arr is None:
        if logger:
            logger(f"STRUCTURE_READS batch skipped after {MAX_ATTEMPTS} failed attempts notes={note_ids}")
        return [], cost_total, {}, True

    rows: list[dict] = []
    drop_reasons: dict[str, int] = {}
    for obj in arr:
        row, reason = _validate_row(obj, text_by_key)
        if row is None:
            drop_reasons[reason] = drop_reasons.get(reason, 0) + 1
            if logger:
                logger(f"STRUCTURE_READS dropped row ({reason}): {obj!r}")
            continue
        rows.append(row)
    return rows, cost_total, drop_reasons, False


# ───────────────────────────── row building + append ─────────────────────────────

def build_row(note_id: str, obj: dict, ts: str) -> dict:
    """Full reads.jsonl row from a validated model object + the note it belongs to.

    id = sha1(note_id|axis|prompt_version) -- unlike score_reads (id has no
    prompt_version), a prompt/model change here intentionally produces NEW ids rather
    than colliding with rows from an earlier prompt version."""
    ticker, quarter, date_iso = parse_note_id(note_id)
    axis = obj["axis"]
    rid = hashlib.sha1(f"{note_id}|{axis}|{PROMPT_VERSION}".encode()).hexdigest()
    return {
        "id": rid, "ticker": ticker, "quarter": quarter, "date": date_iso, "note_id": note_id,
        "axis": axis, "score": obj["score"], "direction": obj["direction"],
        "magnitude": obj["magnitude"], "reason": obj["reason"], "quote": obj["quote"],
        "model": MODEL, "prompt_version": PROMPT_VERSION, "ts": ts,
    }


def _load_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ids.add(json.loads(line)["id"])
        except (json.JSONDecodeError, KeyError):
            continue
    return ids


def append_rows(path: Path, rows: list[dict], existing_ids: set[str] | None = None) -> dict:
    """Idempotent append: a row whose id is already on disk (or already seen this run, via
    `existing_ids`) is skipped. Returns {written, dupes}. `existing_ids` is mutated in
    place so callers can thread it across multiple append_rows calls in one run."""
    if existing_ids is None:
        existing_ids = _load_existing_ids(path)
    written = dupes = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            if r["id"] in existing_ids:
                dupes += 1
                continue
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            existing_ids.add(r["id"])
            written += 1
    return {"written": written, "dupes": dupes}


# ───────────────────────────── batching + orchestration ─────────────────────────────

def _note_items(path: Path) -> tuple[str, list[tuple[str, str, str]]]:
    note_id = path.relative_to(NOTES).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    axes = axis_texts(text)
    return note_id, [(note_id, axis, t) for axis, t in axes.items()]


def _batches(paths: list[Path], batch_size: int = BATCH_SIZE):
    """Group `paths` into chunks of `batch_size` NOTES (not items); yields
    (note_ids, items) per chunk. Notes with zero axis text are skipped entirely."""
    notes_with_items = []
    for p in paths:
        note_id, items = _note_items(p)
        if items:
            notes_with_items.append((note_id, items))
    for i in range(0, len(notes_with_items), batch_size):
        chunk = notes_with_items[i:i + batch_size]
        yield [nid for nid, _its in chunk], [it for _nid, its in chunk for it in its]


def _resolve(paths) -> list[Path]:
    out = []
    for p in paths:
        p = Path(p)
        out.append(p if p.is_absolute() else REPO / p)
    return out


def process_notes(paths, *, out_path: Path | str | None = None, batch_size: int = BATCH_SIZE,
                  rebuild: bool = False, dry_run: bool = False, logger=print) -> dict:
    """Structure §5/§6/§7 reads for `paths` (note file paths, absolute or repo-relative --
    both "notes/T/f.md" and "T/f.md" resolve correctly) into reads.jsonl rows.

    `dry_run=True` reads notes and builds batches but makes NO claude -p calls and writes
    nothing -- the returned dict's "detail" lists exactly what would be sent.

    `rebuild=True` accumulates every valid row across the whole run and truncates+rewrites
    `out_path` at the end (score_reads.py's --rebuild semantics); otherwise each batch is
    appended (idempotent) as soon as it completes, so a mid-run SessionLimitError still
    leaves prior batches' rows on disk.

    Raises SessionLimitError (a RuntimeError) on a 429 -- the caller decides whether to
    fail loud (--backfill) or swallow (the cron hook's try/except). Never retries/splits
    around a SessionLimitError itself (see _call_batch)."""
    out_path = Path(out_path) if out_path is not None else READS_PATH
    resolved = _resolve(paths)
    batches = list(_batches(resolved, batch_size))
    total_notes = sum(len(nids) for nids, _items in batches)
    total_items = sum(len(items) for _nids, items in batches)

    if dry_run:
        detail = [{"note_ids": nids, "axes": [(nid, ax) for nid, ax, _t in items]}
                  for nids, items in batches]
        return {"batches": len(batches), "notes": total_notes, "items": total_items,
                "detail": detail}

    ts = datetime.now(timezone.utc).isoformat()
    existing_ids = _load_existing_ids(out_path) if not rebuild else set()
    written = dupes = batch_failures = 0
    cost_total = 0.0
    drop_reasons: dict[str, int] = {}
    rebuild_rows: list[dict] = []
    for nids, items in batches:
        rows, cost, reasons, batch_failed = _call_batch(items, logger=logger)
        cost_total += cost
        if batch_failed:
            batch_failures += 1
        for reason, n in reasons.items():
            drop_reasons[reason] = drop_reasons.get(reason, 0) + n
        built = [build_row(r["note_id"], r, ts) for r in rows]
        if rebuild:
            for r in built:
                if r["id"] not in existing_ids:
                    rebuild_rows.append(r)
                    existing_ids.add(r["id"])
                    written += 1
                else:
                    dupes += 1
        else:
            res = append_rows(out_path, built, existing_ids)
            written += res["written"]
            dupes += res["dupes"]

    if rebuild:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for r in rebuild_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dropped = sum(drop_reasons.values())
    # Items sent that never surfaced as ANY row -- a fully skipped batch, or the model just
    # not echoing an object for that item within an otherwise-successful batch. Both are
    # invisible to `written`/`dupes`/`dropped` alone; this is the guard against a 100%-failed
    # run reporting a clean "written: 0" (see claude_p_oauth_expiry_hygiene memory: rc=1 from
    # a lapsed subscription OAuth is a RuntimeError this job retries-then-skips, not raises).
    omitted = total_items - written - dupes - dropped
    return {"batches": len(batches), "notes": total_notes, "items": total_items,
            "written": written, "dupes": dupes, "dropped": dropped, "omitted": omitted,
            "drop_reasons": drop_reasons, "batch_failures": batch_failures, "cost": cost_total}


# ───────────────────────────── CLI ─────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true",
                    help="walk the vault (or --ticker's dir) and structure every note's §5/§6/§7 reads")
    ap.add_argument("--rebuild", action="store_true",
                    help="regenerate the output from scratch (truncate, then write every row this run "
                         "produces fresh). Requires an explicit --out, or --yes to confirm the default "
                         "canonical path. Cannot be combined with --ticker.")
    ap.add_argument("--dry-run", action="store_true", help="print batch/note/axis counts only; no claude -p calls")
    ap.add_argument("--ticker", help="limit to one ticker's notes/<T>/ directory")
    ap.add_argument("--since", help="YYYY-MM-DD; only notes dated on/after this (incremental mode)")
    ap.add_argument("--out", default=None, help="output jsonl path (default: state/thesis/reads.jsonl)")
    ap.add_argument("--yes", action="store_true", help="confirm --rebuild against the default canonical --out path")
    a = ap.parse_args(argv)
    if not a.backfill:
        ap.error("only --backfill is supported")
    if a.rebuild:
        if a.out is None and not a.yes:
            ap.error("--rebuild requires an explicit --out, or --yes to confirm rebuilding the default canonical path")
        if a.ticker:
            ap.error("--rebuild regenerates the whole file; it cannot be combined with --ticker")
    out_path = Path(a.out) if a.out is not None else READS_PATH

    paths = iter_note_paths(a.ticker)
    if a.since:
        paths = [p for p in paths
                if parse_note_id(p.relative_to(NOTES).as_posix())[2] >= a.since]

    if a.dry_run:
        summary = process_notes(paths, out_path=out_path, dry_run=True)
        print(f"batches: {summary['batches']}")
        print(f"notes: {summary['notes']}")
        print(f"items (note,axis pairs): {summary['items']}")
        for d in summary["detail"]:
            axes = ", ".join(f"{nid}:{ax}" for nid, ax in d["axes"])
            print(f"  batch notes={d['note_ids']} -> {axes}")
        print("(dry run: no claude -p calls made, nothing written)")
        return 0

    try:
        summary = process_notes(paths, out_path=out_path, rebuild=a.rebuild, logger=print)
    except (SessionLimitError, claude_p.ClaudeWrapperRegression) as e:
        print(f"ABORT: {e}")
        return 1
    print(f"batches: {summary['batches']}  notes: {summary['notes']}  items: {summary['items']}")
    print(f"written: {summary['written']}  dupes: {summary['dupes']}  dropped: {summary['dropped']}  "
         f"omitted: {summary['omitted']}")
    if summary["drop_reasons"]:
        print(f"drop reasons: {dict(sorted(summary['drop_reasons'].items()))}")
    if summary["batch_failures"]:
        print(f"BATCH FAILURES: {summary['batch_failures']}/{summary['batches']} batches never "
             f"produced usable JSON after {MAX_ATTEMPTS} attempts -- see the STRUCTURE_READS log "
             f"lines above for cause")
    print(f"cost: ${summary['cost']:.4f}")
    verb = "rebuilt" if a.rebuild else "written"
    print(f"{verb}: {summary['written']} rows -> {out_path}")
    return 1 if summary["batch_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
