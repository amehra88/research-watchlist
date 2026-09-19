## Theme diffusion — 2026-09-19

Current quarter **CY2026-Q3** (in progress — counts are partial); prior CY2026-Q2. Quarters covered: CY2025-Q4, CY2026-Q1, CY2026-Q2, CY2026-Q3.

### Coverage (read first)
| quarter | earnings_call companies | conference companies | MD&A filers |
|---|---|---|---|
| CY2025-Q4 | 7 | 16 | 8 |
| CY2026-Q1 | 41 | 22 | 62 |
| CY2026-Q2 | 43 | 23 | 70 |
| CY2026-Q3 | 51 | 37 | 71 |

No transcript coverage — no results: AWS, DE, DPC, HSAI, INIO, NTES, PLAB, SE, SEI, TSEM, TTWO; incomplete/unknown: A000660, MU, NET, PLTR, POET, PWR, RKLB, SHOP, SNPS, SPCX, TSLA, TXN, WELL, accelink.cn, eoptolink.cn, hgtech.cn, innolight.cn, kaori.tw, mtar.in; unmappable: base_power.us, hisense_broadband.cn, source_photonics.cn. FactSet retrieval is topically scoped (theme-derived queries), not whole-call export.

- challenging_rate (spec §5) is not computed: exchange rows carry no challenging flag and 99% of analyst turns are sentiment=Neutral.
- P3 foreign evidence is not built: stages and lags use US MD&A evidence only; Chinese filers appear only in the exclusions list. Corprep transcript speech is reported as a count (n_corprep_companies) but does not set a stage: at its 0.30 threshold it mis-paired 3 of 5 spot-checked stage-2 rows.
- MD&A counts need >= 2 mapped blocks per filer-quarter and are lower-confidence than transcript counts (mdna precision ~0.4 at its threshold).
- The Tier-0 lag runs from MD&A filing dates only (corprep answers share the question's date). Both windows are truncated — questions 2025-11-11..2026-09-16, filings 2025-12-10..2026-09-11 — but the binding problem is PER-TICKER, not global: 21 tickers have MD&A coverage starting >30d after their call coverage, and those names produce the negative tail. A pair is only counted once the register that produced its SECOND event had been observed for 30d beforehand; today 27 negative and 25 positive pairs fail that test. The guard runs in BOTH directions on purpose: applying it to negative lags alone moved the same corpus from 34.2% to 86.2% evidence-led (measured 2026-09-15), which is not a correction but the discarding of every observation that disagreed.
- Call-side backfill is the binding gap and it is fixable: 23 of 66 tickers with any call coverage have their FIRST observed call in the last 45 days, i.e. one call and no question history at all. Nothing about those names can be identified in either direction, and they account for most of the dropped positive pairs. More transcript history moves this number; more statistics does not.
- Pairs whose filing and question fall within 3d are excluded as one reporting event rather than a disclosure and a response: the call-to-filing offset for the same quarter ran median +1d (p25 0, p75 2) when measured 2026-09-15. Tier 0 therefore measures leads and lags longer than one reporting cycle; a genuinely simultaneous disclosure is out of scope by construction, not absent from the data.
- No trend lines by design: three or four observations per theme support a comparison, not a slope.

### Movers — CY2026-Q3 vs CY2026-Q2 (n_banks first, then n_companies; host banks excluded at their own conferences)
| theme | banks | prev | Δ | companies asked | prev | disclosing (MD&A) | prev |
|---|---|---|---|---|---|---|---|
| enterprise_ai_adoption | 14 | 7 | +7 | 13 | 6 | 0 | 0 |
| local_commerce_delivery | 11 | 4 | +7 | 4 | 1 | 2 | 3 |
| cybersecurity_competitive_landscape | 12 | 7 | +5 | 9 | 3 | 3 | 2 |
| software_seat_pricing_pressure | 5 | 1 | +4 | 5 | 1 | 28 | 30 |
| nand_demand_cycle | 25 | 22 | +3 | 14 | 8 | 0 | 1 |
| frontier_model_competition | 3 | 0 | +3 | 5 | 2 | 0 | 0 |
| humanoid_robotics_competition | 3 | 0 | +3 | 4 | 1 | 0 | 0 |
| platform_take_rate | 4 | 1 | +3 | 4 | 1 | 6 | 10 |
| capex_vs_opex_shift | 7 | 4 | +3 | 6 | 4 | 22 | 33 |
| china_ai_infrastructure_demand | 3 | 0 | +3 | 2 | 0 | 0 | 0 |
| data_center_deployment_constraints | 21 | 18 | +3 | 13 | 12 | 3 | 0 |
| ai_compute_topology | 7 | 4 | +3 | 6 | 8 | 0 | 0 |
| foundation_model_economics | 2 | 0 | +2 | 3 | 1 | 0 | 0 |
| hbm_competitive_landscape | 16 | 15 | +1 | 9 | 5 | 0 | 0 |
| ai_re_architected_incumbent | 1 | 0 | +1 | 3 | 0 | 0 | 0 |
| agentic_commerce | 3 | 2 | +1 | 4 | 2 | 0 | 0 |
| ai_inference_margin_compression | 6 | 5 | +1 | 10 | 8 | 0 | 0 |
| automotive_semiconductor_demand | 3 | 2 | +1 | 5 | 3 | 12 | 12 |
| sovereign_ai_deployments | 1 | 0 | +1 | 2 | 0 | 0 | 0 |
| ad_market_strength | 3 | 2 | +1 | 4 | 3 | 5 | 9 |
| ai_native_vertical | 2 | 1 | +1 | 2 | 2 | 0 | 0 |
| defense_drones | 1 | 0 | +1 | 1 | 1 | 0 | 0 |
| china_export_controls | 0 | 0 | +0 | 2 | 0 | 2 | 3 |
| search_disruption | 2 | 2 | +0 | 3 | 1 | 0 | 0 |
| energy_storage_buildout | 15 | 15 | +0 | 9 | 8 | 4 | 2 |
| model_commoditization | 0 | 0 | +0 | 1 | 0 | 0 | 0 |
| thermal_management_cooling | 4 | 4 | +0 | 7 | 6 | 0 | 0 |
| ai_generated_content | 0 | 0 | +0 | 1 | 1 | 0 | 0 |
| ai_infrastructure_capex | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| ai_infrastructure_software | 4 | 4 | +0 | 5 | 5 | 0 | 0 |
| ai_regulation | 0 | 0 | +0 | 2 | 2 | 0 | 0 |
| antitrust_action | 0 | 0 | +0 | 0 | 0 | 0 | 1 |
| autonomous_vehicle_competition | 1 | 1 | +0 | 1 | 1 | 1 | 1 |
| china_consumer_demand | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| china_us_tensions | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| demographic_demand_tailwinds | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| fed_policy_tech | 0 | 0 | +0 | 0 | 0 | 1 | 1 |
| foundry_capacity | 0 | 0 | +0 | 0 | 0 | 5 | 3 |
| silicon_architecture_competition | 0 | 0 | +0 | 0 | 0 | 0 | 0 |
| space_supply_chain | 0 | 0 | +0 | 0 | 0 | 1 | 1 |

### Lifecycle (spec §6.3) — Tier-0 lag = first analyst question minus first MD&A filing, days
**Only 1 identified pair** (both registers observed >= 30d before the first event) — fewer than the 20 needed to state a distribution, so no share is reported. The lag is **not yet measurable from this corpus**, in either direction.
_Raw (censored, not a finding):_ n=58 pairs with both a filing and a question — median -1.0, 43.1% evidence-led, 32 negative. 27 negative and 25 positive pairs fail the observation test; a further 5 are same-reporting-event pairs (|lag| <= 3d) with no timing content. Do not quote these as a result; see the censoring note above.
Stage counts (theme, company): stage 1: 13, stage 2: 153, stage 3: 253, stage 4: 219
Stage 4 is **not assertable** for 21 theme(s): every company where the theme is known to be relevant has already been asked about it, so "asked at most covered names" has nothing to come out false against and those pairs are held at stage 3. Assigning these themes to companies in `config/watchlist.yaml` is what makes stage 4 computable for them: `advanced_materials_ai_infra`, `agentic_commerce`, `ai_generated_content`, `ai_inference_margin_compression`, `ai_regulation`, `chip_design_competition`, `cybersecurity_competitive_landscape`, `datacenter_buildout_pacing`, `defense_drones`, `energy_storage_buildout`, `foundation_model_economics`, `handset_competition`….

### Stage 2 — asked at another name, not here (153; verified-adjacent askers first)
| theme | company | adjacent asked (route, first question) | other askers | first evidence | open days | evidence |
|---|---|---|---|---|---|---|
| hyperscaler_revenue_concentration | NVDA | CBRS (manual:competitor, 2026-06-23); MRVL (manual:partnership, 2025-12-02) | AAOI, AMD, ANET, ARM, AVGO, CIEN +11 | 2026-02-25 | 206 | mdna |
| capex_vs_opex_shift | HPQ | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2025-12-10 | 283 | mdna |
| software_seat_pricing_pressure | HPQ | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-10 | 283 | mdna |
| solar_supply_chain | HPQ | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-10 | 283 | mdna |
| capex_vs_opex_shift | AMAT | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2025-12-12 | 281 | mdna |
| software_seat_pricing_pressure | AMAT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-12 | 281 | mdna |
| software_seat_pricing_pressure | CIEN | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-12 | 281 | mdna |
| automotive_semiconductor_demand | AVGO | — | AAPL, AMAT, AMBA, ANET, HPE, LRCX +2 | 2025-12-18 | 275 | mdna |
| capex_vs_opex_shift | AVGO | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2025-12-18 | 275 | mdna |
| capex_vs_opex_shift | MU | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2025-12-18 | 275 | mdna |
| china_export_controls | AVGO | — | AMAT, ASML, LRCX, NXPI | 2025-12-18 | 275 | mdna |
| nand_demand_cycle | MU | — | 000660.KS, 005930.KS, AAPL, AMAT, AMBA, AMD +13 | 2025-12-18 | 275 | mdna |
| pc_demand | HPE | — | AAPL, ANET, HPQ | 2025-12-18 | 275 | mdna |
| semiconductor_cycle | MU | — | 000660.KS, 005930.KS, AAPL, AMAT, AMBA, ANET +16 | 2025-12-18 | 275 | mdna |
| software_seat_pricing_pressure | AVGO | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 275 | mdna |
| software_seat_pricing_pressure | DE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 275 | mdna |
| software_seat_pricing_pressure | HPE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-18 | 275 | mdna |
| solar_supply_chain | HPE | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-18 | 275 | mdna |
| capex_vs_opex_shift | SNPS | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2025-12-22 | 271 | mdna |
| china_export_controls | SNPS | — | AMAT, ASML, LRCX, NXPI | 2025-12-22 | 271 | mdna |
| software_seat_pricing_pressure | SNPS | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2025-12-22 | 271 | mdna |
| solar_supply_chain | SNPS | — | BE, CRS, FPS, GEV, GLW, MTRN | 2025-12-22 | 271 | mdna |
| pc_demand | INTC | — | AAPL, ANET, HPQ | 2026-01-23 | 239 | mdna |
| solar_supply_chain | INTC | — | BE, CRS, FPS, GEV, GLW, MTRN | 2026-01-23 | 239 | mdna |
| software_seat_pricing_pressure | MSFT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-28 | 234 | mdna |
| capex_vs_opex_shift | LRCX | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-01-29 | 233 | mdna |
| capex_vs_opex_shift | NOW | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-01-29 | 233 | mdna |
| platform_take_rate | META | — | AAPL, AMZN, DASH, WMT | 2026-01-29 | 233 | mdna |
| software_seat_pricing_pressure | META | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-29 | 233 | mdna |
| software_seat_pricing_pressure | NOW | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-01-29 | 233 | mdna |
| automotive_semiconductor_demand | FN | — | AAPL, AMAT, AMBA, ANET, HPE, LRCX +2 | 2026-02-03 | 228 | mdna |
| capex_vs_opex_shift | FN | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-03 | 228 | mdna |
| china_consumer_demand | FN | — | AAPL, AMAT, LRCX | 2026-02-03 | 228 | mdna |
| platform_take_rate | FN | — | AAPL, AMZN, DASH, WMT | 2026-02-03 | 228 | mdna |
| aerospace_defense_aftermarket | COHR | — | CRS, GEV, LITE, MRVL, MTRN | 2026-02-04 | 227 | mdna |
| automotive_semiconductor_demand | COHR | — | AAPL, AMAT, AMBA, ANET, HPE, LRCX +2 | 2026-02-04 | 227 | mdna |
| capex_vs_opex_shift | TTWO | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-04 | 227 | mdna |
| platform_take_rate | TTWO | — | AAPL, AMZN, DASH, WMT | 2026-02-04 | 227 | mdna |
| software_seat_pricing_pressure | TTWO | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-04 | 227 | mdna |
| ad_market_strength | GOOGL | — | AAPL, DASH, GOOG, META, RDDT, WMT | 2026-02-05 | 226 | mdna |
| software_seat_pricing_pressure | GOOG | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-05 | 226 | mdna |
| software_seat_pricing_pressure | GOOGL | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-05 | 226 | mdna |
| ad_market_strength | AMZN | — | AAPL, DASH, GOOG, META, RDDT, WMT | 2026-02-06 | 225 | mdna |
| automotive_semiconductor_demand | TXN | — | AAPL, AMAT, AMBA, ANET, HPE, LRCX +2 | 2026-02-06 | 225 | mdna |
| capex_vs_opex_shift | AMZN | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-06 | 225 | mdna |
| platform_take_rate | RDDT | — | AAPL, AMZN, DASH, WMT | 2026-02-06 | 225 | mdna |
| software_seat_pricing_pressure | RDDT | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-06 | 225 | mdna |
| capex_vs_opex_shift | BE | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-09 | 222 | mdna |
| software_seat_pricing_pressure | BE | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-09 | 222 | mdna |
| capex_vs_opex_shift | ENTG | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-11 | 220 | mdna |
| capex_vs_opex_shift | SITM | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-11 | 220 | mdna |
| software_seat_pricing_pressure | ENTG | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-11 | 220 | mdna |
| software_seat_pricing_pressure | SITM | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-11 | 220 | mdna |
| automotive_semiconductor_demand | GLW | — | AAPL, AMAT, AMBA, ANET, HPE, LRCX +2 | 2026-02-12 | 219 | mdna |
| software_seat_pricing_pressure | GLW | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-12 | 219 | mdna |
| ad_market_strength | ROKU | — | AAPL, DASH, GOOG, META, RDDT, WMT | 2026-02-13 | 218 | mdna |
| capex_vs_opex_shift | ROKU | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-13 | 218 | mdna |
| platform_take_rate | ROKU | — | AAPL, AMZN, DASH, WMT | 2026-02-13 | 218 | mdna |
| software_seat_pricing_pressure | ROKU | — | CRWD, DDOG, GWRE, IOT, MDB, PANW +1 | 2026-02-13 | 218 | mdna |
| capex_vs_opex_shift | CSCO | — | AAPL, ANET, CIEN, CRWD, FPS, GLW +5 | 2026-02-17 | 214 | mdna |

### Stage 1 — evidence, nobody asked anywhere (13)
| theme | company | first evidence | open days | n_evidence | sources |
|---|---|---|---|---|---|
| foundry_capacity | CIEN | 2025-12-12 | 281 | 2 | mdna |
| silicon_architecture_competition | FN | 2026-02-03 | 228 | 2 | mdna |
| antitrust_action | GOOG | 2026-02-05 | 226 | 2 | mdna |
| antitrust_action | GOOGL | 2026-02-05 | 226 | 2 | mdna |
| fed_policy_tech | UPST | 2026-02-10 | 221 | 18 | mdna |
| foundry_capacity | GLW | 2026-02-12 | 219 | 12 | mdna |
| foundry_capacity | NXPI | 2026-02-19 | 212 | 7 | mdna |
| foundry_capacity | AXON | 2026-02-25 | 206 | 2 | mdna |
| antitrust_action | META | 2026-04-30 | 142 | 2 | mdna |
| space_supply_chain | RKLB | 2026-05-07 | 135 | 16 | mdna |
| foundry_capacity | RDNT | 2026-05-11 | 131 | 5 | mdna |
| foundry_capacity | LITE | 2026-08-17 | 33 | 2 | mdna |
| foundry_capacity | FN | 2026-08-18 | 32 | 3 | mdna |

### Newly said in CY2026-Q3 (80) — absent from the same filer's two prior quarters (findings R4/R5)
| company | theme | register | source | rows |
|---|---|---|---|---|
| AAPL | hbm_competitive_landscape | evidence | exchange | 1 |
| AMAT | automotive_semiconductor_demand | evidence | mdna | 2 |
| AMAT | networking_margin_trajectory | question | exchange | 1 |
| AMAT | pc_demand | question | exchange | 1 |
| AMD | ai_re_architected_incumbent | evidence | exchange | 1 |
| AMD | enterprise_ai_adoption | evidence | exchange | 1 |
| AMD | humanoid_robotics_competition | evidence | exchange | 1 |
| AMD | silicon_architecture_competition | evidence | exchange | 1 |
| AMD | thermal_management_cooling | evidence | exchange | 6 |
| ANET | advanced_materials_ai_infra | evidence | exchange | 1 |
| AVGO | advanced_materials_ai_infra | evidence | exchange | 1 |
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
| CRWD | inference_compute_economics | evidence | exchange | 2 |
| CRWD | model_commoditization | evidence | exchange | 1 |
| CRWV | sovereign_ai_deployments | evidence | exchange | 2 |
| CSCO | solar_supply_chain | evidence | mdna | 2 |
| DDOG | ai_re_architected_incumbent | question | exchange | 1 |
| DOCN | vertical_ai_applications | evidence | exchange | 1 |
| ENTG | solar_supply_chain | evidence | mdna | 2 |
| FN | foundry_capacity | evidence | mdna | 3 |
| FPS | hyperscaler_capex_buildout | evidence | exchange | 1 |
| FPS | silicon_architecture_competition | evidence | exchange | 1 |
| GDS | hyperscaler_revenue_concentration | evidence | exchange | 2 |
| GDS | solar_supply_chain | evidence | exchange | 1 |
| GEV | agent_framework_landscape | evidence | exchange | 1 |
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
| LRCX | data_center_deployment_constraints | question | exchange | 3 |
| LRCX | energy_storage_buildout | question | exchange | 1 |
| LRCX | pc_demand | question | exchange | 1 |
| LRCX | software_seat_pricing_pressure | evidence | mdna | 2 |
| LRCX | solar_supply_chain | question | exchange | 1 |
| LRCX | solar_supply_chain | evidence | mdna | 2 |
| MPWR | capex_vs_opex_shift | question | exchange | 1 |
| MTRN | space_supply_chain | evidence | exchange | 3 |
| NVDA | capex_vs_opex_shift | evidence | mdna | 2 |
| PWR | energy_storage_buildout | evidence | mdna | 2 |
| RBRK | cybersecurity_competitive_landscape | evidence | mdna | 2 |
| SITM | automotive_semiconductor_demand | evidence | mdna | 2 |
| SNOW | hyperscaler_revenue_concentration | evidence | mdna | 2 |
| SNPS | automotive_semiconductor_demand | evidence | mdna | 3 |
| STX | software_seat_pricing_pressure | evidence | mdna | 2 |
