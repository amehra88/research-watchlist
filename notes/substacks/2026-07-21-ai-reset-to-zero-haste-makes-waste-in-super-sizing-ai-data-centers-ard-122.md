---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260721004009.3.cff53cc881aa628f@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/haste-makes-waste-in-super-sizing
source_date: '2026-07-21'
subscription_tier: free
tickers:
- META
- SPCX
themes:
- ai_infrastructure_capex
- datacenter_buildout_pacing
- data_center_deployment_constraints
- hyperscaler_capex_buildout
- foundation_model_economics
- inference_compute_economics
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Haste Makes Waste in Super-Sizing AI Data Centers. ARD #122](https://substack.com/app-link/post?publication_id=684161&post_id=207854194&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNzg1NDE5NCwiaWF0IjoxNzg0NTk0NDE2LCJleHAiOjE3ODcxODY0MTYsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.o_rF3S-frBan7IlCJhYpmG19qHd7X2qgHv02Blgsocs)

### ..Elon’s Memphis pushback becomes the epicenter of a nationwide data-center backlash, Oracle’s billions in cost+ surprise, & Meta’s ~$10B potential 'ZWS' Anthropic compute deal

Today’s theme: ‘haste makes waste’ in the ‘super-sizing’ of AI data centers so far in this [AI Tech Wave](https://substack.com/redirect/9ef0a8ff-9734-47e3-96be-e4638680296f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) — and the bill is starting to come due. Three events today — Elon’s Memphis pushback, the repercussions rippling nationwide, and the business-scaling challenges ahead — each with my Take, then my Overall Take. Plus a Gadget AI on how smart door locks are finally going hands-free with ease, and two questions. Let’s get started.

## (1) Sharp Lessons and Pushback in Memphis — Ground Zero for ‘Table Stakes’ AI Data Centers

MP TAKE: Elon’s building of Colossus 1 and 2 got early praise across Silicon Valley — including from Nvidia’s Jensen — and was emulated by Mark Zuckerberg’s Meta build-out around the country. Standing up 100,000-plus AI GPU data centers in months instead of years was, until recently, almost inconceivable; now the plans run to trillions of dollars at roughly $50 billion per data center. The industry solved the components, the GPUs, and the power. What it didn’t solve were the regulatory and community headwinds.

In hindsight, that ‘speed above all’ approach set a negative framework for how AI data centers treat the communities around them. Memphis neighborhoods bore real costs — pollution, noise, hundreds of families impacted — that could have been mitigated up front. The economic headroom to make those accommodations was there; the companies just didn’t make them early enough. Memphis became the lightning rod — and a more careful approach is now becoming the framework it should have been from the start. A lesson learned the hard way, and a cautionary one as SpaceX/xAI pushes its boundless ambitions further, including [into Pentagon AI compute](https://substack.com/redirect/060ce495-9ad2-4aab-b9e7-bc025529d6b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Sources, in narrative order: CNBC — [Elon Musk’s Memphis AI Empire Is the Epicenter of the Data Center Backlash](https://substack.com/redirect/d3493847-b7ed-4d72-a6e2-8b8b23c169bd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (and the [CNBC video on Elon in Memphis](https://substack.com/redirect/9e701807-e96b-4196-ae90-a9a36c984139?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)); WSJ — [SpaceX in Talks to Provide Computing Power for Pentagon’s AI Push](https://substack.com/redirect/060ce495-9ad2-4aab-b9e7-bc025529d6b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). For longtime readers: ‘Going to “Super-sized” 100,000++ AI GPU data centers’ in [AI-RTZ #551](https://substack.com/redirect/95cb37aa-eab0-49d2-895a-45c318a15967?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); ‘The “100,000 AI GPUs Table Stakes”’ in [AI-RTZ #477](https://substack.com/redirect/dcdc0284-5903-4eb0-b45f-68a471500c60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); ‘The new AI “Table Stakes”’ in [AI-RTZ #473](https://substack.com/redirect/fa66430f-37f5-4c1e-968a-f72908721a89?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); and ‘SpaceX/xAI IPO filing outlines Elon’s boundless AI Ambitions’ in [AI-RTZ #1066.](https://substack.com/redirect/2053c236-94d5-476c-801a-5239ff2509cd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) Repercussions Across the Country for All the AI Hyperscalers

MP TAKE: Memphis was the catalyst; the backlash is now national. Reuters counts 142 protests across 42 US states, and surveys show people are broadly against AI data centers — especially in their own neighborhoods. Meta, Microsoft, OpenAI and Anthropic are all facing it.

The Information puts a number on it, using Oracle — building for OpenAI and others across Texas and Arizona — as the example: a couple of data centers running $40-50 billion are now $5-10 billion higher after adjustments for pollution and behind-the-meter power (moving from natural gas toward fuel cells and more ecologically friendly sources). The payback math still works — even at $60 billion per gigawatt, roughly $15 billion-plus of revenue a year gives a four-to-five-year payback. But the soft costs — projects delayed by months or longer, and the fight for local goodwill — deserve much sharper consideration than the industry has given them.

Sources, in narrative order: Reuters — [Data Center Opponents Stage 142 Protests Across 42 US States](https://substack.com/redirect/7d7ef0f7-9950-4e18-800c-f67474830f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); The Information — [Oracle Data Centers Face Multibillion-Dollar Cost Surprises](https://substack.com/redirect/1f823d17-975c-492b-a44e-128d49d9edcb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). For longtime readers: ‘Power Plays begin to build Gigawatt AI Data Center’ in [AI-RTZ #481](https://substack.com/redirect/22102f5a-562d-4184-ae68-a4245785408a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); and ‘The AI Power Grab’ in [AI-RTZ #407.](https://substack.com/redirect/e4633be9-7024-4583-8376-43c432dccfbd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) The Economic Stakes of Building AI Data Centers on Uncertain Foundations

MP TAKE: The paybacks work today because we’re in a period of AI-compute scarcity driven by the exponential demand of the two frontier labs in particular. But the economics rest on a narrow foundation — it’s really the frontier model companies (the OpenAIs and Anthropics, with Google and others) that are the key anchor tenants. Recall Anthropic’s ~$40 billion multi-year deal and Google’s ~$30 billion around the SpaceX IPO — and now there are rumblings that Meta may bring Anthropic on as a tenant at ~$10 billion or more. Expandng his ‘Zuck Web Services’ effort, echoing Amazon AWS. The ‘rents’ these frontier labs pay run roughly two to three times the going market rate, and that’s what’s keeping the enthusiasm for these data centers going.

The broader question: will there be enough market appetite at these prices beyond the frontier labs — especially as cheaper, open-source AI alternatives arrive from both Chinese and US companies (the thread I wrote about all last week, and in Sunday’s piece)? SemiAnalysis (Dylan Patel’s team) lays out the ‘heads you win, tails you win’ economics of why everyone wants to be a ‘neocloud’ — and how tough these are to execute if Meta and the other hyperscalers can’t find alternative customers for excess capacity, or more uses for the compute with their own models. Economics resting on today’s scarcity are a shaky foundation for tomorrow’s demand.

Sources, in narrative order: SemiAnalysis — [Meta Compute: Everyone Wants to Be a Neocloud](https://substack.com/redirect/6236b308-5f45-4d2e-bf77-6f3f6f9ad256?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); NYTimes — [Meta in Talks to Lease Computing Power to Anthropic in Potential $10 Billion Deal](https://substack.com/redirect/ef822beb-b29f-425a-bdd9-fa031cc40bb0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). For longtime readers: ‘Meta and Zuck aiming for the AI Clouds’ in [AI-RTZ #1135](https://substack.com/redirect/30f3f931-be4c-41a0-9775-0f5b25fd27e5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); ‘Anthropic’s AI Compute Constraints throttling growth’ in [AI-RTZ #1086](https://substack.com/redirect/826f0775-b106-4cf2-a5cf-41f4d7c9a60d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); ‘Meta’s Amazon AWS size opportunity’ in [AI-RTZ #456](https://substack.com/redirect/2341f151-7c00-4f92-94dc-9ed2540a6ba8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); and ‘Government and Corporate AI Stakes get bigger’ in [ARD #89.](https://substack.com/redirect/c32f0212-6ef2-420b-8230-2cdd26bf29f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## MP OVERALL TAKE

All three narratives show how fast the state and local backlash has built up against the industry’s propensity to ‘build fast and break things.’ In this case, breaking things is adding costs in the billions and time in years. On the national side, the White House had been firmly on the side of the frontier AI companies and the hyperscalers — but the ground is shifting, especially with an election coming up. New York just became one of the first states to put a one-year moratorium on data centers, and states like New Jersey are considering the same. It’s becoming a political football.

In hindsight, the industry could have been more proactive — adding economics and settlements for local communities up front, especially where real estate and pollution were involved. The Memphis story is vivid and, in many ways, sad. But it’s a lesson some companies — Meta, Google and others — appear to be taking to heart, reaching out earlier to local and state authorities and communities. That’s a step in the right direction. This is a long journey, measured in years, with hundreds of billions still to invest — and we’re only at the beginning of the data-center pushback. The headroom to do it right is there; the companies just have to choose to use it.

# GADGET AI

## Smart Door Locks Finally Go Hands-Free — With Ease

### MP TAKE — Gadget AI (take-first, Ep 103+)

This category is a great example of how long it takes to get smart devices finally right. They always look easy on the surface, but execution at scale almost always takes longer than it seems — in both money and time. The Verge reviewed three or four of the latest smart locks and is finally celebrating that they’re hands-free with facial recognition that’s seamless, helped by new wireless standards and protocols that make them work with a lot less muss and fuss. They’re still expensive — and likely to get more so amid RAMageddon — but as prosaic an item as a door lock has taken over a decade to reach the point where The Verge can recommend not one but potentially four. It’s part of the broader thread I’ve tracked: the next big AI services will be in and around the home, arriving one hard-won category at a time.

Sources, in narrative order: The Verge — [Surprise! Facial Recognition Smart Locks Are Actually Good](https://substack.com/redirect/110d34ac-58a6-4157-bf27-6de6d5037cf8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). For longtime readers: ‘Next big AI services could be in and around the home’ in [AI-RTZ #865.](https://substack.com/redirect/7e17eecd-c6c5-4549-9f87-29a4df50f3d0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# QUESTIONS

## Q1 — What’s Michael’s experience with smart door locks?

Answer: Great — when they work. In a recent renovation my wife put in smart locks (I believe Google’s), and even without facial recognition we had fobs and programmable PIN codes, so people could come and go without changing locks. Generally convenient — but with plenty of teething problems: installation, power, and Wi-Fi issues all came with the package.

## Q2 — What’s Michael’s biggest issue with them to date?

Answer: You’re truly stuck when they don’t work — when the power goes out, the Wi-Fi drops, or the app just won’t connect. Then you’re scrounging around for those physical keys — and someone asks, “did you leave them inside?” Pardon the pun, but that’s the real doorstopper.

# WRAP

Today’s AI-RTZ #1153 — [China Ramping Up in AI vs the US, Open Source and Beyond](https://substack.com/redirect/ad717645-00a6-4580-a586-0d55be8f7efb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) — on China’s accelerating AI push against the US, in open source and beyond; a whole new issue I’ll have more to say about this week and next.

AI Ramblings Daily on AI-RTZ is here to think through AI and reset. Together.

Tomorrow — back with ARD 123 on AI-RTZ 1154.

Thanks for joining us today, AI Curious Folk. Stay tuned.

— MP

## Full Source Reading —

For the broader context, see the canonical sources for ARD 122 — in today’s narrative order:

### Event 1 — Sharp Lessons and Pushback in Memphis

- CNBC — [Elon Musk’s Memphis AI Empire Is the Epicenter of the Data Center Backlash](https://substack.com/redirect/d3493847-b7ed-4d72-a6e2-8b8b23c169bd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · CNBC (video) — [Elon Musk in Memphis](https://substack.com/redirect/9e701807-e96b-4196-ae90-a9a36c984139?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · WSJ — [SpaceX in Talks to Provide Computing Power for Pentagon’s AI Push](https://substack.com/redirect/060ce495-9ad2-4aab-b9e7-bc025529d6b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- AI-RTZ #551 — [Going to ‘Super-sized’ 100,000++ AI GPU data centers](https://substack.com/redirect/95cb37aa-eab0-49d2-895a-45c318a15967?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #477 — [The ‘100,000 AI GPUs Table Stakes’](https://substack.com/redirect/dcdc0284-5903-4eb0-b45f-68a471500c60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #473 — [The new AI ‘Table Stakes’](https://substack.com/redirect/fa66430f-37f5-4c1e-968a-f72908721a89?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #1066 — [SpaceX/xAI IPO filing outlines Elon’s boundless AI Ambitions](https://substack.com/redirect/2053c236-94d5-476c-801a-5239ff2509cd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Event 2 — Nationwide Repercussions for the Hyperscalers

- Reuters — [Data Center Opponents Stage 142 Protests Across 42 US States](https://substack.com/redirect/7d7ef0f7-9950-4e18-800c-f67474830f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · The Information — [Oracle Data Centers Face Multibillion-Dollar Cost Surprises](https://substack.com/redirect/1f823d17-975c-492b-a44e-128d49d9edcb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- AI-RTZ #481 — [Power Plays begin to build Gigawatt AI Data Center](https://substack.com/redirect/22102f5a-562d-4184-ae68-a4245785408a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #407 — [The AI Power Grab](https://substack.com/redirect/e4633be9-7024-4583-8376-43c432dccfbd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Event 3 — Economic Stakes on Uncertain Foundations

- SemiAnalysis — [Meta Compute: Everyone Wants to Be a Neocloud](https://substack.com/redirect/6236b308-5f45-4d2e-bf77-6f3f6f9ad256?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · NYTimes — [Meta in Talks to Lease Computing Power to Anthropic in Potential $10 Billion Deal](https://substack.com/redirect/ef822beb-b29f-425a-bdd9-fa031cc40bb0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- AI-RTZ #1135 — [Meta and Zuck aiming for the AI Clouds](https://substack.com/redirect/30f3f931-be4c-41a0-9775-0f5b25fd27e5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #1086 — [Anthropic’s AI Compute Constraints throttling growth](https://substack.com/redirect/826f0775-b106-4cf2-a5cf-41f4d7c9a60d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #456 — [Meta’s Amazon AWS size opportunity](https://substack.com/redirect/2341f151-7c00-4f92-94dc-9ed2540a6ba8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · ARD #89 — [Government and Corporate AI Stakes get bigger](https://substack.com/redirect/c32f0212-6ef2-420b-8230-2cdd26bf29f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI — Smart Door Locks Go Hands-Free

- The Verge — [Surprise! Facial Recognition Smart Locks Are Actually Good](https://substack.com/redirect/110d34ac-58a6-4157-bf27-6de6d5037cf8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · AI-RTZ #865 — [Next big AI services could be in and around the home](https://substack.com/redirect/7e17eecd-c6c5-4549-9f87-29a4df50f3d0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### Clip 1 — Elon Musk’s Memphis Data Center Backlash

[Watch on YouTube Shorts](https://substack.com/redirect/a6a53ced-d6d5-4531-82dc-2d44159ffa3a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Elon’s Colossus data centers stood up 100,000-plus AI GPUs in Memphis in months instead of years — praised by Silicon Valley and the markets. But CNBC reports the local backlash: pollution, noise, and hundreds of families impacted.

MP Take: In hindsight, that ‘speed above all’ approach set a negative framework for how AI data centers treat their communities. The economic headroom to mitigate those costs up front was there — the companies just didn’t take it early enough. Memphis became the cautionary tale, and a more careful approach is now becoming the framework it should have been from the start.

### Clip 2 — AI Data Centers Face Community Backlash

[Watch on YouTube Shorts](https://substack.com/redirect/35dbdb22-a3a5-4558-9b1c-82d15584bedd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

The data-center backlash has gone national — Reuters counts 142 protests across 42 US states. Meta, Microsoft, OpenAI and Anthropic are all facing it now.

MP Take: The Oracle example puts a number on it — mitigating community and regulatory resistance can add billions, pushing a $50 billion, one-gigawatt data center toward $60 billion-plus. The hard payback math still works, but the soft costs — projects delayed by months or longer, and the fight for local goodwill — deserve much sharper consideration than the industry has given them.

### Clip 3 — Data Centers: Economic Uncertainty Looms

[Watch on YouTube Shorts](https://substack.com/redirect/69d92150-5363-40ab-86bf-8f95a7092509?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Today’s AI data-center economics still pencil out — but on a narrow foundation. Meta is reportedly in talks to lease compute to Anthropic (~$10 billion); everyone wants to be a ‘neocloud.’

MP Take: The paybacks work because we’re in a period of AI-compute scarcity driven by the two frontier labs’ exponential demand. But the market will increasingly question the longer-term sustainability of those economics — especially as US tech leans into cheaper, open-source AI alternatives, from both Chinese and US companies. Build economics resting on today’s scarcity are a shaky foundation for tomorrow.

## About AI Ramblings Daily (ARD), and AI-RTZ

Both are daily. Both are free. Both are about AI. But they’re different mediums carrying different messages.

AI-RTZ is the morning text — a deeper written take on one idea, published by at least 5 AM EST. Today: post #1153.

AI Ramblings Daily is the afternoon video + podcast — my ad hoc takes and perspective on the day’s AI issues & news flow, around 20 minutes, with short 1-2 minute clips for quick topic views. Today: episode #122.

Subscribe to either or both on [michaelparekh.substack.com](https://substack.com/redirect/9601dfb5-240f-461e-a39c-4ed163142e0f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). They run as separate Sections you can opt into or out of.

## Links used in today’s show (already embedded inline above; listed here for reference)

Take 1 — Sharp Lessons and Pushback in Memphis:

- [CNBC — Elon Musk’s Memphis AI Empire Is the Epicenter of the Data Center Backlash](https://substack.com/redirect/d3493847-b7ed-4d72-a6e2-8b8b23c169bd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [CNBC (video) — Elon Musk in Memphis](https://substack.com/redirect/9e701807-e96b-4196-ae90-a9a36c984139?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [WSJ — SpaceX in Talks to Provide Computing Power for Pentagon’s AI Push](https://substack.com/redirect/060ce495-9ad2-4aab-b9e7-bc025529d6b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #551 — Going to ‘Super-sized’ 100,000++ AI GPU data centers](https://substack.com/redirect/95cb37aa-eab0-49d2-895a-45c318a15967?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #477 — The ‘100,000 AI GPUs Table Stakes’](https://substack.com/redirect/dcdc0284-5903-4eb0-b45f-68a471500c60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #473 — The new AI ‘Table Stakes’](https://substack.com/redirect/fa66430f-37f5-4c1e-968a-f72908721a89?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1066 — SpaceX/xAI IPO filing outlines Elon’s boundless AI Ambitions](https://substack.com/redirect/2053c236-94d5-476c-801a-5239ff2509cd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Take 2 — Nationwide Repercussions for the Hyperscalers:

- [Reuters — Data Center Opponents Stage 142 Protests Across 42 US States](https://substack.com/redirect/7d7ef0f7-9950-4e18-800c-f67474830f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Information — Oracle Data Centers Face Multibillion-Dollar Cost Surprises](https://substack.com/redirect/1f823d17-975c-492b-a44e-128d49d9edcb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #481 — Power Plays begin to build Gigawatt AI Data Center](https://substack.com/redirect/22102f5a-562d-4184-ae68-a4245785408a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #407 — The AI Power Grab](https://substack.com/redirect/e4633be9-7024-4583-8376-43c432dccfbd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Take 3 — Economic Stakes on Uncertain Foundations:

- [SemiAnalysis — Meta Compute: Everyone Wants to Be a Neocloud](https://substack.com/redirect/6236b308-5f45-4d2e-bf77-6f3f6f9ad256?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [NYTimes — Meta in Talks to Lease Computing Power to Anthropic in Potential $10 Billion Deal](https://substack.com/redirect/ef822beb-b29f-425a-bdd9-fa031cc40bb0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1135 — Meta and Zuck aiming for the AI Clouds](https://substack.com/redirect/30f3f931-be4c-41a0-9775-0f5b25fd27e5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1086 — Anthropic’s AI Compute Constraints throttling growth](https://substack.com/redirect/826f0775-b106-4cf2-a5cf-41f4d7c9a60d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #456 — Meta’s Amazon AWS size opportunity](https://substack.com/redirect/2341f151-7c00-4f92-94dc-9ed2540a6ba8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #89 — Government and Corporate AI Stakes get bigger](https://substack.com/redirect/c32f0212-6ef2-420b-8230-2cdd26bf29f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Gadget AI — Smart Door Locks Go Hands-Free:

- [The Verge — Surprise! Facial Recognition Smart Locks Are Actually Good](https://substack.com/redirect/110d34ac-58a6-4157-bf27-6de6d5037cf8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #865 — Next big AI services could be in and around the home](https://substack.com/redirect/7e17eecd-c6c5-4549-9f87-29a4df50f3d0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Companion text:

- [AI-RTZ #1153 — China Ramping Up in AI vs the US, Open Source and Beyond](https://substack.com/redirect/ad717645-00a6-4580-a586-0d55be8f7efb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/2ecfa729-ede4-418a-b8b8-0c07ef3d6da9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).)

Subscribe to AI: Reset to Zero for daily AI Ramblings + Sunday Bigger Picture posts.
