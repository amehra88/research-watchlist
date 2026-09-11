#!/usr/bin/env python3
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme_notes as tn


def _cell(theme, cq, banks=0, companies=0, disclosing=0, corprep=0):
    return {"theme": theme, "cal_quarter": cq, "n_banks": banks, "banks": [f"B{i}" for i in range(banks)],
            "n_companies": companies, "companies": [f"C{i}" for i in range(companies)], "n_exchanges": banks + companies,
            "n_disclosing": disclosing, "disclosing": [f"D{i}" for i in range(disclosing)], "n_corprep_companies": corprep,
            "first_seen_quarter": cq}


def _pair(theme, ticker, stage, fe=None, ff=None, fq=None, lag=None):
    return {"theme": theme, "ticker": ticker, "stage": stage, "first_evidence_date": fe, "first_filing_date": ff,
            "first_question_date": fq, "lag_days": lag, "n_evidence": 1, "n_question": 1 if fq else 0, "banks": []}


SNAP = {"as_of": "2026-09-10", "quarters": ["CY2026-Q1", "CY2026-Q2", "CY2026-Q3"], "current_quarter": "CY2026-Q3",
        "denominators": {"CY2026-Q1": {"earnings_call": 40, "conference": 20, "mdna_filers": 60},
                         "CY2026-Q2": {"earnings_call": 43, "conference": 23, "mdna_filers": 69},
                         "CY2026-Q3": {"earnings_call": 45, "conference": 29, "mdna_filers": 67}},
        "no_coverage": {"no_results": ["ADI"], "incomplete": ["innolight.cn"], "no_factset_id": []},
        "metrics": [_cell("t1", "CY2026-Q2", banks=1, companies=1, disclosing=3), _cell("t1", "CY2026-Q3", banks=3, companies=4),
                    _cell("t2", "CY2026-Q3", banks=1, companies=2)],
        "pairs": [_pair("t1", "COHR", 2, fe="2026-04-20", ff="2026-04-20"), _pair("t1", "AAOI", 3, fq="2026-08-06"),
                  _pair("t1", "LITE", 2, fe="2026-05-01", ff="2026-05-01"), _pair("t2", "NVDA", 3, fq="2026-08-01")]}


def test_quarter_closes_fourteen_days_after_its_end():
    assert tn.quarter_end("CY2026-Q2").isoformat() == "2026-06-30"
    assert tn.is_closed("CY2026-Q2", "2026-07-14") and not tn.is_closed("CY2026-Q2", "2026-07-13")
    assert not tn.is_closed("CY2026-Q3", "2026-09-10")


def test_gate_needs_breadth_on_either_register():
    assert tn.clears_gate([_cell("t", "q", banks=2, companies=3)])
    assert tn.clears_gate([_cell("t", "q", disclosing=3)])
    assert not tn.clears_gate([_cell("t", "q", banks=2, companies=2), _cell("t", "q2", disclosing=2)])


def test_theme_state_takes_the_earliest_stage_among_affected_holdings():
    st = tn.theme_state("t1", SNAP, {"COHR": ["t1"], "LITE": ["t1"], "NVDA": ["t2"]})
    assert st["stage"] == 2 and st["affects"] == ["COHR", "LITE"] and st["tickers"] == ["AAOI", "COHR", "LITE"]
    assert st["first_evidence_date"] == "2026-04-20" and st["first_question_date"] == "2026-08-06"
    assert st["lag_days"] == 108 and st["status"] == "approved"
    st2 = tn.theme_state("t2", SNAP, {})            # no affected holding: fall back to all tickers
    assert st2["stage"] == 3 and st2["affects"] == []


def test_frontmatter_matches_spec_7_1():
    st = tn.theme_state("t1", SNAP, {"COHR": ["t1"]})
    fm = tn.render_frontmatter(st, "2026-09-10")
    import yaml
    d = yaml.safe_load(fm.strip("-\n"))
    assert d["doc_type"] == "theme_state" and d["theme"] == "t1" and d["stage"] == 2
    assert d["tickers"] == ["AAOI", "COHR", "LITE"] and d["affects"] == ["COHR"]
    assert d["first_evidence_date"] == "2026-04-20" and d["lag_days"] == 108 and d["updated"] == "2026-09-10"


