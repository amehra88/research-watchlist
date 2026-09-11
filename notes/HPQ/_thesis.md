---
doc_type: thesis
ticker: HPQ
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#HPQ
- notes/HPQ/20260528-2Q26.md
- notes/HPQ/20260827-3Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: ps_revenue_yoy_positive_q326
  statement: 'Personal Systems segment revenue growth (YoY) was positive in Q3''26
    at the time of scoring (conditions at scoring: +18%); the revenue leg of the pc_demand
    thesis had not broken despite a 16% unit volume decline.'
  derived_from: 'pc_demand: Drift — ''record revenue $11.8B, +18% YoY (Commercial
    +22%, Consumer +10%); units -16%'''
  themes:
  - pc_demand
  challenged_by:
  - Q4'26 10-Q showing Personal Systems segment revenue below the prior-year Q4'25
    level on a reported basis
  - HP management disclosing accelerated channel inventory destocking that reverses
    YoY PS revenue growth in Q4'26 prepared remarks
  confirmed_by:
  - Q4'26 10-Q Personal Systems segment revenue line exceeding the prior-year Q4'25
    level
  - Q4'26 earnings press release citing ninth-or-more consecutive quarter of PS top-line
    growth
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ps_op_profit_not_materially_down
  statement: 'Personal Systems earnings from operations at Q3''26 ($537M) were not
    materially below the prior-year comparable ($541M); the profit pool had not collapsed
    in dollar terms despite the unit volume contraction (conditions at scoring: -0.7%
    YoY).'
  derived_from: 'pc_demand: Drift — ''Personal Systems earnings from operations $537M
    vs. $541M in Q3''25 — down 0.7% in absolute dollars on 18% more revenue'''
  themes:
  - pc_demand
  challenged_by:
  - Q4'26 10-Q showing PS segment earnings from operations below $480M, implying pricing
    and mix failed to absorb memory and storage cost inflation
  - HP issuing an intra-quarter update disclosing PS operating margin guidance below
    3.5% for Q4'26
  confirmed_by:
  - Q4'26 10-Q showing PS segment earnings from operations at or above $510M
  - Q4'26 earnings press release citing PS operating margin within 100bps of Q3'26's
    4.6%
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: q4_is_ps_margin_trough
  statement: Q4'26 is the Personal Systems segment operating margin trough per management's
    Q3'26 guidance arithmetic (ex-refund Q4 EPS guide $0.61–$0.71 vs. ex-refund Q3
    actual $0.72); PS margin in Q1'27 does not print below the Q4'26 actual.
  derived_from: 'pc_demand: Drift — ''Q4''26 is the Personal Systems margin trough
    is confirmed by the guidance arithmetic itself, not merely by management''s verbal
    reaffirmation'''
  themes:
  - pc_demand
  challenged_by:
  - Q1'27 10-Q showing PS segment operating margin below the Q4'26 actual reported
    in the Q4'26 10-Q
  - HP Q4'26 earnings call disclosing that memory and storage cost inflation accelerated
    further into FY27, invalidating the Q4 trough call
  confirmed_by:
  - Q1'27 10-Q showing PS segment operating margin at or above the Q4'26 actual
  - Q4'26 earnings press release showing PS operating margin sequentially above Q3'26's
    4.6%, pulling the trough into Q3
  status: open
  status_source: draft
  pressure:
    confirm: 5.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ai_pc_mix_46pct_q326
  statement: AI PCs comprised 46% of HP PC unit shipments in Q3'26 as stated in prepared
    remarks (conditions at scoring); this figure had not been contradicted by a subsequent
    10-Q segment disclosure.
  derived_from: 'pc_demand: Drift — ''AI PCs: 46% of Q3 PC shipments (transcript),
    vs. 44% in Q2''26 and 35% in Q1''26'''
  themes:
  - pc_demand
  challenged_by:
  - Q3'26 10-Q or Q4'26 10-Q disclosure revising the Q3'26 AI PC share below 40%
  - Q4'26 earnings prepared remarks citing AI PC share of shipments below the Q2'26
    44% level
  confirmed_by:
  - Q4'26 earnings prepared remarks citing AI PC share at or above 46% of shipments
  - Q3'26 10-Q segment narrative corroborating the 46% AI PC shipment mix without
    revision
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fy26_eps_raise_tariff_composition
  statement: The FY26 non-GAAP EPS guidance midpoint increase from $3.00 to $3.24
    is attributable primarily to tariff refunds ($0.19 estimated) rather than underlying
    operations (core operating raise approximately $0.05 at the midpoint, zero at
    the high end) per Q3'26 management disclosure (conditions at Q3'26 scoring).
  derived_from: 'pc_demand: Drift — ''Core operating raise +$0.05 at the midpoint
    and zero at the high end... the apparent ~+8% guidance raise is ~80% tariff refunds'''
  themes:
  - pc_demand
  challenged_by:
  - Q4'26 10-K disclosing total FY26 IEEPA tariff refunds recognized below $0.12/share
    diluted, reducing the refund share of the raise below 50%
  - HP issuing a restated FY26 EPS bridge in the Q4'26 press release showing operating
    improvement accounted for more than half of the raise vs. the prior guide midpoint
  confirmed_by:
  - Q4'26 10-K disclosing total FY26 IEEPA tariff refund recovery at or above $0.17/share
    diluted
  - Q4'26 earnings press release decomposing FY26 EPS vs. prior guidance with tariff
    refunds as the largest single line item in the bridge
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `notes` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
