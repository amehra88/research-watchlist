---
ticker: MRVL
primary_ticker: MRVL
subject_tickers:
  - MRVL
  - NVDA  # Jensen guest appearance + $2B investment relevant to NVDA syntheses too
period: conference-2026-06-02
event_date: "2026-06-02"
doc_type: conference_summary
event_type: keynote
event_name: Marvell Technology Computex 2026 Keynote
event_location: Taipei, Taiwan
speakers:
  - name: Matt Murphy
    title: CEO, Marvell Technology
  - name: Jensen Huang
    title: CEO, NVIDIA
    role_in_event: surprise guest appearance (~10 minutes)
source_urls:
  - https://www.digitimes.com/news/a20260602VL210/nvidia-ceo-marvell-jensen-huang-computex.html
  - https://www.cnbc.com/2026/06/02/jensen-huang-nvidia-marvell-technology-trillion-dollar-ai.html
  - https://www.hpcwire.com/off-the-wire/nvidias-jensen-huang-to-join-marvell-ceo-matt-murphy-at-computex-2026-keynote/
  - https://finance.yahoo.com/markets/stocks/articles/jensen-huang-calls-marvell-next-112630287.html
cross_reference_urls:
  - https://www.servethehome.com/marvell-computex-2026-keynote-live-coverage/   # structural keynote coverage — primary for Murphy remarks/products
  - https://nvidianews.nvidia.com/news/nvidia-ai-ecosystem-expands-as-marvell-joins-forces-through-nvlink-fusion  # 2026-03-31 partnership release (NVLink Fusion roles, $2B figure)
ingestion_date: "2026-06-03"
extraction_source: "WebFetch multi-query extraction + WebSearch corroboration via Claude Code session 2026-06-03 (Day 2 of MRVL workstream). NOT a verbatim transcript — content is paraphrased summary across multiple targeted extraction queries. ACCESS NOTE (honesty): of the four primary source_urls, only Yahoo Finance returned full body text; Digitimes was largely paywalled (headline + one related-headline only); CNBC and HPCwire both returned HTTP 403 and were NOT directly fetched — their content reaches this note secondhand via Yahoo (which cites CNBC) and WebSearch snippets. The richest accessible structural coverage came from ServeTheHome live coverage and the NVIDIA 2026-03-31 newsroom release (see cross_reference_urls). Future synthesis agents should treat as summary coverage, not quotable verbatim source. For verbatim quotes, refer to the source URLs."
---

# Marvell Technology Computex 2026 Keynote — June 2, 2026

_Multi-query WebFetch + WebSearch summary ingested 2026-06-03 (Claude Code session, Day 2 of MRVL workstream). Matt Murphy keynote at Computex Taipei, June 2, with a ~10-minute surprise guest appearance by NVIDIA CEO Jensen Huang. This is a SEPARATE event from the NVIDIA GTC Taipei keynote of June 1 (ingested at `notes/NVDA/20260601-conf-gtc-taipei.md`). Accessible sources: Yahoo Finance (full text), ServeTheHome (structural live coverage), NVIDIA newsroom (2026-03-31 partnership release), WebSearch corroboration. Digitimes paywalled; CNBC + HPCwire 403 (secondhand only)._

## Fidelity note

This note is a **multi-query WebFetch + WebSearch summary, NOT a verbatim transcript ingest.** It sits **two layers of summarization** between any source's original wording and this note (WebFetch passes each page through a summarization model and answers a per-query prompt rather than returning raw text). **Every quoted line below is the summary's rendering of reported wording and must NOT be treated as exactly quotable** — for verbatim quotes or precise wording, refer to the source URLs in frontmatter. Where two sources render the same Jensen remark differently, both renderings are shown to make the summary-variance explicit (see §3). Two of the four task-designated primary sources (CNBC, HPCwire) were **inaccessible (HTTP 403)** and reach this note only secondhand; Digitimes was largely **paywalled**. A future ingest cycle should re-pull this keynote via a proper transcript-fidelity path (FactSet_UnstructuredContent semantic query on the Marvell Computex 2026 keynote, or a direct transcript source) — **filed as next-session work.** Cross-source discrepancies and unverified claims are flagged inline below.

