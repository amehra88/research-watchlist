#!/usr/bin/env python3
"""Ingest a YouTube analyst-day keynote into a structured research note.

Uses Gemini 2.5 Pro multimodal to extract structured analyst-day metadata + content
directly from a YouTube URL (Gemini handles the video transcription internally; no
yt-dlp / Whisper / download step required).

Output: notes/{TICKER}/{YYYYMMDD}-conf-{shortname}.md with YAML frontmatter
matching the existing conf-* convention (doc_type: conference_transcript).

Usage (run from anywhere; paths are absolute):
    source /root/podcasts/.env
    /root/research-watchlist/scripts/ingest_youtube_keynote.py \\
        --url https://www.youtube.com/watch?v=11PBno-cJ1g \\
        --ticker GOOGL \\
        --date 2026-04-22 \\
        --shortname cloud-next \\
        --conference-name "Google Cloud Next 2026"

The script:
  - Calls Gemini 2.5 Pro with a structured-output prompt designed for analyst-day
    content (named customers, quantified guides, product launches, cross-ticker
    implications), NOT the investor-digest format used by /root/podcasts/summarizer.py
  - Writes the result to notes/{TICKER}/{YYYYMMDD}-conf-{shortname}.md
  - Atomic write (temp file + rename)
  - Refuses to overwrite an existing note unless --force
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

NOTES_ROOT = Path("/root/research-watchlist/notes")

EXTRACTION_PROMPT = """You are an investment research analyst processing the recorded transcript of a major company analyst-day keynote / product launch event. The company is {ticker} (a public technology company).

Your job: extract structured content from this video that an investment-research synthesis agent (downstream) can read. The downstream agent specifically hunts for LEADING SIGNALS — competitor forward-guidance, named-customer wins, quantified product specs, strategic positioning statements — so prioritize those.

CRITICAL EXTRACTION RULES:
1. NAMED CUSTOMERS: Capture every customer name mentioned on stage with the specific product / use case they discussed (e.g., "Citadel Securities — using TPU for X workload"). This is the highest-value data type for downstream analysis.
2. QUANTIFIED CLAIMS: Capture every TAM number, growth rate, capacity figure, customer count, performance multiplier WITH the exact value AND who said it.
3. PRODUCT LAUNCHES: Capture each new product name, its claimed specs (verbatim, not paraphrased), and ship date / availability timing.
4. STRATEGIC POSITIONING: Capture verbatim statements that signal competitive direction — e.g., "select group of customers", "merchant silicon", "open ecosystem", "incrementally bearish [competitor]" if anyone says such things on stage.
5. COMPETITOR MENTIONS: When competing products / companies are named (TPU vs NVDA GPU, Trainium, MTIA, AMD MI400, etc.), capture WHO said it and the framing.
6. SPEAKERS: For each substantial section, capture the speaker's name + title + company. List ALL speakers who appear (CEO, CFO, segment heads, customer guests, partner guests).
7. CROSS-TICKER IMPLICATIONS: When the content has clear implications for OTHER public tickers (NVDA, AMZN, MSFT, AMD, etc.), surface them in their own section.

DO NOT:
- Summarize at a high level — be granular, specific, quantified, attributed
- Invent or extrapolate beyond what's actually said in the video
- Use "demo showed" or "discussed" as substitutes for the actual content
- Omit numbers, customer names, or product specs in favor of narrative flow

OUTPUT STRUCTURE (markdown, exactly this shape):

# {ticker} — {conference_name} ({event_date})

_Ingested from YouTube via Gemini 2.5 Pro on {ingestion_date}. Source: {source_url}_

## 1. Headline read

3-5 sentences identifying the single most material strategic announcement(s) and their thesis-level implications. Frame as leading signals where applicable.

## 2. Speakers

List every named speaker who appears, in roughly the order they take the stage:
- Name — Title, Company
- (repeat)

## 3. Product announcements

For each new product / major update announced:

### {Product Name}
- **Specs/claims:** verbatim quoted specs (e.g., "3x raw computing power", "9,600 TPUs per pod", "2 PB shared bandwidth memory")
- **Availability:** ship/launch date
- **Said by:** who announced it
- **Strategic framing:** how the company positioned it (e.g., "first dual-chip approach with specialized architectures for training and inference")

## 4. Named customers and partners

For every customer or partner mentioned by name on stage:

| Customer/Partner | Product/Use Case | Speaker | Verbatim notes |
|---|---|---|---|
| Citadel Securities | TPU 8 | Kurian | "..." |
| (repeat) | | | |

## 5. Quantified guidance and TAM claims

Every number stated on stage with its attribution:
- {Number / metric} — {speaker} — "{verbatim quote if memorable}"
- (repeat)

