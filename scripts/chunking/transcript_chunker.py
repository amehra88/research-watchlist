#!/usr/bin/env python3
"""
Raw FactSet transcript chunker (advisor next-step #2).

The markdown note chunker (chunker.py) splits on `##` section headers — raw
FactSet "Formatted Report" transcripts have NO such structure. Their grammar:

  CORPORATE PARTICIPANTS  (roster: name + title)
  OTHER PARTICIPANTS      (analysts + firms)
  MANAGEMENT DISCUSSION SECTION   <- prepared remarks, by speaker turn
  QUESTION AND ANSWER SECTION     <- turns marked "Name Q" / "Name A"

Key wins this grammar hands us for free (vs the operator-note gloss):
  - Q&A turns are explicitly tagged Q vs A in the header line.
  - Each turn repeats the speaker's TITLE on the next line -> answerer_role is
    deterministic (no hardcoded exec dict, no roster join). Analyst turns show a
    FIRM instead of a title -> that's how we tell asker from answerer.
  - The ANSWER is verbatim and complete (claim_source=management), where the
    note only had the operator's one-line summary (claim_source=operator_opinion).
    These are linkable by (ticker, fiscal_quarter) — the corpus-dedup story (#3).

Produces the same Chunk schema as chunker.py, answerer-centric per the operator's
rule (who answers is signal; the asker is asker_citation only, never ranked).

Usage:
    python3 scripts/chunking/transcript_chunker.py \
        /root/research/raw-transcripts/processed/GOOGL-2025-10-29-3Q25.pdf
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Optional

import pdfplumber

from chunker import Chunk, tag_chunk, _directness, _slug

# repeated page furniture to drop (FactSet CallStreet boilerplate + page nums)
_BOIL = re.compile(
    r"^(1-877-FACTSET.*|.*Formatted Report.*|Total Pages.*|Copyright ©.*|"
    r"\d{1,3}|.*\bEarnings Call\b.*\d{4}.*|\(\w+\)|[A-Z][a-z]+, Inc\.|"
    r"\.{6,}|\s*)$")

_SECTION = ("MANAGEMENT DISCUSSION SECTION", "QUESTION AND ANSWER SECTION")


def role_from_title(line: str) -> Optional[str]:
    """Map a title line to a role. Returns None for analyst FIRM lines (no title)
    — that absence is exactly how we distinguish an answerer from an asker."""
    t = line.lower()
    if "chief executive" in t:                              return "CEO"
    if "chief financial" in t:                              return "CFO"
    if "chief operating" in t:                              return "COO"
    if "chief business" in t:                               return "CBO"
    if "chief technology" in t:                             return "CTO"
    if "investor relations" in t or t.startswith("head-"):  return "IR"
    if any(w in t for w in ("chief", "president", "director", "officer", "founder")):
        return "EXEC"
    return None  # firm line (e.g. "Morgan Stanley & Co. LLC") -> asker, not answerer


def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join((pg.extract_text() or "") for pg in pdf.pages)


def _clean(text: str) -> list[str]:
    return [l.rstrip() for l in text.splitlines() if not _BOIL.match(l.strip())]


def _doc_meta(pdf_path: Path) -> dict:
    raw = pdf_path.read_bytes()
    m = re.match(r"([A-Z.]+)-(\d{4})-(\d{2})-(\d{2})-(.+)\.pdf$", pdf_path.name)
    ticker = m.group(1) if m else None
    event_date = f"{m.group(2)}-{m.group(3)}-{m.group(4)}" if m else None
    tail = m.group(5) if m else ""
    qm = re.search(r"([1-4]Q\d{2})", tail) or re.search(r"Q([1-4]).?(\d{2,4})", tail)
    fq = qm.group(1) if qm and qm.lastindex == 1 else None
    is_conf = "conf" in tail
    return dict(
        doc_id=hashlib.sha256(raw).hexdigest(), ticker=ticker,
        event_date=event_date, fiscal_quarter=fq,
        doc_type="conference_transcript" if is_conf else "earnings_transcript")


def _qa_turns(lines: list[str]):
    """Yield (name, qa_marker, title_or_firm, body) for each turn in the Q&A section."""
    # a turn header is a short line ending in ' Q' or ' A'
    hdr = re.compile(r"^([A-Z][\w.\-' ]{1,40}?) (Q|A)$")
    turns, i = [], 0
    while i < len(lines):
        m = hdr.match(lines[i].strip())
        if m and i + 1 < len(lines):
            name, qa = m.group(1).strip(), m.group(2)
            title = lines[i + 1].strip()
            body, j = [], i + 2
            while j < len(lines) and not hdr.match(lines[j].strip()):
                body.append(lines[j])
                j += 1
            turns.append((name, qa, title, "\n".join(body).strip()))
            i = j
        else:
            i += 1
    return turns


def chunk_transcript(pdf_path: Path) -> list[Chunk]:
    meta = _doc_meta(pdf_path)
    lines = _clean(extract_text(pdf_path))
    base = f"{meta['ticker']}-{meta['fiscal_quarter'] or _slug(pdf_path.stem)}"
    chunks: list[Chunk] = []

    # locate the Q&A section
    qa_start = next((i for i, l in enumerate(lines)
                     if l.strip() == "QUESTION AND ANSWER SECTION"), None)
    md_lines = lines[:qa_start] if qa_start is not None else lines
    qa_lines = lines[qa_start:] if qa_start is not None else []

    # ---- Q&A: group each analyst Q with the following management A turn(s) ----
    parent_id = f"{base}-qa"
    pair, n = [], 0
    turns = _qa_turns(qa_lines)

    def flush(pair):
        nonlocal n
        q = next((t for t in pair if t[1] == "Q"), None)
        answers = [t for t in pair if t[1] == "A"]
        if not answers:
            return
        n += 1
        asker = q[0] if q else None
        asker_firm = q[2] if q else None
        body = ""
        if q:
            body += f"Q ({asker}, {asker_firm}): {q[3]}\n\n"
        ans_by, ans_role = [], []
        for a in answers:
            r = role_from_title(a[2])
            ans_by.append(a[0]); ans_role.append(r or "EXEC")
            body += f"A — {a[0]} ({a[2]}): {a[3]}\n\n"
        body = body.strip()
        tags = tag_chunk(body, section="Q&A", doc_type=meta["doc_type"])
        tags["claim_source"] = "management"  # verbatim mgmt answer, not operator gloss
        chunks.append(Chunk(
            chunk_id=f"{parent_id}-{n:02d}", doc_id=meta["doc_id"],
            parent_id=parent_id, kind="child", text=body,
            tickers=[meta["ticker"]] if meta.get("ticker") else [], doc_type=meta["doc_type"],
            event_date=meta["event_date"], fiscal_quarter=meta["fiscal_quarter"],
            section="Q&A",
            answered_by=", ".join(ans_by) or None,
            answerer_role="/".join(dict.fromkeys(ans_role)) or None,
            answer_directness=_directness(body),
            asker_citation=(f"{asker} ({asker_firm})" if asker else None),
            **tags))

    for t in turns:
        if t[1] == "Q" and pair:           # a new question closes the prior pair
            flush(pair); pair = []
        pair.append(t)
    flush(pair)

    # ---- prepared remarks: one chunk per management speaker turn ----
    pr_parent = f"{base}-prepared"
    spk = re.compile(r"^([A-Z][\w.\-' ]{1,40})$")
    i, k = 0, 0
    while i < len(md_lines) - 1:
        line = md_lines[i].strip()
        title = md_lines[i + 1].strip()
        if spk.match(line) and role_from_title(title):  # mgmt speaker turn
            body, j = [], i + 2
            while j < len(md_lines) - 1:
                if spk.match(md_lines[j].strip()) and role_from_title(md_lines[j + 1].strip()):
                    break
                body.append(md_lines[j]); j += 1
            text = "\n".join(body).strip()
            if len(text) > 60:
                k += 1
                tags = tag_chunk(text, section="Prepared remarks", doc_type=meta["doc_type"])
                tags["claim_source"] = "management"
                chunks.append(Chunk(
                    chunk_id=f"{pr_parent}-{k:02d}", doc_id=meta["doc_id"],
                    parent_id=pr_parent, kind="child", text=text,
                    tickers=[meta["ticker"]] if meta.get("ticker") else [], doc_type=meta["doc_type"],
                    event_date=meta["event_date"], fiscal_quarter=meta["fiscal_quarter"],
                    section="Prepared remarks", speaker=line,
                    speaker_role=role_from_title(title), **tags))
            i = j
        else:
            i += 1
    return chunks


def main():
    ap = argparse.ArgumentParser(description="Raw FactSet transcript chunker.")
    ap.add_argument("pdf", type=Path)
    args = ap.parse_args()
    if not args.pdf.exists():
        sys.exit(f"no such pdf: {args.pdf}")
    chunks = chunk_transcript(args.pdf)
    qa = [c for c in chunks if c.section == "Q&A"]
    pr = [c for c in chunks if c.section == "Prepared remarks"]
    print(f"{args.pdf.name}: {len(pr)} prepared-remark turns, {len(qa)} Q&A pairs\n")
    for c in qa:
        ans = f"{c.answered_by}/{c.answerer_role}({c.answer_directness or '?'})"
        print(f"  {c.chunk_id}  →{ans}  facets={c.facets}")
        print(f"      asker(cite-only)={c.asker_citation}")
        print(f"      {c.text[:90].replace(chr(10),' ')}…")


if __name__ == "__main__":
    main()
