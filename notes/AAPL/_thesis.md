---
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
    confirm: 0.5
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-09'
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
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
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
    confirm: 0
    challenge: 1.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: true
---
## Rationale

Drafted 2026-09-09 in mode `scores` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
