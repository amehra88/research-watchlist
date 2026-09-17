"""Builder CLI: scripts/portal/build_portal.py (RIS4 slice 2, Task 6).

The single entry point that turns the five builder modules (Tasks 1-5) into
one build: `python3 scripts/portal/build_portal.py --out DIR [flags]`.

Two halves, deliberately kept separate (see the brief's "Code Organization"):
  - a generic, REPO-free ATOMIC BUILD ENGINE (`run_stages`/`build`/`dry_run`/
    `_publish`) that knows nothing about vault/reports/etc. -- it just runs an
    ordered list of `(name, fn(tmp_dir) -> stats_dict)` stages into a fresh
    `<out_dir>/.tmp-<pid>`, then EITHER publishes every file into `out_dir`
    via `os.replace` (removing any file already under `out_dir`, under an
    OWNED_PATHS prefix (see that constant's own comment), that this build
    did not produce -- never anything outside OWNED_PATHS, e.g. an
    operator-placed `smoke/` dir survives untouched) OR discards the tmp
    tree entirely and leaves `out_dir` exactly as it was -- on a stage
    exception, a publish-time exception, (both exit 1) or a budget.check()
    violation (exit 2). This half is what test_build_portal.py exercises
    directly, against synthetic stage lists, with no live REPO/notes access
    at all.
  - the PRODUCTION stage list (`_default_stages`) that wires the five real
    builder modules together in the brief's mandated order and is only
    exercised by the real, live `python3 build_portal.py --out ...` run (see
    the Task 6 report for that build's output) -- not by the unit tests.

Orchestration order (brief, verbatim): reports -> etf_trades -> tickers/pvt/
ingest bundles -> search index -> state_bundles.build_state() (which writes
data/manifest.json LAST, after hashing every file already on disk under
out_dir -- see state_bundles.manifest()'s own docstring). Concretely:

  1. reports.build_reports()      -> data/reports/<date>.json + summaries
                                      (cached onto ctx.report_summaries so
                                      manifest() reuses them instead of
                                      re-running build_reports(days=1)).
  2. etf_trades.etf_trades()      -> data/etf_trades.json
  3. (this module) per-ticker /   -> data/tickers/<T>.json, data/pvt/<slug>.json,
     pvt / ingest bundles            data/ingest/<bucket>.json -- no existing
                                      module writes these (see module
                                      docstring below for who's who); refs +
                                      the ingest dict built here are cached
                                      and handed to stage 4 so it isn't
                                      recomputed.
  4. search_index.build_units()   -> data/search.json (reuses this build's
     + write_index()                 refs/ingest from stage 3; builds its
                                      OWN news_sec.news_bundle() -- see the
                                      "double work" note below).
  5. (optional) copy app/         -> index.html/styles.css/app.js/vendor/ --
                                      skipped whenever scripts/portal/app/
                                      doesn't exist OR --no-app is passed.
                                      Runs BEFORE stage 6's build_state() so
                                      the app files are already on disk when
                                      manifest.json hashes the tree.
  6. state_bundles.build_state()  -> themes/ideas/scores/market/news shards+
                                      index/sec_30d/manifest.json (LAST).

INTENDED, not a bug: --no-app composes with stale-file removal exactly like
every other stage. If a PRIOR build published index.html/styles.css/app.js/
vendor/* and a LATER build runs with --no-app, `_publish()` will remove those
files as stale (this build didn't produce them) -- out_dir always converges
to exactly what the current stage list produces, on every build, not just
the first one. --no-app is for "the app doesn't exist / isn't ready yet" (as
in this task's own required `--no-app` live build), not for "temporarily
omit the app from an otherwise-complete published tree."

Who writes data/tickers/<T>.json / data/pvt/<slug>.json / data/ingest/
<bucket>.json? Neither vault.py (Task 1, which only builds the per-ticker
dict via `ticker_bundle()`/`ingest_bundles()` in memory) nor state_bundles.py
(Task 4, whose `build_state()` never calls either function) writes them --
search_index.py (Task 5) only ever *references* those paths as the `f` field
of a search doc record, it never writes the files themselves. So stage 3
above is this module's own addition, exactly as the Task 6 brief directs:
one file per universe ticker that has notes/thesis/profile (tickers with
none of the three are skipped entirely, per the brief -- "tickers without
notes are NOT given files"), split into data/tickers/ for real tickers and
data/pvt/ for `.pvt` identifiers (slug = the id with the trailing `.pvt`
stripped, e.g. `openai.pvt` -> `data/pvt/openai.json`), plus the six
ingest_bundles() buckets verbatim under data/ingest/.

DOUBLE WORK (flagged per the brief's "note any double work" instruction,
not fixed here -- state_bundles.build_state() is Task 4's module and out of
this task's scope to change):
  - vault.discover() runs twice: once in stage 3 (whose `refs` stage 4
    reuses) and again inside state_bundles.build_state()'s own
    _load_context() call, which does not accept a pre-built refs/bundles
    list from ctx even though Ctx *has* ticker_bundles/universe/refs fields
    for exactly this purpose -- build_state() unconditionally overwrites
    them (see its own docstring: "Builds ticker_bundles + refs ONCE ... and
    shares them" -- true *within* build_state(), not across this module's
    own separate stage 3 pass). vault.discover() measured ~8.5s live per
    state_bundles.py's own docstring, so this is the single largest
    avoidable cost in the whole build if a future task wires ctx-reuse into
    build_state() itself.
  - news_sec.news_bundle() runs twice for the same reason: once inside
    search_index.build_units() (stage 4, which has no pre-built `news` to
    reuse yet -- build_state() hasn't run) and again inside build_state()
    itself (stage 5, which writes data/news/*.json). The brief's mandated
    order (search index BEFORE build_state, so search.json is hashed into
    the manifest) makes this unavoidable without changing build_state()'s
    own internals, which is out of scope here.

Every zero-arg-default path in the five builder modules already reads live
data from REPO (see scripts/portal/__init__.py) -- this module adds no new
REPO-reading logic beyond what's documented above, and its own writes are
strictly confined to `<out_dir>/.tmp-<pid>` (published atomically into
`out_dir`) and a `tempfile.mkdtemp()` scratch dir for --dry-run (deleted
before this module returns). Never notes/, config/, or state/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Callable

# Bootstrap ONLY to make this package importable when run directly (`python3
# scripts/portal/build_portal.py`, which puts scripts/portal/ -- not scripts/
# -- on sys.path[0]) or loaded as a bare `build_portal` module by the
# no-pytest test harness convention. Same two-insert shape as
# state_bundles.py / search_index.py: scripts/ parent so `from portal import
# REPO` resolves, and scripts/portal/ itself so the sibling modules below
# resolve as bare imports.
_here = Path(__file__).resolve().parent             # scripts/portal
_here_parent = str(_here.parent)                     # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

_here_str = str(_here)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import budget                  # noqa: E402
import etf_trades as etf        # noqa: E402
import evidence as ev             # noqa: E402
import identity                    # noqa: E402
import reports as rp                # noqa: E402
import search_index as si            # noqa: E402
import state_bundles as sb            # noqa: E402
import vault                           # noqa: E402


def log(msg: str) -> None:
    print(f"[build_portal] {msg}", flush=True)


# ---------------------------------------------------------------------------
# small IO/collection helpers (duplicated single-purpose helpers, same
# convention state_bundles.py's own `_known_sets`/`_write_json` already use --
# see those docstrings for why a private name is duplicated rather than
# imported across modules)
# ---------------------------------------------------------------------------
def _known_sets(refs: list) -> tuple[set, set]:
    tickers = {r.ticker for r in refs if r.ticker}
    themes = {Path(r.rel).stem for r in refs if r.kind == "theme"}
    return tickers, themes


def _write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


# ---------------------------------------------------------------------------
# atomic build engine -- REPO-free, exercised directly by test_build_portal.py
# ---------------------------------------------------------------------------
def run_stages(tmp_dir: Path, stages: list[tuple[str, Callable[[Path], dict]]]) -> dict:
    """Run each (name, fn) in order; fn(tmp_dir) writes under tmp_dir and
    returns a small stats dict, logged with the stage's own elapsed time.
    Propagates the FIRST exception unchanged and stops -- later stages never
    run, and the caller (build()/dry_run()) owns tmp_dir cleanup from there.
    """
    stats = {}
    for name, fn in stages:
        t0 = time.monotonic()
        log(f"stage {name}: starting")
        result = fn(tmp_dir)
        elapsed = time.monotonic() - t0
        log(f"stage {name}: done in {elapsed:.1f}s ({result})")
        stats[name] = result
    return stats


def _new_tmp_dir(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir / f".tmp-{os.getpid()}"
    if tmp_dir.exists():          # leftover from a killed prior run under this same pid
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    return tmp_dir


# fix round 1 (Critical, controller-directed): stale-file removal must be
# scoped to exactly what this builder is allowed to own. The unscoped version
# deleted portal_build/smoke/ (a Phase 0 artifact source that ISN'T builder
# output) in the first live run. OWNED_PATHS is the exhaustive list of
# top-level things build_portal.py is ever allowed to write, publish-replace,
# or remove-as-stale -- a directory entry (trailing "/") matches by prefix,
# a bare name matches exactly. Anything else already under out_dir (e.g.
# smoke/, or any other operator-placed content) is invisible to `_publish` --
# never listed, never removed, never pruned -- no matter what `stages`
# produced or didn't produce this run.
OWNED_PATHS = ("data/", "vendor/", "index.html", "app.js", "app2.js", "styles.css")


def _is_owned(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in OWNED_PATHS)


def _publish(tmp_dir: Path, out_dir: Path) -> tuple[int, int]:
    """os.replace every file from tmp_dir (assumed to be `<out_dir>/.tmp-*`)
    into its matching path under out_dir, then remove any file already under
    out_dir, UNDER AN OWNED_PATHS PREFIX, that this build did NOT produce
    (stale removal -- see OWNED_PATHS' own comment for why the scope check
    exists), then prune any now-empty directory strictly under data/ or
    vendor/. Returns (n_published, n_removed_stale). Any other `.tmp-*`
    sibling directory under out_dir (a DIFFERENT pid's in-flight build) is
    left completely alone by both the publish and the stale-removal passes,
    as is everything outside OWNED_PATHS.

    ATOMICITY NOTE (fix round 1, Important): publishing itself is atomic
    PER FILE (each `os.replace` is a single atomic rename), not atomic as a
    whole tree -- if this function raises partway through (a later
    `os.replace` fails, e.g. ENOSPC or a permissions error), every file
    replaced before the failure is already live under out_dir and every file
    not yet reached is unaffected; there is a narrow window where out_dir can
    hold a MIX of a new build's files and a prior build's files. The caller
    (`build()`) catches any such exception, discards tmp_dir, and returns a
    non-zero exit rather than silently reporting success -- see its own
    docstring. This is a real, accepted gap (full per-tree atomicity would
    need a swappable top-level symlink, out of scope here), not a claim that
    it can't happen.
    """
    produced = set()
    for p in sorted(tmp_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(tmp_dir)
        produced.add(rel.as_posix())
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(p, target)

    removed = 0
    for p in sorted(out_dir.rglob("*"), reverse=True):  # children before parents
        rel_parts = p.relative_to(out_dir).parts
        if not rel_parts or rel_parts[0].startswith(".tmp-"):
            continue
        rel = p.relative_to(out_dir).as_posix()
        if p.is_file():
            if not _is_owned(rel):
                continue   # never touch anything outside OWNED_PATHS
            if rel not in produced:
                p.unlink()
                removed += 1
                log(f"removed stale file: {rel}")
        elif p.is_dir():
            if rel_parts[0] not in ("data", "vendor"):
                continue   # only prune empty dirs strictly under data/ or vendor/
            try:
                p.rmdir()   # only succeeds once empty -- a harmless no-op otherwise
            except OSError:
                pass

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return len(produced), removed


def build(out_dir: Path, stages: list[tuple[str, Callable[[Path], dict]]]) -> int:
    """Run `stages` into a fresh `<out_dir>/.tmp-<pid>`, print the budget
    table, then either publish (0) or leave `out_dir` untouched and return
    1 (a stage raised, OR publishing itself raised -- see _publish()'s own
    "ATOMICITY NOTE" docstring section for the narrow per-file-not-per-tree
    exception) or 2 (budget.check() violation) -- a failing stage or a
    budget breach never reaches `out_dir` at all, so whatever a prior
    successful build already published there survives unchanged.
    """
    out_dir = Path(out_dir)
    tmp_dir = _new_tmp_dir(out_dir)
    t_start = time.monotonic()
    try:
        run_stages(tmp_dir, stages)
    except Exception as exc:  # noqa: BLE001 -- any stage failure aborts the whole build
        log(f"BUILD FAILED: {type(exc).__name__}: {exc} -- discarding {tmp_dir}, "
            f"{out_dir} left untouched")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return 1

    print(budget.table(tmp_dir))
    violations = budget.check(tmp_dir)
    if violations:
        log("BUDGET VIOLATIONS (build NOT published -- previous tree, if any, is untouched):")
        for v in violations:
            log(f"  - {v}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return 2

    try:
        n_published, n_removed = _publish(tmp_dir, out_dir)
    except Exception as exc:  # noqa: BLE001 -- fix round 1 (Important): a mid-publish
        # failure must not be silently swallowed or reported as success. Some files may
        # already be live under out_dir (each os.replace() is atomic per-file, not the
        # whole tree -- see _publish()'s own "ATOMICITY NOTE"); this only discards
        # whatever's left in tmp_dir and reports failure, it does not attempt to roll
        # back files already replaced.
        log(f"PUBLISH FAILED: {type(exc).__name__}: {exc} -- discarding remaining "
            f"{tmp_dir}; {out_dir} may be PARTIALLY updated (files already replaced "
            f"before the failure stay published -- publishing is atomic per file, "
            f"not per tree)")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return 1

    elapsed = time.monotonic() - t_start
    log(f"published {n_published} file(s), removed {n_removed} stale file(s), "
        f"total {elapsed:.1f}s")
    return 0


def dry_run(stages: list[tuple[str, Callable[[Path], dict]]]) -> int:
    """Runs `stages` into a throwaway tempfile.mkdtemp() scratch dir that is
    NOT under --out (--out is never created, stat()ed, or otherwise touched),
    prints the same budget table + a counts/bytes summary a real build would
    publish, then discards the scratch dir entirely. Returns 0 clean / 2
    budget violation, matching build()'s own convention; a stage exception
    still propagates (there's nothing sensible to catch on preview data).
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="ris4-portal-dry-run-"))
    try:
        run_stages(tmp_dir, stages)
        n = sum(1 for p in tmp_dir.rglob("*") if p.is_file())
        total = sum(p.stat().st_size for p in tmp_dir.rglob("*") if p.is_file())
        log(f"[dry-run] would write {n} file(s), {total} bytes total -- nothing written to --out")
        print(budget.table(tmp_dir))
        violations = budget.check(tmp_dir)
        if violations:
            log("[dry-run] BUDGET VIOLATIONS:")
            for v in violations:
                log(f"  - {v}")
            return 2
        return 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# production stages -- live REPO only, not exercised by test_build_portal.py
