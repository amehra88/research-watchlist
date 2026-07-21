"""
Test the verdict cache (Lever 3): hit/miss, TTL expiry, version invalidation, and — the point of it —
that a cache HIT means classify_clusters makes ZERO claude -p calls for that cluster.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_verdict_cache.py
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import classify_llm                    # noqa: E402
from newsdigest.classify_llm import Classification     # noqa: E402
from newsdigest.verdict_cache import VerdictCache, build_version_tag  # noqa: E402

NOW = datetime(2026, 7, 21, 7, 0, 0)


class FakeCluster:
    def __init__(self, i):
        self.hash = f"{i:016x}"
        self._t = f"Test headline {i}"
        self.items = [{"title": self._t}]
        self.sources = ["Wire"]
        self.volume = 1
        self.representative = {"title": self._t}


def _cls(cid):
    return Classification(cluster_id=cid, materiality=["NVDA"], themes=[], macro=[],
                          confidence="high", rationale="stub")


def _cache(tag="v1"):
    path = os.path.join(tempfile.mkdtemp(), "vc.json")
    return VerdictCache(path, tag, ttl_hours=12), path


def test_put_get_roundtrip():
    c, _ = _cache()
    c.put("aaa", _cls("aaa"), NOW)
    got = c.get("aaa", NOW)
    assert got is not None and got.materiality == ["NVDA"] and got.confidence == "high"
    assert c.get("zzz", NOW) is None, "unknown hash must miss"
    print("  ✓ put/get roundtrip + miss on unknown hash")


def test_ttl_expiry():
    c, _ = _cache()
    c.put("aaa", _cls("aaa"), NOW - timedelta(hours=13))   # older than 12h TTL
    assert c.get("aaa", NOW) is None, "entry past TTL must miss"
    print("  ✓ TTL expiry → miss")


def test_version_invalidation():
    c, path = _cache(tag="v1")
    c.put("aaa", _cls("aaa"), NOW)
    c.save()
    reopened_same = VerdictCache(path, "v1")
    assert reopened_same.get("aaa", NOW) is not None, "same version must load entries"
    reopened_diff = VerdictCache(path, "v2-different")
    assert reopened_diff.get("aaa", NOW) is None, "changed version tag must discard the cache"
    print("  ✓ version tag mismatch invalidates the whole cache")


def test_build_version_tag_changes_with_vocab():
    a = build_version_tag({"NVDA": "NVIDIA"}, {"ai"}, {"categories": [{"name": "fed"}]})
    b = build_version_tag({"NVDA": "NVIDIA", "AMD": "AMD"}, {"ai"}, {"categories": [{"name": "fed"}]})
    assert a != b, "adding a ticker must change the version tag"
    print("  ✓ version tag fingerprints the vocab (universe change flips it)")


def test_cache_hit_skips_claude():
    """The whole point: a pre-cached cluster is NOT sent to claude -p."""
    clusters = [FakeCluster(i) for i in range(4)]
    c, _ = _cache()
    for cl in clusters[:3]:                        # pre-seed 3 of 4 verdicts
        c.put(cl.hash, _cls(cl.hash), NOW)

    calls = []
    def stub(prompt, repo_root, timeout=classify_llm.CLAUDE_TIMEOUT_S):
        cids = re.findall(r"cluster_id: ([0-9a-f]+)", prompt)
        calls.append(len(cids))
        arr = [{"cluster_id": cid, "materiality": ["NVDA"], "themes": [], "macro": [],
                "confidence": "high", "rationale": "fresh"} for cid in cids]
        return json.dumps(arr), 0.001

    orig = classify_llm._run_claude
    classify_llm._run_claude = stub
    try:
        out, cost, unclassified = classify_llm.classify_clusters(
            clusters, {"categories": []}, {"NVDA": "NVIDIA"}, {"ai"}, "/tmp",
            batch_size=40, logger=None, cache=c, now=NOW)
    finally:
        classify_llm._run_claude = orig

    assert len(out) == 4 and unclassified == [], "all 4 accounted for (3 cached + 1 fresh)"
    assert c.hits == 3 and c.misses == 1, f"expected 3 hits / 1 miss, got {c.hits}/{c.misses}"
    assert sum(calls) == 1, f"only the 1 uncached cluster hits claude -p, got {sum(calls)} classified"
    assert abs(cost - 0.001) < 1e-9, f"cost only for the fresh classify, got {cost}"
    assert c.get(clusters[3].hash, NOW) is not None, "the fresh verdict was written back to the cache"
    print(f"  ✓ 3 cached + 1 fresh → 1 claude -p call, 3 verdicts reused at $0, fresh one persisted")


if __name__ == "__main__":
    for fn in (test_put_get_roundtrip, test_ttl_expiry, test_version_invalidation,
               test_build_version_tag_changes_with_vocab, test_cache_hit_skips_claude):
        fn()
    print("\nALL PASS — verdict cache reuses prior verdicts, skips claude -p on hits.")
