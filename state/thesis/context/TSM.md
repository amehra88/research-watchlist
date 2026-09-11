# Context for TSM (generated 2026-09-11T06:30:54+00:00)

## Open thesis assumptions (from notes/TSM/_thesis.md)
```yaml
doc_type: thesis
ticker: TSM
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#TSM
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '5'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: tsm_sole_leadingedge_foundry
  statement: At scoring date, no other foundry was producing leading-edge AI chips
    at N3/N2/A16-class nodes for named customers (NVDA, AMD, AVGO, Apple, hyperscaler
    ASICs); those conditions had not changed as of the observation date.
  derived_from: 'ai_positioning: 5 — "Sole leading-edge foundry (N3/N2/A16) manufacturing
    essentially every advanced AI chip — NVDA, AMD, AVGO, Apple, and hyperscaler ASICs"'
  themes:
  - foundry_capacity
  - ai_infrastructure_capex
  - lithography_roadmap
  challenged_by:
  - Samsung Foundry or Intel Foundry publicly announces a named AI chip designer has
    taped out or entered volume production at a node equivalent to N3 or better
  - A named TSMC AI customer (NVDA, AMD, AVGO, or a hyperscaler ASIC team) discloses
    in a filing or earnings call that it is sourcing leading-edge production from
    a non-TSMC foundry
  confirmed_by:
  - All publicly announced N3/N2/A16 tape-outs by AI chip designers continue to cite
    TSMC as sole source in earnings commentary, 20-F filings, or supply disclosures
  - TSMC earnings disclosures show AI-related advanced-node utilization at or above
    prior-period levels with no competitive displacement noted
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: cowos_no_qualified_alternative
  statement: At scoring date, no alternative CoWoS-equivalent advanced-packaging source
    had been qualified by a major AI chip customer for HBM integration; those conditions
    had not changed as of the observation date.
  derived_from: 'ai_positioning: 5 — "CoWoS advanced-packaging chokehold gating HBM
    integration"'
  themes:
  - foundry_capacity
  - ai_infrastructure_capex
  challenged_by:
  - A named AI chip customer (NVDA, AMD, AVGO, or a hyperscaler ASIC team) files or
    publicly announces qualification of an alternative advanced-packaging supplier
    for HBM integration
  - An HBM supplier (SK Hynix, Micron, Samsung) announces a production agreement using
    non-TSMC CoWoS-equivalent packaging for a named AI accelerator
  confirmed_by:
  - TSMC earnings disclosures report CoWoS capacity as fully allocated with no alternate
    source named by customers
  - No competing OSATs or foundries announce qualification of a CoWoS-equivalent process
    for a tier-1 AI customer in public filings or press releases
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: every_fabless_ai_routes_tsm
  statement: At scoring date, every major fabless AI chip design targeting leading-edge
    nodes was routed through TSMC with no leading-edge AI production volume at a competing
    foundry; those conditions had not changed as of the observation date.
  derived_from: 'competitive_advantage.distribution: 5 — "every fabless AI design
    routes through TSMC"'
  themes:
  - foundry_capacity
  - ai_infrastructure_capex
  challenged_by:
  - A named fabless AI chip designer (NVDA, AMD, AVGO, or a hyperscaler) announces
    volume production at a non-TSMC foundry on a leading-edge node
  - A hyperscaler ASIC program publicly discloses a second-source foundry qualification
    for its AI silicon
  confirmed_by:
  - Named AI chip customers cite TSMC as sole leading-edge production source in 10-K,
    20-F, or earnings call disclosures within the observation period
  - TSMC advanced-node revenue mix attributable to AI customers is flat or higher
    in successive earnings prints with no competitive displacement cited
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: n2_a16_process_leadership
  statement: At scoring date, TSMC held process node leadership on the N2/A16 roadmap
    with no competing foundry having publicly announced a comparable-node qualification
    for a tier-1 AI chip customer; those conditions had not changed as of the observation
    date.
  derived_from: 'competitive_advantage.innovation_rate: 5 — "clear process leadership
    (N2/A16 roadmap) plus CoWoS/SoIC packaging"'
  themes:
  - lithography_roadmap
  - foundry_capacity
  challenged_by:
  - Samsung Foundry or Intel Foundry publicly qualifies a tier-1 AI chip designer
    on an N2-equivalent or more-advanced node and announces a volume production timeline
  - TSMC announces a delay to N2 or A16 volume ramp while a competing foundry announces
    an accelerated schedule for a comparable node
  confirmed_by:
  - TSMC N2 volume ramp proceeds to schedule per management commentary in earnings
    disclosures with no competing foundry announcing a comparable node qualification
    with a named AI customer
  - No tier-1 AI chip designer publicly announces a tape-out at a competing foundry
    at N2-equivalent or better within the observation period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: geopolitical_risk_conditions_hold
  statement: The Taiwan/China geopolitical risk level — cited at scoring as the single
    cap on investor interest — had not escalated beyond scoring-date conditions as
    of the observation date.
  derived_from: 'potential_investor_interest.score: 4 — "Held at 4 by Taiwan/China
    geopolitical risk and ADR/foreign-listing considerations — the single cap on an
    otherwise-5 profile"'
  themes:
  - china_us_tensions
  challenged_by:
  - A Taiwan Strait military incident reported by a government or international body
    that triggers operational contingency disclosures from TSMC or named customers
  - New US, Taiwan, or China sanctions or export controls are enacted that directly
    restrict TSMC's ability to serve named AI customers or procure EUV tooling
  - A TSMC customer files a disclosure citing geopolitical risk as the basis for sourcing
    diversification away from TSMC
  confirmed_by:
  - No material cross-strait escalation events reported by official government sources
    or TSMC in regulatory filings within the observation period
  - No new semiconductor export control measures enacted that name TSMC, its customers,
    or its EUV supply chain within the observation period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: wafer_pricing_power_conditions_hold
  statement: The wafer pricing power cited at scoring date had not been reduced by
    customer renegotiations or announced price concessions as of the observation date.
  derived_from: 'potential_investor_interest.score: 4 — "wafer-price pricing power,
    AI-demand-driven revenue acceleration"'
  themes:
  - semiconductor_cycle
  - ai_infrastructure_capex
  challenged_by:
  - TSMC management discloses pricing concessions or a reduction in advanced-node
    ASPs in earnings commentary or an 8-K/6-K filing
  - A named AI chip customer publicly discloses in a filing or earnings call that
    it has renegotiated wafer pricing below prior contract levels with TSMC
  confirmed_by:
  - TSMC earnings commentary confirms flat or higher advanced-node ASPs with no announced
    price reductions to named customers
  - TSMC gross margin guidance or actuals are flat or higher relative to prior-period
    disclosures with management attributing pricing as a positive factor
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
| INC_GROSS | 2Q26 | 26340.0 | 24545.5370341628 | None | None | None | None |
| SALES | 2Q26 | 39600.0 | 38027.00614961708 | None | None | None | None |
| SALES | 1Q26 | 35200.0 | 33382.50103375017 | 35978.71453114 | 35351.04709018274 | above | 0.022122571907386413 |
| EPS | 1Q26 | None | None | 3.502371552 | 3.301410760710714 | None | None |
| INC_GROSS | 1Q26 | 22534.0 | 20031.080182327107 | 23834.3680721 | 22811.1964362648 | above | 0.057706934947190834 |
| SALES | 4Q25 | 32800.0 | 31548.353589990023 | 33138.1959335 | 33007.92726996097 | in_range | 0.010310851631097538 |
| INC_GROSS | 4Q25 | 19686.0 | 18117.680744768866 | 20653.74198405 | 19985.23945814091 | above | 0.04915889383572085 |
| EPS | 4Q25 | None | None | 3.088619625 | 2.903599286626923 | None | None |
| SALES | 3Q25 | 32400.0 | 30698.60508612073 | 32337.58201174 | 32071.9914156883 | in_range | -0.0019264811191358065 |
| INC_GROSS | 3Q25 | 18312.0 | 17557.26663525539 | 19225.89298299 | 18329.203512253065 | above | 0.0499067815088467 |
| EPS | 3Q25 | None | None | 2.848556296 | 2.626361829916 | None | None |
| EPS | 2Q25 | None | None | 2.6115343104 | 2.386964869825 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "TSM", "date_range": ["2020-06-30", "2026-03-31"], "consistency": 0.972597312090959, "sandbag_index": -0.03604498267479214, "guide_hit_rate": 0.5714285714285714, "n_guided_periods": 21, "consensus_beat_rate": 0.76, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.009017539341898768, "avg_beat_vs_consensus": 0.007976396383899059, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.9047619047619048}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "TSM", "date_range": ["2020-06-30", "2026-03-31"], "consistency": 0.96582995920386, "sandbag_index": -0.05495752312354847, "guide_hit_rate": 0.8947368421052632, "n_guided_periods": 19, "consensus_beat_rate": 0.96, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.03373331843101636, "avg_beat_vs_consensus": 0.02863054026656671, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "TSM", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.92, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.05242918881895019, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
