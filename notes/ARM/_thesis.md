---
doc_type: thesis
ticker: ARM
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#ARM
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: arm_ai_chip_corr_licensing
  statement: ARM's price co-movement with AI chip names at scoring reflects material
    royalty revenue exposure to AI compute silicon, not only broad sector sympathy.
  derived_from: 'RECENT NEWS: — "ARM''s continued co-movement with AI chip names confirms
    its role as an AI compute proxy"'
  themes:
  - silicon_architecture_competition
  - inference_compute_economics
  challenged_by:
  - ARM earnings print showing AI/compute royalty revenue flat or declining in a quarter
    when NVDA or AMD revenue grows materially
  - ARM disclosing that correlated price moves were not accompanied by corresponding
    royalty backlog or bookings increases
  confirmed_by:
  - ARM earnings disclosing AI-specific royalty revenue growing faster than total
    company royalty revenue
  - A hyperscaler filing or investor day quantifying volume of ARM-architecture chips
    deployed in inference clusters
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: arm_arch_no_qualified_alt
  statement: At scoring, no competing ISA has reached production-scale qualification
    at a major hyperscaler that would displace ARM architecture in AI inference silicon.
  derived_from: 'RECENT NEWS: — "persistent retail attention on ARM''s valuation relative
    to its silicon architecture opportunity is a background sentiment indicator"'
  themes:
  - chip_design_competition
  - silicon_architecture_competition
  challenged_by:
  - A hyperscaler filing or press release announcing production deployment of a RISC-V-based
    AI inference chip at volume scale
  - An ARM licensee publicly announcing qualification of a second-source ISA for its
    next-generation AI accelerator program
  confirmed_by:
  - ARM disclosing a new compute subsystem license with a named AI chip customer in
    an SEC filing or earnings call
  - A hyperscaler announcing renewal or expansion of an ARM architecture license for
    data center or AI silicon
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: arm_anet_capex_additive
  statement: At scoring, AI infrastructure capex directed at compute silicon (ARM's
    addressable layer) and at networking (ANET's addressable layer) is treated as
    additive by hyperscalers, not as substitutable budget lines.
  derived_from: 'RECENT NEWS: — "ANET and ARM represent complementary layers of the
    AI infrastructure stack — switching and CPU/accelerator architecture — and their
    comparative growth rates inform where incremental AI capex is landing"'
  themes:
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - ARM and ANET reporting divergent revenue trajectories in the same quarter alongside
    a hyperscaler earnings call disclosing an explicit reallocation between compute
    silicon and networking budgets
  - A hyperscaler 10-Q or investor day disclosing a single consolidated AI infrastructure
    capex envelope where compute and networking compete for share
  confirmed_by:
  - ARM and ANET both reporting accelerating revenue in the same reporting quarter
    with hyperscalers citing parallel ramps in compute and networking spend
  - A hyperscaler investor day presenting separate, independently growing budget lines
    for compute silicon procurement and networking infrastructure
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
