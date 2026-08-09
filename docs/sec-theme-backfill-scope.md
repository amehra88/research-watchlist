# SEC theme backfill — scope & cost (measurement only, nothing run)

**Status:** SCOPED, NOT RUN. Written 2026-08-09 at operator request ("scope it, don't run it").
No notes rewritten, no re-ingest, no `claude -p` spend incurred producing this document.

## What happened

`claude -p` theme extraction failed during two subscription-OAuth outages (~2026-07-01→07-08
and 2026-08-05→08-09; see the `claude-p-oauth-expiry-hygiene` memory). The SEC channel logs
the failure and continues (`theme extraction failed (continuing)`), writing the note with
`themes: []` in frontmatter. 678 such failures appear in `logs/v3_sec.log`.

## The number that matters is 828, not 1,769

**1,769** SEC notes on disk carry `themes: []` in frontmatter — but that is *not* the
retrieval-degraded population. `chunker.py:353-356` unions doc-level frontmatter themes with
a **per-chunk heuristic** (`_THEME_CUES`), so most of those notes still received themes at
chunk level and remain reachable by theme-scoped queries.

Measured against pg (`doc_type='sec_filing'`):

| Population | Count |
|---|---|
| SEC docs in pg | 4,026 |
| SEC chunks in pg | 18,313 |
| Chunks with no themes | 3,748 (20%) |
| **Docs where EVERY chunk has zero themes** | **828 (21%)** |

Those 828 are the genuinely theme-invisible docs — themes are a HARD scope filter in
`store.search()` (set overlap), so a theme-scoped query cannot return them at all. The other
~941 frontmatter-empty notes were rescued by the heuristic.

## Breakdown of the 828

**By tier** — all are T1/T2 (the SEC channel only ingests those tiers, so "T1+T2 only" is
not a reduction; recency is the only real lever):

- T2: 436
- T1: 392

**By filing year:**

| Year | Docs | | Year | Docs |
|---|---|---|---|---|
| 2018 | 5 | | 2023 | 147 |
| 2019 | 6 | | 2024 | 171 |
| 2020 | 10 | | 2025 | 192 |
| 2021 | 52 | | 2026 | 139 |
| 2022 | 106 | | | |

**Recency cuts:** 2024+ = 502 · 2025+ = 331 · 2026-only = 139

**Most-affected tickers:** AMBA (26), CRDO (24), GLW (23), CSCO (23), HPQ (21), WMT (21),
BE (20), TXN (20), MPWR (20), ADI (19), PWR (19), CRWD (18)

Note the spread is wide and shallow — no single ticker dominates, so a per-ticker fix buys
little. Scope by date or take the whole set.

## Cost

Measured basis: the 2026-08-09 bounded run did 12 filings for $1.5195 = **$0.127/filing**,
which covers fetch + parse + theme extraction + embed. Theme extraction alone is a fraction
of that, so treat these as conservative ceilings:

| Scope | Docs | Ceiling |
|---|---|---|
| All | 828 | ~$105 |
| 2024+ | 502 | ~$65 |
| 2025+ | 331 | ~$43 |
| 2026 only | 139 | ~$18 |

## Recommended implementation — update in place, do NOT re-ingest

The naive approach (re-run the notes through the channel) would re-chunk and re-embed
everything. Unnecessary: **the note text is unchanged — only the `themes` field is wrong.**

1. For each affected doc, run theme extraction only (`claude -p` against the existing note
   body, same prompt the channel uses, gated to `config/watchlist.yaml` valid themes).
2. Write themes into the note's frontmatter on disk.
3. `UPDATE chunks SET themes = %s WHERE doc_id = %s` for that doc's chunks — union with any
   existing per-chunk heuristic themes to preserve what the heuristic already found.

This avoids re-embedding entirely (no Gemini spend, no `embed_cache` load, no OOM exposure)
and keeps `chunk_id`s stable, so nothing else in the corpus shifts.

**Gate it:** take a pg dump first, run the gold eval before and after — it must hold at
15/28/28 (see the `eval-baseline-restored` memory). Adding themes changes scope-filter
behavior, so an eval regression is the signal that the extraction went wrong.

## Prevention

The channel currently treats a theme-extraction failure as non-fatal and writes the note
anyway, which is what silently built this backlog. Options, cheapest first:

- **Record the failure in frontmatter** (e.g. `themes_failed: true`) so a backfill can find
  affected notes precisely instead of inferring from `themes: []` — which, as shown above,
  over-counts by more than 2×.
- **Retry the extraction** once before giving up.
- Do not fail the whole run on it — partial ingest is still better than none.

## Open question for the operator

Nothing here is scheduled. Decide scope (all / 2024+ / 2025+ / skip) when the retrieval gap
actually bites — the 828 skew toward older filings that may matter less.
