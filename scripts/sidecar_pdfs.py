#!/usr/bin/env python3
"""
sidecar_pdfs.py — Idempotent PDF metadata sidecar generator.

For each PDF in raw-transcripts/ (top level) and raw-transcripts/processed/:
  - sidecar exists AND in index → skip
  - sidecar exists, NOT in index → append to index
  - no sidecar, filename matches a pattern → extract, write sidecar, append to index
  - no sidecar, filename unmatched → log and skip (no crash)

Designed to run on cron after gmail_poller. Idempotent: safe to run repeatedly.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from metadata.extract_filename import extract_from_filename
from metadata.sidecar import sidecar_path, write_sidecar, read_sidecar
from metadata.index import append_to_index, index_contains
from metadata.schema import SourceOrigin

SCAN_DIRS = [
    Path("/root/research/raw-transcripts"),
    Path("/root/research/raw-transcripts/processed"),
]


def find_pdfs():
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for path in sorted(scan_dir.iterdir()):
            if path.is_file() and path.suffix.lower() == ".pdf":
                yield path


def process(pdf: Path) -> str:
    side = sidecar_path(pdf)
    if side.exists():
        try:
            existing = read_sidecar(pdf)
        except Exception as e:
            return f"error: sidecar unreadable: {type(e).__name__}: {e}"
        if existing is None:
            return "error: sidecar exists but read returned None"
        try:
            if index_contains(existing.doc_id):
                return "skip"
        except Exception as e:
            return f"error: index_contains failed: {type(e).__name__}: {e}"
        try:
            append_to_index(existing)
        except Exception as e:
            return f"error: append_to_index failed: {type(e).__name__}: {e}"
        return "appended"

    try:
        meta = extract_from_filename(pdf, source_origin=SourceOrigin.GMAIL_POLLER)
    except (ValueError, KeyError) as e:
        return f"unmatched: {e}"
    except Exception as e:
        return f"error: extract_from_filename: {type(e).__name__}: {e}"

    if meta is None:
        return "unmatched: extractor returned None"

    try:
        write_sidecar(pdf, meta)
    except Exception as e:
        return f"error: write_sidecar: {type(e).__name__}: {e}"

    try:
        if not index_contains(meta.doc_id):
            append_to_index(meta)
    except Exception as e:
        return f"error: index append: {type(e).__name__}: {e}"

    return "new"


def main() -> int:
    counts = {"new": 0, "appended": 0, "skip": 0, "unmatched": 0, "error": 0}
    for pdf in find_pdfs():
        status = process(pdf)
        if status == "new":
            counts["new"] += 1
            print(f"new       {pdf.name}")
        elif status == "appended":
            counts["appended"] += 1
            print(f"appended  {pdf.name}")
        elif status == "skip":
            counts["skip"] += 1
        elif status.startswith("unmatched"):
            counts["unmatched"] += 1
            print(f"unmatched {pdf.name}: {status}")
        else:
            counts["error"] += 1
            print(f"ERROR     {pdf.name}: {status}")
    print()
    print(
        f"Summary: new={counts['new']} appended={counts['appended']} "
        f"skip={counts['skip']} unmatched={counts['unmatched']} error={counts['error']}"
    )
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
