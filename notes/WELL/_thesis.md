---
doc_type: thesis
ticker: WELL
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#WELL
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: well_ai_ops_and_mktsel_in_prod
  statement: At scoring, WELL was actively using AI tools for both property operations
    and capital-allocation (buy/sell) market-selection decisions — not merely piloting
    or describing them aspirationally.
  derived_from: 'ai_positioning: 3 — "uses AI for operations AND for market selection
    (which markets to buy/sell — capital allocation). AI-driven operating platform
    + data-science capital allocation is a real edge"'
  themes:
  - vertical_ai_applications
  challenged_by:
  - 10-K or proxy disclosure clarifying that market-selection decisions are not AI-assisted
  - Management walkback on an earnings call stating AI is in pilot or advisory-only
    stage for capital allocation
  confirmed_by:
  - 10-Q or 10-K describing AI/data-science platform as operational for both property
    ops and acquisition/disposition screening
  - Investor day materials citing specific AI-driven market-selection decisions and
    deal outcomes
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: well_ai_edge_differentiated_vs_reit_peers
  statement: WELL's data-science-driven operating platform and capital-allocation
    analytics were differentiated relative to peer REITs at the time of scoring —
    even if modest in absolute technology terms.
  derived_from: 'competitive_advantage.innovation_rate: 3 — "data-science-driven operating
    platform and capital-allocation analytics — differentiated for a REIT, modest
    in absolute tech terms"'
  themes:
  - vertical_ai_applications
  challenged_by:
  - A peer REIT (e.g., Ventas, Healthpeak) publicly disclosing a comparable AI/data-science
    capital-allocation platform in a filing or investor presentation
  - Third-party technology vendor announcing a white-label market-selection AI product
    adopted by multiple REIT operators
  confirmed_by:
  - No peer REIT 10-K, 8-K, or investor presentation describing equivalent AI-driven
    market-selection capability through the next earnings cycle
  - Industry survey or analyst note citing WELL as the sole or leading REIT deployer
    of capital-allocation AI
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: well_reit_core_not_ai_core
  statement: WELL's primary business at scoring is REIT-core; AI/data constitutes
    an operating layer, not a standalone segment or primary revenue source.
  derived_from: 'competitive_advantage.overall: 3 — "held at 3 as the business is
    REIT-core not AI-core"'
  themes:
  - vertical_ai_applications
  challenged_by:
  - SEC filing introducing an AI or technology services segment with material separate
    revenue
  - 10-K business description recharacterizing the company as a technology or data
    platform rather than a REIT
  confirmed_by:
  - 10-K revenue breakdown showing real-estate operations as the dominant revenue
    driver with no standalone AI/technology segment
  - REIT qualification and dividend distribution maintained under IRS REIT rules in
    the most recent annual filing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: well_snr_housing_portfolio_scale_intact
  statement: WELL's large-scale senior-housing/medical-office portfolio and operator
    relationships that support distribution score 4 were intact at scoring.
  derived_from: 'competitive_advantage.distribution: 4 — "large-scale senior-housing/medical-office
    portfolio and operator relationships"'
  themes:
  - demographic_demand_tailwinds
  challenged_by:
  - 10-Q or 8-K disclosing a material portfolio disposition program that reduces total
    asset count or geographic reach significantly
  - 8-K or earnings call disclosing loss of or material renegotiation with a top-5
    operator relationship
  confirmed_by:
  - 10-Q property count and operator concentration table consistent with scoring-period
    levels
  - No 8-K filed citing departure of a major operator or sale of a property category
    comprising >10% of NOI
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: well_snr_housing_ops_strong_at_scoring
  statement: Senior-housing operating performance conditions characterized as strong
    at scoring — as reflected in occupancy and same-store NOI — held through the most
    recently reported quarter at scoring.
  derived_from: 'potential_investor_interest.score: 4 — "strong senior-housing-operating
    performance"'
  themes:
  - demographic_demand_tailwinds
  challenged_by:
  - Subsequent 10-Q showing same-store NOI growth turning negative or occupancy declining
    materially from the prior-year period
  - Earnings release citing operator distress, rent deferrals, or coverage ratio deterioration
    for senior-housing operators
  confirmed_by:
  - 10-Q same-store senior-housing NOI growth positive year-over-year in the quarter
    following scoring
  - Occupancy rate in senior-housing operating portfolio at or above the level reported
    at time of scoring
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: well_index_inclusion_holds_at_scoring
  statement: WELL held inclusion in its primary benchmark index at the time of scoring,
    supporting the institutional investor demand component of potential_investor_interest
    score 4.
  derived_from: 'potential_investor_interest.score: 4 — "index inclusion"'
  themes:
  - demographic_demand_tailwinds
  challenged_by:
  - Index provider announcement (S&P, MSCI, FTSE Russell) of WELL's removal from a
    constituent index
  - Press release or data-vendor update showing WELL reclassified out of the REIT
    or healthcare sector in a benchmark that drives passive flows
  confirmed_by:
  - Index constituent file from S&P 500, MSCI US REIT Index, or equivalent benchmark
    listing WELL as a current member
  - Passive fund 13-F filings continuing to show WELL as a position consistent with
    index-driven ownership
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
