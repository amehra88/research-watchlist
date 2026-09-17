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
    check("n == 3 and trimmers sorted",
         clusters["COHR"]["trimmers"] == ["SMH", "VGT", "XLK"] and clusters["COHR"]["n"] == 3,
         clusters["COHR"])
    check("cluster_start is the date the 3rd distinct trimmer appeared (2026-09-07)",
         clusters["COHR"]["cluster_start"] == "2026-09-07", clusters["COHR"])


def test_cluster_start_unaffected_by_a_4th_trimmer_joining_later():
    """Coordinator's acceptance criterion: a cluster that GROWS (new manager joins) keeps
    the same source_id, i.e. the same cluster_start -- it does NOT reset to the new
    manager's join date."""
    by_ticker = {
        "COHR": [
            {"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
            {"date": "2026-09-03", "etf": "SMH", "action": "exit"},
            {"date": "2026-09-07", "etf": "VGT", "action": "trimmed"},   # crosses bar here
            {"date": "2026-09-10", "etf": "QQQ", "action": "trimmed"},   # 4th, joins later
        ],
    }
    clusters = EE.peer_trim_clusters(by_ticker, min_peer_etfs=3)
    check("n reflects all 4 distinct trimmers", clusters["COHR"]["n"] == 4, clusters["COHR"])
    check("cluster_start stays pinned to the 3rd-crossing date, not the 4th trimmer's date",
         clusters["COHR"]["cluster_start"] == "2026-09-07", clusters["COHR"])


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
    clusters = {"COHR": {"trimmers": ["SMH", "VGT", "XLK"], "n": 3, "cluster_start": "2026-09-07"}}
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
    check("source_id keyed by ticker+cluster_start (NOT the run's as_of date)",
         row["source_id"] == "peer_etf:COHR:2026-09-07", row)


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
        clusters = {"COHR": {"trimmers": ["SMH", "VGT", "XLK"], "n": 3, "cluster_start": "2026-09-07"}}
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


# ─────────────────────────── cross-day dedup (coordinator fix round 1, item 1) ──────

def _thesis_with_investor_interest():
    return {"COHR": {"assumptions": [
        {"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4",
        "status": "open"},
    ]}}


def _patched_theme_polarity():
    from thesis import theme_polarity as TP
    real_bearish, real_competition = TP.bearish_themes, TP.competition_slugs
    TP.bearish_themes = lambda *a, **k: set()
    TP.competition_slugs = lambda *a, **k: set()
    return TP, real_bearish, real_competition


def test_two_consecutive_day_archives_same_cluster_produce_one_evidence_row():
    """The bug this fix closes: a 14-day trailing-window archive re-computed daily must
    NOT re-attach the same persisting cluster every day. Two archives (day1, day2) whose
    windows both contain the SAME 3 trims (window just slid by one day, nothing aged out)
    must produce evidence rows with the IDENTICAL source_id -- the real dedup then happens
    in main() against thesis.match_evidence's existing log (ticker|source_id|assumption_id
    key), so day2's write becomes a no-op there. This test proves the identity the dedup
    depends on: same cluster_start -> same source_id, regardless of which day it's read on."""
    TP, real_b, real_c = _patched_theme_polarity()
    try:
        by_ticker_day1 = {"COHR": [
            {"date": "2026-09-01", "etf": "XLK", "action": "trimmed"},
            {"date": "2026-09-03", "etf": "SMH", "action": "exit"},
            {"date": "2026-09-07", "etf": "VGT", "action": "trimmed"},
        ]}
        by_ticker_day2 = dict(by_ticker_day1)   # window slid 1 day, same trims still present
        theses = _thesis_with_investor_interest()

        c1 = EE.peer_trim_clusters(by_ticker_day1)
        ev1 = EE.evidence_rows(c1, theses, "2026-09-07", covered_days=7)
        c2 = EE.peer_trim_clusters(by_ticker_day2)
        ev2 = EE.evidence_rows(c2, theses, "2026-09-08", covered_days=7)   # next day's run
    finally:
        TP.bearish_themes, TP.competition_slugs = real_b, real_c

    check("both days produce exactly one evidence row each",
         len(ev1) == 1 and len(ev2) == 1, (ev1, ev2))
    check("source_id is IDENTICAL across the two days (dedup key is stable)",
         ev1[0]["source_id"] == ev2[0]["source_id"] == "peer_etf:COHR:2026-09-07",
         (ev1[0]["source_id"], ev2[0]["source_id"]))
    # Simulate main()'s own dedup against an existing log containing day1's row.
    existing = {f"{r['ticker']}|{r['source_id']}|{r['assumption_id']}" for r in ev1}
    day2_new = [r for r in ev2 if f"{r['ticker']}|{r['source_id']}|{r['assumption_id']}" not in existing]
    check("day2's write is a no-op against day1's log entry", day2_new == [], day2_new)


def test_cluster_that_lapses_and_reforms_gets_a_new_start_date():
    """When the old trims have fully aged out of the trailing window and a cluster later
    re-forms from entirely new trims, cluster_start (and therefore source_id) must be the
    NEW crossing date, not the old one -- a genuinely new challenge episode, not a
    duplicate of the first."""
    old_cluster = {"COHR": [
        {"date": "2026-08-01", "etf": "XLK", "action": "trimmed"},
        {"date": "2026-08-03", "etf": "SMH", "action": "exit"},
        {"date": "2026-08-07", "etf": "VGT", "action": "trimmed"},
    ]}
    # A later archive whose 14-day window no longer contains the August trims at all
    # (they've aged out) and instead holds a fresh September cluster.
    reformed_cluster = {"COHR": [
        {"date": "2026-09-10", "etf": "QQQ", "action": "trimmed"},
        {"date": "2026-09-12", "etf": "IYW", "action": "exit"},
        {"date": "2026-09-15", "etf": "SOXX", "action": "trimmed"},
    ]}
    c_old = EE.peer_trim_clusters(old_cluster)
    c_new = EE.peer_trim_clusters(reformed_cluster)
    check("old cluster start is the August crossing date",
         c_old["COHR"]["cluster_start"] == "2026-08-07", c_old["COHR"])
    check("reformed cluster gets a NEW, later start date",
         c_new["COHR"]["cluster_start"] == "2026-09-15", c_new["COHR"])
    check("the two cluster_starts (and therefore source_ids) differ",
         c_old["COHR"]["cluster_start"] != c_new["COHR"]["cluster_start"])


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
    test_cluster_start_unaffected_by_a_4th_trimmer_joining_later()
    test_any_add_suppresses_the_cluster()
    test_below_threshold_not_clustered()
    test_evidence_rows_attaches_to_investor_interest_assumption()
    test_evidence_rows_skips_ticker_with_no_thesis()
    test_evidence_rows_competitive_advantage_route_via_monkeypatch()
    test_two_consecutive_day_archives_same_cluster_produce_one_evidence_row()
    test_cluster_that_lapses_and_reforms_gets_a_new_start_date()
    test_load_archive_missing_day_returns_empty_dict_not_error()
    test_load_archive_reads_written_file()
    test_cli_dry_run_no_archive_is_a_clean_noop()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_etf_evidence")
