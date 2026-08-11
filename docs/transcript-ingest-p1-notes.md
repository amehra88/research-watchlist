# P1 transcript ingest — build notes and measurements

Companion to `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` §4.1.
Everything below was measured on the droplet on 2026-08-11 against the live FactSet
connector. Where a number is an estimate or a proxy, it says so.

Component: `scripts/v3_ingest/transcript_ingest.py`
Tests: `scripts/v3_ingest/test_transcript_ingest.py` (no pytest in this env — run directly)
Fixtures: `scripts/v3_ingest/fixtures/*.json` — real API responses, one earnings call
and one conference, trimmed but otherwise unaltered.

## How to run

    python3 scripts/v3_ingest/transcript_ingest.py --print-universe
    python3 scripts/v3_ingest/transcript_ingest.py --ticker AAOI --max-queries 1 --dry-run
    python3 scripts/v3_ingest/transcript_ingest.py --ticker AAOI --max-queries 3
    python3 scripts/v3_ingest/transcript_ingest.py                     # full 9-month backfill
    python3 scripts/v3_ingest/transcript_ingest.py --window-months 1   # forward cron

### Forward cron (prepared, NOT installed)

The daily incremental. A 1-month window with the same ledger means each run only
fetches what is genuinely new; a re-run of a finished slice costs nothing (measured
at 0.65s, zero API calls). Weekdays only, after the SEC channel at 11:00 UTC:

    30 11 * * 1-5 cd /root/research-watchlist && /root/bin/alert_on_failure.sh \
      v3_transcripts python3 scripts/v3_ingest/transcript_ingest.py --window-months 1 \
      >> logs/v3_transcripts.log 2>&1

Deliberately left for the operator to install: it is a recurring production job
with a real per-run cost, and P1's backfill should be reviewed before a daily
process starts appending to the same corpus.

Outputs, all under `state/transcripts/`:

| File | Tracked? | What it is |
|---|---|---|
| `exchanges.jsonl` | no (gitignored) | one row per retrieved chunk — the P2/P4 substrate |
| `_progress.json` | no | resume ledger, three states per (factset_id, query, offset) |
| `_no_coverage.json` | **yes** | the exclusion list every downstream figure must print |
| `raw/` | no | raw FactSet payloads, kept so rows can be re-derived without re-calling |

The `{TICKER}.json` files already in that directory are the earnings-reviewer's
dedup ledgers and are untouched by this component.

## Transport — how Python reaches a claude.ai MCP connector

FactSet is a workspace connector, so a script cannot call it directly; the repo
pattern is `claude -p` with the MCP tool allowed (`newsdigest/factset_news.py`,
`cron_earnings_reviewer.py`). For news headlines it does not matter if the model
retypes the payload. For verbatim transcript text it matters a great deal, so this
component takes a different route and only falls back to retyping:

1. **`payload_source: "file"` (the normal case).** At `limit=50` the tool result is
   large enough (~107 KB measured) that the harness spills it to a file and hands
   the model the path. The prompt asks for **only that path**; the script reads the
   JSON itself. The model never touches the content. Every live page in the ramp
   runs took this path.
2. **`payload_source: "model_text"` (fallback).** Small results stay inline, so the
   model echoes the raw JSON. Every chunk is then checked against the API's own
   `textLength` field, and **one mismatch fails the whole page** rather than
   admitting a paraphrase. A file-sourced payload drops the individual bad chunk
   instead of failing the page — the API is the authority there, not a model.

If the harness ever stops spilling to files, path 2 still works: slower and
costlier, never silently lossy.

A direct HTTPS MCP client (`https://mcp.factset.com/content/v1`) would remove
`claude -p` from this path entirely. Not built: it needs the connector's OAuth
token, which is the operator's credential to authorise, not something to lift.

## What the API actually returns (probed live, all load-bearing)

