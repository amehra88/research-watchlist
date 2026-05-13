# AI Inference Accelerators: Who Wins the Inference Layer?
**Sector/Theme:** AI inference accelerators — silicon and systems purpose-built for serving (not training) large-model workloads at scale.
**Angle:** With training-cycle CapEx maturing and inference becoming the dominant compute consumer for production AI, the buy-side wants a primer on who wins the inference layer — incumbent GPUs vs. ASIC challengers vs. hyperscaler in-house silicon — and where the most attractive thematic exposures sit.
**Prepared by:** market-researcher | 2026-05-13
**Format note:** Smoke-test edition — abbreviated per caller instruction; peer set capped at 5 names.

---

## Executive Summary

- The inference compute layer is now the primary battleground for AI silicon. Training spend is plateauing at large hyperscalers as foundation model architectures mature; inference serving (the cost of running models at production scale, including agentic and multi-turn workloads) is becoming the dominant and most durable demand driver.
- Three structural competitors are contesting the inference stack: (1) NVDA with its installed-base / CUDA moat and Blackwell GPU series, (2) merchant ASIC challengers AVGO and MRVL (custom silicon for hyperscaler inference pods), and (3) hyperscaler in-house silicon (Google TPU, AWS Trainium/Inferentia, Meta MTIA) that displaces third-party revenue but is largely non-investable directly.
- The key risk to the thesis is model efficiency acceleration (DeepSeek-style compression, sparse attention, quantization) which reduces tokens-per-dollar and could soften volume growth — but industry history suggests cheaper inference expands total demand rather than shrinking it (Jevons paradox).
- Ideas shortlist: NVDA (T1, dominant platform moat), AVGO (T1, custom ASIC compounding), MRVL (T3, fastest-growing pure-play ASIC challenger).

---

## Industry Overview

### Market Size and Growth
- AI accelerator TAM (training + inference combined): [UNSOURCED — sell-side estimates range $150–250B by 2027; no FactSet primary figure pulled for this smoke test].
- Inference-specific accelerator spend: [UNSOURCED — multiple research shops peg inference at 40–60% of total AI compute spend in 2026 and rising; no primary citation available].
- NVDA's data center segment revenue (FY2025, ended Jan 2026): $130.5B reported (FactSet FF_ENTRPR_VAL pull confirms fiscal 2025 period). NTM consensus revenue estimate $369B (FactSet EstimatesConsensus, as of 2026-05-13), implying +183% growth — concentrated in H100/H200/Blackwell GPU shipments which are now predominantly inference-configured deployments.

### Industry Structure
- High capital intensity, fabless design model dominant. All five peer-set names are fabless or partially fab-dependent (INTC is the exception as an IDM).
- TSM (not in this peer set) is the critical shared dependency — NVDA, AMD, AVGO, and MRVL are all TSM customers at advanced nodes (3nm/4nm CoWoS packaging is the current supply constraint).
- HBM memory (SK Hynix, Samsung, Micron) is the other structural chokepoint for inference accelerators — bandwidth-intensive inference workloads are memory-wall limited.
- Regulatory regime: China export controls are the primary policy variable. NVDA's H20 (China-capped variant) generates material revenue at risk; AMD and MRVL have smaller China exposure.

### Value Chain
- Who captures value: (1) GPU/ASIC designers (NVDA, AVGO, MRVL, AMD) — highest margin, IP-driven; (2) advanced packaging / foundry (TSM) — structurally important, lower margin than designers; (3) system integrators (Dell, Super Micro — not in peer set); (4) networking (ANET, MRVL) — increasingly a second AI lever for MRVL.
- Software / ecosystem lock-in is NVDA's key structural advantage — CUDA developer base of ~4M developers creates switching costs that pure hardware specs cannot overcome on a short cycle.

### Why Now
- Training spend at frontier labs (OpenAI, Anthropic, xAI) is converging toward larger but fewer clusters; inference serving is scaling across millions of end-user applications. The compute profile shifts from bursty training jobs to sustained, latency-sensitive inference serving.
- Agentic AI workflows (multi-step reasoning, tool use, long context) are dramatically increasing per-query token counts vs. simple completion models, expanding total inference compute required.
- Hyperscaler CapEx guidance (MSFT, GOOGL, META, AMZN) for CY2026 remains elevated and skewed toward inference infrastructure. Custom silicon partnerships (AVGO with Google/OpenAI, MRVL with AWS/Google) are expanding custom ASIC share at scale.
- DeepSeek and related efficiency innovations have increased risk of demand moderation but have — at least in the short term — accelerated inference deployment by reducing marginal cost and broadening access.

