"""Thesis loop: per-ticker `_thesis.md` objects, evidence matching, reporting."""
from pathlib import Path
REPO = Path("/root/research-watchlist")
STATE_DIR = REPO / "state" / "thesis"


def extract_json(text: str) -> dict:
    """Parse the JSON object in a claude -p reply: fenced, bare, or with trailing prose."""
    import json, re
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", t):
        try:
            obj, _ = dec.raw_decode(t, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj:
            return obj
    raise json.JSONDecodeError("no JSON object found", t[:80], 0)


def save_failed_reply(name: str, text: str):
    p = STATE_DIR / "_failed"
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{name}.txt").write_text(text, encoding="utf-8")
