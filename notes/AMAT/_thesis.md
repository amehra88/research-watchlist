---
doc_type: thesis
ticker: AMAT
tier: tier_1_bctk
drafted: '2026-09-09'
draft_mode: notes
thin_inputs: false
drafted_from:
- config/watchlist.yaml#AMAT
- notes/AMAT/20260515-2Q26.md
reviewed_by_operator: false
scores: {}
proposed_scores: {}
assumptions:
- id: foundry_eight_qtr_forecast_basis
  statement: At the time of scoring, TSMC, Samsung, and Intel Foundry customer commitments
    took the form of eight-quarter rolling forecasts — not exploratory indications
    — and those forecasts were the stated basis for AMAT's supply-chain capacity expansion
    decisions.
  derived_from: 'foundry_capacity: Confirm — ''rolling eight-quarter customer forecasts
    cited as the source of confidence; planning for sustained elevated run-rate, not
    a peak'''
  themes:
  - foundry_capacity
  challenged_by:
  - TSMC, Samsung, or Intel Foundry quarterly filing or earnings call that revises
    2026–2027 capex guidance downward or discloses shortened equipment-commitment
    horizons
  - AMAT 10-Q or press release referencing customer booking deferrals or order cancellations
    attributed to foundry customers
  confirmed_by:
  - TSMC, Samsung, or Intel Foundry quarterly filing reaffirms or raises 2026–2027
    node-buildout capex at or above levels implied by the eight-quarter forecast language
  - AMAT FQ3'26 prepared remarks reiterate eight-quarter customer visibility as an
    active input to supply-chain planning
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: wfe_30pct_two_year_guide
  statement: At scoring, AMAT had publicly guided WFE market growth at 'more than
    30%' for FY2026 and explicitly characterized FY2027 as having a similar growth
    profile — a two-year forward commitment the company had not previously made at
    this stage of a cycle.
  derived_from: 'semiconductor_cycle: Drift (positive) — ''Semi equipment business
    raised to more than 30% growth for 2026, with similar trajectory expected in 2027;
    management is investing capex into the view'''
  themes:
  - semiconductor_cycle
  challenged_by:
  - AMAT removes or qualifies the FY2027 growth-profile language in a subsequent quarterly
    filing or press release
  - AMAT revises the FY2026 WFE growth characterization below 30% in a subsequent
    earnings release
  confirmed_by:
  - AMAT FQ3'26 or FQ4'26 earnings release reiterates WFE growth at 30%+ for FY2026
    and preserves the similar-trajectory language for FY2027
  - A SEMI or Gartner industry WFE forecast published after the scoring date reports
    2026 industry growth ≥30%
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: hbm_expansion_drives_dram_wfe
  statement: At scoring, AMAT's DRAM revenue growth of +18% YoY and the advanced packaging
    revenue trajectory (+50% FY2026 guided) were attributed to HBM capacity expansion
    at leading DRAM makers, and those were the conditions as of the note date.
  derived_from: 'hbm_competitive_landscape: Confirm — ''leading-edge DRAM as one of
    the segments expected to drive over 80% of YoY WFE spending growth in 2026 and
    2027''; ''HBM demand is flowing through to DRAM WFE and advanced packaging tools'''
  themes:
  - hbm_competitive_landscape
  challenged_by:
  - SK Hynix, Samsung, or Micron quarterly filing or earnings call disclosing a reduction
    in HBM capacity investment or a delay in HBM3E/HBM4 production ramp
  - AMAT FQ3'26 filing reports DRAM segment revenue declining QoQ with management
    attributing the shortfall to DRAM customer demand
  confirmed_by:
  - SK Hynix, Samsung, or Micron quarterly filing discloses incremental HBM capacity
    addition and associated tool purchase commitments
  - AMAT FQ3'26 filing reports DRAM segment revenue growth at or above the FQ2'26
    YoY rate
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: china_no_incremental_restriction
  statement: At scoring, China represented approximately 24% of AMAT Semi Systems
    plus AGS revenue, and no export restriction beyond the Huawei-specific measures
    already embedded in FQ3'26 guidance had been announced.
  derived_from: 'china_export_controls: Confirm (no drift) — ''Huawei restrictions
    have been factored into its guidance; China/ICAPS characterized as flat to slightly
    higher in 2026; already factored in'''
  themes:
  - china_export_controls
  challenged_by:
  - BIS publishes a new rule, expands the Entity List, or issues an executive order
    restricting AMAT product categories for China shipment beyond the Huawei-era scope
  - AMAT 10-Q or 8-K discloses a material revenue impact from an export control action
    not present in prior guidance
  confirmed_by:
  - BIS issues a clarification or general license restoring a previously restricted
    AMAT product category for China customers
  - AMAT FQ3'26 10-Q reports China revenue share without disclosing incremental restriction
    impacts beyond those cited in the FQ2'26 call
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: gaa_ramp_drives_non_litho_intensity
  statement: At scoring, the gate-all-around node transition at TSMC and Samsung was
    the primary mechanism cited for the per-wafer tool-spend increase accruing to
    AMAT's deposition, etch, and materials engineering product lines, and that ramp
    was in progress.
  derived_from: 'lithography_roadmap: Confirm — ''transition to gate all-around nodes
    driving Semi Systems growth''; ''GAA node transition is the single largest WFE
    intensity step-up of the decade for non-lithography process steps (deposition,
    etch, materials engineering)'''
  themes:
  - lithography_roadmap
  challenged_by:
  - TSMC or Samsung quarterly filing or earnings call discloses a yield-driven delay
    or volume reduction for N2/A14 GAA production
  - AMAT Semi Systems segment revenue in a subsequent quarterly filing falls short
    of the FQ3'26 guide midpoint with management citing foundry node timing as a factor
  confirmed_by:
  - TSMC or Samsung quarterly filing confirms production-worthy GAA yield and raises
    associated 2026–2027 capex line items
  - AMAT filing or investor event discloses Trillium ALD or precision PECVD tool qualification
    at a named GAA customer
  status: open
  status_source: draft
  pressure:
    confirm: 0
    challenge: 0
    window_days: 90
    last_evidence: null
  draft: true
- id: nand_absent_from_amat_growth_mix
  statement: At scoring, NAND WFE was absent from AMAT's FQ2'26 growth attribution
    in both prepared remarks and Q&A, and the note treated this absence as placing
    NAND outside the 'over 80% of YoY WFE spending growth' segments identified by
    management.
  derived_from: 'nand_demand_cycle: Drift (cautious) — ''NAND was not called out as
    a growth driver in the prepared remarks… leaving NAND implicitly in the other
    ~20% bucket; no analyst pressed on NAND specifically; absence in Q&A is itself
    the signal'''
  themes:
  - nand_demand_cycle
  challenged_by:
  - AMAT management names NAND as a growth contributor in a subsequent quarterly earnings
    call or filing
  - Samsung, Kioxia, or Micron discloses incremental greenfield NAND capacity investment
    in a quarterly filing that includes AMAT tool purchase orders
  confirmed_by:
  - NAND WFE is absent from AMAT's growth segment attribution in the FQ3'26 earnings
    prepared remarks
  - Major NAND producers do not announce incremental greenfield NAND capacity expansions
    in quarterly filings through Q4 2026
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
