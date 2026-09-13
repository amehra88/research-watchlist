# Context for LRCX (generated 2026-09-13T20:05:55+00:00)

## Open thesis assumptions (from notes/LRCX/_thesis.md)
```yaml
doc_type: thesis
ticker: LRCX
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#LRCX
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '5'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: gaa_adv_pkg_tool_wins
  statement: At scoring, LRCX held tool-qualification wins at leading-edge customers
    for gate-all-around and advanced-packaging etch and deposition steps.
  derived_from: 'competitive_advantage.innovation_rate: 5 — "gate-all-around and advanced-packaging
    tool wins"'
  themes:
  - foundry_capacity
  - lithography_roadmap
  challenged_by:
  - A competitor announcing a qualified tool win at a tier-1 foundry for GAA etch
    or deposition steps in a press release or earnings call
  - A tier-1 foundry filing disclosing qualification of a second-source etch or deposition
    supplier for GAA or advanced-packaging flows
  confirmed_by:
  - LRCX disclosing in an earnings filing or investor presentation that GAA or advanced-packaging
    tool shipments contributed to revenue in the reported period
  - A tier-1 foundry naming LRCX as a qualified GAA etch/dep supplier in a technology
    roadmap filing or public announcement
  status: open
  status_source: draft
  pressure:
    confirm: 8.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: csbg_service_annuity_material
  statement: At scoring, LRCX's installed-base service revenue constituted a material
    recurring revenue stream that differentiated its distribution advantage from peers.
  derived_from: 'competitive_advantage.distribution: 5 — "entrenched WFE installed
    base with strong service annuity"'
  themes:
  - semiconductor_cycle
  challenged_by:
  - LRCX reporting a year-over-year decline in Customer Support Business Group revenue
    in a quarterly earnings filing
  - A competitor disclosing a multi-customer service contract covering tools previously
    serviced exclusively by LRCX
  confirmed_by:
  - LRCX reporting CSBG revenue growth at or above system-revenue growth in an earnings
    release
  - LRCX management citing installed-base expansion or service-contract renewals in
    an earnings call transcript
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: lrcx_exec_vs_amat_klac
  statement: At scoring, LRCX's multi-cycle execution record — measured by gross margin
    and etch/deposition market-share retention — exceeded that of AMAT and KLAC across
    the prior two WFE cycles.
  derived_from: 'competitive_advantage.overall: 5 — "execution consistency vs AMAT/KLAC
    over multiple cycles compounds the technical advantage"'
  themes:
  - semiconductor_cycle
  - hbm_competitive_landscape
  challenged_by:
  - LRCX reporting gross margin compression relative to AMAT or KLAC in a quarterly
    filing covering a WFE down-cycle period
  - Third-party WFE share data or company disclosures showing LRCX losing etch or
    deposition market share to AMAT in a down-cycle quarter
  confirmed_by:
  - LRCX reporting gross margins at or above AMAT and KLAC levels across a full WFE
    down-cycle per quarterly earnings filings
  - Independent WFE market-share analysis or LRCX disclosures showing etch/dep share
    growth through a trough period
  status: open
  status_source: draft
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: hbm_capex_near_term_driver
  statement: At scoring, HBM capacity investment by memory producers constituted a
    material near-term revenue opportunity for LRCX etch and deposition tools.
  derived_from: 'ai_positioning: 4 — "levered to AI-memory (HBM)"'
  themes:
  - hbm_competitive_landscape
  - semiconductor_cycle
  challenged_by:
  - A major HBM producer announcing a capex reduction or deferral of HBM capacity
    expansion in a quarterly filing or earnings call
  - LRCX management citing no meaningful HBM-related tool orders in an earnings call
    transcript
  confirmed_by:
  - LRCX management explicitly attributing a portion of etch or deposition revenue
    to HBM capacity build in an earnings call transcript or investor presentation
  - A major HBM producer disclosing increased etch or deposition tool purchases from
    LRCX in a capital expenditure filing
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-07'
  draft: true
- id: wfe_cycle_caps_not_comp_erosion
  statement: At scoring, the constraint on LRCX's investor-interest score reflected
    WFE spending cyclicality, with no evidence of etch or deposition competitive-position
    loss.
  derived_from: 'potential_investor_interest.score: 4 — "cap on potential_investor_interest
    at 4 reflects WFE cyclicality, NOT competitive-position erosion"'
  themes:
  - semiconductor_cycle
  - hbm_competitive_landscape
  challenged_by:
  - A competitor announcing a design win at a customer previously served exclusively
    by LRCX for etch or deposition in a leading-edge node
  - LRCX disclosing in a quarterly filing that etch or deposition revenue share declined
    versus AMAT in the same period
  confirmed_by:
  - LRCX reporting etch and deposition revenue share at or above the prior-cycle level
    in a quarterly filing
  - No public announcement of a competing tool qualification displacing LRCX in GAA,
    HBM, or advanced-packaging etch/dep flows during the period
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 12.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: china_export_drag_at_scoring
  statement: At scoring, export-control restrictions on China-bound WFE reduced LRCX's
    China-region addressable revenue versus the pre-restriction baseline.
  derived_from: 'potential_investor_interest.score: 4 — "China-revenue/export drag
    temper it"'
  themes:
  - china_export_controls
  - semiconductor_cycle
  challenged_by:
  - A U.S. government announcement of a general license or policy reversal restoring
    LRCX's ability to ship previously restricted tool categories to China
  - LRCX reporting China-region revenue at or above pre-export-control baseline levels
    in a quarterly earnings filing
  confirmed_by:
  - BIS confirming continuation of entity-list restrictions on China-bound WFE with
    no new general licenses issued covering LRCX product categories
  - LRCX disclosing in a quarterly filing that China-region revenue is below prior-year
    levels with export-control restrictions cited as a contributing factor
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
| EPS | 1Q27 | 2.15 | 1.8406709436888888 | None | None | None | None |
| SALES | 1Q27 | 8100.0 | 7109.475596552174 | None | None | None | None |
| INC_GROSS | 1Q27 | 4216.0 | 3598.4733333333334 | None | None | None | None |
| EPS | 4Q26 | 1.65 | 1.453039961951852 | 1.82 | 1.6867663557703703 | above | 0.10303030303030312 |
| SALES | 4Q26 | 6600.0 | 6040.4561830247 | 6722.238 | 6664.8350414208335 | in_range | 0.018520909090909133 |
| INC_GROSS | 4Q26 | 3337.0 | 2965.36 | 3478.74 | 3356.7375 | in_range | 0.04247527719508534 |
| SALES | 3Q26 | 5700.0 | 5333.063711244792 | 5841.488 | 5750.347901209833 | in_range | 0.02482245614035093 |
| INC_GROSS | 3Q26 | 2796.0 | 2587.2066666666665 | 2910.527 | 2828.8133333333335 | in_range | 0.040961015736766825 |
| EPS | 3Q26 | 1.35 | 1.2028839092666668 | 1.47 | 1.3639097905592592 | above | 0.0888888888888888 |
| INC_GROSS | 2Q26 | 2525.0 | 2298.8333333333335 | 2658.256 | 2539.786666666667 | in_range | 0.05277465346534648 |
| EPS | 2Q26 | 1.15 | 1.029830062444 | 1.27 | 1.1707237595518518 | above | 0.10434782608695663 |
| SALES | 2Q26 | 5200.0 | 4795.374543903864 | 5344.791 | 5233.2352063125 | in_range | 0.02784442307692311 |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "LRCX", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.9735925003271447, "sandbag_index": -0.04203784288922816, "guide_hit_rate": 0.92, "n_guided_periods": 25, "consensus_beat_rate": 0.8571428571428571, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.02404131218493299, "avg_beat_vs_consensus": 0.017630467218368473, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "LRCX", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.9540477709092757, "sandbag_index": -0.04750021487264233, "guide_hit_rate": 0.84, "n_guided_periods": 25, "consensus_beat_rate": 0.8214285714285714, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.038338306018419456, "avg_beat_vs_consensus": 0.027769649759725783, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.96}
- EPS: {"metric": "EPS", "ticker": "LRCX", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.9507687087505922, "sandbag_index": -0.06838363525437491, "guide_hit_rate": 0.96, "n_guided_periods": 25, "consensus_beat_rate": 0.9642857142857143, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.08516484015341255, "avg_beat_vs_consensus": 0.07452445543443337, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
