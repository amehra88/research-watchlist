"""Tests for scripts/check.py's theme-polarity coverage assertion (RIS5 Part A
pre-merge fix 1). Run directly: python3 scripts/test_check.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check as C  # noqa: E402


def _write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return p


def test_matching_fixture_has_no_issues():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n    - b_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 1\nb_slug: 0\ncompetition_slugs:\n  - b_slug\n")
        assert C.theme_polarity_issues(wl, pol) == []


def test_flags_watchlist_slug_missing_from_polarity():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n    - b_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 1\n")  # b_slug missing
        issues = C.theme_polarity_issues(wl, pol)
        assert issues and "b_slug" in issues[0], issues


def test_flags_non_slug_competition_slugs_entry():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wl = _write(tmp, "watchlist.yaml", "themes:\n  demand:\n    - a_slug\n")
        pol = _write(tmp, "polarity.yaml", "a_slug: 0\ncompetition_slugs:\n  - a_slug\n  - not_a_real_slug\n")
        issues = C.theme_polarity_issues(wl, pol)
        assert any("not_a_real_slug" in i for i in issues), issues


def test_noop_when_watchlist_missing():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        assert C.theme_polarity_issues(tmp / "no-watchlist.yaml", tmp / "no-polarity.yaml") == []


def test_real_repo_config_has_zero_issues():
    """The assertion must pass on the actual worktree config -- this is what
    `python3 scripts/check.py` exercises for real."""
    issues = C.theme_polarity_issues(C.ROOT / "config" / "watchlist.yaml", C.ROOT / "config" / "theme_polarity.yaml")
    assert issues == [], issues


if __name__ == "__main__":
    test_matching_fixture_has_no_issues()
    test_flags_watchlist_slug_missing_from_polarity()
    test_flags_non_slug_competition_slugs_entry()
    test_noop_when_watchlist_missing()
    test_real_repo_config_has_zero_issues()
    print("OK test_check")
