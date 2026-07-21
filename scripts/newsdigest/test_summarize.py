"""
Deterministic proof that the summarizer NEVER silently drops a survivor and FAST-ABORTS on a
session-limit 429 (regression for the 2026-07-21 defect: under quota exhaustion the summarizer
caught the 429 as a generic per-batch WARNING and plowed all ~13 batches into the drained quota
07:46→07:48, degrading the digest silently instead of stopping).

No pytest in this env — run directly:  python3 scripts/newsdigest/test_summarize.py

`_run_claude` is stubbed so no real claude -p / network is touched. The stub decides success vs.
SessionLimitError vs. a generic failure purely from the prompt / call count, letting us force the
exact modes and assert the invariant: every survivor is either summarized or explicitly returned in
`unsummarized` (fail-loud) — never silently missing — and a 429 stops after ONE call.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import summarize                      # noqa: E402
from newsdigest.classify_llm import SessionLimitError  # noqa: E402


class FakeCluster:
    """Duck-typed stand-in for cluster.Cluster — only the attrs the summarizer prompt reads."""
    def __init__(self, i):
        self.hash = f"{i:016x}"
        self._title = f"Test survivor headline number {i}"
        self.items = [{"title": self._title}]
        self.sources = ["TestWire"]
        self.volume = 1

    # summarize._story_block reads getattr(c, "_fa_sentiment", None); default absent is fine.


class FakeCls:
    """Duck-typed stand-in for classify_llm.Classification (the tags the summarizer echoes)."""
    materiality = ["NVDA"]
    themes = []
    macro = []
    confidence = "high"
    rationale = "stub"


def _survivors(n):
    return [(FakeCluster(i), FakeCls()) for i in range(n)]


def make_ok_stub(calls_counter=None):
    """Fake _run_claude that summarizes every cluster in the prompt (one Summary each)."""
    def _stub(prompt, repo_root, timeout=None):
        cids = re.findall(r"cluster_id: ([0-9a-f]+)", prompt)
        if calls_counter is not None:
            calls_counter.append(len(cids))
        arr = [{"cluster_id": c, "headline": "H", "bullets": ["b1", "b2", "b3"],
                "lens_tags": ["Company: NVDA"], "why_it_matters": "w"} for c in cids]
        return json.dumps(arr), 0.001
    return _stub


def make_session_limit_stub(calls_counter=None):
    """Fake _run_claude that always raises SessionLimitError — persistent quota exhaustion.
    Counts calls so the test can assert fast-abort (no continue across remaining batches)."""
    def _stub(prompt, repo_root, timeout=None):
        if calls_counter is not None:
            calls_counter.append(len(re.findall(r"cluster_id: ([0-9a-f]+)", prompt)))
        raise SessionLimitError("resets 11:30am (America/New_York)")
    return _stub


def make_second_batch_fails_stub(calls_counter=None):
    """OK on the first batch, generic RuntimeError on every later batch — exercises per-batch
    isolation: the good batch summarizes, the failing batches land in `unsummarized`, run CONTINUES."""
    seen = {"n": 0}

    def _stub(prompt, repo_root, timeout=None):
        cids = re.findall(r"cluster_id: ([0-9a-f]+)", prompt)
        if calls_counter is not None:
            calls_counter.append(len(cids))
        seen["n"] += 1
        if seen["n"] == 1:
            arr = [{"cluster_id": c, "headline": "H", "bullets": ["b1", "b2", "b3"],
                    "lens_tags": [], "why_it_matters": "w"} for c in cids]
            return json.dumps(arr), 0.001
        raise RuntimeError("claude -p rc=1 (generic transient)")
    return _stub


def _run(survivors, batch_size, stub):
    orig = summarize._run_claude
    summarize._run_claude = stub
    try:
        return summarize.summarize_survivors(survivors, "/tmp", batch_size=batch_size, logger=None)
    finally:
        summarize._run_claude = orig


def test_clean_run_all_summarized():
    """Baseline: nothing fails → every survivor summarized, none unsummarized."""
    survivors = _survivors(45)
    calls = []
    out, cost, unsummarized = _run(survivors, 20, make_ok_stub(calls_counter=calls))
    assert len(out) == 45 and unsummarized == [], "clean run must summarize all"
    assert len(calls) == 3, f"45 survivors / batch 20 = 3 calls, got {len(calls)}"
    assert abs(cost - 0.003) < 1e-9, f"cost accumulates per call, got {cost}"
    print(f"  ✓ clean run → 45/45 summarized in {len(calls)} calls, cost=${cost:.4f}")


def test_generic_batch_failure_isolated_not_aborted():
    """A generic (non-429) batch failure leaves ONLY that batch unsummarized and the run CONTINUES —
    per-batch isolation preserved (no fast-abort). Here batch 1 (20) succeeds, batches 2 & 3 fail."""
    survivors = _survivors(45)
    calls = []
    out, cost, unsummarized = _run(survivors, 20, make_second_batch_fails_stub(calls_counter=calls))
    got = set(out) | set(unsummarized)
    assert got == {c.hash for c, _ in survivors}, "every survivor accounted for (summarized or unsummarized)"
    assert len(out) == 20, f"only the first batch summarizes, got {len(out)}"
    assert len(unsummarized) == 25, f"the two failing batches → 25 unsummarized, got {len(unsummarized)}"
    assert len(calls) == 3, f"all 3 batches attempted (isolation, not abort), got {len(calls)} calls"
    print(f"  ✓ generic batch failure → isolated: 20 summarized, 25 unsummarized, all 3 batches tried")


def test_persistent_429_fast_abort_no_continue():
    """A session-limit 429 must ABORT fast: no continue across batches. Every survivor lands in
    `unsummarized` (fail-loud), and exactly ONE claude -p call is made — proving we do NOT storm
    the drained quota (the 2026-07-21 pathology of ~13 doomed batch calls). Regression for the
    summarizer 429 fast-abort."""
    survivors = _survivors(60)          # 3 batches of 20 — a run that WOULD storm without fast-abort
    calls = []
    out, cost, unsummarized = _run(survivors, 20, make_session_limit_stub(calls_counter=calls))
    assert out == {}, f"nothing summarizable under a session limit, got {len(out)}"
    assert set(unsummarized) == {c.hash for c, _ in survivors}, "all 60 must be UNSUMMARIZED (fail-loud)"
    assert len(calls) == 1, f"429 must fast-abort after ONE call (no continue), got {len(calls)}"
    assert cost == 0.0, f"a failed 429 call accrues no cost, got {cost}"
    print(f"  ✓ persistent 429 → fast-abort in {len(calls)} call, 60/60 UNSUMMARIZED, 0 storm, non-zero-exit signal")


if __name__ == "__main__":
    for fn in (test_clean_run_all_summarized,
               test_generic_batch_failure_isolated_not_aborted,
               test_persistent_429_fast_abort_no_continue):
        fn()
    print("\nALL PASS — summarizer no-silent-drop + 429 fast-abort invariant holds.")
