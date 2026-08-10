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
**Statement:** In-house indium-phosphide laser → transceiver vertical integration is a
durable cost/supply advantage competitors cannot easily replicate.
**Derived from:** `competitive_advantage.innovation_rate: 4` — *"vertically integrated optics
(indium-phosphide lasers -> transceivers), datacom transceiver ramp"*.
**Challenged by:** a competitor demonstrating in-house InP/EML chip capability at comparable
volume; merchant laser supply becoming abundant enough that integration stops mattering;
Accelink or similar shipping integrated chip-to-module at 800G+.
**Confirmed by:** competitors publicly constrained by third-party laser supply; COHR gross
margin holding while merchant module prices fall.

### `supply_tightness`
**Statement:** Datacom transceiver supply remains tight, supporting price and share.
**Derived from:** `competitive_advantage.distribution: 4` — *"broad datacom customer base
across hyperscalers amid transceiver supply tightness"*.
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

### `customer_concentration_tolerable`
**Statement:** Datacom customer concentration is a known risk but not thesis-breaking.
**Derived from:** `competitive_advantage.distribution: 4` — *"some customer concentration in
datacom"*.
**Challenged by:** a top customer qualifying a second source; concentration rising; a named
customer moving volume to a Chinese supplier.

### `deleveraging_on_track`
**Statement:** Post-II-VI/Finisar leverage continues to come down.
**Derived from:** `potential_investor_interest: 4` — *"turnaround/deleveraging story ...
Post-II-VI/Finisar balance-sheet leverage is a watch-item"*.
**Challenged by:** leverage flat or rising; refinancing at worse terms; FCF miss.

### **[GAP] — no assumption in your notes covers Chinese competition**
Nothing in COHR's 2026-06-02 scoring mentions Chinese competitors at all, yet the corpus
holds 110 documents naming them. Either that is a deliberate judgement (they do not compete
in COHR's segments / quality tier) — which should be written down as a testable assumption so
evidence can attack it — or it is an omission. **This is the single most consequential thing
for you to decide**, because it determines whether incoming Chinese-competitor evidence
confirms an existing view or contradicts an unstated one.

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

### `component_not_systems_position`
**Statement:** Being a component supplier rather than a systems vendor caps innovation
scoring but is a stable position.
**Derived from:** `competitive_advantage.innovation_rate: 3` — *"strong laser/EML technology
but more component than systems"*.
**Challenged by:** margin compression at the component layer; module makers integrating
backwards.

### `datacom_recovery`
**Statement:** The AI datacom cycle recovery continues, offsetting legacy weakness.
**Derived from:** `potential_investor_interest: 4` — *"AI datacom-cycle recovery and
transceiver/EML demand"*.
**Challenged by:** datacom order pauses; recovery stalling before telecom drag abates.

### `telecom_drag_contained`
**Statement:** Legacy telecom weakness is contained and does not offset datacom gains.
**Derived from:** `potential_investor_interest: 4` — *"legacy-telecom-segment weakness ...
temper"*.
**Challenged by:** telecom declining faster than datacom grows; segment write-downs.

### `cloud_light_integration`
**Statement:** The Cloud Light acquisition integrates and contributes to the datacom ramp.
**Derived from:** `competitive_advantage.innovation_rate` — *"3+ on the AI datacom ramp and
Cloud Light integration"*.
**Challenged by:** integration problems; Cloud Light customer losses.

### **[GAP] — same omission as COHR**
No assumption covers Chinese competition.

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

1. **The [GAP] on Chinese competition** — deliberate judgement or omission? Everything
   downstream depends on this.
2. **Whether these restatements are faithful.** I derived them from your notes; if any
   misrepresents what you actually believe, it will generate wrong signals forever.
3. **The COHR/LITE tension** — should COHR's vertical integration be an explicit bear
   input to LITE's thesis?
