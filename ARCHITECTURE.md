# Research Intelligence System — Architecture

_Living document. Current as of 2026-06-03. Complements `CLAUDE.md` (operational/agent-facing
instructions); this file is descriptive — what's built, why, and how it fits together._

## 1. System purpose

A single-operator research-intelligence system for **Ashim Mehra**, covering ~150 AI-infrastructure
tickers for the **BCTK ETF (Baron Capital Technology)**. It exists to hold **durable analytical
state** (scored conviction, primary-source notes, supply-chain relationships) that would otherwise
live only in an analyst's head, to **automatically surface** what's new (earnings, news, conferences),
and to **assist synthesis** via on-demand agents. The repo is the source of truth; the operator
curates, the automation feeds it, and agents read it.

Two git repos cooperate:
- **`/root/research-watchlist`** — canonical analytical state (this repo), synced to GitHub
  (`amehra88/research-watchlist`, private). Mac/iPad are **pull-only** clones.
- **`/root/research`** — sibling repo, **local-only (never pushed)**: holds operator-curated
  supply-chain edges, incoming raw transcripts, and some ingest scripts.

## 2. Core concepts

- **Tiers** (in `config/watchlist.yaml`):
  - **T1 (`tier_1_bctk`, 40)** — actual BCTK holdings. T1 = *ownership*, not conviction.
  - **T2 (`tier_2_active_candidates`, 18; 4 fully scored)** — high-interest unowned names; scored
    candidates for promotion.
  - **T3 (`tier_3_watchlist`, 91)** — watch list; mostly bare stubs (ticker + themes), no full scoring.
  - **`.pvt` private drivers (10)** — private companies that drive public theses (OpenAI, Anthropic,
    SpaceX, Moonshot, DeepSeek, Mistral, LangChain, …). Addressed like tickers via a `<name>.pvt`
    id; never enter the public news/earnings pipelines. On IPO, renamed in place to the real ticker
    and promoted to T1 (preserving pre-IPO history).
- **Scoring rubric** — **four** 1–5 scored axes, each allowing a `+` modifier (e.g. `4+`):
  `ai_positioning`, `competitive_advantage.innovation_rate`, `competitive_advantage.distribution`,
  and `potential_investor_interest`. `competitive_advantage.overall` is a **synthesis** of
  innovation_rate + distribution — not a separate 5th score. Plus `scoring_notes` + `scoring_date`.
  Example — **MRVL**: competitive_advantage `4+/4/4` (innovation_rate 4+, distribution 4, overall 4),
  potential_investor_interest `5`.
- **Themes** — controlled vocabulary (61 tags), category-keyed:
  `demand` (15) · `supply` (17) · `margins_pricing` (4) · `strategic` (21) · `macro_policy` (4).
  Stored as **bare name-strings** (no inline descriptions); definitions live in commit history /
  this doc. Assigned per-ticker as a tag list.
- **Supply-chain edges** (in the `research` repo) — directed relationships, `kind` ∈
  {supplier, customer, partnership, competitor}, `significance` ∈ {high, medium, low},
  `provenance` ∈ {manual, verified, extracted}.
- **`.pvt` registry invariant** — every `.pvt` id referenced in `supply-chain-manual.yaml` or
  `notes/` must resolve to a `private_drivers:` entry. Removing a `.pvt` requires retargeting any
  orphaned reference (e.g., today's `NVDA→xai.pvt` edge was retargeted to `NVDA→spacex.pvt` after
  `xai.pvt` was absorbed into `spacex.pvt`).
- **OPERATOR-PRIVATE SIGNAL** — the single canonical tag (uppercase, in `scoring_notes`) marking a
  score that reflects the operator's private view over public-data consensus. One tag, one semantic.
- **Notes** — per-ticker primary-source content at `notes/{TICKER}/`: earnings syntheses,
  conference summaries, analyst-meeting notes, and agent-generated `synthesis-*.md` runs.

## 3. Artifact layer

| Artifact | Repo | What it holds |
|---|---|---|
| `config/watchlist.yaml` | research-watchlist | Tiered entries, scoring, themes, `private_drivers`, `web_sources` — the analytical state |
| `notes/{TICKER}/` | research-watchlist | Primary-source content (`YYYYMMDD-{quarter}.md`, `-conf-{name}.md`) + agent syntheses |
| `notes/{pvt_id}/` | research-watchlist | Private-driver profiles (`_profile.md`) and blog/news content |
| `config/ticker_identity.yaml` | research-watchlist | News-digest scope (49): name ↔ ticker ↔ FactSet id + Google query |
| `config/news_sources.yaml` | research-watchlist | News-digest source-quality tiers + denylist |
| `config/supply-chain-manual.yaml` | research (local) | Operator-curated edges (high-signal, hand-authored) |
| `config/supply-chain.yaml` | research (local) | FactSet auto-extracted edges (~146-ticker coverage, mostly noise per Phase A audit — fallback, weighted below manual) |

## 4. Automation layer (cron, wrapped by `alert_on_failure.sh` → Brevo email on non-zero exit)

