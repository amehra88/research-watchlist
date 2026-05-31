"""Pydantic schema for LLM-extracted content metadata.

Fields here are populated by `extract_content.py` calling Gemini 2.5 Pro
against the PDF text. They layer on top of the structural fields already
populated by `extract_from_filename` (ticker, date, doc_type, etc.).

All fields are Optional so the model can return null when something can't
be determined from the document -- preferred over hallucination.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class Speaker(BaseModel):
    """A single participant in an earnings call or conference."""
    name: str = Field(..., description="Full name as it appears in the transcript")
    role: Optional[str] = Field(None, description="Title or role, e.g., 'CEO', 'CFO', 'Analyst'")
    company: Optional[str] = Field(None, description="Employer or affiliation, e.g., 'Alphabet', 'Morgan Stanley'")


class ExtractionOutput(BaseModel):
    """The full content-extraction payload returned by the LLM."""

    speakers: Optional[List[Speaker]] = Field(
        None,
        description=(
            "Company management/executives only (CEO, CFO, segment heads, IR head). "
            "Do NOT include sell-side analysts or 'Unverified Participant' entries."
        )
    )
    transcript_provider: Optional[str] = Field(
        None,
        description=(
            "The source/publisher of the transcript itself, e.g., 'Bloomberg', 'FactSet', "
            "'Motley Fool', 'InsiderScore', 'company IR'. Look for branding, "
            "boilerplate, or 'CORRECTED TRANSCRIPT' markers. Null if not determinable."
        )
    )
    sponsor_firm: Optional[str] = Field(
        None,
        description=(
            "For conference transcripts only: the sell-side firm hosting the conference "
            "(e.g., 'Morgan Stanley', 'Goldman Sachs'). Null for earnings calls."
        )
    )


# Convenience: the JSON schema dict for passing to Gemini's response_schema parameter
EXTRACTION_OUTPUT_SCHEMA = ExtractionOutput.model_json_schema()
