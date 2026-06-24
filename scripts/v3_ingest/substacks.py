#!/usr/bin/env python3
"""
Path A v3 Substack channel.

Daily (06:00 ET) the droplet reads the Gmail "Substack" label on
ashimmehratranscripts@gmail.com, converts each newsletter's HTML body to markdown,
matches the sender to config/substack_subscriptions.yaml, LLM-extracts tickers +
themes (claude -p, subscription auth), writes
notes/substacks/{date}-{pub-slug}-{title-slug}.md with multi-ticker frontmatter,
and ingests it into the pg corpus via the existing v3-aware chunker.

Reuses the transcript poller's IMAP credentials (/root/.gmail-poller.env) but reads
the **Substack LABEL** (not INBOX UNSEEN) in READ-ONLY mode and **never sets
\\Seen**, so it cannot collide with poll_gmail_transcripts.py (which scans INBOX
UNSEEN and marks Seen). Dedup is by Message-ID in a watermark file.

  cron: 0 10 * * * cd /root/research-watchlist && /root/bin/alert_on_failure.sh \\
        v3_substacks python3 scripts/v3_ingest/substacks.py >> logs/v3_substacks.log 2>&1

  python3 scripts/v3_ingest/substacks.py            # process new labeled messages
  python3 scripts/v3_ingest/substacks.py --dry-run  # parse + extract, no write/ingest/watermark
  python3 scripts/v3_ingest/substacks.py --eml FILE  # process a local .eml (no IMAP) — testing

Env: self-loads GMAIL_USER/GMAIL_APP_PASSWORD from /root/.gmail-poller.env and
CHUNK_STORE_BACKEND from /root/podcasts/.env. Does NOT source podcasts/.env wholesale
(it holds ANTHROPIC_API_KEY, which would flip claude -p off subscription auth);
claude -p is additionally invoked with ANTHROPIC_API_KEY stripped from the subprocess
env. embed.py + pgconn.py self-load GEMINI_API_KEY / DATABASE_URL.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email
import imaplib
import json
import os
import re
import subprocess
import sys
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path

import yaml

# ───────────────────────────── Configuration ─────────────────────────────

REPO_ROOT = Path("/root/research-watchlist")
NOTES_DIR = REPO_ROOT / "notes" / "substacks"
STATE_DIR = REPO_ROOT / "state" / "v3_ingest"
WATERMARK_FILE = STATE_DIR / "substacks_watermark.json"
SUBS_CONFIG = REPO_ROOT / "config" / "substack_subscriptions.yaml"
TICKER_IDENTITY = REPO_ROOT / "config" / "ticker_identity.yaml"
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
CHUNKING_DIR = REPO_ROOT / "scripts" / "chunking"

GMAIL_ENV = Path("/root/.gmail-poller.env")
PODCASTS_ENV = Path("/root/podcasts/.env")
GMAIL_HOST = "imap.gmail.com"
GMAIL_LABEL = "Substack"

MODEL = "claude-sonnet-4-6"
CLAUDE_TIMEOUT_S = 300
CONTENT_CAP = 16_000               # chars of post body passed to the LLM extractor
MAX_MESSAGES_PER_RUN = 50

sys.path.insert(0, str(CHUNKING_DIR))   # chunker / ingest / store / embed

_GMAIL_USER = ""
_GMAIL_PW = ""


# ───────────────────────────── Logging ─────────────────────────────

def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] v3_substacks: {msg}", flush=True)


# ───────────────────────────── Env ─────────────────────────────

def _read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith((f"{key}=", f"export {key}=")):
            return line.split("=", 1)[1].strip().strip("\"'")
    return None


def load_env() -> None:
    """Populate gmail creds (module globals) + CHUNK_STORE_BACKEND (os.environ).
    Does NOT touch ANTHROPIC_API_KEY (kept absent so claude -p uses subscription)."""
    global _GMAIL_USER, _GMAIL_PW
    _GMAIL_USER = os.environ.get("GMAIL_USER") or _read_env_value(GMAIL_ENV, "GMAIL_USER") or ""
    _GMAIL_PW = (os.environ.get("GMAIL_APP_PASSWORD")
                 or _read_env_value(GMAIL_ENV, "GMAIL_APP_PASSWORD") or "")
    if not os.environ.get("CHUNK_STORE_BACKEND"):
        os.environ["CHUNK_STORE_BACKEND"] = _read_env_value(PODCASTS_ENV, "CHUNK_STORE_BACKEND") or "pg"


def _claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def run_claude(prompt: str) -> tuple[str, float]:
    cmd = ["claude", "-p", prompt, "--output-format", "json",
           "--allowedTools", "", "--model", MODEL]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=CLAUDE_TIMEOUT_S, cwd=str(REPO_ROOT), env=_claude_env())
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} stderr={result.stderr[:300]}")
    env = json.loads(result.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"claude -p is_error: {str(env.get('result'))[:200]}")
    return env.get("result", ""), float(env.get("total_cost_usd", 0.0) or 0.0)


# ───────────────────────────── Vocab + subscriptions ─────────────────────────────

def load_valid_tickers() -> set[str]:
    return {str(k) for k in (yaml.safe_load(TICKER_IDENTITY.read_text()) or {}).keys()}


def load_valid_themes() -> set[str]:
    block = (yaml.safe_load(WATCHLIST_YAML.read_text()) or {}).get("themes", {}) or {}
    out: set[str] = set()
    for cat in block.values():
        out.update(cat or [])
    return out


def load_subscriptions() -> list[dict]:
    return (yaml.safe_load(SUBS_CONFIG.read_text()) or {}).get("publications", [])


def match_publication(from_header: str, subs: list[dict]) -> dict | None:
    low = (from_header or "").lower()
    for pub in subs:
        for pat in (pub.get("sender_patterns") or []):
            if pat.lower() in low:
                return pub
    return None


# ───────────────────────────── IMAP ─────────────────────────────

def imap_connect() -> imaplib.IMAP4_SSL:
    if not _GMAIL_USER or not _GMAIL_PW:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD not loaded (check /root/.gmail-poller.env)")
    imap = imaplib.IMAP4_SSL(GMAIL_HOST)
    imap.login(_GMAIL_USER, _GMAIL_PW.replace(" ", ""))
    return imap


def fetch_labeled(imap: imaplib.IMAP4_SSL) -> list[tuple[bytes, Message]]:
    """Select the Substack label READ-ONLY (EXAMINE — guarantees no flag writes,
    so \\Seen is never set) and return [(uid, Message)] for ALL messages in it."""
    typ, _ = imap.select(f'"{GMAIL_LABEL}"', readonly=True)
    if typ != "OK":
        raise RuntimeError(f"cannot select label {GMAIL_LABEL!r} (filter/label not set up yet?)")
    typ, data = imap.search(None, "ALL")
    if typ != "OK":
        raise RuntimeError(f"IMAP search failed: {typ}")
    out = []
    for uid in data[0].split():
        typ, msg_data = imap.fetch(uid, "(RFC822)")
        if typ != "OK" or not msg_data or not msg_data[0]:
            log(f"  fetch failed uid={uid.decode(errors='ignore')}")
            continue
        out.append((uid, email.message_from_bytes(msg_data[0][1])))
    return out


# ───────────────────────────── Parse + transform ─────────────────────────────

def _decode(s: str | None) -> str:
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:  # noqa: BLE001
        return s


def message_id(msg: Message) -> str:
    return (msg.get("Message-ID") or "").strip()


def msg_date(msg: Message) -> str:
    raw = msg.get("Date")
    try:
        return parsedate_to_datetime(raw).date().isoformat()
    except Exception:  # noqa: BLE001
        return dt.date.today().isoformat()


def extract_html_body(msg: Message) -> str:
    """Best HTML part (fallback text/plain wrapped)."""
    html = plain = ""
    for part in msg.walk():
        ctype = part.get_content_type()
        if part.get_content_maintype() == "multipart":
            continue
        if ctype not in ("text/html", "text/plain"):
            continue
        try:
            payload = part.get_payload(decode=True)
            text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        if ctype == "text/html" and not html:
            html = text
        elif ctype == "text/plain" and not plain:
            plain = text
    if html:
        return html
    return f"<pre>{plain}</pre>" if plain else ""


_FOOTER_MARKERS = ("Unsubscribe", "View this post on the web", "View in browser",
                   "You're currently a free subscriber", "Get the app",
                   "© 20", "You're receiving this", "Update your profile",
                   "Like Comment Restack", "No longer want to receive")


def html_to_markdown(html: str) -> str:
    """bs4-based HTML→markdown (no html2text/trafilatura installed). Treats h*/p/li/
    blockquote/pre as leaf blocks (no recursion into them → no nested duplication),
    recurses through containers, renders <a> inline as [text](url). Trims Substack
    footer chrome."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html or "", "html.parser")
    for t in soup(["script", "style", "head", "img", "svg", "noscript"]):
        t.decompose()
    for sel in soup.select('[class*="footer"],[class*="subscribe"],[class*="share"],'
                            '[class*="comment"],[class*="unsubscribe"],[class*="preview"],'
                            '[id*="footer"]'):
        sel.decompose()

    def inline(el) -> str:
        parts = []
        for d in el.children:
            if isinstance(d, str):
                parts.append(d)
            elif getattr(d, "name", None) == "a" and d.get("href"):
                parts.append(f"[{d.get_text(' ', strip=True)}]({d['href']})")
            elif getattr(d, "name", None) == "br":
                parts.append("\n")
            else:
                parts.append(inline(d))
        return "".join(parts)

    prefix = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ", "li": "- ", "blockquote": "> "}
    leaf = set(prefix) | {"p", "pre"}
    container = {"ul", "ol", "div", "section", "article", "table", "tbody",
                 "thead", "tr", "td", "th", "body", "main", "center", "span", "font", "html"}
    lines: list[str] = []

    def walk(el) -> None:
        for child in el.children:
            name = getattr(child, "name", None)
            if name is None:
                continue
            if name in leaf:
                txt = re.sub(r"[ \t]+", " ", inline(child)).strip()
                if txt:
                    lines.append(prefix.get(name, "") + txt)
            elif name in container:
                walk(child)

    walk(soup.body or soup)
    md = re.sub(r"\n{3,}", "\n\n", "\n\n".join(lines)).strip()

    # Trim footer: cut at the earliest footer marker that appears well into the body.
    cut = len(md)
    for marker in _FOOTER_MARKERS:
        i = md.find(marker)
        if i >= 600:
            cut = min(cut, i)
    return md[:cut].strip()


