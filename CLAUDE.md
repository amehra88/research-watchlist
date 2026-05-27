# Financial Services Plugins

Cowork plugins and Claude Managed Agent templates for financial services. Each named agent ships two ways from one source.

## Repository Structure

```
├── plugins/
│   ├── agent-plugins/               #   named agents — one self-contained plugin each
│   │   └── <slug>/
│   │       ├── .claude-plugin/plugin.json
│   │       ├── agents/<slug>.md     #   ← canonical system prompt (one source, two wrappers)
│   │       └── skills/              #   ← bundled copies, synced from vertical-plugins/
│   ├── vertical-plugins/            #   FSI verticals — skill sources, commands, MCPs
│   │   └── <vertical>/
│   │       ├── .claude-plugin/plugin.json
│   │       ├── commands/
│   │       ├── skills/
│   │       └── .mcp.json
│   └── partner-built/               #   partner plugins (LSEG, S&P Global)
├── managed-agent-cookbooks/         # CMA cookbooks (one dir per named agent)
│   └── <slug>/
│       ├── agent.yaml               #   system + skills → ../../plugins/agent-plugins/<slug>/...
│       ├── subagents/*.yaml         #   depth-1 leaf workers
│       ├── steering-examples.json
│       └── README.md                #   security tier + handoff notes
├── claude-for-msft-365-install/     # admin tooling for the Microsoft 365 add-in (separate from FSI plugins)
└── scripts/                         # deploy-managed-agent.sh, check.py, validate.py, orchestrate.py, sync-agent-skills.py
```

Run `python3 scripts/check.py` before committing — it lints every manifest, verifies all `system.file` / `skills.path` / `callable_agents.manifest` references resolve, and fails if any `agent-plugins/<slug>/skills/` copy has drifted from its `vertical-plugins/` source. **Edit skills in `vertical-plugins/`**, then run `python3 scripts/sync-agent-skills.py` to propagate into the agent bundles.

## Key Files

- `marketplace.json`: Marketplace manifest - registers all plugins with source paths
- `plugin.json`: Plugin metadata - name, description, version, and component discovery settings
- `commands/*.md`: Slash commands invoked as `/plugin:command-name`
- `skills/*/SKILL.md`: Detailed knowledge and workflows for specific tasks
- `*.local.md`: User-specific configuration (gitignored)
- `mcp-categories.json`: Canonical MCP category definitions shared across plugins

## Development Workflow

1. Edit markdown files directly - changes take effect immediately
2. Test commands with `/plugin:command-name` syntax
3. Skills are invoked automatically when their trigger conditions match


## Research Intelligence System

Beyond the FSI plugin templates above, this repo is also Ashim Mehra's working research intelligence system covering ~150 tech tickers for the BCTK ETF (Baron Capital Technology). Files outside `plugins/`, `managed-agent-cookbooks/`, `claude-for-msft-365-install/`, and `scripts/` belong to this system.

### Purpose and scope

Watchlist: 147 tickers in `config/watchlist.yaml`, tiered T1 (BCTK, 41 tickers), T2 (17), T3 (89). Supply chain map: `config/supply-chain.yaml` (146/147 coverage, FactSet-extracted) plus `config/supply-chain-manual.yaml` for overrides.

Three analytical dimensions tracked per ticker: competitive position, product cadence, revenue growth and margins. Synthesized in ticker-level notes at `notes/{TICKER}/`.

### File layout (research side)

- `notes/{TICKER}/{YYYYMMDD}-{quarter}.md` — earnings transcript synthesis (e.g., `notes/GOOGL/20260429-1Q26.md`)
- `notes/{TICKER}/{YYYYMMDD}-conf-{shortname}.md` — conference transcript synthesis
- `notes/{TICKER}/synthesis-{YYYYMMDD-HHMMSS}.md` — ticker-level synthesis runs
- `raw-transcripts/` — incoming PDF transcripts (lives in sibling `/root/research` repo); moved to `raw-transcripts/processed/` after wrapper runs
- `raw-web/` — Web Clipper destination from Mac browser
- `state/` — cron state files (last-poll timestamps, dedup ledgers)
- `logs/` — cron output and operational logs (contents gitignored, directory tracked via .gitkeep)

### Sync architecture

**The droplet at `/root/research-watchlist` is canonical.** GitHub (`amehra88/research-watchlist`, private) is the sync hub. Mac and iPad are read-only clones.

