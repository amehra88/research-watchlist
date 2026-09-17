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


def test_pricing_power_in_shortage_is_plus_one():
    # RIS5 A4 fix round 1: watchlist.yaml lines 100-102 document this as a bullish
    # value-capture theme (suppliers raising prices while demand outruns supply) per its
    # own 2026-09-10 provenance comment -- despite living in the margins_pricing family, it
    # is NOT a challenge/bearish signal, so it's +1, not 0 or -1.
    pol = TP.load(REAL_POLARITY, REAL_WATCHLIST)
    assert pol["pricing_power_in_shortage"] == 1
    assert "pricing_power_in_shortage" in TP.bullish_themes(REAL_POLARITY, REAL_WATCHLIST)
    assert "pricing_power_in_shortage" not in TP.bearish_themes(REAL_POLARITY, REAL_WATCHLIST)


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


def test_competition_slugs_real_file_all_polarity_zero():
    # RIS5 A4 fix 0: competition_slugs is a separate, additive list -- every entry stays
    # polarity 0 in the main mapping (rule 2: a competition theme firing is two-sided).
    comp = TP.competition_slugs(REAL_POLARITY, REAL_WATCHLIST)
    pol = TP.load(REAL_POLARITY, REAL_WATCHLIST)
    assert comp and comp <= set(pol)                       # every entry is a real watchlist slug
    assert all(pol[s] == 0 for s in comp)
    assert "hbm_competitive_landscape" in comp and "platform_take_rate" in comp
    assert TP.COMPETITION_KEY not in pol   # the reserved key itself never leaks into load()'s returned mapping


def test_competition_slugs_fails_loud_on_non_watchlist_entry():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 0\ncompetition_slugs:\n  - a_slug\n  - not_a_real_slug\n")
        try:
            TP.competition_slugs(pol, wl)
            raise AssertionError("expected ValueError for a non-watchlist competition_slugs entry")
        except ValueError as e:
            assert "not_a_real_slug" in str(e)


def test_competition_slugs_fails_loud_on_non_list_value():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 0\ncompetition_slugs: a_slug\n")
        try:
            TP.competition_slugs(pol, wl)
            raise AssertionError("expected ValueError for a non-list competition_slugs value")
        except ValueError as e:
            assert "list" in str(e)


def test_competition_slugs_empty_when_key_absent():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 0\n")   # no competition_slugs key at all
        assert TP.competition_slugs(pol, wl) == set()


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
    test_pricing_power_in_shortage_is_plus_one()
    test_load_fails_loud_on_missing_slug()
    test_load_fails_loud_on_bad_value()
    test_competition_slugs_real_file_all_polarity_zero()
    test_competition_slugs_fails_loud_on_non_watchlist_entry()
    test_competition_slugs_fails_loud_on_non_list_value()
    test_competition_slugs_empty_when_key_absent()
    test_extra_slug_in_polarity_file_is_tolerated_but_not_returned()
    print("OK test_theme_polarity")
