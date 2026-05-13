#!/usr/bin/env python3
"""
Cron wrapper for scheduled earnings-reviewer runs.

Designed to run daily at 6:30am ET. Queries the earnings calendar for the last
24 hours via claude -p, intersects with the watchlist at config/watchlist.yaml,
invokes earnings-reviewer for each matched ticker. Logs STATUS markers per
invocation to logs/cron-earnings-reviewer.log.

Configuration is baked in (see CONFIG below). Modify in place if scope/window
changes.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# === Configuration ===

REPO_ROOT = Path("/root/research-watchlist")
WATCHLIST_PATH = REPO_ROOT / "config" / "watchlist.yaml"  # symlink to /root/research/config/watchlist.yaml
LOG_PATH = REPO_ROOT / "logs" / "cron-earnings-reviewer.log"
WINDOW_HOURS = 24  # earnings calendar lookback window
ALLOWED_TOOLS = (
    "Read,Write,Edit,Glob,Grep,"
    "mcp__claude_ai_InsiderScore__*,"
    "mcp__claude_ai_FactSet_AI-Ready_Data__*"
)
TIERS = ("tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist")

# === Helpers ===

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log_write(line: str) -> None:
    """Append a single line to the log file with newline. Creates file if missing."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")

def log_section(header: str) -> None:
    """Write a visually prominent section header in the log."""
    bar = "=" * 70
    log_write("")
    log_write(bar)
    log_write(header)
    log_write(bar)

def load_watchlist_tickers() -> list[str]:
    """Read watchlist.yaml, return all tickers across all three tiers."""
    with WATCHLIST_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    tickers: list[str] = []
    for tier in TIERS:
        for entry in data.get(tier, []) or []:
            ticker = entry.get("ticker")
            if ticker:
                tickers.append(ticker)
    return sorted(set(tickers))

def run_claude(prompt: str, timeout_seconds: int = 300) -> tuple[int, str, str]:
    """
    Invoke claude -p with the given prompt and the project's allowed tools.
    Returns (returncode, stdout, stderr). Captures combined stream into stdout.
    """
    cmd = [
        "claude", "-p", prompt,
        "--allowedTools", ALLOWED_TOOLS,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(REPO_ROOT),
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", f"TIMEOUT after {timeout_seconds}s: {e.stderr or ''}"

def query_calendar(watchlist_tickers: list[str]) -> list[str] | None:
    """
    Ask Claude what tickers in our watchlist reported in the last WINDOW_HOURS.
    Expects a strict JSON array response. Returns the list of ticker strings,
    or None if the query failed or response was unparseable.
    """
    prompt = (
        f"Query the earnings calendar for the {WINDOW_HOURS}-hour window ending now. "
        f"Identify which of the following watchlist tickers reported earnings in that window: "
        f"{', '.join(watchlist_tickers)}.\n\n"
        "Return ONLY a JSON array of the ticker symbols that reported. No prose, no markdown, "
        "no code fences, no explanation. Just a JSON array. Empty array if none reported. "
        "Example output for a day where NVDA and AMD reported: [\"NVDA\", \"AMD\"]. "
        "Example output for a day with no reports: []."
    )
    rc, stdout, stderr = run_claude(prompt, timeout_seconds=180)
    if rc != 0:
        log_write(f"  CALENDAR_QUERY_FAILED rc={rc} stderr={stderr[:200]}")
        return None
    # Find the JSON array in the response. Strip whitespace and any leading/trailing prose.
    match = re.search(r"\[\s*(?:\"[A-Z]+\"\s*,?\s*)*\]", stdout)
    if not match:
        log_write(f"  CALENDAR_QUERY_UNPARSEABLE response={stdout[:300]!r}")
        return None
    try:
        tickers = json.loads(match.group(0))
        if not isinstance(tickers, list) or not all(isinstance(t, str) for t in tickers):
            log_write(f"  CALENDAR_QUERY_BAD_SHAPE parsed={tickers!r}")
            return None
        return tickers
    except json.JSONDecodeError as e:
        log_write(f"  CALENDAR_QUERY_JSON_ERROR err={e} match={match.group(0)!r}")
        return None

def extract_status(stdout: str) -> str:
    """Extract the last STATUS: line from agent stdout. Returns the marker line, or '' if not found."""
    status_lines = [line for line in stdout.splitlines() if line.startswith("STATUS:")]
    return status_lines[-1].strip() if status_lines else ""

def run_earnings_reviewer(ticker: str) -> str:
    """Invoke earnings-reviewer for one ticker. Returns the STATUS marker line, or an error marker."""
    prompt = f"Use the earnings-reviewer agent to review {ticker}'s latest earnings call."
    rc, stdout, stderr = run_claude(prompt, timeout_seconds=900)  # 15 minutes per ticker
    if rc != 0:
        return f"STATUS: error reason=invocation-failed detail=rc={rc} stderr={stderr[:150]!r}"
    marker = extract_status(stdout)
    if not marker:
        return f"STATUS: error reason=no-marker-emitted detail=stdout_tail={stdout[-200:]!r}"
    return marker

# === Main ===

def main() -> int:
    log_section(f"CRON RUN {now_iso()}")

    # Load watchlist
    try:
        watchlist = load_watchlist_tickers()
        log_write(f"  Loaded {len(watchlist)} tickers from watchlist")
    except Exception as e:
        log_write(f"  WATCHLIST_LOAD_FAILED err={e}")
        return 1

    # Query calendar
    log_write(f"  Querying earnings calendar (window={WINDOW_HOURS}h)")
    reported = query_calendar(watchlist)
    if reported is None:
        log_write("  ABORT: calendar query failed; no tickers processed this run")
        return 1
    log_write(f"  Calendar returned {len(reported)} ticker(s): {reported}")

    # Intersect with watchlist (defense; Claude should have already filtered)
    watchlist_set = set(watchlist)
    to_process = [t for t in reported if t in watchlist_set]
    dropped = [t for t in reported if t not in watchlist_set]
    if dropped:
        log_write(f"  Dropped {len(dropped)} non-watchlist ticker(s): {dropped}")

    if not to_process:
        log_write("  No watchlist tickers reported in window; exiting cleanly")
        log_write(f"  CRON_RUN_SUMMARY processed=0 errors=0")
        return 0

    # Process each ticker
    log_write(f"  Processing {len(to_process)} ticker(s)")
    error_count = 0
    for ticker in to_process:
        log_write(f"  --- {ticker} ---")
        marker = run_earnings_reviewer(ticker)
        log_write(f"  {marker}")
        if marker.startswith("STATUS: error"):
            error_count += 1

    log_write(f"  CRON_RUN_SUMMARY processed={len(to_process)} errors={error_count}")
    return 1 if error_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
