# Context for BE (generated 2026-09-12T20:00:03+00:00)

## Open thesis assumptions (from notes/BE/_thesis.md)
```yaml
doc_type: thesis
ticker: BE
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#BE
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: 3+
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: fuel_cell_dc_power_relevance
  statement: Fuel cell technology was considered a viable power solution for data
    centers at scoring, and conditions supporting that view have not changed.
  derived_from: 'competitive_advantage.innovation_rate: 4 — "Fuel cell technology
    relevant for data center power"'
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - A major hyperscaler issues procurement guidance explicitly excluding fuel cells
    as qualified on-site generation
  - A competing on-site power technology achieves data center qualification at comparable
    cost and footprint, displacing fuel cell in operator evaluations
  confirmed_by:
  - A hyperscaler or colocation operator publicly discloses a signed fuel cell power
    purchase agreement
  - BE files an 8-K announcing a new data center power deployment contract
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: hyperscaler_partnerships_active
  statement: At scoring, hyperscaler partnerships were the mechanism supporting distribution
    improvement; those partnerships have not been paused or cancelled.
  derived_from: 'competitive_advantage.distribution: 3+ — "Distribution improving
    via hyperscaler partnerships"'
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - A named hyperscaler partner publicly pauses or cancels a BE deployment
  - BE 10-Q discloses no new hyperscaler orders and a decline in backlog attributable
    to that channel
  confirmed_by:
  - BE press release or 8-K announces a new or expanded hyperscaler deployment agreement
  - 10-Q names a hyperscaler as a significant customer or discloses capacity expansion
    under an existing agreement
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: no_dc_customer_substitution
  statement: At scoring, BE faced no active substitution of its technology by a competing
    solution at existing data center customers.
  derived_from: 'competitive_advantage.overall: 4 — "Solid competitive position"'
  themes:
  - data_center_deployment_constraints
  challenged_by:
  - An existing BE data center customer publicly qualifies a second-source supplier
    for the same power application
  - A competitor announces a design win at a site previously disclosed as a BE deployment
  confirmed_by:
  - BE renews or expands a contract with an existing data center customer at unchanged
    or improved terms
  - No second-source qualification for BE's power application disclosed in customer
    procurement filings or earnings call transcripts
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: dc_power_narrative_conditions_intact
  statement: At scoring, data center power was a hot sector driving narrative momentum
    for BE; conditions supporting that narrative have not materially unwound.
  derived_from: 'potential_investor_interest.score: 5 — "Hot sector adjacency to data
    center power. Strong narrative momentum."'
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - Hyperscaler AI capex guidance is cut in a quarterly earnings call, materially
    reducing the data center power demand narrative
  - A cluster of sell-side downgrades cites saturation or substitution in data center
    on-site power, reducing sector narrative momentum
  confirmed_by:
  - Multiple sell-side initiations or upgrades explicitly cite data center power demand
    as the primary BE thesis
  - Hyperscaler earnings calls reference on-site generation constraints driving interest
    in fuel cell sourcing
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: investor_interest_not_deteriorated
  statement: Factors supporting investor interest trajectory at scoring have not deteriorated.
  derived_from: 'potential_investor_interest.score: 5 — "Trajectory improving on investor
    interest factors"'
  themes:
  - ai_infrastructure_capex
  challenged_by:
  - 13-F filings show net institutional exits from BE in the quarter following scoring
  - Short interest in BE rises materially above levels prevailing at scoring
  confirmed_by:
  - 13-F filings show new institutional entrants disclosing BE positions citing AI
    infrastructure power demand
  - New sell-side coverage initiations in the period following scoring
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| EPS | 1Q26 | None | None | 0.44 | 0.12390406822105263 | None | None |
| SALES | 1Q26 | None | None | 751.054 | 539.941904041165 | None | None |
| INC_GROSS | 1Q26 | None | None | 225.544 | 158.8425 | None | None |
| SALES | 4Q25 | None | None | 777.683 | 648.499293755215 | None | None |
| INC_GROSS | 4Q25 | None | None | 239.895 | 206.9868181818182 | None | None |
| EPS | 4Q25 | None | None | 0.45 | 0.30679110555555555 | None | None |
| SALES | 3Q25 | None | None | 519.048 | 427.1464374297111 | None | None |
| INC_GROSS | 3Q25 | None | None | 157.637 | 123.8751 | None | None |
| EPS | 3Q25 | None | None | 0.15 | 0.100698425 | None | None |
| INC_GROSS | 2Q25 | None | None | 113.35 | 96.7756 | None | None |
| EPS | 2Q25 | None | None | 0.1 | 0.012108142857142857 | None | None |
| SALES | 2Q25 | None | None | 401.242 | 375.9968204250111 | None | None |

## Credibility scores
- SALES: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "SALES", "ticker": "BE", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.64, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.044109984144779076, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "BE", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.6, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.0726780350623568, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "BE", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.4782608695652174, "n_consensus_periods": 23, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": -2.1322955262828147, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
