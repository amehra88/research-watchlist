#!/usr/bin/env python3
"""
Prototype note chunker — Store A (narrative) ingestion.

Implements the design in docs/chunking-strategy.md for the highest-value
source type first: section-structured markdown notes (operator_note /
earnings_transcript reads), with first-class handling of the
"## 8. Management Q&A flags" section as Q&A-item chunks.

Produces parent + child chunks (parent-child / auto-merge retrieval) carrying
the three-axis metadata:
  - Axis 1 (physical): section / Q&A-item / theme-block boundaries
  - Axis 2 (facet):    enum-validated, <=4 per chunk            [HEURISTIC here]
  - Axis 3 (theme):    watchlist themes                          [HEURISTIC here]
plus claim_source + time_orientation (the two fields the operator endorsed).

The facet / theme / claim_source / time_orientation taggers here are HEURISTIC
stand-ins so the prototype runs with no LLM. In production these are one
StructuredOutput call per chunk, wired into enrich_sidecars.py. The swap-in
point is tag_chunk() — replace its body, keep its signature.

Usage:
    python3 scripts/chunking/chunker.py notes/NVDA/20260521-1Q27.md
    python3 scripts/chunking/chunker.py notes/NVDA/20260521-1Q27.md --out chunks.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys

import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Controlled enum (mirror of docs/chunking-strategy.md §4, top-level keys).
# Heuristic tagger maps regex cues -> these. Production validates against this.
# ---------------------------------------------------------------------------
FACETS = [
    "supply_chain", "competitive_advantage", "product", "revenue", "market",
    "margins", "fcf", "capital_allocation", "risks", "guidance",
    "operating_kpis", "regulatory_geopolitical", "demand_signals",
    "capital_structure", "management",
]

# regex cue -> facet. Order does not matter; all matches collected then capped.
_FACET_CUES = {
    "margins": r"\bmargin|gross margin|operating margin|ebitda|incremental|basis points|bps\b",
    # incl. contracted/forward revenue signals (ARR, backlog, RPO, deferred
    # revenue, net-new ARR) per operator request — these also carry operating_kpis
    # (multi-label): they are a revenue signal AND a leading indicator. NOTE: this
    # deliberately groups GAAP-recognized revenue with contracted-but-unrecognized
    # balances; a "what was revenue" query can now surface a backlog/RPO chunk.
    "revenue": r"\brevenue|top-?line|yoy|qoq|sequential|grew|growth|"
               r"\barrs?\b|backlog|deferred revenue|remaining performance obligation|net new arr\b",
    "guidance": r"\bguid(e|ance)|outlook|expect|we (will|aim)|next quarter|full[- ]year|FY2\d|±|going forward\b",
    "fcf": r"\bfree cash flow|\bfcf\b|capex|capital expenditure\b",
    "capital_allocation": r"\bbuyback|repurchase|dividend|authoriz|capital return|\bm&a\b|acquisition|debt paydown\b",
    "competitive_advantage": r"\bmarket share|\bshare\b|moat|competit|merchant silicon|\basic\b|displace\b",
    "supply_chain": r"\bcustomer|vendor|supplier|hyperscaler|foundry|tsmc|partner|ecosystem\b",
    "market": r"\btam\b|addressable market|market (growth|dynamic)|substitution|demand environment\b",
    "product": r"\bproduct|roadmap|launch|\bramp\b|platform|next-?gen|cadence|blackwell|rubin|vera\b",
    "operating_kpis": r"\barr\b|\brpo\b|bookings|attach|take[- ]rate|\basp\b|\bdau\b|\bmau\b|backlog|"
                      r"\bkpis?\b|submarket|new segment|segment disclosure|segmentation|leading indicator\b",
    "risks": r"\brisk|headwind|overhang|concern|caveat|deterioration\b",
    "regulatory_geopolitical": r"\bexport control|china|antitrust|regulat|tariff|sovereign|import permit\b",
    "demand_signals": r"\bdemand|sales cycle|budget|pipeline|order fulfillment\b",
    "capital_structure": r"\bleverage|liquidity|debt maturit|balance sheet\b",
    "management": r"\bhuang|kress|\bceo\b|\bcfo\b|management|executive\b",
}

# theme cues -> watchlist theme slugs (subset; production reads watchlist.yaml)
_THEME_CUES = {
    "hyperscaler_capex_buildout": r"hyperscaler capex|ai infra(structure)? capex|data center capex",
    "silicon_architecture_competition": r"\basic\b|custom silicon|architecture|blackwell|rubin|vera|gpu|cpu socket",
    "china_export_controls": r"china|export control|h200|import permit",
    "inference_compute_economics": r"inference|token|cost-per-token|tokens? per",
    "frontier_model_competition": r"frontier model|anthropic|openai|grok",
}

# Per-company exec roster (prototype subset; production reads a roster file).
# Maps an answerer's surname -> role. The ANSWERER carries signal; the asker
# (analyst) does not, so there is no analyst roster on purpose.
EXEC_ROLES = {
    "Huang": "CEO", "Kress": "CFO", "Su": "CEO", "Tan": "CEO",
    "Narayen": "CEO", "Pichai": "CEO", "Nadella": "CEO", "Cook": "CEO",
    "Maddison": "IR", "Simmons": "IR",
}
EXEC_NAMES = tuple(EXEC_ROLES)

# answer-quality cues -> directness label (the alpha is in the RESPONSE).
_DIRECTNESS_CUES = [
    ("evasive",        r"deflect|dodge|declin|evasive|side-?stepped|tease|punted|non-?answer"),
    ("new_disclosure", r"new disclosure|first time|new segment|more substantive|disclosed for the first|net-new"),
    ("direct",         r"directly|direct (answer|rebuttal)|answered directly|clear(ly)? answer|more direct"),
    ("reiteration",    r"reiterat|unchanged|standard (execution|caveat)|same as|status quo|no (new |)flag"),
]


@dataclass
class Chunk:
    # --- identity / lineage ---
    chunk_id: str
    doc_id: str
    parent_id: Optional[str]
    kind: str                 # "parent" | "child"
    text: str
    # --- provenance / structural (inherited from doc) ---
    tickers: list             # PER-CHUNK ticker array (multi-ticker notes, §v3); [] for macro/sector
    doc_type: str
    event_date: Optional[str]
    fiscal_quarter: Optional[str]
    section: Optional[str]
    speaker: Optional[str] = None        # prepared-remarks speaker; None for Q&A
    speaker_role: Optional[str] = None
    # --- Q&A: the ANSWERER is first-class; the asker is non-ranking citation ---
    answered_by: Optional[str] = None    # exec who responded (signal)
    answerer_role: Optional[str] = None  # CEO | CFO | COO | IR (signal)
    answer_directness: Optional[str] = None  # direct | evasive | new_disclosure | reiteration
    asker_citation: Optional[str] = None # e.g. "Reitzes (Melius)" — citation ONLY, nothing ranks on it
    # --- operator-endorsed fields ---
    claim_source: str = "operator_opinion"
    time_orientation: str = "current"
    # --- Axis 2 + Axis 3 ---
    facets: list = field(default_factory=list)
    themes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Doc-level metadata from filename + first line (mirrors metadata/extract_*).
# ---------------------------------------------------------------------------
def _norm_role(title: str) -> str:
    """FactSet speaker title -> short role tag (CEO/CFO/CBO/COO/CTO/IR)."""
    t = (title or "").lower()
    for needle, role in (("chief executive", "CEO"), ("chief financial", "CFO"),
                         ("chief business", "CBO"), ("chief operating", "COO"),
                         ("chief technology", "CTO")):
        if needle in t:
            return role
    if "investor relations" in t:
        return "IR"
    return (title or "").split("&")[0].strip()[:24] or "exec"


def _parse_frontmatter(text: str) -> dict:
    """The note's YAML frontmatter as a dict ({} if absent/malformed)."""
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return {}
    try:
        return yaml.safe_load(fm.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _parse_roster(text: str) -> dict:
    """Per-doc {last_name: role} from the note's YAML `speakers:` frontmatter.
    Generalizes answerer-role lookup beyond the hardcoded global EXEC_ROLES so a
    new ticker's CFO/CBO resolve without editing code (step 3b)."""
    meta = _parse_frontmatter(text)
    roster = {}
    for sp in (meta.get("speakers") or []):
        # Tolerate a malformed `speakers:` entry that is a bare string rather
        # than a {name, role} mapping (real case: NVDA conf-analyst-meeting
        # note) — skip it instead of crashing the whole-corpus ingest.
        if not isinstance(sp, dict):
            continue
        name = (sp.get("name") or "").strip()
        if name:
            roster[name.split()[-1]] = _norm_role(sp.get("role", ""))
    return roster


def parse_doc_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    doc_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
    fm = _parse_frontmatter(text)
    parts = path.parts
    # base_ticker drives ONLY the chunk_id prefix (kept separate from `tickers`
    # so legacy IDs stay byte-identical); `tickers` is the retrieval array.
    base_ticker = parts[parts.index("notes") + 1] if "notes" in parts else None
    if base_ticker in ("sector",):
        base_ticker = None  # sector notes are multi-ticker; assigned per-segment downstream
    # -? makes the inner date separators optional: matches legacy 20260521-… AND
    # ISO-dashed 2026-05-21-… filenames (CKPT C; verified non-regressive corpus-wide).
    m = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})-(.+)\.md$", path.name)
    event_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
    tail = m.group(4) if m else ""
    fq = None
    qm = re.search(r"([1-4]Q\d{2})", tail)
    if qm:
        fq = qm.group(1)
    # tickers: frontmatter `tickers:` is canonical (multi-ticker; may be []);
    # absent -> [base_ticker] (legacy single-ticker note path -> ['NVDA']).
    if "tickers" in fm:
        tickers = [t for t in (fm.get("tickers") or []) if t]
    else:
        tickers = [base_ticker] if base_ticker else []
    themes = list(fm.get("themes") or []) if "themes" in fm else []  # union'd per-chunk
    doc_type = fm.get("doc_type") or (                               # FM wins, else heuristic
        "earnings_transcript" if fq else
        "conference_transcript" if "conf" in tail else "operator_note")
    return dict(doc_id=doc_id, tickers=tickers, base_ticker=base_ticker,
                event_date=event_date, fiscal_quarter=fq, doc_type=doc_type,
                themes=themes, text=text, roster=_parse_roster(text))


