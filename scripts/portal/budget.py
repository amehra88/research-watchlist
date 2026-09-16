"""Budget checks: scripts/portal/budget.py (RIS4 slice 2, Task 6).

The one thing this module knows about is a directory tree on disk -- it never
imports vault/state_bundles/etc. and never reads notes/, config/, or state/.
build_portal.py calls `check()` against its own `<out>/.tmp-<pid>` staging
tree before it ever publishes anything, and `table()` for the human-readable
log line printed on every build (success or failure), per the brief's four
hard limits:

  - files:            <= MAX_FILES               (240)
  - any TEXT file:    <= MAX_TEXT_FILE_BYTES      (14 MB)
  - total bytes:      <= MAX_TOTAL_BYTES          (48 MB)
  - index.html:       <= MAX_INDEX_HTML_BYTES     (1 MB)

"Text file" (the per-file 14 MB cap) is judged by extension -- the portal
tree is pure JSON/HTML/CSS/JS (data/*.json, index.html, styles.css, app.js)
plus whatever Task 7/8's vendor/ ships (fonts, icons -- binary, and
deliberately NOT subject to this cap; the brief's own wording is "any single
text file"). `_TEXT_EXTS` is the exhaustive list of extensions this build is
ever expected to produce as text.
"""
from __future__ import annotations

from pathlib import Path

MAX_FILES = 240
MAX_TEXT_FILE_BYTES = 14 * 1024 * 1024
MAX_TOTAL_BYTES = 48 * 1024 * 1024
MAX_INDEX_HTML_BYTES = 1 * 1024 * 1024

TOP_N = 25

_TEXT_EXTS = {".json", ".html", ".htm", ".css", ".js", ".mjs", ".md", ".txt", ".svg", ".jsonl"}


def _files(out_dir: Path) -> list[Path]:
    out_dir = Path(out_dir)
    return [p for p in sorted(out_dir.rglob("*")) if p.is_file()]


def check(out_dir: Path) -> list[str]:
    """List of human-readable violation strings; [] means clean. Never raises
    for a missing/empty out_dir -- that's just zero files, zero violations.
    """
    out_dir = Path(out_dir)
    files = _files(out_dir)
    violations: list[str] = []

    n = len(files)
    if n > MAX_FILES:
        violations.append(f"files: {n} > MAX_FILES ({MAX_FILES})")

    total = 0
    for p in files:
        size = p.stat().st_size
        total += size
        rel = p.relative_to(out_dir).as_posix()
        if p.suffix.lower() in _TEXT_EXTS and size > MAX_TEXT_FILE_BYTES:
            violations.append(f"{rel}: {size} bytes > MAX_TEXT_FILE_BYTES ({MAX_TEXT_FILE_BYTES})")
        if rel == "index.html" and size > MAX_INDEX_HTML_BYTES:
            violations.append(f"index.html: {size} bytes > MAX_INDEX_HTML_BYTES ({MAX_INDEX_HTML_BYTES})")

    if total > MAX_TOTAL_BYTES:
        violations.append(f"total: {total} bytes > MAX_TOTAL_BYTES ({MAX_TOTAL_BYTES})")

    return violations


def table(out_dir: Path, top_n: int = TOP_N) -> str:
    """(path, bytes) sorted desc by size, top `top_n`, plus a files/total summary
    line. Pure string -- the caller decides whether/where to print or log it.
    """
    out_dir = Path(out_dir)
    files = _files(out_dir)
    rows = sorted(
        ((p.relative_to(out_dir).as_posix(), p.stat().st_size) for p in files),
        key=lambda r: r[1], reverse=True,
    )
    total = sum(size for _, size in rows)

    lines = [f"{'bytes':>10}  path", "-" * 72]
    for rel, size in rows[:top_n]:
        lines.append(f"{size:>10}  {rel}")
    lines.append("-" * 72)
    lines.append(f"files={len(files)} (max {MAX_FILES})  "
                 f"total_bytes={total} (max {MAX_TOTAL_BYTES})")
    return "\n".join(lines)
