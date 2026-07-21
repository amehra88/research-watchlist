"""
verdict_cache — Lever 3: a per-day content-hash cache of classifier verdicts, so the morning brief
(and postmarket) REUSE the ~300 verdicts premarket already produced instead of re-calling `claude -p`
on the same clusters 24 min later. NO claude -p. Halves morning classify load; cuts tokens AND calls.

Why it's safe: the key is `cluster.hash` = sha1 of the cluster's sorted normalized tokens. Two clusters
with the same hash have the same token content → the same story → the same classification is valid.
A cache MISS just classifies normally, so a low hit-rate never loses correctness — only savings.

Self-populating and order-independent: every run both reads (skip claude -p on a hit) and writes (store
each fresh verdict). The first run to see a cluster classifies + caches it; later runs within the TTL
reuse. Invalidation: the file stores a `version` tag (classifier prompt/model/vocab); a mismatch on load
discards the whole cache, so a prompt or universe change never serves stale verdicts. Per-day filename +
a TTL on each entry bound staleness.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta

from .classify_llm import Classification, MODEL, PROMPT_VERSION


def build_version_tag(ticker_names: dict, valid_themes, macro_cfg: dict) -> str:
    """A fingerprint of everything that determines a verdict: model, prompt version, and the three
    vocabularies. Any change flips the tag → the cache invalidates (never serves cross-vocab verdicts)."""
    macro = sorted(c.get("name", "") for c in (macro_cfg.get("categories") or []))
    payload = "|".join([
        MODEL, PROMPT_VERSION,
        ",".join(sorted(ticker_names)),
        ",".join(sorted(valid_themes)),
        ",".join(macro),
    ])
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


class VerdictCache:
    def __init__(self, path: str, version_tag: str, ttl_hours: int = 12):
        self.path = path
        self.version_tag = version_tag
        self.ttl = timedelta(hours=ttl_hours)
        self._data: dict = {}          # cluster_hash -> {"ts": iso, "v": {...verdict...}}
        self.hits = 0
        self.misses = 0
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            raw = json.load(open(self.path))
        except (json.JSONDecodeError, ValueError, OSError):
            return
        if raw.get("version") != self.version_tag:   # vocab/prompt changed → discard
            return
        self._data = raw.get("entries", {}) or {}

    def get(self, cluster_hash: str, now: datetime):
        e = self._data.get(cluster_hash)
        if not e:
            self.misses += 1
            return None
        try:
            ts = datetime.fromisoformat(e["ts"])
        except (KeyError, ValueError, TypeError):
            self.misses += 1
            return None
        if now is not None and now - ts > self.ttl:
            self.misses += 1
            return None
        self.hits += 1
        d = e["v"]
        return Classification(
            cluster_id=d.get("cluster_id", ""),
            materiality=list(d.get("materiality", [])),
            themes=list(d.get("themes", [])),
            macro=list(d.get("macro", [])),
            confidence=d.get("confidence", "low"),
            rationale=d.get("rationale", ""),
        )

    def put(self, cluster_hash: str, cls: Classification, now: datetime):
        self._data[cluster_hash] = {
            "ts": (now or datetime.now()).isoformat(),
            "v": {
                "cluster_id": cls.cluster_id,
                "materiality": list(cls.materiality),
                "themes": list(cls.themes),
                "macro": list(cls.macro),
                "confidence": cls.confidence,
                "rationale": cls.rationale,
            },
        }

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"version": self.version_tag, "entries": self._data}, fh)
        os.replace(tmp, self.path)
