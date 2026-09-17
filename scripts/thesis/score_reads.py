"""Parse and record score-recommendation lines from earnings/conference notes.

The earnings-reviewer's §5 (AI positioning), §6 (competitive advantage, with
sub-blocks for innovation_rate / distribution / overall) and §7 (investor
interest) sections each end with a recommendation sentence using one of six
verb forms: `hold at N`, `drift to N`, `revise to N`, `propose N`,
`propose initial score N`, `Populate as N` (N = [1-5] with an optional
trailing +/-, sometimes bolded).

`parse_recs` is the single source of truth for turning note text into
{axis, verb, value} tuples, reusing the exact section/sub-block split that
`match_evidence.lift_score_recs` has always used. `hold`/`populate` are
reaffirmations (no proposal); `drift`/`revise`/`propose` are proposals when
they differ from the currently-applied score -- that distinction is drawn by
the caller (`match_evidence.lift_score_recs`), not here: this module records
every read, regardless of verb.

CLI (backfill the historical vault into state/thesis/score_reads.jsonl):
    python3 scripts/thesis/score_reads.py --backfill --dry-run
    python3 scripts/thesis/score_reads.py --backfill --ticker AMAT
    python3 scripts/thesis/score_reads.py --backfill --out /path/to/score_reads.jsonl
"""
from __future__ import annotations
import argparse, glob, hashlib, json, re, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
NOTES = REPO / "notes"
sys.path.insert(0, str(REPO / "scripts"))
from thesis import STATE_DIR, thesis_io as tio   # noqa: E402

SCORE_READS = STATE_DIR / "score_reads.jsonl"
NOTE_GLOBS = ("*-[1-4]Q[0-9][0-9].md", "*-conf-*.md")

# Six verb forms, case-insensitive, tolerant of "**", ":" and "a"/"an" between the verb
# and the value. Whitespace between tokens is restricted to literal spaces (not \s) so a
# match can never stretch across a newline into an unrelated number further down the block.
# The connector also tolerates a quoted ("N") or backtick-quoted (`N`) value on either
# side, and "initial" alone (score word optional) so "propose initial 4" -- with no
# "score" -- still resolves to the existing PROPOSE verb, not a new idiom.
_CONNECT = r"[ :]*\**[ ]*(?:an?[ ]+)?\**[ ]*[\"'`]?\**[ ]*"
# Trailing sign also accepts the Unicode minus (U+2212), which some note prose uses in
# place of ASCII "-"; _norm_value() below folds it back to ASCII so every stored value
# uses one consistent character.
_VALUE = r"([1-5][+\-−]?)"
_CLOSE = r"[\"'`]?\**"
_LOOKAHEAD = r"(?![%\d])"
_DASH = r"(?:[:—–-])?[ ]*"   # colon / em-dash / en-dash / hyphen separator, or none


def _norm_value(v: str) -> str:
    return v.replace("−", "-")

VERB_RE = re.compile(
    r"\b(hold|drift|revise|propose|populate)\b"
    r"(?:[ ]+(?:at|to|as|initial(?:[ ]+score)?))?"
    + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD,
    re.I,
)

