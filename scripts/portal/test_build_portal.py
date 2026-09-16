"""
Unit tests for scripts/portal/budget.py and scripts/portal/build_portal.py
(RIS4 slice 2, Task 6).

Only the REPO-free "atomic build engine" half of build_portal.py is exercised
here (run_stages/build/dry_run/_publish/_copy_app) -- against synthetic
stage lists and tempfile scratch dirs, never against live notes/config/state.
The PRODUCTION stage list (_default_stages(), which wires reports/etf_trades/
vault/identity/search_index/state_bundles together against the live REPO) is
exercised by the real `python3 build_portal.py --out ...` build documented in
the Task 6 report, not by this file -- see build_portal.py's own module
docstring for why that split exists.

No pytest in this env -- run directly:
    python3 scripts/portal/test_build_portal.py
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget          # noqa: E402
import build_portal as bp  # noqa: E402


def _stage(name, write=None, raise_exc=None):
    """A synthetic (name, fn) stage: `write(tmp_dir)` if given, then raise
    RuntimeError(raise_exc) if given, else return {"name": name}.
    """
    def fn(tmp_dir):
        if write is not None:
            write(tmp_dir)
        if raise_exc is not None:
            raise RuntimeError(raise_exc)
        return {"name": name}
    return (name, fn)


def _write(rel: str, content: bytes = b"x"):
    def w(tmp_dir):
        p = tmp_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    return w


def _tmpdir(prefix="bp_test_"):
    return Path(tempfile.mkdtemp(prefix=prefix))


# ───────────────────────── budget.check / budget.table ─────────────────────────

def test_budget_check_clean_tree_has_no_violations():
    td = _tmpdir()
    try:
        (td / "data").mkdir()
        (td / "data" / "a.json").write_text('{"a":1}')
        assert budget.check(td) == []
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_budget_check_flags_too_many_files():
    orig = budget.MAX_FILES
    budget.MAX_FILES = 2
    td = _tmpdir()
    try:
        for i in range(3):
            (td / f"f{i}.json").write_text("{}")
        violations = budget.check(td)
        assert any("files:" in v for v in violations), violations
    finally:
        budget.MAX_FILES = orig
        shutil.rmtree(td, ignore_errors=True)


def test_budget_check_flags_oversized_text_file():
    orig = budget.MAX_TEXT_FILE_BYTES
    budget.MAX_TEXT_FILE_BYTES = 10
    td = _tmpdir()
    try:
        (td / "data").mkdir()
        (td / "data" / "big.json").write_text("x" * 100)
        violations = budget.check(td)
        assert any("data/big.json" in v for v in violations), violations
    finally:
        budget.MAX_TEXT_FILE_BYTES = orig
        shutil.rmtree(td, ignore_errors=True)


def test_budget_check_flags_oversized_index_html_even_under_the_text_cap():
    orig_html, orig_text = budget.MAX_INDEX_HTML_BYTES, budget.MAX_TEXT_FILE_BYTES
    budget.MAX_INDEX_HTML_BYTES = 10
    budget.MAX_TEXT_FILE_BYTES = 10_000  # keep the generic text cap well above this file's size
    td = _tmpdir()
    try:
        (td / "index.html").write_text("<html>way too big for the 1MB-style cap</html>")
        violations = budget.check(td)
        assert any(v.startswith("index.html:") for v in violations), violations
    finally:
        budget.MAX_INDEX_HTML_BYTES, budget.MAX_TEXT_FILE_BYTES = orig_html, orig_text
        shutil.rmtree(td, ignore_errors=True)


def test_budget_check_flags_total_bytes():
    orig = budget.MAX_TOTAL_BYTES
    budget.MAX_TOTAL_BYTES = 5
    td = _tmpdir()
    try:
        (td / "a.json").write_text("0123456789")
        violations = budget.check(td)
        assert any(v.startswith("total:") for v in violations), violations
    finally:
        budget.MAX_TOTAL_BYTES = orig
        shutil.rmtree(td, ignore_errors=True)


def test_budget_table_sorted_desc_and_capped_at_top_n():
    td = _tmpdir()
    try:
        (td / "big.json").write_text("x" * 100)
        (td / "small.json").write_text("x" * 10)
        tbl = budget.table(td, top_n=1)
        rows = [ln for ln in tbl.splitlines()
                if ln.strip() and not ln.startswith("-") and "path" not in ln and "files=" not in ln]
        assert len(rows) == 1, rows
        assert "big.json" in rows[0], rows
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_budget_table_reports_files_and_total_summary_line():
    td = _tmpdir()
    try:
        (td / "a.json").write_text("x" * 10)
        tbl = budget.table(td)
        assert "files=1" in tbl and "total_bytes=10" in tbl, tbl
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── build(): success + stale removal ─────────────────────────

def test_build_publishes_files_and_returns_zero():
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc = bp.build(out_dir, [_stage("a", _write("data/a.json", b'{"a":1}'))])
        assert rc == 0
        assert (out_dir / "data" / "a.json").read_bytes() == b'{"a":1}'
        assert not list(out_dir.glob(".tmp-*")), "no leftover tmp dir after a clean build"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_build_removes_stale_files_no_longer_produced():
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc1 = bp.build(out_dir, [
            _stage("a", _write("data/a.json", b'{"a":1}')),
            _stage("b", _write("data/b.json", b'{"b":1}')),
        ])
        assert rc1 == 0
        assert (out_dir / "data" / "a.json").exists()
        assert (out_dir / "data" / "b.json").exists()

        # second build only produces a.json -- b.json is stale and must be removed
        rc2 = bp.build(out_dir, [_stage("a", _write("data/a.json", b'{"a":2}'))])
        assert rc2 == 0
        assert (out_dir / "data" / "a.json").read_bytes() == b'{"a":2}'
        assert not (out_dir / "data" / "b.json").exists(), "stale file must be removed"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_build_never_removes_unowned_content_outside_owned_paths():
    # fix round 1 (Critical): stale-file removal is scoped to OWNED_PATHS
    # ("data/", "vendor/", "index.html", "app.js", "styles.css"). Anything
    # else already under out_dir -- e.g. an operator-placed smoke/ dir, the
    # real incident that motivated this fix -- must survive every build,
    # whether or not this build's own stages produce anything at all.
    td = _tmpdir()
    out_dir = td / "out"
    try:
        (out_dir / "smoke").mkdir(parents=True)
        (out_dir / "smoke" / "probe.txt").write_text("unrelated Phase 0 artifact")

        rc = bp.build(out_dir, [_stage("a", _write("data/a.json", b'{"a":1}'))])
        assert rc == 0
        assert (out_dir / "smoke" / "probe.txt").read_text() == "unrelated Phase 0 artifact", \
            "unowned content outside OWNED_PATHS must never be touched"
        assert (out_dir / "data" / "a.json").exists()

        # a second build that ALSO doesn't produce anything under smoke/ must still
        # leave it alone (it's not "stale" -- it was never this builder's to own)
        rc2 = bp.build(out_dir, [_stage("a", _write("data/a.json", b'{"a":2}'))])
        assert rc2 == 0
        assert (out_dir / "smoke" / "probe.txt").exists()
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_is_owned_matches_directory_prefixes_and_exact_filenames():
    assert bp._is_owned("data/tickers/NVDA.json")
    assert bp._is_owned("vendor/lib.js")
    assert bp._is_owned("index.html")
    assert bp._is_owned("app.js")
    assert bp._is_owned("styles.css")
    assert not bp._is_owned("smoke/probe.json")
    assert not bp._is_owned("smoke/index.html")
    assert not bp._is_owned("README.md")
    # a prefix-only partial match must not be treated as owned
    assert not bp._is_owned("datafoo.json")
    assert not bp._is_owned("vendorish/x.js")


def test_build_prunes_empty_dirs_only_under_data_or_vendor():
    td = _tmpdir()
    out_dir = td / "out"
    try:
        (out_dir / "smoke" / "empty_sub").mkdir(parents=True)
        rc = bp.build(out_dir, [
            _stage("a", _write("data/sub/a.json", b"{}")),
            _stage("v", _write("vendor/sub/lib.js", b"//")),
        ])
        assert rc == 0
        # now a rebuild that stops producing data/sub/a.json and vendor/sub/lib.js --
        # the now-empty data/sub/ and vendor/sub/ dirs get pruned, smoke/empty_sub/
        # (outside OWNED_PATHS) is left alone even though it's also empty
        rc2 = bp.build(out_dir, [_stage("b", _write("data/b.json", b"{}"))])
        assert rc2 == 0
        assert not (out_dir / "data" / "sub").exists(), "empty data/ subdir should be pruned"
        assert not (out_dir / "vendor").exists(), "empty vendor/ tree should be pruned"
        assert (out_dir / "smoke" / "empty_sub").is_dir(), \
            "empty dirs outside data/ or vendor/ must never be pruned"
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── build(): atomic replace on a failing stage ─────────────────────────

def test_atomic_replace_exception_mid_build_leaves_previous_tree_intact():
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc1 = bp.build(out_dir, [_stage("a", _write("data/a.json", b"good"))])
        assert rc1 == 0
        before = (out_dir / "data" / "a.json").read_bytes()

        rc2 = bp.build(out_dir, [
            _stage("a", _write("data/a.json", b"corrupt-in-progress")),
            _stage("boom", raise_exc="simulated failure"),
        ])
        assert rc2 == 1
        assert (out_dir / "data" / "a.json").read_bytes() == before, \
            "a stage exception must leave the previously-published tree untouched"
        assert not list(out_dir.glob(".tmp-*")), "no leftover tmp dir after a failed build"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_build_on_a_fresh_out_dir_that_immediately_fails_creates_nothing():
    td = _tmpdir()
    out_dir = td / "out"   # does not exist yet
    try:
        rc = bp.build(out_dir, [_stage("boom", raise_exc="fails before writing anything")])
        assert rc == 1
        # out_dir itself may exist (mkdir'd to host the tmp dir) but must be empty
        if out_dir.exists():
            assert list(out_dir.iterdir()) == [], list(out_dir.iterdir())
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── build(): budget breach ─────────────────────────

def test_budget_breach_returns_exit_code_2_and_does_not_publish():
    orig = budget.MAX_TOTAL_BYTES
    budget.MAX_TOTAL_BYTES = 5
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc = bp.build(out_dir, [_stage("small", _write("data/small.json", b"0123456789ABCDE"))])
        assert rc == 2
        assert not (out_dir / "data" / "small.json").exists(), \
            "a budget-violating build must not be published"
        assert not list(out_dir.glob(".tmp-*"))
    finally:
        budget.MAX_TOTAL_BYTES = orig
        shutil.rmtree(td, ignore_errors=True)


def test_budget_breach_leaves_a_prior_good_build_untouched():
    orig = budget.MAX_TOTAL_BYTES
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc1 = bp.build(out_dir, [_stage("a", _write("data/a.json", b"fine"))])
        assert rc1 == 0
        before = (out_dir / "data" / "a.json").read_bytes()

        budget.MAX_TOTAL_BYTES = 1  # now anything at all breaches the cap
        rc2 = bp.build(out_dir, [_stage("a", _write("data/a.json", b"still-fine-but-over-cap"))])
        assert rc2 == 2
        assert (out_dir / "data" / "a.json").read_bytes() == before
    finally:
        budget.MAX_TOTAL_BYTES = orig
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── build(): mid-publish failure (fix round 1, Important) ─────────────────────────

def test_publish_failure_returns_nonzero_and_leaves_no_tmp_dir():
    # Monkeypatch os.replace so the SECOND file it's asked to move raises --
    # simulating a real mid-publish failure (e.g. ENOSPC, a permissions
    # error). build() must catch it, log, discard whatever's left of tmp_dir,
    # and return non-zero rather than reporting success. See _publish()'s own
    # "ATOMICITY NOTE" docstring: the first file may already be live under
    # out_dir at this point -- publishing is atomic per file, not per tree --
    # this test only asserts the process-level contract (exit code, no
    # leftover tmp dir), not that out_dir ends up fully rolled back.
    td = _tmpdir()
    out_dir = td / "out"
    orig_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src, dst):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("simulated mid-publish failure")
        return orig_replace(src, dst)

    try:
        bp.os.replace = flaky_replace
        rc = bp.build(out_dir, [
            _stage("a", _write("data/a.json", b"one")),
            _stage("b", _write("data/b.json", b"two")),
        ])
        assert rc == 1, rc
        assert not list(out_dir.glob(".tmp-*")), "no leftover tmp dir after a publish failure"
    finally:
        bp.os.replace = orig_replace
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── dry_run(): writes nothing ─────────────────────────

def test_dry_run_never_creates_or_touches_out_dir():
    td = _tmpdir()
    out_dir = td / "out"   # bp.dry_run() never even receives this path -- see its own docstring
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = bp.dry_run([_stage("a", _write("data/a.json", b"hello"))])
        assert rc == 0
        assert not out_dir.exists(), "dry-run must never create/touch --out"
        assert "files=1" in buf.getvalue(), buf.getvalue()
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_dry_run_reports_budget_violation_without_writing_out_dir():
    orig = budget.MAX_TOTAL_BYTES
    budget.MAX_TOTAL_BYTES = 1
    td = _tmpdir()
    out_dir = td / "out"
    try:
        rc = bp.dry_run([_stage("a", _write("data/a.json", b"way-over-the-tiny-cap"))])
        assert rc == 2
        assert not out_dir.exists()
    finally:
        budget.MAX_TOTAL_BYTES = orig
        shutil.rmtree(td, ignore_errors=True)


def test_dry_run_leaves_no_scratch_dir_behind():
    before = set(Path(tempfile.gettempdir()).glob("ris4-portal-dry-run-*"))
    bp.dry_run([_stage("a", _write("data/a.json", b"x"))])
    after = set(Path(tempfile.gettempdir()).glob("ris4-portal-dry-run-*"))
    assert after == before, "dry_run's own scratch dir must be cleaned up"


# ───────────────────────── _publish(): concurrent-tmp-dir safety ─────────────────────────

def test_publish_does_not_touch_a_concurrent_tmp_dir():
    td = _tmpdir()
    out_dir = td / "out"
    out_dir.mkdir()
    other_tmp = out_dir / ".tmp-999999"
    other_tmp.mkdir()
    (other_tmp / "scratch.json").write_text("{}")
    try:
        my_tmp = out_dir / ".tmp-123"
        (my_tmp / "data").mkdir(parents=True)
        (my_tmp / "data" / "a.json").write_text('{"a":1}')
        n_pub, n_rm = bp._publish(my_tmp, out_dir)
        assert n_pub == 1 and n_rm == 0
        assert (out_dir / "data" / "a.json").exists()
        assert (other_tmp / "scratch.json").exists(), \
            "must never touch a different pid's in-flight tmp dir"
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── _copy_app() ─────────────────────────

def test_copy_app_copies_top_level_files_and_the_vendor_tree():
    td = _tmpdir()
    try:
        app_src = td / "app_src"
        (app_src / "vendor" / "sub").mkdir(parents=True)
        (app_src / "index.html").write_text("<html></html>")
        (app_src / "styles.css").write_text("body{}")
        (app_src / "app.js").write_text("console.log(1)")
        (app_src / "vendor" / "lib.js").write_text("//lib")
        (app_src / "vendor" / "sub" / "x.css").write_text("/*x*/")

        tmp_dir = td / "tmp_build"
        tmp_dir.mkdir()
        stats = bp._copy_app(tmp_dir, app_src=app_src)
        assert stats == {"copied": 5}, stats
        assert (tmp_dir / "index.html").read_text() == "<html></html>"
        assert (tmp_dir / "vendor" / "lib.js").read_text() == "//lib"
        assert (tmp_dir / "vendor" / "sub" / "x.css").read_text() == "/*x*/"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_copy_app_is_a_clean_noop_when_app_src_is_missing():
    td = _tmpdir()
    try:
        tmp_dir = td / "tmp_build"
        tmp_dir.mkdir()
        stats = bp._copy_app(tmp_dir, app_src=td / "does_not_exist")
        assert stats == {"copied": 0}
        assert list(tmp_dir.iterdir()) == []
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_build_with_app_stage_included_copies_into_published_tree():
    td = _tmpdir()
    out_dir = td / "out"
    app_src = td / "app_src"
    app_src.mkdir()
    (app_src / "index.html").write_text("<html>hi</html>")
    try:
        rc = bp.build(out_dir, [
            _stage("data", _write("data/a.json", b"{}")),
            ("app", lambda tmp_dir: bp._copy_app(tmp_dir, app_src=app_src)),
        ])
        assert rc == 0
        assert (out_dir / "index.html").read_text() == "<html>hi</html>"
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── run_stages(): ordering + stats ─────────────────────────

def test_run_stages_runs_in_order_and_returns_per_stage_stats():
    td = _tmpdir()
    order = []
    try:
        def mk(name):
            def fn(tmp_dir):
                order.append(name)
                return {"n": len(order)}
            return (name, fn)

        stats = bp.run_stages(td, [mk("one"), mk("two"), mk("three")])
        assert order == ["one", "two", "three"]
        assert stats == {"one": {"n": 1}, "two": {"n": 2}, "three": {"n": 3}}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_run_stages_stops_at_the_first_failure():
    td = _tmpdir()
    ran = []
    try:
        def ok(tmp_dir):
            ran.append("ok")
            return {}

        def boom(tmp_dir):
            ran.append("boom")
            raise RuntimeError("nope")

        def never(tmp_dir):
            ran.append("never")
            return {}

        try:
            bp.run_stages(td, [("ok", ok), ("boom", boom), ("never", never)])
            raise AssertionError("expected RuntimeError to propagate")
        except RuntimeError as exc:
            assert str(exc) == "nope"
        assert ran == ["ok", "boom"], ran
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── CLI arg parsing ─────────────────────────

def test_parse_args_defaults_match_the_brief():
    args = bp._parse_args([])
    assert args.format == "json"
    assert args.news_days == 30
    assert args.sec_days == 30
    assert args.reports_days == 14
    assert args.dry_run is False
    assert args.no_app is False
    assert args.out.name == "portal_build"


def test_default_stages_put_the_app_copy_before_state_so_the_manifest_hashes_it():
    # state_bundles.build_state() writes data/manifest.json LAST and hashes
    # whatever is already on disk at that moment -- the app copy must land
    # before it, or index.html/styles.css/app.js/vendor/* would be silently
    # absent from manifest.files forever. _default_stages() does no I/O (the
    # _stage_* factories only build closures), so this is safe to call bare.
    names = [n for n, _ in bp._default_stages(bp._parse_args([]))]
    assert "app" in names and "state" in names, names
    assert names.index("app") < names.index("state"), names
    assert names[-1] == "state", names  # build_state() writes manifest.json LAST


def test_default_stages_omits_the_app_stage_with_no_app():
    names = [n for n, _ in bp._default_stages(bp._parse_args(["--no-app"]))]
    assert "app" not in names, names
    assert names[-1] == "state", names


def test_parse_args_rejects_a_non_json_format():
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            bp._parse_args(["--format", "xml"])
        raise AssertionError("expected SystemExit for an invalid --format")
    except SystemExit as exc:
        assert exc.code == 2


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
