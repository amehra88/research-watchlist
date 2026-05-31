#!/usr/bin/env python3
"""Backfill YAML frontmatter into existing notes from their enriched sidecars.

Walks /root/research-watchlist/notes/{TICKER}/*.md, for each note:
  1. Parses the filename for ticker and date
  2. Locates the matching PDF + sidecar in /root/research/raw-transcripts/{,processed/}
  3. Reads the sidecar (structural fields + enrichment block)
  4. Builds YAML frontmatter from sidecar fields
  5. Prepends frontmatter to the note (atomic write)

Idempotent: skips notes that already have frontmatter (line 1 is '---') unless --force.

Designed for one-shot retrofit of notes written before commit 28b6d5d
(earnings-reviewer-from-pdf emitting frontmatter).

Note filename conventions (from doc section 4):
  earnings:   {YYYYMMDD}-{quarter}.md         e.g. 20260429-1Q26.md
  conference: {YYYYMMDD}-conf-{shortname}.md  e.g. 20260514-conf-moffettnathanson.md

Sidecar lookup: takes the note's parent dir (ticker), parses date,
constructs the corresponding PDF filename ({TICKER}-{YYYY-MM-DD}-{rest}.pdf),
then searches both raw-transcripts roots.

Usage:
    /root/research-watchlist/scripts/backfill_frontmatter.py
    /root/research-watchlist/scripts/backfill_frontmatter.py --dry-run -v
    /root/research-watchlist/scripts/backfill_frontmatter.py --note /path/to/note.md
    /root/research-watchlist/scripts/backfill_frontmatter.py --force --limit 1
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

NOTES_ROOT = Path("/root/research-watchlist/notes")
PDF_ROOTS = [
    Path("/root/research/raw-transcripts"),
    Path("/root/research/raw-transcripts/processed"),
]

# Parse note filename. Two patterns:
#   {YYYYMMDD}-{quarter}.md                   (earnings)
#   {YYYYMMDD}-conf-{shortname}.md            (conference)
EARNINGS_RE = re.compile(r"^(\d{8})-([0-9]Q\d{2})\.md$")
CONFERENCE_RE = re.compile(r"^(\d{8})-conf-(.+)\.md$")


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _yyyymmdd_to_iso(s: str) -> str:
    """20260429 -> 2026-04-29"""
    return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"


def _parse_note_filename(note_path: Path) -> dict | None:
    """Extract ticker, event_date, and a 'rest' fragment identifying the PDF.

    Returns dict with keys: ticker, event_date (YYYY-MM-DD), rest (the part
    after the date in the PDF filename: e.g. '1Q26' or 'conf-moffettnathanson').
    Returns None if filename doesn't match a known pattern.
    """
    ticker = note_path.parent.name
    name = note_path.name

    m = EARNINGS_RE.match(name)
    if m:
        return {
            "ticker": ticker,
            "event_date": _yyyymmdd_to_iso(m.group(1)),
            "rest": m.group(2),  # e.g. "1Q26"
        }

    m = CONFERENCE_RE.match(name)
    if m:
        return {
            "ticker": ticker,
            "event_date": _yyyymmdd_to_iso(m.group(1)),
            "rest": f"conf-{m.group(2)}",
        }

    return None


def _find_sidecar(ticker: str, event_date: str, rest: str) -> Path | None:
    """Locate the sidecar for {TICKER}-{YYYY-MM-DD}-{rest}.pdf in both PDF roots."""
    expected_pdf_name = f"{ticker}-{event_date}-{rest}.pdf"
    expected_sidecar_name = f"{expected_pdf_name}.meta.json"
    for root in PDF_ROOTS:
        candidate = root / expected_sidecar_name
        if candidate.exists():
            return candidate
    return None


def _has_frontmatter(note_path: Path) -> bool:
    """True if the note begins with '---' on its very first line."""
    try:
        with note_path.open("r", encoding="utf-8") as f:
            first_line = f.readline().rstrip("\n")
        return first_line.strip() == "---"
    except Exception:
        return False


def _yaml_escape(value: str) -> str:
    """Conservative scalar quoting for YAML.

    YAML accepts unquoted strings in most cases, but if the value contains
    a colon, leading dash, quote, or starts with chars YAML reserves, wrap
    in double quotes. We always double-quote to keep it simple and safe.
    """
    if value is None:
        return "null"
    # Escape backslashes and double quotes for YAML double-quoted scalar
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _build_frontmatter(sidecar: dict) -> str:
    """Build the YAML frontmatter string (including --- delimiters) from a sidecar dict.

    Maps both structural fields and enrichment.* fields. Skips fields that are
    absent or null. Preserves the field order that earnings-reviewer-from-pdf
    emits (commit 28b6d5d), with enrichment fields appended at the end.
    """
    lines = ["---"]

    # Structural fields (mirror earnings-reviewer-from-pdf emission order)
    structural_order = [
        "doc_type",
        "primary_ticker",
        "subject_tickers",
        "event_date",
        "year",
        "fiscal_quarter",       # earnings only
        "conference_name",      # conference only
        "ingestion_date",
        "source_origin",
        "source_file_path",
    ]
    for key in structural_order:
        if key not in sidecar or sidecar[key] is None:
            continue
        val = sidecar[key]
        if isinstance(val, list):
            if not val:
                continue
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {_yaml_escape(str(item))}")
        elif isinstance(val, (int, float)):
            lines.append(f"{key}: {val}")
        else:
            lines.append(f"{key}: {_yaml_escape(str(val))}")

    # Enrichment fields, if any
    enrichment = sidecar.get("enrichment") or {}
    if enrichment.get("extraction_status") == "ok":
        # Simple scalar enrichment fields
        for key in ("transcript_provider", "sponsor_firm", "word_count"):
            val = enrichment.get(key)
            if val is None:
                continue
            if isinstance(val, (int, float)):
                lines.append(f"{key}: {val}")
            else:
                lines.append(f"{key}: {_yaml_escape(str(val))}")

        # Speakers as list of nested dicts
        speakers = enrichment.get("speakers")
        if speakers:
            lines.append("speakers:")
            for sp in speakers:
                name = sp.get("name") or ""
                lines.append(f"  - name: {_yaml_escape(name)}")
                if sp.get("role"):
                    lines.append(f"    role: {_yaml_escape(sp['role'])}")
                if sp.get("company"):
                    lines.append(f"    company: {_yaml_escape(sp['company'])}")

    lines.append("---")
    lines.append("")  # blank line after frontmatter, before note body
    return "\n".join(lines) + "\n"


def _write_note_atomic(note_path: Path, content: str) -> None:
    """Write note via tempfile+rename for atomicity."""
    fd, tmp_path = tempfile.mkstemp(
        prefix=".tmp-",
        suffix=".md",
        dir=note_path.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, note_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _find_all_notes(notes_root: Path) -> list[Path]:
    """Walk notes/ recursively, return all .md files."""
    notes: list[Path] = []
    if not notes_root.exists():
        logging.warning("Notes root does not exist: %s", notes_root)
        return notes
    for entry in notes_root.rglob("*.md"):
        if entry.is_file():
            notes.append(entry)
    return sorted(notes)


def process_one(note_path: Path, force: bool, dry_run: bool) -> str:
    """Backfill frontmatter into one note. Returns status string."""
    # 1. Parse filename
    parsed = _parse_note_filename(note_path)
    if not parsed:
        logging.warning("Could not parse filename: %s", note_path)
        return "unparseable"

    # 2. Skip if already has frontmatter (unless force)
    if not force and _has_frontmatter(note_path):
        logging.debug("Already has frontmatter, skipping: %s", note_path)
        return "skip"

    # 3. Locate sidecar
    sidecar_path = _find_sidecar(parsed["ticker"], parsed["event_date"], parsed["rest"])
    if not sidecar_path:
        logging.warning("No sidecar found for note %s (looked for %s-%s-%s.pdf.meta.json)",
                        note_path, parsed["ticker"], parsed["event_date"], parsed["rest"])
        return "no_sidecar"

    # 4. Read sidecar
    try:
        with sidecar_path.open("r", encoding="utf-8") as f:
            sidecar = json.load(f)
    except Exception as e:
        logging.error("Failed to read sidecar %s: %s", sidecar_path, e)
        return "error"

    if dry_run:
        logging.info("[DRY RUN] Would prepend frontmatter to %s (from %s)",
                     note_path.name, sidecar_path.name)
        return "would_update"

    # 5. Build new content. If --force and existing frontmatter, replace it.
    try:
        with note_path.open("r", encoding="utf-8") as f:
            existing = f.read()
    except Exception as e:
        logging.error("Failed to read note %s: %s", note_path, e)
        return "error"

    if force and _has_frontmatter(note_path):
        # Strip existing frontmatter: find the closing '---' on its own line
        lines = existing.split("\n")
        # lines[0] is '---'. Find next '---'.
        close_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                close_idx = i
                break
        if close_idx is not None:
            # Body starts at close_idx + 1. Skip any blank line right after.
            body_start = close_idx + 1
            while body_start < len(lines) and lines[body_start].strip() == "":
                body_start += 1
            body = "\n".join(lines[body_start:])
        else:
            # Malformed existing frontmatter; preserve whole file as body
            logging.warning("Existing frontmatter on %s has no closing '---'; treating whole file as body",
                            note_path)
            body = existing
    else:
        body = existing

    frontmatter = _build_frontmatter(sidecar)
    new_content = frontmatter + body

    # 6. Atomic write
    try:
        _write_note_atomic(note_path, new_content)
    except Exception as e:
        logging.error("Failed to write %s: %s", note_path, e)
        return "error"

    logging.info("Backfilled: %s", note_path)
    return "updated"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--force", action="store_true",
                        help="Replace existing frontmatter (default: skip notes that already have it)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N notes (useful for testing)")
    parser.add_argument("--note", type=Path, default=None,
                        help="Process a single specific note instead of walking notes/")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done, don't write")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose (DEBUG-level) logging")
    args = parser.parse_args(argv)

    _setup_logging(args.verbose)

    if args.note:
        notes = [args.note]
    else:
        notes = _find_all_notes(NOTES_ROOT)

    logging.info("Found %d note(s) to consider", len(notes))

    counts = {"updated": 0, "would_update": 0, "skip": 0,
              "no_sidecar": 0, "unparseable": 0, "error": 0}
    processed = 0

    for note in notes:
        status = process_one(note, force=args.force, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
        if status in ("updated", "would_update"):
            processed += 1
            if args.limit is not None and processed >= args.limit:
                logging.info("Hit --limit of %d, stopping", args.limit)
                break

    logging.info(
        "Summary: updated=%d would_update=%d skip=%d no_sidecar=%d unparseable=%d error=%d",
        counts["updated"], counts["would_update"], counts["skip"],
        counts["no_sidecar"], counts["unparseable"], counts["error"]
    )
    return 1 if counts["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
