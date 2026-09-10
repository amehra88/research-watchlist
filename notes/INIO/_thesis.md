---
doc_type: thesis
ticker: INIO
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#INIO
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: dc_power_contract_activity
  statement: As of the scoring date, gas reciprocating engine solutions are being
    actively evaluated or contracted for data center prime/backup power by at least
    one named customer, not merely cited as an addressable market in management commentary.
  derived_from: thin — 'our modular, high–efficiency systems are ideally positioned
    to deliver the prime and backup power required to sustain intensive AI workloads'
  themes: []
  challenged_by:
  - Two consecutive 10-Q Equipment segment filings show data center revenue flat or
    declining as a share of segment total
  - A major hyperscaler publicly selects a competing distributed-power technology
    (fuel cell, small modular reactor, grid-tied battery) for AI campus buildout in
    an 8-K or press release
  confirmed_by:
  - INIO discloses a named data center customer or signed contract in a 10-Q, 8-K,
    or earnings call transcript
  - A data center operator files a building permit or press release explicitly citing
    Jenbacher or Waukesha engine systems
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: services_captive_rate_holds
  statement: INIO's proprietary component design prevents third-party suppliers from
    capturing a material share of aftermarket service revenue from the approximately
    44 GW installed base, as conditions stood at the scoring date.
  derived_from: thin — 'The proprietary design of many critical components positions
    us to capture a substantial majority of the life cycle service and parts opportunity'
  themes: []
  challenged_by:
  - A third-party aftermarket parts supplier publicly announces qualification of interchangeable
    components for Jenbacher J-series or Waukesha VGF engines
  - Services segment revenue per installed-GW declines in two consecutive quarterly
    filings relative to prior-year comparable periods
  confirmed_by:
  - Services segment gross margin stable or expanding in sequential 10-Q filings relative
    to the IPO prospectus baseline
  - Multi-year service agreement backlog disclosed in a 10-Q grows year-over-year
    in absolute dollar terms
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: pe_sovereign_secondary_absent
  statement: The Advent/ADIA combined 86.2% ownership does not result in a registered
    secondary offering or disclosed block sale during the scoring window, leaving
    float conditions as they stood at the scoring date.
  derived_from: thin — 'Advent International and ADIA collectively hold an 86.2% stake'
    per ownership disclosure filing
  themes: []
  challenged_by:
  - SEC filing of an S-1, F-1, or S-3 shelf registration statement by AI Alpine (Luxembourg)
    S.à r.l. or a named Advent/ADIA entity for resale of INIO shares
  - A Form 4 or SC 13D/A filing discloses a principal-shareholder block sale reducing
    aggregate PE/sovereign ownership below 80%
  confirmed_by:
  - No secondary registration statement appears on SEC EDGAR for INIO in the two quarters
    following the scoring date
  - Lock-up expiry date (per IPO prospectus) passes without a disclosed secondary
    offering or Form 144 filing by a principal shareholder
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
