# Thesis assumptions — COHR / LITE (DRAFT for operator review)

**Status: PROPOSAL. Nothing wired, nothing written to `config/watchlist.yaml`.**

Phase 3 of the plan. Every assumption below is *restated from your own scoring notes* dated
**2026-06-02** — the `derived_from` line quotes the phrase it came from. I have not invented
a view. Where I think an assumption is missing from your notes entirely, it is marked
**[GAP]** and needs your judgement, not mine.

Why decompose at all: a score of "4" cannot be challenged by evidence. A statement like
"datacom transceiver supply stays tight" can be — and that is what lets new filings and news
be tested against the position instead of just accumulating.

Each assumption carries a `challenged_by` line describing *observable* evidence. That is the
part the entity/claim extraction can actually match against.

---

## COHR — Coherent (T1, scored 2026-06-02)

### `vertical_integration_moat`
**Statement:** COHR is vertically integrated from in-house indium-phosphide lasers through to
transceivers, and that integration is why innovation scores 4.  *(CORRECTED 2026-08-21 —
originally added "durable" and "competitors cannot easily replicate". The note establishes
that COHR IS integrated; it does not claim the advantage is durable or hard to replicate.
That distinction is load-bearing now that `chinese_laser_capability` is the crux.)*
**Derived from:** `competitive_advantage.innovation_rate: 4` — *"vertically integrated optics
(indium-phosphide lasers -> transceivers), datacom transceiver ramp"*.
**Challenged by:** a competitor demonstrating in-house InP/EML chip capability at comparable
volume; merchant laser supply becoming abundant enough that integration stops mattering;
Accelink or similar shipping integrated chip-to-module at 800G+.
**Confirmed by:** competitors publicly constrained by third-party laser supply; COHR gross
margin holding while merchant module prices fall.

### `supply_was_tight_at_scoring`  *(CORRECTED 2026-08-21)*
**Statement:** Datacom transceiver supply was tight as at 2026-06-02, and the distribution
score of 4 was set under those conditions. The assumption is that those conditions still hold
— not that tightness is a durable property of the market.
**Derived from:** `competitive_advantage.distribution: 4` — *"broad datacom customer base
across hyperscalers **amid** transceiver supply tightness"*.
**Correction note:** originally *"supply REMAINS tight, SUPPORTING price and share"*. Two
additions: "remains" projected a point-in-time observation forward, and "supporting price and
share" added a causal mechanism the note never states. "Amid" describes the backdrop the score
was set against. This matters for how evidence reads: as originally written, Chinese capacity
growth "challenges the thesis"; as the operator actually wrote it, the same evidence says
"the conditions behind a June score have changed" — which is a re-score trigger, not a
falsification.
**Challenged by:** capacity additions at 800G/1.6T from Innolight/Eoptolink; a large capital
raise funding competitor capacity; transceiver ASP declines; hyperscalers publicly
dual-sourcing on price.
**Confirmed by:** continued lead-time extension; customers pre-paying or committing capacity.
**Note:** this is the assumption most exposed to the Chinese-competition question, and the
one the 2026-07-30 Innolight Hong Kong listing (~$6.8-7B raised) bears on most directly.

### `datacom_ramp_continues`
**Statement:** The 800G→1.6T datacenter ramp continues to pull COHR volume.
**Derived from:** `ai_positioning: 4` — *"AI-datacenter optical transceivers (800G/1.6T)
... Direct AI-optics beneficiary on the datacenter buildout"*.
**Challenged by:** hyperscaler capex digestion; a shift to co-packaged optics that bypasses
pluggable transceivers; slower 1.6T adoption than planned.
**Confirmed by:** hyperscaler capex guides up; 1.6T design wins.

### `customer_concentration_not_worsening`  *(CORRECTED 2026-08-21)*
**Statement:** Datacom customer concentration exists and is already reflected in the
distribution score of 4; the assumption is that it does not deteriorate from there.
**Derived from:** `competitive_advantage.distribution: 4` — *"some customer concentration in
datacom"*.
**Challenged by:** a top customer qualifying a second source; concentration rising; a named
customer moving volume to a Chinese supplier.
**Correction note:** originally written as `customer_concentration_tolerable` — *"a known risk
but not thesis-breaking"*. That was an over-read: the operator's note records concentration as
a CAVEAT on the score, not a judgement that it is tolerable. The claim now asserts only what
the score itself implies.

