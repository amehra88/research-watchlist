---
doc_type: thesis
ticker: RBRK
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#RBRK
- notes/RBRK/20260828-2Q27.md
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '3'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: ai_data_security_differentiation
  statement: At scoring, RBRK's AI-data-security/governance angle — securing data
    used in AI pipelines — constitutes product-level differentiation beyond the core
    cyber-resilience platform, sufficient to support a 3+ ai_positioning score. The
    conditions producing that assessment held as of the scoring date.
  derived_from: 'ai_positioning: 3 — ''cyber resilience / data security (backup, ransomware
    recovery) plus an AI data-governance/security angle (securing data for AI). 3+
    on AI-data-security positioning'''
  themes:
  - cybersecurity_competitive_landscape
  - enterprise_ai_adoption
  challenged_by:
  - Rubrik Agent Cloud paying customer count reported at next earnings does not grow
    beyond the 15 disclosed at 2Q27 end (fiscalEndDate 2026-07-31), as stated in an
    8-K Ex-99.1 or earnings-call transcript
  - No enterprise-scale contract citing AI-data-governance as a primary purchase criterion
    is disclosed in any SEC filing or earnings-call transcript through FY27
  confirmed_by:
  - Management discloses an Agent Cloud paying customer count milestone above 15 in
    an 8-K, press release, or earnings-call transcript
  - Agent Cloud ARR contribution is quantified and cited separately in a forward-guidance
    line item in any quarterly filing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: innovation_ai_governance_competitive
  statement: At scoring, RBRK's data-security platform — combining cyber-resilience
    with AI-governance features — produced differentiated outcomes in competitive
    evaluations, consistent with an innovation_rate score of 4.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''strong data-security
    platform with cyber-resilience differentiation and AI-governance features'''
  themes:
  - cybersecurity_competitive_landscape
  - ai_infrastructure_software
  challenged_by:
  - An incumbent vendor (Commvault, Cohesity, or Veeam) discloses an equivalent AI-governance
    or agent-security product capability in a press release or SEC filing
  - RBRK discloses a material decline in competitive win rates in a filing or earnings-call
    transcript
  confirmed_by:
  - Management names AI-governance or Identity Resilience features as the cited reason
    for competitive displacement wins in an 8-K, press release, or earnings-call transcript
  - RBRK is named as a Leader in a subsequent Gartner Magic Quadrant for Backup and
    Data Protection at a position at or ahead of the 2026 Vision-axis placement
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: land_expand_installed_base
  statement: At scoring, RBRK's land-and-expand motion was generating measurable growth
    in its installed base from a smaller starting point than incumbents — the distribution
    score of 3+ requires that customer-count and ARR expansion were occurring, not
    stagnating.
  derived_from: 'competitive_advantage.distribution: 3 — ''scaling post-2024-IPO,
    land-and-expand, smaller installed base than incumbents; 3+'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - YoY growth rate of $100K+ subscription ARR customers (23% at 2Q27 end per 8-K
    Ex-99.1) decelerates to single digits in a subsequently reported quarterly filing
  - Net new subscription ARR turns negative in any quarterly period reported in an
    8-K Ex-99.1
  confirmed_by:
  - $100K+ subscription ARR customer count YoY growth rate is reported at or above
    20% in the next quarterly earnings filing
  - Net new subscription ARR grows sequentially in the next reported quarter per 8-K
    Ex-99.1
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: lockup_overhang_cleared
  statement: At scoring (2026-06-02), the pre-IPO lock-up overhang was assessed as
    largely cleared, removing a technical suppressor from institutional participation
    — a condition that underpins the 4 on potential_investor_interest. The assessment
    that overhang was largely behind held as of the scoring date.
  derived_from: 'potential_investor_interest.score: 4 — ''lock-up overhang largely
    behind'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - A Form S-3 secondary registration by a pre-IPO holder is filed with the SEC on
    or after the scoring date (2026-06-02)
  - A block trade above 5% of total shares outstanding by a pre-IPO holder is disclosed
    in a Form 4 or 8-K filing
  confirmed_by:
  - No Form S-3 secondary registration or insider block trade above 2% of shares outstanding
    is disclosed in SEC filings through end of calendar Q4 2026
  - Institutional ownership breadth increases in the next 13-F filing cycle without
    a concurrent secondary offering registration
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: profitability_watch_no_deterioration
  statement: Profitability was flagged as a watch-item at scoring — the assumption
    embedded in the 4 score is that the developing path to non-GAAP profitability
    does not worsen from the conditions that held at scoring into a thesis-breaking
    headwind.
  derived_from: 'potential_investor_interest.score: 4 — ''profitability path the watch-item'''
  themes:
  - cybersecurity_competitive_landscape
  - ai_agent_monetization
  challenged_by:
  - Management issues forward guidance implying non-GAAP EPS decline from the 2Q27
    delivered level ($0.20 diluted) for two or more consecutive quarters, as disclosed
    in an 8-K or earnings-call transcript
  - Full-year free cash flow guidance is cut below zero in any subsequent quarterly
    filing
  confirmed_by:
  - Full-year non-GAAP EPS guidance is maintained or raised in the next quarterly
    earnings filing (8-K Ex-99.1)
  - Free cash flow guidance for FY27 is maintained at or above the $323–333M range
    disclosed in the 2Q27 8-K Ex-99.1
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
