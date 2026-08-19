---
name: ai-application-layer-screen
description: Use when assessing whether a company is genuinely "AI-powered" or AI-washed, screening for AI application-layer investment candidates, evaluating an AI product claim in a filing or earnings call, or running and interpreting the quarterly EDGAR AI screens in scripts/screens/
---

# AI Application-Layer Screen

## Overview

Separates companies where AI is load-bearing from companies that merely mention AI. Core principle:
**delete the model — does the product still exist and still sell?**

Worked analysis and per-name defenses: `docs/ai-application-layer-screen.md` (heavy reference — read
it for the examples, not for the method).

## When to Use

- "Is X really an AI company?" / "Is this AI-washing?"
- Screening for AI application-layer candidates outside semis and hyperscalers
- Interpreting output from `scripts/screens/` (quarterly EDGAR scans)
- Evaluating an AI product claim in a 10-K, 8-K, or earnings transcript

Not for semiconductor or hyperscaler analysis — that is an infrastructure thesis, not an
application-layer one.

## The Two Archetypes

Classify before comparing. They carry different risks and different disconfirming evidence.

| | **A — Model-native** | **B — Corpus + technical leadership** |
|---|---|---|
| Model deleted | No product | Product survives intact |
| Moat | Labeled proprietary corpus + regulatory or reimbursement gate | Owned data + leadership that actually rewires the org |
| Revenue | Inference *is* the line item | AI shows up as margin before it shows as a SKU |
| Fails when | A frontier model commoditizes the task; the corpus proves replicable; the payer says no | The data is legally the customer's; gains compete away; an agent layer disintermediates the UI |

**Highest-value pattern:** B sitting on a corpus that can convert to A — the Axon shape. Become the
system of record first, then sell model-native product to the same buyer through the same
procurement cycle.

## The Four Tests

Ordered by how hard each is to fake. Weight accordingly.

| # | Test | Source | Fakeable? |
|---|---|---|---|
| 1 | Named product, priced, replacing something | Product and pricing disclosure | Very hard — customers must pay |
| 2 | Quantified AI revenue, or inference in COGS | 10-K / 10-Q full text | Hard — audited |
| 3 | Senior AI officer named in a filing | 8-K Item 5.02, DEF 14A | Moderate — real cost, but can be defensive |
| 4 | Delete-the-model reasoning | Analysis | N/A — judgment, not evidence |

Use 4 to generate hypotheses and 1–3 to test them. **A name passing only test 4 is a story, not a
finding.**

## Negative Screen — disqualify when

1. The AI is a vendor API in a wrapper — no data edge, and gross margin falls rather than rises.
2. The data belongs to the customer; contracts forbid cross-tenant training.
3. Agents were announced, but nothing was repriced and nothing shrank. Conviction shows up as a price
   change, a changed pricing *unit*, or lower headcount. None of the three means it is a demo.
4. The AI SKU sells to the same buyer out of the same budget — a feature defending existing revenue,
   not a product creating new revenue.

**Also check the mirror:** when the moat is workflow and seat count rather than data, the company is
the layer being disrupted, not the application layer.

## Required Output Format — one block per name

Never assert a name is AI-powered without all five parts. The counter-argument is not optional; a
list where nothing fails reads as unfiltered.

```
**TICKER — Name** [industry]
- The inference:        what specific inference actually runs
- The corpus:           what trains it, and why a competitor cannot obtain it
- Delete the model:     what is genuinely left
- Best counter-argument: the strongest skeptical case — then rebut it or concede it
- Defense strength:     Strong / Moderate / Thin
```

Grade AI-centrality and business quality **separately** when they diverge — they often do. A name can
be perfectly model-native and a poor business, or an excellent business with a thin AI claim.

## Running the Screens

```bash
scripts/screens/run_ai_screens.sh     # both scans, then diff vs the previous run
```

Interpreting output — **rarity is precision.** Calibrated Aug 2026: "artificial intelligence" appears
in ~4,194 10-Ks (~60% of filers — useless), while "AI revenue" appears in 5 (~0.3% — near-perfect).
Screen the rare tail and ignore the common vocabulary. New filers crossing into that tail are the
leading indicator.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Ranking by keyword frequency | Frequency measures talking. Weight phrases by disclosure cost. |
| Trusting a phrase match | Check collisions — apartment REITs hit "AI revenue" via *"AI revenue management"* pricing software. |
| Treating the officer screen as complete | It only sees Section 16 officers: high precision, poor recall. It misses VP-level AI hires entirely. |
| Running the screen without a size filter | The tail is full of sub-$50m shells with "AI" in the name. The filter is the part that cannot be automated. |
| Conflating archetypes A and B | They fail differently. Classify first. |
| Skipping the counter-argument | Then it is not a defense, it is a pitch. |

## Status

Framework validated against a 28-name worked screen (see heavy reference). **Not subagent
pressure-tested** — treat this as a reference/pattern skill, not a discipline-enforcing one.
