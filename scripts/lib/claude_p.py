"""Shared `claude -p` invocation wrapper: lean (tool-less) and MCP modes.

WHY THIS EXISTS
---------------
Every `claude -p` call loads the Claude Code harness into the prompt: the agent
system prompt, built-in tool schemas, plugin/skill listings, CLAUDE.md and memory.
Measured 2026-09-07 on this droplet with a trivial prompt ("Reply with exactly: OK"),
summing input + cache_creation + cache_read from the JSON envelope:

    default (what these jobs used before, incl. `--allowedTools ""`)   30,950
    `--allowedTools ""` alone                    no change (gates permissions, not schemas)
    `--setting-sources ""` alone                                       24,527
    `--system-prompt "<tiny>"` alone                                   24,436
    `--tools none`   <- INVALID VALUE, inflates                        88,150
    `--system-prompt` + `--setting-sources ""` + `--strict-mcp-config`  16,108
    the above + `--tools ""`                                            2,621

Validated on the production SEC theme-tagging prompt: 31,112 -> 2,792 tokens with
byte-identical output. The documented way to drop tool schemas is `--tools ""`;
`--tools none` is not a valid value and is a ~3x regression, so never use it.

These jobs run on SUBSCRIPTION auth (ANTHROPIC_API_KEY is stripped), so the payoff
is not dollars — it is headroom in the 5-hour rolling quota. Exhausting that window
is what cut the news digest to 40 of 256 stories.

TWO MODES
---------
lean mode (`system_prompt=`) — for tool-less text->JSON and text->text jobs.
    Strips the harness. Requires a task-specific system prompt: replacing the
    default preamble means the prompt must carry its own instructions.

mcp mode (`tools=`) — for jobs that call an MCP tool (FactSet, InsiderScore).
    Keeps settings and plugin config loaded, because the MCP servers come from
    the plugin marketplace in settings.json. Stripping settings here would NOT
    error — the model would lose the tool and answer from memory, writing
    plausible-looking but fabricated data downstream. Never put an MCP job in
    lean mode.

mcp-lean mode (`mcp_tool=` + `system_prompt=`) — `run_mcp()`; used by
    newsdigest/factset_news.py, etfflows/factset_flows.py, etfflows/lookthrough.py.
    An MCP job CAN drop most of the harness if, and only if, it reads the raw
    tool_result from a stream-json transcript and verifies the tool_use happened
    (so an unloaded tool is a hard error, not a fabricated answer). Measured
    2026-09-07 on the news pull, per session of 3 API turns:

        default                                          ~100,000 prompt tokens
        --system-prompt + --setting-sources ""              59,654
        + --tools ToolSearch                                21,953   <- use this
        + --tools "" or --tools <mcp tool name>             ~76,400  (all schemas eager)
        + --strict-mcp-config                               tool unloaded, never runs

    `--setting-sources ""` alone does NOT unload the claude.ai connectors —
    `--strict-mcp-config` is the flag that does. `--tools ToolSearch` keeps only
    the discovery tool (the deferred-schema round-trip is the floor; there is no
    documented single-tool preload, and ENABLE_TOOL_SEARCH=false is the 76K case).
"""
from __future__ import annotations

import json
import os
import subprocess

# A lean-mode call should carry ~2.6-3K tokens of wrapper on top of its payload.
# If the flags ever stop taking effect (a CLI change, an arg-parsing quirk that
# swallows the empty `--tools` value), the call still SUCCEEDS — it just silently
# costs ~31K again. Fail loudly instead of regressing quietly.
#
# The envelope reports total prompt tokens, not wrapper alone, so the guard checks
# total MINUS an estimate of the payload.
#
# The divisor is deliberately CONSERVATIVE (it over-estimates payload tokens, which
# under-estimates overhead and biases the guard toward staying silent). Measured over
# real production prompts on 2026-09-07, English prose mixed with tickers, JSON and
# comma-separated vocabularies runs 1.98-3.37 chars/token — nowhere near 4:
#
#     sec tagger      2.14 - 2.47      news summarize  1.98 - 2.19
#     news classify   2.11 - 3.37      news rank       2.67 - 2.90
#
# At chars/4 the largest real ranking prompt (83,558 chars) scored an apparent
# overhead of 13,028 against this 12,000 ceiling — a FALSE TRIP that would have hard-
# failed the digest on a call that was behaving perfectly. Biasing the other way costs
# nothing, because the signal this guard exists to catch is the ~28K harness returning:
# with the flags dead, overhead lands ~20-29K on these same prompts, still far above
# the ceiling. Under-estimating payload is what makes the guard fragile; over-
# estimating it only makes the guard more conservative.
LEAN_WRAPPER_CEILING = 12000
_CHARS_PER_TOKEN = 2

