# Tiers 4 and 5 — review

2026-08-21. Completing the one-by-one walk after tiers 1–3. **27 names**: 18 in tier 4
(score 45–60, "AI real but not load-bearing") and 9 in tier 5 (<45, "thin").

Two things to settle before the names.

---

## 1. The cap did not delete anything

Tier 5 sits entirely below the top-50 cap set last session, along with nine tier-4 names
(WAY, VRSK, CGNX, ZBRA, INOD, KVYO, INTU, DOCU, MA). The cap is a **report boundary, not a
deletion** — the ranker now emits everything below the floor as a classified list, so any
name here can be argued back up without re-running a screen.

## 2. The bigger finding: the score stops working below ~60

Five names tie at **exactly 52.7** — NU, WAY, VRSK, CGNX, ZBRA — with identical judgment
vectors (centrality 2/5, product 2/3, ml_content 2/3). Their order is a tie-break artifact.

That is not a ranking. It is a bucket wearing a rank number, and I should not have shipped
it as an ordered list. The axes are small integers, so the bottom of the distribution
collapses into a handful of repeated combinations.

Worse than the false precision is what the number **implies**. A score of 52.7 reads as
"about half as good as Hinge Health." That misdescribes what these companies are. They are
not weak versions of tier 1 — they are *different objects* that fail the thesis for reasons
that do not compare to each other. Intuitive Surgical, which owns the best unconverted
corpus in med-tech and needs one priced product to graduate, is not 1.8 points better than
Cognex, which will never convert because its product is classical vision. One of those is a
watch-list name with a trigger. The other is permanently disqualified.

**So below 60 the algorithm now stops ranking and starts classifying.** The reason code is
the output. Six reasons, and each implies a different action.

---

## Group 1 — corpus unconverted *(the only group that can graduate)*

Owns genuine ground truth; has not turned it into a model-native product sold at a price.
These are watch names, and the trigger is a **priced product**, not a press release.

**ISRG (57.9)** — the strongest name in either tier and the clearest Axon shape on the list.
Largest surgical video corpus anywhere, paired with synchronised instrument telemetry, which
is the part nobody else can assemble. The business is excellent independent of any of this:
revenue +18.5% YoY to $2.89bn, gross margin 66.3%→67.8%, operating margin 30.5%→33.6%. There
is no AI revenue line. Own it for the robot; the corpus is a free option. **Trigger: a
reimbursed AI SKU.**

**V (54.5)** — the transaction graph is among the most valuable behavioural datasets in
finance and there is a real agentic-commerce surface being built. But the network survives
entirely untouched without any model, which caps centrality at 2. Not an AI trade.

**VRSK (52.7)** — pooled claims data contributed by competing carriers over decades is a
natural monopoly no entrant can recreate. The genuinely new part is computer vision on aerial
property imagery replacing physical field inspection. That is the piece to size.

**INTU (50.9)** — owns tax returns and small-business ledgers *outright*, not held in trust,
which is a materially better ownership position than most of this list. Moving from software
that helps you do the work to agents that do it attacks the accountant's fee pool rather than
a software budget. Lab-encroachment 2/3.

**DOCU (50.4)** — plausibly the largest corpus of executed agreements in existence. Trying to
convert a signature utility into agreement intelligence. Repo traction near zero, so the
conversion is a hypothesis, not a result. Lab-encroachment 3/3 — this is precisely the corpus
a frontier lab would like to sit on top of.

**MCO (32.8)** — excellent ratings and credit corpus, research assistant layered on it, AI not
yet doing the commercial work.

**TYL (25.5)** — records and workflow for local government. Included only as watch-for-conversion:
it owns a civic corpus that could plausibly become model-native. Nothing today.

## Group 2 — claims exceed traction *(the screens catching something)*

The filing says one thing, the practitioner evidence says another. This group is the
cross-signal layer paying for itself — these are names the screens **caught**, not found.

**MORN (44.1)** — topped the MCP *filing* screen with 22 mentions, ahead of FactSet's 12. Public
repo: 21 stars, 338 days since last push. I recommended this name earlier as "arguably the
better business" and the traction data contradicted me; the retraction stands.

