"""
Unit tests for topic_map (spec §4.2 — the shared topic vocabulary).

Embeddings are FAKED here. The real path is Gemini gemini-embedding-001 via
scripts/chunking/embed.py; a unit test must not spend API calls or need a key.

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_topic_map.py
"""
import math
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_map as tm  # noqa: E402

WATCHLIST = """
themes:
  demand:
    - ai_infrastructure_capex
    - china_ai_infrastructure_demand
  supply:
    - optical_component_supply
  strategic:
    - space_supply_chain
"""


def test_load_themes_flattens_every_group():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "watchlist.yaml"
        p.write_text(WATCHLIST)
        got = tm.load_themes(p)
        assert got == sorted([
            "ai_infrastructure_capex", "china_ai_infrastructure_demand",
            "optical_component_supply", "space_supply_chain"])


def test_load_themes_does_not_hardcode_a_count():
    """The spec says 61; space_supply_chain made it 62 and it will move
    again. Count at runtime, never in source."""
    src = Path(tm.__file__).read_text()
    assert " 61" not in src and "== 61" not in src


def test_anchor_text_turns_a_slug_into_a_phrase():
    assert tm.anchor_text("china_ai_infrastructure_demand") == \
        "china ai infrastructure demand"


def test_cosine_is_one_for_identical_and_zero_for_orthogonal():
    assert math.isclose(tm.cosine([1.0, 0.0], [1.0, 0.0]), 1.0, abs_tol=1e-9)
    assert math.isclose(tm.cosine([1.0, 0.0], [0.0, 1.0]), 0.0, abs_tol=1e-9)


