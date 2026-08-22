---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260821050325.3.6a3462b3d24d46a0@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-global-state-of-open-source
source_date: '2026-08-21'
subscription_tier: free
tickers:
- AMD
- NVDA
- META
- BABA
themes:
- model_commoditization
- frontier_model_competition
- model_efficiency_evolution
- china_ai_infrastructure_demand
- china_us_tensions
- silicon_architecture_competition
- foundation_model_economics
ingestion_date: '2026-08-22'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: The Global State of Open Source AI Models (part 2). AI-RTZ #1185](https://substack.com/app-link/post?publication_id=684161&post_id=211385616&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMTM4NTYxNiwiaWF0IjoxNzg3Mjg4ODIwLCJleHAiOjE3ODk4ODA4MjAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.H-q6JdRJCwjdBpByL37pAqzKFMCmp0HFC8zaMyy7Z7Q)

### ...Hugging Face’s census of open AI: five findings, five charts, and my takes. The zoom-out after yesterday’s China zoom-in.

[Yesterday’s part 1 was the ‘zoom-in’ close-up: China’s week in downloads and valuations.](https://substack.com/redirect/6c18da99-b345-4741-a9d4-87b47fde0c69?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)Today, the zoom-out for this [AI Tech Wave](https://substack.com/redirect/3a18db73-5a8e-455a-95be-d85483ec39ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) globally: the full picture of open source AI worldwide, through Hugging Face’s biannual [State of Open Models report](https://substack.com/redirect/1906b981-7af9-430e-ac51-c403f558a231?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), published this week. It is a noteworthy overview of the open AI ecosystem the world over with reasonable proxies for AI ‘census’ data. And its charts and graphs reward a slow walk. Here are the five findings that matter most, with my takes on each.

First, the shape of the ecosystem itself. The Hugging Face hub grew from 2.43 to 2.96 million public model repositories between January and August, with datasets crossing a million. But the distribution underneath is extreme: 85.6% of models have fewer than 200 lifetime downloads, and 1.5% of repositories account for 99.2% of all downloads.

My take: open source AI is a hits business, more concentrated than music or venture returns. That is precisely why ‘default workflow’ status, the thing Alibaba Qwen just won in part 1, is the whole game: in a 99.2/1.5 world, distribution compounds and the long tail is a rounding error.

Second, the parameter ceilings. In almost every month of 2026, the largest open model from a Chinese lab was bigger than anything American labs released. China’s monthly ceiling ran between 754 billion and 2.78 trillion parameters. America’s stayed under 130 billion in five of seven months, the exceptions being Nvidia’s Nemotron 3 Ultra at 561 billion and Thinking Machines’ Inkling. I [wrote about them](https://substack.com/redirect/ddb0e294-9771-43c0-b6f1-0ff9605804be?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and Nvidia recently.

My take: the report’s own framing is the right one: size is now a statement of intent, not capability. Two camps have formed. [China’s](https://substack.com/redirect/eb5f17e9-cef0-417f-8209-c256e223c657?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) Moonshot, MiniMax, Xiaomi and Z.ai publish almost nothing below 70 billion parameters, staking everything on benchmark position. Alibaba and Tencent cover the whole range, from under 1 billion up, bidding to be the family developers standardize on. Different prizes, both rational. And the community’s quantization layer, which makes giant models runnable within days, quietly referees the whole contest.

Third, the most surprising finding: America’s top open source publishers are now its chipmakers. AMD and Nvidia each released more than 200 new model repositories this year, far ahead of everyone else, with Google and Meta ranking well below. As the report puts it:

> “Hardware vendors have realized that open models are a way to sell chips: a model optimized for your hardware and freely available is the clearest proof that the hardware works.”

My take: this is the [Nvidia kingmaker thesis](https://substack.com/redirect/e59f1f9d-ed7b-4d6f-86ca-1329dee4e5fd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) confirmed from primary data, and it marks a structural handoff: open source AI has moved from the model labs to the hardware and infrastructure companies. Meta, which defined open model publishing for years, has drifted toward closed flagships, a shift we covered in [‘Open Source AI: Rockets Are Hard’](https://substack.com/redirect/fae97cce-8655-4014-970e-e430172c0627?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The US is still fully present in open source. It just moved down the stack, closer to the silicon.

Fourth, the interleaving nobody talks about. Most US model releases above 100 billion parameters this year are not new models: they are built on top of Chinese open models. The short list of original American entries at that scale: Thinking Machines’ Inkling at 952 billion, Nvidia’s Nemotron 3 Ultra and Super, and Arcee’s Trinity-Large. Meanwhile AMD’s conversion work makes trillion-parameter Chinese models run efficiently on American hardware, and Chinese models are increasingly optimized for domestic chips, the same competition in reverse.

My take: this is the strongest anti-‘US/China race’ datapoint in the report. The stack is interleaving, not decoupling: American silicon running Chinese weights, Chinese fabs like the CXMT story from [part 1](https://substack.com/redirect/62335864-70ae-4a56-ae10-350b7d4d2a0c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) racing to serve domestic models, and developers everywhere fine-tuning whatever runs best. As I argued on [America’s 250th July 4th](https://substack.com/redirect/0854d20b-4942-42dc-85c4-d272331ec5b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a race needs separable lanes. There are none here.

Fifth, attention is not adoption. Hugging Face compared the top 25 model repositories by downloads with the top 25 by likes. Exactly one repository appears on both lists.

My take: ‘likes’ are marketing, downloads are production. The models that trend on launch day are almost never the ones quietly doing the world’s work a quarter later. It is the same lesson as the valuation twist in part 1: the loud signal and the load-bearing signal are different signals. Measure what runs.

The zoom-out, in one paragraph: open source AI is now global infrastructure, with China supplying the gravitational mass of models, America supplying the silicon and the optimization layers, and a concentrated handful of model families carrying nearly all the traffic.

The watch list from here: whether Meta’s closed turn holds, the AMD and Nvidia publishing cadence, Qwen’s derivative ecosystem compounding, and the domestic-chip optimization loop in China. None of that is a lap time either. The pie expands, and this report is the census of it doing so.

An impact of open source/weight AI the world over. This [AI Tech Wave](https://substack.com/redirect/3a18db73-5a8e-455a-95be-d85483ec39ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is just beginning. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