# ---------------------------------------------------------------------------
def _stage_reports(ctx: sb.Ctx, today: date) -> Callable[[Path], dict]:
    def fn(tmp_dir: Path) -> dict:
        summaries = rp.build_reports(tmp_dir, days=ctx.reports_days, today=today)
        ctx.report_summaries = summaries   # manifest() reuses this instead of re-running build_reports(days=1)
        return {"cards": len(summaries)}
    return fn


def _stage_etf_trades(ctx: sb.Ctx, today: date) -> Callable[[Path], dict]:
    def fn(tmp_dir: Path) -> dict:
        result = etf.etf_trades(days=ctx.reports_days, out_dir=tmp_dir, today=today)
        return {"days": len(result.get("days") or []), "tickers": len(result.get("by_ticker") or {})}
    return fn


def _stage_tickers_ingest(ctx: sb.Ctx, sb_paths: sb.Paths, shared: dict,
                           today: date) -> Callable[[Path], dict]:
    def fn(tmp_dir: Path) -> dict:
        refs = vault.discover(sb_paths.notes)
        universe = identity.load_universe(sb_paths.watchlist, sb_paths.notes)
        names = identity.display_names(sb_paths.watchlist, notes_dir=sb_paths.notes)
        known_tickers, known_themes = _known_sets(refs)
        # loaded once for the whole ticker loop below (2,685 rows as of
        # 2026-09-16) -- evidence.py's own docstring on why this is cheap
        # relative to re-reading it per ticker.
        evidence_index = ev.load_index(ev.Paths(thesis_state=sb_paths.thesis_state))

        bundles: dict = {}
        n_tickers = n_pvt = n_skipped = 0
        for e in universe:
            tk = e["ticker"]
            b = vault.ticker_bundle(tk, refs, names, known_tickers, known_themes, meta=e)
            # BEFORE the file is written below -- see evidence.attach_thesis's
            # own docstring for why this ordering keeps the manifest's file
            # hashing (Task 4, state_bundles.manifest(), run at the LAST
            # stage) intact.
            ev.attach_thesis(b, evidence_index)
            bundles[tk] = b
            has_notes = bool(b["notes"]) or bool(b["thesis"]["fm_without_body"]) or bool(b["profile"])
            if not has_notes:
                n_skipped += 1
                continue
            if tk.endswith(".pvt"):
                slug = tk[: -len(".pvt")]
                _write_json(tmp_dir / "data" / "pvt" / f"{slug}.json", b)
                n_pvt += 1
            else:
                _write_json(tmp_dir / "data" / "tickers" / f"{tk}.json", b)
                n_tickers += 1

        ingest = vault.ingest_bundles(refs, days=ctx.news_days, today=today)
        for bucket, payload in ingest.items():
            _write_json(tmp_dir / "data" / "ingest" / f"{bucket}.json", payload)

        # cached for stage 4 (search index) to reuse without re-discovering/re-building
        shared["refs"], shared["ingest"] = refs, ingest
        ctx.refs, ctx.universe, ctx.ticker_bundles = refs, universe, bundles

        return {"tickers": n_tickers, "pvt": n_pvt, "tickers_without_notes": n_skipped,
                "ingest_buckets": len(ingest),
                "ingest_items": sum(len(v["items"]) for v in ingest.values())}
    return fn


def _stage_search_index(ctx: sb.Ctx, sb_paths: sb.Paths, shared: dict,
                         today: date) -> Callable[[Path], dict]:
    def fn(tmp_dir: Path) -> dict:
        units = si.build_units(paths=si.Paths(notes=sb_paths.notes), refs=shared.get("refs"),
                                ingest=shared.get("ingest"), today=today, news_days=ctx.news_days)
        return si.write_index(tmp_dir, units, today=today)
    return fn


def _stage_build_state(ctx: sb.Ctx) -> Callable[[Path], dict]:
    def fn(tmp_dir: Path) -> dict:
        return sb.build_state(tmp_dir, ctx)
    return fn


def _copy_app(tmp_dir: Path, app_src: Path = None) -> dict:
    """Copies index.html/styles.css/app.js/app2.js + every file under vendor/ from
    scripts/portal/app/ (Task 7/8, does not exist yet) into tmp_dir's root
    (NOT under data/ -- these are top-level, served alongside data/). Missing
    app_src entirely (the current, pre-Task-7/8 state) is a clean no-op, not
    an error -- see the module docstring's "6." stage description.
    """
    app_src = app_src if app_src is not None else (_here / "app")
    if not app_src.is_dir():
        log(f"app: {app_src} not found (Task 7/8 not built yet) -- skipping app copy")
        return {"copied": 0}

    copied = 0
    for rel_name in ("index.html", "styles.css", "app.js", "app2.js"):
        src = app_src / rel_name
        if not src.is_file():
            log(f"app: {rel_name} missing under {app_src} -- skipped")
            continue
        dst = tmp_dir / rel_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        copied += 1

    vendor_src = app_src / "vendor"
    if vendor_src.is_dir():
        for p in sorted(vendor_src.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(app_src)
            dst = tmp_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(p.read_bytes())
            copied += 1
    else:
        log(f"app: {vendor_src} absent -- no vendor/ files to copy")

    return {"copied": copied}


def _default_stages(args: argparse.Namespace) -> list[tuple[str, Callable[[Path], dict]]]:
    today = date.today()
    ctx = sb.Ctx(today=today, news_days=args.news_days, sec_days=args.sec_days,
                 reports_days=args.reports_days)
    sb_paths = sb.DEFAULT_PATHS
    shared: dict = {}

    stages = [
        ("reports", _stage_reports(ctx, today)),
        ("etf_trades", _stage_etf_trades(ctx, today)),
        ("tickers_and_ingest", _stage_tickers_ingest(ctx, sb_paths, shared, today)),
        ("search_index", _stage_search_index(ctx, sb_paths, shared, today)),
    ]
    if not args.no_app:
        # MUST run before "state" -- state_bundles.build_state() writes
        # data/manifest.json LAST and hashes every file already on disk under
        # out_dir at that moment (manifest()'s own docstring). An app stage
        # appended after "state" would publish index.html/styles.css/app.js/
        # vendor/* successfully but leave them OUT of manifest.files forever.
        stages.append(("app", lambda tmp_dir: _copy_app(tmp_dir)))
    stages.append(("state", _stage_build_state(ctx)))
    return stages


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _parse_args(argv: list[str] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build the RIS4 mobile-web portal JSON bundles (+ app/ copy) into --out.")
    p.add_argument("--out", type=Path, default=REPO / "portal_build",
                    help="output directory (default: REPO/portal_build)")
    p.add_argument("--format", choices=["json"], default="json",
                    help="output format (only json is implemented)")
    p.add_argument("--news-days", type=int, default=30)
    p.add_argument("--sec-days", type=int, default=30)
    p.add_argument("--reports-days", type=int, default=14)
    p.add_argument("--dry-run", action="store_true",
                    help="build into a scratch dir, print counts/sizes, write nothing to --out")
    p.add_argument("--no-app", action="store_true",
                    help="skip copying scripts/portal/app/ into --out")
    return p.parse_args(argv)


def main(argv: list[str] = None) -> int:
    args = _parse_args(argv)
    log(f"out={args.out} format={args.format} news_days={args.news_days} "
        f"sec_days={args.sec_days} reports_days={args.reports_days} "
        f"dry_run={args.dry_run} no_app={args.no_app}")
    stages = _default_stages(args)
    if args.dry_run:
        return dry_run(stages)
    return build(Path(args.out), stages)


if __name__ == "__main__":
    sys.exit(main())
