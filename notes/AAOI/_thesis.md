---
doc_type: thesis
ticker: AAOI
tier: null
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#AAOI
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: aaoi_domestic_laser_fab_advantage
  statement: At the time of scoring, AAOI's domestic laser chip manufacturing in Sugar
    Land, TX functions as a qualifying criterion for at least a subset of data center
    customers.
  derived_from: MD&A overview — 'we believe that many of our customers prefer to source
    key components from suppliers who have domestic manufacturing capacity'
  themes: []
  challenged_by:
  - A top-3 AAOI data center customer qualifies an Asian-sourced laser chip alternative
    (disclosed via design-win announcement, supply agreement filing, or competitor
    press release)
  - AAOI 10-Q or 10-K discloses reduction in Sugar Land capacity utilization without
    an offsetting volume explanation
  confirmed_by:
  - New data center design win citing domestic-supply or ITAR/export-control requirement
    in a press release or 8-K
  - Sequential revenue growth in the internet data center segment in the next filed
    10-Q alongside flat or reduced China-facility headcount
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: aaoi_ai_dc_demand_active
  statement: At the time of scoring, AI data center retooling is an active, not merely
    anticipated, demand driver for AAOI's higher-speed optical products.
  derived_from: MD&A overview — 'AI workloads are fueling the retooling of existing
    data centers and the construction of purpose-built data centers for AI, in both
    cases significantly increasing demand for higher speed optical networking technology'
  themes: []
  challenged_by:
  - A hyperscaler customer discloses a pause or reduction in optical interconnect
    procurement in an earnings call or 8-K
  - AAOI data center segment revenue declines sequentially in the next filed 10-Q
    without a disclosed product-transition explanation
  confirmed_by:
  - AAOI internet data center segment revenue grows sequentially in the next filed
    10-Q
  - A hyperscaler issues a new optical transceiver qualification notice or purchase
    order expansion disclosed in an AAOI 8-K or press release
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: aaoi_catv_return_path_active
  statement: At the time of scoring, MSO return-path bandwidth upgrade spending constitutes
    an active procurement cycle, not a deferred one, for AAOI's CATV segment.
  derived_from: MD&A overview — 'the desire by CATV multiple system operators to increase
    the return-path bandwidth available to offer to their customers'
  themes: []
  challenged_by:
  - A major MSO (Charter, Comcast, Cox) discloses capex reduction or program delay
    on DOCSIS 3.1/4.0 return-path upgrades in an earnings call or 8-K
  - AAOI CATV segment revenue declines two consecutive quarters in filed 10-Qs
  confirmed_by:
  - AAOI CATV segment revenue grows sequentially in the next filed 10-Q
  - An MSO issues a new equipment RFP or design-win award for return-path amplifiers
    disclosed in an AAOI press release or SEC filing
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
