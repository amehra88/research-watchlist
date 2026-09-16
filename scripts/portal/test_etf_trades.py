"""
Unit tests for scripts/portal/etf_trades.py (RIS4 slice 2, Task 3 — split out of
reports.py in fix round 1).

fixtures/etf_trades/ws/report_2026-01-05.txt is a byte-for-byte copy of a real
report_2026-09-15.txt (re-dated) so the parser is tested against real Unicode
(em dash, →, σ), not hand-typed approximations of them; report_2026-01-06.txt
is the same content re-dated again, for the "second day" / tolerate-a-gap tests.

No pytest in this env — run directly:
    python3 scripts/portal/test_etf_trades.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etf_trades as et  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "etf_trades"
BASE_PATHS = et.Paths(ws_reports=FIXTURES / "ws")

DAY1, DAY2 = "2026-01-05", "2026-01-06"


def test_etf_trades_parses_new_exits_added_trimmed():
    result = et.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
    day = next(d for d in result["days"] if d["date"] == DAY1)
    etfs = {e["etf"]: e for e in day["etfs"]}

    assert len(etfs) == 15, sorted(etfs)

    jtek = etfs["JTEK"]
    assert [n["sym"] for n in jtek["new"]] == ["ADSK", "GENB"]
    assert jtek["new"][0] == {"sym": "ADSK", "name": "AUTODESK INC COMMON",
                               "weight": 0.25, "shares": 47525}
    assert len(jtek["added"]) == 4
    assert len(jtek["trimmed"]) == 2
    assert jtek["trimmed"][0] == {"sym": "ORCL", "name": "ORACLE CORP COMMON STOCK",
                                   "delta_pp": -0.83, "from_weight": 1.18, "to_weight": 0.32}

    tek = etfs["TEK"]
    assert len(tek["added"]) == 1 and len(tek["trimmed"]) == 1

    alai = etfs["ALAI"]
    assert len(alai["new"]) == 1 and len(alai["added"]) == 3 and len(alai["trimmed"]) == 24

    ais = etfs["AIS"]
    assert len(ais["new"]) == 1 and len(ais["exits"]) == 1
    assert ais["exits"][0] == {"sym": "688008", "name": "C1 Montage Technology Co Ltd",
                                "weight": 1.01, "shares": 351334}

    no_trade = etfs["SPRX"]
    assert no_trade == {"etf": "SPRX", "name": "SPEAR Alpha ETF",
                         "new": [], "exits": [], "added": [], "trimmed": []}


def test_etf_trades_by_ticker_inverted_index():
    result = et.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
    assert result["by_ticker"]["ADSK"] == [{"date": DAY1, "etf": "JTEK", "action": "new"}]
    assert result["by_ticker"]["ORCL"] == [{"date": DAY1, "etf": "JTEK", "action": "trimmed"}]
    assert {"date": DAY1, "etf": "AIS", "action": "exit"} in result["by_ticker"]["688008"]


def test_etf_trades_tolerates_missing_day():
    result = et.etf_trades(3, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 7))
    dates = {d["date"] for d in result["days"]}
    assert dates == {DAY1, DAY2}  # 2026-01-07 has no ws fixture -> skipped, not an error


def test_etf_trades_writes_file_when_out_dir_given():
    import tempfile
    import json
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        result = et.etf_trades(1, out_dir=out, paths=BASE_PATHS,
                                today=__import__("datetime").date(2026, 1, 5))
        out_path = out / "data" / "etf_trades.json"
        assert out_path.exists()
        assert json.loads(out_path.read_text()) == result


def test_etf_trades_no_write_without_out_dir():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        cwd = os.getcwd()
        os.chdir(td)
        try:
            et.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
            # A stray relative-path write (the out_dir=None branch writing anyway)
            # would land under this cwd -- assert the whole tree stayed empty.
            assert list(Path(td).iterdir()) == []
        finally:
            os.chdir(cwd)


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
