---
doc_type: thesis
ticker: HTFL
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#HTFL
- notes/HTFL/20260515-1Q26.md
- notes/HTFL/20260814-2Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: htfl_passes_initial_screen
  statement: HTFL cleared the PM's minimum watchlist-inclusion bar as of 2026-06-24
    — sufficient to log for monitoring, not sufficient to assign themes or a formal
    score.
  derived_from: 'scoring_notes: (unscored) — "Tier-2 candidate; themes/scoring pending
    next earnings cycle"'
  themes: []
  challenged_by:
  - HTFL removed from watchlist.yaml before any theme or score is assigned
  confirmed_by:
  - HTFL retained in watchlist.yaml and assigned at least one theme following an earnings-cycle
    review
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: next_earnings_is_scoring_trigger
  statement: The Q2'26 earnings cycle (the next print after the 2026-06-24 add date)
    was the PM's intended trigger to assign themes and scores; evidence available
    before that print was not deemed sufficient to score.
  derived_from: 'scoring_notes: (unscored) — "themes/scoring pending next earnings
    cycle"'
  themes: []
  challenged_by:
  - 'watchlist.yaml HTFL entry shows themes: [] and scores: {} after the 2026-08-14
    Q2''26 earnings note was filed'
  confirmed_by:
  - HTFL themes and at least one scored attribute populated in watchlist.yaml with
    a commit timestamp after 2026-08-14
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: htfl_not_a_current_holding
  statement: The PM does not hold HTFL in the portfolio as of the 2026-06-24 add date;
    the name is under evaluation, not owned.
  derived_from: 'scoring_notes: (unscored) — "Tier-2 candidate"'
  themes: []
  challenged_by:
  - HTFL appears in bctk_derived.yaml as an active holding at any point before formal
    theme/score assignment
  confirmed_by:
  - HTFL absent from bctk_derived.yaml after the next scraper sync following 2026-06-24
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: factset_coverage_blocker_resolved
  statement: FactSet data coverage for HTFL was incomplete prior to 2026-06-24 (residual-20
    gap, pull-drop defect) and the watchlist add was contingent on that fix being
    applied.
  derived_from: 'scoring_notes: (unscored) — "Store B metrics-coverage expansion (residual-20
    close, factset-pull-drop fix)"'
  themes: []
  challenged_by:
  - FactSet pull for HTFL returns empty rows or a drop error for FY26/Q1 or FY26/Q2
    after 2026-06-24
  confirmed_by:
  - HTFL FactSet pull returns populated revenue, EPS, and EBITDA surprise rows for
    at least one quarter with a surpriseDate after 2026-06-24
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
