#!/usr/bin/env python3
"""
Ingestion job — Store A (docs/chunking-strategy.md step 4).

notes/**/*.md  ->  chunk_note()  ->  embed children (Gemini)  ->  Store.upsert

Idempotent: chunks are keyed by deterministic chunk_id and embeddings are
cached by content hash (embed.py), so re-running only embeds chunks whose text
changed. Safe to wire into enrich_sidecars.py / cron later.

Parents are stored as metadata only (no embedding) — they are the auto-merge
return target (§3a); children carry the vectors.

Usage:
    python3 scripts/chunking/ingest.py --all              # all notes
    python3 scripts/chunking/ingest.py --note notes/NVDA/20260521-1Q27.md
    python3 scripts/chunking/ingest.py --all --rebuild    # drop + reload
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from chunker import chunk_note
from embed import embed, EMBED_DIM
from store import FileStore

NOTES_ROOT = Path("/root/research-watchlist/notes")


def _iter_notes(args) -> list[Path]:
    if args.note:
        return [Path(args.note)]
    return sorted(NOTES_ROOT.rglob("*.md"))


def ingest(notes: list[Path], *, rebuild: bool = False) -> None:
    store = FileStore()
    if rebuild:
        store.clear()

    all_records: list[dict] = []
    child_texts: list[str] = []
    child_idx: list[int] = []   # index into all_records for each child needing an embedding
    skipped = 0

    for path in notes:
        try:
            chunks = chunk_note(path)
        except Exception as e:  # noqa: BLE001 — one bad note must not abort the batch
            skipped += 1
            print(f"  ! skip {path} ({type(e).__name__}: {e})", file=sys.stderr)
            continue
        for c in chunks:
            rec = asdict(c)
            rec["embedding"] = None
            if c.kind == "child":
                child_idx.append(len(all_records))
                child_texts.append(c.text)
            all_records.append(rec)

    print(f"chunked {len(notes) - skipped}/{len(notes)} notes "
          f"({skipped} skipped) -> {len(child_texts)} children to embed")

    if child_texts:
        print(f"embedding {len(child_texts)} children via gemini-embedding-001 "
              f"(dim {EMBED_DIM}; cache-backed) …", file=sys.stderr)
        vecs = embed(child_texts, "retrieval_document")
        for j, rec_i in enumerate(child_idx):
            all_records[rec_i]["embedding"] = vecs[j]

    store.upsert(all_records)
    p, c = store.count()
    print(f"store: {p} parents + {c} children at {store.dir}")


def main():
    ap = argparse.ArgumentParser(description="Ingest notes into Store A.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="ingest every notes/**/*.md")
    g.add_argument("--note", help="ingest a single note")
    ap.add_argument("--rebuild", action="store_true",
                    help="clear the store before ingesting (full rebuild)")
    args = ap.parse_args()
    ingest(_iter_notes(args), rebuild=args.rebuild)


if __name__ == "__main__":
    main()