## 6. Strategic positioning statements

Verbatim or near-verbatim quotes that signal competitive direction. Each on its own line with speaker attribution. These are the leading-signal gold.

## 7. Cross-ticker implications

What this content means for other public companies in the watchlist (NVDA, AMZN, MSFT, AMD, ANET, AVGO, MRVL, etc.). One short paragraph per affected ticker, with explicit citation to which Cloud Next content drives the implication.

## 8. Drift signals vs prior coverage

If this content resolves, reverses, or introduces signals relative to what the company previously said (last earnings call, last analyst day), flag those drifts explicitly. If you have no prior baseline (which is likely — you don't have access to prior notes), say "Unable to assess drift — no prior baseline in this ingest context."

---

Begin extraction now. Be specific, quantified, attributed. The downstream agent depends on the granularity of your output."""


FRONTMATTER_TEMPLATE = """---
doc_type: conference_transcript
primary_ticker: "{ticker}"
subject_tickers:
  - "{ticker}"
event_date: "{event_date}"
year: {year}
conference_name: "{conference_name}"
ingestion_date: "{ingestion_date}"
source_origin: youtube_ingest
source_url: "{source_url}"
extraction_model: "gemini-2.5-pro"
language: en
---

"""


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _write_note_atomic(note_path: Path, content: str) -> None:
    """Write via tempfile + rename for atomicity. Creates parent dir if needed."""
    note_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", suffix=".md", dir=note_path.parent)
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


def call_gemini(url: str, ticker: str, conference_name: str, event_date: str, ingestion_date: str, source_url: str) -> str:
    """Call Gemini 2.5 Pro with the YouTube URL + structured-extraction prompt.

    Mirrors the pattern from /root/podcasts/summarizer.py but with a different prompt
    and longer timeout (analyst-day videos run 90-120min; Gemini processes them
    in roughly real-time for video input).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set; source /root/podcasts/.env first")

    from google import genai
    from google.genai import types

    prompt = EXTRACTION_PROMPT.format(
        ticker=ticker,
        conference_name=conference_name,
        event_date=event_date,
        ingestion_date=ingestion_date,
        source_url=source_url,
    )

    logging.info("Calling Gemini 2.5 Pro on %s ...", url)
    logging.info("(Video processing typically takes 2-10 min for a ~100min keynote; be patient)")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(file_data=types.FileData(file_uri=url, mime_type="video/*")),
            ]
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned empty response")
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--url", required=True, help="YouTube URL of the keynote")
    ap.add_argument("--ticker", required=True, help="Primary public ticker (e.g., GOOGL)")
    ap.add_argument("--date", required=True, dest="event_date",
                    help="Event date in YYYY-MM-DD format (e.g., 2026-04-22)")
    ap.add_argument("--shortname", required=True,
                    help="Short slug for the filename (e.g., cloud-next, google-io)")
    ap.add_argument("--conference-name", required=True,
                    help='Full conference name for frontmatter (e.g., "Google Cloud Next 2026")')
    ap.add_argument("--force", action="store_true", help="Overwrite existing note if present")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    _setup_logging(args.verbose)

    # Validate date format
    try:
        dt = datetime.strptime(args.event_date, "%Y-%m-%d")
    except ValueError:
        logging.error("--date must be YYYY-MM-DD, got: %s", args.event_date)
        return 2
    yyyymmdd = dt.strftime("%Y%m%d")
    year = dt.year

    # Compute output path
    note_path = NOTES_ROOT / args.ticker / f"{yyyymmdd}-conf-{args.shortname}.md"
    if note_path.exists() and not args.force:
        logging.error("Note already exists: %s (use --force to overwrite)", note_path)
        return 3

    ingestion_date = datetime.now(timezone.utc).date().isoformat()

    # Call Gemini
    try:
        body = call_gemini(
            url=args.url,
            ticker=args.ticker,
            conference_name=args.conference_name,
            event_date=args.event_date,
            ingestion_date=ingestion_date,
            source_url=args.url,
        )
    except Exception as e:
        logging.error("Gemini call failed: %s: %s", type(e).__name__, e)
        return 4

    # Build frontmatter + body
    frontmatter = FRONTMATTER_TEMPLATE.format(
        ticker=args.ticker,
        event_date=args.event_date,
        year=year,
        conference_name=args.conference_name,
        ingestion_date=ingestion_date,
        source_url=args.url,
    )
    content = frontmatter + body + "\n"

    # Atomic write
    try:
        _write_note_atomic(note_path, content)
    except Exception as e:
        logging.error("Failed to write %s: %s", note_path, e)
        return 5

    logging.info("Wrote: %s", note_path)
    logging.info("Body size: %d chars", len(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
