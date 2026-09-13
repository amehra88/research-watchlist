# Context for AAPL (generated 2026-09-13T20:14:36+00:00)

## Open thesis assumptions (from notes/AAPL/_thesis.md)
```yaml
doc_type: thesis
ticker: AAPL
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AAPL
reviewed_by_operator: false
scores:
  ai_positioning: '3'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: aapl_ai_laggard_at_scoring
  statement: At scoring, Apple had not shipped a frontier model and the Siri overhaul
    had slipped, leaving advanced AI capability dependent on OpenAI/Google partnerships.
  derived_from: 'ai_positioning: 3 — ''relative AI laggard among mega-caps: Apple
    Intelligence underwhelmed and the Siri overhaul slipped, no frontier model, leaning
    on partners (OpenAI/Google) for advanced AI'''
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - Apple files or ships a proprietary frontier-class model without partner routing
    for advanced queries
  - Siri overhaul ships on an announced schedule with Apple disclosing no OpenAI/Google
    dependency for advanced queries
  confirmed_by:
  - Apple confirms in an earnings call or regulatory filing that advanced AI queries
    continue to route to OpenAI or Google
  - A subsequent product cycle concludes without Apple announcing a proprietary frontier
    model
  status: open
  status_source: draft
  pressure:
    confirm: 2.5
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-12'
  draft: true
- id: aapl_active_device_2b_at_scoring
  statement: Active installed base at scoring stood at or above 2 billion devices
    — the figure the PM cited as the basis for a distribution score of 5.
  derived_from: 'competitive_advantage.distribution: 5 — ''2B+ active devices and
    unmatched ecosystem lock-in — AI reaches the installed base instantly once it
    ships'''
  themes:
  - ai_re_architected_incumbent
  - handset_competition
  challenged_by:
  - Apple discloses an active device count materially below 2 billion in a filing
    or earnings disclosure
  confirmed_by:
  - Apple confirms active device count at or above 2 billion in a filing or earnings
    disclosure
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: aapl_silicon_ondevice_optionality
  statement: Apple Silicon and Neural Engine architecture, as of scoring, were technically
    capable of running on-device inference — the basis for the optionality the PM
    ascribed in the AI positioning note.
  derived_from: 'ai_positioning: 3 — ''custom Apple Silicon / Neural Engine give on-device-inference
    optionality'''
  themes:
  - silicon_architecture_competition
  - ai_re_architected_incumbent
  challenged_by:
  - Apple Intelligence technical disclosures confirm the majority of inference is
    cloud-routed rather than on-device
  - A published third-party benchmark shows Apple Silicon on-device inference materially
    outpaced by a competing mobile SoC
  confirmed_by:
  - Apple Intelligence technical documentation confirms on-device inference via Neural
    Engine for a material portion of shipped features
  status: open
  status_source: draft
  pressure:
    confirm: 2.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-13'
  draft: true
- id: aapl_distribution_buffers_ai_lag
  statement: The distribution advantage — not AI innovation execution — is the factor
    the PM credited for lifting overall competitive advantage to 4 rather than lower;
    that advantage rests on the 2B+ device count at scoring.
  derived_from: 'competitive_advantage.overall: 4 — ''the distribution moat buffers
    the AI-innovation lag; caps below 5 until AI execution delivers'''
  themes:
  - ai_re_architected_incumbent
  - handset_competition
  challenged_by:
  - Apple reports a material decline in active device count in a subsequent filing,
    reducing the distribution base underpinning the buffer claim
  - A competitor discloses ecosystem metrics (e.g., switching rates, services attach
    rates) comparable to Apple's in a filing
  confirmed_by:
  - Apple's disclosed active device count is at or above the 2B figure cited at scoring
    in a subsequent filing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: aapl_china_iphone_cap_inv_int
  statement: China revenue exposure and decelerating iPhone unit growth were, at scoring,
    the factors the PM identified as capping potential investor interest below 5.
  derived_from: 'potential_investor_interest: 4 — ''AI-laggard narrative, China exposure,
    and decelerating iPhone growth cap upside. Factors: … AI-skepticism/China cap'''
  themes:
  - china_us_tensions
  - handset_competition
  challenged_by:
  - Apple reports iPhone unit growth accelerating on a YoY basis in a quarterly earnings
    filing
  - Apple reports China segment revenue growing materially YoY in a quarterly earnings
    filing
  confirmed_by:
  - Apple reports iPhone unit growth flat or negative YoY in a subsequent quarterly
    earnings filing
  - Apple reports China segment revenue declining YoY in a subsequent quarterly earnings
    filing
  status: open
  status_source: draft
  pressure:
    confirm: 0.5
    challenge: 3.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
- id: aapl_fcf_buyback_inv_int_support
  statement: FCF generation magnitude and buyback activity were, at scoring, the primary
    factors the PM cited as supporting the investor interest score of 4.
  derived_from: 'potential_investor_interest: 4 — ''Mega-cap quality, enormous FCF,
    massive buybacks, and index-anchor weight support the score'''
  themes:
  - platform_take_rate
  challenged_by:
  - Apple announces a material reduction in buyback authorization in an SEC filing
  - Apple reports a material YoY decline in free cash flow in a quarterly filing
  confirmed_by:
  - Apple maintains or increases buyback authorization in a subsequent SEC filing
  - Apple reports FCF at or above the prior-year comparable period in a quarterly
    filing
  status: open
  status_source: draft
  pressure:
    confirm: 1.0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: true
```

