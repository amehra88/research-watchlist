"""Run directly: python3 scripts/thesis/test_insider_pull.py  (no network)"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import insider_pull as I  # noqa: E402


def _transcript(payload: str) -> str:
    return "\n".join([json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": I.TOOL, "input": {}}]}}),
                      json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": payload}]}})])


def test_prompt_excludes_10b5_1():
    p = I.prompt(["COHR", "LITE"], "2026-09-01", "2026-09-08")
    assert "tenb5: 'E'" in p and '"COHR"' in p and "use_disclosure_date: true" in p and "EXACTLY ONCE" in p


def test_parse_rows_json_and_csv():
    rows = [{"ticker": "COHR", "insider": "A", "txntype": "Buy", "shares": 100, "value": 5000, "date": "2026-09-02"}]
    assert I.parse_rows(_transcript(json.dumps({"data": rows})))[0]["ticker"] == "COHR"
    assert I.parse_rows(_transcript(json.dumps(rows)))[0]["insider"] == "A"
    csv_text = "ticker,insider_name,transaction_type,shares,value,transaction_date\nLITE,B,Sell,10,\"1,000\",2026-09-03\n"
    out = I.parse_rows(_transcript(csv_text))
    assert out and out[0]["ticker"] == "LITE"
    live = ("ticker,entityname,mcap,sector,iacc,formtype,txnid,txndate,datefiled,code,acquired_disposed,rptcik,insider,pos_type,has_10b5,tenb5planid,shares,value,pctchange,notable_event,link\r\n"
            "NVDA,NVIDIA,5450702310000,Technology,43725689,4,24696410,2026-09-04 00:00:00,2026-09-08 00:00:00,Sale,,1199039,Mark A. Stevens,Director,False,,1022239.0,235636867.411,-3.41,,https://x/\r\n")
    out = I.parse_rows(_transcript(json.dumps({"result": live})))            # the real InsiderScore shape: {"result": "<CSV>"}
    n = I.normalize(out[0])
    assert n["ticker"] == "NVDA" and n["txn_type"] == "Sell" and n["insider"] == "Mark A. Stevens" and n["position"] == "Director"
    assert n["date"] == "2026-09-04" and n["value"] == 235636867.411 and n["tenb5"] is False


def test_normalize_key_variants():
    n = I.normalize({"Ticker": "lite", "Insider Name": "B", "Transaction Type": "Sale", "Shares": "10", "Value": "$1,000", "Transaction Date": "2026-09-03T00:00:00", "Position": "CFO"})
    assert n["ticker"] == "LITE" and n["insider"] == "B" and n["txn_type"] == "Sell" and n["value"] == 1000.0 and n["date"] == "2026-09-03" and n["position"] == "CFO"


def test_clusters_and_evidence_direction():
    rows = [I.normalize(r) for r in [
        {"ticker": "COHR", "insider": "A", "txntype": "Buy", "value": 100}, {"ticker": "COHR", "insider": "B", "txntype": "Buy", "value": 200},
        {"ticker": "LITE", "insider": "C", "txntype": "Sell", "value": 50}, {"ticker": "LITE", "insider": "C", "txntype": "Sell", "value": 50}]]
    cl = I.clusters(rows)
    assert cl["COHR"]["buyers"] == ["A", "B"] and cl["COHR"]["buy_value"] == 300 and cl["LITE"]["sellers"] == ["C"]
    theses = {"COHR": {"assumptions": [{"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4", "status": "open"},
                                       {"id": "datacom_ramp_continues", "derived_from": "ai_positioning: 4", "status": "open"}]},
              "LITE": {"assumptions": [{"id": "x_investor", "derived_from": "potential_investor_interest.score: 3", "status": "open"}]}}
    ev = I.evidence_rows(cl, theses, "2026-09-08")
    assert len(ev) == 1 and ev[0]["ticker"] == "COHR" and ev[0]["assumption_id"] == "leverage_is_a_watch_item"
    assert ev[0]["direction"] == "confirm" and ev[0]["strength"] == 1 and ev[0]["source"] == "insider"   # LITE: one seller only → nothing


def test_investor_assumptions_confirm_unaffected_by_bearish_themes():
    # RIS5 A4: confirm direction (or no direction at all) never picks up the bearish-theme
    # route -- only 'challenge' does. Same fixture shape as test_clusters_and_evidence_direction.
    fm = {"assumptions": [{"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4", "status": "open"},
                          {"id": "margin_holds", "derived_from": "ai_positioning: 4", "status": "open",
                           "themes": ["ai_inference_margin_compression"]}]}
    assert I.investor_assumptions(fm) == ["leverage_is_a_watch_item"]
    assert I.investor_assumptions(fm, "confirm") == ["leverage_is_a_watch_item"]


def test_investor_assumptions_challenge_also_attaches_bearish_theme_assumptions():
    # A challenge cluster attaches to (a) the usual investor-interest assumptions and (b) any
    # assumption tagged with a polarity -1 theme -- not only investor-interest ones (RIS5 A4).
    fm = {"assumptions": [
        {"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4", "status": "open"},
        {"id": "margin_holds", "derived_from": "ai_positioning: 4", "status": "open", "themes": ["ai_inference_margin_compression"]},
        {"id": "unrelated", "derived_from": "ai_positioning: 4", "status": "open", "themes": ["ad_market_strength"]},
        {"id": "retired_margin", "derived_from": "ai_positioning: 4", "status": "retired", "themes": ["ai_inference_margin_compression"]},
    ]}
    bearish = {"ai_inference_margin_compression"}
    out = I.investor_assumptions(fm, "challenge", bearish=bearish)
    assert set(out) == {"leverage_is_a_watch_item", "margin_holds"}   # unrelated (bullish theme) and retired excluded
    assert out[0] == "leverage_is_a_watch_item"                       # investor-interest ids still come first


def test_investor_assumptions_challenge_never_double_counts_an_id():
    # An assumption that is BOTH investor-interest-derived AND bearish-themed appears once.
    fm = {"assumptions": [{"id": "x_investor", "derived_from": "potential_investor_interest.score: 3", "status": "open",
                           "themes": ["ai_inference_margin_compression"]}]}
    out = I.investor_assumptions(fm, "challenge", bearish={"ai_inference_margin_compression"})
    assert out == ["x_investor"]


def test_investor_assumptions_challenge_default_loads_real_theme_polarity():
    # No explicit `bearish` -> loads config/theme_polarity.yaml for real (worktree-local file,
    # not the REPO default path) via a real watchlist slug known to be polarity -1.
    from thesis import theme_polarity as TP
    real_polarity = Path(__file__).resolve().parents[2] / "config" / "theme_polarity.yaml"
    real_watchlist = Path(__file__).resolve().parents[2] / "config" / "watchlist.yaml"
    bearish = TP.bearish_themes(real_polarity, real_watchlist)
    assert "ai_inference_margin_compression" in bearish
    fm = {"assumptions": [{"id": "margin_holds", "derived_from": "ai_positioning: 4", "status": "open",
                           "themes": ["ai_inference_margin_compression"]}]}
    assert I.investor_assumptions(fm, "challenge", bearish=bearish) == ["margin_holds"]


def test_clusters_and_evidence_direction_routes_challenge_through_bearish_themes():
    # End-to-end through evidence_rows: a challenge cluster (sellers only) attaches to a
    # bearish-themed assumption even though it has no investor-interest derivation at all.
    # evidence_rows -> investor_assumptions(fm, direction) with no explicit `bearish`, which
    # lazily loads thesis.theme_polarity.bearish_themes() -- monkeypatched here so the test
    # stays hermetic (REPO points at the main checkout, not this worktree's own
    # config/theme_polarity.yaml, until this branch merges).
    from thesis import theme_polarity as TP
    real_bearish_themes = TP.bearish_themes
    TP.bearish_themes = lambda *a, **k: {"ai_inference_margin_compression"}
    try:
        rows = [I.normalize(r) for r in [
            {"ticker": "CIEN", "insider": "A", "txntype": "Sell", "value": 100}, {"ticker": "CIEN", "insider": "B", "txntype": "Sell", "value": 200}]]
        cl = I.clusters(rows)
        theses = {"CIEN": {"assumptions": [{"id": "margin_trajectory_holds", "derived_from": "ai_positioning: 4", "status": "open",
                                            "themes": ["ai_inference_margin_compression"]}]}}
        ev = I.evidence_rows(cl, theses, "2026-09-08")
    finally:
        TP.bearish_themes = real_bearish_themes
    assert len(ev) == 1 and ev[0]["ticker"] == "CIEN" and ev[0]["assumption_id"] == "margin_trajectory_holds"
    assert ev[0]["direction"] == "challenge" and ev[0]["source"] == "insider"


if __name__ == "__main__":
    test_prompt_excludes_10b5_1(); test_parse_rows_json_and_csv(); test_normalize_key_variants(); test_clusters_and_evidence_direction()
    test_investor_assumptions_confirm_unaffected_by_bearish_themes()
    test_investor_assumptions_challenge_also_attaches_bearish_theme_assumptions()
    test_investor_assumptions_challenge_never_double_counts_an_id()
    test_investor_assumptions_challenge_default_loads_real_theme_polarity()
    test_clusters_and_evidence_direction_routes_challenge_through_bearish_themes()
    print("OK test_insider_pull")