def post_url_from_body(html: str) -> str | None:
    m = re.search(r'https?://[^\s"\'<>]+/p/[^\s"\'<>?]+', html or "")
    return m.group(0) if m else None


# ───────────────────────────── Tag extraction (LLM) ─────────────────────────────

EXTRACT_INSTRUCTIONS = """\
You are a precise financial-research tagging assistant. From the SUBSTACK POST
below, extract two things, using ONLY the provided vocabularies.

1. tickers — the WATCHLIST TICKERS substantively discussed (meaningful discussion of
   the company's business, strategy, products, financials, competitive position,
   capital allocation, or outlook). EXCLUDE mere name-drops or generic sector
   mentions. Use the EXACT watchlist symbol.
2. themes — the THEME TAGS substantively present. Only tags from the list.

Output ONLY a JSON object, no prose / markdown / code fences:
{"tickers": ["..."], "themes": ["..."]}
"""


def extract_tags(content: str, pub: dict | None, valid_tickers: set[str],
                 valid_themes: set[str]) -> tuple[list[str], list[str], float]:
    hints = ", ".join((pub or {}).get("default_themes") or []) or "(none)"
    prompt = (EXTRACT_INSTRUCTIONS
              + "\nWATCHLIST TICKERS (only these are valid):\n" + ", ".join(sorted(valid_tickers))
              + "\n\nTHEME TAGS (only these are valid):\n" + ", ".join(sorted(valid_themes))
              + f"\n\nPUBLICATION: {(pub or {}).get('name', 'unknown')} "
              + f"(typical themes, hints only — still verify per-post: {hints})"
              + "\n\nSUBSTACK POST:\n" + content[:CONTENT_CAP] + "\n")
    text, cost = run_claude(prompt)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object in extraction response: {text[:160]!r}")
    obj = json.loads(m.group(0))
    tickers = [t for t in (obj.get("tickers") or []) if t in valid_tickers]
    themes = [t for t in (obj.get("themes") or []) if t in valid_themes]
    return tickers, themes, cost


