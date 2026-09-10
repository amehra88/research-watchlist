---
doc_type: thesis
ticker: CRWV
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#CRWV
- notes/CRWV/20260812-2Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: crwv_2h_ramp_power_gated
  statement: The approximately $8.15B of 2H26 revenue implied by the FY26 midpoint
    guidance requires power additions that management characterised as back-end loaded
    toward a 1.85GW year-end target; a shortfall in that power delivery schedule reduces
    the achievable revenue range without a demand shortfall.
  derived_from: 'data_center_deployment_constraints: Drift — ''Management ties the
    ramp to power: 1.85GW active by year end (raised from 1.7GW) off 1.5GW at quarter
    end, with additions explicitly described as back-end loaded'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - 3Q26 10-Q discloses active power materially below the implied trajectory toward
    1.85GW (e.g., below ~1.65GW at 3Q26 end)
  - An 8-K or press release announces a delay to a specific power-delivery project
    contributing to the year-end target
  confirmed_by:
  - 3Q26 10-Q reports active power at or above the implied step-up trajectory toward
    1.85GW
  - 3Q26 earnings commentary confirms no change to the power delivery schedule
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwv_debt_cost_conditions_held
  statement: The financing conditions that produced a ~300bps year-over-year reduction
    in weighted average cost of debt and enabled $18B of capital raised in a single
    quarter had not materially reversed at the time of scoring.
  derived_from: 'ai_infrastructure_capex: Confirm — ''weighted average cost of debt
    down ~300bps YoY (~$1.1B annualized interest saved)'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - A subsequent 8-K disclosing a new debt issuance or finance lease at a spread materially
    above the 2Q26 weighted average cost of debt
  - 3Q26 10-Q interest expense grows faster than the proportional increase in total
    debt outstanding, implying a higher marginal cost
  confirmed_by:
  - Next debt issuance disclosed via 8-K prices at or below the 2Q26 weighted average
    cost of debt
  - 3Q26 10-Q interest expense grows no faster than total debt outstanding
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwv_vera_rubin_margin_premium
  statement: At 2Q26 close, CRWV's first-to-market position on NVIDIA Vera Rubin NVL72
    was the cited mechanism for new-deal contribution margins running 5–10 points
    above prior-quarter levels.
  derived_from: 'ai_compute_topology: Confirm — ''industry-first bring-up and validation
    of NVIDIA''s Vera Rubin NVL72...strong demand and margin expansion attached to
    Vera Rubin''; inference_compute_economics: Drift — ''new-deal contribution margins
    are 5–10 points above prior quarters'''
  themes:
  - ai_compute_topology
  - inference_compute_economics
  challenged_by:
  - A competing neocloud announces Vera Rubin NVL72 cluster availability via press
    release or 10-Q filing
  - 3Q26 earnings commentary or 10-Q discloses contribution margin on new deals reverting
    to the pre-Vera Rubin range
  confirmed_by:
  - 3Q26 earnings confirms no comparable-scale Vera Rubin deployment announced by
    a listed or named competitor
  - 3Q26 earnings shows sequential adjusted operating margin expansion toward the
    low-teens 4Q26 target cited by management
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwv_a100_residual_pricing
  statement: 2020-vintage A100 GPU fleet was re-contracting at prices described as
    'attractive' at 2Q26 close — a condition that, if it does not hold, invalidates
    the useful-life and residual-value assumptions applied to the prior-generation
    fleet.
  derived_from: 'ai_compute_topology: Confirm — ''2020-vintage A100s are described
    as re-contracting at attractive prices'''
  themes:
  - ai_compute_topology
  - inference_compute_economics
  challenged_by:
  - A peer neocloud 10-Q or earnings filing discloses declining renewal prices or
    underutilisation on A100-class inventory
  - CRWV 3Q26 10-Q shows an impairment charge or accelerated depreciation on A100-class
    assets
  confirmed_by:
  - 3Q26 earnings commentary confirms A100 fleet re-contracted at prices at or above
    2Q26 levels
  - No impairment charge on A100-class assets appears in the 3Q26 10-Q
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwv_regulatory_no_impact_scored
  statement: At 2Q26 close, the increased regulatory scrutiny and local opposition
    to data centers that management acknowledged had not caused any delay or reduction
    in the deliverable capacity underpinning guidance — a condition management stated
    in an explicitly unqualified way.
  derived_from: 'data_center_deployment_constraints: Drift — ''Management acknowledges
    increased regulatory scrutiny and local opposition to data centers but states
    no current impact on guidance or deliverable capacity. An unusually unqualified
    statement given the acknowledged rise in local opposition'''
  themes:
  - data_center_deployment_constraints
  challenged_by:
  - A permit denial, injunction, or government order affecting a CRWV data center
    site disclosed via 8-K or 10-Q
  - 3Q26 10-Q or earnings commentary discloses a project delay attributed to regulatory
    or community-opposition proceedings
  confirmed_by:
  - 3Q26 10-Q Risk Factors section carries no new regulatory proceedings or permit
    delays beyond those disclosed at 2Q26
  - 3Q26 earnings commentary reaffirms no guidance impact from regulatory or local-opposition
    events
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwv_gaap_gm_gap_da_not_price
  statement: The approximately 27-percentage-point gap between as-reported GAAP gross
    margin (~38.8%) and street-basis gross margin (~66.0%) in 2Q26 reflects D&A attributed
    to facilities and power infrastructure scaling with $9.4B of quarterly capex,
    not a deterioration in revenue per unit of compute delivered — making the street-basis
    miss of -0.70% the operationally relevant signal on unit pricing.
  derived_from: 'inference_compute_economics: Drift — ''the ~27pt gap versus the street
    basis above is not an error — FactSet fundamentals gross income is struck after
    D&A, which the sell-side gross-profit line evidently is not, and D&A is scaling
    with $9.4B/quarter of capex'''
  themes:
  - inference_compute_economics
  - ai_infrastructure_capex
  challenged_by:
  - 3Q26 10-Q shows the street-basis gross margin miss widening beyond the 2Q26 -0.9pt
    delta at a similar or higher revenue growth rate
  - A 3Q26 cost-of-revenue footnote shows non-D&A cost items (e.g., power, rent) growing
    faster than revenue
  confirmed_by:
  - 3Q26 FactSet INC_GROSS surprise is >= 0% while the as-reported GAAP gross margin
    continues to compress, consistent with the D&A explanation
  - 3Q26 10-Q cost-of-revenue footnote identifies D&A as the primary driver of the
    GAAP-to-street gross margin divergence
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
