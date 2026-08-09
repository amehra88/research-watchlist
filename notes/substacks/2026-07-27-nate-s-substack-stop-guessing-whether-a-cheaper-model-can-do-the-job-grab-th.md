---
doc_type: substack_post
source: substack
publication: Nate's Substack
publication_url: https://natesnewsletter.substack.com/
source_email: <20260727130056.3.f16e502701557635@mg2.substack.com>
source_sender: Nate from Nate’s Substack <natesnewsletter@substack.com>
source_url: https://open.substack.com/pub/natesnewsletter/p/chinese-ai-models-test
source_date: '2026-07-27'
subscription_tier: free_plus_paid
tickers: []
themes:
- frontier_model_competition
- model_commoditization
- foundation_model_economics
- model_efficiency_evolution
- agent_framework_landscape
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Stop guessing whether a cheaper model can do the job. Grab the bakeoff guide: the validator, the manifest, the sco…

Get the full post and max your AI career leverage, plus connect with tens of thousands of paid subscribers in Nate’s Substack chat.

# [Stop guessing whether a cheaper model can do the job. Grab the bakeoff guide: the validator, the manifest, the score sheet, and the fixtures.](https://substack.com/app-link/post?publication_id=1373231&post_id=208510556&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwODUxMDU1NiwiaWF0IjoxNzg1MTYxNDAzLCJleHAiOjE3ODc3NTM0MDMsImlzcyI6InB1Yi0xMzczMjMxIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.ezi7qI4JKRrAPLISY6-_YrRGYppVLM-1g6bZVGurRhs)

### The test I use for Qwen, GLM, DeepSeek, Kimi, and MiniMax—and the work I still keep on frontier models.

Someone on your team wants to move a workload onto a Chinese model because it costs a fifth as much. Someone else says absolutely not. Both of them are arguing about a country. What actually decides it is a job, an endpoint, and a check. I have run these models inside a live multi-agent system, and I can tell you which of those arguments survives contact with real work. I will also tell you where my own records are incomplete, because I am not going to blur separate experiments together so the headline sounds cleaner.

The Chinese-model conversation has a bad habit. One good answer from DeepSeek, Qwen, GLM, Kimi, or MiniMax, and suddenly the American frontier has been caught. One censorship failure or bad citation, and the whole Chinese stack is declared unusable. Neither tells me whether I should put the model on a real job.

My answer up front is yes: serious AI users should test Chinese models. I use them selectively—aggressively in some workflows—but the job, the model, and the deployment path are separate decisions.

While I was building [Ringer](https://substack.com/redirect/864d31d3-fff7-4fc7-bf4d-63e88e5647ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), I tried Qwen as one of the workers, and it was useful. I do not have a complete log of the exact Qwen checkpoint, task mix, pass rate, and cost from that experiment. The 34-task Ringer run where I have the full logs used GLM-5.2, GPT-5.5, Grok 4.5, and Composer 2.5 Fast, with the last two running through the Grok Build CLI.

In the video, I promised to show the test. Here’s what’s inside:

- The [Ringer](https://substack.com/redirect/864d31d3-fff7-4fc7-bf4d-63e88e5647ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) run that changed how I place models. A 34-task job where one worker reported 213 verified quotations and 13 of them turned out to be stitched together.

- What an accepted result actually costs. The number that replaces token price, and why a cheaper model can double your review time.

- Where I’d start with each family. DeepSeek, Qwen, GLM, Kimi, and MiniMax, with the specific failure to watch on each one.

- The bakeoff kit. A validator, a manifest, a score sheet, and the two fixtures you use to prove your checker actually rejects bad work.

The run that taught me all of this cost about $8 USD. Let’s start there.

## Watch with a 7-day free trial

Subscribe to Nate’s Substack to watch this video and get 7 days of free access to the full post archives.

### A subscription gets you:
