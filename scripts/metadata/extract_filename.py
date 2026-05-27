"""
Filename regex extractor for source document metadata.

Parses filenames following established conventions, returns partial DocMetadata
with what can be inferred from the filename alone. Content-derived fields
(speakers, word_count, etc.) are left as defaults — those come from the LLM
extractor in a separate module.

Conventions:
- Earnings: {TICKER}-{YYYY-MM-DD}-{quarter}.pdf
  e.g., GOOGL-2026-04-29-1Q26.pdf
- Conference: {TICKER}-{YYYY-MM-DD}-conf-{shortname}.pdf
  e.g., GOOGL-2026-03-03-conf-morgan-stanley-tmt.pdf
"""

import re
import hashlib
from datetime import date
from pathlib import Path
from typing import Optional

from .schema import DocMetadata, DocType, SourceOrigin

EARNINGS_PATTERN = re.compile(
    r"^(?P<ticker>[A-Z]+)-(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<quarter>\d[QqFfHh]?\d{2})$",
)
CONFERENCE_PATTERN = re.compile(
    r"^(?P<ticker>[A-Z]+)-(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-conf-(?P<shortname>[a-z0-9\-]+)$",
)


def compute_doc_id(path: Path) -> str:
    """SHA256 of source file content. Primary key for the doc."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def slug_to_title(slug: str) -> str:
    """Convert kebab-case slug to title-cased name (best-effort)."""
    return " ".join(part.capitalize() for part in slug.split("-"))


def extract_from_filename(
    path: Path,
    source_origin: SourceOrigin = SourceOrigin.GMAIL_POLLER,
) -> Optional[DocMetadata]:
    """
    Parse filename, return partial DocMetadata. None if no pattern matches.
    """
    stem = path.stem
    today = date.today()

    m = EARNINGS_PATTERN.match(stem)
    if m:
        ticker = m.group("ticker")
        year = int(m.group("year"))
        month = int(m.group("month"))
        day = int(m.group("day"))
        quarter = m.group("quarter")
        return DocMetadata(
            doc_id=compute_doc_id(path),
            doc_type=DocType.EARNINGS_TRANSCRIPT,
            source_file_path=str(path.resolve()),
            source_origin=source_origin,
            ingestion_date=today,
            primary_ticker=ticker,
            subject_tickers=[ticker],
            event_date=date(year, month, day),
            year=year,
            fiscal_quarter=quarter,
        )

    m = CONFERENCE_PATTERN.match(stem)
    if m:
        ticker = m.group("ticker")
        year = int(m.group("year"))
        month = int(m.group("month"))
        day = int(m.group("day"))
        shortname = m.group("shortname")
        return DocMetadata(
            doc_id=compute_doc_id(path),
            doc_type=DocType.CONFERENCE_TRANSCRIPT,
            source_file_path=str(path.resolve()),
            source_origin=source_origin,
            ingestion_date=today,
            primary_ticker=ticker,
            subject_tickers=[ticker],
            event_date=date(year, month, day),
            year=year,
            conference_name=slug_to_title(shortname),
        )

    return None
