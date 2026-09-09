# Thesis-integrated research loop: plan

## Context

The operator asked how the earnings reviewer, the news channel, and company presentations
feed thesis, themes, forecasts, and rankings, and concluded the system "is not as integrated
as I would like." Goal: better-informed investment decisions via one integrated output, a
report that highlights changes to thesis and draws on every channel.

### What exists today (verified 2026-09-09 by three read-only explorations)

- **Earnings reviewer** (`scripts/cron_earnings_reviewer.py` + `.claude/agents/earnings-reviewer.md`,
  cron 02:30 ET). Per print: transcript + FactSet consensus → Confirm/Drift/Break per assigned theme,
  hold/revise recommendations on the four scores → `notes/{TICKER}/{YYYYMMDD}-{1QYY}.md`.
  Reads nothing intra-quarter (no `retrieve()`, no pg, no Store B, no news/SEC/substack notes).
  Prior-note glob `*-earnings-*.md` matches nothing → every unattended run is "first observation".
  **19 notes since June carry 44 explicit score-change recommendations; 0 applied.** Scores in
  `config/watchlist.yaml` are all stamped 2026-06-01/02. Cron health is flaky (calendar step
  rc=124/rc=1 on 09-06..09-08; clean on 09-09).
- **News channel** (`scripts/news_digest.py`): 18,265 notes + 85k pg chunks (55% of corpus),
  frontmatter `tickers[]` (= materiality), `themes[]`, `confidence`, `summarized`. Consumer: email only.
- **SEC channel** + `scripts/v3_ingest/entities.py` (14:00): 8,009 notes; pg `entity_mentions`
  (3,297 rows, `affects[]` = whose thesis it bears on); `state/evidence/claims.jsonl` (8,251).
  Consumer: none. **PDF exhibits are skipped** (`sec_filings.py:376`), so investor-day / conference
  decks furnished under 8-K 7.01 never enter the corpus.
- **Presentations**: only operator-emailed PDFs matching `{TICKER}-{date}-conf-{name}` (11 notes) or
  manual keynote ingests. FactSet verbatim conference transcripts exist only on the stalled
  `worktree-idea-surfacing-spec` branch (extraction 420/8,717 units, stopped 2026-08-22).
- **Thesis**: four 1–5 scores + `scoring_notes` per T1/T2 name. Testable-assumption structure drafted
  for COHR/LITE only (`docs/thesis-assumptions-draft.md`), never wired; `thesis_challenges.py` never
  written. No per-ticker thesis document exists.
- **Forecasts**: no operator numbers. Store B (`scripts/chunking/store_b.py`, pg `metrics` 5,202 rows,
  `metrics_credibility`, view `guidance_with_track_record`) holds consensus/guidance/surprise but is
  frozen at `as_of 2026-06-24` because `ingest_metrics.py` is manual. (The "FactSet not cron-reachable"
  note in `config/optical_revenue.yaml` is stale: `scripts/lib/claude_p.run_mcp` already runs FactSet
  from cron for factset_news / etf_flows.)
- **Ranking**: none. Tiers = ownership. AI-forward screen ranking is a hand-coded dict, manual.
- Original roadmap `/root/research/DESIGN.md` §9.1 "M-6 daily-watch: continuous thesis-maintenance
  synthesis between earnings prints" names this gap; never built.

**Root cause:** there is no thesis object for channels to write against. Every pipeline terminates in a
document or an email, and the operator is the join.

### Operator decisions (this session)

- All four (thesis, themes, forecasts, rankings) feed one integrated output: a report of thesis changes.
- The system drafts thesis assumptions itself from scoring notes + earnings notes; drafts are flagged
  and corrected as they surface, not gated on up-front review.

### Standing constraints honoured

- `config/watchlist.yaml` is never machine-written (tiers, scores, vocabulary are operator-only).
- Pause `auto_sync` for the build (backup crontab → `/root/backups/crontab.pre_build_<ts>.bak`), restore
  at end. Orphan-process scan before launching any batch.
- `claude -p` jobs use the lean recipe in `scripts/lib/claude_p.py` (`run` / `run_mcp`), fail loud on
  auth/429, and are resumable via a ledger.
