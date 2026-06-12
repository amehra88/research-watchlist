#!/usr/bin/env python3
"""
Store B — structured metrics (the numbers). File-backed today; the managed-
pgvector port (PgStore + the schema.sql `metrics` table & guidance_with_track_record
VIEW) is the step-5b swap. Mirrors schema.sql `metrics` column-for-column.

Fed by two FactSet endpoints (raw JSON pulled by a FactSet-MCP agent into
state/chunk_store/factset_raw/, transformed here — see ingest_metrics.py):
  - estimate_type='guidance' -> guided range + consensus-at-guide (meanBefore)
  - estimate_type='surprise' -> actual (surpriseAfter) + consensus-at-print

THREE relationships per period (design §2, verified against live FactSet 2026-06-09):
  1. actual vs consensus    (street beat/miss)        <- surprise
  2. actual vs own guidance (the §2a credibility tell) <- guidance JOIN surprise on fiscalEndDate
  3. guidance vs consensus  (sandbag-at-guide tell)    <- guidance.meanSurpriseAmtPercent

UNIT NOTE (real FactSet quirk): guidance `meanSurpriseAmtPercent` is a DECIMAL
(0.53 = +53%) but surprise `surprisePercent` is a PERCENT NUMBER (20.7 = +20.7%).
Both are normalized to decimals here.
"""
from __future__ import annotations

import json
import statistics
from decimal import Decimal as _Decimal
from pathlib import Path
from typing import Optional

STORE_DIR = Path("/root/research-watchlist/state/chunk_store")
_METRICS_FILE = "metrics.jsonl"
_CRED_FILE = "credibility.json"

# FactSet CONVENTION QUIRK (not a bug): for off-calendar fiscal years FactSet's
# `fiscalYear` can trail the company's own FY label by a year. NVDA's quarter
# ending 2026-04-30 is FactSet fiscalYear=2026/period=1, but NVDA — and our gold
# notes — call it "1Q27" (NVDA's FY27 ends Jan-2027). So we add +1 to FactSet's
# fiscalYear for NVDA to match the note convention. Calendar-FY names (GOOGL)
# align already → offset 0. Add an entry per off-cycle ticker as Store B grows.
_FY_LABEL_OFFSET = {"NVDA": 1}


def fiscal_label(ticker: str, fiscal_year: int, fiscal_period: int) -> str:
    yr = int(fiscal_year) + _FY_LABEL_OFFSET.get(ticker, 0)
    return f"{int(fiscal_period)}Q{yr % 100:02d}"


# ---------------------------------------------------------------------------
# Transform: raw FactSet rows -> metrics records (schema.sql `metrics` shape)
# ---------------------------------------------------------------------------
def _dedupe_by_period(rows: list[dict]) -> dict:
    """Collapse monthly-sampled rows to one per fiscal period. Values are
    constant across a period's monthly samples; only the sample date varies.
    Rows with a null fiscalEndDate (e.g. GOOGL's empty-guidance sentinel) drop."""
    out: dict[str, dict] = {}
    for r in rows:
        fe = r.get("fiscalEndDate")
        if fe:
            out[fe] = r
    return out


