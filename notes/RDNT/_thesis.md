---
doc_type: thesis
ticker: RDNT
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#RDNT
reviewed_by_operator: false
scores:
  ai_positioning: '4'
proposed_scores: {}
assumptions:
- id: rdnt_scanner_image_outcome_stack
  statement: At scoring, RadNet operates the scanners, holds the imaging archive,
    and retains the diagnostic outcome labels used to supervise the DeepHealth model
    — no layer of this three-part stack has been sold, licensed out, or transferred
    to a third party.
  derived_from: 'ai_positioning: 4 — "owns the scanners, the images AND the outcomes
    that label them"'
  themes:
  - ai_native_vertical
  - ai_re_architected_incumbent
  challenged_by:
  - 8-K or press release disclosing a sale or licensing of RadNet's imaging data or
    outcome labels to a third-party AI company
  - Divestiture or spin-out of DeepHealth disclosed in an SEC filing
  confirmed_by:
  - 10-K or 10-Q confirming DeepHealth as a wholly-owned subsidiary with no third-party
    data licensing arrangements
  - Management statement on an earnings call affirming outcome data is retained within
    RadNet's own network
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: rdnt_captive_outcome_supervision
  statement: The DeepHealth model's supervision signal is derived from diagnostic
    outcome labels generated within RadNet's own patient population — the model has
    not been retrained primarily on externally sourced or synthetic labels.
  derived_from: 'ai_positioning: 4 — "outcomes that label them"'
  themes:
  - ai_native_vertical
  challenged_by:
  - FDA 510(k) or De Novo submission for a DeepHealth product citing external or synthetic
    datasets as the primary training source
  - RadNet regulatory or investor disclosure indicating outcome labels are sourced
    from a third-party annotation vendor rather than its own clinical reads
  confirmed_by:
  - FDA 510(k) or De Novo predicate submission citing RadNet's own clinical outcomes
    as the training data source
  - Management statement on an earnings call specifying proprietary outcome data as
    the model's supervision signal
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: rdnt_deephealth_cashpay_model
  statement: At scoring, DeepHealth revenue is generated via an incremental cash-pay
    charge on top of the base imaging fee — it is not reimbursed through standard
    payer codes or bundled into base-contract pricing.
  derived_from: 'ai_positioning: 4 — "DeepHealth sold as cash-pay upsell"'
  themes:
  - ai_native_vertical
  challenged_by:
  - CMS or major commercial payer announcement of a reimbursement code covering DeepHealth-assisted
    reads
  - Investor day or earnings disclosure showing DeepHealth folded into standard service
    contract pricing rather than a separate cash-pay line
  confirmed_by:
  - Earnings supplement or investor presentation disclosing DeepHealth as a discrete
    cash-pay revenue line separate from base imaging fees
  - Management commentary on a quarterly call confirming no payer reimbursement pathway
    for DeepHealth at that date
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: rdnt_deephealth_distribution_captive
  statement: At scoring, DeepHealth is deployed exclusively or predominantly through
    RadNet's own imaging centers — it is not licensed at material scale to external
    hospital systems or competing radiology operators.
  derived_from: 'ai_positioning: 4 — "Vertically integrated data/model/distribution"'
  themes:
  - ai_native_vertical
  - ai_re_architected_incumbent
  challenged_by:
  - RadNet press release or 8-K announcing an enterprise licensing agreement for DeepHealth
    with a hospital chain or third-party radiology group
  - Earnings disclosure of a material third-party licensing revenue line for DeepHealth
  confirmed_by:
  - Earnings call management commentary confirming DeepHealth deployment is limited
    to RadNet-operated centers
  - 10-K business description showing no third-party licensing segment for DeepHealth
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: rdnt_vertical_stack_not_matched
  statement: At scoring, no single competitor in AI-assisted radiology operates a
    captive stack of comparable scale — owned scanners, a proprietary image archive,
    and labeled diagnostic outcomes under one roof — such that RadNet's vertical integration
    is a basis for differentiation rather than parity.
  derived_from: 'ai_positioning: 4 — "Vertically integrated data/model/distribution.
    Rank #5."'
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - A publicly announced merger or acquisition combining a large radiology network
    with an AI radiology company producing a comparable end-to-end stack, disclosed
    via SEC filing or major press release
  confirmed_by:
  - Absence of any announced comparable full-stack integration — owned centers plus
    captive labeled outcomes plus AI model — from a single radiology operator in SEC
    filings or major press releases at re-score date
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
