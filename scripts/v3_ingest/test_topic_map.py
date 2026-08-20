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
