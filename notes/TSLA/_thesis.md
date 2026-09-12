---
doc_type: thesis
ticker: TSLA
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#TSLA
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: fsd_deployed_at_scale
  statement: At scoring, FSD was deployed to a fleet at commercial scale — the program
    was not limited to a supervised-only pilot phase.
  derived_from: 'ai_positioning: 5 — ''FSD/autonomy at scale'''
  themes:
  - autonomous_vehicle_competition
  challenged_by:
  - NHTSA or DOJ order materially restricting FSD commercial availability issued after
    scoring date
  - Tesla 10-Q or earnings call disclosing active FSD subscriber count below mass-market
    threshold or rollout suspension
  confirmed_by:
  - Tesla filing or earnings disclosure citing cumulative FSD miles driven or active
    subscriber count consistent with mass-deployment
  - Tesla AI Day or investor day slide showing FSD fleet size exceeding prior disclosed
    milestone
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: custom_inference_silicon_active
  statement: At scoring, Tesla's custom inference silicon was in active production
    or vehicle/robot deployment, not pre-production.
  derived_from: 'ai_positioning: 5 — ''custom inference silicon constitute winner-tier
    real-world AI'''
  themes:
  - silicon_architecture_competition
  - autonomous_vehicle_competition
  challenged_by:
  - Tesla earnings call or 10-K disclosing custom chip program cancellation or delay
    beyond scoring date
  - Supply chain trade data showing no volume wafer orders for a Tesla proprietary
    inference chip
  confirmed_by:
  - Tesla 10-K capital allocation disclosure citing custom inference chip production
    ramp
  - Tesla earnings call management commentary confirming custom silicon in production
    vehicles or Optimus units
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: optimus_program_active
  statement: At scoring, Optimus humanoid was an active development program — not
    suspended, cancelled, or de-prioritized by management.
  derived_from: 'ai_positioning: 5 — ''Optimus humanoid'''
  themes:
  - humanoid_robotics_competition
  challenged_by:
  - Tesla earnings call or SEC filing disclosing Optimus program suspension or funding
    cut
  - Absence of Optimus-related capital expenditure line in Tesla 10-K/10-Q filings
    for two consecutive quarters post-scoring
  confirmed_by:
  - Tesla earnings call or filing disclosing Optimus unit count in testing or limited
    production after scoring date
  - Tesla investor day or AI day presentation showing a new Optimus production milestone
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ev_demand_decel_conditions_hold
  statement: At scoring, EV unit demand was decelerating and competitive intensity
    in EV markets was increasing — neither condition had reversed.
  derived_from: 'competitive_advantage.distribution: 4 — ''EV demand decelerating
    with rising competition'''
  themes:
  - autonomous_vehicle_competition
  - china_us_tensions
  challenged_by:
  - Tesla quarterly delivery report showing YoY and sequential unit volume acceleration
    in the quarter of or following scoring
  - Industry EV registration data showing Tesla gaining share from new entrants in
    its core price segments
  confirmed_by:
  - Tesla delivery report showing flat or declining YoY unit volume in the quarter
    of or following scoring
  - Regulatory filings or press releases documenting new competitor EV model launches
    in Tesla's primary price segments
  status: open
  status_source: draft
  pressure:
    confirm: 4.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: auto_base_under_financial_pressure
  statement: At scoring, conditions of pricing pressure or delivery volume softness
    in Tesla's auto segment were active — not historical or resolved.
  derived_from: 'competitive_advantage.overall: 4 — ''autonomy/robotics optionality
    on an auto base under pressure'''
  themes:
  - autonomous_vehicle_competition
  - china_us_tensions
  challenged_by:
  - Tesla earnings report showing auto gross margin expansion YoY with simultaneous
    sequential delivery acceleration
  - Tesla press release or earnings call announcing price increases on core Model
    Y or Model 3 without disclosed demand destruction
  confirmed_by:
  - Tesla earnings report showing auto gross margin at or below the comparable prior-year
    quarter
  - Tesla press release announcing additional vehicle price reductions after scoring
    date
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: robotaxi_optimus_narrative_primary
  statement: At scoring, the robotaxi/Optimus narrative — not auto-segment fundamentals
    — was the stated basis for the 5 investor-interest score.
  derived_from: 'potential_investor_interest.score: 5 — ''robotaxi/Optimus narrative
    drives outsized investor appeal'''
  themes:
  - autonomous_vehicle_competition
  - humanoid_robotics_competition
  challenged_by:
  - Robotaxi commercial-launch date pushed out by management on a Tesla earnings call
    or in a regulatory filing after scoring
  - Optimus volume-production timeline publicly extended by more than 12 months vs.
    prior management guidance
  confirmed_by:
  - TSLA equity market capitalization remains at or above 5x next-largest auto OEM
    by market cap at the time of the following earnings print
  - Tesla earnings call transcript showing a majority of sell-side analyst questions
    focused on autonomy or robotics rather than auto deliveries or margins
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
