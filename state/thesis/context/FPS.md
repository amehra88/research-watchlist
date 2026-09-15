# Context for FPS (generated 2026-09-15T06:31:55+00:00)

## Open thesis assumptions (from notes/FPS/_thesis.md)
```yaml
doc_type: thesis
ticker: FPS
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#FPS
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '3'
  competitive_advantage.overall: '3'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: fps_datacenter_revenue_material
  statement: FPS derives a material share of revenue from datacenter customers purchasing
    power-transformer and electrical equipment.
  derived_from: 'ai_positioning: 3 — ''large power-transformer and electrical-equipment
    supplier into datacenters (per operator)'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - S-1 or annual filing showing datacenter end-market below a material portion of
    total revenue
  - Earnings call segment disclosure placing datacenter-related revenue below single-digit
    percent of total
  confirmed_by:
  - Filing or earnings call naming datacenter operators as significant customers or
    disclosing a datacenter revenue segment
  - Customer concentration table in 10-K listing hyperscalers or datacenter operators
    among top customers
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fps_indirect_ai_exposure_power_only
  statement: FPS's AI-infrastructure exposure is indirect—via datacenter power and
    electrical-equipment demand—and FPS offers no AI-native products (models, chips,
    or software).
  derived_from: 'ai_positioning: 3 — ''a datacenter-power-buildout beneficiary, not
    AI'''
  themes:
  - ai_infrastructure_capex
  - data_center_deployment_constraints
  challenged_by:
  - FPS product launch or investor materials describing AI-specific product lines
    marketed to GPU-cluster or AI-datacenter buyers
  - Revenue or segment disclosure revealing a software, semiconductor, or AI-model
    product line
  confirmed_by:
  - Product catalog and S-1 business description limited to power-transformer and
    switchgear product lines
  - Absence of R&D or segment disclosures referencing semiconductor, software, or
    AI-model products
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: transformer_supply_constrained_at_scoring
  statement: Power-transformer supply into datacenter projects was constrained at
    the scoring date, supporting the demand-pull cited as the basis for the distribution
    score.
  derived_from: 'competitive_advantage.distribution: 3 — ''3+ on transformer-shortage
    demand pull'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - Industry publication or peer-supplier filing showing transformer lead times returning
    to pre-shortage norms
  - Hyperscaler or utility commentary disclosing transformer procurement no longer
    on the critical path for datacenter delivery
  confirmed_by:
  - FPS backlog or order-book disclosure showing extended delivery lead times as of
    or after scoring date
  - Peer earnings call or industry survey confirming transformer supply still tight
    post-scoring
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fps_competes_on_capacity_not_innovation
  statement: FPS's competitive position in heavy electrical equipment is driven by
    manufacturing capacity and execution, not product innovation rate.
  derived_from: 'competitive_advantage.innovation_rate: 3 — ''capacity/execution-driven
    not fast-innovation'''
  themes:
  - data_center_deployment_constraints
  challenged_by:
  - FPS patent filings or product announcements describing differentiated technology
    vs. established transformer peers
  - Customer win attributed to product design advantage rather than delivery capacity
    or pricing
  confirmed_by:
  - Earnings or investor-day commentary citing production ramp and manufacturing capacity
    as primary competitive levers
  - Capital expenditure disclosures focused on plant expansion with R&D spend below
    a minimal threshold
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fps_lockup_overhang_active_at_scoring
  statement: The IPO lock-up period was in effect at the scoring date, with insider
    shares restricted from sale.
  derived_from: 'potential_investor_interest.score: 4 — ''Lock-up overhang and a limited
    public track record are watch-items'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - Prospectus lock-up expiration date confirmed to have fallen prior to the scoring
    date of 2026-06-02
  - Form 4 filings showing insider sales executed before the scoring date
  confirmed_by:
  - Prospectus or S-1 filing confirming lock-up expiration date falls after 2026-06-02
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: fps_below_two_public_earnings_cycles
  statement: At scoring, FPS had completed fewer than two quarterly earnings cycles
    as a public company, leaving execution track record as a public issuer unverified.
  derived_from: 'competitive_advantage.distribution: 3 — ''a new public company so
    distribution/track-record is still proving''; potential_investor_interest.score:
    4 — ''limited public track record are watch-items'''
  themes:
  - data_center_deployment_constraints
  - ai_infrastructure_capex
  challenged_by:
  - SEC EDGAR filing history showing two or more 10-Q filings prior to 2026-06-02
  - Earnings call transcripts prior to scoring date showing multiple quarters of public
    guidance and delivery
  confirmed_by:
  - SEC EDGAR filing history showing fewer than two 10-Q filings as of 2026-06-02
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
| SALES | 4Q26 | 412.0 | 395.1702435333125 | None | None | None | None |
| INC_GROSS | 3Q26 | None | None | 131.1192 | 120.8156 | None | None |
| EPS | 3Q26 | None | None | 0.17818972222222224 | 0.15843289439 | None | None |
| SALES | 3Q26 | None | None | 378.709 | 329.5965137787 | None | None |
| INC_GROSS | 2Q26 | None | None | 101.8712 | 102.228 | None | None |
| SALES | 2Q26 | None | None | 296.404 | 286.5584285714286 | None | None |
| EPS | 2Q26 | None | None | 0.11842232222222222 | 0.1148 | None | None |

## Credibility scores
- SALES: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "SALES", "ticker": "FPS", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 2, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.09168294747555909, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "FPS", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.5, "n_consensus_periods": 2, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.04086632407379093, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "FPS", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 2, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.09071193391513033, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
