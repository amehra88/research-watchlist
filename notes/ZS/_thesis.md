---
doc_type: thesis
ticker: ZS
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#ZS
- notes/ZS/20260904-4Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: sse_distribution_not_impaired
  statement: 'Conditions at scoring hold: CRWD/PANW/Microsoft platform encroachment
    has not materially impaired ZS''s large-enterprise zero-trust distribution position.'
  derived_from: 'competitive_advantage.distribution: 4 — ''large enterprise zero-trust
    base with strong channel, but facing platform encroachment from CRWD/PANW/Microsoft'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - ZS management discloses a declining win rate against named platform competitors
    in an earnings call or 10-Q risk-factor update
  - Net new ARR from the >$1M ARR customer cohort declines sequentially in a quarterly
    press release
  - A publicly named enterprise customer announces displacement of ZS by CRWD or PANW
    in a press release or regulatory filing
  confirmed_by:
  - ZS quarterly press release shows sequential growth in both the >$1M ARR and >$100K
    ARR customer cohorts
  - ZS press release discloses new Zero Trust enterprise additions at or above the
    prior-quarter pace
  - ZS announces a competitive displacement design win naming a displaced legacy vendor
    (not ZS) in a press release
  status: open
  status_source: draft
  pressure:
    confirm: 9.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: billings_watch_not_worsened
  statement: 'Conditions at scoring hold: the billings/deferred-revenue watch-item
    has not worsened — the gap between deferred revenue growth and revenue growth
    has not widened beyond the gap observed at the 4Q FY26 print.'
  derived_from: 'competitive_advantage.overall: 4 — ''billings scrutiny are the watch-items'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - ZS 10-Q shows deferred revenue YoY growth rate falling materially below 15% while
    revenue growth holds above 16%
  - ZS management explicitly characterizes deferred revenue or bookings trends as
    a forward demand headwind in an earnings call
  confirmed_by:
  - ZS 10-Q shows deferred revenue YoY growth rate converging toward the revenue growth
    rate
  - Organic net new ARR in the subsequent quarter meets or exceeds the low end of
    the FY27 ARR guide run-rate ($4.396B annual)
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: ai_data_sec_innovation_lead
  statement: 'Conditions at scoring hold: no competitor has shipped a GA product that
    closes the AI/data-security integration gap underlying the innovation-rate score
    of 4.'
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''SSE platform leadership
    expanding into AI/data security'''
  themes:
  - cybersecurity_competitive_landscape
  - enterprise_ai_adoption
  challenged_by:
  - PANW, CRWD, or Microsoft announces GA of an AI/data-security feature with disclosed
    enterprise customer adoption in a press release or 10-K product section
  - ZS management acknowledges losing a competitive bake-off on AI/data-security feature
    basis in an earnings call or analyst-day transcript
  confirmed_by:
  - ZS press release announces a new AI/data-security product module reaching GA with
    a disclosed enterprise customer count
  - ZS 10-Q or 10-K names AI/data-security as a contributing driver of net new ARR
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 20.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: security_first_ai_positioning
  statement: ZS's AI-positioning score of 3 reflects a security-first architecture
    where AI is applied to threat detection and data protection, and no AI-native
    competitor has won material enterprise deals against ZS on an AI-feature basis
    at scoring.
  derived_from: 'ai_positioning: 3 — ''Security-first, not AI-first; 3+ on AI-security
    feature expansion'''
  themes:
  - enterprise_ai_adoption
  - ai_infrastructure_software
  challenged_by:
  - An AI-native security vendor publicly discloses enterprise design wins displacing
    ZS in a press release or customer case study
  - ZS management acknowledges losing competitive evaluations on AI-feature basis
    in an earnings call or conference transcript
  confirmed_by:
  - ZS press release announces a new AI-security capability reaching GA with named
    enterprise customer adoptions
  - ZS earnings call Q&A contains no analyst or management commentary attributing
    losses to an AI-feature gap
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 9.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: decel_not_displacement
  statement: 'Conditions at scoring hold: the constraint on investor interest is growth
    deceleration and billings scrutiny, not reported evidence of active competitive
    displacement in ZS''s customer base.'
  derived_from: 'potential_investor_interest.score: 3 — ''platform competition and
    billings/growth-deceleration scrutiny make it less of a momentum name than CRWD.
    Factors: sector, growth (decelerating); competition cap'''
  themes:
  - cybersecurity_competitive_landscape
  challenged_by:
  - ZS management attributes net new ARR deceleration to competitive displacement
    in an earnings call or 8-K
  - A quarterly press release shows organic net new ARR below the low end of the FY27
    guided ARR pace ($4.396B annual rate) without a macro explanation from management
  confirmed_by:
  - ZS quarterly press release shows organic net new ARR at or above the low end of
    the FY27 guided pace with no competitive-displacement language from management
    or in analyst Q&A
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 7.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
