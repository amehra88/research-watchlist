#!/usr/bin/env python3
"""Backfill themes onto SEC notes whose extraction failed during an OAuth outage.

Implements docs/sec-theme-backfill-scope.md. Themes are a HARD scope filter in
store.search(), so a doc whose every chunk has zero themes cannot be returned by a
theme-scoped query at all. Two outages (2026-07-01→07-08, 2026-08-05→08-09) left
826 such SEC docs.

WHAT THIS DOES NOT DO: re-chunk or re-embed. The note text is unchanged apart from
the frontmatter `themes:` line, so chunk boundaries and embeddings stay valid. It
runs theme extraction only, then updates the existing rows in place.

  python3 scripts/v3_ingest/theme_backfill.py --year 2026 --dry-run
  python3 scripts/v3_ingest/theme_backfill.py --year 2026 --limit 3
  python3 scripts/v3_ingest/theme_backfill.py --year 2026

SELECTION: `themes_failed: true` (added 2026-08-09, commit b1c351aa) only marks
notes written from that date onward, so the historical population is identified the
measured way instead — docs where EVERY chunk in pg has zero themes, mapped back to
disk by sha256 of the note text.

doc_id STALENESS (important): doc_id is sha256 of the full note text, so rewriting
frontmatter CHANGES it. The pg doc_id column therefore goes stale relative to the
file until someone re-ingests the note. That is safe: chunk_id is path-derived
(base_ticker + fiscal_quarter/stem), and the store upserts ON CONFLICT (chunk_id)
DO UPDATE, so a later re-ingest refreshes the same rows in place rather than
duplicating them. Consequence for this script: the doc_id→path map is computed ONCE
up front and the pg UPDATE uses the pre-edit hash. Do not recompute mid-loop.

If extraction returns an empty list the note is left completely untouched — the
filing genuinely discusses none of the vocabulary, and rewriting it would burn a
doc_id change for nothing.

Progress is checkpointed per doc, so an interrupted run resumes without re-spending.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path("/root/research-watchlist")
NOTES_DIR = REPO_ROOT / "notes" / "sec"
STATE = REPO_ROOT / "state" / "v3_ingest" / "theme_backfill.json"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v3_ingest"))

from sec_filings import extract_themes_with_retry, load_valid_themes, log  # noqa: E402


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"done": {}, "cost": 0.0}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n")


def themeless_doc_ids() -> set[str]:
    """SEC docs in pg where EVERY chunk has zero themes — the retrieval-degraded set."""
    from pgconn import connect
    cx = connect()
    cur = cx.cursor()
    cur.execute("""SELECT doc_id FROM chunks WHERE doc_type='sec_filing'
                   GROUP BY doc_id
                   HAVING bool_and(themes IS NULL OR cardinality(themes)=0)""")
    return {r[0] for r in cur.fetchall()}


def doc_id_map() -> dict[str, Path]:
    """sha256(note text) -> path, for every SEC note on disk. Computed once."""
    out = {}
    for p in NOTES_DIR.glob("*.md"):
        out[hashlib.sha256(p.read_text(errors="ignore").encode()).hexdigest()] = p
    return out


def note_body_and_ticker(path: Path) -> tuple[str, str]:
    """(body without frontmatter, filer ticker). The ticker comes from frontmatter,
    not the filename — filename slicing breaks on short tickers (GE -> 'GE-8')."""
    t = path.read_text(errors="ignore")
    m = re.match(r"^---\n(.*?\n)---\n", t, re.S)
    if not m:
        return t, ""
    fm = yaml.safe_load(m.group(1)) or {}
    return t[m.end():], str(fm.get("ticker") or "")


def rewrite_themes(path: Path, themes: list[str]) -> None:
    """Set `themes:` in frontmatter, preserving key order and every other field."""
    text = path.read_text(errors="ignore")
    m = re.match(r"^(---\n)(.*?\n)(---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError(f"no frontmatter in {path.name}")
    fm = yaml.safe_load(m.group(2)) or {}
    fm["themes"] = themes
    fm["themes_backfilled"] = dt.date.today().isoformat()
    fm.pop("themes_failed", None)          # resolved — drop the marker
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    path.write_text(f"---\n{front}---\n{m.group(4)}")


def update_pg(doc_id: str, themes: list[str]) -> int:
    """Union the new themes into every chunk of this doc, preserving whatever the
    per-chunk heuristic already found. Returns rows touched."""
    from pgconn import connect
    cx = connect()
    cur = cx.cursor()
    cur.execute(
        """UPDATE chunks
              SET themes = ARRAY(SELECT DISTINCT unnest(COALESCE(themes,'{}'::text[]) || %s::text[]))
            WHERE doc_id = %s""",
        (themes, doc_id),
    )
    n = cur.rowcount
    cx.commit()
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill themes onto theme-invisible SEC notes")
    ap.add_argument("--year", help="filing year to scope to (note filename prefix), e.g. 2026")
    ap.add_argument("--limit", type=int, help="process at most N docs (pilot runs)")
    ap.add_argument("--dry-run", action="store_true",
                    help="extract + print; no note rewrite, no pg update, no checkpoint")
    args = ap.parse_args()

    valid_themes = load_valid_themes()
    st = load_state()
    done = st["done"]

    themeless = themeless_doc_ids()
    h2p = doc_id_map()                     # computed ONCE — see docstring
    targets = []
    for doc_id in themeless:
        p = h2p.get(doc_id)
        if p is None:
            continue                       # note edited/removed since ingest
        if args.year and not p.name.startswith(args.year):
            continue
        if doc_id in done:
            continue
        targets.append((doc_id, p))
    targets.sort(key=lambda t: t[1].name)
    if args.limit:
        targets = targets[:args.limit]

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log(f"BACKFILL START mode={mode} year={args.year or 'all'} targets={len(targets)} "
        f"already_done={len(done)} vocab={len(valid_themes)}")

    applied = empty = failed = 0
    cost = 0.0
    for i, (doc_id, path) in enumerate(targets, 1):
        try:
            body, ticker = note_body_and_ticker(path)
            themes, c = extract_themes_with_retry(body, ticker, valid_themes)
            cost += c
        except Exception as e:  # noqa: BLE001
            failed += 1
            log(f"  [{i}/{len(targets)}] FAILED {path.name}: {type(e).__name__}: {e}")
            continue

        if not themes:
            empty += 1
            log(f"  [{i}/{len(targets)}] EMPTY {path.name} — genuinely no vocabulary themes; "
                f"note left untouched")
            if not args.dry_run:
                done[doc_id] = {"themes": [], "at": dt.datetime.now().isoformat(timespec="seconds")}
                st["cost"] = st.get("cost", 0.0) + cost
                save_state(st)
            continue

        if args.dry_run:
            log(f"  [{i}/{len(targets)}] [dry-run] {path.name} -> {themes}")
            applied += 1
            continue

        rewrite_themes(path, themes)
        rows = update_pg(doc_id, themes)
        applied += 1
        done[doc_id] = {"themes": themes, "rows": rows,
                        "at": dt.datetime.now().isoformat(timespec="seconds")}
        st["cost"] = st.get("cost", 0.0) + cost
        save_state(st)                     # checkpoint per doc — never re-spend
        log(f"  [{i}/{len(targets)}] OK {path.name} -> {themes} ({rows} chunks)")

    log(f"BACKFILL DONE mode={mode} applied={applied} empty={empty} failed={failed} "
        f"cost=${cost:.4f} (cumulative ${st.get('cost', 0.0):.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
