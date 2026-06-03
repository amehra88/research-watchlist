# Chunking & Retrieval Strategy (design)

_Status: DESIGN — not yet implemented. Drafted 2026-06-03._
_Owner: operator. Supersedes the "add a vector store at ~200 docs" placeholder in `research/docs/tech-team-memo-draft.md`._

## 0. Current state (what this replaces)

Today there is **no chunking pipeline**. Company notes (`notes/{TICKER}/*.md`) are git-tracked markdown, searched with `grep` and read **whole** by agents, selected by *freshness rank* (`MAX(event_date, ingestion_date)`). There is a doc-level metadata layer already — `DocMetadata` (`scripts/metadata/schema.py`) + `config/document-index.jsonl` — but nothing below the document.

This document specifies the layer below the document: how a note becomes retrievable *pieces*, and what each piece is tagged with.

## 1. Core principle: chunking ≠ faceting (three independent axes)

The analytical lenses the operator cares about (supply chain, margins, FCF, management…) are **not** a chunking strategy — they are a *faceting taxonomy*, the dimensions we retrieve **by**. One sentence in an earnings call routinely spans four of them:

> "Data-center revenue grew 154% as hyperscaler capex accelerated and we took share from merchant silicon, though gross margin compressed 200bps on the Blackwell ramp."
> → revenue + market + competitive-advantage + margins, in one breath.

Chunking *by* facet would force that sentence to be duplicated or arbitrarily filed. Instead:

- **Axis 1 — Chunk unit (physical):** split by the *grammar of the source* (Q&A pair, speaker turn, section).
- **Axis 2 — Facet (semantic label):** multi-label each chunk with the analytical taxonomy (§4).
- **Axis 3 — Theme (cross-company narrative):** the existing `watchlist.yaml` themes (`hyperscaler_capex_buildout`, `agent_framework_landscape`, …).

A query then composes all three: _"margin commentary [facet] tagged `hyperscaler_capex_buildout` [theme] from Q1'26 earnings [provenance] across the hyperscalers."_

## 2. Two stores, not one (the spine)

The facets the operator cares about most — revenue, margins, FCF, comps, **guidance-beat track record** — are **numbers**, and vector search is bad at numbers ("NVDA DC gross margin Q3'26 vs Q3'25" is a table lookup; an embedding returns the wrong quarter). So:

| | **Store A — narrative** | **Store B — structured metrics** |
|---|---|---|
| What | prose chunks: transcripts, podcasts, conf, operator notes | numbers, keyed `ticker × period × metric` |
| Holds | the *why* — framing, demand color, moat commentary | the *what* — actuals, consensus, guidance, beat/miss |
| Source | notes (this pipeline) | **FactSet** (`Fundamentals`, `EstimatesConsensus`, `Metrics`) + numbers extracted from notes |
| Retrieval | vector similarity + metadata filters | SQL / time-series lookup |

Both live in **one Postgres (pgvector)** so a `guidance` chunk in A can JOIN to B in a single query and the model sees *what they guided* (prose) **and** *their history of hitting it* (quant). This is the "RAG for narrative, SQL for numbers" pattern — the correct spine for an investing book. (Factor exposures, deferred, are also Store B machinery, not chunk facets.)

### 2a. Guidance-beat track record → a management-quality signal

In Store B, model guidance as a per-ticker time series: **guided range → consensus → actual → beat / miss / in-line + magnitude**, per quarter, per metric. Derive a **guidance-credibility score**: hit-rate, average beat magnitude, sandbag-vs-overpromise tendency. That score is attributable to the *management team* — so it is the quantitative bridge into the management dossier (§5). "Do these people sandbag?" is simultaneously a FactSet computation and a jockey signal. Mostly FactSet-sourced; worth the wiring.

## 3. Chunk units, by source type (Axis 1)

The boundary follows the grammar of the source. One size does **not** fit transcripts and podcasts.

