# Idea surfacing & sub-sector timeliness — design

**Status: SPEC, approved in brainstorming 2026-08-11. Nothing built.**

Answers the operator's standing question: *"how do we surface new investment ideas, or the
timeliness of a sub-sector we can invest against — and is it timely?"*

Every corpus number in §1 was measured on the droplet during the design session, not assumed.
Every external-source capability in §2 was probed live against the real API. Where something
was not tested, it says so.

---

## 1. What the corpus actually is (measured 2026-08-11)

The design is constrained by this table more than by anything else.

### 1.1 Volume by channel, keyed on publication date (never ingestion date)

| Channel | Usable span | Docs | Verdict for trend work |
|---|---|---|---|
| SEC filings | 2024-01 → 2026-08, 31 months | 4,022 | Continuous, but see §1.2 |
| News | **2026-07 → now, ~6 weeks** | 5,339 | No QoQ possible. Corroboration only |
| Substacks | 2026-06 → now | 184 | Corroboration only |
| Podcasts | 2026-06 → now | 86–100 | 23 of 61 themes only |
| **Earnings transcripts** | — | **3** | The signal the operator wants; effectively absent |
| **Sell-side research** | — | **0** | Not ingested; parked (§9) |

Date fields differ per channel and any aggregation must handle all four:
`published_date` (news, podcasts), `filed_date` (SEC), `source_date` (substacks).

### 1.2 The SEC corpus is 8-K-dominated, not periodic-report-dominated

Section census across all 4,022 SEC notes (every note has `##` headers; zero exceptions):

| Section | Count | Cadence |
|---|---|---|
| 8-K body | 2,482 | event-driven |
| Exhibit EX-99.1 | 1,710 | event-driven (press/earnings releases) |
| 10-Q Item 2 (MD&A) | 777 | quarterly |
| 10-K Item 7 (MD&A) | 309 | annual |
| 10-K Item 1A (Risk Factors) | 308 | annual |

**Consequence:** the SEC corpus is dominated by IR-authored press-release language — the
noisiest register available. It is deliberately **not** the trend substrate for this system.

### 1.3 Theme extraction is broken at the recent end

| Month | SEC docs | themeless | assigns/doc |
|---|---|---|---|
| 2026-05 | 141 | 78 | 2.26 |
| 2026-06 | 106 | **98** | **0.15** |
| 2026-07 | 64 | 44 | 1.00 |
| 2026-08 | 22 | 18 | 1.27 |

Cause is documented in `docs/sec-theme-backfill-scope.md`: `claude -p` theme extraction failed
during two subscription-OAuth outages (2026-07-01→07-08, 2026-08-05→08-09) and notes were
written with `themes: []`. 828 docs are genuinely theme-invisible.

**Scope note — this backfill is NOT a prerequisite for this project.** It was, under an earlier
design that computed heat from SEC frontmatter themes. This design computes heat from transcript
Q&A instead, so the 828 docs are off the critical path. They still matter for retrieval
(`store.search()` uses themes as a hard set-overlap filter) and should be fixed on their own
schedule.

Baseline themeless rate is 30–55% across the whole 31 months and drifting up, which is why every
metric in §5 is a **share or a count of distinct entities**, never a raw document count.

---

## 2. What the external sources actually provide (probed live 2026-08-11)

### 2.1 FactSet `ALL_TRANSCRIPTS` — the primary substrate

Verbatim text, structurally typed. Fields that carry the design:

| Field | Values seen | Used for |
|---|---|---|
| `speakerType` | `analyst` / `corprep` / `operator` | the analyst-vs-management split (§6) |
| `speakerCompanyName` | *"JPMorgan Securities (Asia Pacific)"*, *"Mizuho Securities USA"* | bank-breadth counts |
| `docNum` | `md_2`, `qna_35` | prepared remarks vs Q&A |
| `financialYear` / `financialQuarter` | `2026` / `Q2` | period key |
| `speakerName`, `speakerEntity` | *"Gokul Hariharan"* | analyst identity |
| `sentiment` | per chunk | secondary |

