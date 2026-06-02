"""
sources — source-quality classification + denylist (spec §3, §5).

Loads config/news_sources.yaml and exposes a SourceClassifier that maps a raw
Google-RSS source string to a tier, and tells the filter whether a url/title is
denylisted outright.

Tiers: top_tier > allowlist > borderline > unknown ; denylist is dropped.
"""
from __future__ import annotations

import os
import re
import yaml

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "news_sources.yaml",
)

TIER_RANK = {"top_tier": 3, "allowlist": 2, "borderline": 1, "unknown": 0, "denylist": -1}


def _norm(name: str) -> str:
    """Normalize a source name for matching: lowercase, drop leading 'the ', strip punctuation."""
    s = (name or "").strip().lower()
    if s.startswith("the "):
        s = s[4:]
    s = re.sub(r"[^a-z0-9 ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


class SourceClassifier:
    def __init__(self, cfg: dict):
        self._tier_of: dict[str, str] = {}
        # aliases: variant -> canonical (normalize both sides)
        self._alias: dict[str, str] = {_norm(k): _norm(v) for k, v in (cfg.get("aliases") or {}).items()}
        for tier in ("top_tier", "allowlist", "borderline"):
            for name in (cfg.get(tier) or []):
                self._tier_of[_norm(name)] = tier
        self._deny_sources = {_norm(n) for n in (cfg.get("denylist", {}).get("sources") or [])}
        self._deny_url_patterns = list(cfg.get("denylist", {}).get("url_patterns") or [])
        self._deny_title_patterns = [p.lower() for p in (cfg.get("denylist", {}).get("title_patterns") or [])]
        self._medium_single = {_norm(n) for n in (cfg.get("medium_single_item") or [])}

    # ── classification ────────────────────────────────────────────────────────
    def _canonical(self, source: str) -> str:
        n = _norm(source)
        return self._alias.get(n, n)

    def classify(self, source: str) -> str:
        """Return 'top_tier' | 'allowlist' | 'borderline' | 'denylist' | 'unknown'."""
        c = self._canonical(source)
        if c in self._deny_sources:
            return "denylist"
        return self._tier_of.get(c, "unknown")

    def is_medium_single(self, source: str) -> bool:
        """True if a lone item from this source qualifies as MEDIUM (§5c)."""
        return self._canonical(source) in self._medium_single

    def rank(self, source: str) -> int:
        return TIER_RANK[self.classify(source)]

    # ── denylist (url / title patterns) ───────────────────────────────────────
    def denied_url(self, url: str) -> bool:
        u = (url or "").lower()
        return any(p.lower() in u for p in self._deny_url_patterns)

    def denied_title(self, title: str) -> bool:
        t = (title or "").lower()
        return any(p in t for p in self._deny_title_patterns)

    def is_denied(self, source: str, url: str, title: str) -> bool:
        return self.classify(source) == "denylist" or self.denied_url(url) or self.denied_title(title)


def load_classifier(path: str | None = None) -> SourceClassifier:
    path = path or _DEFAULT_PATH
    with open(path) as fh:
        cfg = yaml.safe_load(fh) or {}
    return SourceClassifier(cfg)
