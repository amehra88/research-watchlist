"""
Tests for factset_flows.py. No LLM is exercised — the runner is faked.

What these protect:
  • null survives the transport as None and is never coerced to 0.0 (the value that makes an
    outage read as "no flow" downstream),
  • date chunking respects the 500-ROW cap, where rows = ids x trading days — the constraint
    that turns the backfill into ~50 calls instead of ~5,
  • a saturated chunk is split rather than silently truncating history,
  • one bad chunk costs its own tickers and is REPORTED, instead of aborting a long backfill,
  • rows demux by requestId, not by call ordering.

No pytest in this env — run directly:  python3 scripts/etfflows/test_factset_flows.py
"""
import json
import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import FACTSET_CHUNK_SIZE, FACTSET_RESULT_LIMIT  # noqa: E402
from etfflows import factset_flows as ff  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


# ── normalisation ─────────────────────────────────────────────────────────────

def test_null_is_preserved_as_none():
    """The real 2026-08-19 shape: today's flow is null until T+1."""
    raw = [
        {"requestId": "XLK", "date": "2026-08-18", "fundFlows": 47558761.75},
        {"requestId": "XLK", "date": "2026-08-19", "fundFlows": None},
    ]
    out = ff.normalize(raw, "flows")
    check("null becomes None, not 0.0", out[1]["value"] is None, f"got {out[1]}")
    check("real value passes through", out[0]["value"] == 47558761.75)


def test_genuine_zero_survives():
    """XLK 2026-07-03 really was 0.0 (2 of 23 July days). It must not be dropped."""
    out = ff.normalize([{"requestId": "XLK", "date": "2026-07-03", "fundFlows": 0.0}], "flows")
    check("genuine 0.0 is kept", len(out) == 1 and out[0]["value"] == 0.0, f"got {out}")
    check("0.0 is distinguishable from None", out[0]["value"] is not None)


def test_aum_uses_share_class_field():
    """fundLevelAUM must never be the value — VOO would be overstated 1.7x."""
    raw = [{"requestId": "VOO", "date": "2026-07-31",
            "fundLevelAUM": 1676909034357.62,
            "shareClassAUMReported": 993823499680.519,
            "numberOfSharesOutstanding": 1448215638.378}]
    out = ff.normalize(raw, "aum")
    check("aum value is shareClassAUMReported",
          out[0]["value"] == 993823499680.519, f"got {out[0]['value']}")
    check("shares outstanding carried through",
          out[0]["shares_outstanding"] == 1448215638.378)


def test_rows_demux_by_request_id():
    raw = [{"requestId": "SPY", "date": "2026-08-18", "fundFlows": 1.0},
           {"requestId": "QQQ", "date": "2026-08-18", "fundFlows": 2.0}]
    out = ff.normalize(raw, "flows")
    check("tickers come from requestId, not call order",
          {r["ticker"] for r in out} == {"SPY", "QQQ"}, f"got {out}")


def test_malformed_rows_dropped():
    raw = [{"requestId": "", "date": "2026-08-18", "fundFlows": 1.0},
           {"requestId": "XLK", "date": "not-a-date", "fundFlows": 1.0},
           {"requestId": "XLK", "date": "2026-08-18", "fundFlows": 1.0}]
    out = ff.normalize(raw, "flows")
    check("rows without ticker/date are dropped", len(out) == 1, f"got {out}")


# ── chunking ──────────────────────────────────────────────────────────────────

def test_date_chunks_respect_row_cap():
    """rows = ids x trading days must stay under the 500 cap for every chunk."""
    chunks = ff.date_chunks("2023-01-01", "2026-01-01", n_ids=10)
    worst = 0
    for cs, ce in chunks:
        cal = (date.fromisoformat(ce) - date.fromisoformat(cs)).days + 1
        trading = cal * 252 / 365.0          # expected trading days in the span
        worst = max(worst, trading * 10)
    check("no chunk is projected to exceed the 500-row cap",
          worst <= FACTSET_RESULT_LIMIT, f"worst projected rows={worst:.0f}")
    check("chunks are contiguous and cover the range",
          chunks[0][0] == "2023-01-01" and chunks[-1][1] == "2026-01-01",
          f"{chunks[0]} .. {chunks[-1]}")


def test_date_chunks_no_gaps_or_overlap():
    chunks = ff.date_chunks("2026-01-01", "2026-06-30", n_ids=10)
    for (_, prev_end), (nxt_start, _) in zip(chunks, chunks[1:]):
        gap = (date.fromisoformat(nxt_start) - date.fromisoformat(prev_end)).days
        if gap != 1:
            check("chunks are exactly contiguous", False, f"gap of {gap} days at {prev_end}")
            return
    check("chunks are exactly contiguous", True)


