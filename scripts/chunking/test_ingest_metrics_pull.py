"""Run directly: python3 scripts/chunking/test_ingest_metrics_pull.py  (no network; RAW redirected)"""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_metrics as IM  # noqa: E402


def test_pull_prompt_shapes():
    g = IM.pull_prompt(["NVDA-US", "AMD-US"], "SALES", "guidance", "2020-01-01", "2026-09-14")
    assert "FactSet_EstimatesConsensus" in g and "estimate_type: 'guidance'" in g and "relativeFiscalStart: 1" in g
    assert "periodicity: 'QTR'" in g and "frequency: 'AM'" in g and '"NVDA-US"' in g and "metrics: [\"SALES\"]" in g
    s = IM.pull_prompt(["NVDA-US"], "EPS", "surprise", "2020-01-01", "2026-09-14")
    assert "estimate_type: 'surprise'" in s and "statistic: 'MEAN'" in s and "relativeFiscalStart" not in s


def test_pull_all_writes_union_and_keeps_prev(tmp):
    IM.RAW = tmp
    (tmp / "SALES_guidance.json").write_text(json.dumps({"data": [{"requestId": "OLD-US"}]}))
    calls = []
    def runner(ids, metric, kind, start, end):
        calls.append((tuple(ids), metric, kind))
        return [{"requestId": i, "metric": metric, "kind": kind} for i in ids]
    IM.IDS_PER_CALL = 2
    counts = IM.pull_all(["NVDA", "AMD", "AVGO"], ["SALES"], kinds=("guidance",), runner=runner, end="2026-09-14")
    assert counts == {"SALES_guidance": 3} and len(calls) == 2 and calls[0][0] == ("NVDA-US", "AMD-US")
    assert [r["requestId"] for r in json.loads((tmp / "SALES_guidance.json").read_text())["data"]] == ["NVDA-US", "AMD-US", "AVGO-US"]
    assert json.loads((tmp / "SALES_guidance.prev.json").read_text())["data"][0]["requestId"] == "OLD-US"


def test_pull_all_failure_leaves_file_untouched(tmp):
    IM.RAW = tmp
    (tmp / "EPS_surprise.json").write_text(json.dumps({"data": [{"requestId": "KEEP-US"}]}))
    def runner(ids, metric, kind, start, end):
        raise RuntimeError("claude -p rc=1")
    try:
        IM.pull_all(["NVDA"], ["EPS"], kinds=("surprise",), runner=runner); assert False
    except RuntimeError:
        pass
    assert json.loads((tmp / "EPS_surprise.json").read_text())["data"][0]["requestId"] == "KEEP-US"


def test_consensus_snapshot_latest_period(tmp):
    recs = [{"ticker": "NVDA", "metric": "SALES", "period": "1Q27", "fiscal_end": "2026-04-30", "guidance_mid": 1, "consensus_at_guide": 2, "consensus_at_print": 3, "actual": 4, "as_of": "2026-09-14"},
            {"ticker": "NVDA", "metric": "SALES", "period": "2Q27", "fiscal_end": "2026-07-31", "guidance_mid": 5, "consensus_at_guide": 6, "consensus_at_print": None, "actual": None, "as_of": "2026-09-14"}]
    p = tmp / "consensus_2026-09-14.jsonl"
    assert IM.consensus_snapshot(recs, p) == 1
    row = json.loads(p.read_text().splitlines()[0])
    assert row["period"] == "2Q27" and row["guidance_mid"] == 5 and row["consensus_at_print"] is None


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_pull_prompt_shapes(); test_pull_all_writes_union_and_keeps_prev(tmp); test_pull_all_failure_leaves_file_untouched(tmp); test_consensus_snapshot_latest_period(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_ingest_metrics_pull")
