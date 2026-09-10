---
doc_type: thesis
ticker: DPC
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#DPC
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: aerospace_igt_super_cycle_conditions
  statement: The conditions described at scoring — aerospace and IGT end markets in
    demand super cycles with OEM backlogs extending into the 2030s — were present
    in the H1 2026 filings that informed the position initiation.
  derived_from: SCORING NOTES — 'aerospace/defense supply chain + IGT demand tied
    to data-center / grid power buildout'; MD&A — 'both of which are experiencing
    demand super cycles' and 'customer order backlogs currently extend well into the
    2030s'
  themes: []
  challenged_by:
  - A published OEM (GE Aerospace, Rolls-Royce, or Safran) 8-K or investor-day filing
    disclosing a production-rate reduction on programs DPC supplies
  - DPC 10-Q showing combined aerospace + IGT revenue share falling below the 80.3%
    reported for H1 2026
  confirmed_by:
  - DPC next 10-Q showing combined aerospace + IGT revenue share at or above 80.3%
    and management reaffirming backlog visibility in MD&A
  - A major OEM investor-day filing reaffirming narrow-body or IGT production-rate
    ramp targets for current programs
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: igt_demand_grid_power_linkage
  statement: The PM's read-through that IGT demand is 'tied to data-center / grid
    power buildout' implies IGT segment revenue at scoring was driven by new gas-fired
    capacity additions linked to electricity grid expansion, not legacy industrial
    plant replacement.
  derived_from: SCORING NOTES — 'IGT demand tied to data-center / grid power buildout';
    MD&A — 'increasing global electricity demand that current grid infrastructure
    cannot maintain is enhancing the demand for natural gas and our IGT parts'
  themes: []
  challenged_by:
  - DPC management attributes IGT revenue growth to legacy plant replacement rather
    than new-unit capacity in a subsequent 10-Q or earnings transcript
  - IGT segment revenue declines in back-to-back quarterly filings concurrent with
    disclosed growth in data-center power capex commitments by hyperscalers
  confirmed_by:
  - DPC 10-Q or earnings transcript explicitly cites new gas-turbine capacity orders
    linked to grid expansion or data-center power demand as the IGT growth driver
  - A major gas-turbine OEM (GE Vernova or Siemens Energy) press release disclosing
    new-unit order volume increases and citing data-center power as the demand source
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: q2_loss_widening_ipo_one_time
  statement: The Q2 2026 net loss of $131.1M on $268.7M revenue — versus a $49.4M
    loss on $200.9M in Q2 2025 — was attributable at scoring to IPO-related SG&A ($189.6M,
    +324% YoY), implying that absent those charges the underlying unit economics were
    not the source of loss widening.
  derived_from: SCORING NOTES — 'BCTK initiated 0.67% position late June'; MD&A —
    Q2 2026 net loss $(131.1)M, SG&A $(189.6)M (+324% YoY), adjusted EBITDA $47.8M
    at 17.8% margin; RECENT NEWS — 'Revenue momentum offset by widening losses; mixed
    signal'
  themes: []
  challenged_by:
  - DPC next 10-Q showing SG&A elevated above normalized pre-IPO quarterly run rate
    with no disclosed one-time charges, indicating a structural cost-base increase
  - Adjusted EBITDA margin in the next quarterly filing declining below the 17.4%
    reported for H1 2026 with no offsetting disclosed item
  confirmed_by:
  - DPC next 10-Q MD&A or footnotes explicitly quantifying IPO transaction costs included
    in Q2 2026 SG&A and showing those charges absent in the subsequent period
  - Adjusted EBITDA margin in the next quarterly filing at or above 17.8% (Q2 2026
    reported level)
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
