# AI application layer — ranked most to least AI-forward

2026-08-20. 60 names, ranked by **thesis score**: model centrality (delete the model —
does the product still exist and sell?) times whether there is a named product doing the
work at a price. Evidence from five EDGAR/GitHub/blog screens adjusts by at most +8 and
is shown per name; it confirms or contradicts a thesis, it never sets one.

**BCTK holdings are marked [BCTK].** Everything else carries a two-sentence note on what
the company does and why it qualifies — or, where the case is weak, why it does not.


## Tier 1 — the model IS the product

**1. HNGE** — 100.4 **[BCTK]**  ·  centrality 5/5, product 3/3  ·  _filing-lang 1_

**2. GH** — 100.4  ·  centrality 5/5, product 3/3  ·  _filing-lang 1_

Liquid-biopsy diagnostics: a blood draw detects circulating tumor DNA for therapy selection, recurrence monitoring and screening. The commercial product is a classifier calling cancer signal at parts-per-million against a proprietary clinical-genomic database — delete the model and you have a vial of blood.

**3. IRTC** — 100.0  ·  centrality 5/5, product 3/3  ·  _not developer-facing_

The Zio patch records up to ~14 days of continuous ECG and returns an adjudicated arrhythmia report. A million-plus heartbeats per patient cannot be read economically by humans, so the classifier plus a decade of labelled recordings is both the product and the moat, gated by FDA clearance and a reimbursement code.

**4. APP** — 98.2  ·  centrality 5/5, product 3/3  ·  _not developer-facing_

Mobile advertising platform whose Axon engine predicts install and purchase probability at auction time. The ranking model literally is the P&L: improvements show up directly as revenue per impression, with no intervening product.

**5. RDNT** — 93.9  ·  centrality 4/5, product 3/3  ·  _not developer-facing_

The largest US outpatient diagnostic imaging network, plus its DeepHealth AI for mammography. It owns the scanners, the images and the biopsy outcomes that label them — data supply, model and distribution vertically integrated — and sells the AI read as a cash-pay upsell.

**6. HTFL** — 90.9  ·  centrality 5/5, product 3/3  ·  _not developer-facing_

Takes an ordinary coronary CT scan and returns a physiologic assessment of blood flow, replacing an invasive catheter procedure. The deliverable IS a deep-learning inference on the scan, FDA-cleared and reimbursed per analysis — the purest form of the thesis.

**7. AXON** — 90.9 **[BCTK]**  ·  centrality 4/5, product 3/3  ·  _not developer-facing_

**8. DE** — 90.9  ·  centrality 4/5, product 3/3  ·  _not developer-facing_

Agricultural and construction equipment. See & Spray runs real-time computer vision across a sprayer boom, classifying each plant as crop or weed and firing individual nozzles; it is priced on herbicide saved, and the training data comes from a machine fleet customers already paid for.

**9. UPST** — 90.3  ·  centrality 5/5, product 2/3  ·  _filing-lang 3_

AI lending platform originating consumer loans through bank partners using its own underwriting model. The product IS the credit decision, trained on repayment outcomes including borrowers a bureau cutoff would have rejected — counterfactual data no traditional lender ever observes.

**10. IOT** — 89.1 **[BCTK]**  ·  centrality 4/5, product 3/3  ·  _not developer-facing_

**11. RXRX** — 86.4  ·  centrality 5/5, product 1/3  ·  _filing-lang 5; AI officer 8_

AI drug discovery: runs industrial-scale automated cell-biology experiments and maps microscopy images into a space where similarity implies shared biological mechanism. The purest archetype A on the list — remove the model and there is no company — but clinical output remains unproven.

**12. PLTR** — 85.7  ·  centrality 4/5, product 3/3  ·  _gh-traction 4.0; blog-operator 4_

Data integration and decision software for governments and large enterprises; AIP wires models into operational workflows. It sells the decision loop rather than a database, and the ontology layer is what makes models actionable on messy institutional data.


## Tier 2 — model-native, weaker proof

**13. CRWD** — 84.3 **[BCTK]**  ·  centrality 3/5, product 3/3  ·  _filing-lang 2; gh-traction 10.0; blog-operator 0_

**14. KDK** — 81.8  ·  centrality 5/5, product 1/3  ·  _not developer-facing_

Driverless trucking for freight and defence applications. Same shape as Aurora: the driving policy is the company, with the same loss-funded data-collection problem.

**15. NTRA** — 81.8  ·  centrality 5/5, product 3/3  ·  _not developer-facing_

Molecular diagnostics; Signatera sequences a patient's tumor to build a personalised ctDNA panel that detects residual or recurrent disease. Detection at parts-per-million is a statistical inference problem whose sensitivity improves with accumulated data — a compounding loop a competitor cannot shortcut.

**16. SERV** — 81.8  ·  centrality 5/5, product 1/3  ·  _not developer-facing_

**17. TSLA** — 81.8 **[BCTK]**  ·  centrality 4/5, product 2/3  ·  _not developer-facing_

**18. AUR** — 79.8  ·  centrality 5/5, product 1/3  ·  _not developer-facing_