| Source (`doc_type`) | Chunk unit | Notes |
|---|---|---|
| `earnings_transcript` — prepared remarks | topic-coherent paragraph, ~150–400 tok | scripted/dense; already topically segmented |
| `earnings_transcript` — Q&A | **one Q&A pair = one chunk** (analyst Q + full mgmt A) | highest-value chunk type. **Who answers is the signal; who asks is noise** — capture `answered_by`/`answerer_role` (CEO/CFO/IR) + `answer_directness`; the analyst-asker is `asker_citation` only, never ranked |
| `conference_transcript` | question→answer exchange | single moderator → clean turns |
| `podcast_transcript` | speaker-attributed **topic segment** | discursive; needs diarization (the `enrich_sidecars` Gemini pass already extracts speakers) |
| `operator_note` | **section-level** (the `##` headers) | already synthesized, high-signal, short — don't over-split |

### 3a. Parent–child (embed small, return large)

Match retrieval on the tight **atomic child** (a self-contained claim + its evidence, ~100–400 tok) for precision, but hand the LLM the **parent** (full Q&A pair / whole section / whole note) for context. LlamaIndex calls this auto-merging / parent-document retrieval. For a rambling multi-part analyst answer, the Q&A pair is the parent and the atomic sub-claims inside are children.

## 4. Facet taxonomy (Axis 2) — controlled enum

Multi-label, **validated against this enum** (StructuredOutput-style), **capped at ~3–4 facets/chunk** so the filter stays meaningful. Top-level → sub-facets:

1. `supply_chain` — customers, vendors, partners/ecosystem, channel, concentration
2. `competitive_advantage` — competition, market_share, moat (network_effects / switching_costs / scale / ip / brand / data)
3. `product` — momentum, leadership, roadmap, rnd_innovation, attach_crosssell
4. `revenue` — growth, comps, mix_segment, pricing, recurring_vs_onetime, backlog_rpo, retention_nrr_churn
5. `market` — tam, dynamics, substitution, growth, drivers
6. `margins` — operating, gaap_vs_nongaap, ebitda, incremental, gross, unit_economics
7. `fcf` — conversion, capex, growth
8. `capital_allocation` — buybacks, dividends, m_and_a, debt_paydown  _(split from FCF: "how much cash" vs "what they do with it")_
9. `risks` — regulatory, customer_concentration, tech_disruption, execution, macro_cyclical, key_person
10. `guidance` — forward outlook as a first-class facet (works with `time_orientation=forward` and the Store-B beat-rate join)
11. `operating_kpis` — leading indicators: arr, rpo, bookings, dau_mau, take_rate, attach_rate, asp, backlog
12. `regulatory_geopolitical` — export controls, antitrust, China policy (recurs across NVDA / GOOGL / BABA / BIDU / NTES)
13. `demand_signals` — qualitative: "elongated sales cycles", "budget scrutiny", "demand outstripping supply"
14. `capital_structure` — leverage, liquidity, debt maturities
15. `management` — commentary *this quarter*; biography lives in the dossier (§5)
16. `factor_exposures` — **parked**; derived from holdings/returns (Store B), not extracted from notes

## 5. Management — its own entity (defer build, fix schema now)

The operator weights the jockey, not just the horse: track record, pedigree, and personal origin (immigrant, single parent, learning disability, hardship overcome in youth — a resilience/grit signal). This data is **near-static and biographical**, lives in podcasts/interviews/profiles (almost never in earnings chunks), so it does **not** belong in transient note chunks. Model it like the `.pvt` profiles: a per-person dossier `people/{slug}/_profile.md`, embedded once, cross-referenced from company notes.

Sub-facets: `track_record` (prior P&L outcomes, capital-allocation history), `pedigree` (education, prior roles), `founder_origin` (adversity/grit), `incentive_alignment` (ownership %, comp), `tenure_turnover`, `key_person_risk`. Source the origin signal from on-record interviews; tag `confidence: biographical`; keep every claim cited. **Bridge:** `track_record` ← the guidance-credibility score from Store B (§2a).

**Decision:** build the `people/` entity *later*; reserve the schema now so note-RAG isn't blocked.

## 6. Chunk metadata schema (all three axes)

Extends `DocMetadata` (every chunk carries its parent doc's identity). New chunk-level fields in **bold**.

```jsonc
{
  // --- identity / lineage ---
  "chunk_id": "NVDA-1Q27-qa-07",      // stable, deterministic
  "doc_id": "<sha256 of source doc>", // FK → DocMetadata / document-index.jsonl
  "parent_id": "NVDA-1Q27-qa-section",// FK → parent chunk (auto-merge target)
  "text": "...",

  // --- provenance / structural (mostly inherited from DocMetadata) ---
  "ticker": "NVDA",                   // PER-SEGMENT (see §7) — may differ from doc.primary_ticker
  "doc_type": "earnings_transcript",
  "event_date": "2026-05-21",
  "fiscal_quarter": "1Q27",
  "answered_by": "Colette Kress",    // exec who RESPONDED — first-class signal
  "answerer_role": "CFO",             // CEO | CFO | COO | IR
  "answer_directness": "direct",      // direct | partial | evasive — answer quality is the alpha
  "asker_citation": "Buchalter (Cowen)", // analyst who asked — provenance ONLY, never ranked/filtered/boosted
  "transcript_provider": "factset",

  // --- the two fields the operator specifically endorsed ---
  "claim_source": "management",       // management | analyst_question | operator_opinion | sell_side | media
  "time_orientation": "forward",      // backward | current | forward

  // --- Axis 2: facets (multi-label, enum-validated, ≤4) ---
  "facets": ["margins.gross", "guidance", "product.roadmap"],

  // --- Axis 3: themes (existing watchlist taxonomy) ---
  "themes": ["silicon_architecture_competition", "hyperscaler_capex_buildout"]
}
```

Two fields financial RAG lives or dies on:
- **`claim_source`** — never let management spin retrieve as ground truth; lets us weight/filter conviction. `operator_opinion` (the operator's own synthesis) is the highest-signal value.
- **`time_orientation`** — "what's the margin" (backward/current) must not return a guide (forward).
- **`answered_by` / `answer_directness`** — on Q&A chunks the asker carries no alpha; the *answerer* and *how directly they answer* do. A CFO directly quantifying a margin question vs. a CEO punting to the analyst day is exactly the signal to filter and weight on — and it feeds the management dossier's credibility thread (§2a, §5). The analyst-asker is `asker_citation`, retained for provenance but excluded from ranking, filtering, and boosting.

## 7. Retrieval-time behavior

- **Per-segment ticker / multi-ticker fan-out.** Podcasts and `sector/` notes name several companies. Assign `ticker` *per chunk segment* (allow a list) so one podcast fans out to each ticker's retrieval instead of being misfiled under `primary_ticker`.
- **Recency decay.** Carry the existing freshness-rank philosophy into ranking — a Q1'24 margin comment should not tie a Q1'26 one for "current trajectory."
- **Operator-opinion boost.** Retrieval-time boost for `claim_source = operator_opinion` so the operator's conviction dominates raw transcript.
- **Hybrid by default.** Facet/theme/provenance filters + vector similarity together (pgvector handles the relational filtering Chroma can't).

## 8. How tags get assigned

LLM-tag at ingestion — a natural extension of `enrich_sidecars.py` (which already runs Gemini for doc-level extraction). Per chunk, emit `facets` + `themes` + `claim_source` + `time_orientation` via a StructuredOutput call against the §4 enum. Operator notes are nearly free: the 10 section headers map to facets ~1:1. The prototype (`scripts/chunking/`) uses **heuristic** taggers as a stand-in so it runs without an LLM; the production swap-in point is marked in code.

## 9. Decisions (locked)

| Decision | Call |
|---|---|
| Granularity | atomic-claim **+ parent-child** |
| Facet assignment | LLM at ingestion; **enum-validated**, **≤4 facets/chunk** |
| Management dossiers | **defer build, reserve schema now** |
| Store | **pgvector** (hosts A + B + dossiers; enables the JOIN) |
| First prototype | **earnings Q&A chunker** — highest value, cleanest boundaries, exercises guidance + claim_source + time_orientation + beat-rate join on one source type |

## 10. Build order

1. ✅ This design doc.
2. ◻ Q&A / section chunker prototype + starter eval set (`scripts/chunking/`). _(in progress)_
3. ◻ Eval set → ~15–20 question→expected-chunk gold pairs (the usually-skipped step; the only way to know the chunker works).
4. ◻ pgvector schema for Store A + Store B; embedding + ingestion job.
5. ◻ Store B: FactSet guidance-beat time series + credibility score.
6. ◻ `people/` dossiers (deferred).