Confirmed coverage that InsiderScore lacks:

- **Foreign filers** — TSM (returns `2330-TW`), ASML (`ASML-NL`), Infineon (`IFX-DE`),
  El.En. (`ELN-IT`), Carl Zeiss (`AFX-DE`), and Indian small caps (`SHREEKARNI-IN`).
- **Conference transcripts, verbatim** — Mizuho Global Technology, TD Cowen Aerospace & Defense,
  Jefferies Global Healthcare. This closes the long-open `conference-transcript-ingest-path`
  item, which has been stuck on "WebFetch is summary-fidelity only" since June.
- **Non-watchlist names** — AAOI, LASR, MKSI returned content. This is also the substrate for
  novel-name discovery (§6.3).

**Do not use FactSet's `themes` field.** It returned *"Science Based Ghgs"*, *"Conflict Minerals"*,
*"Recyclable Packaging"* on a TSMC capacity discussion — it is an ESG taxonomy misfiring on tech.
Use `speakerType`, `docNum`, and the text.

**Interface constraint:** this is semantic search (`similarityScore`), not bulk export.
`limit` ≤ 50, `offset` paging, `resultsBySource` for per-source limits. Queries must be natural-
language sentences with no topic expansion beyond what was asked. Retrieval strategy in §4.1.

### 2.2 InsiderScore — secondary, for metadata only

