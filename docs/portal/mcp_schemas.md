# FactSet MCP tool schemas — field names verified live

Reference for `scripts/valuation/` (RIS5 A3) and any future consumer of the FactSet
AI-Ready Data MCP tools, so a schema doesn't have to be rediscovered on every call site.
Sections marked "confirmed live" were verified against a real tool_result, not just the
tool's own parameter-schema description; sections marked "from tool schema only" are taken
from the tool definition's own description text (fetched via ToolSearch 2026-09-17) and
have NOT yet been checked against a real response.

## FactSet_GlobalPrices

### `data_type='prices'` (from tool schema + confirmed live 2026-09-17)

Request: `ids` (<=500 for single-day, <=50 for multi-day/other data_types), `startDate`,
optional `endDate`, `fields` (subset of `price`/`priceOpen`/`priceHigh`/`priceLow`/`volume`/
`turnover`/`tradeCount`/`vwap`), `frequency` (default `D`).

Response row (confirmed live, `fields: ['price','volume']`):
```
{"requestId": "<id as sent>", "fsymId": "...", "date": "YYYY-MM-DD",
 "price": <float>, "volume": <float>, "currency": "<ISO code>"}
```
`requestId` echoes the id sent — this is the join key back to ticker, not call order (same
convention as etfflows/factset_flows.py's fund endpoints).

### `data_type='market_value'` (current market cap, millions)

Request: `ids` only (tool schema says <=50/call — this is the "all other data types" cap,
NOT the 500 used by single-day prices — **but the live run hit a real 408 Request Timeout
on a 50-id batch** on 2026-09-17, so RIS5 A3 fix 2 tightens the code's own batch size to
25, below the documented 50-id ceiling, as a timeout mitigation, not a schema correction).
A 408/5xx on any batch is retried once after a 20s wait, then marked failed (see
`snapshot.py`'s `_retry_once`/`_is_retryable_error`). `currency`/`calendar`/`fields`/dates
are all "NOT USED" per the tool's own schema (fixed response shape).

**Field name for the cap value: CONFIRMED live 2026-09-17** — `currentMarketValue`. None
of the pre-live guesses (`marketValue`/`mktVal`/`market_value`/`mcap`/`value`) matched.
Raw row observed (first live 25-id batch, ticker 000660.KS / SK Hynix):
```
{"fsymId": "SZG8SG-R", "requestId": "000660-KR", "currentMarketValue": 1240826747.5,
 "currency": "KRW", "date": "2026-09-17"}
```
Notes:
- **RESOLVED (RIS5 A3 fix 3, coordinator review, HIGH):** `currency` IS now carried
  through into both the dated row and `latest.json` as `mcap_currency` (alongside
  `price_currency` from the `prices` pull) — `normalize_market_value_rows()` was fixed to
  stop dropping it. The live run showed real disagreement between the two: `market_value`
  returns the security's LOCAL-exchange currency while `prices` can return an ADR's USD
  quote for the SAME ticker — 15 names (ASML/ASMIY/ASX/BABA/BESIY/BIDU/GDS/NOK/NTES/
  RELX/SONY/SPOT/TCEHY/TSM/UMC) hit this live. `check_mcap_quality` now fails these as
  `fail:currency_mismatch`; `build_latest` seats the ticker's `price` regardless and nulls
  only `mcap`, recording the reason in `skipped_mcap`.
- **RESOLVED (RIS5 A3 fix 3 round 2):** `currentMarketValue` is confirmed to be in
  MILLIONS of the row's currency (matching the tool schema's own "(millions)" label),
  not raw units. Confirmed by reconciling 6 live USD names' implied share counts
  (mcap/price) against their real public share counts — NVDA/AAPL/MSFT/WMT/ZS/COHR all
  land in the right ballpark ONLY when the raw value is multiplied by 1e6 before the
  comparison (see `scripts/valuation/snapshot.py`'s `MCAP_UNIT_MULTIPLIER` for the full
  worked table). **This multiplier is applied ONLY inside the plausibility check
  (`check_mcap_quality`'s implied-share-count math) — the `mcap` value actually
  PERSISTED in the dated file and `latest.json` stays in millions, unscaled.** Rescaling
  the persisted value would break `scripts/valuation/expectations.py`'s
  `ev = entry["mcap"] + net_debt`, since `net_debt` (`FactSet_Fundamentals`' FF_NET_DEBT)
  and the consensus SALES/EBITDA/FCF figures this same module writes are ALL natively in
  millions with no rescaling applied anywhere in the codebase — multiplying only mcap
  would silently break every downstream EV/multiple computation by 6 orders of magnitude.
  Before this fix, EVERY non-ADR ticker in the universe (161 of them) failed
  `fail:mcap_scale` because the implied-share check compared an un-multiplied
  "millions of shares" figure against a threshold calibrated for raw share counts.
- `scripts/valuation/snapshot.py`'s `_MCAP_KEYS` now tries `currentMarketValue` first,
  with the original guesses kept as a defensive (currently dead) fallback list — logs a
  WARNING naming the fallback key if one is ever actually used.
- **FX conversion follow-up (explicitly NOT attempted this session, per coordinator
  instruction — no live calls spent testing it):** `FactSet_GlobalPrices`' `currency`
  PARAMETER (checked from this session's own tool-schema fetch, not a live call) is
  documented as usable for `data_type='prices'`/`returns`/`corporate_actions`/
  `annualized_dividends`/`returns_range` but explicitly **"NOT USED" for
  `market_value`/`shares_outstanding`** — there is no way to request `market_value`
  pre-converted into the ADR's currency at fetch time. Two real paths for the next
  session: (1) a downstream FX-rate lookup applied to the 15 currency-mismatched names
  specifically, or (2) pull `data_type='shares_outstanding'` (also currency-agnostic —
  a share count, not a monetary value) and compute `mcap = shares_outstanding * price`
  directly in the ADR's own currency, sidestepping the mismatch entirely instead of
  converting it. Neither is built here.

## FactSet_EstimatesConsensus

### `estimate_type='consensus_rolling'` (from tool schema; confirmed shape live 2026-09-17)

Request: `ids` (<=3000), `metrics` (**max 1 per request**), `periodicity` (`ANN`/`QTR`/...),
`relativeFiscalStart`/`relativeFiscalEnd` (1=next period/FY1, 2=FY2, ...; 4/5 for the
weekly FY4-FY5 pull, amendment v1.2 — no separate discovery needed, `relativeFiscalStart`/
`End` just take a bigger number). No `startDate`/`endDate` needed for "current" consensus
(the PIT rule only applies when BOTH dates are given — omit both for the latest snapshot,
which is what a daily valuation snapshot wants).

Response row **CONFIRMED live 2026-09-17** (RIS5 A3 live run; this replaces an earlier,
WRONG pre-live guess of `count`/`date` that made every single row from the first live
pull fail quality even though `mean`/`median`/`up`/`down` were all real, valid data):
```
{"requestId": "<id>", "fsymId": "...", "metric": "SALES", "periodicity": "ANN",
 "fiscalPeriod": 1, "fiscalYear": 2026, "fiscalEndDate": "YYYY-MM-DD",
 "relativePeriod": 1|2|3|4|5, "estimateDate": "YYYY-MM-DD",
 "currency": "LOCAL", "estimateCurrency": "USD",
 "mean": <float|null>, "median": <float|null>, "standardDeviation": <float>,
 "high": <float>, "low": <float>, "estimateCount": <int>, "up": <int>, "down": <int>}
```
There is **no top-level `count` or `date` key at all** — the analyst count is
`estimateCount` and the snapshot date is `estimateDate`. `scripts/valuation/snapshot.py`'s
`normalize_consensus_rows()` now reads the correct keys (fixed post-live; see its
docstring for the incident).

**up/down: evidence toward TRAILING, not cumulative** (for A5's breadth flag) — live
NVDA/AVGO SALES rows: NVDA FY1 up=52 down=2 estimateCount=63; FY2 up=54 down=1 count=62;
FY3 up=29 down=0 count=39. AVGO FY2 up=14 down=14 count=44; FY3 up=21 down=0 count=36. In
every observed row `up + down <= estimateCount` by a comfortable margin (never equal to
or exceeding it), which is the shape you'd expect from "analysts who revised in some
recent window" (a trailing stat) rather than "every up/down revision ever recorded for
this fiscal period" (a cumulative counter, which would tend to grow toward or past
`estimateCount` over a period's lifetime as the same analysts revise multiple times).
Not proven by a single day's snapshot — a definitive test would compare the SAME
(ticker, metric, relativePeriod)'s up/down across two dates and check whether the trailing
one resets/varies non-monotonically, which A3 did not run — but this is the strongest
signal available from one live pull, and A5 should treat it as trailing-window unless a
multi-day comparison says otherwise.

### Metric codes (amendment v1.2: daily pull is now SALES/EPS/EBITDA/FCF)

- `SALES`, `EPS` — confirmed live (this task's earlier run, 2026-09-17 afternoon).
- `EBITDA` — confirmed live 2026-09-17: real, non-null `mean`/`estimateCount` values
  returned for the full 178-ticker universe (531 rows, 515 quality-ok).
- `FCF` — confirmed live 2026-09-17: works as the literal unprefixed code `FCF` against
  the real endpoint (531 rows, 503 quality-ok), even though it was NOT surfaced by a
  `FactSet_Metrics` discovery call with `data_products=["fundamentals","estimates"]` (that
  search's "free cash flow"/"free cash flow margin" queries returned only `dataProduct:
  "fundamentals"` FF_ candidates in their top 10 — no `estimates`-tagged result ranked).
  Discovery and the live endpoint disagree here; the endpoint is the source of truth and
  `FCF` is what `snapshot.py`'s `CONSENSUS_METRICS` uses. `snapshot.py`'s
  `f"{label}_{metric.lower()}"` key convention produces `fy1_fcf`/`fy2_fcf`/`fy3_fcf` as
  expected (matches `scripts/valuation/expectations.py`'s pre-existing hardcoded
  `entry.get("fy1_fcf")` reads).

## FactSet_Metrics (discovery tool for FactSet_Fundamentals / FactSet_Estimates)

`text: [queries]` (no hyphens — spaces only), `target='metric'` (default),
`data_products=['fundamentals']` to restrict to FF_* codes. Response: metric records keyed
by `properties.metric` (the exact code to paste into Fundamentals — never abbreviated or
inferred). See `scripts/valuation/fundamentals.py`'s `discover_metrics_prompt`.

## FactSet_Fundamentals

Mandatory workflow: FactSet_Metrics MUST be called first; codes must come verbatim from
its response. `audit` is a REQUIRED parameter (pass `null` explicitly for no audit data —
`scripts/valuation/fundamentals.py` always does this; there is no ingest use for the audit
trail). Periodicity fallback ladder if unspecified: QTR -> SEMI -> ANN (only applies when
periodicity is NOT given -- this module always specifies one explicitly). Max 250 ids, max
1600 metrics per call (confirmed from the tool's own schema) — the full 178-ticker
universe at 7 metrics fits in ONE call per periodicity group, well under both caps.

**RESOLVED (RIS5 A3 fix 4, coordinator review):** the original QTR-only pull produced
FCF margins understated ~4x (NVDA 3.8% vs a real ~40%) because `FF_FREE_CF` (one
quarter's cash flow) was being divided against an ANNUAL sales figure sourced from a
DIFFERENT pull (`snapshot.py`'s consensus SALES) — a period mismatch, not a real margin.
Fixed two ways:
1. **`FF_SALES` is now pulled in the SAME `FactSet_Fundamentals` call as `FF_FREE_CF`**
   (`scripts/valuation/fundamentals.py`'s `FLOW_METRICS`), so `fcf_margin =
   FF_FREE_CF / FF_SALES` always comes from one period, one call —
   `compute_fcf_margin_rows()` additionally verifies the two rows share the same
   `fiscal_end` before dividing, failing `fail:period_mismatch` rather than silently
   computing a wrong ratio if they ever don't.
2. **Periodicity is `LTM` for flow metrics, still `QTR` for balance-sheet metrics.**
   `LTM` (trailing twelve months) is a valid enum value on this tool's own schema
   (`ANN, ANN_R, QTR, QTR_R, SEMI, SEMI_R, LTM, LTM_R, LTMSG, LTM_SEMI, LTM_SEMI_R, YTD`)
   and gives `FF_FREE_CF`/`FF_SALES` a genuinely annualized (12-month) figure without
   waiting for the next full fiscal year-end. **But a full-universe LTM attempt against
   `FF_NET_DEBT`/`FF_DEBT`/`FF_CASH_GENERIC` returned 0/178 ok for all three** —
   balance-sheet items are point-in-time snapshots with no "trailing twelve months"
   concept, discovered live while building this fix, not guessed. So a full pull is now
   **TWO calls**, one per periodicity group (`BALANCE_SHEET_METRICS` at `QTR`,
   `FLOW_METRICS` at `LTM`) — a tool constraint (periodicity is one value per call,
   applying to every requested metric), not a stylistic choice.

**CONFIRMED live 2026-09-17** (RIS5 A3, both the original QTR-only round and fix 4's
LTM/QTR split; NVDA-US/AVGO-US/COHR-US 3-id probe, then two full 178-ticker pulls):

| label | FF_ code | periodicity | live values (NVDA / AVGO / COHR) |
|---|---|---|---|
| `net_debt` | `FF_NET_DEBT` | QTR | -60509 / 35444 / 1532.82 |
| `total_debt` | `FF_DEBT` | QTR | 38860 / 59419 / 3554.994 |
| `cash` | `FF_CASH_GENERIC` | QTR | 99369 / 23975 / 2022.174 |
| `gross_margin` | `FF_GROSS_MGN` | LTM | 74.98 / 67.46 / 38.38 (already a percentage) |
| `operating_margin` | `FF_OPER_MGN` | LTM | 66.24 / 54.31 / 13.79 (already a percentage) |
| `fcf` | `FF_FREE_CF` | LTM | 120230 / 27325 / -1034.833 |
| `sales` | `FF_SALES` | LTM | 302969 / 89104 / 7118.148 |
| `fcf_margin` (derived) | `FF_FREE_CF / FF_SALES * 100` | LTM | **39.68% / 30.67% / -14.54%** |

Internal consistency check on the QTR probe: NVDA `total_debt - cash` = 38860 - 99369 =
-60509 = NVDA's own `net_debt` row exactly, confirming both the field mapping and the
sign convention (net_debt negative = net cash position). `FactSet_Metrics` reports
`"factor": "1000000"` on the debt/cash metrics (values are already in the stated currency
units — i.e. $millions for a company reporting in USD — not literal dollars); margins
carry no `factor` (already percentages, no rescaling needed). COHR's LTM FCF margin is
genuinely negative (-14.54%, on FCF=-$1,035M / sales=$7,118M) — plausible given COHR's
recent heavy restructuring/capex following the II-VI/Coherent merger; not a bug, but
flagged since it diverges from a coordinator sanity-check ballpark of positive 5-15%.

**No dedicated FCF-margin FF_ code exists.** Neither "free cash flow margin" nor "free
cash flow" surfaced an FF_ metric distinct from `FF_FREE_CF` (Free Cash Flow, a dollar
figure) in the top 10 `FactSet_Metrics` results — no `FF_FCF_MARGIN`-shaped candidate.
`fcf_margin` is DERIVED (fix 4: inside this module now, `compute_fcf_margin_rows()`, not
downstream) as `FF_FREE_CF / FF_SALES` — both pulled together, never sourced separately.

Raw row shape (one row per (id, metric) at the requested periodicity):
```
{"requestId": "<id>", "fsymId": "...", "metric": "FF_NET_DEBT", "periodicity": "QTR",
 "fiscalPeriod": 2, "fiscalYear": 2026, "fiscalPeriodLength": 91,
 "fiscalEndDate": "YYYY-MM-DD", "reportDate": "YYYY-MM-DD", "epsReportDate": "YYYY-MM-DD",
 "updateType": "Final", "currency": "USD", "value": <float>}
```
**Code bug found + fixed (fix 4):** `normalize_fundamentals_rows()` read `date`/
`fiscalPeriodEnd` — NEITHER key exists on any real row (this doc already showed the
correct `fiscalEndDate`/`reportDate` shape above, but the code never matched it) — so
`fiscal_end` was silently `None` on every fundamentals row ever written, including both
full-universe pulls before this fix. Harmless in isolation (nothing compared `fiscal_end`
values before fix 4), but it would have defeated `compute_fcf_margin_rows()`'s
same-period check (`None == None` trivially "matches" without verifying anything). Fixed
to read `fiscalEndDate` (fiscal_end) / `reportDate` (date), with the old guessed keys
kept as a defensive fallback. **The two dated pulls already on disk from before this
code fix still show `fiscal_end: None`** for every row — not re-fetched (no live call
budget spent on this since period alignment is structurally guaranteed within fix 4's
design: fcf and sales always come from the SAME call/periodicity/universe now, so a
`None == None` false-match couldn't actually smuggle in a cross-period ratio even before
this code fix landed); a future pull will populate `fiscal_end` correctly and get a real
verification, not just a structural guarantee.

Full-universe pulls (178 ids each; two calls, one per periodicity group):
- QTR (`BALANCE_SHEET_METRICS`, 3 metrics): 534 raw rows, 528 quality-ok (176/178
  tickers per metric).
- LTM (`FLOW_METRICS`, 4 metrics + derived `fcf_margin`): 1246 raw + 178 derived rows;
  843/1424 quality-ok combined (gross_margin 171/178, operating_margin 172/178, fcf
  164/178, sales 172/178, fcf_margin 164/178 — the fcf_margin count exactly tracks fcf's,
  since a ticker needs both legs present and matching to derive one).
- 32 tickers had FCF <= 0 on an LTM basis (down from the QTR-based run's cash-negative
  count the coordinator flagged as inflated by the period mismatch — not independently
  re-verified against that exact prior count, but the LTM figure is the one to trust
  going forward).

**Argument-drift gotcha (fixed):** the live call placed `audit` as the literal STRING
`"null"` in the tool_use input the model actually submitted, not JSON `null`/Python
`None` — `_run_and_parse`'s argument-drift check (expecting Python `None` from
`_fundamentals_args`) false-positived on the very first live Fundamentals call
("argument drift in audit: placed {'audit': 'null'}"). Fixed in `snapshot.py`'s
`_arg_norm()`: `None` and the case-insensitive string `"null"` now normalize to the same
value. This is the only None-valued expected arg anywhere in `scripts/valuation/`.

---
_Last updated: 2026-09-17, RIS5 A3 fix round 4. Every section above (GlobalPrices
`prices`/`market_value`, EstimatesConsensus `consensus_rolling`, FactSet_Metrics discovery,
FactSet_Fundamentals) is confirmed against real tool_result payloads from this task's
live runs. Fix 4 closed the FCF-margin period-mismatch bug (LTM/QTR periodicity split +
FF_SALES in the same call) and a `fiscal_end` field-name bug found while testing it. See
task-3-report.md's "Fix round 4" section for the full run-by-run counts and cost._
