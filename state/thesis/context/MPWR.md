# Context for MPWR (generated 2026-09-13T20:28:25+00:00)

## Open thesis assumptions (from notes/MPWR/_thesis.md)
```yaml
doc_type: thesis
ticker: MPWR
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MPWR
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: mpwr_nvda_supplier_at_scoring
  statement: MPWR held a qualified power-delivery supplier position with NVDA at the
    time of scoring; that status had not been displaced.
  derived_from: 'ai_positioning: 4 — "an NVDA power-delivery supplier"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - NVDA 10-K, supply-chain filing, or platform teardown names an alternative power-module
    vendor on the same GPU board generation
  - MPWR drops below the >10% customer disclosure threshold for NVDA in a subsequent
    10-K
  confirmed_by:
  - MPWR 10-K or 10-Q discloses NVDA as a >10% customer
  - Independent platform teardown identifies MPWR power-module SKUs on current NVDA
    GPU board
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ai_server_design_in_intact
  statement: MPWR had active design-ins on major AI-server platforms at scoring; no
    platform refresh had selected an alternative power-management vendor.
  derived_from: 'competitive_advantage.distribution: 4 — "designed into major AI-server
    platforms plus broad analog base"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - OEM or hyperscaler platform BOM for the next server generation publicly identifies
    a competing power-management vendor in MPWR's slot
  - MPWR data-center segment revenue declines sequentially while overall AI-server
    shipment volumes are flat or rising
  confirmed_by:
  - MPWR earnings call or investor presentation cites design-win count or design-in
    revenue on a named next-generation AI-server platform
  - System integrator or analyst teardown report identifies MPWR components on a newly
    released AI server SKU
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-13'
  draft: true
- id: nvda_concentration_caps_distribution
  statement: NVDA single-customer concentration was the binding constraint that prevented
    the distribution score from exceeding 4 at scoring; it had not been diversified
    away.
  derived_from: 'competitive_advantage.distribution: 4 — "carries single-customer
    concentration risk (NVDA)"'
  themes:
  - ai_infrastructure_capex
  - semiconductor_cycle
  challenged_by:
  - MPWR wins and publicly discloses design-ins with a second hyperscaler's custom
    AI-silicon program, reducing NVDA revenue share
  - NVDA falls below the material-customer disclosure threshold in a subsequent MPWR
    annual filing
  confirmed_by:
  - MPWR 10-K discloses NVDA as >10% customer for two consecutive annual periods post-scoring
  - MPWR management quantifies NVDA-related revenue as a majority of data-center segment
    on an earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: ai_server_units_and_density_lever
  statement: AI-server unit volume and per-server power density — not AI software
    or model revenue — were the primary revenue levers for MPWR at scoring.
  derived_from: 'ai_positioning: 4 — "well-levered to AI-server unit growth and rising
    power density"'
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - MPWR data-center revenue diverges materially from publicly reported AI-server
    shipment unit trends for two consecutive quarters
  - MPWR management identifies a non-AI-server segment as the primary revenue growth
    driver on an earnings call
  confirmed_by:
  - MPWR segment or product-family revenue disclosure shows data-center growing as
    a share of total for two consecutive quarters
  - MPWR management explicitly ties revenue guidance to AI-server unit build forecasts
    on a quarterly earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: valuation_drag_investor_interest
  statement: Valuation was a drag on potential investor interest at scoring — it was
    cited as a limiting factor, not a neutral or positive attribute.
  derived_from: 'potential_investor_interest.score: 4 — "Valuation and single-customer
    (NVDA) concentration temper the score"'
  themes:
  - semiconductor_cycle
  - ai_infrastructure_capex
  challenged_by:
  - MPWR price-to-earnings or EV/Sales compresses to the median of publicly traded
    power-analog peers following a miss or guidance cut
  - Sell-side consensus price targets fall below MPWR's trailing-twelve-month average
    market price
  confirmed_by:
  - MPWR trades at a sustained premium greater than 1.5x the NTM P/E of publicly traded
    power-analog peers for two consecutive quarters post-scoring
  - MPWR investor-day or roadshow materials include a slide defending premium multiple
    via content-per-server growth
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
| SALES | 3Q26 | 1150.0 | 998.3597142857143 | None | None | None | None |
| INC_GROSS | 3Q26 | 638.28 | 546.9690833333333 | None | None | None | None |
| EPS | 2Q26 | None | None | 6.5 | 5.871415952407143 | None | None |
| INC_GROSS | 2Q26 | 500.43 | 453.1823846153846 | 541.07 | 501.0163333333333 | above | 0.08121015926303388 |
| SALES | 2Q26 | 900.0 | 817.1092133333333 | 980.6 | 903.3025 | above | 0.08955555555555558 |
| INC_GROSS | 1Q26 | 432.93 | 408.37584615384617 | 446.391 | 433.81461538461537 | above | 0.031092786362691457 |
| EPS | 1Q26 | None | None | 5.1 | 4.89903764403125 | None | None |
| SALES | 1Q26 | 780.0 | 737.9674866666667 | 804.185 | 781.9301133333333 | above | 0.031006410256410186 |
| INC_GROSS | 4Q25 | 410.73 | 401.3750769230769 | 417.078 | 411.42715384615383 | in_range | 0.015455408662624976 |
| EPS | 4Q25 | None | None | 4.79 | 4.74139176954375 | None | None |
| SALES | 4Q25 | 740.0 | 725.2662666666666 | 751.155 | 742.3995933333333 | above | 0.015074324324324288 |
| SALES | 3Q25 | 720.0 | 679.3779071428571 | 737.176 | 722.3988733333333 | above | 0.023855555555555616 |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "MPWR", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.9748639936300117, "sandbag_index": -0.05336972340312588, "guide_hit_rate": 1.0, "n_guided_periods": 27, "consensus_beat_rate": 1.0, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.030333238690088478, "avg_beat_vs_consensus": 0.02888989886536465, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "MPWR", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.9198588852046761, "sandbag_index": -0.10041223734461253, "guide_hit_rate": 0.7407407407407407, "n_guided_periods": 27, "consensus_beat_rate": 0.8571428571428571, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.00801128939316182, "avg_beat_vs_consensus": 0.027623105727738153, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.9629629629629629}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "MPWR", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 28, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.03935023229709475, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
