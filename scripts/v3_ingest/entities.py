#!/usr/bin/env python3
"""Entity + claim extraction — the analytical layer the 61 themes cannot provide.

WHY THIS EXISTS. The theme vocabulary is a closed set of 61 terms, hard-gated at
extraction (`t in valid_themes`), so a genuinely new subject can never appear. It is also
far too coarse to act on: `silicon_architecture_competition` tags 57.9% of all documents,
and NOTHING in the vocabulary covers optics, lasers or photonics. Meanwhile the corpus
holds 110 documents naming Chinese optical competitors that nothing connects to anything.

This extracts what you can actually act on: NAMED ENTITIES (including non-tickered
competitors like Innolight and Eoptolink), the SPECS at issue (400G/800G/1.6T, CPO, EML,
indium phosphide) and a one-sentence CLAIM, each pinned to the chunk it came from so every
downstream assertion is citable.

STORAGE. A separate `entity_mentions` table, NOT an array column on `chunks`:
  - a claim needs several fields, which an array cannot hold;
  - `chunks` is left completely untouched, so there is no re-embed and no risk to the
    15/28/28 gold eval.

SCOPE. Deliberately one vertical (optics/photonics) rather than the whole corpus. A cheap
regex pre-filter selects candidates (224 child chunks), so a full pass is ~$5-11 rather
than the ~$50-60 a corpus-wide pass would cost. Prove the output is worth acting on before
widening.

COVERAGE LIMIT — READ THIS BEFORE TRUSTING THE OUTPUT. Innolight, Eoptolink and Accelink
are Shenzhen/Shanghai-listed and file NOTHING with EDGAR. Everything extracted about them
is what US filers and narrative sources say ABOUT them — secondhand, and systematically
thinner than primary evidence. Treat a Chinese-competitor claim as a lead to verify, not
as established fact.

  python3 scripts/v3_ingest/entities.py --vertical optics --dry-run --limit 3
  python3 scripts/v3_ingest/entities.py --vertical optics --limit 20
  python3 scripts/v3_ingest/entities.py --vertical optics

Progress is checkpointed per chunk; an interrupted run resumes without re-spending.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/root/research-watchlist")
STATE = REPO_ROOT / "state" / "v3_ingest" / "entities.json"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v3_ingest"))

from sec_filings import is_auth_failure, log, run_claude  # noqa: E402

CONTENT_CAP = 14_000        # chars of chunk text sent to the extractor

# Pre-filter: cheap regex that decides which chunks are worth spending a call on.
VERTICALS: dict[str, str] = {
    "optics": (
        r"innolight|eoptolink|accelink|hisense broadband|hg genuine|source photonics|"
        r"400g|800g|1\.6t|silicon photonics|co-packaged|\bCPO\b|indium phosphide|\bEML\b"
    ),
}

ENTITY_TYPES = ("company", "product", "technology", "customer", "facility")
ROLES = ("competitor", "supplier", "customer", "partner", "self", "unclear")
STANCES = ("threat", "supportive", "neutral")

PROMPT = """You are extracting competitive intelligence from a research corpus excerpt.

Extract every NAMED entity that matters competitively, and for each one a single factual
claim the excerpt actually supports. Extract ONLY what the text states. Do not infer, do
not add outside knowledge, and do not include an entity the text merely lists in passing
with nothing said about it.

For each mention return:
  entity        the name as written (e.g. "Eoptolink", "InnoLight", "Fabrinet")
  entity_type   one of: company, product, technology, customer, facility
  country       the country of the entity if the text makes it clear, else null
  role          relative to {subject}: competitor, supplier, customer, partner, self, unclear
  specs         technical specs at issue, e.g. ["800G","1.6T","CPO"] — [] if none
  claim         ONE sentence, quoting or closely paraphrasing what the text says
  stance        threat / supportive / neutral, from {subject}'s point of view
  confidence    high / medium / low — how directly the text supports the claim

Output ONLY a JSON object, no prose or code fences:
{{"mentions": [{{"entity": "...", "entity_type": "...", "country": null, "role": "...",
"specs": [], "claim": "...", "stance": "...", "confidence": "..."}}]}}

If nothing competitively meaningful is present, return {{"mentions": []}}.