# ---------------------------------------------------------------------------
# HEURISTIC tagger — PRODUCTION SWAP POINT.
# Replace body with a StructuredOutput LLM call; keep the signature.
# ---------------------------------------------------------------------------
def tag_chunk(text: str, *, section: str, doc_type: str,
              idf: Optional[dict] = None, exec_names: tuple = EXEC_NAMES) -> dict:
    low = text.lower()

    # Rank facets by tf*idf, then cap at 4 (docs §11). Ranking by raw cue-COUNT
    # (the old behaviour) let high-frequency boilerplate (revenue, supply_chain)
    # crowd out the rare, discriminating facet the query keys on (e.g. `market`
    # from a single "TAM"), and broke count-ties on dict-insertion order. Weight
    # each facet's term-frequency by its inverse document frequency across the
    # note's chunks so rarity wins; break remaining ties alphabetically (stable,
    # non-arbitrary). idf=None (e.g. ad-hoc single-chunk calls) falls back to
    # tf-only with the same deterministic tie-break.
    tf = {f: len(re.findall(pat, low, re.I)) for f, pat in _FACET_CUES.items()}
    matched = [(f, n) for f, n in tf.items() if n]
    matched.sort(key=lambda fn: (-(fn[1] * (idf or {}).get(fn[0], 1.0)), fn[0]))
    facets = [f for f, _ in matched[:4]]

    themes = [t for t, pat in _THEME_CUES.items() if re.search(pat, low, re.I)]

    # claim_source: operator notes are operator synthesis by default; upgrade to
    # management when a direct exec quote/attribution is present; analyst_question
    # when the segment is an analyst asking (Q&A-flag items name the analyst+firm).
    claim_source = "operator_opinion" if doc_type == "operator_note" else "media"
    if re.search(r"\b(analyst|asked|question)\b", low) and re.search(
            r"\((melius|cantor|ubs|bofa|bernstein|goldman|cowen|morgan stanley|"
            r"jpmorgan|barclays|citi|wells|evercore|melius)\)", low):
        claim_source = "analyst_question"
    if any(n.lower() in low for n in exec_names) and (
            '"' in text or "answered" in low or "guided" in low or "said" in low):
        claim_source = "management"

    # time_orientation: forward cues win; else backward if past-tense result cues.
    if re.search(r"\bguid(e|ance|ed)|expect|will|outlook|next quarter|"
                 r"full[- ]year|FY2\d|going forward|ramp Q[1-4]|beyond\b", low):
        time_orientation = "forward"
    elif re.search(r"\bgrew|reported|print|actual|last 12 months|"
                   r"\+\d+% yoy|was \$|came in\b", low):
        time_orientation = "backward"
    else:
        time_orientation = "current"

    return dict(facets=facets, themes=themes,
                claim_source=claim_source, time_orientation=time_orientation)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


