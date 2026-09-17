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

**Field name for the cap value: NOT YET CONFIRMED against a real response as of this
commit** — `scripts/valuation/snapshot.py`'s `normalize_market_value_rows()` tries, in
order: `marketValue`, `mktVal`, `market_value`, `mcap`, `value` (see `_MCAP_KEYS`). Update
this section with the real key and delete the others from that list once the first live
daily run has inspected a raw response (see the RIS5 A3 task report for that run's actual
output, or grep `state/valuation/prices_<date>.jsonl` `quality` values for `fail:mcap<=0`
across every row — an all-fail pattern there means the key guess was wrong).

## FactSet_EstimatesConsensus

### `estimate_type='consensus_rolling'` (from tool schema; confirmed shape live 2026-09-17)

Request: `ids` (<=3000), `metrics` (**max 1 per request**), `periodicity` (`ANN`/`QTR`/...),
`relativeFiscalStart`/`relativeFiscalEnd` (1=next period/FY1, 2=FY2, ...; 4/5 for the
weekly FY4-FY5 pull, amendment v1.2 — no separate discovery needed, `relativeFiscalStart`/
`End` just take a bigger number). No `startDate`/`endDate` needed for "current" consensus
(the PIT rule only applies when BOTH dates are given — omit both for the latest snapshot,
which is what a daily valuation snapshot wants).

Response row (per relativeFiscalPeriod requested):
```
{"requestId": "<id>", "date": "YYYY-MM-DD", "relativePeriod": 1|2|3|4|5,
 "fiscalEndDate": "YYYY-MM-DD", "mean": <float|null>, "median": <float|null>,
 "count": <int>, "up": <int>, "down": <int>}
```

### Metric codes (amendment v1.2: daily pull is now SALES/EPS/EBITDA/FCF)

- `SALES`, `EPS` — confirmed live (this task's earlier run, 2026-09-17 afternoon).
- `EBITDA` — confirmed directly from the `FactSet_EstimatesConsensus` tool's own schema
  description, which gives it verbatim as an unprefixed example metric ("SALES, EPS,
  EBITDA, PRICE_TGT are all valid `metrics` values, no FF_ prefix"). Not yet checked
  against a real response row as of this commit (fix 2, pre-live) — see the RIS5 A3 task
  report's "Live run" section for whether the first live EBITDA batch returned non-null
  `mean`/`count` values.
- `FCF` — **resolved via a live `FactSet_Metrics` discovery call**
  (`data_products=["fundamentals","estimates"]`, combined with the Fundamentals FF_ code
  probe below so both discoveries cost one call, not two) rather than guessed, per the
  coordinator's pre-live-call review. See the task report for the confirmed code and
  whether it is literally `FCF` (in which case `snapshot.py`'s existing
  `f"{label}_{metric.lower()}"` key convention produces `fy1_fcf`/etc. unchanged) or
  something else (in which case a `CONSENSUS_METRIC_LABELS` override map is needed instead
  of `.lower()` — see the report for which branch was taken).

## FactSet_Metrics (discovery tool for FactSet_Fundamentals / FactSet_Estimates)

`text: [queries]` (no hyphens — spaces only), `target='metric'` (default),
`data_products=['fundamentals']` to restrict to FF_* codes. Response: metric records keyed
by `properties.metric` (the exact code to paste into Fundamentals — never abbreviated or
inferred). See `scripts/valuation/fundamentals.py`'s `discover_metrics_prompt`.

## FactSet_Fundamentals

Mandatory workflow: FactSet_Metrics MUST be called first; codes must come verbatim from
its response. `audit` is a REQUIRED parameter (pass `null` explicitly for no audit data —
`scripts/valuation/fundamentals.py` always does this; there is no ingest use for the audit
trail). Periodicity fallback ladder if unspecified: QTR -> SEMI -> ANN.

**Net debt / cash / gross margin / operating margin / FCF margin FF_ codes: NOT YET
confirmed** — `scripts/valuation/fundamentals.py`'s `FUNDAMENTALS_METRICS` dict is empty
until the live probe runs (`main()` refuses to guess). Update this section with the
confirmed `{label: FF_code}` mapping once the probe (`discover_metrics_prompt` +
FactSet_Fundamentals 3-id verification, per the task's QUOTA rules) has run, and hardcode
the same mapping into `FUNDAMENTALS_METRICS`.

---
_Last updated: 2026-09-17, RIS5 A3. GlobalPrices `prices` and EstimatesConsensus
`consensus_rolling` sections are confirmed against real tool_result payloads from this
task's live daily snapshot run. `market_value`'s field name and the Fundamentals FF_ codes
are still open — see the task-3-report.md for whether this task's own probe closed them._
