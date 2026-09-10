---
doc_type: thesis
ticker: LITE
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: imported
thin_inputs: false
drafted_from:
- config/watchlist.yaml#LITE
- notes/LITE/20260811-4Q26.md
reviewed_by_operator: false
scores:
  ai_positioning: '4'
  competitive_advantage.innovation_rate: '3'
  competitive_advantage.distribution: '4'
  competitive_advantage.overall: '4'
  potential_investor_interest.score: '4'
proposed_scores: {}
assumptions:
- id: eml_laser_supply_position
  statement: LITE is designed into the AI transceiver supply chain as a key indium-phosphide
    / EML laser supplier.
  derived_from: '`ai_positioning: 4` — *"key indium-phosphide laser supplier into
    the transceiver chain"*.'
  themes: []
  challenged_by:
  - transceiver makers qualifying alternative EML sources
  - Chinese laser-chip capability at 800G+
  - 'customers vertically integrating laser supply in-house (note: COHR''s own `vertical_integration_moat`
    is precisely this threat to LITE)'
  confirmed_by:
  - design-win announcements
  - EML capacity sold out
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: component_tier_is_why_innovation_is_3
  statement: LITE sits at the component tier rather than the systems tier, and that
    — not a technology deficiency — is why innovation scores 3 rather than 4. The
    assumption is about the REASON for the score, and that the reason still holds.
  derived_from: '`competitive_advantage.innovation_rate: 3` — *"strong laser/EML technology
    but more component than systems"*.'
  themes: []
  challenged_by:
  - margin compression at the component layer
  - module makers integrating backwards
  - LITE moving up-stack into systems (which would invalidate the rationale rather
    than the score)
  confirmed_by: []
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: datacom_recovery
  statement: The AI datacom cycle recovery is underway and is one of the named positives
    behind an investor-interest score of 4.
  derived_from: '`potential_investor_interest: 4` — *"AI datacom-cycle recovery and
    transceiver/EML demand"*.'
  themes: []
  challenged_by:
  - datacom order pauses
  - recovery stalling before telecom drag abates
  confirmed_by: []
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: telecom_drag_no_worse
  statement: Legacy telecom weakness is ALREADY subtracting from the score — it is
    one of the two named reasons investor interest is capped at 4 rather than 5. The
    assumption is that it does not get worse, not that it is held at bay.
  derived_from: '`potential_investor_interest: 4` — *"legacy-telecom-segment weakness
    and customer concentration temper"*.'
  themes: []
  challenged_by:
  - telecom declining faster than datacom grows
  - segment write-downs
  confirmed_by: []
  status: open
  status_source: operator
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: false
- id: cloud_light_is_an_upgrade_condition
  statement: Cloud Light integration is one of the two conditions that would take
    LITE's innovation score from 3 to 3+. It is a potential upside trigger, NOT an
    established fact.
  derived_from: '`competitive_advantage.innovation_rate: 3` — *"**3+** on the AI datacom
    ramp and Cloud Light integration"*.'
  themes: []
  challenged_by:
  - integration problems
  - Cloud Light customer losses
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
  statement: 'Shared with COHR: Chinese vendors have not yet closed the high-end laser
    gap (see COHR).'
  derived_from: operator
  themes: []
  challenged_by:
  - operator to specify
  confirmed_by: []
  status: open
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
