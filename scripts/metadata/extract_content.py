"""LLM-based content extraction for transcript PDFs.

Reads a PDF, extracts plain text, sends it to Gemini 2.5 Pro with a
structured-output schema, and returns the populated fields.

Layered on top of `extract_from_filename` which handles structural fields
(ticker, date, doc_type). This module fills content-derived fields that
require reading the document body.

Requirements:
- `GEMINI_API_KEY` environment variable (source /root/podcasts/.env)
- `google-genai` SDK (>=1.0)
- `pypdf` for PDF text extraction

Usage:
    from metadata.extract_content import extract_content_from_pdf
    result = extract_content_from_pdf("/path/to/transcript.pdf")
    # result is a dict with keys: speakers, transcript_provider, sponsor_firm,
    # moderator, word_count, extraction_model, extraction_timestamp
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Cap text sent to the model. Gemini Pro accepts 1M tokens but transcripts
# rarely exceed 100K chars. This caps the rare outlier from blowing input cost.
#
# Two caps: earnings calls have a fixed small speaker list (4-5 execs) named in
# the first few pages, so 30K is plenty. Conferences and analyst-day events may
# have many segment heads scattered throughout, so they need a larger window.
MAX_TEXT_CHARS_EARNINGS = 30_000
MAX_TEXT_CHARS_OTHER = 100_000

# Tail char count to also include from end of doc (Q&A section often has
# analyst names that don't appear in the prepared remarks).
TAIL_CHARS = 5_000

# Model identifier. Centralized so it can be overridden for testing or
# upgraded without hunting through code.
DEFAULT_MODEL = "gemini-2.5-pro"

# Prompt is intentionally explicit about what counts as evidence and when
# to return null. Gemini's structured-output mode respects the schema but
# the model can still hallucinate if the prompt is loose.
EXTRACTION_PROMPT = """\
You are extracting structured metadata from a financial transcript (earnings call \
or investor conference). Read the provided text carefully and populate the JSON \
schema with what you find.

CRITICAL RULES:
1. Only populate a field if you have direct textual evidence for it. If a field \
cannot be determined from the text, return null. Do not guess.
2. For `speakers`, include ONLY company management/executives presenting prepared \
remarks or answering questions (CEO, CFO, COO, segment heads, Chief Business Officer, \
Investor Relations head, etc.). DO NOT include:
   - Sell-side analysts, even if they ask questions
   - Speakers marked "Unverified Participant"
   - The operator/conference moderator
Use the name as it appears in the transcript. Include role and company affiliation when stated.
3. IGNORE the following sections entirely when identifying speakers:
   - "Important Disclosures", "Other Participants", or any compliance/disclaimer appendix
   - Risk factor boilerplate or safe-harbor statements
   - Any text after the main Q&A concludes (typically marked by closing remarks then disclaimers)
4. For `transcript_provider`, look for explicit branding, copyright lines, header/\
footer boilerplate, or markers like "CORRECTED TRANSCRIPT", "Bloomberg Transcript", \
"FactSet CallStreet", "Motley Fool", "InsiderScore", etc. If only the COMPANY's \
investor relations branding appears, the provider is "company IR".
5. For conference transcripts only:
   - `sponsor_firm` is the sell-side firm hosting the event (e.g., "Morgan Stanley" \
in "Morgan Stanley TMT Conference"). Null for earnings calls.

TRANSCRIPT TEXT FOLLOWS:
---
{text}
---
"""


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract plain text from a PDF using pypdf.

    Returns the full text. Caller is responsible for any truncation.
    """
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise RuntimeError(
            "pypdf not installed. Install with: pip install pypdf --break-system-packages"
        ) from e

    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as e:
            logger.warning("Failed to extract text from a page in %s: %s", pdf_path, e)
            continue
    return "\n".join(pages)


