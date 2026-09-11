#!/usr/bin/env python3
"""Verified ticker adjacency for Detector 1 (spec §6.1).

Three operator-vetted sources, nothing extracted: supply-chain-manual.yaml edges (provenance
manual/verified), watchlist `ingest_comparables[].informs`, and `tier_4_ecosystem[].affects`.
The 8,756 FactSet-extracted edges are excluded by operator decision 2026-09-10 — they are
unaudited and name-keyed, and a false adjacency makes stage 2 fire on noise.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path("/root/research-watchlist")
MANUAL = Path("/root/research/config/supply-chain-manual.yaml")   # sibling repo, not symlinked
WATCHLIST = REPO / "config" / "watchlist.yaml"
TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.]*$|^[a-z_]+\.(cn|tw|in|us|kr)$")   # tickers, or tier_4 ids
MANUAL_PROVENANCE = {"manual", "verified"}


def _is_node(s) -> bool:
    return bool(s) and not str(s).endswith(".pvt") and bool(TICKER_RE.match(str(s)))


def _link(g: dict, a: str, b: str, route: str) -> None:
    for x, y in ((a, b), (b, a)):
        routes = g.setdefault(x, {}).setdefault(y, [])
        if route not in routes:
            routes.append(route)


def build_adjacency(manual_edges: list, comparables: list, tier4: list) -> dict:
    """-> {ticker: {neighbor: [route, ...]}} undirected; routes name the source of the edge."""
    g: dict = {}
    for e in manual_edges or []:
        if (e.get("provenance") or "").lower() not in MANUAL_PROVENANCE:
            continue
        s, t = e.get("source"), e.get("target")
        if _is_node(s) and _is_node(t):
            for kind in (e.get("kind") or ["related"]):
                _link(g, s, t, f"manual:{kind}")
    for c in comparables or []:
        t = c.get("ticker")
        for h in (c.get("informs") or []):
            if _is_node(t) and _is_node(h):
                _link(g, t, h, "comparable")
    for e in tier4 or []:
        cid = e.get("id")
        for h in (e.get("affects") or []):
            if _is_node(cid) and _is_node(h):
                _link(g, cid, h, f"tier4:{cid}")
    return g


def load_adjacency(manual_path: Path = MANUAL, watchlist_path: Path = WATCHLIST) -> dict:
    edges = ((yaml.safe_load(manual_path.read_text()) or {}).get("edges") or []) if manual_path.exists() else []
    wl = yaml.safe_load(watchlist_path.read_text()) or {}
    return build_adjacency(edges, wl.get("ingest_comparables") or [], wl.get("tier_4_ecosystem") or [])


if __name__ == "__main__":
    g = load_adjacency()
    print(f"{len(g)} nodes, {sum(len(v) for v in g.values()) // 2} undirected edges")
    for k in sorted(g):
        print(f"  {k}: " + ", ".join(f"{n}[{'|'.join(r)}]" for n, r in sorted(g[k].items())))
