"""Run directly: python3 scripts/thesis/test_theme_polarity.py  (hermetic: tmp fixture files)"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import theme_polarity as TP  # noqa: E402

REAL_POLARITY = Path(__file__).resolve().parents[2] / "config" / "theme_polarity.yaml"
REAL_WATCHLIST = Path(__file__).resolve().parents[2] / "config" / "watchlist.yaml"


def _write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return p


def test_load_real_files_every_watchlist_slug_covered():
    # Exercises the actual worktree config/ files (explicit paths -- REPO points at the
    # main checkout, not this worktree, so the module's own defaults must not be used here).
    pol = TP.load(REAL_POLARITY, REAL_WATCHLIST)
    slugs = TP.watchlist_theme_slugs(REAL_WATCHLIST)
    assert set(pol) == slugs and len(slugs) == 72
    assert all(v in (-1, 0, 1) for v in pol.values())
    assert pol["ai_inference_margin_compression"] == -1 and pol["software_seat_pricing_pressure"] == -1
    assert pol["chip_design_competition"] == 0            # competition slug -> 0
    assert pol["ad_market_strength"] == 1                  # clearly positive demand label


def test_bearish_themes_is_exactly_the_minus_one_set():
    bearish = TP.bearish_themes(REAL_POLARITY, REAL_WATCHLIST)
    assert bearish == {"ai_inference_margin_compression", "software_seat_pricing_pressure"}


def test_bullish_themes_nonempty_and_disjoint_from_bearish():
    bullish = TP.bullish_themes(REAL_POLARITY, REAL_WATCHLIST)
    bearish = TP.bearish_themes(REAL_POLARITY, REAL_WATCHLIST)
    assert bullish and not (bullish & bearish)


def test_load_fails_loud_on_missing_slug():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n    - b_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 1\n")   # b_slug missing
        try:
            TP.load(pol, wl)
            raise AssertionError("expected ValueError for missing slug")
        except ValueError as e:
            assert "b_slug" in str(e)


def test_load_fails_loud_on_bad_value():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 2\n")   # not in {-1,0,1}
        try:
            TP.load(pol, wl)
            raise AssertionError("expected ValueError for bad value")
        except ValueError as e:
            assert "a_slug" in str(e)


def test_extra_slug_in_polarity_file_is_tolerated_but_not_returned():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: -1\nretired_slug: 1\n")
        out = TP.load(pol, wl)
        assert out == {"a_slug": -1}


if __name__ == "__main__":
    test_load_real_files_every_watchlist_slug_covered()
    test_bearish_themes_is_exactly_the_minus_one_set()
    test_bullish_themes_nonempty_and_disjoint_from_bearish()
    test_load_fails_loud_on_missing_slug()
    test_load_fails_loud_on_bad_value()
    test_extra_slug_in_polarity_file_is_tolerated_but_not_returned()
    print("OK test_theme_polarity")