def test_fewer_ids_means_longer_spans():
    """The cap is on rows, so a 1-ticker pull can cover 10x the calendar of a 10-ticker pull."""
    wide = ff.date_chunks("2023-01-01", "2026-01-01", n_ids=1)
    narrow = ff.date_chunks("2023-01-01", "2026-01-01", n_ids=10)
    check("1 id needs far fewer calls than 10 ids", len(wide) < len(narrow),
          f"{len(wide)} vs {len(narrow)}")


def test_id_chunks_respect_tool_limit():
    ids = ff.id_chunks([f"T{i}" for i in range(47)])
    check("no chunk exceeds the 10-id tool limit",
          all(len(c) <= FACTSET_CHUNK_SIZE for c in ids), f"got {[len(c) for c in ids]}")
    check("all tickers covered exactly once",
          sum(len(c) for c in ids) == 47)


def test_estimate_calls_matches_spec_order_of_magnitude():
    """The spec's ~52-call figure was FLOWS ONLY. Price and AUM history cost extra.

    Printed here so the real backfill budget is a number someone read, not a surprise
    discovered halfway through a 5-hour quota window.
    """
    trig = ff.estimate_calls(28, "2023-08-19", "2026-08-19", "flows")
    ctx = ff.estimate_calls(19, "2025-08-19", "2026-08-19", "flows")
    total = trig + ctx
    print(f"       [flows] trigger 3y={trig}, context 1y={ctx}, total={total}")
    check("flows backfill is tens of calls, not ~5 (the spec's corrected figure)",
          30 <= total <= 90, f"got {total}")


def test_aum_chunking_is_frequency_aware():
    """aum is MONTH-END. Planning it at daily frequency costs ~24x the calls it needs."""
    daily_plan = len(ff.date_chunks("2023-08-19", "2026-08-19", 10, rows_per_year=252))
    monthly_plan = len(ff.date_chunks("2023-08-19", "2026-08-19", 10, rows_per_year=12))
    print(f"       [aum 3y, 10 ids] daily-planned={daily_plan} vs month-aware={monthly_plan}")
    check("month-end endpoint plans far fewer chunks", monthly_plan < daily_plan / 5,
          f"{monthly_plan} vs {daily_plan}")
    check("3y of month-end data fits in a single chunk", monthly_plan == 1,
          f"got {monthly_plan}")

    # 36 month-end rows x 10 ids = 360 rows, comfortably under the 500 cap.
    check("projected rows stay under the cap", 36 * 10 <= FACTSET_RESULT_LIMIT)


def test_full_backfill_budget_is_reported():
    """Total across all three endpoints — the number that gates when this may be run."""
    plan = {
        "flows (trigger 3y)": ff.estimate_calls(28, "2023-08-19", "2026-08-19", "flows"),
        "flows (context 1y)": ff.estimate_calls(19, "2025-08-19", "2026-08-19", "flows"),
        "aum   (all 3y)":     ff.estimate_calls(47, "2023-08-19", "2026-08-19", "aum"),
        "prices (all ~1y)":   ff.estimate_calls(47, "2025-08-19", "2026-08-19", "prices"),
    }
    for k, v in plan.items():
        print(f"       {k:22s} {v:3d} calls")
    total = sum(plan.values())
    print(f"       {'TOTAL':22s} {total:3d} calls")
    check("full backfill budget is known and bounded", total < 200, f"got {total}")


# ── fetch behaviour ───────────────────────────────────────────────────────────

def test_saturation_triggers_a_split():
    calls = []

    def runner(ids, data_type, start, end, limit, frequency):
        calls.append((start, end))
        # Saturate only the first, widest call; splits come back small.
        if len(calls) == 1:
            return [{"requestId": ids[0], "date": "2026-01-05", "fundFlows": 1.0}] * limit
        return [{"requestId": ids[0], "date": "2026-01-05", "fundFlows": 1.0}]

    recs, failed = ff.fetch_range(["XLK"], "flows", "2026-01-01", "2026-03-31", runner)
    check("a saturated chunk is split, not accepted", len(calls) > 1, f"calls={calls}")
    check("split results are collected", len(recs) > 0)
    check("no tickers reported failed", failed == [])


