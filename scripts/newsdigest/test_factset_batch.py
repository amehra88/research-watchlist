"""
Test the batched FactSet pull: chunking, the saturation split, one-item-per-document, and
multi-ticker attribution.

Why this exists: the pull used to fire one `claude -p` per ticker per run (~87 sessions x 3 runs
= ~800 calls, ~8M billed tokens/day — 93% of all news-pipeline spend), because each session
re-sent the system prompt plus the FactSet MCP tool schemas to carry a ~500-token payload. The
`ids` argument accepts up to 100 identifiers, and a live A/B showed the batched call is LOSSLESS
(AAPL alone returned exactly the same three documentIDs it got inside a 10-ticker batch; the
binding constraint is the similarity threshold, not `limit`). So Python now chunks the universe
and the model never decides how to paginate.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_factset_batch.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import factset_news                                    # noqa: E402
from newsdigest.identity import Identity                               # noqa: E402

PASS = 0
FAIL = 0


def ck(label, got, want):
    global PASS, FAIL
    if got == want:
        print(f"  ✓ {label}")
        PASS += 1
    else:
        print(f"  ✗ {label}\n      got:  {got!r}\n      want: {want!r}")
        FAIL += 1


def idents(*tickers):
    return [Identity(t, f"{t} Inc", f"{t}-US", f"{t} query") for t in tickers]


def doc(doc_id, ids, headline=None):
    """A FactSet_UnstructuredContent result element, in the tool's real response shape."""
    return {
        "documentID": doc_id,
        "headline": headline or f"headline for {doc_id}",
        "sentiment": "Neutral",
        "source": "SA",
        "storyDateTime": "2026-08-14T07:24:18",
        "viewUrl": f"https://example.invalid/{doc_id}",
        "ids": ids,
    }


class Recorder:
    """Stands in for the claude -p subprocess. Records the id-chunks it was asked for and
    replays a scripted response per chunk, so tests assert on real call structure, not a mock."""

    def __init__(self, responses=None, default=()):
        self.responses = responses or {}
        self.default = list(default)
        self.calls = []

    def __call__(self, ids, window_hours, limit):
        key = tuple(sorted(ids))
        self.calls.append(list(ids))
        if key in self.responses:
            r = self.responses[key]
            if isinstance(r, Exception):
                raise r
            return list(r), "ok"
        return list(self.default), "ok"


# ── 1. chunking ────────────────────────────────────────────────────────────────
print("chunking")
rec = Recorder()
factset_news.fetch_batch(idents(*[f"T{i}" for i in range(70)]), 24, rec, chunk_size=30)
ck("70 tickers at chunk_size=30 -> 3 chunks", len(rec.calls), 3)
ck("chunk sizes are 30/30/10", [len(c) for c in rec.calls], [30, 30, 10])
ck("every ticker queried exactly once",
   sorted(i for c in rec.calls for i in c), sorted(f"T{i}-US" for i in range(70)))

rec = Recorder()
factset_news.fetch_batch(idents("AAPL"), 24, rec, chunk_size=30)
ck("a single ticker still makes exactly one call", len(rec.calls), 1)

rec = Recorder()
factset_news.fetch_batch([], 24, rec, chunk_size=30)
ck("empty universe makes zero claude -p calls", len(rec.calls), 0)

# ── 2. saturation split ────────────────────────────────────────────────────────
# A chunk returning exactly `limit` docs may have been truncated, so Python splits it and
# re-queries each half. This is the guard that keeps batching lossless without asking the
# model to paginate.
print("\nsaturation split")
big = [doc(f"d{i}", ["A-US"]) for i in range(5)]
rec = Recorder(responses={("A-US", "B-US"): big}, default=[doc("x", ["A-US"])])
factset_news.fetch_batch(idents("A", "B"), 24, rec, chunk_size=2, limit=5)
ck("saturated chunk is split and re-queried", len(rec.calls), 3)
ck("the split halves are single ids", [len(c) for c in rec.calls[1:]], [1, 1])

