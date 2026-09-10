---
doc_type: thesis
ticker: CRWD
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#CRWD
- notes/CRWD/20260604-1Q27.md
- notes/CRWD/20260827-2Q27.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: crwd_charlotte_ai_shipped_product
  statement: The ai_positioning score of 4 rests on Charlotte AI being a commercially
    available agentic SOC capability on the single-agent Falcon platform; conditions
    at scoring hold if Charlotte AI is a shipped product with documented enterprise
    adoption, not a roadmap announcement.
  derived_from: 'ai_positioning: 4 — ''Charlotte AI agentic SOC, single-agent Falcon
    platform; AI-driven detection plus platform consolidation. Strong AI-security
    positioning.'''
  themes:
  - enterprise_ai_adoption
  - ai_native_vertical
  challenged_by:
  - CRWD 10-Q or earnings call reframes Charlotte AI as a roadmap item without disclosing
    customer adoption metrics
  - A competitor files a product announcement for a generally available agentic SOC
    with named enterprise customer wins that CRWD management does not address with
    equivalent Charlotte AI customer evidence
  confirmed_by:
  - CRWD 10-Q or earnings call discloses Charlotte AI customer count or a distinct
    ARR contribution
  - CRWD press release or referenced analyst briefing documents an enterprise customer
    operating Charlotte AI in a live SOC environment
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwd_falcon_module_expansion_pace
  statement: The innovation-rate score of 4 rests on the single-agent Falcon platform
    delivering new AI-driven modules; conditions at scoring hold if CRWD's disclosed
    product set shows net-new AI-driven modules built on the Falcon single-agent architecture
    consistent with the '4+ on module expansion' characterization.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''Falcon single-agent
    platform + Charlotte agentic AI; 4+ on module expansion'''
  themes:
  - ai_native_vertical
  - cybersecurity_competitive_landscape
  challenged_by:
  - CRWD investor day or 10-K product section shows no net-new AI-driven module introductions
    on the Falcon architecture in a fiscal year
  - CRWD earnings call or investor day discloses a shift away from the single-agent
    Falcon design to a multi-agent or third-party-integrated architecture for AI-driven
    detection
  confirmed_by:
  - CRWD 10-K or investor day product section lists a net-new AI-driven Falcon module
    not present at the 2026-06-02 scoring date
  - Earnings call discloses a new Charlotte AI or adjacent AI-driven Falcon capability
    with disclosed enterprise deployments
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwd_lanx_multimodule_enterprise
  statement: The distribution score of 4 rests on platform-consolidation land-and-expand
    generating measurable module uptake within large-enterprise accounts; conditions
    at scoring hold if CRWD's average module count per customer or multi-module deal
    activity is consistent with a top-quartile distribution assessment.
  derived_from: 'competitive_advantage.distribution: 4 — ''platform-consolidation
    land-and-expand with large-enterprise reach; 4+'''
  themes:
  - cybersecurity_competitive_landscape
  - enterprise_ai_adoption
  challenged_by:
  - CRWD 10-Q or earnings call reports a material decline in average module count
    per customer, or management characterizes the land-and-expand motion as slowing
    in the large-enterprise segment
  - CRWD discloses material large-enterprise churn in a 10-Q filing attributable to
    a competing platform consolidation offer
  confirmed_by:
  - CRWD earnings call or 10-Q reports an increase in average module count per Falcon
    customer
  - Earnings call discloses a large-enterprise platform-consolidation win adding three
    or more Falcon modules in a single transaction
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: crwd_outage_residual_not_worsening
  statement: The overall competitive-advantage score of 4 incorporates 'modest residual'
    competitive damage from the 2024 outage; the score is undermined if material incremental
    customer losses or win-rate deterioration explicitly attributed to the outage
    are disclosed after the scoring date.
  derived_from: 'competitive_advantage.overall: 4 — ''leading AI-native security platform;
    the 2024 outage recovery is largely behind with modest residual'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - CRWD 10-Q or earnings call discloses material incremental customer churn explicitly
    attributed to the 2024 outage
  - A published analyst channel survey documents a measurable increase in large-enterprise
    accounts citing the 2024 outage as the primary driver of a completed vendor switch
  confirmed_by:
  - CRWD gross revenue retention figure disclosed in a subsequent 10-Q at or above
    the level reported at the prior fiscal year-end
  - Management disclosure on a subsequent earnings call confirming no material incremental
    competitive losses linked to the 2024 outage, unchallenged by analyst follow-up
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: crwd_valuation_cap_pii_bound
  statement: The potential investor interest score of 4 rests on strong FCF and growth
    rate as primary support, with the premium multiple explicitly identified as the
    binding cap; conditions at scoring hold if FCF margin and revenue growth are at
    levels that justify a 4 assessment and the premium multiple has not expanded to
    a level that suppresses incremental institutional buyer appetite below the scoring-date
    baseline.
  derived_from: 'potential_investor_interest.score: 4 — ''Security leader, post-outage
    recovery, premium multiple, strong NRR/FCF; valuation caps. Factors: hot sector,
    FCF, growth rate; valuation cap.'''
  themes:
  - cybersecurity_competitive_landscape
  - enterprise_ai_adoption
  challenged_by:
  - CRWD 10-Q reports FCF margin below 25% in a quarter where management previously
    guided to 30% or higher
  - Consensus forward price-to-sales ratio for CRWD per FactSet expands above the
    90th percentile of large-cap security software peers, indicating the valuation
    cap has tightened further without a corresponding upward revision to growth estimates
  confirmed_by:
  - CRWD 10-Q reports FCF margin at or above 30% (the FY27 guided floor disclosed
    in the Q1'27 earnings call)
  - CRWD forward price-to-sales ratio compresses toward the large-cap security software
    peer median per FactSet consensus without an accompanying deceleration in consensus
    revenue growth estimates
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