def build_metrics(ticker: str, guidance_rows: list[dict], surprise_rows: list[dict],
                  *, metric: str = "SALES", as_of: Optional[str] = None) -> list[dict]:
    g = _dedupe_by_period(guidance_rows)
    s = _dedupe_by_period(surprise_rows)
    records = []
    for fe in sorted(set(g) | set(s)):
        gr, sr = g.get(fe), s.get(fe)
        base = gr or sr
        rec = {
            "ticker": ticker,
            "period": fiscal_label(ticker, base["fiscalYear"], base["fiscalPeriod"]),
            "fiscal_end": fe,
            "metric": metric,
            # guidance side -------------------------------------------------
            "guidance_date": gr.get("guidanceDate") if gr else None,
            "guidance_low": gr.get("guidanceLow") if gr else None,
            "guidance_mid": gr.get("guidanceMidpoint") if gr else None,
            "guidance_high": gr.get("guidanceHigh") if gr else None,
            "consensus_at_guide": gr.get("meanBefore") if gr else None,
            # already a decimal fraction in FactSet
            "guide_vs_consensus_pct": gr.get("meanSurpriseAmtPercent") if gr else None,
            # actual side ---------------------------------------------------
            "actual": sr.get("surpriseAfter") if sr else None,
            "consensus_at_print": sr.get("surpriseBefore") if sr else None,
            # FactSet surprisePercent is a percent NUMBER -> normalize to decimal
            "beat_vs_consensus_pct": (sr["surprisePercent"] / 100.0)
            if sr and sr.get("surprisePercent") is not None else None,
            "surprise_date": sr.get("surpriseDate") if sr else None,
            "source": "factset",
            "as_of": as_of,
        }
        # derived: actual vs their OWN guidance (the credibility signal) ----
        if rec["actual"] is not None and rec["guidance_mid"] is not None:
            a, lo, mid, hi = (rec["actual"], rec["guidance_low"],
                              rec["guidance_mid"], rec["guidance_high"])
            rec["beat_vs_guidance"] = ("above" if a > hi else
                                       "below" if a < lo else "in_range")
            rec["beat_vs_guidance_pct"] = (a - mid) / mid if mid else None
        else:
            rec["beat_vs_guidance"] = None
            rec["beat_vs_guidance_pct"] = None
        records.append(rec)
    return records


# ---------------------------------------------------------------------------
# §2a guidance-credibility score (per ticker, aggregated from the rows above)
# ---------------------------------------------------------------------------
def credibility_score(records: list[dict]) -> dict:
    """Derive the management guidance-credibility signal. Falls back to a
    consensus-beat-only profile for non-guiders (e.g. GOOGL)."""
    if not records:
        return {}
    ticker, metric = records[0]["ticker"], records[0]["metric"]
    judged = [r for r in records if r.get("beat_vs_guidance") is not None]
    cons = [r["beat_vs_consensus_pct"] for r in records
            if r.get("beat_vs_consensus_pct") is not None]

    out = {
        "ticker": ticker,
        "metric": metric,
        "guides_quantitatively": bool(judged),
        # consensus-beat track record exists for guiders AND non-guiders
        "n_consensus_periods": len(cons),
        "avg_beat_vs_consensus": (statistics.mean(cons) if cons else None),
        "consensus_beat_rate": (sum(1 for x in cons if x > 0) / len(cons) if cons else None),
    }
    if not judged:
        out.update({
            "n_guided_periods": 0,
            "guide_hit_rate": None, "guide_hit_rate_inrange": None,
            "avg_beat_vs_guidance": None, "sandbag_index": None,
            "consistency": None, "date_range": None,
            "note": "no quantitative guidance issued; consensus-beat fallback only",
        })
        return out

    beats = [r["beat_vs_guidance_pct"] for r in judged]
    # hit = actual at/above guide midpoint; in-range = within the guided band
    hit_mid = sum(1 for r in judged if r["actual"] >= r["guidance_mid"]) / len(judged)
    hit_band = sum(1 for r in judged if r["beat_vs_guidance"] in ("above", "in_range")) / len(judged)
    # sandbag_index (asymmetric): credit lowballing the street (-gvc), and only
    # PENALIZE — never reward — missing your own guide (min(bvg,0)). Positive =
    # sandbagger (guide low, then beat); negative = overpromiser (guide high, miss).
    sb = []
    for r in judged:
        gvc, bvg = r.get("guide_vs_consensus_pct"), r.get("beat_vs_guidance_pct")
        if gvc is None or bvg is None:
            continue
        sb.append(-gvc + min(bvg, 0.0))
    out.update({
        "n_guided_periods": len(judged),
        "guide_hit_rate": hit_mid,
        "guide_hit_rate_inrange": hit_band,
        "avg_beat_vs_guidance": statistics.mean(beats),
        "sandbag_index": (statistics.mean(sb) if sb else None),
        "consistency": 1.0 - (statistics.pstdev(beats) if len(beats) > 1 else 0.0),
        "date_range": [judged[0]["fiscal_end"], judged[-1]["fiscal_end"]],
    })
    return out


