"""Publish helper: scripts/portal/publish_files.py (RIS4 slice 2, Task 9).

The Artifact tool's `files` parameter for redeploying the portal page needs a
JSON MAP of {published/path: published/path} covering every file the builder
owns except index.html (published separately, via `file_path`) -- see
docs/portal/README.md's publish runbook for the exact call shape verified
against the live artifact. This module computes that map from a built
--out tree so a session never has to hand-enumerate 144 files.

Read-only: this module never writes into --out (a built portal_build/ tree),
notes/, config/, or state/. It only reads.

    python3 scripts/portal/publish_files.py [--out DIR]           # print the map
    python3 scripts/portal/publish_files.py [--out DIR] --check   # + verify hashes

What counts as "published" (collect()): every regular file under --out
EXCEPT
  - index.html                          (passed to Artifact via file_path, not files)
  - anything under smoke/               (Phase 0 smoke-test source, gitignored,
                                          never builder output -- see build_portal.py's
                                          OWNED_PATHS comment for why the builder itself
                                          never touches it either)
  - a dotfile (any path component starting with ".")
  - anything NOT matching build_portal.OWNED_PATHS (today: app.js, app2.js,
    ask.js, styles.css, vendor/**, data/** -- see that module for the
    authoritative list)

Exit codes (main()):
  0 - map printed to stdout (and, with --check, every published file's sha256
      matched data/manifest.json's own `files` entry)
  2 - --out is missing index.html or data/manifest.json, OR the map would
      have MORE than MAX_FILES entries (254 -- the Artifact tool's 255-file
      cap minus the one slot index.html itself occupies via file_path)
  3 - --check found a sha256 mismatch, or a published path with no entry in
      data/manifest.json's own `files` map at all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Bootstrap: same two-insert shape as build_portal.py (see its own comment) --
# scripts/ parent so `from portal import REPO` resolves, and scripts/portal/
# itself so `import build_portal` resolves as a bare sibling import.
_here = Path(__file__).resolve().parent             # scripts/portal
_here_parent = str(_here.parent)                     # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

_here_str = str(_here)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import build_portal as bp  # noqa: E402

# The Artifact tool's own hard cap is 255 files total. index.html occupies one
# slot via file_path (never a `files` key), so the map itself may hold at most
# 254 -- see build_portal's OWNED_PATHS docstring for the publish-side context.
MAX_FILES = 254


def _is_owned(rel: str) -> bool:
    """Same prefix/exact match as build_portal._is_owned, duplicated rather
    than imported -- both modules keep this one-line private helper local by
    the same convention build_portal.py itself documents for _known_sets/
    _write_json (see that module's own comment)."""
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in bp.OWNED_PATHS)


def _is_dotfile_path(rel: str) -> bool:
    return any(part.startswith(".") for part in Path(rel).parts)


def collect(out_dir: Path) -> list[str]:
    """Sorted published-path strings under out_dir passing every filter in
    the module docstring's "What counts as 'published'" list. A missing or
    empty out_dir is just an empty result -- required-file presence is
    main()'s job, not this function's, so callers can use collect() on a
    partially-built or synthetic tree without it raising.
    """
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return []
    paths: list[str] = []
    for p in sorted(out_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(out_dir).as_posix()
        if rel == "index.html":
            continue
        if rel == "smoke" or rel.startswith("smoke/"):
            continue
        if _is_dotfile_path(rel):
            continue
        if not _is_owned(rel):
            continue
        paths.append(rel)
    return paths


def files_map(out_dir: Path) -> dict[str, str]:
    """{published/path: published/path} for every collect()ed path -- the
    exact shape the Artifact tool's `files` parameter needs (map form; the
    list form `["a.js", ...]` is rejected -- see the README's publish runbook).
    """
    return {rel: rel for rel in collect(out_dir)}


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def check_hashes(out_dir: Path, paths: list[str]) -> list[str]:
    """Verify each of `paths` against data/manifest.json's own `files` entry
    (written by state_bundles.manifest() -- see that function's own
    docstring for what it hashes and when). Returns a list of human-readable
    problem strings; [] means every path matched. A path with no manifest
    entry at all is reported, not silently skipped -- manifest() hashes
    every file under out_dir at build time (except data/manifest.json
    itself), so an untracked published path means the tree was hand-edited
    or built with a manifest() that predates this file.
    """
    out_dir = Path(out_dir)
    manifest_path = out_dir / "data" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 -- report, don't crash the CLI
        return [f"data/manifest.json unreadable: {type(exc).__name__}: {exc}"]

    manifest_files = manifest.get("files") or {}
    problems: list[str] = []
    for rel in paths:
        if rel == "data/manifest.json":
            continue   # manifest() never hashes itself -- see its own docstring
        entry = manifest_files.get(rel)
        if entry is None:
            problems.append(f"{rel}: not tracked in data/manifest.json 'files'")
            continue
        actual = _sha256_file(out_dir / rel)
        expected = entry.get("sha256")
        if actual != expected:
            problems.append(f"{rel}: sha256 mismatch (manifest={expected}, disk={actual})")
    return problems


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--out", type=Path, default=REPO / "portal_build",
                     help="built portal tree to scan (default: REPO/portal_build)")
    ap.add_argument("--check", action="store_true",
                     help="also verify every published file's sha256 against "
                          "data/manifest.json's own 'files' entry")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    out_dir = Path(args.out)

    if not (out_dir / "index.html").is_file():
        print(f"ERROR: {out_dir}/index.html not found -- is --out a built portal tree?",
              file=sys.stderr)
        return 2
    if not (out_dir / "data" / "manifest.json").is_file():
        print(f"ERROR: {out_dir}/data/manifest.json not found -- is --out a built portal tree?",
              file=sys.stderr)
        return 2

    paths = collect(out_dir)
    if len(paths) > MAX_FILES:
        print(f"ERROR: {len(paths)} published files exceeds MAX_FILES ({MAX_FILES}) -- "
              f"the Artifact tool's 255-file cap (minus index.html's own slot)",
              file=sys.stderr)
        return 2

    if args.check:
        problems = check_hashes(out_dir, paths)
        if problems:
            print(f"CHECK FAILED: {len(problems)}/{len(paths)} file(s) did not verify:",
                  file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            return 3
        # `paths` includes data/manifest.json itself (it's an ordinary owned file),
        # but check_hashes() never compares it against its own `files` entry --
        # manifest() doesn't hash itself (see that function's own docstring) --
        # so only len(paths) - 1 files actually had a sha256 verified here.
        n_checked = len(paths) - (1 if "data/manifest.json" in paths else 0)
        print(f"check: {n_checked}/{len(paths)} files hash-verified "
              f"(manifest itself excluded) against data/manifest.json", file=sys.stderr)

    print(json.dumps(files_map(out_dir), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