# ---------------------------------------------------------------------------
# Chunking: split note into ## sections (parents) and atomic children.
# ---------------------------------------------------------------------------
def _compute_idf(texts: list[str]) -> dict:
    """Smoothed IDF per facet across the note's own chunks: facets that match
    nearly every chunk (revenue, supply_chain) get ~1; rare ones (market,
    operating_kpis) get a high weight so they survive the <=4 cap. Single-doc df
    is a heuristic stand-in — the production LLM tagger (docs §8) replaces it,
    and a multi-note corpus df would be the better long-term signal."""
    n = len(texts) or 1
    df = {f: 0 for f in _FACET_CUES}
    for t in texts:
        low = t.lower()
        for f, pat in _FACET_CUES.items():
            if re.search(pat, low, re.I):
                df[f] += 1
    return {f: math.log((n + 1) / (df[f] + 1)) + 1 for f in _FACET_CUES}


def _detect_sections(lines: list[str]) -> re.Pattern:
    """Pick the section delimiter: the FIRST of ## / ### / full-line **bold**
    that is PRESENT in the doc wins (CKPT D cascade). All 62 legacy notes use
    ##, so they are unaffected (identical sections); podcast/external notes that
    lack ## fall through to ### or bold so they still split into sections."""
    for pat in (r"^##\s+(.*)$", r"^###\s+(.*)$", r"^\*\*(.+?)\*\*\s*$"):
        rx = re.compile(pat)
        if any(rx.match(ln) for ln in lines):
            return rx
    return re.compile(r"^##\s+(.*)$")  # harmless default (matches nothing -> 0 sections)


