#!/usr/bin/env python3
import sys, tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import embed_store as es


class FakeClient:
    def __init__(self, fail_first=0):
        self.calls, self.fail_first = [], fail_first
    def embed_content(self, model, content, task_type):
        self.calls.append(list(content))
        if self.fail_first:
            self.fail_first -= 1
            raise RuntimeError("429 Resource has been exhausted")
        return {"embedding": [[float(len(t))] + [0.0] * (es.EMBED_DIM - 1) for t in content]}


def test_ensure_embeds_only_missing_in_batches_and_persists():
    with tempfile.TemporaryDirectory() as d:
        st = es.EmbedStore(Path(d))
        c = FakeClient()
        n = st.ensure([("a", "xx"), ("b", "xxxx"), ("c", "x")], batch=2, client=c)
        assert n == 3 and [len(x) for x in c.calls] == [2, 1]
        assert st.has("a") and st.matrix(["a"]).shape == (1, es.EMBED_DIM)
        st2 = es.EmbedStore(Path(d))                      # reload from disk
        assert st2.ids == ["a", "b", "c"]
        assert st2.ensure([("a", "xx"), ("d", "y")], client=c) == 1
        m = st2.matrix(["b", "d"])
        assert m.dtype == np.float32 and abs(np.linalg.norm(m[0]) - 1.0) < 1e-3   # unit vectors


def test_rate_limit_is_retried_with_backoff_not_fatal(monkeypatch=None):
    with tempfile.TemporaryDirectory() as d:
        st = es.EmbedStore(Path(d))
        c = FakeClient(fail_first=2)
        slept = []
        es.time.sleep = lambda s: slept.append(s)
        assert st.ensure([("a", "x")], client=c) == 1
        assert len(c.calls) == 3 and slept == [es.RATE_LIMIT_SLEEP_S, 2 * es.RATE_LIMIT_SLEEP_S]


def test_is_rate_limit_matches_429_and_resource_exhausted():
    assert es.is_rate_limit(RuntimeError("429 Too Many Requests"))
    assert es.is_rate_limit(RuntimeError("ResourceExhausted: quota"))
    assert not es.is_rate_limit(RuntimeError("400 invalid argument"))


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for f in fns:
        try:
            f(); print(f"  ✓ {f.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1; print(f"  ✗ {f.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns)-bad}/{len(fns)} pass"); sys.exit(1 if bad else 0)
