# Tier 0 is not identifiable from the current corpus (2026-09-15)

The daily chain headlined a lag distribution that reads as a falsification of
the premise the whole system rests on:

```
lag {'n': 53, 'median': -4, 'p25': -77, 'p75': 174,
     'n_negative': 31, 'share_evidence_led': 39.6}
```

Read plainly: companies disclose *after* the street asks, ~60% of the time.

**It is not a market finding. It is the edge of the corpus.**

## The evidence: the same data gives three opposite answers

Measured on the live map (73 pairs on the looser join, 53 under the pipeline's
MD&A block rule — same shape either way):

| correction | n | median | evidence-led |
|---|---|---|---|
| raw, uncorrected | 73 | −1d | **34.2%** |
| drop only the censored *negative* lags | 29 | +174d | **86.2%** |
| guard applied in **both** directions | 1 | −1d | — |

A quantity that moves from 34% to 86% to nothing depending on which defensible
correction you pick is not measured. That instability is the result.

**The middle row is the trap, and it is worth naming.** Censoring obviously
threatens negative lags — "the analyst asked before the company wrote it" is
untestable if MD&A was not yet being ingested — so guarding only those feels
principled. It isn't. It discards exactly the observations that disagree with
the premise, and it is the single easiest mistake to make here. The mirror case
is just as real: a late-starting call register hides an earlier question and
makes a positive lag spurious.

The rule now shipped: a pair counts only if the register that produced the
**second** event was already under observation, by 30 days, when the **first**
event happened.

## Why the corpus cannot answer it

1. **The themes predate the corpus.** The anchors are broad and durable —
   `semiconductor_cycle`, `cybersecurity_competitive_landscape`,
   `lithography_roadmap`. Their true first mention is off the left edge for
   every ticker, so "first evidence" is unmeasurable from a 10-month window.

2. **Coverage starts at different times per ticker.** 21 of 51 tickers have
   MD&A beginning >30 days after their call coverage (CRWD +93d, IOT +102d,
   AAOI +79d). Those names produce the *entire* negative tail — AMAT −189,
   CRWD −184. The global window spans in the old report note understate this
   badly; the binding constraint is per-ticker.

