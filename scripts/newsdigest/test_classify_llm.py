"""
Deterministic proof that the classifier NEVER silently drops a cluster (regression test for
the 2026-07-08 timeout-drop defect: a timed-out batch became silent DROPs, undercounting the
news pool by 40 clusters).

No pytest in this env — run directly:  python3 scripts/newsdigest/test_classify_llm.py

`_run_claude` is stubbed so no real claude -p / network is touched. The stub decides success
vs. TimeoutExpired purely from the number of clusters in the prompt, letting us force the
exact failure modes (oversized-batch timeout, total unavailability, partial response) and
assert the invariant: every input cluster is either classified or explicitly UNCLASSIFIED —
never silently missing.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import classify_llm  # noqa: E402


class FakeCluster:
    """Duck-typed stand-in for cluster.Cluster — only the attrs the prompt/classifier read."""
    def __init__(self, i):
        self.hash = f"{i:016x}"
        self._title = f"Test headline number {i}"
        self.items = [{"title": self._title}]
        self.sources = ["TestWire"]
        self.volume = 1
        self.representative = {"title": self._title}


MACRO_CFG = {"categories": [{"name": "fed_policy", "description": "rates"},
                            {"name": "growth", "description": "gdp"}]}
TICKER_NAMES = {"NVDA": "NVIDIA", "AMD": "Advanced Micro Devices"}
VALID_THEMES = {"semiconductor_cycle", "ai_infrastructure_capex"}


def make_stub(timeout_above=None, drop_last=False, calls_counter=None):
    """Return a fake _run_claude. Times out when the prompt carries > timeout_above clusters;
    otherwise emits one verdict per cluster (optionally omitting the last → partial response)."""
    def _stub(prompt, repo_root, timeout=classify_llm.CLAUDE_TIMEOUT_S):
        if calls_counter is not None:
            calls_counter.append(len(re.findall(r"cluster_id: ([0-9a-f]+)", prompt)))
        cids = re.findall(r"cluster_id: ([0-9a-f]+)", prompt)
        if timeout_above is not None and len(cids) > timeout_above:
            raise subprocess.TimeoutExpired(cmd="claude", timeout=timeout)
        emit = cids[:-1] if (drop_last and len(cids) > 1) else cids
        arr = [{"cluster_id": c, "materiality": ["NVDA"], "themes": [], "macro": [],
                "confidence": "high", "rationale": "stub"} for c in emit]
        return json.dumps(arr), 0.001
    return _stub


def make_session_limit_stub(calls_counter=None):
    """Return a fake _run_claude that always raises SessionLimitError — the persistent-429
    (quota exhausted) case. Counts calls so the test can assert fast-abort (no retry/split)."""
    def _stub(prompt, repo_root, timeout=classify_llm.CLAUDE_TIMEOUT_S):
        if calls_counter is not None:
            calls_counter.append(len(re.findall(r"cluster_id: ([0-9a-f]+)", prompt)))
        raise classify_llm.SessionLimitError("resets 8:30am (America/New_York)")
    return _stub


def _run(clusters, batch_size, stub):
    orig = classify_llm._run_claude
    classify_llm._run_claude = stub
    classify_llm.time.sleep = lambda *_a, **_k: None  # no real backoff sleeps in tests
    try:
        return classify_llm.classify_clusters(
            clusters, MACRO_CFG, TICKER_NAMES, VALID_THEMES, "/tmp",
            batch_size=batch_size, logger=None)
    finally:
        classify_llm._run_claude = orig


def test_no_drop_on_oversized_batch_timeout():
    """A batch that times out at size 20 must split until sub-batches succeed — 0 dropped."""
    clusters = [FakeCluster(i) for i in range(30)]
    calls = []
    out, cost, unclassified = _run(clusters, 20, make_stub(timeout_above=10, calls_counter=calls))
    got = set(out) | set(unclassified)
    assert got == {c.hash for c in clusters}, "every cluster must be accounted for"
    assert unclassified == [], f"nothing should be unclassified, got {unclassified}"
    assert len(out) == 30, f"all 30 classified, got {len(out)}"
    # split must have fired: batch[0:20] timed out (1 call) → 10/10 (2 calls) → batch[20:30] (1 call)
    assert len(calls) >= 4, f"split did not fire (only {len(calls)} calls)"
    print(f"  ✓ oversized-batch timeout → split → 30/30 classified, 0 dropped ({len(calls)} calls)")


def test_total_unavailability_is_unclassified_not_dropped():
    """If EVERY call times out (even single clusters), clusters land in UNCLASSIFIED, not silently gone."""
    clusters = [FakeCluster(i) for i in range(5)]
    out, cost, unclassified = _run(clusters, 20, make_stub(timeout_above=0))
    assert out == {}, f"nothing classifiable, got {len(out)}"
    assert set(unclassified) == {c.hash for c in clusters}, "all 5 must be flagged UNCLASSIFIED"
    print(f"  ✓ total claude -p failure → 5/5 flagged UNCLASSIFIED (fail-loud), 0 silently dropped")


def test_partial_response_recovers_missing():
    """When the model omits clusters from an otherwise-valid response, the missing subset is recovered."""
    clusters = [FakeCluster(i) for i in range(6)]
    out, cost, unclassified = _run(clusters, 6, make_stub(timeout_above=None, drop_last=True))
    got = set(out) | set(unclassified)
    assert got == {c.hash for c in clusters}, "every cluster accounted for"
    assert unclassified == [], f"partial responses must be recovered, got unclassified={unclassified}"
    assert len(out) == 6, f"all 6 recovered, got {len(out)}"
    print(f"  ✓ partial response (model omits one) → missing subset recovered, 6/6 classified")


def test_clean_run_all_classified():
    """Baseline: when nothing fails, every cluster is classified in one pass per batch."""
    clusters = [FakeCluster(i) for i in range(45)]
    calls = []
    out, cost, unclassified = _run(clusters, 20, make_stub(timeout_above=None, calls_counter=calls))
    assert len(out) == 45 and unclassified == [], "clean run must classify all"
    assert len(calls) == 3, f"45 clusters / batch 20 = 3 calls, got {len(calls)}"
    assert abs(cost - 0.003) < 1e-9, f"cost accumulates per call, got {cost}"
    print(f"  ✓ clean run → 45/45 classified in {len(calls)} calls, cost=${cost:.4f}")


def test_persistent_429_fast_abort_no_split():
    """A session-limit 429 must ABORT fast: no retry, no split. Every cluster lands in
    UNCLASSIFIED (fail-loud), and exactly ONE claude -p call is made — proving we do NOT
    storm the drained quota (the 2026-07-20 pathology). Regression for the 429 fast-abort."""
    clusters = [FakeCluster(i) for i in range(30)]
    calls = []
    out, cost, unclassified = _run(clusters, 20, make_session_limit_stub(calls_counter=calls))
    assert out == {}, f"nothing classifiable under a session limit, got {len(out)}"
    assert set(unclassified) == {c.hash for c in clusters}, "all 30 must be UNCLASSIFIED (fail-loud)"
    assert len(calls) == 1, f"429 must fast-abort after ONE call (no retry/split), got {len(calls)}"
    assert cost == 0.0, f"a failed 429 call accrues no cost, got {cost}"
    print(f"  ✓ persistent 429 → fast-abort in {len(calls)} call, 30/30 UNCLASSIFIED, 0 split, non-zero-exit signal")



def test_precheck_maps_429_through_claude_p_wrapper():
    """The 429 precheck must survive the move onto scripts/lib/claude_p.py.

    Every OTHER 429 test in this file stubs `_run_claude` itself and raises
    SessionLimitError directly, so none of them touch `_precheck_session_limit` — they
    would all still pass if the precheck were wired up wrongly (or not at all). This
    test goes through the real `_run_claude` -> `claude_p.run` path with only the
    subprocess faked, which is the only way to prove the wiring.

    The distinction is load-bearing: a quota 429 must raise the NON-RETRYABLE
    SessionLimitError. If it degrades to RuntimeError, the recovery ladder treats it as
    transient and re-sends the batch, burning quota that is already exhausted.
    """
    import claude_p

    class _FakeCompleted:
        def __init__(self, stdout, returncode):
            self.stdout, self.returncode, self.stderr = stdout, returncode, ""

    # The two shapes a subscription 429 actually arrives in.
    cases = [
        # Text must carry a phrase _SESSION_LIMIT_RE actually matches ("session limit" /
        # "usage limit"). An is_error envelope WITHOUT one is a different failure and is
        # correctly a generic RuntimeError — asserting otherwise just tests a bad fixture.
        ("rc!=0", _FakeCompleted(
            '{"is_error":true,"result":"Claude usage limit reached; resets 4pm"}', 1)),
        ("api_error_status 429", _FakeCompleted(
            '{"is_error":true,"api_error_status":429,"result":"resets 4pm"}', 0)),
    ]
    orig = claude_p.subprocess.run
    try:
        for label, fake in cases:
            claude_p.subprocess.run = lambda *a, **k: fake
            try:
                classify_llm._run_claude("prompt", ".", timeout=5)
            except classify_llm.SessionLimitError:
                pass                      # correct
            except Exception as e:        # noqa: BLE001 — any other type is the bug
                raise AssertionError(
                    f"{label}: 429 raised {type(e).__name__}, not SessionLimitError — the "
                    f"precheck is not wired through claude_p.run, so the retry ladder "
                    f"would re-send an exhausted batch") from e
            else:
                raise AssertionError(f"{label}: 429 raised nothing at all")
    finally:
        claude_p.subprocess.run = orig
    print("  \u2713 429 -> SessionLimitError through the real claude_p.run precheck (both envelope shapes)")


if __name__ == "__main__":
    for fn in (test_clean_run_all_classified,
               test_no_drop_on_oversized_batch_timeout,
               test_total_unavailability_is_unclassified_not_dropped,
               test_partial_response_recovers_missing,
               test_persistent_429_fast_abort_no_split,
               test_precheck_maps_429_through_claude_p_wrapper):
        fn()
    print("\nALL PASS — no-silent-drop invariant holds (incl. 429 fast-abort).")
