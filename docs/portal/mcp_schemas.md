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
- `currency` IS present on the market_value row (the tool schema's "NOT USED" note was
  about the request-side `currency` param, not the response), but
  `normalize_market_value_rows()` does not currently carry it through to `mcap` — only
  the price row's own `currency` survives into `latest.json`. For a non-USD name (like
  this one, KRW) that means `mcap` and `price` could in principle disagree on currency if
  FactSet ever returns them differently; observed today they were consistent (both local
  currency), but this is undocumented behavior worth a follow-up if A5's math assumes
  `mcap` is USD or matches `price`'s currency unconditionally.
- The literal magnitude (`1240826747.5`) is NOT obviously "millions" as the module
  docstring assumed going in — flagged for whoever reconciles it against a known SK Hynix
  market cap; not fixed here since the field NAME (not scale) was fix 2's job.
- `scripts/valuation/snapshot.py`'s `_MCAP_KEYS` now tries `currentMarketValue` first,
  with the original guesses kept as a defensive (currently dead) fallback list.

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
trail). Periodicity fallback ladder if unspecified: QTR -> SEMI -> ANN. Max 250 ids, max
1600 metrics per call (confirmed from the tool's own schema) — the full 178-ticker
universe at 6 metrics fits in ONE call, well under both caps.

**CONFIRMED live 2026-09-17** (RIS5 A3 live run: one combined `FactSet_Metrics` discovery
call, then a 3-id verification call for NVDA-US/AVGO-US/COHR-US, then the full 178-ticker
pull, periodicity `QTR`):

| label | FF_ code | live probe values (NVDA / AVGO / COHR) |
|---|---|---|
| `net_debt` | `FF_NET_DEBT` | -60509 / 35444 / 1532.82 |
| `total_debt` | `FF_DEBT` | 38860 / 59419 / 3554.994 |
| `cash` | `FF_CASH_GENERIC` | 99369 / 23975 / 2022.174 |
| `gross_margin` | `FF_GROSS_MGN` | 74.98 / 67.46 / 38.49 (already a percentage) |
| `operating_margin` | `FF_OPER_MGN` | 66.24 / 54.31 / 15.74 (already a percentage) |
| `fcf` | `FF_FREE_CF` | 15353 / 10562 / -486.225 |

Internal consistency check on the probe: NVDA `total_debt - cash` = 38860 - 99369 =
-60509 = NVDA's own `net_debt` row exactly, confirming both the field mapping and the
sign convention (net_debt negative = net cash position). `FactSet_Metrics` reports
`"factor": "1000000"` on the debt/cash metrics (values are already in the stated currency
units — i.e. $millions for a company reporting in USD — not literal dollars); margins
carry no `factor` (already percentages, no rescaling needed).

**No dedicated FCF-margin FF_ code exists.** Neither "free cash flow margin" nor "free
cash flow" surfaced an FF_ metric distinct from `FF_FREE_CF` (Free Cash Flow, a dollar
figure) in the top 10 `FactSet_Metrics` results — no `FF_FCF_MARGIN`-shaped candidate.
`fcf_margin` must be DERIVED downstream as `FF_FREE_CF / SALES`, where SALES is a
fundamentals actual sourced separately (e.g. `ingest_metrics.py`'s existing SALES pull),
not fetched by this module.

Raw row shape (one row per (id, metric) at the requested periodicity):
```
{"requestId": "<id>", "fsymId": "...", "metric": "FF_NET_DEBT", "periodicity": "QTR",
 "fiscalPeriod": 2, "fiscalYear": 2026, "fiscalPeriodLength": 91,
 "fiscalEndDate": "YYYY-MM-DD", "reportDate": "YYYY-MM-DD", "epsReportDate": "YYYY-MM-DD",
 "updateType": "Final", "currency": "USD", "value": <float>}
```
Full-universe pull (178 ids, 6 metrics, one call): 1068 raw rows, 1050 quality-ok
(176/178 tickers with >=1 ok metric — 2 tickers had no coverage on this pull).

**Argument-drift gotcha (fixed):** the live call placed `audit` as the literal STRING
`"null"` in the tool_use input the model actually submitted, not JSON `null`/Python
`None` — `_run_and_parse`'s argument-drift check (expecting Python `None` from
`_fundamentals_args`) false-positived on the very first live Fundamentals call
("argument drift in audit: placed {'audit': 'null'}"). Fixed in `snapshot.py`'s
`_arg_norm()`: `None` and the case-insensitive string `"null"` now normalize to the same
value. This is the only None-valued expected arg anywhere in `scripts/valuation/`.

---
_Last updated: 2026-09-17, RIS5 A3 (live run relaunch). Every section above (GlobalPrices
`prices`/`market_value`, EstimatesConsensus `consensus_rolling`, FactSet_Metrics discovery,
FactSet_Fundamentals) is now confirmed against real tool_result payloads from this task's
live runs — nothing left open. See task-3-report.md's "Live run (relaunch)" section for
the full run-by-run counts and cost._
