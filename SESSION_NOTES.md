# Session Notes

_Append-only chronological log of working sessions — **most recent at top**. New sessions add a `## YYYY-MM-DD — <title>` section above the existing entries (directly below this line)._

## 2026-06-03 — Chunking/retrieval: step 3b committed + step 4 (Store-A pipeline) built

**Session focus:** Pick up the note-chunking/RAG workstream. Closed out the uncommitted step-3b work, then built step 4 — the Store-A embedding + ingestion + retrieval pipeline.

**Step 3b (committed `fdc3ada`):** pinned the GOOGL backlog gold case to require BOTH `operating_kpis` + `revenue` facets (guards the operator-requested multi-label against a future IDF/cue tweak); scope-honest eval wording ("no reachability gap on the constructed gold set", not "no retrieval ceiling").

**Step 4 — Store-A pipeline (committed `b607034`, `c8fa9da`), all in `scripts/chunking/`:**
- `schema.sql` — durable **pgvector DDL** (Store A `chunks` + Store B `metrics` + A↔B JOIN sketch), `vector(3072)`. Not executed today; the target spec.
- `embed.py` (Gemini helper + sha256 cache), `store.py` (`Store` iface + `FileStore` numpy cosine + `PgStore` step-5 stub; `get_store()`←`CHUNK_STORE_BACKEND`), `ingest.py`, `retrieve.py` (auto-merge to parent), `eval_store.py` (regression gate).
- Fixed a real `_parse_roster` crash (bare-string `speakers:` entry) → all 56 notes chunk (487 parents + 2,339 children).

**Key decision (operator-approved after discussion):** pgvector is the locked target but runs **file-backed today** — the A↔B JOIN that justifies a DB is Store B (step 5), so a daemon buys nothing at ~2.3k vectors. `schema.sql` = durable spec; swap to managed pgvector (`PgStore`, `CHUNK_STORE_BACKEND=pg`) is the **step-5 trigger**. (Operator initially leaned "managed now"; agreed to defer once the JOIN-earns-the-daemon framing was clear.)

**Honest verification scope (advisor caught — same self-consistency trap as 3a/3b):** the gold eval (25/31/32, reproduces §11c) ran on **cached 3b vectors**, so it proves `store.py` ranking math + plumbing, NOT the embedding path. Flipped `retrieve()` default to `production_boosts=False` so default == measured config (the §7 operator/recency boosts are untuned → OFF until measured).

**⚠ OPEN — blocks step-4 "done":** `embed.py`→Gemini has **zero live runs**; key in `/root/podcasts/.env` is **expired** (operator will refresh later tonight 2026-06-03). Then the real acceptance gate is one command:
```
python3 scripts/chunking/ingest.py --all --rebuild
```
Watch: seeded cache (111 vectors, 2 gold notes) mixes cleanly with fresh embeds for the other 54; live `retrieval_document` vector matches the cached one. Then re-run `eval_store.py` to confirm 25/31/32 end-to-end on live vectors → step 4 flips code-complete → verified.

**Next:** step 5 = Store B (FactSet guidance-beat time series + credibility score) = also the managed-pgvector cutover. Still 2 large-cap notes w/ NVDA-flavored cues → LLM tagger (§8) is the real generalizer.

---

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
