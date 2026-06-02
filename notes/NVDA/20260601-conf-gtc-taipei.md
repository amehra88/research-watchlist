---
ticker: NVDA
primary_ticker: NVDA
subject_tickers:
  - NVDA
period: conference-2026-06-01
event_date: "2026-06-01"
doc_type: conference_summary
event_type: keynote
event_name: NVIDIA GTC Taipei 2026 (Computex)
event_location: Taipei, Taiwan
speakers:
  - name: Jensen Huang
    title: CEO and Founder, NVIDIA
transcript_provider: singjupost.com
source_url: https://singjupost.com/nvidia-gtc-taipei-2026-keynote-w-ceo-jensen-huang-transcript/
cross_reference_urls:
  - https://semiconalpha.substack.com/p/nvidia-keynote-computex-2026-key
  - https://www.servethehome.com/nvidia-computex-2026-keynote-live-coverage/
ingestion_date: "2026-06-02"
extraction_source: "WebFetch multi-query extraction via Claude Code session 2026-06-02. NOT verbatim transcript — content is paraphrased summary across multiple targeted extraction queries against Singju Post (primary) + Semicon Alpha + ServeTheHome (cross-reference). Future synthesis agents should treat as summary coverage, not quotable verbatim source."
---

# NVIDIA GTC Taipei 2026 Keynote — June 1, 2026

_Multi-query WebFetch summary ingested 2026-06-02 (Claude Code session). Jensen Huang keynote at Computex Taipei, ~2 hours. Sources: Singju Post (primary transcript), Semicon Alpha (analyst framing, paywalled — limited), ServeTheHome (live-coverage structural specifics)._

## Fidelity note

This note is a **multi-query WebFetch summary, NOT a verbatim transcript ingest.** Content captures structural announcements, named entities, and thesis framing with reasonable fidelity, but it sits **two layers of summarization** between Singju Post's verbatim transcript and this note (WebFetch passes each page through a summarization model, and answers a per-query prompt rather than returning raw text). **Quoted wording below is the summary's rendering and should not be treated as exactly quotable** — for verbatim quotes or precise wording, refer to the source URLs in frontmatter. A future ingest cycle should re-pull this keynote via a proper transcript-fidelity path (FactSet_UnstructuredContent semantic query on Computex 2026, or direct HTML parse of Singju Post) — **filed as next-session work.** Cross-source discrepancies are flagged inline below where the three sources disagree.

## 1. Headline announcements

- **Vera Rubin in full production** (as of the keynote). Multi-rack AI supercomputer: NVL72 inference GPU; Vera CPU rack; Grok/Groq LPX inference tier; BlueField 4 (storage/security); Spectrum-X Ethernet Photonics with 200Gb co-packaged optics. Assembly time cut "from two hours to five minutes" per Grace-Blackwell-class rack. "No cables in a Vera Rubin compute tray."
- **Vera CPU** — "CPU built for the age of AI." ⚠️ *Cross-source discrepancy on core count:* Singju Post reports **88 "Olympus" cores** (monolithic mesh, ~10 IPC, 3.6TB/s cross-sectional fabric, LPDDR5X 1.2TB/s, "40% lower peak memory latency vs x86"); ServeTheHome reports **20 cores** with "highest IPC in the world," "1.8x agentic performance of x86," "3x faster SQL," reticle-limit "no chiplet tax." The 20-core figure may be a conflation with the RTX Spark CPU (below); treat exact Vera CPU core count as **unconfirmed pending verbatim source.**
- **NVDA PC entry — RTX Spark (N1X architecture).** TSMC 3nm, ~70B transistors, 20-core Grace CPU co-developed with MediaTek, 6,144 CUDA cores (~1 petaflop), 128GB unified memory. Framed as "reinventing the PC for the first time in 40 years." Forms: laptop (fall availability), desktop (MSI reference shown), workstation; DGX Station for Windows. **Microsoft partnership** — joint Jensen + Satya Nadella presentation scheduled for the following evening (June 2). PC roadmap: Vera Rubin Spark (2028), Rosa Feynman Spark (2030).
- **DSX AI Factory Platform.** DSXSim (Omniverse blueprint for digital-twin validation), DSX OS (provisioning/monitoring), DSX Max LPS (power optimization; 45°C hot liquid cooling), DSX FLEX (grid-cooperative dynamic power allocation). Framing: "a gigawatt of AI infrastructure will reach $100 billion… no room for error."
- **CUDA-X libraries positioned as agent tools:** CULITHO (lithography), CUOPT (optimization), cuDSS (sparse solvers), AIQ (document analysis), Aerial (AI-RAN), Warp (differentiable physics), Parabricks (genomics).
- **Open models / physical AI:** Nemotron 3 Ultra (open; "5x faster," "30% cheaper," hybrid SSM + MoE); Nemotron 4 (in development); Cosmos 3 (physical-AI foundation model); Alpamayo 2 ("world's first reasoning autonomous vehicle," on Drive Hyperion); Isaac GR00T (humanoid reference platform, Jetson Thor compute, Unitree body).
- **Networking:** ConnectX-9 SuperNICs, BlueField 4 DPUs, Spectrum-X Ethernet switches, NVLink switch trays. Claim: **"NVIDIA is now the largest networking company in the world."**
- **Marvell:** NOT announced in this keynote — see §3 for the separate June 2 event.

## 2. Thesis-relevant content for the NVDA story

