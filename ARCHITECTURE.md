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
| `scripts/chunking/` + `state/chunk_store/` | research-watchlist | **Retrieval layer (in progress)** — the sub-document store below `notes/`. Chunker + embed/ingest/retrieve job + `schema.sql` (durable pgvector spec). `state/chunk_store/` holds the file-backed vectors (gitignored, regenerable). Design + status in `docs/chunking-strategy.md`. |

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
- **Thesis loop (2026-09-09)** — every channel now terminates in `notes/{TICKER}/_thesis.md`
  (machine-drafted, operator-correctable assumptions with confirm/challenge pressure) instead of an
  email. Crons: `thesis_match` (15:00 daily, `scripts/thesis/match_evidence.py`: news/SEC/entity
  claims/substack+podcast/conference/inbox evidence → `claude -p` Sonnet verdicts →
  `state/thesis/evidence_log.jsonl` + status proposals), `thesis_alerts_am/pm` (06:20 / 15:45, thin
  one-line-per-event email, announced once), `thesis_weekly` (Mon 06:15, `thesis_report.py --weekly
  --auto-quarterly`: movers ranked by thesis delta, per-name detail, themes, pending score proposals,
  drafts needing your eye, quiet names, coverage → Brevo + `notes/reports/thesis-delta-*.md` +
  `state/thesis/ranking_*.json`), `thesis_draft` (Sun 07:00, `draft_thesis.py --missing-only`),
  `store_b_weekly` (Sun 08:00, `ingest_metrics.py --cron`: FactSet EstimatesConsensus via
  `run_mcp`, ~54 calls, + consensus snapshot), `insider_pull` (Sun 09:30, InsiderScore open-market
  ex-10b5-1 → `state/thesis/insiders_*.jsonl`), `transcript_conferences` (Sat 09:00,
  `scripts/v3_ingest/transcript_ingest.py --conferences 8`: FactSet CalendarEvents lists the
  week's Conference sessions per name, then one UnstructuredContent pull per (name, session day)
  over a 3-day window — one page holds the whole event, where paging a whole-window corpus left
  gaps — → verbatim `corprep` rows in `state/transcripts/exchanges.jsonl`, read by the matcher's
  `conference_since`; Haiku mcp-lean, the placed tool arguments are verified against the
  transcript and the page is read from the raw tool_result), `topic_map` (Sat 11:00,
  `scripts/topics/topic_map.py --run --suggest-names --email`: every exchange in
  `exchanges.jsonl` — analyst = question register, corprep = evidence register — embedded once
  (Gemini, float16 store) and scored against the 62 theme anchors = mean-centered pg centroids
  of the labelled chunks, calibrated threshold from `state/topics/anchors_meta.json`; below-
  threshold units are greedy-clustered and clusters with ≥3 companies and ≥2 banks become
  candidates in `state/topics/candidates.json` + `notes/reports/theme-candidates.md`; the
  operator names/rejects with `--accept/--reject`, never the system). `config/watchlist.yaml` stays operator-only:
  proposals surface in the report and are applied by `scripts/thesis/apply_scores.py --write`.
  Design: `docs/superpowers/specs/2026-09-09-thesis-loop-design.md`.
- **`daily_digest` / `nport_*` / `watchlist_derive`** — adjacent pipelines (daily report email, NPORT
  weekly marks, BCTK-holdings derive) feeding/around the system.

### News digest (Phase C)
Dual-source over **49 tickers** (T1 + scored T2 + selected T3): **Google News RSS** (breadth) +
**FactSet ALL_NEWS** (quality/sentiment, called via `claude -p` + the FactSet MCP). Pipeline:
fetch → cluster (headline Jaccard ≥ 0.6) → classify HIGH/MEDIUM/DROP (volume, top-tier-source w/
relevance gate, FactSet in-both / sentiment) → 18h state-ledger de-dup → plain-text Brevo email.
Per-ticker isolation; degraded-coverage banners; rendered body persisted to a gitignored
`logs/news_digest_*.txt` audit artifact. Code: `scripts/news_digest.py` + `scripts/newsdigest/`.
**Story cap (2026-08-19):** the digest carries at most **30 stories**, **max 2 per ticker**, chosen by
an editorial ranking pass (`scripts/newsdigest/rank.py`) that runs between classify and summarize —
tier → estimate-changing → novelty → cross-read, with sell-side rating actions ranked last and
admitted only when they state a non-valuation rationale. Sitting before the summarizer is what makes
it a cost cut (~$5.6 → ~$3.1 per run) rather than a cosmetic one. Survivors below the cut are still
filed to `notes/news/` + pg as headline-only notes, so corpus recall is unchanged. Header reads
`top 30 of N`; a ranking failure falls back to a deterministic order and says so in a banner.

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
  and operator-uploaded transcripts. **Thesis-aware since 2026-09-09:** Step 3 reads
  `notes/{T}/_thesis.md` and the wrapper's pre-staged `state/thesis/context/{T}.md` (open
  assumptions + Store B guidance track record); new **§4b Assumption read** gives one
  machine-readable Confirm/Challenge/Silent line per assumption id (the matcher lifts these as
  strength-3 evidence and the §5–7 score recommendations as `proposed_scores`).
