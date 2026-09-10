---
doc_type: thesis
ticker: AMZN
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AMZN
reviewed_by_operator: false
scores:
  ai_positioning: 4+
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: 4+
proposed_scores: {}
assumptions:
- id: aws_leads_enterprise_ai_distribution
  statement: AWS constitutes a leading enterprise distribution channel for AI workloads
    at the time of scoring, consistent with the maximum distribution score.
  derived_from: 'competitive_advantage.distribution: 5 — ''AWS gives massive AI distribution
    to enterprise'''
  themes:
  - hyperscaler_capex_buildout
  - vertical_ai_applications
  challenged_by:
  - Azure or GCP surpasses AWS in enterprise AI workload market share in a third-party
    analyst report or industry survey published after the scoring date
  - A named large enterprise customer announces consolidation of AI workloads away
    from AWS in a press release or earnings call transcript
  confirmed_by:
  - AWS segment revenue growth rate equals or exceeds Azure and GCP as reported in
    the respective companies' quarterly filings
  - Bedrock enterprise customer count disclosed in AMZN earnings materials increases
    quarter-over-quarter
  status: open
  status_source: draft
  pressure:
    confirm: 7.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: bedrock_anthropic_closes_model_gap
  statement: The Bedrock + Anthropic partnership closes the model-layer capability
    gap relative to pure-AI innovators at the time of scoring.
  derived_from: 'ai_positioning: 4+ — ''Bedrock + Anthropic partnership covers model-layer
    gap'''
  themes:
  - ai_agent_monetization
  - agent_framework_landscape
  challenged_by:
  - Anthropic publicly restricts or terminates its AWS partnership arrangement, disclosed
    in an SEC filing or press release
  - Multiple published enterprise case studies document selection of non-Bedrock foundation
    model providers over Bedrock for production deployments
  confirmed_by:
  - Anthropic model lineup on Bedrock expands as disclosed in an AWS product announcement
  - AMZN 10-K or investor day materials cite Bedrock design wins at named enterprise
    accounts
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 2.5
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: logistics_prime_no_single_rival
  statement: No single competitor replicates the combined logistics network and Prime
    loyalty program at the time of scoring.
  derived_from: 'competitive_advantage.distribution: 5 — ''Logistics + Prime distribution
    moat unique'''
  themes:
  - local_commerce_delivery
  - agentic_commerce
  challenged_by:
  - A competitor discloses fulfillment node count and same-day delivery coverage closing
    within 20% of AMZN's disclosed footprint in a 10-K or press release
  - A rival loyalty program reaches Prime-equivalent subscriber count in a major AMZN
    geography, disclosed in a competitor 10-K or earnings release
  confirmed_by:
  - AMZN 10-K or 10-Q discloses fulfillment and delivery network expansion while no
    competitor files comparable capacity additions in the same period
  - Prime subscriber count disclosed in AMZN earnings materials equals or exceeds
    the figure reported in the quarter prior to scoring
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: distribution_dominates_over_innovation
  statement: At the time of scoring, distribution advantage is the dominant competitive
    factor in AMZN's core businesses, such that a lower pure-AI innovation rate relative
    to NVDA and GOOG does not reduce the overall competitive advantage score below
    5.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''Innovation rate lower
    than NVDA/GOOG on pure AI, but distribution dominates the equation for the businesses
    they’re in'''
  themes:
  - silicon_architecture_competition
  - hyperscaler_capex_buildout
  challenged_by:
  - AWS loses two or more named enterprise AI platform design wins to a competitor
    in a single quarter, documented in customer announcements or press releases
  - AMZN 10-K or earnings materials add AI innovation rate as a newly disclosed competitive
    risk factor not present in the prior annual filing
  confirmed_by:
  - AWS AI-workload market share in a third-party industry report published after
    scoring date is at or above the level reported closest to the scoring date
  - New enterprise AI platform contract awards naming AWS as selected provider are
    disclosed in AMZN investor materials or customer press releases
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ads_revenue_material_at_scoring
  statement: Advertising Services is a material contributor to AMZN's consolidated
    revenue at the time of scoring.
  derived_from: 'potential_investor_interest.score: 4+ — ''Advertising business material
    and growing'''
  themes:
  - ad_market_strength
  challenged_by:
  - Advertising Services segment revenue declines sequentially or year-over-year in
    a reported 10-Q or 10-K filing
  - Advertising segment revenue share falls below 5% of consolidated net sales as
    disclosed in a 10-K segment footnote
  confirmed_by:
  - Advertising Services line item in the next reported 10-Q equals or exceeds the
    figure from the most recent quarter prior to scoring
  - Advertising segment revenue growth rate disclosed in an earnings release exceeds
    consolidated net sales growth rate in the same period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: aws_growth_reaccelerating_at_scoring
  statement: AWS segment revenue growth rate at the time of scoring is higher than
    the rate reported in the immediately prior quarter.
  derived_from: 'potential_investor_interest.score: 4+ — ''AWS reacceleration story'''
  themes:
  - hyperscaler_capex_buildout
  challenged_by:
  - Next 10-Q filing shows AWS segment revenue growth rate below the rate reported
    in the most recent quarter prior to scoring
  - AMZN management guides AWS revenue growth below the prior-quarter rate in an 8-K
    or earnings call transcript
  confirmed_by:
  - Next 10-Q or earnings release shows AWS segment revenue growth rate equal to or
    above the most recently reported pre-scoring quarter
  - AWS remaining performance obligations (RPO) backlog disclosed in the next 10-Q
    increases year-over-year
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