- Do not restart the idea-surfacing extraction; do not build an operator forecast model; do not wire
  IR feeds or sell-side. Those stay parked.

---

## Design

Four components, built in the order below. Each is independently testable.

```
 earnings note ─┐
 news (HIGH)    │   ┌──────────────────────┐    ┌───────────────────────┐
 SEC claims     ├──▶│ 2. match_evidence.py │───▶│ state/thesis/          │
 substack/pod   │   │   daily 15:00 ET     │    │   evidence_log.jsonl   │
 conf/decks ────┘   └──────────────────────┘    │   pressure per assump. │
                              ▲                 └───────────┬───────────┘
 1. notes/{T}/_thesis.md ─────┘ (assumptions)               │
    drafted by draft_thesis.py                              ▼
                                                ┌───────────────────────┐
 Store B (refreshed weekly) ───────────────────▶│ 4. thesis_report.py   │──▶ email + notes/reports/
 3. earnings reviewer (thesis-aware) ──────────▶│   weekly + on-event   │    + state/thesis/ranking.json
                                                └───────────────────────┘
```

### 1. Thesis object — `notes/{TICKER}/_thesis.md`

One file per T1 + T2 name (≈90). Underscore prefix sorts first, matching the existing
`notes/{pvt}/_profile.md` convention; visible in Obsidian. YAML frontmatter is the machine-read
part; the body is a short human rationale.

```yaml
---
doc_type: thesis
ticker: COHR
tier: tier_1_bctk
drafted: 2026-09-10            # by draft_thesis.py
drafted_from: [config/watchlist.yaml#COHR, notes/COHR/20260813-4Q26.md]
reviewed_by_operator: false     # flips only when the operator edits or approves
scores:                         # snapshot of watchlist.yaml at draft time (read-only mirror); keys = watchlist paths
  ai_positioning: "4"                       # bare string OR {score, notes} in the watchlist; mirror stores the score string
  competitive_advantage.innovation_rate: "4"
  competitive_advantage.distribution: "4"
  competitive_advantage.overall: "4"
  potential_investor_interest.score: "4"
proposed_scores:                # machine-maintained; from reviewer recs + evidence pressure
  potential_investor_interest.score: {value: "4+", since: 2026-08-13, source: notes/COHR/20260813-4Q26.md}
assumptions:
  - id: datacom_ramp_continues
    statement: "The 800G→1.6T datacenter ramp continues to pull COHR volume."
    derived_from: "ai_positioning: 4"
    themes: [ai_infrastructure_capex, optical_interconnect]
    challenged_by: ["hyperscaler capex digestion", "CPO bypassing pluggables", "slower 1.6T adoption"]
    confirmed_by: ["hyperscaler capex guides up", "1.6T design wins"]
    status: open                # open | confirmed | challenged | retired
    status_source: draft        # draft | evidence | operator
    pressure: {confirm: 0, challenge: 0, window_days: 90, last_evidence: null}
    draft: true                 # cleared when operator edits/approves
---
```

**Drafting rule** (`scripts/thesis/draft_thesis.py`, one `claude_p.run` per ticker, Sonnet):
inputs are the ticker's watchlist scoring blocks + `scoring_notes`, the two most recent earnings
notes, and any `synthesis-*.md`. Prompt embeds the COHR/LITE lesson verbatim: claim only what the
score itself implies; a watch-item stays a watch-item; never add "durable", "remains", "offsetting",
or a causal mechanism the note does not state; 3–6 assumptions; each must have observable
`challenged_by`. Existing `docs/thesis-assumptions-draft.md` content is imported directly for
COHR/LITE (not re-drafted) and serves as the gold check for the drafter (run the drafter on
COHR/LITE too and diff; the over-reads it must NOT reproduce are listed in that doc).

Resumable via `state/thesis/_draft_progress.json`. Re-running never overwrites a file whose
`reviewed_by_operator` is true or whose assumptions carry `draft: false`.

**Input coverage (measured 2026-09-09):** of 90 T1+T2 names, 48 have a scoring block (T1 36, T2 12)
and 42 do not. Three drafter modes, recorded in frontmatter as `draft_mode`:
- `scores` (48 names): scoring blocks + `scoring_notes` + up to 2 earnings notes; the "claim only what
  the score implies" rule applies.