def test_chunk_failure_is_reported_not_fatal():
    seen = []

    def runner(ids, data_type, start, end, limit, frequency):
        if "BAD" in ids:
            raise RuntimeError("rc=1: boom")
        return [{"requestId": ids[0], "date": "2026-08-18", "fundFlows": 1.0}]

    recs, failed = ff.fetch_range(["BAD"], "flows", "2026-08-01", "2026-08-19",
                                  runner, on_progress=seen.append)
    check("failure does not raise", True)
    check("failed ticker is reported", failed == ["BAD"], f"got {failed}")
    check("failure is logged for the operator", any("FAIL" in m for m in seen), f"got {seen}")


def _stream_line(payload_text):
    """One stream-json transcript line carrying a tool_result block."""
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "content": [{"type": "text", "text": payload_text}]}]}})


def test_tool_result_extracted_from_stream_json():
    body = json.dumps({"data": [{"requestId": "XLK", "date": "2026-08-18",
                                 "fundFlows": 47558761.75}]})
    blocks = ff._tool_result_blocks(_stream_line(body) + "\n")
    check("tool_result block found", len(blocks) == 1, f"got {blocks}")
    obj = ff.resolve_payload(blocks[0])
    check("payload parses to the raw FactSet response",
          obj["data"][0]["fundFlows"] == 47558761.75, f"got {obj}")


def test_spilled_result_is_followed_to_disk():
    """The real 2026-08-19 case: a 500-row result never reaches the model at all.

    The MCP layer writes it to a file and hands back a pointer, which is exactly why asking
    the model to 'copy every value verbatim' could not work — it had nothing to copy from.
    """
    with tempfile.TemporaryDirectory() as d:
        spill = os.path.join(d, "tool-result.txt")
        with open(spill, "w") as fh:
            json.dump({"data": [{"requestId": "SPY", "date": "2025-08-19",
                                 "fundFlows": -1865645765.4}]}, fh)
        msg = (f"Error: result (75,593 characters across 3,510 lines) exceeds maximum "
               f"allowed tokens. Output has been saved to {spill}")
        obj = ff.resolve_payload(msg)
        check("spill pointer is followed", obj is not None and obj["data"][0]["requestId"] == "SPY",
              f"got {obj}")
        check("value read byte-exact from the file",
              obj["data"][0]["fundFlows"] == -1865645765.4)


def test_missing_spill_file_is_a_failure_not_empty():
    obj = ff.resolve_payload("Output has been saved to /nonexistent/nope.txt")
    check("unreadable spill -> None (a failure), never []", obj is None)


def test_no_tool_result_is_a_failure():
    """Returning [] when the call never happened would write a silent gap into history."""
    check("garbage transcript yields no blocks", ff._tool_result_blocks("not json\n") == [])
    check("prose payload does not resolve", ff.resolve_payload("I couldn't find that") is None)


def test_prompt_does_not_ask_the_model_to_echo_data():
    """The whole fix: the model makes the call, it does not retype 500 rows."""
    p = ff._prompt(["XLK"], "flows", "2026-08-01", "2026-08-19", 500, None)
    check("prompt pins the tool to a single call", "EXACTLY ONCE" in p)
    check("prompt asks only for DONE", "DONE" in p)
    for banned in ("VERBATIM", "JSON array", "Copy every value"):
        if banned in p:
            check("prompt no longer requests an echo of the data", False, f"found {banned!r}")
            return
    check("prompt no longer requests an echo of the data", True)


def test_frequency_is_correct_per_endpoint():
    seen = {}

    def runner(ids, data_type, start, end, limit, frequency):
        seen[data_type] = frequency
        return []

    for dt in ("flows", "prices", "aum"):
        ff.fetch_range(["XLK"], dt, "2026-08-01", "2026-08-19", runner)
    check("prices uses daily frequency", seen["prices"] == "D", f"got {seen.get('prices')}")
    check("aum uses monthly (no daily option exists)", seen["aum"] == "M",
          f"got {seen.get('aum')}")
    check("flows passes no frequency", seen["flows"] is None, f"got {seen.get('flows')}")


def test_prompt_carries_the_query_arguments():
    p = ff._prompt(["XLK", "SMH"], "prices", "2026-08-01", "2026-08-19", 500, "D")
    check("ids passed through", '"XLK"' in p and '"SMH"' in p)
    check("data_type passed through", "data_type: 'prices'" in p)
    check("frequency passed through when set", "frequency: 'D'" in p)
    check("frequency omitted for flows",
          "frequency" not in ff._prompt(["XLK"], "flows", "2026-08-01", "2026-08-19", 500, None))


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        print(f"\n{fn.__name__}:")
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
        return 1
    print(f"All checks passed ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