DEFAULT_TIMEOUT_S = 300


class ClaudeWrapperRegression(RuntimeError):
    """Lean-mode call exceeded the wrapper ceiling — flags are not taking effect."""


class ToolUnavailableError(RuntimeError):
    """mcp-lean: the transcript has no tool_use naming the MCP tool — it was never called.

    This is what a mis-set flag produces (e.g. `--strict-mcp-config` unloading the
    connector): the model cannot see the tool, so it answers without data. It is NOT an
    empty result and NOT transient — retrying, or splitting a batch per id, fails the same
    way N more times. Callers should fail the whole unit of work at once.
    """


# One system prompt for every mcp-lean job: the model's only job is to make the call.
# The data is read from the tool_result, never from the reply.
MCP_SYSTEM_PROMPT = (
    "You are a data-retrieval backend. Call the tool you are told to call, exactly once, with "
    "exactly the arguments given, then reply DONE. Do not summarise or restate the tool output."
)


def claude_env() -> dict:
    """Environment with ANTHROPIC_API_KEY stripped, forcing subscription auth."""
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def build_cmd(prompt: str, *, system_prompt: str | None = None,
              tools: str | None = None, mcp_tool: str | None = None,
              model: str | None = None, output_format: str = "json",
              extra: list[str] | None = None) -> list[str]:
    """Build the argv for a `claude -p` call. Exactly one mode:

        lean      system_prompt=                 tool-less text->text/JSON
        mcp       tools=                         full harness, MCP tool allowed (legacy)
        mcp-lean  mcp_tool= + system_prompt=     stream-json transcript, raw tool_result
    """
    lean = system_prompt is not None and tools is None and mcp_tool is None
    mcp = tools is not None and system_prompt is None and mcp_tool is None
    mcp_lean = mcp_tool is not None and system_prompt is not None and tools is None
    if sum((lean, mcp, mcp_lean)) != 1:
        raise ValueError("pass exactly one of system_prompt= (lean), tools= (mcp), "
                         "or mcp_tool=+system_prompt= (mcp-lean)")

    if mcp_lean:
        # `--verbose` is what makes stream-json carry the tool_use/tool_result blocks.
        # `--tools ToolSearch`, NOT "" and NOT the MCP tool's name: both of those drop the
        # deferral and load every connector's schemas eagerly (~76K). No --strict-mcp-config.
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--allowedTools", mcp_tool,
               "--system-prompt", system_prompt,
               "--setting-sources", "",
               "--tools", "ToolSearch"]
    elif lean:
        cmd = ["claude", "-p", prompt, "--output-format", output_format]
        # Flag order matters: `--tools` is variadic, so keep its empty value
        # immediately followed by another flag rather than trailing the argv.
        cmd += ["--system-prompt", system_prompt,
                "--tools", "",
                "--setting-sources", "",
                "--strict-mcp-config"]
    else:
        cmd = ["claude", "-p", prompt, "--output-format", output_format,
               "--allowedTools", tools]
    if model:
        cmd += ["--model", model]
    if extra:
        cmd += extra
    return cmd


def wrapper_tokens(envelope: dict) -> int:
    """Total prompt tokens (fresh + cache write + cache read) from a JSON envelope."""
    u = envelope.get("usage") or {}
    return (u.get("input_tokens", 0)
            + u.get("cache_creation_input_tokens", 0)
            + u.get("cache_read_input_tokens", 0))