- `notes` (25 unscored names that have an earnings note): themes + earnings note §1/§3/§4 + latest
  MD&A; assumptions carry `derived_from: themes+earnings`.
- `thin` (17 names with neither: T1 A000660, DPC, simaai.pvt, INIO, SPCX, STX; T2 ARM, DASH, DOCN, GLW,
  INTC, NOW, NXPI, RDDT, ROKU, TXN, SEI): themes + latest 10-Q/10-K MD&A section from pg + last 30 days
  of HIGH news; at most 3 assumptions; `thin_inputs: true` so report §5 surfaces them first.
`.pvt` ids and the `A000660` alias are skipped (reuse `ingest_metrics.universe()` for enumeration).

**Store hygiene:** `_thesis.md` will be chunked by `ingest --all` like any note (`ingest.py` rglobs
`*.md`; chunker derives `base_ticker` from the path and honours frontmatter `doc_type`; chunk_id becomes
`{TICKER}-thesis`). Add `thesis: 1.00` to `_DOC_TYPE_WEIGHTS` (`scripts/chunking/store.py:56`). Do NOT
route thesis frontmatter through `scripts/metadata/schema.py::DocMetadata` (pydantic, `extra="forbid"`,
fixed `DocType` enum). Extend `scripts/check.py` to validate: unique ids per ticker, enum statuses,
every T1/T2 ticker has a `_thesis.md` (warn, not fail). Create `notes/reports/` (does not exist yet).

**`thesis_io.py`** owns frontmatter round-tripping: split on the first `^---\n(.*?)\n---\n` block (the
regex from `chunker._parse_frontmatter`), `yaml.safe_dump(sort_keys=False)` the dict, reattach the body
untouched, write via the atomic tmp+`os.replace` pattern in `scripts/backfill_frontmatter.py::_write_note_atomic`.
No existing helper does "rewrite YAML, keep body", so this is new code (~60 lines) with tests.

### 2. Evidence matcher — `scripts/thesis/match_evidence.py` (cron 15:00 ET daily, after entities 14:00)

Per T1/T2 ticker, collect evidence since the per-ticker watermark (`state/thesis/watermarks.json`):

| Source | Query | Text passed |
|---|---|---|
| Earnings notes | `notes/{T}/????????-[1-4]Q??.md` newer than watermark | §1, §3, §4, §5–7 |
| News | **from disk, not pg**: `notes/news/{YYYY-MM-DD}-*.md` with filename date > wm, parse frontmatter, keep `T in tickers` and (`summarized: true` or `confidence: high`). (pg `chunks` has no path column and `doc_id` is a text sha256, so the frontmatter filter cannot be expressed in SQL.) | note body |
| SEC | pg `chunks WHERE kind='parent' AND doc_type='sec_filing' AND %s = ANY(tickers) AND event_date > wm AND (section LIKE 'Exhibit EX-99%%' OR section LIKE 'Item %%Management%%' OR section = '8-K body')` (item codes are not a column; sections are literal header strings) + `entity_mentions WHERE (subject = %s OR %s = ANY(affects)) AND extracted_at > wm` (`affects` alone hits 245/3,297 rows; `subject` carries the rest) | section text / claim + stance |
| Substack / podcast | pg `kind='parent' AND doc_type IN ('substack_post','podcast_summary') AND %s = ANY(tickers)` | parent chunk |
| Conference / decks | `notes/{T}/*-conf-*.md` + (after P6) `doc_type='sec_filing'` sections `Exhibit EX-99.N (slides)` + `state/transcripts/exchanges.jsonl` conference `corprep` rows | note §2, §3 / chunk / exchange text |

pg access via `scripts/chunking/pgconn.py::connect()` (resolves `DATABASE_URL` from env or
`/root/podcasts/.env` itself), imported the way `entities.py:49` does.

Skip the ticker if nothing new (most days for most names). Otherwise one `claude_p.run` (Sonnet,
lean flags) with the assumptions and up to N evidence items (cap ~12k chars; overflow deferred to
next run, watermark advanced only past what was sent). `claude_p.run` returns plain text: prompt for a
JSON-only reply and `json.loads` it; reject and retry once on parse failure. Pass
`precheck=` reusing `sec_filings._LIMIT_RE` / `classify_llm._detect_session_limit` so a 429 or session
limit aborts the ticker loop immediately instead of grinding through 90 names. Output per evidence item:
`{assumption_id | null, direction: confirm|challenge|neutral, strength: 1-3, why, quote, source, date}`.

