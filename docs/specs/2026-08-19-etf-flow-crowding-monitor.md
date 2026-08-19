# ETF Flow & Crowding Monitor

## Step 0 — Session persistence — COMPLETE

Completed 2026-08-19:

- [x] Spec copied into the repo at `docs/specs/2026-08-19-etf-flow-crowding-monitor.md` (310 lines).
- [x] Memory file written:
      `/root/.claude/projects/-root-research-watchlist/memory/etf-flow-crowding-monitor.md`
      (`type: project`) — locked decisions, verified facts, open actions.
- [x] Pointer line appended to `MEMORY.md` (line 18), which is auto-loaded into context at the start
      of every session in this project. **This is the mechanism that makes a future session pick the
      work up without being re-briefed.**

- [x] Committed and pushed to `origin/main` (commit `88f5cf76`).

Note for future sessions: `auto_sync.py` is `#PAUSED_FOR_BUILD` in crontab, so nothing pushes on its
own — any later edits to this spec need a manual `git commit` + `git push`. The memory files live
under `/root/.claude/` and are outside the repo, so they are never carried by these commits.

**Nothing outstanding in Step 0. Implementation starts at Phase 1 below.**

## Context

The 7am daily digest currently carries competitive ETF holdings trades (`/root/ws` → "ETF UPDATE"),
insider activity, podcasts, and news flow. It has no measure of **fund flows** — where money is
actually going — and no way to tell whether a move in the book is idiosyncratic or the result of
being on the crowded side of a factor.

This adds an **ETF flow and crowding monitor** to that email, immediately after the ETF UPDATE
section. The goal the operator stated: *know when there is crowding*, backed by metrics rather than
a gauge needle, and — when a factor like momentum posts an extreme move — decompose what is driving
it and cross-check those names against the portfolio.

Deliberate framing: this is a **positioning/crowding monitor, not a directional signal**. The
academic evidence (Ben-David/Franzoni/Moussawi; Brown/Davies/Ringgenberg) is that ETF flows are
largely non-fundamental demand that mean-reverts over multi-week horizons — so "inflows = bullish"
is likely backwards at exactly the horizons we report. See the validation gate below.

## Verified before planning

| Question | Answer |
|---|---|
| Daily flows available? | **Yes** — `FactSet_FundsETF` `data_type='flows'`, daily USD, per ticker |
| History depth? | **MTUM back to 2019-01-01, 3,982 rows** — ample for stable baselines |
| Data lag? | T+1 (2026-08-18 flows available midday 2026-08-19) |
| FactSet from Python? | **No REST API / no credentials.** Must shell out to `claude -p --allowedTools mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_FundsETF` (pattern: `scripts/newsdigest/factset_news.py`) |
| Batch limits | 10 ids/request, `limit` max 500 → whole universe ≈ 5 calls/day |
| CNN Fear & Greed | **Works** — `production.dataviz.cnn.io/index/fearandgreed/graphdata` returns current + full history, but **418s from this droplet without a `Referer: https://www.cnn.com/markets/fear-and-greed` + `sec-fetch-site: same-site` header set**. Verified live: 57.9 / "greed" |

### Identity corrections found during exploration

- **LITE is not an ETF** — it is Lumentum Holdings, ~$78B equity. The intended ticker was **LYTE**.
- **LYTE** = Roundhill Photonics & Optics ETF. Inception **2026-08-06** → ~10 trading days, AUM not
  yet reported. Trackable, but **no baseline for months**.
- **DRAM** = Roundhill Memory ETF. Inception 2026-04-02 (~95 trading days), $24.5B AUM already.
  **Actively managed and synthetically backed** (swaps/forwards).
- DRAM and LYTE are therefore **excluded from z-scores and from any look-through**: synthetic
  creations do not mechanically buy the underlying shares.
- **Explicit, so nobody "fixes" it later:** DRAM's ~95 trading days clears the raw 63d *window* but
  gives no usable 3y *baseline* — a 63d z-score for DRAM would be computed against ~1 non-overlapping
  observation. Raw flow and flow/AUM only, flagged "insufficient history." LYTE (10 days) has
  neither.

## Universe

Two tiers with **different privileges**. Data cost is negligible; the reason to tier is statistical.
24 trigger-eligible ETFs × 2 horizons ≈ 48 tests/day — at 2σ that is ~2 false alerts *per day* by
chance alone. Tiering plus the thresholds below keeps the false-positive budget near 1/week.

### Trigger tier — may fire alerts (>$2B AUM, >2y history, physically backed, distinct exposure)