def chunk_note(path: Path) -> list[Chunk]:
    meta = parse_doc_meta(path)
    lines = meta["text"].splitlines()
    base = f"{meta['base_ticker'] or 'SECTOR'}-{meta['fiscal_quarter'] or _slug(path.stem)}"
    # Per-doc roster (from the note's `speakers:` frontmatter) augments the
    # hardcoded global EXEC_ROLES so a new ticker's CFO/CBO resolve as answerers
    # without a code edit; the global dict remains the fallback (step 3b).
    roster = {**EXEC_ROLES, **meta["roster"]}
    exec_names = tuple(roster)
    chunks: list[Chunk] = []

    # split into sections — cascade ## -> ### -> full-line **bold** (CKPT D).
    section_rx = _detect_sections(lines)
    sections: list[tuple[str, list[str]]] = []
    cur_title, cur_body = None, []
    for ln in lines:
        h = section_rx.match(ln)
        if h:
            if cur_title is not None:
                sections.append((cur_title, cur_body))
            cur_title, cur_body = h.group(1).strip(), []
        elif cur_title is not None:
            cur_body.append(ln)
    if cur_title is not None:
        sections.append((cur_title, cur_body))

    # Pass 1: enumerate every parent + child unit WITHOUT tags. The <=4-facet
    # cap is IDF-weighted, so a chunk's tags depend on the whole note's facet
    # distribution — we need all units before tagging any.
    units: list[dict] = []
    for title, body in sections:
        sec_slug = _slug(title)
        parent_id = f"{base}-{sec_slug}"
        body_text = "\n".join(body).strip()
        if not body_text:
            continue
        units.append(dict(kind="parent", chunk_id=parent_id, parent_id=None,
                          text=body_text, section=title, child=None))
        # children: split by the section's grammar
        for i, child in enumerate(_split_children(title, body, roster), 1):
            ctext = child["text"].strip()
            if len(ctext) < 25:
                continue
            units.append(dict(kind="child", chunk_id=f"{parent_id}-{i:02d}",
                              parent_id=parent_id, text=ctext, section=title,
                              child=child))

    idf = _compute_idf([u["text"] for u in units])

    # Pass 2: tag (IDF-aware) + construct.
    for u in units:
        tags = tag_chunk(u["text"], section=u["section"],
                         doc_type=meta["doc_type"], idf=idf, exec_names=exec_names)
        # Axis 3: union doc-level frontmatter themes with the per-chunk heuristic
        # themes (FM first, dedup, order-preserving). Legacy notes carry no FM
        # themes -> no-op -> byte-identical to today.
        tags["themes"] = list(dict.fromkeys(list(meta["themes"]) + list(tags.get("themes", []))))
        child = u["child"] or {}
        chunks.append(Chunk(
            chunk_id=u["chunk_id"], doc_id=meta["doc_id"], parent_id=u["parent_id"],
            kind=u["kind"], text=u["text"], tickers=meta["tickers"],
            doc_type=meta["doc_type"], event_date=meta["event_date"],
            fiscal_quarter=meta["fiscal_quarter"], section=u["section"],
            speaker=child.get("speaker"), speaker_role=child.get("speaker_role"),
            answered_by=child.get("answered_by"),
            answerer_role=child.get("answerer_role"),
            answer_directness=child.get("answer_directness"),
            asker_citation=child.get("asker_citation"),
            **tags))
    return chunks


