---
doc_type: thesis
ticker: SNPS
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#SNPS
- notes/SNPS/20260528-2Q26.md
- notes/SNPS/20260827-3Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: cadence_erosion_not_accelerating
  statement: The competitive distribution score of 4 prices in SNPS losing full-flow
    EDA account share to Cadence at the rate observed at scoring; no single named
    customer engagement has defected from a SNPS-led full-flow toolchain to a CDNS-led
    toolchain at a magnitude beyond what produced that score.
  derived_from: 'competitive_advantage.distribution: 4 — "entrenched but trajectorily
    eroding against Cadence; the duopoly framing alone overstates current strength"'
  themes:
  - chip_design_competition
  challenged_by:
  - Cadence disclosing full-flow technical win counts materially above SNPS's >30-wins
    figure in a consecutive quarter's prepared remarks or investor presentation
  - A named tier-1 fabless or hyperscaler publicly attributing a new design engagement
    to CDNS toolchain where SNPS was previously the incumbent, in a filing or earnings
    transcript
  confirmed_by:
  - SNPS disclosing full-flow technical win count at or above the >30 figure cited
    in 2Q26 prepared remarks in the next quarterly earnings filing
  - No analyst-identified SNPS-to-CDNS EDA account loss appearing in CDNS's own win
    disclosures or sell-side channel checks reported in public research
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: agentic_eda_pre_revenue_at_scoring
  statement: The ai_positioning score of 4 (not 4+) is premised on agentic EDA being
    in customer-evaluation phase at 20 customers with >25 agents; zero incremental
    commercial revenue from agentic tools is embedded in either the 2Q26 beat or the
    FY26 guidance range that produced the score.
  derived_from: 'ai_positioning: 4 — "agentic AI / multi-physics fusion called out
    as the next monetization leg in 2Q26"'
  themes:
  - ai_infrastructure_capex
  - chip_design_competition
  challenged_by:
  - Cadence or a new entrant announcing a commercially priced agentic EDA product
    with a disclosed paying customer before SNPS converts any of its 20 evaluation-phase
    customers to a paid license
  - SNPS disclosing at September 2026 Investor Day or a subsequent earnings call that
    no incremental revenue from agentic tools was recognized in FY26
  confirmed_by:
  - September 2026 Investor Day disclosing a binding pricing structure or a quantified
    incremental revenue target for agentic EDA
  - SNPS filing or earnings call disclosing at least one of the 20 evaluation customers
    converting to a paid agentic EDA license
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: china_eda_headwind_not_expanded
  statement: Export-control headwinds affecting SNPS EDA-license volumes in China
    have not extended to additional tool categories or customer geographies beyond
    the conditions that produced the watch-item language at the 2Q26 scoring date;
    the constraint is the same set of restrictions already reflected in the 4 score.
  derived_from: 'potential_investor_interest.score: 4 — "China demand are watch-items"'
  themes:
  - china_export_controls
  challenged_by:
  - A new BIS rule published in the Federal Register explicitly restricting EDA software
    exports to PRC-domiciled chip designers
  - SNPS disclosing a sequential step-down in China revenue in a quarterly filing
    or earnings call covering any period after 2Q26, where management attributes the
    decline to a new regulatory action
  confirmed_by:
  - SNPS providing a regional revenue breakdown in a filing covering any period after
    2Q26 that shows no sequential decline in China revenue from the 2Q26 base
  - Management explicitly confirming in a subsequent earnings call that no new EDA-license
    restrictions have been imposed in China beyond conditions cited in the 2Q26 call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: snps_tool_layer_no_volume_link
  statement: The ai_positioning score of 4 (not 5) is premised on SNPS generating
    EDA and IP revenue through fixed-fee licenses and subscriptions, not through per-tape-out
    royalties or per-chip-shipped participation; at scoring no contract structure
    creates a direct proportional link between AI accelerator unit volumes and SNPS
    revenue.
  derived_from: 'ai_positioning: 4 — "One step removed from AI compute -> 4"'
  themes:
  - ai_infrastructure_capex
  - silicon_architecture_competition
  challenged_by:
  - SNPS executing and publicly disclosing a royalty-per-tape-out or per-chip-shipped
    revenue contract with a hyperscaler or major fabless customer, in a filing or
    earnings prepared remarks
  - SNPS September 2026 Investor Day introducing a volume-participation IP pricing
    tier as a commercial product
  confirmed_by:
  - September 2026 Investor Day explicitly characterizing all IP licensing as fixed-fee
    or multi-year subscription with no volume-participation component
  - SNPS FY26 annual filing showing IP segment revenue growth below the YoY growth
    rate of AI accelerator unit shipments reported by major customers in the same
    period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ip_segment_trough_not_deepening
  statement: The potential_investor_interest score of 4 treats the Design IP segment
    as a watch-item at a trough, not in accelerating decline; the -6% YoY figure at
    2Q26 has not deteriorated further in the quarter immediately following the scoring
    date.
  derived_from: 'potential_investor_interest.score: 4 — "Design-IP segment bottoming...
    are watch-items"'
  themes:
  - silicon_architecture_competition
  - chip_design_competition
  challenged_by:
  - SNPS reporting a second consecutive quarter of Design IP segment YoY revenue decline
    worse than -6% in a public quarterly filing
  - A named hyperscaler publicly disclosing an in-house Design IP development initiative
    intended to replace SNPS-licensed IP, in a filing, press release, or earnings
    transcript
  confirmed_by:
  - SNPS reporting Design IP segment sequential revenue growth in a filing covering
    any quarter after 2Q26
  - SNPS reporting Design IP segment YoY revenue at or above flat in any quarter after
    2Q26
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
