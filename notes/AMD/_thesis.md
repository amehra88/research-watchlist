---
doc_type: thesis
ticker: AMD
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AMD
- notes/AMD/20260505-1Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: amd_dc_gpu_number_two_position
  statement: 'Conditions at scoring — AMD is the #2 data-center GPU vendor (behind
    NVIDIA), with MI300X/MI325 in production shipment — still hold.'
  derived_from: 'ai_positioning: 4 — ''the #2 data-center GPU vendor (MI300X/MI325
    shipping, MI350/MI400 roadmap on annual cadence)'''
  themes:
  - silicon_architecture_competition
  - ai_infrastructure_capex
  challenged_by:
  - A hyperscaler press release or earnings disclosure naming a competitor other than
    AMD (Broadcom custom ASIC, Intel Gaudi, or a new entrant) as their primary non-NVIDIA
    merchant GPU vendor
  - AMD quarterly filing showing data-center GPU revenue declined sequentially without
    a named successor-ramp explanation
  confirmed_by:
  - Two or more hyperscalers (AWS, Azure, GCP, Oracle) naming AMD Instinct as their
    principal non-NVIDIA GPU SKU in a new capacity-expansion press release within
    the same quarter
  - AMD 10-Q or earnings disclosure showing data-center GPU revenue at a level consistent
    with sole non-NVIDIA merchant GPU at scale
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: rocm_materially_trails_cuda
  statement: Conditions at scoring — AMD's ROCm software ecosystem materially trails
    CUDA — still hold.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''software ecosystem still
    materially trails CUDA'''
  themes:
  - silicon_architecture_competition
  - inference_compute_economics
  challenged_by:
  - A major inference-serving framework (vLLM, TGI, or equivalent) publishing a production
    ROCm backend with documented feature parity with its CUDA path for two or more
    leading model families
  - A hyperscaler public engineering disclosure designating ROCm as the default inference
    runtime for a named production deployment
  confirmed_by:
  - AMD earnings call Q&A in which management acknowledges ROCm software ecosystem
    as a continuing customer objection, on the record
  - MLPerf Inference benchmark results showing AMD ROCm-backed systems at lower throughput-per-dollar
    than NVIDIA CUDA systems on the same model class in the same test cycle
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: cuda_gap_caps_inference_distribution
  statement: Conditions at scoring — the CUDA software gap caps AMD's GPU distribution
    in inference workloads relative to NVIDIA — still hold.
  derived_from: 'competitive_advantage.distribution: 4 — ''the CUDA gap caps inference
    distribution vs NVDA'''
  themes:
  - inference_compute_economics
  - silicon_architecture_competition
  challenged_by:
  - A cloud inference provider (Fireworks AI, Together AI, or a major hyperscaler
    inference product) publishing a press release designating AMD Instinct as a primary
    inference backend in a production deployment
  - AMD disclosing in a filing or earnings call a named inference-at-scale customer
    win not previously associated with its GPU products
  confirmed_by:
  - Hyperscaler earnings calls describing GPU inference capacity expansions exclusively
    in terms of NVIDIA SKUs, with AMD referenced only for training or CPU workloads
  - AMD management citing software ecosystem investment as the primary barrier to
    inference share gains in a subsequent earnings call transcript
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: mi450_demand_exceeds_2027_plan
  statement: Conditions at scoring — MI450 customer demand forecasts exceed AMD's
    initial 2027 supply plans — still hold; no customer forecast reduction has been
    publicly disclosed.
  derived_from: 'ai_positioning: 4 — 1Q26 earnings note: ''Customer forecasts for
    MI450 already exceed initial 2027 plans, with new customers engaging on large-scale
    deployments'''
  themes:
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - A hyperscaler earnings commentary, press release, or SEC filing disclosing a reduction,
    deferral, or cancellation of MI450 or Helios orders
  - AMD guiding 2027 data-center AI revenue below the 'tens of billions' threshold
    referenced on the 1Q26 earnings call, on a subsequent earnings call
  confirmed_by:
  - AMD disclosing incremental MI450 multi-year supply agreements or raising 2027
    data-center AI revenue guidance in a press release or subsequent earnings call
  - A named hyperscaler beyond Meta and OpenAI announcing a MI450 or Helios procurement
    in a capacity-expansion press release or SEC filing
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: meta_openai_sole_named_gpu_customers
  statement: At scoring, Meta (6GW deployment) and OpenAI are the only named large-scale
    Instinct GPU customers publicly identified; AMD's AI GPU demand is concentrated
    in these two relationships at this stage.
  derived_from: 'ai_positioning: 4 — 1Q26 earnings note: ''Meta''s 6GW deployment
    and an OpenAI partnership named on the call''; theme: hyperscaler_revenue_concentration'
  themes:
  - hyperscaler_revenue_concentration
  - ai_infrastructure_capex
  challenged_by:
  - Meta or OpenAI disclosing a shift of planned GPU capacity to NVIDIA-only or custom-silicon
    alternatives in a press release or earnings call
  - AMD 10-K or 10-Q triggering a customer-concentration disclosure (≥10% of revenue
    threshold) naming Meta or OpenAI, with no additional named GPU customers added
  confirmed_by:
  - A hyperscaler other than Meta or OpenAI (AWS, Azure, GCP, xAI, or equivalent)
    announcing a large-scale MI450 or Helios procurement agreement in a press release
    or SEC filing
  - AMD 10-K or 10-Q showing that no single customer accounts for ≥10% of total revenue,
    without a corresponding disclosure of new named GPU customers added in the same
    period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: sw_distribution_gap_holds_score_below_5
  statement: At scoring, AMD's software and distribution gap to NVIDIA is the stated
    reason competitive_advantage is scored 4 and not 5; that gap is the binding constraint
    on the score.
  derived_from: 'competitive_advantage.overall: 4 — ''software/distribution gap to
    NVDA holds it below 5'''
  themes:
  - silicon_architecture_competition
  - model_efficiency_evolution
  challenged_by:
  - AMD disclosing in a filing or investor-day presentation that a named customer
    selected AMD over NVIDIA citing software-stack parity as the deciding factor
  - A hyperscaler public engineering blog or technical white paper confirming ROCm
    production equivalence with CUDA for a named workload class at scale
  confirmed_by:
  - AMD earnings call Q&A in which management explicitly ranks software ecosystem
    investment ahead of hardware roadmap as the primary competitive priority for the
    coming year
  - MLPerf or SPECaccel benchmark publication showing AMD ROCm-based inference systems
    failing to reach CUDA parity on throughput-per-dollar in the same test cycle as
    a new Instinct hardware generation
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