def _directness(text: str) -> Optional[str]:
    low = text.lower()
    for label, pat in _DIRECTNESS_CUES:
        if re.search(pat, low):
            return label
    return None


def _split_children(title: str, body: list[str], roster: dict = None) -> list[dict]:
    """Return one dict per atomic child, by section grammar.

    For Q&A items the ANSWERER (exec who responded) + answer_directness are the
    signal; the asker (analyst/firm) is captured only as a non-ranking citation.
    `roster` is the per-doc {last_name: role} map (frontmatter ∪ global); falls
    back to the global EXEC_ROLES when not supplied.
    """
    roster = roster or EXEC_ROLES
    text = "\n".join(body)

    # Q&A flags: numbered items -> one chunk each. Center the answerer.
    if re.search(r"q&a", title, re.I):
        out = []
        for it in re.split(r"\n(?=\d+\.\s)", text):
            it = it.strip()
            if not it:
                continue
            # asker = analyst (Firm) — citation only, nothing ranks on it
            firm = re.search(r"\*\*([A-Z][a-zA-Z'-]+)\s*\(([^)]+)\)", it)
            asker_citation = f"{firm.group(1)} ({firm.group(2)})" if firm else None
            # answerer = first named exec in the item (the signal)
            exec_m = re.search(r"\b(" + "|".join(map(re.escape, roster)) + r")\b", it)
            answered_by = exec_m.group(1) if exec_m else None
            out.append(dict(
                text=it,
                answered_by=answered_by,
                answerer_role=roster.get(answered_by),
                answer_directness=_directness(it),
                asker_citation=asker_citation,
            ))
        return out

    # Theme blocks (### subheaders) -> one chunk each.
    if re.search(r"thesis read", title, re.I):
        return [dict(text=b.strip())
                for b in re.split(r"\n(?=###\s)", text) if b.strip()]

    # Default: bullet points and paragraphs.
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if re.match(r"^[-*]\s", para) or "\n- " in para:
            for b in re.split(r"\n(?=[-*]\s)", para):
                if b.strip():
                    out.append(dict(text=b.strip()))
        else:
            out.append(dict(text=para))
    return out


def main():
    ap = argparse.ArgumentParser(description="Prototype note chunker (Store A).")
    ap.add_argument("note", type=Path, help="path to a notes/{TICKER}/*.md file")
    ap.add_argument("--out", type=Path, help="write JSONL here (default: stdout summary)")
    args = ap.parse_args()

    if not args.note.exists():
        sys.exit(f"no such note: {args.note}")
    chunks = chunk_note(args.note)

    if args.out:
        with args.out.open("w", encoding="utf-8") as fh:
            for c in chunks:
                fh.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
        print(f"wrote {len(chunks)} chunks -> {args.out}")
    else:
        parents = [c for c in chunks if c.kind == "parent"]
        children = [c for c in chunks if c.kind == "child"]
        print(f"{args.note.name}: {len(parents)} parents, {len(children)} children\n")
        for c in chunks:
            head = c.text.replace("\n", " ")[:80]
            tag = f"[{c.claim_source[:4]}/{c.time_orientation[:4]}]"
            facets = ",".join(c.facets) or "-"
            ans = (f" →{c.answered_by}/{c.answerer_role}"
                   f"({c.answer_directness or '?'})" if c.answered_by else "")
            indent = "  " if c.kind == "child" else ""
            print(f"{indent}{c.chunk_id}{ans} {tag} {facets}")
            print(f"{indent}    {head}…")


if __name__ == "__main__":
    main()
