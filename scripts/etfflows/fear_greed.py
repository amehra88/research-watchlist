"""
fear_greed — CNN Fear & Greed index, the sentiment regime line above Block A.

WHY THE HEADERS MATTER: `production.dataviz.cnn.io` returns HTTP 418 to this droplet for a
plain request, and also for a request carrying only a browser User-Agent. It needs the
Referer/Origin/sec-fetch-site set below to look like a same-site XHR from the Fear & Greed
page. Verified 200 / 177,385 bytes on 2026-08-19 with exactly these headers; verified 418
without them. Do not "simplify" the header block.

SCOPE, STATED ONCE SO IT IS NOT RE-ASKED: this is a MARKET-WIDE index. There is no
per-stock CNN Fear & Greed. Nothing here can be sliced by ticker.

DEGRADATION IS THE POINT: sentiment is context, not the product. A CNN outage must never
take down the 07:00 digest, so every failure path falls back to the last cached value
labelled with its age, and the caller gets a line either way.

Payload shape (verified live):
  fear_and_greed: {score, rating, timestamp, previous_close,
                   previous_1_week, previous_1_month, previous_1_year}
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import NamedTuple

from . import FEAR_GREED_MAX_AGE_HOURS, FEAR_GREED_URL

# The exact header set that turns a 418 into a 200 from this box.
_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Referer": "https://www.cnn.com/markets/fear-and-greed",
    "Origin": "https://www.cnn.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "Accept": "application/json, text/plain, */*",
}


class FearGreed(NamedTuple):
    score: float
    rating: str
    timestamp: str
    previous_close: float | None
    week_ago: float | None
    month_ago: float | None
    year_ago: float | None
    fetched_at: str

    def as_dict(self) -> dict:
        return dict(self._asdict())


def fetch(url: str = FEAR_GREED_URL, timeout: int = 20) -> dict:
    """Raw GET. Raises on any transport error — callers use `get()`, which degrades."""
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def parse(payload: dict, now: datetime | None = None) -> FearGreed:
    """Extract the header fields. Raises if the block is missing — a silent default would
    print a confident 0.0 / 'extreme fear' that nobody could distinguish from real data."""
    block = (payload or {}).get("fear_and_greed")
    if not isinstance(block, dict) or block.get("score") is None:
        raise ValueError("payload has no usable fear_and_greed block")
    now = now or datetime.now(timezone.utc)

    def num(key):
        v = block.get(key)
        return float(v) if isinstance(v, (int, float)) else None

    return FearGreed(
        score=float(block["score"]),
        rating=str(block.get("rating") or "unknown"),
        timestamp=str(block.get("timestamp") or ""),
        previous_close=num("previous_close"),
        week_ago=num("previous_1_week"),
        month_ago=num("previous_1_month"),
        year_ago=num("previous_1_year"),
        fetched_at=now.isoformat(),
    )


def save_cache(path: str, fg: FearGreed) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w") as fh:
        json.dump(fg.as_dict(), fh)
    os.replace(tmp, path)          # atomic: a crash mid-write must not leave a torn cache


def load_cache(path: str) -> FearGreed | None:
    try:
        with open(path) as fh:
            return FearGreed(**json.load(fh))
    except (OSError, ValueError, TypeError):
        return None


def age_hours(fg: FearGreed, now: datetime | None = None) -> float | None:
    now = now or datetime.now(timezone.utc)
    try:
        then = datetime.fromisoformat(fg.fetched_at)
    except ValueError:
        return None
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return (now - then).total_seconds() / 3600.0


def get(cache_path: str, fetcher=None, now: datetime | None = None
        ) -> tuple[FearGreed | None, str]:
    """Return (reading, status). NEVER raises.

    status is one of:
      'live'   — fetched fresh this run
      'cached' — fetch failed, serving the last known value (its age goes in the rendered line)
      'stale'  — cached value older than FEAR_GREED_MAX_AGE_HOURS; still shown, clearly marked
      'none'   — no fetch and no cache; the caller omits the line entirely
    """
    fetcher = fetcher or fetch
    now = now or datetime.now(timezone.utc)
    try:
        fg = parse(fetcher(), now=now)
        try:
            save_cache(cache_path, fg)
        except OSError:
            pass                   # a read-only cache dir must not lose us a good reading
        return fg, "live"
    except Exception:              # noqa: BLE001 — deliberate: sentiment never fails the digest
        cached = load_cache(cache_path)
        if cached is None:
            return None, "none"
        age = age_hours(cached, now)
        if age is not None and age > FEAR_GREED_MAX_AGE_HOURS:
            return cached, "stale"
        return cached, "cached"


def _arrow(cur: float, prev: float | None) -> str:
    if prev is None:
        return "n/a"
    d = cur - prev
    return f"{'+' if d >= 0 else ''}{d:.0f}"


def render_line(fg: FearGreed | None, status: str, now: datetime | None = None) -> str:
    """The one-line regime header that sits ABOVE Block A (operator layout decision)."""
    if fg is None or status == "none":
        return "FEAR & GREED: unavailable (CNN fetch failed, no cached value)"

    parts = [f"FEAR & GREED: {fg.score:.0f} ({fg.rating})"]
    parts.append(f"1w {_arrow(fg.score, fg.week_ago)}")
    parts.append(f"1m {_arrow(fg.score, fg.month_ago)}")
    line = "  |  ".join(parts)

    if status in ("cached", "stale"):
        age = age_hours(fg, now)
        age_txt = f"{age:.0f}h old" if age is not None else "age unknown"
        line += f"   [CACHED — {age_txt}, CNN fetch failed]"
    return line
