"""
Document metadata schema for the research intelligence system.

Two-layer metadata model:
1. Doc-level: JSON sidecar next to each source file
2. Note-level: YAML frontmatter in generated notes
3. Central index: config/document-index.jsonl (one line per ingested doc)

DocMetadata is the canonical model. All extractors produce DocMetadata instances;
all consumers (agents, sync scripts, indexes) read DocMetadata instances.
"""

from __future__ import annotations
from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocType(str, Enum):
    EARNINGS_TRANSCRIPT = "earnings_transcript"
    CONFERENCE_TRANSCRIPT = "conference_transcript"
    SELL_SIDE_NOTE = "sell_side_note"
    SUBSTACK_POST = "substack_post"
    PODCAST_TRANSCRIPT = "podcast_transcript"
    SEC_FILING = "sec_filing"
    OPERATOR_NOTE = "operator_note"
    OTHER = "other"


class SourceOrigin(str, Enum):
    GMAIL_POLLER = "gmail_poller"
    MANUAL_UPLOAD = "manual_upload"
    FACTSET_API = "factset_api"
    INSIDERSCORE_API = "insiderscore_api"
    WEB_CLIPPER = "web_clipper"
    PODCAST_PIPELINE = "podcast_pipeline"
    OTHER = "other"


class ReportType(str, Enum):
    INITIATION = "initiation"
    UPDATE = "update"
    DEEP_DIVE = "deep_dive"
    POST_EARNINGS = "post_earnings"
    SECTOR_REPORT = "sector_report"
    OTHER = "other"


class InternalExternal(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class DocMetadata(BaseModel):
    """Canonical metadata for any source document in the research system."""

    model_config = ConfigDict(extra="forbid")

    # Required common fields
    doc_id: str = Field(..., description="SHA256 of source content; primary key")
    doc_type: DocType
    source_file_path: str = Field(..., description="Absolute path on droplet")
    source_origin: SourceOrigin
    ingestion_date: date = Field(..., description="When we processed this doc")

    # Optional common fields
    primary_ticker: Optional[str] = Field(None, description="Main focus, e.g. GOOGL")
    subject_tickers: List[str] = Field(default_factory=list, description="All tickers covered")
    event_date: Optional[date] = Field(None, description="When event happened")
    year: Optional[int] = None
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[str] = Field(None, description="e.g. 1Q26")
    quarter: Optional[str] = Field(None, description="e.g. Q1 26 (apostrophe-free)")
    total_pages: Optional[int] = None
    word_count: Optional[int] = None
    language: str = "en"
    internal_vs_external: Optional[InternalExternal] = None
    tags: List[str] = Field(default_factory=list)

    # Earnings / conference fields
    transcript_provider: Optional[str] = Field(None, description="factset, insiderscore, ai_whisper, etc.")
    speakers: List[str] = Field(default_factory=list)
    conference_name: Optional[str] = None
    sponsor_firm: Optional[str] = None
    host_firm: Optional[str] = None
    moderator: Optional[str] = None

    # Sell-side fields
    analyst_firm: Optional[str] = None
    lead_analyst: Optional[str] = None
    co_analysts: List[str] = Field(default_factory=list)
    rating: Optional[str] = None
    prior_rating: Optional[str] = None
    price_target: Optional[float] = None
    prior_price_target: Optional[float] = None
    report_type: Optional[ReportType] = None
    section_titles: List[str] = Field(default_factory=list)

    # Substack / blog fields
    publication_name: Optional[str] = None
    author: Optional[str] = None
    post_url: Optional[str] = None
    is_paid: Optional[bool] = None

    # Podcast fields
    podcast_name: Optional[str] = None
    episode_title: Optional[str] = None
    episode_number: Optional[int] = None
    hosts: List[str] = Field(default_factory=list)
    guests: List[str] = Field(default_factory=list)
    duration_minutes: Optional[float] = None
    transcript_source: Optional[str] = None

    # SEC filing fields
    sec_form_type: Optional[str] = None
    accession_number: Optional[str] = None
    filer_cik: Optional[str] = None
    filing_date: Optional[date] = None
    period_end_date: Optional[date] = None