Autonomous trucking, operating driverless Class 8 freight on highway routes. Perception, prediction and planning are the entire product — unambiguous AI centrality, unproven business, and it must fund its data collection at a loss.

**19. EVLV** — 77.3  ·  centrality 4/5, product 3/3  ·  _not developer-facing_

AI weapons screening at venue entrances — stadiums, schools, hospitals — letting people walk through without emptying their pockets. Discriminating a firearm from a laptop in a live physical stream is precisely what explicit rules failed at, so the model is the product. Caveat: past accounting and disclosure problems.

**20. NET** — 75.9 **[BCTK]**  ·  centrality 3/5, product 2/3  ·  _gh-traction 10.0; blog-operator 7_

**21. GEHC** — 75.2  ·  centrality 3/5, product 2/3  ·  _AI officer 8_

Imaging hardware — MRI, CT, ultrasound — plus diagnostics. The largest installed base generating imaging data, a named Chief AI Officer, and reconstruction and triage models shipping inside the scanner itself.

**22. TEM** — 74.3  ·  centrality 4/5, product 2/3  ·  _filing-lang 1_

Precision medicine: sequences tumors and links results to longitudinal clinical outcomes, monetised as diagnostics and as data licensing to pharma. The asset is the *join* between molecular and clinical data, which requires being embedded at the point of care — diligence the licensing revenue mix before underwriting it.

**23. ADPT** — 73.5  ·  centrality 4/5, product 3/3  ·  _filing-lang 2_

Immune medicine: sequences T- and B-cell receptors, and clonoSEQ tracks minimal residual disease in blood cancers. Structurally identical to Natera — a classifier over a proprietary immune-repertoire database, with FDA clearance and reimbursement gating any entrant.

**24. CNH** — 72.7  ·  centrality 3/5, product 2/3  ·  _not developer-facing_

**25. AVAV** — 72.7  ·  centrality 3/5, product 2/3  ·  _not developer-facing_

**26. ONDS** — 72.7  ·  centrality 3/5, product 2/3  ·  _not developer-facing_


## Tier 3 — strong corpus, real overlay

**27. RELX** — 67.3  ·  centrality 3/5, product 3/3  ·  _developer-facing, no data collected_

LexisNexis legal research, Elsevier scientific publishing, and risk/identity analytics. It owns the ground truth generative systems must be grounded in — editorially maintained case-law citation treatment and the scientific literature — and sells the answer rather than the search box.

**28. TRI** — 67.3  ·  centrality 3/5, product 3/3  ·  _developer-facing, no data collected_

Legal, tax and news information; CoCounsel does research and drafting grounded in the Westlaw corpus. Same liability-grounding argument as RELX: a lawyer cannot file a brief citing a case that may not exist, and the verification layer is proprietary.

**29. MDB** — 65.4  ·  centrality 3/5, product 2/3  ·  _filing-lang 1; gh-traction 2.2; blog-operator 13_

General-purpose document database with integrated vector search. It is substrate for retrieval-augmented applications, and its engineering writing scores the highest operator-register of anything screened — it writes like an organisation actually running models in production.

**30. TEAM** — 65.4  ·  centrality 2/5, product 3/3  ·  _AI officer 7; gh-traction 10.0; blog-operator 2_

Jira, Confluence and Bitbucket, with Rovo adding search and agents over a company's own work artifacts. It sits on an enormous proprietary corpus of tickets, documents and code review, and its 1,038-star public MCP server shows the agent surface is real — but Jira sells perfectly well without any of it.

**31. FICO** — 63.6  ·  centrality 3/5, product 3/3  ·  _not developer-facing_

Sells credit scores and decisioning software to lenders. The score is a model sold as inference, behind a regulatory-blessed near-monopoly with demonstrated pricing power — archetype A hiding in plain sight since 1989.

**32. PL** — 63.6  ·  centrality 3/5, product 2/3  ·  _not developer-facing_

Operates the largest fleet of Earth-imaging satellites, photographing the entire landmass daily. It sells answers — crop state, change detection, asset counts — derived from a temporal record that cannot be back-filled at any price, because yesterday is gone. Trades near ~35x sales.

**33. MBLY** — 63.6  ·  centrality 2/5, product 2/3  ·  _not developer-facing_

Supplies ADAS and autonomous driving systems to automakers. The perception stack is the product, and its training data arrives from a deployed vehicle fleet that OEM customers paid for — the profitable side of the data-collection channel.

**34. APTV** — 63.6  ·  centrality 2/5, product 2/3  ·  _not developer-facing_

**35. NP** — 63.5  ·  centrality 3/5, product 2/3  ·  _filing-lang 4_

Private flood insurance underwritten on its own risk model rather than federal rate tables. The pricing model is the company — what Lemonade claimed to be, in a line where the modelling edge is directly measurable in loss ratios.

**36. OPEN** — 63.0  ·  centrality 3/5, product 2/3  ·  _filing-lang 3_

iBuyer: purchases homes directly from sellers and resells them. The automated valuation model *is* the business — misprice and the inventory eats you — which is maximum centrality attached to punishing economics.