### `leverage_is_a_watch_item`  *(CORRECTED 2026-08-21)*
**Statement:** Post-II-VI/Finisar balance-sheet leverage is a monitored risk, explicitly
flagged as a watch-item within an investor-interest score of 4. The assumption is that it does
not worsen — NOT that deleveraging is progressing.
**Derived from:** `potential_investor_interest: 4` — *"turnaround/deleveraging story ...
Post-II-VI/Finisar balance-sheet leverage is a **watch-item**"*.
**Challenged by:** leverage flat or rising; refinancing at worse terms; FCF miss.
**Correction note:** originally *"leverage continues to come down"*. Same failure as the
telecom inversion: a watch-item is a risk under observation, and I converted it into an
assertion that progress is being made. The note calls deleveraging a "story" (the narrative)
and the leverage itself a "watch-item" (the risk).

### `chinese_laser_capability` — THE CRUX (operator, 2026-08-21)
**Statement:** Chinese optical vendors cannot yet manufacture high-quality lasers (InP/EML)
at high yield, and that manufacturing gap — not policy — is what limits their share gain
against COHR and LITE.
**Derived from:** operator, 2026-08-21 — *"The real thing we should continue to monitor is
whether the chinese companies can garner more marketshare and manufacture high quality lasers
with high yields and high quality. that's the real concern."*
**SHARED WITH LITE.** This is the same question underneath COHR's `vertical_integration_moat`
and LITE's `eml_laser_supply_position`: COHR's moat IS in-house InP laser manufacture, and
LITE's position IS being the merchant laser supplier. Chinese laser parity erodes both at
once. Track it as ONE assumption, not two — a single piece of evidence moves both names.
**Challenged by:** a Chinese vendor disclosing in-house laser/EML chip production at scale;
published or implied yield improvement; a Chinese module maker shifting from imported to
domestic laser chips; hyperscaler qualification of a Chinese-laser-based module; share gain
at 800G/1.6T sustained with margin (price-cutting alone is not capability).
**Confirmed by:** continued external chip sourcing by Chinese module makers; yield or quality
problems disclosed; Chinese vendors competing on assembly/price rather than component tech.

**EVIDENCE STATUS: one real data point FOR the assumption, and a coverage gap.**
- **FOR:** Innolight's FY2025 annual report describes its key raw materials as externally
  sourced optical components and IC chips, with NO in-house chip or laser claim
  (`高速光模块产品所需原材料主要包括光器件、集成电路芯片以及结构件等`). The largest Chinese
  transceiver maker is a module assembler that BUYS its lasers — which is exactly the gap
  this assumption asserts, and is also a point in favour of COHR's moat.
- **AGAINST / unresolved:** Innolight's 1.6T runs a dual EML + silicon-photonics platform,
  and SiPh is offered as an EML alternative at 800G. Silicon photonics is a route AROUND the
  InP laser bottleneck, not through it — capability parity may not be required.
- **GAP:** the corpus holds nothing on Chinese laser yield or quality. Every "yield" hit is
  Samsung/Micron memory. **Accelink (002281-CN) is the name to watch** — unlike Innolight it
  has in-house chip capability, so its filings are where domestic laser capability would show
  up first. The CNINFO channel covers it.