# ───────────────────────────── Note write + ingest ─────────────────────────────

def slugify(s: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s[:maxlen].strip("-")) or "untitled"


def build_note(*, pub: dict | None, subject: str, sender: str, msg_id: str,
               source_url: str | None, source_date: str, tickers: list[str],
               themes: list[str], body_md: str) -> str:
    fm = {
        "doc_type": "substack_post",
        "source": "substack",
        "publication": (pub or {}).get("name") or "unknown",
        "publication_url": (pub or {}).get("url") or "",
        "source_email": msg_id,                  # Message-ID — dedup key
        "source_sender": sender,
        "source_url": source_url or "",
        "source_date": source_date,
        "subscription_tier": (pub or {}).get("tier") or "unknown",
        "tickers": tickers,
        "themes": themes,
        "ingestion_date": dt.date.today().isoformat(),
        "extraction_source": "v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes",
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    # Many Substack posts carry the title as a leading H1 in the body — don't
    # duplicate it. Prepend a title heading only when the body lacks its own.
    head = "" if body_md.lstrip().startswith("# ") else f"# {subject}\n\n"
    return f"---\n{front}---\n\n{head}{body_md}\n"


def note_path(pub: dict | None, source_date: str, subject: str) -> Path:
    pub_slug = slugify((pub or {}).get("name", "unknown"), 30)
    return NOTES_DIR / f"{source_date}-{pub_slug}-{slugify(subject)}.md"


def ingest_note(path: Path) -> None:
    from ingest import ingest
    ingest([path])


# ───────────────────────────── Watermark ─────────────────────────────

def load_watermark() -> dict:
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"processed_message_ids": {}, "runs": 0}


