#!/usr/bin/env python3
"""
Store B ingest (file-backed). Reads raw FactSet JSON (pulled by a FactSet-MCP
agent into state/chunk_store/factset_raw/ — the production puller; manual tonight),
transforms via store_b.build_metrics, writes metrics.jsonl + credibility.json,
and (--demo) shows the Store-A <-> Store-B join on a real guidance chunk.

    python3 scripts/chunking/ingest_metrics.py            # build + report
    python3 scripts/chunking/ingest_metrics.py --demo     # + A<->B join demo
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from store_b import STORE_DIR, MetricsStore, build_metrics, credibility_score  # noqa: E402

RAW = STORE_DIR / "factset_raw"
TICKERS = ["NVDA", "GOOGL"]
METRIC = "SALES"


def _raw(ticker: str, kind: str) -> list[dict]:
    p = RAW / f"{ticker}_{kind}.json"
    return json.loads(p.read_text()).get("data", []) if p.exists() else []


def build() -> tuple[list[dict], dict]:
    as_of = date.today().isoformat()
    all_records, cred = [], {}
    for tk in TICKERS:
        recs = build_metrics(tk, _raw(tk, "guidance"), _raw(tk, "surprise"),
                             metric=METRIC, as_of=as_of)
        all_records.extend(recs)
        cred[f"{tk}:{METRIC}"] = credibility_score(recs)
    return all_records, cred


def _fmt(x, p="{:.1f}"):
    return "—" if x is None else p.format(x)


def report(records, cred, store):
    print(f"\n=== Store B written: {store.dir / 'metrics.jsonl'} ===")
    print(f"records: {len(records)}  |  tickers: {sorted({r['ticker'] for r in records})}")

    print("\n--- sample NVDA metrics rows (judged periods, newest 5) ---")
    nv = [r for r in records if r["ticker"] == "NVDA" and r.get("beat_vs_guidance")]
    for r in sorted(nv, key=lambda r: r["fiscal_end"], reverse=True)[:5]:
        print(f"  {r['period']:>5}  guide[{_fmt(r['guidance_low'])}/{_fmt(r['guidance_mid'])}/"
              f"{_fmt(r['guidance_high'])}]  actual={_fmt(r['actual'])}  "
              f"vsGuide={r['beat_vs_guidance']:>8} ({_fmt(r['beat_vs_guidance_pct'],'{:+.1%}')})  "
              f"vsCons={_fmt(r['beat_vs_consensus_pct'],'{:+.1%}')}  "
              f"guideVsStreet={_fmt(r['guide_vs_consensus_pct'],'{:+.1%}')}")

    print("\n--- GOOGL state (no-guidance fallback) ---")
    gg = [r for r in records if r["ticker"] == "GOOGL"]
    sample = sorted(gg, key=lambda r: r["fiscal_end"], reverse=True)[:3]
    for r in sample:
        print(f"  {r['period']:>5}  guidance={r['beat_vs_guidance']}  actual={_fmt(r['actual'])}  "
              f"vsCons={_fmt(r['beat_vs_consensus_pct'],'{:+.1%}')}")

    print("\n--- credibility scores ---")
    for key, c in cred.items():
        if c.get("guides_quantitatively"):
            print(f"  {key}: hit_rate={_fmt(c['guide_hit_rate'],'{:.0%}')} "
                  f"(in-band {_fmt(c['guide_hit_rate_inrange'],'{:.0%}')})  "
                  f"avg_beat_vs_guide={_fmt(c['avg_beat_vs_guidance'],'{:+.1%}')}  "
                  f"sandbag_index={_fmt(c['sandbag_index'],'{:+.3f}')}  "
                  f"consistency={_fmt(c['consistency'],'{:.2f}')}  "
                  f"n={c['n_guided_periods']} {c['date_range']}")
        else:
            print(f"  {key}: NO QUANTITATIVE GUIDANCE -> fallback: "
                  f"consensus_beat_rate={_fmt(c['consensus_beat_rate'],'{:.0%}')} "
                  f"avg_beat_vs_consensus={_fmt(c['avg_beat_vs_consensus'],'{:+.1%}')} "
                  f"n={c['n_consensus_periods']}")


def demo_join(store):
    """A<->B JOIN: find a real Store-A guidance/forward chunk and attach Store B."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from store import FileStore
    a = FileStore()
    cand = [r for r in a.records.values()
            if r.get("ticker") == "NVDA" and r.get("kind") == "child"
            and "guidance" in (r.get("facets") or [])
            and r.get("time_orientation") == "forward"]
    if not cand:  # relax if the exact facet∧forward combo isn't present
        cand = [r for r in a.records.values()
                if r.get("ticker") == "NVDA" and r.get("kind") == "child"
                and "guidance" in (r.get("facets") or [])]
    print("\n=== A<->B JOIN demo (guidance_with_track_record) ===")
    if not cand:
        print("  no NVDA guidance chunk in Store A; skipping")
        return
    joined = store.join_guidance_chunk(cand[0], n=4)
    c = joined["credibility"]
    print(f"  chunk_id: {joined['chunk_id']}  ({joined['fiscal_quarter']})")
    print(f"  narrative: {(joined['narrative'] or '')[:200].strip()}…")
    print(f"  -> management credibility (SALES guidance): hit_rate="
          f"{c['guide_hit_rate']:.0%}, avg_beat_vs_guide={c['avg_beat_vs_guidance']:+.1%}, "
          f"sandbag_index={c['sandbag_index']:+.3f}  (n={c['n_guided_periods']})")
    print("  -> last 4 quarters (actual vs their own guide):")
    for r in joined["track_record"]:
        print(f"       {r['period']}: actual {r['actual']:.0f} vs guide-mid "
              f"{r['guidance_mid']:.0f}  = {r['beat_vs_guidance']} ({r['beat_vs_guidance_pct']:+.1%})")


def main():
    records, cred = build()
    store = MetricsStore()
    store.write(records, cred)
    report(records, cred, store)
    if "--demo" in sys.argv:
        demo_join(store)


if __name__ == "__main__":
    main()