- **RESOLVED-ISH 2026-08-21 — Accelink's own filings, and the answer is TWO-SIDED.** The
  CNINFO channel ingested Accelink's 2025 and 2026 annual reports (70 extracted claims).
  Accelink is the Chinese name with in-house chip capability, so this is the direct test.
  * **CHALLENGES the assumption:** Accelink claims *"full vertical integration from chip to
    component to module"* with laser chip types **FP, DFB, EML, VCSEL** plus PD/APD detectors
    and a SiP platform (`拥有多种类型激光器芯片（FP、DFB、EML、VCSEL 等）、探测器芯片（PD、APD）
    以及 SiP 芯片平台`). EML in-house is exactly the capability the assumption says is absent.
    The blanket form of "Chinese vendors cannot make high-quality lasers" does not survive.
  * **SUPPORTS the narrower form:** the same filings disclose that *"core raw materials and key
    components, including HIGH-END optical chip materials and specialty components, partially
    rely on external supply, with high market concentration"* (`核心原材料、关键零部件（如高端
    光芯片相关材料、特种元器件等）部分依赖外部供应`), and that the plan is to *"improve the
    optical chip process platform, increase iteration efficiency, and FILL GAPS in key product
    series to support high-end business"* (`补齐重点产品系列`). "Fill gaps in key product
    series" is Accelink saying, in its own words, that the high-end series is incomplete.
  * **Bearing on assembly-vs-capability:** Accelink flags `低价竞争` — LOW-PRICE COMPETITION —
    as an industry risk alongside peer capacity expansion, which is at least consistent with
    share being contested on price as well as on technology.
  **How to hold it:** the assumption should be narrowed from "cannot manufacture high-quality
  lasers" to "has not yet closed the HIGH-END gap and still depends on external supply for
  high-end optical chip materials." That version is both supported by the evidence and still
  testable — watch for Accelink dropping the external-dependence language or declaring the
  product-series gaps filled.
- **Mirror evidence already held:** AAOI states it manufactures ALL laser chips exclusively
  at Sugar Land, Texas via proprietary MBE + MOCVD, and treats that as a competitive claim.
  That is the benchmark a Chinese vendor would have to meet.

### `chinese_laser_capability` — OPERATOR POSITION, 2026-08-21
**Status: OPEN QUESTION, monitored — not resolved in either direction.** Operator: *"its an
open question that we need to continue to monitor, set against limited insider selling at LITE
and COHR, and a very robust demand environment and commentary from their most recent earnings
calls."*

So the Chinese threat is live and unresolved, but weighed against three counterweights. Two of
the three were VERIFIED with data on 2026-08-21 rather than accepted on assertion:

**1. Limited insider selling — VERIFIED (InsiderScore, 6 months to 2026-08-21).**
Gross figures look heavy: LITE 32 sells / 0 buys / -$46.7M, COHR 21 sells / 0 buys / -$7.0M.
But excluding 10b5-1 plan sales, DISCRETIONARY selling is small:
  LITE  2 sales,  8,454 sh,  $7.5M   (~84% of the gross was scheduled 10b5-1)
  COHR  1 sale,   3,911 sh,  $0.94M  (~87% scheduled; ONE discretionary sale in six months)
The operator's read is correct and the gross number is the misleading one. **The 10b5-1 split
is the analytically load-bearing distinction — always exclude plan sales before reading insider
behaviour as signal.**

**2. Robust demand — VERIFIED from the companies' own filings.**
COHR 2026-08-14: *"We continue to experience continued strong demand in our Datacenter and
Communications markets... increasing investments by hyperscale and other cloud providers in AI
datacenter infrastructures have significantly boosted demand for our datacenter transceivers"*;
elevated ZR/ZR+ demand; actively investing in manufacturing capacity.
LITE 2026-08-17: *"AI/ML has caused a dramatic surge in the growing demands on data networking
in cloud data centers."*

**3. Recent earnings-call commentary** — same source as (2); both reported within the fortnight.

**How to hold this:** Chinese capacity/quality evidence does NOT by itself move the theses. It
is weighed against insider behaviour and the demand environment. A downgrade wants Chinese
progress AND at least one counterweight breaking — discretionary insider selling picking up,
or demand commentary softening. Track the counterweights as first-class signals, not as
background.

**Counter-nuance found while verifying:** LITE's own risk factors list *"higher tariffs and
other trade restrictions between the U.S. and other countries, including China and Thailand"*
as a risk TO LITE. Its manufacturing footprint is in Asia, so a trade-restriction regime is
not purely a shelter — it is partly an exposure. This cuts against reading `policy_shelter` as
one-directionally favourable even if it does arrive.

### SHARE IS THE TEST — resolved 2026-08-21, and it is measurable now

Operator: *"if they take material share, yes it could be a thesis breaker. They all also talk
about tam, and we can triangulate what it is and then try and back into market share."*

**This resolves the silicon-photonics question.** Share taken via SiPh counts exactly the same
as share taken via InP. The route does not matter; the share does. `chinese_laser_capability`
is therefore a MECHANISM to watch, not the test itself — the test is share.

**On TAM triangulation — do it, but not as the primary measure.** The corpus does hold TAM
language (LITE 2026-08-11: CPO/NPO engagements *"significantly upping our optical TAM"*, scope
undefined; CRDO 2026-04-13: *"SiPho PIC market ... $6 billion by 2030"* per LightCounting).
But the statements are sparse for optical names, scoped inconsistently (whole-optical vs
component-level), and usually sourced to a third party. Normalising the definitions is the
hard part, not finding the numbers.

**A bottom-up denominator is available today and is self-consistent:** total disclosed revenue
across the tracked set. We now hold primary revenue for BOTH sides — US names via EDGAR,
Chinese via CNINFO and StreetAccount. No third-party TAM estimate required.

**First cut, 2026-08-21 (INDICATIVE — see caveats):**

| company | latest revenue | growth |
|---|---|---|
| COHR | $2.05B Q4 FY26 -> ~$8.2B annualised | +34% y/y |
| LITE | $1.01B Q4 FY26; $1.25B Q1 guide -> ~$4-5B | growing |
| Innolight | RMB 37.46B FY2025 ~ $5.2B | **+64%** |
| Eoptolink | RMB 24.84B FY2025 ~ $3.45B | **+187%** |

Two readings, and the second is the one that matters:
1. **Level:** Innolight alone is already larger than LITE's entire company. On datacom only
   the gap is wider still — Innolight and Eoptolink are near pure-play, while COHR's $2.05B
   includes lasers and industrial.
2. **Trajectory — the actual share signal:** +64% and +187% against COHR's +34%. Share is
   shifting on the growth differential regardless of the absolute base. If those rates
   persist for even a few quarters the shift is material on the operator's own test.

**CAVEATS, do not skip:** fiscal periods are NOT aligned (COHR/LITE FY26 ended mid-2026;
Chinese FY2025 is calendar 2025). FX assumed ~7.2 CNY/USD, not looked up. Segment mix is not
matched. These are indicative magnitudes, not a share calculation.

**To make it a real measure:** align on calendar quarters, use a looked-up FX rate, and
compare DATACOM segment revenue rather than company totals — COHR and LITE both disclose
segment splits, and the Chinese names are close enough to pure-play to use totals. Then track
the ratio quarterly. That is a small, bounded build and it turns this assumption from a
judgement into a tracked number.

### `policy_shelter` — WATCH ITEM, NOT AN ASSUMPTION (revised 2026-08-21)
**Operator, 2026-08-21:** *"partially right as its still debated and the policy has not come
out yet and is unlikely in the next 12 months."*

So this is explicitly **NOT load-bearing**. It is a low-probability, non-near-term option on
the upside, and the theses must stand without it. Recorded here so that (a) nobody later
mistakes it for a supporting pillar, and (b) if a rule does emerge it is already framed.

**Would become relevant if:** an optical-specific restriction is actually proposed (Section
889 / FCC Covered List / ICTS reaching transceivers); a hyperscaler states a non-China
sourcing requirement.
**Horizon:** unlikely before 2027-08. Re-examine then, or on a concrete rulemaking signal.
**Note if it ever does land:** it walls off *China-manufactured* product, which equally
advantages AAOI (US) and Fabrinet (Thailand). AAOI's filings show capex materially higher
through end-2027 expanding 400G/800G/1.6T capacity inside that shelter. It would redirect
competition, not remove it.

---

## LITE — Lumentum (T1, scored 2026-06-02)

### `eml_laser_supply_position`
**Statement:** LITE is designed into the AI transceiver supply chain as a key indium-phosphide
/ EML laser supplier.
**Derived from:** `ai_positioning: 4` — *"key indium-phosphide laser supplier into the
transceiver chain"*.
**Challenged by:** transceiver makers qualifying alternative EML sources; Chinese laser-chip
capability at 800G+; customers vertically integrating laser supply in-house (note: COHR's own
`vertical_integration_moat` is precisely this threat to LITE).
**Confirmed by:** design-win announcements; EML capacity sold out.
**Cross-thesis tension worth naming:** COHR's moat assumption and LITE's supplier assumption
are in partial conflict — COHR integrating laser supply in-house is bearish for LITE. Your
notes score both at 4 without acknowledging the tension.

### `component_tier_is_why_innovation_is_3`  *(CORRECTED 2026-08-21)*
**Statement:** LITE sits at the component tier rather than the systems tier, and that — not a
technology deficiency — is why innovation scores 3 rather than 4. The assumption is about the
REASON for the score, and that the reason still holds.
**Derived from:** `competitive_advantage.innovation_rate: 3` — *"strong laser/EML technology
but more component than systems"*.
**Challenged by:** margin compression at the component layer; module makers integrating
backwards; LITE moving up-stack into systems (which would invalidate the rationale rather
than the score).
**Correction note:** originally written as *"caps innovation scoring but is a stable
position"*. "Stable" appears nowhere in the operator's note — it converted a scoring rationale
into a claim about durability that was never made.

### `datacom_recovery`
**Statement:** The AI datacom cycle recovery is underway and is one of the named positives
behind an investor-interest score of 4.  *(CORRECTED 2026-08-21 — originally "continues,
OFFSETTING legacy weakness". The note lists datacom recovery as a positive and telecom
weakness as a separate temper; it never claims one offsets the other. They are independent
factors and should be tracked as such.)*
**Derived from:** `potential_investor_interest: 4` — *"AI datacom-cycle recovery and
transceiver/EML demand"*.
**Challenged by:** datacom order pauses; recovery stalling before telecom drag abates.

### `telecom_drag_no_worse`  *(CORRECTED 2026-08-21)*
**Statement:** Legacy telecom weakness is ALREADY subtracting from the score — it is one of
the two named reasons investor interest is capped at 4 rather than 5. The assumption is that
it does not get worse, not that it is held at bay.
**Derived from:** `potential_investor_interest: 4` — *"legacy-telecom-segment weakness and
customer concentration temper"*.
**Challenged by:** telecom declining faster than datacom grows; segment write-downs.
**Correction note:** originally written as `telecom_drag_contained` — *"contained and does not
offset datacom gains"*. That inverted the sense. "Tempers" means the drag is already being
applied to the score; "contained" implied it was being kept from applying. Opposite readings,
and they would have produced opposite signals from identical evidence.

### `cloud_light_is_an_upgrade_condition`  *(CORRECTED 2026-08-21)*
**Statement:** Cloud Light integration is one of the two conditions that would take LITE's
innovation score from 3 to 3+. It is a potential upside trigger, NOT an established fact.
**Derived from:** `competitive_advantage.innovation_rate: 3` — *"**3+** on the AI datacom ramp
and Cloud Light integration"*.
**Would upgrade the score if:** integration completes and contributes measurably to datacom.
**Challenged by:** integration problems; Cloud Light customer losses.
**Correction note:** originally *"integrates and contributes to the datacom ramp"*, stated as
fact. The "3+" notation marks a conditional upgrade path, not something already achieved.

### `chinese_laser_capability` — SHARED WITH COHR
See the COHR section. LITE's exposure is the direct one: it IS the merchant EML/InP supplier,
so Chinese laser parity attacks its position without needing to beat COHR on modules. The
silicon-photonics route matters even more here — SiPh at 800G/1.6T reduces EML content per
module regardless of who makes the laser.

---

## Proposed YAML shape (if you approve)

Added under each ticker in `config/watchlist.yaml`, alongside the existing scoring blocks:

```yaml
  - ticker: COHR
    # ... existing ai_positioning / competitive_advantage / ... unchanged ...
    assumptions:
      - id: supply_tightness
        statement: "Datacom transceiver supply remains tight, supporting price and share."
        derived_from: "competitive_advantage.distribution: 4"
        scored_date: 2026-06-02
        challenged_by: ["competitor capacity additions at 800G/1.6T", "transceiver ASP decline",
                        "hyperscaler dual-sourcing on price"]
        status: open        # open | challenged | confirmed | retired
