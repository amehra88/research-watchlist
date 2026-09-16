"""ETF trades: scripts/portal/etf_trades.py — RIS4 portal builder, Task 3.

`etf_trades(days, out_dir)` parses `/root/ws`'s daily ETF-holdings-change report
text into structured new/exits/added/trimmed rows per ETF, plus an inverted
`by_ticker` index, and (when given an `out_dir`) writes `data/etf_trades.json`.

Split out of scripts/portal/reports.py in fix round 1 (controller-directed,
size/responsibility separation only — the public interface and output shape
are unchanged; nothing imports `etf_trades` from reports.py, so no re-export
shim was added there). Call it as:

    from portal import etf_trades
    etf_trades.etf_trades(days, out_dir)

Data source note: /root/ws/data/etf_holdings.db's `holdings` table only stores
raw daily snapshots (date, etf_ticker, symbol, weight, shares) — the same
inputs ws's own compare.py logic diffs to produce the change report. There is
no separate structured "what changed" file (JSON/CSV) per day; the report text
at data/reports/report_{date}.txt is the only per-day record of that
computation, so this module parses it (the sanctioned fallback per the Task 3
brief).

Every zero-arg-default path reads live data (`/root/ws/data/reports`). The
`paths: Paths` override lets tests run only against
scripts/portal/fixtures/etf_trades/ — a minimal, module-local dataclass (just
`ws_reports`), independent of reports.py's own larger `Paths`. Read-only: this
module never writes into notes/, config/, or state/; its only write is
`<out_dir>/data/etf_trades.json`, and only when an `out_dir` is actually
passed in.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

# No REPO/sys.path bootstrap needed here (unlike reports.py/vault.py/identity.py):
# every path this module touches (/root/ws/data/reports) is an absolute literal, and
# it imports nothing else from the `thesis`/`topics` packages under REPO/scripts.
# Both `import etf_trades` (bare-module test convention) and `from portal import
# etf_trades` (package-relative, per this module's own docstring) work unchanged
# either way -- this file just has nothing to bootstrap for.


def log(msg: str) -> None:
    print(f"[etf_trades] {msg}", flush=True)


@dataclass
class Paths:
    ws_reports: Path = None

    def __post_init__(self):
        self.ws_reports = self.ws_reports or Path("/root/ws/data/reports")


DEFAULT_PATHS = Paths()


# ---------------------------------------------------------------------------
# ws ETF-holdings report parser
# ---------------------------------------------------------------------------
_ETF_HEADER_RE = re.compile(r"^(?P<name>.+) \((?P<etf>[A-Z0-9]+)\)$")
_DASH_LINE_RE = re.compile(r"^-{5,}$")
_TABLE_DIVIDER_RE = re.compile(r"^-{5,}(\s+-{5,})+$")
_SECTION_RE = re.compile(
    r"^\s*(BOUGHT — NEW POSITIONS|SOLD — FULL EXIT|ADDED|TRIMMED) \(\d+\):\s*$")
_SECTION_KIND = {
    "BOUGHT — NEW POSITIONS": "new", "SOLD — FULL EXIT": "exits",
    "ADDED": "added", "TRIMMED": "trimmed",
}
_BOUGHT_ROW_RE = re.compile(
    r"^\s*\+\s+(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}(?P<weight>[\d.]+)%\s+"
    r"\((?P<shares>[\d,]+) shares\)\s*$")
_SOLD_ROW_RE = re.compile(
    r"^\s*-\s+(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}\(was (?P<weight>[\d.]+)%, "
    r"(?P<shares>[\d,]+) shares\)\s*$")
_TABLE_ROW_RE = re.compile(
    r"^\s*(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}(?P<delta>[+-][\d.]+)pp\s+"
    r"(?P<frm>[\d.]+)% → (?P<to>[\d.]+)%\s*$")


def _is_etf_header(lines: list[str], i: int) -> re.Match | None:
    """An ETF block header is a "Name (TICKER)" line immediately followed by a
    dashed divider -- this two-line requirement is what keeps the parser from
    tripping on the report's other ALL-CAPS banner lines (data-quality alert,
    section titles), none of which are followed by a bare dash line."""
    if i + 1 >= len(lines):
        return None
    m = _ETF_HEADER_RE.match(lines[i].strip())
    if m and _DASH_LINE_RE.match(lines[i + 1].strip()):
        return m
    return None


def _parse_ws_report(text: str) -> list[dict]:
    """Parses the ws ETF-holdings daily-summary text into
    [{etf, name, new:[{sym,name,weight,shares}], exits:[{sym,name,weight,shares}],
      added:[{sym,name,delta_pp,from_weight,to_weight}],
      trimmed:[{sym,name,delta_pp,from_weight,to_weight}]}].

    added/trimmed use delta_pp/from_weight/to_weight rather than weight/shares --
    a deliberate deviation from the brief's abbreviated {sym,name,weight,shares}
    gloss (written for the `new` list specifically). The ADDED/TRIMMED table in
    the source report never carries a share count, only an active-weight delta
    and before/after weight, so there is nothing to put in a `shares` field for
    those two lists.
    """
    lines = text.splitlines()
    etfs: list[dict] = []
    i, n = 0, len(lines)
    while i < n:
        m = _is_etf_header(lines, i)
        if not m:
            i += 1
            continue
        rec = {"etf": m.group("etf"), "name": m.group("name").strip(),
               "new": [], "exits": [], "added": [], "trimmed": []}
        i += 2  # past the header + its dash divider
        section = None
        while i < n and not _is_etf_header(lines, i):
            line = lines[i]
            stripped = line.strip()
            sm = _SECTION_RE.match(line)
            if sm:
                section = _SECTION_KIND[sm.group(1)]
                i += 1
                continue
            if stripped.startswith("Symbol") or _TABLE_DIVIDER_RE.match(stripped):
                i += 1
                continue
            if section == "new":
                rm = _BOUGHT_ROW_RE.match(line)
                if rm:
                    rec["new"].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                        "weight": float(rm["weight"]),
                                        "shares": int(rm["shares"].replace(",", ""))})
            elif section == "exits":
                rm = _SOLD_ROW_RE.match(line)
                if rm:
                    rec["exits"].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                          "weight": float(rm["weight"]),
                                          "shares": int(rm["shares"].replace(",", ""))})
            elif section in ("added", "trimmed"):
                rm = _TABLE_ROW_RE.match(line)
                if rm:
                    rec[section].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                          "delta_pp": float(rm["delta"]),
                                          "from_weight": float(rm["frm"]),
                                          "to_weight": float(rm["to"])})
            i += 1
        etfs.append(rec)
    return etfs


_ACTION_KEYS = ("new", "exits", "added", "trimmed")
_ACTION_LABEL = {"new": "new", "exits": "exit", "added": "added", "trimmed": "trimmed"}


def etf_trades(days: int = 14, out_dir: Path = None, paths: Paths = None,
               today: date = None) -> dict:
    """{as_of, days: [{date, etfs:[...]}, ...], by_ticker: {SYM: [{date, etf, action}]}}
    over the trailing `days` days (including today), parsed from
    /root/ws/data/reports/report_{date}.txt. Writes <out_dir>/data/etf_trades.json
    when `out_dir` is given; always returns the dict either way. Days with no
    report file (real gaps exist, e.g. weekends/holidays) are skipped with a log
    line, never an error.
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    days_out = []
    by_ticker: dict[str, list] = {}

    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        p = paths.ws_reports / f"report_{d}.txt"
        if not p.exists():
            log(f"etf_trades: no ws report for {d}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        etfs = _parse_ws_report(text)
        if not etfs:
            # A non-empty report file that yielded zero ETF blocks means the header
            # regex didn't match something in this run (e.g. a ticker with a dot/dash
            # the [A-Z0-9]+ pattern doesn't cover) -- silent-empty is exactly the
            # failure mode a nightly build can't otherwise see, so this is a WARN,
            # not a routine "no report today" skip.
            log(f"etf_trades: WARNING — {p} parsed to 0 ETF blocks "
                f"({len(text)} chars); header regex may be missing a symbol shape")
            continue
        days_out.append({"date": d, "etfs": etfs})
        for rec in etfs:
            for action_key in _ACTION_KEYS:
                for item in rec[action_key]:
                    by_ticker.setdefault(item["sym"], []).append(
                        {"date": d, "etf": rec["etf"], "action": _ACTION_LABEL[action_key]})

    result = {"as_of": today.isoformat(), "days": days_out, "by_ticker": by_ticker}
    if out_dir is not None:
        out_dir = Path(out_dir)
        (out_dir / "data").mkdir(parents=True, exist_ok=True)
        (out_dir / "data" / "etf_trades.json").write_text(
            json.dumps(result, indent=1), encoding="utf-8")
    return result
