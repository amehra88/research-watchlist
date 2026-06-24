#!/bin/bash
# research-watchlist-sync.sh — Mac side of the Path A inbox channel.
#
# Runs every 15 min via launchd (com.amehra.research-watchlist-sync). Two jobs:
#   1. PUSH operator inbox submissions: stage anything new under notes/inbox/,
#      commit, push to origin/main — so the droplet's 15-min watcher can pick it up.
#   2. PULL the droplet's results: the same rebase brings back the {stem}.summary.md
#      files the droplet wrote, into Obsidian.
#
# SAFETY — the repo's cardinal rule is "Mac is pull-only" because a client pushing a
# stale/incomplete tree can overwrite production. We narrow the blast radius: this
# script `git add`s ONLY notes/inbox/, so the Mac can never push changes to any
# production file outside the inbox folder, no matter what Obsidian touches.
#
# Order is commit -> pull --rebase -> push: local inbox commits are replayed on top
# of whatever the droplet pushed in between, so the two directions never fight.
# Idempotent and silent on a no-op (nothing staged, nothing to pull).
set -euo pipefail

REPO="$HOME/research-watchlist"
LOG="$HOME/Library/Logs/research-watchlist-sync.log"
BRANCH="main"

mkdir -p "$(dirname "$LOG")"
ts() { date "+%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

cd "$REPO" || { log "ERROR: repo not found at $REPO"; exit 1; }

# Only operate on the expected branch.
cur="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
if [ "$cur" != "$BRANCH" ]; then
  log "ERROR: on branch '$cur', expected '$BRANCH' — skipping (no push from wrong branch)"
  exit 0
fi

# 1. Stage + commit ONLY inbox submissions (scoped blast radius).
git add notes/inbox/ 2>>"$LOG" || true
if ! git diff --cached --quiet; then
  files="$(git diff --cached --name-only | tr '\n' ' ')"
  git commit -q -m "inbox: operator submission $(ts)" 2>>"$LOG"
  log "COMMIT inbox: $files"
fi

# 2. Pull (rebase) — brings back droplet summaries; replays our inbox commit on top.
if git pull --rebase origin "$BRANCH" >>"$LOG" 2>&1; then
  :
else
  log "WARN: pull --rebase failed; aborting rebase, will retry next run"
  git rebase --abort >/dev/null 2>&1 || true
  exit 0
fi

# 3. Push if we are ahead of origin.
ahead="$(git rev-list --count origin/$BRANCH..HEAD 2>/dev/null || echo 0)"
if [ "$ahead" -gt 0 ]; then
  if git push origin "$BRANCH" >>"$LOG" 2>&1; then
    log "PUSH ok ($ahead commit(s))"
  else
    log "WARN: push failed (origin advanced?) — will retry next run"
  fi
fi

exit 0