# ---------------------------------------------------------------------------
# File-backed Store B + the A<->B join
# ---------------------------------------------------------------------------
class MetricsStore:
    """File-backed Store B. metrics.jsonl mirrors schema.sql `metrics`;
    credibility.json caches the per-(ticker,metric) §2a score."""

    def __init__(self, store_dir: Path = STORE_DIR):
        self.dir = Path(store_dir)
        self.records: list[dict] = []
        self.cred: dict[str, dict] = {}   # "TICKER:METRIC" -> score
        self._load()

    def _load(self) -> None:
        mf = self.dir / _METRICS_FILE
        if mf.exists():
            self.records = [json.loads(l) for l in mf.read_text().splitlines() if l.strip()]
        cf = self.dir / _CRED_FILE
        if cf.exists():
            self.cred = json.loads(cf.read_text())

    def write(self, records: list[dict], cred: dict[str, dict]) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with (self.dir / _METRICS_FILE).open("w") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
        (self.dir / _CRED_FILE).write_text(json.dumps(cred, indent=2))
        self.records, self.cred = records, cred

    def credibility(self, ticker: str, metric: str = "SALES") -> Optional[dict]:
        return self.cred.get(f"{ticker}:{metric}")

    def track_record(self, ticker: str, metric: str = "SALES", n: int = 4) -> list[dict]:
        """Most-recent n JUDGED periods (have actual vs own guide), newest first."""
        rows = [r for r in self.records
                if r["ticker"] == ticker and r["metric"] == metric
                and r.get("beat_vs_guidance") is not None]
        rows.sort(key=lambda r: r["fiscal_end"], reverse=True)
        return rows[:n]

    def join_guidance_chunk(self, chunk: dict, n: int = 4) -> Optional[dict]:
        """The A<->B JOIN (reproduces schema.sql guidance_with_track_record).
        Given a Store-A `guidance`/forward chunk, attach its management's
        quantitative track record + credibility score, keyed on ticker."""
        # §v3: chunk carries `tickers` (array). base_ticker is the canonical
        # path-derived owner; fall back to tickers[0] for source-dir notes with
        # no path ticker. Skip the join when neither is present.
        ticker = chunk.get("base_ticker") or (chunk.get("tickers") or [None])[0]
        if ticker is None:
            return None
        return {
            "chunk_id": chunk.get("chunk_id"),
            "ticker": ticker,
            "fiscal_quarter": chunk.get("fiscal_quarter"),
            "narrative": chunk.get("text"),
            "credibility": self.credibility(ticker),
            "track_record": self.track_record(ticker, n=n),
        }


