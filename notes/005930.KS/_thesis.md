---
doc_type: thesis
ticker: 005930.KS
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#005930.KS
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: hbm3e_nvda_unqualified_at_scoring
  statement: Samsung HBM3E had not received NVIDIA production qualification at the
    time of scoring, leaving it behind SK Hynix and Micron in HBM3E supplier status.
  derived_from: 'ai_positioning: 3 — "behind SK Hynix and Micron on HBM3E qualification
    at NVDA"'
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - NVIDIA publicly names Samsung as a qualified HBM3E supplier in a press release,
    earnings call, or SEC filing
  - Samsung discloses an HBM3E volume purchase order from NVIDIA in a regulatory or
    investor filing
  confirmed_by:
  - Samsung absent from NVIDIA's qualified HBM vendor disclosures in subsequent quarterly
    filings or analyst-day materials
  - NVIDIA earnings call or 10-Q lists only SK Hynix and Micron as qualified HBM3E
    sources
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hbm4_catchup_unconfirmed_at_scoring
  statement: Samsung's HBM4 development had not produced a customer qualification
    or production commitment from a major AI chip buyer at the time of scoring.
  derived_from: 'ai_positioning: 3 — "3+ trajectory on an HBM4 catch-up shot"'
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - Samsung issues a press release or discloses in an earnings call a named HBM4 qualification
    by NVIDIA, AMD, Google, or a hyperscaler
  - A major AI chip buyer files a supply agreement or qualification notice referencing
    Samsung HBM4
  confirmed_by:
  - Samsung reports no HBM4 customer qualification through the next two earnings cycles
  - Competitor HBM4 qualifications announced while Samsung's remain unconfirmed in
    public disclosures
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: foundry_lags_tsmc_leading_edge
  statement: Samsung foundry held lower leading-edge capacity utilization and fewer
    leading-edge AI-chip customer wins than TSMC at the time of scoring.
  derived_from: 'competitive_advantage.innovation_rate: 3 — "leading-edge foundry
    execution lag SK Hynix/TSMC respectively"'
  themes:
  - semiconductor_cycle
  - ai_infrastructure_capex
  challenged_by:
  - Samsung foundry announces a named tape-out win for an AI accelerator at ≤3nm from
    an NVIDIA-, AMD-, or Apple-tier customer
  - Industry capacity data (e.g., TrendForce) shows Samsung closing TSMC's lead in
    ≤3nm revenue share by more than 5 percentage points quarter-over-quarter
  confirmed_by:
  - Subsequent TrendForce or analyst foundry share reports show Samsung ≤3nm revenue
    share unchanged or declining relative to TSMC
  - Samsung foundry segment operating loss or utilization disclosure in quarterly
    earnings remains below breakeven while TSMC ≤3nm is fully booked
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: samsung_no1_dram_nand_volume
  statement: Samsung held the largest global volume share in both DRAM and NAND at
    the time of scoring.
  derived_from: 'competitive_advantage.distribution: 5 — "largest DRAM/NAND maker
    plus a global consumer-electronics footprint"'
  themes:
  - semiconductor_cycle
  - nand_demand_cycle
  challenged_by:
  - 'TrendForce, IDC, or Omdia DRAM or NAND shipment report shows Samsung falling
    to #2 in either product by volume share'
  - A competitor discloses a DRAM or NAND capacity expansion that analysts estimate
    would displace Samsung's volume leadership within two quarters
  confirmed_by:
  - 'TrendForce or IDC quarterly shipment data confirms Samsung #1 in both DRAM and
    NAND volume share in the next reported period'
  - Samsung's own earnings disclosures reference continued share leadership in memory
    without qualification
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: governance_access_friction_present
  statement: A conglomerate governance discount and Korea-listing access friction
    were both present and unresolved at the time of scoring, acting as identifiable
    caps on foreign investor demand.
  derived_from: 'potential_investor_interest.score: 3 — "conglomerate/governance discount,
    and Korea-listing access friction temper appeal"'
  themes:
  - semiconductor_cycle
  challenged_by:
  - Samsung announces a material governance reform (e.g., holding-company restructuring,
    independent board expansion, or enhanced shareholder return commitment) in a KRX
    or SEC filing
  - A GDR, ADR, or secondary listing on a major Western exchange is announced or completed,
    reducing access friction for foreign investors
  confirmed_by:
  - No corporate governance restructuring or new shareholder return framework announced
    through the next annual general meeting
  - Samsung remains listed solely on KRX with no new depository receipt program disclosed
    in filings
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
