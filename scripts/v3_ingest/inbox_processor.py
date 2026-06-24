#!/usr/bin/env python3
"""
Path A Phase 0 — Obsidian inbox channel.

Operator drops a markdown file in notes/inbox/ on the Mac (Obsidian), declaring a
`process:` type in frontmatter. The Mac launchd job auto-pushes; this watcher
(15-min droplet cron) detects the new file, synthesizes a desk-format summary via
`claude -p` (subscription auth), and writes a sibling `{stem}.summary.md`.
Auto-sync returns it to GitHub; the Mac auto-pulls it back into Obsidian. Zero
operator action beyond saving the file.

Frontmatter contract (on the inbox file):
    ---
    process: transcript | link | note
    source: <descriptor or URL>
    tickers: [OPTIONAL — LLM-extracted if absent]
    themes:  [OPTIONAL — LLM-extracted if absent]
    ---
    <body: pasted transcript, a URL, or plain notes>

Per file: link-fetch (process=link) -> extract tickers/themes if missing ->
chunk_note() the enriched note (v3 multi-ticker pipeline; validation + STOP guard)
-> retrieve 5-10 related EXISTING corpus chunks (scoped by extracted tickers) ->
attach Store B guidance track records -> synthesize -> write summary.

Phase-0 scope: the inbox note is chunked in-memory only (NOT persisted to pg) —
persisting would key chunk_id/base_ticker on the literal "inbox" path segment (the
known invalid-base_ticker hygiene trap). Cross-references retrieve against the
existing corpus. Persisting inbox content into Store A is a Phase-1 decision.

Idempotency: a file is skipped if its sibling {stem}.summary.md already exists.
Failures are isolated per-file (logged, the others proceed) and retried next run
(no summary written -> still a candidate). State (audit watermark) lives in
state/v3_ingest/ (gitignored).

Env: self-loads CHUNK_STORE_BACKEND from /root/podcasts/.env (embed.py + pgconn.py
self-load GEMINI_API_KEY / DATABASE_URL). `claude -p` is invoked with
ANTHROPIC_API_KEY stripped from the subprocess env -> forces subscription auth
(the operator's `env -u ANTHROPIC_API_KEY` cost decision).

Usage:
    python3 scripts/v3_ingest/inbox_processor.py            # process all new inbox files
    python3 scripts/v3_ingest/inbox_processor.py --dry-run  # synth to stdout, no file/watermark
    python3 scripts/v3_ingest/inbox_processor.py --file notes/inbox/foo.md   # one file
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ───────────────────────────── Configuration ─────────────────────────────

REPO_ROOT = Path("/root/research-watchlist")
INBOX_DIR = REPO_ROOT / "notes" / "inbox"
STATE_DIR = REPO_ROOT / "state" / "v3_ingest"
WATERMARK_FILE = STATE_DIR / "inbox_watermark.json"
TMP_DIR = STATE_DIR / "inbox_tmp"
ENV_FILE = Path("/root/podcasts/.env")
TICKER_IDENTITY = REPO_ROOT / "config" / "ticker_identity.yaml"
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
CHUNKING_DIR = REPO_ROOT / "scripts" / "chunking"

MODEL = "claude-sonnet-4-6"        # matches podcasts pipeline + cost-model decision
CLAUDE_TIMEOUT_S = 300
CONTENT_CAP = 12_000               # head chars of submitted content passed to synth
RELATED_K = 8                      # 5-10 cross-reference candidates
RETRIEVE_PER_TICKER = 4
MAX_TICKERS_RETRIEVE = 4
VALID_PROCESS = {"transcript", "link", "note"}
DOC_TYPE_BY_PROCESS = {"transcript": "earnings_transcript",
                       "note": "operator_note", "link": "news"}

sys.path.insert(0, str(CHUNKING_DIR))   # chunker / retrieve / store_b / embed


# ───────────────────────────── Logging ─────────────────────────────

def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] v3_inbox: {msg}", flush=True)


# ───────────────────────────── Env ─────────────────────────────

def ensure_backend() -> None:
    """Ensure CHUNK_STORE_BACKEND is set (get_store/get_metrics_store read it).
    embed.py + pgconn.py self-load GEMINI_API_KEY / DATABASE_URL on their own."""
    if os.environ.get("CHUNK_STORE_BACKEND"):
        return
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith(("CHUNK_STORE_BACKEND=", "export CHUNK_STORE_BACKEND=")):
                os.environ["CHUNK_STORE_BACKEND"] = line.split("=", 1)[1].strip().strip("\"'")
                return
    os.environ["CHUNK_STORE_BACKEND"] = "pg"   # the pinned default in /root/podcasts/.env


def _claude_env() -> dict:
    """os.environ minus ANTHROPIC_API_KEY -> claude -p uses subscription auth."""
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def run_claude(prompt: str, *, allowed_tools: str = "") -> tuple[str, float]:
    """Invoke `claude -p` (JSON envelope, subscription auth). Returns (text, cost)."""
    cmd = ["claude", "-p", prompt, "--output-format", "json",
           "--allowedTools", allowed_tools, "--model", MODEL]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=CLAUDE_TIMEOUT_S, cwd=str(REPO_ROOT), env=_claude_env())
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} stderr={result.stderr[:300]}")
    env = json.loads(result.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"claude -p is_error: {str(env.get('result'))[:200]}")
    return env.get("result", ""), float(env.get("total_cost_usd", 0.0) or 0.0)


# ───────────────────────────── Vocab loaders ─────────────────────────────

def load_valid_tickers() -> set[str]:
    data = yaml.safe_load(TICKER_IDENTITY.read_text()) or {}
    return {str(k) for k in data.keys()}


def load_valid_themes() -> set[str]:
    data = yaml.safe_load(WATCHLIST_YAML.read_text()) or {}
    block = data.get("themes", {}) or {}
    out: set[str] = set()
    for cat in block.values():
        out.update(cat or [])
    return out


# ───────────────────────────── Note parsing ─────────────────────────────

def split_note(text: str) -> tuple[dict, str]:
    """(frontmatter dict, body). {} frontmatter if absent/malformed."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return (fm if isinstance(fm, dict) else {}), m.group(2)


