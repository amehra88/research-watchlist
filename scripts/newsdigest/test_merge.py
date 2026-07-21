"""
Test the two-stage event-merge (Lever 1): fragments of ONE event collapse, distinct events of the SAME
company stay separate (the over-merge risk), blocks are per-ticker, and a merged cluster keeps all items
(volume goes up).

No pytest in this env — run directly:  python3 scripts/newsdigest/test_merge.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import merge  # noqa: E402


class FakeCluster:
    """Duck-typed stand-in for cluster.Cluster with the attrs merge reads/mutates."""
    def __init__(self, title, source, ticker):
        self.items = [{"title": title, "source": source, "ticker": ticker, "_is_factset": False}]
        self.tokens = set(title.lower().split())

    @property
    def headline(self):
        return self.items[0]["title"]

    @property
    def sources(self):
        return {it["source"] for it in self.items if it.get("source")}

    @property
    def volume(self):
        return len(self.sources)


TN = {"005930.KS": "Samsung Electronics", "NVDA": "NVIDIA", "TSM": "Taiwan Semiconductor"}


def test_event_fragments_merge():
    """Reworded fragments of the SAME event (Samsung robotics division) collapse to one cluster."""
    cs = [
        FakeCluster("Samsung Electronics Formalizes Robotics as a Key Strategic Growth Division", "A", "005930.KS"),
        FakeCluster("Samsung forms dedicated robotics division in strategic pivot", "B", "005930.KS"),
        FakeCluster("Samsung Electronics Launches Dedicated Robotics Division with Expansion Plans", "C", "005930.KS"),
    ]
    out = merge.merge_clusters(cs, TN, logger=None)
    assert len(out) == 1, f"3 robotics fragments must merge to 1, got {len(out)}"
    assert out[0].volume == 3, f"merged cluster keeps all 3 sources (volume up), got {out[0].volume}"
    assert len(out[0].items) == 3, "merged cluster keeps all items"
    print(f"  ✓ 3 event-fragments → 1 cluster, volume 1→{out[0].volume} (corroboration up)")


def test_distinct_same_ticker_events_stay_separate():
    """Distinct events of the SAME company must NOT merge — the over-merge failure mode. Name-stripping
    leaves {robotics,division} vs {cuts,jobs,us} vs {galaxy,credit,card} with ~zero overlap."""
    cs = [
        FakeCluster("Samsung Electronics Formalizes Robotics as a Growth Division", "A", "005930.KS"),
        FakeCluster("Samsung Cuts Hundreds of Jobs in US Consumer Electronics Division", "B", "005930.KS"),
        FakeCluster("Samsung Launches Galaxy Credit Card With Cashback", "C", "005930.KS"),
    ]
    out = merge.merge_clusters(cs, TN, logger=None)
    assert len(out) == 3, f"3 distinct Samsung events must stay separate, got {len(out)} (over-merge!)"
    print("  ✓ 3 DISTINCT same-ticker events stay separate (no over-merge)")


def test_blocks_are_per_ticker():
    """Two clusters that happen to share content words but sit in different ticker blocks don't merge."""
    cs = [
        FakeCluster("NVIDIA reports strong quarterly growth in data center", "A", "NVDA"),
        FakeCluster("Taiwan Semiconductor reports strong quarterly growth in data center", "B", "TSM"),
    ]
    out = merge.merge_clusters(cs, TN, logger=None)
    assert len(out) == 2, f"different ticker blocks must not merge, got {len(out)}"
    print("  ✓ different ticker blocks never merge")


def test_no_spurious_merge_of_singletons():
    """A pool of unrelated single stories passes through unchanged."""
    cs = [
        FakeCluster("NVIDIA unveils new Vera CPU architecture", "A", "NVDA"),
        FakeCluster("NVIDIA faces China export control questions", "B", "NVDA"),
        FakeCluster("Taiwan Semiconductor raises capex guidance", "C", "TSM"),
    ]
    out = merge.merge_clusters(cs, TN, logger=None)
    assert len(out) == 3, f"unrelated stories must not merge, got {len(out)}"
    print("  ✓ unrelated stories pass through unchanged")


if __name__ == "__main__":
    for fn in (test_event_fragments_merge, test_distinct_same_ticker_events_stay_separate,
               test_blocks_are_per_ticker, test_no_spurious_merge_of_singletons):
        fn()
    print("\nALL PASS — event-merge collapses fragments, preserves distinct events.")