Appended to `state/thesis/evidence_log.jsonl` (append-only, `(ticker, source_id, assumption_id)`
dedup). Then `_thesis.md` frontmatter is rewritten in place (frontmatter only; body untouched):
`pressure` recomputed over the 90-day window; **status proposal rule**: `challenged` when
challenge-strength sum ≥ 4 from ≥ 2 distinct sources or one earnings-note Break; `confirmed`
symmetrically; only when `status_source != operator`. A status change is logged with the evidence
ids that caused it, so the report can show "why".

Reuse: `scripts/lib/claude_p.py` (`run`), pg connection pattern from `scripts/v3_ingest/entities.py`,
watermark/ledger pattern from `scripts/v3_ingest/sec_filings.py`, frontmatter parsing from
`scripts/chunking/chunker.py` / `scripts/metadata/schema.py`.

### 2b. Source coverage: how every channel keeps the thesis updated

The matcher is the single write path. Each source below is either already in pg/notes (wire it) or
needs a small ingest change (build it). Nothing is a new pipeline; the goal is that every channel
terminates in `evidence_log.jsonl` instead of an email.

| Source | Enters via | Cadence | Updates | Status |
|---|---|---|---|---|
| Earnings calls | reviewer note §4/§4b/§5–7 | per print (02:30 daily) | assumption status, `proposed_scores` | exists; P3 makes it assumption-aware |
| News (Google RSS + FactSet StreetAccount) | pg `doc_type='news'`, HIGH/summarized only | daily | pressure | exists; wire (P2) |
| SEC filings (8-K signal items, 10-Q/10-K MD&A, risk factors) | pg `doc_type='sec_filing'` | daily 11:00 | pressure; MD&A used for thin-input drafting | exists; wire (P2) |
| Company presentations: investor-day / conference decks | 8-K EX-99 PDF exhibits → pg | daily 11:00 | pressure | **build** (P6) |
| Conference appearances, verbatim (fireside chats, sell-side conferences) | `scripts/v3_ingest/transcript_ingest.py` (on main, not on cron) → `state/transcripts/exchanges.jsonl`; matcher reads `corprep` rows with `event_type='conference'` | weekly (Sun 09:00) | pressure; Q&A pushback flags | exists; **schedule + wire** (P2) |
| Operator-emailed transcripts / decks | `-conf-` notes via gmail poller | 15 min | pressure | exists; wire (P2) |
| Podcasts | pg `doc_type='podcast_summary'` (`scripts/v3_ingest/podcasts.py`) | daily | pressure (weight 0.5: commentary, not disclosure) | exists; wire (P2) |
| Substacks | pg `doc_type='substack_post'` | daily 10:00 | pressure (weight 0.5) | exists; wire (P2) |
| Competition (tier_4_ecosystem: Innolight, Eoptolink, Accelink, Base Power…) | pg `entity_mentions` (`affects[]`) + `foreign_filing` chunks (CNINFO) | daily 14:00 | pressure on the affected holding's assumptions (cross-ticker) | exists; wire (P2) |
| Supply-chain adjacents (manual/verified edges) | evidence at a partner/supplier/customer whose note or claim names the holding | daily | pressure, tagged `cross_ticker: true` | exists; wire (P2) |
| Insider transactions | InsiderScore `get_insider_transactions` via `claude_p.run_mcp`, 10b5-1 excluded (the load-bearing split per the COHR/LITE analysis) | weekly | counterweight signal in report §2; strength-1 evidence on `investor_interest` assumptions | **build small** (P4) |
| Consensus / guidance / surprise | Store B weekly refresh | weekly | forecast leg, credibility, consensus drift | exists; **schedule** (P5) |
| ETF flows / crowding | `scripts/etf_flows.py` triggers | daily 05:30 | report §2 context line only | exists; wire (P4) |
| Operator notes (Obsidian inbox) | `notes/inbox/*.summary.md`, `doc_type='operator_note'` | 15 min | pressure at strength 3, `status_source: operator` when the note names an assumption id | exists; wire (P2) |
| Macro signals | news `macro_signals[]` | daily | report §3 macro line; no per-assumption match | exists; wire (P4) |

