---
doc_type: thesis
ticker: CRDO
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#CRDO
- notes/CRDO/20260602-3Q26.md
- notes/CRDO/20260902-1Q27.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: aec_defacto_standard_intra_rack
  statement: At the time of the Q1 FY27 print, AEC held de facto standard status for
    AI intra-rack and short-reach rack-to-rack connectivity at major hyperscalers.
  derived_from: earnings note 3Q26 §4 networking_competitive_landscape — 'management
    defended AEC as the de facto standard for intra-rack and rack-to-rack connectivity
    up to 7 meters'
  themes: []
  challenged_by:
  - A hyperscaler publicly qualifies an optical module or CPO solution for intra-rack
    runs ≤7m in a design disclosure, RFP, or published rack architecture specification
  - NVIDIA discloses volume CPO deployment displacing copper in a current-generation
    AI cluster build in an investor or technical disclosure
  confirmed_by:
  - CRDO discloses a new AEC design win at a hyperscaler for a next-generation cluster
    without a copper-to-optical substitution noted in the disclosure
  - A hyperscaler publishes a rack architecture specification citing AEC as the sole
    short-reach interconnect for intra-rack runs
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: optical_primary_fy27_growth_engine
  statement: As of the Q1 FY27 earnings call, CRDO's optical segment (ZeroFlap / DustPhotonics)
    was the primary stated FY27 growth engine, with management explicitly framing
    AEC growth as decelerating.
  derived_from: earnings note 1Q27 §1 — 'the optical business it once framed as complementary
    to copper is now the primary growth engine (>$600M in FY27 across three $100M+
    segments), AEC growth is decelerating by management's own framing'
  themes: []
  challenged_by:
  - Q2 FY27 10-Q segment or product-line disclosure shows AEC revenue exceeding optical
    revenue in the quarter
  - Management restores AEC as the primary sequential growth driver on the Q2 FY27
    earnings call
  confirmed_by:
  - Management reconfirms the >$600M optical FY27 target and AEC deceleration framing
    on the Q2 FY27 earnings call
  - Q2 FY27 10-Q or product-line disclosure shows optical revenue tracking at or above
    the implied quarterly run-rate for a >$600M annual total
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: top2_hyperscaler_concentration_71pct
  statement: At the Q3 FY26 print, the two largest customers accounted for approximately
    71% of quarterly revenue (39% and 32% individually), making a single hyperscaler
    capex decision a material revenue swing factor.
  derived_from: earnings note 3Q26 §4 hyperscaler_revenue_concentration — 'the largest
    was 39%, second 32%, third 17% — i.e. ~88% of revenue in three accounts'
  themes: []
  challenged_by:
  - A subsequent 10-Q filing shows the single largest customer below 30% of quarterly
    revenue
  - A non-hyperscaler customer first exceeds 10% of quarterly revenue in a filed 10-Q
  confirmed_by:
  - Q2 FY27 10-Q shows the two largest customers accounting for 65% or more of quarterly
    revenue combined
  - Management discloses on the Q2 FY27 call that the largest customer again exceeded
    30% of quarterly revenue
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gaap_gm_gap_dustphotonics_amort
  statement: GAAP gross margin in Q1 FY27 (64.5%) ran approximately 350bp below the
    non-GAAP guided midpoint (68.0%), with the gap sourced in the Q1 FY27 10-Q to
    amortization of acquired intangible assets from the DustPhotonics acquisition.
  derived_from: earnings note 1Q27 §2 — 'GAAP gross margin runs ~350bp below the guided
    level all year'; MD&A — 'Gross margin...decreased...primarily driven by amortization
    of acquired intangible assets'
  themes: []
  challenged_by:
  - Q2 FY27 10-Q shows GAAP gross margin at 66% or higher, narrowing the gap to within
    100bp of the non-GAAP guided midpoint
  - Q2 FY27 10-Q purchase accounting note shows acquired-intangible amortization running
    through COGS at a materially lower rate than in Q1 FY27
  confirmed_by:
  - Q2 FY27 10-Q shows GAAP gross margin at or below 65%, with the purchase accounting
    note attributing the shortfall to DustPhotonics acquired-intangible amortization
  - DustPhotonics intangible amortization schedule disclosed in the Q1 FY27 10-Q implies
    a drag of 300bp or more persisting for at least three additional quarters
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: opex_above_guidance_q1fy27_rd
  statement: Non-GAAP operating expenses in Q1 FY27 rose 16% sequentially and exceeded
    the high end of management's own guidance, driven by R&D spending.
  derived_from: earnings note 1Q27 §2 — 'management disclosed that non-GAAP operating
    expenses rose 16% sequentially in Q1, above the high end of guidance, mainly due
    to increased R&D spending'
  themes: []
  challenged_by:
  - Q2 FY27 non-GAAP opex comes in at or below the midpoint of management's Q2 FY27
    guidance on the earnings call
  - Q2 FY27 10-Q shows R&D expense as a percentage of revenue declining quarter-over-quarter
  confirmed_by:
  - Q2 FY27 non-GAAP opex again exceeds the high end of management's Q2 FY27 guidance
  - Q2 FY27 10-Q shows R&D expense in dollar terms growing faster quarter-over-quarter
    than it did in Q1 FY27
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
