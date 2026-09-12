---
doc_type: thesis
ticker: MU
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MU
- notes/MU/20260624-2Q26.md
- notes/MU/20260625-3Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: mu_nvda_hbm_qual_holds
  statement: MU held NVDA HBM qualification at the time of scoring; that qualification
    had not been displaced by an alternative supplier.
  derived_from: 'ai_positioning: 4 — ''gaining qualification share at NVDA'''
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - NVDA press release or SEC filing names a new HBM supplier displacing MU in a next-generation
    platform design win
  - MU 10-Q or 8-K discloses loss of a major HBM customer or cancellation of an HBM
    supply agreement
  confirmed_by:
  - MU or NVDA press release or SEC filing confirms MU as an HBM supplier on a new
    named NVDA platform
  - MU earnings disclosure itemizes HBM revenue growth attributable to NVDA platform
    shipments in a subsequent 10-Q
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: sk_hynix_hbm_lead_intact
  statement: At the time of scoring, SK Hynix led MU on HBM — the gap that caps MU's
    innovation-rate score at 4 rather than 5.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''follows SK Hynix (000660.KS)
    on HBM leadership'''
  themes:
  - hbm_competitive_landscape
  challenged_by:
  - A verified market-share report (e.g., TrendForce quarterly) published after scoring
    shows MU's HBM share at or above SK Hynix's share
  - MU press release or earnings filing discloses it achieved first-to-volume qualification
    on a new HBM generation before SK Hynix
  confirmed_by:
  - SK Hynix earnings filing (000660.KS) discloses higher HBM revenue or HBM bit-shipment
    volume than MU's equivalent disclosure for the same period
  - TrendForce or comparable supply-chain research published post-scoring places SK
    Hynix's HBM market share above MU's
  status: open
  status_source: draft
  pressure:
    confirm: 9.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: hbm_alloc_locking_ai_customers
  statement: At the time of scoring, HBM allocation to major AI customers was described
    as locking in — the condition that supports the distribution score of 4.
  derived_from: 'competitive_advantage.distribution: 4 — ''HBM allocation locking
    in with major AI customers'''
  themes:
  - hbm_competitive_landscape
  - ai_infrastructure_capex
  challenged_by:
  - A major AI customer (hyperscaler or AI accelerator OEM) redirects HBM sourcing
    away from MU, documented in a supply agreement termination, press release, or
    10-K supplier list update
  - MU 10-Q discloses a reduction in committed HBM purchase agreements or a material
    decline in AI-customer revenue concentration
  confirmed_by:
  - MU press release or earnings filing announces a new multi-year HBM supply agreement
    with a named AI hyperscaler or accelerator OEM
  - MU 10-K or 10-Q identifies binding take-or-pay HBM contracts with AI customers
    as a revenue backlog line item
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: dram_cyclicality_caps_inv_interest
  statement: At the time of scoring, commodity DRAM cyclicality constituted a material
    cap on MU's investor interest score — holding it at 4 rather than 5.
  derived_from: 'potential_investor_interest.score: 4 — ''Held below 5 on DRAM cyclicality
    and cycle-timing risk'''
  themes:
  - semiconductor_cycle
  - nand_demand_cycle
  challenged_by:
  - MU 10-K or 10-Q discloses that non-cancellable supply agreements cover the majority
    of projected DRAM shipments for the next 12 months in a binding backlog disclosure,
    removing the primary cyclical exposure mechanism
  - MU earnings filing discloses exit from commodity DRAM product lines, concentrating
    revenue exclusively in HBM and specialty DRAM
  confirmed_by:
  - MU 10-Q filing reports a QoQ DRAM revenue decline exceeding 10%, evidencing cycle
    dynamics persist
  - MU management revises capex guidance downward citing weakening demand in a press
    release or 8-K
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 3.0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: china_export_ctrl_not_escalated
  statement: China export-control exposure, flagged as a watch-item at the time of
    scoring, had not escalated to a level causing material revenue or operational
    impact.
  derived_from: 'potential_investor_interest.score: 4 — ''China export-control exposure
    a watch-item'''
  themes:
  - china_export_controls
  challenged_by:
  - BIS or Commerce Department issues a new rule or Entity List addition that directly
    restricts MU's product shipments to China customers, documented in a Federal Register
    notice or MU 8-K
  - MU 10-Q or annual filing discloses a revenue impact from China export restrictions
    that management characterizes as material
  confirmed_by:
  - MU 10-Q filing period covers China-related revenue without new restriction disclosures
    or material-impact characterization
  - No new BIS rulemaking targeting commodity DRAM or NAND exports to China is published
    in a Federal Register notice during the review period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hbm_pricing_power_at_scoring
  statement: At the time of scoring, HBM commanded surging pricing power for MU —
    the condition underlying the ai_positioning score of 4.
  derived_from: 'ai_positioning: 4 — ''surging pricing power'''
  themes:
  - hbm_competitive_landscape
  - semiconductor_cycle
  challenged_by:
  - MU earnings filing or call transcript discloses a QoQ decline in HBM average selling
    price
  - TrendForce or DRAMeXchange publishes a report documenting HBM contract price declines
    covering the scoring period
  confirmed_by:
  - MU earnings filing discloses HBM ASP flat or higher QoQ in a subsequent 10-Q
  - MU 10-Q reports HBM revenue-per-bit rising year-over-year
  status: open
  status_source: draft
  pressure:
    confirm: 14.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
