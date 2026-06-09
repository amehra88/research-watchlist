#!/usr/bin/env python3
"""migrate_spacex_to_spcx.py — pre-staged `.pvt` -> ticker promotion for the SpaceX IPO.

DRY-RUN BY DEFAULT: prints a unified diff of every change and writes nothing.
Pass --apply to perform the changes. Idempotent (safe to re-run).

State-aware: the SPCX pending stub already lives in `tier_2_active_candidates`
(NOT tier_3 as the original spec assumed), so this ENRICHES that entry in place
and REMOVES the `private_drivers` entry — it does not add a duplicate T2 entry.
Promotion to T1 is out of scope (the BCTK scraper handles T2/T3 -> T1).

Touches:
  1. config/watchlist.yaml          — remove private_drivers spacex.pvt; enrich T2 SPCX entry
  2. config/ticker_identity.yaml    — add SPCX identity (factset_id SPCX-US, google query)
  3. /root/research/config/supply-chain-manual.yaml — retarget `target: spacex.pvt` -> SPCX
  4. notes/spacex.pvt/ -> notes/SPCX/  — git mv the directory (carries _profile.md)

Review the dry-run diff and run scripts/check.py before --apply.
"""
import argparse
import difflib
import io
import subprocess
import sys
from datetime import date
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq

RW = Path("/root/research-watchlist")
WL = RW / "config/watchlist.yaml"
TI = RW / "config/ticker_identity.yaml"
SCM = Path("/root/research/config/supply-chain-manual.yaml")
NOTES_SRC = RW / "notes/spacex.pvt"
NOTES_DST = RW / "notes/SPCX"

PVT_ID = "spacex.pvt"
TICKER = "SPCX"
TODAY = date.today().isoformat()  # stamp at run time (Friday), not at staging time

ENRICHED_THEMES = ["space_economy", "frontier_model_competition", "ai_infrastructure_capex"]
ENRICHED_NOTES = (
    f"SpaceX (Space Exploration Technologies). Public as of {TODAY} on Nasdaq (SPCX); "
    "IPO priced ~$135/share fixed, ~$1.75T valuation. Consolidated entity: launch "
    "services + Starlink (~58% of FY24 rev) + xAI/Grok (absorbed 2026-02-02, folded "
    "into SpaceX's AI division May 2026). Major NVDA compute consumer (Colossus; Vera "
    "CPU early adopter; planned orbital DCs). Read-through: NVDA, GEV (power), TSLA (Grok). "
    "Contingencies still riding on this name: EchoStar spectrum + Cursor/Anysphere "
    "(operator signal, non-public) deals — fold Cursor in on close, no standalone .pvt. "
    "Promote to T1 automatically when SPCX appears in BCTK. See notes/SPCX/_profile.md."
)

TI_BLOCK = (
    "\n# ── Added on SpaceX IPO (spacex.pvt -> SPCX promotion) ──\n"
    f'{TICKER}:\n'
    '  name: "SpaceX"\n'
    f'  factset_id: "{TICKER}-US"\n'
    f"  google: '\"SpaceX\" OR {TICKER} stock'\n"
)


# New supply-chain edges that replace the read-throughs formerly encoded in the
# spacex.pvt `affects: [NVDA, GEV, TSLA]` list. NVDA is preserved by retargeting
# the existing NVDA->spacex.pvt edge; GEV and TSLA need fresh edges.
GEV_EDGE = (
    "- source: GEV\n"
    f"  target: {TICKER}\n"
    "  kind:\n"
    "  - supplier\n"
    "  significance: medium\n"
    "  notes: Data-center power read-through. GEV growth narrative has shifted toward "
    "data-center power (gas turbines, grid equipment) and SpaceX is a major data-center "
    "power consumer via xAI/Grok training (Colossus) and Starlink ground operations. "
    "Created on the SpaceX IPO 2026-06-12, replacing the read-through formerly encoded in "
    "the spacex.pvt private_drivers affects list.\n"
    "  provenance: manual\n"
)
TSLA_EDGE = (
    "- source: TSLA\n"
    f"  target: {TICKER}\n"
    "  kind:\n"
    "  - competitor\n"
    "  significance: medium\n"
    "  notes: Primary kind competitor reflects technology adjacency — Tesla (Optimus, "
    "Dojo, FSD compute) and SpaceX/SpaceXAI (Grok training compute) overlap on AI and "
    "robotics training infrastructure. Operator-flagged dimension is governance — "
    "shared-CEO (Musk) concentration risk across both names, encoded as competitor since "
    "the schema has no governance_link kind. Created on the SpaceX IPO 2026-06-12, "
    "replacing the spacex.pvt affects read-through.\n"
    "  provenance: manual\n"
)
# (marker that proves the edge already exists -> idempotent skip, block to append)
SCM_NEW_EDGES = [
    (f"- source: GEV\n  target: {TICKER}", GEV_EDGE),
    (f"- source: TSLA\n  target: {TICKER}", TSLA_EDGE),
]


def _yaml():
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def _diff(path, old, new):
    if old == new:
        return f"  (no change to {path})\n"
    d = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    )
    return "".join(d)


