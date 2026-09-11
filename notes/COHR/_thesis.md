---
doc_type: thesis
ticker: COHR
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: imported
thin_inputs: false
drafted_from:
- config/watchlist.yaml#COHR
- notes/COHR/20260813-4Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '4'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: vertical_integration_moat
  statement: COHR is vertically integrated from in-house indium-phosphide lasers through
    to transceivers, and that integration is why innovation scores 4.
  derived_from: '`competitive_advantage.innovation_rate: 4` — *"vertically integrated
    optics (indium-phosphide lasers -> transceivers), datacom transceiver ramp"*.'
  themes: []
  challenged_by:
  - a competitor demonstrating in-house InP/EML chip capability at comparable volume
  - merchant laser supply becoming abundant enough that integration stops mattering
  - Accelink or similar shipping integrated chip-to-module at 800G+
  confirmed_by:
  - competitors publicly constrained by third-party laser supply
  - COHR gross margin holding while merchant module prices fall
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: supply_was_tight_at_scoring
  statement: Datacom transceiver supply was tight as at 2026-06-02, and the distribution
    score of 4 was set under those conditions. The assumption is that those conditions
    still hold — not that tightness is a durable property of the market.
  derived_from: '`competitive_advantage.distribution: 4` — *"broad datacom customer
    base across hyperscalers **amid** transceiver supply tightness"*.'
  themes: []
  challenged_by:
  - capacity additions at 800G/1.6T from Innolight/Eoptolink
  - a large capital raise funding competitor capacity
  - transceiver ASP declines
  - hyperscalers publicly dual-sourcing on price
  confirmed_by:
  - continued lead-time extension
  - customers pre-paying or committing capacity
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 23.0
    window_days: 90
    last_evidence: '2026-09-11'
  draft: false
- id: datacom_ramp_continues
  statement: The 800G→1.6T datacenter ramp continues to pull COHR volume.
  derived_from: '`ai_positioning: 4` — *"AI-datacenter optical transceivers (800G/1.6T)
    ... Direct AI-optics beneficiary on the datacenter buildout"*.'
  themes: []
  challenged_by:
  - hyperscaler capex digestion
  - a shift to co-packaged optics that bypasses pluggable transceivers
  - slower 1.6T adoption than planned
  confirmed_by:
  - hyperscaler capex guides up
  - 1.6T design wins
  status: open
  status_source: operator
  pressure:
    confirm: 8.0
    challenge: 0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: false
- id: customer_concentration_not_worsening
  statement: Datacom customer concentration exists and is already reflected in the
    distribution score of 4; the assumption is that it does not deteriorate from there.
  derived_from: '`competitive_advantage.distribution: 4` — *"some customer concentration
    in datacom"*.'
  themes: []
  challenged_by:
  - a top customer qualifying a second source
  - concentration rising
  - a named customer moving volume to a Chinese supplier
  confirmed_by: []
  status: open
  status_source: operator
  pressure:
    confirm: 2.0
    challenge: 5.0
    window_days: 90
    last_evidence: '2026-09-10'
  draft: false
- id: leverage_is_a_watch_item
  statement: Post-II-VI/Finisar balance-sheet leverage is a monitored risk, explicitly
    flagged as a watch-item within an investor-interest score of 4. The assumption
    is that it does not worsen — NOT that deleveraging is progressing.
  derived_from: '`potential_investor_interest: 4` — *"turnaround/deleveraging story
    ... Post-II-VI/Finisar balance-sheet leverage is a **watch-item**"*.'
  themes: []
  challenged_by:
  - leverage flat or rising
  - refinancing at worse terms
  - FCF miss
  confirmed_by: []
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: chinese_laser_capability
  statement: Chinese optical vendors cannot yet manufacture high-quality lasers (InP/EML)
    at high yield, and that manufacturing gap — not policy — is what limits their
    share gain against COHR and LITE.
  derived_from: operator, 2026-08-21 — *"The real thing we should continue to monitor
    is whether the chinese companies can garner more marketshare and manufacture high
    quality lasers with high yields and high quality. that's the real concern."*
  themes: []
  challenged_by:
  - a Chinese vendor disclosing in-house laser/EML chip production at scale
  - published or implied yield improvement
  - a Chinese module maker shifting from imported to domestic laser chips
  - hyperscaler qualification of a Chinese-laser-based module
  - share gain at 800G/1.6T sustained with margin (price-cutting alone is not capability)
  confirmed_by:
  - continued external chip sourcing by Chinese module makers
  - yield or quality problems disclosed
  - Chinese vendors competing on assembly/price rather than component tech
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: policy_shelter
  statement: Policy shelter is a watch item, not an assumption (operator 2026-08-21).
  derived_from: operator
  themes: []
  challenged_by:
  - an optical-specific restriction is actually proposed (Section 889 / FCC Covered
    List / ICTS reaching transceivers)
  - a hyperscaler states a non-China sourcing requirement
  confirmed_by: []
  status: retired
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
---
## Rationale

Drafted 2026-09-09 in mode `imported` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
