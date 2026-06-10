#!/usr/bin/env python3
"""
v3 podcast ingest — extract watchlist ticker / theme tags from new podcast episode
summaries and write canonical notes to notes/podcasts/.

Reads new rows from /root/podcasts/data/podcasts.db (summaries JOIN episodes),
LLM-extracts substantively-discussed watchlist tickers + strategic theme tags via
`claude -p` (subscription auth — the repo has no ANTHROPIC_API_KEY), and writes one
note per episode with metadata-array tags. Single-note-multi-ticker per the
v3-ingest-design memory: NO per-ticker stub fanout; retrieval filters by metadata.

Cost note: each `claude -p` invocation pays a fixed ~$0.11 harness/system-prompt
overhead (≈29.7k cache-creation tokens). We therefore process all new episodes in a
SINGLE batched call so the overhead is paid once per run (≈$0.28 for a full 20-cap
batch), not per episode (~$2.30). Per-episode fallback only for uuids the batch drops.

Watermark = summaries.created_at (monotonic ingest order; date_published can be
backdated/empty). First run with no watermark seeds the cutoff to YESTERDAY so we
catch only new episodes going forward — no bulk historical backfill.

Usage:
    python3 scripts/v3_ingest/podcasts.py [--dry-run]

--dry-run still calls the LLM (so you see real extractions) but writes no note files
and does not advance the watermark; it prints what WOULD be written.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

# ───────────────────────────── Configuration ─────────────────────────────

REPO_ROOT = Path("/root/research-watchlist")
PODCASTS_DB = Path("/root/podcasts/data/podcasts.db")
TICKER_IDENTITY = REPO_ROOT / "config" / "ticker_identity.yaml"
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
NOTES_DIR = REPO_ROOT / "notes" / "podcasts"
WATERMARK_FILE = REPO_ROOT / "state" / "v3_ingest" / "podcasts_watermark.json"

MAX_EPISODES_PER_RUN = 20          # cap runaway cost if watermark is reset
BUDGET_WARN_USD = 0.50             # warn (not abort) if pre-flight estimate exceeds this
MODEL = "claude-sonnet-4-6"        # Sonnet: substantive-vs-name-drop judgment quality
CLAUDE_TIMEOUT_S = 300

# Which watchlist.yaml theme categories are extractable. Per the spec this is
# strategic[] only; widen to more categories by adding names here (e.g.
# "macro_policy" to allow ai_regulation / antitrust_action). One-line swap —
# see Checkpoint B discussion (regulation-heavy episodes land in macro_policy).
THEME_SCOPE = ["strategic"]

# Pre-flight cost model (Sonnet 4.6, USD per 1M tokens). Used ONLY for the budget
# warning; actual cost is read back from claude's total_cost_usd after the call.
FIXED_OVERHEAD_USD = 0.12          # observed harness cache-creation cost per claude -p
PRICE_INPUT_PER_M = 3.0
PRICE_OUTPUT_PER_M = 15.0

# ───────────────────────────── Logging ─────────────────────────────
# Structured lines to stdout; run_daily.sh tees stdout into logs/v3_podcasts.log.

def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] v3_podcasts: {msg}", flush=True)


# ───────────────────────────── Config loaders ─────────────────────────────

def load_watchlist_tickers() -> list[str]:
    """Top-level keys of ticker_identity.yaml = canonical T1+T2 watchlist tickers."""
    with open(TICKER_IDENTITY) as f:
        data = yaml.safe_load(f)
    tickers = [str(k) for k in data.keys()]
    if not tickers:
        raise RuntimeError("no tickers loaded from ticker_identity.yaml")
    return tickers


def load_themes(scope: list[str]) -> list[str]:
    """Flatten the selected theme categories from watchlist.yaml themes:{}."""
    with open(WATCHLIST_YAML) as f:
        data = yaml.safe_load(f)
    themes_block = data.get("themes", {}) or {}
    out: list[str] = []
    for cat in scope:
        out.extend(themes_block.get(cat, []) or [])
    if not out:
        raise RuntimeError(f"no themes loaded for scope {scope}")
    return out


# ───────────────────────────── Watermark ─────────────────────────────

def load_watermark() -> dict | None:
    if not WATERMARK_FILE.exists():
        return None
    try:
        return json.loads(WATERMARK_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log(f"WATERMARK_UNREADABLE ({e}); treating as first run")
        return None


def compute_cutoff(wm: dict | None) -> str:
    """
    Return the created_at cutoff string (DB format 'YYYY-MM-DD HH:MM:SS').
    First run (no watermark): yesterday's date → only new episodes going forward.
    """
    if wm and wm.get("last_ingested_at"):
        return wm["last_ingested_at"]
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    return yesterday  # 'YYYY-MM-DD' < any 'YYYY-MM-DD HH:MM:SS' that day, lexicographic-safe


def save_watermark(wm: dict | None, processed: list[dict], total_written: int) -> None:
    prev_total = (wm or {}).get("episodes_processed_total", 0)
    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    if processed:
        last = processed[-1]  # processed is created_at-ascending
        last_uuid = last["episode_uuid"]
        last_at = last["created_at"]
    else:
        last_uuid = (wm or {}).get("last_ingested_uuid", "")
        last_at = (wm or {}).get("last_ingested_at", "")
    new_wm = {
        "last_ingested_uuid": last_uuid,
        "last_ingested_at": last_at,
        "episodes_processed_total": prev_total + total_written,
        "last_run_at": now_iso,
    }
    WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_FILE.write_text(json.dumps(new_wm, indent=2) + "\n")
    log(f"WATERMARK_SAVED last_uuid={last_uuid} last_at={last_at!r} "
        f"total={new_wm['episodes_processed_total']}")


# ───────────────────────────── DB read ─────────────────────────────

def fetch_candidates(cutoff: str) -> list[dict]:
    """
    summaries JOIN episodes, created_at >= cutoff, ascending. We use >= (not >) so
    same-second ties at the boundary are never lost; the file-exists check skips
    already-written ones cheaply, BEFORE any LLM cost.
    """
    if not PODCASTS_DB.exists():
        raise RuntimeError(f"podcasts DB not found: {PODCASTS_DB}")
    conn = sqlite3.connect(f"file:{PODCASTS_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT s.episode_uuid   AS episode_uuid,
                   s.summary_text   AS summary_text,
                   s.created_at     AS created_at,
                   e.podcast_name   AS podcast_name,
                   e.title          AS title,
                   e.date_published AS date_published
            FROM summaries s
            JOIN episodes e ON s.episode_uuid = e.uuid
            WHERE s.created_at >= ?
              AND s.summary_text IS NOT NULL
              AND TRIM(s.summary_text) <> ''
            ORDER BY s.created_at ASC
            """,
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


