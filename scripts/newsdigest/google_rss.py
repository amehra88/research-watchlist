"""
google_rss — breadth channel (spec §1a).

Fetch Google News RSS for one ticker's query, parse to article dicts, strip the
trailing " - {source}" from titles, apply the recency window, drop denylisted
items, and cap the feed.

Article dict: {ticker, title, source, link, published(datetime, tz-aware UTC), tier}
stdlib only (urllib, xml.etree, email.utils).
"""
from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from . import FEED_CAP

_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
_UA = "Mozilla/5.0"


def _parse_pubdate(s: str) -> datetime | None:
    try:
        dt = parsedate_to_datetime(s)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _strip_source_suffix(title: str, source: str) -> str:
    if source and title.endswith(f" - {source}"):
        return title[: -(len(source) + 3)].strip()
    return title.strip()


def fetch(ticker, query, window_hours, now, classifier, timeout=20):
    """
    Return (articles, status).
      status: 'ok' (items parsed, feed reached) or 'error' (network/parse failure).
    Raises nothing — failure is reported via status so the run continues (§10).
    """
    url = _RSS.format(q=urllib.parse.quote(query))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        root = ET.fromstring(data)
    except Exception as e:  # noqa: BLE001 — per-ticker isolation, any failure degrades to 'error'
        return [], f"error: {type(e).__name__}: {e}"

    cutoff = now - timedelta(hours=window_hours)
    out = []
    for item in root.findall(".//item"):
        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        src_el = item.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        published = _parse_pubdate(item.findtext("pubDate") or "")

        if not raw_title:
            continue
        if published is not None and published < cutoff:
            continue
        title = _strip_source_suffix(raw_title, source)
        if classifier.is_denied(source, link, title):
            continue
        out.append({
            "ticker": ticker,
            "title": title,
            "source": source,
            "link": link,
            "published": published or now,
            "tier": classifier.classify(source),
        })

    # newest first, cap
    out.sort(key=lambda a: a["published"], reverse=True)
    return out[:FEED_CAP], "ok"