# ---------------------------------------------------------------------------
# Pg-backed Store B + the pg-native A<->B join (step 5b managed-pgvector swap)
# ---------------------------------------------------------------------------
class PgMetricsStore:
    """Postgres-backed Store B. Same interface as MetricsStore, but metrics live
    in schema.sql `metrics`, the credibility cache in `metrics_credibility`
    (JSONB), and the A<->B JOIN is pg-native (track_record + credibility are SQL
    reads keyed on ticker — no Python recompute). This is pg's raison d'être per
    schema.sql: a retrieved guidance chunk JOINs to its management's quant
    track record in the same database."""

    _COLS = ["ticker", "period", "metric", "fiscal_end", "guidance_date",
             "guidance_low", "guidance_mid", "guidance_high", "consensus_at_guide",
             "guide_vs_consensus_pct", "actual", "consensus_at_print",
             "beat_vs_consensus_pct", "surprise_date", "beat_vs_guidance",
             "beat_vs_guidance_pct", "source", "as_of"]
    _DATE_COLS = ("fiscal_end", "guidance_date", "surprise_date", "as_of")

    def __init__(self):
        import pgconn
        self._conn = pgconn.connect()

    def write(self, records: list[dict], cred: dict[str, dict]) -> None:
        from psycopg2.extras import execute_values, Json
        rows = [[(r.get(c) or None) if c in self._DATE_COLS else r.get(c)
                 for c in self._COLS] for r in records]
        keys = ("ticker", "period", "metric")
        set_clause = ", ".join(f"{c}=EXCLUDED.{c}" for c in self._COLS if c not in keys)
        cred_rows = [[k.split(":", 1)[0], k.split(":", 1)[1], Json(v)]
                     for k, v in cred.items()]
        with self._conn.cursor() as cur:
            execute_values(
                cur,
                f"INSERT INTO metrics ({', '.join(self._COLS)}) VALUES %s "
                f"ON CONFLICT (ticker, period, metric) DO UPDATE SET {set_clause}",
                rows)
            if cred_rows:
                execute_values(
                    cur,
                    "INSERT INTO metrics_credibility (ticker, metric, score) VALUES %s "
                    "ON CONFLICT (ticker, metric) DO UPDATE SET score = EXCLUDED.score",
                    cred_rows)
        self._conn.commit()

    def credibility(self, ticker: str, metric: str = "SALES") -> Optional[dict]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT score FROM metrics_credibility "
                        "WHERE ticker = %s AND metric = %s", (ticker, metric))
            row = cur.fetchone()
        return row[0] if row else None  # JSONB -> dict

    def _rowdicts(self, cur) -> list[dict]:
        cols = [d[0] for d in cur.description]
        out = []
        for row in cur.fetchall():
            rec = dict(zip(cols, row))
            for c in self._DATE_COLS:                      # DATE -> str (file parity)
                if rec.get(c) is not None:
                    rec[c] = rec[c].isoformat()
            for c in rec:                                  # NUMERIC -> float (Decimal parity)
                if isinstance(rec[c], _Decimal):
                    rec[c] = float(rec[c])
            out.append(rec)
        return out

    def track_record(self, ticker: str, metric: str = "SALES", n: int = 4) -> list[dict]:
        """Most-recent n JUDGED periods (actual vs own guide), newest first."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"SELECT {', '.join(self._COLS)} FROM metrics "
                "WHERE ticker = %s AND metric = %s AND beat_vs_guidance IS NOT NULL "
                "ORDER BY fiscal_end DESC LIMIT %s", (ticker, metric, n))
            return self._rowdicts(cur)

    def join_guidance_chunk(self, chunk: dict, n: int = 4) -> Optional[dict]:
        """Pg-native A<->B JOIN — same shape as MetricsStore.join_guidance_chunk."""
        # §v3: base_ticker (canonical, path-derived) or tickers[0]; skip if neither.
        ticker = chunk.get("base_ticker") or (chunk.get("tickers") or [None])[0]
        if ticker is None:
            return None
        return {
            "chunk_id": chunk.get("chunk_id"),
            "ticker": ticker,
            "fiscal_quarter": chunk.get("fiscal_quarter"),
            "narrative": chunk.get("text"),
            "credibility": self.credibility(ticker),
            "track_record": self.track_record(ticker, n=n),
        }


def get_metrics_store():
    """Backend dispatch, parallel to store.get_store(): file (default) | pg."""
    import os
    backend = os.environ.get("CHUNK_STORE_BACKEND", "file").lower()
    if backend == "file":
        return MetricsStore()
    if backend == "pg":
        return PgMetricsStore()
    raise ValueError(f"unknown CHUNK_STORE_BACKEND: {backend!r} (file | pg)")