Explicitly not sources: sell-side research (0 docs, parked), IR feeds (unwired), 业绩说明会/HKEX (parked).

### 2c. Keeping the thesis files current: lifecycle rules (implemented in `thesis_io.py` + matcher)

- **Quarterly reset:** when a new earnings note lands, the reviewer's §4b verdicts are applied first;
  assumptions marked Silent for 2 consecutive prints are flagged `stale_candidate` in the report.
- **Staleness:** any assumption with no evidence in 180 days is listed under "Drafts needing your eye"
  with a retire/keep prompt; nothing is auto-retired.
- **Score mirror:** each matcher run re-reads `watchlist.yaml`; if the operator changed a score, the
  `scores` mirror updates and any matching `proposed_scores` entry is cleared (loop closed).
- **Tier changes:** a name entering T1/T2 gets drafted on the next drafter run (weekly, Sun 07:00, only
  for tickers with no `_thesis.md`); a name leaving both tiers has its file moved to
  `notes/{TICKER}/_thesis.archived.md` and drops out of matching.
- **Re-draft on request only:** `draft_thesis.py --ticker X --force` regenerates a draft while
  preserving any assumption with `draft: false` or operator edits.
- **Vocabulary feedback:** reviewer §9 vocabulary candidates and matcher evidence that matched no
  assumption at strength 3 are collected into report §5 as "unassumed signal" so new assumptions
  (or themes) come from what the evidence keeps saying, not from re-reading old notes.
- **Audit trail:** every status or proposed-score change is a row in `evidence_log.jsonl` with the
  evidence ids; `_thesis.md` frontmatter is derived state and can be rebuilt from the log
  (`thesis_io.py --rebuild TICKER`).

### 3. Earnings reviewer becomes thesis-aware (`.claude/agents/earnings-reviewer.md` + wrapper)

- Step 3: fix the glob to `notes/{TICKER}/????????-[1-4]Q??.md`; **also** read `notes/{TICKER}/_thesis.md`.
- New section **4b. Assumption read**: one line per assumption id: Confirm | Challenge | Silent,
  evidence, location. (Section 4 by theme stays; the matcher treats 4b as strength-3 evidence.)
- Wrapper pre-stage: `cron_earnings_reviewer.py` writes `state/thesis/context/{TICKER}.md` before
  dispatch containing the Store B track record (query `metrics` + `metrics_credibility` directly, NOT
  the `guidance_with_track_record` view, which fans out to ~30k rows per ticker) and the ticker's open
  assumptions, so the agent (no Bash, no DB) can Read it; the one-line dispatch prompt at line 227
  gains "Read state/thesis/context/{TICKER}.md first if it exists." T3 names are dispatched too and
  have no `_thesis.md`: the pre-stage writes a context file that says so, and §4b reads "no thesis file".
  Section 8 then judges "sandbag" against the recorded track record, not just tone.
- Step 5 unchanged otherwise. Score recommendations stay advisory text; the matcher lifts them into
  `proposed_scores` in `_thesis.md`.
- P0 health: confirm the calendar step is stable (memory says 600s+retry landed 09-07 but 09-07/08 still
  failed); run one manual dispatch end-to-end before relying on it.

### 4. Report — `scripts/thesis/thesis_report.py`

**Delivery cadence** (all via `scripts/newsdigest/email_send.send`, Brevo, same address as the digests):

| When | What | Trigger |
|---|---|---|
| Weekly, Monday 06:15 ET | Full thesis-delta report (sections 1–7 below) | always, even if quiet (then it is short) |
| Daily 06:20 ET | **Thesis alert** | only if, since the last alert: an earnings note landed overnight, an assumption changed status, a strength-3 challenge hit, or a new score proposal appeared |
| Daily 15:45 ET | Thesis alert (same rule) | catches intra-day news / filings / decks matched at 15:00 |
| Quarterly, ~2 weeks after the bulk of T1 has reported | "State of theses" edition of the weekly: every name, not just movers, plus pending proposals and stale assumptions | calendar (InsiderScore `future_earnings_dates`) |

