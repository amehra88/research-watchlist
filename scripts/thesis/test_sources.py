"""Run directly: python3 scripts/thesis/test_sources.py  (uses real notes/ + pg read-only)"""
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import sources as S  # noqa: E402

def test_news_filter_from_disk():
    ev = S.news_since("NVDA", date(2026, 9, 1))
    assert ev and all(e.source == "news" and e.ticker == "NVDA" for e in ev)
    assert all(e.date >= "2026-09-01" for e in ev)
    assert all(e.source_id.startswith("notes/news/") for e in ev)

def test_earnings_notes_glob_matches_real_names():
    ev = S.earnings_notes_since("AMBA", date(2026, 8, 1))
    assert any(e.source_id.endswith("2Q27.md") for e in ev)
    assert "## 4." in ev[-1].text          # thesis-read section carried through

def test_entity_claims_use_subject_or_affects():
    ev = S.entity_claims_since("COHR", date(2026, 8, 1))
    assert any("Accelink" in e.title or "Innolight" in e.title for e in ev)
    assert all(e.source == "entity_claim" for e in ev)

def test_collect_all_dedups_and_sorts():
    ev = S.collect_all("COHR", date(2026, 8, 1))
    ids = [e.source_id for e in ev]
    assert len(ids) == len(set(ids)) and ids == [e.source_id for e in sorted(ev, key=lambda e: e.date)]

if __name__ == "__main__":
    test_news_filter_from_disk(); test_earnings_notes_glob_matches_real_names()
    test_entity_claims_use_subject_or_affects(); test_collect_all_dedups_and_sorts()
    print("OK test_sources")
