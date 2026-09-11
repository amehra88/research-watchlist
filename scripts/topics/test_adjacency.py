#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjacency as adj


def test_manual_edges_are_undirected_and_keep_kind():
    edges = [{"source": "NVDA", "target": "CBRS", "kind": ["competitor"], "provenance": "manual"},
             {"source": "CBRS", "target": "openai.pvt", "kind": ["customer"], "provenance": "manual"},
             {"source": "DDOG", "target": "Grafana", "kind": ["competitor"], "provenance": "manual"},
             {"source": "AMD", "target": "Intel Corporation", "kind": ["competitor"], "provenance": "extracted"}]
    g = adj.build_adjacency(edges, [], [])
    assert g["NVDA"]["CBRS"] == ["manual:competitor"]
    assert g["CBRS"]["NVDA"] == ["manual:competitor"]
    assert "openai.pvt" not in g.get("CBRS", {})          # privates never enter
    assert "Grafana" not in g.get("DDOG", {})              # bare names are not tickers
    assert "AMD" not in g                                  # extracted provenance is excluded by decision


def test_comparables_and_tier4_routes():
    comps = [{"ticker": "AAOI", "informs": ["COHR", "LITE"]}]
    t4 = [{"id": "innolight.cn", "affects": ["COHR", "LITE"]}]
    g = adj.build_adjacency([], comps, t4)
    assert g["AAOI"]["COHR"] == ["comparable"] and g["COHR"]["AAOI"] == ["comparable"]
    assert g["innolight.cn"]["COHR"] == ["tier4:innolight.cn"]
    assert g["COHR"]["innolight.cn"] == ["tier4:innolight.cn"]


def test_routes_accumulate_without_duplicates():
    edges = [{"source": "AAOI", "target": "COHR", "kind": ["competitor"], "provenance": "verified"}]
    comps = [{"ticker": "AAOI", "informs": ["COHR"]}]
    g = adj.build_adjacency(edges, comps, [])
    assert g["AAOI"]["COHR"] == ["manual:competitor", "comparable"]
    g2 = adj.build_adjacency(edges + edges, comps, [])
    assert g2["AAOI"]["COHR"] == ["manual:competitor", "comparable"]


def test_load_adjacency_reads_the_real_files():
    g = adj.load_adjacency()
    assert "COHR" in g["AAOI"], "AAOI informs COHR via ingest_comparables (spec §11.3 depends on this)"
    assert all(not n.endswith(".pvt") for d in g.values() for n in d)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1; print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass"); sys.exit(1 if failed else 0)