- **Conference chunks have no `financialQuarter` key at all** — confirmed on the
  Lumentum/Mizuho 2026-06-09 document, which is one of §11.2's gold citations.
  Earnings chunks do have it. Period keys are therefore fiscal for earnings calls
  and calendar (from the event date) for conferences, and each row records which
  basis it used in `period_basis`.
- **`meta.pagination.total` is the returned count, not a corpus total** — `limit=3`
  gives `total: 3`, `limit=50` gives `total: 50`. A short page is the only honest
  stop condition; anything keyed on `total` would silently truncate.
- **`storyDateTime` is publication, not the event.** AAOI's 6-August call carries
  `storyDateTime: 2026-08-07T14:52:24`. The true event date exists **only in the
  headline**, which is why the row schema here persists `headline` even though
  §4.1's schema omits it. §10's host-firm exclusion also needs it.
- **Pages overlap.** Three pages at `limit=50` returned 150 chunks with 129 unique
  `vectorId`s. Dedup is not optional.
- FactSet's own `themes` field is an ESG taxonomy misfiring on tech, as §2.1 says.
  Unused.

## Recall — the §10 measurement, taken early

§10 requires measuring retrieval recall before P4 because FactSet is semantic
search, not whole-call export. Proxy: `docNum` carries a monotonic block index per
document (`md_3`, `qna_14`), so *blocks retrieved / highest block index seen* is a
conservative per-event coverage estimate.

AAOI, three theme-derived queries, 9-month window, 200 unique chunks:

| Event | Type | Blocks seen | Max index | Coverage |
|---|---|---|---|---|
| 2025-12-09 Raymond James TMT and Consumer Conf. | conference | 35 | 59 | 59% |
| 2026-02-26 Q4 2025 Earnings Call | earnings_call | 16 | 69 | 23% |
| 2026-03-03 Raymond James Institutional Investors Conf. | conference | 30 | 45 | 67% |
| 2026-05-07 Q1 2026 Earnings Call | earnings_call | 19 | 65 | 29% |
| 2026-05-13 Needham Technology Media Consumer Conf. | conference | 31 | 221 | 14% |
| 2026-08-06 Q2 2026 Earnings Call | earnings_call | 17 | 49 | 35% |

Marginal yield per additional query saturates fast: query 1 → 129 new chunks,
query 2 → 57, query 3 → 14.

**Read this honestly.** Coverage is 23–67% of each event, and the queries saturate,
which means more queries of the same kind will not close the gap — the retrieval is
topically scoped by construction, exactly as §4.1 warned. Two consequences:

- Every §7 output must state the limitation, per the spec.
- §11.2's gold test may fail under theme-derived queries. §11 already says that is
  the recall measurement, not a bug to paper over, and that the fix is widening
  query generation via the supply-chain graph — never hand-adding the query the
  test looks for.

Conference coverage is the pleasant surprise: 95 of AAOI's first 129 chunks came
from four conferences, versus three earnings calls. That is the Detector 1
substrate, and it closes the long-open `conference-transcript-ingest-path` item at
transcript fidelity rather than summary fidelity.

## Ramp results (2026-08-11)

Ramped one name → one name at full query depth → five names covering every
universe route. 990 rows, 33 pages `ok`, 2 pages `empty`, **0 failed**, every page
via the file transport.

| Name | Route | Rows | Events retrieved |
|---|---|---|---|
| AAOI | comparable + adjacent | 200 | 7 (3 earnings, 4 conference) |
| LITE | T1 | 211 | 10 (3 earnings, 7 conference) |
| FN | comparable | 194 | 7 (2 earnings, 5 conference) |
| COHR | T1 | 193 | 6 (2 earnings, 4 conference) |
| TSM | T1 (foreign filer) | 192 | 3 (3 earnings, 0 conference) |
| innolight.cn | tier_4 | 0 | none — recorded as `no_results` |

Corpus shape: 802 Q&A vs 188 prepared-remarks chunks; 524 conference vs 466
earnings-call chunks; 356 analyst chunks across 38 distinct firm strings; every
row carried a parsed `event_type`, `event_date` and `period_key`.

