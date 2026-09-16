"""
Unit tests for scripts/portal/publish_files.py (RIS4 slice 2, Task 9).

publish_files.py prints the `files` map for the Artifact publish call: a JSON
object {published/path: published/path} for every regular file under --out
that is (a) not index.html, (b) not under smoke/, (c) not a dotfile (no path
component starting with "."), and (d) matches build_portal.OWNED_PATHS. All
tests build a synthetic tree under a tempfile.mkdtemp() dir -- never the live
REPO/portal_build.

No pytest in this env -- run directly:
    python3 scripts/portal/test_publish_files.py
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish_files as pf  # noqa: E402


def _sha256(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _write(root: Path, rel: str, content: bytes = b"x") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def _minimal_tree(root: Path, manifest_files: dict | None = None) -> None:
    """A tiny but structurally-real portal_build/ tree: index.html + smoke/ +
    a couple of owned data/vendor/top-level files + data/manifest.json.
    """
    _write(root, "index.html", b"<html>index</html>")
    _write(root, "app.js", b"var app = 1;")
    _write(root, "app2.js", b"var app2 = 1;")
    _write(root, "styles.css", b"body{}")
    _write(root, "vendor/markdown-it.min.js", b"/* vendor */")
    _write(root, "data/scores.json", b'{"a": 1}')
    _write(root, "data/tickers/AAPL.json", b'{"t": "AAPL"}')
    _write(root, "smoke/probe.json", b'{"probe": true}')
    _write(root, "smoke/probe.js", b"/* probe */")
    if manifest_files is None:
        manifest_files = {}
    _write(root, "data/manifest.json", json.dumps({"files": manifest_files}).encode())


def _tmp() -> Path:
    return Path(tempfile.mkdtemp(prefix="publish-files-test-"))


# ───────────────────────── collect() ─────────────────────────

def test_collect_excludes_index_html():
    root = _tmp()
    try:
        _minimal_tree(root)
        paths = pf.collect(root)
        assert "index.html" not in paths, paths
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_collect_excludes_smoke_dir():
    root = _tmp()
    try:
        _minimal_tree(root)
        paths = pf.collect(root)
        assert not any(p.startswith("smoke/") for p in paths), paths
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_collect_excludes_dotfiles():
    root = _tmp()
    try:
        _minimal_tree(root)
        _write(root, "data/.DS_Store", b"junk")
        _write(root, ".hidden-top", b"junk")
        paths = pf.collect(root)
        assert "data/.DS_Store" not in paths, paths
        assert ".hidden-top" not in paths, paths
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_collect_excludes_paths_not_matching_owned_paths():
    root = _tmp()
    try:
        _minimal_tree(root)
        _write(root, "secrets.json", b"nope")            # top-level, not in OWNED_PATHS
        _write(root, "not_owned_dir/thing.json", b"nope")
        paths = pf.collect(root)
        assert "secrets.json" not in paths, paths
        assert not any(p.startswith("not_owned_dir/") for p in paths), paths
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_collect_includes_owned_data_and_top_level_files():
    root = _tmp()
    try:
        _minimal_tree(root)
        paths = pf.collect(root)
        for expect in ("app.js", "app2.js", "styles.css",
                       "vendor/markdown-it.min.js", "data/scores.json",
                       "data/tickers/AAPL.json", "data/manifest.json"):
            assert expect in paths, (expect, paths)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_collect_missing_out_dir_returns_empty():
    root = _tmp()
    try:
        missing = root / "does-not-exist"
        assert pf.collect(missing) == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ───────────────────────── files_map() ─────────────────────────

def test_files_map_is_identity_map_of_collect():
    root = _tmp()
    try:
        _minimal_tree(root)
        paths = pf.collect(root)
        fm = pf.files_map(root)
        assert set(fm.keys()) == set(paths)
        for k, v in fm.items():
            assert k == v
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ───────────────────────── main() CLI ─────────────────────────

def _run_main(argv):
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = pf.main(argv)
    return rc, out.getvalue(), err.getvalue()


def test_main_prints_json_map_and_exits_0():
    root = _tmp()
    try:
        _minimal_tree(root)
        rc, out, err = _run_main(["--out", str(root)])
        assert rc == 0, err
        obj = json.loads(out)
        assert isinstance(obj, dict)
        assert "index.html" not in obj
        assert "data/scores.json" in obj
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_exits_2_when_index_html_missing():
    root = _tmp()
    try:
        _minimal_tree(root)
        (root / "index.html").unlink()
        rc, out, err = _run_main(["--out", str(root)])
        assert rc == 2, (rc, out, err)
        assert "index.html" in err
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_exits_2_when_manifest_missing():
    root = _tmp()
    try:
        _minimal_tree(root)
        (root / "data" / "manifest.json").unlink()
        rc, out, err = _run_main(["--out", str(root)])
        assert rc == 2, (rc, out, err)
        assert "manifest.json" in err
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_exits_2_when_count_exceeds_254():
    root = _tmp()
    try:
        _minimal_tree(root)
        for i in range(300):
            _write(root, f"data/many/{i}.json", b"{}")
        rc, out, err = _run_main(["--out", str(root)])
        assert rc == 2, (rc, out, err)
        assert "254" in err
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_check_passes_on_matching_hashes():
    root = _tmp()
    try:
        scores_bytes = b'{"a": 1}'
        aapl_bytes = b'{"t": "AAPL"}'
        app_bytes = b"var app = 1;"
        app2_bytes = b"var app2 = 1;"
        css_bytes = b"body{}"
        vendor_bytes = b"/* vendor */"
        manifest_files = {
            "app.js": {"bytes": len(app_bytes), "sha256": _sha256(app_bytes)},
            "app2.js": {"bytes": len(app2_bytes), "sha256": _sha256(app2_bytes)},
            "styles.css": {"bytes": len(css_bytes), "sha256": _sha256(css_bytes)},
            "vendor/markdown-it.min.js": {"bytes": len(vendor_bytes), "sha256": _sha256(vendor_bytes)},
            "data/scores.json": {"bytes": len(scores_bytes), "sha256": _sha256(scores_bytes)},
            "data/tickers/AAPL.json": {"bytes": len(aapl_bytes), "sha256": _sha256(aapl_bytes)},
            "index.html": {"bytes": 19, "sha256": _sha256(b"<html>index</html>")},
        }
        _minimal_tree(root, manifest_files=manifest_files)
        rc, out, err = _run_main(["--out", str(root), "--check"])
        assert rc == 0, (rc, out, err)
        obj = json.loads(out)
        assert "data/scores.json" in obj
        # 7 published files (app.js/app2.js/styles.css/vendor/.../data/scores.json/
        # data/tickers/AAPL.json/data/manifest.json) minus the manifest itself ==
        # 6 actually hash-checked; the message must say so honestly, not claim
        # the manifest (never compared to itself) was "verified" too.
        assert "6/7 files hash-verified (manifest itself excluded)" in err, err
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_check_exits_3_on_mismatch():
    root = _tmp()
    try:
        manifest_files = {
            "app.js": {"bytes": 999, "sha256": "0" * 64},   # deliberately wrong
        }
        _minimal_tree(root, manifest_files=manifest_files)
        rc, out, err = _run_main(["--out", str(root), "--check"])
        assert rc == 3, (rc, out, err)
        assert "app.js" in err
        assert "mismatch" in err.lower()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_check_exits_3_when_file_not_tracked_in_manifest():
    root = _tmp()
    try:
        _minimal_tree(root, manifest_files={})   # nothing tracked
        rc, out, err = _run_main(["--out", str(root), "--check"])
        assert rc == 3, (rc, out, err)
    finally:
        shutil.rmtree(root, ignore_errors=True)


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
