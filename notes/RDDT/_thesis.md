---
doc_type: thesis
ticker: RDDT
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#RDDT
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: rddt_arpu_expansion_not_at_ceiling
  statement: 'Advertiser demand per DAUq is not at a ceiling: ARPU of $6.18 (+36%
    YoY) at Q2 2026 implies ad pricing or inventory fill has not yet saturated'
  derived_from: 'themes: ad_market_strength — MD&A: ''Average revenue per unique was
    $6.18 for the three months ended June 30, 2026, an increase of 36% year-over-year'''
  themes:
  - ad_market_strength
  challenged_by:
  - Q3 2026 10-Q filing showing ARPU growth rate decelerating materially below Q2's
    36% YoY without a volume offset
  - Earnings call or 8-K disclosing a named large-advertiser pullback or CPM pricing
    compression in the subsequent quarter
  confirmed_by:
  - Q3 2026 10-Q filing showing ARPU growth at or above 36% YoY
  - Full-year 2026 guidance raise for revenue per unique in a subsequent earnings
    release
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 8.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: search_referral_traffic_still_material
  statement: Search engine referral traffic is a material DAUq driver at the scoring
    date, such that third-party algorithm changes can move the total DAUq metric in
    a reported quarter
  derived_from: 'themes: search_disruption — MD&A: ''change in global DAUq...was primarily
    driven by the combination of third-party search engine algorithm changes''; news:
    ''Reddit stock declines as concerns over falling search referral traffic weigh
    on sentiment'''
  themes:
  - search_disruption
  challenged_by:
  - Q3 2026 10-Q MD&A omitting third-party search algorithm changes as a cited DAUq
    driver
  - Company disclosure that logged-out or search-sourced sessions have declined below
    a cited materiality threshold
  confirmed_by:
  - Q3 2026 10-Q citing third-party search algorithm changes as a DAUq driver for
    a second consecutive quarter
  - Investor day or filing quantifying search as a top-two acquisition channel with
    a stated share of total sessions
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ai_data_licensing_contracts_intact
  statement: AI data-licensing agreements flagged as a watch-item at the scoring date
    have not been disclosed as cancelled or non-renewed as of that date
  derived_from: 'themes: ai_re_architected_incumbent — news summary: ''More relevant
    triggers would be advertising revenue trends or progress on AI data-licensing
    agreements'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - 8-K or press release disclosing non-renewal or termination of a named AI data-licensing
    agreement
  - 10-Q note showing licensing revenue bundled into 'Other' with a sequential decline
    and no offsetting disclosure
  confirmed_by:
  - Press release or 8-K announcing renewal or expansion of a named AI data-licensing
    agreement
  - 10-Q or 10-K disclosing a separate data-licensing revenue line item with a year-over-year
    increase
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `thin` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
