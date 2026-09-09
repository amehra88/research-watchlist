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


if __name__ == "__main__":
    test_prompt_excludes_10b5_1(); test_parse_rows_json_and_csv(); test_normalize_key_variants(); test_clusters_and_evidence_direction()
    print("OK test_insider_pull")