## 1. Headline announcements

- **Jensen Huang surprise guest appearance** — ~10 minutes during Murphy's keynote. Confirmed across Digitimes, Yahoo/CNBC, ServeTheHome.
- **Jensen called Marvell "the next trillion-dollar company"** — the quote that drove yesterday's MRVL scoring update. Reported wording: *"The next trillion-dollar company, ladies and gentlemen,"* delivered after Murphy wrapped his AI-infrastructure presentation (Digitimes headline; Yahoo; ServeTheHome). See §3 for context and the two-rendering variance.
- **NVIDIA $2 billion investment in Marvell** — figure is **unanimous across every source** (NVIDIA newsroom, ServeTheHome, Yahoo/CNBC, plus WebSearch corroboration from Tom's Hardware, optics.org, TradingKey). ⚠️ **Timing nuance (material for honesty):** the $2B was **announced March 31, 2026** as part of the NVLink Fusion partnership (NVIDIA newsroom release: *"In addition, NVIDIA has invested $2 billion in Marvell"*) — it was **reiterated/contextualized at the June 2 Computex keynote, not freshly announced there.** Murphy referenced it onstage as validation of the partnership direction. No source disclosed structure beyond the headline figure (no stake %, no terms).
- **NVLink Fusion partnership** — Marvell positioned as a custom-silicon + scale-up-networking participant in the NVIDIA rack-scale ecosystem (see §4 for the verbatim role split). ⚠️ The specific phrase **"preferred custom silicon partner" was NOT found in any accessible source.** NVIDIA's own release uses "joins forces … through NVLink Fusion" and "greater choice and flexibility," not "preferred." ServeTheHome explicitly notes the coverage does not use "preferred custom silicon partner" language. **Treat that phrasing as an unverified paraphrase, not a sourced quote.**

## 2. Matt Murphy's thesis content

Murphy's keynote articulated the **connectivity-as-AI-bottleneck thesis** in his own remarks (source: ServeTheHome live coverage; reported wording):

- **The bottleneck has moved from compute → memory → connectivity.** *"The next major innovation will instead be connectivity. And particularly the switch over from electrical to optical connectivity."*
- **The "copper wall."** *"200G per lane will be the last generation where copper is sufficient."* As bandwidth demand grows, the copper-viability distance shrinks, forcing the optical transition. (Digitimes rendered a related framing as *"the copper wall is moving inside the rack, and co-packaged optics is the only way through"* — headline-level, paywalled body.)
- **Marvell's neutral-supplier positioning.** *"We are the Switzerland of the industry. We work with everybody."* Murphy noted Marvell now derives **~75% of revenue from data centers** (consistent with the 76% in the 1Q27 note) and spans connectivity across every distance — die-to-die, intra-rack, inter-rack, inter-datacenter.
- **Co-packaged optics (CPO) as the enabler.** Traditional pluggable optics can't meet density/power constraints at scale — *"You won't have enough power or enough space."* A size comparison showed CPO-based 100T switches as *"vastly smaller"* than traditional builds. Murphy stressed it is operational now: *"This isn't some futuristic thing. It's happening now."*

**Product / roadmap announcements at the keynote (ServeTheHome):**
- **T100 "Teralink" switch** — a 100-Terabit switch for in-datacenter scale-out. ⚠️ *Possible relationship to prior note:* the 1Q27 note (`notes/MRVL/20260528-1Q27.md`) cited a *"102.4 Tbps AI/cloud switch announced 2026-06-01."* T100 Teralink (100T) is plausibly the productized name of that same switch family, but the sources do **not** confirm identity — flag, do not assert.
- **COLORZ 1600** — Marvell's **4th-generation silicon photonics**, coherent modulation for long-haul DCI (hundreds-to-thousands of km). Aligns with the 1Q27 DCI-doubling roadmap ($500M FY26 → $1B FY28).

## 3. Jensen Huang's remarks (during guest appearance)

Reported wording; **summary rendering, see Fidelity note.**

- **The "next trillion-dollar" framing**, delivered after Murphy's presentation: *"The next trillion-dollar company, ladies and gentlemen."*
- **Why connectivity makes Marvell essential** — note the **two summary renderings of the same remark** (illustrates the fidelity gap; neither is exact-quotable):
  - Yahoo/WebSearch rendering: *"When you take a computing challenge, and you break it down into numerous components, distributing it throughout the entire data center, connectivity becomes crucial. This is why Matt is performing so well, and why Marvell is so vital."*
  - Earlier Yahoo rendering of the same passage: *"That's the reason why Matt's doing so well. That's the reason why Marvell is so essential."*
- **Agentic AI drives connectivity demand** — Jensen tied agent workloads' *"disaggregated nature"* to rising networking demand across distributed compute (ServeTheHome).
- **Copper/optics pragmatism** — *"Optics where you must, copper where you can."* NVIDIA continues to use copper for scale-up (~2.5–7 m) and optics for longer spans (ServeTheHome). This is notable: NVDA's own framing endorses the copper-wall/optical-transition thesis that anchors Murphy's keynote — i.e. the two CEOs are narrating the **same** connectivity-bottleneck story from both sides of the partnership.
- **Strategic positioning read:** Jensen anchoring the partnership publicly at Computex reframes Marvell from *silicon-displacement threat* (custom XPUs let hyperscalers reduce GPU dependence) to *ecosystem participant* via NVLink Fusion — the "soft ecosystem lock-in / toll booth" read appears in third-party commentary (Tom's Hardware, TheNextWeb headlines surfaced in search; not ingested in body — flagged as external interpretation, not source fact).

## 4. Investment + partnership details

**$2B NVIDIA investment** (source: NVIDIA newsroom 2026-03-31 release, verbatim): *"In addition, NVIDIA has invested $2 billion in Marvell."* No structure, stake %, or conditions disclosed in any accessible source. WebSearch context (not in body sources): reported as NVIDIA's second $2B investment of 2026 (the first being CoreWeave in January) — corroborating, treat as background.

**NVLink Fusion role split** (source: NVIDIA newsroom, near-verbatim):
- **Marvell provides:** custom XPUs; NVLink Fusion-compatible scale-up networking; silicon photonics technology.
- **NVIDIA provides:** Vera CPU; ConnectX NICs; BlueField DPUs; NVLink interconnect; Spectrum-X switches; rack-scale AI compute; supply-chain/ecosystem access.
- **Jensen (release quote):** *"Together with Marvell, we are enabling customers to leverage NVIDIA's AI infrastructure ecosystem and scale to build specialized AI compute."*
- **Murphy (release quote):** *"By connecting Marvell's leadership in high-performance analog, optical DSP, silicon photonics and custom silicon to NVIDIA's expanding AI ecosystem through NVLink Fusion, we are enabling customers to build scalable, efficient AI infrastructure."*

**Cross-partner mentions:** the partnership also names silicon-photonics collaboration (per WebSearch on the release). No other named third-party partners surfaced in the keynote coverage.

## 5. Market reaction

- **MRVL stock:** premarket/overnight surge reported across a **range that varies by source** — *+17%* (Yahoo "MRVL stock ripping overnight"), *+20%* (Benzinga), *~+25%* (CNBC/Yahoo lead article), with one trending figure of *+29%*. ⚠️ The spread reflects different snapshot times (overnight vs. premarket peak), not a factual disagreement. **By June 2 close, +14%** (already captured in yesterday's morning scoring update). The widely-quoted "+20–25% premarket" sits inside this range.
- **Sell-side:** no specific analyst rating/PT actions captured in accessible coverage.

## 6. Cross-ticker signal extraction (for synthesis cross-reading)

- **NVDA:** $2B investment + NVLink Fusion role split + Jensen's public endorsement at Computex. Relevant to NVDA's competitive-position narrative (custom-silicon participation, not displacement) and supply-chain edge. Note Jensen's *"optics where you must, copper where you can"* echoes the June 1 GTC "largest networking company" claim — NVDA is narrating connectivity leadership on both event days. The MRVL→NVDA manual supply-chain edge already exists; this note quantifies the equity at **$2B** and dates it **2026-03-31**.
- **AVGO:** implicit competitive read — Murphy's "Switzerland of the industry / we work with everybody" is a direct contrast to AVGO's deeper single-customer custom-silicon entanglements (e.g. Google TPU). MRVL's neutral-multi-customer framing is the competitive wedge. No AVGO named in coverage (inference flagged, not source fact).
- **ANET / COHR / LITE / CRDO:** the connectivity-bottleneck + copper-wall + CPO thesis cross-validates the broader AI-connectivity sub-sector. Murphy's *"200G per lane is the last copper generation"* and CPO emphasis are the same axis CRDO's 3Q26 note (2026-06-02) confirmed from the PAM4/AEC side. COLORZ 1600 (coherent DCI) reads through to COHR/LITE coherent-optics franchises. **Cross-validation, not new competitive delta** — the sub-sector is accelerating together.

## 7. Operator-relevant observations

- **MRVL scoring implication — the $2B anchor.** The current MRVL scoring / `supply-chain-manual.yaml` MRVL→NVDA edge references *"NVDA direct equity investment in MRVL"* **without a figure**; the synthesis (`synthesis-20260602-run1.md`) likewise carries the partnership unquantified. This note supplies the verified number — **$2 billion, announced 2026-03-31** — which anchors the NVDA relationship at a concrete scale. **Filed as a follow-up: refresh the MRVL scoring / manual supply-chain edge with the $2B figure + 2026-03-31 date.**
- **Honesty check on the workstream's premise.** Yesterday's framing treated the $2B as a Computex-announced datapoint; sources show it was a **March 31 announcement reiterated at Computex.** Computex's genuinely new contribution is (a) Jensen's public "trillion-dollar" endorsement and (b) Murphy's articulated connectivity-bottleneck thesis + T100 Teralink / COLORZ 1600 product reveals — not the investment itself.
- **Unverified claim to retire.** "Preferred custom silicon partner" is not in any accessible source — avoid carrying it forward as a sourced quote in scoring; use the verified NVLink Fusion role-split language instead.
- **Forward catalysts implied:** T100 Teralink / COLORZ 1600 ship timing (not dated in coverage); CPO transition ("happening now"); the Photonic Fabric scale-up revenue conversion (Q4 FY28 $500M run rate per 1Q27 note) remains the next genuine score-moving event.

## 8. Sourcing & coverage gaps

- **Primary (accessible):** Yahoo Finance (full body); ServeTheHome live coverage (richest structural source for Murphy remarks + products); NVIDIA newsroom 2026-03-31 release (partnership roles + $2B verbatim); WebSearch corroboration (Tom's Hardware, optics.org, Benzinga, TradingKey — background only).
- **Designated-but-limited:** Digitimes — **paywalled**, headline + one related headline only. CNBC + HPCwire — **HTTP 403, not directly fetched**; content reaches this note secondhand via Yahoo (cites CNBC) and search snippets.
- **Known gaps:** no verbatim-quotable text (summary fidelity); investment structure/terms beyond $2B undisclosed; T100-Teralink-vs-102.4Tbps-switch identity unconfirmed; "preferred custom silicon partner" phrasing unverified (likely paraphrase); exact close-day move (+14%) sourced from prior scoring, not re-derived here; no sell-side detail. Proper transcript-fidelity re-ingest filed as next-session work.