`earnings_transcript_report` returns an **AI-generated summary**, not verbatim ("may contain
inaccurate or misstated information"). It is therefore not the text substrate. But
`earnings_transcript_info` is a cheap bulk-metadata call and provides two things FactSet does not:

- `challenging_analyze_exchanges` — a per-call count of analyst pushback, pre-computed
- an earnings **calendar** (date, quarter, sentiment) for many tickers in one call

Measured: 20 tickers → 57 transcripts over the 9-month window, ~3 per ticker. TSM and ASML
returned nothing, consistent with the `edgar_coverage: false` pattern.

**Role:** InsiderScore supplies the calendar and the challenging-exchange flag; FactSet supplies
the text.

### 2.3 Chinese A-shares — no transcripts, three other routes

A-share companies do not hold US-style earnings calls. `ALL_TRANSCRIPTS` with verified IDs
`300308-CN` / `300502-CN` returns zero, while the identical query shape returns 10 results for
`TSM-US` / `ASML-NL`. This is coverage, not an identifier problem — `docs/foreign-filings-sourcing.md`
already eliminated the ID-format hypothesis (`300308-SZ` fails; China resolves as `-CN` regardless
of exchange).

**Route A — FactSet StreetAccount (`ALL_NEWS` + `ids`).** Zero build. English, structured,
**carries sell-side consensus**, so beats/misses are measurable:
Innolight Q1'26 revenue CNY 19.50B vs consensus CNY 14.71B (33% beat); Eoptolink H1'25
CNY 10.44B vs CNY 2.73B year-ago (~4x).

**Route B — CNINFO (巨潮资讯网), China's EDGAR analogue.** Re-verified live this session:
309 Innolight announcements since 2025-01-01, HTTP 200, no key, no auth.

```
POST http://www.cninfo.com.cn/new/information/topSearch/query   keyWord=300308
  -> orgId
POST http://www.cninfo.com.cn/new/hisAnnouncement/query
     stock=300308,9900022016      # MUST be "code,orgId"; code alone returns 0
     tabName=fulltext column=szse pageSize=30 pageNum=1
     seDate=2025-01-01~2026-08-11
GET  http://static.cninfo.com.cn/<adjunctUrl>
```

Annual reports are **text-based PDFs** — `pypdf` pulled 208,079 chars from Innolight's 229-page
FY2025 report with no OCR. `claude -p` reads Chinese natively and emits English while preserving
the source phrase for audit. Measured cost: **11 thesis-linked claims for $0.1478** per
12,000-char slice.

> **Implementation warning, learned the hard way this session:** `orgId` must be resolved via
> `topSearch`, never guessed. A guessed Eoptolink `orgId` returned `totalRecordNum=0` — which is
> indistinguishable from "no filings" and would silently produce a false coverage gap.

**Route C — 业绩说明会 (results briefings).** The genuine transcript analogue. Chinese issuers
must hold results briefings and file 投资者关系活动记录表. Innolight's FY2025 briefing
announcement was found on CNINFO (2026-04-20), but that is the *notice* — the Q&A record lives on
`irm.cninfo.com.cn` (互动易), a separate platform. **Out of scope for this spec** (§9).

**Route D — HKEX.** Innolight dual-listed in Hong Kong July 2026 (H-share admission announcements
confirmed in the CNINFO feed this session). HKEX requires **bilingual** filings, so English
originals should exist, removing the Chinese-extraction step for this name. Retrieval is
unresolved — `titleSearchServlet.do` returns a well-formed empty result, almost certainly a
parameter-convention mismatch. **Out of scope** (§9), but the highest-value item in the backlog.

---

## 3. Design decisions, and why

| Decision | Rationale |
|---|---|
| **Transcript Q&A is the trend substrate**, not filings or news | Operator's judgement, and correct: Q&A is unscripted and analyst-driven. Filings/news are IR-authored |
| **FactSet for text, InsiderScore for calendar + pushback flag** | Verbatim beats AI summary; FactSet types the speaker; InsiderScore has `challenging_analyze_exchanges` |
| **The 61 themes are demoted to anchors, not deleted** | They are load-bearing (`store.search()` hard filter, chunker union) and are the only labeled history. Deleting breaks retrieval |
| **Open vocabulary comes from analyst topics, not LLM extraction over the corpus** | Costs embeddings of short phrases instead of ~4,000 `claude -p` calls against a bucket with a proven OAuth-outage failure mode |
| **9-month window, accumulate forward** | Operator's call. Backfill cost scales with window; 31 months would be 800+ transcripts |
| **Cross-sectional diffusion metrics, never trend lines** | 9 months of quarterly documents = **3 observations per company**. Velocity, slope, and seasonality are not computable and will not be faked |
| **Theme-centric ingest, not holdings-centric** | The most informative document on COHR/LITE China risk in 9 months was **AAOI's** call — a non-holding |
| **Foreign evidence (StreetAccount + CNINFO) is in scope from day one** | Without it, the blind-spot detector launches with a US-only evidence base — precisely the blindness being fixed |

### Explicitly dropped during design

- **8-Ks and news as trend inputs** — IR register, deprioritized by the operator.
- **Risk-Factor → MD&A register migration** — 308 Item 1A docs at annual cadence gives 0–1
  observations inside a 9-month window. Not a metric.
- **Retroactive clustering over 31 months** — superseded by the 9-month decision, and it pulled
  toward the 8-K-dominated corpus anyway.
- **Building the "B1" fixed-vocabulary heat metric first** — it is throwaway work; this design
  computes the same numbers better and gives new themes their history.

---

## 4. Architecture

Five components. Each is independently testable and owns one job.

```
                 ┌─────────────────────────────────────────┐
  FactSet        │ 1. transcript_ingest.py                 │
  ALL_TRANSCRIPTS│    universe -> exchanges.jsonl          │
  InsiderScore   │    (verbatim, speaker-typed)            │
  (calendar)     └────────────────┬────────────────────────┘
                                  v
                 ┌─────────────────────────────────────────┐
                 │ 2. topic_map.py                         │
                 │    exchange -> topic phrases            │
                 │    -> anchor to 61 themes | candidate   │
                 └────────────────┬────────────────────────┘
  StreetAccount  ┌────────────────┴────────────────────────┐
  CNINFO PDFs    │ 3. foreign_evidence.py                  │
                 │    -> claims.jsonl (affects: [TICKER])  │
                 └────────────────┬────────────────────────┘
                                  v
                 ┌─────────────────────────────────────────┐
                 │ 4. diffusion.py                         │
                 │    counts + lifecycle stage + detectors │
                 └────────────────┬────────────────────────┘
                                  v
                 ┌─────────────────────────────────────────┐
                 │ 5. report renderer (over newsdigest/)   │
                 │    notes/sector/heat-YYYY-QQ.md + email │
                 └─────────────────────────────────────────┘
```

### 4.1 `transcript_ingest.py`

**Universe** — resolved per run and printed, never hardcoded:
- T1 + T2 from `config/watchlist.yaml`
- plus supply-chain adjacents of any T1/T2 name from `config/supply-chain-manual.yaml`
  (provenance `manual` / `verified` only — FactSet-extracted edges are too noisy, consistent
  with the ticker-synthesis v1.6 rule)
- plus `tier_4_ecosystem` entries that have transcript coverage
- minus names with no coverage, which are recorded in a `no_coverage` list, not dropped silently

**Retrieval strategy.** FactSet is semantic search, not bulk export, so a transcript cannot simply
be downloaded. Per (company, quarter), issue a small set of broad natural-language queries derived
from the company's assigned themes, page via `offset` to `limit=50`, and dedupe on `vectorId`.
This yields **coverage of the topically relevant portion of each call, not the whole call** — a
limitation that must be stated in output (§7) and is the largest open risk (§10).

**Output** — `state/transcripts/exchanges.jsonl`, one row per retrieved chunk:

```json
{
  "vector_id": "3510330-t_3510330-t_qna_14_0",
  "document_id": "3510330-t",
  "ticker": "AAOI", "factset_id": "AAOI-US",
  "event_type": "earnings_call",
  "event_date": "2026-08-06",
  "fiscal_year": "2026", "fiscal_quarter": "Q2",
  "section": "qna",
  "speaker_type": "analyst",
  "speaker_name": "Simon Leopold",
  "speaker_firm": "Raymond James & Associates, Inc.",
  "text": "...new manufacturing of lasers coming out of China...",
  "retrieved_by_query": "...", "similarity": 0.9309
}
```

Resumable, and marks failures explicitly rather than writing empty results — reusing the pattern
from commit `b1c351aa` (`v3 SEC: mark theme-extraction failures in frontmatter + retry transient
ones`). A silent empty result is the failure mode that created the 828-doc hole.

### 4.2 `topic_map.py`

Per **analyst** exchange, extract short topic phrases, then map to the vocabulary:

1. Embed the 61 themes from `config/watchlist.yaml` as anchors (Gemini `gemini-embedding-001`,
   the existing path; ~$0.50–2/mo per `docs/cost-model.md`).
2. Embed each extracted topic phrase.
3. Cosine ≥ threshold to an anchor → inherit that theme name, preserving continuity with the
   existing 8,843 assignments.
4. Below threshold → **new-theme candidate**. Cluster candidates across the corpus; a cluster
   reaching a minimum company-and-bank count is surfaced for operator review.

**The operator names or rejects every new theme. The system never writes to
`config/watchlist.yaml`.** Tier and vocabulary changes are operator-only — the same rule that
governs tier promotion.

### 4.3 `foreign_evidence.py`

Two sub-paths, both feeding one `claims.jsonl` with an `affects: [TICKER]` mapping so foreign
claims land beside US-filing claims and route through the existing `entity_mentions` treatment in
`scripts/v3_ingest/entities.py`.

- **StreetAccount:** `ALL_NEWS` + `ids` for the six verified T4 identifiers. Structured results
  vs consensus. No new infrastructure.
- **CNINFO:** annual/interim reports; **MD&A and capacity/product sections only**, not whole
  documents. ~$0.15 per 12k-char slice, a handful of slices per report. `orgId` always resolved
  via `topSearch`. Rate-limit politely — no published cap exists.

Every claim carries the source Chinese phrase for audit, and is marked **lead to verify, not
established fact** — figures have not been checked against audited statements.

### 4.4 `diffusion.py` and 4.5 the renderer

Metrics in §5, detectors in §6, output in §7. The renderer reuses `scripts/newsdigest/` plumbing
(clustering, state-ledger dedup, source tiering, Brevo delivery) rather than building a parallel
digest.

---

## 5. Metrics — cross-sectional only

For each (topic, fiscal quarter):

| Metric | Definition |
|---|---|
| `n_companies` | distinct companies where an **analyst** raised it |
| `n_banks` | distinct `speaker_firm` values raising it — **the primary breadth signal** |
| `n_exchanges` | raw count (reported, never ranked on) |
| `denominator` | companies with transcript coverage that quarter |
| `challenging_rate` | share of raising calls flagged `challenging_analyze_exchanges > 0` |
| `first_seen` | earliest quarter observed |

Reported as: *"Neoclouds — raised at 11 of 84 covered companies by 7 distinct banks this quarter,
vs 1 company / 1 bank two quarters ago."*

**`n_banks` is weighted above `n_companies`, which is weighted above `n_exchanges`.** A topic
named by 12 companies across 4 supply-chain layers is a diffusing idea; named 40 times by one
company is that company's marketing.

**Prohibited by design:** velocity, slope fitting, smoothing, seasonal adjustment, or any
presentation implying a continuous time series. Three observations do not support them. The
metric strengthens automatically each quarter as observations accumulate.

---

## 6. Detectors

### 6.1 Detector 1 — asked-elsewhere (coverage gap)

Topic is live in analyst Q&A at a company **adjacent** to a holding (competitor / supplier /
customer per the supply-chain graph and `tier_4_ecosystem.affects`) but absent from Q&A at the
holding itself.

Live positive today, and the acceptance test (§11): Chinese laser competition was raised at
**AAOI (2026-08-06, Simon Leopold, Raymond James)** and at **LITE's Mizuho conference
(2026-06-09, Vijay Rakesh, Mizuho)** — both inside the window, neither in the corpus — while
`docs/thesis-assumptions-draft.md` records *"[GAP] — no assumption in your notes covers Chinese
competition."*

### 6.2 Detector 2 — evidence without question

Topic present in `corprep` speech, in SEC filings, or in foreign evidence (§4.3), with **zero**
`analyst` questions anywhere in the covered universe. The genuinely unasked question. Only
computable because FactSet types the speaker.

### 6.3 Lifecycle staging — the timeliness answer

The lag between evidence appearing and questions appearing is the timing signal.

| Stage | State | Read |
|---|---|---|
| 1 | Evidence exists, zero analyst questions | **Early** — window open |
| 2 | Questions at adjacent names only | **Arriving** |
| 3 | Questions at the holding itself | Consensus forming |
| 4 | Questions on most covered calls | **Late / priced** |

Worked example from the design session — Innolight FY2025 annual report (capacity +34% YoY to
28.06M units, gross margin 34.65% → 42.61%, published ~April 2026) preceded the first analyst
question (2026-06-09) by roughly two months. **Chinese optical competition is at stage 2 today.**

### 6.4 Novel-name discovery

Entity mentions inside exchanges that resolve to nothing in the watchlist, `private_drivers`, or
`tier_4_ecosystem` registries — ranked by distinct-company and distinct-bank mention counts.
`entities.py` already does alias resolution; this is its residual. Surfaced as candidates only;
**the operator decides what enters the watchlist.**

---

## 7. Output

`notes/sector/heat-{YYYY}-{QQ}.md`, plus an email rendered through the existing digest plumbing.

Required sections:

1. **Coverage statement, first and unmissable** — companies attempted, covered, and **the named
   list with no coverage** (Innolight, Eoptolink, and any other zero-transcript name). Also the
   §4.1 caveat that FactSet retrieval is topically-scoped, not whole-call.
2. **Movers** — topics by change in `n_banks` and `n_companies`, with the prior-quarter figure.
3. **Stage 1 and 2 items** — the actionable list: evidence without questions, and questions
   arriving at adjacent names.
4. **New-theme candidates** — for naming or rejection.
5. **Novel names** — unresolved entities by mention breadth.
6. **Challenging exchanges** — where analysts pushed back hardest.

**The coverage denominator is load-bearing.** A diffusion figure that says "11 of 84" while
silently excluding Innolight and Eoptolink is the AAOI trap from the `tier_4_ecosystem` comment
restated as a number. Every figure prints its denominator and its exclusions.

---

## 8. Phasing

| Phase | Deliverable | Depends on |
|---|---|---|
| **P1** | `transcript_ingest.py` — 9-month backfill + forward cron; `exchanges.jsonl` | — |
| **P2** | `topic_map.py` — anchors, mapping, new-theme candidates | P1 |
| **P3** | `foreign_evidence.py` — StreetAccount + CNINFO → `claims.jsonl` | — (parallel to P2) |
| **P4** | `diffusion.py` — metrics, detectors, lifecycle staging | P2, P3 |
| **P5** | Renderer + cron + email | P4 |

P1 and P3 are independent and can proceed concurrently.

---

## 9. Out of scope

- **Sell-side research ingest.** Parked at operator instruction. The connected tools do not carry
  it: `InsiderScore.get_research` is Verity's own notes (types Buying/Selling/Buyback/Comp/ATM),
  and FactSet `UnstructuredContent` covers filings/news/transcripts only. The analyst Q&A stream
  substitutes for most of its value. Revisit when the actual entitlement is identified.
- **业绩说明会 / 互动易 scraping** (Route C). Highest effort, least structured.
- **HKEX retrieval fix** (Route D) — highest-value backlog item; bilingual filings would remove
  Chinese extraction for Innolight entirely.
- **The 828-doc SEC theme backfill** — no longer on this critical path (§1.3). Fix on its own
  schedule for retrieval quality.
- **Any automated write to `config/watchlist.yaml`** — tiers, scores, and vocabulary are
  operator-only, permanently.

---

## 10. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **FactSet semantic retrieval is not whole-call export** — topically-scoped coverage may bias diffusion counts toward topics we already query for | **High — the largest unresolved risk** | Broad per-company query sets derived from assigned themes; measure recall against one hand-checked call before P4; state the limitation in every report |
| 3 observations per company invites over-reading | High | No trend lines by design (§5); prior-quarter figures always printed alongside |
| `claude -p` OAuth outages | Medium | Resumable, failure-marking ingest per `b1c351aa`. P3 CNINFO extraction is the exposed path; P1/P2 are not `claude -p`-dependent |
| CNINFO `orgId` guessed rather than resolved → false zero | Medium | Always resolve via `topSearch`; treat `totalRecordNum=0` as suspect until the orgId is confirmed |
| New-theme candidate churn (noise proposed as themes) | Medium | Minimum company-and-bank thresholds; operator approves every name |
| Foreign figures unaudited | Medium | Carry the source Chinese phrase; label as lead-to-verify |
| Conference transcripts inflate a bank's apparent breadth (a bank hosting a conference asks all the questions) | Low | Count distinct banks per company-event, not per exchange |

---

## 11. Acceptance criteria

The build is done when all of the following hold:

1. `exchanges.jsonl` covers T1+T2+adjacents for the trailing 9 months, and the `no_coverage`
   list explicitly names Innolight and Eoptolink.
2. **China-laser gold test.** The system independently places Chinese optical competition at
   **stage 2**, citing AAOI 2026-08-06 (Raymond James) and LITE/Mizuho 2026-06-09 (Mizuho) as the
   adjacent-name questions, and Innolight FY2025 capacity/margin data as the preceding evidence.
   This case is known-answer and must be reproduced without hand-holding.
3. Detector 1 fires on COHR/LITE for that topic — the holdings themselves show no such Q&A.
4. At least one new-theme candidate is proposed that is absent from the 61 (e.g. "Neoclouds",
   observed at NVDA Q1'27).
5. Every report figure prints its denominator and its exclusions.
6. A report renders end to end through the existing digest plumbing.
7. `python3 scripts/check.py` passes clean.

---

## 12. Open questions

- FactSet retrieval recall per call — unmeasured, and the top risk (§10). Measure before P4.
- Kaori (`8996-TW`) transcript coverage — untested.
- Whether FactSet Fundamentals/Estimates cover the T4 `fsymId`s — likely, untested; would be
  cleaner than parsing CNINFO PDFs for financials.
- Cosine threshold for anchor-vs-candidate — to be calibrated empirically against the 61 themes,
  not chosen a priori.