def run(prompt: str, *, system_prompt: str | None = None, tools: str | None = None,
        model: str | None = None, cwd: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_S, check_wrapper: bool = True,
        precheck=None, extra: list[str] | None = None) -> tuple[str, float, dict]:
    """Run `claude -p` and return (result_text, cost_usd, envelope).

    Raises RuntimeError on rc!=0 or an is_error envelope. Callers keep their own
    session-limit / auth-failure classification on top of that — this wrapper
    deliberately does not swallow those, since each job maps them differently.

    `precheck` is a callable invoked with the raw stdout BEFORE the returncode is
    examined. This ordering is load-bearing, not stylistic: a subscription 429 can
    arrive either with rc!=0 or as an is_error envelope, and it must map to the
    caller's non-retryable SessionLimitError rather than a generic RuntimeError
    (see classify_llm._detect_session_limit). A precheck that raises wins.
    """
    cmd = build_cmd(prompt, system_prompt=system_prompt, tools=tools,
                    model=model, extra=extra)
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout, cwd=cwd, env=claude_env())
    if precheck is not None:
        precheck(result.stdout)
    if result.returncode != 0:
        # Auth/usage errors land on STDOUT (stderr is usually empty) — log both.
        raise RuntimeError(f"claude -p rc={result.returncode} "
                           f"stderr={result.stderr[:200]!r} stdout={result.stdout[:800]!r}")
    envelope = json.loads(result.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude -p is_error: {str(envelope.get('result'))[:200]}")

    if check_wrapper and system_prompt is not None:
        total = wrapper_tokens(envelope)
        payload_est = (len(prompt) + len(system_prompt)) // _CHARS_PER_TOKEN
        overhead = total - payload_est
        if overhead > LEAN_WRAPPER_CEILING:
            raise ClaudeWrapperRegression(
                f"lean-mode wrapper was ~{overhead} tokens (ceiling {LEAN_WRAPPER_CEILING}; "
                f"total={total}, payload_est={payload_est}). The harness-stripping flags "
                f"are not taking effect — a `claude` CLI change is the likely cause. "
                f"Re-measure before letting this run at ~10x cost.")

    return (envelope.get("result", ""),
            float(envelope.get("total_cost_usd", 0.0) or 0.0),
            envelope)


def tool_was_called(stdout: str, tool_name: str) -> bool:
    """True iff a stream-json transcript contains a tool_use block naming `tool_name`.

    Presence of SOME tool_result is not enough: when the connector is missing the model
    reaches for ToolSearch instead, and ToolSearch's "No matching deferred tools found" is
    a perfectly well-formed tool_result. The invocation itself is what has to be checked.
    """
    for line in (stdout or "").splitlines():
        try:
            ev = json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        content = (ev.get("message") or {}).get("content") if isinstance(ev, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" \
                    and block.get("name") == tool_name:
                return True
    return False


def run_mcp(prompt: str, *, mcp_tool: str, system_prompt: str = MCP_SYSTEM_PROMPT,
            model: str | None = None, cwd: str | None = None,
            timeout: int = DEFAULT_TIMEOUT_S) -> str:
    """mcp-lean call. Returns the raw stream-json transcript (stdout) for the caller to
    read tool_result blocks from. Raises RuntimeError on rc!=0 and ToolUnavailableError
    if the named tool was never invoked — never returns a transcript the caller could
    misread as "the tool returned nothing".
    """
    cmd = build_cmd(prompt, mcp_tool=mcp_tool, system_prompt=system_prompt, model=model)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                            cwd=cwd, env=claude_env())
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} "
                           f"stderr={(result.stderr or '').strip()[:200]!r}")
    stdout = result.stdout or ""
    if not tool_was_called(stdout, mcp_tool):
        raise ToolUnavailableError(
            f"no {mcp_tool.rsplit('__', 1)[-1]} tool_use in transcript — the tool was never "
            f"called: {stdout.strip()[-200:]}")
    return stdout
