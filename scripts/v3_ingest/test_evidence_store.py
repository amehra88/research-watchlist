"""
Unit tests for evidence_store (spec §4.3, §4.4 — the shared claim record).

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_evidence_store.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_store as es  # noqa: E402


def test_calendar_quarter_maps_month_to_quarter():
    assert es.calendar_quarter("2026-08-19") == "2026Q3"
    assert es.calendar_quarter("2026-01-01") == "2026Q1"
    assert es.calendar_quarter("2025-12-31") == "2025Q4"


def test_join_period_key_ignores_a_fiscal_label_and_uses_the_date():
    """The silent-mismatch guard. exchanges.jsonl carries 6,035 fiscal and
    4,086 calendar period_keys; claims are always calendar. LITE's fiscal
    2026Q4 call happened 2026-08-11, which is calendar 2026Q3 — joining on the
    raw label would line it up two quarters away, with no error raised."""
    got = es.join_period_key(period_key="2026Q4", period_basis="fiscal",
                             event_date="2026-08-11")
    assert got == "2026Q3", got
    # a calendar row derives to the same thing it already claims
    assert es.join_period_key(period_key="2026Q1", period_basis="calendar",
                              event_date="2026-02-04") == "2026Q1"


def test_join_period_key_refuses_to_guess_without_a_date():
    """A fiscal label with no date cannot be converted. Returning it anyway
    would reintroduce exactly the silent mismatch this function exists to
    prevent, so it raises instead."""
    try:
        es.join_period_key(period_key="2026Q4", period_basis="fiscal",
                           event_date=None)
    except ValueError as e:
        assert "calendar" in str(e)
    else:
        raise AssertionError("a fiscal label with no date must raise")
    # ... but a calendar label with no date is already usable
    assert es.join_period_key(period_key="2026Q1", period_basis="calendar",
                              event_date=None) == "2026Q1"


def test_claim_id_is_stable_and_text_sensitive():
    a = es.claim_id("mdna", "doc1", "capacity rose 34%")
    b = es.claim_id("mdna", "doc1", "capacity rose 34%")
    c = es.claim_id("mdna", "doc1", "capacity rose 35%")
    assert a == b, "same inputs must give same id"
    assert a != c, "text change must change the id"
    assert len(a) == 16


def test_make_claim_requires_first_evidence_date():
    """The lifecycle clock (spec §6.3). A claim without it is a bug."""
    try:
        es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="",
                      period_key="2026Q3", text="x")
    except ValueError as e:
        assert "first_evidence_date" in str(e)
    else:
        raise AssertionError("empty first_evidence_date must raise")


def test_make_claim_derives_period_key_when_absent():
    c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="2026-08-19",
                      period_key=None, text="x")
    assert c["period_key"] == "2026Q3"


def test_make_claim_has_exactly_the_declared_fields():
    c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                      affects=["ADI"], first_evidence_date="2026-08-19",
                      period_key="2026Q3", text="x")
    assert set(c) == set(es.CLAIM_FIELDS)
    assert c["verified"] is False, "claims are leads, never established fact"


def test_append_claims_dedupes_across_runs():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"
        c = es.make_claim(source="mdna", document_id="d", ticker="ADI",
                          affects=["ADI"], first_evidence_date="2026-08-19",
                          period_key="2026Q3", text="capacity rose")
        first = es.append_claims(p, [c])
        second = es.append_claims(p, [c])
        assert first == {"written": 1, "dupes": 0}
        assert second == {"written": 0, "dupes": 1}, "re-run must not duplicate"
        assert len(p.read_text().strip().splitlines()) == 1


def test_existing_claim_ids_tolerates_missing_file():
    with tempfile.TemporaryDirectory() as d:
        assert es.existing_claim_ids(Path(d) / "nope.jsonl") == set()


# ───────────────────────── runner ─────────────────────────

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
