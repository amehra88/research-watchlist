"""
email_send — plain-text digest delivery via Brevo (spec §7).

Self-contained mirror of /root/daily/combine_and_send.py's Brevo HTTP pattern
(no shared import). Sender = SMTP_USER, display name "News Digest", single
recipient per spec. Credentials from the environment (cron sources
/root/podcasts/.env before invoking).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

TO_ADDRESS = "amehra@baroncapitalgroup.com"   # spec §7: single recipient; mail rules handle forwarding
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send(subject: str, body: str, to_address: str = TO_ADDRESS) -> int:
    """Send the digest. Returns the HTTP status. Raises on misconfig / HTTP error."""
    sender = os.environ.get("SMTP_USER", "")
    api_key = os.environ.get("SMTP_PASSWORD", "")
    if not sender or not api_key:
        raise RuntimeError("SMTP_USER / SMTP_PASSWORD not set (source /root/podcasts/.env)")

    payload = json.dumps({
        "sender": {"name": "News Digest", "email": sender},
        "to": [{"email": to_address}],
        "subject": subject,
        "textContent": body,
    }).encode()

    req = urllib.request.Request(
        BREVO_API_URL,
        data=payload,
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status
