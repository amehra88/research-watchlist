# Avicena — private driver profile

- **pvt_id:** `avicena.pvt`
- **Display name:** Avicena (AvicenaTech Corp)
- **Aliases:** Avicena · AvicenaTech · AvicenaTech Corp · Avicena Tech
- **Added:** 2026-06-03
- **Type:** Standing profile (not an earnings note). Privates have no public filings;
  this dir holds blog/news/conference synthesis and read-through notes.

> Synthesized from config (watchlist `private_drivers`, `supply-chain-manual.yaml`)
> plus web research verified 2026-06-03 (sources at bottom). Private company — no
> SEC filings; figures are from company/press disclosures.

## What it is

MicroLED-based **chip-to-chip optical interconnect** ("LightBundle") — uses arrays of
microLEDs (not lasers) to move data between GPUs/chips at high bandwidth and low power.
Positioned as an alternative to laser-based silicon-photonics interconnect for AI
data-center scale-up. The microLED approach is the company's core differentiation vs.
the silicon-photonics field.

## Why it's tracked

A credible disruptor in the AI optical-interconnect stack. Two read-through vectors:
1. **Competitive** — directly contests MRVL's Celestial AI Photonic Fabric, and is a
   structural long-dated threat to laser/transceiver datacom optics (COHR, LITE) **if
   the microLED approach scales to volume**.
2. **Strategic adoption** — its investor/partner roster (TSMC, SK Hynix, Samsung,
   Micron) is itself a signal: the memory and foundry leaders are funding/co-developing
   it, which both validates the threat to optics incumbents and gives those names
   optionality.

## Read-through to public names (`affects`)

MRVL · COHR · LITE · TSM · 000660.KS (SK Hynix) · MU (Micron) · 005930.KS (Samsung)

## Supply-chain edges (from `config/supply-chain-manual.yaml`)

**Avicena as competitor (`source → avicena.pvt`):**

| Source | Kind | Sig | Note |
|--------|------|-----|------|
| MRVL | competitor | high | LightBundle competes with Celestial AI Photonic Fabric, which MRVL acquired for $3.25B (closed 2026-02-02). Alternative optical scale-up interconnect. |
| COHR | competitor | medium | Emerging/long-dated threat — microLED interconnect could displace laser-based datacom optics if it scales. No current product overlap. Same disruption axis as POET (see POET→COHR edge). |
| LITE | competitor | medium | Same thesis as COHR — microLED could erode laser/transceiver demand at volume. Speculative, multi-year. |

**Avicena as partner/investee (`avicena.pvt → target`):**

| Target | Kind | Sig | Note |
|--------|------|-----|------|
| TSM | partnership, customer | medium | Co-manufacturing alliance (joint production of microLED interconnect, ~Jun 2025). Primary = partnership (true today); customer = forward thesis. Positive for TSM advanced-packaging optionality. |
| 000660.KS (SK Hynix) | strategic_investment, customer | medium | Series B investor (May 2025). Primary = investment (today); customer = forward HBM/memory optical-disaggregation thesis. |
| MU (Micron) | strategic_investment, customer | medium | Series B investor (May 2025). Same memory-disaggregation axis as SK Hynix. |
| 005930.KS (Samsung) | strategic_investment, customer | medium | Series B investor (May 2025). Same memory-disaggregation axis as SK Hynix / Micron. |

## Funding & key relationships

- **Series B: $65M (May 2025)**, led by **Tiger Global**; strategic investors **SK Hynix,
  Samsung, Micron, Lam Research** (also Maverick Silicon, Prosperity7, Venture Tech
  Alliance, Cerberus, Hitachi Ventures). Prior ~$25M raised in 2022.
- **TSMC** — co-manufacturing alliance (~Jun 2025) to jointly produce the microLED
  optical-interconnect products.
- **ams OSRAM / Lumileds** — microLED array production partners (capacity / mass-production).

## Competitive landscape

- **Closest tech peer:** Hyperlume (also microLED-based interconnect).
- **Silicon-photonics rivals:** Ayar Labs, Lightmatter, Celestial AI (now MRVL),
  Lightelligence, Quintessent, Salience Labs, NcodiN, RANOVUS.
- **Adjacent (tracked):** POET Technologies — optical-interposer / integrated light
  source; see `POET→COHR` and `POET→MRVL` edges in `supply-chain-manual.yaml`.

## Web sources

- Avicena Newsroom — https://avicena.tech/ — company_blog. Product, funding, and
  partnership announcements. (`affects:` MRVL, COHR, LITE, TSM, 000660.KS, MU, 005930.KS)