Three results worth keeping:

- **`innolight.cn` returned nothing**, confirming §2.3's finding that A-shares have
  no transcript coverage — and it landed in `_no_coverage.json` as `no_results`
  rather than vanishing. TSM works fine as `TSM-US`, so foreign-filer coverage is
  real where FactSet has it.
- **§10's host-firm problem is bigger than "sometimes"**: 107 of 213 conference
  analyst chunks (50%) were asked by the conference host's own firm. Counting
  those toward `n_banks` would roughly double apparent breadth at conferences.
- **Fiscal and calendar periods genuinely diverge** — 89 rows key to 2026Q3 and 11
  to 2026Q4 on a fiscal basis while the window ends in calendar Q3. `period_basis`
  is on every row so P4 never has to guess which clock a figure is on.

## Deltas from the spec, and why

1. **`ingest_comparables` added to the universe.** §4.1 lists T1+T2, supply-chain
   adjacents and `tier_4_ecosystem`, which leaves AAOI out of the universe
   entirely — while §3's rationale and §11.2's gold test both require it. Treated
   as an omission in §4.1's list, not a design decision. Every entry prints the
   route it entered by.
2. **`headline`, `event_name`, `host_hint`, `speaker_title`, `view_url`,
   `sentiment` persisted** beyond §4.1's row schema. The first three are what make
   event date, event type and §10's host-firm exclusion computable at all.
3. **`_no_coverage.json` written**, distinguishing three reasons that mean
   different things: `no_factset_id` (cannot ask), `no_themes` (nothing to ask),
   `no_results` (asked, nothing there).
4. **Supply chain reads `/root/research/config/supply-chain-manual.yaml`**, in the
   sibling repo. `watchlist.yaml` is symlinked into this repo; the supply-chain
   files are not, and CLAUDE.md's `config/supply-chain-manual.yaml` is misleading
   on that point.

## Universe as resolved on 2026-08-11

94 names: 43 T1 + 41 T2, plus supply-chain adjacents (manual/verified provenance
only), 3 comparables (FN, AAOI, POET) and 6 tier-4 ecosystem names with FactSet
ids. `.pvt` privates are excluded by construction. Two tier-4 entries
(`hisense_broadband.cn`, `source_photonics.cn`) have no `factset_id` and are
recorded as unresolvable rather than guessed.

**26 of the 94 have no assigned themes and therefore generate no queries** —
including CSCO, MDB, PANW, BABA, BIDU, CRDO and NBIS. This is a real coverage hole
and it is an operator decision, not a code fix: the fix is theme assignment in
`watchlist.yaml`, which only the operator writes. They are listed in
`_no_coverage.json` under `no_themes`.

Two watchlist data artifacts surfaced while resolving: `A000660` (a T1 entry that
looks like a mangled duplicate of `000660.KS`) and `AWS` (reached as a
supply-chain adjacent of DDOG, but a segment of AMZN rather than a listed
security). Both are harmless here — they will simply return nothing and land in
`no_results` — but both are worth a look in the watchlist itself.

## Known items for P2/P4, deliberately not solved in P1

- **Analyst firm names need normalising before `n_banks` is counted.** The AAOI run
  alone produced both `Needham & Co. LLC` and `Needham & Company, LLC`. Counting
  raw strings would inflate bank breadth.
- **`host_hint` is a hint.** It is the leading non-generic words of the event name
  (`Mizuho Global Technology Conference` → `Mizuho`), meant to be matched against
  `speaker_firm` at P4. Company-hosted events yield a non-bank hint (`AOI OFC`),
  which is correct: nothing to exclude.
- **`speaker_type` can be empty** in the API (16 of 200 live chunks); rows
  normalise `""` to `null` so no count can treat it as a fourth speaker class.
- Multi-company conference documents can carry very high block indices (the
  Needham document reaches 221), so the recall proxy understates coverage for
  those. Chunks are still attributed only to the queried company.
