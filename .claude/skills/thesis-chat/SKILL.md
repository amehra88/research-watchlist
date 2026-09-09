---
name: thesis-chat
description: Weekly operator chat over the thesis loop — walks the open questions in state/thesis/questions.jsonl (drafts that got their first evidence, stale assumptions, pending score proposals), shows the evidence behind each, records the operator's decision via scripts/thesis/answer.py, and answers ad-hoc questions about any ticker's thesis from notes/{T}/_thesis.md + state/thesis/evidence_log.jsonl. Use when the operator says "thesis chat", "walk me through the thesis questions", "what changed on COHR's thesis", or after reading a Thesis delta email.
---

# Thesis chat

You are the operator's weekly thesis review partner. Everything you show comes from files; every
decision you record goes through `scripts/thesis/answer.py` (never edit `_thesis.md` by hand here,
and never touch `config/watchlist.yaml` — score changes go through `apply_scores.py --write`, which
only the operator triggers).

## Opening

1. `python3 scripts/thesis/answer.py --list` — the open questions, grouped by ticker.
2. Read the latest `notes/reports/thesis-delta-*.md` (most recent file) for context; mention the
   top three movers in one line each.
3. Ask which ticker to start with, or walk in file order if the operator says "go".

## Per question

- **draft_review** (`draft:{T}:{id}`): show the assumption statement, `derived_from`, `challenged_by`
  / `confirmed_by`, and the evidence rows for that assumption id from `state/thesis/evidence_log.jsonl`
  (filter `ticker`, `assumption_id`; show date, source, direction/strength, why, ref; newest first,
  at most 6). Offer: keep as written / edit the statement / retire / mark confirmed / mark challenged.
  Record with `--action keep|edit|retire|confirm|challenge` (`--text` for edit).
- **stale** (`stale:{T}:{id}`): show the statement and days since last evidence. Offer retire / keep.
- **score_proposal** (`score:{T}:{key}`): show proposed vs applied, the source note path, and the
  note's section 5/6/7 lines that carry the recommendation. Offer accept / reject. `accept` prints
  the `apply_scores.py` command; run it WITHOUT `--write` first, show the diff, and run `--write`
  only when the operator confirms in this conversation.

After each answer, echo the `answer.py` output line so the operator sees exactly what changed.

## Ad-hoc questions

"What is the thesis on X?" → read `notes/X/_thesis.md` (frontmatter + body) and summarize the
assumptions with their status, pressure and last evidence date. "What changed on X since <date>?" →
filter `state/thesis/changes.jsonl` and `evidence_log.jsonl` by ticker and date. "Why is X ranked
there?" → `state/thesis/ranking_{latest}.json` row for X (delta, why, proposed vs applied scores).

## Closing

Print the count answered / remaining. Remind the operator that `reviewed_by_operator: true` files
are never re-drafted by `draft_thesis.py --missing-only`, and that `--force` preserves anything
with `draft: false`.
