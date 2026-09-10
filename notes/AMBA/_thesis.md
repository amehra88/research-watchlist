---
doc_type: thesis
ticker: AMBA
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AMBA
- notes/AMBA/20260529-1Q27.md
- notes/AMBA/20260904-2Q27.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: ai_soc_unit_cadence_holds
  statement: The cumulative AI SoC shipment trajectory observable when T2 candidacy
    was designated (46M+ units reported at 1Q27, the cycle immediately preceding the
    2026-06-24 add date) had not plateaued or reversed by the 2Q27 print.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - 2Q27 8-K or earnings transcript citing a cumulative AI SoC count at or below the
    1Q27 figure of 46M+
  - Management withdrawing the cumulative shipped-units disclosure from 2Q27 earnings
    materials without explanation
  confirmed_by:
  - 2Q27 8-K or earnings transcript citing a cumulative AI SoC count above 46M+
  - 2Q27 10-Q product-line or segment note showing unit growth in AI-enabled products
    YoY
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hanwha_lta_unmodified
  statement: The Hanwha long-term agreement citing >$800M potential lifetime revenue
    — referenced as a constructive element in the 1Q27 note filed before the add date
    — had not been amended, scope-reduced, or terminated as of the 2Q27 10-Q filing.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - 8-K, 10-Q, or Hanwha public filing disclosing amendment, volume reduction, renegotiation,
    or termination of the LTA
  - 2Q27 or subsequent earnings call in which management omits the Hanwha LTA from
    prepared remarks with no substituted disclosure
  confirmed_by:
  - 2Q27 or subsequent earnings call transcript referencing the Hanwha LTA as active
    with scope unchanged
  - Absence of any amendment or termination notice in AMBA SEC filings through the
    2Q27 reporting period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: inventory_drift_not_break
  statement: The inventory build and FCF burn flagged as a drift watch item in the
    1Q27 note (inventory days 145, FCF −$29.6M) — conditions on record when the PM
    designated T2 candidacy — have not converted to a thesis-break event by the 2Q27
    reporting period.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - Customer order cancellations or push-outs attributable to memory cost pass-through
    disclosed in an 8-K or the 3Q27 earnings call
  - 3Q27 10-Q showing inventory days above the 2Q27 level of 157, accompanied by cash
    and marketable securities below $250M
  confirmed_by:
  - 3Q27 10-Q showing inventory days no higher than the 2Q27 level of 157
  - 3Q27 earnings call in which management characterizes the memory pass-through impact
    as bounded or resolved, with a specific quarter cited
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: auto_seg_record_not_single_peak
  statement: The all-time automotive segment quarterly revenue record reported at
    1Q27 — cited as the lead constructive element in the note filed before the 2026-06-24
    add date — was not reversed in the immediately following reporting period.
  derived_from: 'scoring_notes: ''Tier-2 candidate'' — ''Tier-2 candidate; themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - 2Q27 10-Q segment disclosure showing automotive revenue below the 1Q27 record
    level
  - 2Q27 or 3Q27 earnings call in which management explicitly flags a sequential decline
    in automotive segment revenue
  confirmed_by:
  - 2Q27 10-Q segment disclosure showing automotive revenue at or above the 1Q27 level
  - A new automotive design-win-to-production-ramp announcement disclosed in a press
    release, 8-K, or 2Q27 prepared remarks
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: scoring_deferred_one_cycle_only
  statement: The 2026-06-24 note's deferral of theme and score assignment to 'next
    earnings cycle' implied the 2Q27 print would supply sufficient product-segment
    and end-market data to form scoring convictions — not that the deferral would
    extend beyond that cycle.
  derived_from: 'scoring_notes: ''pending next earnings cycle'' — ''themes/scoring
    pending next earnings cycle'''
  themes: []
  challenged_by:
  - 'AMBA watchlist.yaml showing themes: [] and SCORES: {} unchanged after the 2Q27
    earnings review cycle closes'
  - A subsequent PM scoring note explicitly deferring theme and score assignment to
    a third earnings cycle
  confirmed_by:
  - AMBA watchlist.yaml updated with at least one non-null theme and one non-null
    score value following the 2Q27 review
  - A PM scoring note referencing specific 2Q27 data points (e.g., X7 design-win disclosures,
    segment revenue mix) as the basis for score initialization
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
