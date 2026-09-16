"""Portal package: builds mobile-web JSON bundles from the research vault.

Every module in this package reads live data from REPO, never from a worktree
checkout — the operator's vault only exists on the droplet at this path.

Module map (RIS4 slice 2):
  - vault.py         (Task 1) — notes/ discovery, note loading, wikilink
                      resolution, per-ticker bundle assembly.
  - identity.py       (Task 2) — ticker universe, display names, FactSet ids.
  - reports.py        (Task 3) — "Today" report cards (Daily Digest, news-digest
                      emails, thesis/stage alerts); etf_trades.py split out of it.
  - etf_trades.py     (Task 3) — ws ETF-holdings-change report parsing.
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
  - budget.py, build_portal.py (Task 6) — CLI + size-budget checks (not yet built).
  - app/              (Tasks 7-8) — the static mobile-web frontend (not yet built).
"""
from pathlib import Path

REPO = Path("/root/research-watchlist")
