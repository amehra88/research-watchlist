---
doc_type: thesis
ticker: DE
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#DE
reviewed_by_operator: false
scores:
  ai_positioning: '4'
proposed_scores: {}
assumptions:
- id: see_spray_per_plant_inference
  statement: See & Spray's CV system makes herbicide-application decisions at individual-plant
    resolution, not at row or zone resolution.
  derived_from: 'ai_positioning: 4 — ''decides per plant'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - Deere technical specification, field trial publication, or third-party agronomic
    study documenting targeting granularity coarser than individual-plant level
  confirmed_by:
  - Deere white paper, patent filing, or peer-reviewed validation explicitly quantifying
    per-plant inference in commercial-production hardware
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: see_spray_outcome_pricing_live
  statement: See & Spray is commercially available under a pricing structure tied
    to measured herbicide savings, not a flat hardware or subscription fee.
  derived_from: 'ai_positioning: 4 — ''priced on herbicide saved'''
  themes:
  - ai_native_vertical
  - ai_re_architected_incumbent
  challenged_by:
  - Deere dealer contract terms, 10-K product-revenue footnote, or customer disclosure
    showing a hardware-only or fixed-subscription pricing model in commercial sales
  confirmed_by:
  - Deere investor-day slide, press release, or customer case study citing active
    contracts priced on a per-unit-of-herbicide-saved basis
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: customer_fleet_primary_data_source
  statement: The training dataset powering See & Spray's CV model is accumulated from
    customer-purchased, customer-operated machines in the field rather than primarily
    from Deere-funded test-farm trials.
  derived_from: 'ai_positioning: 4 — ''training data from a customer-funded machine
    fleet'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - Deere R&D disclosure, academic paper, or earnings call stating that training data
    is predominantly sourced from company-run test farms, partnerships, or synthetic
    generation
  confirmed_by:
  - Deere disclosure quantifying the proportion or volume of training images annotated
    from commercially deployed customer machines
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: see_spray_revenue_generating_at_score
  statement: At scoring date, See & Spray units operating under the herbicide-savings
    pricing model are generating commercial revenue — the product is not in pilot
    or pre-commercial status.
  derived_from: 'ai_positioning: 4 — ''priced on herbicide saved; proves the thesis
    outside tech'''
  themes:
  - ai_native_vertical
  challenged_by:
  - 10-K, 10-Q, or earnings call characterizing See & Spray as a pilot program, beta,
    or pre-revenue offering with no units under commercial pricing contracts
  confirmed_by:
  - Deere earnings call or press release citing units sold or revenue recognized under
    the herbicide-savings pricing model
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: herbicide_saving_primary_value_metric
  statement: Herbicide cost reduction is the primary customer value metric that justifies
    the pricing model, as opposed to yield improvement, labor savings, or equipment
    utilization.
  derived_from: 'ai_positioning: 4 — ''priced on herbicide saved'''
  themes:
  - ai_native_vertical
  challenged_by:
  - Deere marketing materials, ROI calculator, or customer survey ranking yield, labor,
    or other benefits as the dominant purchasing driver over herbicide savings
  confirmed_by:
  - Deere case study or investor presentation showing herbicide reduction as the headline
    value metric in customer contract pricing and renewal decisions
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
