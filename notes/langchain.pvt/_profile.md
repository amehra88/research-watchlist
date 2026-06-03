# LangChain — private driver profile

- **pvt_id:** `langchain.pvt`
- **Display name:** LangChain
- **Aliases:** LangChain · LangChain Inc. · LangGraph
- **Added:** 2026-06-02
- **Type:** Standing profile (not an earnings note). Privates have no public filings;
  this dir holds blog/news/conference synthesis and read-through notes.

> **Sourcing:** Unlike the config-only privates, this profile incorporates external
> research (web + PitchBook), with figures flagged by verification status in the
> table below. Anchor name for the `agent_framework_landscape` theme.

## Why it's tracked

The adoption leader of the **open-source orchestration-framework layer** — the
build-your-own-agent plumbing that sits above the model. Operator's anchor name for
`agent_framework_landscape`. Repositioned around "agent engineering": **LangGraph** is
the durable agent runtime (graph-based state, checkpoints, human-in-the-loop), and
**LangSmith** is the commercial engine (observability / eval / tracing). The framework
primitives are commoditizing across vendors (LangGraph, OpenAI Agents SDK, Google ADK,
AWS Strands all converging); LangChain's durable edge is the LangSmith eval/observability
flywheel + distribution, not the orchestration primitives themselves.

## Read-through to public names (`affects`)

NET · GOOGL · NBIS

Competes for the orchestration layer above the model with edge platforms (**NET**),
hyperscaler agent stacks (**GOOGL** Antigravity/ADK), and neo-cloud hosting (**NBIS**).
LangSmith observability sits in the same category as **DDOG** (public) and Langfuse/Arize
(private).

## Key figures — verification status

| Metric | Value (secondary) | Source | PitchBook status |
|--------|-------------------|--------|------------------|
| Last round | Series B, $125M | Fortune, LangChain blog (Oct 2025) | ⏳ pending |
| Post-money valuation | $1.25B | Fortune / SiliconANGLE (Oct 2025) | ⏳ pending |
| Total raised | $260M over 4 rounds | Tracxn | ⏳ pending |
| ARR | ~$12–16M mid-2025 ("low for where we are today" per co.) | TechCrunch / getlatka | ⏳ pending |
| LangSmith trace volume | 12× YoY | LangChain blog | n/a (operational) |
| Founded / founder | 2022, Harrison Chase | — | ⏳ pending |

Lead/notable investors (secondary): IVP (Series B lead); Sequoia, Benchmark (existing);
CapitalG, Sapphire, ServiceNow Ventures, Workday Ventures, Cisco Investments, Datadog,
Databricks (new in Series B). — ⏳ pending PitchBook investor list.

> IPO: "IPO by 2026" has been floated in secondary press but is **unconfirmed**. Track.

## Adoption signals

- LangGraph: ~34.5M monthly downloads; 24.8k+ GitHub stars (since 2024 release).
- LangGraph Platform: ~400 production deployments incl. Cisco, Uber, LinkedIn,
  BlackRock, JPMorgan (secondary-sourced).
- Architecturally stronger than the original LangChain `AgentExecutor` for complex
  agentic patterns (tool loops, conditional routing, human-in-the-loop checkpoints).

## Competitive set (agent_framework_landscape)

- **Orchestration frameworks:** OpenAI Agents SDK (~10.3M downloads, OpenAI-tethered),
  Google ADK (multimodal leader), CrewAI (44k+ stars but ~3× tokens/latency),
  Pydantic AI (type-tight, winning Python-backend teams).
- **Hyperscaler-native:** AWS Bedrock AgentCore/Strands, Google Vertex Agent Builder,
  MSFT Azure AI Foundry / Copilot Studio.
- **Observability adjacency:** LangSmith vs Langfuse / Arize (private) vs DDOG (public).

## Related

- Sector landscape: `notes/sector/20260603-agentic-framework-harness-landscape.md`
- Sibling new privates: `cognition.pvt`, `sierra.pvt`, `decagon.pvt`
- Theme: `agent_framework_landscape` (config/watchlist.yaml)
