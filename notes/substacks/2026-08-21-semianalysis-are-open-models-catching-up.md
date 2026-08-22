---
doc_type: substack_post
source: substack
publication: SemiAnalysis
publication_url: https://newsletter.semianalysis.com/
source_email: <20260821164002.3.d9bd8e29a6823462@mg-d1.substack.com>
source_sender: SemiAnalysis <semianalysis@substack.com>
source_url: https://open.substack.com/pub/semianalysis/p/are-open-models-catching-up
source_date: '2026-08-21'
subscription_tier: paid
tickers:
- GOOGL
- META
themes:
- model_commoditization
- frontier_model_competition
- foundation_model_economics
- ai_inference_margin_compression
- agent_framework_landscape
- ai_agent_monetization
ingestion_date: '2026-08-22'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Are Open Models Catching Up?](https://substack.com/app-link/post?publication_id=6349492&post_id=211750658&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMTc1MDY1OCwiaWF0IjoxNzg3MzMwNjA4LCJleHAiOjE3ODk5MjI2MDgsImlzcyI6InB1Yi02MzQ5NDkyIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.kdtavxoYxlBsjKA8jkmfqW40iz7NesWpifwW9E2ccWI)

### Comparing open vs. closed models across the eras of frontier models

The past two months have been a breakout period for open source AI. Yes, there was the “DeepSeek moment” back in January 2025, but no one actually used R1 to do any economically valuable work. In contrast, models like GLM 5.3 and Kimi K3 are genuinely capable of many of the same coding and agentic tasks that rocketed Anthropic to $65B+ ARR. Unlike others who inflated ARR, [our figures were much closer to reality.](https://substack.com/redirect/6c467ecc-40f5-4a14-9e7c-671cb1da3a1e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

It is an exciting time to be a token consumer. Competition is heating up, usage resets are being doled out, and the battle for your tokens now extends beyond the OpenAI-Anthropic duopoly. Fireworks alone is processing over [40T](https://substack.com/redirect/be1a27f0-b4ab-4eea-bf11-66ac8375203b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) tokens per day—2x the OpenAI API’s [volume](https://substack.com/redirect/c1a7ee16-5f9f-46c1-901e-321ac6a17811?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) at the end of March.

However, major FUD has also emerged as a result of open model success: if open models stay capable enough relative to the closed frontier at a fraction of the cost, won't the model layer become commoditized? This outcome would obviously be disastrous for frontier lab margins. For full details on Anthropic and OpenAI’s financials, see our[Tokenomics Model](https://substack.com/redirect/6c467ecc-40f5-4a14-9e7c-671cb1da3a1e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

To project how the open vs closed capability gap will progress in the future, we first need to measure the past. Naively, you might pick a single set of benchmarks to measure all historical models, but this is a mistake. Every benchmark is a product of a particular era. When someone creates a new benchmark, their goal is to discern differences in model capabilities at the time. If they’re successful, the model makers will climb said benchmark until it becomes saturated. Once that happens, everyone stops caring about the benchmark, and the cycle repeats.

There have been three eras thus far in the history of LLMs: early scaling, reasoning, and agentic. Each era represented a step-function increase in model utility, and rather than trying to plot a single continuous trend, we believe it’s better to evaluate the models and benchmarks from each era individually.

When viewed this way, it becomes clear that the open vs. closed gap moves in cycles. At the start of each era, a frontier lab completes some promising research, trains an impressive model, deploys it at scale to their users, and jumps ahead. Then, other labs identify the key advances, reverse-engineer what the frontier lab is doing, replicate them in their own models, and close the gap. Nothing stays secret forever—especially when you factor in distillation. It’s just a question of how long it takes.

To answer this question, we took all the relevant models from each era and ran a curated set of benchmarks to get a composite capability score. The result is a clear trend: with each generation, open-source models take half as long to catch up to the first closed-source model of the era.

Of course, benchmarks don’t tell the full story, and we’ll highlight all the relevant caveats below. Finally, we’ll extend this analysis into the future, and explain why it’s less bearish frontier models than you might initially think.

# How we measured

Here’s an overview of the models and benchmarks we selected for each era:

Picking a single SOTA closed and open model at a particular time is subjective, but our selections reflect the general consensus among AI experts. In cases where there’s debate—e.g. Fable 5 vs GPT 5.6 today—we were conservative and tested both.

For benchmarks, we relied on a combination of personal taste and popularity. Humanities Last Exam (HLE), for example, is known to have lots of [issues](https://substack.com/redirect/e3ccda1c-c0cf-4474-9a43-b37625a151b1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), but was also truly one of the defining benchmarks of the reasoning era with no close substitutes. SWE-bench Pro, on the other hand, is similarly popular and [problematic](https://substack.com/redirect/bcaa10af-f9ca-4283-acfe-38ac9f86b889?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), but also closely approximated by DeepSWE.

Most of the benchmark scores here we ran ourselves using [Prime Intellect](https://substack.com/redirect/3f75c136-e324-4c2a-b9ad-90c0fe3c314d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)'s evaluation stack, specifically their environments hub and the evals harness included in[Prime-RL](https://substack.com/redirect/90cc08cf-b946-4786-9e31-c9638bd44a14?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The rest come from runs by our friends at [Artificial Analysis](https://substack.com/redirect/449c770b-e6e6-4453-afb2-bfe2a4f709da?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and Datacurve's [DeepSWE leaderboard](https://substack.com/redirect/16fb847a-ae44-4baa-a0e9-936eff2affab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Open models were served the way they would have been at release: vLLM versions, hardware that was in use at the time, and sampling settings from the model card. For closed models, we ran against their pinned API versions. Where our numbers share a chart with third-party values, we matched their rulesets.

We’d like to give a huge thank you to Florian Brand ([@xeophon](https://substack.com/redirect/9f2585fd-106b-4b0c-9184-fd12da868065?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)) from Prime Intellect for helping us pick benchmarks/models, implement evals, and check for correctness.

# Era 1 | Early scaling (2022-2024)

It’s June 2023. The world is reckoning with ChatGPT, and Mark Zuckerberg just agreed to fight Elon Musk at the Colosseum. But while Zuck is training jiu-jitsu and doing Murphs, his company is doing some training of their own. FAIR is about to push past the Mistral exodus and other drama, and successfully ship Llama-2-70B. The first open model that approached the frontier.

How far behind the frontier was it? Four benchmarks helped define SOTA at the time: GSM8K, HumanEval, TriviaQA, and MMLU-Pro:

These benchmarks are representative of what the frontier models were capable of at the time. Simple multiple choice questions, word problems, and programming problems scoped to single functions. How times have changed! Here is how Llama-2 stacked up against GPT-3.5 Turbo in a cage match of their own:

To account for differences in benchmark difficulty, we normalized the scores. Each era’s best result is set to 100, and every other model is scored relative to that. The composite score represents the equal-weight average of the four: 75.7 for GPT-3.5 Turbo on the frontier, and 39.9 for Llama-2-70B. A measured, but considerable gap. This initial lag creates the storyline for the rest of the era: Mixtral-8x7B released in December 2023 created momentum towards GPT-4 capability, only to have GPT-4 Turbo and GPT-4o race ahead:

It took until the Llama-3.1-405B release in July 2024 for open models to close the GPT-3.5 Turbo gap, with a composite score of 86. The last frontier model, GPT-4o, was matched in capability by DeepSeek V3 in December 2024, scoring 95.5 and 94.1 respectively. Qwen2.5-72B landed within striking distance of GPT-4o at a sixth of the 405B parameter count, pre-trained on 18T tokens.

This is the first instance of the gap closing. Through this era, we didn’t see the frontier rise much beyond the capabilities of GPT-4, but this was mostly due to priorities: Turbo and 4o were built to make GPT-4 cheaper and faster, not smarter.

Meanwhile, OpenAI had been working towards a different kind of model. The [process-reward paper](https://substack.com/redirect/755d0b62-6a18-4c39-bc66-0617ffd0ada1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Noam Brown hire](https://substack.com/redirect/890e35bb-ad9c-42fc-a82e-3596e7e6e0c8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) both pointed at reasoning, and by mid-2024 [every major lab was publishing test-time-compute research](https://substack.com/redirect/4d89e70e-eaef-4774-bb35-85f65ddcf98b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Seven weeks after 405B, on September 12 2024, OpenAI shipped o1-preview: a model that sparked a new era of innovation.

# Era 2 | Reasoning (2024-2025)

o1 reset the choice of benchmarks, along with the gap. The elementary evals from Era 1 were no longer difficult enough to test o1’s full abilities. Grade school math problems were replaced by the AIME. Scale AI collected some of the most esoteric, PhD-level multiple choice questions in the world and provocatively called it Humanity’s Last Exam.

It’s hard to overstate how important the release of o1 was in tech circles. Many consider it the day “we knew for sure we’d get AGI.” However, unlike Llama-2-70B vs GPT-4, the gap between open vs closed source started off much smaller during Era 2. The culprit? A little known model called DeepSeek R1.

A 12.1 point gap vs 35.8 at the start of the previous era. The market puked in response. Fortunately, the AI capex trade quickly recovered, as people realized good models being open source is good for AI infrastructure. The "we're so back" open model momentum established by R1 was soon squashed by Meta's Llama-4 Maverick and other Chinese models.

Gemini 2.5 Pro and o3 continued to push the reasoning frontier, and the R1-0528 checkpoint closed the initial gap in May 2025 with a score of 78. An 8.5 month window to close a 12.1 point gap:

Notably absent from the charts so far is Anthropic. Their model cards reported these benchmarks like everyone else's, but they never fought for the top of the leaderboard in this era. While OpenAI and Google traded crowns, Anthropic was turning Claude into the default coding agent. This set the terms for the next era: the benchmarks that now matter run in a terminal.

# Era 3 | Agentic (2025 - Today)

Prior to Claude Code, agents had their moments (like Cognition’s [viral demo of Devin](https://substack.com/redirect/054fa19c-8c32-404a-91b0-09ca82de9ebc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in March 2024), but Anthropic was the first to nail a model + harness product—and it paid off. Since the general release of Claude Code in May 2025, Anthropic has added north of $65B in ARR. For in-depth Anthropic and OpenAI ARR projections, see our [Tokenomics Model](https://substack.com/redirect/6c467ecc-40f5-4a14-9e7c-671cb1da3a1e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

With agents came yet another new set of benchmarks. Fancy math problems were no longer the best test of model capabilities. Instead, people wanted to know how well models could write code, do web search, and generally use a computer like a human.

Terminal-Bench 2.1, BrowseComp-Plus, 𝜏³-banking, and DeepSWE cover the long-horizon work agents are used for today: software engineering, deep research, and knowledge work. We also picked benchmarks that skew newer by design to limit memorization.

Most AI experts consider Opus 4.5 the official start of the agentic era due to the reliability of the model. Interestingly, GPT-5.2 (OpenAI’s flagship at the time) performed better on our benchmark suite, but this didn’t correspond to a better user experience. The full agentic product (model + harness) was now what mattered, and Anthropic had been laser-focused on iterating towards a harness that excelled at general agentic work. Codex, in contrast, was comparatively crude, and OpenAI was simultaneously pursuing side quests like [web browsers](https://substack.com/redirect/0c7fc9fa-7e0b-4337-b74b-7e2db0bdcd0e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Model releases also compressed between the two frontier labs. OpenAI and Anthropic created their duopoly by releasing a model every 51 days on average throughout this era. Compared to the 213 and 120 day release averages throughout Era 1 and Era 2, respectively, this is a massive speed up.

Yet despite the massive explosion in economic value created by frontier models, the gap closed faster in Era 3 than either era before it. Kimi K2.6 surpassed Opus 4.5 with a score of 56.3 in 4.8 months, and GLM-5.2 cleared GPT-5.2 with a score of 72.4 in 6 months. The trend of the closing time halving with each subsequent era is remarkably consistent.

# Looking forward

So, what does this all mean for the future of closed vs open source models?

First, we want to acknowledge that benchmarks are not the end all be all. Kimi K3 may score higher than Fable 5 on our curated composite, but we still prefer using Fable at SemiAnalysis for our day to day work. This is partly because Anthropic has done a better job productizing their model via things like Claude Code and Claude Tag, but also largely because benchmarks aren’t a perfect proxy for real work. This is especially true for public benchmarks, which model makers can easily hill climb by simply creating a bunch of RL environments that closely mimic the benchmark tasks.

Second, you may argue that the closing time for Era 3 is artificially deflated due to Anthropic and OpenAI spending more time on safety testing than Moonshot and Zhipu, but this is not a new phenomenon. GPT-4, for example, finished training 218 days before release. Even if we assume Mythos finished training in mid February, that’s still only a 114 day delay before the Fable release.

## The Upcoming Era...

## Subscribe to SemiAnalysis to unlock the rest.

Become a paying subscriber of SemiAnalysis to get access to this post and other subscriber-only content.

### A subscription gets you:
