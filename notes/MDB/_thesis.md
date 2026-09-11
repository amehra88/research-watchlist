---
doc_type: thesis
ticker: MDB
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MDB
- notes/MDB/20260529-1Q27.md
- notes/MDB/20260902-2Q27.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: atlas_growth_at_candidacy
  statement: Atlas YoY revenue growth at approximately +29% (Q1 FY27, reported 2026-05-28)
    was a condition present when T2 candidacy was established on 2026-06-24 — a materially
    lower Atlas growth rate at Q2 FY27 would indicate that the growth rate observable
    at the time of addition was not present at Q2 FY27.
  derived_from: 'scoring_notes: Tier-2 candidate — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - Q2 FY27 8-K (filed 2026-09-01) disclosing Atlas YoY revenue growth materially
    below 25%
  - Q3 FY27 8-K disclosing Atlas YoY revenue growth materially below management's
    FY27 ~27% guide issued on 2026-09-01
  confirmed_by:
  - Q2 FY27 8-K disclosing Atlas YoY revenue growth at or above 27%
  - Q3 FY27 8-K disclosing Atlas YoY revenue growth at or above management's FY27
    ~27% Atlas guide
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 6.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: ai_memory_layer_not_displaced
  statement: MongoDB's role as a memory and state layer for AI agents — evidenced
    by LangChain integration, Vector Search with Voyage AI embeddings, and named Frontier
    Lab adoptions (Adobe, ElevenLabs, Endor Labs, Zomato) visible at the time of addition
    — was a condition present at T2 candidacy.
  derived_from: 'scoring_notes: Tier-2 candidate — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - Press release or 10-Q/10-K from Adobe, ElevenLabs, Endor Labs, or Zomato disclosing
    migration of AI agent workloads to an alternative vector or document store
  - LangChain press release designating a competing platform (pgvector, Pinecone,
    Weaviate) as its primary database integration
  - Q3 FY27 8-K or 10-Q disclosing a QoQ decline in Atlas Vector Search customer count
    or Atlas Vector Search workload revenue
  confirmed_by:
  - Q3 FY27 earnings call citing net-new Frontier Lab or AI-native enterprise customer
    wins on Atlas Vector Search
  - Press release or 8-K disclosing an expanded LangChain or Frontier Lab partnership
    with MongoDB
  status: open
  status_source: draft
  pressure:
    confirm: 19.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: mdb_not_bctk_held_at_addition
  statement: T2 candidacy at addition (2026-06-24) implies MDB was not held in the
    BCTK portfolio on that date — a buy execution on any date from 2026-06-24 onward
    would require a tier promotion to T1.
  derived_from: 'scoring_notes: Tier-2 candidate — ''Tier-2 candidate'''
  themes: []
  challenged_by:
  - BCTK portfolio buy record for MDB on any date from 2026-06-24 onward without a
    corresponding T1 promotion in watchlist.yaml
  confirmed_by:
  - MDB tier field in watchlist.yaml reading T2 or T3 with no buy record at the next
    portfolio review
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: q2fy27_is_scoring_trigger
  statement: '''Themes/scoring pending next earnings cycle'' (written 2026-06-24,
    after Q1 FY27 results) identified Q2 FY27 (reporting 2026-09-01) as the event
    enabling formal theme and score assignment — the Q2 FY27 8-K, 10-Q, and earnings-reviewer
    note now on file constitute the anticipated evidence set.'
  derived_from: 'scoring_notes: unscored — ''themes/scoring pending next earnings
    cycle'''
  themes: []
  challenged_by:
  - PM scoring notes updated after the 2026-09-02 Q2 FY27 note to again defer scoring
    to a subsequent earnings cycle without assigning any score values
  confirmed_by:
  - watchlist.yaml updated with MDB theme labels and score values (any non-empty SCORES
    field) referencing Q2 FY27 as the evidence basis
  - SCORE NOTES updated with explicit numeric scores following the earnings-reviewer
    note dated 2026-09-02
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `notes` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
