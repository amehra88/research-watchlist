#!/bin/bash
# P5b weekday chain (2026-09-11): earnings-call pull -> topic_map -> diffusion -> stage alert.
# Sequential on purpose: diffusion refuses a map older than its inputs, so the steps must not
# race on timed cron lines. mdna_evidence runs at 12:30 on its own line; this starts at 12:45.
# Each step pages on failure via alert_on_failure.sh but the chain continues: a failed pull
# must not block an MD&A-driven alert, and diffusion's staleness guard protects itself.
set -u
cd /root/research-watchlist || exit 1
set -a; . /root/podcasts/.env; set +a
A=/root/bin/alert_on_failure.sh
$A transcript_earnings python3 scripts/v3_ingest/transcript_ingest.py --earnings 3 >> logs/transcript_ingest_earnings.log 2>&1
$A topic_map_daily     python3 scripts/topics/topic_map.py --run                    >> logs/topic_map.log 2>&1
$A diffusion_daily     python3 scripts/topics/diffusion.py --run                    >> logs/diffusion.log 2>&1
$A stage_alert         python3 scripts/topics/stage_alert.py --run --email          >> logs/stage_alert.log 2>&1
