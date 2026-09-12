# Context for META (generated 2026-09-12T20:35:29+00:00)

## Open thesis assumptions (from notes/META/_thesis.md)
```yaml
doc_type: thesis
ticker: META
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#META
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '5'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: meta_advplus_revenue_contribution
  statement: Advantage+ and AI-driven ad recommendations were generating a measurable,
    attributable revenue contribution to META's ad business at the time of scoring.
  derived_from: 'ai_positioning: 5 — ''AI-driven ad engine (Advantage+, recommendations)...ad-AI
    monetization make it a clear AI winner'''
  themes:
  - ad_market_strength
  - ai_agent_monetization
  challenged_by:
  - META 10-Q or earnings release removing or zeroing out Advantage+ revenue attribution
    metrics, or disclosing advertiser adoption of Advantage+ products as flat or declining
    quarter-over-quarter
  - Disclosed ad revenue growth rate in a 10-Q filing decelerated to below the prior
    four-quarter average despite Advantage+ rollout
  confirmed_by:
  - META earnings call transcript or shareholder letter disclosing Advantage+ advertiser
    penetration rate, revenue contribution, or year-over-year growth rate showing
    material incremental lift vs. non-AI ad products
  - 10-Q segment disclosure attributing a quantified revenue increment to AI-optimized
    ad delivery
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: meta_llama_below_frontier
  statement: Llama open-weight models ranked below OpenAI, Google, and Anthropic frontier
    models on third-party capability benchmarks at the time of scoring.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''Llama strong but not
    frontier-leading (trails OpenAI/Google/Anthropic at the frontier)'''
  themes:
  - model_efficiency_evolution
  - silicon_architecture_competition
  challenged_by:
  - A Llama model achieves the top-ranked position on LMSYS Chatbot Arena, MMLU-Pro,
    HumanEval, or an equivalent widely-cited independent benchmark in results published
    at or after the scoring date
  - Independent third-party evaluation (published in a peer-reviewed venue or by a
    recognized AI safety org) places a Llama release above all GPT-4-class, Gemini-Ultra-class,
    and Claude-3-class models simultaneously
  confirmed_by:
  - Third-party benchmark leaderboard results published at or after the scoring date
    showing at least one GPT, Gemini, and Claude model each outranking the contemporaneous
    Llama release on the same eval suite
  - META's own model card or technical report for the most recent Llama release explicitly
    listing benchmark scores below those of named frontier competitors
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: meta_dap_3b_at_scoring
  statement: META's daily active people (DAP) across its family of apps was at or
    above 3 billion at the time of scoring.
  derived_from: 'competitive_advantage.distribution: 5 — ''3B+ daily users, unmatched
    consumer distribution and ad reach'''
  themes:
  - ad_market_strength
  challenged_by:
  - META 10-Q or earnings release disclosing DAP below 3.0 billion for the most recently
    completed quarter at the time of scoring
  confirmed_by:
  - META 10-Q or earnings release disclosing DAP at or above 3.0 billion for the most
    recently completed quarter at the time of scoring
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: meta_capex_100b_commitment
  statement: META's publicly disclosed AI infrastructure capex commitment for the
    current investment cycle was at or above $100 billion at the time of scoring.
  derived_from: 'potential_investor_interest: 4 — ''Capex scale ($100B+ AI buildout)...capex-scrutiny
    cap'''
  themes:
  - hyperscaler_capex_buildout
  challenged_by:
  - META files an 8-K, issues a press release, or discloses in an earnings release
    a downward revision to annual capex guidance that brings the stated figure below
    $100B for the current fiscal year
  confirmed_by:
  - META 10-Q, annual 10-K, earnings release, or investor day slide deck filed at
    or after the scoring date confirming aggregate capex guidance at or above $100B
    for the current fiscal year
  status: open
  status_source: draft
  pressure:
    confirm: 1.5
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: meta_reality_labs_net_loss
  statement: The Reality Labs segment was reporting an operating loss at the time
    of scoring.
  derived_from: 'potential_investor_interest: 4 — ''Reality Labs burn are the cautions'''
  themes:
  - hyperscaler_capex_buildout
  - vertical_ai_applications
  challenged_by:
  - META 10-Q filing disclosing Reality Labs segment operating income as a positive
    figure for any quarter at or after the scoring date
  confirmed_by:
  - META 10-Q filing disclosing a Reality Labs segment operating loss for the most
    recently completed quarter at the time of scoring
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
| SALES | 2Q26 | 59500.0 | 59479.01184353544 | None | None | None | None |
| EPS | 1Q26 | None | None | 10.44 | 6.697230308129167 | None | None |
| INC_GROSS | 1Q26 | None | None | 46156.56 | 44500.63461538462 | None | None |
| SALES | 1Q26 | 55000.0 | 51368.22127448353 | 56311.0 | 55556.594925838355 | in_range | 0.023836363636363635 |
| INC_GROSS | 4Q25 | None | None | 49024.23809523809 | 47305.4625 | None | None |
| EPS | 4Q25 | None | None | 8.88 | 8.212158660817021 | None | None |
| SALES | 4Q25 | 57500.0 | 57362.80432560798 | 59893.0 | 58460.683751112556 | above | 0.04161739130434783 |
| INC_GROSS | 3Q25 | None | None | 42096.62962962963 | 40004.82592592593 | None | None |
| EPS | 3Q25 | None | None | 1.05 | 6.7226415350875 | None | None |
| SALES | 3Q25 | 49000.0 | 46253.67461631167 | 51242.0 | 49508.12826868049 | above | 0.04575510204081633 |
| SALES | 2Q25 | 44000.0 | 43838.61781760082 | 47516.0 | 44821.43859675483 | above | 0.07990909090909092 |
| INC_GROSS | 2Q25 | None | None | 39068.28571428572 | 36172.26896551724 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "META", "date_range": ["2021-12-31", "2026-03-31"], "consistency": 0.9806133593597959, "sandbag_index": 0.0012472444120477594, "guide_hit_rate": 0.8888888888888888, "n_guided_periods": 18, "consensus_beat_rate": 0.88, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.03226824955732274, "avg_beat_vs_consensus": 0.02928208179979031, "guides_quantitatively": true, "guide_hit_rate_inrange": 1.0}
- INC_GROSS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "INC_GROSS", "ticker": "META", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.88, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.03675398372641588, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "META", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.76, "n_consensus_periods": 25, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.09379266766531799, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
