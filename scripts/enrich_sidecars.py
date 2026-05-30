#!/usr/bin/env python3
"""Walk sidecar files, enrich those missing LLM-extracted fields.

This script is the orchestrator on top of `metadata.extract_content`.
It:
  1. Walks /root/research/raw-transcripts/{,processed/} for *.pdf
  2. For each PDF, locates the corresponding .meta.json sidecar
  3. If the sidecar lacks an `enrichment` block (or --force is set),
     calls extract_content_from_pdf() and merges the result into the sidecar
  4. Writes the updated sidecar atomically

Idempotent: re-running picks up only sidecars without an `enrichment`
block. The block's presence is the gate.

Usage:
    # Source the env file holding GEMINI_API_KEY first
    source /root/podcasts/.env
    /root/research-watchlist/scripts/enrich_sidecars.py
    /root/research-watchlist/scripts/enrich_sidecars.py --force
    /root/research-watchlist/scripts/enrich_sidecars.py --limit 1   # test with one
    /root/research-watchlist/scripts/enrich_sidecars.py --pdf /path/to/single.pdf

Designed to be wired to cron after manual validation.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

# Allow running this script from anywhere by adding the scripts dir to path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from metadata.extract_content import extract_content_from_pdf  # noqa: E402

# Source dirs to scan for PDFs
DEFAULT_PDF_ROOTS = [
    Path("/root/research/raw-transcripts"),
    Path("/root/research/raw-transcripts/processed"),
]


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _sidecar_path_for(pdf_path: Path) -> Path:
    """Convention: sidecar lives next to the PDF as <pdf_path>.meta.json."""
    return pdf_path.with_suffix(pdf_path.suffix + ".meta.json")


def _read_sidecar(sidecar_path: Path) -> dict:
    with sidecar_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_sidecar_atomic(sidecar_path: Path, data: dict) -> None:
    """Write the sidecar via tempfile + rename to avoid partial writes."""
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    # Use a tempfile in the same dir so the rename is atomic on the same FS
    fd, tmp_path = tempfile.mkstemp(
        prefix=".tmp-",
        suffix=".meta.json",
        dir=sidecar_path.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_path, sidecar_path)
    except Exception:
        # Clean up the tempfile if anything went wrong before the rename
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _find_all_pdfs(roots: list[Path]) -> list[Path]:
    """Collect all PDFs in the given roots, non-recursively per the
    convention that /raw-transcripts/ and /raw-transcripts/processed/ are
    each flat directories (see section 4 of the project status doc)."""
    pdfs: list[Path] = []
    for root in roots:
        if not root.exists():
            logging.warning("PDF root does not exist, skipping: %s", root)
            continue
        for entry in sorted(root.iterdir()):
            if entry.is_file() and entry.suffix.lower() == ".pdf":
                pdfs.append(entry)
    return pdfs


def _needs_enrichment(sidecar: dict, force: bool) -> bool:
    if force:
        return True
    enrichment = sidecar.get("enrichment")
    if not enrichment:
        return True
    # If a previous run failed (status != ok), retry
    if enrichment.get("extraction_status") != "ok":
        return True
    return False


def process_one(pdf_path: Path, force: bool, dry_run: bool) -> str:
    """Enrich a single PDF's sidecar. Returns a status string for the
    summary line: 'enriched', 'skip', 'no_sidecar', 'error'."""
    sidecar_path = _sidecar_path_for(pdf_path)
    if not sidecar_path.exists():
        logging.warning("No sidecar found for %s -- run sidecar_pdfs.py first",
                        pdf_path.name)
        return "no_sidecar"

    try:
        sidecar = _read_sidecar(sidecar_path)
    except Exception as e:
        logging.error("Failed to read sidecar %s: %s", sidecar_path, e)
        return "error"

    if not _needs_enrichment(sidecar, force):
        logging.debug("Already enriched, skipping: %s", pdf_path.name)
        return "skip"

    if dry_run:
        logging.info("[DRY RUN] Would enrich %s", pdf_path.name)
        return "enriched"

    try:
        enrichment = extract_content_from_pdf(pdf_path)
    except Exception as e:
        logging.exception("Extraction failed for %s: %s", pdf_path.name, e)
        # Persist a stub failure marker so we can see this in the sidecar
        # without blocking future retries (status != ok means we retry).
        sidecar["enrichment"] = {
            "extraction_status": "error",
            "extraction_error": str(e),
        }
        try:
            _write_sidecar_atomic(sidecar_path, sidecar)
        except Exception as e2:
            logging.error("Also failed to persist error stub for %s: %s",
                         pdf_path.name, e2)
        return "error"

    sidecar["enrichment"] = enrichment
    try:
        _write_sidecar_atomic(sidecar_path, sidecar)
    except Exception as e:
        logging.error("Failed to write enriched sidecar %s: %s", sidecar_path, e)
        return "error"

    logging.info("Enriched: %s", pdf_path.name)
    return "enriched"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--force", action="store_true",
                        help="Re-enrich even if enrichment block exists")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N PDFs needing enrichment (useful for testing)")
    parser.add_argument("--pdf", type=Path, default=None,
                        help="Process a single specific PDF instead of walking all roots")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done, don't call the LLM or write sidecars")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose (DEBUG-level) logging")
    parser.add_argument("--sleep", type=float, default=0.0,
                        help="Seconds to sleep between API calls (rate-limit pacing)")
    args = parser.parse_args(argv)

    _setup_logging(args.verbose)

    if args.pdf:
        pdfs = [args.pdf]
    else:
        pdfs = _find_all_pdfs(DEFAULT_PDF_ROOTS)

    logging.info("Found %d PDF(s) to consider", len(pdfs))

    counts = {"enriched": 0, "skip": 0, "no_sidecar": 0, "error": 0}
    processed_count = 0

    for pdf in pdfs:
        status = process_one(pdf, force=args.force, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1

        # Track how many we actually sent to the LLM, for --limit purposes
        if status == "enriched":
            processed_count += 1
            if args.sleep > 0:
                time.sleep(args.sleep)
            if args.limit is not None and processed_count >= args.limit:
                logging.info("Hit --limit of %d, stopping", args.limit)
                break

    logging.info(
        "Summary: enriched=%d skip=%d no_sidecar=%d error=%d",
        counts["enriched"], counts["skip"], counts["no_sidecar"], counts["error"]
    )

    # Exit non-zero if any errors occurred -- lets alert_on_failure.sh catch it
    return 1 if counts["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
