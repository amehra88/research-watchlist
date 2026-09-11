---
doc_type: thesis
ticker: ANET
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#ANET
- notes/ANET/20260805-2Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: eos_platform_no_competing_qual
  statement: 'Conditions at scoring still hold: no Tier-1 hyperscaler had qualified
    a non-EOS switching platform to replace Arista spines in an AI cluster, sustaining
    the basis for the innovation-rate score of 4.'
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''EOS software + merchant-silicon
    (Broadcom Tomahawk/Jericho) leadership in high-radix switching'''
  themes:
  - networking_competitive_landscape
  challenged_by:
  - A Tier-1 hyperscaler announces qualification of a competing software platform
    (white-box NOS or vendor alternative) for AI-cluster spine switching in a press
    release, 8-K, or earnings call
  confirmed_by:
  - A new hyperscaler or neocloud Etherlink design win is disclosed in a press release,
    8-K, or earnings call after the scoring date
  status: open
  status_source: draft
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: supply_binding_not_demand
  statement: 'Conditions at scoring still hold: the binding constraint on ANET revenue
    conversion was supply availability—evidenced by $9.7B in purchase commitments
    and $600M sequential product-deferred-revenue growth—not demand erosion or competitive
    displacement.'
  derived_from: 'ai_positioning: 4 — ''supply — not demand or competition — is now
    the governor of the model'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - Purchase commitments decline below $9.7B in the next 10-Q filing
  - Product deferred revenue declines q/q in the next 10-Q filing
  confirmed_by:
  - Purchase commitments meet or exceed $9.7B in the next 10-Q filing
  - Product deferred revenue increases q/q in the next 10-Q filing
  status: open
  status_source: draft
  pressure:
    confirm: 11.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: concentration_not_eased_at_scoring
  statement: 'Conditions at scoring still hold: hyperscaler and AI-lab customer concentration
    had not improved materially from the level that capped the distribution score
    at 4; a potential new AI-lab customer expected to cross 10% of revenue in Q4 was
    an additional concentration event, not a diversification event.'
  derived_from: 'competitive_advantage.distribution: 4 — ''heavily hyperscaler-concentrated
    (large Microsoft/Meta revenue exposure) — single-customer-cluster concentration
    risk'''
  themes:
  - hyperscaler_revenue_concentration
  challenged_by:
  - Enterprise plus campus revenue exceeds 20% of quarterly revenue per a 10-Q filing,
    evidencing material diversification away from hyperscalers
  confirmed_by:
  - A new 10%-plus customer in an AI-lab category is disclosed in a Q4 FY26 or subsequent
    10-Q or 10-K filing
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: nvda_scaleup_domain_holds
  statement: 'Conditions at scoring still hold: NVIDIA InfiniBand and Spectrum-X held
    the NVLink scale-up domain and Ethernet displacement in that domain had not begun
    ahead of the two-to-three-year horizon described at scoring, leaving this the
    cited cap on the overall competitive-advantage score of 4.'
  derived_from: 'competitive_advantage.overall: 4 — ''concentration + NVDA Spectrum-X
    competition cap it at 4'''
  themes:
  - networking_competitive_landscape
  - ai_compute_topology
  challenged_by:
  - A Tier-1 hyperscaler discloses an Ethernet-based NVLink-class scale-up cluster
    deployment in an earnings call, press release, or 8-K
  confirmed_by:
  - NVIDIA reports InfiniBand attach-rate growth in its next two quarterly earnings
    reports, indicating no large-scale Ethernet displacement in the scale-up domain
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: scale_across_no_competing_win
  statement: 'Conditions at scoring still hold: no competing vendor had won a disclosed
    scale-across (distributed, multi-site AI networking) design at a Tier-1 hyperscaler
    that would challenge the architecture leadership cited in the AI-positioning score
    of 4.'
  derived_from: 'ai_positioning: 4 — ''scale-across switching/routing TAM cited at
    "$15 billion to $20 billion in 2030"'''
  themes:
  - ai_compute_topology
  - networking_competitive_landscape
  challenged_by:
  - A competing networking vendor announces a scale-across design win at a Tier-1
    hyperscaler in a press release, 8-K, or earnings call transcript
  confirmed_by:
  - ANET discloses additional Etherlink scale-across design wins at Tier-1 hyperscalers
    or neoclouds in a press release or earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ai_fabrics_target_supply_gated
  statement: 'Conditions at scoring still hold: the AI fabrics FY26 target of at least
    $3.5B was described as supply-gated and conservatively held; the target had not
    been reduced or withdrawn due to competitive pressure at the time of scoring.'
  derived_from: 'ai_positioning: 4 — ''AI fabrics guide ≥$3.5B''; earnings note flags
    ''AI line may be supply-gated / conservatively held'''
  themes:
  - ai_infrastructure_capex
  - networking_competitive_landscape
  challenged_by:
  - ANET reduces or withdraws the $3.5B AI fabrics FY26 target in an earnings call
    or press release, citing competitive displacement as the cause
  confirmed_by:
  - ANET reaffirms or raises the AI fabrics target in its next quarterly earnings
    call without citing competitive displacement
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
