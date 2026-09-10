---
doc_type: thesis
ticker: NBIS
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#NBIS
- notes/NBIS/20260514-1Q26.md
- notes/NBIS/20260813-2Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: h2_arr_step_achieves_guide
  statement: The $4–6B H2'26 ARR addition required to reach the reiterated $7–9B December
    exit is achievable from conditions described at Q2'26; NBIS does not cut or narrow
    its ARR exit guidance before Q4'26 results.
  derived_from: 'ai_infrastructure_capex: Confirm (direction) — ''ARR $3.0B at end-June
    against a $7–9B December exit implies a required H2 step of $4–6B — the single
    most testable claim in the guide'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - Q3'26 ARR print below $5.0B, implying an H2 run-rate inconsistent with a $7B December
    exit
  - Any downward revision to the $7–9B ARR exit guidance disclosed before Q4'26 results
  confirmed_by:
  - Q3'26 ARR print at or above $5.0B, keeping a $7B December exit within reach
  - December 2026 ARR exit at or above $7.0B confirmed in Q4'26 earnings or press
    release
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: per_mw_pricing_conditions_hold
  statement: Per-MW pricing conditions at Q2'26 scoring — capacity auction clearing
    15% above prior benchmarks and short-duration contract rates at roughly double
    long-term rates — have not reversed as of the Q3'26 earnings disclosure.
  derived_from: 'inference_compute_economics: Confirm — ''first capacity auction cleared
    15% above any previous price... short-duration deals are signing at roughly double
    the per-MW rate of long-term contracts, which effectively breaks the bear case
    on inference-compute margin compression'''
  themes:
  - inference_compute_economics
  challenged_by:
  - Q3'26 disclosure of a new capacity auction clearing at or below prior pricing
    benchmarks
  - Nebius AI segment adj. EBITDA margin reported below 40% in Q3'26, reversing the
    Q1–Q2 expansion trajectory from 24% to 50%
  confirmed_by:
  - Q3'26 disclosure of a new capacity auction clearing at or above Q2'26 benchmark
    levels
  - Nebius AI segment adj. EBITDA margin at or above 45% in Q3'26 earnings
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: connected_power_yend26_milestone
  statement: The connected power milestone of 800 MW–1 GW by year-end 2026, reaffirmed
    at Q2'26, is achieved without a publicly disclosed delay — connected power being
    identified in the Q2'26 note as the binding near-term revenue constraint.
  derived_from: 'data_center_deployment_constraints: Confirm — ''Connected power:
    800 MW–1 GW for 2026 reaffirmed... connected power, not contracted, is the near-term
    revenue constraint'''
  themes:
  - data_center_deployment_constraints
  challenged_by:
  - Q3'26 or Q4'26 disclosure placing year-end 2026 connected power below 700 MW
  - Management acknowledgment in a filing, press release, or earnings call of permitting,
    construction, or grid-interconnection delays affecting the YE26 connected-power
    target
  confirmed_by:
  - Year-end 2026 connected-power figure at or above 800 MW confirmed in Q4'26 earnings
    or an 8-K
  - Q3'26 interim capacity update showing connected-power additions on pace for the
    800 MW–1 GW YE26 target
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: asset_light_pipeline_no_deterioration
  statement: The asset-light partnership pipeline, which stood at zero signed deals
    with 'dozens of inquiries' as of Q2'26, shows no evidence of deterioration — defined
    as management ceasing to report pipeline activity or explicitly withdrawing the
    model — without a signed agreement disclosed by Q4'26.
  derived_from: 'ai_infrastructure_capex: Drift (mechanism) — ''no signed asset-light
    partner was disclosed... dozens of partner inquiries... management reports the
    model as early-stage'''
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - Q3'26 or Q4'26 earnings disclosure, 8-K, or press release stating the asset-light
    model has been paused, restructured, or that partner inquiries have declined
  - Complete absence of pipeline commentary in Q3'26 earnings without a stated commercial
    rationale
  confirmed_by:
  - First signed asset-light capacity partner agreement publicly disclosed in an 8-K,
    press release, or earnings call
  - Q3'26 earnings update quantifying a live pipeline or naming a partner in negotiation
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: meta_concentration_no_deepening
  statement: Customer concentration at Q2'26 scoring — with the Meta $27B contract
    as the largest single disclosed commitment within a >$40B contracted backlog —
    does not increase further as a share of that backlog at Q3'26 disclosure.
  derived_from: 'hyperscaler_revenue_concentration: Drift — ''customer concentration
    is now structurally higher (Meta alone $27B contract)... Drift on hyperscaler_revenue_concentration
    — no Breaks'''
  themes:
  - hyperscaler_revenue_concentration
  challenged_by:
  - Q3'26 disclosure of a new single-customer contract that, combined with Meta, raises
    top-1 customer share above the implied ~67% of the >$40B backlog figure cited
    at Q2'26
  - Meta exercising the $15B option ahead of its disclosed schedule without proportional
    new-customer additions growing the backlog
  confirmed_by:
  - Q3'26 contracted-backlog disclosure growing above $50B with identified additions
    from multiple new customers, reducing Meta's fractional share
  - Q3'26 earnings naming one or more new customers signing commitments of $1B or
    more
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: nvidia_exemplar_status_intact
  statement: NVIDIA Exemplar Cloud designation and associated supply-chain priority,
    cited at Q1'26 and Q2'26 as a mechanism securing GPU allocation across multiple
    GPU generations, have not been revoked or reclassified as of Q3'26.
  derived_from: 'ai_compute_topology: Confirm — ''NVIDIA Exemplar Cloud status — among
    the first across multiple GPU generations — secures roadmap alignment with NVIDIA''s
    product cycles... materially raises the bar for any new entrant'''
  themes:
  - ai_compute_topology
  challenged_by:
  - An NVIDIA press release, partner-program filing, or earnings disclosure indicating
    NBIS has been removed from or reclassified within the Exemplar Cloud program
  - NBIS earnings disclosure of GPU delivery delays explicitly attributed to a change
    in supply-priority standing with NVIDIA
  confirmed_by:
  - NVIDIA or NBIS disclosure of NBIS receiving first-batch allocation of a next-generation
    GPU SKU consistent with Exemplar Cloud tier
  - NVIDIA investor materials or partner announcements continuing to list NBIS as
    an Exemplar Cloud partner after Q2'26
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

Drafted 2026-09-09 in mode `notes` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
