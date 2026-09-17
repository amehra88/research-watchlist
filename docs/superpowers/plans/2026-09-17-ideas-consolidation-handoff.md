# Ideas consolidation — handoff to the RIS5 session (2026-09-17)

**Decision (operator):** gap list only. This session does not edit the RIS5 spec, the
Part-A plan, or `worktree-ris5-a`. Everything below is for the RIS5 session to act on.

## The one-paragraph version

RIS5 (scored persistent ideas ledger over momentum × (1 − priced-in), valuation
first-class) and this session's work (measurement-integrity guards, transcript coverage,
a language screen) are **two layers of one system that never named each other.** RIS5
consumes this layer's outputs in three places without saying so. One of those is unsafe
until PR #6 merges. Nothing contradicts; several things are unwired; one thing is missed.

## Gap 1 — the one that matters: RIS5 scores `stages.json` before the stage fixes are all in

RIS5 reads the theme lifecycle stage through **three** paths:

- B1 momentum axis: "theme lifecycle" (spec line 40)
- B1 priced-in axis: "street attention (theme diffusion stage at the name vs peers) 15" (line 14)
- A5 `supported_growth`: durability multiplier from "mean theme lifecycle stage of the
  ticker's themes" read from `state/topics/stages.json` (Part-A line 92)

The stage values were wrong in two ways this week. **PR #5 (merged)** fixed stage 4: the
denominator was the *detection* set, so 408 of 631 pairs read "late/priced" by
construction; now 215. **PR #6 (open)** fixes stages 1/2: 61 pairs asserted "nobody
asked" about companies whose calls were never pulled — GOOGL/antitrust_action at stage 1
on a company never queried. Until #6 merges, A5 and B1 would score those 61 as real.

**Action:** merge #6 before A5/B1 read `stages.json`. Also consume the snapshot's
`stage4_not_assertable` list and `unheard` list so "no stage" is never scored as
stage 0 — it means *unobserved*, not *early*.

## Gaps 2–7

2. **"Management narrative" has no producer.** Line 15 requires two independent evidence
   families to open an idea and names "management narrative" first; A1–B3 build no
   producer for it. `state/topics/trigger_hits.jsonl` (PR #8) is it: rows with
   `role=management`, `negated=false`, weighted by rarity, `novel` flagged. Live: 217
   scored hits over 7 days, 56 watchlist / 161 market-wide.
3. **"First-to-disclose behaviour on themes analysts later ask peers about" (line 17) is
   `diffusion.newly_said`,** tested and live, being re-derived as prose in A2. Consume the
   primitive; have A2 cite it rather than infer it.
4. **§6.4 novel-name discovery was silently dropped** (RIS4 stream 6 never had a producer).
   PR #8's non-watchlist section is the producer. Add-to-tier-3 / private_driver / Dismiss
   stays operator-only.
5. **Evidence completeness is an unstated prerequisite** for any "first said" claim.
   `exchanges.jsonl` held ~57% of each call; PR #7 raises it to 85–99% (verified on six
   calls). The historical backfill was **OS-killed at 200 of ~1,460 pulls** — resume with
   `--replay-events --workers 1`, never concurrent with another `claude -p` job (the box
   carries ~2.1 GB of live Claude sessions on 3.9 GB).
6. **The RIS5 spec is untracked** — 0 commits on any branch. It is the authoritative
   definition and can vanish with a clean. Commit it.
7. **Part B has no plan file.** Ledger schema, kinds, open/close rules exist only as prose.

## Factor and weighting critiques

- **Street attention (15) treats an ordinal as interval.** Stage is 1–4 by definition,
  not a scale; "stage at the name vs peers" should be rank or categorical, never a
  linear difference.
- **"Change over 2–4 quarters" with ≤4 quarters of reads is one or two deltas,** and a
  90-day decay over quarterly data puts nearly all weight on a single read. The Part-A
  plan already gates z-scores on ≥60 daily points; apply an equivalent minimum-history
  gate to momentum and say "trend needs N more quarters" on the card.
- **"Re-fit weights from ledger outcomes"** on ~68 tickers × 4 quarters is the
  overfitting the earnings-call literature warns about (LLM/sentiment signals do not
  survive short-horizon prediction). Report 1/3/6-month outcomes; do not auto-refit
  until N is large.
- **The two-family rule can be satisfied by one family twice.** "Street" (revision
  breadth) and "street attention" (diffusion stage) are both sell-side. Define the
  families so those two count as one.
- **Valuation gap at 60 lets one bad input move the whole axis.** FactSet surprise
  fields have documented per-field corruption (memory: `surpriseBefore + surpriseAmount
  ≠ surpriseAfter` on several issuers). Run that identity check on ingest before anything
  reaches the reverse-DCF.

## Data sources you can use now

- **InsiderScore `search_filings` with `formtypes=["TSCRIPT"]`** reaches complete
  transcript bodies sentence-by-sentence, with speaker, firm, `basetype`
  (presentation vs Q&A), deep links; market-wide, mcap/date filtered. Already connected.
  `get_filing_content` on a transcript iacc returns `{}` — search is the only route.
- **2,658 analyst-question → management-answer pairs** already in `exchanges.jsonl`
  (72% of analyst turns have their adjacent answer). Q↔A cosine = an evasion measure —
  the strongest "management narrative" signal in the literature, needs no phrase list.
- **Analyst-engagement decline:** distinct asking firms per call; a fall precedes
  underperformance. 42 of 64 tickers have ≥3 covered events.
- **Cross-company naming:** `supply-chain.yaml` (8,756 edges) + `entities.py` alias
  resolution turn a named customer/supplier into a graph edge.
- **Do not use FactSet's `sentiment` field:** 2,753 Neutral / 1,266 empty / 24 signed
  across all analyst turns.
- **FactSet MCP has no document fetch** — 22 tools, `UnstructuredContent` is "vectorized
  data" by FactSet's own description. Full transcripts are a separate paid product
  (Documents Distributor); own-MCP buys nothing.

## Failure modes seen this week — every one in a single day

- **The observation process mistaken for the phenomenon**, three times: window edges
  read as market timing (Tier-0 lag: 34% → 86% → n=1 depending on correction); the
  detection set read as relevance (stage 4); absence of data read as silence (stage 1/2).
  Any new factor that counts over an uneven universe inherits this. Gate every negative
  claim on "was this actually observed".
- **A universe step-change looks exactly like diffusion.** Adding tier 3 (111 tickers)
  to the transcript universe would jump every cross-sectional count and burn once-ever
  alert ids. PR #6 records universe size per snapshot; consume it.
- **Negation.** About a third of "step function" hits negate it. Any language-derived
  factor needs a negation gate or it scores "not a step function" as bullish.
- **Document-level boolean.** `search_filings` matches at document level; post-filter on
  the returned snippet or precision collapses silently.
- **Memory.** Three `claude -p` workers plus one more job OOM-kills on this box.

## Two boundaries to keep

- RIS5 measures momentum as change in *score reads*; spec §5 forbids slopes on
  *diffusion counts*, and RIS5 keeps `diffusion.py` count-only. Compatible by design —
  keep it so.
- This is a **timeliness tool**, not a return predictor. The moment an idea is framed as
  predicting returns, the entire disconfirming literature applies and the sample cannot
  support it.

## Where the detail is

PRs #6, #7, #8 (this repo). Write-ups:
`docs/superpowers/plans/2026-09-15-tier0-not-identifiable.md`,
`docs/superpowers/plans/2026-09-15-transcript-coverage-saturation.md` (branch
`transcript-coverage-findings`). Memory: `idea-surfacing-p2-p3b-state.md`.