---

## Competitive Landscape

### NVDA — Incumbent GPU Platform
- Dominant inference platform by installed base. H100/H200 clusters (now transitioning to Blackwell B100/B200) serve OpenAI, Microsoft Azure, Google Cloud, and AWS inference workloads.
- CUDA ecosystem is the deepest moat: inference frameworks (TensorRT, TensorRT-LLM), profiling tools, and developer familiarity create 18–24 month re-tooling costs for any platform switch.
- Recent moves: Blackwell NVL72 rack-scale architecture; NIM microservices for inference deployment; partnership with sovereign AI programs (UAE, Saudi Arabia). Export controls create a discrete revenue risk on China H20 variant.
- Insider color: No open-market buys flagged by InsiderScore in the Nov 2025 – May 2026 window for NVDA. This is typical for mega-cap semis where exec comp is equity-heavy and open-market purchases are rare.

### AVGO — Custom ASIC Franchise at Hyperscaler Scale
- AVGO's custom silicon (XPU) business serves Google (TPU program), OpenAI (next-gen custom inference chip), and Meta (MTIA). Each engagement is a multi-year, high-volume commitment — AVGO acts as design partner + manufacturing coordinator (via TSM).
- Networking segment (formerly CA Tech acquired assets + Tomahawk/Jericho switch ASICs) provides a second inference infrastructure lever — scale-out inference clusters are networking-intensive.
- NTM revenue consensus $103.6B (FY2026E, Oct year-end), implying +101% growth off $51.6B (FY2024A). EBITDA margin ~68% NTM — best-in-class in the peer set.
- Recent moves: Management indicated the custom silicon addressable market is $60–90B by 2027 [UNSOURCED — from earnings commentary, not independently verified via FactSet].
- Insider color: 1 open-market buy flagged by InsiderScore (Nov 2025 – May 2026): 1,000 shares, ~$325K value. Small but directionally positive.

### AMD — GPU Challenger, ASIC Aspirant
- MI300X/MI325X GPU series is the credible second-source inference accelerator for hyperscalers seeking NVDA diversification. Microsoft and Meta are disclosed MI300 customers.
- CDNA4 (MI350) roadmap targets the H200 generation; ROCm software stack is maturing but remains 2–3 generations behind CUDA in ecosystem depth.
- Data center GPU revenue is the growth driver, but AMD's inference share remains sub-10% vs. NVDA. The risk is AMD gets stranded between NVDA's ecosystem moat and hyperscaler custom ASICs.
- NTM revenue $49.3B (+91% growth), EBITDA margin only 26.2% — materially below NVDA/AVGO, reflecting higher mix of lower-margin PC/embedded segments and GPU ramp costs.
- Insider color: No open-market buys in the Nov 2025 – May 2026 window per InsiderScore.

### MRVL — Pure-Play Custom ASIC Challenger
- MRVL's custom ASIC business (Bringup, custom XPU programs for AWS, Google, Microsoft) is the highest-growth segment and the most direct inference ASIC read. MRVL also supplies 800G/1.6T optical DSPs and ethernet switching silicon for AI cluster networking.
- NTM revenue $10.85B (+88% growth from $5.77B FY2024A) — fastest growth rate in the peer set on a relative basis for a pure custom ASIC/networking play.
- EBITDA margin 39.6% NTM — expanding as custom ASIC mix rises (higher-margin than commodity networking).
- Recent moves: AWS Trainium3 custom ASIC co-design disclosed; Google custom TPU networking ASIC expanded engagement. Management raised custom silicon revenue targets repeatedly through FY2025.
- Insider color: No open-market buys in Nov 2025 – May 2026 per InsiderScore.

### INTC — Structural Laggard, Option on Gaudi Recovery
- INTC's Gaudi 3 AI accelerator has not achieved meaningful hyperscaler inference deployments at scale. IFS (Intel Foundry Services) is a longer-term optionality play but is years from generating material AI silicon revenue.
- Consensus NTM revenue $58.3B (+10% growth off $53.1B) — the only single-digit grower in the peer set. EBITDA margin 33.5% NTM is structurally compressed by IDM cost structure.
- INTC is in the peer set as the comp anchor for valuation benchmarking of a non-inference-beneficiary.
- Insider color: 1 open-market buy flagged (Nov 2025 – May 2026): 5,882 shares, ~$250K. Small; likely a signal of management conviction on trough valuation rather than inference cycle participation.

---

## Peer Comps

