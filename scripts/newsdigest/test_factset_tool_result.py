"""
The FactSet news runner reads the tool's OWN output from the stream-json transcript instead of
asking the model to echo rows back. That removed a transcription step that could reword, drop
or invent rows — and it is what makes the harness-stripping flags safe on an MCP job: if the
tool is not loaded, the model cannot fabricate a result, because we never read the model.

These tests pin the guard that carries that guarantee. Each case is a transcript shape that
was actually observed on 2026-09-07, not a hypothetical:

  * `--strict-mcp-config` unloads the server: the model calls ToolSearch (a well-formed
    tool_result saying "No matching deferred tools found") and answers with no data. That
    MUST raise ToolUnavailableError — "some tool_result exists" is not a sufficient check.
  * The tool runs and returns rows -> those exact rows, untouched.
  * The tool runs and returns {"data": []} -> a real empty, NOT an error.
  * The tool runs but the payload is an error string -> ValueError (a failure, not "no news").
  * fetch_batch must NOT split a ToolUnavailableError chunk per ticker: that would fire one
    doomed call per id and fail identically 30 times.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_factset_tool_result.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import factset_news as fn                              # noqa: E402
from newsdigest.identity import Identity                               # noqa: E402

FACTSET = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_UnstructuredContent"


def _line(role, blocks):
    return json.dumps({"type": role, "message": {"role": role, "content": blocks}})


def _tool_use(name):
    return {"type": "tool_use", "id": "t1", "name": name, "input": {}}


def _tool_result(text, is_error=None):
    b = {"type": "tool_result", "tool_use_id": "t1", "content": text}
    if is_error is not None:
        b["is_error"] = is_error
    return b


def transcript(*lines):
    return "\n".join(lines) + "\n"


ROWS = [{"documentID": "sa_1", "headline": "H1", "sentiment": "", "source": "SA",
         "storyDateTime": "2026-09-04T14:01:26", "viewUrl": "u1", "ids": ["NVDA-US"]},
        {"documentID": "sa_2", "headline": "H2", "sentiment": "Positive", "source": "SA",
         "storyDateTime": "2026-09-05T09:00:00", "viewUrl": "u2", "ids": ["AMD-US", "NVDA-US"]}]


def _runner_on(stdout, rc=0):
    """Build the production runner with subprocess faked to return `stdout`."""
    class _R:
        def __init__(self):
            self.stdout, self.returncode, self.stderr = stdout, rc, ""
    orig = fn.claude_p.subprocess.run
    fn.claude_p.subprocess.run = lambda *a, **k: _R()
    try:
        from datetime import datetime
        return fn.make_runner(datetime(2026, 9, 7, 7), ".")(["NVDA-US", "AMD-US"], 24, 50)
    finally:
        fn.claude_p.subprocess.run = orig


def test_strict_mcp_shape_raises_tool_unavailable():
    """Observed with --strict-mcp-config: ToolSearch x3, no FactSet call, prose answer."""
    t = transcript(
        _line("assistant", [_tool_use("ToolSearch")]),
        _line("user", [_tool_result("No matching deferred tools found")]),
        _line("assistant", [_tool_use("ToolSearch")]),
        _line("user", [_tool_result("")]),
        _line("assistant", [{"type": "text", "text": "The FactSet tool is not available."}]),
    )
    try:
        _runner_on(t)
    except fn.ToolUnavailableError:
        print("  ✓ ToolSearch-only transcript (tool unloaded) -> ToolUnavailableError, not []")
        return
    raise AssertionError("tool never ran but the runner returned instead of raising")


def test_real_rows_returned_untouched():
    """Observed with --setting-sources '' alone: ToolSearch once, then the real call."""
    t = transcript(
        _line("assistant", [_tool_use("ToolSearch")]),
        _line("user", [_tool_result("")]),
        _line("assistant", [_tool_use(FACTSET)]),
        _line("user", [_tool_result(json.dumps({"data": ROWS}))]),
        _line("assistant", [{"type": "text", "text": "DONE"}]),
    )
    rows, status = _runner_on(t)
    assert status == "ok" and rows == ROWS, rows
    print("  ✓ real payload -> the tool's own rows, byte-identical (ToolSearch noise skipped)")


def test_empty_data_is_a_real_empty_not_an_error():
    t = transcript(
        _line("assistant", [_tool_use(FACTSET)]),
        _line("user", [_tool_result(json.dumps({"data": []}))]),
        _line("assistant", [{"type": "text", "text": "DONE"}]),
    )
    rows, status = _runner_on(t)
    assert rows == [] and status == "ok"
    print("  ✓ {\"data\": []} -> [] (a legitimate empty window, not a failure)")


def test_error_payload_is_a_failure_not_empty():
    t = transcript(
        _line("assistant", [_tool_use(FACTSET)]),
        _line("user", [_tool_result("Error: upstream 503", is_error=True)]),
        _line("assistant", [{"type": "text", "text": "The tool errored."}]),
    )
    try:
        _runner_on(t)
    except ValueError:
        print("  ✓ tool ran but payload is an error string -> ValueError (never read as 'no news')")
        return
    raise AssertionError("error payload was accepted as data")


def test_model_prose_is_never_read_as_data():
    """The model's own text is not a data source, even when it looks like the old JSON echo."""
    t = transcript(
        _line("assistant", [_tool_use("ToolSearch")]),
        _line("user", [_tool_result("No matching deferred tools found")]),
        _line("assistant", [{"type": "text", "text": json.dumps(ROWS)}]),   # a fabricated echo
    )
    try:
        _runner_on(t)
    except fn.ToolUnavailableError:
        print("  ✓ a plausible JSON echo in model text with no tool call -> still ToolUnavailableError")
        return
    raise AssertionError("model prose was read as tool data — the fabrication path is open")


