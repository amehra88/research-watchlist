#!/usr/bin/env python3
import datetime as dt
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import diffusion as df
import lifecycle as lc


def _r(rid, reg, ticker, date, cq, themes, firm=None, source="exchange", event_type="earnings_call"):
    return {"id": rid, "register": reg, "ticker": ticker, "event_date": date, "cal_quarter": cq, "firm": firm,
            "source": source, "event_type": event_type, "period_key": "x", "threshold": 0.3, "best": 0.5,
            "themes": [{"theme": t, "score": 0.5} for t in themes], "candidate": None}


def test_host_firm_matching_handles_real_headline_forms():
    assert df.is_host_firm("Goldman Sachs & Co. LLC", "Goldman Sachs Communacopia +")
    assert df.is_host_firm("Citigroup Global Markets, Inc.", "Citi")
    assert df.is_host_firm("BofA Securities, Inc.", "Bank of America")
    assert df.is_host_firm("JPMorgan Securities LLC", "JP Morgan")
    assert not df.is_host_firm("Mizuho Securities USA LLC", "Goldman Sachs")
    assert not df.is_host_firm(None, "Citi") and not df.is_host_firm("Citi", None)


def test_metrics_count_banks_companies_exchanges_and_exclude_host_from_banks():
    rows = [_r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"], firm="Raymond James & Associates, Inc."),
            _r("q2", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], firm="Goldman Sachs & Co. LLC", event_type="conference"),
            _r("q3", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], firm="Mizuho Securities USA LLC", event_type="conference"),
            _r("q4", "question", "LITE", "2026-08-12", "CY2026-Q3", ["t2"], firm="Mizuho Securities USA LLC")]
    meta = {"q2": {"host_hint": "Goldman Sachs Communacopia +"}, "q3": {"host_hint": "Goldman Sachs Communacopia +"}}
    m = df.metrics(rows, meta)
    t1 = m[("t1", "CY2026-Q3")]
    assert t1["n_exchanges"] == 3 and t1["n_companies"] == 2
    assert t1["n_banks"] == 2 and t1["n_host_excluded"] == 1     # Goldman at its own conference is out
    assert t1["companies"] == ["AAOI", "LITE"]
    assert m[("t2", "CY2026-Q3")]["n_banks"] == 1


def test_mdna_disclosing_needs_two_mapped_blocks_per_filer_quarter():
    rows = [_r("c1", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("c2", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("c3", "evidence", "LITE", "2026-05-02", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("e1", "evidence", "FN", "2026-05-03", "CY2026-Q2", ["t1"])]
    t1 = df.metrics(rows, {})[("t1", "CY2026-Q2")]
    assert t1["disclosing"] == ["COHR"] and t1["n_disclosing"] == 1   # LITE has one block: not counted
    assert t1["n_corprep_companies"] == 1                              # FN corprep speech is evidence, separately
    assert t1["n_companies"] == 0 and t1["n_banks"] == 0


def test_apply_mdna_block_rule_drops_single_block_themes_but_keeps_exchange_rows():
    rows = [_r("c1", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1", "t2"], source="mdna"),
            _r("c2", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna"),
            _r("e1", "evidence", "FN", "2026-05-03", "CY2026-Q2", ["t2"])]
    out = df.apply_mdna_block_rule(rows)
    assert [t["theme"] for t in out[0]["themes"]] == ["t1"]          # t2 had one COHR block that quarter
    assert [t["theme"] for t in out[2]["themes"]] == ["t2"]          # exchange rows untouched
    assert rows[0]["themes"][1]["theme"] == "t2"                       # input not mutated


def test_first_seen_quarter_is_the_earliest_quarter_with_any_row():
    rows = [_r("q1", "question", "AAOI", "2026-02-01", "CY2026-Q1", ["t1"], firm="X"),
            _r("c1", "evidence", "COHR", "2025-11-01", "CY2025-Q4", ["t1"], source="mdna"),
            _r("c2", "evidence", "COHR", "2025-11-01", "CY2025-Q4", ["t1"], source="mdna")]
    m = df.metrics(rows, {})
    assert m[("t1", "CY2026-Q1")]["first_seen_quarter"] == "CY2025-Q4"


def test_denominators_count_covered_companies_per_quarter_and_event_type_over_all_rows():
    rows = [_r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", []),                       # unmapped still covered
            _r("e1", "evidence", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"]),
            _r("q2", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], event_type="conference"),
            _r("c1", "evidence", "COHR", "2026-08-01", "CY2026-Q3", [], source="mdna", event_type="10-Q")]
    d = df.denominators(rows)
    assert d["CY2026-Q3"] == {"earnings_call": 1, "conference": 1, "mdna_filers": 1}


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1; print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass"); sys.exit(1 if failed else 0)
