---
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
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 6.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
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
    confirm: 2.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-10'
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
    confirm: 6.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
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
    confirm: 4.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-10'
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
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
