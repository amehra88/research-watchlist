# News v3 — pre-LLM volume reduction (dedup + category filter + overlap cache + batch size)

**Date:** 2026-07-21
**Status:** approved design, pre-implementation
**Owner:** news v3 channel (`scripts/news_digest.py` + `scripts/newsdigest/`)

## Context — why this exists

The v3 news channel broke the morning of 2026-07-21: the `claude -p` **summarizer** hit the shared
subscription **session-limit 429** (resets 11:30am ET), had no 429 handling, plowed all ~13 batches
into the drained quota (07:46→07:48), and silently emitted a partial digest (premarket 220/250
summarized). Root cause is the standing budget problem ([[news_classifier_quota_budget_open]]):
~300 clusters/run through `claude -p` competes with interactive usage on one quota pool and drains it
before the morning reset.

An earlier recommendation (a pre-LLM **source-tier / volume gate**) was built and measured, and
**rejected**: on today's real 220 survivors it hit 14-39% false-negatives because material breaking
news is overwhelmingly a single low-tier-source cluster ("The Tech Buzz: Nvidia takes 9.3% stake in
Nebius"). And even its most aggressive config kept 362 > `MAX_CLUSTERS=300`, so the existing cap
re-trimmed to 300 anyway → **zero call relief**. See the frontier data in the quota-budget memory.

Inspecting the "duplicates" the operator flagged revealed the *real* noise, in two forms:
- **Pattern A — event-fragments:** one event reworded into many clusters (Samsung robotics ×15,
  NBIS/Nvidia stake ×11, Innolight IPO ×6, TSMC price hike ×6). A *merging* problem.
- **Pattern B — boilerplate categories:** distinct items of a low-signal class — routine 13F/ownership
  disclosures ("Swedish Pension Fund adds ADI shares" — ADI 5/5 survivors, NVDA 5/8), analyst-rating
  stubs ("DDOG Maintained by Barclays — PT $290"), template listicles ("Is X Undervalued Right Now"),
  no-catalyst price stubs. A *filtering* problem (they don't merge — different funds).

## Goal

Cut the cluster count reaching the LLM **safely** (the original's 60-70% goal, without its FN failure),
via four FN-safe levers that attack fragments, boilerplate, the duplicate morning pass, and calls/cluster.
Then lower/retire the blunt `MAX_CLUSTERS` volume cap (which itself drops material low-volume stories)
so the reduction actually reaches the LLM.

## Already shipped (this session)

**FIX 1 — summarizer 429 fast-abort** (`58ebee3`, local-only pending push). `summarize.py` catches
`SessionLimitError` → fast-abort (no retry/continue), returns `(summaries, cost, unsummarized)`;
`news_digest.py` folds `unsummarized` into the terminal fail-loud (exit non-zero + banner). Tests 3/3
(`test_summarize.py`), classifier 5/5 (no regression). This stops the silent degradation; it does NOT
reduce volume (that's this build) and does NOT fix the exit-137 email SIGKILL (orthogonal).

## Pipeline position

```
sourcing → dedup(ledger) → stage-1 cluster
  → [Lever 2] category filter        (drop boilerplate)
  → [Lever 1] stage-2 event-merge    (collapse fragments; T=0.3, post-filter)
  → MAX_CLUSTERS cap  (lowered/removed once reduction is proven)
  → LLM classify [Lever 4: batch 40] → summarize → route/render/file
```
FactSet clusters are **exempt from Levers 1 & 2** (curated per-ticker + sentiment — never gate; the
single biggest FN-safety lever).

## Lever 2 — boilerplate-category filter  (`pre_filter.py`, rewritten)

Drop clusters whose headlines match a well-defined low-signal **category** (NOT source tier). Categories,
each a high-precision title-pattern set kept in config (`config/news_sources.yaml` new block, editable):
- **institutional-holdings / 13F:** `buys|sells|purchases|acquires|reduces|increases|trims N shares of`,
  `has $X (stock) position in`, `initiates position in`, `raises/reports … holding/stake/position` +
  a fund/advisor entity. (Do NOT match "takes 9.3% **stake**" corporate disclosures — pattern must
  require the fund-action shape, not the word "stake" alone.)
- **analyst-rating stubs:** `Maintained|Reiterated by … Price Target Raised/Cut to $`, `New Buy/Sell
  Rating for`, `Earns "Buy/Sell" Rating from`. (Precision-critical: a genuine downgrade that moves the
  stock must survive; only the routine "maintained, PT nudged" template is boilerplate.)
- **template listicles:** `Is X Undervalued Right Now`, `Makes X a Strong Momentum Stock`, existing
  denylist listicle patterns.
- **no-catalyst price stubs:** `No Catalyst (Named|Specified)`, `Stock Movement … Explainer/Examined`,
  `Benchmarked Against … Peers`, `Headline Too Truncated`.

FactSet-exempt. A cluster with ANY non-boilerplate headline survives (drop only if the whole cluster is
boilerplate). Log per-category drop counts.

**Measurement (offline, no claude -p):** this filter is DESIGNED to drop clusters the LLM would keep
(ADI holdings were survivors), so "LLM-survivor dropped" is NOT the FN metric. Instead: (a) **precision
of drops** — sample the dropped set, confirm ≥95% are genuine boilerplate; (b) **hard guard** — verify
no known-material survivor class (M&A, equity stakes, earnings, product, guidance) matches any pattern.
**STOP if drop-precision <90%** (patterns too greedy).

## Lever 1 — two-stage event-merge  (`cluster.py` or new `merge.py`)

Stage 1 = current `cluster_items` (Jaccard 0.6 on raw tokens), unchanged. **Stage 2**, over stage-1
clusters, after Lever 2:
- **content signature** = `normalize_tokens(headline)` minus the block ticker's own name tokens minus
  generic corp/sector tokens (`inc/corp/electronics/stock/shares/price/analyst/earnings/…`). Strips the
  constant company name so *distinct events of the same company separate* (robotics vs job-cuts vs
  credit-card) while fragments of one event overlap strongly.
- **block** clusters by dominant queried `item["ticker"]` (free, reliable).
- **merge** within block via union-find (transitive) when content-signature Jaccard **≥ 0.3**.
- Merged cluster keeps ALL items → volume/tier go UP (better corroboration signal to the LLM).

**Line rationale (measured on today's fresh 914-cluster pool):** T=0.3 collapses the real fragmentation
(Samsung robotics ×12→1, NBIS ×11→1) at ~11% cut; the ONLY over-merge at 0.3 was template-spam
(GNW/KHC/VC/IX "Undervalued" listicles) — which **Lever 2 removes first**, so filter-then-merge makes
T=0.3 safe. Fallback T=0.4 if the post-filter over-merge gate trips.

**Measurement:** over-merge = distinct events wrongly collapsed. Eyeball the merge-groups on the
post-filter pool + a structured check. **STOP if over-merge >5%** (fall back to T=0.4).

**Known limitation (accepted):** blocking by queried ticker leaves a cross-ticker event (Nebius under
both NBIS & NVDA queries) as 2 clusters, not 1 — still ~14→2. Cross-block merge is a future refinement.

## Lever 3 — kill the premarket↔brief overlap  (verdict cache)

Today premarket classified 300 @07:16 and brief re-classified 300 independently @07:40 — two full
passes ~24min apart, both hitting the 429. Add a **content-hash verdict cache** (like the FactSet/chunk
caches): keyed on `cluster.hash` (+ prompt/model version), storing the classification. The brief (and
any run within a short TTL) reuses cached verdicts instead of re-calling `claude -p`. ~Halves morning
load; cuts tokens AND calls. Cache is per-day, in `state/`.

## Lever 4 — bigger classify batches

`classify_llm.BATCH_SIZE 20 → 40` — **classifier only** (its split-ladder recovers oversized-batch
timeouts). Summarizer stays at 20 (no split-ladder; larger batches are what broke it). Halves classify
calls on whatever remains.

## Cap

Once combined reduction is proven, lower `MAX_CLUSTERS` (e.g. 300→150) or gate it on post-reduction
count. The cap is a blunt volume-sorted drop that itself loses material low-volume stories; the levers
replace most of its job. Keep a high safety backstop, logged.

## Testing

- `pre_filter.py`: unit tests — each category pattern matches its boilerplate and does NOT match a
  curated set of real material headlines (stakes/M&A/earnings/guidance). `__main__` runner (no pytest).
- `merge.py`: unit tests — fragments merge, distinct same-ticker events stay separate, FactSet exempt,
  merged volume/items correct. `__main__` runner.
- Verdict cache: hit/miss/expiry.
- Regression: `test_classify_llm.py` 5/5 and `test_summarize.py` 3/3 still green.
- Offline end-to-end measurement on today's pool: combined reduction ratio + both FN gates.

## Success criteria & STOP gates

- Lever 2 drop-precision ≥90% (target ≥95%); Lever 1 over-merge ≤5%.
- No regression in classifier/summarizer tests; retrieval eval not made worse *by these changes*
  (note: current 13/23/24 vs 14/28/28 baseline is pre-existing news-channel corpus drift, unrelated).
- **Budget → RESOLVED only if** the measured combined reduction (levers + lowered cap) plausibly clears
  the morning session window. Otherwise the memory stays OPEN with the new evidence.

## Rollout

FIX 1 ships now (urgent, orthogonal). Levers 1-4 land as one measured build (auto_sync paused during
it, per the build-workflow policy), verified offline before any push.