# Idiom -> verb map for phrasing the six canonical forms don't cover (RIS5 A1 fix round 1).
# Reviewer-sourced corpus idioms, all first-baseline ("populate": reaffirm, no proposal)
# unless noted. Order doesn't matter for correctness -- every phrase's next literal token
# after "initial" differs (score/proposed/proposal/at), so there's no cross-matching risk.
_IDIOMS: list[tuple[str, re.Pattern]] = [
    ("populate", re.compile(r"\binitiali[sz]e\b[ ]+(?:at|to)\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\binitiate\b[ ]+at\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\bestablish\b(?:[ ]+initial)?[ ]+at\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\bproposed\b[ ]+initial[ ]+score\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\binitial\b[ ]+proposed[ ]+score\b(?:[ ]+of)?" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\binitial\b[ ]+score\b(?:[ ]+of)?" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\bfirst-baseline\b[ ]+proposal\b[ ]*" + _DASH + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("populate", re.compile(r"\binitial\b[ ]+proposal\b[ ]*" + _DASH + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    ("hold", re.compile(r"\breaffirm\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    # "hold [at] the (prior|previous|<N>Q<YY>) (recommendation|score) of N" (RIS5 A1 fix
    # round 3) -- too much text between "hold" and the value for VERB_RE's connector.
    ("hold", re.compile(r"\bhold\b(?:[ ]+at)?[ ]+the[ ]+(?:prior|previous|[1-4]Q\d{2})"
                         r"[ ]+(?:recommendation|score)[ ]+of\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
    # "revise upward/up/down/downward ... to N" -- the target value follows the LAST "to"
    # on the line, so any earlier quoted prior score ("from ... "4-" to "4"") is skipped.
    ("revise", re.compile(r"\brevise\b[ ]+(?:up|upward|down|downward)\b[^\n]{0,300}?\bto\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
]


# A line -- after stripping a leading "-" bullet and any "**" bold -- that starts with the
# word "Recommendation" (any bold/colon variant). Anchors matching to that single line so
# an unrelated quoted mention elsewhere in the block/section (a "Current score" recap, a
# hedge in "Reasoning:") can never win (RIS5 A1 fix round 2).
_REC_LINE_RE = re.compile(r"^[ \t]*-?[ \t]*\**[ \t]*Recommendation\b", re.I)


def _recommendation_line(text: str) -> str | None:
    """The first line in `text` that starts with "Recommendation", or None if there isn't one."""
    for line in text.splitlines():
        if _REC_LINE_RE.match(line):
            return line
    return None


def _search(scope: str) -> tuple[str, str] | None:
    """VERB_RE first, then the idiom list in list order (fix-round-1 behavior)."""
    if m := VERB_RE.search(scope):
        return m.group(1).lower(), _norm_value(m.group(2))
    for verb, pat in _IDIOMS:
        if m := pat.search(scope):
            return verb, _norm_value(m.group(1))
    return None


def _search_positional(scope: str) -> tuple[str, str] | None:
    """Every pattern (VERB_RE + every idiom) searched independently within `scope`; the
    leftmost-starting match wins, regardless of which pattern found it -- used only on a
    single recommendation line, where at most one real verb+value should ever appear."""
    candidates: list[tuple[int, str, str]] = []
    if m := VERB_RE.search(scope):
        candidates.append((m.start(), m.group(1).lower(), _norm_value(m.group(2))))
    for verb, pat in _IDIOMS:
        if m := pat.search(scope):
            candidates.append((m.start(), verb, _norm_value(m.group(1))))
    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0])
    return candidates[0][1], candidates[0][2]


def _match_rec(text: str) -> tuple[str, str] | None:
    """(verb, value) for a section/sub-block.

    Anchors to the line that starts with "Recommendation" when one exists, matching only
    within that line (positionally, across VERB_RE + every idiom) -- this is what keeps an
    unrelated quoted mention elsewhere in the block/section from winning. Falls back to the
    fix-round-1 whole-block search (VERB_RE first, then the idiom list in order) only when
    no such line exists at all.
    """
    line = _recommendation_line(text)
    if line is not None:
        return _search_positional(line)
    return _search(text)


_SUBBLOCK_LABELS = (
    ("Innovation rate", "competitive_advantage.innovation_rate"),
    ("Distribution", "competitive_advantage.distribution"),
    ("Overall", "competitive_advantage.overall"),
)

# Every "## N. Title" heading in a note, any N (not just 5/6/7) -- title-first
# identification (RIS5 A2 fix round 1) has to be able to find e.g. "AI positioning
# signal" wherever it actually sits, not assume it is always at position 5.
_HEADING_RE = re.compile(r"^## (\d+)\.[ \t]*(.*)$", re.M)

# heading-key -> title regex. Matched against the heading TITLE only (never the section
# body), case-insensitive. Order doesn't matter across axes (a real note only carries one
# heading per topic), but within one axis the FIRST matching heading in document order
# wins (see _sections()).
_TITLE_PATTERNS = (
    ("5", re.compile(r"ai.?positioning", re.I)),
    ("6", re.compile(r"competitive|moat|competition", re.I)),
    ("7", re.compile(r"investor.?interest", re.I)),
)


def _all_headings(note_text: str) -> list[tuple[str, str, int]]:
    """[(number, title, start_offset)] for every "## N. Title" heading, in document order."""
    return [(m.group(1), m.group(2).strip(), m.start()) for m in _HEADING_RE.finditer(note_text)]


def _section_text_from(note_text: str, start: int) -> str:
    """Section text from a heading's start offset up to (not including) the next
    "\\n## " heading, or end of document -- same boundary the old numeric-only
    _SECTION_RE used."""
    m = re.search(r"\n## ", note_text[start:])
    end = start + m.start() if m else len(note_text)
    return note_text[start:end]


def _sections(note_text: str) -> dict[str, str]:
    """The ai_positioning / competitive-advantage / investor-interest sections, keyed
    "5"/"6"/"7" (unchanged key shape -- every existing caller, parse_recs and
    structure_reads.axis_texts, reads sec["5"]/sec["6"]/sec["7"]).

    Sections are identified by HEADING TITLE first (RIS5 A2 fix round 1): a heading
    matching /ai.?positioning/i, /competitive|moat|competition/i, or
    /investor.?interest/i is used regardless of its number -- a conference note whose
    real "## 5." heading is "Market reaction" is no longer misread as the AI-positioning
    section just because it happens to sit at position 5.

    Numeric position ("## 5."/"## 6."/"## 7.") is used ONLY as a fallback for a heading
    that carries NO title text at all (a bare "## 5." with nothing after the number) --
    never for a heading with a real, non-matching title. A heading like "Market reaction"
    or "Cross-ticker implications" has a real title that matches nothing, so it maps to
    NOTHING (no row), not to an axis by number.
    """
    headings = _all_headings(note_text)
    out: dict[str, str] = {}
    for key, pat in _TITLE_PATTERNS:
        for num, title, start in headings:
            if pat.search(title):
                out[key] = _section_text_from(note_text, start)
                break
    for key in ("5", "6", "7"):
        if key in out:
            continue
        for num, title, start in headings:
            if num == key and not title:
                out[key] = _section_text_from(note_text, start)
                break
    return out


def parse_recs(note_text: str) -> list[dict]:
    """Every explicit score-recommendation line in the note, by axis.

    Returns [{axis, verb, value}], verb lowercased to one of
    hold|drift|revise|propose|populate, axis one of thesis_io.SCORE_KEYS.
    """
    sec = _sections(note_text)
    out: list[dict] = []
    if "5" in sec and (r := _match_rec(sec["5"])):
        out.append({"axis": "ai_positioning", "verb": r[0], "value": r[1]})
    if "6" in sec:
        for label, key in _SUBBLOCK_LABELS:
            blk = re.search(rf"\*\*{label}\*\*.*?(?=\n- \*\*|\Z)", sec["6"], re.S)
            if blk and (r := _match_rec(blk.group(0))):
                out.append({"axis": key, "verb": r[0], "value": r[1]})
    if "7" in sec and (r := _match_rec(sec["7"])):
        out.append({"axis": "potential_investor_interest.score", "verb": r[0], "value": r[1]})
    return out


_QTR_RE = re.compile(r"-([1-4]Q\d{2})(?=\.md$)")


def parse_note_id(note_id: str) -> tuple[str, str | None, str]:
    """('COHR/20260904-2Q27.md') -> ('COHR', '2Q27', '2026-09-04'); conf notes have no quarter."""
    ticker, filename = note_id.split("/", 1)
    date_iso = f"{filename[:4]}-{filename[4:6]}-{filename[6:8]}"
    m = _QTR_RE.search(filename)
    return ticker, (m.group(1) if m else None), date_iso


def build_rows(note_id: str, note_text: str, applied: dict[str, str] | None, ts: str) -> list[dict]:
    """Full score_reads rows for one note: {ticker, quarter, date, note_id, axis, verb, value, applied, ts, id}.

    id = sha1(note_id|axis) -- one row per (note, axis) pair, so a re-run over the same note
    never duplicates. `applied` is the watchlist score for that axis at write time, or None.
    """
    ticker, quarter, date_iso = parse_note_id(note_id)
    applied = applied or {}
    rows = []
    for r in parse_recs(note_text):
        axis = r["axis"]
        rid = hashlib.sha1(f"{note_id}|{axis}".encode()).hexdigest()
        rows.append({
            "id": rid, "ticker": ticker, "quarter": quarter, "date": date_iso, "note_id": note_id,
            "axis": axis, "verb": r["verb"], "value": r["value"], "applied": applied.get(axis), "ts": ts,
        })
    return rows


def append_rows(path: Path, rows: list[dict], replace: bool = False) -> dict:
    """Write `rows` into `path`, keyed by id.

    Default (replace=False -- the live-ingest path, match_evidence.lift_score_recs): a row
    whose id is already on disk is skipped. Returns {written, dupes}.

    replace=True (the --backfill CLI, RIS5 A1 fix round 2): a row whose id is already on
    disk is REPLACED when its (verb, value, applied) differ from what's stored -- an
    earlier matcher bug can leave a wrong row under a since-fixed id, and a dupe-skip would
    keep it wrong forever. The stored row's `ts` is kept unchanged unless the row is
    actually replaced, in which case the new `ts` (from the caller's build_rows call) wins.
    The whole file is rewritten, in its original id order (new ids appended). Returns
    {written, replaced, unchanged, changes}, where `changes` is
    [{"id", "old": {verb,value,applied}, "new": {verb,value,applied}}] for every replaced row.
    """
    existing: dict[str, dict] = {}
    order: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                existing[row["id"]] = row
                order.append(row["id"])
            except (json.JSONDecodeError, KeyError):
                continue

    if not replace:
        written = dupes = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            for r in rows:
                if r["id"] in existing:
                    dupes += 1
                    continue
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                existing[r["id"]] = r
                written += 1
        return {"written": written, "dupes": dupes}

    _CMP_KEYS = ("verb", "value", "applied")
    written = replaced = unchanged = 0
    changes: list[dict] = []
    for r in rows:
        old = existing.get(r["id"])
        if old is None:
            existing[r["id"]] = r
            order.append(r["id"])
            written += 1
        elif tuple(old.get(k) for k in _CMP_KEYS) != tuple(r.get(k) for k in _CMP_KEYS):
            changes.append({"id": r["id"], "old": {k: old.get(k) for k in _CMP_KEYS},
                             "new": {k: r.get(k) for k in _CMP_KEYS}})
            existing[r["id"]] = r
            replaced += 1
        else:
            unchanged += 1   # keep the stored row -- including its original ts -- untouched
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rid in order:
            f.write(json.dumps(existing[rid], ensure_ascii=False) + "\n")
    return {"written": written, "replaced": replaced, "unchanged": unchanged, "changes": changes}


def iter_note_paths(ticker: str | None = None) -> list[Path]:
    """notes/<T>/*-<N>Q<YY>.md and notes/<T>/*-conf-*.md, across all ticker dirs or one."""
    tickers = [ticker] if ticker else sorted(p.name for p in NOTES.iterdir() if p.is_dir())
    paths: list[str] = []
    for t in tickers:
        for pat in NOTE_GLOBS:
            paths += glob.glob(str(NOTES / t / pat))
    return sorted(Path(p) for p in paths)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true", help="walk the vault and append/replace every parsed recommendation")
    ap.add_argument("--rebuild", action="store_true",
                     help="regenerate the output from scratch: truncate, then write every parsed row fresh "
                          "(rows the current parser no longer produces are dropped, not carried over stale). "
                          "Requires an explicit --out, or --yes to confirm against the default canonical path. "
                          "Cannot be combined with --ticker (it would truncate the whole file for a partial run).")
    ap.add_argument("--dry-run", action="store_true", help="parse and print counts only; do not write")
    ap.add_argument("--ticker", help="limit to one ticker's notes/<T>/ directory")
    ap.add_argument("--out", default=None, help="output jsonl path (default: state/thesis/score_reads.jsonl)")
    ap.add_argument("--yes", action="store_true", help="confirm --rebuild against the default canonical --out path")
    a = ap.parse_args(argv)
    if not a.backfill:
        ap.error("only --backfill is supported")
    if a.rebuild:
        if a.out is None and not a.yes:
            ap.error("--rebuild requires an explicit --out, or --yes to confirm rebuilding the default canonical path")
        if a.ticker:
            ap.error("--rebuild regenerates the whole file; it cannot be combined with --ticker")
    out_path = Path(a.out) if a.out is not None else SCORE_READS
    watchlist = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    ts = datetime.now(timezone.utc).isoformat()
    verb_counts: Counter = Counter()
    axis_counts: Counter = Counter()
    per_ticker_rows: Counter = Counter()
    notes_with_recs = total_rows = total_written = total_replaced = total_unchanged = 0
    all_changes: list[dict] = []   # [(note_id, axis, old, new)] for the report
    rebuild_rows: list[dict] = []  # only accumulated when --rebuild
    applied_cache: dict[str, dict] = {}
    for p in iter_note_paths(a.ticker):
        note_id = p.relative_to(NOTES).as_posix()
        ticker = note_id.split("/", 1)[0]
        text = p.read_text(encoding="utf-8", errors="replace")
        recs = parse_recs(text)
        if not recs:
            continue
        if ticker not in applied_cache:
            applied_cache[ticker] = tio.watchlist_scores(ticker, watchlist)
        rows = build_rows(note_id, text, applied_cache[ticker], ts)
        notes_with_recs += 1
        total_rows += len(rows)
        per_ticker_rows[ticker] += len(rows)
        for r in rows:
            verb_counts[r["verb"]] += 1
            axis_counts[r["axis"]] += 1
        if a.dry_run:
            continue
        if a.rebuild:
            rebuild_rows.extend(rows)
        else:
            # --backfill (no --rebuild) uses replace mode: an earlier matcher bug can leave
            # a wrong row under a since-fixed id, and a dupe-skip would keep it wrong forever.
            res = append_rows(out_path, rows, replace=True)
            total_written += res["written"]
            total_replaced += res["replaced"]
            total_unchanged += res["unchanged"]
            by_id = {r["id"]: r for r in rows}
            for c in res["changes"]:
                row = by_id[c["id"]]
                all_changes.append((row["note_id"], row["axis"], c["old"], c["new"]))
    if a.rebuild and not a.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for r in rebuild_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"notes with recommendations: {notes_with_recs}")
    print(f"rows parsed: {total_rows}")
    print("by verb:", dict(sorted(verb_counts.items())))
    print("by axis:", dict(sorted(axis_counts.items())))
    if a.ticker:
        print(f"{a.ticker}: {per_ticker_rows[a.ticker]} rows")
    if a.dry_run:
        print("(dry run: nothing written)")
    elif a.rebuild:
        print(f"rebuilt: {len(rebuild_rows)} rows -> {out_path}")
    else:
        print(f"written: {total_written}, replaced: {total_replaced}, unchanged: {total_unchanged} -> {out_path}")
        for note_id, axis, old, new in all_changes:
            print(f"  REPLACED {note_id} {axis}: {old['verb']}/{old['value']} -> {new['verb']}/{new['value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
