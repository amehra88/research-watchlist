# Topic-space findings — does MD&A land where analyst questions land?

*Measured 2026-08-21, before building P2 Tasks 4–6. Prompted by the operator's
concern that extracting topics from all MD&A prose "might explode the number of
topics, which could have downstream impact."*

The concern is right to raise and the measurement says the risk is **real but
inverted**: MD&A does not explode the topic space, it *collapses* into it —
wrongly. That is a worse failure mode, because an explosion is visible in the
review queue and a misfiling is invisible in the metrics.

## Why topic count is the wrong thing to fear

Topic count per se is not what breaks. Three things downstream are sensitive,
and all three are sensitive to *mismatch*, not to *count*:

1. **The §5 diffusion metrics are cross-sectional counts** (`n_banks` >
   `n_companies` > `n_exchanges`). Their power comes from many companies sharing
   *few* topics. A sparse space makes every `n_companies` = 1 and nothing ever
   crosses a threshold.
2. **The §6.2 gap detector** fires on "evidence exists, nobody is asking". If
   MD&A grows a private vocabulary disjoint from analyst vocabulary, *every*
   MD&A topic has zero questions and the detector fires on everything.
3. **The operator review queue is one person.** Hundreds of candidate clusters
   is operationally the same as none.

## Method

400 MD&A claim texts (sampled from the 8,251 in `state/evidence/claims.jsonl`,
9-month window) and 400 analyst utterances >60 chars (from
`state/transcripts/exchanges.jsonl`), embedded with `gemini-embedding-001`
against the 62 `watchlist.yaml` theme slugs as anchors. Best cosine per unit.
Probe: `topic_space_probe.py` (job scratch, not committed).

## Results

Best cosine to the nearest of the 62 themes:

| | p05 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|---|
| MD&A | 0.698 | 0.716 | 0.730 | 0.745 | 0.780 |
| analyst | 0.720 | 0.741 | 0.756 | 0.773 | 0.801 |

Share landing above threshold (i.e. inheriting an existing theme):

| threshold | MD&A | analyst |
|---|---|---|
| 0.70 | 93.8% | 98.5% |
| **0.72** | **68.0%** | **95.0%** |
| 0.75 | 18.0% | 61.3% |
| 0.80 | 1.8% | 5.2% |

Distinct nearest-themes touched: **MD&A 28 of 62, analyst 40 of 62.**

## Reading

**1. MD&A is narrower than analyst questions, not broader.** 28 themes vs 40.
The vocabulary-explosion hypothesis is not supported. Whatever else is wrong,
MD&A will not flood the operator with novel topics.

**2. The real defect is silent misfiling.** The twelve lowest-scoring MD&A
blocks are all accounting, liquidity, and legal housekeeping — and every one of
them was still assigned a confident-looking nearest theme:

| block | nearest theme | cosine |
|---|---|---|
| "Our corporate website is located at www.mongodb.com…" | `data_center_deployment_constraints` | 0.672 |
| pension plan funded status / actuarial assumptions | `ai_generated_content` | 0.683 |
| 4.00% convertible senior notes due 2031 | `ai_generated_content` | 0.689 |
| total minimum lease payments $152.3 million | `ai_generated_content` | 0.688 |
| uncertain tax positions $199.7 million | `data_center_deployment_constraints` | 0.693 |

At threshold 0.70, 93.8% of MD&A "inherits" a theme — which means pension
accounting is filed under `ai_generated_content` and counted in its diffusion.
`n_companies` for a theme then measures how many filers discuss convertible
notes. **That corrupts the metric without producing a single visible symptom.**

**3. The threshold is a razor's edge.** MD&A inherit rate runs 93.8% → 68.0% →
18.0% across 0.70 → 0.72 → 0.75. The whole distribution is 0.08 wide. A single
global `SIM_THRESHOLD` with a "60–80% inherit" calibration target is
under-specified: 0.72 hits the target, but with no margin on either side.

**4. Signal genuinely exists, at the top of the distribution.** The highest
scorers are exactly the thesis-relevant prose: semiconductor cycle (0.868),
`ai_infrastructure_capex` on "cash paid for property and equipment was $7.7
billion" (0.805), `hyperscaler_revenue_concentration` on "Data Center net
revenue of $16.6 billion increased 32%" (0.796). The component is worth
building; it is the assignment mechanism that needs work.

## Probe limitations — stated so the numbers are not over-read

- **This embedded whole blocks, not extracted phrases.** The plan's Task 4
  extracts a short topic phrase via `claude -p` *before* embedding. A 4-word
  phrase against a 3-word anchor should separate far better than a 1,500-char
  passage against a 3-word anchor, so the compression above is partly an
  artifact. It does establish that the block-level shortcut is unusable, which
  makes Task 4's extraction step load-bearing rather than optional.
- One sample, one seed, n=400 per register.
- The MD&A sample comes from the diff-survivor claims file, not from all prose.

## Recommendations

**R1 — Add a register filter before extraction (highest leverage).** Drop
accounting, liquidity and legal-housekeeping prose — pension, convertible notes,
lease commitments, uncertain tax positions, contractual obligations, revenue
recognition policy, prospectus mechanics, corporate-website boilerplate — before
spending a `claude -p` call on it. This removes the misfiling risk at its source
*and* cuts extraction spend. It cannot be replaced by a higher threshold,
because this prose appears in every filer, so the existing
`MIN_CANDIDATE_COMPANIES = 3` gate passes it happily.

**R2 — Require an assignment margin, not just a threshold.** If best and
second-best anchors are within ~0.02, the assignment is noise: treat as
candidate rather than inherit. Directly targets the observed failure, where
unrelated prose lands on an arbitrary theme by a hair.

**R3 — Calibrate on phrases, and record the curve.** Recompute this table on
extracted phrases and keep the inherit-rate-vs-threshold curve in the repo, so
the chosen value is auditable and its sensitivity visible. Do not fix a value
against the current corpus alone — coverage is still partial and
optical/networking-skewed.

**R4 — Keep "newly said", at the topic level.** It is what the operator wants
and it is *structurally more robust* than raw counts, for a reason worth stating
plainly: **anything that recurs every quarter can never register as new.**
Boilerplate recurs every quarter by definition. So even where R1 and R2 leak,
misfiled housekeeping is misfiled *consistently*, appears in the baseline, and
never fires the novelty signal. Topic-level novelty is partially self-immunising
against exactly the defect this probe found. Raw diffusion counts are not — R1
is still required for them.

**R5 — Baseline depth: 2 prior quarters.** A `(filer, topic)` pair is newly said
when absent from that filer's two previous MD&As. Reading more history costs
nothing (notes are on disk, no API), so read ~24 months and emit for the
9-month window, giving every filer a full baseline instead of only the most
recent quarter.

## Infrastructure blockers found on the way — both must be fixed before Task 6

- **`embed()` reloads and re-serialises a 334 MB JSON cache on every call**
  (`scripts/chunking/embed.py`). A batched bulk pass spends all its time in
  `json.dumps`. Killed a probe run at exit 137. Load once and pass through, or
  give the topic path its own cache.
- **Embedding is one API call per text, ~2.4 s.** Measured 100 embeddings per
  ~4 minutes. At ~16,000 phrases that is ~10.7 hours. Needs the batch
  embedding endpoint before Task 6 is runnable.
