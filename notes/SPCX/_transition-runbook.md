---
doc_type: runbook
subject: spacex.pvt -> SPCX (.pvt -> ticker promotion at IPO)
prepared: 2026-06-09
execute_on: 2026-06-12 (Fri AM ET), ONLY after SPCX confirmed trading
status: STAGED — do not execute until the decision gates below pass
---

# Runbook: `spacex.pvt` → `SPCX` transition

Pre-staged for the SpaceX IPO. **Nothing in this transition runs until SPCX is confirmed trading on Nasdaq.** A half-renamed identifier in production (if the listing slips) is the failure mode to avoid.

## ⚠ State note (read before executing)

The original plan assumed SPCX was a **tier_3_watchlist** stub to be promoted to T2. **It is not** — as of 2026-06-09 the SPCX pending stub already lives in **`tier_2_active_candidates`** (`config/watchlist.yaml`, ~line 1089). So the transition **enriches the existing T2 entry in place** and **removes the `private_drivers` entry** — it does *not* add a new T2 entry (that would duplicate). The migration script (`scripts/migrate_spacex_to_spcx.py`) detects the actual location and acts accordingly. Promotion to **T1** is *not* part of this transition — that happens automatically when SPCX appears in BCTK holdings (the scraper promotes T2/T3→T1).

## Decision gates (ALL must be true before step 2)

1. **Pricing occurred** — SpaceX priced the eve of 2026-06-11 (pricing press release out).
2. **First trade actually opened** — SPCX is live and trading on Nasdaq (not halted, not postponed).

If either is false (deal slips / postponed), **STOP** — leave `spacex.pvt` in place and re-stage for the new date.

## Execution checklist (operator)

- [ ] **a. Confirm SPCX trading.** Web search ("SPCX stock price"), or FactSet ticker check (`SPCX-US` now resolves to a public security / GlobalPrices returns a quote). A live last-price = go.
- [ ] **b. Dry-run the migration:**
      ```
      cd /root/research-watchlist
      python3 scripts/migrate_spacex_to_spcx.py            # --dry-run is the default
      ```
      Review the unified diff for: `private_drivers` removal, T2 SPCX enrichment, `ticker_identity.yaml` add, `supply-chain-manual.yaml` retarget, `notes/` rename.
- [ ] **c. Operator approves the diff.** Spot-check no unrelated lines / comments are mangled by the YAML round-trip.
- [ ] **d. Apply:**
      ```
      python3 scripts/migrate_spacex_to_spcx.py --apply
      ```
- [ ] **e. Validate:** `python3 scripts/check.py` (must pass). Optionally re-run the news-digest identity load to confirm SPCX resolves.
- [ ] **f. Commit + push** (deliberate exception to the no-manual-push rule, on the droplet):
      ```
      git add -A && git commit -m "SpaceX IPO: promote spacex.pvt -> SPCX (ticker live 2026-06-12)"
      git push origin main      # or let auto_sync.py pick it up within 15 min
      ```
- [ ] **g. File a transition memory note** (`spacex-pvt-to-spcx-transition`, type project): date executed, final price/valuation, what changed, that the Cursor/EchoStar contingencies still ride on the post-IPO SPCX entry.

## What the migration touches (full inventory)

1. `config/watchlist.yaml`
   - **Remove** `private_drivers` entry `pvt_id: spacex.pvt` (and its `affects:/notes:` block).
   - **Enrich** the existing `tier_2_active_candidates` SPCX entry: notes → "trading as of 2026-06-12", inherit key context (Starlink/xAI/compute), drop the "retire the private_drivers entry" reminder. Themes carried + expanded (`space_economy` (+ `frontier_model_competition`, `ai_infrastructure_capex` from the xAI absorption)).
2. `config/ticker_identity.yaml`
   - **Add** `SPCX:` → `name: "SpaceX"`, `factset_id: "SPCX-US"`, `google: '"SpaceX" OR SPCX stock'`. (Enables digest enrichment once the security exists.)
3. `/root/research/config/supply-chain-manual.yaml` (sibling repo)
   - **Retarget** `target: spacex.pvt` → `target: SPCX` (line ~94) and touch the inline provenance comment (line ~101).
4. `notes/spacex.pvt/` → `notes/SPCX/`
   - `git mv` the directory (carries `_profile.md`). This runbook can be deleted post-transition.

## Rollback

The change is one commit. To undo before push: `git restore --staged . && git checkout -- .` and `mv notes/SPCX notes/spacex.pvt`. After push (droplet is canonical): `git revert <sha>` and re-run `scripts/check.py`.
