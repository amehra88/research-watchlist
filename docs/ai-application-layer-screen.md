# The AI Application Layer — Framework and Candidate Screen

*Drafted 2026-08-19. Prompted by: "find companies like Hinge Health, HeartFlow, and Axon that
utilize AI at their core — new AI application-layer companies. Shopify also fits the mold. What
else, outside semiconductors and hyperscalers? Maybe TEAM now." Follow-ups: "I want you to be able to
defend why each of these companies is 'AI powered' — each of them"; "there is a trucking and shipping
company also. TSLA is another example."*

Status: analytical draft, not a position sheet. Screened on business structure — not valuation,
entry price, or timing.

**On the defenses in §4:** each is argued from *mechanism* — what inference runs, on what data, and
what remains without it — rather than from product announcements or quarterly AI-revenue
disclosures. Mechanism is stable; product names and launch quarters are not, and my knowledge runs
to ~May 2026. Every claim below is structural and should hold; anything you want to cite in a
write-up should be re-verified against the SEC and news channels already running in this system.
Each name carries an explicit **defense strength** grade, and the strongest counter-argument is
stated before the rebuttal. Names I cannot defend well are graded *Thin* and kept visible rather
than quietly dropped.

---

## 1. Your exemplars contain two different theses

Run every name through one portable test:

> **Delete the model. Does the product still exist and still sell?**

| Name | Model deleted → what's left | Verdict |
|---|---|---|
| HeartFlow (HTFL) | A CT scan and a radiologist. FFR-CT *is* an inference. | **No product** |
| Hinge Health (HNGE) | A telehealth scheduler for physical therapy — a commodity. The motion-tracking CV is what replaces the clinician's labor. | **No product** |
| Axon (AXON) | Tasers, body cameras, evidence.com — a business that ran fine for 15 years. But report drafting, plate recognition, and auto-redaction do not survive. | **Split** |
| Tesla (TSLA) | A large, capable EV manufacturer. The company survives — but FSD, robotaxi, and Optimus are plausibly the entire premium over an auto multiple. | **Product survives, premium does not** |
| Shopify (SHOP) | Shopify. Unchanged and excellent. | **Product survives** |
| Atlassian (TEAM) | Jira and Confluence. Unchanged. | **Product survives** |

The four names you grouped are **two archetypes** carrying different risks. Worth separating before
screening, because a single list conflates them.

### Archetype A — Model-native product

The model *is* the product. Inference is the revenue line. The moat is a **labeled proprietary
corpus** that is expensive, slow, illegal, or physically impossible for a competitor to assemble —
usually reinforced by a **regulatory gate** (FDA clearance, a reimbursement code, an evidentiary
standard, a lending regulator).

*Fails when:* a frontier model commoditizes the task from outside; the corpus proves replicable; or
the regulator/payer declines.

### Archetype B — Proprietary corpus + technical leadership, AI as compounding overlay

The product predates AI and survives without it. The bet is three-part: (i) data others cannot
legally or practically train on, (ii) leadership that will genuinely rewire the org rather than ship
a chat box, (iii) AI arriving first as **margin** — fewer support, sales, and engineering heads per
dollar of revenue — before it arrives as a new SKU.

*Fails when:* the data legally belongs to the customer; every competitor gets the same models and
the gain competes away in a year; or an agent layer disintermediates the UI you monetize.

### Why Axon is the right template

Axon started as B and is **converting to A on a corpus nobody else can obtain**. It spent fifteen
years becoming the system of record for police evidence, then turned that corpus into model-native
products sold to the same buyer through the same procurement cycle. That conversion — *B sitting on
a corpus that can become A* — is the highest-value thing to screen for, and rarer than either pure
archetype.

Shopify and Atlassian pass your data and leadership criteria and **fail the centrality one**. Not a
reason to drop them; a reason to hold them under a different thesis with different disconfirming
evidence. TEAM is a clean B: enormous proprietary corpus of work artifacts, technical founders, real
commitment — and Jira sells regardless.

### The criterion your framing under-weights: *who owns the training data*

Shopify owns merchant transaction data outright. Salesforce does not own its customers' CRM records
in any way it can train on. This one distinction disqualifies roughly half the enterprise-software
complex currently marketing itself as AI-central. **Ask of every candidate: could they legally train
on it, and could a competitor get it?**

---

## 2. Negative screen — what disqualifies a name

1. **The AI is a vendor API in a wrapper.** No data advantage, and gross margin goes *down*, not up.
   Inference is COGS for them and revenue for someone else.
2. **The data belongs to the customer.** Contracts forbid cross-tenant training. The moat is the
   customer's, not theirs.
3. **Agents announced, nothing repriced and nothing shrunk.** A company that believes its own AI
   story raises price, changes the pricing *unit* (per outcome, per resolution), or reduces
   headcount. None of the three → it's a demo.
4. **The AI SKU is sold to the same buyer out of the same budget.** A feature defending existing
   revenue, not a product creating it.

---

## 3. The mirror risk — app layer vs. *disrupted* layer

Several names that superficially look like AI application-layer companies are most exposed to
*being* the layer removed. The tell: **the moat is workflow and seat count, not data.**

- Per-seat SaaS whose core value is "a place for a human to type."
- Developer tooling priced per developer, against agentic coding.
- Contact-center software — the paid unit is the seat the technology eliminates.
- Communications plumbing whose application layer consolidates above it.
- Staffing and BPO.

The genuinely hard case: **NICE and Verint** own a real proprietary corpus (decades of recorded
customer interactions) *and* sell the seat being automated. Same company, both sides of the trade.
The most interesting single debate in this category; it resolves on whether they can reprice to
outcomes fast enough. Worth a note before it's worth a position.

---

## 4. Candidates, each with its defense

Excluded per your constraint: semiconductors and semi-cap, EDA (semi-adjacent), hyperscalers.
**Bold = not currently in the watchlist.** Bracketed tag = industry.

---

### 4a. Archetype A — model-native

#### Healthcare and life sciences

The richest hunting ground, because it is the one industry where labeled proprietary data, a
regulatory gate, and a reimbursement code stack on top of each other. Three moats, not one.

---

**iRhythm — IRTC** *[med-tech]* — **the closest structural twin to HeartFlow on your list**

- **The inference.** A wearable patch records continuous single-lead ECG for up to ~14 days. That is
  on the order of a million heartbeats per patient. No human reads that economically — the
  deep-learning classifier segments the entire recording, flags arrhythmia episodes, and hands a
  technician a reviewable shortlist. The product sold to the cardiologist is *the interpreted
  report*, not the tape.
- **The corpus.** Well over a decade of long-duration ambulatory ECG recordings with adjudicated
  human labels, accumulated one patient at a time under FDA-cleared workflows. It cannot be
  scraped, bought, or synthesized; it accretes only by having already won the market.
- **Delete the model.** An adhesive patch and an unreadable data file. The business does not exist.
- **Best counter-argument.** "It's a medical device company with software in the loop — the moat is
  the reimbursement code, not the algorithm."
- **Rebuttal.** The reimbursement code exists *because* the interpreted output has clinical value a
  24-hour Holter monitor cannot match, and that output is only economically producible by the
  classifier. The two moats are the same moat: the code pays for the inference. And any entrant must
  clear FDA *and* assemble the labeled corpus *and* obtain reimbursement — sequentially, over years.
- **Defense strength: Strong.** Highest-conviction new name for the pure thesis.

---

**Tempus AI — TEM** *[diagnostics / data]*

- **The inference.** Two distinct products. (1) Diagnostics: molecular and imaging classifiers that
  return a clinical result. (2) The one that matters more: a queryable library linking genomic
  sequencing to *de-identified longitudinal clinical outcomes* from the ordering physicians —
  licensed to pharma for trial design, cohort identification, and biomarker discovery.
- **The corpus.** The linkage is the asset. Sequencing data is increasingly commoditized; sequencing
  data *joined to what happened to that patient over the following three years* is not. That join
  requires being embedded in the clinical workflow at the point of order, which is why it took a
  decade and enormous losses to build.
- **Delete the model.** A sequencing lab — a commodity business with poor economics. The data
  library and its algorithmic layer are the entire equity story.
- **Best counter-argument.** "It has 'AI' in the corporate name, which is exactly what §2 tells you
  to distrust. Much of the revenue is ordinary lab reimbursement, and 'data licensing' may be
  consulting in a trench coat."
- **Rebuttal, and a concession.** The counter-argument is partly right and this is the one name here
  where I would not wave it away. The defensible claim is narrow: the *data-licensing* line is
  genuinely model-adjacent and genuinely defensible; the lab line is not. The diligence question is
  therefore mechanical — what share of revenue is licensing, is it recurring or project-based, and
  is gross margin on it expanding? If licensing is a small, lumpy, project-shaped line, this is a
  lab company and the thesis fails.
- **Defense strength: Moderate — conditional on that revenue-mix diligence.** Include for the corpus;
  do not underwrite on the name.

---

**Natera — NTRA** *[diagnostics]*

- **The inference.** Signatera is tumor-informed minimal-residual-disease detection: sequence the
  patient's tumor, computationally design a *personalized* panel of variants unique to that patient,
  then detect vanishingly rare circulating tumor DNA against a background of normal DNA. The
  detection is a statistical-inference problem at signal levels below what any fixed assay resolves.
