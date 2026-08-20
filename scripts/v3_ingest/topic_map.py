#!/usr/bin/env python3
"""Shared topic vocabulary over both registers (spec §4.2).

ONE VOCABULARY, TWO REGISTERS. Analyst exchanges (exchanges.jsonl) are the
question side; MD&A diffs and foreign claims (claims.jsonl) are the evidence
side. Both map into the SAME topic namespace — otherwise §6.2's two-count
comparison has no way to know that a disclosure and a question concern the same
topic, and the gap metric is simply not computable.

THEMES ARE ANCHORS, NOT BOXES. The config/watchlist.yaml slugs seed the space
and preserve continuity with the existing labelled history. A phrase that lands
near one inherits it; a phrase that lands far from all of them becomes a
new-theme CANDIDATE. That is how the vocabulary grows.

THE OPERATOR OWNS THE VOCABULARY. Candidates are written to a review file. This
module NEVER writes to config/watchlist.yaml — the same rule that governs tier
promotion.
"""
from __future__ import annotations

import datetime as dt
import math
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

REPO_ROOT = Path("/root/research-watchlist")
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"

# Cosine on gemini-embedding-001. Calibrated in Task 6 against the real
# corpus; this is the starting point, not a tuned value.
SIM_THRESHOLD = 0.72


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] topic_map: {msg}", flush=True)


def load_themes(watchlist_path: Path = WATCHLIST_YAML) -> list:
    """Every slug across every theme group, sorted. The count is whatever the
    file says today — it has already changed once and will change again."""
    data = yaml.safe_load(watchlist_path.read_text()) or {}
    slugs = set()
    for group in (data.get("themes") or {}).values():
        for slug in group or []:
            slugs.add(str(slug))
    return sorted(slugs)


def anchor_text(slug: str) -> str:
    """A slug is not a sentence. Embedding `china_ai_infrastructure_demand`
    raw wastes the model's language prior; the spaced phrase does not."""
    return slug.replace("_", " ")


def cosine(a: list, b: list) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def assign(phrase_vecs: list, anchor_vecs: list, anchors: list,
           threshold: float = SIM_THRESHOLD) -> list:
    """-> [(theme_or_None, similarity)] aligned to phrase_vecs.

    The similarity is reported even on a miss: a phrase that scored 0.71
    against an existing theme is a different kind of candidate from one that
    scored 0.2, and the operator review in §4.2 needs to see which."""
    out = []
    for pv in phrase_vecs:
        best_i, best_s = -1, -1.0
        for i, av in enumerate(anchor_vecs):
            s = cosine(pv, av)
            if s > best_s:
                best_i, best_s = i, s
        out.append((anchors[best_i] if best_s >= threshold else None, best_s))
    return out
