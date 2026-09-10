---
doc_type: thesis
ticker: ASML
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#ASML
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '5'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: euv_no_leading_edge_competitor
  statement: At scoring, no EUV-class tool from a competitor had been qualified at
    a leading-edge fab for advanced-node production.
  derived_from: 'competitive_advantage.innovation_rate: 5 — ''EUV/High-NA monopoly
    — no leading-edge competitor'''
  themes:
  - lithography_roadmap
  challenged_by:
  - A non-ASML EUV-class exposure tool receives process qualification at TSMC, Samsung,
    or Intel Foundry for a sub-5nm node, as disclosed in a customer earnings call,
    press release, or SEC filing
  confirmed_by:
  - TSMC, Samsung, or Intel Foundry capital-equipment procurement disclosures in earnings
    or annual filings listing only ASML for EUV-class exposure steps at leading-edge
    nodes
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: leading_edge_fab_euv_required
  statement: At scoring, no volume sub-3nm node had been demonstrated at a leading-edge
    fab without EUV tools.
  derived_from: 'competitive_advantage.distribution: 5 — ''every leading-edge fab
    must buy EUV'''
  themes:
  - foundry_capacity
  - lithography_roadmap
  challenged_by:
  - A leading-edge foundry tapes out or achieves yield on a sub-3nm process at volume
    using DUV multi-patterning only, as confirmed in a technical disclosure, process
    qualification announcement, or earnings statement
  confirmed_by:
  - ASML EUV shipment and installed-base data per quarterly earnings consistent with
    exclusive EUV use across all fabs running sub-3nm nodes in production
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: china_export_drag_at_scoring_scope
  statement: At scoring, Dutch and US export-control restrictions were limiting ASML
    tool sales to China at the scope in force as of scoring date.
  derived_from: 'ai_positioning: 4 — ''China-export drag''; potential_investor_interest:
    4 — ''China export-control revenue drag'''
  themes:
  - china_export_controls
  challenged_by:
  - Dutch or US government expands export restrictions to additional ASML tool categories
    beyond those in force at scoring, as announced by a regulatory authority or disclosed
    in an ASML filing or earnings call
  confirmed_by:
  - ASML quarterly earnings disclosing China revenue as a share of total revenue and
    tool categories shipped to China consistent with the restriction scope in force
    at scoring
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: order_book_lumpy_conversion
  statement: At scoring, ASML's order-to-revenue timing was subject to variability
    that the PM treated as a cap on both ai_positioning and investor interest scores.
  derived_from: 'ai_positioning: 4 — ''lumpy order-timing''; potential_investor_interest:
    4 — ''lumpy order book'''
  themes:
  - semiconductor_cycle
  challenged_by:
  - ASML discloses a material order cancellation, customer-requested delivery deferral,
    or backlog drawdown in an earnings release or ad-hoc order-intake update that
    exceeds the variability implied at scoring
  confirmed_by:
  - ASML order-intake and backlog figures in quarterly earnings consistent with the
    conversion-timing variability reflected in the scoring-date assessment, without
    step-change cancellations or deferrals
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: high_na_ramp_sub2nm_at_scoring
  statement: At scoring, High-NA EUV tool ramp for sub-2nm node development was underway
    at one or more leading-edge customers.
  derived_from: 'ai_positioning: 4 — ''Trending 4+ as High-NA EUV ramps for sub-2nm
    AI nodes'''
  themes:
  - lithography_roadmap
  - semiconductor_cycle
  challenged_by:
  - A leading-edge customer (TSMC, Samsung, or Intel Foundry) postpones, cancels,
    or defers High-NA EUV tool acceptance or integration into a node roadmap, as disclosed
    in an ASML earnings release, customer filing, or press release
  confirmed_by:
  - ASML earnings or filing reports High-NA EUV tool shipment acceptance or process-integration
    milestone at TSMC, Samsung, or Intel Foundry for a sub-2nm development node
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ai_demand_one_step_removed
  statement: At scoring, ASML's AI-driven revenue exposure was mediated entirely through
    foundry and IDM capex decisions, not through any direct arrangement with fabless
    AI chip designers.
  derived_from: 'ai_positioning: 4 — ''indispensable, but one step removed from AI
    compute'''
  themes:
  - foundry_capacity
  - semiconductor_cycle
  challenged_by:
  - A fabless AI chip designer or hyperscaler custom-silicon team publicly announces
    a direct EUV tool co-development agreement or procurement arrangement with ASML,
    as disclosed in a press release, SEC filing, or earnings call
  confirmed_by:
  - ASML annual report customer-concentration disclosures confirming all tool revenue
    flows through foundry or IDM customers, with no direct fabless AI designer in
    the customer base
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