def test_section_prints_counts_denominators_gap_and_citations():
    cites = {"questions": [{"ticker": "AAOI", "date": "2026-08-06", "speaker": "Simon Leopold", "firm": "Raymond James",
                            "event": "Q2 2026 Earnings Call", "text": "What's it like competitively?"}],
             "mdna": [{"ticker": "COHR", "date": "2026-04-20", "form": "10-Q", "text": "Capacity additions in China..."}]}
    s = tn.render_section("t1", "CY2026-Q3", SNAP, cites, "2026-09-10", closed=False)
    assert s.startswith("## CY2026-Q3 — in progress (as of 2026-09-10)")
    assert "3 banks" in s and "4 of 45 earnings-call" in s and "29 conference" in s
    assert "[[COHR/_thesis|COHR]]" in s and "Simon Leopold" in s and "Raymond James" in s and "10-Q" in s
    c = tn.render_section("t1", "CY2026-Q2", SNAP, {"questions": [], "mdna": []}, "2026-09-10", closed=True)
    assert c.startswith("## CY2026-Q2\n") and "3 disclosing / 1 asked" in c


def test_upsert_appends_closed_once_replaces_open_and_rewrites_frontmatter():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t1.md"
        fm1 = "---\ndoc_type: theme_state\nstage: 2\n---\n"
        r = tn.upsert_note(p, fm1, [("CY2026-Q2", "## CY2026-Q2\nclosed v1\n", True),
                                    ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-10)\nopen v1\n", False)])
        assert r["created"] and r["appended"] == ["CY2026-Q2", "CY2026-Q3"]
        # re-run same day: nothing changes in the closed section, open section replaced with identical text
        r = tn.upsert_note(p, fm1, [("CY2026-Q2", "## CY2026-Q2\nclosed v2 MUST NOT LAND\n", True),
                                    ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-10)\nopen v1\n", False)])
        t = p.read_text()
        assert r["unchanged"] == ["CY2026-Q2", "CY2026-Q3"] and "closed v1" in t and "MUST NOT LAND" not in t
        # next week: frontmatter rewritten, open section replaced, closed untouched
        r = tn.upsert_note(p, "---\ndoc_type: theme_state\nstage: 3\n---\n",
                           [("CY2026-Q2", "## CY2026-Q2\nclosed v3\n", True),
                            ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-17)\nopen v2\n", False)])
        t = p.read_text()
        assert r["replaced"] == ["CY2026-Q3"] and "stage: 3" in t and "closed v1" in t and "open v2" in t and "open v1" not in t
        assert t.count("## CY2026-Q3") == 1 and t.count("## CY2026-Q2") == 1
        # quarter closes: the open section is replaced by the frozen one, then never again
        r = tn.upsert_note(p, fm1, [("CY2026-Q3", "## CY2026-Q3\nfrozen\n", True)])
        t = p.read_text()
        assert r["replaced"] == ["CY2026-Q3"] and "frozen" in t and "in progress" not in t
        r = tn.upsert_note(p, fm1, [("CY2026-Q3", "## CY2026-Q3\nfrozen AGAIN\n", True)])
        assert r["unchanged"] == ["CY2026-Q3"] and "AGAIN" not in p.read_text()


def test_ticker_index_links_to_theme_notes_and_is_rewritten():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "_themes.md"
        assert tn.write_ticker_index("COHR", [{"theme": "t1", "stage": 2, "lag_days": None, "open_lag_days": 143}], p)
        t = p.read_text()
        assert "doc_type: theme_index" in t and "[[themes/t1|t1]]" in t and "stage 2" in t
        assert not tn.write_ticker_index("COHR", [{"theme": "t1", "stage": 2, "lag_days": None, "open_lag_days": 143}], p)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1; print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass"); sys.exit(1 if failed else 0)