# ───────────────────────────── Link fetch ─────────────────────────────

URL_RE = re.compile(r"https?://\S+")


def extract_url(fm: dict, body: str) -> str | None:
    src = (fm.get("source") or "").strip()
    if URL_RE.match(src):
        return src
    for line in body.splitlines():
        m = URL_RE.search(line)
        if m:
            return m.group(0).rstrip(").,>\"'")
    return None


def fetch_url(url: str) -> str:
    """trafilatura if importable, else requests + BeautifulSoup. Raises on hard failure."""
    try:
        import trafilatura  # type: ignore
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            txt = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if txt and txt.strip():
                return txt.strip()
    except Exception:  # noqa: BLE001 — fall through to bs4
        pass
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(url, timeout=30,
                     headers={"User-Agent": "Mozilla/5.0 (research-watchlist-inbox)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    main = soup.find("article") or soup.find("main") or soup.body or soup
    parts = [el.get_text(" ", strip=True)
             for el in main.find_all(["h1", "h2", "h3", "p", "li"])]
    txt = "\n".join(p for p in parts if p)
    if not txt.strip():
        raise RuntimeError("no extractable text from URL")
    return txt.strip()


# ───────────────────────────── Tag extraction (LLM) ─────────────────────────────

EXTRACT_INSTRUCTIONS = """\
You are a precise financial-research tagging assistant. From the SOURCE MATERIAL
below, extract two things, using ONLY the provided vocabularies.

1. tickers — the WATCHLIST TICKERS substantively discussed (meaningful discussion
   of the company's business, strategy, products, financials, competitive
   position, capital allocation, or outlook). EXCLUDE mere name-drops or generic
   sector mentions. Use the EXACT watchlist symbol.
2. themes — the THEME TAGS substantively present. Only tags from the list.

Output ONLY a JSON object, no prose / markdown / code fences:
{"tickers": ["..."], "themes": ["..."]}
"""


def extract_tags(content: str, valid_tickers: set[str],
                 valid_themes: set[str]) -> tuple[list[str], list[str], float]:
    prompt = (EXTRACT_INSTRUCTIONS
              + "\nWATCHLIST TICKERS (only these are valid):\n" + ", ".join(sorted(valid_tickers))
              + "\n\nTHEME TAGS (only these are valid):\n" + ", ".join(sorted(valid_themes))
              + "\n\nSOURCE MATERIAL:\n" + content[:CONTENT_CAP] + "\n")
    text, cost = run_claude(prompt)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object in extraction response: {text[:160]!r}")
    obj = json.loads(m.group(0))
    tickers = [t for t in (obj.get("tickers") or []) if t in valid_tickers]
    themes = [t for t in (obj.get("themes") or []) if t in valid_themes]
    return tickers, themes, cost


# ───────────────────────────── Chunk validation (v3) ─────────────────────────────

def chunk_validate(stem: str, tickers: list[str], themes: list[str],
                   doc_type: str, body: str) -> int:
    """Write an enriched note to a temp path OUTSIDE notes/ (so base_ticker resolves
    to None and `tickers` come from frontmatter, not the literal 'inbox' path) and
    run the v3 chunker on it. Returns chunk count. Raises if the chunker can't
    handle the shape (a STOP-condition signal)."""
    from chunker import chunk_note
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    fm = {"doc_type": doc_type, "tickers": tickers, "themes": themes}
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)
    tmp = TMP_DIR / f"{stem}.md"
    tmp.write_text(f"---\n{front}---\n\n{body}\n")
    try:
        chunks = chunk_note(tmp)
    finally:
        tmp.unlink(missing_ok=True)
    return len(chunks)


# ───────────────────────────── Retrieval (cross-references) ─────────────────────────────

def retrieve_related(query: str, tickers: list[str]):
    from retrieve import retrieve
    seen: set[str] = set()
    out = []
    for tk in (tickers[:MAX_TICKERS_RETRIEVE] or [None]):
        try:
            hits = retrieve(query, k=RETRIEVE_PER_TICKER, ticker=tk)
        except Exception as e:  # noqa: BLE001 — one ticker's retrieval miss must not abort
            log(f"  retrieve failed (ticker={tk}): {type(e).__name__}: {e}")
            continue
        for h in hits:
            cid = h.chunk.get("chunk_id")
            if cid in seen:
                continue
            seen.add(cid)
            out.append(h)
    return out[:RELATED_K]


def render_related(hits) -> str:
    if not hits:
        return "— none retrieved —"
    blocks = []
    for h in hits:
        c = h.chunk
        tk = ", ".join(c.get("tickers") or []) or "?"
        fq = c.get("fiscal_quarter") or ""
        sec = c.get("section") or "?"
        cs = c.get("claim_source") or "?"
        to = c.get("time_orientation") or "?"
        if c.get("answered_by"):
            spk = (f" | answered by {c['answered_by']} "
                   f"({c.get('answerer_role') or '?'}, {c.get('answer_directness') or '?'})")
        elif c.get("speaker"):
            spk = f" | speaker {c['speaker']} ({c.get('speaker_role') or '?'})"
        else:
            spk = ""
        snip = re.sub(r"\s+", " ", (c.get("text") or "")).strip()[:220]
        blocks.append(f"[{tk} {fq} | {sec} | {cs}/{to}{spk}]\n{snip}…")
    return "\n---\n".join(blocks)


# ───────────────────────────── Store B track records ─────────────────────────────

def _pct(x):
    return "—" if x is None else f"{x:.0%}"


def _num(x):
    return "—" if x is None else (f"{x:+.3f}" if isinstance(x, float) else str(x))


def render_track_records(tickers: list[str]) -> str:
    if not tickers:
        return "— no tickers extracted —"
    from store_b import get_metrics_store
    ms = get_metrics_store()
    lines = []
    for tk in tickers:
        try:
            cr = ms.credibility(tk, "SALES")
        except Exception as e:  # noqa: BLE001
            log(f"  store_b credibility failed ({tk}): {type(e).__name__}: {e}")
            cr = None
        if not cr:
            lines.append(f"{tk}: no Store B guidance coverage.")
            continue
        lines.append(
            f"{tk}: guides_quantitatively={cr.get('guides_quantitatively')}, "
            f"guide_hit_rate={_pct(cr.get('guide_hit_rate'))}, "
            f"sandbag_index={_num(cr.get('sandbag_index'))}, "
            f"n_guided_periods={cr.get('n_guided_periods')}, "
            f"range={cr.get('date_range')}")
        tr = ms.track_record(tk, "SALES", n=4)
        if tr:
            lines.append("  recent judged periods (newest first):")
            for r in tr:
                lines.append(
                    f"    {r.get('period')}: actual {r.get('actual')} vs "
                    f"guide_mid {r.get('guidance_mid')} -> {r.get('beat_vs_guidance')}")
    return "\n".join(lines)


# ───────────────────────────── Synthesizer ─────────────────────────────

SYNTH_INSTRUCTIONS = """\
You are a senior equity-research analyst on a technology-sector desk (the BCTK
coverage universe). An operator has submitted source material — an earnings or
conference transcript, a web article, or personal notes — for synthesis into the
desk's house summary format. Produce a tight, decision-useful summary grounded
STRICTLY in the material provided below: the submitted content, the related
corpus excerpts, and the management-guidance track records.

GROUNDING RULES (non-negotiable):
- Use ONLY facts present in the SUBMITTED CONTENT, RELATED CORPUS, or TRACK
  RECORD blocks. Never invent numbers, dates, quotes, or events. If you reason
  beyond the text, label it "(inference)".
- If a section has no supporting material, write "— none identified —". The
  operator values signal density over padding; be terse.
- Quote numbers exactly as they appear, with units and period labels. Do not
  recompute or round unless the source does.
- Cross-references: cite ONLY the RELATED CORPUS excerpts actually provided,
  each by its "TICKER PERIOD (section)" label exactly as given. Invent nothing.
- Surprises vs. Recent Guidance: use ONLY the TRACK RECORD block. For a ticker
  with no track record provided, say coverage is absent — never guess credibility.

Q&A WEIGHTING (transcript material only):
For process=transcript, when synthesizing the Q&A portion:
- Weight WHO ANSWERS over who asks. CEO/CFO/IR-head answers carry the most
  signal; mid-level executive deflections or "we don't comment on that" carry
  signal-as-absence.
- Surface the answerer's directness: did they confirm with specifics, hedge with
  qualifications, deflect to a future date, or refuse to answer at all?
- For "Key Data Points" extracted from Q&A, prefer facts confirmed by named
  senior management (CEO, CFO, IR head) over those from junior speakers or
  analyst inference.
- When citing Q&A in cross-references, include the answerer's name + title where
  present in the SUBMITTED CONTENT.

OUTPUT: emit GitHub-flavored markdown beginning at "# Summary", with EXACTLY
these sections, in this order, and nothing before or after:

# Summary
<2-4 sentences: what this material is and the single most important takeaway.>

## Key Data Points
<bullets — the concrete material facts/metrics/announcements from the submitted
content; one fact per bullet, with its number and period.>

## Tickers Mentioned
<one line per ticker (from the provided list): its role in this material.>

## Themes
<one line per strategic theme this material touches (from the provided list):
how it shows up.>

## Cross-References
<bullets linking to the RELATED CORPUS excerpts provided; for each:
"TICKER PERIOD (section) — how it corroborates / extends / contrasts with the
submitted material." Only excerpts provided below.>

## Surprises vs. Recent Guidance
<for each ticker WITH a track record: does the submitted material's data
confirm, beat, or undercut that management's recent guide-vs-actual pattern and
credibility? Cite the guide_hit_rate / sandbag_index / latest beat_vs_guidance
from the TRACK RECORD block. For tickers without coverage:
"TICKER — no Store B guidance coverage.">

## Actionable Implications
<2-5 bullets: what a PM should watch, re-underwrite, or act on next, given this
material plus the track records. Tie each to evidence above.>

## Source
<one line: the original filename and process type; include the URL if process=link.>
"""


def build_synth_prompt(*, process: str, source: str, filename: str, content: str,
                       truncated: bool, tickers: list[str], themes: list[str],
                       related_block: str, n_related: int, track_block: str) -> str:
    note = f"  [NOTE: submitted content truncated to first {CONTENT_CAP} chars]" if truncated else ""
    return (
        SYNTH_INSTRUCTIONS
        + "\n============================ DATA ============================\n\n"
        + f"=== SUBMITTED CONTENT (file={filename}, process={process}, source={source}){note} ===\n"
        + content[:CONTENT_CAP] + "\n\n"
        + "=== EXTRACTED TICKERS ===\n" + (", ".join(tickers) or "(none)") + "\n\n"
        + "=== EXTRACTED THEMES ===\n" + (", ".join(themes) or "(none)") + "\n\n"
        + f"=== RELATED CORPUS EXCERPTS ({n_related} retrieved; cross-reference candidates) ===\n"
        + related_block + "\n\n"
        + "=== MANAGEMENT GUIDANCE TRACK RECORDS (Store B; SALES) ===\n"
        + track_block + "\n"
    )


def build_summary_file(*, filename: str, tickers: list[str], themes: list[str],
                       body: str) -> str:
    fm = {
        "summary_of": filename,
        "processed_at": dt.datetime.now().isoformat(timespec="seconds"),
        "tickers": tickers,
        "themes": themes,
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{front}---\n\n{body.strip()}\n"


# ───────────────────────────── Per-file processing ─────────────────────────────

def process_one(path: Path, *, dry_run: bool, valid_tickers: set[str],
                valid_themes: set[str]) -> tuple[str, float]:
    """Returns (status, total_cost_usd). Raises on hard failure (caller isolates)."""
    raw = path.read_text(encoding="utf-8")
    fm, body = split_note(raw)
    process = (fm.get("process") or "note").strip().lower()
    if process not in VALID_PROCESS:
        raise ValueError(f"invalid process={process!r} (expected one of {sorted(VALID_PROCESS)})")
    source = str(fm.get("source") or "").strip()
    cost = 0.0

    content = body
    # a. link: fetch + append
    if process == "link":
        url = extract_url(fm, body)
        if not url:
            raise ValueError("process=link but no URL found in source or body")
        source = source or url
        log(f"  fetching {url}")
        fetched = fetch_url(url)
        content = (body.strip() + f"\n\n--- FETCHED CONTENT ({url}) ---\n\n" + fetched).strip()
        log(f"  fetched {len(fetched)} chars")

    # b. tickers/themes — frontmatter wins; LLM-extract whatever is missing
    fm_tickers = [t for t in (fm.get("tickers") or []) if t]
    fm_themes = [t for t in (fm.get("themes") or []) if t]
    if fm_tickers and fm_themes:
        tickers, themes = fm_tickers, fm_themes
    else:
        ex_t, ex_th, c = extract_tags(content, valid_tickers, valid_themes)
        cost += c
        tickers = fm_tickers or ex_t
        themes = fm_themes or ex_th
    log(f"  tickers={tickers} themes={themes}")

    # c. chunk the enriched note (v3 pipeline; validation + STOP guard)
    doc_type = str(fm.get("doc_type") or DOC_TYPE_BY_PROCESS.get(process, "operator_note"))
    n_chunks = chunk_validate(path.stem, tickers, themes, doc_type, content)
    log(f"  chunked: {n_chunks} chunks (in-memory; not persisted to pg)")

    # d. related corpus + e. track records
    query = (content[:600] + " " + " ".join(themes)).strip()
    related = retrieve_related(query, tickers)
    related_block = render_related(related)
    track_block = render_track_records(tickers)
    log(f"  related_chunks={len(related)}")

    # f. synthesize
    truncated = len(content) > CONTENT_CAP
    prompt = build_synth_prompt(
        process=process, source=source, filename=path.name, content=content,
        truncated=truncated, tickers=tickers, themes=themes,
        related_block=related_block, n_related=len(related), track_block=track_block)
    body_md, c = run_claude(prompt)
    cost += c
    if not body_md.strip().startswith("#"):
        raise ValueError(f"synth output does not start with a markdown heading: {body_md[:120]!r}")

    summary = build_summary_file(filename=path.name, tickers=tickers, themes=themes, body=body_md)
    out_path = path.parent / f"{path.stem}.summary.md"
    if dry_run:
        log(f"  [dry-run] would write {out_path.name} ({len(summary)} chars); cost=${cost:.4f}")
        print("\n----- DRY-RUN SUMMARY (" + path.name + ") -----\n" + summary + "----- END -----\n",
              flush=True)
    else:
        out_path.write_text(summary)
        log(f"  WROTE {out_path.name} ({len(summary)} chars); cost=${cost:.4f}")
    return "ok", cost


# ───────────────────────────── Watermark ─────────────────────────────

def load_watermark() -> dict:
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"processed": {}, "runs": 0}


def save_watermark(wm: dict, newly_done: dict) -> None:
    wm.setdefault("processed", {}).update(newly_done)
    wm["runs"] = wm.get("runs", 0) + 1
    wm["last_run_at"] = dt.datetime.now().isoformat(timespec="seconds")
    WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_FILE.write_text(json.dumps(wm, indent=2) + "\n")


# ───────────────────────────── Main ─────────────────────────────

def list_inbox() -> list[Path]:
    if not INBOX_DIR.exists():
        return []
    return sorted(p for p in INBOX_DIR.glob("*.md") if not p.name.endswith(".summary.md"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Path A Phase 0 — Obsidian inbox processor")
    ap.add_argument("--dry-run", action="store_true",
                    help="synthesize + print; write no summary, advance no watermark")
    ap.add_argument("--file", help="process a single inbox file (path)")
    args = ap.parse_args()

    ensure_backend()
    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log(f"START mode={mode} backend={os.environ.get('CHUNK_STORE_BACKEND')}")

    if args.file:
        candidates = [Path(args.file)]
    else:
        candidates = list_inbox()
    log(f"inbox_files={len(candidates)}")

    valid_tickers = load_valid_tickers()
    valid_themes = load_valid_themes()

    wm = load_watermark()
    newly_done: dict[str, str] = {}
    processed = skipped = failed = 0
    total_cost = 0.0

    for path in candidates:
        out_path = path.parent / f"{path.stem}.summary.md"
        if out_path.exists() and not args.dry_run:
            skipped += 1
            continue
        log(f"PROCESS {path.name}")
        try:
            status, cost = process_one(path, dry_run=args.dry_run,
                                       valid_tickers=valid_tickers, valid_themes=valid_themes)
            total_cost += cost
            processed += 1
            if not args.dry_run:
                newly_done[path.name] = dt.datetime.now().isoformat(timespec="seconds")
        except Exception as e:  # noqa: BLE001 — per-file isolation; retried next run
            failed += 1
            log(f"  FAILED {path.name}: {type(e).__name__}: {e}")

    if not args.dry_run and newly_done:
        save_watermark(wm, newly_done)

    log(f"DONE mode={mode} processed={processed} skipped_existing={skipped} "
        f"failed={failed} cost=${total_cost:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
