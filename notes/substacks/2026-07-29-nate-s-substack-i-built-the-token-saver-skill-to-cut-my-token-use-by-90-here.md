---
doc_type: substack_post
source: substack
publication: Nate's Substack
publication_url: https://natesnewsletter.substack.com/
source_email: <20260729130343.3.00a96160877a3add@mg-d0.substack.com>
source_sender: Nate from Nate’s Substack <natesnewsletter@substack.com>
source_url: https://open.substack.com/pub/natesnewsletter/p/reduce-ai-token-usage
source_date: '2026-07-29'
subscription_tier: free_plus_paid
tickers: []
themes:
- inference_compute_economics
- foundation_model_economics
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# I Built The Token Saver Skill To Cut My Token Use By 90%. Here Is What It Can
 And Cannot Do For You.

Get the full post and max your AI career leverage, plus connect with tens of thousands of paid subscribers in Nate’s Substack chat.

# [I Built The Token Saver Skill To Cut My Token Use By 90%. Here Is What It Can And Cannot Do For You.](https://substack.com/app-link/post?publication_id=1373231&post_id=208928045&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwODkyODA0NSwiaWF0IjoxNzg1MzM0MzI5LCJleHAiOjE3ODc5MjYzMjksImlzcyI6InB1Yi0xMzczMjMxIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.LKe2YiDj3rspW1tnnZ8eoNEnvdf8_hgPLZWjAm2E_Sw)

### My tracker logged 3.77 billion Codex tokens in one day. 95.73% of that input was reported as reused — material I never typed. So I went looking for what I could remove without making the work worse.

You’re hitting limits on a plan you already pay for, and you didn’t do anything unreasonable to get there. You asked a handful of questions. Somewhere around the tenth one, the meter started running much faster than you were.

I opened my Token Burn tracker after a long day in Codex and found 3.77 billion tokens. The split bothered me more than the total: of the 3.75 billion input tokens in the record, 3.59 billion were reported as reused input, or 95.73%.

My first reaction was to attack the 96%, but the number couldn’t tell me how.

It came from my own local event log, not an OpenAI bill. The log includes cumulative usage updates across 143 Codex threads and 28,877 local records. I treat 3.77 billion as a signal to investigate, not as a clean billable-token total.

“Reused” doesn’t mean “useless,” either. A difficult job may depend on the decision from twenty minutes ago, the file already changed, the error that ruled out the obvious fix, or the paragraph approved after four bad versions. Eligible repeated material may also receive a provider cache discount. Continuity is a large part of what makes these tools useful.

But continuity has a cost. A later request can contain much more than the new sentence I type. It may also carry earlier exchanges, standing instructions, tool definitions, files, screenshots, browser results, command output, rejected answers, and whatever state the product uses to continue the job.

The tenth message can be much larger than the first, even when the visible prompt is shorter. You typed less. You paid more.

I have argued before that [a token count is a trace, not a scoreboard](https://substack.com/redirect/4db45ea2-24a0-46c8-976a-5d1ed0deb41a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). I still believe it. A large day can mean an agent carried real work across files, browsers, drafts, and checks. Cutting the number without asking what the work produced is a bad way to manage AI.

The reused share raised a different question: how much of that material could still change the work, and how much remained because nothing in the system had a reason to let it go?

My target is aggressive: cut reported reused input by 90% without increasing mistakes, retries, review time, or work that has to be repeated.

Here’s what’s inside:

- The measurement. One real job run two ways, with the provider-reported numbers and what the comparison does and doesn’t prove.

- Fifteen changes, sorted by what actually backs them. Each one written out with the conditions where it helps, the conditions where it hurts, and whether I measured it or am still assuming.

- Nine you can use today. The habits that keep material out of a request in the products you already open. Nothing to install.

- The Token Saver skill. What it carries for you in Codex and Claude Code, the four changes it enforces, and the one boundary it can’t cross.

- What caching actually costs. The five-minute versus one-hour math, and why cached input never leaves your bill.

- What I still can’t prove. The limits of a single matched job, and the test that has to come next.

The percentage alone can’t tell me whether I have done that. I need a comparison.

## Watch with a 7-day free trial

Subscribe to Nate’s Substack to watch this video and get 7 days of free access to the full post archives.

### A subscription gets you:
