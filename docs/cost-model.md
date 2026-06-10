# Research System Cost Model

_Last updated: 2026-06-09. Update when costs change or new channels added._

## Monthly cost summary

| Category | Subcategory | ~Monthly cost | Notes |
|---|---|---|---|
| Infrastructure | DigitalOcean droplet (4GB / 2 vCPU / 80GB) | ~$24 | Post-resize 2026-06-09; was 2GB at ~$12 prior |
| Infrastructure | DigitalOcean Postgres (local on droplet) | $0 | Local install, not managed; included in droplet |
| Subscription | Claude Max 5x | $100 | Shared bucket: claude.ai chat + Claude Code + Cowork + claude -p calls |
| API — Anthropic | Pay-per-token (overage past Max 5x) | $0 today | Only kicks in if subscription bucket exhausted |
| API — Gemini | gemini-embedding-001 (chunking) | ~$0.50-2 | Variable: re-embedding on corpus changes |
| API — Gemini | Generation (if used) | $0 currently | Not currently in production pipeline |
| API — FactSet | MCP usage | $0 incremental | Per existing contract |
| API — Brevo | Transactional email (digests) | $0 | Free tier covers current volume |
| **Total fixed monthly** | | **~$124** | Subscription + droplet |
| **Total variable monthly** | | **~$0.50-2** | Gemini embeddings on changes |

## Cost provenance by component

### 1. Infrastructure

**DigitalOcean droplet:** $24/mo for 4GB / 2 vCPU / 80GB. Resized from 2GB on 2026-06-09 to host local Postgres + pgvector for chunking Step 5b. Resize was "CPU and RAM only" — reversible if Postgres pressure proves unnecessary.

**Postgres + pgvector:** $0 incremental. Installed locally on droplet via apt. Trade-off: operator owns Postgres ops (backups, restarts, OOM tuning). Alternative considered: Neon free tier (0.5GB, sufficient for current scale ~65MB), Neon paid ($19/mo), or DO managed Postgres ($15/mo).

### 2. Claude subscription (Max 5x, $100/mo)

**Shared bucket across:**
- claude.ai web chat
- Claude Code (CLI sessions)
- Cowork (if used)
- claude -p calls from pipelines (subscription auth)

**Current utilization profile:** Operator hits subscription limits occasionally (a few times a month), driven primarily by heavy Claude Code coding sessions. Background pipelines (synthesis runs, future v3 ingest) consume the rest of the bucket without crowding interactive work.

**Per-call subscription consumption:**
- Interactive Claude Code session: variable, can be intensive (~5-50K tokens/minute during active reasoning)
- claude -p batch call: ~29.7K cache-creation tokens fixed overhead + per-task tokens (measured 2026-06-09 on podcast extraction prototype)
- claude -p per-item call: ~$0.11 nominal value (subscription tokens), batched amortizes this overhead

**Why subscription is the right path for current pipeline LLM use:**
1. Already paid — marginal cost is zero unless bucket exhausted
2. Quality on edge cases (ambiguous classification, subsidiary mentions, indirect ticker references) generally better than Gemini Flash
3. Existing claude -p pattern in the codebase; no new SDK integration

**When to reconsider:**
- If coding sessions grow AND background pipelines grow AND interactive limits hit regularly (more than ~weekly during peak hours)
- If specific pipeline gets too heavy (e.g., adding v3 IR/8-K ingest at 100+ items/day on top of podcasts)

**Reversibility:** Pipeline LLM backend is a config flag swap — script architecture supports gemini-2.5-flash or claude -p interchangeably.

### 3. Gemini API (pay-per-token, ~$0.50-2/mo currently)

**gemini-embedding-001 (chunking):**
- Used for embedding notes corpus into pgvector
- Cost: ~$0.0001/embedding call at 3072-dim model
- Current corpus: 3,005 vectors. Re-embedding from scratch: ~$0.30 one-time
- Steady state: only new chunks embedded incrementally (each new note → ~5-30 chunks)
- Realistic monthly run-rate: ~$0.50-2/mo as corpus grows via v3 ingest

