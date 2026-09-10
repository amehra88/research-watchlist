---
doc_type: thesis
ticker: CSCO
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#CSCO
- notes/CSCO/20260514-3Q26.md
- notes/CSCO/20260813-4Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: t2_candidacy_not_disqualified
  statement: No event between CSCO's watchlist addition (2026-06-24) and formal scoring
    has eliminated the Tier-2 candidacy the PM provisionally assigned.
  derived_from: 'scoring_notes: ''Tier-2 candidate; themes/scoring pending next earnings
    cycle'''
  themes: []
  challenged_by:
  - An 8-K or press release filed after 2026-06-24 documenting a material business
    deterioration the PM would treat as disqualifying
  - PM removes CSCO from watchlist.yaml without assigning a score
  confirmed_by:
  - PM assigns a T2 entry with themes and scores in watchlist.yaml following 4Q26
    review
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: 4q26_cycle_sufficient_as_gate
  statement: The 4Q26 earnings cycle (reported 2026-08-12) is the specific event the
    PM designated as sufficient to formalize themes and scoring for CSCO.
  derived_from: 'scoring_notes: ''themes/scoring pending next earnings cycle'' — addition
    date 2026-06-24; next earnings print after addition was Q4''26'
  themes: []
  challenged_by:
  - PM documents a reason to defer scoring beyond 4Q26 (e.g., a pending strategic
    event or new data gap flagged in the earnings-reviewer run)
  confirmed_by:
  - PM populates SCORES and SCORE NOTES in watchlist.yaml for CSCO with explicit reference
    to 4Q26 data as scoring basis
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: factset_coverage_not_re_broken
  statement: The FactSet data-pull defect that delayed CSCO's inclusion was resolved
    at addition and has not produced a subsequent coverage gap for CSCO.
  derived_from: 'scoring_notes: ''Store B metrics-coverage expansion (residual-20
    close, factset-pull-drop fix)'''
  themes: []
  challenged_by:
  - An [UNSOURCED] tag on a load-bearing consensus or actuals row in notes/CSCO/20260813-4Q26.md
    attributable to a FactSet pull failure rather than a data-availability limitation
  confirmed_by:
  - All consensus and actuals rows in the 4Q26 earnings note carry sourced values
    without FactSet-pull-related gaps
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: csco_not_in_bctk_portfolio
  statement: CSCO was not held in the BCTK portfolio at watchlist addition and has
    not been purchased before formal scoring is completed.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — per memory/tier-promotion-criterion.md,
    T2 designates an unowned name; T1 is triggered only by an actual buy'
  themes: []
  challenged_by:
  - bctk_derived.yaml lists CSCO as a T1 holding prior to PM completing a scored watchlist.yaml
    entry
  confirmed_by:
  - bctk_derived.yaml omits CSCO through the date the PM formally assigns themes and
    scores in watchlist.yaml
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