Alerts are thin: one line per event with the citation and a link to the `_thesis.md`. A ledger
(`state/thesis/alerts_sent.jsonl`) guarantees an event is announced once. Every weekly and quarterly
report is also written to `notes/reports/thesis-delta-{YYYYMMDD}.md` (vault-visible, wikilinks to
`[[COHR]]` and `[[COHR/_thesis]]`), so the history is browsable in Obsidian and retrievable in pg.
Nothing is added to the 07:00 daily digest (that duplication was removed once already).

Sections, in order:
1. **Movers** — T1+T2 ranked by thesis delta this period. Delta = weighted sum of: assumption status
   changes (±3), earnings-note score recommendations (±2 per axis), net evidence pressure (±1 per
   strength point, capped). Each row: ticker, direction, one line why, evidence count by source.
   This IS the ranking view for v1; written to `state/thesis/ranking_{date}.json` (deterministic).
2. **Per-name detail** for movers only: assumptions that changed (statement, new status, top 2
   citations with date/source), proposed vs current scores, guidance credibility (Store B: hit rate,
   sandbag index), consensus vs guidance now and change since last report (from weekly Store B
   snapshots, so drift appears from week 2).
3. **Themes** — for each theme with ≥ 2 evidence items this period across names: confirm vs challenge
   counts, top movers. Cheap cross-name rollup using the assumption→themes field; no topic modeling.
4. **Pending score proposals** — every `proposed_scores` entry not yet reflected in `watchlist.yaml`,
   with source note. The operator applies by editing the watchlist (invariant kept); a helper
   `scripts/thesis/apply_scores.py --accept T1,T2,...` prints/applies the exact YAML diff on request.
5. **Drafts needing your eye** — assumptions still `draft: true` that received their first evidence
   hit this period (review happens where it matters, not up front).
6. **Quiet names** — one line each.
7. **Coverage & health** — evidence counts by source, tickers with no `_thesis.md`, reviewer cron
   outcome summary for the week, Store B `as_of`.

### 5. Forecast leg: Store B on a weekly cron

`scripts/chunking/ingest_metrics.py` only reads cached JSON (`rows_for()`, lines 87-100, from
`state/chunk_store/factset_raw/{METRIC}_{guidance|surprise}.json`, shape `{"data":[{"requestId":"NVDA-US",...}]}`);
the pull was done by hand in an MCP session. Add a `--pull` stage that calls
`claude_p.run_mcp(mcp_tool="mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_EstimatesConsensus")` with
`periodicity='QTR', frequency='AM'`, ≤10 ids per call, parses via
`scripts/etfflows/factset_flows._tool_result_blocks / resolve_payload / rows_of` (handles the
spill-to-file case), writes the same raw files, then runs the unchanged `build()`. ≈54 calls/week
(90 names / 10 ids × 3 metrics × 2 kinds). Cron Sunday 08:00 ET; also write a dated consensus snapshot
`state/thesis/consensus_{date}.jsonl` for drift. Respect the FactSet traps in memory (`fiscalEndDate`
not `fiscalPeriod`; surprise query wrong-quarter; ADR units).

### 6. Presentations gap: PDF exhibits in the SEC channel

In `scripts/v3_ingest/sec_filings.py::fetch_ex99` (the `.pdf` skip is line 376), add an
`items: list[str] | None = None` parameter, passed from the call site in `process_filing` (~line 734,
`filing["items"]`), and take the PDF branch only when `{"2.02","7.01","8.01"} & set(items)`: download,
extract with `pypdf` (6.10.2 installed; same `PdfReader(io.BytesIO(...))` pattern as
`cninfo_filings.py:157-160`), cap at 60 pages / 120k chars, write as section `## Exhibit EX-99.N (slides)`. Deck text is bullet-heavy; the chunker's
`##`-header rule already applies. This closes the most common presentation path (investor days and
conference decks furnished on 8-K). Measure the volume increase on one week before backfilling.

---

## Phasing and files

