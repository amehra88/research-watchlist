---
doc_type: thesis
ticker: IRTC
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#IRTC
reviewed_by_operator: false
scores:
  ai_positioning: '4'
proposed_scores: {}
assumptions:
- id: fda_clearance_active_at_scoring
  statement: iRhythm's AI ECG classifier held FDA clearance at the time of scoring.
  derived_from: 'ai_positioning: 4 — "FDA clearance"'
  themes:
  - ai_native_vertical
  challenged_by:
  - FDA issues a recall, warning letter, or clearance withdrawal covering iRhythm's
    AI ECG classifier
  confirmed_by:
  - iRhythm's AI classifier listed as active on FDA 510(k)/De Novo device database
    with no open enforcement action
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: cpt_code_active_at_scoring
  statement: A CPT billing code covering iRhythm's AI-classifier-derived service was
    active at the time of scoring.
  derived_from: 'ai_positioning: 4 — "CPT code"'
  themes:
  - ai_native_vertical
  challenged_by:
  - AMA CPT Editorial Panel or CMS removes, sunsets, or restricts the relevant CPT
    code in a final fee-schedule rule
  confirmed_by:
  - CMS physician fee schedule or AMA CPT codebook lists the relevant code as active
    and reimbursable for the applicable year
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: decade_labeled_ecg_dataset
  statement: iRhythm's labeled ECG training archive had accumulated over approximately
    a decade at the time of scoring.
  derived_from: 'ai_positioning: 4 — "a decade of labelled recordings"'
  themes:
  - ai_native_vertical
  challenged_by:
  - Company filing or disclosure revises the stated duration or volume of the labeled
    training dataset to materially less than ten years
  confirmed_by:
  - 10-K, investor presentation, or peer-reviewed clinical publication cites dataset
    vintage spanning approximately ten years of continuous patch recordings
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: classifier_14d_continuous_ecg_input
  statement: The AI classifier processed continuous ~14-day ECG patch recordings as
    its primary input at the time of scoring.
  derived_from: 'ai_positioning: 4 — "Classifier reads ~14d continuous ECG"'
  themes:
  - ai_native_vertical
  challenged_by:
  - FDA-cleared product label or 510(k) summary specifies a materially shorter analysis
    window than 14 days for the AI classification function
  confirmed_by:
  - 510(k) summary or peer-reviewed clinical validation study confirms approximately
    14-day continuous patch as the standard recording and analysis window
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: ai_native_rank_3_at_scoring
  statement: 'iRhythm ranked #3 within the PM''s ai_native_vertical cohort at the
    time of scoring.'
  derived_from: 'ai_positioning: 4 — "Rank #3"'
  themes:
  - ai_native_vertical
  challenged_by:
  - A competing long-duration ECG AI classifier obtains FDA clearance and an active
    CMS CPT code, reducing iRhythm's structural differentiation within the cohort
  - 'A subsequent watchlist scoring update revises iRhythm''s cohort rank below #3'
  confirmed_by:
  - No FDA clearance granted to a competing continuous-patch ECG AI classifier during
    the scoring period
  - 'Watchlist scoring records show iRhythm''s ai_native_vertical rank at #3 or higher
    at the next scheduled review'
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
