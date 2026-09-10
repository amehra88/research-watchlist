---
doc_type: thesis
ticker: FRVO
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#FRVO
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '3'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: frvo_google_partnership_disclosed
  statement: A Google partnership exists as a disclosed business relationship, not
    solely an operator inference.
  derived_from: 'ai_positioning: 4 — ''Google partner (per operator)... the Google
    partnership is a validation signal'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - FRVO S-1 or 10-K lists no Google entity as a customer, partner, or counterparty
  confirmed_by:
  - 8-K, press release, or prospectus discloses a signed agreement with a Google entity
    in AI power or energy
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: frvo_ai_datacenter_power_primary_biz
  statement: FRVO's primary disclosed business is power or energy supply to AI datacenters.
  derived_from: 'ai_positioning: 4 — ''squarely AI-positioned datacenter-power/AI-energy
    name'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - S-1 or 10-K shows the primary revenue segment is not AI datacenter power or energy
  confirmed_by:
  - S-1 or 10-K designates AI datacenter power or energy as the primary disclosed
    revenue segment
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: frvo_google_anchor_narrow_base
  statement: 'Narrow-customer-base conditions at scoring still hold: Google is the
    anchor customer and no additional disclosed customers are material.'
  derived_from: 'competitive_advantage.distribution: 3 — ''the Google partnership
    is a strong anchor customer but the base is narrow'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - 10-Q or 10-K discloses a second customer contributing material revenue alongside
    Google
  confirmed_by:
  - 10-Q or 10-K shows a Google entity as the sole or majority revenue contributor
    with no other named material customers
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: frvo_lockup_conditions_at_scoring
  statement: Post-IPO lock-up overhang conditions observed at scoring still hold.
  derived_from: 'potential_investor_interest: 3 — ''Lock-up overhang and limited track
    record temper it'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - SEC prospectus supplement or 8-K confirms the IPO lock-up expiration date has
    passed
  confirmed_by:
  - Prospectus or SEC filing confirms the lock-up period was active as of the scoring
    date and expiration has not yet occurred
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: frvo_pre_first_earnings_cycle
  statement: At scoring, FRVO had not completed its first public earnings cycle, leaving
    financial track record unestablished.
  derived_from: 'potential_investor_interest: 3 — ''early and unproven as a public
    company... limited track record'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - FRVO SEC filing history shows two or more quarterly earnings reports filed as
    a public company prior to the scoring date
  confirmed_by:
  - FRVO SEC filing history shows fewer than two quarterly earnings reports filed
    before the scoring date
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: frvo_google_halo_lifts_positioning
  statement: The Google partnership is the primary basis for ai_positioning being
    scored at 4, above the analyst-draft score of 3.
  derived_from: 'ai_positioning: 4 — ''operator-set, above analyst-draft 3... the
    Google partnership is a validation signal'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - FRVO files a material-event 8-K disclosing loss or termination of the Google relationship
  - Google publicly denies an active partnership with FRVO in AI power or energy
  confirmed_by:
  - Prospectus or contract announcement confirms an active Google engagement in AI
    power or energy that post-dates the IPO filing
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
