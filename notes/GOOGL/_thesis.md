---
doc_type: thesis
ticker: GOOGL
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#GOOGL
- notes/GOOGL/20260204-4Q25.md
- notes/GOOGL/20260429-1Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: cloud_supply_constraint_holds
  statement: Conditions at the time of scoring — Cloud revenue constrained by supply
    rather than by demand — still hold as of the most recent quarter in the record.
  derived_from: '1Q26 earnings note §3: ''Our Cloud revenue would have been higher
    if we were able to meet the demand''; ''This is now the fourth consecutive print
    framing Cloud as supply-constrained'''
  themes: []
  challenged_by:
  - A subsequent 10-Q or earnings transcript in which management cites weakening demand,
    customer deferrals, or rising deal slippage rather than supply as the binding
    constraint on Cloud revenue
  - A quarter in which Cloud revenue growth decelerates while data-center capacity
    expansions are announced as completed
  confirmed_by:
  - Q2 2026 earnings transcript (2026-07-23) in which management again attributes
    any Cloud revenue shortfall to capacity or supply limitations
  - A 10-Q or 8-K disclosing new data-center lease signings or power procurement contracts
    alongside supply-constraint language
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: search_ai_not_cutting_revenue
  statement: AI Overviews and AI Mode, at the time of scoring, are not reducing aggregate
    Search advertising revenue per query.
  derived_from: '4Q25 earnings note §4 search_disruption: ''AI Mode + AI Overviews
    as drivers, not headwinds''; 1Q26 actuals table: ''Google Search & other ad revenue
    $60.4B (+19% y/y)'''
  themes: []
  challenged_by:
  - A 10-Q or earnings transcript disclosing a decline in Search paid-click volume
    or cost-per-click in a quarter where overall Search query volume is flat or rising
  - An SEC filing or management disclosure attributing Search revenue deceleration
    to AI-generated-answer zero-click behavior
  confirmed_by:
  - A subsequent 10-Q reporting paid-click growth and stable or rising cost-per-click
    alongside continued AI Overview rollout milestones
  - An earnings transcript in which management quantifies advertiser ROI improvement
    tied to AI Max or AI Mode placements
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fy26_capex_guide_not_cut
  statement: The FY26 capex guidance of $180–190B disclosed at the 1Q26 print has
    not been revised downward as of the scoring date.
  derived_from: '1Q26 earnings note §3: ''FY26 CapEx guidance raised to $180–190B
    (from prior $175–185B)'' (Ashkenazi, p.11–12)'
  themes: []
  challenged_by:
  - A subsequent 10-Q, 8-K, or earnings transcript revising FY26 capex guidance below
    $180B
  - A management disclosure citing macroeconomic conditions, regulatory decisions,
    or supply-chain constraints as reasons to defer planned infrastructure spend
  confirmed_by:
  - Q2 2026 earnings transcript (2026-07-23) reiterating FY26 capex guidance at $180–190B
    or higher
  - A 10-Q capital expenditure line for Q2 2026 consistent with the quarterly run-rate
    implied by the $180–190B annual guide
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: cloud_backlog_no_material_cancel
  statement: The $462B Cloud backlog disclosed at 1Q26 has not experienced material
    cancellation or renegotiation as of the scoring date.
  derived_from: '1Q26 earnings note actuals table: ''Cloud backlog $462B (~2x sequentially)''
    (Ashkenazi, p.11); note trajectory: ''3Q25 $155B → 4Q25 $240B → 1Q26 $462B'''
  themes: []
  challenged_by:
  - A 10-Q or earnings transcript disclosing a decline in remaining performance obligations
    (RPO) that is not explained by accelerating revenue recognition
  - A management or customer disclosure citing contract modifications, terminations,
    or force-majeure clauses tied to geopolitical or regulatory events
  confirmed_by:
  - Q2 2026 10-Q Note on remaining performance obligations showing backlog stable
    or growing from the $462B 1Q26 base
  - A Cloud revenue print in 2H26 that tracks at or above the pace implied by backlog
    burn-down at historical conversion rates
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: q1_eps_beat_was_non_operating
  statement: The 1Q26 EPS beat of +90.5% versus consensus was driven by $37.7B in
    non-operating unrealized equity gains, and the operating income result did not
    outperform consensus by a comparably large margin.
  derived_from: '1Q26 earnings note §2 reconciliation: ''driven primarily by $37.7B
    in Other Income & Expense... unrealized gains in our nonmarketable equity securities
    portfolio... NOT operating outperformance''; revenue beat was +2.73%'
  themes: []
  challenged_by:
  - A subsequent 10-Q restatement or analyst-accessible FactSet surprise figure showing
    that GAAP operating income also beat consensus by more than the revenue beat percentage
    implies
  - A period in which OI&E returns to near-zero and EPS growth rate remains above
    80% y/y, indicating the operating baseline was permanently higher
  confirmed_by:
  - Q2 2026 10-Q in which OI&E normalizes to a lower level and EPS growth reverts
    closer to operating income growth
  - A FactSet or EDGAR disclosure confirming that the Anthropic or SpaceX equity stakes
    drove the 1Q26 OI&E spike as mark-to-market
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: tpu_rev_skewed_to_2027
  statement: TPU hardware sale agreements signed through 1Q26 will recognize the significant
    majority of their revenues in 2027, with only a small percentage recognized in
    the remainder of 2026.
  derived_from: '1Q26 earnings note §3: ''small percent of the revenues from these
    agreements later this year, with the vast majority of revenues to be realized
    in 2027'' (Ashkenazi, p.11); MD&A: ''we began recognizing revenues from these
    agreements, with the significant majority to be recognized in 2027'''
  themes: []
  challenged_by:
  - A Q2, Q3, or Q4 2026 10-Q Cloud segment disclosure showing TPU product-sale revenue
    materially above what 'small percent' of the total agreements implies
  - A management disclosure or 8-K announcing accelerated delivery schedules or new
    TPU agreements with 2026 recognition dates
  confirmed_by:
  - Q2 2026 10-Q Cloud segment note confirming TPU hardware revenue recognized to
    date is a small percentage of total agreement value
  - A subsequent earnings transcript in which Ashkenazi characterizes 2026 TPU revenue
    contribution as immaterial relative to the 2027 pipeline
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