- **"Compute is revenue" narrative (the central thesis).** Reported wording: *"Compute is revenue now. Compute is profit… Every token is profitable. Every token is revenues. Tokens per watt… Performance per watt is your revenues."* And: *"agentic AI has arrived… useful AI has arrived. AI is now a profit generator. AI is now a GDP generator."* This is the keynote's defensive spine against AI-capex-bubble framing — recasting AI infrastructure spend as directly revenue-generating.
- **AI-bubble / jobs pushback.** *"People talk about AI reducing jobs — complete nonsense. It's causing more software engineers to be hired."* GitHub-productivity argument: ~30M developers ≈ $3T GDP, now ~3x output → *"effectively $9 trillion of productivity from $3 trillion of salaries."*
- **Full-stack as the answer to merchant/custom silicon (implicit, no competitor named).** *"Choosing the wrong architecture just because the chips are cheaper doesn't make sense. You need to make sure your revenues per watt — the more you buy, the more you make."* Plus a longevity/flexibility argument: software advances every few months, so an inflexible architecture has unpredictable useful life ("I can [predict how long my system lasts]"). Emphasis on "extreme co-design" across GPU + CPU + networking + storage. No explicit naming of AVGO/AMD/TPU competitors detected.
- **Roadmap / production visibility:** Vera Rubin in full production now; RTX Spark fall availability; PC roadmap to 2030 (Vera Rubin Spark 2028, Rosa Feynman Spark 2030).

## 3. Cross-ticker signal extraction

- **MRVL — NOT in this keynote.** ⚠️ The widely-cited Jensen *"next trillion dollar company"* endorsement of Marvell came from a **separate event on June 2, 2026**: Jensen made a ~10-minute surprise guest appearance at **Marvell CEO Matt Murphy's own Computex keynote**. Reported context: Marvell's networking/connectivity silicon as essential to distributed data-center compute; building on the March 2026 NVDA-MRVL partnership; **NVIDIA's ~$2B investment in Marvell**; NVLink Fusion positioning Marvell as "preferred custom silicon partner." MRVL stock +~20-25% premarket June 2. **This warrants a separate note** — `notes/MRVL/20260602-conf-computex-murphy.md` — filed as next-session work; it is out of scope for this June 1 NVDA keynote artifact. (Sources: Digitimes, CNBC, HPCwire, Yahoo Finance — see also supply-chain-manual.yaml MRVL→NVDA partnership.)
- **TSM** — foundry for Vera CPU and RTX Spark (3nm); manufacturing partners Foxconn, Quanta, MediaTek; "150 supply-chain partners across Taiwan." No foundry-constraint commentary surfaced.
- **AVGO / AMD / TPU** — no explicit competitive naming in the keynote; competitive positioning is implicit via the "wrong architecture / cheaper chips" custom-silicon pushback (§2).
- **Private drivers (Vera CPU early adopters):** **OpenAI, Anthropic, SpaceX** named as Vera CPU early adopters (ServeTheHome). Relevant to `notes/openai.pvt/`, `notes/anthropic.pvt/`, and the SpaceX/SPCX driver.
- **Cramer's ARM/ORCL/NBIS/CRWV "keynote winners" framing** — NOT verifiable from accessible sources (Semicon Alpha paywalled; not present in Singju/ServeTheHome). Not captured; flag for a dedicated source if this framing matters.

## 4. Reported quotes worth preserving (summary rendering — see Fidelity note)

> "Compute is revenue now. Compute is profit… Every token is profitable. Every token is revenues."

> "agentic AI has arrived… AI is now a profit generator. AI is now a GDP generator."

> "Choosing the wrong architecture just because the chips are cheaper doesn't make sense. You need to make sure your revenues per watt — the more you buy, the more you make."

> "People talk about AI reducing jobs — complete nonsense. It's causing more software engineers to be hired."

> "NVIDIA is now the largest networking company in the world."

## 5. Operator-relevant observations

- **Competitive position (anchor 5/5/5):** Reinforces, does not move. The keynote is a maximal full-stack assertion — GPU + Vera CPU + networking ("largest networking company") + DSX factory platform + open models — and an explicit narrative defense ("compute is revenue") against both the AI-capex-bubble thesis and the merchant/custom-silicon-displacement thesis. Consistent with the standing read; nothing here is inconsistent with the 5/5/5 holding. (Note the networking-leadership claim sits adjacent to the MRVL/CRDO/ANET connectivity-as-bottleneck axis.)
- **Investor interest (anchor 4, 4→4+ live):** Supportive — agentic-AI-monetization + "compute is revenue" is exactly the narrative that sustains momentum into the 2026-08-26 Q2'27 print.
- **Forward catalysts implied:** Vera Rubin in full production; RTX Spark fall availability; June 2 joint Microsoft (Nadella) PC event; next earnings 2026-08-26.
- **Risks/hedges:** No explicit competitive-threat acknowledgment in the keynote (all-offense framing). Customer-concentration not addressed. The merchant/custom-silicon pushback is rhetorical, not data-backed in the accessible content.

## 6. Sourcing & coverage gaps

- **Primary:** Singju Post transcript (summarized via WebFetch) — appeared complete (ended on closing remarks).
- **Cross-reference:** ServeTheHome live coverage (structural specifics, generally consistent; the Vera CPU core-count discrepancy noted in §1). Semicon Alpha **paywalled** — only the agentic-AI headline takeaway was accessible.
- **Known gaps:** exact Vera CPU core count unconfirmed; no verbatim-quotable text (summary fidelity); Cramer "winners" framing unverified; MRVL June 2 event documented here by reference only (separate note pending).
