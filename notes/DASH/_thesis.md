---
doc_type: thesis
ticker: DASH
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#DASH
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: nrm_no_compression_post_integration
  statement: Conditions at scoring — Net Revenue Margin of 13.5% of Marketplace GOV
    — have not deteriorated as Deliveroo integration costs layer into the revenue
    base.
  derived_from: 'theme: platform_take_rate — ''Net Revenue Margin 13.5%, consistent
    with the same quarter of 2025'''
  themes:
  - platform_take_rate
  - local_commerce_delivery
  challenged_by:
  - Q3 2026 10-Q discloses Net Revenue Margin below 13.0% with management attribution
    to integration-driven cost absorption or merchant subsidy expansion
  - Management issues guidance explicitly stepping down take-rate to fund Deliveroo
    merchant incentives in any quarterly filing or earnings call transcript
  confirmed_by:
  - Q3 2026 10-Q discloses Net Revenue Margin at or above 13.5% alongside Contribution
    Profit margin at or above 5.0% of Marketplace GOV
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ad_revenue_not_in_retreat
  statement: Conditions at scoring — DASH offers advertising as a value-added service
    to merchants and CPG companies across Marketplaces — have not seen a material
    pullback in advertiser participation or spend.
  derived_from: 'theme: ad_market_strength — ''advertising as a value-added service
    through our Marketplaces to help merchants and consumer packaged goods companies
    increase consumer engagement and drive incremental revenue'''
  themes:
  - ad_market_strength
  - platform_take_rate
  challenged_by:
  - DASH discloses a Y/Y decline in advertising revenue or ad attach rates in a 10-Q
    filing or investor presentation
  - A top-5 CPG company discloses a reduction in grocery or on-demand delivery ad
    spend on its own quarterly earnings call
  confirmed_by:
  - DASH separately discloses advertising revenue as a line item showing Y/Y growth,
    or management quantifies advertising contribution in a 10-Q or investor day presentation
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: av_no_coverage_displacement
  statement: Conditions at scoring — no autonomous-vehicle delivery operator has reached
    commercial coverage density sufficient to displace Dasher fulfillment — have not
    changed in any top-10 DASH U.S. city.
  derived_from: 'theme: autonomous_vehicle_competition — ''investment to increase
    system capacity for Dashers and in support of longer distance and higher effort
    deliveries'''
  themes:
  - autonomous_vehicle_competition
  - local_commerce_delivery
  challenged_by:
  - An AV delivery operator files or publicly announces a citywide commercial delivery
    launch in a top-10 DASH U.S. market (by GOV)
  - DASH 10-Q discloses a decline in Dasher utilization rate in the same period an
    AV competitor announces market entry in an overlapping geography
  confirmed_by:
  - No AV delivery operator files for or announces a commercial citywide launch in
    a top-10 DASH market across the subsequent two quarterly reporting periods
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