- **The corpus.** Millions of processed samples with linked clinical outcomes, feeding error models
  that determine how confidently you can call a signal at parts-per-million. Detection sensitivity
  is a direct function of accumulated data. This is a compounding loop: more tests → better error
  models → better sensitivity → more clinical evidence → more payer coverage → more tests.
- **Delete the model.** Sequencing output with no interpretable answer. There is no product.
- **Best counter-argument.** "That's bioinformatics and statistics, not AI. You are relabeling
  computational biology to fit a theme."
- **Rebuttal.** This objection deserves a direct answer rather than a definitional dodge. If "AI
  powered" means *transformers*, this fails. If it means *the commercial product is a learned
  inference over a proprietary data asset, and the accuracy improves with data volume in a way
  competitors cannot replicate* — which is the definition that actually matters for durability of
  returns — it passes cleanly, and it passes for a reason more robust than most: the learning loop
  is tied to regulated clinical evidence, not to a model checkpoint anyone can retrain. I'd argue
  the label objection is cosmetic and the economics are the point.
- **Defense strength: Strong**, with the definitional caveat stated openly.

---

**Guardant Health — GH** *[diagnostics]*

- **The inference.** Same class of problem, applied to screening and therapy selection from blood
  rather than tumor-informed MRD: classify cancer signal from cell-free DNA fragments.
- **The corpus.** Large clinical-genomic database with outcome linkage; screening in particular is a
  pure classifier-performance business — the whole regulatory and commercial argument is sensitivity
  and specificity at population scale.
- **Delete the model.** No test. A blood draw.
- **Best counter-argument.** "Screening economics are brutal, and the classifier competes against
  established modalities with decades of evidence. Being model-native doesn't make it a good
  business."
- **Rebuttal.** Concede the business point entirely — this is a *weaker business* than NTRA with an
  *equally clean* AI-centrality claim. Those are separate questions, and I'd rank it below Natera on
  everything except thesis purity.
- **Defense strength: Strong on centrality, weak on business quality.** Second derivative of NTRA.

---

**RadNet — RDNT** *[imaging services]* — the structural oddity worth the most attention

- **The inference.** FDA-cleared deep-learning models reading mammography and other imaging studies,
  used two ways: as a productivity layer letting radiologists read more studies per hour, and as a
  *cash-pay upsell* — the patient pays out of pocket for an AI-enhanced read layered on the
  insurance-reimbursed scan.
- **The corpus.** This is the part almost everyone misses. RadNet **owns the imaging centers**, so it
  owns the scans, the priors, and the downstream biopsy outcomes that label them. Nearly every other
  imaging-AI company is a vendor begging hospital systems for data access under restrictive
  agreements. RadNet is its own data supplier *and* its own distribution channel.
- **Delete the model.** A profitable but capital-intensive outpatient imaging roll-up. The business
  survives — but the margin-expansion story and the cash-pay revenue line do not.
- **Best counter-argument.** "It's an asset-heavy services roll-up with a software story bolted on.
  The AI is a rounding error on revenue and always will be."
- **Rebuttal, partly conceded.** Correct today on revenue share — this is archetype B, not A, and I've
  placed it in A only because the AI product line is genuinely model-native even if small. The real
  argument is structural, not current: vertical integration of data supply, model, and distribution
  is the configuration every imaging-AI startup wishes it had and cannot buy. Also note it screens
  out of every tech-investor filter because it is classified under healthcare services — which is
  precisely why it's mispriced as an AI asset, if it is.
- **Defense strength: Moderate**, but the *structure* is the strongest in the group. Flagged as the
  most differentiated idea on this list.

---

**Intuitive Surgical — ISRG** *[med-tech]*

- **The inference.** Today, honestly: modest. Instrument tracking, workflow segmentation of surgical
  video, case analytics benchmarking a surgeon against a population of comparable procedures.
- **The corpus.** Plausibly the largest surgical video and instrument-kinematics dataset in
  existence, generated continuously by an enormous installed base, with the crucial property that
  **every frame is paired with synchronized robot telemetry** — exactly what an action-labeled
  dataset requires. Nobody else can assemble this without first selling the robots.
- **Delete the model.** The company is unchanged. Surgeons buy the robot for the instrument and the
  visualization. This is archetype B without ambiguity.
- **Best counter-argument.** "You are describing a data asset, not an AI business. The AI generates
  no meaningful revenue and might never — surgical autonomy faces a regulatory wall that may not
  come down this decade."
- **Rebuttal — mostly a concession.** Both points stand. I include it because the screen you asked
  for is "B sitting on a corpus that can become A," and this is the single most defensible unconverted
  corpus in medical technology. But the honest framing is: **own it for the robot, hold the corpus as
  a free option.** Anyone underwriting ISRG on AI today is front-running by years.
- **Defense strength: Thin as an AI-revenue claim, Strong as a corpus claim.** Graded honestly.

---

**Recursion — RXRX** *[drug discovery]*

- **The inference.** Industrial-scale automated cell-biology experiments generating microscopy
  images of cells under perturbation; models embed those images into a representation space where
  similarity implies shared biological mechanism, used to nominate targets and compounds.
- **The corpus.** Petabyte-scale proprietary phenomic data generated in-house rather than mined from
  literature — the rare case where a company *manufactures* its own training data on purpose, at a
  volume no academic lab can match.
- **Delete the model.** Nothing at all. There is no other product. This is the purest archetype A on
  the entire list.
- **Best counter-argument.** "Purity of thesis and zero clinical validation. Every AI-drug-discovery
  company has a beautiful platform story and a thin pipeline; the industry's base rate for
  converting computational leads into approved drugs is, so far, unproven."
- **Rebuttal.** No real rebuttal — the counter-argument is correct. The defense is only that the
  *AI-centrality* question is unambiguous, which is what you asked me to defend; the *investment*
  question is separate and currently unresolved.
- **Defense strength: Strong on centrality, unproven on output.** Option-value sizing, not core.

---

#### Financial services

---

**Upstart — UPST** *[consumer lending]*

- **The inference.** The credit decision itself. A borrower applies; a model prices and approves.
  The entire commercial claim is that a many-variable learned model separates default risk better
  than a traditional score at the same approval rate — i.e. it approves borrowers a FICO cutoff
  would reject, at equal or lower realized loss.
- **The corpus.** Repayment outcomes on loans originated through its own funnel, including — and
  this is the technically important part — outcomes on borrowers a conventional model would have
  declined. Traditional lenders never observe those, because they never funded them. That
  counterfactual coverage is genuinely hard to replicate and only accumulates by taking the risk.
- **Delete the model.** There is no company. Not a metaphor: the product is the decision.
- **Best counter-argument.** "The model has not been proven through a full credit cycle, and the
  business is really a funding-markets business — when capital retreats, model quality is irrelevant."
- **Rebuttal, half conceded.** The funding-fragility point is correct and is the reason this is
  thesis-clean but position-hostile. On cycle-testing: the model has now seen a rate shock and a
  normalization, which is more than it had, though not a full recession. The defense of
  *AI-centrality* is airtight regardless of whether the model is *good* — those are different
  claims, and I'd keep them apart.
- **Defense strength: Strong on centrality; unresolved on model efficacy.** The cleanest live
  experiment on whether a proprietary underwriting corpus beats a bureau score.

---

**Nu Holdings — NU** *[banking, LatAm]*

- **The inference.** Two places it's real: (1) credit underwriting and limit-setting for tens of
  millions of customers with thin or no bureau file, using in-app behavioral and transactional
  signals rather than a credit history that does not exist; (2) customer service resolution, where
  the meaningful metric is cost to serve per active customer.
- **The corpus.** First-party transaction and behavior data on a very large base of customers who
  are invisible to traditional bureaus. In a thin-file market, the company that holds the behavioral
  data effectively *is* the bureau. Structurally different from a US bank, which rents its risk view
  from FICO and the bureaus.
- **Delete the model.** A well-run, low-cost digital bank. It survives, and it would still be good.
  Archetype B.
- **Best counter-argument.** "This is a good bank with good software. Every bank runs credit models —
  calling Nubank AI-powered stretches the term to the point of meaninglessness."
- **Rebuttal.** The distinction I'd defend is *substitution*, not sophistication: incumbents use models
  to price risk they can already see; Nubank uses models to *see risk that has no other record*, which
  is what allowed the customer base to exist at all. Cost-to-serve is the falsifiable test — if
  operating expense per active customer is not falling as the base grows, the AI claim is decoration.
  That number is public and checkable each quarter.
- **Defense strength: Moderate.** Include as B with the cost-to-serve metric as the live test.

---

**Verisk — VRSK** *[insurance data]*

- **The inference.** Loss-cost prediction, fraud detection across carriers, and increasingly
  computer vision on aerial and property imagery to assess roof condition, wildfire exposure, and
  post-catastrophe damage without a physical inspection.
- **The corpus.** Pooled claims and policy data contributed by the carriers themselves over
  decades — an asset a new entrant cannot recreate at any price, because it requires competing
  insurers to agree to contribute to a shared utility, which they did once and would not do again
  for a startup. Roughly a natural monopoly on the industry's loss history.
- **Delete the model.** The data-subscription business largely survives; the analytics and imagery
  products do not. Archetype B with an unusually good corpus.
- **Best counter-argument.** "This is an actuarial data vendor. It has sold statistical models since
  before 'AI' was a marketing term — nothing changed."
