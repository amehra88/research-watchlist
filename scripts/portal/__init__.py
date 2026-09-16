"""Portal package: builds mobile-web JSON bundles from the research vault.

Every module in this package reads live data from REPO, never from a worktree
checkout — the operator's vault only exists on the droplet at this path.
"""
from pathlib import Path

REPO = Path("/root/research-watchlist")
