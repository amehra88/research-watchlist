#!/usr/bin/env python3
"""One-shot watchdog for the 2026-08-10 11:00 ET SEC run — the first UNATTENDED
test of the OOM fix (a47ad095). See the v3-ingest-oom-fix memory.

Background: logs/v3_sec.log has had a START every day since 2026-07-15 and zero
DONE lines — the runs were being SIGKILLed by the OOM killer partway through.
a47ad095 fixed the read-timing that caused it, but was only verified on a bounded
12-filing run whose RSS still trended 141 -> 165 MB. The open question is whether
that creep is per-filing (which would still kill a ~600-filing run) or one-time.

So this does two jobs:
  1. Reports the terminal outcome (PASS / DIED / NO_START / TIMEOUT), once.
  2. While the run is live, samples RSS every hour alongside the filings-processed
     count, so the verdict email carries the MB-per-filing trend — the actual
     evidence for whether the leak is gone, not just whether this one run survived.

Runs hourly on the droplet and stays quiet until it can answer. It emails exactly
once, at the moment the answer is known, then removes its own crontab line.

  cron: 0 * * * * /root/bin/alert_on_failure.sh sec_run_check \
        python3 /root/research-watchlist/scripts/v3_ingest/check_sec_run_oneshot.py

Safe to delete after it fires.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/root/ws")
from emailer import send_alert  # noqa: E402

LOG = Path("/root/research-watchlist/logs/v3_sec.log")
STATE = Path("/root/research-watchlist/state/v3_ingest/sec_run_check.json")

RUN_DATE = "2026-08-10"                      # the run being watched
NO_START_AFTER = dt.datetime(2026, 8, 10, 12, 30)   # cron fires 11:00; allow slack
DEADLINE = dt.datetime(2026, 8, 11, 14, 0)   # 27h — past the worst historical run (19h)
STALL_MINUTES = 45                           # no new log line + no process = dead


def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"samples": []}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n")


def run_pid() -> str:
    """PID of a live sec_filings.py, or '' — excludes this watchdog itself."""
    return sh("pgrep -f 'python3 .*sec_filings\\.py' | head -1")


def rss_mb(pid: str) -> float | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def log_lines() -> list[str]:
    return LOG.read_text(errors="ignore").splitlines() if LOG.exists() else []


def last_log_time(lines: list[str]) -> dt.datetime | None:
    for line in reversed(lines):
        m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
        if m:
            return dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
    return None


def self_remove() -> None:
    subprocess.run("crontab -l 2>/dev/null | grep -v check_sec_run_oneshot | crontab -",
                   shell=True)


def finish(verdict: str, headline: str, detail: list[str], st: dict) -> None:
    samples = st.get("samples", [])
    body = [headline, ""]
    body += detail
    if samples:
        body += ["", "RSS trend while running (the per-filing leak question):", ""]
        body.append(f"  {'time':<18}{'RSS MB':>9}{'filings':>10}{'MB/filing':>12}")
        first = samples[0]
        for s in samples:
            d_rss = s["rss_mb"] - first["rss_mb"]
            d_f = s["filings"] - first["filings"]
            per = f"{d_rss / d_f:.2f}" if d_f > 0 else "—"
            body.append(f"  {s['at'][-8:]:<18}{s['rss_mb']:>9.0f}{s['filings']:>10}{per:>12}")
        if len(samples) > 1:
            d_rss = samples[-1]["rss_mb"] - first["rss_mb"]
            d_f = samples[-1]["filings"] - first["filings"]
            body += ["", f"  Net: {d_rss:+.0f} MB over {d_f} filings."]
            if d_f > 0:
                body.append(f"  ~{d_rss / d_f:.2f} MB/filing — flat/negative means the leak is "
                            f"gone; sustained positive means it is still per-filing.")
    body += ["", f"Log: {LOG}", "Watchdog has removed its own crontab line."]
    text = "\n".join(body)
    send_alert(f"SEC run {RUN_DATE} — {verdict}", text)
    print(text)
    st["fired"] = {"verdict": verdict, "at": dt.datetime.now().isoformat(timespec="seconds")}
    save_state(st)
    self_remove()


def main() -> int:
    now = dt.datetime.now()
    st = load_state()
    if st.get("fired"):
        self_remove()
        return 0

    lines = log_lines()
    started = [l for l in lines if f"[{RUN_DATE}" in l and "v3_sec: START" in l]
    done = [l for l in lines if "v3_sec: DONE" in l
            and (f"[{RUN_DATE}" in l or "[2026-08-11" in l)]
    pid = run_pid()

    # Filings written so far in this run (log lines dated on/after RUN_DATE).
    idx = lines.index(started[0]) if started else len(lines)
    filings = sum(1 for l in lines[idx:] if "WROTE+INGESTED" in l)

    if pid:
        mb = rss_mb(pid)
        if mb is not None:
            st.setdefault("samples", []).append(
                {"at": now.isoformat(timespec="seconds"), "rss_mb": round(mb, 1),
                 "filings": filings})
            save_state(st)

    if done:
        finish("PASS — reached DONE", done[-1].strip(),
               ["The OOM fix holds on a full unattended run.",
                f"Filings written this run: {filings}.",
                "",
                "Next: the SEC backlog (nothing ingested since 2026-07-15) drains via the "
                "daily cron; the per-ticker watermark flush makes incremental catch-up safe."], st)
        return 0

    if not started:
        if now < NO_START_AFTER:
            print(f"[{now:%H:%M}] no START yet for {RUN_DATE}; waiting.")
            return 0
        finish("NO_START — the 11:00 cron never fired",
               f"No 'v3_sec: START' line dated {RUN_DATE} in the log.",
               ["The job did not run at all. Check `crontab -l | grep v3_sec` and whether "
                "the crontab was left paused by a build (see the "
                "build-workflow-pause-autosync-default memory)."], st)
        return 0

    last = last_log_time(lines)
    stalled = last is not None and (now - last).total_seconds() > STALL_MINUTES * 60

    if not pid and stalled:
        oom = sh("dmesg -T 2>/dev/null | grep -i 'killed process' | tail -3")
        finish("DIED — START but no DONE",
               f"Run started {RUN_DATE} 11:00 but the process is gone with no DONE line.",
               [f"Filings written before it died: {filings}.",
                f"Last log activity: {last}.",
                "",
                "Recent OOM kills (empty = killed by something else):",
                oom or "  (none found in dmesg)",
                "",
                "If OOM: the leak is per-filing and lives somewhere the lazy-load fix in "
                "a47ad095 did not reach. The RSS trend below is the diagnostic."], st)
        return 0

    if now > DEADLINE:
        finish("TIMEOUT — still running past 27h",
               f"Run started {RUN_DATE} 11:00 and is still going (pid={pid or 'none'}).",
               [f"Filings written so far: {filings}.",
                "Longer than any historical run (worst was ~19h). Could be the 25-day "
                "backlog plus the new theme-extraction retry (b1c351aa) doubling worst-case "
                "time on timeouts — not necessarily a fault. Check it directly."], st)
        return 0

    print(f"[{now:%H:%M}] running (pid={pid or 'none'}), {filings} filings, "
          f"{len(st.get('samples', []))} RSS samples; staying quiet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