- **Rebuttal, and a real concession.** Largely fair for the legacy business. The genuinely new
  component is the imagery layer: assessing millions of properties from overhead imagery is a
  computer-vision problem that did not exist as a product a decade ago and directly substitutes for
  field-inspection labor. If you want a crisp defense, defend that segment, not the whole company.
- **Defense strength: Moderate.** Strongest data moat on this list; weakest claim that AI changed
  anything.

---

#### Public safety and government — the Axon adjacency

---

**Cellebrite — CLBT** *[digital forensics]*

- **The inference.** Extraction is engineering, not AI. The AI is what happens next: an investigator
  faces a terabyte of messages, photos, video, and location history from a seized device and needs
  the relevant fragment. Models do entity resolution across devices, image and object classification,
  transcription and translation of media, and timeline reconstruction. The paid job is *triage*, and
  triage is inference.
- **The corpus.** Less a training corpus than an accumulated device-behavior knowledge base plus a
  government install base with evidentiary-standard lock-in — a competitor must not only match the
  capability but be accepted by courts.
- **Delete the model.** Extraction tooling survives; the investigator drowns in the output. The
  revenue-expansion story is entirely the analysis layer.
- **Best counter-argument.** "The core asset is exploit research and device access, not machine
  learning. The AI is a search UI on top of a security-research business."
- **Rebuttal.** Partly conceded — access is the foundation and it isn't AI. But the *growth* is in
  seats and modules sold for analysis, which is the Axon pattern exactly: a system-of-record moat
  built on something else, then monetized through model-native product on top. That's the shape you
  asked me to screen for, and it's genuinely present here.
- **Defense strength: Moderate.** Closest business-model analogue to Axon on this list.

---

**Tyler Technologies — TYL** *[govtech]*

- **The inference.** Today: modest. Document understanding on court and permit filings, redaction,
  routing, some case-outcome analytics.
- **The corpus.** The civic system of record — courts, permits, licensing, public safety — for a
  large share of US local government, with switching costs measured in decades.
- **Delete the model.** Completely unaffected. This is a records and workflow company.
- **Best counter-argument.** "There is no AI thesis here. You included it because the *buyer* looks
  like Axon's buyer, which is pattern-matching on customers rather than on technology."
- **Rebuttal — conceded.** That objection is correct and I'll take it. Tyler belongs on a
  *watch-for-conversion* list, not on a list of AI-powered companies. Its qualification is
  positional: it owns a corpus that could become model-native, in a procurement environment where
  Axon has proven the upsell works. That is a hypothesis about the future, not a defense of the
  present.
- **Defense strength: Thin.** Kept visible and demoted rather than dropped, so the list stays honest.

---

#### Professional information

---

**RELX** *[legal, scientific, risk information]* — **the most under-discussed name in this category**

- **The inference.** Retrieval and generation over proprietary corpora in domains where a fabricated
  answer is disqualifying: legal research that must cite real, still-good case law; scientific
  literature synthesis; identity and fraud scoring on proprietary risk data. The product is
  transitioning from *find me the documents* to *give me the answer, with citations that verify*.
- **The corpus.** LexisNexis holds curated case law with editorially-maintained citation treatment —
  the annotations telling you whether a precedent still stands. That editorial layer is a century of
  human work and is exactly the grounding a generative system needs to be trustworthy. Elsevier
  holds the scientific literature. Risk holds identity graphs. All three are owned, licensed, and
  legally trainable by them and by essentially no one else.
- **Delete the model.** The subscription businesses survive. Archetype B — but with the most
  valuable *unconverted* corpus of any name here.
- **Best counter-argument.** "A frontier model plus freely available public case law commoditizes
  legal research from below. Publishers are the classic disruption target — this is the mirror risk
  in §3, not an opportunity."
- **Rebuttal.** The strongest counter on this list, and it's right about the low end: routine
  research does get commoditized. But it inverts at the top, for a reason specific to law:
  liability. A lawyer cannot file a brief citing a case that may not exist or may have been
  overturned, and the verification layer that prevents that is precisely the proprietary editorial
  asset. Generative AI *raises* the value of authoritative grounding at exactly the moment it makes
  ungrounded text free. The falsifiable test is pricing and retention in the premium legal segment —
  if those hold while volume shifts to AI-assisted workflows, the thesis is working.
- **Defense strength: Strong**, with the disruption debate stated squarely rather than dodged.

---

**Thomson Reuters — TRI** *[legal, tax]*

- **The inference.** Same class: generative research and drafting grounded in the Westlaw legal
  corpus and proprietary tax content, sold as a per-seat professional product.
- **The corpus.** Westlaw's case law with its own editorial classification and citation system —
  structurally the same asset as LexisNexis, and the same reason a general-purpose model cannot
  substitute for it in a filing.
- **Delete the model.** Subscriptions survive. Archetype B.
- **Best counter-argument.** Identical to RELX, plus a sharper one: TRI is more concentrated in legal
  and tax, so it has less diversification if the low end erodes faster than expected.
- **Rebuttal.** Same liability-grounding argument, correctly applied. The concentration point is
  real and is why I'd rank it behind RELX rather than beside it.
- **Defense strength: Strong**, ranked second to RELX on the same logic.

---

#### Industrial and physical world

---

**Deere — DE** *[agriculture]* — **the best "outside tech" answer**

- **The inference.** See & Spray: cameras mounted across a sprayer boom moving through a field at
  speed, running real-time computer vision that classifies each individual plant as crop or weed and
  fires the corresponding nozzle within milliseconds. This is a hard vision problem — variable
  light, motion blur, occlusion, species that look alike — solved on embedded hardware in the field.
  Separately: field autonomy, and agronomic models on machine telemetry.
- **The corpus.** Hundreds of millions of labeled plant images across geographies, species, and
  growth stages, gathered through a machine fleet no one else has. The data can only be collected by
  driving equipment through fields, and Deere owns the fleet, the dealers, and the telemetry
  channel.
- **Delete the model.** See & Spray does not exist, and neither does autonomy. Deere the tractor
  company is unaffected — so it is B at the corporate level, but the specific product line is A, and
  it is priced on outcome (herbicide volume saved), which is the §2 test for a company that believes
  its own AI story.
- **Best counter-argument.** "This is a deeply cyclical heavy-equipment manufacturer. The AI is a
  small attachment on a very large P&L driven by crop prices and interest rates. Owning DE to own AI
  is owning the wrong variable."
- **Rebuttal, half conceded.** The cyclicality point is entirely correct and is the main reason not
  to size it as an AI position. What survives: this is the clearest example anywhere of AI being
  sold *as measured physical outcome* rather than as a software seat, by a company with a real
  engineering organization and an uncopyable data-collection channel. If you want proof the thesis
  extends beyond software, this is the exhibit.
- **Defense strength: Strong on mechanism, weak as a pure-play expression.**

---

**Aurora Innovation — AUR** *[autonomous trucking]*

- **The inference.** The entire driving stack — perception, prediction, planning — replacing a
  commercial driver on highway freight routes.
- **The corpus.** Accumulated driving data and, more importantly, a validation and simulation
  apparatus; the binding constraint in autonomy is proving safety, not achieving nominal
  competence.
- **Delete the model.** Nothing whatsoever. There is no other product, no other revenue, no other
  asset.
- **Best counter-argument.** "Unambiguously AI and nearly un-investable. Capital-intensive, timeline
  has slipped repeatedly across the whole sector, and the outcome is binary."
- **Rebuttal.** None on the business. Included because the centrality question is trivially
  affirmative, and because it usefully marks the far end of the spectrum — maximum AI purity,
  minimum business certainty. Useful as a calibration point for the rest of the list.
- **Defense strength: Strong on centrality, speculative as an investment.**

---

**Cognex — CGNX** *[machine vision]*

- **The inference.** Industrial inspection: is this part defective, is this label correct, is this
  weld sound. Increasingly deep-learning-based rather than rule-based, which is what allows
  inspection of variable and organic surfaces that classical machine vision could never handle.
- **The corpus.** Application-specific and largely built per-deployment on customer data — which is
  the weakness. The moat is toolchain, optics, and installed base more than accumulated data.
- **Delete the model.** The classical rules-based vision business survives; the addressable market
  contracts sharply, since deep learning is what opened the non-deterministic inspection tasks.
- **Best counter-argument.** "Vision models are commoditizing fast and open-source. Cognex's moat is
  hardware and channel, and the AI layer is the part most likely to be competed to zero."
- **Rebuttal.** Weak. I'd concede the commoditization risk is real and that this is the most exposed
  name here to §2's first disqualifier. It stays on the list because the *product* is genuinely an
  inference and the cyclical entry point may matter — but not because the moat is strong.
- **Defense strength: Thin.**

---

**Symbotic — SYM** *[warehouse automation]*

- **The inference.** Multi-agent orchestration of hundreds of autonomous bots in a dense storage
  structure — routing, sequencing, and collision avoidance — plus vision for item identification and
  grasp.
- **The corpus.** Operational data from deployed systems; useful, but the core is arguably classical
  optimization and controls rather than learned models.
- **Delete the model.** Depends where you draw the line, which is itself the problem: much of the
  orchestration is solvable with operations research, not machine learning.
- **Best counter-argument.** "This is robotics and optimization software, and it's sold to
  essentially one customer. Both the AI label and the business quality are questionable."
- **Rebuttal.** I'd largely concede. Customer concentration is a genuine hazard independent of the
  AI question, and the AI question itself is definitionally soft here.