- **`earnings_reviewer`** (06:30 ET daily) — finds prior-day earnings among watchlist tickers via
  InsiderScore/FactSet MCP, drafts syntheses (`scripts/cron_earnings_reviewer.py` + agent).
- **`news_digest_premarket` (06:45 ET) / `news_digest_postmarket` (18:30 ET), Mon–Fri** — Phase C
  dual-source digest (see below); **BUILT + LIVE 2026-06-02**.
- **`sidecar_pdfs` / `enrich_sidecars`** (every 15 min, offset) — process operator-attached PDFs into
  notes with metadata sidecars.
- **`gmail_poller`** (every 15 min) — pulls emailed transcripts/notes; hands to the from-PDF wrapper
  (auto-trigger gap is open — see §8).
- **`auto_sync`** (every 15 min) — **commits and pushes any uncommitted `research-watchlist` changes.**
  Architecturally load-bearing: hand edits frequently **race** with the sweep and land in a generic
  `Auto-sync:` commit before a manual commit runs. **This race recurred ~6 times in the 2026-06-02
  session — the dominant commit-flow shape.** Working pattern: *write → may be swept → follow-up
  commit if needed, never rewrite pushed history* (Mac/iPad are pull-only and would be clobbered by a
  force-push).
- **`daily_digest` / `nport_*` / `watchlist_derive`** — adjacent pipelines (daily report email, NPORT
  weekly marks, BCTK-holdings derive) feeding/around the system.

### News digest (Phase C)
Dual-source over **49 tickers** (T1 + scored T2 + selected T3): **Google News RSS** (breadth) +
**FactSet ALL_NEWS** (quality/sentiment, called via `claude -p` + the FactSet MCP). Pipeline:
fetch → cluster (headline Jaccard ≥ 0.6) → classify HIGH/MEDIUM/DROP (volume, top-tier-source w/
relevance gate, FactSet in-both / sentiment) → 18h state-ledger de-dup → plain-text Brevo email.
Per-ticker isolation; degraded-coverage banners; rendered body persisted to a gitignored
`logs/news_digest_*.txt` audit artifact. Code: `scripts/news_digest.py` + `scripts/newsdigest/`.
**Thresholds are v1 — known tuning items are tracked in §8 (cluster embeddings, SEO patterns,
sentiment-only HIGH, MEDIUM volume), to revisit after ~1 week of live output.**

## 5. Agent layer

- **`ticker-synthesis` (v1.6)** — prompt at
  `plugins/agent-plugins/ticker-synthesis/agents/ticker-synthesis.md`. On-demand. Reads a ticker's
  `notes/`, its watchlist scoring block, and supply-chain edges, then writes
  `notes/{TICKER}/synthesis-YYYYMMDD-runN.md`: operator anchors, snapshot per dimension,
  direction-of-travel (leading vs lagging signals), most-important-change, coverage gaps.
  - **Cross-ticker rule (v1.6):** also deep-reads the scoring blocks of watchlisted partners reached
    via **operator-authored (manual/verified) partnership edges**, and records them in a required
    "Cross-ticker watchlist sources considered" line. FactSet-extracted edges are excluded (too noisy).
  - **Prompt history:** v1.0 baseline → … → v1.6 added the partnership-edge extension + coverage
    transparency line (validated via NVDA run 12). A v1.6.1 cosmetic fix (doubled considered-list
    label) is open.
  - **Phase 2 sources (deferred, see §8):** insider transactions, sell-side estimate revisions,
    podcasts, and direct FactSet fundamentals pulls are **stubbed** — current syntheses run from
    `notes/` + config only.
- **`earnings-reviewer` / `earnings-reviewer-from-pdf`** — production agents behind the earnings cron
  and operator-uploaded transcripts.
- **`market-researcher`** — general market-research helper; may suggest ideas but never edits
  `watchlist.yaml` (tier changes are operator-only).

## 6. Workflow patterns

- **News → triage:** the digest surfaces items; the operator decides the response per tier —
  **T1**: read and absorb; **T2**: lightweight scoring update; **T3**: full ingest + scoring workstream.
