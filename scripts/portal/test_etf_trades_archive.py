"""Tests for scripts/portal/etf_trades_archive.py (RIS5 A3). Reuses the real
scripts/portal/fixtures/etf_trades/ws/ report fixtures (no network/claude -p).
    python3 scripts/portal/test_etf_trades_archive.py
"""
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etf_trades as et                       # noqa: E402
import etf_trades_archive as archiver          # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "etf_trades"
BASE_PATHS = et.Paths(ws_reports=FIXTURES / "ws")

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def test_archive_writes_dated_file_matching_etf_trades_output():
    direct = et.etf_trades(1, out_dir=None, paths=BASE_PATHS, today=date(2026, 1, 5))
    with tempfile.TemporaryDirectory() as td:
        out_path = archiver.archive(days=1, state_dir=Path(td), today=date(2026, 1, 5),
                                    paths=BASE_PATHS)
        check("file named <date>.json", out_path.name == "2026-01-05.json", out_path)
        archived = json.loads(out_path.read_text())
    check("archived shape == etf_trades() return value (no translation)",
         archived == direct, (archived.keys(), direct.keys()))
    check("by_ticker present", "by_ticker" in archived and archived["by_ticker"])


def test_archive_idempotent_on_rerun_same_day():
    with tempfile.TemporaryDirectory() as td:
        p1 = archiver.archive(days=1, state_dir=Path(td), today=date(2026, 1, 5), paths=BASE_PATHS)
        content1 = p1.read_text()
        p2 = archiver.archive(days=1, state_dir=Path(td), today=date(2026, 1, 5), paths=BASE_PATHS)
        content2 = p2.read_text()
    check("re-run same day overwrites identically", content1 == content2)
    check("same path both times", p1 == p2)


def test_archive_does_not_depend_on_out_dir_or_prior_build():
    """archive() must never pass out_dir to etf_trades() -- there is no stable
    <out_dir>/data/etf_trades.json to depend on (build_portal's out_dir is transient)."""
    with tempfile.TemporaryDirectory() as td:
        archiver.archive(days=1, state_dir=Path(td), today=date(2026, 1, 5), paths=BASE_PATHS)
        # No data/ subdirectory should have been created anywhere under the state dir --
        # only the flat <date>.json archive file.
        check("no data/ subdir created (no out_dir side effect)",
             not (Path(td) / "data").exists())


def test_cli_main_smoke():
    with tempfile.TemporaryDirectory() as td:
        rc = archiver.main(["--state-dir", td, "--date", "2026-01-05",
                            "--days", "1"])
    check("main() returns 0", rc == 0)


if __name__ == "__main__":
    test_archive_writes_dated_file_matching_etf_trades_output()
    test_archive_idempotent_on_rerun_same_day()
    test_archive_does_not_depend_on_out_dir_or_prior_build()
    test_cli_main_smoke()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_etf_trades_archive")