- **Defense strength: Thin.** Listed for completeness of the physical-world category.

---

#### Transport and logistics

*Added after your prompt: "there is a trucking and shipping company also." My read is C.H. Robinson —
freight brokerage is the clearest case in transport where **the labor being automated *is* the
product**. Alternates and exclusions listed below; tell me if you meant a different one.*

---

**C.H. Robinson — CHRW** *[freight brokerage / logistics]*

- **The inference.** Freight brokerage, stripped to its mechanics, is thousands of people on phones
  and email matching a shipper's load to a carrier's empty truck and negotiating a price. The AI
  does three jobs in that loop: parse unstructured inbound quote requests and tender emails into
  structured orders; price the lane automatically; and match load to carrier on predicted acceptance
  and reliability. Every one of those was a human task with a salary attached.
- **The corpus.** Decades of lane-level transaction data — what a given lane cleared at, which
  carriers accept which loads at which price, how capacity moves seasonally and around
  disruptions — at a network scale few brokers match. It is genuinely proprietary, though not
  unique: the largest competitors have their own versions.
- **Delete the model.** Brokerage survives; it is a 120-year-old business. But the operating-leverage
  story disappears entirely — and that story is the whole reason to own it, because it breaks the
  industry's historical iron link between shipment growth and headcount growth. Archetype B.
- **Best counter-argument.** "This is a cyclical spread business and the 'AI' is a cost-cutting
  program with a narrative attached. Margins are set by the freight cycle, not by software.
  Digitally-native brokers already exist and haven't won."
- **Rebuttal.** Cyclicality: conceded, and it's the reason not to size this as a technology position.
  But on the specific question you asked me to defend, CHRW has something almost nothing else on this
  list has — **publicly observable proof that the substitution happened.** Shipments per employee is
  a disclosed operational metric. §2's third disqualifier asks whether a company that claims AI
  actually repriced or shrank; here you can read the answer off the operating statistics rather than
  taking the earnings-deck's word for it. That makes it one of the most *falsifiable* AI claims in
  the market, which is worth more than a louder claim you cannot check.
- **Defense strength: Moderate-to-Strong on labor substitution; weak on data exclusivity.** The
  clearest AI-displaces-labor evidence on this entire list.

---

**RXO — RXO** *[asset-light truck brokerage]*

- **The inference.** Same automated pricing and load-matching loop, built more recently and marketed
  harder as a technology platform.
- **The corpus.** Smaller network, therefore thinner data than CHRW — and in a matching business,
  data advantage scales with network size, so this is a real disadvantage rather than a cosmetic one.
- **Delete the model.** Same answer: brokerage survives, the differentiation does not.
- **Best counter-argument.** "A subscale competitor to CHRW with a better slide deck and more
  cyclical leverage."
- **Rebuttal.** Mostly conceded. The mechanism is identical, so if you like the freight-brokerage
  automation thesis, the question is purely which balance sheet and which network size you want.
- **Defense strength: Moderate**, ranked behind CHRW on network scale.

---

**Uber — UBER** *[mobility, delivery, freight]* — adjacent

- **The inference.** Real-time matching, dynamic pricing, ETA prediction, and routing across
  millions of daily transactions — plus Uber Freight applying the same machinery to trucking. The
  marketplace has never functioned any other way; there is no manual-dispatch version of Uber.
- **The corpus.** Enormous first-party data on demand, supply, routes, and pricing elasticity across
  cities and modes.
- **Delete the model.** Uniquely, this one *does* fail: a manual dispatch system cannot clear that
  volume in real time. On mechanism, Uber is more model-native than most software companies here.
- **Best counter-argument.** "Nobody thinks of Uber as an AI company, and the marketplace ML is a
  decade-old commodity capability. The forward risk is that autonomy — someone else's models —
  disintermediates the driver network Uber's value rests on."
- **Rebuttal.** The commodity objection is weak: the matching engine is a genuine operating asset
  even if it isn't fashionable. The autonomy objection is the serious one, and it's unresolved —
  Uber is either the demand aggregator autonomous fleets must plug into, or the middleman they
  route around. That's a real fork, not a detail.
- **Defense strength: Moderate.** Include as adjacent; the autonomy fork is the whole debate.

---

**Screened out of transport, and why** — GXO (warehouse orchestration: same definitional softness as
SYM, largely optimization and controls rather than learned models); XPO, ODFL, Landstar, Expeditors
(operationally excellent, no defensible model-centrality claim — asset networks and human brokerage
with conventional software). Aurora is covered above under the physical-world block: it is the
*pure* trucking-autonomy expression, maximum AI purity and minimum business certainty.

---

#### Consumer and commerce

---

**Tesla — TSLA** *[autos, autonomy, robotics]* — **already T1; included because you raised it, and
because it is the template rather than a new idea**

- **The inference.** FSD is an end-to-end learned driving policy: camera video in, vehicle controls
  out, with hand-written rules progressively removed in favor of a network trained on human driving.
  Optimus is the same bet applied to manipulation. Both are inference products in the most literal
  sense — there is no rules-based fallback that does the job.
- **The corpus.** The most valuable structural asset in the company and the reason it belongs on
  this list: a very large fleet of customer-owned vehicles continuously generating camera video
  labeled by what the human driver actually did. Two properties make it near-uncopyable. First,
  **the data collection is revenue-positive** — customers *pay* to expand the training fleet, where
  every competing autonomy program pays to operate one. Second, the coverage is long-tail: rare
  events that a dedicated test fleet would need decades to encounter show up weekly at fleet scale.
  This is the Deere pattern — own the machines, own the data channel — at a far larger scale.
- **Delete the model.** A large, capable EV manufacturer remains. So at the corporate level this is
  archetype B — but the distinction matters less here than anywhere else, because FSD, robotaxi, and
  Optimus plausibly *are* the entire valuation premium over an automotive multiple. Delete the model
  and you delete the reason the stock trades where it does, even though the company survives.
- **Best counter-argument.** Several, all serious. The auto business generates the cash and faces
  real margin pressure from Chinese competition. Unsupervised autonomy has been imminent for roughly
  a decade. Regulatory approval is unresolved and non-uniform across jurisdictions. And vision-only
  remains a contested architectural bet against sensor-fusion approaches.
- **Rebuttal, with an important framing caveat.** The data asymmetry is structural and survives every
  one of those objections — no competitor has a revenue-funded fleet producing labeled driving video
  at that scale, and that fact is independent of whether the timeline slips again. But I'd be honest
  about what TSLA contributes to *this* exercise: it is the market's largest and most-discussed
  AI-application-layer position, so it carries essentially zero informational edge. Its value here is
  as **the template** — fleet → proprietary corpus → model → product — which is precisely the pattern
  I used to argue for Deere, RadNet, and iRhythm. It validates the screen; it isn't an output of it.
- **Defense strength: Strong on centrality of the valuation premium; nil as a differentiated idea.**
  Already T1, no action.

---

**Klaviyo — KVYO** *[marketing technology]*

- **The inference.** Predicting, per individual shopper, what to send, when, and through which
  channel — churn probability, expected next order date, predicted lifetime value — and then
  generating the message. The customer buys revenue attributable to the send, which means the
  product is judged on predictive accuracy.
- **The corpus.** Behavioral event data across a very large number of e-commerce merchants —
  crucially, *cross-merchant*, so an individual shopper's patterns inform predictions in a way no
  single merchant could achieve alone. This is the layer directly above Shopify, and it is the
  natural second expression of the Shopify data argument you already hold.
- **Delete the model.** An email service provider — a commodity with commodity pricing. The
  predictive layer is what supports the price point.
- **Best counter-argument.** "The data is the merchants', not Klaviyo's, which trips §2's second
  disqualifier. And it is existentially dependent on a platform (Shopify) that could build this
  itself."
- **Rebuttal, partly conceded.** Platform dependency is a real and unhedgeable risk — take it
  seriously. On data ownership the objection is weaker than it looks: aggregated cross-merchant
  behavioral modeling is generally within terms, and it's the aggregation, not any single tenant's
  data, that creates the advantage. Still, this is a *moderate* defense, not a strong one.
- **Defense strength: Moderate.**

---

**Roblox — RBLX** *[gaming / UGC]*

- **The inference.** Two genuinely central uses. (1) Safety: real-time classification of text and
  voice across an enormous volume of interactions involving minors — a regulatory necessity that no
  human moderation workforce could cover at that scale, and an existential requirement rather than a
  feature. (2) Generative creation tools that let a non-programmer build 3D environments and
  behaviors from description.
- **The corpus.** Years of in-platform interaction data with moderation outcomes attached, plus a
  vast library of user-generated 3D content and the telemetry of how players engage with it. Both
  are unavailable anywhere else.
- **Delete the model.** The platform is unusable — not degraded, unusable. It could not lawfully
  operate a minor-heavy social platform without automated safety classification. That is a rare and
  strong form of centrality: the AI is a *license to operate*, not a feature.
- **Best counter-argument.** "Safety AI is a cost center, not a product. Nobody pays Roblox for
  moderation, so it doesn't make the company AI-powered in any commercially meaningful sense."
- **Rebuttal.** A cost that is a precondition for the entire revenue base is not incidental — but I'd
  concede it isn't a *revenue* argument, and the stronger commercial case is the generative creation
  side, which expands the creator base by lowering the skill floor. Judge it on creator-count and
  content-volume growth.
