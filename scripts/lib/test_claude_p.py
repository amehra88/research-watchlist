"""Pins for scripts/lib/claude_p.py. No pytest here: python3 scripts/lib/test_claude_p.py

The argv shapes are MEASURED recipes (see the module docstring); a drift costs 3-30x
silently because the call still succeeds. So the tests pin the exact flags.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claude_p  # noqa: E402

TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_FundsETF"


def _flag(cmd, name):
    assert name in cmd, f"missing {name}: {cmd}"
    return cmd[cmd.index(name) + 1]


def test_lean_mode_argv():
    cmd = claude_p.build_cmd("hi", system_prompt="sp", model="m")
    assert _flag(cmd, "--tools") == "" and _flag(cmd, "--setting-sources") == ""
    assert "--strict-mcp-config" in cmd and _flag(cmd, "--output-format") == "json"
    print("  ✓ lean argv")


def test_mcp_lean_mode_argv():
    cmd = claude_p.build_cmd("hi", mcp_tool=TOOL, system_prompt="sp", model="m")
    assert cmd[:2] == ["claude", "-p"]
    assert _flag(cmd, "--allowedTools") == TOOL
    assert _flag(cmd, "--tools") == "ToolSearch", cmd          # NOT "" (76K), NOT the tool name (76K)
    assert _flag(cmd, "--setting-sources") == ""
    assert _flag(cmd, "--system-prompt") == "sp"
    assert _flag(cmd, "--output-format") == "stream-json" and "--verbose" in cmd
    assert "--strict-mcp-config" not in cmd, "unloads the claude.ai connector"
    assert _flag(cmd, "--model") == "m"
    print("  ✓ mcp-lean argv: --tools ToolSearch, no --strict-mcp-config, stream-json")


def test_modes_are_exclusive():
    for kw in ({}, {"system_prompt": "s", "tools": "t"}, {"mcp_tool": "t"},
               {"mcp_tool": "t", "tools": "t", "system_prompt": "s"}):
        try:
            claude_p.build_cmd("hi", **kw)
        except ValueError:
            continue
        raise AssertionError(f"build_cmd accepted {kw}")
    print("  ✓ exactly one mode: system_prompt | tools | mcp_tool+system_prompt")


def _line(role, blocks):
    return json.dumps({"type": role, "message": {"role": role, "content": blocks}})


def test_tool_was_called():
    ts = _line("assistant", [{"type": "tool_use", "id": "1", "name": "ToolSearch", "input": {}}])
    miss = _line("user", [{"type": "tool_result", "tool_use_id": "1",
                           "content": "No matching deferred tools found"}])
    hit = _line("assistant", [{"type": "tool_use", "id": "2", "name": TOOL, "input": {}}])
    assert not claude_p.tool_was_called("\n".join([ts, miss]), TOOL)
    assert claude_p.tool_was_called("\n".join([ts, miss, hit]), TOOL)
    assert not claude_p.tool_was_called("", TOOL) and not claude_p.tool_was_called("garbage\n{", TOOL)
    assert issubclass(claude_p.ToolUnavailableError, RuntimeError)
    print("  ✓ tool_was_called: a well-formed ToolSearch miss is NOT a call; the named tool_use is")


if __name__ == "__main__":
    for t in (test_lean_mode_argv, test_mcp_lean_mode_argv, test_modes_are_exclusive,
              test_tool_was_called):
        t()
    print("\nALL PASS")
