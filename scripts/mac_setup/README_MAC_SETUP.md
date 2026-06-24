# Mac setup — Path A Obsidian inbox channel

This wires your Mac into the inbox round-trip. After setup, the flow is **zero-action**:

1. In Obsidian, you drop a markdown file into `notes/inbox/` (with a `process:` frontmatter line).
2. A launchd agent on the Mac auto-pushes it to GitHub every 15 min — **you never `git push`**.
3. The droplet's watcher (also every 15 min) detects it, synthesizes a desk summary, and writes a sibling `{name}.summary.md`.
4. The same launchd agent pulls that summary back into Obsidian.

End-to-end: the summary appears next to your file in **~30–45 min**, no further action.

The two pieces in this folder:

| File | Role |
|------|------|
| `research-watchlist-sync.sh` | The sync script: commit inbox → pull --rebase → push. Lives in the repo (already on your Mac after a pull). |
| `com.amehra.research-watchlist-sync.plist` | The launchd agent that runs the script every 900s. |

> **Safety note.** The repo's cardinal rule is "Mac is pull-only" — a client pushing a stale tree can overwrite production. This script deliberately `git add`s **only `notes/inbox/`**, so it can never push changes to any production file outside the inbox folder. It is the one sanctioned exception to pull-only, scoped to a single folder.

---

## Prerequisites

- The repo is already cloned at **`~/research-watchlist`** (the existing `com.ashim.research-watchlist-pull` agent uses this path; do **not** use `~/Documents/research-watchlist` — TCC restrictions).
- You push to GitHub over **SSH** (`git@github.com:amehra88/research-watchlist.git`). Confirm:
  ```bash
  cd ~/research-watchlist && git remote -v
  ```
  If the remote is `https://…`, switch it to SSH:
  ```bash
  git remote set-url origin git@github.com:amehra88/research-watchlist.git
  ```

> **Coexistence with the existing pull agent.** If `com.ashim.research-watchlist-pull` is still loaded, it does a read-only `git pull --ff-only` every 15 min. This new sync agent already pulls, so the old pull agent is now redundant — you may leave it (harmless) or unload it (`launchctl unload ~/Library/LaunchAgents/com.ashim.research-watchlist-pull.plist`). Do **not** run two agents that both push.

---

## 1. Configure SSH so launchd can push unattended

launchd runs without your interactive shell, so the SSH key must be loadable from the keychain without a passphrase prompt.

Edit `~/.ssh/config` (create it if absent) and ensure a `github.com` block:

```sshconfig
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519       # <- your GitHub key
    UseKeychain yes
    AddKeysToAgent yes
```

Then **seed the keychain once, interactively**, so the passphrase is stored:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519   # enter passphrase once; macOS stores it
ssh -T git@github.com                            # should greet you by username
```

After this, launchd-spawned `git push` authenticates silently from the keychain.

---

## 2. Install the launchd agent

```bash
cd ~/research-watchlist/scripts/mac_setup

# Make the sync script executable (it's tracked in the repo).
chmod +x research-watchlist-sync.sh

# Fill the __HOME__ tokens in the plist with your real home dir, writing the
# final copy straight into LaunchAgents.
sed "s|__HOME__|$HOME|g" com.amehra.research-watchlist-sync.plist \
    > ~/Library/LaunchAgents/com.amehra.research-watchlist-sync.plist

# Load it (RunAtLoad fires the first sync immediately).
launchctl load ~/Library/LaunchAgents/com.amehra.research-watchlist-sync.plist
```

---

## 3. Verify

```bash
# Agent is registered (shows a PID or last exit code):
launchctl list | grep amehra

# Watch the sync log:
tail -f ~/Library/Logs/research-watchlist-sync.log

# Trigger an immediate run instead of waiting 15 min:
launchctl start com.amehra.research-watchlist-sync
```

A healthy run logs either nothing-to-do silence or lines like:
```
[2026-06-24 15:30:00] COMMIT inbox: notes/inbox/2026-06-24-some-note.md
[2026-06-24 15:30:03] PUSH ok (1 commit(s))
```

**End-to-end smoke test:** create `notes/inbox/2026-06-24-test.md` with:
```markdown
---
process: note
source: setup smoke test
---
Quick note on NVDA data center demand to verify the inbox round-trip.
```
Save it. Within ~15 min the Mac pushes it; within another ~15–30 min a
`2026-06-24-test.summary.md` appears beside it in Obsidian. Delete both when done.

---

## 4. Unload / disable

```bash
launchctl unload ~/Library/LaunchAgents/com.amehra.research-watchlist-sync.plist
# (optional) remove it:
rm ~/Library/LaunchAgents/com.amehra.research-watchlist-sync.plist
```

---

## Inbox file format (reference)

Drop files in `notes/inbox/` named like `YYYY-MM-DD-short-slug.md`:

```markdown
---
process: transcript | link | note      # required
source: <descriptor or URL>            # for process:link this is the URL
tickers: [NVDA, AVGO]                  # OPTIONAL — auto-extracted if omitted
themes:  [ai_infrastructure_capex]     # OPTIONAL — auto-extracted if omitted
---
<body: pasted transcript text, a URL (for process:link), or your notes>
```

- `process: transcript` — pasted earnings/conference transcript text.
- `process: link` — a URL; the droplet fetches and synthesizes the article.
- `process: note` — your own notes/observations.

The droplet writes `{name}.summary.md` beside it with sections: Summary, Key Data
Points, Tickers Mentioned, Themes, Cross-References, Surprises vs. Recent Guidance,
Actionable Implications, Source. Leave the `.summary.md` files in place — they are
the output; the processor skips any file that already has one.