- **Defense strength: Moderate.**

---

### 4b. Archetype B — corpus + technical leadership (the Shopify/Atlassian shape)

---

**Intuit — INTU** *[fintech / SMB software]*

- **The inference.** Extracting structure from unstructured financial documents, categorizing
  transactions, and — the strategically important part — moving from *software that helps you do
  the work* to *an agent that does the work*, with a human expert on call. That is a direct attack
  on the professional-services labor line, not a feature.
- **The corpus.** Owns the tax returns and the small-business general ledgers outright. This is the
  §1 distinction in its purest form: not customer data held in trust under a restrictive contract,
  but data whose use rights they hold. Very few software companies can say this.
- **Delete the model.** TurboTax and QuickBooks are excellent businesses, unchanged. Archetype B,
  unambiguously.
- **Best counter-argument.** "Every large software company claims agents now. Intuit's moat is
  brand, distribution, and switching costs — it would be dominant with or without AI, so the AI is
  not doing the work in the thesis."
- **Rebuttal.** Fair as stated, so I'd make the claim narrower and testable: the thesis is not that
  AI creates the moat, it is that AI lets Intuit capture the *services* revenue that currently goes
  to accountants and tax preparers — a far larger pool than the software they sell today. That is
  falsifiable on the §2 test: does the pricing unit change from a seat/return to a
  done-for-you outcome, and does attach rate on assisted offerings climb? If pricing doesn't move,
  the story is decoration.
- **Defense strength: Moderate**, with a clean falsifier.

---

**Toast — TOST** *[restaurant technology]*

- **The inference.** Demand forecasting, labor scheduling, menu and pricing optimization, plus
  agentic handling of orders — all against a restaurant's thinnest margin lines.
- **The corpus.** Transaction-level data across a large installed base of restaurants, with
  location, weather, and time-of-day covariates.
- **Delete the model.** A point-of-sale and payments company. Fully intact.
- **Best counter-argument.** "This is a payments company with an analytics dashboard. The economics
  are payment spread, and AI is a retention feature."
- **Rebuttal.** Largely conceded — the AI is not currently doing the commercial work.
- **Defense strength: Thin.**

---

**AppFolio — APPF** *[property management software]*

- **The inference.** Handling the high-volume, low-complexity communication load of property
  management — leasing inquiries, maintenance triage — which is genuinely the labor cost of the
  industry, and is priced as an add-on above the core seat.
- **The corpus.** Vertical-specific interaction and maintenance data across its customer base.
- **Delete the model.** The core property-management software survives.
- **Best counter-argument.** "Small company, single vertical, and the underlying capability is a
  foundation model anyone can call — §2 disqualifier one."
- **Rebuttal.** Partly conceded on the model commoditization; the defensible piece is the vertical
  workflow integration and the fact that it is priced as a separate outcome-shaped module rather
  than bundled free, which is at least evidence of conviction.
- **Defense strength: Thin to Moderate.** Small but a clean illustration of the vertical pattern.

---

**SentinelOne — S** *[security]*

- **The inference.** Behavioral detection of malicious activity on endpoints, and increasingly
  autonomous triage of alerts — the analyst labor line.
- **The corpus.** Telemetry across its install base, which is real and theirs.
- **Delete the model.** Signature-based detection survives, which is to say: the product regresses
  by a decade.
- **Best counter-argument.** "Centrality is fine, but it competes directly with CRWD — already a T1
  holding — and is losing. A correct thesis on the wrong horse."
- **Rebuttal.** Conceded. Included for category completeness, not conviction.
- **Defense strength: Strong on centrality, weak on competitive position.** Low priority.

---

### 4c. Already tracked — reconsider the tier, not the name

Promotion arguments, not new ideas:

- **APP (T3) — AppLovin.** Its ad-ranking engine (also, coincidentally, named Axon) *is* the P&L:
  auction-time prediction of install and purchase probability, trained on outcome data from its own
  install base, with the improvement showing up directly as revenue per impression. Under this exact
  thesis it is the strongest promotion case in the whole T3 block — arguably a purer archetype A
  than anything in §4a. **Defense strength: Strong.**
- **FICO (T3).** The score is a model, sold as inference, behind a regulatory-blessed near-monopoly,
  with pricing power that proves it. Textbook archetype A hiding in plain sight since 1989. The only
  counter is the definitional one already answered under Natera. **Defense strength: Strong.**
- **TEAM (T3).** Your own suggestion. Clean archetype B — huge proprietary corpus of work artifacts,
  technical founders, real commitment; Jira sells regardless. Promote to T2 if buying B; leave in T3
  under strict centrality.
- Already covered, no action: GWRE, IOT, SPOT, SHOP, AXON, HNGE (T1); PLTR, HTFL, RDDT, DASH, NOW,
  SNOW, MDB (T2); DUOL, TTD, MELI, NFLX, PINS, MSI, CVNA, Z, RKT, U, TWLO (T3).

### 4d. Private

The purest examples are not public — clinical documentation, legal agents, customer-service agents,
and coding agents, where the model is unambiguously the entire product and the delete-the-model test
is trivial. The `.pvt` mechanism already handles these (`config/watchlist.yaml → private_drivers`,
`notes/<pvt_id>/_profile.md`), and the SpaceX→SPCX migration is the proven IPO path. Say the word
and I'll draft a private-side screen on the same framework.

---

## 5. Scorecard

Defense strength on the *AI-powered* claim only — not on business quality, which is noted separately
where the two diverge.

| Strong | Moderate | Thin |
|---|---|---|
| IRTC, NTRA, GH¹, RELX, TRI, UPST², DE³, AUR⁴, RXRX⁵, APP, FICO, S⁶, TSLA⁹ | TEM, RDNT⁷, NU, VRSK, CLBT, KVYO, RBLX, INTU, **CHRW**¹⁰, RXO, UBER | TYL, CGNX, SYM, TOST, APPF, ISRG⁸ |

¹ weak business ² funding-fragile ³ cyclical, not a pure play ⁴ speculative ⁵ output unproven
⁶ losing to CRWD ⁷ best *structure* on the list ⁸ Thin on AI revenue, Strong on corpus
⁹ already T1; the template, not a new idea ¹⁰ most *verifiable* labor-substitution claim on the list

### The four tests, and how they relate

Across this memo we've now built four independent filters. They are ordered here by how hard each is
to fake — which is the same as how much weight to give each:

| # | Test | Source | Fakeable? |
|---|---|---|---|
| 1 | **Named product, priced, replacing something** (§8) | Product/pricing disclosure | Very hard — customers must pay |
| 2 | **Quantified AI revenue / inference in COGS** (§6) | 10-K, 10-Q full text | Hard — audited |
| 3 | **Senior AI officer named in a filing** (§7) | 8-K 5.02, DEF 14A | Moderate — real cost, but can be defensive |
| 4 | **Delete-the-model reasoning** (§1, §4) | Analysis | N/A — judgment, not evidence |

Use 4 to generate hypotheses, 1–3 to test them. A name passing three of four is a genuine
application-layer company; a name passing only 4 is a story I told myself, which is why every entry
in §4 carries its counter-argument.

*The shortlist that used to sit here has moved to **§11** — it was written before the §6–§9 screens
ran and no longer reflected the best names.*

---

## 6. Casting a wider net — the EDGAR language screen

*Added on your prompt: "cast a wider net than the companies under coverage — screen for words like
LLM, multiple models, AI-based product innovation… or revenue from AI."*

Sections 1–5 were bounded by what I could reason about. This section is bounded by nothing: it runs
against **EDGAR full-text search across every US filer**, not the 159 tickers in `watchlist.yaml`.
Script and dated output are saved at `scripts/screens/edgar_ai_language_screen.py` and
`…_20260819.json` — re-runnable each quarter.

### 6.1 The design principle: rarity *is* precision

The obvious version of this screen fails. Here is the calibration run, 10-K filings, Jun 2025 –
Aug 2026:

| Phrase | 10-K hits | 10-Q hits | Verdict |
|---|---|---|---|
| "artificial intelligence" | **4,194** | 5,979 | Useless — ~60% of all filers |
| "large language models" | 325 | — | Weak — vocabulary, not commitment |
| "foundation models" | 66 | 71 | Weak |
| "proprietary datasets" | 65 | 77 | Moderate |
| "monetize AI" | 4 | 1 | Strong |
| **"AI revenue"** | **5** | **13** | **Very strong** |
| "revenue from AI" | 5 | 7 | Very strong |
| "AI-driven revenue" | 0 | 3 | Very strong |
| "inference costs" | 7 | — | Very strong |

**This is the finding, and it validates your instinct precisely.** Roughly three in five public
companies now say "artificial intelligence" in a 10-K, so the word carries no information. But
almost none say **"AI revenue"** — about 0.3% of the filers who mention AI at all. The phrases worth
screening on are the ones that are *expensive to say falsely*: quantified revenue, and **inference
treated as cost of revenue**. A company that discusses inference in COGS is running models in
production at a volume material enough for the auditors, which is a far harder claim to fake than
"we are leveraging AI to transform." So I weighted phrases by disclosure cost — revenue and COGS
language at 5, proprietary-model/data claims at 2–3, generic vocabulary at 1 — and scored filers on
the sum of *distinct* phrases hit, not raw frequency.

That directly implements §2's third disqualifier: don't ask whether a company *talks* about AI, ask
whether it has **put a number next to it in an audited document.**

