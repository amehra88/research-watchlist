"""
Unit tests for scripts/portal/__init__.py's REPO constant (RIS5 A6, A5
carry-forward C2's sibling fix).

REPO used to be hardcoded to Path("/root/research-watchlist") -- the main
checkout -- so every consumer that reads REPO-derived paths (e.g.
state_bundles.Paths().valuation_state) silently pointed at the main
checkout's (possibly empty/stale) state/ even when build_portal.py was run
from a worktree. RIS5 A5's live valuation run wrote a 161-ticker
state/valuation/expectations_latest.json in THIS worktree, and
`build_portal.py --dry-run` still reported `valuation_tickers: 0` because of
this exact trap (see task-5-report.md's "3. build_portal.py --dry-run"
section). This test pins REPO to `__file__`-derived resolution so that
regresses loudly.

No pytest in this env -- run directly:
    python3 scripts/portal/test_init.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # scripts/, so "portal" resolves as a package
import portal as _pkg  # noqa: E402  (scripts/portal/, loaded as the "portal" package)


def _expected_repo_root() -> Path:
    # scripts/portal/__init__.py -> scripts/portal -> scripts -> repo root
    return Path(__file__).resolve().parents[2]


def test_repo_is_derived_from_file_not_hardcoded():
    assert _pkg.REPO == _expected_repo_root(), (
        f"REPO={_pkg.REPO!r} but this file's own repo root is "
        f"{_expected_repo_root()!r} -- REPO must track __file__, not a hardcoded string"
    )


def test_repo_matches_this_checkout_exactly():
    # Whichever checkout this test runs from (main checkout or a worktree),
    # REPO must resolve to THAT checkout, not always the main one.
    assert str(_pkg.REPO) == str(Path(__file__).resolve().parents[2])


def test_repo_is_this_worktree_when_run_from_worktree():
    # Regression guard for the exact bug: when this file lives under
    # .claude/worktrees/<name>, REPO must NOT collapse to the bare
    # "/root/research-watchlist" main checkout.
    here = Path(__file__).resolve()
    if ".claude/worktrees/" in str(here):
        assert str(_pkg.REPO) != "/root/research-watchlist", (
            "REPO fell back to the main checkout even though this test is "
            "running from a worktree -- the __file__-derived fix regressed"
        )


def test_build_portal_dry_run_reports_nonzero_valuation_tickers():
    # End-to-end guard matching the brief's own verification step: from
    # THIS checkout, build_portal.py --dry-run must report the real
    # valuation ticker count (161 as of the A5 fix-round-4 live run), not 0.
    repo = _expected_repo_root()
    valuation_latest = repo / "state" / "valuation" / "expectations_latest.json"
    if not valuation_latest.is_file():
        print("  (skip: no state/valuation/expectations_latest.json in this checkout)")
        return
    result = subprocess.run(
        [sys.executable, str(repo / "scripts" / "portal" / "build_portal.py"), "--dry-run"],
        cwd=str(repo), capture_output=True, text=True, timeout=120,
    )
    combined = result.stdout + result.stderr
    assert "valuation_tickers" in combined, combined[-4000:]
    assert "valuation_tickers: 0" not in combined, combined[-4000:]


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