- **Droplet → GitHub**: `scripts/auto_sync.py` runs every 15 min via cron; commits and pushes any uncommitted changes
- **GitHub → Mac**: launchd job at `~/Library/LaunchAgents/com.ashim.research-watchlist-pull.plist` pulls every 15 min (`--ff-only`) into `~/research-watchlist` (NOT `~/Documents/research-watchlist` — TCC restriction)
- **GitHub → iPad**: Obsidian Git plugin (when re-set up; auto-push and auto-backup MUST be disabled to prevent damage)

**Cardinal rule: Mac and iPad do NOT push.** They are pull-only by design. Pushing from a client with a stale or incomplete working tree (which is what isomorphic-git on iOS can produce) overwrites production files. See Recovery Procedure below.

### Agents (production)

- `.claude/agents/earnings-reviewer.md` — production agent invoked by cron at 6:30am ET daily via `scripts/cron_earnings_reviewer.py`; processes prior-day earnings transcripts via InsiderScore + FactSet MCPs
- `.claude/agents/earnings-reviewer-from-pdf.md` — same logic for operator-uploaded PDFs, wrapped by `/root/research/scripts/process_uploaded_transcript.py` (sibling repo)
- `plugins/agent-plugins/ticker-synthesis/agents/ticker-synthesis.md` — synthesizes a ticker's three dimensions from notes/, watchlist, supply chain (Phase 2 sources stubbed)
- `.claude/agents/market-researcher.md` — general market research helper

### MCP servers and permission patterns

Connected MCP servers (configured in claude.ai workspace):

- `FactSet AI-Ready Data` → permission pattern: `mcp__claude_ai_FactSet_AI-Ready_Data__*`
- `InsiderScore` → `mcp__claude_ai_InsiderScore__*`
- `Gmail` → `mcp__claude_ai_Gmail__*`

Name transformation: spaces and dots become underscores; hyphens preserved. Use these patterns in `.claude/settings.local.json` allowlists and in `--allowedTools` flags for cron wrappers. See `scripts/cron_earnings_reviewer.py` for the canonical `ALLOWED_TOOLS` constant.

### Gitignore conventions

Never commit:
- `logs/*.log` — cron output (directory tracked via .gitkeep)
- `tmp/`, `.claude/settings.local.json` — local working state
- `.obsidian/workspace*.json`, `.obsidian/plugins/`, `.obsidian/community-plugins.json`, `.obsidian/graph.json`, `.obsidian/cache` — per-device Obsidian state; iPad's Obsidian Git plugin will auto-commit these if not gitignored
- `Untitled*.md`, `Untitled*.canvas`, `Untitled*.base` — accidental Obsidian-client creations

PATs and secrets never go in committed files. If a PAT ever pushes (e.g., via `.obsidian/plugins/obsidian-git/data.json`), revoke on GitHub immediately — even after force-pushing it out, the token persists in dangling commits for ~90 days.

### Recovery procedure (if a client damages the repo)

Symptom: `auto_sync.py` cron alerts with exit 127 (file not found) or production scripts show unexpected modifications. Diagnosis steps:

    # On droplet, identify damage:
    cd /root/research-watchlist
    git fetch origin
    git log --oneline -10                            # spot "vault backup" or other suspicious commits
    git diff --name-status <last-good-commit>..HEAD  # see what was deleted/modified

If damage is widespread, hard-reset and force-push:

    git show HEAD:.gitignore > /tmp/saved-gitignore  # save any deliberate changes
    git reset --hard <last-good-commit>
    cp /tmp/saved-gitignore .gitignore
    git add .gitignore && git commit -m "Recovery: reset after client damage"
    git push --force-with-lease origin main

Then sync Mac to the rewritten origin:

    cd ~/research-watchlist
    git fetch origin && git reset --hard origin/main

If the offending client was iPad's Obsidian Git plugin, disable **Auto backup interval** and **Auto push interval** in plugin settings before re-setting up — iPad must be pull-only.

### Operating rules

- All production crons are wrapped by `/root/bin/alert_on_failure.sh` which sends Brevo SMTP alerts on non-zero exit
- `auto_sync.py` does `git pull --rebase` before push, so it tolerates other commits arriving on origin between cron cycles
- Don't run `git push` from Mac or iPad as a routine action (this commit is a deliberate exception)
- When debugging, check `logs/auto-sync.log` and `logs/earnings-reviewer.log` first
