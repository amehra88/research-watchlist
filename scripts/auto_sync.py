#!/usr/bin/env python3
"""
Auto-sync cron — detects uncommitted changes, commits them, rebases on origin,
and pushes to GitHub. Runs every 15 minutes via cron.

Logs to /root/research-watchlist/logs/auto-sync.log. Quiet exit when nothing
to do (no log spam during idle).
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path("/root/research-watchlist")
LOG_PATH = REPO_ROOT / "logs" / "auto-sync.log"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(f"[{now_iso()}] {msg}\n")


def run(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def main() -> int:
    # Detect uncommitted changes
    rc, stdout, stderr = run(["git", "status", "--porcelain"])
    if rc != 0:
        log(f"ERROR: git status failed rc={rc} stderr={stderr[:200]}")
        return 1

    changes = stdout.strip()
    n_files = len(changes.split("\n")) if changes else 0

    # Commit local changes first (if any)
    if changes:
        log(f"detected {n_files} change(s); staging and committing")
        rc, _, stderr = run(["git", "add", "-A"])
        if rc != 0:
            log(f"ERROR: git add failed: {stderr[:200]}")
            return 1
        commit_msg = f"Auto-sync: {now_iso()} ({n_files} file{'s' if n_files != 1 else ''})"
        rc, _, stderr = run(["git", "commit", "-m", commit_msg])
        if rc != 0:
            log(f"ERROR: git commit failed: {stderr[:200]}")
            return 1

    # Rebase on remote to incorporate any commits from Mac/iPad
    rc, _, stderr = run(["git", "pull", "--rebase", "origin", "main"])
    if rc != 0:
        log(f"ERROR: git pull --rebase failed: {stderr[:200]}")
        run(["git", "rebase", "--abort"])
        log(f"  aborted rebase; manual intervention required")
        return 1

    # Push
    rc, _, stderr = run(["git", "push", "origin", "main"])
    if rc != 0:
        log(f"ERROR: git push failed: {stderr[:200]}")
        return 1

    if changes:
        log(f"SUCCESS: pushed {n_files} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
