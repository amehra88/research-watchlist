---
doc_type: thesis
ticker: HPE
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#HPE
- notes/HPE/20260602-2Q26.md
- notes/HPE/20260903-3Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: t2_candidacy_conditions_hold
  statement: The conditions that supported HPE's T2 candidacy at 2026-06-24 had not
    materially deteriorated as of the scoring date.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - Revenue miss or guidance cut disclosed in an 8-K or 10-Q filed after 2026-06-24
  - Material customer cancellation or contract loss announced in an SEC filing or
    press release
  confirmed_by:
  - HPE retained in watchlist.yaml tier_2 after the Q3 FY26 earnings cycle (2026-09-03
    print) with no removal annotation
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 44.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: not_a_bctk_holding_at_addition
  statement: HPE was not a BCTK portfolio holding at 2026-06-24 and had not been purchased
    into the portfolio as of the scoring date.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - HPE entry appearing in bctk_derived.yaml
  - T1 promotion entry written to watchlist.yaml
  confirmed_by:
  - Absence of HPE from bctk_derived.yaml as of the scoring date
  - HPE listed exclusively under tier_2 in watchlist.yaml with no tier change record
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: q3_earnings_planned_eval_trigger
  statement: The Q3 FY26 earnings cycle was the planned trigger for establishing HPE's
    themes and scores.
  derived_from: 'scoring_notes: ''themes/scoring pending next earnings cycle'' — ''Tier-2
    candidate; themes/scoring pending next earnings cycle'''
  themes: []
  challenged_by:
  - Continued absence of themes and score attributes in watchlist.yaml after 2026-09-03
    with no annotation explaining further deferral
  - HPE removed from the watchlist before scoring was completed
  confirmed_by:
  - Themes and score attributes populated in watchlist.yaml with an effective date
    on or after 2026-09-03
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: no_scores_assigned_at_addition
  statement: No scoring attributes had been assessed for HPE as of 2026-06-24.
  derived_from: 'scoring_notes: ''themes/scoring pending'' — ''themes/scoring pending
    next earnings cycle'''
  themes: []
  challenged_by:
  - Any score value appearing in watchlist.yaml for HPE with a timestamp prior to
    2026-09-03
  - A score annotation in any repo commit dated before 2026-09-03
  confirmed_by:
  - SCORES and SCORE NOTES fields remaining empty in watchlist.yaml at the 2026-06-24
    git commit that added the name
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
