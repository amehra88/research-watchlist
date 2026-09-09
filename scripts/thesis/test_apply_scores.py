"""Run directly: python3 scripts/thesis/test_apply_scores.py"""
import sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import apply_scores as A  # noqa: E402

SAMPLE = """tier_1_bctk:
  - ticker: COHR
    themes: [a, b]
    ai_positioning:
      score: "4"
      notes: "n"
    competitive_advantage:
      innovation_rate: "4"
      distribution: "4"   # comment
      overall: "4"
    potential_investor_interest:
      score: "4"
      notes: "n"
  - ticker: ZZZ
    ai_positioning: "3"
    competitive_advantage:
      innovation_rate: "3"
    potential_investor_interest: "2"
tier_3_watchlist:
  - ticker: COHR
    themes: [a]
"""


def test_patch_nested_and_inline_forms():
    t = A.patch_text(SAMPLE, "COHR", "potential_investor_interest.score", "4+")
    t = A.patch_text(t, "COHR", "competitive_advantage.distribution", "5")
    t = A.patch_text(t, "ZZZ", "ai_positioning", "3+")
    d = yaml.safe_load(t)
    assert d["tier_1_bctk"][0]["potential_investor_interest"]["score"] == "4+"
    assert d["tier_1_bctk"][0]["competitive_advantage"]["distribution"] == "5" and "# comment" in t
    assert d["tier_1_bctk"][1]["ai_positioning"] == "3+"
    assert d["tier_3_watchlist"][0] == {"ticker": "COHR", "themes": ["a"]}          # T3 block untouched
    assert t.count("\n") == SAMPLE.count("\n")                                     # formatting preserved


def test_patch_errors():
    for args in (("NOPE", "ai_positioning", "4"), ("ZZZ", "competitive_advantage.overall", "4")):
        try:
            A.patch_text(SAMPLE, *args); assert False, args
        except A.PatchError:
            pass


if __name__ == "__main__":
    test_patch_nested_and_inline_forms(); test_patch_errors()
    print("OK test_apply_scores")