def _flow(items):
    seq = CommentedSeq(items)
    seq.fa.set_flow_style()
    return seq


def transform_watchlist(text):
    y = _yaml()
    data = y.load(text)
    notes = []

    # 1. remove private_drivers entry (in-place del to preserve sibling comments)
    pd = data.get("private_drivers") or []
    removed = False
    for i, e in enumerate(pd):
        if e.get("pvt_id") == PVT_ID:
            del pd[i]
            removed = True
            break
    notes.append("removed private_drivers spacex.pvt" if removed
                 else "private_drivers spacex.pvt NOT found (already migrated?)")

    # 2. find SPCX entry across tiers; enrich in place (or create in T2 as fallback)
    found_tier = None
    for tier in ("tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist"):
        for e in (data.get(tier) or []):
            if e.get("ticker") == TICKER:
                found_tier, entry = tier, e
                break
        if found_tier:
            break
    if found_tier:
        entry["themes"] = _flow(ENRICHED_THEMES)
        entry["notes"] = ENRICHED_NOTES
        entry["added_date"] = entry.get("added_date", TODAY)
        notes.append(f"enriched existing SPCX entry in {found_tier}")
    else:
        new_entry = {"ticker": TICKER, "themes": _flow(ENRICHED_THEMES),
                     "added_date": TODAY, "notes": ENRICHED_NOTES}
        data.setdefault("tier_2_active_candidates", CommentedSeq()).append(new_entry)
        notes.append("SPCX not found in any tier -> created in tier_2_active_candidates")

    buf = io.StringIO()
    y.dump(data, buf)
    return buf.getvalue(), notes


def transform_ticker_identity(text):
    if f"\n{TICKER}:" in text or text.startswith(f"{TICKER}:"):
        return text, ["SPCX already in ticker_identity.yaml (skip)"]
    new = text if text.endswith("\n") else text + "\n"
    new += TI_BLOCK
    return new, ["appended SPCX identity block"]


def transform_supply_chain(text):
    notes = []
    new = text
    # a. retarget the existing NVDA->spacex.pvt edge (historical comment left as-is)
    old_line = f"target: {PVT_ID}"
    if old_line in new:
        new = new.replace(old_line, f"target: {TICKER}")
        notes.append(f"retargeted `target: {PVT_ID}` -> `target: {TICKER}` "
                     "(historical comment left as-is)")
    else:
        notes.append(f"no `target: {PVT_ID}` to retarget (already migrated?)")
    # b. append GEV/TSLA read-through edges (idempotent)
    if not new.endswith("\n"):
        new += "\n"
    for marker, block in SCM_NEW_EDGES:
        src = marker.split("source: ", 1)[1].split("\n", 1)[0]
        if marker in new:
            notes.append(f"edge {src} -> {TICKER} already present (skip)")
        else:
            new += block
            notes.append(f"appended new edge {src} -> {TICKER}")
    # c. safety: confirm the result still parses as YAML
    try:
        _yaml().load(new)
    except Exception as e:  # pragma: no cover
        notes.append(f"!! WARNING: generated YAML failed to parse: {e}")
    return new, notes


def rename_notes(apply):
    if NOTES_DST.exists():
        return [f"{NOTES_DST} already exists (skip rename)"]
    if not NOTES_SRC.exists():
        return [f"{NOTES_SRC} does not exist (nothing to rename)"]
    if apply:
        r = subprocess.run(["git", "-C", str(RW), "mv", "notes/spacex.pvt", "notes/SPCX"],
                           capture_output=True, text=True)
        if r.returncode != 0:  # not tracked yet -> plain mv
            NOTES_SRC.rename(NOTES_DST)
            return [f"mv {NOTES_SRC} -> {NOTES_DST} (plain; was untracked)"]
        return [f"git mv {NOTES_SRC} -> {NOTES_DST}"]
    return [f"WOULD rename {NOTES_SRC} -> {NOTES_DST}"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True,
                   help="print diffs, write nothing (default)")
    g.add_argument("--apply", action="store_true", help="perform the changes")
    args = ap.parse_args()
    apply = args.apply

    print(f"=== migrate {PVT_ID} -> {TICKER}  ({'APPLY' if apply else 'DRY-RUN'})  {TODAY} ===\n")

    jobs = [
        (WL, transform_watchlist),
        (TI, transform_ticker_identity),
        (SCM, transform_supply_chain),
    ]
    for path, fn in jobs:
        if not path.exists():
            print(f"!! {path} missing — skipped\n")
            continue
        old = path.read_text()
        new, notes = fn(old)
        print(f"--- {path}")
        for n in notes:
            print(f"    • {n}")
        print(_diff(path, old, new))
        if apply and new != old:
            path.write_text(new)
            print(f"    ✓ wrote {path}\n")

    print("--- notes/ rename")
    for n in rename_notes(apply):
        print(f"    • {n}")

    print("\n" + ("APPLIED. Now run: python3 scripts/check.py, then commit + push."
                  if apply else
                  "DRY-RUN complete. Re-run with --apply after operator approval."))


if __name__ == "__main__":
    main()