**KVYO (51.3)** — cross-merchant behavioural prediction is a genuine aggregation no single
store could achieve. Thin repo traction, and platform dependency on Shopify.

**FDS (55.1)** — flagged by the same rule, and it is a **false positive**. The MCP server is
real, it is simply not on public GitHub, so a GitHub-traction screen cannot see it. Worth
stating plainly because it shows the flag's failure mode: it cannot distinguish "no traction"
from "traction I have no instrument for."

## Group 3 — classical, not learned *(does not convert)*

An algorithm is the product, but it is not modern learned ML. This is the `ml_content` axis
doing its job — the same distinction that demoted FICO.

**CGNX (52.7)** — deep learning genuinely opened inspection tasks classical vision could never
handle. But that capability is commoditising from above, and the durable moat is optics and
channel, not data.

**ZBRA (52.7)** — machine vision and scanning across warehouse and retail; closer to classical
than learned.

**MA (47.1)** — Decision Intelligence scores fraud across an exceptional graph. The network is
not an AI business and would operate without it. Same verdict as V, one tier lower on product.

**ALGN (43.7)** — millions of completed orthodontic cases is a real dataset, but I walked back
the stronger claim and it stays walked back: Align staged aligners with human planners for two
decades, so automated planning is a labour-cost story, not proof of centrality.

**SYM (25.5)** — orchestrating bots is largely optimisation and control, not learned policy.
Severe customer concentration on top.

**TOST (25.5)** — the economics are payment spread; AI is analytics and retention.

## Group 4 — supplier to the app layer, not a member *(different trade)*

**INOD (51.6)** — flagging this one explicitly because it is my framework arguing with a direct
instruction of yours ("keep INOD/WLY"). The thesis objection stands: Innodata sells engineered
training data **to** the labs, so it is picks-and-shovels — it tracks frontier-lab capex, not
application-layer adoption. Lab-encroachment 3/3 by construction, since its customers are the
labs.

But my *business* objection was wrong and the data kills it. I wrote that "margin quality is
the open question" because the underlying work is expert human labour. It isn't: revenue went
**$58.4m → $92.1m, +57.8% YoY, with gross margin rising 39.8% → 45.8%**. Labour-arbitrage
businesses do not expand margin as they scale. Good business, wrong list — and those are
separable verdicts.

**OUST (54.5)** — lidar plus perception software sold into other people's autonomy stacks.

## Group 5 — immaterial to the P&L

**WLY (53.9)** — the other name you said to keep, and the honest sizing is less flattering than
the screen hit. Wiley is one of five 10-K filers in fourteen months to print the phrase "AI
revenue," which is genuinely rare and costly to fake. But revenue is **flat** — $447.9m in
Apr-26 against $442.6m in Apr-25, +1.2% — and the operating margin gain (20.1%→25.3%) is
cost-out, not AI mix. The corpus licence is a real option and the disclosure is admirable. It
is not yet moving the business.

**IQV (38.0)** — enormous curated health dataset; the AI layer is a small component of a
services-driven P&L.

**HII (36.4)** — unmanned maritime is real and strategically interesting, but it is a rounding
error on a defense prime. This is what the industrial screen surfacing a shipbuilder looks
like when you size it honestly.

## Group 6 — the leftovers

**QXO (37.1)** — named a Chief AI Officer at founding and is running an explicit AI-transformation
playbook on a deliberately low-tech industry. The most interesting non-tech bet on the list and
entirely unproven. Score is meaningless here; it is a jockey bet.

**NU (52.7)**, **WAY (52.7)**, **SHOP (56.8)**, **ESTC (53.6)**, **FIG (54.7)** — thesis-adjacent.
Each has something real (Nubank underwrites where no bureau file exists and effectively *is* the
bureau in a thin-file market; Waystar predicts denials on a proprietary claims corpus; Elastic is
retrieval infrastructure *under* the app layer with a 765-star MCP server; Figma holds design
files as structured data with a 1,910-star server). None is primarily an AI trade.

---

# Algorithm changes from this review

**1. Discrimination floor at 60.** Below it, classify instead of ranking. Implemented in
`rank_ai_forward.py` — six reason codes, all 27 names assigned, emitted as a grouped appendix
under the ranked 50.