```

`status` is the field that makes this live: `thesis_challenges.py` (Phase 4) proposes a move
to `challenged`, but a human decides. Nothing auto-downgrades a thesis.

## What I need from you

1. ~~The [GAP] on Chinese competition~~ **ANSWERED 2026-08-21.** Not policy — manufacturing.
   The crux is whether Chinese vendors reach high-yield, high-quality laser production. Now
   captured as `chinese_laser_capability`, shared across COHR and LITE.
2. ~~Whether these restatements are faithful.~~ **PARTLY RESOLVED 2026-08-21.** Three were
   over-reads and have been corrected in place, each with a correction note: the two
   concentration/telecom ones asserted judgements the notes never made, and
   `telecom_drag_contained` actually INVERTED the sense of "tempers". Correction principle
   applied throughout: claim only what the score itself implies, add no judgement.
   **2026-08-21, second pass:** the remaining set was reviewed and five more were corrected
   (`supply_tightness`, `deleveraging_on_track`, `vertical_integration_moat`,
   `datacom_recovery`, `cloud_light_integration`). EIGHT of eleven needed correction, all
   failing the same way — hedges, observations and watch-items hardened into forward-looking
   assertions. Only `datacom_ramp_continues` and `eml_laser_supply_position` survived the
   review unchanged.
3. **The COHR/LITE tension** — should COHR's vertical integration be an explicit bear
   input to LITE's thesis?
