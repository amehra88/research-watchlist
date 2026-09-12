# Context for NXPI (generated 2026-09-12T20:34:06+00:00)

## Open thesis assumptions (from notes/NXPI/_thesis.md)
```yaml
doc_type: thesis
ticker: NXPI
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#NXPI
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: auto_revenue_q2_level_holds
  statement: Automotive end-market revenue conditions at the time of the most recent
    MD&A ($1,938M in Q2 2026, +12.1% YoY) had not yet reversed at the point the automotive_semiconductor_demand
    theme was assigned.
  derived_from: 'theme: automotive_semiconductor_demand — ''Revenue in the Automotive
    end market was $1,938 million, an increase of $209 million or 12.1% versus the
    year-ago quarter. The increase was predominantly due to growth in processors'''
  themes:
  - automotive_semiconductor_demand
  - semiconductor_cycle
  challenged_by:
  - Q3 2026 10-Q showing automotive segment revenue declining sequentially from the
    Q2 2026 level of $1,938M
  - An 8-K pre-announcement citing automotive demand deterioration before Q3 results
    are filed
  confirmed_by:
  - Q3 2026 10-Q showing automotive segment revenue at or above the Q1 2026 level
    of $1,782M
  - Q3 2026 earnings press release citing no change to full-year automotive end-market
    trajectory relative to guidance issued on the Q2 call
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 5.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: analyst_pushback_no_guide_revision
  statement: The sell-side analyst pushback recorded on the most recent earnings call
    had not been followed by a formal guidance revision or earnings warning at the
    time of scoring.
  derived_from: 'theme: semiconductor_cycle — ''analysts questioned or challenged
    NXP Semiconductors on its most recent earnings call... automotive semi upcycle
    is less clean than consensus'''
  themes:
  - semiconductor_cycle
  - automotive_semiconductor_demand
  challenged_by:
  - An 8-K filing revising or withdrawing Q3 2026 revenue guidance below the range
    issued on the Q2 earnings call
  - A press release disclosing a material change in customer order patterns in automotive
    or industrial end markets prior to the Q3 earnings release
  confirmed_by:
  - Q3 2026 earnings release showing revenue at or above the midpoint of Q3 guidance
    issued on the Q2 call
  - Management reaffirmation of Q3 or full-year 2026 guidance at a dated investor
    conference transcript before Q3 results
  status: open
  status_source: draft
  pressure:
    confirm: 6.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: comminfra_processor_growth_present
  statement: Communication Infrastructure & Other processor-driven revenue growth
    (+41.3% YoY, $452M in Q2 2026) was present in the most recent reported period
    at the time of scoring.
  derived_from: 'theme: ai_infrastructure_capex — ''Revenue in the Communication Infrastructure
    & Other end market was $452 million, an increase of $132 million or 41.3% versus
    the year-ago quarter. The increase was predominantly due to growth in processors'''
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - Q3 2026 10-Q showing Communication Infrastructure & Other revenue declining sequentially
    from the Q2 2026 level of $452M
  - A customer or hyperscaler public disclosure of a delayed or cancelled infrastructure
    build citing capex constraints, naming NXP as a supplier
  confirmed_by:
  - Q3 2026 10-Q showing Communication Infrastructure & Other revenue at or above
    $452M
  - A dated design-win announcement or customer qualification filing naming NXP processors
    in a communication infrastructure program
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| SALES | 2Q26 | 3450.0 | 3274.5534916666666 | None | None | None | None |
| INC_GROSS | 2Q26 | 2001.5 | 1883.929411764706 | None | None | None | None |
| EPS | 2Q26 | 3.505 | 3.2130281304347825 | None | None | None | None |
| EPS | 1Q26 | 2.97 | 2.945669 | 3.05 | 2.9819982173913044 | in_range | 0.02693602693602681 |
| INC_GROSS | 1Q26 | 1796.0 | 1764.96875 | 1815.0 | 1798.735294117647 | in_range | 0.010579064587973273 |
| SALES | 1Q26 | 3150.0 | 3097.8528641666667 | 3181.0 | 3157.393541666667 | in_range | 0.009841269841269842 |
| SALES | 4Q25 | 3300.0 | 3230.3410626 | 3335.0 | 3307.7834 | above | 0.010606060606060607 |
| INC_GROSS | 4Q25 | 1898.0 | 1850.8631578947368 | 1913.0 | 1899.2117647058824 | in_range | 0.007903055848261328 |
| EPS | 4Q25 | 3.28 | 3.281753125 | 3.35 | 3.3118101666666666 | in_range | 0.021341463414634235 |
| SALES | 3Q25 | 3150.0 | 3078.1835384615383 | 3173.0 | 3161.68856 | in_range | 0.007301587301587302 |
| INC_GROSS | 3Q25 | 1796.0 | 1744.285 | 1810.0 | 1801.2315789473685 | in_range | 0.0077951002227171495 |
| EPS | 3Q25 | 3.095 | 3.0614414722076924 | 3.11 | 3.1230092916666665 | in_range | 0.004846526655896504 |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "NXPI", "date_range": ["2020-06-30", "2026-03-31"], "consistency": 0.9736652657209564, "sandbag_index": -0.012907671969947118, "guide_hit_rate": 1.0, "n_guided_periods": 24, "consensus_beat_rate": 0.88, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.015197635724277228, "avg_beat_vs_consensus": 0.007968957634375533, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "NXPI", "date_range": ["2020-06-30", "2026-03-31"], "consistency": 0.9693316069084564, "sandbag_index": -0.014066867910378335, "guide_hit_rate": 0.9583333333333334, "n_guided_periods": 24, "consensus_beat_rate": 0.88, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.020891924621266943, "avg_beat_vs_consensus": 0.012325460646990777, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- EPS: {"metric": "EPS", "ticker": "NXPI", "date_range": ["2023-03-31", "2026-03-31"], "consistency": 0.9851060622313805, "sandbag_index": 0.006999926583775388, "guide_hit_rate": 0.9230769230769231, "n_guided_periods": 13, "consensus_beat_rate": 0.88, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.02180445532682164, "avg_beat_vs_consensus": -0.03451719498232282, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
