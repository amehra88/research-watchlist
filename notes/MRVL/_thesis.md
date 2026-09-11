---
doc_type: thesis
ticker: MRVL
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MRVL
- notes/MRVL/20260528-1Q27.md
- notes/MRVL/20260829-2Q27.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: 4+
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: celestial_ai_rev_guide_unimpaired
  statement: At scoring, no disclosed program failure, customer disengagement, or
    technology setback had impaired the basis for MRVL management's guide of a $500M
    Celestial AI Photonic Fabric quarterly run rate by Q4 FY28 and $1B by Q4 FY29.
  derived_from: 'competitive_advantage.innovation_rate: 4+ — "Trajectory toward 5
    if the photonic-fabric capability converts to MRVL-guided revenue at scale (Q4
    FY28: $500M run rate; Q4 FY29: $1B)"'
  themes:
  - silicon_architecture_competition
  - ai_compute_topology
  challenged_by:
  - MRVL earnings call or 8-K disclosing withdrawal or downward revision of the $500M
    Q4 FY28 / $1B Q4 FY29 Celestial AI Photonic Fabric revenue guide
  - Customer public disclosure of a competing optical memory disaggregation design
    selection displacing Celestial AI Photonic Fabric at a named hyperscaler
  confirmed_by:
  - MRVL Q3 or Q4 FY27 earnings call reaffirming the $500M Q4 FY28 / $1B Q4 FY29 Photonic
    Fabric guide without downward revision
  - MRVL segment or product-line disclosure of initial Celestial AI Photonic Fabric
    revenue consistent with the guided ramp slope
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: avgo_no_photonic_bundle_match
  statement: 'At scoring, AVGO had not publicly announced a competing optical-decoupled
    memory disaggregation product matching the Celestial AI Photonic Fabric''s three-capability
    bundle: physical compute-memory decoupling via optical signals, sub-150ns remote-memory
    latency, and pooled-memory economics eliminating per-server DRAM overprovisioning.'
  derived_from: 'competitive_advantage.innovation_rate: 4+ — "combining the three
    capabilities (physical decoupling + sub-150ns latency + pooled-memory economics)
    gives MRVL a moat dimension AVGO does not obviously match"'
  themes:
  - silicon_architecture_competition
  - ai_compute_topology
  challenged_by:
  - AVGO product announcement, investor-day slide deck, or verified industry teardown
    describing an optical memory disaggregation solution with latency specifications
    at or below 150ns
  - AVGO acquisition of a company whose primary product is optical compute-memory
    decoupling
  confirmed_by:
  - AVGO interconnect product roadmap filings and investor-day disclosures through
    the scoring date contain no announced optical memory disaggregation capability
    with a sub-150ns latency specification
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: custom_xpu_10b_fy29_no_cancellation
  statement: At scoring, no disclosed hyperscaler customer cancellation, second-source
    qualification of a competing custom XPU vendor, or formal guidance withdrawal
    had impaired the basis for MRVL's $10B+ custom XPU FY29 revenue guidance across
    more than 50 active custom opportunities.
  derived_from: 'ai_positioning: 4 — "custom XPU ($10B+ FY29 line of sight on a $55B
    TAM)"; competitive_advantage.overall: 4 — "the moat compounds in design wins but
    is renewed every cycle"'
  themes:
  - silicon_architecture_competition
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - MRVL earnings commentary disclosing active custom opportunities falling below
    50 or formal withdrawal of the $10B FY29 guidance
  - Named hyperscaler public announcement of a second-source custom XPU qualification
    with a vendor other than MRVL or AVGO for a program previously attributed to MRVL
  confirmed_by:
  - MRVL reaffirms or raises the $10B FY29 custom XPU guide in a subsequent earnings
    call or investor event with an active-opportunity count at or above 50
  status: open
  status_source: draft
  pressure:
    confirm: 5.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: nvda_partnership_not_terminated
  statement: At scoring, the NVDA NVLink Fusion co-integration partnership and the
    $2B NVDA equity investment in MRVL (disclosed 2026-03-31) had not been formally
    terminated or materially amended.
  derived_from: 'competitive_advantage.distribution: 4 — "NVIDIA NVLink Fusion partnership
    plus a $2B NVDA equity investment in MRVL (partnership + investment announced
    2026-03-31)"'
  themes:
  - silicon_architecture_competition
  - networking_competitive_landscape
  challenged_by:
  - SEC filing, NVDA press release, or MRVL 8-K disclosing termination or material
    amendment of the NVLink Fusion co-integration agreement
  - NVDA Schedule 13F or Form 4 showing full or majority liquidation of the $2B MRVL
    equity position
  confirmed_by:
  - MRVL 10-Q or 10-K confirming the NVDA equity position and NVLink Fusion co-development
    as active
  - Joint NVDA-MRVL product milestone announcement executed under the NVLink Fusion
    co-integration framework
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: google_warrant_no_exclusivity_clause
  statement: At scoring, the Google warrant agreement (8-K 2026-08-19, 240 tranches
    vesting per $500M of Custom Products revenue through FY2033) did not impose exclusivity
    or customer-exclusion obligations on MRVL as a vesting condition, leaving multi-customer
    neutrality unimpaired by contract.
  derived_from: 'competitive_advantage.distribution: 4 — "MRVL''s multi-customer neutrality
    is the structural differentiator on the distribution axis"; 2Q27 note watch-item:
    "hyperscaler_revenue_concentration moves to Drift — one customer anchors the FY29+
    custom story and holds a warrant on up to 6.7% of the company"'
  themes:
  - hyperscaler_revenue_concentration
  - silicon_architecture_competition
  challenged_by:
  - MRVL 10-Q, 10-K, or 8-K exhibit disclosing exclusivity, right-of-first-refusal,
    or non-compete provisions embedded in the Google warrant agreement terms
  - MRVL management disclosure of customer-specific design or deployment constraints
    linked to the Google warrant as a condition of vesting
  confirmed_by:
  - MRVL 10-Q for the period ending 2026-10-31 or later filed without exclusivity
    covenants in the Google warrant exhibit
  - MRVL management explicitly confirming multi-customer custom silicon engagement
    continues without Google-imposed constraints after the warrant disclosure
  status: open
  status_source: draft
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: dc_rev_growth_exceeds_capex_growth_fy28
  statement: MRVL's data center revenue grows faster than aggregate hyperscaler CapEx
    in FY28, as management guided in 1Q FY27 ('+45% y/y despite cloud CapEx growth
    moderating to ~30% range'), a claim that presupposes share gain and rising silicon
    content per dollar of CapEx.
  derived_from: 'ai_positioning: 4 — "growth is leverage on others'' capex"; 1Q27
    earnings note section 4 ai_infrastructure_capex — "decouples MRVL growth from
    absolute capex growth — implying share gain and rising content per box"'
  themes:
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - MRVL FY28 full-year data center revenue growth rate at or below the aggregate
    CapEx growth rate reported by AWS, Azure, and Google Cloud for the same fiscal
    year
  - MRVL guidance revision reducing FY28 data center revenue growth below 40% while
    at least two major hyperscalers report CapEx growth at or above 30%
  confirmed_by:
  - MRVL FY28 annual data center revenue growth rate exceeds the CapEx growth rate
    reported by at least two of the three major cloud providers (AWS, Azure, Google
    Cloud) for the same reporting period
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