| Phase | Deliverable | New / modified files | Depends |
|---|---|---|---|
| P0 | Reviewer cron verified healthy; auto_sync paused; crontab backed up | — | — |
| P1 | Thesis object + drafter, run on all T1+T2; COHR/LITE imported from the draft doc | `scripts/thesis/draft_thesis.py`, `scripts/thesis/thesis_io.py` (frontmatter read/write, schema), `scripts/check.py` (+validation), `scripts/chunking/store.py` (+weight) | — |
| P2 | Evidence matcher + daily cron | `scripts/thesis/match_evidence.py`, `state/thesis/{evidence_log.jsonl,watermarks.json}` | P1 |
| P3 | Thesis-aware reviewer | `.claude/agents/earnings-reviewer.md` (+ canonical copy under `plugins/agent-plugins/earnings-reviewer/agents/`), `scripts/cron_earnings_reviewer.py` (context pre-stage) | P1 |
| P4 | Weekly report + on-event alert + ranking json + crons | `scripts/thesis/thesis_report.py`, `scripts/thesis/apply_scores.py`, `notes/reports/` | P2, P3 |
| P5 | Store B weekly refresh via `run_mcp` | `scripts/chunking/ingest_metrics.py` | — (parallel) |
| P6 | PDF exhibit ingest | `scripts/v3_ingest/sec_filings.py` | — (parallel) |

Cron additions (all wrapped by `/root/bin/alert_on_failure.sh`, env via `/root/podcasts/.env`):
`0 15 * * *` match_evidence · `20 6 * * *` and `45 15 * * *` thesis_report --alerts · `15 6 * * 1` thesis_report --weekly ·
`0 7 * * 0` draft_thesis --missing-only · `0 8 * * 0` ingest_metrics --cron · `0 9 * * 0` transcript_ingest
--conferences --since-last · `30 9 * * 0` insider_pull. Sunday jobs are spaced so no two `claude -p`
batches overlap (the 429 lesson from the classifier).

Docs: update `ARCHITECTURE.md` §4/§5/§8, add `docs/superpowers/specs/2026-09-09-thesis-loop-design.md`
(this design), update `docs/cost-model.md` (≈90 Sonnet calls/day worst case for matching, most skipped;
weekly report 1 call; Store B weekly ≈54 MCP calls; drafter one-off ≈90 Sonnet calls).

## Verification

1. **Drafter gold check**: run `draft_thesis.py --ticker COHR --dry-run` and diff against
   `docs/thesis-assumptions-draft.md`; none of the eight documented over-reads may reappear
   ("remains tight", "deleveraging on track", "contained", "offsetting", "stable"). Then run all
   T1+T2; `check.py` clean; spot-read 5 names across tiers.
2. **Matcher backfill test**: run `match_evidence.py --since 2026-08-01 --ticker COHR,LITE,AAOI`.
   Expected: Accelink EML claims → `chinese_laser_capability` challenge; COHR 08-14 demand language →
   `datacom_ramp_continues` confirm; LITE tariff risk-factor → neutral/challenge on `policy_shelter`;
   no assumption flips to `challenged` on one source alone. Re-run → zero new rows (idempotent).
3. **Reviewer**: manual dispatch on the next reporting name (or replay AMBA 2Q27 with state reset);
   note contains §4b with every assumption id; §8 cites the Store B track record; prior notes found
   without dispatch override.
4. **Report**: `thesis_report.py --weekly --dry-run` renders end to end from the backfilled log;
   movers order is deterministic (run twice, diff empty); `--alerts` emits once for a status change and
   not again on re-run; email arrives via Brevo; `notes/reports/` file resolves wikilinks in Obsidian.
5. **Store B**: after cron run, `SELECT max(as_of) FROM metrics` = run date; row counts ≥ prior; one
   ticker's SALES guidance spot-checked against FactSet interactive.
6. **PDF exhibits**: one known 7.01 investor-day 8-K (pick from `notes/sec/` index) re-fetched yields a
   slides section; chunk count > 0 in pg; ingest memory stays under the 165 MB envelope noted in memory.
7. `python3 scripts/check.py` clean; crontab restored and verified; commits per phase (not swept by
   auto-sync); memory notes updated (`thesis_loop_*`).

## Open question for the operator (non-blocking; default stated)

Should the movers ranking use machine-proposed scores or only operator-applied scores?
**Default in this plan: proposed scores, clearly labelled, with applied scores shown beside them.**
Otherwise the ranking cannot move until the operator edits the watchlist, which is the loop that has
been open since June.
