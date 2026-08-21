"""
Unit tests for mdna_evidence (spec §4.4 — the US evidence side).

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_mdna_evidence.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mdna_evidence as me  # noqa: E402

NOTE = """---
doc_type: sec_filing
ticker: ADI
form_type: 10-Q
filed_date: '2026-08-19'
themes:
- semiconductor_cycle
---

# ADI 10-Q — filed 2026-08-19

## Item 2. Management's Discussion and Analysis

Revenue increased forty percent driven by demand across the industrial and
automotive end markets, with particular strength in datacenter power.
"""

NOTE_NO_MDNA = """---
doc_type: sec_filing
ticker: ADI
form_type: 8-K
filed_date: '2026-08-19'
---

# ADI 8-K — filed 2026-08-19

## Item 2.02 Results of Operations

Press release furnished herewith.
"""


def _write(d, name, body):
    p = Path(d) / name
    p.write_text(body)
    return p


def test_parse_note_extracts_frontmatter_and_mdna_body():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "2026-08-19-ADI-10-Q-2-3.md", NOTE)
        got = me.parse_note(p)
        assert got["ticker"] == "ADI"
        assert got["filed_date"] == "2026-08-19"
        assert got["form_type"] == "10-Q"
        assert "Revenue increased forty percent" in got["mdna"]
        assert "doc_type" not in got["mdna"], "frontmatter must not leak in"


def test_parse_note_returns_none_without_an_mdna_section():
    """8-Ks dominate the SEC corpus (spec §1.2). They carry no MD&A and must
    be skipped silently rather than producing empty claims."""
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "2026-08-19-ADI-8-K-2.02.md", NOTE_NO_MDNA)
        assert me.parse_note(p) is None


def test_split_blocks_treats_each_line_as_a_paragraph():
    """The notes/sec/ writer emits one paragraph per line and essentially no
    blank lines. Splitting on blank lines instead collapsed a 40,888-char MD&A
    into two blocks — a blob that carries every topic at once and so carries
    none. Sampling 1,200 notes found 0 laid out in blank-line paragraphs."""
    real_shape = (
        "Industry Conditions\n"
        "Coherent is a global leader in photonic technology, which is "
        "foundational to the performance and scalability of AI datacenters "
        "and critical to many industrial and communications end markets.\n"
        "Agreements with NVIDIA\n"
        "On March 2, 2026, the Company entered into a multi-year strategic "
        "agreement with NVIDIA to advance the development of advanced optics "
        "technologies for accelerated computing platforms.\n")
    blocks = me.split_blocks(real_shape)
    assert len(blocks) == 4, f"one block per line, got {len(blocks)}"
    # the two short sub-headings are dropped at the min_words gate, not here
    kept = me.added_blocks("", real_shape)
    assert len(kept) == 2
    assert all("NVIDIA" in b or "photonic" in b for b in kept)


def test_parse_note_does_not_leak_the_tail_of_the_heading():
    """The heading regex stops at "Discussion"; the rest of the real heading
    ("and Analysis of Financial Condition...") must not open the body."""
    note = NOTE.replace(
        "## Item 2. Management's Discussion and Analysis",
        "## Item 2. Management's Discussion and Analysis of Financial "
        "Condition and Results of Operations")
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "2026-08-19-ADI-10-Q-2-3.md", note)
        got = me.parse_note(p)
        assert not got["mdna"].startswith("and Analysis"), got["mdna"][:60]
        assert got["mdna"].startswith("Revenue increased forty percent")


def test_added_blocks_suppresses_unchanged_boilerplate():
    """The regression that matters: safe-harbor text is byte-identical QoQ and
    must never surface as new evidence."""
    boiler = ("This report contains forward-looking statements subject to the "
              "safe harbor created under the Private Securities Litigation "
              "Reform Act of 1995 and other safe harbors, and actual results "
              "could differ materially from those anticipated herein for many "
              "reasons including the risk factors described in Item 1A.")
    prev = boiler
    curr = boiler + "\n\n" + (
        "We began qualifying a second source for high-power lasers during the "
        "quarter, and we now expect that supplier to carry a meaningful share "
        "of datacenter interconnect volume in the coming fiscal year.")
    got = me.added_blocks(prev, curr)
    assert len(got) == 1, f"expected only the new block, got {len(got)}"
    assert "second source for high-power lasers" in got[0]
    assert "safe harbor" not in got[0]


def test_added_blocks_drops_short_fragments():
    """Table rows and page numbers survive the diff as noise. A claim needs
    enough prose to carry a topic."""
    got = me.added_blocks("alpha beta", "alpha beta\n\n17\n\nRevenue $ 4,021")
    assert got == []


def test_added_blocks_treats_a_renumbered_paragraph_as_a_restatement():
    """The near-duplicate guard. Most MD&A paragraphs return each quarter with
    the figures updated; that is a restatement, not a new disclosure. Guards
    the fast upper-bound gating in added_blocks — real_quick_ratio and
    quick_ratio bound ratio from above, so they must not change any verdict."""
    base = ("Revenue for the quarter was {} million, an increase driven by "
            "continued demand across the industrial and automotive end "
            "markets and by particular strength in datacenter power "
            "conversion products sold into hyperscale customers.")
    assert me.added_blocks(base.format("4021"), base.format("4022")) == []
    # ... while a genuinely different paragraph of similar length survives.
    other = ("We began qualifying a second source for high-power lasers "
             "during the quarter and expect that supplier to carry a "
             "meaningful share of datacenter interconnect volume during the "
             "coming fiscal year as capacity is brought online.")
    assert me.added_blocks(base.format("4021"), other) == [other]


def test_claims_for_ticker_orders_by_filed_date_and_sets_the_clock():
    notes = [
        {"ticker": "ADI", "filed_date": "2026-08-19", "form_type": "10-Q",
         "document_id": "notes/sec/b.md", "mdna": "shared prose here. " * 5 +
         "We qualified a second laser source this quarter across our "
         "datacenter interconnect product family and expect volume."},
        {"ticker": "ADI", "filed_date": "2026-05-14", "form_type": "10-Q",
         "document_id": "notes/sec/a.md", "mdna": "shared prose here. " * 5},
    ]
    claims = me.claims_for_ticker(notes)
    assert len(claims) == 1
    c = claims[0]
    assert c["first_evidence_date"] == "2026-08-19", "clock = the LATER filing"
    assert c["document_id"] == "notes/sec/b.md"
    assert c["period_key"] == "2026Q3"
    assert c["source"] == "mdna"
    assert c["affects"] == ["ADI"]
    assert c["verified"] is False


def test_window_start_walks_back_whole_months():
    import datetime as dt
    assert me.window_start(9, dt.date(2026, 8, 21)) == "2025-11-21"
    assert me.window_start(9, dt.date(2026, 3, 31)) == "2025-06-30", \
        "day must clamp into a 30-day month"
    assert me.window_start(0, dt.date(2026, 8, 21)) == "2026-08-21"


def test_claims_for_ticker_window_reads_the_prior_filing_but_never_emits_it():
    """The filing before the window is the diff BASELINE. Drop it and the
    first in-window quarter has nothing to diff against, so it dumps its whole
    MD&A — the exact flood the window is meant to prevent."""
    shared = "shared prose here. " * 12
    notes = [
        {"ticker": "ADI", "filed_date": "2025-05-14", "form_type": "10-Q",
         "document_id": "notes/sec/old.md",
         "mdna": shared + "Pre-window sentence about legacy analog demand "
                          "that should never reach the claims file at all."},
        {"ticker": "ADI", "filed_date": "2026-05-06", "form_type": "10-Q",
         "document_id": "notes/sec/in.md",
         "mdna": shared + "We qualified a second laser source this quarter "
                          "across the datacenter interconnect family and "
                          "expect meaningful volume next year."},
    ]
    claims = me.claims_for_ticker(notes, since="2025-11-21")
    assert len(claims) == 1
    assert claims[0]["document_id"] == "notes/sec/in.md"
    assert "second laser source" in claims[0]["text"]
    # and with no window both pairs are eligible, but there is still only one
    assert len(me.claims_for_ticker(notes)) == 1


def test_claims_for_ticker_emits_nothing_for_a_single_filing():
    """With one filing there is no prior to diff against, so there is no
    'newly said' — emitting the whole MD&A would flood the evidence side."""
    notes = [{"ticker": "ADI", "filed_date": "2026-08-19", "form_type": "10-Q",
              "document_id": "notes/sec/b.md", "mdna": "prose " * 60}]
    assert me.claims_for_ticker(notes) == []


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
