---
doc_type: thesis
ticker: 000660.KS
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#000660.KS
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: hynix_nvda_primary_hbm3e_supplier
  statement: At scoring, SK Hynix was NVDA's primary HBM3E supplier.
  derived_from: 'ai_positioning: 5 — ''NVDA''s primary HBM3E supplier'''
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - NVDA 10-Q or supply-chain filing naming Samsung or Micron as a primary HBM3E source
  - NVDA press release announcing qualification of a second HBM3E supplier to a material
    volume share
  confirmed_by:
  - NVDA annual report or earnings transcript confirming SK Hynix as primary HBM3E
    supplier for shipping GPU products
  - SK Hynix earnings call citing NVDA as the dominant HBM3E customer destination
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hbm_ai_compute_bottleneck_holds
  statement: Conditions at scoring — HBM being the critical AI-compute memory bottleneck
    — still hold.
  derived_from: 'ai_positioning: 5 — ''HBM is the critical AI-compute memory bottleneck'''
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  - model_efficiency_evolution
  challenged_by:
  - A major AI accelerator program announced with a non-HBM primary memory architecture
  - A leading AI lab publishing an efficiency architecture that materially reduces
    per-accelerator HBM capacity requirements at comparable inference performance
  confirmed_by:
  - Next-generation GPU or custom AI accelerator from NVDA, AMD, or a hyperscaler
    launched with HBM as primary memory type
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hynix_first_to_market_hbm_gens
  statement: At scoring, SK Hynix had shipped each major HBM generation ahead of Samsung
    and Micron.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''first-to-market on HBM
    generations'''
  themes:
  - hbm_competitive_landscape
  - semiconductor_cycle
  challenged_by:
  - Samsung or Micron announcing a first customer shipment or design-win qualification
    of HBM4 before SK Hynix discloses a comparable HBM4 shipment
  confirmed_by:
  - SK Hynix press release or earnings disclosure of first HBM4 customer shipment
    predating comparable Samsung or Micron announcements
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hynix_hbm_share_beyond_nvda
  statement: At scoring, SK Hynix held leading HBM share across the broad memory customer
    base beyond NVDA.
  derived_from: 'competitive_advantage.distribution: 4 — ''leading HBM share locked
    in with NVDA plus a broad memory customer base'''
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - Third-party HBM market share data (e.g., TrendForce) showing Samsung or Micron
    overtaking SK Hynix in total HBM unit or revenue share
  - AMD or a hyperscaler custom-silicon program publicly disclosing Samsung or Micron
    as its primary HBM source
  confirmed_by:
  - Third-party HBM market share report placing SK Hynix above 50% of total HBM revenue
  - SK Hynix earnings disclosing HBM customer count or revenue mix consistent with
    multi-customer leadership
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: base_dram_commodity_pricing
  statement: At scoring, SK Hynix's non-HBM DRAM segments carried commodity-level
    pricing.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''base DRAM is partly
    commodity'''
  themes:
  - semiconductor_cycle
  challenged_by:
  - SK Hynix earnings disclosing a material ASP premium over spot DRAM pricing in
    standard DRAM segments
  - SK Hynix management citing differentiated pricing power in commodity DRAM on an
    earnings call
  confirmed_by:
  - SK Hynix quarterly earnings showing standard DRAM ASP in line with TrendForce
    or DRAMeXchange spot market pricing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: korea_listing_friction_unresolved
  statement: At scoring, no broadly accessible US-listed instrument eliminated Korea-listing
    access friction for SK Hynix for US investors.
  derived_from: 'potential_investor_interest.score: 4 — ''Korea-listing access friction
    for some US investors'''
  themes:
  - semiconductor_cycle
  challenged_by:
  - Launch of a registered US ADR program for SK Hynix
  - SEC registration of a US-listed instrument tracking 000660.KS directly
  confirmed_by:
  - SK Hynix IR confirming no active US ADR filing as of the check date
  - SEC Edgar search returning no registered ADR program for 000660.KS
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

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
