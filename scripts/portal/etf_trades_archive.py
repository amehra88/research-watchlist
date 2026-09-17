#!/usr/bin/env python3
"""portal/etf_trades_archive.py — daily archive of etf_trades.py's output (RIS5 A3).

Task 3 brief: "build_portal (or a tiny cron) copies data/etf_trades.json to
state/etf_trades/<date>.json daily (gitignored) so history accrues." This is the "tiny
cron" branch, NOT build_portal: A4's report (task-4-report.md, "Fix round 2") established
that build_portal.py must keep its "never notes/, config/, or state/" invariant
UNCONDITIONALLY and `--dry-run` must be fully dry — a live `state/` write from inside
build_portal was ruled a real defect there, not an acceptable exception. Adding a second
state/ writer to build_portal here would repeat exactly that mistake.

Also NOT wired through `<out_dir>/data/etf_trades.json`: `etf_trades.etf_trades(days,
out_dir)` only ever writes into build_portal's OWN transient `.tmp-<pid>` scratch dir (see
build_portal.py's `_stage_etf_trades`), so there is no stable on-disk path this module
could copy from even if it wanted to depend on a build having run recently. Instead this
CLI calls `etf_trades.etf_trades(days=...)` directly (no out_dir) to get the dict
in-memory and writes it straight to `state/etf_trades/<date>.json` — independent of
whether/when build_portal last ran.

Archived shape is byte-identical to etf_trades()'s own return value:
`{as_of, days: [{date, etfs: [...]}], by_ticker: {SYM: [{date, etf, action}]}}` — no
schema translation, so `scripts/thesis/etf_evidence.py` (the peer-trim challenge-evidence
consumer) and any other future reader see exactly what etf_trades.py itself computed.

    python3 scripts/portal/etf_trades_archive.py                  # live: writes today's archive
    python3 scripts/portal/etf_trades_archive.py --state-dir /tmp/x --date 2026-09-17
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "portal"))
import etf_trades as et                                       # noqa: E402

REPO = Path("/root/research-watchlist")
STATE_DIR = REPO / "state" / "etf_trades"

DEFAULT_DAYS = 14   # matches etf_trades.py's own default trailing window


def archive(days: int = DEFAULT_DAYS, state_dir: Path = STATE_DIR, today: date = None,
           paths=None) -> Path:
    """Compute etf_trades() fresh (no out_dir -- no dependency on a build having run) and
    write it to state_dir/<date>.json. Overwrites if re-run the same day (idempotent)."""
    today = today or date.today()
    result = et.etf_trades(days=days, out_dir=None, paths=paths, today=today)
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    out_path = state_dir / f"{today.isoformat()}.json"
    fd, tmp = tempfile.mkstemp(prefix=".etf_trades_archive-", suffix=".tmp", dir=str(state_dir))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1)
        Path(tmp).replace(out_path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return out_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--state-dir", default=None)
    ap.add_argument("--date", default=None, help="override today (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    state_dir = Path(args.state_dir) if args.state_dir else STATE_DIR
    today = date.fromisoformat(args.date) if args.date else None
    out_path = archive(days=args.days, state_dir=state_dir, today=today)
    print(f"archived etf_trades -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
