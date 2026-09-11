---
doc_type: thesis
ticker: INTC
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#INTC
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: server_share_floor_not_established
  statement: INTC server CPU unit share has not reached a quantifiable floor at the
    time of scoring; AMD EPYC Venice reporting a record 46.2% share is the most recent
    disclosed data point with no subsequent data release showing a reversal.
  derived_from: 'news: (no score assigned) — ''AMD EPYC Venice hits record 46.2% server
    share; major competitive milestone directly pressuring INTC''s server franchise'''
  themes:
  - silicon_architecture_competition
  challenged_by:
  - A third-party data release (Mercury Research, IDC, or equivalent) showing INTC
    server unit share stabilizing or recovering quarter-over-quarter
  - Intel 10-Q or earnings call disclosing sequential unit growth in the Data Center
    and AI segment
  confirmed_by:
  - A subsequent third-party data release placing AMD EPYC share at or above 50% with
    INTC share declining further
  - Intel Data Center and AI segment revenue declining sequentially in the next 10-Q
    filing
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: foundry_win_not_yet_filed
  statement: As of scoring, no signed external foundry customer contract has been
    disclosed in an Intel 8-K or press release; the foundry win flagged by analyst
    Dan Niles is an unverified analyst assertion without a corresponding public filing.
  derived_from: 'news: (no score assigned) — ''Analyst Dan Niles publicly called an
    imminent foundry customer win for Intel'''
  themes:
  - foundry_capacity
  challenged_by:
  - Intel 8-K or investor press release naming a specific external foundry customer
    and process node commitment
  - IFS management disclosing a signed customer agreement in an SEC filing or earnings
    call transcript
  confirmed_by:
  - Intel's next earnings call transcript passing without disclosure of a named external
    leading-edge foundry customer
  - No foundry customer announcement appearing in an Intel SEC filing within 60 days
    of the analyst flag
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: net_debt_gap_holds_post_equity_raise
  statement: At Q2 2026 close, Intel carries approximately $20.8B net debt (total
    debt $50.5B versus cash and short-term investments $29.7B); the $15B equity raise
    proceeds were deployed to retire the Apollo Ireland SCIP minority interest and
    refinance senior notes, not to reduce the net-debt position.
  derived_from: 'mda: (no score assigned) — ''Total cash and short-term investments
    $29,727 ... Total debt $50,537 ... we acquired the minority ownership interest
    in our majority-owned and consolidated Ireland SCIP VIE for aggregate cash consideration
    of $14.2 billion'''
  themes:
  - foundry_capacity
  - ai_infrastructure_capex
  challenged_by:
  - Next Intel 10-Q showing total debt below $45B or total cash and short-term investments
    above $35B
  - Intel announcing a binding asset sale (e.g., Altera stake, IFS minority interest)
    generating proceeds that retire gross debt
  confirmed_by:
  - Next Intel 10-Q showing net debt at or above $20B with no disclosed asset-sale
    or debt-paydown event
  - Intel drawing on its $7B revolving credit facility or issuing commercial paper
    prior to the next earnings release
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 4.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `thin` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
