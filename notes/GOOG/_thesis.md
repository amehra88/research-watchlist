---
doc_type: thesis
ticker: GOOG
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: scores
thin_inputs: false
drafted_from:
- config/watchlist.yaml#GOOG
reviewed_by_operator: false
scores:
  ai_positioning: '5'
  competitive_advantage.innovation_rate: '5'
  competitive_advantage.distribution: '5'
  competitive_advantage.overall: 4+
  potential_investor_interest.score: '5'
proposed_scores: {}
assumptions:
- id: gemini_quality_improving_at_scoring
  statement: At the time of scoring, Gemini model quality metrics showed improvement
    versus prior-period third-party benchmark measurements.
  derived_from: 'potential_investor_interest.score: 5 — "Gemini quality climbing"'
  themes:
  - ai_agent_monetization
  - agent_framework_landscape
  challenged_by:
  - A published third-party benchmark (e.g., LMSYS Chatbot Arena, Artificial Analysis
    frontier index) showing Gemini's composite rank declining quarter-over-quarter
    at the time of scoring
  - A model evaluation suite publication placing Gemini below its prior-period ranking
    on reasoning or coding tasks
  confirmed_by:
  - A third-party benchmark publication dated within the scoring window showing Gemini
    ranked at or above its prior-period position on at least two major evaluation
    suites
  - Google disclosing Gemini API usage growth in a quarterly filing or earnings call
    consistent with developer adoption of an improving model
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: search_ad_model_at_risk
  statement: At the time of scoring, the Search advertising revenue model faced a
    material, not merely theoretical, risk of displacement from agentic search query
    behavior.
  derived_from: 'competitive_advantage.overall: 4+ — "Search ad model is genuinely
    at risk from agentic search — the company is the most AI-capable AND the most
    AI-exposed simultaneously"'
  themes:
  - search_disruption
  - ad_market_strength
  - agentic_commerce
  challenged_by:
  - Google management disclosing AI Overviews monetization per query at parity with
    or above standard organic Search query ad revenue in an earnings call or investor
    filing
  - Third-party ad-tech data showing Search click-through rates and CPCs unchanged
    or rising in periods of elevated AI Overviews usage
  confirmed_by:
  - A quarterly earnings disclosure showing a sequential or year-over-year deceleration
    in Search advertising revenue not attributable to macro ad-market softness
  - A disclosed metric showing AI Overviews or zero-click query share increasing as
    a percentage of total Google Search queries
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: goog_ai_stack_best_in_class
  statement: At the time of scoring, GOOG's integrated AI capability stack — Gemini
    models, DeepMind research output, and proprietary TPU silicon — ranked above all
    hyperscaler peers on a combined basis.
  derived_from: 'ai_positioning: 5 — "Native AI capability (Gemini, DeepMind, TPUs)
    is best-in-class"'
  themes:
  - silicon_architecture_competition
  - agent_framework_landscape
  - hyperscaler_capex_buildout
  challenged_by:
  - A major independent AI evaluation (e.g., HELM, government model assessment, MLPerf)
    ranking a competitor's integrated model-plus-silicon stack above GOOG's at the
    scoring date
  - A hyperscaler peer announcing a proprietary AI accelerator achieving higher throughput-per-dollar
    than TPU v5/v6 in a verifiable third-party benchmark
  confirmed_by:
  - Gemini retaining a top-two ranking on a frontier model evaluation leaderboard
    at the scoring date alongside a disclosed TPU design win in Cloud AI workloads
  - DeepMind publishing a peer-reviewed result establishing a new state-of-the-art
    in a domain where competitors had no equivalent published work at scoring
  status: confirmed
  status_source: evidence
  pressure:
    confirm: 10.5
    challenge: 0.5
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: search_defense_not_breached
  statement: At the time of scoring, Google Search had not experienced a revenue or
    query-share loss beyond the level embedded in prior-period analyst consensus estimates.
  derived_from: 'potential_investor_interest.score: 5 — "search defense holding better
    than feared"'
  themes:
  - search_disruption
  - ad_market_strength
  challenged_by:
  - A quarterly earnings filing showing Google Search revenue below the analyst consensus
    estimate prevailing at the time of scoring
  - A third-party data provider (e.g., StatCounter, SimilarWeb, Comscore) publishing
    a query-share dataset showing Google losing material share to an AI-native search
    product in the scoring period
  confirmed_by:
  - Search segment revenue in the earnings filing covering the scoring period meeting
    or exceeding the analyst consensus estimate prevailing at scoring
  - Management citing Search query volume growth or advertiser spend growth in an
    earnings call covering the scoring period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: distribution_five_score_basis
  statement: At the time of scoring, no single competitor matched GOOG's simultaneous
    distribution reach across Search, Android, Workspace, and Cloud, which was the
    factual basis for a distribution score of 5.
  derived_from: 'competitive_advantage.distribution: 5 — "Distribution via Search,
    Android, Workspace, Cloud is enormous"'
  themes:
  - ad_market_strength
  - hyperscaler_capex_buildout
  - agentic_commerce
  challenged_by:
  - A competitor publishing verified metrics showing equivalent or greater reach across
    two or more of the four named distribution channels (Search, Android, Workspace,
    Cloud) at the scoring date
  - A regulatory or antitrust filing disclosing a court-ordered structural separation
    of one of the four distribution assets
  confirmed_by:
  - GOOG's annual filing or earnings disclosures covering the scoring period showing
    active user or revenue figures across Search, Android, Workspace, and Cloud with
    no disclosed peer matching scale in more than one channel
  - A third-party market-share report placing GOOG first in at least three of the
    four distribution channels at the scoring date
  status: open
  status_source: draft
  pressure:
    confirm: 3.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-08'
  draft: true
- id: ai_capable_and_ai_exposed
  statement: At the time of scoring, GOOG's AI capability lead and its core-revenue
    exposure to AI-driven Search disruption were both highest among large-cap peers
    — neither the capability nor the exposure claim was disputed by public data.
  derived_from: 'competitive_advantage.overall: 4+ — "the company is the most AI-capable
    AND the most AI-exposed simultaneously"'
  themes:
  - search_disruption
  - ai_agent_monetization
  - agent_framework_landscape
  challenged_by:
  - A third-party analysis published at or before the scoring date ranking a competitor's
    AI model suite above Gemini and attributing higher Search-equivalent revenue concentration
    to that competitor
  - Google disclosing a diversified revenue mix in which Search advertising fell below
    50% of total revenue, reducing the AI-exposure characterization in the PM's notes
  confirmed_by:
  - Google's 10-Q or 10-K covering the scoring period disclosing Search advertising
    revenue above 55% of total revenue, consistent with the 'most AI-exposed' characterization
  - A frontier model ranking placing Gemini first or tied-first at the scoring date,
    consistent with the 'most AI-capable' characterization
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
