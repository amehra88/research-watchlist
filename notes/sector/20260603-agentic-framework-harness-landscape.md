# Agentic Framework / Harness Landscape: Who Are the Best-of-Breed Leaders?
**Sector/Theme:** `agent_framework_landscape` — the orchestration, harness, and runtime layer that sits *above the model* and turns frontier LLMs into deployable agents (build-your-own frameworks, coding-agent harnesses, hyperscaler agent platforms, enterprise vertical-agent platforms, and the interop-protocol layer).
**Angle:** Operator wants the best-of-breed leaders in agentic frameworks/harnesses **wherever they sit** — public, private, embedded in a hyperscaler, or inside a frontier lab — not just the names that happen to be public. LangChain is the anchor name of interest. Central tension: best-of-breed is overwhelmingly **private or embedded**, so listed exposure is almost entirely a read-through.
**Prepared by:** market-researcher | 2026-06-03
**Sourcing note:** Several ARR/valuation figures lean on secondary/blog sources (flagged inline). Better-sourced items (LangChain Series B, Sierra raise) cite TechCrunch/Fortune/CNBC. Treat single-blog figures as directional until verified against PitchBook/primary press. Cursor→SpaceX item is an **operator-private signal** (non-public, unverified).

---

## Executive Summary

- The agent stack has split into five distinguishable layers, each with a different best-of-breed leader and a different investability profile: (1) **open-source orchestration frameworks**, (2) **coding-agent harnesses**, (3) **hyperscaler-native agent platforms**, (4) **enterprise vertical-agent platforms**, (5) the **interop-protocol layer**.
- **LangChain/LangGraph is the adoption leader of the orchestration-framework layer** (~34.5M monthly LangGraph downloads; ~400 production deployments on LangGraph Platform incl. Cisco, Uber, LinkedIn, BlackRock, JPMorgan). Repositioned around "agent engineering": LangGraph = durable runtime, **LangSmith = the commercial engine** (observability/eval; trace volume 12x YoY). $1.25B val, $125M Series B (Oct 2025). Private; "IPO by 2026" floated but unconfirmed.
- **The investability problem is the headline:** there is essentially **no public pure-play** in the framework/harness layer. Leaders are private (LangChain, Cursor/Anysphere, Cognition, Sierra, Decagon) or embedded in a giant (Claude Code→Anthropic, Codex→OpenAI, Antigravity→GOOGL, Copilot→MSFT, AgentCore→AMZN). Listed exposure = read-through only.
- Architectures are **converging** (tools + reasoning loop + memory + guardrails), so the durable moat is shifting to **runtime + observability + distribution** — exactly where LangChain (LangSmith), the hyperscalers (distribution), and the protocol owners (Anthropic/MCP, Google/A2A) are positioned.
- **Ideas / tracking shortlist:** Anchor private = **LangChain**. Add private drivers **Cognition** (Devin+Windsurf), **Sierra**, **Decagon**. Public read-throughs tagged `agent_framework_landscape`: **GOOGL, MSFT, AMZN, NET, NOW, PLTR, DDOG**. Watch item: **Cursor/Anysphere → SpaceX/SPCX** acquisition (operator signal).

---

## The Five Layers

### 1. Open-source orchestration frameworks — *where LangChain sits*
The build-your-own-agent plumbing. **Leader: LangChain/LangGraph.**

| Name | Where it sits | Read | Investable? |
|---|---|---|---|
| **LangChain / LangGraph** | Private ($1.25B) | **Adoption leader.** LangGraph = graph-based durable runtime (state, checkpoints, human-in-loop); LangSmith = observability/eval commercial engine. ~$16M+ ARR, trace volume 12x YoY. Backers incl. IVP, Sequoia, Benchmark, CapitalG, ServiceNow, Workday, Cisco, Datadog, Databricks. | Private — `langchain.pvt` |
| **OpenAI Agents SDK** | Inside OpenAI | ~10.3M downloads, lightweight, OpenAI-tethered; tracing + guardrails | Embedded (`openai.pvt`) |
| **Google ADK** | Inside GOOGL | Strongest for multimodal (video/voice/image/text) agents; enterprise-grade | GOOGL |
| **CrewAI** | Private | 44k+ GitHub stars, role-play multi-agent; but ~3x token use / latency vs LangGraph | Private (not yet tracked) |
| **Pydantic AI** | OSS / private | Type-tight; winning Python-backend teams off LangGraph | Private (not tracked) |
| AutoGen/AG2, LlamaIndex, Mastra, Smolagents | OSS | Secondary in enterprise share | — |

**Read:** all converging architecturally → LangChain's edge is the LangSmith observability/eval flywheel + distribution, not the framework primitives themselves.

### 2. Coding-agent harnesses — *the "harness" layer proper*
Where the word *harness* bites hardest. No single winner; three best-of-breed, all private or embedded.

