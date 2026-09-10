---
doc_type: thesis
ticker: NOW
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#NOW
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: now_ai_contract_value_at_1b
  statement: NOW's AI contract value was at or above $1B at the time of scoring, representing
    enterprise AI spend that had crossed from exploratory to committed bookings.
  derived_from: 'news: AI contract milestone — "enterprise AI spend is moving from
    exploration to committed revenue — a bellwether for the broader SaaS AI monetization
    thesis"'
  themes:
  - enterprise_ai_adoption
  - ai_agent_monetization
  challenged_by:
  - Q3 2026 earnings filing or investor day disclosure showing AI contract value below
    $1B or explicitly restated downward
  - Earnings call transcript in which management declines to reaffirm the $1B figure
    or attributes it to non-recurring deals
  confirmed_by:
  - Q3 2026 10-Q or supplemental filing explicitly disclosing AI contract value at
    or above $1B
  - Management reiteration of the $1B milestone with sequential or YoY growth figures
    on next earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: now_rpo_growth_at_scoring
  statement: RPO of $29.0B and cRPO growing 21% YoY as of June 30, 2026 are the backlog
    conditions present at scoring; those growth rates had not decelerated in the intervening
    period.
  derived_from: 'MD&A: RPO — "RPO was $29.0 billion, of which 46% represented cRPO.
    RPO and cRPO both increased by 21% compared to June 30, 2025"'
  themes:
  - ai_infrastructure_software
  - enterprise_ai_adoption
  challenged_by:
  - Sept 30, 2026 10-Q showing cRPO YoY growth below 21%
  - Intra-quarter 8-K or investor conference filing disclosing deal slippage or contract
    restructuring reducing cRPO
  confirmed_by:
  - Sept 30, 2026 10-Q disclosing cRPO growth at or above 21% YoY
  - Q3 2026 earnings release reaffirming RPO trajectory with no contract cancellations
    flagged
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: now_q2_selloff_not_fundamental
  statement: The post-Q2 price decline was not accompanied by fundamental deterioration
    in NRR or AI SKU mix at the time of scoring.
  derived_from: 'news: Q2 reaction — "''sell the news'' reaction to a strong print
    is a direct signal on how much AI upside is already discounted... selloff may
    represent a re-entry point rather than a thesis break"'
  themes:
  - ai_re_architected_incumbent
  - enterprise_ai_adoption
  challenged_by:
  - Q3 2026 10-Q or earnings supplement disclosing net revenue retention below the
    prior quarter's level
  - Earnings call transcript in which management discloses AI SKU attach rate deceleration
    or customer down-sizing of AI workflow licenses
  confirmed_by:
  - Q3 2026 earnings release reporting NRR at or above Q2 2026 levels
  - Supplemental filing or earnings call disclosing AI SKU mix expansion relative
    to Q2 2026
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
