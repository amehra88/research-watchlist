---
doc_type: thesis
ticker: AVGO
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AVGO
- notes/AVGO/20260604-2Q26.md
- notes/AVGO/20260902-3Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: avgo_xpu_multi_hyperscaler_wins
  statement: AVGO holds active, multi-generation custom XPU design wins with at least
    three distinct hyperscaler or frontier-lab customers as the primary ASIC co-design
    partner — the factual basis the ai_positioning 5 requires.
  derived_from: 'ai_positioning: 5 — ''custom XPU/ASIC franchise (Google TPU co-design,
    Meta MTIA, plus the 2025 OpenAI custom-inference-silicon + networking commitment)
    anchoring hyperscaler captive silicon'''
  themes:
  - silicon_architecture_competition
  - hyperscaler_revenue_concentration
  challenged_by:
  - A named hyperscaler or frontier lab discloses in an 8-K, press release, or earnings
    call that its next-generation custom accelerator program is transitioning to a
    silicon partner other than AVGO
  confirmed_by:
  - A new multi-generation XPU supply agreement or design-win disclosure naming AVGO
    as co-design partner for a customer not previously named, filed as an 8-K or announced
    on an earnings call
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 17.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: avgo_ai_networking_material_leg
  statement: AI networking (Tomahawk/Jericho switching, optical DSPs) is a material
    contributor to AVGO's AI revenue base — not subordinate or incidental — as implied
    by the 'two legs' characterization in the ai_positioning 5 notes.
  derived_from: 'ai_positioning: 5 — ''AI networking (Tomahawk/Jericho switching,
    optical DSPs)... Top-tier AI beneficiary on two legs'''
  themes:
  - networking_competitive_landscape
  - ai_compute_topology
  challenged_by:
  - A named hyperscaler announces, in a filing or earnings call, that a competing
    Ethernet switching or optical fabric platform has been qualified as the primary
    AI cluster fabric, displacing AVGO switching
  confirmed_by:
  - AVGO discloses a new 100T or 200T Ethernet switching or CPO design win at a named
    hyperscaler, filed in an 8-K or announced on an earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: avgo_codesign_retains_successive_gens
  statement: AVGO's co-design integrator model — not frontier-architecture invention
    — is sufficient to retain existing XPU customers across at least two consecutive
    accelerator generations, which is the stated rationale for innovation_rate 4 rather
    than 3.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''elite custom-silicon
    + networking integrator/co-design house rather than a frontier-architecture inventor
    (vs NVDA 5)'''
  themes:
  - silicon_architecture_competition
  challenged_by:
  - A named existing XPU customer announces publicly that its next-generation accelerator
    was developed without AVGO co-design involvement, disclosed in a press release,
    filing, or the customer's own earnings call
  confirmed_by:
  - A next-generation XPU contract or design-win announcement names AVGO as co-design
    partner for a successive generation of an existing customer's accelerator program,
    filed or disclosed on an earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 5.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: avgo_google_2ndsrc_not_yet_material
  statement: As of the Q3'26 earnings note (2026-09-03), the Google second-sourcing
    risk acknowledged in the Q2'26 call has not resulted in a competing ASIC partner
    qualifying for AVGO's existing Google TPU-generation workloads — the condition
    the distribution 5 requires to hold at this score level.
  derived_from: 'competitive_advantage.distribution: 5 — ''deeply entrenched hyperscaler
    design wins''; Q2''26 note: ''Tan acknowledged Google may diversify sourcing ...
    the Google second-sourcing concession is the canonical drift-down trigger to watch;
    not yet material'''
  themes:
  - hyperscaler_revenue_concentration
  challenged_by:
  - Google discloses in a filing, press release, or its own earnings call that a second
    ASIC partner has qualified for the same TPU-generation workloads currently supplied
    by AVGO
  confirmed_by:
  - Google places an incremental purchase order or multi-year supply agreement with
    AVGO for a subsequent TPU generation, disclosed in an AVGO 8-K or earnings call
    prepared remarks
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: avgo_ai_semi_majority_of_segment
  statement: AI semiconductor revenue constitutes a majority of AVGO's semiconductor
    solutions segment revenue, per the 'dominant share of semiconductor segment' characterization,
    with the Q4'26 guide implying ~$21.7B AI semi against ~$26.1B total semiconductor
    solutions (~83%).
  derived_from: 'ai_positioning: 5 — ''AI revenue scaling toward a dominant share
    of semiconductor segment''; Q3''26 note: ''AI semi $16.7B (+221% y/y, +54% q/q,
    56% of total revenue); Q4 guided to $21.7B'''
  themes:
  - ai_infrastructure_capex
  - inference_compute_economics
  challenged_by:
  - Q4'26 AI semiconductor revenue reported in the 8-K Ex. 99.1 falls below $21.7B,
    or non-AI semiconductor revenue grows faster than guided such that AI semi's share
    of the semiconductor segment declines sequentially from Q3'26's reported level
  confirmed_by:
  - Q4'26 8-K Ex. 99.1 reports AI semiconductor revenue at or above $21.7B, maintaining
    AI semi as a majority of the semiconductor solutions segment
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 5.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