| Sleeve | Tickers |
|---|---|
| Core index + siblings | SPY, IVV, VOO, QQQ, QQQM, IWM, DIA, RSP |
| Sectors (SPDR) | XLK, XLC, XLF, XLE, XLV, XLY, XLP, XLI, XLU, XLB, XLRE |
| Semis + software | SMH, SOXX, IGV |
| **Factor** | **MTUM, QUAL, VLUE, USMV, IWF, IWD** |

Sibling pairs matter: SPY is a trading/hedging vehicle (±$8B daily swings on mechanics), so
**SPY vs IVV+VOO** and **QQQ vs QQQM** divergence is far more informative than either alone.
Pair mappings live in config.

### Context tier — stored and shown as backing detail, never alerts on its own

VGT, IYW, IGM, CIBR, SKYY, FDN, AIQ, BOTZ, MAGS, XLG, XSD, PSI, SPLV, PDP, **DRAM, LYTE**,
**BCTK, JTEK, BAI**.

Rationale: VGT/IYW/IGM are ~90% the same exposure as XLK — letting them alert independently
triple-counts one move.

- **Competitor sleeve (operator decision):** JTEK (JPMorgan U.S. Tech Leaders, $4.1B) + **BAI**
  (iShares A.I. Innovation and Tech Active, $13.0B — next largest excluding SEMI), plus **BCTK**
  itself ($179M). SEMI excluded ($37.6M).
- **Auto-excluded by rule:** SIZE ($429M) and SPHB ($976M) — too small. SOXL — leveraged, distorted
  AUM math.

## Horizons: 5d and 63d

Three overlapping windows read the same impulse three times and inflate apparent confirmation
(21d *contains* 5d; 1d is the first day of both). Two horizons, chosen to be independent:

