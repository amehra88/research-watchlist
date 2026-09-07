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
# total MINUS an estimate of the payload. The estimate is crude (chars/4), but it
# only has to separate ~2.6K from ~31K — a 28K gap that dwarfs tokenization error.
LEAN_WRAPPER_CEILING = 12000
_CHARS_PER_TOKEN = 4

DEFAULT_TIMEOUT_S = 300


class ClaudeWrapperRegression(RuntimeError):
    """Lean-mode call exceeded the wrapper ceiling — flags are not taking effect."""


def claude_env() -> dict:
    """Environment with ANTHROPIC_API_KEY stripped, forcing subscription auth."""
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def build_cmd(prompt: str, *, system_prompt: str | None = None,
              tools: str | None = None, model: str | None = None,
              output_format: str = "json", extra: list[str] | None = None) -> list[str]:
    """Build the argv for a `claude -p` call.

    Exactly one of `system_prompt` (lean mode) or `tools` (mcp mode) must be given.
    """
    if (system_prompt is None) == (tools is None):
        raise ValueError("pass exactly one of system_prompt= (lean) or tools= (mcp)")

    cmd = ["claude", "-p", prompt, "--output-format", output_format]
    if system_prompt is not None:
        # Flag order matters: `--tools` is variadic, so keep its empty value
        # immediately followed by another flag rather than trailing the argv.
        cmd += ["--system-prompt", system_prompt,
                "--tools", "",
                "--setting-sources", "",
                "--strict-mcp-config"]
    else:
        cmd += ["--allowedTools", tools]
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