3. **The evidence side is sampled ~3 times per ticker** over ~10 months, so
   "when management first wrote this" resolves to about a quarter, while the
   effect being hunted (the spec's Innolight anecdote) is ~2 months. The
   measurement error exceeds the signal.

Ruled out: the call-vs-filing anchor. Filings land a median **+1 day** after
the call, so the two events are near-simultaneous and anchoring is not the
problem. The window is.

Also ruled out: the handful of pairs that survive a naive guard. All four were
same-day call/filing coincidences sitting exactly on a coverage boundary (FPS,
DASH, ZS, HPE) — they passed only because `lag == 0` is neither positive nor
negative and an `if/elif` guard skipped it.

## What this does and does not say

- It does **not** say evidence fails to lead questions. That is untested.
- It does **not** say evidence *does* lead. The 86.2% is an artifact of a
  one-sided correction.
- It says the retrospective framing cannot answer the question, and no extra
  compute over this corpus changes that. **Unidentifiable is a different
  problem from expensive.**

## What shipped

`lifecycle.coverage_starts`, `lifecycle.lag_is_identified`,
`lifecycle.identified_lags`, `SAME_EVENT_DAYS` and `LAG_MIN_N`. The report now leads with the
identified count and, below the floor, states in words that the lag is not yet
measurable. Raw figures remain in the snapshot for continuity, explicitly
labelled "not a finding".

Live output: *"Only 1 identified pair … the lag is not yet measurable from
this corpus, in either direction."*

## Review pass (same day): two corrections to the guard above

**A same-day filing is one reporting event, not a response.** One of the two
pairs the guard first called identified was AMBA — filed 2026-09-04, asked
2026-09-03, lag −1. That is the 10-Q that accompanies the call, not a company
reacting to an analyst. Half the surviving sample was the reporting calendar.
The corpus-wide call-to-filing offset for the same quarter is median +1d
(p25 0, p75 2), so pairs within 3 days now get their own bucket — kept apart
from the censoring counts, because they are well observed and simply carry no
timing content. 5 of 53 pairs. Identified pairs: 2 → 1.

Consequence worth stating: Tier 0 now measures leads and lags **longer than
one reporting cycle**. Simultaneous disclosure is out of scope by
construction, not missing from the data.

**The actionable finding, which the statistics were burying.** 20 of 63
tickers with any call coverage have their *first* observed call within the
last 45 days — one call, no question history at all. Nothing about those names
can be identified in either direction, and they account for 21 of the dropped
positive pairs (HPQ, PANW, HPE, NXPI, RDDT). This is a **transcript-backfill
gap, not a statistical one**: more call history moves the identified count,
more statistics does not. It is the cheapest lever on Tier 0 becoming
answerable sooner than "wait a year".

Current accounting: 1 identified + 26 negative-censored + 21 positive-censored
+ 5 same-event = 53 pairs.

## What is answerable

**Forward-only.** `state/topics/detections.jsonl` stamps first-seen dates and
never restamps them. It is already running and is the correct instrument — it
needs elapsed time, not engineering. A pair first detected in CY2026-Q4 has a
clean left edge, because both registers were demonstrably live and silent
beforehand. The identified-pair count is now the thing to watch: when it
passes `LAG_MIN_N`, Tier 0 starts answering.

## FIXED (2026-09-15, follow-up): stage 4 was degenerate

```
stages {'1': 13, '2': 158, '3': 52, '4': 408}
```

408 of 631 pairs are stage 4 ("late / priced"); 13 are stage 1. This is not
anchors being too broad — it is a denominator bug.

`stage()` calls a theme stage 4 when it is asked at >= 3 tickers **and** at
more than half of `covered`, where `covered` is the set of tickers for which a
(theme, ticker) pair exists in the index. But a pair only exists where the
theme was *detected*. So for any theme the evidence side never matches,
`covered == asked` and the majority test cannot fail:

| theme | asked | covered | ratio | mdna |
|---|---|---|---|---|
| inference_compute_economics | 22 | 22 | 1.00 | 0 |
| hyperscaler_capex_buildout | 20 | 20 | 1.00 | 0 |
| enterprise_ai_adoption | 16 | 16 | 1.00 | 0 |
| ai_compute_topology | 15 | 15 | 1.00 | 0 |
| thermal_management_cooling | 14 | 14 | 1.00 | 0 |

**24 of the 40 stage-4 themes have zero MD&A evidence anywhere, and 28 of 40
sit at a ratio of exactly 1.00** (median across all stage-4 themes: 1.00).
"Late / priced" is being assigned by construction to themes that are simply
invisible to the evidence side.

The denominator should be the companies where the theme *could have been*
observed — those with call coverage in the window — not the companies where it
*was* observed. With the current definition, thin evidence coverage is
indistinguishable from broad analyst saturation, and the two have opposite
meanings for an operator.

### The fix

The denominator is now the companies where the theme is **relevant** and whose
call we **actually heard**. Relevance comes from two sources that do not depend
on who asked: the operator's per-ticker `themes:` in `watchlist.yaml` (157 of
191 entries carry one; all 50 tokens are anchor slugs), and companies that
disclosed the theme without being asked — the §6.2 gap itself.

Intersecting with heard calls cuts both ways, which is how you know it is the
right restriction: it stops a theme being held back from stage 4 because *we*
never ingested a call, and it is why `ad_market_strength` legitimately **rises**
to stage 4 — 3 of its 10 "covered" names were names we never heard.

**Result: stage 4 408 → 215, stage 3 52 → 245.**

Where relevance is unknown the claim is vacuous, so stage 4 is *not assertable*
and the pair is held at 3. The 21 affected themes are named in the report:
holding them at 3 for an unexplained reason would just trade a wrong number for
a mysterious one, and assigning them in `watchlist.yaml` is the concrete lever
that makes stage 4 computable for them.

### Two consistency traps found while wiring it

- `pairs` in the snapshot still called `lc.stage()` without the new
  denominator. That is what `stage_alert` diffs and `theme_notes` renders, so
  the snapshot would have disagreed with its own `stage_counts`.
- `stage_alert.render` computed `n = len(pairs)` itself — the legacy detected
  set. The live dry-run printed *"asked at 5 of 10 covered names"* as the
  justification for stage 4, a ratio that does not clear the >half rule it
  claims to have met. The denominator is now published in the snapshot and
  quoted from there.

### Migration

None needed. `diff_events` absorbs downgrades silently (`if st <= was:
continue`), so the 193 pairs moving 4→3 emit nothing. The live dry-run produces
exactly one event: the genuine `ad_market_strength` upgrade.
