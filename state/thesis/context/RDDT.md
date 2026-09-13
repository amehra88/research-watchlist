# Context for RDDT (generated 2026-09-13T20:38:58+00:00)

## Open thesis assumptions (from notes/RDDT/_thesis.md)
```yaml
doc_type: thesis
ticker: RDDT
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#RDDT
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: rddt_arpu_expansion_not_at_ceiling
  statement: 'Advertiser demand per DAUq is not at a ceiling: ARPU of $6.18 (+36%
    YoY) at Q2 2026 implies ad pricing or inventory fill has not yet saturated'
  derived_from: 'themes: ad_market_strength — MD&A: ''Average revenue per unique was
    $6.18 for the three months ended June 30, 2026, an increase of 36% year-over-year'''
  themes:
  - ad_market_strength
  challenged_by:
  - Q3 2026 10-Q filing showing ARPU growth rate decelerating materially below Q2's
    36% YoY without a volume offset
  - Earnings call or 8-K disclosing a named large-advertiser pullback or CPM pricing
    compression in the subsequent quarter
  confirmed_by:
  - Q3 2026 10-Q filing showing ARPU growth at or above 36% YoY
  - Full-year 2026 guidance raise for revenue per unique in a subsequent earnings
    release
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 8.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: search_referral_traffic_still_material
  statement: Search engine referral traffic is a material DAUq driver at the scoring
    date, such that third-party algorithm changes can move the total DAUq metric in
    a reported quarter
  derived_from: 'themes: search_disruption — MD&A: ''change in global DAUq...was primarily
    driven by the combination of third-party search engine algorithm changes''; news:
    ''Reddit stock declines as concerns over falling search referral traffic weigh
    on sentiment'''
  themes:
  - search_disruption
  challenged_by:
  - Q3 2026 10-Q MD&A omitting third-party search algorithm changes as a cited DAUq
    driver
  - Company disclosure that logged-out or search-sourced sessions have declined below
    a cited materiality threshold
  confirmed_by:
  - Q3 2026 10-Q citing third-party search algorithm changes as a DAUq driver for
    a second consecutive quarter
  - Investor day or filing quantifying search as a top-two acquisition channel with
    a stated share of total sessions
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 2.0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ai_data_licensing_contracts_intact
  statement: AI data-licensing agreements flagged as a watch-item at the scoring date
    have not been disclosed as cancelled or non-renewed as of that date
  derived_from: 'themes: ai_re_architected_incumbent — news summary: ''More relevant
    triggers would be advertising revenue trends or progress on AI data-licensing
    agreements'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - 8-K or press release disclosing non-renewal or termination of a named AI data-licensing
    agreement
  - 10-Q note showing licensing revenue bundled into 'Other' with a sequential decline
    and no offsetting disclosure
  confirmed_by:
  - Press release or 8-K announcing renewal or expansion of a named AI data-licensing
    agreement
  - 10-Q or 10-K disclosing a separate data-licensing revenue line item with a year-over-year
    increase
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 4.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| SALES | 3Q26 | 865.0 | 829.7208999162036 | None | None | None | None |
| SALES | 2Q26 | 720.0 | 710.8983556385116 | 804.905 | 731.002273142275 | above | 0.11792361111111108 |
| INC_GROSS | 2Q26 | None | None | 734.8248333333333 | 664.7685263157895 | None | None |
| EPS | 2Q26 | None | None | 1.25 | 0.9493291616833334 | None | None |
| INC_GROSS | 1Q26 | None | None | 607.0754210526316 | 550.2664705882353 | None | None |
| SALES | 1Q26 | 600.0 | 576.8697582694273 | 663.0 | 607.7406358521384 | above | 0.105 |
| EPS | 1Q26 | None | None | 1.01 | 0.568743146126087 | None | None |
| EPS | 4Q25 | None | None | 1.24 | 0.9370112232217391 | None | None |
| INC_GROSS | 4Q25 | None | None | 667.008 | 608.5614117647059 | None | None |
| SALES | 4Q25 | 660.0 | 637.5023507170434 | 725.607 | 665.9312983277416 | above | 0.09940454545454541 |
| SALES | 3Q25 | 540.0 | 473.3305121756522 | 585.0 | 549.1200843075695 | above | 0.08333333333333333 |
| EPS | 3Q25 | None | None | 0.8 | 0.5248875545047619 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "RDDT", "date_range": ["2024-06-30", "2026-06-30"], "consistency": 0.9639828131201077, "sandbag_index": -0.06219093681349011, "guide_hit_rate": 1.0, "n_guided_periods": 9, "consensus_beat_rate": 1.0, "n_consensus_periods": 10, "avg_beat_vs_guidance": 0.11747406407190668, "avg_beat_vs_consensus": 0.09902722536312113, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "RDDT", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 10, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.11240645830368258, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "RDDT", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 1.0, "n_consensus_periods": 9, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 1.2318636025545582, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
