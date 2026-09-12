# Context for GLW (generated 2026-09-12T20:18:46+00:00)

## Open thesis assumptions (from notes/GLW/_thesis.md)
```yaml
doc_type: thesis
ticker: GLW
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#GLW
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: optical_comms_primary_driver
  statement: Optical communications is the dominant contributor to GLW's above-trend
    revenue growth as of Q2 2026, accounting for more than half of the incremental
    year-over-year dollar increase.
  derived_from: 'MD&A: net sales — ''increase in sales for optical communication products
    of $506 million'' vs. total Q2 net sales increase of $643 million'
  themes:
  - ai_infrastructure_capex
  - ai_compute_topology
  challenged_by:
  - Optical communications segment revenue growth rate falls below the company-level
    17% growth rate in the next 10-Q filing
  - A named hyperscaler publicly discloses a shift from fiber-based to alternative
    interconnect architecture for intra-cluster AI traffic
  confirmed_by:
  - Optical communications segment discloses a capacity expansion commitment or take-or-pay
    agreement with a named data center customer in an 8-K or earnings filing
  - Optical communications segment revenue as a share of total GLW net sales increases
    in the next quarterly filing
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 20.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: solar_margin_drag_capacity_ramp
  statement: Gross margin pressure in the Solar segment as of Q2 2026 reflects a capacity
    ramp cost, not a structural competitive cost disadvantage.
  derived_from: 'MD&A: gross margin — ''higher profit in Optical Communications was
    partially offset by temporarily higher costs to ramp up capacity to produce more
    in Solar'''
  themes:
  - solar_supply_chain
  challenged_by:
  - Solar segment gross margin fails to improve in the next two consecutive quarterly
    10-Q filings after the stated ramp period
  - A solar polysilicon competitor publicly announces lower-cost production achieving
    qualification at a shared GLW customer
  confirmed_by:
  - Solar segment gross margin expands quarter-over-quarter in the next 10-Q filing
    with no ramp-cost language in the MD&A
  - Solar capacity additions are disclosed as complete in a subsequent earnings call
    transcript or 10-Q filing
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: optical_complex_capex_cycle_risk
  statement: GLW optical revenue is exposed to the same systematic AI infrastructure
    capex cycle risk as optical networking peers, as evidenced by the simultaneous
    -4.8%/-6.0% co-movement with CIEN in the same session at the time of scoring.
  derived_from: 'recent_news: networking signal — ''CIEN fell 6.0% and GLW fell 4.8%
    in the same session — a simultaneous decline across'''
  themes:
  - networking_competitive_landscape
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - GLW discloses multi-year take-or-pay supply agreements with named hyperscalers
    in an 8-K or 10-Q filing that de-link optical revenue from spot capex cycle
  - GLW optical communications backlog is disclosed in a subsequent earnings filing
    and diverges materially upward from CIEN bookings in the same period
  confirmed_by:
  - GLW and CIEN continue to trade in the same direction on two or more subsequent
    macro-driven optical infrastructure sessions with no company-specific catalyst
  - GLW optical communications quarterly revenue growth decelerates in the next 10-Q
    in the same quarter that CIEN reports a bookings miss
  status: challenged
  status_source: evidence
  pressure:
    confirm: 2.0
    challenge: 11.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| EPS | 2Q26 | 0.75 | 0.7501296191916667 | None | None | None | None |
| SALES | 2Q26 | 4600.0 | 4650.91685523086 | None | None | None | None |
| SALES | 1Q26 | 4250.0 | 4261.613737880625 | 4345.0 | 4297.99385258723 | above | 0.02235294117647059 |
| EPS | 1Q26 | 0.68 | 0.6683182559636364 | 0.7 | 0.6917657842833334 | in_range | 0.029411764705882214 |
| INC_GROSS | 1Q26 | None | None | 1700.0 | 1617.4 | None | None |
| SALES | 4Q25 | 4350.0 | 4256.077369862523 | 4412.0 | 4361.895602931267 | above | 0.014252873563218391 |
| INC_GROSS | 4Q25 | None | None | 1682.0 | 1685.2666666666667 | None | None |
| EPS | 4Q25 | 0.7 | 0.6735069345545455 | 0.72 | 0.70694970704 | in_range | 0.0285714285714286 |
| INC_GROSS | 3Q25 | None | None | 1664.0 | 1633.4 | None | None |
| EPS | 3Q25 | 0.65 | 0.61424913575 | 0.67 | 0.6645010564818182 | in_range | 0.030769230769230795 |
| SALES | 3Q25 | 4200.0 | 4013.31518594867 | 4272.0 | 4231.496481343311 | above | 0.017142857142857144 |
| SALES | 2Q25 | 3850.0 | 3822.1525646436776 | 4045.0 | 3856.07266989806 | above | 0.05064935064935065 |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "GLW", "date_range": ["2021-03-31", "2026-03-31"], "consistency": 0.978041302463274, "sandbag_index": -0.0009461356238329071, "guide_hit_rate": 0.8095238095238095, "n_guided_periods": 21, "consensus_beat_rate": 0.92, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.021245717850384652, "avg_beat_vs_consensus": 0.022955473418024803, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.9523809523809523}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "GLW", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.6, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.026327334212205785, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"metric": "EPS", "ticker": "GLW", "date_range": ["2021-03-31", "2026-03-31"], "consistency": 0.9661542293914159, "sandbag_index": 0.02125110039114146, "guide_hit_rate": 0.8, "n_guided_periods": 20, "consensus_beat_rate": 0.8, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.03651808469529676, "avg_beat_vs_consensus": 0.08541423592128443, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
