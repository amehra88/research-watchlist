"""Portal package: builds mobile-web JSON bundles from the research vault.

Every module in this package reads live data from REPO, never from a worktree
checkout — the operator's vault only exists on the droplet at this path.

Module map (RIS4 slice 2, extended in slice 3):
  - vault.py         (Task 1) — notes/ discovery, note loading, wikilink
                      resolution, per-ticker bundle assembly.
  - identity.py       (Task 2) — ticker universe, display names, FactSet ids.
  - reports.py        (Task 3) — "Today" report cards (Daily Digest, news-digest
                      emails, thesis/stage alerts); etf_trades.py split out of it.
                      Slice 3: thesis/stage alert cards gain a structured
                      `items` array, built with evidence.py.
  - etf_trades.py     (Task 3) — ws ETF-holdings-change report parsing.
  - evidence.py       (slice 3, Tasks 1-2) — evidence index over
                      state/thesis/evidence_log.jsonl keyed by (ticker,
                      assumption_id), attached to ticker bundles as
                      `thesis.evidence`; plus stage-alert enrichment (cited
                      analyst exchange, breadth trend, tier-1/2 names on a
                      theme) read from state/topics/ and
                      state/transcripts/exchanges.jsonl. Read by reports.py
                      and build_portal.py's ticker stage.
  - state_bundles.py  (Task 4) — scores/market bundles + the manifest +
                      build_state(out_dir, ctx), the single entry point Task 6's
                      CLI calls. news_sec.py and theme_ideas.py split out of it.
  - news_sec.py       (Task 4) — 30-day news/SEC-filing shards.
  - theme_ideas.py    (Task 4, fix round 1) — themes/candidates bundle + the
                      six-stream ideas bundle. Imports FROM state_bundles.py
                      (Paths/DEFAULT_PATHS/_known_sets/_read_json/_read_jsonl);
                      state_bundles.py imports theme_ideas back for use in
                      manifest()/build_state() — see theme_ideas.py's own
                      docstring for why that two-way import is safe.
  - budget.py, build_portal.py (Task 6) — CLI + size-budget checks.
  - app/              (Tasks 7-8) — the static mobile-web frontend: index.html,
                      styles.css, app.js + app2.js, vendor/.
  - app/ask.js        (slice 3, Task 4) — Ask Claude: note/ticker/desk prompts
                      and byte budgets, the three desk-mode page tools
                      (search_vault/get_note/ticker_brief), streaming and
                      error handling, all via the artifact `sample`
                      capability. Loaded after app.js/app2.js; a no-op if
                      either is missing.
  - publish_files.py  (Task 9) — read-only helper: prints the `files` map a
                      session's Artifact publish call needs (every OWNED_PATHS
                      file under --out except index.html/smoke/dotfiles), plus
                      a --check mode that verifies sha256 against
                      data/manifest.json. See docs/portal/README.md for the
                      full publish runbook and docs/portal/cron.txt for the
                      two build-cron lines (not yet installed).
"""
from pathlib import Path

REPO = Path("/root/research-watchlist")
