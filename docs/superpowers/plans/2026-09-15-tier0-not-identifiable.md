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
`lifecycle.identified_lags`, and `LAG_MIN_N`. The report now leads with the
identified count and, below the floor, states in words that the lag is not yet
measurable. Raw figures remain in the snapshot for continuity, explicitly
labelled "not a finding".

Live output: *"Only 2 identified pair(s) … the lag is not yet measurable from
this corpus, in either direction."*

## What is answerable

**Forward-only.** `state/topics/detections.jsonl` stamps first-seen dates and
never restamps them. It is already running and is the correct instrument — it
needs elapsed time, not engineering. A pair first detected in CY2026-Q4 has a
clean left edge, because both registers were demonstrably live and silent
beforehand. The identified-pair count is now the thing to watch: when it
passes `LAG_MIN_N`, Tier 0 starts answering.

## Open, and deliberately not bundled here

```
stages {'1': 13, '2': 158, '3': 52, '4': 408}
```

408 of 631 pairs are stage 4 ("late / priced"); 13 are stage 1. A system built
to find things early reports that two-thirds of what it tracks is already
everywhere. That is either anchors too broad to isolate anything early, or a
true statement about a well-covered universe. It is a threshold/anchor-design
question, answerable now, and it deserves its own change.
