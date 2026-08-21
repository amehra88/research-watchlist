#!/bin/bash
# Snapshot the droplet crontab into the repo so schedule changes are versioned.
#
# The crontab is production configuration for ~15 jobs but lives only on the droplet.
# Until 2026-08-21 the only record of a change was an ad-hoc /root/backups/crontab.pre_*
# file, so schedule edits left no audit trail and documentation silently drifted from
# reality (CLAUDE.md claimed the earnings reviewer ran at 06:30 for hours after it moved
# to 02:30). Snapshotting into the repo means auto_sync commits any change within 15
# minutes, and `git log config/crontab.snapshot` becomes the schedule history.
#
#   scripts/snapshot_crontab.sh          # write the snapshot
#   scripts/snapshot_crontab.sh --check  # exit 1 if live crontab differs from snapshot
#
# Restore:  crontab config/crontab.snapshot   (strip the header comment lines first)
set -u
REPO=/root/research-watchlist
OUT="$REPO/config/crontab.snapshot"

live=$(crontab -l 2>/dev/null)
if [ -z "$live" ]; then echo "refusing to snapshot an empty crontab" >&2; exit 2; fi

if [ "${1:-}" = "--check" ]; then
    diff <(grep -v '^# snapshot' "$OUT" 2>/dev/null) <(echo "$live") >/dev/null 2>&1 \
        && { echo "crontab matches snapshot"; exit 0; } \
        || { echo "crontab DIFFERS from snapshot"; exit 1; }
fi

{ echo "# snapshot of the live droplet crontab — written by scripts/snapshot_crontab.sh"
  echo "# snapshot taken: $(date -Is)"
  echo "$live"; } > "$OUT"
echo "wrote $OUT ($(echo "$live" | grep -cE '^[0-9*]') active jobs)"
