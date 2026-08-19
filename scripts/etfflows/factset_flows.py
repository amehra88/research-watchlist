"""
factset_flows — the only route to FactSet fund data from this box.

There is NO FactSet REST API and no credentials here, so every pull shells out to
`claude -p --allowedTools mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_FundsETF`. The model
is a VERBATIM TRANSPORT, not an analyst: Python owns chunking, date-splitting and the
saturation retry. This mirrors scripts/newsdigest/factset_news.py deliberately — that path
is proven and the failure modes are already understood.

THE ROW CAP IS THE THING THAT BITES. `limit` maxes at 500 ROWS, and rows = ids x trading
days. A 10-ticker chunk therefore covers only ~50 trading days per call, which is why the
3-year backfill is a ~52-call one-shot and not the "~5 calls" that steady-state daily
operation costs. Chunking happens on BOTH axes.

Endpoints used (all verified live 2026-08-19 against XLK/VOO):
  flows  -> {fsymId, requestId, fundFlows, currency, date}
  prices -> {fsymId, requestId, date, currency, price, firstNAVDate}     frequency=D
  aum    -> {fsymId, requestId, fundLevelAUM, shareClassAUMReported,
             shareClassAUMActual, currency, numberOfSharesOutstanding, date}   frequency=M

`requestId` echoes the ticker we asked for, so batches demux from the data rather than from
call ordering.

NULL IS NOT ZERO. Today's row comes back with a null value until T+1. We preserve None and
let metrics.py decide; writing 0.0 here would silently drag every rolling window down.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import date, timedelta

from . import FACTSET_CHUNK_SIZE, FACTSET_RESULT_LIMIT, FACTSET_TIMEOUT_SECONDS

_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_FundsETF"
MODEL = "claude-sonnet-4-6"   # matches the newsdigest transport

# Calendar days per trading day, with headroom. 252/365 -> ~1.449; we plan spans with this
# and still verify against the row cap, because a wrong guess here silently truncates history.
_CALENDAR_PER_TRADING = 1.45

# Which field carries the value we want, per endpoint. shareClassAUMReported is deliberate:
# fundLevelAUM would understate VOO by ~41% (verified $1.70T vs $994B, 2026-07-31).
VALUE_FIELD = {
    "flows": "fundFlows",
    "prices": "price",
    "aum": "shareClassAUMReported",
}

# Rows each endpoint returns per year, which is what the 500-row cap actually bounds.
# `aum` is month-end only (the tool's frequency enum has no daily option), so planning it
# at 252 would cost ~24x more calls than it needs.
ROWS_PER_YEAR = {"flows": 252, "prices": 252, "aum": 12}

# Fraction of the row cap a planned chunk aims to fill. See date_chunks.
CHUNK_FILL_TARGET = 0.8


def _claude_env() -> dict:
    """Strip ANTHROPIC_API_KEY so `claude -p` stays on subscription auth.

    Copied verbatim rather than imported — the repo convention is to copy it (it appears
    identically in five files) so no module grows a dependency on newsdigest internals.
    """
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def _extract_json_array(text: str):
    """Pull the first top-level JSON array out of claude's stdout."""
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _prompt(ids, data_type: str, start: str, end: str, limit: int,
            frequency: str | None) -> str:
    """Ask the model to MAKE THE CALL and nothing else.

    It deliberately does NOT ask for the data back — see make_runner. Asking the model to
    echo rows was slow, lossy, and impossible above ~500 rows because the payload never
    reaches it in the first place.
    """
    freq_line = f"  frequency: '{frequency}'\n" if frequency else ""
    return (
        f"Call the FactSet_FundsETF tool EXACTLY ONCE with these arguments:\n"
        f"  ids: {json.dumps(list(ids))}\n"
        f"  data_type: '{data_type}'\n"
        f"  startDate: '{start}'\n"
        f"  endDate: '{end}'\n"
        f"{freq_line}"
        f"  limit: {limit}\n"
        "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different "
        "arguments.\n\n"
        "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat "
        "any of the data — it is read directly from the tool output, not from your reply."
    )