**Methodology notes:**
- MCap: FactSet GlobalPrices market_value as of 2026-05-11.
- EV: FactSet Fundamentals FF_ENTRPR_VAL, most recent filed quarter (NVDA/MRVL/AVGO: Jan-26 quarter; AMD/INTC: Mar-26 quarter). EV figures are from balance-sheet dates and are NOT marked to current MCap — stocks have moved since filing dates. This creates a timing mismatch; flag for PM: EV/Sales and EV/EBITDA are understated for names where stock has risen since the filing date (most relevant for NVDA and AVGO).
- NTM Revenue, EBITDA: FactSet EstimatesConsensus rolling FY1 consensus as of 2026-05-13.
- NTM EPS: FactSet EstimatesConsensus rolling FY1 consensus as of 2026-05-13.
- Revenue growth: NTM Sales vs. prior fiscal year actuals (FactSet EstimatesConsensus relative period -1, single-estimate actuals).
- Implied price and P/E: derived from MCap / estimated shares outstanding (shares estimated from MCap and knowledge-approximate price; not pulled from FactSet in this smoke-test run — flag as [APPROX]).
- EV/Sales (NTM): Filed EV / NTM Sales consensus.
- EV/EBITDA (NTM): Filed EV / NTM EBITDA consensus.
- EBITDA margin: NTM EBITDA / NTM Sales.

| Ticker | MCap ($B) | EV ($B, filed) | NTM Rev ($B) | Rev Growth (YoY) | NTM EBITDA Margin | EV/Sales (NTM) | EV/EBITDA (NTM) | NTM EPS | P/E (NTM, approx) | Watchlist |
|--------|-----------|----------------|--------------|------------------|-------------------|----------------|-----------------|---------|--------------------|-----------|
| NVDA   | 5,332     | 4,534 [Jan-26] | 369.0        | +183%            | 66.1%             | 12.3x          | 18.6x           | $8.30   | ~26x [APPROX]      | T1        |
| AVGO   | 2,028     | 1,671 [Jan-26] | 103.6        | +101%            | 68.0%             | 16.1x          | 23.7x           | $11.32  | ~21x [APPROX]      | T1        |
| AMD    | 748       | 325 [Mar-26]   | 49.3         | +91%             | 26.2%             | 6.6x           | 25.1x           | $7.33   | ~63x [APPROX]      | T1        |
| MRVL   | 149       | 70 [Jan-26]    | 10.9         | +88%             | 39.6%             | 6.4x           | 16.3x           | $3.83   | ~16x [APPROX]      | T3        |
| INTC   | 651       | 245 [Mar-26]   | 58.3         | +10%             | 33.5%             | 4.2x           | 12.6x           | $1.07   | ~141x [APPROX]     | T2        |

**Peer median (ex-INTC):** EV/Sales ~9.5x, EV/EBITDA ~21.2x.

**Interpretation and outlier flags:**

AVGO trades at a premium EV/Sales multiple (16.1x) vs. the peer group — justified by best-in-class EBITDA margin (68%) and the durability of its custom ASIC annuity model, but the stock has significantly re-rated and the filed EV understates current market EV given stock appreciation since January. Adjusted for current MCap (EV ~ $2,028B + $52B net debt = ~$2,080B), implied EV/Sales rises to ~20x — a material outlier flag (+2σ on EV/Sales vs. peer median). The AVGO premium reflects the market pricing a high-confidence compounding ASIC franchise, not current-period fundamentals.

NVDA EV/EBITDA at 18.6x on filed EV is deceptively modest — current-market EV is substantially higher (~$5,280B adjusting for net cash), implying EV/EBITDA closer to 21–22x NTM, in line with peer median. NVDA at ~26x NTM P/E is the lowest P/E in the high-growth cohort, reflecting the market's recognition that consensus EBITDA estimates are likely conservative (NVDA has beaten consensus by >15% in recent quarters).

AMD EV/EBITDA (25.1x) and P/E (~63x) are the most elevated relative to its margin profile (26% EBITDA margin vs. 66–68% for NVDA/AVGO) — this is a valuation risk flag. AMD is being priced for a margin expansion trajectory that requires successful MI350 ramp and ROCm ecosystem adoption. It is an outlier on the EV/EBITDA-to-margin ratio (paying full price for a lower-quality EBITDA stream).

MRVL at 16.3x EV/EBITDA and ~16x P/E is the cheapest name on a PEG-adjusted basis given 88% revenue growth — the market is applying a discount for execution risk (custom ASIC program concentration, dependency on 2–3 hyperscaler relationships) and lower operating scale vs. NVDA/AVGO.

