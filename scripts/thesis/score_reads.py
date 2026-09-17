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
_VALUE = r"([1-5][+-]?)"
_CLOSE = r"[\"'`]?\**"
_LOOKAHEAD = r"(?![%\d])"
_DASH = r"(?:[:—–-])?[ ]*"   # colon / em-dash / en-dash / hyphen separator, or none

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
    # "revise upward/up/down/downward ... to N" -- the target value follows the LAST "to"
    # on the line, so any earlier quoted prior score ("from ... "4-" to "4"") is skipped.
    ("revise", re.compile(r"\brevise\b[ ]+(?:up|upward|down|downward)\b[^\n]{0,300}?\bto\b" + _CONNECT + _VALUE + _CLOSE + _LOOKAHEAD, re.I)),
]


def _match_rec(text: str) -> tuple[str, str] | None:
    """(verb, value) for the first recommendation line in `text`: the canonical six-verb
    regex first, then the wider idiom map. Returns None if neither matches."""
    if m := VERB_RE.search(text):
        return m.group(1).lower(), m.group(2)
    for verb, pat in _IDIOMS:
        if m := pat.search(text):
            return verb, m.group(1)
    return None


# Same "## 5|6|7." section split match_evidence.lift_score_recs has always used.
_SECTION_RE = re.compile(r"## (5|6|7)\..*?(?=\n## |\Z)", re.S)
_SUBBLOCK_LABELS = (
    ("Innovation rate", "competitive_advantage.innovation_rate"),
    ("Distribution", "competitive_advantage.distribution"),
    ("Overall", "competitive_advantage.overall"),
)


def _sections(note_text: str) -> dict[str, str]:
    """Split a note body into its ## 5./6./7. sections, keyed by leading digit."""
    return {m.group(1): m.group(0) for m in _SECTION_RE.finditer(note_text)}


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


def append_rows(path: Path, rows: list[dict]) -> dict:
    """Idempotent append: rows whose id is already in the file are skipped. Returns {written, dupes}."""
    existing: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                existing.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                continue
    written = dupes = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            if r["id"] in existing:
                dupes += 1
                continue
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            existing.add(r["id"])
            written += 1
    return {"written": written, "dupes": dupes}


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
    ap.add_argument("--backfill", action="store_true", help="walk the vault and append every parsed recommendation")
    ap.add_argument("--dry-run", action="store_true", help="parse and print counts only; do not write")
    ap.add_argument("--ticker", help="limit to one ticker's notes/<T>/ directory")
    ap.add_argument("--out", default=str(SCORE_READS), help="output jsonl path (default: state/thesis/score_reads.jsonl)")
    a = ap.parse_args(argv)
    if not a.backfill:
        ap.error("only --backfill is supported")
    out_path = Path(a.out)
    watchlist = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    ts = datetime.now(timezone.utc).isoformat()
    verb_counts: Counter = Counter()
    axis_counts: Counter = Counter()
    per_ticker_rows: Counter = Counter()
    notes_with_recs = total_rows = total_written = total_dupes = 0
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
        if not a.dry_run:
            res = append_rows(out_path, rows)
            total_written += res["written"]
            total_dupes += res["dupes"]
    print(f"notes with recommendations: {notes_with_recs}")
    print(f"rows parsed: {total_rows}")
    print("by verb:", dict(sorted(verb_counts.items())))
    print("by axis:", dict(sorted(axis_counts.items())))
    if a.ticker:
        print(f"{a.ticker}: {per_ticker_rows[a.ticker]} rows")
    if a.dry_run:
        print("(dry run: nothing written)")
    else:
        print(f"written: {total_written}, dupes: {total_dupes} -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
