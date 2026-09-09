#!/usr/bin/env python3
"""Record operator answers from state/thesis/questions.jsonl into notes/{T}/_thesis.md.

    python3 scripts/thesis/answer.py --list [--ticker COHR]
    python3 scripts/thesis/answer.py --id draft:COHR:datacom_ramp_continues --action keep|retire|confirm|challenge|edit [--text "..."]
    python3 scripts/thesis/answer.py --id score:COHR:ai_positioning --action accept|reject

Assumption actions set status_source: operator, draft: false and reviewed_by_operator: true on the
file ('keep' leaves the status as it stands; 'edit' replaces the statement). 'accept' on a score
question only prints the apply_scores command — the watchlist is written by apply_scores --write.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from thesis import STATE_DIR, thesis_io as tio   # noqa: E402

QUESTIONS = STATE_DIR / "questions.jsonl"
STATUS_FOR = {"retire": "retired", "confirm": "confirmed", "challenge": "challenged"}
ASSUMPTION_ACTIONS = ("keep", "edit", *STATUS_FOR)


def load_questions() -> list[dict]:
    if not QUESTIONS.exists():
        return []
    return [json.loads(l) for l in QUESTIONS.read_text(encoding="utf-8").splitlines() if l.strip()]


def save_questions(rows: list[dict]):
    tmp = QUESTIONS.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    tmp.replace(QUESTIONS)


def apply_answer(q: dict, action: str, text: str | None = None) -> str:
    fm = tio.load(q["ticker"])
    if not fm:
        raise ValueError(f"no thesis file for {q['ticker']}")
    if q["kind"] == "score_proposal":
        if action == "accept":
            return f"run: python3 scripts/thesis/apply_scores.py --accept {q['ticker']} --key {q['key']} --write"
        if action == "reject":
            (fm.get("proposed_scores") or {}).pop(q["key"], None)
            tio.save(q["ticker"], fm)
            return f"{q['ticker']} {q['key']}: proposal dropped"
        raise ValueError("score questions take --action accept|reject")
    if action not in ASSUMPTION_ACTIONS:
        raise ValueError(f"--action must be one of {ASSUMPTION_ACTIONS}")
    a = next((x for x in fm.get("assumptions") or [] if x["id"] == q["assumption_id"]), None)
    if not a:
        raise ValueError(f"{q['ticker']}: assumption {q['assumption_id']} not found")
    if action == "edit":
        if not text:
            raise ValueError("edit needs --text")
        a["statement"] = text.strip()
    elif action in STATUS_FOR:
        a["status"] = STATUS_FOR[action]
    a["status_source"] = "operator"
    a["draft"] = False
    fm["reviewed_by_operator"] = True
    tio.save(q["ticker"], fm)
    return f"{q['ticker']}/{a['id']}: {action} → status {a['status']} (operator)"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true"); ap.add_argument("--ticker"); ap.add_argument("--id"); ap.add_argument("--action"); ap.add_argument("--text")
    a = ap.parse_args(argv)
    rows = load_questions()
    if a.list or not a.id:
        for q in rows:
            if q.get("answered_at") or (a.ticker and q["ticker"] != a.ticker):
                continue
            print(f"{q['id']}\n    {q['text']}")
        return 0
    q = next((x for x in rows if x["id"] == a.id), None)
    if not q:
        print(f"unknown question id {a.id}"); return 1
    if not a.action:
        print("--action required"); return 1
    try:
        msg = apply_answer(q, a.action, a.text)
    except ValueError as e:
        print(f"ERROR {e}"); return 1
    q["answered_at"] = datetime.now(timezone.utc).isoformat()
    q["answer"] = {"action": a.action, "text": a.text}
    save_questions(rows)
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