- **`thesis-chat`** (skill, `.claude/skills/thesis-chat/SKILL.md`) — weekly operator review: walks
  `state/thesis/questions.jsonl` (drafts that got first evidence, stale assumptions, score
  proposals), shows the evidence, records decisions through `scripts/thesis/answer.py`.
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

- **Idea surfacing / sub-sector timeliness (spec 2026-08-11)** — P1 transcript ingest built
  (backfill 08-11, forward cron 09-10); **P2 topic_map built 2026-09-10** on main
  (`scripts/topics/`, calibrated pg-centroid anchors, no per-unit LLM extraction). P3
  foreign_evidence, P3b MD&A evidence, P4 diffusion/detectors, P5 renderers still open. NOTE: the
  local branch `worktree-idea-surfacing-spec` (2026-08-19..22, never merged, never ran end to end)
  holds an earlier P2 (claude -p phrase extraction, 21.5h serial) plus `mdna_evidence.py`
  (P3b, 8,251 claims), `lifecycle.py` (Tier-0 lag measurement) and `evidence_store.py` — start
  P3b/P4 from those files, and from `docs/superpowers/plans/2026-08-21-topic-space-findings.md`
  (housekeeping filter; MD&A is rewritten each quarter so a diff is a filter, not a signal).
- **Thesis loop follow-ups (2026-09-09)** — (a) ~~conference-transcript feed~~ CLOSED 2026-09-10:
  `transcript_ingest.py --conferences 8` on the Saturday cron (§4), calendar-driven; still open
  there: a session dated today is pulled with a window clamped to today and only completed by the
  next week's run, and names FactSet's calendar does not list are not pulled at all (`--scan`
  keeps the whole-window fallback); (b) ETF context in the report is BCTK weight +
  5-day flow only (no per-name days-of-ADV yet); (c) the quarterly "state of theses" edition
  triggers off the earnings-note calendar on disk, not InsiderScore `future_earnings_dates`;
  (d) InsiderScore row keys were verified on one live pull — extend `insider_pull.normalize` if a
  new key shape appears.

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
- **Sub-document retrieval (chunking) — the answer to the old "vector store at ~200 docs"
  question, now being built.** `docs/chunking-strategy.md` is the design (decisions locked in §9
  there). Status: chunker + file-backed Store A pipeline is **code-complete (step 4)**; ranking +
  plumbing verified (gold eval 25/31/32), but the **embedding path is unverified — full-corpus
  ingest is blocked on a refreshed Gemini key** in `/root/podcasts/.env` (operator to refresh, then
  `python3 scripts/chunking/ingest.py --all --rebuild`). Open after that: **Store B** (FactSet
  guidance-beat metrics) = step 5, which is also the **managed-pgvector cutover** (today the job is
  file-backed numpy; pgvector is the locked target but earns its keep only when the A↔B JOIN lands).
  The heuristic facet tagger is NVDA/SaaS-cue-flavored → the planned **LLM tagger (§8 of that doc)**
  is the real generalizer.

## 9. Recent milestones (most recent first)

- **2026-09-10** — **P2 topic_map** (`scripts/topics/`): theme anchors = pg centroids of the
  labelled chunks, mean-centered (uncentered, every chunk sat within cosine 0.74 of every theme),
  threshold calibrated on a held-out fifth (0.30: P 0.31 / R 0.37 / cov 0.80, top-1 0.55 vs the
  chunker's own tags); exchanges embedded once into a float16 store (batched, 429-aware);
  greedy-leader candidate clusters behind a 3-company/2-bank gate; operator decisions via CLI.
  Cron Sat 11:00. Prior unmerged branch work recorded in §8.
- **2026-09-10** — **Conference-transcript weekly feed** (`transcript_ingest.py --conferences`):
  ingester moved to the mcp-lean transport (~100K → ~22K tokens/call) and to Haiku (A/B vs Sonnet
  on 3 names: identical vectorIds; the model only places the call, and an argument-drift guard
  fails a page whose tool_use input differs from the request); window-scoped ledger keys so
  forward runs never collide with the backfill; calendar-driven per-event pulls after the
  whole-window scan measured 22/50 overlapping chunks between pages of one query; FactSet
  rejects future end dates, so event windows clamp to today. Cron Sat 09:00.
- **2026-09-09** — **Thesis loop built end to end** (`scripts/thesis/`): `_thesis.md` object +
  drafter (scores/notes/thin modes, COHR/LITE imported from the assumptions draft), evidence
  collectors for every channel, daily matcher, thesis-aware earnings reviewer (§4b), weekly delta
  report + alerts + quarterly edition + ranking json, InsiderScore weekly pull, Store B weekly
  FactSet refresh via `run_mcp`, PDF EX-99 exhibits in the SEC channel (6-K always; the survey
  found every PDF exhibit on 6-Ks), `apply_scores.py`, `check.py` thesis validation,
  `thesis-chat` skill. Plan: `docs/superpowers/plans/2026-09-09-thesis-loop.md`.

- **2026-06-03** — **Chunking/retrieval steps 3b + 4**: second gold note (GOOGL) clears
  generalization (combined recall@5 32/32); **Store-A pipeline built** (`scripts/chunking/`:
  chunker fix + `schema.sql` + `embed`/`store`/`ingest`/`retrieve`/`eval_store`) — file-backed now,
  pgvector at step 5. Code-complete; full-corpus embed pending a Gemini-key refresh. See
  `docs/chunking-strategy.md` §12.
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