## Guidance track record (Store B, last 12 rows)
| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |
|---|---|---|---|---|---|---|---|
| SALES | 3Q26 | 108611.58 | 102805.53084393247 | 109417.0 | 109038.89987367907 | in_range | 0.007415599699405885 |
| EPS | 3Q26 | None | None | 2.02 | 1.891882633240625 | None | None |
| INC_GROSS | 3Q26 | None | None | 54770.0 | 52432.361391304345 | None | None |
| INC_GROSS | 2Q26 | 52962.36 | 49678.60442857143 | 54781.0 | 52896.65558333333 | above | 0.034338348970854006 |
| EPS | 2Q26 | None | None | 2.01 | 1.945765692634375 | None | None |
| SALES | 2Q26 | 109186.055 | 104931.55648591158 | 111184.0 | 109457.58884375855 | above | 0.018298536383606928 |
| EPS | 1Q26 | None | None | 2.84 | 2.6733241526387097 | None | None |
| SALES | 1Q26 | 137973.0 | 131817.30208938278 | 143756.0 | 138391.0075885116 | above | 0.041913997666210054 |
| INC_GROSS | 1Q26 | 65543.39 | 62109.73675 | 69231.0 | 65648.19831818182 | above | 0.056262118880332564 |
| SALES | 4Q25 | None | None | 102466.0 | 102227.07455970187 | None | None |
| INC_GROSS | 4Q25 | None | None | 48363.952 | 47730.07786956522 | None | None |
| EPS | 4Q25 | None | None | 1.85 | 1.777147104732258 | None | None |

## Credibility scores
- SALES: {"metric": "SALES", "ticker": "AAPL", "date_range": ["2019-12-31", "2026-06-30"], "consistency": 0.944996624828117, "sandbag_index": -0.05882015399162042, "guide_hit_rate": 0.8, "n_guided_periods": 5, "consensus_beat_rate": 0.9285714285714286, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.0028222421344599588, "avg_beat_vs_consensus": 0.030069900529027794, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.8}
- INC_GROSS: {"metric": "INC_GROSS", "ticker": "AAPL", "date_range": ["2019-12-31", "2026-03-31"], "consistency": 0.9316691411502896, "sandbag_index": -0.0743868271705829, "guide_hit_rate": 0.75, "n_guided_periods": 4, "consensus_beat_rate": 0.9285714285714286, "n_consensus_periods": 28, "avg_beat_vs_guidance": 0.010747236497552616, "avg_beat_vs_consensus": 0.045377590513094146, "guides_quantitatively": true, "guide_hit_rate_inrange": 0.75}
- EPS: {"note": "no quantitative guidance issued; consensus-beat fallback only", "metric": "EPS", "ticker": "AAPL", "date_range": null, "consistency": null, "sandbag_index": null, "guide_hit_rate": null, "n_guided_periods": 0, "consensus_beat_rate": 0.9642857142857143, "n_consensus_periods": 28, "avg_beat_vs_guidance": null, "avg_beat_vs_consensus": 0.08161664960098991, "guides_quantitatively": false, "guide_hit_rate_inrange": null}
