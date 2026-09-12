---
doc_type: thesis
ticker: DOCN
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#DOCN
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: ai_arr_reflects_production_workloads
  statement: AI Customer ARR of $234M as of June 30, 2026 reflects customers running
    production inference workloads on DOCN GPU infrastructure, not primarily trial
    or pilot usage.
  derived_from: 'MD&A: AI Customer ARR — ''AI Customer ARR as of June 30, 2026 was
    $234 million, up from $75 million as of June 30, 2025'''
  themes:
  - inference_compute_economics
  - ai_infrastructure_software
  challenged_by:
  - AI Customer ARR growth rate decelerates materially below the trailing YoY pace
    in the September 2026 10-Q filing without a stated macro or seasonal explanation
  - Management disclosure that a small number of accounts constitute a disproportionate
    share of AI ARR, indicating trial-concentration rather than broad workload deployment
  confirmed_by:
  - AI Customer ARR growth rate reported in the September 2026 10-Q is at or above
    100% YoY
  - Increase in $1M+ Customer count attributable to AI-specific workloads disclosed
    in a subsequent quarterly filing or earnings call transcript
  status: open
  status_source: draft
  pressure:
    confirm: 36.0
    challenge: 3.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: dne_mix_shift_no_sam_cost_blowout
  statement: The shift in top-25 customer revenue share from approximately 9% to approximately
    20% between Q2 2025 and Q2 2026 is occurring without a material increase in sales
    and marketing expense as a percentage of revenue.
  derived_from: 'MD&A: go-to-market efficiency — ''sales and marketing expense was
    approximately 8% of our revenue'' and ''top 25 customers made up approximately
    20% and 9% of our revenue in the three months ended June 30, 2026 and 2025, respectively'''
  themes:
  - enterprise_ai_adoption
  - ai_infrastructure_software
  challenged_by:
  - S&M expense as a percentage of revenue rises materially above 8% in a subsequent
    10-Q filing
  - Proxy statement or 10-Q headcount disclosures indicating significant enterprise
    sales force expansion not captured in the reported 8% S&M ratio
  confirmed_by:
  - S&M expense as a percentage of revenue is at or below 8% in the September 2026
    10-Q while DNE customer count and top-25 revenue share grow
  - Management reiterates self-service as the primary customer acquisition channel
    with no structural go-to-market change described in a subsequent filing or earnings
    call
  status: open
  status_source: draft
  pressure:
    confirm: 7.0
    challenge: 5.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: gpu_supply_not_binding_in_q2
  statement: GPU infrastructure supply capacity at DOCN as of the June 2026 quarter
    was not a binding constraint on AI Customer ARR growth.
  derived_from: 'MD&A: AI platform build-out — ''production-ready GPU infrastructure''
    and ''Gradient AI Infrastructure with offerings such as GPU Droplets and Bare
    Metal GPUs'''
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  - inference_compute_economics
  challenged_by:
  - Management commentary in a subsequent earnings call or 10-Q disclosing GPU waitlists,
    customer churn attributed to supply limitations, or qualification of GPU Droplet
    or Bare Metal GPU availability
  - Capex guidance revised materially upward with explicit disclosure that demand
    exceeded supply in the prior period
  confirmed_by:
  - No supply-constraint language appears in AI infrastructure risk factors or operational
    discussion in the September 2026 10-Q
  - GPU Droplet and Bare Metal GPU product availability confirmed without capacity
    qualification in a press release, product changelog, or 8-K during Q3 2026
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 14.0
    challenge: 11.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `thin` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