### 6.2 What the screen caught, and one instructive failure

213 filing rows (209 distinct CIKs) hit the high-precision phrase set; 192 were outside your
coverage; 11 were already on the watchlist (a reassuring cross-check — ANET, CRWD, GWRE, HNGE, IOT, MDB, PINS, SHOP, WELL and others
surfaced independently); 10 were excluded semis/hyperscalers.

**The instructive false positive:** Mid-America Apartment (MAA), Camden Property Trust (CPT), Realty
Income, Extra Space, and Public Storage all hit "AI revenue." They are not AI companies. Apartment
REITs run **"AI revenue management"** pricing software — a phrase collision. Also filtered out:
crypto miners repurposing sites into datacenters (MARA, CLSK, HUT, Mawson, Rackspace) which are
infrastructure, not application layer; and a long tail of sub-$50m shells with "AI" in the name
(Glidelogic, Z Squared, AIRWA, Appsoft, Safe Pro, Fusemachines). **A language screen without a size
and business filter returns mostly garbage** — the filter is what makes it usable, and it is the
part that cannot be automated away.

### 6.3 New names the screen produced — ranked

Market caps are latest reported quarter, USD millions, via FactSet. None of these are in T1–T4.

**Genuinely new and defensible — worth real work:**

| Name | Mkt cap | Phrase evidence | One-line defense |
|---|---|---|---|
| **ALGN** Align Technology | $12,016 (~2.8x sales) | "cost of AI" — **one weight-3 hit only** | Worth work, but **I initially overclaimed this and am correcting it.** The wrong version: "delete the model and you cannot manufacture the product." That is falsifiable and probably false — Align staged aligner series for two decades using CAD plus human treatment planners in offshore planning centers. The defensible version is archetype **B**: it owns an orthodontic outcomes dataset (millions of completed cases with before/after 3D geometry) that no competitor can assemble, and automating treatment planning attacks a large human labor line. That's a good idea; it is not proof of model-centrality, and the screen evidence here is thin — a single phrase. **Open diligence question: how much of treatment staging is a learned model today versus CAD with technician review?** Answer that before sizing anything. |
| **PL** Planet Labs | $13,176 (~35x sales) | "our proprietary AI models"; proprietary datasets | Owns a daily-refreshed imagery record of the entire landmass — a *temporal* corpus that cannot be back-filled at any price, because yesterday is gone. The sellable product is inference over it (change detection, crop state, asset counting), not pixels. **Valuation flag:** $13.2bn against $94m of quarterly revenue is roughly 35x sales and represents a very large rerating from this name's history. The business logic is sound; the price may already hold all of it. Verify the multiple independently before acting. |
| **DOCU** DocuSign | $8,879 | "AI infrastructure costs"; "inference costs"; proprietary datasets | Contrarian, and the phrase evidence is unusually strong — it discloses inference in its cost structure. Holds plausibly the largest corpus of executed agreements in existence, and is trying to convert a signature utility into agreement intelligence. If that conversion works it is a genuine B→A; if not, it's a melting seat business. Cheap enough that the option is not fully priced. |
| **ADPT** Adaptive Biotech | $3,412 | proprietary datasets | Structurally identical to Natera: immune-receptor sequencing plus a classifier for minimal residual disease, compounding on a proprietary immune-repertoire database. Same loop, earlier and smaller. |
| **INOD** Innodata | $2,598 | **"revenue from AI"**; foundation models | Sells engineered training and evaluation data to the frontier labs. Note the honest distinction: this is a **supplier to** the application layer, not a member of it — closer to picks-and-shovels. Its AI dependency is total; its margin quality is the open question, since the underlying work is expert human labor. |
| **WLY** John Wiley | $2,081 | **"AI revenue"** | One of only five 10-K filers in fourteen months to use that phrase. Licenses its scholarly corpus to model developers and discloses the revenue. The RELX argument in miniature, with the advantage that the number is actually printed. Risk: content licensing may prove episodic rather than recurring. |
| **NP** Neptune Insurance | $4,322 | proprietary datasets | Flood underwriting driven by a proprietary risk model rather than the federal rate tables — the pricing model *is* the company. What Lemonade claimed to be, in a line where the modeling edge is measurable. Recent listing, thin history. |
| **KDK** Kodiak AI | $986 | LLM/foundation-model vocabulary | Driverless trucking — a second, more literal answer to your "trucking and shipping" prompt than CHRW. Same profile as Aurora: unambiguous AI centrality, unproven business. |
| **EVLV** Evolv Technologies | $1,049 | "large language models"; proprietary datasets | AI weapons screening at venue entry — the model is the product, sold to the Axon-adjacent buyer. **Caveat: past accounting/disclosure problems.** Diligence governance before anything else. |
| **WAY** Waystar | $3,940 | proprietary datasets | Healthcare claims and denial prediction on a large proprietary claims corpus; attacks the revenue-cycle labor line directly. |
| **OPEN** Opendoor | $4,475 | "our proprietary AI models" | The home-pricing model literally is the business — buy wrong and you eat it. Maximum centrality, punishing economics. |
| **RDVT** Red Violet | $899 | proprietary datasets | Identity-resolution graph; small, profitable, genuine data asset. |

**Large-cap corpus plays the screen surfaced (already-known businesses, under-appreciated as AI assets):**
MCO Moody's ($78,437, "AI monetization" — ratings and credit corpus), IQV IQVIA ($31,804 — health
data at scale), PAYX Paychex ($34,486 — payroll data), FDS FactSet ($8,782, "AI monetization" —
your own vendor, which is a nice sanity check on the method), CLVT Clarivate ($1,382 — a distressed
version of the RELX argument).

**Recent IPOs disclosing inference as a cost — the §2 test passing in real time:**
FIG Figma ($9,598), TTAN ServiceTitan ($5,672), NAVN Navan ($4,417), NTSK Netskope ($4,020),
NCNO nCino ($1,902). Whatever else is true, these companies are running models at material volume.

**Too small to act on, noted for completeness:** CRNC Cerence ($512), GDYN Grid Dynamics ($461),
ZIP ZipRecruiter ($308), VERI Veritone ($136), SSTI SoundThinking ($119), NRDY Nerdy ($116).

### 6.4 The screen's unexpected bonus: it also finds the *disrupted*

IBEX, TaskUs, Genpact, ExlService, Robert Half, and Accenture all scored — because they discuss AI
heavily in **risk-factor** language rather than product language. That is §3's mirror risk showing up
as a machine-readable signal. Worth formalizing: the same phrase set, partitioned by whether the
language sits in Item 1 (Business) or Item 1A (Risk Factors), separates the companies selling AI
from the companies being sold out by it. That's a clean next iteration of this screen.

---

## 7. Cross-check: senior AI hiring

*Added on your prompt: "cross-check with hiring. Welltower has had jobs for AI but more importantly
hired senior people into senior AI roles."*

Your distinction is the right one and it is the whole design of this screen: **job postings are
cheap, org charts are expensive.** Anyone can post twelve ML-engineer reqs. Creating a C-suite or
EVP-level AI role, naming a person to it, and disclosing it to the SEC is a board-level capital
allocation that survives a budget cycle. So I screened **officer titles** in 8-K Item 5.02 (officer
appointments), DEF 14A proxies, and 10-K officer lists, Jan 2024 – Aug 2026. 122 filing rows matched,
representing **115 distinct companies** (some file the same title across several documents).

### 7.1 First, the honest limitation — your own example escapes it

**Welltower does not appear in these results.** That is not evidence Welltower hasn't hired senior AI
people; it is evidence of where the method is blind. SEC filings only name Section 16 officers and
named executive officers. A company can hire a VP of AI or a Head of ML from a hyperscaler — a
genuinely senior, genuinely expensive hire — and never file a word about it. So this screen has
**high precision and poor recall**: everything it finds is real, and it misses most of what you
actually want, including the case that prompted it.

The complete version needs job-posting and professional-profile data (posting velocity by seniority,
and inbound moves from frontier labs and hyperscalers), which SEC filings cannot see and this system
does not currently ingest. That is a real gap and worth naming as a build decision rather than
papering over. **Note also that WELL is already T1** — so the instinct that generated the example is
already reflected in the portfolio; what's missing is the systematic version.

### 7.2 What it did find — senior AI officers, ranked

**Large-cap, non-tech, genuinely notable:**

| Name | Title disclosed | Why it matters |
|---|---|---|
| **SPGI** S&P Global | Chief AI Officer (8-K) | Completes the professional-information set alongside RELX, TRI, MCO. Owns ratings, indices, and commodity price assessments — proprietary corpora with the same liability-grounding argument as legal research. Strong candidate; belongs in §4. |
| **MA** Mastercard | Chief AI and Data Officer (proxy) | The transaction graph is arguably the most valuable proprietary behavioral dataset in finance, and fraud scoring on it is genuinely model-native and genuinely priced. Fails §1 centrality (the network survives without it) but the corpus is exceptional. |
| **GEHC** GE HealthCare | Chief AI Officer (proxy) | Imaging AI at scale, with an installed base of scanners generating the data. Direct adjacency to HeartFlow and RadNet — the third leg of the medical-imaging AI thesis and the largest. Strong add. |
| **QXO** QXO | Chief Artificial Intelligence Officer (8-K) | The most interesting *non-tech* hit. A building-products distribution roll-up that named a Chief AI Officer at founding — explicitly running an AI-transformation playbook on a low-tech industry. Archetype B in its purest, most aggressive form. Unproven, but exactly the shape you're screening for. |
| **TW** Tradeweb | Head of AI (10-K, 8-K) | Electronic fixed-income trading; proprietary execution data. |
| **EXPE** Expedia | Chief AI Officer (proxy) | Travel demand and pricing data. |
| **RJF** Raymond James, **WFC** Wells Fargo, **BAM** Brookfield, **FNF** Fidelity National | CAIO / Head of AI | Financials committing at officer level. |