def test_cosine_handles_a_zero_vector_without_dividing_by_zero():
    assert tm.cosine([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_assign_inherits_the_nearest_theme_above_threshold():
    anchors = ["ai_infrastructure_capex", "optical_component_supply"]
    anchor_vecs = [[1.0, 0.0], [0.0, 1.0]]
    phrases = [[0.99, 0.14]]                 # clearly the first anchor
    got = tm.assign(phrases, anchor_vecs, anchors, threshold=0.7)
    assert got[0][0] == "ai_infrastructure_capex"
    assert got[0][1] > 0.7


def test_assign_returns_none_below_threshold_as_a_new_theme_candidate():
    """Below threshold is the whole point: it is how the vocabulary grows
    (spec §4.2 step 4) instead of forcing everything into 62 boxes."""
    anchors = ["ai_infrastructure_capex"]
    anchor_vecs = [[1.0, 0.0]]
    phrases = [[0.0, 1.0]]
    got = tm.assign(phrases, anchor_vecs, anchors, threshold=0.7)
    assert got[0][0] is None
    assert got[0][1] < 0.7, "the near-miss score must still be reported"


import json  # noqa: E402  (appended with the Task 4 tests)


def test_assign_refuses_a_coin_flip_between_two_anchors():
    """Findings 2026-08-21 R2. Unrelated MD&A prose lands on an arbitrary theme
    by a hair — convertible notes scored 0.689 against ai_generated_content.
    When best and second-best are within min_margin the assignment is noise, so
    it becomes a candidate rather than silently inflating a theme's count."""
    anchors = ["ai_infrastructure_capex", "optical_component_supply"]
    anchor_vecs = [[1.0, 0.0], [0.9999, 0.0141]]     # nearly identical anchors
    phrases = [[1.0, 0.0]]
    theme, sim = tm.assign(phrases, anchor_vecs, anchors,
                           threshold=0.5, min_margin=0.02)[0]
    assert theme is None, f"coin flip must not inherit, got {theme}"
    assert sim > 0.5, "the score is still reported for operator review"
    # with the margin disabled the same input does inherit
    assert tm.assign(phrases, anchor_vecs, anchors, threshold=0.5,
                     min_margin=0.0)[0][0] == "ai_infrastructure_capex"


def test_assign_margin_is_not_applied_when_there_is_one_anchor():
    got = tm.assign([[1.0, 0.0]], [[1.0, 0.0]], ["only_theme"],
                    threshold=0.5, min_margin=0.02)
    assert got[0][0] == "only_theme"


def test_iter_question_units_keeps_only_analyst_speech():
    """The question side is analysts. corprep speech is the company talking
    about itself — that is evidence, and it arrives via claims.jsonl."""
    rows = [
        {"vector_id": "v1", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "analyst", "speaker_firm": "Wolfe Research LLC",
         "text": "I wanted to ask about the Chinese transceivers and the ramp"},
        {"vector_id": "v2", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "corprep", "speaker_firm": None, "text": "Thanks"},
        {"vector_id": "v3", "ticker": "AAOI", "event_date": "2026-08-06",
         "speaker_type": "operator", "speaker_firm": None, "text": "Next"},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exchanges.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows))
        got = list(tm.iter_question_units(p))
        assert [u["unit_id"] for u in got] == ["v1"]
        assert got[0]["register"] == "question"
        assert got[0]["speaker_firm"] == "Wolfe Research LLC"
        assert got[0]["period_key"] == "2026Q3"


def test_iter_question_units_ignores_a_fiscal_period_label():
    """53.1% of the real corpus shifts quarter when derived from event_date
    instead of the stored label. Preferring period_key — as the plan's draft
    did — silently misaligns the two registers."""
    row = {"vector_id": "v9", "ticker": "LITE", "event_date": "2026-08-11",
           "period_key": "2026Q4", "period_basis": "fiscal",
           "speaker_type": "analyst", "speaker_firm": "Mizuho",
           "text": "How should we think about laser capacity into next year"}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exchanges.jsonl"
        p.write_text(json.dumps(row))
        got = list(tm.iter_question_units(p))
        assert got[0]["period_key"] == "2026Q3", got[0]["period_key"]


def test_iter_evidence_units_reads_claims_and_carries_the_clock():
    rows = [{"claim_id": "c1", "ticker": "ADI", "period_key": "2026Q3",
             "first_evidence_date": "2026-08-19",
             "text": "we qualified a second source for high power lasers "
                     "during the quarter across the interconnect family"}]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"
        p.write_text(json.dumps(rows[0]))
        got = list(tm.iter_evidence_units(p))
        assert got[0]["unit_id"] == "c1"
        assert got[0]["register"] == "evidence"
        assert got[0]["speaker_firm"] is None
        assert got[0]["first_evidence_date"] == "2026-08-19"


def test_is_housekeeping_drops_accounting_prose_but_keeps_capex():
    """Findings 2026-08-21 R1. This prose appears in EVERY filer, so
    MIN_CANDIDATE_COMPANIES cannot filter it — it has to go before extraction.
    The capex case is the one that must survive: it scored 0.805 against
    ai_infrastructure_capex and is exactly the signal we want."""
    drop = [
        "As of March 31, 2026, our total minimum lease payments was $152.3 "
        "million, of which $18.7 million is due in the following twelve months",
        "On March 6, 2026, we issued $170.5 million aggregate principal amount "
        "of our 4.00% convertible senior notes which are due in March 2031",
        "The funded status of our pension plans is dependent upon actuarial "
        "assumptions and interest rates at year-end and prior investment return",
        "Our corporate website is located at www.mongodb.com and we make "
        "available free of charge our annual and quarterly reports",
    ]
    for t in drop:
        assert tm.is_housekeeping(t), t[:60]

    keep = [
        "During the three months ended March 31, 2026 cash paid for property "
        "and equipment was $7.7 billion and we expect capital expenditures to "
        "increase substantially to support demand for AI services",
        "Data Center net revenue of $16.6 billion in 2025 increased by 32% "
        "driven by demand for our accelerated computing platforms",
        "We began qualifying a second source for high-power lasers during the "
        "quarter and expect meaningful datacenter interconnect volume",
    ]
    for t in keep:
        assert not tm.is_housekeeping(t), t[:60]


def test_iter_evidence_units_applies_the_housekeeping_filter():
    rows = [
        {"claim_id": "c1", "ticker": "ADI", "period_key": "2026Q3",
         "first_evidence_date": "2026-08-19",
         "text": "Our effective tax rate for the three months ended March 31 "
                 "was negative nineteen percent compared with prior year"},
        {"claim_id": "c2", "ticker": "ADI", "period_key": "2026Q3",
         "first_evidence_date": "2026-08-19",
         "text": "Demand across the industrial and automotive end markets rose "
                 "with particular strength in datacenter power conversion"},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows))
        assert [u["unit_id"] for u in tm.iter_evidence_units(p)] == ["c2"]


def test_parse_phrases_reads_a_json_array_from_the_envelope():
    env = {"is_error": False, "result": '["chinese transceiver competition", '
                                        '"800g ramp timing"]'}
    phrases, status = tm.parse_phrases(env)
    assert status == "ok"
    assert phrases == ["chinese transceiver competition", "800g ramp timing"]


def test_parse_phrases_reports_failed_not_empty_on_a_bad_envelope():
    """empty is answered-and-done; failed is unknown-and-retried. Conflating
    them is the b1c351aa lesson."""
    _, status = tm.parse_phrases({"is_error": True, "result": "boom"})
    assert status.startswith("failed"), status


def test_parse_phrases_treats_an_empty_array_as_answered():
    phrases, status = tm.parse_phrases({"is_error": False, "result": "[]"})
    assert phrases == []
    assert status == "empty"


def test_is_limit_cliff_matches_the_2026_08_11_signature():
    """267 pages died this way: instant return, one turn, zero cost. Detecting
    it is the difference between a resumable pause and an hour of burnt clock."""
    assert tm.is_limit_cliff({"is_error": True, "duration_api_ms": 0,
                              "num_turns": 1, "total_cost_usd": 0})
    assert not tm.is_limit_cliff({"is_error": True, "duration_api_ms": 3507,
                                  "num_turns": 2, "total_cost_usd": 0.07})
    assert not tm.is_limit_cliff({"is_error": False, "duration_api_ms": 0,
                                  "num_turns": 1, "total_cost_usd": 0})


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
