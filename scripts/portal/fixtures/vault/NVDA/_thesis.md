---
doc_type: thesis
ticker: NVDA
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#NVDA
- notes/NVDA/20260521-1Q27.md
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '5'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: cuda_dev_lock_in_distribution_moat
  statement: At scoring date, the NVDA developer base constitutes the primary mechanism
    supporting a competitive_advantage.distribution score of 5.
  derived_from: 'competitive_advantage.distribution: 5 — "Customer lock-in via developer
    base"'
  themes:
  - silicon_architecture_competition
  challenged_by:
  - A hyperscaler publicly announces production-scale deployment of a non-CUDA accelerator
    without a CUDA compatibility layer
  confirmed_by:
  - A hyperscaler 10-K or earnings disclosure citing CUDA as the only approved runtime
    for production AI workloads
  status: challenged
  status_source: evidence
  pressure:
    confirm: 6.0
    challenge: 17.5
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
---

# NVDA — thesis

Developer lock-in via [[NVDA]] CUDA remains the core moat claim; tracked under [[themes/silicon_architecture_competition|silicon_architecture_competition]].
