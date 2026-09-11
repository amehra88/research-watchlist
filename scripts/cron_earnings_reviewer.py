#!/usr/bin/env python3
"""
Cron wrapper for scheduled earnings-reviewer runs.

Designed to run daily at 02:30 ET (moved from 06:30 on 2026-08-21 — see CLAUDE.md). Queries the earnings calendar for the last
24 hours via claude -p, intersects with the watchlist at config/watchlist.yaml,
invokes earnings-reviewer for each matched ticker. Logs STATUS markers per
invocation to logs/cron-earnings-reviewer.log.

Configuration is baked in (see CONFIG below). Modify in place if scope/window
changes.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# === Configuration ===

REPO_ROOT = Path("/root/research-watchlist")
CONTEXT_DIR = REPO_ROOT / "state" / "thesis" / "context"
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
    """
    Read watchlist.yaml, return all tickers across all three tiers as strings.

    Defensive: YAML can parse bare tokens like `ON`, `OFF`, `NO`, `Y`, etc. as
    booleans. We require all ticker values to be strings. If a non-string ticker
    is encountered, we raise loudly rather than silently coercing — the watchlist
    author should quote the ticker in YAML.
    """
    with WATCHLIST_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    tickers: list[str] = []
    bad: list[tuple[str, object]] = []
    for tier in TIERS:
        for entry in data.get(tier, []) or []:
            ticker = entry.get("ticker")
            if ticker is None:
                continue
            if not isinstance(ticker, str):
                bad.append((tier, ticker))
                continue
            # `.pvt` ids are private companies with no filings and no transcripts. CLAUDE.md calls
            # the ticker-only gate here deliberate and load-bearing; it was previously enforced only
            # by the [A-Z]+ regexes downstream, which this loader never applied. simaai.pvt
            # (2026-08-19) is the first .pvt to sit in a tier block, so the gate is made explicit.
            if ticker.endswith(".pvt"):
                continue
            tickers.append(ticker)
    if bad:
        details = "; ".join(f"{tier}: {t!r} ({type(t).__name__})" for tier, t in bad)
        raise ValueError(
            f"Watchlist contains non-string ticker(s) — YAML parsed them as something else. "
            f"Quote the value in watchlist.yaml. Offenders: {details}"
        )
    return sorted(set(tickers))

CHEAP_MODEL = "claude-sonnet-4-6"   # for mechanical JSON lookups, not the review itself

# Measured 2026-09-07 on a day with NO reporting tickers: 62s, 95s, 100s, 118s.
# The old 180s ceiling left under 2x margin on the CHEAPEST possible case, and the
# query costs strictly more as tickers actually report (more MCP calls) — which is
# why rc=124 aborts clustered on active days (08-30, 09-06, 09-07), each zeroing
# out the whole run. One retry covers ordinary variance; a persistent failure still
# aborts rather than silently reporting an empty calendar.
CALENDAR_TIMEOUT_S = 600
CALENDAR_ATTEMPTS = 2


def _claude_env() -> dict:
    """Strip ANTHROPIC_API_KEY so claude -p stays on subscription auth."""
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def run_claude(prompt: str, timeout_seconds: int = 300,
               model: str | None = None) -> tuple[int, str, str]:
    """
    Invoke claude -p with the given prompt and the project's allowed tools.
    Returns (returncode, stdout, stderr). Captures combined stream into stdout.

    model=None inherits the account default (Opus) — correct for the earnings review,
    which is the analytical work product. Pass CHEAP_MODEL for mechanical lookups.
    """
    cmd = [
        "claude", "-p", prompt,
        "--allowedTools", ALLOWED_TOOLS,
    ]
    if model:
        cmd += ["--model", model]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(REPO_ROOT),
            env=_claude_env(),
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
    for attempt in range(1, CALENDAR_ATTEMPTS + 1):
        rc, stdout, stderr = run_claude(prompt, timeout_seconds=CALENDAR_TIMEOUT_S,
                                        model=CHEAP_MODEL)
        if rc == 0:
            break
        log_write(f"  CALENDAR_QUERY_FAILED rc={rc} attempt={attempt}/{CALENDAR_ATTEMPTS} "
                  f"stderr={stderr[:200]}")
        if attempt == CALENDAR_ATTEMPTS:
            return None
    # Find the JSON array in the response. Strip whitespace and any leading/trailing prose.
    # Symbols may carry digits, dots or dashes (2308.TW, 000660.KS, UMG.AS, BRK.B): a single
    # such entry used to make the whole array unmatchable and abort the run (2026-07-29/31,
    # 09-10). The watchlist filter in main() is what drops non-watchlist names, not this regex.
    match = re.search(r"\[\s*(?:\"[A-Z0-9.\-]+\"\s*,?\s*)*\]", stdout)
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

def infer_outcome_from_artifacts(ticker: str, run_started_at: datetime) -> str | None:
    """
    When the agent didn't emit a STATUS marker, inspect artifacts to determine
    what actually happened. Returns a synthesized STATUS marker, or None if
    artifacts are inconclusive (true error case).

    Detection logic:
    - State file mtime newer than run_started_at AND note file present → new-note-written
    - State file present but mtime older than run_started_at → no-new-transcript (idempotency held silently)
    - State file missing entirely → cannot infer; return None
    """
    state_path = REPO_ROOT / "state" / "transcripts" / f"{ticker}.json"
    if not state_path.exists():
        return None

    state_mtime = datetime.fromtimestamp(state_path.stat().st_mtime, tz=timezone.utc)
    if state_mtime < run_started_at:
        # State exists but wasn't touched this run — idempotency exit
        try:
            with state_path.open("r", encoding="utf-8") as f:
                state = json.load(f)
            iacc = state.get("last_iacc", "unknown")
            ts = state.get("last_processed_at", "unknown")
            return f"STATUS: no-new-transcript ticker={ticker} last_iacc={iacc} last_processed_at={ts}"
        except (json.JSONDecodeError, OSError):
            return f"STATUS: no-new-transcript ticker={ticker} last_iacc=unreadable last_processed_at=unreadable"

    # State was touched this run — look for a fresh note
    try:
        with state_path.open("r", encoding="utf-8") as f:
            state = json.load(f)
        iacc = state.get("last_iacc", "unknown")
        period = state.get("last_period", "unknown")
        note_path = state.get("last_note_path", "unknown")
    except (json.JSONDecodeError, OSError):
        return None
    return f"STATUS: new-note-written ticker={ticker} period={period} iacc={iacc} path={note_path}"

def build_prompt(ticker: str) -> str:
    return (f"Use the earnings-reviewer agent to review {ticker}'s latest earnings call. "
            f"Before Step 4, Read state/thesis/context/{ticker}.md if it exists — it carries the open thesis "
            f"assumptions and the guidance track record for Section 4b and Section 8.")


def write_context(ticker: str) -> Path:
    """Pre-stage: the agent has no Bash/DB, so the wrapper hands it thesis + Store B facts as a file.

    Queries `metrics` + `metrics_credibility` directly — never the `guidance_with_track_record`
    view, which fans out to ~30k rows per ticker."""
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# Context for {ticker} (generated {datetime.now(timezone.utc).isoformat(timespec='seconds')})", ""]
    th = REPO_ROOT / "notes" / ticker / "_thesis.md"
    if th.exists():
        parts = th.read_text(encoding="utf-8").split("---\n", 2)
        fm_text = parts[1] if len(parts) >= 2 else ""
        lines += [f"## Open thesis assumptions (from notes/{ticker}/_thesis.md)", "```yaml", fm_text.rstrip(), "```", ""]
    else:
        lines += ["## Thesis", f"No thesis file for {ticker} (not a T1/T2 name or not yet drafted). Section 4b reads 'no thesis file'.", ""]
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
        from pgconn import connect
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""SELECT metric, period, guidance_mid, consensus_at_guide, actual, consensus_at_print, beat_vs_guidance, beat_vs_guidance_pct
                           FROM metrics WHERE ticker=%s AND (actual IS NOT NULL OR guidance_mid IS NOT NULL) ORDER BY fiscal_end DESC NULLS LAST LIMIT 12""", (ticker,))
            rows = cur.fetchall()
            cur.execute("SELECT metric, score FROM metrics_credibility WHERE ticker=%s", (ticker,))
            cred = cur.fetchall()
        lines += ["## Guidance track record (Store B, last 12 rows)", "| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |", "|---|---|---|---|---|---|---|---|"]
        lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |" for r in rows]
        if not rows:
            lines.append("| (no Store B rows for this ticker) | | | | | | | |")
        lines += ["", "## Credibility scores"] + ([f"- {m}: {json.dumps(sc, default=str)}" for m, sc in cred] or ["- none"])
    except Exception as e:  # noqa: BLE001 — context is best-effort; the review must not fail on pg
        lines += ["## Guidance track record", f"unavailable: {type(e).__name__}: {e}"]
    p = CONTEXT_DIR / f"{ticker}.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def run_earnings_reviewer(ticker: str, run_started_at: datetime) -> str:
    """
    Invoke earnings-reviewer for one ticker. Returns the STATUS marker line.

    Primary detection: parse STATUS marker from agent stdout (the contract).
    Fallback detection: if no marker, inspect artifacts (note file, state file)
    for changes since this run started. This catches the case where the agent
    completed real work but skipped emitting the marker.
    """
    try:
        ctx = write_context(ticker)
        log_write(f"  CONTEXT_WRITTEN {ctx.relative_to(REPO_ROOT)}")
    except Exception as e:  # noqa: BLE001
        log_write(f"  CONTEXT_FAILED {ticker} err={type(e).__name__}: {e}")
    prompt = build_prompt(ticker)
    rc, stdout, stderr = run_claude(prompt, timeout_seconds=900)  # 15 minutes per ticker

    if rc != 0:
        return f"STATUS: error reason=invocation-failed detail=rc={rc} stderr={stderr[:150]!r}"

    # Primary path: STATUS marker in stdout (the contract)
    marker = extract_status(stdout)
    if marker:
        return marker

    # Fallback: inspect artifacts to infer outcome
    fallback = infer_outcome_from_artifacts(ticker, run_started_at)
    if fallback:
        return fallback + " | fallback=artifact-inspection (agent did not emit marker)"

    # Neither marker nor artifact change — true error
    return f"STATUS: error reason=no-marker-emitted detail=stdout_tail={stdout[-200:]!r}"

# === Main ===

def main() -> int:
    run_started_at = datetime.now(timezone.utc)
    log_section(f"CRON RUN {run_started_at.isoformat(timespec='seconds')}")

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
        marker = run_earnings_reviewer(ticker, run_started_at)
        log_write(f"  {marker}")
        if marker.startswith("STATUS: error"):
            error_count += 1

    log_write(f"  CRON_RUN_SUMMARY processed={len(to_process)} errors={error_count}")
    return 1 if error_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