| Name | Where it sits | Read |
|---|---|---|
| **Claude Code** | Anthropic (`anthropic.pvt`) | Widely cited strongest harness; ~$2.5B annualized run-rate (blog-sourced) |
| **Cursor / Anysphere** | Private (~$1.2B ARR) | Best-of-breed IDE coding agent. **OPERATOR SIGNAL: agreement to be acquired by SpaceX/SPCX, expected ≤12mo (non-public, unverified)** → routes into post-IPO SPCX, not a standalone .pvt |
| **Cognition (Devin + Windsurf)** | Private (~$10.2B, ~$150M ARR) | Acquired Windsurf/Codeium; Windsurf 2.0 (Apr 2026) unified one harness across editor/terminal/cloud — cleanest "same harness everywhere" story. `cognition.pvt` |
| OpenAI Codex | Inside OpenAI | `openai.pvt` |
| Google Antigravity 2.0 | Inside GOOGL | GOOGL |
| GitHub Copilot (agent mode) | Inside MSFT | MSFT |
| Kiro | Inside AWS | AMZN |

### 3. Hyperscaler-native agent platforms — *framework sits inside the cloud*
The framework is a managed service; distribution is the moat.

- **Microsoft (MSFT):** Agent 365 + Azure AI Foundry Agent Service + Copilot Studio + AutoGen/Agent Framework. Explicitly building the enterprise "orchestration fabric"; leans into MCP + A2A interop. Identity via Entra ID is the structural lock-in.
- **Google (GOOGL):** Vertex AI Agent Builder / ADK / Antigravity / Gemini Enterprise — the full-stack bet against OpenAI + Anthropic.
- **Amazon (AMZN):** Bedrock AgentCore + **Strands** ("bring any framework") + Kiro. Managed, model-agnostic.

### 4. Enterprise vertical-agent platforms — *application/harness layer*
Packaged agents for a business function (customer support first).

- **Sierra** (private, `sierra.pvt`): best-of-breed customer-agent platform. Bret Taylor + Clay Bavor; **~$15B val, $950M raise May 2026, $150M+ ARR, >40% of Fortune 50.**
- **Decagon** (private, `decagon.pvt`): the principal direct Sierra competitor in autonomous customer support.
- **Public proxies:** Salesforce **Agentforce** ($540M ARR, 18.5k customers — CRM, *not in watchlist*); **ServiceNow** AI Control Tower (NOW); **Palantir** ontology-driven, deterministic/high-trust agents (PLTR). Also UiPath, SAP, Oracle, IBM.

### 5. Interop-protocol layer — *the connective tissue*
- **MCP (Anthropic)** and **A2A (Google)** are now the de-facto interop standards everyone embeds. Not directly investable, but **owning the protocol is the quiet land-grab** — a strategic-moat signal for `anthropic.pvt` and GOOGL. Observability adjacency: LangSmith vs Langfuse/Arize (private) vs **Datadog (DDOG, public)**.

---

## Investability Map (where listed exposure actually exists)

| Public ticker | In watchlist | Agentic-framework/harness exposure |
|---|---|---|
| **GOOGL** | ✓ | ADK, Antigravity, Vertex Agent Builder, Gemini Enterprise; A2A protocol owner |
| **MSFT** | ✓ | Copilot Studio, Agent 365, Azure AI Foundry, GitHub Copilot; MCP+A2A embrace |
| **AMZN** | ✓ | Bedrock AgentCore, Strands, Kiro |
| **NET** | ✓ | Edge agent runtime; orchestration-at-edge competitor to the framework layer |
| **NOW** | ✓ | AI Control Tower digital-labor orchestration; competes w/ Sierra/Decagon |
| **PLTR** | ✓ | Ontology-driven deterministic agent execution |
| **DDOG** | ✓ | Agent observability (LangSmith/Langfuse/Arize category) |
| CRM | ✗ (not in 147) | Agentforce ($540M ARR) — candidate add if vertical-agent exposure is wanted |
| NBIS | ✓ (infra theme only) | Neocloud compute substrate; **not** tagged here (infra, not framework) — judgment call, revisit |

**Private drivers (`.pvt`) for this theme:** `langchain.pvt` (anchor), `cognition.pvt`, `sierra.pvt`, `decagon.pvt`. Cursor/Anysphere intentionally **not** a standalone .pvt — folds into SPCX on the rumored SpaceX acquisition.

---

## Key Risks / What Would Change the Map
- **Convergence commoditizes the framework layer** → value migrates to whoever owns distribution (hyperscalers) or the eval/observability flywheel (LangSmith, DDOG). A standalone OSS framework without a runtime business is the weakest position.
- **Frontier labs absorbing the harness** (Claude Code, Codex, Antigravity) could starve independent framework adoption — the embedded harness is "free" with the model.
- **Protocol standardization (MCP/A2A)** lowers switching costs *between* frameworks — good for buyers, compresses framework lock-in.
- **Cursor→SpaceX** (if confirmed) removes the strongest independent coding-agent harness from the open market and concentrates it in a pre-IPO/newly-public mega-cap.

---

## Open Follow-ups
- Verify single-blog ARR/val figures (Cursor $1.2B, Claude Code $2.5B, Cognition $10.2B/$150M) against PitchBook / primary press before they harden into thesis inputs.
- Supply-chain edges for the new .pvts (deferred): cognition→MSFT/GOOGL [competitor]; sierra/decagon→NOW [competitor]; langchain→NET/NBIS [orchestration-layer competition / partnership].
- Confirm Cursor→SPCX agreement; on close, fold into the post-IPO SPCX entry.
- Decide whether to add **CRM** to the 147 to capture Agentforce as the cleanest listed vertical-agent pure-play.
- Seed `notes/langchain.pvt/_profile.md`, `notes/cognition.pvt/`, `notes/sierra.pvt/`, `notes/decagon.pvt/` profile docs.
