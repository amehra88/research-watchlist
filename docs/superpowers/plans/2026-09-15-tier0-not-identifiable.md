# Tier 0 is not identifiable from the current corpus (2026-09-15)

The daily chain reports a lag distribution that looks like a falsification of
the system's core premise:

```
lag {'n': 53, 'median': -4, 'p25': -77, 'p75': 174,
     'n_negative': 31, 'share_evidence_led': 39.6}
```

Read naively: companies disclose *after* the street asks, 60% of the time. That
would gut the premise the whole system rests on.

**It is not a market finding. It is the edge of the corpus.**

## The measurement

Recomputed independently from `state/topics/topic_map.jsonl` (73 pairs on a
slightly looser join than lifecycle's 53 — same shape: median −1, 34.2%
evidence-led).

For each (theme, ticker) pair carrying both registers, take the earliest date
at which either register mentions the theme, and compare it to the point where
**both** registers are live for that ticker:

```
days from "both registers live" to the pair's FIRST mention (n=73):
  min=-272  p25=-93  median=-29  p75=-1  max=0
  73 of 73 pairs first appear AT OR BEFORE the window opens
```

**All 73.** There is not one pair where both channels were observed quietly and
a topic then appeared. Every "first mention" is pinned to when ingestion
starts, so the lag is measuring the window boundary, not the market.

## Why, structurally

1. **The themes predate the corpus.** The anchors are broad and durable —
   `semiconductor_cycle`, `cybersecurity_competitive_landscape`,
   `lithography_roadmap`. These were being discussed long before 2025-11.
   "First evidence" for such a theme is unmeasurable from a 10-month window;
   the true first mention is off the left edge for every one of them.

2. **Coverage starts at different times per ticker.** 21 of 51 tickers have
   MD&A coverage beginning >30 days after their call coverage (CRWD +93d,
   IOT +102d, AAOI +79d). Those tickers can only ever produce negative lags,
   and they are exactly the names driving the tail (AMAT −189, CRWD −184).

3. **The evidence side is sampled ~3 times per ticker** over ~10 months. So
   "when did management first write this" resolves to about a quarter — while
   the effect being hunted (the spec's Innolight anecdote) is ~2 months. The
   measurement error is larger than the signal.

Note the call→filing offset is NOT the explanation: filings land a median of
**+1 day** after the call, so the two events are near-simultaneous. The problem
is the window, not the anchor event.

## What this does and does not say

- It does **not** say evidence fails to lead questions. That remains untested.
- It does say the retrospective framing cannot answer it, and no amount of
  additional compute over this corpus changes that. The quantity is not
  identifiable from the data, which is a different problem from an expensive
  one.

## What is answerable

**Forward-only.** `state/topics/detections.jsonl` already stamps first-seen
dates and never restamps them. That is the correct instrument and it is
running — it needs elapsed time, not engineering. A topic first detected in
CY2026-Q4 has a clean left edge, because both registers were demonstrably live
and silent beforehand.

Two things would sharpen it:

- **Report the censoring, don't hide it.** The diffusion email should carry the
  lag with an explicit caveat, or suppress it until pairs clear the window
  edge. A number that looks like a falsified premise should not ship unlabelled
  in a daily report.
- **Gate the lag on window clearance.** Only count a pair whose first mention
  is ≥60d after both registers are live for that ticker. Today that yields
  n=0, which is the honest answer, and it will start producing pairs as the
  corpus lengthens.

## Separately: the stage mix is worth a look

```
stages {'1': 13, '2': 158, '3': 52, '4': 408}
```

408 of 631 pairs are stage 4 ("late / priced"); 13 are stage 1. A system built
to find things early is reporting that two-thirds of what it tracks is already
everywhere. That is either anchors too broad to isolate anything early, or a
true statement about a well-covered universe — and it is answerable now,
unlike the lag.
