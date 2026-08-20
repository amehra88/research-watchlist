#!/usr/bin/env bash
# Quarterly AI application-layer screens (EDGAR full-text, all filers).
#
#   language screen -> companies whose FILINGS carry high-disclosure-cost AI language
#                      (quantified AI revenue, inference in COGS, proprietary training data)
#   officer screen  -> companies that NAMED a senior AI officer in an 8-K/proxy
#   mcp screen      -> companies making their corpus agent-addressable (MCP servers)
#
# Both write dated JSON next to this script, then diff against the previous run.
# The report is written to docs/ so it syncs to Obsidian with everything else.
#
# Framework for interpreting output: skills/ai-application-layer-screen/SKILL.md
# Worked analysis:                   docs/ai-application-layer-screen.md
#
# Cron (quarterly, 1st of Feb/May/Aug/Nov at 07:15 UTC):
#   15 7 1 2,5,8,11 * /root/bin/alert_on_failure.sh ai_screens /root/research-watchlist/scripts/screens/run_ai_screens.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
STAMP="$(date +%Y%m%d)"
REPORT="$REPO/docs/ai-screen-report-$STAMP.md"

export SCREEN_OUTDIR="$HERE"
export SCREEN_STAMP="$STAMP"

echo "[ai-screens] $STAMP starting" >&2

# EDGAR is rate-limited and occasionally 500s; the scripts retry internally.
python3 "$HERE/edgar_ai_language_screen.py"
python3 "$HERE/edgar_ai_officer_screen.py"
python3 "$HERE/edgar_mcp_screen.py"

{
  echo "# AI application-layer screen — $STAMP"
  echo
  echo "Automated quarterly run. **New entrants are the signal**: a filer newly using"
  echo "quantified-AI-revenue or proprietary-data language, newly naming a senior AI"
  echo "officer, or newly exposing its corpus via MCP has crossed a threshold that is"
  echo "expensive to fake."
  echo
  echo "Interpret with \`skills/ai-application-layer-screen/SKILL.md\` — in particular, apply the"
  echo "size filter and check for phrase collisions before treating any row as a candidate."
  echo "Rows marked *tracked* are already in \`config/watchlist.yaml\`."
  echo
  python3 "$HERE/cross_signal.py"
  echo
  python3 "$HERE/diff_screens.py" edgar_ai_language_screen
  echo
  python3 "$HERE/diff_screens.py" edgar_ai_officer_screen
  echo
  python3 "$HERE/diff_screens.py" edgar_mcp_screen
} > "$REPORT"

echo "[ai-screens] wrote $REPORT" >&2

# Keep the repo from accumulating unbounded run artifacts: retain the last 8 runs each.
for p in edgar_ai_language_screen edgar_ai_officer_screen edgar_mcp_screen; do
  ls -1t "$HERE/${p}"_*.json 2>/dev/null | tail -n +9 | xargs -r rm --
done

echo "[ai-screens] done" >&2