# The MCP layer spills an oversized tool result to disk and hands the model a pointer instead.
# Verified 2026-08-19: "Error: result (75,593 characters across 3,510 lines) exceeds maximum
# allowed tokens. Output has been saved to /root/.claude/projects/.../tool-results/....txt"
# Anchored on the .txt extension, NOT on the next whitespace: the message renders the path
# immediately followed by a sentence-ending period ("...1787179767087.txt.\nFormat: ..."),
# so a whitespace-terminated match captures that trailing dot and the open() fails.
_SPILL_RE = re.compile(r"saved to (/\S+\.txt)")


def _tool_result_blocks(stdout: str) -> list[str]:
    """Every tool_result payload in a stream-json transcript, as text, in order."""
    out: list[str] = []
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            c = block.get("content")
            if isinstance(c, str):
                out.append(c)
            elif isinstance(c, list):
                out.append("".join(b.get("text", "") for b in c if isinstance(b, dict)))
    return out


def resolve_payload(text: str) -> dict | None:
    """One tool_result payload -> the parsed FactSet response, following a spill if needed."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    m = _SPILL_RE.search(text)
    if not m:
        return None
    try:
        with open(m.group(1)) as fh:
            obj = json.load(fh)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def make_runner(repo_root, timeout: int = FACTSET_TIMEOUT_SECONDS):
    """Build the production runner: one `claude -p` per (id-chunk, date-chunk, endpoint).

    THE MODEL MAKES THE CALL; WE READ THE TOOL'S OWN OUTPUT. The obvious design — ask the
    model to echo the rows back as JSON — was measured on 2026-08-19 and is not viable:

        500 rows, echo-verbatim : 590s, stdout truncated at the FRONT, unparseable
        500 rows, this approach :  18s, all 500 rows, byte-exact

    The echo approach also cannot work in principle at this size. A large tool result never
    reaches the model at all: the MCP layer spills it to disk and hands the model a pointer,
    so "copy every value verbatim" asks it to transcribe data it cannot see. That is why the
    first backfill produced partial data with loud timeouts rather than an obvious error.

    Reading the raw payload is also strictly more faithful — with no transcription step there
    is no opportunity to round, reorder or drop a row.
    """
    def run(ids, data_type, start, end, limit, frequency):
        cmd = ["claude", "-p", _prompt(ids, data_type, start, end, limit, frequency),
               "--allowedTools", _TOOL, "--model", MODEL,
               "--output-format", "stream-json", "--verbose"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                cwd=str(repo_root), env=_claude_env())
        if result.returncode != 0:
            raise RuntimeError(f"rc={result.returncode}: {(result.stderr or '').strip()[:200]}")

        blocks = _tool_result_blocks(result.stdout or "")
        if not blocks:
            # No tool_result at all means the call never happened. That is a failure, not an
            # ETF with no flows — returning [] here would write a silent gap into history.
            raise ValueError("no tool_result in transcript: "
                             f"{(result.stdout or '').strip()[-200:]}")
        for text in reversed(blocks):
            obj = resolve_payload(text)
            if obj is not None and isinstance(obj.get("data"), list):
                return [r for r in obj["data"] if isinstance(r, dict)]
        raise ValueError(f"tool_result unusable: {blocks[-1][:200]}")
    return run


def id_chunks(tickers, size: int = FACTSET_CHUNK_SIZE):
    t = list(tickers)
    return [t[i:i + size] for i in range(0, len(t), size)]


def date_chunks(start: str, end: str, n_ids: int,
                limit: int = FACTSET_RESULT_LIMIT,
                rows_per_year: int = 252) -> list[tuple[str, str]]:
    """Split [start, end] into spans small enough that n_ids x rows stays under `limit`.

    `rows_per_year` MUST match the endpoint's frequency. Assuming 252 (daily) for the
    month-end `aum` endpoint would plan ~48 calls where 2 suffice — 46 wasted `claude -p`
    calls pointed straight at the quota ceiling that broke the 2026-08-13 digest.

    Saturation is still checked after the fact — this is the cheap guard, not the only one.
    """
    if n_ids <= 0:
        raise ValueError("n_ids must be positive")
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    if e < s:
        raise ValueError(f"end {end} before start {start}")

    # Aim BELOW the cap, not at it. Planning for exactly `limit` rows means a chunk that
    # lands on a full trading period hits the cap exactly, trips the saturation check, and
    # splits into two more calls — observed on the 2026-08-19 run, where the very first
    # chunk returned exactly 500 rows and recursed. Filling to ~80% costs a few more planned
    # chunks and avoids roughly doubling the executed ones.
    rows_budget = max(1, int(limit * CHUNK_FILL_TARGET) // n_ids)
    span = max(1, int(rows_budget * (365.0 / rows_per_year)))

    out, cur = [], s
    while cur <= e:
        chunk_end = min(cur + timedelta(days=span - 1), e)
        out.append((cur.isoformat(), chunk_end.isoformat()))
        cur = chunk_end + timedelta(days=1)
    return out


def _midpoint(start: str, end: str) -> str:
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    return (s + (e - s) // 2).isoformat()


def normalize(rows, data_type: str) -> list[dict]:
    """FactSet result elements -> [{ticker, date, value, shares_outstanding?}].

    Rows without a usable ticker or date are dropped; a null VALUE is preserved as None.
    """
    field = VALUE_FIELD[data_type]
    out = []
    for r in rows:
        ticker = (r.get("requestId") or "").strip().upper()
        d = (r.get("date") or "").strip()
        if not ticker or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            continue
        rec = {"ticker": ticker, "date": d, "value": r.get(field)}
        if data_type == "aum":
            rec["shares_outstanding"] = r.get("numberOfSharesOutstanding")
        out.append(rec)
    return out


def fetch_range(tickers, data_type: str, start: str, end: str, runner,
                limit: int = FACTSET_RESULT_LIMIT,
                on_progress=None, _depth: int = 0) -> tuple[list[dict], list[str]]:
    """Fetch one endpoint for many tickers over a date range.

    Returns (records, failed_tickers) and never raises for a single chunk failure — a bad
    chunk costs its own tickers for that span and is reported, rather than aborting a
    50-call backfill at call 37.

    SATURATION SPLIT: a chunk returning exactly `limit` rows was probably truncated, so the
    date range is halved and retried. Bounded by _depth so a genuinely dense response cannot
    recurse forever.
    """
    frequency = {"prices": "D", "aum": "M", "flows": None}[data_type]
    rows_per_year = ROWS_PER_YEAR[data_type]
    records: list[dict] = []
    failed: list[str] = []

    for ids in id_chunks(tickers):
        for cs, ce in date_chunks(start, end, len(ids), limit, rows_per_year):
            try:
                raw = runner(ids, data_type, cs, ce, limit, frequency)
            except Exception as exc:                     # noqa: BLE001 - reported, not swallowed
                if on_progress:
                    on_progress(f"FAIL {data_type} {','.join(ids)} {cs}..{ce}: {exc}")
                failed.extend(ids)
                continue

            if len(raw) >= limit and _depth < 4 and cs != ce:
                # Truncated. Halve and recurse rather than accept a silently short history.
                mid = _midpoint(cs, ce)
                nxt = (date.fromisoformat(mid) + timedelta(days=1)).isoformat()
                if on_progress:
                    on_progress(f"saturated {data_type} {cs}..{ce} ({len(raw)} rows) -> split")
                for a, b in ((cs, mid), (nxt, ce)):
                    if a <= b:
                        r, f = fetch_range(ids, data_type, a, b, runner, limit,
                                           on_progress, _depth + 1)
                        records.extend(r)
                        failed.extend(f)
                continue

            records.extend(normalize(raw, data_type))
            if on_progress:
                on_progress(f"ok {data_type} {len(ids)}ids {cs}..{ce} -> {len(raw)} rows")

    return records, sorted(set(failed))


def estimate_calls(n_tickers: int, start: str, end: str,
                   data_type: str = "flows",
                   chunk: int = FACTSET_CHUNK_SIZE,
                   limit: int = FACTSET_RESULT_LIMIT) -> int:
    """How many `claude -p` calls one endpoint will cost. Printed before any backfill runs.

    This exists because the 2026-08-13 incident (two claude -p heavy jobs in one rolling 5h
    window exhausted the subscription; the digest shipped 40 of 256 stories) came from not
    knowing the number in advance.
    """
    n_chunks = (n_tickers + chunk - 1) // chunk
    ids_per = min(chunk, n_tickers)
    return n_chunks * len(date_chunks(start, end, ids_per, limit,
                                      ROWS_PER_YEAR[data_type]))