# ───────────────────────────── Note path / frontmatter ─────────────────────────────

def note_date(ep: dict) -> str:
    """Filename/frontmatter date: date_published, else created_at's date."""
    dp = (ep.get("date_published") or "").strip()
    if dp:
        return dp[:10]
    return (ep.get("created_at") or "")[:10] or "undated"


def note_path(ep: dict) -> Path:
    uuid8 = ep["episode_uuid"][:8]
    return NOTES_DIR / f"{note_date(ep)}-{uuid8}.md"


def build_note(ep: dict, tickers: list[str], themes: list[str]) -> str:
    fm = {
        "doc_type": "podcast_summary",
        "source": "podcast",
        "source_id": ep["episode_uuid"],
        "podcast_name": ep.get("podcast_name") or "",
        "episode_title": ep.get("title") or "",
        "published_date": note_date(ep),
        "tickers": tickers,
        "themes": themes,
        "ingestion_date": dt.date.today().isoformat(),
        "extraction_source": (
            "v3 podcast ingest pipeline, claude-extracted tickers/themes from "
            "/root/podcasts/data/podcasts.db summaries table"
        ),
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    title = ep.get("title") or ep["episode_uuid"]
    body = (ep.get("summary_text") or "").strip()
    return f"---\n{front}---\n\n# {title}\n\n{body}\n"


# ───────────────────────────── LLM extraction ─────────────────────────────

EXTRACTION_INSTRUCTIONS = """\
You are a precise financial-research tagging assistant. You will receive a BATCH of
podcast episode summaries. For EACH episode, independently extract two things.

1. tickers — which of the WATCHLIST TICKERS are SUBSTANTIVELY discussed in that
   episode: a meaningful discussion of the company's business, strategy, products,
   financials, competitive position, capital allocation, or market outlook. EXCLUDE
   tickers that are merely name-dropped, listed in passing, or cited only as a generic
   sector example with no real substance. Return only symbols from the watchlist, using
   the EXACT watchlist symbol.

2. themes — which of the THEME TAGS are substantively present in that episode. Return
   only tags from the provided list. Empty array if none apply.

CRITICAL RULES
- Evaluate each episode in COMPLETE ISOLATION. Never let one episode's tickers or
  themes bleed into another. Reset your judgment at every episode boundary.
- A ticker/theme not in the provided lists must NEVER appear in output.
- Output ONLY a JSON array — one object per episode, every input episode included, in
  the same order. Each object is exactly:
  {"episode_uuid": "<uuid>", "tickers": ["..."], "themes": ["..."]}
  No prose, no markdown, no code fences, no commentary.
"""


def build_prompt(episodes: list[dict], tickers: list[str], themes: list[str]) -> str:
    blocks = []
    for ep in episodes:
        summary = (ep.get("summary_text") or "").strip()
        blocks.append(
            f"<<<EPISODE episode_uuid={ep['episode_uuid']}>>>\n"
            f"Podcast: {ep.get('podcast_name') or ''}\n"
            f"Title: {ep.get('title') or ''}\n"
            f"Summary:\n{summary}\n"
            f"<<<END EPISODE>>>"
        )
    return (
        EXTRACTION_INSTRUCTIONS
        + "\nWATCHLIST TICKERS (only these are valid):\n"
        + ", ".join(tickers)
        + "\n\nTHEME TAGS (only these are valid):\n"
        + ", ".join(themes)
        + "\n\nEPISODES:\n"
        + "\n\n".join(blocks)
        + "\n"
    )


def estimate_cost(prompt: str, n_episodes: int) -> float:
    in_tokens = len(prompt) / 4
    out_tokens = n_episodes * 80
    return (
        FIXED_OVERHEAD_USD
        + in_tokens * PRICE_INPUT_PER_M / 1e6
        + out_tokens * PRICE_OUTPUT_PER_M / 1e6
    )


def run_claude(prompt: str) -> tuple[str, float]:
    """Invoke `claude -p` (tool-free, JSON envelope). Returns (model_text, cost_usd)."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--allowedTools", "",
        "--model", MODEL,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=CLAUDE_TIMEOUT_S, cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} stderr={result.stderr[:300]}")
    envelope = json.loads(result.stdout)
    text = envelope.get("result", "")
    cost = float(envelope.get("total_cost_usd", 0.0) or 0.0)
    return text, cost


def parse_extraction(text: str, valid_tickers: set[str], valid_themes: set[str]) -> dict:
    """Parse the model's JSON array → {uuid: {'tickers':[...], 'themes':[...]}}, filtered
    to the valid vocab. Tolerates code fences / leading prose by grabbing the array."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON array in response: {text[:200]!r}")
    arr = json.loads(match.group(0))
    out: dict[str, dict] = {}
    for obj in arr:
        uuid = obj.get("episode_uuid")
        if not uuid:
            continue
        out[uuid] = {
            "tickers": [t for t in (obj.get("tickers") or []) if t in valid_tickers],
            "themes": [t for t in (obj.get("themes") or []) if t in valid_themes],
        }
    return out