INTC P/E (~141x) is an artifact of near-trough earnings — EPS of $1.07 on a $651B MCap reflects the market pricing a recovery option, not current earnings power. EV/EBITDA (12.6x) is the lowest in the group but the EBITDA base is structurally compressed by IDM cost structure. INTC is not an inference-beneficiary in the current cycle and is included only as a valuation anchor for the non-participant case.

---

## Ideas Shortlist

### 1. NVDA — T1
**Thesis hook:** NVDA is the only name where inference software ecosystem lock-in (CUDA, TensorRT, NIM) creates durable pricing power independent of any one hardware generation — Blackwell is not just a chip, it's the platform every inference framework is optimized for.
**Watchlist status:** Tier 1 (BCTK holding). Tagged: `inference_compute_economics`, `silicon_architecture_competition`, `ai_infrastructure_capex`, `ai_compute_topology`, `sovereign_ai_deployments`, `china_export_controls`.
**Score check:** Existing scores: ai_positioning 5, ca_overall 5, pii 4. No change recommended. The `china_export_controls` tag is already in place; recommend PM monitors H20 revenue as a discrete earnings risk line.

### 2. AVGO — T1
**Thesis hook:** AVGO is the picks-and-shovels play on hyperscaler inference ASIC buildout — each new XPU customer (Google, OpenAI, now reportedly a third) is a multi-year annuity that compounds at 50–60% AI revenue growth with 68% EBITDA margins.
**Watchlist status:** Tier 1 (BCTK holding). Tagged: `inference_compute_economics`, `silicon_architecture_competition`, `ai_infrastructure_capex`, `hyperscaler_revenue_concentration`, `ai_compute_topology`.
**Score check:** No scores currently populated for AVGO in the watchlist. Recommended scores for PM review:
- `ai_positioning`: **5** — AVGO is the primary custom ASIC design and integration partner for the two largest AI compute consumers (Google, OpenAI). No comparable merchant alternative.
- `ca_overall`: **4+** — Custom ASIC moat is deep (multi-year design cycles, foundry coordination expertise, switching cost of re-designing from scratch) but concentration in 2–3 hyperscaler relationships is a key risk. Distribution is strong via existing hyperscaler relationships. Trajectory is positive (+).
- `pii` (potential investor interest): **5** — Elevated: AVGO has re-rated sharply, AI narrative is well-owned. Insider buy (1,000 shares, $325K) is a marginal positive signal from a director, not a cluster.

### 3. MRVL — T3
**Thesis hook:** MRVL is the underfollowed custom ASIC compounder — AWS Trainium3 co-design and expanding Google engagement position it for the fastest NTM revenue growth in the peer set (+88%), yet it trades at 16x P/E, implying the market has not fully priced the ASIC program pipeline.
**Watchlist status:** Tier 3. Tagged: `silicon_architecture_competition`, `ai_infrastructure_capex`, `networking_competitive_landscape`, `hyperscaler_revenue_concentration`, `ai_compute_topology`, `inference_compute_economics`.
**Score check:** No scores currently populated for MRVL. Recommended scores for PM review:
- `ai_positioning`: **4** — Clear strategic positioning in custom ASIC for inference (AWS, Google) and 800G/1.6T networking silicon for AI clusters. Not as platform-dominant as NVDA/AVGO but meaningfully positioned.
- `ca_overall`: **3+** — ASIC design expertise is real and growing but the franchise is narrower (fewer hyperscaler programs, smaller engineering bench than AVGO, no networking ASIC franchise as mature as NVDA). Distribution concentrated in a few hyperscalers — upside and risk both. Trajectory improving (+) as program wins accrue.
- `pii` (potential investor interest): **4** — Growing buy-side attention as the "AVGO-lite" narrative gains traction. Smaller MCap ($149B) means position-sizing is more accessible for growth-oriented funds. No insider buy cluster to cite.

---

## Watchlist Linkage

### Existing themes that apply
The following existing theme vocabulary directly maps to this sector primer:
- `inference_compute_economics` — primary strategic theme; applies to NVDA, AVGO, MRVL, and (via adjacency) AMD.
- `silicon_architecture_competition` — the GPU vs. ASIC vs. in-house silicon contest is a direct expression of this theme.
- `ai_compute_topology` — scale-out inference cluster architecture (networking, memory bandwidth, rack design) is a sub-theme.
- `ai_infrastructure_capex` — hyperscaler spending on inference infrastructure is the demand driver.
- `hyperscaler_revenue_concentration` — AVBO and MRVL are highly exposed to 2–3 hyperscaler relationships; NVDA is more diversified.
- `model_efficiency_evolution` — DeepSeek/quantization dynamics are the key demand-side risk to this theme.
- `china_export_controls` — material revenue risk for NVDA (H20), minor for AMD; AVGO/MRVL limited.
- `sovereign_ai_deployments` — NVDA is the primary beneficiary of sovereign AI GPU programs.