rec = Recorder(responses={("A-US", "B-US"): big[:4]})
factset_news.fetch_batch(idents("A", "B"), 24, rec, chunk_size=2, limit=5)
ck("an unsaturated chunk is NOT split", len(rec.calls), 1)

# a single saturated id cannot be split further — must not recurse forever
rec = Recorder(responses={("A-US",): big})
factset_news.fetch_batch(idents("A"), 24, rec, chunk_size=1, limit=5)
ck("a saturated single id terminates instead of recursing", len(rec.calls), 1)

# ── 3. one item per document ───────────────────────────────────────────────────
print("\none item per document")
shared = doc("sa_1", ["AAPL-US", "GOOGL-US"], "Apple and Google both named")
rec = Recorder(responses={
    ("AAPL-US",): [shared],
    ("GOOGL-US",): [shared],
})
docs, _ = factset_news.fetch_batch(idents("AAPL", "GOOGL"), 24, rec, chunk_size=1)
ck("a story naming two tickers is emitted ONCE", len(docs), 1)
ck("its documentID is preserved", docs[0]["documentID"], "sa_1")

rec = Recorder(responses={("AAPL-US", "GOOGL-US"): [shared, shared]})
docs, _ = factset_news.fetch_batch(idents("AAPL", "GOOGL"), 24, rec, chunk_size=30)
ck("a duplicate inside one response is collapsed", len(docs), 1)

# ── 4. multi-ticker attribution ────────────────────────────────────────────────
# The response carries the real id list per document, so a story lands on every watchlist
# ticker it names — and on no others.
print("\nmulti-ticker attribution")
rec = Recorder(responses={("AAPL-US", "GOOGL-US"): [
    doc("sa_2", ["AAPL-US", "GOOGL-US", "9988-HK", "NYT-US"]),
]})
docs, _ = factset_news.fetch_batch(idents("AAPL", "GOOGL"), 24, rec, chunk_size=30)
ck("watchlist tickers are attributed", docs[0]["tickers"], ["AAPL", "GOOGL"])
ck("off-watchlist ids are dropped", [t for t in docs[0]["tickers"] if "-" in t], [])

rec = Recorder(responses={("AAPL-US",): [doc("sa_3", ["9988-HK"])]})
docs, _ = factset_news.fetch_batch(idents("AAPL"), 24, rec, chunk_size=30)
ck("a doc naming no watchlist ticker is dropped entirely", docs, [])

# ── 5. failure isolation ───────────────────────────────────────────────────────
# Batching widens the blast radius: one bad chunk used to cost one ticker, now it costs 30.
# A failed chunk must fall back to per-ticker calls for that chunk ONLY.
print("\nfailure isolation")
boom = RuntimeError("connector attach failed")
rec = Recorder(responses={
    ("A-US", "B-US"): boom,
    ("A-US",): [doc("d_a", ["A-US"])],
    ("B-US",): [doc("d_b", ["B-US"])],
    ("C-US", "D-US"): [doc("d_c", ["C-US"])],
})
docs, statuses = factset_news.fetch_batch(idents("A", "B", "C", "D"), 24, rec, chunk_size=2)
ck("failed chunk falls back to per-ticker", sorted(d["documentID"] for d in docs),
   ["d_a", "d_b", "d_c"])
ck("the healthy chunk is not retried", rec.calls.count(["C-US", "D-US"]), 1)

rec = Recorder(responses={("A-US", "B-US"): boom, ("A-US",): boom, ("B-US",): boom})
docs, statuses = factset_news.fetch_batch(idents("A", "B"), 24, rec, chunk_size=2)
ck("total failure returns no docs rather than raising", docs, [])
ck("total failure is reported per ticker", sorted(statuses), ["A", "B"])

print(f"\nPASS={PASS} FAIL={FAIL}")
sys.exit(1 if FAIL else 0)
