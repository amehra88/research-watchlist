# Context for ARM (generated 2026-09-13T20:00:03+00:00)

## Open thesis assumptions (from notes/ARM/_thesis.md)
```yaml
doc_type: thesis
ticker: ARM
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#ARM
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: arm_ai_chip_corr_licensing
  statement: ARM's price co-movement with AI chip names at scoring reflects material
    royalty revenue exposure to AI compute silicon, not only broad sector sympathy.
  derived_from: 'RECENT NEWS: — "ARM''s continued co-movement with AI chip names confirms
    its role as an AI compute proxy"'
  themes:
  - silicon_architecture_competition
  - inference_compute_economics
  challenged_by:
  - ARM earnings print showing AI/compute royalty revenue flat or declining in a quarter
    when NVDA or AMD revenue grows materially
  - ARM disclosing that correlated price moves were not accompanied by corresponding
    royalty backlog or bookings increases
  confirmed_by:
  - ARM earnings disclosing AI-specific royalty revenue growing faster than total
    company royalty revenue
  - A hyperscaler filing or investor day quantifying volume of ARM-architecture chips
    deployed in inference clusters
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: arm_arch_no_qualified_alt
  statement: At scoring, no competing ISA has reached production-scale qualification
    at a major hyperscaler that would displace ARM architecture in AI inference silicon.
  derived_from: 'RECENT NEWS: — "persistent retail attention on ARM''s valuation relative
    to its silicon architecture opportunity is a background sentiment indicator"'
  themes:
  - chip_design_competition
  - silicon_architecture_competition
  challenged_by:
  - A hyperscaler filing or press release announcing production deployment of a RISC-V-based
    AI inference chip at volume scale
  - An ARM licensee publicly announcing qualification of a second-source ISA for its
    next-generation AI accelerator program
  confirmed_by:
  - ARM disclosing a new compute subsystem license with a named AI chip customer in
    an SEC filing or earnings call
  - A hyperscaler announcing renewal or expansion of an ARM architecture license for
    data center or AI silicon
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: arm_anet_capex_additive
  statement: At scoring, AI infrastructure capex directed at compute silicon (ARM's
    addressable layer) and at networking (ANET's addressable layer) is treated as
    additive by hyperscalers, not as substitutable budget lines.
  derived_from: 'RECENT NEWS: — "ANET and ARM represent complementary layers of the
    AI infrastructure stack — switching and CPU/accelerator architecture — and their
    comparative growth rates inform where incremental AI capex is landing"'
  themes:
  - ai_infrastructure_capex
  - hyperscaler_revenue_concentration
  challenged_by:
  - ARM and ANET reporting divergent revenue trajectories in the same quarter alongside
    a hyperscaler earnings call disclosing an explicit reallocation between compute
    silicon and networking budgets
  - A hyperscaler 10-Q or investor day disclosing a single consolidated AI infrastructure
    capex envelope where compute and networking compete for share
  confirmed_by:
  - ARM and ANET both reporting accelerating revenue in the same reporting quarter
    with hyperscalers citing parallel ramps in compute and networking spend
  - A hyperscaler investor day presenting separate, independently growing budget lines
    for compute silicon procurement and networking infrastructure
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
| SALES | 2Q27 | 1380.0 | 1346.4883157668519 | None | None | None | None |
| EPS | 2Q27 | 0.47 | 0.44432055019285716 | None | None | None | None |
| SALES | 1Q27 | 1260.0 | 1245.6722180076038 | 1289.0 | 1263.2924166375137 | in_range | 0.023015873015873017 |
| EPS | 1Q27 | 0.4 | 0.3654653029862069 | 0.45 | 0.40307755446666665 | above | 0.12499999999999997 |
| INC_GROSS | 1Q27 | None | None | 1262.8 | 1237.3285714285714 | None | None |
| EPS | 4Q26 | 0.58 | 0.5672120671 | 0.6 | 0.580008764525 | in_range | 0.03448275862068969 |
| INC_GROSS | 4Q26 | None | None | 1464.05 | 1440.415 | None | None |
| SALES | 4Q26 | 1470.0 | 1439.6260517857143 | 1490.0 | 1470.8114178527612 | in_range | 0.013605442176870748 |
| INC_GROSS | 3Q26 | None | None | 1220.55 | 1203.47 | None | None |
| SALES | 3Q26 | None | None | 1242.0 | 1226.8965172413793 | None | None |
| EPS | 3Q26 | None | None | 0.43 | 0.4091383424933333 | None | None |
| INC_GROSS | 2Q26 | None | None | 1114.3 | 1043.6777777777777 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "ARM", "date_range": ["2024-03-31", "2026-06-30"], "consistency": 0.9780772354537473, "sandbag_index": -0.01860995222971483, "guide_hit_rate": 1.0, "n_guided_periods": 9, "consensus_beat_rate": 0.9166666666666666, "n_consensus_periods": 12, "avg_beat_vs_guidance": 0.03509533406735121, "avg_beat_vs_consensus": 0.03902340620552542, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "ARM", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.9166666666666666, "n_consensus_periods": 12, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.04416684064140791, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"metric": "EPS", "ticker": "ARM", "date_range": ["2024-03-31", "2026-06-30"], "consistency": 0.9338399927231458, "sandbag_index": -0.040386135605048126, "guide_hit_rate": 1.0, "n_guided_periods": 9, "consensus_beat_rate": 1.0, "n_consensus_periods": 12, "avg_beat_vs_guidance": 0.1279927138446408, "avg_beat_vs_consensus": 0.14124010034361112, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