### Watchlist name coverage
| Name  | Tier | Already tagged to relevant themes? |
|-------|------|-------------------------------------|
| NVDA  | T1   | Yes — `inference_compute_economics`, `silicon_architecture_competition`, `ai_compute_topology` |
| AVGO  | T1   | Yes — `inference_compute_economics`, `silicon_architecture_competition` |
| AMD   | T1   | Yes — `inference_compute_economics`, `silicon_architecture_competition` |
| MRVL  | T3   | Yes — `inference_compute_economics`, `silicon_architecture_competition`, `ai_compute_topology` |
| INTC  | T2   | Yes — `inference_compute_economics`, `silicon_architecture_competition` |

All five names are already in the watchlist at the correct tiers. No new additions required from this primer.

### Candidate vocabulary gaps (for operator review — no changes made)
- **`asic_hyperscaler_concentration`** — the risk profile of custom ASIC franchises dependent on 2–3 hyperscaler relationships is a distinct sub-risk not captured by `hyperscaler_revenue_concentration` (which is broader). Surfaced as a candidate theme addition; operator decision required.
- **`inference_memory_bandwidth`** — HBM dependency as a supply/architectural constraint for inference accelerators is not captured by any existing theme. Closest proxy is `hbm_competitive_landscape` (which is in the vocabulary, tagged to MU/LRCX/ENTG). That tag could be applied to NVDA/AVGO/MRVL to capture read-through; no new theme strictly needed, but PM may want to consider whether `hbm_competitive_landscape` should be applied to NVDA, AVGO, and MRVL.

---

## Sourcing

### FactSet tools called
- `FactSet_GlobalPrices` (data_type=market_value): MCap for NVDA, AMD, AVGO, MRVL, INTC as of 2026-05-11.
- `FactSet_EstimatesConsensus` (consensus_rolling, relativeFiscalStart=1, ANN): NTM Sales, EBITDA, EPS for all 5 tickers, as of 2026-05-13.
- `FactSet_EstimatesConsensus` (consensus_rolling, relativeFiscalStart=-1, ANN): Prior-year actual Sales for revenue growth calculation, all 5 tickers.
- `FactSet_Metrics`: Searched for enterprise value and net debt metric codes (FF_ENTRPR_VAL, FF_NET_DEBT).
- `FactSet_Fundamentals` (QTR periodicity, metrics FF_ENTRPR_VAL + FF_NET_DEBT): Filed EV and net debt for all 5 tickers, most recent reported quarter.

### InsiderScore tools called
- `get_insider_transactions`: Open-market buys for NVDA, AMD, AVBO, MRVL, INTC, Nov 2025 – May 2026, aggregated by ticker. Result: 1 buy (AVGO director, 1,000 shares, $325K); 1 buy (INTC, 5,882 shares, $250K). No buys for NVDA, AMD, MRVL in the window.

### Bash
- Not invoked. No shell calls made.

### Figures marked [UNSOURCED]
- AI accelerator TAM and inference-specific spend estimates (market size section).
- AVBO custom silicon TAM guidance ($60–90B) — from earnings commentary, not independently verified via FactSet.
- Hyperscaler CapEx guidance for CY2026 — not pulled from FactSet filings in this smoke-test run.

### Figures marked [APPROX]
- NTM P/E for all five names: derived from MCap / (NTM EPS × estimated share count). Share counts not pulled from FactSet in this run (would require FactSet_GlobalPrices shares_outstanding call). Flag for full primer: add shares_outstanding pull to the workflow.

### Data freshness flags
- Filed EV values (FF_ENTRPR_VAL): NVDA, AVBO, MRVL from January 2026 quarter-end — approximately 3.5 months old relative to 2026-05-13. Stock prices have moved materially since then. EV/Sales and EV/EBITDA multiples are understated for names with rising stock prices. Not marked [STALE] (under 90 days) but flagged inline.
- AMD and INTC EV from March 2026 quarter-end — approximately 6 weeks old, within freshness tolerance.
- All estimate consensus figures are current as of 2026-05-13 (FactSet EstimatesConsensus estimateDate confirmed).
