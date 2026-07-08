#!/usr/bin/env python3
"""Daily canary for claude -p subscription-auth health (Option 1: manual /login model).

Reads the Claude Code OAuth *refresh-token* expiry from ~/.claude/.credentials.json and
exits NON-ZERO (so /root/bin/alert_on_failure.sh emails the operator) when auth is within
WARN_DAYS of lapsing OR has already lapsed. When the refresh token expires, headless cron
cannot renew it (no interactive browser), so every `claude -p` call across the v3 channels
(podcasts, substacks, inbox theme-extraction + synthesis) silently fails until a human runs
`claude` + /login on the droplet. This canary is what makes the manual-/login strategy
viable: it turns "hope you remember" into "get warned ~7 days ahead".

  cron: 30 10 * * *   (06:30 ET / 10:30 UTC — droplet cron runs in UTC) via
        /root/bin/alert_on_failure.sh claude_auth_canary python3 \\
        scripts/v3_ingest/claude_auth_canary.py

FIX WHEN ALERTED: SSH to droplet -> run `claude` -> /login -> complete OAuth in browser.
Renews the refresh token for ~28 days. See memory: claude_p_oauth_expiry_hygiene.

Note: this catches the predictable ~28-day refresh-token lapse (the known failure mode).
An *unexpected* auth break (revocation, server-side change) that leaves the expiry field
looking valid is caught instead by the channels' own all-fail non-zero exit (belt & braces).
"""
import datetime as dt
import json
import sys
from pathlib import Path

CREDS = Path.home() / ".claude" / ".credentials.json"
WARN_DAYS = 7


def main() -> int:
    now = dt.datetime.now(dt.UTC)
    if not CREDS.exists():
        print(f"CANARY CRITICAL: {CREDS} missing — claude -p subscription auth cannot work.")
        return 1
    try:
        oauth = (json.loads(CREDS.read_text()).get("claudeAiOauth") or {})
        rt_ms = oauth.get("refreshTokenExpiresAt")
    except Exception as e:  # noqa: BLE001
        print(f"CANARY CRITICAL: cannot parse {CREDS}: {type(e).__name__}: {e}")
        return 1
    if not rt_ms:
        print("CANARY CRITICAL: no refreshTokenExpiresAt in credentials — cannot verify auth.")
        return 1

    expiry = dt.datetime.fromtimestamp(rt_ms / 1000, dt.UTC)
    days = (expiry - now).total_seconds() / 86400.0
    stamp = expiry.isoformat()

    if days <= 0:
        print(f"CANARY CRITICAL: claude -p subscription auth EXPIRED {stamp} "
              f"({-days:.1f}d ago). All claude -p channels (podcasts/substacks/inbox) are DOWN "
              f"until re-login. SSH to droplet -> `claude` -> /login.")
        return 1
    if days <= WARN_DAYS:
        print(f"CANARY WARNING: claude -p subscription auth expires {stamp} (in {days:.1f}d). "
              f"SSH to droplet -> `claude` -> /login before then to avoid a silent outage "
              f"across podcasts/substacks/inbox.")
        return 1

    print(f"CANARY OK: claude -p subscription auth valid until {stamp} ({days:.1f}d left).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
