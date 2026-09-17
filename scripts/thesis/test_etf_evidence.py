"""Tests for scripts/thesis/etf_evidence.py (RIS5 A3, peer-ETF challenge evidence).
No claude -p, no live archive reads.
    python3 scripts/thesis/test_etf_evidence.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import etf_evidence as EE  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


# ─────────────────────────── peer_trim_clusters ────────────────────────────

def test_distinct_etfs_not_entries_counted():
    """The single likeliest bug: the same ETF trimming on 3 different archived days must
    count as ONE manager, not three."""
    by_ticker = {
        "COHR": [
            {"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
            {"date": "2026-09-05", "etf": "XLK", "action": "trimmed"},   # same ETF, repeat
            {"date": "2026-09-10", "etf": "XLK", "action": "trimmed"},   # same ETF, repeat
        ],
    }
    clusters = EE.peer_trim_clusters(by_ticker, min_peer_etfs=3)
    check("one repeating ETF does NOT clear a 3-manager bar", "COHR" not in clusters, clusters)


def test_three_distinct_etfs_clears_bar():
    by_ticker = {
        "COHR": [
            {"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
            {"date": "2026-09-03", "etf": "SMH", "action": "exit"},
            {"date": "2026-09-07", "etf": "VGT", "action": "trimmed"},
        ],
    }
    clusters = EE.peer_trim_clusters(by_ticker, min_peer_etfs=3)
    check("3 distinct trimmers clears the bar", "COHR" in clusters, clusters)
    check("n == 3 and trimmers sorted", clusters["COHR"] == {"trimmers": ["SMH", "VGT", "XLK"], "n": 3},
         clusters["COHR"])


def test_any_add_suppresses_the_cluster():
    by_ticker = {
        "STX": [
            {"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
            {"date": "2026-09-03", "etf": "SMH", "action": "exit"},
            {"date": "2026-09-07", "etf": "VGT", "action": "trimmed"},
            {"date": "2026-09-08", "etf": "QQQ", "action": "added"},    # one add kills it
        ],
    }
    clusters = EE.peer_trim_clusters(by_ticker, min_peer_etfs=3)
    check("a single add suppresses the challenge cluster", "STX" not in clusters, clusters)


def test_below_threshold_not_clustered():
    by_ticker = {"PANW": [{"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
                          {"date": "2026-09-03", "etf": "SMH", "action": "trimmed"}]}
    clusters = EE.peer_trim_clusters(by_ticker, min_peer_etfs=3)
    check("2 distinct trimmers < 3 -> no cluster", "PANW" not in clusters, clusters)


# ─────────────────────────── evidence_rows (unconditional investor-interest route) ──

def test_evidence_rows_attaches_to_investor_interest_assumption():
    # investor_assumptions(direction="challenge") ALWAYS lazily loads bearish_themes()/
    # competition_slugs() even for the unconditional investor-interest route (it's one
    # function, not two) -- theme_polarity.py's zero-arg default REPO points at the main
    # checkout, which doesn't have config/theme_polarity.yaml pre-merge (the same "REPO
    # trap" A4's own test_insider_pull.py works around). Monkeypatch here too.
    from thesis import theme_polarity as TP
    real_bearish, real_competition = TP.bearish_themes, TP.competition_slugs
    TP.bearish_themes = lambda *a, **k: set()
    TP.competition_slugs = lambda *a, **k: set()
    clusters = {"COHR": {"trimmers": ["SMH", "VGT", "XLK"], "n": 3}}
    theses = {"COHR": {"assumptions": [
        {"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4",
        "status": "open"},
    ]}}
    try:
        ev = EE.evidence_rows(clusters, theses, "2026-09-17", covered_days=14)
    finally:
        TP.bearish_themes, TP.competition_slugs = real_bearish, real_competition
    check("one evidence row produced", len(ev) == 1, ev)
    row = ev[0]
    check("source is peer_etf", row["source"] == "peer_etf", row)
    check("direction is challenge", row["direction"] == "challenge", row)
    check("family is 'other managers'", row["family"] == "other managers", row)
    check("strength 1", row["strength"] == 1, row)
    check("ticker/assumption_id correct", row["ticker"] == "COHR"
         and row["assumption_id"] == "leverage_is_a_watch_item", row)
    check("why cites the trimmer count and names", "3 peer ETFs" in row["why"] and "XLK" in row["why"], row)
    check("source_id keyed by ticker+date", row["source_id"] == "peer_etf:COHR:2026-09-17", row)


def test_evidence_rows_skips_ticker_with_no_thesis():
    clusters = {"NOTHESIS": {"trimmers": ["A", "B", "C"], "n": 3}}
    ev = EE.evidence_rows(clusters, theses={}, as_of="2026-09-17", covered_days=14)
    check("no thesis -> no evidence rows", ev == [], ev)


def test_evidence_rows_competitive_advantage_route_via_monkeypatch():
    """Mirrors test_insider_pull.py's own monkeypatch convention (theme_polarity.py's
    default REPO points at the main checkout pre-merge) -- proves the challenge-specific
    routes ((a)/(b)/(c) from A4 fix 0) are reachable through this evidence path too, not
    just the unconditional investor-interest route exercised above."""
    from thesis import theme_polarity as TP
    real_bearish, real_competition = TP.bearish_themes, TP.competition_slugs
    TP.bearish_themes = lambda *a, **k: set()
    TP.competition_slugs = lambda *a, **k: set()
    try:
        clusters = {"COHR": {"trimmers": ["SMH", "VGT", "XLK"], "n": 3}}
        theses = {"COHR": {"assumptions": [
            {"id": "vertical_integration_moat",
            "derived_from": "competitive_advantage.innovation_rate: 4 — 'vertically integrated'",
            "status": "open", "themes": []},
        ]}}
        ev = EE.evidence_rows(clusters, theses, "2026-09-17", covered_days=14)
    finally:
        TP.bearish_themes, TP.competition_slugs = real_bearish, real_competition
    check("competitive_advantage-derived assumption attached via challenge routing",
         len(ev) == 1 and ev[0]["assumption_id"] == "vertical_integration_moat", ev)


# ─────────────────────────── load_archive ──────────────────────────────────

def test_load_archive_missing_day_returns_empty_dict_not_error():
    with tempfile.TemporaryDirectory() as td:
        result = EE.load_archive("2026-01-01", Path(td))
    check("missing archive day -> {}", result == {})


def test_load_archive_reads_written_file():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "2026-09-17.json"
        p.write_text(json.dumps({"as_of": "2026-09-17", "by_ticker": {"X": []}}))
        result = EE.load_archive("2026-09-17", Path(td))
    check("archive round-trips", result["by_ticker"] == {"X": []}, result)


# ─────────────────────────── CLI dry-run smoke ─────────────────────────────

def test_cli_dry_run_no_archive_is_a_clean_noop():
    with tempfile.TemporaryDirectory() as td:
        rc = EE.main(["--date", "2026-01-01", "--archive-dir", td, "--dry-run"])
    check("main() returns 0 when no archive exists yet", rc == 0, rc)


if __name__ == "__main__":
    test_distinct_etfs_not_entries_counted()
    test_three_distinct_etfs_clears_bar()
    test_any_add_suppresses_the_cluster()
    test_below_threshold_not_clustered()
    test_evidence_rows_attaches_to_investor_interest_assumption()
    test_evidence_rows_skips_ticker_with_no_thesis()
    test_evidence_rows_competitive_advantage_route_via_monkeypatch()
    test_load_archive_missing_day_returns_empty_dict_not_error()
    test_load_archive_reads_written_file()
    test_cli_dry_run_no_archive_is_a_clean_noop()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_etf_evidence")