def extract_all(episodes: list[dict], tickers: list[str], themes: list[str]) -> tuple[dict, float]:
    """
    Batched extraction with per-episode fallback for any uuid the batch drops.
    Returns ({uuid: {tickers, themes}}, total_cost_usd).
    """
    valid_t, valid_th = set(tickers), set(themes)
    prompt = build_prompt(episodes, tickers, themes)
    est = estimate_cost(prompt, len(episodes))
    log(f"COST_ESTIMATE ${est:.3f} for {len(episodes)} episodes "
        f"(batched, model={MODEL})")
    if est > BUDGET_WARN_USD:
        log(f"BUDGET_WARNING estimated ${est:.2f} exceeds ${BUDGET_WARN_USD:.2f} per-run guard")

    total_cost = 0.0
    results: dict[str, dict] = {}
    try:
        text, cost = run_claude(prompt)
        total_cost += cost
        results = parse_extraction(text, valid_t, valid_th)
        log(f"BATCH_OK extracted {len(results)}/{len(episodes)} episodes, cost=${cost:.4f}")
    except (RuntimeError, ValueError, json.JSONDecodeError) as e:
        log(f"BATCH_FAILED ({e}); falling back to per-episode")

    missing = [ep for ep in episodes if ep["episode_uuid"] not in results]
    if missing:
        log(f"FALLBACK per-episode for {len(missing)} uuid(s)")
    for ep in missing:
        try:
            text, cost = run_claude(build_prompt([ep], tickers, themes))
            total_cost += cost
            one = parse_extraction(text, valid_t, valid_th)
            results.update(one)
            if ep["episode_uuid"] in one:
                log(f"  FALLBACK_OK {ep['episode_uuid']} cost=${cost:.4f}")
            else:
                log(f"  FALLBACK_EMPTY {ep['episode_uuid']} (uuid not in response)")
        except (RuntimeError, ValueError, json.JSONDecodeError) as e:
            log(f"  FALLBACK_FAILED {ep['episode_uuid']} ({e})")
    log(f"COST_ACTUAL ${total_cost:.4f} total this run")
    return results, total_cost


