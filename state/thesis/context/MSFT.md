# Context for MSFT (generated 2026-09-12T20:35:25+00:00)

## Open thesis assumptions (from notes/MSFT/_thesis.md)
```yaml
doc_type: thesis
ticker: MSFT
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#MSFT
reviewed_by_operator: false
scores:
  ai_positioning: 4-
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '3'
proposed_scores: {}
assumptions:
- id: openai_partnership_alignment_loose
  statement: At scoring, strategic alignment between MSFT and OpenAI had loosened,
    with OpenAI actively moving toward operational independence from Microsoft.
  derived_from: 'ai_positioning: 4- — ''OpenAI partnership has materially weakened
    — strategic alignment loosening, OpenAI moving toward independence'''
  themes:
  - ai_re_architected_incumbent
  - enterprise_ai_adoption
  challenged_by:
  - MSFT and OpenAI announce a new multi-year exclusivity extension or expanded compute-for-equity
    agreement disclosed in a press release or SEC filing
  confirmed_by:
  - OpenAI signs a compute or cloud partnership with a competing hyperscaler (AWS,
    GCP) disclosed in a press release or regulatory filing
  - OpenAI releases a consumer or enterprise product that directly competes with an
    existing Microsoft-branded offering without MSFT co-branding
  status: open
  status_source: draft
  pressure:
    confirm: 3.5
    challenge: 0.5
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: msft_no_native_frontier_model
  statement: At scoring, MSFT had not shipped a proprietary frontier-scale AI model
    and relied on OpenAI models as its primary AI capability.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''Late to innovate on
    a native AI model'''
  themes:
  - ai_re_architected_incumbent
  - ai_infrastructure_software
  challenged_by:
  - MSFT publicly releases a proprietary frontier-scale model evaluated against GPT-4o
    or Claude on a named third-party benchmark leaderboard
  confirmed_by:
  - MSFT earnings call or product keynote cites only OpenAI models as primary AI capability
    with no proprietary frontier model disclosed or announced
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: anthropic_app_optimization_share_gain
  statement: At scoring, Anthropic had captured application optimization surface area
    at the expense of MSFT's positioning in that segment.
  derived_from: 'competitive_advantage.overall: 4 — ''Anthropic taking surface area
    on application optimization'''
  themes:
  - ai_re_architected_incumbent
  - enterprise_ai_adoption
  - agent_framework_landscape
  challenged_by:
  - Enterprise customers publicly disclose migrating application optimization workloads
    from Anthropic/Claude to Azure OpenAI in earnings commentary or disclosed customer
    case studies
  confirmed_by:
  - Anthropic press releases or enterprise customer announcements disclose new application
    optimization wins in segments where Azure OpenAI was the prior deployment
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: msft_ai_tooling_below_peer_quality
  statement: At scoring, MSFT's AI developer tooling quality was below that of primary
    peers.
  derived_from: 'competitive_advantage.innovation_rate: 4 — ''AI tooling still subpar
    relative to peers'''
  themes:
  - ai_infrastructure_software
  - agent_framework_landscape
  challenged_by:
  - A third-party developer survey (e.g., Stack Overflow Annual Developer Survey)
    or independent benchmark published after the scoring date ranks MSFT or GitHub
    Copilot at or above the peer median for AI tooling quality
  confirmed_by:
  - A third-party developer survey or independent benchmark published after the scoring
    date continues to rank MSFT AI tooling below primary peers (e.g., Google, Anthropic,
    AWS)
  status: open
  status_source: draft
  pressure:
    confirm: 0.5
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
  draft: true
- id: enterprise_distribution_moat_intact
  statement: At scoring, MSFT's enterprise distribution moat was overwhelming and
    had not been materially eroded by AI-era competitive entry.
  derived_from: 'competitive_advantage.distribution: 5 — ''Distribution moat through
    enterprise remains overwhelming'''
  themes:
  - enterprise_ai_adoption
  - ai_re_architected_incumbent
  challenged_by:
  - MSFT quarterly earnings filing shows material deceleration in Azure commercial
    bookings or Microsoft 365 enterprise seat count relative to prior-period growth
    rates
  confirmed_by:
  - MSFT quarterly earnings filing shows commercial cloud bookings and enterprise
    seat counts consistent with prior-period growth rates across reported segments
  status: open
  status_source: draft
  pressure:
    confirm: 1.5
    challenge: 0.5
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
- id: investor_momentum_factors_weakening
  statement: At scoring, momentum factors for MSFT were weakening relative to mega-cap
    tech peers, and investor enthusiasm around AI model differentiation had cooled.
  derived_from: 'potential_investor_interest.score: 3 — ''momentum factors weakening''
    and ''Investor enthusiasm cooled. Once-dominant AI narrative has shifted to question
    marks about model differentiation, partnership dependence, and tooling quality'''
  themes:
  - ai_re_architected_incumbent
  - enterprise_ai_adoption
  challenged_by:
  - Published factor model data or ETF flow reports show MSFT 3- or 6-month relative
    price momentum turning positive vs. S&P 500 mega-cap tech peers
  confirmed_by:
  - Published factor model data or ETF flow reports show continued negative momentum
    signal for MSFT vs. mega-cap tech peers at the next scheduled portfolio review
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
| SALES | 4Q26 | 87250.0 | 87565.42082054439 | None | None | None | None |
| EPS | 3Q26 | None | None | 4.27 | 4.062460836254545 | None | None |
| INC_GROSS | 3Q26 | None | None | 56059.294117647056 | 54670.71573333333 | None | None |
| SALES | 3Q26 | 81200.0 | 81228.4526214607 | 82886.0 | 81444.3729775506 | above | 0.020763546798029556 |
| INC_GROSS | 2Q26 | None | None | 55295.3125 | 53851.26091935484 | None | None |
| EPS | 2Q26 | None | None | 4.14 | 3.9028659712027776 | None | None |
| SALES | 2Q26 | None | None | 81273.0 | 80308.7016858399 | None | None |
| INC_GROSS | 1Q26 | None | None | 53595.06060606061 | 50970.33793103448 | None | None |
| EPS | 1Q26 | None | None | 4.13 | 3.6733179081114287 | None | None |
| SALES | 1Q26 | None | None | 77673.0 | 75494.67845185808 | None | None |
| SALES | 4Q25 | None | None | 76441.0 | 73961.12957279138 | None | None |
| INC_GROSS | 4Q25 | None | None | 52426.22580645161 | 50183.73269354839 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "MSFT", "date_range": ["2020-06-30", "2026-03-31"], "consistency": 0.976221517186322, "sandbag_index": -0.0027413286388144257, "guide_hit_rate": 0.8888888888888888, "n_guided_periods": 9, "consensus_beat_rate": 0.92, "n_consensus_periods": 25, "avg_beat_vs_guidance": 0.03343455832912764, "avg_beat_vs_consensus": 0.022687909095706494, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.8888888888888888}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "MSFT", "date_range": ["2022-06-30", "2022-06-30"], "consistency": null, "sandbag_index": -0.000686343826434687, "guide_hit_rate": 0.0, "n_guided_periods": 1, "consensus_beat_rate": 0.92, "n_consensus_periods": 25, "avg_beat_vs_guidance": -0.008783216783216783, "avg_beat_vs_consensus": 0.0316335391267831, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.0}
- EPS: {"metric": "EPS", "ticker": "MSFT", "date_range": ["2022-06-30", "2022-06-30"], "consistency": null, "sandbag_index": -0.002572419126937602, "guide_hit_rate": 0.0, "n_guided_periods": 1, "consensus_beat_rate": 0.96, "n_consensus_periods": 25, "avg_beat_vs_guidance": -0.02192982456140343, "avg_beat_vs_consensus": 0.07530383321517471, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.0}
