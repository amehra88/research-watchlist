# Session Notes

_Append-only chronological log of working sessions — **most recent at top**. New sessions add a `## YYYY-MM-DD — <title>` section above the existing entries (directly below this line)._

## 2026-06-03 — Agentic framework/harness landscape build-out

**Session focus:** Operator pivoted the `agent_framework_landscape` theme from "privates as thesis drivers" to "best-of-breed leaders in agentic frameworks/harnesses, wherever they sit." LangChain is the anchor name.

**Landed in research-watchlist (config/watchlist.yaml):**
- 3 new private_drivers: `cognition.pvt` (Devin+Windsurf, ~$10.2B, affects MSFT/GOOGL), `sierra.pvt` (Bret Taylor, $15B/$950M raise May'26, $150M+ ARR, affects NOW), `decagon.pvt` (Sierra competitor, affects NOW)
- Tagged `agent_framework_landscape` onto 7 public read-throughs: GOOGL, MSFT, AMZN, NET, NOW, PLTR, DDOG (CRM not in 147; NBIS/NVDA/AVGO/META excluded as infra/silicon/model)
- spacex.pvt notes += **OPERATOR SIGNAL** (non-public, unverified): SpaceX has an agreement to acquire Cursor/Anysphere (~$1.2B ARR coding-agent harness) within ~12mo → folds into post-IPO SPCX, no standalone cursor.pvt
- New sector note: `notes/sector/20260603-agentic-framework-harness-landscape.md` (five-layer map + investability/read-through table)

**Filed to operator memory:** cursor-spacex-acquisition-signal (project type).

**Open follow-ups:**
- Verify single-blog ARR/val figures (Cursor $1.2B, Claude Code $2.5B, Cognition $10.2B/$150M) vs PitchBook/primary before they harden into thesis inputs
- Supply-chain edges for new .pvts (cognition→MSFT/GOOGL, sierra/decagon→NOW, langchain→NET/NBIS) — deferred
- Seed _profile.md for langchain.pvt + the 3 new .pvt dirs
- Decide whether to add CRM to the 147 (cleanest listed vertical-agent pure-play via Agentforce)
- Confirm Cursor→SPCX; on close fold into renamed SPCX T1 entry

---

## 2026-06-02 — News digest live + MRVL closure + private-driver expansion

**Session focus:** Close MRVL Murphy keynote workstream, build and deploy Phase C news digest, expand private-driver coverage (frontier models + agent frameworks), restructure spacex.pvt post-xAI merger.

**Landed in research-watchlist:**
- b3f5eb6 — Murphy/Computex keynote ingest (notes/MRVL/20260602-conf-computex-murphy.md) with WebFetch summary-fidelity disclaimer
- 41ddcc3 + fc13cf1 — MRVL scoring 5-item refresh (verified $2B/2026-03-31 NVDA investment; "preferred custom silicon partner" struck as unverified; Switzerland/copper-wall thesis content added)
- e31b7d4 — config/ticker_identity.yaml (Phase C checkpoint 1, 44 tickers)
- e3fede7 — config/news_sources.yaml (Phase C checkpoint 2)
- f060fd0 — scripts/newsdigest/ package + scripts/news_digest.py
- 6c548ac — digest fixes (regional edition collapse, top-tier relevance gate)
- 6dd13eb — digest artifact persistence (logs/news_digest_*.txt)
- 64539bc — chmod +x + cron enabled (06:45 ET premarket / 18:30 ET postmarket Mon-Fri)
- 259e226 — OPERATOR-PRIVATE SIGNAL canonical normalization (SNPS, WELL)
- a900bb5 — 5 T3 optical/photonics additions (Zhongji Innolight, Eoptolink, Suzhou Dongshan, AAOI, POET); ticker_identity.yaml grew 44→49
- 1871bc9 — 2 new themes (frontier_model_competition, agent_framework_landscape) + 4 new .pvts (moonshot, deepseek, mistral, langchain) + spacex.pvt restructure absorbing xai.pvt
- 9acca42 — BABA themes += frontier_model_competition (closes Qwen encoding loop)
- 6fcf960 — ARCHITECTURE.md (system overview, 197 lines)

**Landed in research (local-only):**
- 7d29498 — MRVL→NVDA supply-chain edge $2B/2026-03-31 framing
- 60778e6 — 11 T3 optical/photonics edges (Chinese names + AAOI + POET, including verified POET→MRVL former-supplier edge)
- 1739a1c — NVDA→xai.pvt edge retargeted to NVDA→spacex.pvt (.pvt registry integrity)

**Now live in production:**
- News digest cron: 06:45 ET premarket + 18:30 ET postmarket, Mon-Fri (next live fire: tonight 18:30 ET as of session write time)
- 49-ticker scope (T1 40 + scored T2 4 + selected T3 5)
- Both channels validated healthy (Google News RSS + FactSet ALL_NEWS via claude -p)

**Open items going into next session:**
- v1.6.1 prompt cleanup (doubled-label fix in ticker-synthesis considered-list bullet) — cosmetic, bundle with next prompt iteration
- Conference-transcript proper ingest path (transcript-fidelity vs WebFetch summary) — design only, no code
- Theme tag assignment pass — frontier_model_competition + agent_framework_landscape to existing tickers (NVDA, MSFT, GOOGL, AMZN, META, NET, NBIS, etc.) — deferred from today's batch per scope
- Supply-chain edges for new themes — moonshot/deepseek → openai+anthropic [competitor], NET→openai+anthropic [partnership at agent framework layer], etc.
- News digest tuning items (post ~1 week live): cluster embeddings, SEO/listicle patterns, sentiment-only HIGH elevation, MEDIUM threshold
- SpaceX IPO transition (expected ~2026-06-11/12) — spacex.pvt → public ticker, T1 promotion
- Architecture redesign (autonomy direction) — revisit after week of digest data

**Architectural decisions made:**
- Architecture redesign paused for ~1 week of digest output (operator chose to pause discussion, finish Phase C first, revisit with empirical data)
- Auto-sync race pattern: don't fight 15-min sweep; follow-up commits for revisions, never rewrite pushed history (pattern recurred ~6 times today)
- POET→MRVL supplier edge: include with former/disrupted framing because confirmed via POET's own SEC 6-K and press releases (not analyst speculation); discipline established that supplier edges require primary-source confirmation
- ARCHITECTURE.md created as living descriptive document (complements operational CLAUDE.md)

**Operator preferences filed for ongoing session behavior:**
- Less conversation, more action — conversations are mostly process overhead
- Shorter responses, fewer questions, less editorializing
- Operator wants more autonomous system (agent-handles-it direction) — staging/pending area concept filed for future build

**Waiting on at session-write time:**
- 18:30 ET postmarket digest run (first live cron fire, background waiter armed, will report when fired)

**Note on commit-date discrepancy:** commit subject lines for 8e2d291 (SESSION_NOTES.md initial) and 6fcf960 (ARCHITECTURE.md initial) reference 2026-06-03 — those were post-dated at write time; the actual work date is 2026-06-02 per the body of this section. The subjects are immutable (already pushed) so they stand as-is; in-tree dates were normalized to 06-02 (this section header + 12 watchlist.yaml references).

---

---
