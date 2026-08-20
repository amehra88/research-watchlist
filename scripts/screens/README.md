# AI application-layer screens

Two quarterly EDGAR full-text scans over **every US filer** — not just the ~159 tickers in
`config/watchlist.yaml`. Built 2026-08-19.

| File | What it does |
|---|---|
| `edgar_ai_language_screen.py` | Scores filers on AI language weighted by **disclosure cost** (quantified AI revenue and inference-in-COGS at 5, proprietary model/data claims at 2–3, generic vocabulary at 1). 10-K + 10-Q. |
| `edgar_ai_officer_screen.py` | Finds companies that **named a senior AI officer** — Chief AI Officer, Head of AI, Chief Data & AI Officer — in an 8-K Item 5.02, DEF 14A, or 10-K. |
| `edgar_mcp_screen.py` | Finds companies making their corpus **agent-addressable** — "Model Context Protocol", "MCP server", "agent-ready". Shipping an MCP server means positioning proprietary data as application-layer substrate rather than defending a UI. |
| `cross_signal.py` | Intersects all three screens. **Read this first** — a name clearing 2+ independent thresholds is the real signal. |
| `diff_screens.py` | Diffs the two most recent runs of either screen and reports new entrants. |
| `run_ai_screens.sh` | Runs both, writes `docs/ai-screen-report-<date>.md`, prunes to the last 8 runs. |

## Run

```bash
scripts/screens/run_ai_screens.sh
```

Takes roughly 10–15 minutes (EDGAR is rate-limited to ~10 req/s and the scripts sleep between
pages). No API key required; EDGAR full-text search is public, but it requires a descriptive
User-Agent, which is set in each script.

## Why weight by disclosure cost

Calibration run, 10-K filings Jun 2025 – Aug 2026:

| Phrase | Hits | Verdict |
|---|---|---|
| "artificial intelligence" | 4,194 | ~60% of all filers — no information |
| "large language models" | 325 | vocabulary, not commitment |
| "proprietary datasets" | 65 | moderate |
| **"AI revenue"** | **5** | ~0.3% — near-perfect precision |
| "Model Context Protocol" | 26 | rare, and a deliberate architectural bet |

Almost every public company now says "AI". Almost none puts a number next to it in an audited
document. **Screen the rare tail.**

**Cost-side phrases are deliberately excluded.** "Inference costs" / "cost of AI" were removed
2026-08-20: what a company *sells* and what data it *owns* is the thesis; what it spends is not.

## Reading the output — three traps

1. **Phrase collisions.** Apartment REITs (MAA, CPT) hit "AI revenue" because they run *"AI revenue
   management"* pricing software. Always read the matched phrase in context.
2. **No size filter is built in.** The tail is full of sub-$50m shells with "AI" in the name, plus
   crypto miners repurposing sites into datacenters. Filter by market cap and business before
   treating a row as a candidate. This step cannot be automated away.
3. **The officer and MCP screens have poor recall.** SEC filings only name Section 16 officers, so a VP-level
   AI hire — often the more meaningful signal — is invisible (Welltower does not appear). MCP
   adoption likewise lives mostly in product docs and GitHub, not filings. High precision, low
   recall; never read an absence as evidence.

## Interpreting results

Use `skills/ai-application-layer-screen/SKILL.md` for the framework (archetype split, four tests,
negative screen, required per-name defense format). Worked analysis with 28 defended names lives in
`docs/ai-application-layer-screen.md`.

## Schedule

Quarterly via droplet cron, wrapped in `alert_on_failure.sh` per repo convention:

```
15 7 1 2,5,8,11 * /root/bin/alert_on_failure.sh ai_screens /root/research-watchlist/scripts/screens/run_ai_screens.sh
```
