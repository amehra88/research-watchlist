---
doc_type: thesis
ticker: MPWR
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MPWR
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: mpwr_nvda_supplier_at_scoring
  statement: MPWR held a qualified power-delivery supplier position with NVDA at the
    time of scoring; that status had not been displaced.
  derived_from: 'ai_positioning: 4 — "an NVDA power-delivery supplier"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - NVDA 10-K, supply-chain filing, or platform teardown names an alternative power-module
    vendor on the same GPU board generation
  - MPWR drops below the >10% customer disclosure threshold for NVDA in a subsequent
    10-K
  confirmed_by:
  - MPWR 10-K or 10-Q discloses NVDA as a >10% customer
  - Independent platform teardown identifies MPWR power-module SKUs on current NVDA
    GPU board
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ai_server_design_in_intact
  statement: MPWR had active design-ins on major AI-server platforms at scoring; no
    platform refresh had selected an alternative power-management vendor.
  derived_from: 'competitive_advantage.distribution: 4 — "designed into major AI-server
    platforms plus broad analog base"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - OEM or hyperscaler platform BOM for the next server generation publicly identifies
    a competing power-management vendor in MPWR's slot
  - MPWR data-center segment revenue declines sequentially while overall AI-server
    shipment volumes are flat or rising
  confirmed_by:
  - MPWR earnings call or investor presentation cites design-win count or design-in
    revenue on a named next-generation AI-server platform
  - System integrator or analyst teardown report identifies MPWR components on a newly
    released AI server SKU
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: nvda_concentration_caps_distribution
  statement: NVDA single-customer concentration was the binding constraint that prevented
    the distribution score from exceeding 4 at scoring; it had not been diversified
    away.
  derived_from: 'competitive_advantage.distribution: 4 — "carries single-customer
    concentration risk (NVDA)"'
  themes:
  - ai_infrastructure_capex
  - semiconductor_cycle
  challenged_by:
  - MPWR wins and publicly discloses design-ins with a second hyperscaler's custom
    AI-silicon program, reducing NVDA revenue share
  - NVDA falls below the material-customer disclosure threshold in a subsequent MPWR
    annual filing
  confirmed_by:
  - MPWR 10-K discloses NVDA as >10% customer for two consecutive annual periods post-scoring
  - MPWR management quantifies NVDA-related revenue as a majority of data-center segment
    on an earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ai_server_units_and_density_lever
  statement: AI-server unit volume and per-server power density — not AI software
    or model revenue — were the primary revenue levers for MPWR at scoring.
  derived_from: 'ai_positioning: 4 — "well-levered to AI-server unit growth and rising
    power density"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - MPWR data-center revenue diverges materially from publicly reported AI-server
    shipment unit trends for two consecutive quarters
  - MPWR management identifies a non-AI-server segment as the primary revenue growth
    driver on an earnings call
  confirmed_by:
  - MPWR segment or product-family revenue disclosure shows data-center growing as
    a share of total for two consecutive quarters
  - MPWR management explicitly ties revenue guidance to AI-server unit build forecasts
    on a quarterly earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: valuation_drag_investor_interest
  statement: Valuation was a drag on potential investor interest at scoring — it was
    cited as a limiting factor, not a neutral or positive attribute.
  derived_from: 'potential_investor_interest.score: 4 — "Valuation and single-customer
    (NVDA) concentration temper the score"'
  themes:
  - semiconductor_cycle
  - ai_infrastructure_capex
  challenged_by:
  - MPWR price-to-earnings or EV/Sales compresses to the median of publicly traded
    power-analog peers following a miss or guidance cut
  - Sell-side consensus price targets fall below MPWR's trailing-twelve-month average
    market price
  confirmed_by:
  - MPWR trades at a sustained premium greater than 1.5x the NTM P/E of publicly traded
    power-analog peers for two consecutive quarters post-scoring
  - MPWR investor-day or roadshow materials include a slide defending premium multiple
    via content-per-server growth
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
