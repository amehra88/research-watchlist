"""
Tests for what a FAILED news_digest run must NOT do.

Both invariants here were violated live on 2026-08-21, when the 06:45 run hit a session-limit 429
on its first classify call:
  • it marked 558 stories "surfaced" in the dedup ledger while delivering zero, which would have
    suppressed them from the next run's pool — losing them from the digest AND from pg;
  • it emailed a 0-story digest carrying nothing but warning banners, on top of the failure alert
    the non-zero exit already sends.

Neither is about cost; both are about not losing stories and not adding noise to an outage.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_failure_paths.py
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import news_digest as nd  # noqa: E402

NOW = datetime(2026, 8, 21, 10, 45, tzinfo=timezone.utc)


class FakeCluster:
    def __init__(self, h, items):
        self.hash = h
        self.items = items


def _item(h, ticker="NVDA"):
    return {"_h": h, "ticker": ticker, "title": f"story {h}", "source": "Src", "published": NOW}


_judged_hashes = nd.judged_item_hashes      # the real implementation, not a copy of it


def test_total_classify_failure_marks_nothing():
    """The 2026-08-21 case: 0 verdicts must mark 0 items, so the next run can retry them."""
    clusters = [FakeCluster(f"c{i}", [_item(f"h{i}")]) for i in range(300)]
    classifications = {}                       # 429 on the first call — nothing classified
    judged = _judged_hashes(clusters, classifications)
    assert judged == set(), f"a run that classified nothing marked {len(judged)} items surfaced"
    print("  ✓ 0 verdicts → 0 ledger marks (the 558-story regression cannot recur)")


def test_partial_failure_marks_only_the_judged():
    """A partial run must mark what it judged and leave the rest available."""
    clusters = [FakeCluster(f"c{i}", [_item(f"h{i}")]) for i in range(10)]
    classifications = {f"c{i}": object() for i in range(4)}      # 4 of 10 classified
    judged = _judged_hashes(clusters, classifications)
    assert judged == {f"h{i}" for i in range(4)}, judged
    print(f"  ✓ partial run marks only the {len(judged)} judged item(s), 6 stay retryable")


def test_merged_cluster_marks_all_its_items():
    """Event-merge folds several clusters into one; a verdict covers every item it absorbed."""
    merged = FakeCluster("m1", [_item("a"), _item("b"), _item("c")])
    judged = _judged_hashes([merged], {"m1": object()})
    assert judged == {"a", "b", "c"}, judged
    print("  ✓ a verdict on a merged cluster marks all items it absorbed")


def test_empty_digest_suppressed_only_when_the_run_failed():
    """Emptiness is a FINDING on a healthy run (send it) and a FAILURE otherwise (suppress)."""
    should_send = nd.should_send_email       # the real implementation, not a copy of it

    # the 2026-08-21 run: nothing classified, nothing delivered → no email
    assert not should_send([], list(range(300)), [], True)
    # a genuinely quiet but HEALTHY run → still email; "nothing cleared the bar" is information
    assert should_send([], [], [], True)
    # partial failures that still produced stories → email, banners carry the caveat
    assert should_send([1, 2, 3], [4], [], True)
    assert should_send([1], [], [2], True)
    assert should_send([1], [], [], False)
    print("  ✓ empty digest suppressed only when empty == failure; quiet-but-healthy still sends")


if __name__ == "__main__":
    for fn in (test_total_classify_failure_marks_nothing,
               test_partial_failure_marks_only_the_judged,
               test_merged_cluster_marks_all_its_items,
               test_empty_digest_suppressed_only_when_the_run_failed):
        fn()
    print("\nALL PASS — a failed run loses no stories and sends no empty email.")
