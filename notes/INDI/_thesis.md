---
doc_type: thesis
ticker: INDI
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#INDI
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '3'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: indi_adas_not_dc_ai
  statement: At scoring, INDI's revenue exposure was to ADAS content-per-vehicle (radar,
    vision, connectivity) and not to datacenter AI compute spend.
  derived_from: 'ai_positioning: 3 — "rides secular ADAS content growth rather than
    the datacenter AI build"'
  themes:
  - autonomous_vehicle_competition
  - automotive_semiconductor_demand
  challenged_by:
  - INDI 10-Q disclosing a new product segment or material revenue from non-automotive
    AI compute applications
  - INDI press release or investor presentation announcing a datacenter or cloud AI
    chip program
  confirmed_by:
  - INDI 10-K/10-Q segment disclosures showing automotive ADAS as the dominant revenue
    category with no material non-automotive AI line
  - Product roadmap filings or conference presentations listing only automotive radar,
    vision, and connectivity programs
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: indi_pre_scale_vs_incumbents
  statement: At scoring, INDI's revenue was materially smaller in absolute scale than
    established automotive semiconductor incumbents competing in ADAS.
  derived_from: 'competitive_advantage.innovation_rate: 3 — "small and pre-scale vs
    auto-semi incumbents"'
  themes:
  - automotive_semiconductor_demand
  - semiconductor_cycle
  challenged_by:
  - INDI quarterly revenue reaching a level within one order of magnitude of a named
    auto-semi incumbent's ADAS segment revenue as reported in their respective filings
  confirmed_by:
  - INDI 10-Q revenue figures continuing to show a gap well below publicly reported
    ADAS segment revenues of established automotive semiconductor peers
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: indi_backlog_conversion_positive
  statement: At scoring, INDI's design-win backlog conversion was on a positive trajectory
    — the basis for the 3+ trend notation on innovation rate.
  derived_from: 'competitive_advantage.innovation_rate: 3 — "trending 3+ on backlog
    conversion"'
  themes:
  - autonomous_vehicle_competition
  - automotive_semiconductor_demand
  challenged_by:
  - An earnings print disclosing design-win deferrals, program cancellations, or revenue
    from recent design wins falling materially below previously communicated ramp
    timelines
  - An OEM or Tier-1 publicly delaying or canceling an ADAS platform where INDI holds
    a disclosed design win
  confirmed_by:
  - INDI quarterly filings showing automotive ADAS revenue growth consistent with
    timelines implied by prior design-win announcements
  - OEM production launch confirmations for vehicle platforms where INDI holds a disclosed
    design win
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: indi_narrow_customer_base
  statement: At scoring, INDI's revenue was concentrated in a small number of automotive
    customers, making results dependent on the automotive production cycle.
  derived_from: 'competitive_advantage.distribution: 3 — "narrow customer base, automotive-cycle
    dependent"'
  themes:
  - automotive_semiconductor_demand
  - semiconductor_cycle
  challenged_by:
  - INDI 10-K disclosing that no single customer exceeds 10% of revenue, or that top-3
    customer concentration has fallen materially year-over-year
  - Design-win announcements spanning five or more distinct OEM or Tier-1 customers
    within a 12-month window
  confirmed_by:
  - INDI 10-K/10-Q showing top customers accounting for the majority of revenue, consistent
    with a narrow base at scoring
  - Earnings call management commentary referencing dependence on a limited number
    of production programs
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: indi_not_yet_profitable
  statement: At scoring, INDI had not achieved operating profitability.
  derived_from: 'potential_investor_interest.score: 3 — "pre-scale/approaching profitability"'
  themes:
  - semiconductor_cycle
  - automotive_semiconductor_demand
  challenged_by:
  - INDI reporting positive GAAP operating income or positive non-GAAP operating income
    in a quarterly filing dated after the scoring date
  confirmed_by:
  - INDI 10-Q filings after the scoring date continuing to show a GAAP operating loss
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
