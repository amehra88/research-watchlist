# RIS4 portal — build, contents, and publish runbook

The RIS4 portal is a static mobile-web bundle (`portal_build/`) generated
entirely from the operator's research vault (`notes/`, `config/`, `state/`,
`logs/`) and published as a private Claude Artifact the operator opens on
the iPhone Claude app. There is no server: the app is a `fetch()`-only
static site, and "live" means "as of the last build," shown on every screen
as "as of `built_at`."

Live artifact: <https://claude.ai/artifact/BRc8rhxBgBDjtwGpzGS4N1> (favicon
🧭 already set on first publish — see "Publish runbook" below for why it is
never passed again).

## What the bundle contains

Top level (builder-owned, see "Stale-file removal scope" below):

| Path | Written by | What it is |
|---|---|---|
| `index.html`, `styles.css`, `app.js`, `app2.js` | copied from `scripts/portal/app/` | the static frontend shell + router (`app.js`) and the Themes/Ideas/Scores/Signals/News/Insiders/ETF/Reports/Search screens (`app2.js`) |
| `vendor/` | copied from `scripts/portal/app/vendor/` | third-party JS the app loads locally (currently `markdown-it.min.js` + `VERSIONS.txt`) |
| `data/manifest.json` | `state_bundles.manifest()` | build metadata: `built_at`, `git_sha`, `counts`, `tickers`/`themes` indexes, `today`/`upcoming`, `health`, `applied_ids`, and `files` (every other published path's `bytes`+`sha256`, hashed at build time — see "Publish runbook / `--check`" below). Read by the **Status** screen and the app's "as of" footer on every screen. |
| `data/tickers/<TICKER>.json` | the builder CLI's own tickers-and-ingest stage (`build_portal.py`, not vault.py/state_bundles.py — see that module's docstring for who's who) | one file per real ticker that has notes, a thesis, or a profile (tickers with none of the three are skipped entirely — "tickers without notes are NOT given files"). Each bundle holds the ticker's Notes/Thesis/Signals/News/Insiders/ETF sub-objects, all rendered from this one fetch by the ticker detail tabs in `app.js`. |
| `data/pvt/<slug>.json` | same stage, for `.pvt` identifiers | same shape as `data/tickers/`, keyed by the id with its trailing `.pvt` stripped (e.g. `openai.pvt` → `data/pvt/openai.json`) |
| `data/ingest/<bucket>.json` | same stage, via `vault.ingest_bundles()` | the six ingest-channel buckets (`flows`, `foreign`, `podcasts`, `pvt`, `sector`, `substacks`) verbatim. No screen of its own — opened from **Search** result rows. |
| `data/reports/<YYYY-MM-DD>.json` | `reports.build_reports()` | daily report cards (Daily Digest, news-digest emails, thesis/stage alerts, ETF update) for the last `--reports-days` (default 14). Read by **Today** and the **More → Reports** archive. |
| `data/etf_trades.json` | `etf_trades.etf_trades()` | ws ETF holdings-change report, parsed, for the last `--reports-days`. Read by **More → ETF trades** and the per-ticker ETF tab. |
| `data/themes.json` | `state_bundles`/`theme_ideas` (`themes_bundle()`) | the 62 P2 theme anchors + adjacency/diffusion/stage state. Read by the **Themes** screen and each ticker's Signals tab. |
| `data/ideas.json` | `theme_ideas.ideas_bundle()` | the six-stream idea-surfacing bundle + pending candidates. Read by the **Ideas** screen (candidate accept/reject buttons are disabled — see "Known limitations"). |
| `data/scores.json` | `state_bundles` | Tier 1–2 `ai_positioning`/`competitive_advantage`/`potential_investor_interest` score table + proposed changes. Read by **More → Scores**. |
| `data/market.json` | `state_bundles` | market/price context bundle. Read by the Signals tab. |
| `data/insiders.json` | `state_bundles` | InsiderScore-derived rows. Read by the per-ticker Insiders tab — **static until slice 4** (no live MCP call from the page yet). |
| `data/sec_30d.json` | `news_sec.news_bundle()` | last 30 days of SEC filing rows. Read by each ticker's News/SEC tab. |
| `data/news/<YYYY-Www>.json` | `state_bundles` (news shards) | weekly news-item shards, last 30 days. Opened from ticker News tabs and Search result rows. |
| `data/news_index.json` | `state_bundles` | index over the news shards (ticker/date/theme). Read by the News screen's filter chips. |
| `data/search.json` | `search_index.build_units()` + `write_index()` | the postings-based search index over notes, theme notes, news rows, and ingest items. Read by the **Search** screen — this is keyword search on the page; semantic search over pg arrives with Phase 5 (see `docs/superpowers/specs/2026-09-15-RIS4-plan.md`). |

`smoke/` (2 files, `probe.json`/`probe.js`) is **not** in this table because
it isn't builder output at all — see "Stale-file removal scope."

## How to build

```
python3 scripts/portal/build_portal.py --out /root/research-watchlist/portal_build
```

Flags (`build_portal.py --help`):

| Flag | Default | Meaning |
|---|---|---|
| `--out DIR` | `REPO/portal_build` | where to publish the built tree (atomically — see below) |
| `--format json` | `json` | only `json` is implemented |
| `--news-days N` | 30 | window for news/SEC shards |
| `--sec-days N` | 30 | window for SEC filing rows |
| `--reports-days N` | 14 | window for report cards + ETF trades archive |
| `--dry-run` | off | build into a scratch dir, print the budget table + counts/bytes, write nothing to `--out` |
| `--no-app` | off | skip copying `scripts/portal/app/` — the app files are then removed as stale if a prior build published them (this is intended: `--out` always converges to exactly what the current stage list produces — see `build_portal.py`'s own docstring) |

Orchestration order (fixed): `reports` → `etf_trades` → `tickers_and_ingest`
→ `search_index` → `app` (copy, unless `--no-app`) → `state` (writes
`data/manifest.json` **last**, after hashing every file already on disk, so
the app files and the search index are both in `manifest.files`).

A live build takes **~50 s** and produces **145 files** (147 on disk once
`smoke/` is present), **~26.6 MB** total — well under every `budget.py`
limit:

| Budget (`scripts/portal/budget.py`) | Limit | Enforced against |
|---|---|---|
| total files | 240 | every file under the staged tree |
| any single text file (`.json .html .htm .css .js .mjs .md .txt .svg .jsonl`) | 14 MB | same file's size |
| total bytes | 48 MB | sum of every file's size |
| `index.html` | 1 MB | that one file |

`build_portal.py` prints the budget table (top 25 files by size + a
files/total summary) on **every** build, success or failure, then:

- **exit 0** — staged tree published (atomically per file — see `_publish()`'s
  own "ATOMICITY NOTE" for the narrow per-file-not-per-tree caveat), stale
  files removed, `n_published`/`n_removed_stale`/elapsed logged.
- **exit 1** — a stage raised, or publishing itself raised. `--out` is left
  exactly as it was before the run (a stage failure) or may be partially
  updated (a mid-publish failure — files already `os.replace()`d before the
  exception stay live).
- **exit 2** — `budget.check()` found a violation. `--out` is left untouched;
  the staged tree is discarded.

`--dry-run` returns 0 (clean) or 2 (budget violation) the same way, but never
touches `--out` at all — it builds into a `tempfile.mkdtemp()` scratch dir
and deletes it before returning.

## Stale-file removal scope (`OWNED_PATHS`)

Publishing a new build doesn't just add files — it also **removes** any file
already under `--out` that this build didn't produce, so `--out` always
converges to exactly the current stage list's output. That removal (and the
initial-publish overwrite) is scoped to `build_portal.OWNED_PATHS`:

```python
OWNED_PATHS = ("data/", "vendor/", "index.html", "app.js", "app2.js", "styles.css")
```

Anything under `--out` that doesn't match one of those prefixes/names —
today, only `smoke/` — is **invisible** to both the publish and stale-removal
passes: never written, never overwritten, never deleted, no matter what a
given build's stage list did or didn't produce. `smoke/` survives because it
is the Phase 0 iPhone smoke-test artifact source (gitignored, `probe.json` +
`probe.js`), not builder output — an earlier, unscoped version of the
stale-removal pass deleted it on the first live run, which is why
`OWNED_PATHS` is an exhaustive allowlist rather than "everything under
`--out`."

## Publish runbook (session steps)

Slice 2 has no automated publish yet — a session does this by hand, following
the operator's standing rule to pause `auto_sync` for any non-trivial build
(back up crontab, comment the 15-min auto_sync line, verify; restore +
verify at the end):

1. **Pause auto_sync.** Back up crontab to
   `/root/backups/crontab.pre_build_<ts>.bak`, comment the auto_sync line,
   verify with `crontab -l`.
2. **Build.**
   ```
   python3 scripts/portal/build_portal.py --out /root/research-watchlist/portal_build
   ```
   Read the printed budget table; confirm exit 0.
3. **Get the files map.**
   ```
   python3 scripts/portal/publish_files.py --check
   ```
   (`--check` also verifies every published file's sha256 against the build's
   own `data/manifest.json`, so a bad build can't silently reach the
   Artifact.) Copy the printed JSON — it's the exact `files` argument for the
   next step.
4. **Publish with the `Artifact` tool.** This is the exact call shape
   verified against the live artifact — every part of it matters:
   - `file_path=/root/research-watchlist/portal_build/index.html`
   - `root=/root/research-watchlist/portal_build`
   - `files=` the JSON **map** `publish_files.py` printed — `{"published/path": "published/path", ...}` for every one of the 144 non-`index.html`, non-`smoke/` files. **The list form `["a.js", ...]` is REJECTED** — the Artifact tool requires the map form.
   - `capabilities: {}` for slice 2 (no runtime capability wired in yet — see the RIS4 plan's Phase 4 capability list, `{db, assets, sample, mcp:{...}}`, for what slice 3+ will add)
   - `favicon` — **only on the very first publish** (already set: 🧭). Passing it again on a redeploy is a mistake to avoid, not merely unnecessary.
   - `label` — free text describing this publish (e.g. `"Task 9 docs + publish helper"`)
   - Redeploy = the same `file_path` from the session that originally
     published it, **or** `url=<the artifact URL>` from any other session —
     never a fresh publish (that creates a second artifact and a new URL).
   - **Every build's `files` map must be sent in full on every redeploy.**
     Files left out of a `files` call are *kept*, not removed — since every
     `data/*` file changes on every build, omitting one means the live
     artifact serves stale data for that file indefinitely.
   - Every published path must already match `OWNED_PATHS` (today:
     `app.js`, `app2.js`, `styles.css`, `vendor/**`, `data/**`) and the whole
     call is subject to the Artifact tool's own **255-file cap** —
     `publish_files.py` enforces the 254-entry half of that (`index.html`
     takes the 255th slot via `file_path`) and exits 2 if exceeded.
5. **Post-publish checks, on the phone:**
   - **Status** screen shows today's `built_at`.
   - `data/manifest.json`'s `health`/caps fields are non-null.
   - One live price renders somewhere that reads FactSet/InsiderScore data
     (once a live capability is wired in — slice 2 has none, so today this
     step is "the bundle's own market/scores data renders, not `?`").
   - A test capture round-trips: appears in `inbound.jsonl` within 15 minutes
     and produces a `.summary.md` within 30 (once the input channel — slice
     5 — exists; not yet applicable to slice 2).
6. **Restore auto_sync.** Uncomment the crontab line, verify with
   `crontab -l`.

## Planned: daily auto-republish (not built)

Phase 0's routine probe (`docs/portal/phase0.md`, §P0.2) confirmed a
one-shot cloud routine has the `Artifact` tool available (`ARTIFACT_TOOL:
available`). The intended daily design, **PLANNED, not built**:

1. A droplet cron builds `portal_build/` (see `docs/portal/cron.txt`).
2. The droplet pushes the built bundle to a private GitHub branch/repo
   (`portal-bundle`).
3. A 07:40 ET cloud routine clones that branch, `Artifact read`s the live
   portal URL to confirm it still owns it, then republishes with `url=` and
   the fresh `files` map — no interactive session required for the daily
   refresh.

This needs a `portal-publish` runbook skill (or routine prompt) that
reproduces step 4 above (the exact call shape) unattended, plus the
GitHub-branch push step, neither of which exists yet. Until then, publishing
is the six-step manual runbook above, run from a session.

## Identity name backfill

One-time, run once on `main` after this slice merges:

```
python3 scripts/portal/identity.py --merge-names scripts/portal/fixtures/names_backfill_20260915.json --write
```

This appends any ticker in the backfill JSON that isn't already a key in
`config/ticker_identity.yaml` (and isn't a `.pvt`/foreign id — see
`identity.py`'s `_skip_from_yaml_write`) as a proper entry. It is safe to
re-run (idempotent — nothing to add on a second run prints "nothing to
merge").

The backfill JSON itself (`scripts/portal/fixtures/names_backfill_20260915.json`)
**stays load-bearing after the write**, not a one-time scaffold to delete:
four identifiers (`A000660`, `UMG.AS`, `2308.TW`, `simaai.pvt`) are
*permanently* skipped from the YAML write, because their `TICKER-US`
FactSet-id default would be wrong — `identity.display_names()` keeps reading
the backfill JSON as a live source at every build, forever, so those four
still resolve to a real display name.

## Tests

No pytest in this environment — every `test_*.py` runs standalone:

```
for t in scripts/portal/test_*.py; do python3 "$t"; done
```

Each prints a `✓`/`✗` per test and a final `N/M pass` line, and exits 1 if
anything failed (0 if clean).

## Known limitations

- **News search is 7-day, headline-only**, capped at the 3 MB `search.json`
  practical ceiling — full-text/30-day news search is out of scope for this
  slice.
- **`upcoming` is always `[]`.** `reports.upcoming()` has no calendar cache
  to read: `scripts/v3_ingest/transcript_ingest.py` fetches the FactSet
  earnings/conference calendar live and never persists it, and per the brief
  this builder must never call FactSet itself just to manufacture one. A
  future calendar-cache writer can be wired in without changing
  `upcoming()`'s signature.
- **Nothing is operator-reviewed yet.** Every card/note shows provenance,
  but the review workflow itself (accept/reject, thesis challenge) is slice
  5's input channel.
- **Insiders is static until slice 4.** `data/insiders.json` is a build-time
  snapshot; there is no live MCP call from the page yet.
- **Candidate/idea buttons are disabled until slice 5.** The Ideas screen
  renders pending candidates but every accept/reject control is a genuinely
  inert, visibly-disabled `<button>` (never a styled `<a>` that looks
  clickable) — see `app2.js`'s `slice5Btn()`.

## Slice roadmap

- **Slice 2 (this one)** — read-only static bundle: builder package +
  frontend + docs/publish runbook (Tasks 1–9).
- **Slice 3** — Ask: an explicit-button, tool-using Q&A screen against the
  bundle (and, later, live MCPs), 3–5 tool rounds, subscription-cost-aware.
- **Slice 4** — live panels: Insiders and other MCP-backed screens read live
  data instead of a build-time snapshot.
- **Slice 5** — input channel: capture (photo/text) → `Portal`-labeled Gmail
  → inbox note → summary; theme accept/reject wired to
  `decisions.jsonl`/`candidates.json`; thesis challenge and ticker-add flows.
- **Slice 6** — novel names: surfacing tickers/companies not yet on the
  watchlist.

See `docs/superpowers/specs/2026-09-15-RIS4-plan.md` for the full plan,
including Phase 5 (a droplet "Research Vault" MCP connector behind a
Cloudflare Tunnel) and the separate "Expectations" spec (Part 2) planned
after slices 1–4 are live.
