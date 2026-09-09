"""Read/write/validate notes/{TICKER}/_thesis.md and the pressure/status math.

Frontmatter is the machine-read state; the body is human prose and is preserved
byte-for-byte on every save. No existing helper rewrites YAML-only, so this is the
one place that does it (regex from chunker._parse_frontmatter; atomic write pattern
from backfill_frontmatter._write_note_atomic).
"""
from __future__ import annotations
import os, re, sys, tempfile
from datetime import date, timedelta
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
NOTES = REPO / "notes"
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
from ingest_metrics import universe  # noqa: E402,F401  (T1+T2, drops A000660)

STATUSES = ("open", "confirmed", "challenged", "retired")
STATUS_SOURCES = ("draft", "evidence", "operator")
SCORE_KEYS = ("ai_positioning", "competitive_advantage.innovation_rate",
              "competitive_advantage.distribution", "competitive_advantage.overall",
              "potential_investor_interest.score")
SOURCE_WEIGHT = {"podcast_summary": 0.5, "substack_post": 0.5}   # commentary, not disclosure
CHALLENGE_THRESHOLD = 4       # strength-sum within window
MIN_SOURCES = 2               # distinct sources within window
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def thesis_path(ticker: str) -> Path:
    return NOTES / ticker / "_thesis.md"


def load(ticker: str) -> dict | None:
    p = thesis_path(ticker)
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ValueError(f"{p}: no frontmatter")
    fm = yaml.safe_load(m.group(1)) or {}
    fm["_body"] = text[m.end():]
    return fm


def save(ticker: str, fm: dict, body: str | None = None) -> Path:
    p = thesis_path(ticker)
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = {k: v for k, v in fm.items() if not k.startswith("_")}
    if body is None:
        body = (load(ticker) or {}).get("_body", "") if p.exists() else ""
    errs = validate(fm)
    if errs:
        raise ValueError(f"{p}: " + "; ".join(errs))
    content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".md", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return p


def validate(fm: dict) -> list[str]:
    errs = []
    if fm.get("doc_type") != "thesis":
        errs.append("doc_type must be 'thesis'")
    if not fm.get("ticker"):
        errs.append("ticker missing")
    seen = set()
    for a in fm.get("assumptions") or []:
        aid = a.get("id")
        if not aid or not re.match(r"^[a-z0-9_]+$", aid):
            errs.append(f"bad id {aid!r}")
        if aid in seen:
            errs.append(f"duplicate id {aid}")
        seen.add(aid)
        if a.get("status") not in STATUSES:
            errs.append(f"{aid}: status {a.get('status')!r} not in {STATUSES}")
        if a.get("status_source") not in STATUS_SOURCES:
            errs.append(f"{aid}: status_source invalid")
        if not a.get("statement"):
            errs.append(f"{aid}: statement missing")
        if not a.get("challenged_by"):
            errs.append(f"{aid}: challenged_by empty")
    for k in fm.get("scores") or {}:
        if k not in SCORE_KEYS:
            errs.append(f"unknown score key {k}")
    return errs


def _score_str(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("score")
    return None if v is None else str(v)


def _load_watchlist() -> dict:
    return yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())


def watchlist_entry(ticker: str, watchlist: dict | None = None) -> tuple[str | None, dict]:
    """(tier, entry) for a T1/T2 ticker; (None, {}) otherwise."""
    w = watchlist or _load_watchlist()
    for tier in ("tier_1_bctk", "tier_2_active_candidates"):
        for e in w.get(tier) or []:
            if isinstance(e, dict) and e.get("ticker") == ticker:
                return tier, e
    return None, {}


def watchlist_scores(ticker: str, watchlist: dict | None = None) -> dict[str, str]:
    """Mirror of the five score keys from watchlist.yaml (both schema variants)."""
    _, e = watchlist_entry(ticker, watchlist)
    if not e:
        return {}
    ca = e.get("competitive_advantage") or {}
    out = {
        "ai_positioning": _score_str(e.get("ai_positioning")),
        "competitive_advantage.innovation_rate": _score_str(ca.get("innovation_rate")),
        "competitive_advantage.distribution": _score_str(ca.get("distribution")),
        "competitive_advantage.overall": _score_str(ca.get("overall")),
        "potential_investor_interest.score": _score_str(e.get("potential_investor_interest")),
    }
    return {k: v for k, v in out.items() if v is not None}


def tier_of(ticker: str, watchlist: dict | None = None) -> str | None:
    return watchlist_entry(ticker, watchlist)[0]


def recompute_pressure(fm: dict, log_rows: list[dict], today: date, window_days: int = 90) -> dict:
    """Recompute per-assumption pressure from evidence rows and propose status moves.

    Rule: `challenged` when challenge strength-sum >= CHALLENGE_THRESHOLD from >= MIN_SOURCES
    distinct sources within the window, OR any row with source 'earnings_break'; `confirmed`
    symmetrically ('earnings_confirm'). Never touches an assumption whose status_source is
    'operator' or whose status is 'retired'. Records changes in fm['_changes'].
    """
    cutoff = today - timedelta(days=window_days)
    by_id: dict[str, list[dict]] = {}
    for r in log_rows:
        if not r.get("assumption_id"):
            continue
        try:
            d = date.fromisoformat(str(r.get("date"))[:10])
        except ValueError:
            continue
        if d >= cutoff:
            by_id.setdefault(r["assumption_id"], []).append(dict(r, _d=d))
    changes = []
    for a in fm.get("assumptions") or []:
        rows = by_id.get(a["id"], [])
        conf = sum(r["strength"] * SOURCE_WEIGHT.get(r["source"], 1.0) for r in rows if r["direction"] == "confirm")
        chal = sum(r["strength"] * SOURCE_WEIGHT.get(r["source"], 1.0) for r in rows if r["direction"] == "challenge")
        last = max((r["_d"] for r in rows), default=None)
        a["pressure"] = {"confirm": conf, "challenge": chal, "window_days": window_days,
                         "last_evidence": last.isoformat() if last else None}
        if a.get("status_source") == "operator" or a.get("status") == "retired":
            continue
        chal_src = {r["source"] for r in rows if r["direction"] == "challenge"}
        conf_src = {r["source"] for r in rows if r["direction"] == "confirm"}
        new = a["status"]
        if "earnings_break" in chal_src or (chal >= CHALLENGE_THRESHOLD and len(chal_src) >= MIN_SOURCES and chal > conf):
            new = "challenged"
        elif "earnings_confirm" in conf_src or (conf >= CHALLENGE_THRESHOLD and len(conf_src) >= MIN_SOURCES and conf > chal):
            new = "confirmed"
        if new != a["status"]:
            changes.append({"assumption_id": a["id"], "from": a["status"], "to": new,
                            "evidence_ids": [r.get("source_id") for r in rows]})
            a["status"] = new
            a["status_source"] = "evidence"
    fm["_changes"] = changes
    return fm