**Healthcare diagnostics — the cluster the hiring screen independently confirms:**
**WGS** GeneDx (Chief AI Officer — genomic interpretation for rare disease; the interpretation *is*
the product), **CDNA** CareDx (Chief Data and AI Officer — transplant surveillance, structurally a
Natera analogue), **HCAT** Health Catalyst, **UTHR** United Therapeutics, plus **RXRX** Recursion and
**ABSI** Absci, which also hit the language screen.

**Both signals — language *and* a senior AI officer.** This is the highest-conviction intersection
the two screens produce, because it pairs an audited economic claim with a board-level org
commitment: **FDS** FactSet, **RXRX** Recursion, **ABSI** Absci, **STGW** Stagwell, **AIOT**
Powerfleet (fleet telematics — video-based driver-safety inference on a proprietary fleet corpus;
small but a clean Samsara analogue). *Fusemachines and Mawson also intersect but are shells or
crypto-infrastructure — excluded.*

**Confirming your own instinct:** **TEAM Atlassian discloses a Head of AI** in both its 10-K and an
8-K. Your "maybe TEAM now" is supported by the org-chart evidence, not just the product narrative.

**And the mirror risk again, sharply:** **HSII** Heidrick & Struggles (executive search) and **EXLS**
ExlService both appointed AI leadership. When the staffing and BPO industries hire Chief AI Officers,
they are buying insurance against their own disruption — §3 showing up in the org chart.

---

## 8. The strongest test of all: name the product

*Added on your prompt: "focus more on AI-powered products — AI DJ at Spotify, AI-generated police
reports at Axon, AI-powered PT at Hinge."*

This is the best filter of the four you've proposed, and it should probably be the primary one. A
keyword can be written by an IR department. An officer title can be a defensive hire. **A shipped,
named product that customers use and that would not exist without a model is the thing itself.**

The test has three parts, and the third is where most candidates die:

1. **Can you name it?** If the answer is "they're infusing AI across the portfolio," there is no
   product.
2. **Does the model do the work, or assist a human who does the work?** AI DJ *chooses and sequences
   and voices*; a "smart playlist" filter does not.
3. **Is it priced, or is it free retention bait?** This is §2's third disqualifier. A product given
   away to defend a seat is a feature. A product with its own SKU, its own unit, or a measurable
   attach rate is a business.

### 8.1 Product inventory

*Two caveats, and the second is the important one. **(a)** Product names are as of my knowledge
(~May 2026) and are the claims most likely to have drifted — verify before citing; the mechanism
descriptions are structural and hold regardless of renaming. **(b) The "priced separately" column is
UNVERIFIED except for the reimbursed-healthcare rows.** Software vendors move products between
bundled and separately-priced frequently, and I am asserting rather than sourcing those cells. Treat
the software rows as hypotheses to check against pricing pages and disclosure. The healthcare rows
are different in kind: a third-party payer set the price after auditing the clinical claim, which is
externally verifiable and is why §8.2 rests its conclusion there.*

| Company | Named product | What the model actually does | Priced separately? |
|---|---|---|---|
| Spotify (T1) | **AI DJ** | Selects, sequences, and voices a personalized radio stream — programming, not filtering | No — retention/engagement |
| Axon (T1) | **Draft One** | Drafts a police report from body-camera audio; officer edits and signs | **Yes** — the model answer |
| Hinge Health (T1) | Computer-vision exercise therapy | Tracks joint position through a camera and corrects form in place of a therapist | **Yes** — it *is* the service |
| HeartFlow (T2) | **FFR<sub>CT</sub>** | Simulates coronary blood flow from a CT scan, replacing an invasive catheter procedure | **Yes** — per-analysis, reimbursed |
| Shopify (T1) | **Sidekick** | Merchant copilot over store data | No — bundled |
| Atlassian (T3) | **Rovo** | Search, agents, and chat over an org's own work artifacts | **Yes** |
| **iRhythm** | **Zio** service | Classifies ~2 weeks of continuous ECG into an adjudicated arrhythmia report | **Yes** — reimbursed per report |
| **Align** | **ClinCheck** / iTero | Turns a 3D oral scan into a staged tooth-movement plan that drives manufacturing | **Yes** — embedded in case price |
| **Deere** | **See & Spray** | Classifies each plant as crop or weed in real time and fires the nozzle | **Yes** — premium + outcome-priced |
| **Natera** | **Signatera** | Detects parts-per-million tumor DNA against a personalized variant panel | **Yes** — reimbursed |
| **Guardant** | **Shield** | Classifies cancer signal from a blood draw | **Yes** — reimbursed |
| **RadNet** | **DeepHealth** | Reads mammography; sold to the patient as an enhanced screen | **Yes** — cash-pay upsell |
| **Thomson Reuters** | **CoCounsel** | Drafts and researches law grounded in Westlaw with verifiable citations | **Yes** |
| **RELX** | **Lexis+ AI / Protégé** | Same, on the LexisNexis corpus | **Yes** |
| AppLovin (T3) | **Axon** engine | Predicts install/purchase probability at auction time | **Yes** — it *is* the revenue |
| CrowdStrike (T1) | **Charlotte AI** | Triages alerts, compressing analyst labor | **Yes** |
| **SentinelOne** | **Purple AI** | Same | **Yes** |
| Palantir (T2) | **AIP** | Wires models into operational decision loops | **Yes** |
| Duolingo (T3) | **Max** / video call | Generates lessons and conversational practice | **Yes** — premium tier |
| **DocuSign** | **IAM** | Extracts obligations and risk from executed agreements | **Yes** |
| **Waystar** | **AltitudeAI** | Predicts and prevents claim denials | **Yes** |
| **Planet Labs** | Planetary Variables | Turns daily imagery into measured land/crop/asset state | **Yes** |
| **Evolv** | **Evolv Express** | Discriminates weapons from benign metal at venue entry | **Yes** — it *is* the product |
| **Tempus** | Lens / xT assays | Diagnostic classifiers + a queryable clinical-molecular library | **Yes** |
| AppFolio (T3 cand.) | **Realm-X** | Handles leasing and maintenance conversations | **Yes** — add-on |
| Robinhood (T3 cand.) | **Cortex** | Synthesizes market context per position | **Yes** — Gold tier |
| **NICE** | CXone Mpower | Automates the contact-center interaction | **Yes** — and cannibalizes seats (§3) |
| Salesforce | **Agentforce** | Task agents over customer-owned CRM data | Yes — *but* §1 data-ownership problem |

### 8.2 What the product lens changes

Reading down the "priced separately" column reorders the list. Three observations:

- **The reimbursed-healthcare names pass all three parts cleanly, and this is the only conclusion the
  table can currently carry.** Named product, model does the work, and independently priced by a
  third-party payer who audited the clinical claim before agreeing to pay. That is the strongest form
  of the test available anywhere, because the pricing decision was made by a skeptical outside party
  rather than by the company's own pricing committee — and unlike the software rows, it is externally
  verifiable. IRTC, NTRA, GH, RDNT, and HTFL clear it.
- **Spotify and Shopify appear to monetize their AI through retention rather than price** — AI DJ and
  Sidekick look like products given away to defend engagement. If that holds, the AI shows up as
  churn reduction rather than a revenue line, which would independently confirm they sit in a
  different bucket from HeartFlow and Hinge. Flagged as *likely* rather than established, per caveat
  (b) above — it is worth ten minutes on their pricing disclosure to settle it, because it's a clean
  test of the archetype split.
- **The best single question to ask any candidate management team** falls straight out of this:
  *"Name the AI product, tell me what it's priced at, and tell me what it replaced."* A company with
  a real answer to all three gives it immediately. A company without one will describe a strategy.

---

## 9. Physical AI — yes, but it inverts the moat logic

*Added on your prompt: "should we add physical AI as is the case with robotics?"*

Yes — and it belongs as a distinct sub-archetype rather than as names sprinkled through §4, because
**what makes a physical-AI company defensible is not what makes a software one defensible.** Getting
that backwards is the main way this category is misjudged.

### 9.1 The boundary: learned policy vs. classical automation

Most of what is marketed as "robotics" fails the delete-the-model test — in the *opposite* direction
from AI-washed software. Industrial robots have done precise, repeatable work for forty years using
classical control theory, kinematics, and operations research. None of that is a learned model, and
bolting a vision classifier onto a pick-and-place cell does not make the company AI-central.

The line worth drawing: **does a learned policy replace a human sensorimotor skill that could not be
programmed explicitly?** Recognizing an individual weed among crops, driving a highway, grasping
arbitrary objects, reading a surgical field — these resisted explicit programming for decades
precisely because the rules cannot be written down. That is physical AI. Palletizing along a fixed
path is not.

This is why §4 graded **SYM** and **CGNX** Thin — warehouse orchestration is substantially an
optimization problem, and industrial machine vision is commoditizing from above — and why **DE**,
**TSLA**, **AUR**, and **KDK** graded Strong on mechanism.

