---
doc_type: thesis
ticker: PLTR
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#PLTR
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: ontology_layer_primary_differentiator
  statement: At scoring, PLTR's ontology layer constituted the primary technical differentiator
    of AIP versus competing enterprise AI-deployment platforms.
  derived_from: 'ai_positioning: 5 — "ontology is the differentiator"'
  themes:
  - enterprise_ai_adoption
  - ai_native_vertical
  challenged_by:
  - A hyperscaler (MSFT, GOOGL, AMZN) ships a generally-available semantic-ontology
    or knowledge-graph layer for its enterprise AI stack, announced via product launch
    filing or press release.
  - PLTR loses a disclosed competitive RFP where a vendor press release or customer
    case study cites ontology-equivalent capability as the basis for selection.
  confirmed_by:
  - PLTR wins a disclosed competitive displacement contract where the press release
    or 8-K cites ontology as the differentiating factor.
  - A publicly filed partner agreement or government contract award references PLTR's
    ontology layer as a technical requirement.
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: us_commercial_growth_accelerating_at_scoring
  statement: US commercial revenue growth rate was accelerating at the time of scoring
    (2026-06-02).
  derived_from: 'ai_positioning: 5 — "rapidly accelerating US commercial"'
  themes:
  - enterprise_ai_adoption
  challenged_by:
  - A 10-Q filed after scoring shows US commercial revenue growth rate (year-over-year)
    lower than the rate reported in the prior quarter's 10-Q.
  - PLTR issues a guidance revision or 8-K that explicitly cites slowing commercial
    pipeline conversion.
  confirmed_by:
  - The next quarterly earnings press release discloses US commercial revenue growth
    rate equal to or above the growth rate reported in the most recent quarter prior
    to 2026-06-02.
  - PLTR's 10-Q shows sequential US commercial customer count growth consistent with
    the prior quarter's trend.
  status: open
  status_source: draft
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: bootcamp_model_supports_commercial_landings
  statement: At scoring, the bootcamp-led sales motion was the mechanism supporting
    new US commercial customer acquisition.
  derived_from: 'competitive_advantage.innovation_rate: 4 — "bootcamp-led product
    motion"'
  themes:
  - enterprise_ai_adoption
  - ai_agent_monetization
  challenged_by:
  - PLTR's next 10-Q or earnings press release shows US commercial customer count
    growth decelerating while the company discloses flat or rising bootcamp volume.
  - A PLTR earnings call transcript or 8-K discloses a change in sales motion away
    from bootcamp as primary commercial entry point.
  confirmed_by:
  - PLTR reports sequential growth in US commercial customer count in its next earnings
    press release.
  - PLTR's investor-day materials or an SEC filing discloses bootcamp-to-contract
    conversion data or volume consistent with land-and-expand progression.
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gov_revenue_majority_of_mix_at_scoring
  statement: At scoring, government revenue constituted the majority of PLTR's total
    revenue mix, with US commercial as a growing but smaller segment.
  derived_from: 'competitive_advantage.distribution: 4 — "still gov-weighted with
    a building commercial base"'
  themes:
  - enterprise_ai_adoption
  - vertical_ai_applications
  challenged_by:
  - A PLTR 10-Q shows US commercial segment revenue exceeding government segment revenue
    in any reported quarter.
  - PLTR investor-day materials revise reported segment definitions in a way that
    reclassifies the revenue mix characterization.
  confirmed_by:
  - The most recent PLTR 10-Q filed prior to 2026-06-02 shows government segment revenue
    above US commercial segment revenue.
  - PLTR's Q2 2026 10-Q (if filed after scoring) shows government segment revenue
    continuing to exceed US commercial segment revenue.
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: rule_of_40_above_threshold_at_scoring
  statement: At scoring, PLTR's Rule-of-40 metric (revenue growth rate plus free-cash-flow
    margin) was above 40.
  derived_from: 'potential_investor_interest.score: 5 — "strong growth + Rule-of-40"'
  themes:
  - enterprise_ai_adoption
  - ai_native_vertical
  challenged_by:
  - A subsequent PLTR 10-Q or earnings press release shows the combined revenue growth
    rate and FCF margin sum falling below 40.
  - PLTR management omits Rule-of-40 from earnings prepared remarks or investor materials
    in a subsequent quarter.
  confirmed_by:
  - PLTR's most recent earnings press release prior to 2026-06-02 explicitly reports
    or allows calculation of revenue growth rate plus FCF margin above 40.
  - PLTR's next quarterly earnings press release reports a Rule-of-40 figure above
    40.
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: sp500_inclusion_active_investor_flow_factor
  statement: At scoring, PLTR's S&P 500 membership was an active factor contributing
    to investor demand and flow.
  derived_from: 'potential_investor_interest.score: 5 — "S&P 500 inclusion"'
  themes:
  - enterprise_ai_adoption
  - ai_native_vertical
  challenged_by:
  - An S&P Dow Jones Indices announcement removes PLTR from the S&P 500 or materially
    reduces its index weight in a scheduled rebalancing.
  - Passive ETF 13-F filings (SPY, IVV, VOO) for the quarter ending after scoring
    show a material reduction in aggregate PLTR share count held.
  confirmed_by:
  - No S&P 500 removal or weight-reduction announcement is issued for PLTR in the
    rebalancing cycle following scoring.
  - Passive ETF 13-F filings for the quarter covering the scoring date show flat or
    increased aggregate PLTR holdings.
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
