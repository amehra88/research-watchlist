---
doc_type: thesis
ticker: STX
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#STX
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: nearline_pricing_actions_hold
  statement: The nearline pricing actions that lifted FY2026 gross margin to 46% (from
    35%) were intact at the time of scoring.
  derived_from: MD&A (unscored) — "favorable pricing actions undertaken by the Company"
    cited as primary driver of 34% revenue growth and 11pp gross margin expansion
  themes: []
  challenged_by:
  - STX next 10-Q reports gross margin below 44%, signaling a pricing rollback
  - A major hyperscaler publicly discloses a multi-year nearline HDD supply agreement
    with WDC or Toshiba at prices below current STX contract ASPs
  confirmed_by:
  - STX next quarterly earnings press release reports nearline ASP flat or higher
    quarter-over-quarter
  - STX management reaffirms pricing-strategy language without disclosing new volume-discount
    arrangements in next earnings filing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: datacenter_80pct_mix_holds
  statement: Data center revenue constituting 80% of STX total revenue — as reported
    for FY2026 — was the prevailing mix at the time of scoring.
  derived_from: 'MD&A (unscored) — "Revenues by Market (%): Data Center 80%" in FY2026
    vs. 75% in FY2025'
  themes: []
  challenged_by:
  - Next STX 10-K or 10-Q discloses data center revenue share below 75%
  - STX management attributes a sequential revenue decline to softening cloud or hyperscaler
    nearline orders in a public earnings call
  confirmed_by:
  - Next STX annual or quarterly filing reports data center as 80% or more of total
    revenue
  - Nearline exabyte shipments in the next reported period meet or exceed 695 EB
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: supply_discipline_conditions_present
  statement: The industry supply-discipline conditions that underpinned STX's pricing
    strategy were present at the time of scoring.
  derived_from: MD&A (unscored) — "executing our pricing strategy and maintaining
    supply discipline ... provide greater visibility into future demand trends"
  themes: []
  challenged_by:
  - Third-party HDD exabyte shipment data (e.g., Trendfocus quarterly report) shows
    industry supply growth outpacing demand for two consecutive quarters
  - WDC or Toshiba publicly announces a nearline HDD manufacturing capacity expansion
    via a press release or investor presentation
  confirmed_by:
  - STX next earnings press release reaffirms supply-discipline language without announcing
    incremental capacity additions
  - Distributor lead-time data from trade publications shows nearline HDD lead times
    unchanged or lengthening at the next quarterly check
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
