## Theme diffusion — 2026-09-10

Current quarter **CY2026-Q3** (in progress — counts are partial); prior CY2026-Q2. Quarters covered: CY2025-Q4, CY2026-Q1, CY2026-Q2, CY2026-Q3.

### Coverage (read first)
| quarter | earnings_call companies | conference companies | MD&A filers |
|---|---|---|---|
| CY2025-Q4 | 7 | 16 | 8 |
| CY2026-Q1 | 41 | 22 | 61 |
| CY2026-Q2 | 43 | 23 | 69 |
| CY2026-Q3 | 45 | 29 | 67 |

No transcript coverage — no results: ADI, AWS, BABA, BIDU, DE, DPC, GH, HSAI, INIO, NTES, PLAB, RDNT, SE, SEI, TSEM, TTWO; incomplete/unknown: A000660, MU, NET, PLTR, POET, PWR, RKLB, SHOP, SNPS, SPCX, TSLA, TXN, WELL, accelink.cn, eoptolink.cn, hgtech.cn, innolight.cn, kaori.tw, mtar.in; unmappable: base_power.us, hisense_broadband.cn, source_photonics.cn. FactSet retrieval is topically scoped (theme-derived queries), not whole-call export.

- challenging_rate (spec §5) is not computed: exchange rows carry no challenging flag and 99% of analyst turns are sentiment=Neutral.
- P3 foreign evidence is not built: stages and lags use US MD&A evidence only; Chinese filers appear only in the exclusions list. Corprep transcript speech is reported as a count (n_corprep_companies) but does not set a stage: at its 0.30 threshold it mis-paired 3 of 5 spot-checked stage-2 rows.
- MD&A counts need >= 2 mapped blocks per filer-quarter and are lower-confidence than transcript counts (mdna precision ~0.4 at its threshold).
- The Tier-0 lag runs from MD&A filing dates only (corprep answers share the question's date). Both windows are truncated — questions 2025-11-11..2026-09-09, filings 2025-12-10..2026-09-10 — so a question dated before the first filing in the window can only look question-first (left-censoring); negative lags near the window start are not evidence against the premise.
- No trend lines by design: three or four observations per theme support a comparison, not a slope.

### Movers — CY2026-Q3 vs CY2026-Q2 (n_banks first, then n_companies; host banks excluded at their own conferences)
| theme | banks | prev | Δ | companies asked | prev | disclosing (MD&A) | prev |
|---|---|---|---|---|---|---|---|
| enterprise_ai_adoption | 14 | 7 | +7 | 12 | 6 | 0 | 0 |
| local_commerce_delivery | 10 | 4 | +6 | 2 | 1 | 2 | 3 |
| cybersecurity_competitive_landscape | 12 | 7 | +5 | 9 | 3 | 2 | 2 |
| software_seat_pricing_pressure | 5 | 1 | +4 | 5 | 1 | 26 | 30 |
| capex_vs_opex_shift | 7 | 3 | +4 | 5 | 3 | 20 | 33 |
| platform_take_rate | 4 | 1 | +3 | 3 | 1 | 6 | 10 |
| automotive_semiconductor_demand | 3 | 1 | +2 | 5 | 2 | 11 | 12 |
| frontier_model_competition | 2 | 0 | +2 | 4 | 2 | 0 | 0 |
| data_center_deployment_constraints | 20 | 18 | +2 | 11 | 12 | 3 | 0 |
| ai_compute_topology | 6 | 4 | +2 | 5 | 8 | 0 | 0 |
| hbm_competitive_landscape | 16 | 15 | +1 | 9 | 5 | 0 | 0 |
| ai_re_architected_incumbent | 1 | 0 | +1 | 3 | 0 | 0 | 0 |
| foundation_model_economics | 1 | 0 | +1 | 2 | 1 | 0 | 0 |
| ad_market_strength | 3 | 2 | +1 | 3 | 3 | 5 | 9 |
| ai_native_vertical | 2 | 1 | +1 | 2 | 2 | 0 | 0 |
| defense_drones | 1 | 0 | +1 | 1 | 1 | 0 | 0 |
| model_efficiency_evolution | 2 | 2 | +0 | 8 | 4 | 0 | 0 |
| china_export_controls | 0 | 0 | +0 | 2 | 0 | 2 | 3 |
| model_commoditization | 0 | 0 | +0 | 1 | 0 | 0 | 0 |
| sovereign_ai_deployments | 0 | 0 | +0 | 1 | 0 | 0 | 0 |
| agentic_commerce | 2 | 2 | +0 | 2 | 2 | 0 | 0 |
| ai_generated_content | 0 | 0 | +0 | 1 | 1 | 0 | 0 |
| ai_infrastructure_capex | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| antitrust_action | 0 | 0 | +0 | 0 | 0 | 0 | 1 |
| china_ai_infrastructure_demand | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| china_consumer_demand | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| china_us_tensions | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| demographic_demand_tailwinds | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| fed_policy_tech | 0 | 0 | +0 | 0 | 0 | 1 | 1 |
| foundry_capacity | 0 | 0 | +0 | 0 | 0 | 5 | 3 |
| humanoid_robotics_competition | 0 | 0 | +0 | 1 | 1 | 0 | 0 |
| silicon_architecture_competition | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| space_supply_chain | 0 | 0 | +0 | 0 | 0 | 1 | 1 |
| surveillance_security_tech | 2 | 2 | +0 | 1 | 1 | 1 | 1 |
| ai_infrastructure_software | 4 | 4 | +0 | 4 | 5 | 0 | 0 |
| ai_regulation | 0 | 0 | +0 | 1 | 2 | 0 | 0 |
| nuclear_energy_buildout | 2 | 2 | +0 | 2 | 3 | 0 | 0 |
| nand_demand_cycle | 21 | 22 | -1 | 13 | 8 | 0 | 1 |
| agent_framework_landscape | 1 | 2 | -1 | 5 | 4 | 0 | 0 |
| search_disruption | 1 | 2 | -1 | 2 | 1 | 0 | 0 |

### Lifecycle (spec §6.3) — Tier-0 lag = first analyst question minus first MD&A filing, days
n=53 (theme, company) pairs with both a filing and a question: min -184, p25 -77, median -4, p75 174, max 272; evidence led in 39.6% (31 negative = question came first, 1 same-day). See the censoring note above.
Stage counts (theme, company): stage 1: 13, stage 2: 155, stage 3: 55, stage 4: 372

### Stage 2 — asked at another name, not here (155; verified-adjacent askers first)
| theme | company | adjacent asked (route, first question) | other askers | first evidence | open days | evidence |
|---|---|---|---|---|---|---|
| hyperscaler_revenue_concentration | NVDA | CBRS (manual:competitor, 2026-06-23); MRVL (manual:partnership, 2025-12-02) | AAOI, AMD, ANET, ARM, AVGO, CIEN +11 | 2026-02-25 | 197 | mdna |
| capex_vs_opex_shift | HPQ | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2025-12-10 | 274 | mdna |
| software_seat_pricing_pressure | HPQ | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-10 | 274 | mdna |
| solar_supply_chain | HPQ | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-10 | 274 | mdna |
| capex_vs_opex_shift | AMAT | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2025-12-12 | 272 | mdna |
| software_seat_pricing_pressure | AMAT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-12 | 272 | mdna |
| software_seat_pricing_pressure | CIEN | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-12 | 272 | mdna |
| automotive_semiconductor_demand | AVGO | — | AAPL, AMAT, AMBA, HPE, LRCX, MPWR +1 | 2025-12-18 | 266 | mdna |
| capex_vs_opex_shift | AVGO | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2025-12-18 | 266 | mdna |
| capex_vs_opex_shift | MU | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2025-12-18 | 266 | mdna |
| china_export_controls | AVGO | — | AMAT, ASML, LRCX, NXPI | 2025-12-18 | 266 | mdna |
| nand_demand_cycle | MU | — | 000660.KS, 005930.KS, AAPL, AMAT, AMBA, AMD +13 | 2025-12-18 | 266 | mdna |
| pc_demand | HPE | — | AAPL, HPQ | 2025-12-18 | 266 | mdna |
| semiconductor_cycle | MU | — | 000660.KS, 005930.KS, AAPL, AMAT, AMBA, ARM +15 | 2025-12-18 | 266 | mdna |
| software_seat_pricing_pressure | AVGO | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 266 | mdna |
| software_seat_pricing_pressure | DE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 266 | mdna |
| software_seat_pricing_pressure | HPE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 266 | mdna |
| solar_supply_chain | HPE | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-18 | 266 | mdna |
| capex_vs_opex_shift | SNPS | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2025-12-22 | 262 | mdna |
| china_export_controls | SNPS | — | AMAT, ASML, LRCX, NXPI | 2025-12-22 | 262 | mdna |
| software_seat_pricing_pressure | SNPS | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-22 | 262 | mdna |
| solar_supply_chain | SNPS | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-22 | 262 | mdna |
| pc_demand | INTC | — | AAPL, HPQ | 2026-01-23 | 230 | mdna |
| solar_supply_chain | INTC | — | BE, CRS, FPS, GEV, GLW, MTRN | 2026-01-23 | 230 | mdna |
| software_seat_pricing_pressure | MSFT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-28 | 225 | mdna |
| capex_vs_opex_shift | LRCX | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-01-29 | 224 | mdna |
| capex_vs_opex_shift | NOW | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-01-29 | 224 | mdna |
| platform_take_rate | META | — | AAPL, AMZN, DASH | 2026-01-29 | 224 | mdna |
| software_seat_pricing_pressure | META | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-29 | 224 | mdna |
| software_seat_pricing_pressure | NOW | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-29 | 224 | mdna |
| automotive_semiconductor_demand | FN | — | AAPL, AMAT, AMBA, HPE, LRCX, MPWR +1 | 2026-02-03 | 219 | mdna |
| capex_vs_opex_shift | FN | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-03 | 219 | mdna |
| china_consumer_demand | FN | — | AAPL, AMAT, LRCX | 2026-02-03 | 219 | mdna |
| platform_take_rate | FN | — | AAPL, AMZN, DASH | 2026-02-03 | 219 | mdna |
| aerospace_defense_aftermarket | COHR | — | CRS, GEV, LITE, MRVL, MTRN | 2026-02-04 | 218 | mdna |
| automotive_semiconductor_demand | COHR | — | AAPL, AMAT, AMBA, HPE, LRCX, MPWR +1 | 2026-02-04 | 218 | mdna |
| capex_vs_opex_shift | TTWO | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-04 | 218 | mdna |
| platform_take_rate | TTWO | — | AAPL, AMZN, DASH | 2026-02-04 | 218 | mdna |
| software_seat_pricing_pressure | TTWO | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-04 | 218 | mdna |
| ad_market_strength | GOOGL | — | AAPL, DASH, GOOG, META, RDDT | 2026-02-05 | 217 | mdna |
| software_seat_pricing_pressure | GOOG | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-05 | 217 | mdna |
| software_seat_pricing_pressure | GOOGL | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-05 | 217 | mdna |
| ad_market_strength | AMZN | — | AAPL, DASH, GOOG, META, RDDT | 2026-02-06 | 216 | mdna |
| automotive_semiconductor_demand | TXN | — | AAPL, AMAT, AMBA, HPE, LRCX, MPWR +1 | 2026-02-06 | 216 | mdna |
| capex_vs_opex_shift | AMZN | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-06 | 216 | mdna |
| platform_take_rate | RDDT | — | AAPL, AMZN, DASH | 2026-02-06 | 216 | mdna |
| software_seat_pricing_pressure | RDDT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-06 | 216 | mdna |
| capex_vs_opex_shift | BE | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-09 | 213 | mdna |
| software_seat_pricing_pressure | BE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-09 | 213 | mdna |
| capex_vs_opex_shift | ENTG | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-11 | 211 | mdna |
| software_seat_pricing_pressure | ENTG | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-11 | 211 | mdna |
| automotive_semiconductor_demand | GLW | — | AAPL, AMAT, AMBA, HPE, LRCX, MPWR +1 | 2026-02-12 | 210 | mdna |
| software_seat_pricing_pressure | GLW | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-12 | 210 | mdna |
| ad_market_strength | ROKU | — | AAPL, DASH, GOOG, META, RDDT | 2026-02-13 | 209 | mdna |
| capex_vs_opex_shift | ROKU | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-13 | 209 | mdna |
| platform_take_rate | ROKU | — | AAPL, AMZN, DASH | 2026-02-13 | 209 | mdna |
| software_seat_pricing_pressure | ROKU | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-13 | 209 | mdna |
| capex_vs_opex_shift | ANET | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-17 | 205 | mdna |
| capex_vs_opex_shift | CSCO | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-17 | 205 | mdna |
| capex_vs_opex_shift | PLTR | — | AAPL, CIEN, CRWD, FPS, GLW, GWRE +3 | 2026-02-17 | 205 | mdna |

### Stage 1 — evidence, nobody asked anywhere (13)
| theme | company | first evidence | open days | n_evidence | sources |
|---|---|---|---|---|---|
| foundry_capacity | CIEN | 2025-12-12 | 272 | 2 | mdna |
| silicon_architecture_competition | FN | 2026-02-03 | 219 | 2 | mdna |
| antitrust_action | GOOG | 2026-02-05 | 217 | 2 | mdna |
| antitrust_action | GOOGL | 2026-02-05 | 217 | 2 | mdna |
| fed_policy_tech | UPST | 2026-02-10 | 212 | 18 | mdna |
| foundry_capacity | GLW | 2026-02-12 | 210 | 12 | mdna |
| foundry_capacity | NXPI | 2026-02-19 | 203 | 7 | mdna |
| foundry_capacity | AXON | 2026-02-25 | 197 | 2 | mdna |
| antitrust_action | META | 2026-04-30 | 133 | 2 | mdna |
| space_supply_chain | RKLB | 2026-05-07 | 126 | 16 | mdna |
| foundry_capacity | RDNT | 2026-05-11 | 122 | 5 | mdna |
| foundry_capacity | LITE | 2026-08-17 | 24 | 2 | mdna |
| foundry_capacity | FN | 2026-08-18 | 23 | 3 | mdna |

### Newly said in CY2026-Q3 (71) — absent from the same filer's two prior quarters (findings R4/R5)
| company | theme | register | source | rows |
|---|---|---|---|---|
| AAOI | automotive_semiconductor_demand | evidence | exchange | 1 |
| AAPL | hbm_competitive_landscape | evidence | exchange | 1 |
| AMAT | automotive_semiconductor_demand | evidence | mdna | 2 |
| AMD | humanoid_robotics_competition | evidence | exchange | 1 |
| AMD | silicon_architecture_competition | evidence | exchange | 1 |
| AMD | thermal_management_cooling | evidence | exchange | 5 |
| ANET | automotive_semiconductor_demand | question | exchange | 1 |
| AVGO | agent_framework_landscape | evidence | exchange | 1 |
| AVGO | automotive_semiconductor_demand | evidence | mdna | 3 |
| AVGO | chip_design_competition | evidence | exchange | 1 |
| AVGO | energy_storage_buildout | evidence | exchange | 1 |
| AVGO | frontier_model_competition | evidence | exchange | 1 |
| AVGO | model_commoditization | evidence | exchange | 1 |
| AVGO | model_efficiency_evolution | evidence | exchange | 5 |
| AVGO | nand_demand_cycle | evidence | exchange | 1 |
| AVGO | pc_demand | evidence | exchange | 1 |
| AVGO | solar_supply_chain | evidence | mdna | 3 |
| AXON | software_seat_pricing_pressure | evidence | exchange | 2 |
| BE | china_ai_infrastructure_demand | evidence | exchange | 1 |
| BE | hyperscaler_revenue_concentration | evidence | exchange | 1 |
| BE | model_commoditization | evidence | exchange | 1 |
| BE | model_efficiency_evolution | evidence | exchange | 1 |
| BE | networking_margin_trajectory | evidence | exchange | 1 |
| CIEN | energy_storage_buildout | question | exchange | 1 |
| COHR | solar_supply_chain | evidence | mdna | 2 |
| CRS | data_center_deployment_constraints | evidence | exchange | 1 |
| CRS | space_supply_chain | evidence | exchange | 1 |
| CRWD | inference_compute_economics | question | exchange | 1 |
| CRWD | model_commoditization | question | exchange | 1 |
| CRWV | sovereign_ai_deployments | evidence | exchange | 2 |
| CSCO | solar_supply_chain | evidence | mdna | 2 |
| DDOG | ai_re_architected_incumbent | question | exchange | 1 |
| DOCN | vertical_ai_applications | question | exchange | 1 |
| ENTG | solar_supply_chain | evidence | mdna | 2 |
| FN | foundry_capacity | evidence | mdna | 3 |
| GDS | hyperscaler_revenue_concentration | evidence | exchange | 2 |
| GDS | solar_supply_chain | evidence | exchange | 1 |
| GLW | enterprise_ai_adoption | evidence | exchange | 1 |
| GLW | handset_competition | evidence | exchange | 2 |
| GOOG | agent_framework_landscape | question | exchange | 2 |
| GOOG | ai_compute_topology | question | exchange | 1 |
| GOOG | software_seat_pricing_pressure | question | exchange | 1 |
| GWRE | ai_infrastructure_software | evidence | exchange | 1 |
| GWRE | ai_native_vertical | evidence | exchange | 2 |
| HNGE | ai_native_vertical | evidence | exchange | 1 |
| HNGE | capex_vs_opex_shift | evidence | exchange | 1 |
| INDI | china_consumer_demand | evidence | exchange | 1 |
| INDI | humanoid_robotics_competition | evidence | exchange | 1 |
| INDI | nand_demand_cycle | evidence | exchange | 2 |
| INTC | hyperscaler_revenue_concentration | question | exchange | 2 |
| IOT | ad_market_strength | question | exchange | 1 |
| IOT | ai_re_architected_incumbent | question | exchange | 1 |
| IOT | data_center_deployment_constraints | question | exchange | 2 |
| IOT | datacenter_buildout_pacing | question | exchange | 1 |
| IOT | platform_take_rate | question | exchange | 1 |
| LITE | foundry_capacity | evidence | mdna | 2 |
| LITE | software_seat_pricing_pressure | evidence | mdna | 5 |
| LITE | solar_supply_chain | evidence | mdna | 2 |
| LRCX | data_center_deployment_constraints | evidence | exchange | 1 |
| LRCX | pc_demand | evidence | exchange | 1 |
| LRCX | software_seat_pricing_pressure | evidence | mdna | 2 |
| LRCX | solar_supply_chain | evidence | exchange | 1 |
| LRCX | solar_supply_chain | evidence | mdna | 2 |
| MPWR | capex_vs_opex_shift | question | exchange | 1 |
| MTRN | space_supply_chain | evidence | exchange | 3 |
| NVDA | capex_vs_opex_shift | evidence | mdna | 2 |
| PWR | energy_storage_buildout | evidence | mdna | 2 |
| RBRK | cybersecurity_competitive_landscape | evidence | mdna | 2 |
| SNOW | hyperscaler_revenue_concentration | evidence | mdna | 2 |
| SNPS | automotive_semiconductor_demand | evidence | mdna | 3 |
| STX | software_seat_pricing_pressure | evidence | mdna | 2 |