def test_fetch_batch_does_not_split_on_tool_unavailable():
    calls = []

    def runner(chunk, window, limit):
        calls.append(list(chunk))
        raise fn.ToolUnavailableError("no FactSet tool_use in transcript")

    idents = [Identity(f"T{i}", f"Name{i}", f"T{i}-US", "q") for i in range(30)]
    docs, failed = fn.fetch_batch(idents, 24, runner, chunk_size=30)
    assert docs == [] and len(failed) == 30, (docs, len(failed))
    assert len(calls) == 1, f"expected 1 call for an unloaded tool, got {len(calls)} (per-ticker split)"
    print(f"  ✓ ToolUnavailableError on a 30-id chunk -> 1 call, all 30 marked failed, no per-ticker storm")


def test_fetch_batch_still_splits_on_transient_error():
    """Regression guard for the case the new branch must NOT swallow: a transient failure
    still falls back per ticker so one bad id does not lose the chunk."""
    calls = []

    def runner(chunk, window, limit):
        calls.append(list(chunk))
        if len(chunk) > 1:
            raise RuntimeError("rc=1: transient")
        return ([{"documentID": f"d{chunk[0]}", "ids": [chunk[0]]}], "ok")

    idents = [Identity(f"T{i}", f"Name{i}", f"T{i}-US", "q") for i in range(3)]
    docs, failed = fn.fetch_batch(idents, 24, runner, chunk_size=3)
    assert len(docs) == 3 and not failed and len(calls) == 4, (len(docs), failed, len(calls))
    print("  ✓ transient RuntimeError still splits per ticker (1 batch + 3 singles), 0 failed")


def test_argv_pins_the_measured_flag_set():
    """The flag set is a MEASURED recipe, not a style choice (2026-09-07, 3-id chunk, per session):

        default harness, JSON echo (pre-2026-09-07 production)        ~100,000 prompt tokens
        --system-prompt + --setting-sources ""                          59,654
        + --tools ToolSearch                                            21,953   <- this
        + --tools ""  (drops ToolSearch -> EVERY MCP schema loads eagerly)  76,377
        + --tools <the FactSet tool name>  (same eager load)                76,374
        + --strict-mcp-config  (unloads the connector; tool never runs)  -> ToolUnavailableError

    `--tools ToolSearch` keeps ONLY the discovery tool, so the built-in tool schemas go and
    the connector tools stay deferred until the one ToolSearch fetch. Any drift in this argv
    silently costs 3-5x, so pin it."""
    captured = {}

    class _R:
        stdout, returncode, stderr = "", 0, ""

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return _R()
    orig = fn.claude_p.subprocess.run
    fn.claude_p.subprocess.run = fake_run
    try:
        from datetime import datetime
        try:
            fn.make_runner(datetime(2026, 9, 7, 7), ".")(["NVDA-US"], 24, 50)
        except fn.ToolUnavailableError:
            pass  # empty stdout -> no tool_use; expected. We only want the argv.
    finally:
        fn.claude_p.subprocess.run = orig
    cmd = captured["cmd"]

    def flag(name):
        assert name in cmd, f"missing {name}: {cmd}"
        return cmd[cmd.index(name) + 1]
    assert cmd[:2] == ["claude", "-p"]
    assert flag("--tools") == "ToolSearch", cmd
    assert flag("--setting-sources") == "", cmd
    assert flag("--system-prompt") == fn.SYSTEM_PROMPT
    assert flag("--allowedTools") == FACTSET
    assert flag("--output-format") == "stream-json" and "--verbose" in cmd
    assert "--strict-mcp-config" not in cmd, "that flag unloads the FactSet connector"
    assert cmd.count("--tools") == 1
    print("  ✓ argv carries --tools ToolSearch / --setting-sources '' / lean system prompt, no --strict-mcp-config")


if __name__ == "__main__":
    for t in (test_strict_mcp_shape_raises_tool_unavailable,
              test_real_rows_returned_untouched,
              test_empty_data_is_a_real_empty_not_an_error,
              test_error_payload_is_a_failure_not_empty,
              test_model_prose_is_never_read_as_data,
              test_fetch_batch_does_not_split_on_tool_unavailable,
              test_fetch_batch_still_splits_on_transient_error,
              test_argv_pins_the_measured_flag_set):
        t()
    print("\nALL PASS — tool_result guard: no fabrication path, no per-ticker storm on an unloaded tool.")