# ───────────────────────────── Main ─────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="v3 podcast ingest")
    ap.add_argument("--dry-run", action="store_true",
                    help="extract + print what WOULD be written; no files, no watermark update")
    args = ap.parse_args()

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log(f"START mode={mode} theme_scope={THEME_SCOPE}")

    tickers = load_watchlist_tickers()
    themes = load_themes(THEME_SCOPE)
    wm = load_watermark()
    cutoff = compute_cutoff(wm)
    first_run = wm is None
    log(f"watchlist_tickers={len(tickers)} themes={len(themes)} "
        f"cutoff={cutoff!r} first_run={first_run}")

    candidates = fetch_candidates(cutoff)
    log(f"candidates_since_cutoff={len(candidates)}")

    # Idempotency: skip episodes whose note file already exists — BEFORE any LLM cost.
    new_eps, skipped = [], 0
    for ep in candidates:
        if note_path(ep).exists():
            skipped += 1
            continue
        new_eps.append(ep)
    if skipped:
        log(f"skipped_existing_files={skipped}")

    capped = False
    if len(new_eps) > MAX_EPISODES_PER_RUN:
        log(f"CAP applying max {MAX_EPISODES_PER_RUN} of {len(new_eps)} new episodes "
            f"(remainder picked up next run as watermark advances)")
        new_eps = new_eps[:MAX_EPISODES_PER_RUN]
        capped = True

    if not new_eps:
        log("NO_NEW_EPISODES — nothing to extract")
        if not args.dry_run:
            save_watermark(wm, processed=[], total_written=0)
        log(f"DONE mode={mode} written=0")
        return 0

    extractions, _cost = extract_all(new_eps, tickers, themes)

    written, written_eps, empty_both = 0, [], []
    for ep in new_eps:
        ex = extractions.get(ep["episode_uuid"], {"tickers": [], "themes": []})
        t, th = ex["tickers"], ex["themes"]
        path = note_path(ep)
        tag = ("thematic-only" if (not t and th) else
               "empty-both" if (not t and not th) else "tagged")
        if not t and not th:
            empty_both.append(ep)
        log(f"  EPISODE {ep['episode_uuid']} [{tag}] tickers={t} themes={th} -> {path.name}")
        if args.dry_run:
            written_eps.append(ep)
            continue
        path.write_text(build_note(ep, t, th))
        written += 1
        written_eps.append(ep)

    if empty_both:
        log(f"EMPTY_BOTH count={len(empty_both)} (no tickers AND no themes — "
            f"written as-is per spec; see Checkpoint C re: skip policy)")

    if args.dry_run:
        log(f"DRY-RUN complete: would write {len(written_eps)} notes "
            f"(capped={capped}); watermark NOT advanced")
    else:
        save_watermark(wm, processed=written_eps, total_written=written)
        log(f"DONE mode={mode} written={written} capped={capped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
