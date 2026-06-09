---
pvt_id: spacex.pvt
name: SpaceX (Space Exploration Technologies Corp.)
doc_type: profile
status: pre-IPO (pricing 2026-06-11 close; first trade 2026-06-12 Nasdaq: SPCX)
factset_entity: 0071BP-E   # privateEntityFlag:1 — no public SPCX security linked until listing
last_updated: 2026-06-09
sources_verified: 2026-06-09
---

# SpaceX — Standing Profile

> Consolidated entity: launch services + Starlink + xAI/Grok (absorbed 2026-02-02, dissolved into SpaceX's AI division May 2026). On IPO this `.pvt` profile is renamed in place to `notes/SPCX/` (see `_transition-runbook.md`).

## 1. IPO snapshot (verified 2026-06-09 — *not yet priced*)

| Item | Value | Note |
|---|---|---|
| Pricing | After close **Wed 2026-06-11** | Final pricing release lands that evening |
| First trade | **Thu 2026-06-12**, **Nasdaq Global Select** | Ticker **SPCX** (dual Nasdaq Texas listing reported) |
| Offer price | **$135.00 / share** | **Fixed price**, not a book-built range (unusual; set by Musk) |
| Shares offered | **~555.6M** base (+ **~83.33M** greenshoe, 15%) | Up to ~639M if over-allotment exercised |
| Raise | **~$75B** base (up to ~$85.7B w/ greenshoe) | Largest IPO on record |
| Valuation | **~$1.75T** headline (**~$1.77T** fully diluted) | $1.77T = CNBC arithmetic at $135 *assuming EchoStar-spectrum + Cursor deals close* |
| Float | **~3–5%, very thin** | Sources range 3% (offered free float) to ~4.2–5% of shares out |
| Retail allocation | **up to ~30%** (~$22.5B) | vs. typical 5–10%; via Robinhood, SoFi, E*Trade, Fidelity, Schwab |

**Structure flags / risks:**
- **Thin-float feedback-loop risk:** index funds may need to buy up to ~30% of the free float, against a ~3–5% float — Bloomberg (2026-06-09) flags a potential demand/price feedback loop.
- **Valuation skepticism:** **Morningstar's Nicolas Owens** called the offering **"significantly overvalued,"** assigning a **$780B fair value — ~55% below the $1.75T target** ("worth less than half"). CNBC, 2026-06-03.
- **Contingent valuation:** the $1.77T fully-diluted figure bakes in the **EchoStar spectrum** and **Cursor/Anysphere** transactions closing (see §4).

**Banking syndicate** (*spec correction applied*): **5 lead bookrunners** — **Goldman Sachs (lead-left)**, Morgan Stanley, Bank of America, Citigroup, JPMorgan. Morgan Stanley is the **stabilization agent** (the spec listed MS as lead-left — it is not). **23 banks total** on the cover (spec said 21). Source: The Daily Upside, 2026-05-21.

## 2. Business lines

- **Launch services** — Falcon 9 / Falcon Heavy / Starship; dominant global launch cadence.
- **Starlink** — satellite broadband subscriptions; **~58% of FY2024 revenue** ($7.7B of ~$13.1B; Sacra/Payload). *Period caveat:* the S-1 reports "Connectivity" at **$11.387B FY2025** and **$3.257B Q1'26** — cite the period explicitly when using a %.
- **xAI / Grok** — frontier-model player; see §4.
- **Compute footprint** — major NVDA consumer (Colossus cluster; planned orbital data centers); **early adopter of NVIDIA's "Vera" CPU** (announced GTC Taipei 2026-06-01; NVIDIA named the adopter as "SpaceXAI").

## 3. Read-throughs (public names)

- **NVDA** — large compute customer (Colossus, Vera CPU early adopter, orbital DC plans).
- **GEV** — affected per supply-chain map (power for data centers).
- **TSLA** — Grok cross-pollination.
- Space-economy publics **RKLB / IRDM / ASTS** — read-through if added to coverage.

## 4. xAI absorption & Cursor signal

- **xAI acquired 2026-02-02** — all-stock, **1 xAI → 0.1433 SpaceX** (SpaceX $1T, xAI $250B → combined $1.25T). Musk announced **2026-05-06** xAI would cease to exist as a standalone company; Grok and X folded into **SpaceX's AI division** (colloquially "SpaceXAI"; SpaceX's own framing is "the AI division of SpaceX"). Absorbed former `xai.pvt` in our registry 2026-06-02.
- **Cursor/Anysphere — OPERATOR SIGNAL (2026-06-03, non-public, unverified):** SpaceX reportedly has an agreement to acquire Cursor/Anysphere (~$1.2B ARR coding-agent harness), expected to close within 12 months. Would add an `agent_framework_landscape` (harness axis) position atop `frontier_model_competition`. Part of the headline $1.77T diluted valuation is contingent on this closing. On close, fold Cursor exposure into the post-IPO SPCX entry (not a standalone `.pvt`).

## 5. Themes

`space_economy`, `frontier_model_competition` (Grok), `ai_infrastructure_capex` (compute consumer), and — pending Cursor close — `agent_framework_landscape`.

## Sources

- S-1 (SEC EDGAR, CIK 0001181412, Reg. 333-296070), filed 2026-05-20; S-1/A No.1 2026-06-01 — pull exact greenshoe / free-float / Starlink revenue-share from EDGAR before final use (SEC.gov blocked automated fetch this session).
- CNBC pricing/Morningstar coverage 2026-06-03; The Daily Upside syndicate 2026-05-21; Bloomberg float feedback-loop 2026-06-09; CNBC retail-access 2026-05-21; Sacra/Payload FY2024 revenue; CNN/Reuters xAI 2026-02-02; The Verge 2026-05-06; Data Center Knowledge / NVIDIA GTC 2026-06-01.

*All figures verified 2026-06-09 via secondary sources; confirm the three highest-variance items (greenshoe, free-float %, Starlink revenue share) against the EDGAR S-1 before relying on them downstream.*
