"""
Unit tests for scripts/portal/identity.py (RIS4 slice 2, Task 2).

Fixtures in fixtures/identity/ are trimmed copies of config/watchlist.yaml and
config/ticker_identity.yaml (plus a small backfill.json and a tiny notes/ tree).
Tests run ONLY against these fixtures, never the live vault/config at
/root/research-watchlist — every helper here takes explicit path overrides so
identity.py's own zero-arg REPO-backed defaults are never exercised in tests.

No pytest in this env — run directly:
    python3 scripts/portal/test_identity.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identity as idm  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "identity"
WATCHLIST = FIXTURES / "watchlist.yaml"
IDENTITY = FIXTURES / "ticker_identity.yaml"
BACKFILL = FIXTURES / "backfill.json"
NOTES = FIXTURES / "notes"


# ───────────────────────── load_universe() ─────────────────────────

def _universe():
    return idm.load_universe(watchlist_path=WATCHLIST, notes_dir=NOTES)


def _by_ticker(entries, ticker):
    return next(e for e in entries if e["ticker"] == ticker)


def test_load_universe_dual_listed_first_tier_wins():
    e = _by_ticker(_universe(), "DUAL")
    assert e["tier"] == "tier_2_active_candidates", e
    assert e["also_in"] == ["tier_3_watchlist"], e
    assert e["themes"] == ["theme_dual_t2"], e


def test_load_universe_scores_present_when_scoring_block_exists():
    e = _by_ticker(_universe(), "FOO")
    assert e["tier"] == "tier_1_bctk"
    assert "scores" in e, e
    assert e["scores"]["ai_positioning"]["score"] == "5"
    assert e["scores"]["competitive_advantage"]["overall"] == "4"
    assert e["scores"]["potential_investor_interest"]["score"] == "4"


def test_load_universe_no_scores_key_for_unscored_entry():
    e = _by_ticker(_universe(), "BAZ")
    assert e["tier"] == "tier_3_watchlist"
    assert "scores" not in e, e
    assert "also_in" not in e, e


def test_load_universe_pvt_id_in_tier1():
    e = _by_ticker(_universe(), "simaai.pvt")
    assert e["tier"] == "tier_1_bctk"
    assert e["themes"] == ["theme_pvt"]


def test_load_universe_orphan_notes_ticker():
    e = _by_ticker(_universe(), "ORPHAN")
    assert e["tier"] == "none", e
    assert e["orphan_notes"] is True, e
    assert e["themes"] == [], e


def test_load_universe_notes_dir_ticker_already_in_watchlist_not_duplicated():
    entries = _universe()
    matches = [e for e in entries if e["ticker"] == "FOO"]
    assert len(matches) == 1, matches
    assert "orphan_notes" not in matches[0], matches[0]


def test_load_universe_excludes_non_ticker_top_dirs():
    tickers = {e["ticker"] for e in _universe()}
    assert "themes" not in tickers
    assert "inbox" not in tickers


def test_load_universe_no_notes_dir_still_works():
    # notes_dir pointing at an empty tmp dir must not blow up, and orphan detection
    # simply finds nothing.
    with tempfile.TemporaryDirectory() as td:
        entries = idm.load_universe(watchlist_path=WATCHLIST, notes_dir=Path(td))
    tickers = {e["ticker"] for e in entries}
    assert "ORPHAN" not in tickers
    assert "FOO" in tickers


# ───────────────────────── display_names() / missing_names() ─────────────────────────

def _names():
    return idm.display_names(watchlist_path=WATCHLIST, identity_path=IDENTITY,
                              backfill_path=BACKFILL, notes_dir=NOTES)


def test_display_names_identity_wins_over_backfill():
    # backfill.json also has a "FOO" entry; ticker_identity.yaml must win.
    assert _names()["FOO"] == "Foo Corporation"


def test_display_names_private_driver_by_pvt_id():
    assert _names()["testdriver.pvt"] == "TestDriver"


def test_display_names_tier4_by_id():
    assert _names()["acme.cn"] == "Acme Components"


def test_display_names_backfill_fills_gap():
    assert _names()["BAR"] == "Bar Incorporated"
    assert _names()["BAZ"] == "Baz Company"


def test_display_names_bare_ticker_fallback():
    # DUAL has no identity/private/tier4/backfill entry in the fixtures.
    assert _names()["DUAL"] == "DUAL"


def test_missing_names_reflects_uncovered_domain():
    missing = idm.missing_names(watchlist_path=WATCHLIST, identity_path=IDENTITY,
                                 backfill_path=BACKFILL, notes_dir=NOTES)
    assert "DUAL" in missing, missing
    assert "ORPHAN" in missing, missing
    assert "FOO" not in missing, missing
    assert "BAR" not in missing, missing
    assert "acme.cn" not in missing, missing
    assert "testdriver.pvt" not in missing, missing


# ───────────────────────── factset_ids() ─────────────────────────

def test_factset_ids_uses_id_maps_and_config_default():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "config").mkdir()
        (repo / "config" / "ticker_identity.yaml").write_text(
            'FOO:\n  name: "Foo Corporation"\n  factset_id: "FOO-XX"\n  google: \'"Foo" stock\'\n'
        )
        orig_repo = idm.ingest_metrics.REPO
        idm.ingest_metrics.REPO = repo
        try:
            ids = idm.factset_ids(["FOO", "ZORK"])
        finally:
            idm.ingest_metrics.REPO = orig_repo
    assert ids["FOO"] == "FOO-XX", ids          # explicit override in ticker_identity.yaml
    assert ids["ZORK"] == "ZORK-US", ids        # id_maps default


# ───────────────────────── _skip_from_yaml_write() ─────────────────────────

def test_skip_from_yaml_write_plain_ticker_not_skipped():
    assert idm._skip_from_yaml_write("AAON") is False


def test_skip_from_yaml_write_pvt_skipped():
    assert idm._skip_from_yaml_write("simaai.pvt") is True


def test_skip_from_yaml_write_digit_id_skipped():
    assert idm._skip_from_yaml_write("A000660") is True


def test_skip_from_yaml_write_dotted_foreign_ticker_skipped():
    assert idm._skip_from_yaml_write("UMG.AS") is True
    assert idm._skip_from_yaml_write("2308.TW") is True


# ───────────────────────── merge_names() dry run ─────────────────────────

def test_merge_names_dry_run_selects_correct_tickers_and_does_not_write():
    before = IDENTITY.read_text(encoding="utf-8")
    block, added = idm.merge_names(BACKFILL, identity_path=IDENTITY, write=False)
    assert added == ["BAR", "BAZ"], added   # FOO already present; A00FOO/simaai.pvt skipped
    assert "BAR:" in block and "BAZ:" in block
    assert "FOO:" not in block
    assert "A00FOO" not in block
    assert "simaai.pvt" not in block
    assert IDENTITY.read_text(encoding="utf-8") == before, "dry run must not touch the file"


def test_merge_names_block_format_is_exact():
    with tempfile.TemporaryDirectory() as td:
        ident_path = Path(td) / "ticker_identity.yaml"
        ident_path.write_text('FOO:\n  name: "Foo Corporation"\n')
        json_path = Path(td) / "backfill.json"
        json_path.write_text(json.dumps({"as_of": "2026-09-15", "source": "unit test",
                                          "names": {"BAR": "Bar Incorporated"}}))
        block, added = idm.merge_names(json_path, identity_path=ident_path, write=False)
    assert added == ["BAR"]
    expected = (
        "# ---- portal name backfill 2026-09-15 (source: unit test) ----\n"
        "BAR:\n"
        '  name: "Bar Incorporated"\n'
        '  factset_id: "BAR-US"          # per id_maps default; foreign tickers keep their existing mapping if any\n'
        "  google: '\"Bar Incorporated\" OR BAR stock'\n"
    )
    assert block == expected, block


def test_merge_names_no_new_tickers_returns_empty():
    with tempfile.TemporaryDirectory() as td:
        ident_path = Path(td) / "ticker_identity.yaml"
        ident_path.write_text('FOO:\n  name: "Foo Corporation"\n')
        json_path = Path(td) / "backfill.json"
        json_path.write_text(json.dumps({"as_of": "2026-09-15", "source": "unit test",
                                          "names": {"FOO": "Foo Corporation"}}))
        block, added = idm.merge_names(json_path, identity_path=ident_path, write=False)
    assert block == "" and added == []


# ───────────────────────── merge_names() --write ─────────────────────────

def _tmp_identity_copy():
    td = tempfile.mkdtemp()
    ident_path = Path(td) / "ticker_identity.yaml"
    shutil.copy(IDENTITY, ident_path)
    return td, ident_path


def test_merge_names_write_appends_and_preserves_comments_and_existing_keys():
    td, ident_path = _tmp_identity_copy()
    try:
        before_text = ident_path.read_text(encoding="utf-8")
        block, added = idm.merge_names(BACKFILL, identity_path=ident_path, write=True)
        assert added == ["BAR", "BAZ"]
        after_text = ident_path.read_text(encoding="utf-8")
        assert after_text.startswith(before_text.rstrip("\n")), "must only append, never rewrite"
        assert "# config/ticker_identity.yaml fixture" in after_text
        assert "comments survive an append" in after_text
        parsed = idm.yaml.safe_load(after_text)
        assert parsed["FOO"] == {"name": "Foo Corporation", "factset_id": "FOO-US",
                                  "google": '"Foo Corporation" OR FOO stock'}
        assert parsed["BAR"]["name"] == "Bar Incorporated"
        assert parsed["BAR"]["factset_id"] == "BAR-US"
        assert parsed["BAZ"]["name"] == "Baz Company"

        # idempotency: second run appends nothing further.
        block2, added2 = idm.merge_names(BACKFILL, identity_path=ident_path, write=True)
        assert added2 == [] and block2 == ""
        assert ident_path.read_text(encoding="utf-8") == after_text
    finally:
        shutil.rmtree(td)


def test_merge_names_write_refuses_and_leaves_file_untouched_on_key_loss():
    td, ident_path = _tmp_identity_copy()
    try:
        before_text = ident_path.read_text(encoding="utf-8")
        # A duplicate top-level "FOO:" key silently overwrites the original mapping
        # under YAML's last-key-wins rule -- this is the "loses a pre-existing key"
        # case the merge must detect and refuse.
        bad_addition = "FOO:\n  name: null\n"
        try:
            idm._safe_append(ident_path, bad_addition)
            assert False, "expected MergeAbortedError"
        except idm.MergeAbortedError:
            pass
        assert ident_path.read_text(encoding="utf-8") == before_text, "file must be untouched on abort"
    finally:
        shutil.rmtree(td)


def test_safe_append_refuses_on_parse_failure():
    td, ident_path = _tmp_identity_copy()
    try:
        before_text = ident_path.read_text(encoding="utf-8")
        bad_addition = "QUX: [unterminated\n"
        try:
            idm._safe_append(ident_path, bad_addition)
            assert False, "expected MergeAbortedError"
        except idm.MergeAbortedError:
            pass
        assert ident_path.read_text(encoding="utf-8") == before_text
    finally:
        shutil.rmtree(td)


# ───────────────────────── CLI ─────────────────────────

def _tmp_repo_from_fixtures():
    """A REPO-shaped tmp tree so main()'s zero-arg (REPO-based) defaults can be
    exercised against fixture content, by monkeypatching idm.REPO for the duration
    of one call -- mirrors how test_factset_ids_* monkeypatches ingest_metrics.REPO.
    """
    td = Path(tempfile.mkdtemp())
    (td / "config").mkdir(parents=True)
    shutil.copy(WATCHLIST, td / "config" / "watchlist.yaml")
    shutil.copy(IDENTITY, td / "config" / "ticker_identity.yaml")
    fixtures_dir = td / "scripts" / "portal" / "fixtures"
    fixtures_dir.mkdir(parents=True)
    shutil.copy(BACKFILL, fixtures_dir / "names_backfill_20260915.json")
    shutil.copytree(NOTES, td / "notes")
    return td


def test_main_merge_names_dry_run_prints_block_and_count():
    td = _tmp_repo_from_fixtures()
    orig_repo = idm.REPO
    idm.REPO = td
    try:
        before = (td / "config" / "ticker_identity.yaml").read_text(encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = idm.main(["--merge-names", str(td / "scripts" / "portal" / "fixtures"
                                                  / "names_backfill_20260915.json")])
        out = buf.getvalue()
        assert rc == 0
        assert "BAR:" in out and "BAZ:" in out
        assert "2 entries" in out
        assert "would append" in out
        # dry run: no --write, so the fixture file must be unchanged.
        assert (td / "config" / "ticker_identity.yaml").read_text(encoding="utf-8") == before
    finally:
        idm.REPO = orig_repo
        shutil.rmtree(td)


def test_main_missing_flag():
    td = _tmp_repo_from_fixtures()
    orig_repo = idm.REPO
    idm.REPO = td
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = idm.main(["--missing"])
        out = buf.getvalue()
        assert rc == 0
        assert "DUAL" in out
        assert "ORPHAN" in out
    finally:
        idm.REPO = orig_repo
        shutil.rmtree(td)


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
