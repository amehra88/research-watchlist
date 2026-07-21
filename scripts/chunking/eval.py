#!/usr/bin/env python3
"""
Eval harness for the note chunker (Store-A prototype).

For each gold case in eval_set.yaml, pick the best-matching chunk by simple
keyword overlap (a stand-in retriever) and check it satisfies the case's
expectations (facets / section / text / time_orientation / claim_source).

This proves the chunks are ADDRESSABLE today. When embeddings land, replace
`retrieve()` with the vector retriever and the SAME gold set measures recall@k.

Usage:
    python3 scripts/chunking/eval.py                       # uses NVDA 1Q27 note
    python3 scripts/chunking/eval.py --note notes/NVDA/20260521-1Q27.md -v
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from chunker import chunk_note, _FACET_CUES  # same dir

_HERE = Path(__file__).resolve().parent
_STOP = set("the a an of to in on for and or is was did how much what by it its "
            "about did vs new this that say said do does are were on with".split())


def _toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9$%]+", s.lower()) if w not in _STOP}


def _query_facets(question: str) -> set[str]:
    """Infer query facets with the same cue map the chunker uses (hybrid retrieval)."""
    low = question.lower()
    return {f for f, pat in _FACET_CUES.items() if re.search(pat, low, re.I)}


def retrieve(question: str, chunks):
    """Stand-in hybrid retriever: token overlap + facet match, tie-break to the
    DENSER (shorter) chunk for precision. Mirrors docs §7 'hybrid by default';
    swap for the vector retriever when embeddings land."""
    qt, qf = _toks(question), _query_facets(question)
    best, score = None, (-1, 0)
    for c in chunks:
        if c.kind != "child":
            continue
        ov = len(qt & _toks(c.text))
        ff = len(qf & {x.split(".")[0] for x in c.facets})
        s = (ov + 2 * ff, -len(c.text))  # facet-weighted; ties -> shorter chunk
        if s > score:
            best, score = c, s
    return best


def check(case: dict, hit) -> list[str]:
    fails = []
    if hit is None:
        return ["no chunk retrieved"]
    if "expect_contains" in case and case["expect_contains"].lower() not in hit.text.lower():
        fails.append(f"missing text {case['expect_contains']!r}")
    if "expect_section" in case and case["expect_section"].lower() not in (hit.section or "").lower():
        fails.append(f"section {hit.section!r} != ~{case['expect_section']!r}")
    if "expect_doc_type" in case and getattr(hit, "doc_type", None) != case["expect_doc_type"]:
        fails.append(f"doc_type {getattr(hit, 'doc_type', None)!r} != {case['expect_doc_type']!r}")
    for f in case.get("expect_facets", []):
        if not any(x == f or x.startswith(f + ".") for x in hit.facets):
            fails.append(f"facet {f!r} not in {hit.facets}")
    if "expect_time" in case and hit.time_orientation != case["expect_time"]:
        fails.append(f"time {hit.time_orientation!r} != {case['expect_time']!r}")
    if "expect_claim" in case and hit.claim_source != case["expect_claim"]:
        fails.append(f"claim {hit.claim_source!r} != {case['expect_claim']!r}")
    if "expect_answered_by" in case and hit.answered_by != case["expect_answered_by"]:
        fails.append(f"answered_by {hit.answered_by!r} != {case['expect_answered_by']!r}")
    if "expect_directness" in case and hit.answer_directness != case["expect_directness"]:
        fails.append(f"directness {hit.answer_directness!r} != {case['expect_directness']!r}")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", type=Path,
                    default=_HERE.parents[1] / "notes/NVDA/20260521-1Q27.md")
    ap.add_argument("--eval-set", type=Path, default=_HERE / "eval_set.yaml",
                    help="gold cases for --note (default: NVDA eval_set.yaml)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    cases = yaml.safe_load(args.eval_set.read_text())["cases"]
    chunks = chunk_note(args.note)

    passed = 0
    for i, case in enumerate(cases, 1):
        hit = retrieve(case["q"], chunks)
        fails = check(case, hit)
        ok = not fails
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {i:2d}. {case['q']}")
        if hit and (args.verbose or not ok):
            print(f"        -> {hit.chunk_id}  facets={hit.facets} "
                  f"[{hit.claim_source}/{hit.time_orientation}]")
        for f in fails:
            print(f"        ! {f}")
    print(f"\n{passed}/{len(cases)} cases pass "
          f"(keyword-overlap stand-in retriever; replace with vector retriever)")


if __name__ == "__main__":
    main()
