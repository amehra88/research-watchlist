---
doc_type: thesis
ticker: SPCX
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#SPCX
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: starlink_rev_share_58pct_fy24
  statement: Starlink (Connectivity segment) constituted approximately 58% of SPCX
    total revenue in FY2024, making it the dominant segment by revenue at the time
    of scoring.
  derived_from: 'scoring_notes: (no numeric score set) — "Starlink (~58% of FY24 rev)"'
  themes:
  - space_economy
  challenged_by:
  - SPCX annual report or 10-K showing Connectivity segment below 50% of FY2024 total
    revenue
  - Restatement or prospectus amendment revising the FY2024 segment revenue split
    materially away from 58%
  confirmed_by:
  - SPCX 10-K or S-1/A filing disclosing Connectivity segment revenue at or near 58%
    of FY2024 consolidated revenue
  - Q2 2026 10-Q trailing-twelve-month segment disclosure corroborating Connectivity
    as largest segment by revenue
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: cursor_merger_no_reg_block
  statement: As of scoring, no material regulatory obstacle to the Cursor/Anysphere
    merger closing had been publicly disclosed, consistent with the PM's instruction
    to incorporate Cursor into SPCX tracking upon close.
  derived_from: 'scoring_notes: (no numeric score set) — "fold Cursor in on close,
    no standalone .pvt"'
  themes:
  - frontier_model_competition
  - ai_infrastructure_capex
  challenged_by:
  - DOJ or FTC second request, complaint, or injunction filed against the Cursor merger
  - SPCX 8-K disclosing termination or indefinite postponement of the Cursor Merger
    Agreement
  confirmed_by:
  - SPCX 8-K filed with SEC announcing consummation of the Cursor merger
  - SPCX 10-Q balance sheet reflecting Anysphere goodwill and intangible assets as
    of a reporting period-end
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: orbital_dc_active_initiative
  statement: SPCX's orbital data center program was an active capital allocation initiative
    at the time of scoring — not abandoned, deferred, or reclassified as exploratory.
  derived_from: 'scoring_notes: (no numeric score set) — "planned orbital DCs"'
  themes:
  - space_economy
  - ai_infrastructure_capex
  challenged_by:
  - SPCX 10-Q, earnings call transcript, or press release withdrawing or indefinitely
    deferring orbital data center development
  - SPCX capex disclosure showing zero allocation to AI segment space infrastructure
    across two consecutive quarters
  confirmed_by:
  - SPCX capital expenditure line item or MD&A narrative referencing orbital or space-based
    AI infrastructure spend
  - Customer or government contract announcement naming SPCX as provider of orbital
    compute capacity
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

Drafted 2026-09-09 in mode `thin` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