def _truncate_with_tail(text: str, max_chars: int,
                       tail_chars: int = TAIL_CHARS) -> str:
    """Truncate text but keep both head and tail.

    Transcripts often have key info (analyst names, closing remarks,
    transcript provider boilerplate) at the end. A naive head-truncation
    would lose that.
    """
    if len(text) <= max_chars:
        return text

    head_budget = max_chars - tail_chars
    if head_budget <= 0:
        # max_chars smaller than tail_chars; just take the tail
        return text[-max_chars:]

    head = text[:head_budget]
    tail = text[-tail_chars:]
    return f"{head}\n\n[... middle of document elided ...]\n\n{tail}"


def _count_words(text: str) -> int:
    """Simple whitespace-tokenized word count."""
    return len(re.findall(r"\S+", text))


def extract_content_from_pdf(
    pdf_path: str | Path,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> dict:
    """Run LLM extraction on a PDF and return enriched metadata fields.

    Args:
        pdf_path: path to the PDF file
        model: Gemini model identifier (default: gemini-2.5-pro)
        api_key: explicit API key; if None, reads from GEMINI_API_KEY env var
        doc_type: 'earnings_transcript' for tight 30K cap; anything else (or None)
            uses the 100K cap. Conferences and analyst days need the larger window
            to capture all segment-head speakers.

    Returns:
        dict with keys:
            speakers: list[dict] | None
            transcript_provider: str | None
            sponsor_firm: str | None
            moderator: str | None
            word_count: int (deterministic, not from LLM)
            extraction_model: str
            extraction_timestamp: ISO 8601 UTC

    Raises:
        FileNotFoundError: pdf_path doesn't exist
        RuntimeError: pypdf missing, API key missing, or API call fails
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Source /root/podcasts/.env before running."
        )

    # Extract text from PDF
    logger.info("Extracting text from %s", pdf_path.name)
    full_text = _extract_pdf_text(pdf_path)
    word_count = _count_words(full_text)
    logger.info("Extracted %d words (%d chars) from %s",
                word_count, len(full_text), pdf_path.name)

    if not full_text.strip():
        logger.warning("PDF %s appears empty or unreadable; returning minimal result",
                       pdf_path)
        return {
            "speakers": None,
            "transcript_provider": None,
            "sponsor_firm": None,
            "moderator": None,
            "word_count": 0,
            "extraction_model": model,
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "extraction_status": "empty_pdf",
        }

    # Truncate (keeps head + tail). Cap depends on doc_type.
    max_chars = MAX_TEXT_CHARS_EARNINGS if doc_type == "earnings_transcript" else MAX_TEXT_CHARS_OTHER
    text_for_llm = _truncate_with_tail(full_text, max_chars=max_chars)
    if text_for_llm != full_text:
        logger.info("Truncated text from %d to %d chars before LLM call (cap=%d, doc_type=%s)",
                    len(full_text), len(text_for_llm), max_chars, doc_type)

    # Build the API call
    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError as e:
        raise RuntimeError(
            "google-genai SDK not installed. Install with: "
            "pip install google-genai --break-system-packages"
        ) from e

    from .schemas.extraction_output import ExtractionOutput

    client = genai.Client(api_key=api_key)
    prompt = EXTRACTION_PROMPT.format(text=text_for_llm)

    logger.info("Calling Gemini model=%s for %s", model, pdf_path.name)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionOutput,
                # Low temperature for extraction. We want determinism, not creativity.
                temperature=0.1,
            ),
        )
    except Exception as e:
        logger.exception("Gemini API call failed for %s", pdf_path.name)
        raise RuntimeError(f"Gemini API call failed: {e}") from e

    # Parse and validate
    try:
        parsed = ExtractionOutput.model_validate_json(response.text)
    except Exception as e:
        logger.exception("Failed to parse Gemini response as ExtractionOutput. "
                         "Raw response: %s", response.text[:500])
        raise RuntimeError(f"Response validation failed: {e}") from e

    result = parsed.model_dump(mode="json")
    result.update({
        "word_count": word_count,
        "extraction_model": model,
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "extraction_status": "ok",
    })

    logger.info(
        "Extraction complete for %s: %d speakers, provider=%s",
        pdf_path.name,
        len(result["speakers"]) if result.get("speakers") else 0,
        result.get("transcript_provider"),
    )
    return result
