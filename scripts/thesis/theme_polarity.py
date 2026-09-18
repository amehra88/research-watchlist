#!/usr/bin/env python3
"""Theme polarity: config/theme_polarity.yaml maps every config/watchlist.yaml theme
slug to a directional sign (-1 bearish/challenge, 0 neutral, +1 bullish/confirm), plus
an explicit `competition_slugs:` list (RIS5 A4 fix 0) of themes with competition/
competitive/market-share semantics -- a SEPARATE, additive signal from polarity
(competition themes stay polarity 0: a competition theme firing is two-sided).

    from thesis.theme_polarity import bearish_themes, competition_slugs
    bearish = bearish_themes()        # {"ai_inference_margin_compression", "software_seat_pricing_pressure"}
    competition = competition_slugs() # {"chip_design_competition", "hbm_competitive_landscape", ...}

`load()` fails loud (ValueError) if any watchlist theme slug is missing from the
polarity mapping, or if any value there isn't in {-1, 0, 1} -- a new theme added to
the watchlist vocabulary must never silently default to a polarity. `competition_slugs()`
fails loud if any entry in the `competition_slugs:` list isn't itself a real watchlist
theme slug.

Default paths point at REPO (the canonical checkout) the same way every other
thesis/ module does; a worktree build's own config/theme_polarity.yaml is only
visible there until merge, so tests and any worktree-local caller should pass
explicit paths rather than rely on the defaults.
"""
from __future__ import annotations
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
POLARITY_PATH = REPO / "config" / "theme_polarity.yaml"
WATCHLIST_PATH = REPO / "config" / "watchlist.yaml"


def watchlist_theme_slugs(watchlist_path: Path = WATCHLIST_PATH) -> set[str]:
    """Every theme slug in config/watchlist.yaml's `themes:` block, across all families."""
    w = yaml.safe_load(Path(watchlist_path).read_text(encoding="utf-8")) or {}
    slugs: set[str] = set()
    for family_slugs in (w.get("themes") or {}).values():
        slugs.update(family_slugs or [])
    return slugs


def load(polarity_path: Path = POLARITY_PATH, watchlist_path: Path = WATCHLIST_PATH) -> dict[str, int]:
    """{slug: -1|0|1} for every watchlist theme slug.

    Raises ValueError if a watchlist slug has no entry in theme_polarity.yaml, or if any
    stored value isn't -1, 0, or 1. Extra slugs in theme_polarity.yaml that the watchlist
    no longer carries are tolerated (a theme can be retired from watchlist.yaml without a
    matching edit here being mandatory), but never returned.
    """
    pol = yaml.safe_load(Path(polarity_path).read_text(encoding="utf-8")) or {}
    slugs = watchlist_theme_slugs(watchlist_path)
    missing = sorted(slugs - pol.keys())
    if missing:
        raise ValueError(f"{polarity_path}: missing polarity for watchlist theme(s): {missing}")
    bad = sorted(s for s in slugs if pol.get(s) not in (-1, 0, 1))
    if bad:
        raise ValueError(f"{polarity_path}: polarity value not in {{-1,0,1}} for: {bad}")
    return {s: int(pol[s]) for s in slugs}


def bearish_themes(polarity_path: Path = POLARITY_PATH, watchlist_path: Path = WATCHLIST_PATH) -> set[str]:
    """Every theme slug whose polarity is -1 (bearish / a challenge signal)."""
    return {s for s, v in load(polarity_path, watchlist_path).items() if v == -1}


def bullish_themes(polarity_path: Path = POLARITY_PATH, watchlist_path: Path = WATCHLIST_PATH) -> set[str]:
    """Every theme slug whose polarity is +1 (bullish / a confirm signal). Not consumed yet
    (only bearish_themes() is wired into insider_pull.py as of RIS5 A4); kept symmetric so a
    future confirm-side router doesn't need a second load/validate path."""
    return {s for s, v in load(polarity_path, watchlist_path).items() if v == 1}


COMPETITION_KEY = "competition_slugs"


def competition_slugs(polarity_path: Path = POLARITY_PATH, watchlist_path: Path = WATCHLIST_PATH) -> set[str]:
    """Every theme slug in theme_polarity.yaml's explicit `competition_slugs:` list (RIS5 A4
    fix 0) -- themes with competition/competitive/market-share semantics. Independent of
    `polarity`, which stays 0 for every one of these (rule 2 in the file: a competition theme
    firing is two-sided, it doesn't confirm or challenge on its own). Raises ValueError if the
    key isn't a list, or if any entry isn't a real config/watchlist.yaml theme slug."""
    raw = yaml.safe_load(Path(polarity_path).read_text(encoding="utf-8")) or {}
    lst = raw.get(COMPETITION_KEY) or []
    if not isinstance(lst, list):
        raise ValueError(f"{polarity_path}: {COMPETITION_KEY!r} must be a YAML list")
    slugs = watchlist_theme_slugs(watchlist_path)
    bad = sorted(set(lst) - slugs)
    if bad:
        raise ValueError(f"{polarity_path}: {COMPETITION_KEY!r} contains non-watchlist slug(s): {bad}")
    return set(lst)
