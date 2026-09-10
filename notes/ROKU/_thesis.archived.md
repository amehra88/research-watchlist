---
doc_type: thesis
ticker: ROKU
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: thin
thin_inputs: true
drafted_from:
- config/watchlist.yaml#ROKU
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: roku_ctv_ad_tailwind_at_scoring
  statement: The CTV digital advertising market was in a growth phase at the time
    of scoring, providing an industry-level tailwind to ROKU's Advertising segment
    independent of company-specific share gains.
  derived_from: 'theme: ad_market_strength — theme tag assigned by PM'
  themes:
  - ad_market_strength
  challenged_by:
  - IAB or Magna quarterly CTV ad spend report showing YoY deceleration concurrent
    with the scoring period
  - ROKU Advertising segment revenue growing materially below the rate implied by
    overall CTV ad market growth in the next 10-Q
  confirmed_by:
  - IAB quarterly report confirming double-digit CTV ad spend growth concurrent with
    the scoring period
  - ROKU next 10-Q disclosing Advertising segment revenue acceleration consistent
    with an industry-level tailwind rather than purely company-specific drivers
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: roku_os_incumbent_not_eroding
  statement: ROKU's streaming OS incumbent position — as measured by streaming hours
    and active accounts — was not losing share to competing CTV platforms at the time
    of scoring.
  derived_from: 'theme: ai_re_architected_incumbent — ''incumbent'' label presupposes
    the installed-base position is intact at the time of the theme assignment'
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - A competing CTV OS (Google TV, Amazon Fire TV, Samsung Tizen) disclosing streaming
    hour or active account growth materially exceeding ROKU's in the same period
  - ROKU next 10-Q disclosing active account or streaming hour growth decelerating
    to a rate below the prior four-quarter average
  confirmed_by:
  - ROKU next 10-Q streaming hours and active account figures consistent with or above
    the prior-period growth trajectory
  - Third-party smart TV OS market share data (e.g., Parks Associates) showing ROKU
    holding or gaining OS share in the scoring period
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: roku_ai_arch_changes_deployed
  statement: At the time of scoring, ROKU had deployed AI-driven changes to its platform
    architecture — in ad targeting, content discovery, or UI — sufficient to constitute
    a structural capability shift rather than incremental feature updates.
  derived_from: 'theme: ai_re_architected_incumbent — ''re-architected'' label implies
    structural changes already deployed, not a forward roadmap item'
  themes:
  - ai_re_architected_incumbent
  challenged_by:
  - ROKU 10-Q or earnings call transcript containing no disclosure of AI-specific
    infrastructure investment or named AI-driven product feature above the prior product
    roadmap
  - ROKU engineering or product release documentation showing AI features classified
    as beta or limited rollout as of the scoring date
  confirmed_by:
  - ROKU 10-Q or earnings call transcript disclosing a named AI-driven capability
    (e.g., ML-based ad auction, AI content recommendations) with confirmed active
    deployment as of the scoring period
  - ROKU SEC filing or press release announcing a signed partnership with an AI infrastructure
    provider tied to platform monetization, with a go-live date on or before the scoring
    date
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

Drafted 2026-09-09 in mode `thin` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
