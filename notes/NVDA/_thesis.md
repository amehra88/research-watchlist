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
- notes/NVDA/20260827-2Q27.md
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
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: roadmap_2yr_named_platforms
  statement: At scoring date, NVDA has publicly named successor platforms with disclosed
    ramp timelines extending at least two calendar years.
  derived_from: 'competitive_advantage.innovation_rate: 5 — "Roadmap visibility 2+
    years"'
  themes:
  - silicon_architecture_competition
  challenged_by:
  - A management announcement delaying Vera Rubin ramp beyond the Q3 calendar 2026
    timeline disclosed in notes/NVDA/20260521-1Q27.md
  - Absence of any publicly named platform successor to Vera Rubin in investor presentations
    or analyst day materials through FY28
  confirmed_by:
  - Vera Rubin customer shipments commencing per the Q3 calendar 2026 ramp disclosed
    in notes/NVDA/20260521-1Q27.md
  - A named next-generation platform announced at GTC or equivalent public forum with
    a disclosed production ramp date
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: vera_cpu_20b_fy27_commitment
  statement: At scoring date, the ~$20B FY27 standalone Vera CPU revenue visibility
    cited in the 1Q27 Huang/Arya exchange reflects specific customer-level commitments
    from named hyperscaler or system-maker partners, not internal management forecasts
    alone.
  derived_from: 'competitive_advantage.overall: 5 — "Vera CPU adds a second architectural
    axis ($200B TAM, ~$20B FY27 standalone revenue visibility — Huang/Arya 1Q27 exchange)"'
  themes:
  - silicon_architecture_competition
  - ai_infrastructure_capex
  challenged_by:
  - Absence of any Vera CPU revenue, backlog, or deferred revenue disclosure in an
    FY27 10-Q or 10-K
  - A publicly named hyperscaler or system-maker announces deferral or cancellation
    of a Vera CPU order before FY27 close
  confirmed_by:
  - A 10-Q or 8-K within FY27 disclosing Vera CPU segment revenue or backlog at or
    above $10B
  - A hyperscaler earnings call confirming Vera CPU deployment in a named production
    cluster
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gm_compression_input_cost_not_pricing
  statement: At scoring date, the gross margin guide trough of 71-72% in Q4 FY27 is
    attributed by management to memory input costs, not to competitive price concessions
    to customers — a distinction that is the basis for holding competitive_advantage.overall
    at 5 despite the margin drift.
  derived_from: 'competitive_advantage.overall: 5 — "Moat composition reinforced;
    score holds at 5/5" — 2Q27 note: "Management attributed this to rising memory
    costs, and was explicitly transparent about it. This is an input-cost margin story,
    not a competitive-pricing one."'
  themes:
  - silicon_architecture_competition
  - inference_compute_economics
  challenged_by:
  - A management statement on any subsequent earnings call attributing any portion
    of gross margin compression to competitive pricing pressure or price concessions
    to customers
  - A competitor announcing an accelerator price reduction accompanied by an NVDA
    management acknowledgment of a corresponding pricing response
  confirmed_by:
  - A 10-Q COGS disclosure showing memory or component cost per unit as the primary
    driver of gross margin change with average selling price flat or higher QoQ
  - An HBM or memory supplier earnings disclosure citing higher contracted prices
    with hyperscaler-facing customers in the relevant quarters
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: valuation_is_sole_investor_score_cap
  statement: At scoring date, the stated basis for the potential_investor_interest
    score of 4 rather than 5 is valuation caution at approximately $5.4T market capitalization,
    with no fundamental concern cited as a co-constraint.
  derived_from: 'potential_investor_interest.score: 4 — "Cap: valuation caution at
    ~$5.4T mcap"'
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - A subsequent PM score note for NVDA potential_investor_interest citing a fundamental
    concern — demand deterioration, competitive design win, or export control escalation
    — as a co-constraint alongside or instead of valuation
  confirmed_by:
  - Sell-side initiations or rating changes to Hold on NVDA citing valuation as the
    primary stated rationale while characterizing demand and competitive position
    as intact
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fifty_pct_fcf_return_structural
  statement: At scoring date, the capital return posture of approximately 50% of FCF
    is characterized in the PM's notes as a structural commitment established at the
    1Q27 print, not a discretionary one-quarter action.
  derived_from: 'potential_investor_interest.score: 4 — "1Q27 print converted capital-return
    posture to structural ~50%-of-FCF commitment: $119B total buyback authorization
    (+$80B incremental)"'
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - A management statement in a subsequent quarter reducing the capital return target
    below 50% of FCF
  - A 10-Q or 8-K disclosure showing suspension or material reduction of the $119B
    buyback authorization
  confirmed_by:
  - The 2Q27 10-Q filed with the SEC containing language equivalent to 'at least 50%
    of free cash flow' in the capital allocation disclosure — consistent with the
    2Q27 earnings note transcript citation
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
