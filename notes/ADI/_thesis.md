---
doc_type: thesis
ticker: ADI
tier: tier_2_active_candidates
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#ADI
- notes/ADI/20260521-2Q26.md
- notes/ADI/20260820-3Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: adi_gm_above_prior_ceiling
  statement: The mix and pricing factors that produced ADI's Q4'26 gross margin guidance
    of 74%—above the 73% ceiling management stated one quarter prior—were present
    and intact at the time of the 3Q26 earnings call.
  derived_from: '3Q26 headline read: Confirm — ''guided Q4 to 74% GM and 52% OM —
    through the stated ceiling one quarter later'''
  themes: []
  challenged_by:
  - ADI Q4'26 10-Q reports gross margin below 73%
  - Management revises Q4'26 gross margin guidance downward at any investor event
    before the print
  confirmed_by:
  - ADI Q4'26 10-Q reports gross margin at or above 74% with no one-time benefit cited
  - Q4'26 earnings call attributes margin to mix and pricing without reference to
    inventory repricing or non-recurring items
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: industrial_upcycle_demand_not_restock
  statement: ADI's industrial revenue growth as of the 3Q26 observation reflected
    end-demand and content gains, not distributor channel restocking.
  derived_from: '3Q26 semiconductor_cycle: Confirm — ''end-market consumption well
    below historical levels, implying the restock is not yet the demand'''
  themes: []
  challenged_by:
  - ADI reports a sequential industrial revenue decline in any quarter while distributor
    channel weeks-on-hand rises above 8 weeks
  - A major ADI distributor issues a public destocking or inventory-reduction notice
  confirmed_by:
  - ADI 10-Q for Q4'26 or Q1'27 shows distributor sell-through tracking sell-in with
    channel weeks-on-hand flat or below current levels
  - ADI industrial revenue grows in a quarter where semiconductor peers report broad
    distributor destocking
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: empower_ivr_design_candidate_ai
  statement: Empower Semiconductor's IVR and silicon capacitor technology was positioned
    as an active design candidate in hyperscaler AI accelerator power-delivery programs
    at the time of the 3Q26 call.
  derived_from: '3Q26 ai_infrastructure_capex: Confirm (strengthening) — ''enables
    power delivery into the processor package, quantified as a 10–15% reduction in
    compute power consumption in 1GW data centers'''
  themes: []
  challenged_by:
  - ADI 2027 earnings calls and filings make no reference to Empower-derived revenue
    or design-win progress
  - A hyperscaler publicly qualifies a competing integrated voltage regulator supplier
    for the AI accelerator application Empower targets
  confirmed_by:
  - ADI calls out a discrete Empower revenue contribution in a 2027 earnings call
    or 10-Q segment disclosure
  - A hyperscaler design win citing integrated voltage regulator or silicon capacitor
    technology from the Empower portfolio is disclosed in an ADI press release or
    filing
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: adi_record_inventory_no_demand_break
  statement: Record ADI balance-sheet and channel inventory levels at the time of
    the 3Q26 report were not accompanied by customer demand signals that would require
    a near-term inventory correction.
  derived_from: '3Q26 data_center_deployment_constraints: Drift — ''inventory at record
    levels both on the balance sheet and in channels; lead times extending'''
  themes: []
  challenged_by:
  - ADI takes an inventory write-down or excess-inventory charge in a Q4'26 or Q1'27
    filing
  - ADI management guides revenue below the prior quarter with inventory normalization
    explicitly cited as a driver
  confirmed_by:
  - ADI Q4'26 10-Q shows inventory balances flat or declining QoQ with no write-down
    or excess charge
  - ADI Q1'27 guidance implies sequential revenue growth with channel weeks-on-hand
    reported at or below the Q3'26 level
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: auto_share_gains_cross_powertrain
  statement: ADI's automotive outperformance at 3Q26 reflected content and share gains
    across both combustion and electric platforms, not concentration in EV BMS alone.
  derived_from: '3Q26 automotive_semiconductor_demand: Confirm — ''above-market growth
    to content and share gains in both combustion and electric vehicles, plus next-gen
    infotainment and electric powertrains'''
  themes: []
  challenged_by:
  - ADI automotive revenue declines sequentially in a quarter where total SAAR is
    flat-to-up and EV unit sales are down
  - ADI loses a named ADAS or GMSL platform award disclosed in a competitor press
    release or OEM design-win announcement
  confirmed_by:
  - ADI automotive revenue grows in a quarter where publicly reported EV unit volumes
    declined year-over-year
  - ADI discloses a new ADAS or infotainment design win on an ICE or hybrid platform
    in a filing, press release, or earnings call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: maxim_synergy_1b_2027_trajectory
  statement: The Maxim integration was on a trajectory consistent with >$1B in annual
    cost synergies by 2027, as explicitly stated at the 3Q26 call.
  derived_from: 3Q26 forward guidance — 'Maxim synergies $700M in 2026 rising to >$1B
    in 2027'
  themes: []
  challenged_by:
  - ADI announces incremental restructuring charges attributed to Maxim integration
    in any 2026 or 2027 filing
  - ADI management revises the >$1B synergy target downward in any public earnings
    call or investor-day presentation
  confirmed_by:
  - ADI FY2027 annual report or earnings call cites >$1B in Maxim synergies realized
  - ADI FY2027 operating margin exceeds FY2026 by a magnitude consistent with $300M+
    in incremental synergy flow-through
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

Drafted 2026-09-09 in mode `notes` from the sources in `drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.