### 9.2 First inversion: in the physical world, nobody has the data

In software the moat question is *who owns the corpus*, and the answer varies enormously — which is
why §1 makes data ownership the key discriminator. In the physical world, **everybody is data-poor.**
There is no internet-scale corpus of robot manipulation or of driving in rare conditions. You cannot
scrape it. It must be generated one physical interaction at a time, at real cost.

So the durable asset is not the data — it is **the data-collection channel**: a deployed fleet,
funded by someone else, generating labeled physical experience as a byproduct of paid work. That one
criterion sorts the category:

- **Tesla** — customers buy the fleet that collects the training data. Collection is revenue-positive.
- **Deere** — machines already in the fields, sold at a profit, instrumented.
- **Intuitive Surgical** — every procedure yields video paired with synchronized instrument telemetry,
  across an installed base that took twenty years to place.
- **Aurora / Kodiak** — must *pay* to run a fleet purely to collect, with no offsetting revenue until
  autonomy works. Structurally the hardest position in the category.

**That asymmetry, not model quality, is the thing to underwrite.** A company collecting at a profit
can iterate indefinitely; one collecting at a loss is racing a cash clock.

### 9.3 Second inversion: the constraint is validation, not capability

In software, a model that is right 95% of the time often ships. In physical AI the binding constraint
is proving safety to a regulator or a court — and that cost scales with **severity of the failure
mode**, not with the difficulty of the task. Which is why surgical autonomy and driverless trucking
have been "two years away" for a decade while agricultural spraying shipped and scaled: **a
misclassified weed costs a few cents.**

Rank physical-AI opportunities by consequence-of-error first and technical difficulty second. It is a
better timeline predictor than any capability benchmark.

### 9.4 Candidates, regrouped

**Already defended in §4:** DE (Strong — profitable collection channel, low consequence-of-error,
shipping now), TSLA (Strong — the template), ISRG (corpus Strong / AI-revenue Thin), AUR and KDK
(pure, but loss-funded collection), CGNX and SYM (Thin — largely classical).

**Worth adding under this frame:**

| Name | Physical-AI claim | Grade |
|---|---|---|
| **MBLY** Mobileye *(already T3)* | Perception stack across a very large deployed vehicle base — a collection channel funded by OEM customers, i.e. the profitable side of §9.2. Under-tiered for this thesis. | Moderate–Strong |
| **AVAV** AeroVironment | Loitering munitions and small UAS with increasing onboard autonomy. The buyer is defense, where consequence-of-error is *accepted* rather than litigated — which materially changes the §9.3 timeline. | Moderate |
| **PRCT** Procept BioRobotics | Robotic tissue resection executing a planned path autonomously rather than under direct manual control. Narrow indication, but genuinely a machine performing the intervention. | Moderate |
| **EVLV** Evolv *(from §6)* | Discriminating weapons from benign metal in a live physical stream — perception where the explicit-rules approach demonstrably failed. Governance caveat stands. | Moderate |
| **ZBRA** Zebra | Vision, scanning, warehouse workflow data at scale. Closer to classical than learned — add only if the AI attach becomes visible in pricing. | Thin |

### 9.5 The honest conclusion: the best physical AI is private

This is the category where the public market offers the worst menu. Public physical-AI is mostly
either (a) pre-revenue pure plays racing a cash clock, or (b) industrial incumbents where the AI is a
small attachment on a cyclical P&L. The companies actually building general manipulation policies and
driverless fleets — the humanoid developers, the robot-foundation-model labs, the leading driverless
operator, the defense-autonomy prime — are **all private.**

That is not a reason to skip the category. It is a reason to route it through machinery you already
have: **register the physical-AI privates as `.pvt` drivers** (`private_drivers` in
`config/watchlist.yaml`, profiles at `notes/<pvt_id>/_profile.md`), exactly as you do for the model
labs. They move public names — TSLA, ISRG, DE, and the T4 supply chain — long before any of them
lists, and the SpaceX→SPCX migration is the proven path if one does.

---

## 10. Suggested actions

1. **Add an `ai_application_layer` theme** to the master vocabulary in `config/watchlist.yaml`, with
   sub-tags `model_native` and `corpus_plus_leadership`, so the news classifier separates the
   archetypes instead of blurring them into the existing `ai_*` themes.
2. **T2 adds from §4, ranked by defense strength × business quality:** IRTC, RELX, DE, NTRA, TRI,
   VRSK, CHRW, NU, TEM, CLBT, RDNT, KVYO, INTU.
2b. **T2/T3 adds from the §6 screen (names I did not reach by reasoning):** ALGN and PL first — both
   are archetype A with corpora that cannot be reconstructed, and neither shows up on conventional
   AI screens. Then ADPT, DOCU, WLY, NP, WAY. T3 for KDK, EVLV, OPEN, RDVT, INOD.
2c. **Re-run the screen quarterly** — `python3 scripts/screens/edgar_ai_language_screen.py` — and
   diff against `edgar_ai_language_screen_20260819.json`. New filers crossing into the "AI revenue" /
   "inference costs" tail are the leading indicator; that tail had roughly 30 members this cycle, so
   additions are individually meaningful rather than lost in noise.
2d. **Build the Item 1 vs Item 1A split** (§6.4) so the same screen separates AI sellers from AI
   casualties.
2e. **Adds from the §7 hiring screen:** SPGI and GEHC first (both are §4-quality names I did not reach
   by reasoning — SPGI completes the professional-information set, GEHC is the largest medical-imaging
   AI asset). Then MA, TW, WGS, CDNA, QXO (the non-tech wildcard), AIOT.
2f. **Close the hiring blind spot (§7.1).** The SEC screen has high precision and poor recall — it
   misses exactly the Welltower case that prompted it. A real hiring signal needs job-posting velocity
   by seniority plus inbound moves from frontier labs and hyperscalers. That is a new ingest channel,
   not a query; scope it before building it.
2g. **Adopt the §8 product test as the primary filter.** For every candidate, record: product name,
   what the model does, price/unit, and what it replaced. Names with no answer get demoted regardless
   of how well they screen on language or hiring.
2h. **Physical AI (§9):** add MBLY tier review (already T3, under-tiered), plus AVAV and PRCT to T3.
   Register the physical-AI privates as `.pvt` drivers — humanoid developers, robot-foundation-model
   labs, the leading driverless operator, the defense-autonomy prime. That is where the category
   actually lives.

## 11. The shortlist, after all four tests

*This replaces the earlier five-name list, which was written before the §6–§9 screens existed.*

**If you take only eight names forward:**

| Name | Why it survives all the filtering |
|---|---|
| **IRTC** iRhythm | Purest archetype A — HeartFlow's structural twin. Labeled ECG corpus + FDA + a reimbursement code; the classifier *is* the report that gets paid for. |
| **RELX** | Best unconverted corpus in the market. Owns the legal and scientific ground truth that generative AI makes *more* valuable, not less, because hallucination is disqualifying in both domains. |
| **DE** Deere | Proves the thesis extends outside tech. Vision decides per plant, priced on outcome, on a data-collection channel competitors cannot buy. |
| **APP** AppLovin *(T3 → promote)* | Already owned, wrong tier. The ranking model is the P&L. |
| **CHRW** C.H. Robinson | The only name where the labor substitution is **publicly auditable** — shipments per employee is a disclosed metric. |
| **SPGI** S&P Global *(§7)* | Named a Chief AI Officer; completes the professional-information set with RELX/TRI/MCO on proprietary, legally trainable corpora. |
| **GEHC** GE HealthCare *(§7)* | The largest medical-imaging AI asset, with an installed base of scanners generating its own training data. Third leg of the imaging thesis alongside HTFL and RDNT. |
| **PL** Planet Labs *(§6)* | A temporal Earth record that cannot be back-filled at any price. **Caveat: ~35x sales — the business logic may already be in the price.** |

**Two names I flagged and then walked back, kept visible so the reasoning is auditable:** ALGN
(overclaimed initially — the corpus argument holds, the model-centrality claim does not survive
scrutiny; see §6.3) and ISRG (superb corpus, no AI revenue — own it for the robot, hold the corpus
as a free option).

## 12. Reusability — what was built, not just concluded

- `scripts/screens/` — both scans, a diff that reports new entrants, a quarterly runner, and a README
  covering the three traps in reading the output.
- `skills/ai-application-layer-screen/SKILL.md` — the judgment layer: archetype split, four tests,
  negative screen, and the required per-name defense format. Loads whenever the question "is this
  really an AI company?" comes up, in this or any future session.
- **The split is deliberate:** cron runs the scans because a skill cannot be scheduled; the skill
  interprets them because a script cannot exercise judgment. Neither half is useful alone.
3. **Tier review:** APP and FICO T3 → T2; TEAM T3 → T2 if buying archetype B. TSLA already T1 — no
   action, but worth re-tagging under the new theme since it is the pattern the rest are screened
   against.
4. **Watch-for-conversion list (not positions):** TYL, ISRG — corpora that could become model-native,
   with no present AI revenue claim.
5. **One-page tension note:** NICE/Verint as corpus-owner *and* disrupted seat (§3). Not a position —
   a framework stress-test that will sharpen every other name here.

---

*Related: [[digest_output_preferences]] (signal density over completeness); the `.pvt` convention in
CLAUDE.md §"Private-name identifiers".*