- **Conference event:** manual ingest with an explicit **fidelity disclaimer** (today's ingests are
  multi-query WebFetch *summaries*, not verbatim transcripts — flagged in frontmatter + a "Fidelity
  note" section). Proper transcript-fidelity ingest is open work (§8).
- **Scoring update:** operator conversation → Claude Code proposes exact diffs → `check.py` → commit →
  push. Substantive changes are shown for review before commit.
- **Pre-IPO → public:** a `.pvt` driver is renamed in place to its ticker and promoted to T1 at
  pricing. **`spacex.pvt` is the imminent case** (IPO ~2026-06-11/12 → likely `SPCX`).

## 7. Integrity mechanisms

- **`scripts/check.py`** — schema/reference validation; run before every commit (lints manifests,
  resolves references, catches drift). Must pass clean.
- **Auto-sync semantics** — the 15-min sweep means "uncommitted = will be committed soon" (see §4);
  verify before editing, use follow-up commits for revisions, never force-push over a pushed
  auto-sync commit.
- **Source-verification discipline** — primary sources only; paraphrase is flagged when unsourced
  (e.g., the MRVL "preferred custom silicon partner" phrase was struck as unverified; the POET→MRVL
  edge was added only after POET's own SEC 6-K / press releases confirmed it).
- **OPERATOR-PRIVATE SIGNAL canonical sweep** — periodic audit to keep the single-tag convention clean
  (lowercase/variant forms normalized).
- **`.pvt` registry invariant** — see §2; removing a `.pvt` entry requires retargeting any edge that
  referenced it.

## 8. Open architectural questions

- **Autonomy direction** — operator wants to shift toward *agent-handles-it* (less turn-by-turn
  conversation). **Will revisit after ~1 week of digest output.** Data to collect during the week:
  digest volume; the fraction of HIGH items that genuinely warrant action vs. read-and-noted;
  MRVL-style workstream frequency in steady state; operator-intervention patterns. **The redesign
  will be informed by that empirical base, not designed in the abstract.**
- **Cross-session memory namespace** — memory is keyed by launch cwd. **Launch from
  `/root/research-watchlist` (not `/root`) to load project memories at session start.** The `-root`
  namespace holds *operational* memories (digest routine, env fixes) but **not** project state — a
  session launched from `/root` will miss the project memory (this caused a "Phase C" lookup miss).
- **Conference-transcript fidelity** — WebFetch summary vs. a proper transcript ingest path
  (FactSet_UnstructuredContent semantic pull or HTML parse) as `scripts/ingest_conference_transcripts.py`.
- **News-digest tuning (post ~1 week live)** — (2) cluster embeddings (same story under-merges),
  (4) SEO/listicle title patterns, (5) strong-sentiment FactSet-only → HIGH, (6) MEDIUM volume noise.
- **ticker-synthesis Phase 2 sources** — wire insider transactions, sell-side revisions, podcasts,
  FactSet fundamentals into synthesis (currently stubbed; see §5).
- **Gmail-poller → wrapper auto-trigger** — no automatic handoff from poller to the from-PDF note
  wrapper; remediate via a sweep cron.

## 9. Recent milestones (most recent first)

- **2026-06-03** — Added `frontier_model_competition` + `agent_framework_landscape` themes; 4 new
  `.pvt` drivers (moonshot, deepseek, mistral, langchain); **`spacex.pvt` absorbed `xai.pvt`**
  (xAI dissolved into SpaceX's SpaceXAI division; Grok now under SpaceX); BABA tagged
  `frontier_model_competition` (Qwen); this ARCHITECTURE.md.
- **2026-06-02** — **News digest Phase C BUILT + LIVE**; 5 T3 optical/photonics additions (Zhongji
  Innolight, Eoptolink, Dongshan, AAOI, POET) + edges; MRVL Murphy/Computex keynote ingest + scoring
  refresh (verified $2B/2026-03-31 NVDA investment); OPERATOR-PRIVATE SIGNAL canonical sweep.
- **2026-06-01** — NVDA GTC Taipei keynote ingest (summary fidelity).
- **2026-05-28** — MRVL 1Q27 earnings ingest + T3→T2 promotion and full scoring.
- **2026-05-17** — T3 stub additions via the WATCHLIST-email process (Innolight `300308.SZ`,
  Eoptolink `300502.SZ` as bare stubs; both enriched 2026-06-03).
- **2026-05-09/10** — OPERATOR-PRIVATE SIGNAL convention codified; initial T1+T2 scoring pass;
  `private_drivers` seeded.

## 10. Memory notes

Project memories — `/root/.claude/projects/-root-research-watchlist/memory/`:
- `watchlist-scoring-rubric` — the scored-axes schema, where defined, calibration anchors.
- `tier-promotion-criterion` — T1 = BCTK holding (not conviction); scraper auto-promotes on buy.
- `demote-means-sold-from-bctk` — operator add/remove is authoritative; edit tiers only.
- `operator-private-signal-convention` — when/how to tag scores with OPERATOR-PRIVATE SIGNAL.
- `ticker-synthesis-v1-6` — partnership-edge cross-ticker extension + coverage line.
- `news-digest-phase-b-spec` — approved dual-source digest spec; BUILT + LIVE; deferred tuning items.
- `spacex-ipo-transition` — `spacex.pvt` absorbed `xai.pvt`; IPO → ticker/T1 handoff plan.
- `mrvl-scoring-refresh-2b` — verified $2B/2026-03-31 NVDA–MRVL investment wired into scoring.
- `conference-transcript-ingest-path` — OPEN: build transcript-fidelity ingest.
- `gmail-poller-wrapper-handoff-gap` — OPEN: poller→wrapper auto-trigger.
- `next-session-cleanups` — (A)+(C) resolved; only (B) v1.6.1 doubled-label fix remains open.

Operational memories — `/root/.claude/projects/-root/memory/` (loaded only when a session launches
from `/root`; see §8):
- `enrich-sidecars-cron-env-fix` — RESOLVED: cron env-load needed `export`/`set -a`, not just `source`.
- (also: `daily-digest-routine`, `env-probe-secret-safety`, `nport-price-cache-stale`, `pre-ipo-watchlist-feature`)
