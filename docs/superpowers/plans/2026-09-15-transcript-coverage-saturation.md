# Transcript coverage: we can reach ~95% on the entitlement we already have

**Date:** 2026-09-15
**Question:** we hold a median **56.9%** of the turns in each earnings call. Is that
a hard limit of the FactSet MCP — meaning we must buy the paid full-transcript
product — or an artefact of how we query it?

**Answer: an artefact. Measured, not argued.**

## What the MCP can and cannot do

Verified against FactSet's own docs (`developer.factset.com/mcp/factset-ai-ready-data-mcp`)
and the tool schema itself, not a summary:

- The MCP exposes **22 tools, none of which fetches a document.**
- The only text tool, `FactSet_UnstructuredContent`, is described by FactSet as
  *"Retrieve **vectorized** data from CallStreet Transcripts, StreetAccount News, and
  EDGAR Filings (10K/10Q/8K) from 2022-present."* A semantic index, not a document store.
- `query` is required and must be natural language; there is no `documentID`
  parameter; `limit` caps at 50.

Full transcripts exist in a **separate paid product** — Documents Distributor —
CallStreet Events (Events and Transcripts API; verbatim XML, speakers, prepared-vs-Q&A).
Third-party pages claiming the MCP "returns full text with speaker attribution" are
describing the content set, not the tool.

So whole-call export is genuinely impossible here. The question is how close we get
without it.

## The experiment

Within a single call — the only valid design, since a cross-sectional comparison
confounds query count with call length (longer calls attract more queries *and* have
more turns to miss). Fired 14 diverse probes at one call, deduped by `vectorId`,
measured turn coverage after each. Transport was the pipeline's own `fetch_page`, so
no payload passed through a model.

| queries | ANET 2026-08-04 (72 turns) | DDOG 2026-08-06 (106 turns) |
|---|---|---|
| corpus baseline | 27.7% | 27.6% |
| 1 | **65.3%** | **45.3%** |
| 2 | 70.8% | 54.7% |
| 4 | 86.1% | 67.0% |
| 8 | 93.1% | 73.6% |
| 11 | **95.8%** | 81.1% |
| 14 | 95.8% (saturated at q11) | **83.0%** |

## Two levers, and the first is the surprise

**1. The window matters more than the query count.** A single probe over a ±1-day
window returned **65.3%** — against a 27.7% baseline built from *four* probes over a
wider window. A call is ~52 chunks (p75 64) and a page holds 50, so a narrow window
lets one call very nearly fit in one page. A wide window makes the 50 slots compete
across several companies' calls.

**2. Diverse probes reach different regions.** The two cron queries are deliberately
generic ("what did analysts ask", "what did management say about results and
guidance"). Semantic search returns what is *near* the query, so two generic probes
keep hitting the same central mass. Probes aimed at margins, competition, capital
allocation, supply, pricing, headcount and regional performance each pull different
turns.

**3. Saturation is real and call-length dependent.** ANET flattened at 95.8% by q11
(q12–14 added nothing). DDOG, half again as long, was still creeping at q14. Longer
calls need more probes; the tail is not free.

## Consequence

**Documents Distributor is not needed for coverage.** ~83–96% is reachable on the
current entitlement, up from ~57%. It costs `claude -p` calls and wall-clock, not
FactSet money — roughly 12 probes per event instead of 2.

Recommended change to `scripts/v3_ingest/transcript_ingest.py`:

- Keep `EARNINGS_WINDOW_DAYS = 3` (already the right shape) and make sure the
  earnings path always uses the narrow window — that is most of the win.
- Replace the two generic `EARNINGS_QUERIES` with a diverse set of ~12.
- Re-measure the 56.9% figure afterwards and **report it as a metric**, not a vibe.

The residual 4–17% is the honest ceiling of a semantic index, and *that* is what the
paid product would buy. Worth revisiting only if a measure needs true completeness —
the evasion signal (analyst question vs management answer) is the one that does,
since it needs both turns and today pairs on only 72% of analyst turns.

## Caveat carried forward

Coverage here means *interior* completeness — turns present between the first and last
we retrieved. Trailing turns never retrieved are structurally invisible to this
measure, the same flaw as `tmp/assemble_factset_transcript.py`'s gap test, which
reported TSM 2Q26 as complete while it was missing Q&A turns
`[8, 22, 51, 55, 63, 97, 107, 108, 109]`. Treat 95.8% as an upper bound on what we
can prove, not a guarantee.
