---
doc_type: thesis
ticker: GDS
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#GDS
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: gds_ai_dc_capacity_beneficiary
  statement: At the time of scoring, GDS's data center capacity buildout was being
    driven by AI-workload demand, not general-purpose compute only.
  derived_from: 'ai_positioning: 4 — ''direct AI-datacenter capacity buildout. AI-infra
    capacity beneficiary'''
  themes:
  - ai_infrastructure_capex
  - china_ai_infrastructure_demand
  challenged_by:
  - GDS earnings disclosure showing AI-specific signed leases as a negligible share
    of new capacity commitments
  - Hyperscaler or cloud tenant cancellation of AI-specific capacity orders disclosed
    in a GDS filing or press release
  confirmed_by:
  - GDS earnings call or investor-day disclosure explicitly attributing new lease
    signings to AI workload tenants
  - Third-party data center capacity report classifying GDS among top AI-ready DC
    operators by AI-specific MW
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gds_china_dc_leading_footprint
  statement: GDS held a leading China data center footprint by deployed capacity at
    the time of scoring.
  derived_from: 'competitive_advantage.distribution: 4 — ''leading China DC footprint'''
  themes:
  - china_ai_infrastructure_demand
  challenged_by:
  - A competitor's public filing or industry report documenting larger total deployed
    China co-location capacity than GDS
  confirmed_by:
  - Third-party market share report placing GDS in the top two China co-location operators
    by MW or cabinet count
  - GDS 20-F or earnings release citing GDS as the largest or second-largest China
    IDC operator by deployed capacity
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gds_intl_hyperscaler_sovereign
  statement: GDS's international expansion via DayOne had secured at least one hyperscaler
    and at least one sovereign customer as tenants at the time of scoring.
  derived_from: 'competitive_advantage.distribution: 4 — ''international expansion
    with hyperscaler/sovereign customers'''
  themes:
  - sovereign_ai_deployments
  - ai_infrastructure_capex
  challenged_by:
  - DayOne lease disclosures or GDS 20-F showing no hyperscaler or sovereign entity
    among named international customers
  - Hyperscaler or sovereign customer non-renewal or termination of a DayOne lease
    disclosed in a filing or press release
  confirmed_by:
  - GDS earnings call or press release naming a hyperscaler as a signed DayOne tenant
  - GDS or DayOne announcement of a sovereign government or sovereign-wealth-affiliated
    entity as a data center customer
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gds_leverage_elevated_at_scoring
  statement: GDS's debt load at the time of scoring was elevated enough to weigh on
    the competitive-advantage assessment, consistent with an Overall score of 3 despite
    a Distribution score of 4.
  derived_from: 'competitive_advantage.overall: 3 — ''China-market and leverage risks
    weigh'''
  themes:
  - china_ai_infrastructure_demand
  challenged_by:
  - GDS filing showing a material debt reduction or equity raise that brings net leverage
    to levels consistent with investment-grade China data center peers
  confirmed_by:
  - GDS 20-F or interim financial statement showing net debt/EBITDA above the level
    of peer co-location operators assigned higher overall competitive-advantage scores
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gds_geopolitical_risk_caps_pi
  statement: China/geopolitical risk conditions at the time of scoring were constraining
    the investor universe for GDS, capping potential investor interest below a score
    of 4.
  derived_from: 'potential_investor_interest.score: 3 — ''geopolitical/China cap'''
  themes:
  - china_us_tensions
  challenged_by:
  - US-China policy announcement materially easing investment restrictions on Chinese
    technology or infrastructure companies (e.g., Treasury or OFAC guidance update)
  - Major US institutional investor publicly disclosing a new or enlarged GDS position
    in a 13-F or equivalent regulatory filing
  confirmed_by:
  - New or tightened US executive order or Congressional action restricting US investment
    in Chinese data center or technology infrastructure companies
  - GDS earnings call citing restricted institutional access due to geopolitical risk
    as a headwind to capital formation
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gds_china_customer_concentration
  statement: GDS's China revenue was concentrated in a limited set of customers at
    the time of scoring rather than broadly diversified.
  derived_from: 'competitive_advantage.distribution: 4 — ''but China-customer concentration'''
  themes:
  - china_ai_infrastructure_demand
  - china_us_tensions
  challenged_by:
  - GDS 20-F or earnings disclosure showing a material increase in China customer
    count or a decline in revenue share attributable to the top-three customers
  confirmed_by:
  - GDS 20-F risk-factor disclosure or earnings call confirming that a small number
    of customers account for a majority of China segment revenue
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
