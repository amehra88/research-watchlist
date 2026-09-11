---
doc_type: thesis
ticker: UPST
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#UPST
reviewed_by_operator: false
scores:
  ai_positioning: '4'
proposed_scores: {}
assumptions:
- id: upst_model_is_primary_decisioner
  statement: UPST's AI model is the primary credit decision mechanism; no traditional
    bureau score cutoff gates applicants before the model evaluates them.
  derived_from: 'ai_positioning: 4 — "the credit decision IS the model"'
  themes:
  - ai_native_vertical
  challenged_by:
  - 10-K or 10-Q disclosure showing a minimum bureau score floor applied to all applicants
    before model scoring
  - Partner bank agreement or regulatory filing revealing a bureau cutoff as a prerequisite
    for loan eligibility
  confirmed_by:
  - 10-K explicitly describing AI model as sole accept/decline mechanism with no prior
    bureau cutoff
  - CFPB or OCC filing confirming UPST applies no FICO minimum before model evaluation
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: upst_trains_on_bureau_rejected_outcomes
  statement: UPST's model training corpus contains repayment outcome data from borrowers
    who would have been declined under conventional bureau-cutoff underwriting.
  derived_from: 'ai_positioning: 4 — "trained on outcomes for borrowers a bureau cutoff
    would reject"'
  themes:
  - ai_native_vertical
  challenged_by:
  - UPST disclosure or investor presentation showing training data is drawn exclusively
    from borrowers who also pass a standard bureau minimum threshold
  - 10-K revealing a retrospective bureau screen applied to historical training labels
  confirmed_by:
  - UPST white paper or SEC filing quantifying the share of training loans originated
    to borrowers below conventional bureau cutoffs
  - 10-K or model-card disclosure confirming no FICO floor was applied to the historical
    origination data used for training
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: upst_funding_fragility_conditions_hold
  statement: The funding fragility conditions present at the time of scoring—loan
    volume dependent on the ongoing participation of external capital partners—have
    not been resolved.
  derived_from: 'ai_positioning: 4 — "Funding-fragile"'
  themes:
  - ai_native_vertical
  challenged_by:
  - UPST 10-Q or 8-K announcing committed whole-loan purchase agreements covering
    the majority of forward origination volume
  - Filing disclosing a captive or affiliated bank subsidiary providing balance-sheet
    funding for originations
  confirmed_by:
  - 10-Q or earnings press release disclosing a reduction in committed funding capacity
    or departure of a significant funding partner
  - 10-K risk-factor section identifying funding partner concentration as a material
    ongoing risk
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 4.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: upst_no_material_balance_sheet_buffer
  statement: UPST does not retain originated loans on its own balance sheet at a scale
    that would buffer origination volume against funding partner withdrawal.
  derived_from: 'ai_positioning: 4 — "Funding-fragile" (implies no self-funding capacity
    absorbs partner risk)'
  themes:
  - ai_native_vertical
  challenged_by:
  - 10-Q balance sheet showing UPST holding a material percentage (e.g., >15%) of
    originated loan volume as on-balance-sheet assets
  - 8-K announcing acquisition of a bank charter or FDIC-insured entity to self-fund
    originations
  confirmed_by:
  - 10-Q showing loans held on balance sheet below 5% of quarterly origination volume
  - 10-K explicitly disclosing that substantially all loans are sold or transferred
    to third-party funding sources at or shortly after origination
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 4.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
