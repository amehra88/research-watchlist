"""
Unit tests for embed.py — batching, dedup, and cache safety.

No pytest in this env — run directly:
    python3 scripts/chunking/test_embed.py

These use a fake `genai` object, so nothing here touches the network.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import embed as E  # noqa: E402


class FakeGenai:
    """Records every call. `content` is a str (single) or list (batch)."""

    def __init__(self, fail_batches_containing=None):
        self.calls = []
        self.fail_on = fail_batches_containing

    def embed_content(self, *, model, content, task_type):
        self.calls.append(content)
        if isinstance(content, list):
            if self.fail_on and any(self.fail_on in c for c in content):
                raise RuntimeError("input too long")
            return {"embedding": [[float(len(c))] * 3 for c in content]}
        if self.fail_on and self.fail_on in content:
            raise RuntimeError("input too long")
        return {"embedding": [float(len(content))] * 3}


def _reset():
    E._CACHES.clear()
    E._DIRTY.clear()


def test_batches_instead_of_one_call_per_text():
    """The 10.7h blocker: 16k phrases at one call per text. Batching is the
    whole fix, so assert on call COUNT, not on the returned vectors."""
    _reset()
    g = FakeGenai()
    texts = [f"phrase number {i}" for i in range(250)]
    out = E.embed(texts, "retrieval_document", use_cache=False, genai=g,
                  batch_size=100)
    assert len(out) == 250
    assert len(g.calls) == 3, f"expected 3 batched calls, got {len(g.calls)}"


def test_duplicate_texts_are_embedded_once():
    """Phrase extraction emits duplicates BY DESIGN — that repetition is what
    MIN_CANDIDATE_COMPANIES counts. Paying for each copy is pure waste."""
    _reset()
    g = FakeGenai()
    out = E.embed(["alpha", "alpha", "beta", "alpha"], "retrieval_document",
                  use_cache=False, genai=g, batch_size=100)
    assert len(out) == 4
    assert out[0] == out[1] == out[3], "same text must give the same vector"
    sent = g.calls[0]
    assert sorted(sent) == ["alpha", "beta"], f"sent {sent}"


def test_a_failing_batch_falls_back_to_per_text():
    """One over-long MD&A block must not cost the other 99 embeddings in its
    request. The batch dies; every good text in it still lands."""
    _reset()
    g = FakeGenai(fail_batches_containing="POISON")
    texts = ["good one", "POISON text", "good two"]
    try:
        E.embed(texts, "retrieval_document", use_cache=False, genai=g,
                batch_size=100)
    except RuntimeError:
        pass
    else:
        raise AssertionError("a text that always fails must still raise")
    singles = [c for c in g.calls if isinstance(c, str)]
    assert "good one" in singles and "good two" in singles, \
        f"good texts were not retried individually: {singles}"


def test_cache_file_is_read_once_per_process():
    """The 334MB blocker. Re-reading per call is what took the probe to
    exit 137."""
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        reads = []
        orig = E._read_cache_file
        E._read_cache_file = lambda path: (reads.append(path), orig(path))[1]
        try:
            g = FakeGenai()
            E.embed(["a"], "retrieval_document", genai=g, cache_path=p)
            E.embed(["b"], "retrieval_document", genai=g, cache_path=p)
            E.embed(["c"], "retrieval_document", genai=g, cache_path=p)
        finally:
            E._read_cache_file = orig
        assert len(reads) == 1, f"cache re-read {len(reads)} times"


def test_second_call_hits_cache_and_spends_no_api_call():
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        g = FakeGenai()
        E.embed(["alpha", "beta"], "retrieval_document", genai=g, cache_path=p)
        n = len(g.calls)
        E.embed(["alpha", "beta"], "retrieval_document", genai=g, cache_path=p)
        assert len(g.calls) == n, "cached texts must not be re-embedded"


def test_cache_survives_a_new_process():
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        g = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g, cache_path=p)
        _reset()                      # simulate a fresh process
        g2 = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g2, cache_path=p)
        assert g2.calls == [], "a persisted embedding must survive a restart"


def test_save_is_atomic_and_leaves_no_tmp_files():
    """A kill mid-write must not truncate the cache. _load_cache swallows
    JSONDecodeError and returns {}, so a truncated file reads as EMPTY and the
    next save overwrites 319MB of real embeddings with a small dict — silent,
    and unrecoverable."""
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        g = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g, cache_path=p)
        assert json.loads(p.read_text()), "cache must be valid JSON after save"
        leftovers = [f for f in os.listdir(d) if f != "c.json"]
        assert leftovers == [], f"temp files left behind: {leftovers}"


def test_a_separate_cache_path_never_touches_the_default():
    """The topic path gets its own file so it cannot corrupt the chunk store."""
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "topics.json"
        g = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g, cache_path=p)
        assert p.exists()
        assert E._CACHE_PATH not in E._CACHES, \
            "the chunk-store cache must not even be LOADED by the topic path"


def test_use_cache_false_writes_nothing():
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        g = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g, cache_path=p,
                use_cache=False)
        assert not p.exists(), "use_cache=False must not create a cache file"


def test_task_type_is_part_of_the_cache_key():
    """Asymmetric embedding: the same string embedded as a query and as a
    document are different vectors and must not collide."""
    _reset()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.json"
        g = FakeGenai()
        E.embed(["alpha"], "retrieval_document", genai=g, cache_path=p)
        n = len(g.calls)
        E.embed(["alpha"], "retrieval_query", genai=g, cache_path=p)
        assert len(g.calls) == n + 1, "query embedding must not reuse the doc vector"


# ───────────────────────── runner ─────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
