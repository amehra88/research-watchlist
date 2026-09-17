"""Theme share: scripts/portal/theme_share.py -- RIS5 Part A, Task 4 (bear-side paths).

`theme_share(topic_map_path, out_dir)` reads state/topics/topic_map.jsonl (rows carry
`ticker`, `themes` (a list of {theme, score} dicts), `cal_quarter`, `register`) and
computes, per (theme, calendar quarter, ticker), that ticker's SHARE of every row
tagged with that theme in that quarter -- a "share of voice" metric, portal-side only.
scripts/topics/diffusion.py stays count-only by design (spec §5 prohibits velocity/
slope/trend derivatives there); this module is the one place a per-ticker share and
its quarter-over-quarter delta are computed, and it never writes into state/topics/
outside its own output file.

Counting rule: EVERY topic_map row with both `ticker` and `cal_quarter` set counts,
regardless of `register` (question/evidence) or `source` (exchange/mdna) -- the brief
asks for "share of that theme's exchanges/evidence", i.e. the union of both registers.
A row naming N themes counts once toward EACH of those N themes (never split as 1/N),
per the task brief. This deliberately does NOT apply diffusion.py's
`apply_mdna_block_rule` (which drops a theme from an MD&A row unless that filer has
>= 2 mapped blocks in the same quarter) -- the brief does not ask for it, and mdna
source rows are a large share of the corpus (5,410 of 18,750 as of 2026-09-17), so
applying diffusion's noise filter here would silently change the denominator diffusion
itself reports. A theme's `_themes()` helper is duplicated from diffusion.py rather
than imported, on purpose: importing diffusion.py drags in its adjacency/lifecycle
module-load side effects for a two-line helper.

Output: {theme: {quarter: {"n": int, "tickers": {ticker: {"share": float,
"delta": float | null, "rows": int}}}}}. `n` (fix round 1) = total rows for the
theme in that quarter -- the denominator every ticker's `share` in that cell was
computed against, so a consumer can discount a thin cell (e.g. n=1) instead of
trusting a 100% share that rests on a single row. `rows` (fix round 1) = that
ticker's own row count for the cell (the numerator). `share` = rows / n. `delta` =
this quarter's share minus the immediately PRIOR quarter's share for that
ticker+theme -- "prior" meaning the previous entry in the GLOBAL sorted list of
calendar quarters present anywhere in topic_map.jsonl (not a per-theme list: a
theme that skips a quarter would otherwise get its delta measured against a
two-quarters-back baseline while its neighbours use a one-quarter baseline, making
deltas incomparable across themes).

`delta` is null in exactly two cases (fix round 1 clarifies the second): (1) the
quarter is the first quarter in the global list (no prior quarter exists at all),
or (2) the theme has ZERO rows anywhere in the prior quarter (the theme itself was
absent that quarter, so there is no real baseline share to diff against -- treating
that as a 0.0 baseline would silently manufacture a "share went from 0% to 100%"
mover out of a theme that simply hadn't started being discussed yet). `delta` stays
a real 0-based numeric value only when the theme DID have rows in the prior quarter
but this particular ticker had none of them (the theme existed, the ticker was
just absent from it -- a genuine "this ticker's share of an existing conversation
went from 0 to N%" is exactly what a share mover should show).

    from portal import theme_share
    theme_share.theme_share(out_path=Path("state/topics/theme_share.json"))

    python3 scripts/portal/theme_share.py                      # writes state/topics/theme_share.json (default)
    python3 scripts/portal/theme_share.py --out /path/to/out.json   # override

Every zero-arg-default path reads live data (state/topics/topic_map.jsonl under
REPO). The `topic_map_path` override lets tests run only against
scripts/portal/fixtures/theme_share/. Read-only except for the optional
`out_path` write (a literal output file path, matching score_reads.py's own
`--out` convention -- not a directory root like etf_trades.py's `out_dir`),
which defaults to state/topics/theme_share.json (RIS5 A4 fix round 2) and is
only skipped when a caller passes `out_path=None` explicitly (the CLI itself
always writes, since `--out` always has a value, default or overridden).

Scheduling note (RIS5 A4 fix round 2): the Saturday topics chain runs this
CLI, with no --out override, right after topic_map.jsonl is rebuilt -- A6
wires the actual cron entry; this module makes no cron/schedule changes
itself. scripts/portal/build_portal.py's own "theme_share" stage is a
READ-ONLY consumer of whatever this CLI last wrote (see that stage's
docstring) -- it never invokes this module's `theme_share()` function.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_here = Path(__file__).resolve().parent
_here_parent = str(_here.parent)
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

DEFAULT_TOPIC_MAP = REPO / "state" / "topics" / "topic_map.jsonl"
DEFAULT_OUT = REPO / "state" / "topics" / "theme_share.json"


def log(msg: str) -> None:
    print(f"[theme_share] {msg}", flush=True)


def _themes(row: dict) -> set[str]:
    """Theme slugs on one topic_map row, deduplicated -- see diffusion.py's own `_themes()`
    (not imported here; see module docstring)."""
    return {t["theme"] if isinstance(t, dict) else t for t in (row.get("themes") or []) if t}


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        log(f"theme_share: no topic_map at {path}")
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def compute_theme_share(rows: list[dict]) -> dict:
    """{theme: {quarter: {"n": int, "tickers": {ticker: {"share", "delta", "rows"}}}}} -- see
    module docstring for the exact null-vs-zero delta rule."""
    # counts[theme][quarter][ticker] = row count (one per row per theme it carries)
    counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    all_quarters: set[str] = set()
    for r in rows:
        cq, ticker = r.get("cal_quarter"), r.get("ticker")
        if not cq or not ticker:
            continue
        all_quarters.add(cq)
        for theme in _themes(r):
            counts[theme][cq][ticker] += 1

    quarters = sorted(all_quarters)          # global order -- see module docstring
    prior_of = {q: (quarters[i - 1] if i > 0 else None) for i, q in enumerate(quarters)}

    out: dict[str, dict] = {}
    for theme, by_q in sorted(counts.items()):
        out[theme] = {}
        for cq, tickers in sorted(by_q.items()):
            total = sum(tickers.values())
            prior_q = prior_of.get(cq)
            prior_tickers = by_q.get(prior_q) if prior_q is not None else None
            # fix round 1: prior_total == 0 means the theme itself had no rows at all in the
            # prior quarter (theme absent) -- delta is null in that case, not a 0-baseline
            # numeric value (see the module docstring's null-vs-zero rule).
            prior_total = sum(prior_tickers.values()) if prior_tickers else 0
            ticker_entries = {}
            for ticker, n in sorted(tickers.items()):
                share = n / total if total else 0.0
                if prior_q is None or prior_total == 0:
                    delta = None
                else:
                    prior_share = prior_tickers.get(ticker, 0) / prior_total
                    delta = round(share - prior_share, 6)
                ticker_entries[ticker] = {"share": round(share, 6), "delta": delta, "rows": n}
            out[theme][cq] = {"n": total, "tickers": ticker_entries}
    return out


def theme_share(topic_map_path: Path = DEFAULT_TOPIC_MAP, out_path: Path = None) -> dict:
    """Compute theme_share (see compute_theme_share) and, when `out_path` is given, write it
    there (a literal file path, parent dirs created as needed). Always returns the dict either way."""
    rows = _read_rows(Path(topic_map_path))
    result = compute_theme_share(rows)
    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8")
        log(f"wrote {out_path} ({len(result)} themes)")
    return result


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topic-map", default=str(DEFAULT_TOPIC_MAP), help="path to topic_map.jsonl")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help=f"output json path (default: {DEFAULT_OUT}, RIS5 A4 fix round 2 -- "
                         "the topics-chain cron runs with no --out at all)")
    a = ap.parse_args(argv)
    result = theme_share(Path(a.topic_map), Path(a.out))
    n_pairs = sum(len(qs) for qs in result.values())
    log(f"{len(result)} themes, {n_pairs} (theme, quarter) cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