def save_watermark(wm: dict, newly: dict) -> None:
    wm.setdefault("processed_message_ids", {}).update(newly)
    wm["runs"] = wm.get("runs", 0) + 1
    wm["last_run_at"] = dt.datetime.now().isoformat(timespec="seconds")
    WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_FILE.write_text(json.dumps(wm, indent=2) + "\n")


# ───────────────────────────── Per-message processing ─────────────────────────────

def process_message(msg: Message, subs: list[dict], *, dry_run: bool,
                    valid_tickers: set[str], valid_themes: set[str]) -> tuple[str, float]:
    """Returns (status, cost). Raises on hard failure (caller isolates per-message)."""
    mid = message_id(msg)
    sender = _decode(msg.get("From", ""))
    subject = _decode(msg.get("Subject")) or "untitled"
    source_date = msg_date(msg)

    pub = match_publication(sender, subs)
    html = extract_html_body(msg)
    body_md = html_to_markdown(html)
    if len(body_md) < 80:
        raise ValueError(f"body too short after HTML→md ({len(body_md)} chars) — not a readable post")

    tickers, themes, cost = extract_tags(body_md, pub, valid_tickers, valid_themes)
    note = build_note(pub=pub, subject=subject, sender=sender, msg_id=mid,
                      source_url=post_url_from_body(html), source_date=source_date,
                      tickers=tickers, themes=themes, body_md=body_md)
    path = note_path(pub, source_date, subject)
    pub_name = pub.get("name") if pub else "UNMATCHED"

    if dry_run:
        log(f"  [dry-run] would write {path.name} (pub={pub_name}, tickers={tickers}, "
            f"themes={themes}, {len(body_md)} body chars); no ingest/watermark")
        print("\n----- DRY-RUN NOTE (" + path.name + ") -----\n"
              + note[:1800] + ("\n…[truncated]…\n" if len(note) > 1800 else "\n")
              + "----- END -----\n", flush=True)
        return "ok", cost

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(note)
    try:
        ingest_note(path)
        log(f"  WROTE+INGESTED {path.name} (pub={pub_name}, tickers={tickers})")
    except Exception as e:  # noqa: BLE001 — note persisted; reingest later via ingest.py --note
        log(f"  WROTE {path.name} but INGEST_DEFERRED: {type(e).__name__}: {e}")
    return "ok", cost


# ───────────────────────────── Main ─────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Path A v3 Substack channel")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse + extract + print; no write, no ingest, no watermark")
    ap.add_argument("--eml", help="process a local .eml file instead of IMAP (testing)")
    args = ap.parse_args()

    load_env()
    subs = load_subscriptions()
    valid_tickers = load_valid_tickers()
    valid_themes = load_valid_themes()
    wm = load_watermark()
    seen = set(wm.get("processed_message_ids", {}))
    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log(f"START mode={mode} backend={os.environ.get('CHUNK_STORE_BACKEND')} "
        f"label={GMAIL_LABEL} publications={len(subs)}")

    imap = None
    if args.eml:
        msgs = [(b"local", email.message_from_bytes(Path(args.eml).read_bytes()))]
    else:
        imap = imap_connect()
        msgs = fetch_labeled(imap)
    log(f"messages_in_scope={len(msgs)}")

    newly: dict[str, str] = {}
    processed = skipped = failed = 0
    total_cost = 0.0
    try:
        for _uid, msg in msgs[:MAX_MESSAGES_PER_RUN]:
            mid = message_id(msg)
            if mid and mid in seen and not args.dry_run:
                skipped += 1
                continue
            log(f"PROCESS {mid or '(no message-id)'} | {_decode(msg.get('Subject'))[:70]!r}")
            try:
                _status, cost = process_message(msg, subs, dry_run=args.dry_run,
                                                valid_tickers=valid_tickers, valid_themes=valid_themes)
                total_cost += cost
                processed += 1
                if mid and not args.dry_run:
                    newly[mid] = dt.datetime.now().isoformat(timespec="seconds")
            except Exception as e:  # noqa: BLE001 — per-message isolation; retried next run
                failed += 1
                log(f"  FAILED msg_id={mid or '(none)'}: {type(e).__name__}: {e}")
    finally:
        if imap is not None:
            try:
                imap.logout()
            except Exception:  # noqa: BLE001
                pass

    if not args.dry_run and newly:
        save_watermark(wm, newly)
    log(f"DONE mode={mode} processed={processed} skipped={skipped} failed={failed} "
        f"cost=${total_cost:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
