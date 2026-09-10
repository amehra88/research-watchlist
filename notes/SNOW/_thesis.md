---
doc_type: thesis
ticker: SNOW
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#SNOW
- notes/SNOW/20260528-1Q27.md
- notes/SNOW/20260903-2Q27.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: snow_ai_product_accel_attribution
  statement: CoCo, CoWork, and Snowflake Intelligence account for approximately half
    of the Q2 FY27 product revenue growth acceleration, as attributed by management.
  derived_from: 'enterprise_ai_adoption: Confirm (strengthened) — ''AI products contributed
    approximately half of the acceleration in the quarter and described AI as a structural
    multiplier for platform consumption'''
  themes:
  - enterprise_ai_adoption
  - ai_agent_monetization
  challenged_by:
  - Q3 FY27 earnings call does not include a management attribution of a measurable
    share of revenue acceleration to AI products
  - CoCo net account adds in Q3 FY27 fall materially below the 2,000 adds delivered
    in Q2 FY27
  confirmed_by:
  - Q3 FY27 earnings call includes a specific management attribution of AI products
    to an equal or larger share of the quarter's acceleration
  - SNOW 10-Q for the period ending October 31, 2026 discloses CoCo accounts above
    11,000
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snow_cortex_gateway_no_model_asset
  statement: SNOW's Cortex AI Gateway routes AI tasks across third-party models for
    cost, performance, and governance without SNOW owning large-scale model training
    assets, as disclosed at the Q2 FY27 call.
  derived_from: 'ai_infrastructure_software: Confirm — ''management positioned model
    neutrality as a core competitive advantage... explicitly not pursuing large-scale
    model training while developing specialized Arctic models for narrow efficiency
    gains'''
  themes:
  - ai_infrastructure_software
  challenged_by:
  - AWS, Azure, or GCP announces a native data-plus-AI gateway with model-routing
    and governance that operates inside the hyperscaler's own storage layer, disclosed
    in a press release or product launch event
  - A Fortune 500 SNOW customer publicly discloses migration of AI workloads to a
    hyperscaler-native data platform in an SEC filing or press release
  confirmed_by:
  - SNOW discloses a Cortex AI Gateway customer adoption count or consumption metric
    in a future 10-Q, 8-K, or earnings supplement
  - SNOW's Q3 or Q4 FY27 earnings call includes a named enterprise customer case study
    for Cortex AI Gateway
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snow_observe_1pp_watch
  statement: Observe contributes approximately 1 percentage point to FY27 product
    revenue growth as of Q2 FY27 scoring; this is a watch-item and conditions at scoring
    still hold.
  derived_from: 'observability_competitive_landscape: Drift (toward de-emphasis) —
    ''Observe acquisition contributing ~1pp to FY27 product revenue growth — the same
    figure carried in the Q1 note, unchanged. There is no Observe-specific narrative,
    no competitive co[mmentary]'''
  themes:
  - observability_competitive_landscape
  challenged_by:
  - Q3 or Q4 FY27 earnings disclosure or 10-Q shows Observe contribution to FY27 product
    revenue growth cited below 1pp
  - DDOG or SPLK issues a press release or 8-K announcing a named customer win displacing
    an Observe deployment
  confirmed_by:
  - Q3 or Q4 FY27 earnings call includes a management statement confirming Observe
    contribution at or above 1pp of FY27 product revenue growth
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snow_natoma_close_agentic
  statement: The pending Natoma acquisition closes and SNOW positions the asset as
    extending an agentic control plane into everyday applications in a governed environment,
    as described at the Q1 FY27 call.
  derived_from: 'ai_agent_monetization: Confirm (material upgrade vs. prior posture)
    — ''Pending Natoma acquisition framed as extending SNOW''s agentic control plane
    into everyday applications in a governed environment'''
  themes:
  - ai_agent_monetization
  challenged_by:
  - An SEC filing (Form 8-K or amended S-4) discloses termination of the Natoma acquisition
  - Two quarters post-close, no generally available Natoma-based agentic product is
    announced in a SNOW press release or earnings call
  confirmed_by:
  - SNOW files a Form 8-K with the SEC confirming Natoma acquisition close
  - SNOW announces a generally available Natoma-based product in a press release or
    earnings call within two quarters of close
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snow_margin_expand_no_headcount
  statement: Non-GAAP operating margin expanded 400bps YoY in Q2 FY27 and management
    guided Q3 FY27 to 15.5%, coinciding with 17 organic net headcount adds in Q1 FY27
    ex-acquisition.
  derived_from: 'ai_re_architected_incumbent: Confirm — ''Hiring constrained (17 organic
    adds in Q1 ex-acquisition)... 25% increase in support case throughput per engineer...
    developer productivity doubled (PRs and LOC per engineer)'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - SNOW's Q3 FY27 10-Q headcount disclosure shows a quarter-over-quarter increase
    that outpaces revenue growth on a percentage basis
  - Q3 FY27 non-GAAP operating margin prints below the 15.5% guide in the 8-K Ex-99.1
  confirmed_by:
  - Q3 FY27 non-GAAP operating margin at or above 15.5% per the 8-K Ex-99.1 non-GAAP
    reconciliation table
  - SNOW discloses internal AI productivity metrics (support throughput, developer
    output) at a future Investor Day or earnings call showing continuation at or above
    Q2 FY27 levels
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snow_ai_gm_compression_74pct
  statement: FY27 non-GAAP product gross margin is guided to 74%, with management
    attributing the ~1pp compression from Q2's 75% to AI revenue mix; compression
    does not exceed the disclosed 74% guide.
  derived_from: 'ai_infrastructure_software: Confirm — ''FY27 non-GAAP product gross
    margin guided to 74%, explicitly attributed by management to a higher revenue
    mix from fast-growing AI workloads, which currently have a lower contribution
    margin'''
  themes:
  - ai_infrastructure_software
  - enterprise_ai_adoption
  challenged_by:
  - Q3 or Q4 FY27 8-K Ex-99.1 non-GAAP reconciliation table shows non-GAAP product
    gross margin below 74%
  - Management revises FY27 non-GAAP product gross margin guidance below 74% in a
    future earnings call or 8-K
  confirmed_by:
  - Q3 FY27 8-K Ex-99.1 non-GAAP reconciliation table shows non-GAAP product gross
    margin at or above 74%
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