**37. SPGI** — 62.5  ·  centrality 3/5, product 2/3  ·  _AI officer 12; gh-traction 0.0_ · ⚠ claims > traction

Ratings, indices, and market and commodity data. Proprietary corpora being made agent-addressable under a named Chief AI Officer — though flagged claims-exceed-traction here, because the public developer surface is thin relative to the filings.

**38. CLBT** — 61.8  ·  centrality 3/5, product 2/3  ·  _not developer-facing_

Digital forensics for law enforcement: extracts and analyses data from seized devices. Extraction is engineering, but the paid job is triage — entity resolution, image classification, transcription across terabytes — the Axon pattern of a system-of-record moat monetised through model-native product.

**39. SPOT** — 61.8 **[BCTK]**  ·  centrality 2/5, product 2/3  ·  _gh-traction 0.0; blog-operator 0_

**40. RBLX** — 61.8  ·  centrality 2/5, product 2/3  ·  _not developer-facing_

User-generated 3D gaming platform. Real-time safety classification across voice and text involving minors is a licence to operate rather than a feature, and generative creation tools lower the skill floor for the creator base that supplies all its content.

**41. CHRW** — 60.0  ·  centrality 3/5, product 2/3  ·  _not developer-facing_

Freight brokerage matching shippers' loads to carriers' trucks. It now parses quote requests, prices lanes and matches carriers automatically — and uniquely on this list, the labour substitution is publicly auditable through disclosed shipments-per-employee.


## Tier 4 — AI real but not load-bearing

**42. ISRG** — 57.9  ·  centrality 3/5, product 1/3  ·  _filing-lang 1_

Makes the da Vinci surgical robots. It owns the largest surgical video corpus paired with synchronised instrument telemetry — the best unconverted dataset in med-tech — with no meaningful AI revenue yet; own it for the robot and hold the corpus as a free option.

**43. SHOP** — 56.8 **[BCTK]**  ·  centrality 2/5, product 2/3  ·  _filing-lang 2; AI officer 4; gh-traction 6.4; blog-operator 0_

**44. FDS** — 55.1  ·  centrality 2/5, product 2/3  ·  _filing-lang 4; AI officer 8; gh-traction 0.0_ · ⚠ claims > traction

Financial data and analytics for institutional investors. It has a Chief AI Officer and is exposing its corpus through MCP so agents can query it directly; it clears all three filing screens, and its claims-exceed-traction flag is a false positive — the MCP server is real, just not on public GitHub.

**45. FIG** — 54.7  ·  centrality 2/5, product 2/3  ·  _filing-lang 3; gh-traction 9.3_

Collaborative interface design software. It holds design files as structured data rather than pixels, which is exactly what makes generative design and its 1,910-star MCP server function.

**46. V** — 54.5  ·  centrality 2/5, product 2/3  ·  _gh-traction 0.0_

Global payment network. The transaction graph is among the most valuable proprietary behavioural datasets in finance and it is building an agentic-commerce surface — but the network survives entirely untouched without any model, so centrality is limited.

**47. OUST** — 54.5  ·  centrality 2/5, product 2/3  ·  _not developer-facing_

**48. WLY** — 53.9  ·  centrality 3/5, product 2/3  ·  _filing-lang 5; AI officer 3_

Academic and professional publishing. It licenses its scholarly corpus to model developers and is one of only five 10-K filers in fourteen months to use the phrase 'AI revenue' — a rare case of a company printing the number rather than gesturing at it. But size the number against the business: revenue is flat (Apr-26 $447.9m vs Apr-25 $442.6m, +1.2%) and the margin gain is cost-out, not AI mix. The disclosure is admirable and the corpus licence is a real option; it is not yet moving the P&L.

**49. ESTC** — 53.6  ·  centrality 2/5, product 2/3  ·  _gh-traction 10.0; blog-operator 1_

Search and observability, built on Elasticsearch with vector search. It is retrieval infrastructure sitting underneath RAG applications, with a 765-star MCP server confirming a real developer surface.

**50. NU** — 52.7  ·  centrality 2/5, product 2/3  ·  _not developer-facing_

Latin American digital bank serving roughly 100m+ customers on an in-house core stack. It underwrites customers who have no bureau file using first-party behavioural data, so in a thin-file market it effectively *is* the bureau; operating expense per active customer is the falsifiable test.


---

## Method notes

- **Ranking is centrality, not evidence volume.** An earlier build folded evidence into
  the denominator and penalised names measured on more dimensions — FactSet cleared all
  three filing screens and fell to 45th while HeartFlow scored 100 partly by being
  measured on fewer. Corrected.
- **Practitioner evidence applies only to developer-facing firms.** Scoring iRhythm on
  GitHub stars would measure that it is a medical device company, not that it is less
  AI-central. The cost: top-tier diagnostics names rest on judgment plus reimbursement,
  with no independent corroboration layer. That is the weakest link in tier 1.
- **⚠ claims > traction** marks names loud in filings and silent where practitioners
  would notice. For FDS this is a known false positive — its MCP server is real but not
  on public GitHub. For MORN it is not: 21 stars, 338 days since last push.
- Regenerate: `python3 scripts/screens/rank_ai_forward.py`