**Generation (not in production):**
- Available via google-genai SDK if needed
- Pricing reference:
  - gemini-2.5-flash: $0.30/M input, $2.50/M output
  - gemini-2.5-pro: $1.25/M input, $10/M output (under 200K context)
- Not currently used; documented for future reference

### 4. FactSet (MCP, $0 incremental)

**Per-contract usage:** Existing FactSet contract covers MCP usage. No per-call billing visible at this layer.

**Channels accessed:**
- ALL_NEWS (StreetAccount) — primary signal channel for v2 digest, primary channel for v3 ingest
- ALL_FILINGS (10-K/10-Q/8-K)
- ALL_TRANSCRIPTS (earnings calls)
- Estimates, fundamentals, supply chain, etc.

**Note:** FactSet MCP cost dynamics may change with usage scale; monitor if v3 ingest expands queries significantly.

### 5. Brevo (transactional email, $0)

**Current free tier:** Covers daily digest + news digest (legacy v1/v2) volume. ~2-4 emails/day operator-facing + occasional alerts.

**When to reconsider:** v3 architecture explicitly drops news digest emails; volume goes DOWN, not up. No paid tier expected.

## Architectural decisions that determine cost

**Decision: Local Postgres on droplet (2026-06-09)**
- Cost: $0 incremental (droplet upsize $12-18/mo to support)
- Alternative: Neon free tier ($0, smaller storage), Neon paid ($19/mo), DO managed Postgres ($15/mo)
- Reasoning: Keep stack-in-droplet ethos; operator accepts Postgres ops

**Decision: claude -p (subscription) for pipeline LLM use, not Gemini Flash (2026-06-09)**
- Cost: $0 incremental (within Max 5x subscription bucket)
- Alternative: Gemini 2.5 Flash direct API (~$2/mo)
- Reasoning: Subscription bucket has headroom; coding sessions are the bottleneck, not pipelines; quality marginally better

**Decision: gemini-embedding-001 for chunking (long-standing)**
- Cost: ~$0.50-2/mo
- Alternative: Self-hosted embedding model (free but slow); OpenAI text-embedding-3-large (~$0.13/M tokens, similar cost)
- Reasoning: 3072-dim quality, ties to existing Gemini API key, integrated with embed.py

**Decision: v3 ingest no daily email (2026-06-09)**
- Cost: $0 saved (Brevo was free anyway)
- Reasoning: Operator preference; query corpus via chunking/RAG instead

## Cost-significant tail risks

**1. Subscription bucket exhaustion:**
- Max 5x bucket exhaustion triggers usage credits (pay-as-you-go API rates) IF operator enables, OR throttling
- Current risk: medium during coding-heavy days; low otherwise
- Mitigation: Move heaviest pipelines to Gemini direct API if hits become regular

**2. Gemini API quota:**
- Operator's account has standard quotas
- Risk: low at current corpus size; growing with v3 ingest
- Mitigation: Monitor `embed.py` call frequency

**3. FactSet usage scale:**
- Per-contract; potential renegotiation if v3 ingest dramatically increases query volume
- Risk: low at current pace
- Mitigation: Cache aggressively (already partially in place); monitor MCP call patterns

**4. Droplet resize-back:**
- Resize to 4GB was reversible (CPU+RAM only). If Postgres pressure proves unnecessary, can scale back to 2GB and save $12-18/mo

## Update protocol

When any of these change, update this doc:
- New channel added to v3 ingest (FactSet/IR/8-K/Substack)
- LLM backend swapped (claude -p ↔ Gemini ↔ other)
- Infrastructure resize (droplet, Postgres tier)
- Subscription tier change
- Pricing changes from providers

Commit changes with message: "cost-model: <what changed>"

DO NOT include actual costs paid (those are in operator's billing dashboards). This doc describes the structural cost model, not the bills.