- **5 trading days** (= the operator's "trailing 7 days"). Shortest window where creation/redemption
  settlement, dividend reinvestment and basket arb average out. Matches the weekly convention
  ETF.com / Lipper / street flow notes publish on.
- **63 trading days** (~1 quarter). Crowding is *accumulated positioning*, not an impulse. Decorrelates
  from 5d, aligns with 13F cadence, and matches where the mean-reversion evidence is strongest.
- **1d is computed but never a headline** — kept only as an event flag ("yesterday printed a 3σ day").

The 2×2 of the two horizons *is* the crowding monitor:

| | 63d low | 63d high |
|---|---|---|
| **5d high** | fresh rotation — early | **sustained crowding — most reversal-prone** |
| **5d low** | neglected | **crowded but stalling — distribution risk** |

## Metrics (Block A — facts, no interpretation)

Per ETF, per horizon:

1. **Net flow, USD** — raw, for scale.
2. **Flow / AUM in bps** — the cross-sectionally comparable unit. Denominator is **prior-period
   AUM**, never AUM that already contains the flow.
3. **Robust z-score** — median/MAD, not mean/σ: daily flows have fat tails and a Gaussian z
   over-fires. Baseline = trailing 3 years.
   **MAD-floor guard (required):** several ETFs (XLB, XLRE, PSI, XSD, PDP, and most context-tier
   names) have long runs of near-identical or zero daily flow. A trailing MAD of ~0 makes every
   reading ±∞σ and destroys the alert budget. Floor the MAD at a minimum bps-of-AUM value; when the
   floor binds, **fall back to empirical percentile only and suppress the σ label**. Unit-test this —
   it is the most likely day-one failure.
4. **Empirical percentile vs trailing history** — report *"99.4th pctile, largest since Nov-2025"*
   rather than *"2.8σ"*. More honest and more readable.
5. **Flow-vs-price divergence** — sign of flow vs sign of same-window return. Inflow on a down tape
   = accumulation; outflow on an up tape = distribution.
6. **Pair spread** — SPY−(IVV+VOO), QQQ−QQQM in bps: separates trading-vehicle mechanics from real
   allocation.
7. **Breadth** — % of trigger tier with positive 63d flow. A risk-appetite gauge.
8. **Factor rotation spread** — MTUM vs VLUE vs USMV vs QUAL normalized flows. This is the "what is
   driving the stocks" read.

### Trigger thresholds — PROVISIONAL until calibrated

These are starting values, **not fixed**. Calibration (verification step 5) runs on backfilled
history and is allowed to move them. Do not wire the email until calibration has run.

- **3σ (robust) fires standalone** → target ≈1 alert/week across the trigger tier.
- **2σ fires only with corroboration** — the other horizon also elevated, or a flow-vs-price
  divergence in the same direction.
- Alerts capped per day, ranked by severity. If the cap truncates, **say so in the output**
  (repo convention: no silent caps).

## Crowding analysis (Block B — separate, after Block A)

Per operator: metrics first, interpretation second, visibly separated.

Triggered only by a Block-A alert — a **conditional** look-through, not a daily per-ticker dump:

1. Name the triggering ETF and the metric that fired.
2. Pull its constituents + weights.
3. Compute **implied demand per underlying** = flow × weight, expressed in **days of ADV**
   (via `FactSet_GlobalPrices` volume). "ETF-driven demand = 3.2 days of ADV" is a crowding
   statement; a dollar figure is not.
4. **Intersect with the portfolio** — BCTK holdings from `/root/ws`'s `data/etf_holdings.db`
   (already scraped daily, with share counts) and `tier_1_bctk` in `config/watchlist.yaml`.
5. Output: which held names sit in the crowded vehicle, and how much of their recent volume is
   ETF-mechanical rather than fundamental.

MTUM's **semi-annual reconstitution** deserves a standing note — a rebalance mechanically reshuffles
which momentum names are bought, and will look like a flow event if unlabelled.

## Fear & Greed

One-line regime header **above** Block A: score, rating, and 1-week / 1-month deltas, so flows are
read in sentiment context. Market-wide only — there is no per-stock version; state that once.
Fetch is a plain HTTPS GET with the header set above. On failure: print last-known value with its
age, never fail the digest.

## Architecture

Follows the `news_digest.py` + `scripts/newsdigest/` precedent exactly.

```
config/etf_universe.yaml       # universe, tiers, pair mappings, per-ETF flags
                               #   (synthetic:, min_history_ok:, trigger_eligible:)
scripts/etf_flows.py           # entry point; --fetch / --report / --backfill / --dry-run
scripts/etfflows/
    __init__.py                # constants only (repo convention): horizons, thresholds, chunk size
    factset_flows.py           # claude -p transport, CHUNK_SIZE=10, verbatim-JSON prompt
    fear_greed.py              # CNN fetch + cache
    metrics.py                 # flow/AUM, robust z, percentile, divergence, breadth, pair spread
    triggers.py                # threshold logic, corroboration, per-day cap
    lookthrough.py             # Phase 2: constituents × weights × ADV × portfolio intersect
    render.py                  # Block A / Block B / full table
state/etf_flows.jsonl          # append-only, idempotent on (ticker, date)
logs/report_etfflows_{date}.txt
notes/flows/{date}-flows.md    # full detail, ## heading (chunker requirement)
```

**Reuse, do not reinvent:** copy `_claude_env()` (strips `ANTHROPIC_API_KEY` so `claude -p` stays on
subscription auth) — the repo convention is to copy it, it appears verbatim in 5 files. Follow
`factset_news.py` for chunking, saturation-split and the **unparseable-output-is-a-failure** rule.

### Data constraints to honor

- **Use `shareClassAUMReported`, not `fundLevelAUM`.** VOO/VGT/VUG are multi-share-class: VOO shows
  $1.68T fund-level vs $994B share-class. Using fund-level silently understates flow/AUM.
- **AUM is month-end only** (`frequency` accepts MTD/M/CQTD/CQ/CYTD/CY — no daily). Roll the
  month-end figure forward with daily flows + NAV returns for the denominator; document the choice.
- **`0.0` ≠ missing.** 2026-07-03 (half-day) returns `0.0`. Store a null/holiday marker distinctly or
  a real zero pollutes the 5d/63d windows.
- Chunk by **both** id-group (10) and date-range (500-row cap) on backfill.

### Backfill cost — one-shot, ~50-75 `claude -p` calls (NOT 5)

The "~5 calls/day" figure is **steady state only**. The `limit` cap is 500 *rows*, and
rows = ids × days, so a 10-ticker group covers only 50 trading days per request. 47 tickers × 750
trading days (3y) ≈ 35,250 rows ÷ 500 = **~71 calls minimum**, each carrying the ~29.7K fixed
cache-creation tokens named in `docs/cost-model.md`.

Mitigation: 3y baseline for the **trigger tier only** (28 tickers ≈ 42 calls); 1y for the context
tier (19 tickers ≈ 10 calls) → **~52 calls**. Context tier never fires alerts, so it does not need a
3y baseline.

Run this as an explicit **one-shot with per-chunk progress logging**, well outside the
06:45–08:15 window. State the call count at invocation so nobody runs it casually.

## Email integration

`/root/daily/combine_and_send.py` — insert one tuple after ETF UPDATE:

```python
REPORTS = [
    ('ETF UPDATE',       '/root/ws/data/reports/report_{date}.txt'),
    ('ETF FLOWS & CROWDING', '/root/research-watchlist/logs/report_etfflows_{date}.txt'),  # NEW
    ('INSIDER ACTIVITY', '/root/is/reports/report_{date}.txt'),
    ('PODCAST DIGEST',   '/root/podcasts/data/reports/report_{date}.txt'),
    ('NEWS FLOW',        '/root/research-watchlist/logs/report_news_{date}.txt'),
]
```

Note `/root/daily` is a **separate git repo** — that one-line change is committed there, not here.
Missing file → section omitted, email still sends (existing behavior).

**Layout (operator decisions):** Fear & Greed line → Block A metrics (~15-20 lines) → Block B
analysis → **full table appended at the END of the email**, after NEWS FLOW.

## Scheduling — quota-constrained

`run_daily.sh` documents that on 2026-08-13 two `claude -p`-heavy jobs in one rolling 5h window
exhausted the subscription and the digest shipped 40 of 256 stories. **Do not add `claude -p` work
in the 06:45–08:15 window.**

Design: **fetch and render are decoupled.**
- `--fetch` runs **05:30 ET weekdays** (~5 `claude -p` calls), appends to `state/etf_flows.jsonl`.
- `--report` runs inside `run_daily.sh` at 07:00 and does **zero LLM calls** — pure computation over
  stored state.

Both wrapped in `/root/bin/alert_on_failure.sh`. Verify empirically what max flow date is available
at 05:30; the report must **print the "flows as of" date** rather than assume T-1.

## Validation gate (before this is called a signal)

Run on backfilled history, report the result honestly:

1. **Does 63d flow z-score add anything beyond 63d price momentum?** Regress forward returns on
   both. If flow adds no incremental information, the honest output is a *positioning monitor* —
   say so in the header and drop any predictive language.
2. **Confirm the sign.** Test whether elevated flow predicts continuation or reversal at 21d/63d.
   If reversal, the crowding framing is validated and Block B language must reflect it.
3. **Sign sanity-check against `/root/ws`** for the overlapping funds (BCTK, QQQ, JTEK).
   **Scope correction — verified against the schema:** `data/etf_holdings.db` has a single
   `holdings` table `(date, etf_ticker, symbol, name, weight, shares, market_value)` — per-position
   only, **no fund-level shares-outstanding series**, and `market_value` is `0.0` in practice. So
   shares × NAV is *not* computable and `fund_baseline_pct` is a proxy inferred from median position
   drift. Treat this as a **check on flow sign**, not an independent flow measurement.
   Useful byproduct: the `weight` column is exactly what Phase 2 look-through needs — for the 18
   funds `/root/ws` scrapes. SMH/MTUM/XLK etc. still require FactSet holdings.

## Phasing

- **Phase 1** — universe config, fetch, 3y backfill, metrics, triggers, Blocks A/B (ETF-level),
  Fear & Greed, email integration, validation gate.
- **Phase 2** — constituent look-through: implied demand in days of ADV, portfolio intersection.
  Deferred because it needs per-ETF holdings-with-weights retrieval verified first. DRAM and LYTE
  are permanently excluded from it.

## Verification

**Order matters** — calibration depends on the backfill, and the email must not be wired until
thresholds are calibrated. Sequence: backfill → validate data → calibrate thresholds → wire email.

1. `--backfill --start 2023-01-01` (the ~52-call one-shot above) → row counts per ticker; assert no
   `(ticker, date)` duplicates; assert holidays are marked, not zeroed.
2. Spot-check three ETFs' 5d/63d sums against a manual FactSet pull.
3. Assert `shareClassAUMReported` is the denominator (unit test on VOO: must not use $1.68T).
4. Unit-test the MAD floor: feed a constant-flow series and assert it degrades to percentile-only
   with no σ label, rather than emitting ±∞σ.
5. **Trigger calibration (gates the email wiring):** run the backfilled history through
   `triggers.py`, count alerts/week. Target ≈1. Materially more means the provisional 3σ/2σ
   thresholds move — that is the expected outcome, not a failure.
6. `python3 scripts/etf_flows.py --dry-run --report` → renders from stored state, no email, no LLM.
7. CNN fetch: assert 200 with headers, and that a forced failure degrades to last-known-value with
   an age note rather than failing the run.
8. End-to-end: `run_daily.sh` on a test date → confirm section appears after ETF UPDATE, full table
   at end, and that a deliberately missing flows file still sends the email.