EXCERPT (subject company: {subject}, source: {doc_type}, dated {event_date}):
{text}
"""

DDL = """
CREATE TABLE IF NOT EXISTS entity_mentions (
    chunk_id     text NOT NULL,
    doc_id       text NOT NULL,
    subject      text,
    entity       text NOT NULL,
    entity_key   text NOT NULL,
    entity_type  text,
    country      text,
    role         text,
    specs        text[],
    claim        text,
    stance       text,
    confidence   text,
    doc_type     text,
    event_date   date,
    competitor_id text,          -- tier_4_competitors.id when the mention resolves
    competes_with text[],        -- whose thesis this bears on, from the registry
    extracted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (chunk_id, entity_key, claim)
);
CREATE INDEX IF NOT EXISTS entity_mentions_key_idx     ON entity_mentions (entity_key);
CREATE INDEX IF NOT EXISTS entity_mentions_subject_idx ON entity_mentions (subject);
CREATE INDEX IF NOT EXISTS entity_mentions_date_idx    ON entity_mentions (event_date);
CREATE INDEX IF NOT EXISTS entity_mentions_comp_idx    ON entity_mentions (competitor_id);
"""


def entity_key(name: str) -> str:
    """Normalise for grouping: 'InnoLight Technology' and 'Innolight' collapse together.

    CJK ideographs are PRESERVED — stripping to [a-z0-9] alone maps every Chinese-name
    alias ('中际旭创') to the empty string, which both loses the alias and collides all
    such names onto one key."""
    k = re.sub(r"[^a-z0-9一-鿿぀-ヿ ]", "", (name or "").lower())
    k = re.sub(r"\b(inc|corp|corporation|co|ltd|limited|plc|technologies|technology|"
               r"holdings|group|company|nv|sa|ag|kk)\b", "", k)
    k = re.sub(r"\s+", " ", k).strip()
    # Never return empty for a non-empty input — an empty key would merge unrelated
    # entities under one primary-key slot.
    return k or re.sub(r"\s+", " ", (name or "").lower()).strip()


def load_competitor_registry() -> tuple[dict[str, str], dict[str, dict]]:
    """(alias_key -> canonical id, id -> entry) from watchlist tier_4_competitors.

    These companies file nothing with EDGAR (`edgar_coverage: false`), so the ONLY way
    they enter the corpus is as mentions inside other companies' documents. Resolving
    aliases here is what turns 'InnoLight'/'Zhongji Innolight'/'中际旭创' scattered across
    filings into one addressable entity mapped to whose thesis it threatens."""
    import yaml
    wl = yaml.safe_load((REPO_ROOT / "config" / "watchlist.yaml").read_text()) or {}
    alias_to_id: dict[str, str] = {}
    by_id: dict[str, dict] = {}
    for e in (wl.get("tier_4_competitors") or []):
        cid = e.get("id")
        if not cid:
            continue
        by_id[cid] = e
        for a in ([e.get("name")] + list(e.get("aliases") or [])):
            k = entity_key(a or "")
            if k:
                alias_to_id[k] = cid
    return alias_to_id, by_id


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"done": [], "cost": 0.0}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n")


def ensure_table() -> None:
    from pgconn import connect
    cx = connect()
    cx.cursor().execute(DDL)
    cx.commit()


def candidates(rx: str, done: set[str]) -> list[dict]:
    from pgconn import connect
    cur = connect().cursor()
    cur.execute("""SELECT chunk_id, doc_id, text, doc_type, event_date, tickers
                     FROM chunks
                    WHERE kind='child' AND text ~* %s
                    ORDER BY event_date DESC NULLS LAST, chunk_id""", (rx,))
    out = []
    for cid, did, text, dtp, ed, tks in cur.fetchall():
        if cid in done:
            continue
        out.append({"chunk_id": cid, "doc_id": did, "text": text, "doc_type": dtp,
                    "event_date": ed, "tickers": tks or []})
    return out


def extract(row: dict, alias_to_id: dict[str, str],
            by_id: dict[str, dict]) -> tuple[list[dict], float]:
    subject = (row["tickers"] or ["the subject company"])[0]
    prompt = PROMPT.format(subject=subject, doc_type=row["doc_type"],
                           event_date=row["event_date"], text=row["text"][:CONTENT_CAP])
    text, cost = run_claude(prompt)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON in response: {text[:160]!r}")
    obj = json.loads(m.group(0))
    out = []
    for x in (obj.get("mentions") or []):
        name = (x.get("entity") or "").strip()
        claim = (x.get("claim") or "").strip()
        if not name or not claim:
            continue
        key = entity_key(name)
        cid = alias_to_id.get(key)
        reg = by_id.get(cid or "", {})
        out.append({
            "entity": name,
            "entity_key": key,
            "competitor_id": cid,
            "competes_with": list(reg.get("competes_with") or []),
            # The registry is authoritative on country — an extractor reading a US
            # filing often cannot tell where a named competitor is domiciled.
            "registry_country": reg.get("country"),
            "entity_type": x.get("entity_type") if x.get("entity_type") in ENTITY_TYPES else None,
            "country": reg.get("country") or (x.get("country") or None),
            "role": x.get("role") if x.get("role") in ROLES else "unclear",
            "specs": [str(s) for s in (x.get("specs") or [])],
            "claim": claim,
            "stance": x.get("stance") if x.get("stance") in STANCES else "neutral",
            "confidence": x.get("confidence"),
        })
    return out, cost


def persist(row: dict, mentions: list[dict]) -> int:
    if not mentions:
        return 0
    from pgconn import connect
    cx = connect()
    cur = cx.cursor()
    subject = (row["tickers"] or [None])[0]
    n = 0
    for m in mentions:
        cur.execute(
            """INSERT INTO entity_mentions
               (chunk_id, doc_id, subject, entity, entity_key, entity_type, country,
                role, specs, claim, stance, confidence, doc_type, event_date,
                competitor_id, competes_with)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (chunk_id, entity_key, claim) DO NOTHING""",
            (row["chunk_id"], row["doc_id"], subject, m["entity"], m["entity_key"],
             m["entity_type"], m["country"], m["role"], m["specs"], m["claim"],
             m["stance"], m["confidence"], row["doc_type"], row["event_date"],
             m.get("competitor_id"), m.get("competes_with") or []))
        n += cur.rowcount
    cx.commit()
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Entity + claim extraction (one vertical)")
    ap.add_argument("--vertical", default="optics", choices=sorted(VERTICALS))
    ap.add_argument("--limit", type=int, help="process at most N chunks")
    ap.add_argument("--dry-run", action="store_true",
                    help="extract + print; no table write, no checkpoint")
    args = ap.parse_args()

    rx = VERTICALS[args.vertical]
    st = load_state()
    done = set(st["done"])
    alias_to_id, by_id = load_competitor_registry()
    if not args.dry_run:
        ensure_table()

    rows = candidates(rx, done if not args.dry_run else set())
    if args.limit:
        rows = rows[:args.limit]
    log(f"ENTITIES START vertical={args.vertical} candidates={len(rows)} "
        f"already_done={len(done)} dry_run={args.dry_run}")

    ok = empty = failed = written = 0
    cost = 0.0
    for i, row in enumerate(rows, 1):
        try:
            mentions, c = extract(row, alias_to_id, by_id)
            cost += c
        except Exception as e:  # noqa: BLE001
            failed += 1
            log(f"  [{i}/{len(rows)}] FAILED {row['chunk_id'][:50]}: {type(e).__name__}: {e}")
            if is_auth_failure(e):
                log("  auth failure — aborting run rather than burning the whole batch")
                break
            continue

        if not mentions:
            empty += 1
        else:
            ok += 1
        if args.dry_run:
            log(f"  [{i}/{len(rows)}] {row['chunk_id'][:46]} ({row['doc_type']}, "
                f"{row['event_date']}) -> {len(mentions)} mentions")
            for m in mentions:
                log(f"       {m['entity']:<20} {str(m.get('competitor_id') or '-'):<20} {m['role']:<11}"
                    f"{','.join(m['specs'])[:18]:<20}{m['stance']:<10} {m['claim'][:90]}")
            continue

        written += persist(row, mentions)
        st["done"].append(row["chunk_id"])
        st["cost"] = st.get("cost", 0.0) + c
        save_state(st)
        log(f"  [{i}/{len(rows)}] {row['chunk_id'][:46]} -> {len(mentions)} mentions")

    log(f"ENTITIES DONE vertical={args.vertical} with_mentions={ok} empty={empty} "
        f"failed={failed} rows_written={written} cost=${cost:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
