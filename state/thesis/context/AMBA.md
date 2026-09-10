# Context for AMBA (generated 2026-09-10T13:33:52+00:00)

## Open thesis assumptions (from notes/AMBA/_thesis.md)
```yaml
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
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| INC_GROSS | 2Q27 | 64.5525 | 63.94718181818182 | None | None | None | None |
| SALES | 2Q27 | 108.0 | 107.0699942 | None | None | None | None |
| SALES | 1Q27 | 100.0 | 96.808732405 | 100.357 | 100.11950083333333 | in_range | 0.0035699999999999933 |
| EPS | 1Q27 | None | None | 0.11 | 0.09923076923076923 | None | None |
| INC_GROSS | 1Q27 | 59.7725 | 58.0948 | 58.589 | 59.91236363636364 | in_range | -0.019800075285457398 |
| SALES | 4Q26 | 100.0 | 94.33177532727272 | 100.867 | 100.16012133333334 | in_range | 0.008670000000000044 |
| EPS | 4Q26 | None | None | 0.13 | 0.10230769230769231 | None | None |
| INC_GROSS | 4Q26 | 59.7725 | 57.2302 | 58.913 | 59.9093 | in_range | -0.01437952235559838 |
| INC_GROSS | 3Q26 | 63.21 | 55.564 | 64.586 | 63.2488 | in_range | 0.02176870748299316 |
| SALES | 3Q26 | 104.0 | 91.11948476363636 | 108.452 | 104.16063090909091 | above | 0.04280769230769229 |
| EPS | 3Q26 | None | None | 0.27 | 0.20333333333333334 | None | None |
| SALES | 2Q26 | 90.0 | 84.67508863636364 | 95.511 | 90.00064363636363 | above | 0.061233333333333285 |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "AMBA", "date_range": ["2020-04-30", "2026-04-30"], "consistency": 0.9705737547820347, "sandbag_index": -0.030627981401629076, "guide_hit_rate": 0.96, "n_guided_periods": 25, "consensus_beat_rate": 1.0, "n_consensus_periods": 26, "avg_beat_vs_guidance": 0.01915794907549062, "avg_beat_vs_consensus": 0.020417636774823847, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "AMBA", "date_range": ["2020-04-30", "2026-04-30"], "consistency": 0.9632689214349605, "sandbag_index": -0.045057659132606696, "guide_hit_rate": 0.48, "n_guided_periods": 25, "consensus_beat_rate": 0.5384615384615384, "n_consensus_periods": 26, "avg_beat_vs_guidance": 0.0013663498658418871, "avg_beat_vs_consensus": 0.004046730564512796, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.92}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "AMBA", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 23, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.4674864009099808, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
