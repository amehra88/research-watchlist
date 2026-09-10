---
doc_type: thesis
ticker: GH
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#GH
reviewed_by_operator: false
scores:
  ai_positioning: '4'
proposed_scores: {}
assumptions:
- id: gh_classifier_functionally_necessary
  statement: GH's AI/ML classifier is functionally necessary — not peripheral — to
    the tumor-naive MRD and screening products; removing it would reduce the product
    to a non-differentiated liquid biopsy with no clinically actionable output.
  derived_from: 'ai_positioning: 4 — "Delete the model and you have a blood draw"'
  themes:
  - ai_native_vertical
  challenged_by:
  - A peer-reviewed publication demonstrates equivalent tumor-naive MRD sensitivity
    using threshold-only or rule-based methylation analysis without a trained classifier
  - GH's FDA submission categorizes the classifier as a post-analytical decision-support
    layer rather than the mechanism of analytical validity
  confirmed_by:
  - GH's De Novo or PMA filing identifies the trained classifier as the core mechanism
    of clinical validity for the tumor-naive detection claim
  - GH publishes an ablation study showing classifier removal materially degrades
    sensitivity or specificity of the assay
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gh_methylation_fragmentomics_inputs
  statement: The input domain of GH's core learned classifier is specifically methylation
    and fragmentomic signals — both modalities are required inputs, not interchangeable
    with other cfDNA signal types.
  derived_from: 'ai_positioning: 4 — "tumor-naive MRD + screening require learned
    classifiers over methylation and fragmentomics"'
  themes:
  - ai_native_vertical
  challenged_by:
  - GH files a technical supplement or analytical validation white paper indicating
    the production classifier relies on a materially different signal domain (e.g.,
    copy-number only, SNV calls)
  - A competing tumor-naive platform achieves FDA clearance using a single-modality
    classifier, implying the methylation-plus-fragmentomics combination is not a necessary
    architecture
  confirmed_by:
  - GH publishes peer-reviewed methodology enumerating methylation and fragmentomic
    features as primary classifier inputs
  - GH's regulatory submission or investor technical brief explicitly identifies methylation
    and fragmentomics as the two integrated signal layers
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gh_tumor_naive_generalization_hard
  statement: The tumor-naive constraint — operating without matched tumor tissue —
    is the distinct AI challenge GH's classifier addresses; the model must generalize
    signal detection across cancer types without a tissue-informed prior.
  derived_from: 'ai_positioning: 4 — "tumor-naive MRD + screening require learned
    classifiers"'
  themes:
  - ai_native_vertical
  challenged_by:
  - GH introduces or acquires a tissue-informed assay variant that achieves materially
    higher sensitivity than the tumor-naive classifier, signaling the tumor-naive
    architecture is not the primary competitive differentiator
  - GH's published validation covers only a single cancer type, indicating the multi-cancer
    generalization claim is unsupported by data at time of scoring
  confirmed_by:
  - GH publishes multi-cancer-type validation data for the tumor-naive classifier
    across ≥3 distinct cancer indications
  - GH's cleared regulatory indication is explicitly scoped as tumor-naive across
    multiple cancer types
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gh_ai_screen_rank2_holds
  statement: 'Conditions supporting GH''s #2 position on the PM''s ai-forward screen
    held at time of scoring and have not worsened.'
  derived_from: 'ai_positioning: 4 — "Rank #2 on ai-forward screen"'
  themes:
  - ai_native_vertical
  - enterprise_ai_adoption
  challenged_by:
  - A competing cfDNA company announces a tumor-naive classifier-based platform with
    published analytical validation, altering GH's relative ai-forward standing
  - GH announces a pipeline discontinuation or regulatory setback affecting the classifier-based
    MRD or screening product
  confirmed_by:
  - 'Next scoring-cycle review reaffirms GH at #2 with no new tumor-naive classifier
    entrants displacing it'
  - No peer cfDNA company publishes a tumor-naive methylation-plus-fragmentomics classifier
    with superior sensitivity between scoring date and next review
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gh_not_singular_ai_leader
  statement: At least one other company in the PM's ai-forward screen outranked GH
    at time of scoring, meaning GH's classifier-based differentiation is not the best-in-screen
    AI deployment.
  derived_from: 'ai_positioning: 4 — "Rank #2 on ai-forward screen"'
  themes:
  - ai_native_vertical
  challenged_by:
  - 'The #1-ranked company suffers a regulatory setback, product withdrawal, or pipeline
    failure that eliminates its lead, prompting GH''s reclassification to #1 at next
    review'
  - 'PM''s next scoring cycle explicitly reclassifies GH to #1 on the ai-forward screen'
  confirmed_by:
  - 'PM''s next scoring cycle maintains GH at #2 with the same entity occupying #1'
  - 'The #1-ranked company publishes a regulatory milestone or classifier validation
    study corroborating its superior ai-forward standing relative to GH'
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