**2. The departures screen was broken and is rebuilt.** This is the significant one.

I built `edgar_ai_departures.py` last session, launched it, and never read the output — a real
process failure, since `leadership_churn` is a live axis (CRWD carries it). Reading it now: it
returned **five companies in fourteen months** and missed CrowdStrike, the case that prompted
it. Not a thin signal — a broken method. Measured against EDGAR:

| Phrase | 8-K filings |
|---|---|
| "Chief Technology Officer resigned" | 2 |
| "no longer serve as Chief Technology Officer" | 0 |
| "will step down as Chief Technology Officer" | 0 |
| "notified the Company of his intention to resign" | 40 |
| "tendered his resignation" | 171 |
| "separation from the Company" | 414 |

The departure verb and the role live in **different sentences**. Counsel writes "On [date],
Jane Doe notified the Company of her intention to resign" in one paragraph and identifies her
as CTO in another. A phrase screen cannot span that gap; it can only catch the rare filing
that collapses both into one clause, which is why it found noise and missed the real case.

Rebuilt as two stages: stage 1 searches departure boilerplate with no role filter (high
recall — **692 candidate filings**), stage 2 fetches each filing and scores it only when a
technical role appears within 1,200 characters of the departure language.

**Result: 5 → 27 companies**, and I verified hits by reading the filing text rather than
trusting the match. Two are names on this list, and both are true positives:

- **AUR** — Sterling Anderson, **co-founder and Chief Product Officer**, resigned May 2025
  from the role *and* the board. For a pre-revenue company whose entire thesis is forward
  execution, losing a founding technical principal is the "technical leadership" criterion
  breaking, not a footnote. **#14 → #18.**
- **ESTC** — CPO Ken Exner resigned June 2026, disclosed in the same 8-K as a restructuring
  plan. **#44 → #49.**

**Correction to my own diagnosis, which matters more than the fix.** I wrote above that the
CrowdStrike miss was a phrase-matching failure. I checked, and it wasn't. CrowdStrike filed
five Item 5.02 8-Ks in this window and **not one of them mentions "Chief Technology Officer"** —
they name the CFO, the President and the Chief Security Officer. There was no filing to find.

A CTO frequently is not a Section 16 officer, so no Item 5.02 obligation attaches and the
departure is announced by press release or on a call instead. So there are **two independent
problems**, and I had merged them:

1. The phrase method genuinely was broken — that is what 5 → 27 fixes, and it is why AUR and
   ESTC surfaced.
2. Even repaired, this screen has a **scope ceiling** it cannot cross. It sees Section 16
   officers in 8-Ks, and much senior technical churn never appears there.

The consequence is a routing decision, not a tuning one: **EDGAR cannot be the primary
instrument for technical-leadership churn.** The right instrument is the news channel, which
already ingests press releases and would have caught CrowdStrike. The rebuilt screen is a
high-precision supplement, not the source of record.

The general lesson still stands on its own terms — a phrase screen works only when the target
is *one phrase* ("AI revenue" is; "the CTO left" is a relationship between two phrases and
needs fetch-and-parse) — but it is not the explanation for the CrowdStrike miss, and I should
not have asserted it as one before checking.

**3. Corrections carried into the notes.** INOD's margin worry removed as empirically false;
WLY's "AI revenue" hit sized against a flat top line.

---

## What I would still fix

- **Route technical churn through the news channel.** The rebuilt EDGAR screen is now a
  verified supplement (it found AUR and ESTC), but its Section 16 ceiling means it will keep
  missing cases like CrowdStrike. The news channel already ingests the press releases that
  carry them.
- **Precision needs watching as this scales.** `"separation from the Company"` alone matches
  414 filings, and a 1,200-character window can in principle catch a filing where the CFO
  leaves and the CTO is merely thanked nearby. The two hits that mattered were verified by
  hand; a larger harvest needs a sample audit before it feeds scoring automatically.
- **The claims>traction flag cannot see private traction** (the FDS false positive). It should
  be downgraded to a prompt to check rather than a scoring penalty.
- **Six reason codes were assigned by hand.** They are judgments, not measurements, and should
  be re-derived when the underlying notes change.
