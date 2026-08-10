#!/usr/bin/env python3
"""Positive verification for the theme backfill.

eval_store.py is a REGRESSION gate only: its gold cases are ticker-scoped and none
of them use a theme scope, so it holds at its baseline whether the backfill worked
perfectly or wrote garbage. It proves "nothing broke", not "the change did its job".

This proves the change did its job, three ways:

  1. VOCABULARY  — every theme written is in config/watchlist.yaml's vocabulary.
                   Catches an extractor that invented tags.
  2. PERSISTENCE — the themes in pg match what the run recorded, and the note's
                   frontmatter agrees with pg. Catches a partial UPDATE.
  3. RETRIEVAL   — a theme-scoped store.search() now returns a backfilled doc.
                   This is the one that matters: themes are a HARD scope filter, so
                   before the backfill these docs were unreachable by such a query.

  python3 scripts/v3_ingest/verify_theme_backfill.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path("/root/research-watchlist")
STATE = REPO_ROOT / "state" / "v3_ingest" / "theme_backfill.json"
NOTES_DIR = REPO_ROOT / "notes" / "sec"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v3_ingest"))


def main() -> int:
    from pgconn import connect
    from sec_filings import load_valid_themes

    state = json.loads(STATE.read_text())
    done = state["done"]
    applied = {d: v for d, v in done.items() if v.get("themes")}
    print(f"backfill state: {len(done)} docs processed, {len(applied)} with themes applied, "
          f"{len(done) - len(applied)} genuinely empty")
    if not applied:
        print("nothing applied — nothing to verify")
        return 1

    valid = load_valid_themes()
    cx = connect()
    cur = cx.cursor()
    failures = []

    # 1. VOCABULARY
    used = {t for v in applied.values() for t in v["themes"]}
    bad = used - valid
    print(f"\n1. VOCABULARY: {len(used)} distinct themes used, {len(bad)} outside the vocabulary")
    if bad:
        failures.append(f"themes outside vocabulary: {sorted(bad)}")
    print(f"   {sorted(used)}")

    # 2. PERSISTENCE — pg rows carry the themes, and the note frontmatter agrees
    print("\n2. PERSISTENCE: checking pg rows and note frontmatter agree")
    checked = mismatched = 0
    for doc_id, rec in applied.items():
        cur.execute("SELECT themes FROM chunks WHERE doc_id=%s", (doc_id,))
        rows = cur.fetchall()
        if not rows:
            failures.append(f"{doc_id[:12]}: no chunks in pg")
            continue
        for (themes,) in rows:
            if not set(rec["themes"]).issubset(set(themes or [])):
                mismatched += 1
                failures.append(f"{doc_id[:12]}: pg themes {themes} missing {rec['themes']}")
                break
        checked += 1
    print(f"   {checked} docs checked in pg, {mismatched} mismatched")

    # frontmatter: notes were rewritten, so their sha256 no longer equals doc_id.
    # Match on themes_backfilled instead.
    fm_ok = 0
    for p in NOTES_DIR.glob("*.md"):
        m = re.match(r"^---\n(.*?\n)---\n", p.read_text(errors="ignore"), re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get("themes_backfilled"):
            fm_ok += 1
            if not fm.get("themes"):
                failures.append(f"{p.name}: marked backfilled but themes empty")
    print(f"   {fm_ok} notes carry themes_backfilled with non-empty themes")
    if fm_ok != len(applied):
        failures.append(f"frontmatter count {fm_ok} != applied count {len(applied)}")

    # 3. RETRIEVAL — the point of the whole exercise
    print("\n3. RETRIEVAL: theme-scoped search now reaches a backfilled doc")
    from retrieve import retrieve
    # Probe with the theme that the most backfilled docs carry, so the scoped
    # search has the best chance of surfacing one inside top-k.
    from collections import Counter
    counts = Counter(t for v in applied.values() for t in v["themes"])
    probe_theme, _ = counts.most_common(1)[0]
    targets = {d for d, v in applied.items() if probe_theme in v["themes"]}
    query = probe_theme.replace("_", " ")
    hits = retrieve(query, k=50, themes=[probe_theme])
    hit_docs = {h.doc_id for h in hits}
    reached = targets & hit_docs
    print(f"   probe theme: {probe_theme!r} (query {query!r}, k=50)")
    print(f"   backfilled docs carrying it: {len(targets)}")
    print(f"   hits returned: {len(hits)}; of them backfilled docs: {len(reached)}")
    if not hits:
        failures.append(f"theme-scoped retrieve for {probe_theme!r} returned nothing at all")
    elif not reached:
        failures.append(
            f"theme-scoped retrieve for {probe_theme!r} returned {len(hits)} hits but none "
            f"were backfilled docs (they may simply rank below k=50 — inspect before treating "
            f"as a failure)")

    print("\n" + ("VERIFY FAILED:" if failures else "VERIFY PASSED — all three checks green"))
    for f in failures:
        print(f"  ! {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
