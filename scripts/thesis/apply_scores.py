#!/usr/bin/env python3
"""Operator-invoked: print/apply the exact watchlist.yaml diff for accepted score proposals.

    python3 scripts/thesis/apply_scores.py --list
    python3 scripts/thesis/apply_scores.py --accept COHR,LITE                    # unified diff only
    python3 scripts/thesis/apply_scores.py --accept COHR --key ai_positioning --write

config/watchlist.yaml is never machine-written on a schedule. This script runs only when the
operator runs it: it edits the score lines in place (text patch — comments and formatting survive),
re-parses the result as YAML before writing, writes atomically through the symlink to the real
file, then mirrors the new scores into notes/{T}/_thesis.md and clears the accepted proposals.
"""
from __future__ import annotations
import argparse, difflib, os, re, sys, tempfile
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from thesis import thesis_io as tio   # noqa: E402

WATCHLIST = REPO / "config" / "watchlist.yaml"
_KEY_PATH = {"ai_positioning": ("ai_positioning", "score"),
             "competitive_advantage.innovation_rate": ("competitive_advantage", "innovation_rate"),
             "competitive_advantage.distribution": ("competitive_advantage", "distribution"),
             "competitive_advantage.overall": ("competitive_advantage", "overall"),
             "potential_investor_interest.score": ("potential_investor_interest", "score")}
_VAL = r'(["\']?)([1-5][+-]?)(["\']?)'


class PatchError(ValueError):
    pass


def proposals(tickers=None) -> list[dict]:
    out = []
    for p in sorted((REPO / "notes").glob("*/_thesis.md")):
        t = p.parent.name
        if tickers and t not in tickers:
            continue
        fm = tio.load(t) or {}
        for k, v in (fm.get("proposed_scores") or {}).items():
            out.append({"ticker": t, "key": k, "value": str(v.get("value")), "applied": (fm.get("scores") or {}).get(k),
                        "since": v.get("since"), "source": v.get("source")})
    return out


def _indent(l: str) -> int:
    return len(l) - len(l.lstrip())


def _block_span(lines: list[str], ticker: str) -> tuple[int, int]:
    """First '- ticker: T' entry (T1 precedes T2 precedes T3 in the file — the same block watchlist_scores reads)."""
    start = next((i for i, l in enumerate(lines) if re.match(rf"^\s*-\s*ticker:\s*{re.escape(ticker)}\s*$", l)), None)
    if start is None:
        raise PatchError(f"{ticker}: no '- ticker: {ticker}' line in watchlist")
    ind = _indent(lines[start])
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip() and _indent(lines[j]) <= ind and not lines[j].lstrip().startswith("#"):
            end = j
            break
    return start, end


def patch_text(text: str, ticker: str, key: str, value: str) -> str:
    """Replace one score inside the ticker's block. Handles both schema variants:
    nested (`ai_positioning:` / `  score: "4"`) and inline (`ai_positioning: "4"`)."""
    if key not in _KEY_PATH:
        raise PatchError(f"unknown score key {key}")
    parent, leaf = _KEY_PATH[key]
    lines = text.split("\n")
    start, end = _block_span(lines, ticker)
    blk = lines[start:end]
    if leaf == "score":                                     # inline form
        for i, l in enumerate(blk):
            m = re.match(rf"^(\s*{parent}:\s*){_VAL}\s*$", l)
            if m:
                blk[i] = f'{m.group(1)}"{value}"'
                return "\n".join(lines[:start] + blk + lines[end:])
    pi = next((i for i, l in enumerate(blk) if re.match(rf"^\s*{parent}:\s*$", l)), None)
    if pi is None:
        raise PatchError(f"{ticker}: no '{parent}:' block")
    pind = _indent(blk[pi])
    for i in range(pi + 1, len(blk)):
        l = blk[i]
        if l.strip() and _indent(l) <= pind:
            break
        m = re.match(rf"^(\s*{leaf}:\s*){_VAL}(\s*(?:#.*)?)$", l)
        if m:
            blk[i] = f'{m.group(1)}"{value}"{m.group(5)}'
            return "\n".join(lines[:start] + blk + lines[end:])
    raise PatchError(f"{ticker}: no '{leaf}:' line under '{parent}:'")


def apply(accept: list[str], key: str | None, write: bool) -> int:
    props = [p for p in proposals(set(accept)) if not key or p["key"] == key]
    if not props:
        print("nothing to apply")
        return 0
    target = WATCHLIST.resolve()
    old = target.read_text(encoding="utf-8")
    new = old
    for p in props:
        new = patch_text(new, p["ticker"], p["key"], p["value"])
    yaml.safe_load(new)                                     # must still parse before anything is written
    print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(target), tofile=str(target) + " (proposed)")) or "(no textual change)")
    if not write:
        print(f"\n{len(props)} change(s) NOT written (add --write)")
        return 0
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".watchlist-", suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, target)
    for p in props:
        fm = tio.load(p["ticker"])
        fm.setdefault("scores", {})[p["key"]] = p["value"]
        (fm.get("proposed_scores") or {}).pop(p["key"], None)
        tio.save(p["ticker"], fm)
        live = tio.watchlist_scores(p["ticker"]).get(p["key"])
        print(f"{p['ticker']} {p['key']}: watchlist now {live!r}" + ("" if live == p["value"] else "  <-- MISMATCH, inspect"))
    print(f"wrote {len(props)} change(s) to {target}; proposals cleared in _thesis.md")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true"); ap.add_argument("--accept", help="comma list of tickers")
    ap.add_argument("--key", help="restrict to one score key"); ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.accept:
        return apply(a.accept.split(","), a.key, a.write)
    for p in proposals():
        print(f"{p['ticker']:<8} {p['key']:<42} proposed {p['value']:<3} applied {p['applied']!s:<4} since {p['since']}  ({p['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
