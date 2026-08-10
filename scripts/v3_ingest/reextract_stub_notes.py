#!/usr/bin/env python3
"""Re-extract periodic-form notes that were written as near-empty stubs.

Before commit f23b06e8 the channel could only anchor sections on "Item N." headers.
Issuers that carry those strings ONLY in a cross-reference index (Intel is the
reference case) produced notes of a few hundred characters — the real 3 MB document
was fetched and discarded. 48 notes across INTC / CRDO / AMBA / GEV / ASML / TSEM
are affected.

The extractor is fixed; these notes still hold the old stub text, so this re-runs
them through the production path (`process_filing`) to rewrite and re-ingest.

  python3 scripts/v3_ingest/reextract_stub_notes.py --dry-run
  python3 scripts/v3_ingest/reextract_stub_notes.py --limit 1
  python3 scripts/v3_ingest/reextract_stub_notes.py --ticker INTC
  python3 scripts/v3_ingest/reextract_stub_notes.py

The `filing` dict process_filing() needs is reconstructed from each note's own
frontmatter (accession, form, filed_date) plus the CIK and primary document parsed
out of filing_url — so fetch, section extraction, theme extraction, note write and
pg ingest all follow exactly the same code path as the daily channel.

STALE CHUNKS: section headings come from config and do not change, so parent
chunk_ids are stable and the far larger set of new children overwrites the old ones
by id. Any chunk_id that still belongs to the doc's old row set and is NOT reproduced
is deleted explicitly, so no orphan stub chunks survive.

Progress is checkpointed per note; an interrupted run resumes without re-spending.
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
STATE = REPO_ROOT / "state" / "v3_ingest" / "reextract_stub.json"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v3_ingest"))

import sec_filings as sf  # noqa: E402

PERIODIC = {"10-K", "10-Q", "20-F", "10-K/A", "10-Q/A"}
STUB_MAX = 2_000          # same threshold the extractor uses to call a section weak


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"done": {}}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n")


def parse_note(path: Path) -> tuple[dict, str] | None:
    m = re.match(r"^---\n(.*?\n)---\n(.*)$", path.read_text(errors="ignore"), re.S)
    if not m:
        return None
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def filing_from_frontmatter(fm: dict) -> dict | None:
    """Rebuild the dict process_filing() expects. filing_url looks like
    https://www.sec.gov/Archives/edgar/data/<cik>/<accession-nodashes>/<primary_doc>"""
    url = fm.get("filing_url") or ""
    m = re.search(r"/data/(\d+)/(\d+)/([^/]+)$", url)
    if not m:
        return None
    form = fm.get("form_type") or ""
    return {
        "ticker": fm.get("ticker"),
        "cik": m.group(1),
        "accession": fm.get("accession_number"),
        "primary_doc": m.group(3),
        "form": form,
        "base_form": form.split("/")[0],
        "filing_date": fm.get("filed_date"),
    }


def doc_id_of(path: Path) -> str:
    return hashlib.sha256(path.read_text(errors="ignore").encode()).hexdigest()


def chunk_ids_for(doc_id: str) -> set[str]:
    from pgconn import connect
    cur = connect().cursor()
    cur.execute("SELECT chunk_id FROM chunks WHERE doc_id=%s", (doc_id,))
    return {r[0] for r in cur.fetchall()}


def delete_chunks(chunk_ids: set[str]) -> int:
    if not chunk_ids:
        return 0
    from pgconn import connect
    cx = connect()
    cur = cx.cursor()
    cur.execute("DELETE FROM chunks WHERE chunk_id = ANY(%s)", (list(chunk_ids),))
    n = cur.rowcount
    cx.commit()
    return n


def find_stubs(ticker: str | None) -> list[Path]:
    out = []
    for p in sorted(NOTES_DIR.glob("*.md")):
        parsed = parse_note(p)
        if not parsed:
            continue
        fm, body = parsed
        if fm.get("form_type") not in PERIODIC:
            continue
        if ticker and fm.get("ticker") != ticker:
            continue
        if len(body) < STUB_MAX:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-extract stub periodic-form notes")
    ap.add_argument("--ticker", help="limit to one ticker")
    ap.add_argument("--limit", type=int, help="process at most N notes")
    ap.add_argument("--dry-run", action="store_true", help="list targets, change nothing")
    args = ap.parse_args()

    sf.load_config()
    st = load_state()
    done = st["done"]

    targets = [p for p in find_stubs(args.ticker) if p.name not in done]
    if args.limit:
        targets = targets[:args.limit]

    sf.log(f"REEXTRACT START targets={len(targets)} already_done={len(done)} "
           f"dry_run={args.dry_run}")
    if args.dry_run:
        for p in targets:
            fm, body = parse_note(p)
            sf.log(f"  would re-extract {p.name} ({len(body)} chars, {fm.get('form_type')})")
        return 0

    ok = failed = 0
    cost = 0.0
    valid_themes = sf.load_valid_themes()
    for i, path in enumerate(targets, 1):
        parsed = parse_note(path)
        if not parsed:
            sf.log(f"  [{i}/{len(targets)}] SKIP {path.name}: unparseable frontmatter")
            continue
        fm, old_body = parsed
        filing = filing_from_frontmatter(fm)
        if not filing or not filing["ticker"]:
            failed += 1
            sf.log(f"  [{i}/{len(targets)}] SKIP {path.name}: cannot rebuild filing dict")
            continue

        old_doc_id = doc_id_of(path)
        old_chunks = chunk_ids_for(old_doc_id)
        try:
            status, c = sf.process_filing(filing, dry_run=False, skip_themes=False,
                                          valid_themes=valid_themes)
            cost += c
        except Exception as e:  # noqa: BLE001
            failed += 1
            sf.log(f"  [{i}/{len(targets)}] FAILED {path.name}: {type(e).__name__}: {e}")
            continue

        new_body = (parse_note(path) or ({}, ""))[1]
        new_chunks = chunk_ids_for(doc_id_of(path))
        stale = old_chunks - new_chunks
        removed = delete_chunks(stale)

        ok += 1
        done[path.name] = {"old_chars": len(old_body), "new_chars": len(new_body),
                           "stale_removed": removed,
                           "at": dt.datetime.now().isoformat(timespec="seconds")}
        save_state(st)
        sf.log(f"  [{i}/{len(targets)}] OK {path.name} status={status} "
               f"{len(old_body)} -> {len(new_body)} chars, {len(new_chunks)} chunks, "
               f"{removed} stale removed")

    sf.log(f"REEXTRACT DONE ok={ok} failed={failed} cost=${cost:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
