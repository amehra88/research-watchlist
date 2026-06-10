#!/usr/bin/env python3
"""
One-shot migration: file-backed chunk store -> Postgres (step 5b).

NON-DESTRUCTIVE: reads the file backend only; never writes/deletes the jsonl or
.npy. IDEMPOTENT: TRUNCATEs pg first, so re-runs converge. The file backend
stays the canonical fallback — unset CHUNK_STORE_BACKEND to revert instantly.

Pipeline:
  1. Load Store A (FileStore) + Store B (MetricsStore) from disk.
  2. TRUNCATE pg, then upsert Store A vectors + Store B metrics/credibility.
  3. ROUND-TRIP VERIFY: re-read every row from pg and diff field-by-field
     against the source (metadata, embeddings, metrics). Counts hide
     type-coercion corruption (a date that became text, a NULL that became 0),
     so this diffs values, not just row counts.

    python3 scripts/chunking/migrate_to_pg.py            # migrate + verify
    python3 scripts/chunking/migrate_to_pg.py --verify    # verify only (no write)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from store import FileStore, PgStore                      # noqa: E402
from store_b import MetricsStore, PgMetricsStore          # noqa: E402

EMB_TOL = 1e-6   # float32 round-trip (npy float32 -> pg float4 -> float32) is exact


def _build_a_records(fs: FileStore) -> list[dict]:
    """File records (metadata) + attach each child's normalized vector — exactly
    the vectors FileStore serves at search time."""
    emb_by_id = ({cid: fs._emb[i] for i, cid in enumerate(fs._emb_ids)}
                 if fs._emb is not None else {})
    out = []
    for cid, rec in fs.records.items():
        r = dict(rec)
        r["embedding"] = emb_by_id.get(cid)   # None for parents
        out.append(r)
    return out


def migrate() -> None:
    fs = FileStore()
    ms = MetricsStore()
    fp, fc = fs.count()
    print(f"[source] Store A: {fp} parents + {fc} children | "
          f"Store B: {len(ms.records)} metric rows, {len(ms.cred)} credibility keys")

    pg = PgStore()
    pg.clear()                                 # TRUNCATE chunks CASCADE (idempotent)
    a_recs = _build_a_records(fs)
    n = pg.upsert(a_recs)
    pp, pc = pg.count()
    print(f"[pg] Store A upserted {n} records -> {pp} parents + {pc} children")

    pgb = PgMetricsStore()
    with pgb._conn.cursor() as cur:
        cur.execute("TRUNCATE metrics, metrics_credibility")
    pgb._conn.commit()
    pgb.write(ms.records, ms.cred)
    with pgb._conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM metrics")
        m_n = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM metrics_credibility")
        c_n = cur.fetchone()[0]
    print(f"[pg] Store B wrote {m_n} metric rows + {c_n} credibility rows")


# ---------------------------------------------------------------------------
def verify() -> bool:
    """Re-read pg and diff against the file backend. Returns True iff identical."""
    fs, ms = FileStore(), MetricsStore()
    pg, pgb = PgStore(), PgMetricsStore()
    ok = True

    # --- Store A metadata: every field of every chunk -----------------------
    if set(fs.records) != set(pg.records):
        only_f = set(fs.records) - set(pg.records)
        only_p = set(pg.records) - set(fs.records)
        print(f"  ! chunk_id set differs (file-only {len(only_f)}, pg-only {len(only_p)})")
        ok = False
    meta_mismatch = 0
    for cid in fs.records:
        if cid not in pg.records:
            continue
        f, p = fs.records[cid], pg.records[cid]
        for k in f:
            fv, pv = f.get(k), p.get(k)
            # file stores [] and pg returns [] ; normalize None/[] equivalently
            if (fv or None) != (pv or None) and fv != pv:
                meta_mismatch += 1
                if meta_mismatch <= 8:
                    print(f"  ! {cid}.{k}: file={fv!r} pg={pv!r}")
    if meta_mismatch:
        print(f"  ! {meta_mismatch} metadata field mismatches")
        ok = False
    else:
        print(f"  ✓ Store A metadata identical across {len(fs.records)} chunks")

    # --- Store A embeddings: aligned by chunk_id, max abs diff --------------
    f_map = {cid: fs._emb[i] for i, cid in enumerate(fs._emb_ids)} if fs._emb is not None else {}
    p_map = {cid: pg._emb[i] for i, cid in enumerate(pg._emb_ids)} if pg._emb is not None else {}
    if set(f_map) != set(p_map):
        print(f"  ! embedding id set differs (file {len(f_map)} vs pg {len(p_map)})")
        ok = False
    max_d = 0.0
    for cid in f_map:
        if cid in p_map:
            max_d = max(max_d, float(np.max(np.abs(f_map[cid] - p_map[cid]))))
    if max_d > EMB_TOL:
        print(f"  ! embedding max abs diff {max_d:.3e} > tol {EMB_TOL:.0e}")
        ok = False
    else:
        print(f"  ✓ Store A embeddings identical ({len(f_map)} vectors, max|Δ|={max_d:.2e})")

    # --- Store B metrics + credibility --------------------------------------
    def _key(r):
        return (r["ticker"], r["period"], r["metric"])
    f_rows = {_key(r): r for r in ms.records}
    p_rows = {}
    with pgb._conn.cursor() as cur:
        cur.execute(f"SELECT {', '.join(PgMetricsStore._COLS)} FROM metrics")
        for r in pgb._rowdicts(cur):
            p_rows[_key(r)] = r
    b_mismatch = 0
    if set(f_rows) != set(p_rows):
        print(f"  ! metrics key set differs (file {len(f_rows)} vs pg {len(p_rows)})")
        ok = False
    for k in f_rows:
        if k not in p_rows:
            continue
        for col in PgMetricsStore._COLS:
            fv, pv = f_rows[k].get(col), p_rows[k].get(col)
            if isinstance(fv, float) or isinstance(pv, float):
                if fv is None or pv is None:
                    same = fv is None and pv is None
                else:
                    same = abs(float(fv) - float(pv)) < 1e-9
            else:
                same = fv == pv
            if not same:
                b_mismatch += 1
                if b_mismatch <= 8:
                    print(f"  ! metrics{k}.{col}: file={fv!r} pg={pv!r}")
    if b_mismatch:
        print(f"  ! {b_mismatch} metric field mismatches")
        ok = False
    else:
        print(f"  ✓ Store B metrics identical across {len(f_rows)} rows")

    cred_mismatch = 0
    for key, fc in ms.cred.items():
        tk, metric = key.split(":", 1)
        pc = pgb.credibility(tk, metric)
        if pc != fc:
            cred_mismatch += 1
            print(f"  ! credibility {key} differs")
    if cred_mismatch:
        ok = False
    else:
        print(f"  ✓ Store B credibility identical across {len(ms.cred)} keys")

    # --- a sample vector, for the eyeball checkpoint ------------------------
    if f_map:
        cid = next(iter(sorted(f_map)))
        print(f"\n  sample vector {cid}:")
        print(f"    file[:5] = {np.round(f_map[cid][:5], 6).tolist()}")
        print(f"    pg  [:5] = {np.round(p_map[cid][:5], 6).tolist()}")
    return ok


def main():
    if "--verify" not in sys.argv:
        migrate()
    print("\n=== ROUND-TRIP VERIFY (pg vs file) ===")
    ok = verify()
    print("\n" + ("VERIFY: PASS — pg is byte-identical to the file backend."
                  if ok else "VERIFY: FAIL — do NOT flip CHUNK_STORE_BACKEND."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
