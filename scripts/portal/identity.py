"""Identity: ticker universe assembly, display-name resolution, and a name-backfill
CLI for the RIS4 portal builder.

Every zero-arg-default path here reads live data from REPO (see
scripts/portal/__init__.py) -- never from a worktree checkout. Every public
function also accepts explicit path overrides so tests can point at fixtures
under scripts/portal/fixtures/identity/ instead. Read-only except the
--merge-names --write path, which appends to config/ticker_identity.yaml and
never touches config/watchlist.yaml, notes/, or state/.

Sources composed here:
  - config/watchlist.yaml: tier_1_bctk / tier_2_active_candidates /
    tier_3_watchlist (the universe), plus tier_4_ecosystem and private_drivers
    (name lookups keyed by id / pvt_id).
  - config/ticker_identity.yaml: the news-digest name/FactSet-id/Google-query
    map (Phase C). id_maps() in scripts/chunking/ingest_metrics.py already
    knows how to read its factset_id column with a TICKER-US default.
  - scripts/portal/fixtures/names_backfill_20260915.json: a one-time manual
    backfill (InsiderScore get_company_info + a handful of manual entries) for
    tickers/ids ticker_identity.yaml doesn't cover yet. display_names() reads
    it as a live source (not just a test fixture) so foreign/private ids that
    are deliberately never written into ticker_identity.yaml (see
    _skip_from_yaml_write) still resolve to a real name at build time. This
    stays true even after a --merge-names --write run: A000660, UMG.AS,
    2308.TW and simaai.pvt are permanently skipped from the YAML write (their
    TICKER-US id would be wrong), so the backfill JSON remains the ONLY
    source for their display names indefinitely -- it is not a one-time
    scaffold that can be deleted once the write has happened.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

# Bootstrap ONLY to make this package importable when this module is loaded as a bare
# `identity` module (the no-pytest test harness convention: sys.path.insert(0, dirname)
# + `import identity`, same as scripts/v3_ingest/test_transcript_ingest.py and
# scripts/portal/vault.py). This uses __file__ solely to find our OWN sibling
# __init__.py. Once REPO is known, ingest_metrics is always imported from the
# CANONICAL REPO/scripts/chunking, per the brief's literal form.
_here_parent = str(Path(__file__).resolve().parent.parent)
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "chunking"))
import ingest_metrics  # noqa: E402

TIERS = ("tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist")
_SCORE_KEYS = ("ai_positioning", "competitive_advantage", "potential_investor_interest")

# Top-level notes/ dirs that are never ticker/pvt-id directories (mirrors
# vault.EXCLUDED_TOP plus vault._TOP_DIR_KIND -- kept as a local literal rather than
# importing vault's private module constants).
_NON_TICKER_TOP_DIRS = {
    "inbox", "news", "sec", "themes", "reports", "substacks",
    "podcasts", "flows", "foreign", "sector",
}

# Sibling asset (ships inside scripts/portal/, next to this file), resolved via
# __file__ like vault.py's own sys.path bootstrap -- NOT REPO-based, because unlike
# notes/config (live, mutable, canonical-only data) this fixture is part of the
# portal package's own checked-in code and must resolve correctly even before this
# branch is merged to the canonical REPO path.
DEFAULT_BACKFILL_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "names_backfill_20260915.json"
BACKFILL_LABEL_DATE = "2026-09-15"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------
def load_universe(watchlist_path: Path | None = None, notes_dir: Path | None = None) -> list[dict]:
    """Every tier_1/tier_2/tier_3 entry in config/watchlist.yaml, deduped by ticker
    (first tier in TIERS order wins; the other tier(s) it also appears in are
    recorded under "also_in"), plus tickers with a notes/<T>/ dir but no watchlist
    entry at all (tier: "none", orphan_notes: True). "scores" is present only when
    the entry carries at least one of the three scoring blocks.
    """
    watchlist_path = watchlist_path or (REPO / "config" / "watchlist.yaml")
    notes_dir = notes_dir if notes_dir is not None else (REPO / "notes")
    wl = _load_yaml(watchlist_path)

    by_ticker: dict[str, dict] = {}
    for tier in TIERS:
        for e in wl.get(tier) or []:
            if not isinstance(e, dict) or not e.get("ticker"):
                continue
            tk = e["ticker"]
            if tk in by_ticker:
                by_ticker[tk].setdefault("also_in", [])
                if tier not in by_ticker[tk]["also_in"]:
                    by_ticker[tk]["also_in"].append(tier)
                continue
            entry = {"ticker": tk, "tier": tier, "themes": e.get("themes") or []}
            scores = {k: e[k] for k in _SCORE_KEYS if k in e}
            if scores:
                entry["scores"] = scores
            by_ticker[tk] = entry

    if notes_dir.is_dir():
        for p in sorted(notes_dir.iterdir()):
            if not p.is_dir():
                continue
            tk = p.name
            if tk in by_ticker or tk in _NON_TICKER_TOP_DIRS:
                continue
            by_ticker[tk] = {"ticker": tk, "tier": "none", "themes": [], "orphan_notes": True}

    return list(by_ticker.values())


# ---------------------------------------------------------------------------
# Display names
# ---------------------------------------------------------------------------
def _name_layers(watchlist_path: Path | None, identity_path: Path | None,
                  backfill_path: Path | None) -> tuple[dict, dict, dict, dict]:
    watchlist_path = watchlist_path or (REPO / "config" / "watchlist.yaml")
    identity_path = identity_path or (REPO / "config" / "ticker_identity.yaml")
    backfill_path = backfill_path if backfill_path is not None else DEFAULT_BACKFILL_FIXTURE

    wl = _load_yaml(watchlist_path)
    identity = _load_yaml(identity_path)
    backfill: dict = {}
    if backfill_path and Path(backfill_path).exists():
        backfill = json.loads(Path(backfill_path).read_text(encoding="utf-8")).get("names") or {}

    identity_names = {tk: v.get("name") for tk, v in identity.items()
                       if isinstance(v, dict) and v.get("name")}
    private_names = {d["pvt_id"]: d["name"] for d in wl.get("private_drivers") or []
                      if isinstance(d, dict) and d.get("pvt_id") and d.get("name")}
    tier4_names = {t["id"]: t["name"] for t in wl.get("tier_4_ecosystem") or []
                   if isinstance(t, dict) and t.get("id") and t.get("name")}
    return identity_names, private_names, tier4_names, backfill


def display_names(watchlist_path: Path | None = None, identity_path: Path | None = None,
                   backfill_path: Path | None = None, notes_dir: Path | None = None) -> dict[str, str]:
    """Union, in precedence order, of: ticker_identity.yaml[T].name -> private_drivers[].name
    (keyed by pvt_id) -> tier_4_ecosystem[].name (keyed by id) -> the backfill JSON -> the
    bare ticker. Domain is every identifier load_universe() returns plus every key any of
    the four sources itself defines (so tier_4/private-driver/backfill-only ids resolve too).
    """
    identity_names, private_names, tier4_names, backfill = _name_layers(
        watchlist_path, identity_path, backfill_path)
    universe_tickers = {e["ticker"] for e in load_universe(watchlist_path, notes_dir)}
    domain = universe_tickers | set(identity_names) | set(private_names) | set(tier4_names) | set(backfill)
    return {
        tk: (identity_names.get(tk) or private_names.get(tk) or tier4_names.get(tk)
             or backfill.get(tk) or tk)
        for tk in domain
    }


def missing_names(watchlist_path: Path | None = None, identity_path: Path | None = None,
                   backfill_path: Path | None = None, notes_dir: Path | None = None) -> list[str]:
    """Identifiers in the display_names() domain that aren't resolved by any real
    source (ticker_identity/private_drivers/tier_4/backfill) -- i.e. would fall back
    to the bare-ticker default. Sorted for deterministic output.
    """
    identity_names, private_names, tier4_names, backfill = _name_layers(
        watchlist_path, identity_path, backfill_path)
    universe_tickers = {e["ticker"] for e in load_universe(watchlist_path, notes_dir)}
    covered = set(identity_names) | set(private_names) | set(tier4_names) | set(backfill)
    domain = universe_tickers | covered
    return sorted(domain - covered)


# ---------------------------------------------------------------------------
# FactSet ids
# ---------------------------------------------------------------------------
def factset_ids(tickers: list[str] | None = None, watchlist_path: Path | None = None,
                 notes_dir: Path | None = None) -> dict[str, str | None]:
    """ticker -> FactSet id via ingest_metrics.id_maps (TICKER-US default, overridden
    per-ticker by config/ticker_identity.yaml's factset_id column) -- EXCEPT for any
    ticker _skip_from_yaml_write() flags as not a plain US ticker (.pvt ids, and
    foreign/digit-containing ids like A000660/UMG.AS/2308.TW): id_maps' TICKER-US
    default is fabricated and simply wrong for those (there is no "UMG.AS-US"),
    so they resolve to None here UNLESS config/ticker_identity.yaml itself carries
    an explicit factset_id for that identifier (an operator-entered real mapping).

    Reads config/ticker_identity.yaml from ingest_metrics.REPO -- the same path
    id_maps() itself resolves against (tests monkeypatch that, not portal.REPO) --
    so the explicit-mapping check always agrees with what id_maps() returned.
    """
    if tickers is None:
        tickers = [e["ticker"] for e in load_universe(watchlist_path, notes_dir)]
    tk_to_fid, _ = ingest_metrics.id_maps(tickers)

    idmap = _load_yaml(ingest_metrics.REPO / "config" / "ticker_identity.yaml")

    result: dict[str, str | None] = {}
    for tk in tickers:
        entry = idmap.get(tk)
        explicit = entry.get("factset_id") if isinstance(entry, dict) else None
        if _skip_from_yaml_write(tk) and not explicit:
            result[tk] = None
        else:
            result[tk] = tk_to_fid.get(tk)
    return result


# ---------------------------------------------------------------------------
# Name-backfill CLI: identity.py --merge-names FILE [--write] / --missing
# ---------------------------------------------------------------------------
class MergeAbortedError(RuntimeError):
    """Raised when appending the backfill block would corrupt config/ticker_identity.yaml
    (the after-parse fails, or any pre-existing top-level key's value would change)."""


def _skip_from_yaml_write(ticker: str) -> bool:
    """.pvt ids and non-plain-US-ticker ids (anything with a dot or a digit, e.g.
    A000660, UMG.AS, 2308.TW) are never written into ticker_identity.yaml here --
    id_maps' TICKER-US default would be wrong for them. Their names still come
    through via display_names()'s backfill layer at build time.
    """
    if ticker.endswith(".pvt"):
        return True
    return not (ticker.isalpha() and ticker.isupper())


def _backfill_entry_block(ticker: str, name: str) -> str:
    # The key is ALWAYS double-quoted, even for plain-looking tickers, never bare
    # `{ticker}:`. PyYAML (yaml 1.1, PyYAML's actual resolver behavior) treats bare
    # ON/OFF/YES/NO/TRUE/FALSE/Y/N (any case) as booleans, not strings -- a bare `ON:`
    # key silently becomes the boolean key True on reparse, which both mis-stores the
    # entry AND breaks the "already present" check on every subsequent run (see
    # merge_names' existing_keys), causing ON to be re-appended as a duplicate
    # top-level key each time. json.dumps() gives correct YAML double-quote escaping.
    google_name = name.replace("'", "''")
    return (
        f"{json.dumps(ticker)}:\n"
        f"  name: {json.dumps(name)}\n"
        f'  factset_id: "{ticker}-US"          '
        f"# per id_maps default; foreign tickers keep their existing mapping if any\n"
        f"  google: '\"{google_name}\" OR {ticker} stock'\n"
    )


def _safe_append(path: Path, addition: str) -> None:
    """Append `addition` to `path`, re-parsing before and after. Aborts (raises
    MergeAbortedError, file untouched) if the after-parse fails, or if any
    pre-existing top-level key's value would change (covers outright loss and the
    YAML last-key-wins corruption case where a duplicate key silently overwrites
    the original entry).
    """
    before_text = path.read_text(encoding="utf-8")
    before = yaml.safe_load(before_text) or {}

    new_text = before_text
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += "\n" + addition

    try:
        after = yaml.safe_load(new_text)
    except yaml.YAMLError as exc:
        raise MergeAbortedError(f"after-parse failed: {exc}") from exc
    if after is None:
        raise MergeAbortedError("after-parse produced no data")

    changed = [k for k, v in before.items() if after.get(k) != v]
    if changed:
        raise MergeAbortedError(f"merge would alter/lose existing key(s): {sorted(changed)}")

    # Atomic write: a sibling temp file (same directory -> same filesystem, so
    # os.replace is a single atomic rename) rather than a direct write_text, so a
    # crash mid-write can never leave `path` half-written.
    fd, tmp_name = tempfile.mkstemp(prefix=".identity-merge-", suffix=".tmp",
                                     dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def merge_names(json_path: Path, identity_path: Path | None = None,
                 write: bool = False) -> tuple[str, list[str]]:
    """(block_text, appended_tickers). block_text is "" and appended_tickers is []
    when there is nothing new to add (idempotent re-run). Only tickers not already
    a key in identity_path AND not skipped by _skip_from_yaml_write are appended.
    Without write=True this is a pure dry run: the file is never touched.
    """
    identity_path = identity_path or (REPO / "config" / "ticker_identity.yaml")
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    names = data.get("names") or {}
    source = data.get("source", "")

    existing = _load_yaml(identity_path)
    # Compare by str(k): a loaded key need not be a python str (e.g. a legacy bare
    # ON/OFF/YES/NO-style key that YAML's boolean resolver already coerced before this
    # module ever quoted its writes) -- `tk not in existing` would miss that and
    # re-append a ticker that is, textually, already present.
    existing_keys = {str(k) for k in existing}
    to_add = sorted(tk for tk in names if tk not in existing_keys and not _skip_from_yaml_write(tk))
    if not to_add:
        return "", []

    header = f"# ---- portal name backfill {BACKFILL_LABEL_DATE} (source: {source}) ----\n"
    block = header + "".join(_backfill_entry_block(tk, names[tk]) for tk in to_add)

    if write:
        _safe_append(identity_path, block)

    return block, to_add


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-names", metavar="FILE",
                     help="backfill JSON ({'names': {ticker: name}, 'source': ...})")
    ap.add_argument("--write", action="store_true",
                     help="append to ticker_identity.yaml (default: dry run, print only)")
    ap.add_argument("--missing", action="store_true",
                     help="print identifiers with no resolvable display name, one per line")
    args = ap.parse_args(argv)

    if args.merge_names:
        json_path = Path(args.merge_names)
        if not json_path.exists():
            print(f"ERROR: {json_path} not found", file=sys.stderr)
            return 1
        try:
            block, added = merge_names(json_path, write=args.write)
        except MergeAbortedError as exc:
            print(f"ABORTED: {exc}", file=sys.stderr)
            return 1
        if not added:
            print("nothing to merge: 0 entries would be appended")
        else:
            print(block, end="")
            verb = "appended" if args.write else "would append"
            print(f"\n# {len(added)} entries {verb}")
        return 0

    if args.missing:
        for tk in missing_names():
            print(tk)
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
