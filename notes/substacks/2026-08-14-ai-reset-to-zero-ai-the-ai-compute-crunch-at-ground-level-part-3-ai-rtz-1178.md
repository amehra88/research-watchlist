---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260814050324.3.55633b6a86488944@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-ai-compute-crunch-at-ground
source_date: '2026-08-14'
subscription_tier: free
tickers:
- NVDA
- CRWV
- NBIS
- SPCX
- AMZN
- GOOG
themes:
- ai_infrastructure_capex
- inference_compute_economics
- hyperscaler_capex_buildout
- datacenter_buildout_pacing
- ai_compute_topology
- foundation_model_economics
ingestion_date: '2026-08-15'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: The AI Compute Crunch at Ground Level (part 3). AI-RTZ #1178](https://substack.com/app-link/post?publication_id=684161&post_id=211047592&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMTA0NzU5MiwiaWF0IjoxNzg2NjgzOTczLCJleHAiOjE3ODkyNzU5NzMsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.8iemx7g68K9V7qFLNYzF6e7tWk8SuIGREdYZfgJWpuQ)

### ...Nvidia’s 2022 H100 rents up 50%, Neoclouds CoreWeave & Nebius cash in, & AI startups squeezed near-term.

This Sunday and Monday I went up to the macro level on the AI Compute buildout in a 2 part series: [Elon’s mega AI data center supply ambitions (part 1)](https://substack.com/redirect/be6bcb80-291b-4037-9f53-442c30542d67?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on Sunday, and [the ‘Dwarkesh’ Compute Demand bull case (part 2)](https://substack.com/redirect/9652d810-8a5b-405a-bc17-97f2ee9fc393?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on Monday. Today, a part 3 at the tactical, ground level: what the AI Compute crunch actually looks like this month if you’re a young AI startup trying to buy [Nvidia](https://substack.com/redirect/221b32ab-3f41-49fe-8a15-6a33aba37ab9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) et al AI compute, or a [neocloud](https://substack.com/redirect/80e0aad8-fac6-455f-92c7-bb4e8b7d4b0b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) selling it.

The short version: prices for AI training and inference compute are being bid UP in the near term, with the squeeze falling hardest on young AI startups, while big tech incumbents and the neoclouds selling capacity are cashing in. And of course Nvidia as well, whose chips from 2022 and later are seeing rental price bumps at the [cloud and neocloud](https://substack.com/redirect/40ef390d-6828-4c7d-88bd-dd741513be19?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) companies.

The Information lays out the ground truth in [“Why The AI Compute Crunch Is Hitting Neolabs Especially Hard”](https://substack.com/redirect/7e84612d-c9ac-4532-b6ef-fdb2459dca43?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

> “The AI chip shortage is causing headaches for tech giants such as OpenAI. Among those hardest hit, though, are the startups trying to build their own AI models, so-called neolabs that need to use their limited funding to secure access to enormous clusters of graphics processing units for the compute-intensive task of model training.”

The ground level detail is striking.

Evan Morikawa of robotics AI startup Generalist canvassed some 17 AI cloud providers for compute this year. Last winter, providers were offering reasonable prices on contracts as short as one year. By May and June, prices had jumped, contract terms had stretched to 3 to 5 years, and clusters of the latest chips carried 12 to 18 month waits. “It’s like VC currency right now to know the current price of GPUs,” he told The Information. And: “Now 1-year contracts are almost impossible to get.”

> “If your company is 1 year old, signing a 5 year contract makes no sense. The value of that 5 year contract is probably 3 times what you have raised, so you’re already underwater on paper.”

It gets more granular. A mid-size AI safety research organization talked to over 20 providers between March and July in search of just 60 chips. Three separate times, capacity that providers were advertising was sold to someone else within two days of the meeting. The org finally signed a deal worth several million dollars with Prime Intellect, reselling compute from data centers in India. An employee bought a cake to celebrate. “It’s a new landscape. We’re all adjusting.”

And at the bigger end of the neolab spectrum, Nvidia-backed Reflection AI is renting chips from SpaceXAI for $150 million a month, plus a multiyear Nebius deal totaling over $1 billion. That is a hefty chunk of the $2.5 billion the startup raised in its last round. Compute is the main use of new funds for these companies.

The number that matters most: the hourly rental price of an Nvidia H100 on a 1-year contract rose 50% from $1.73 in mid-December to $2.60 in mid-June, per Semianalysis. The H100 is a 2022 chip, TWO generations behind Nvidia’s latest. For on-demand H100s, Semianalysis often cannot quote a price at all in recent months. The column just reads ‘sold out’.

Even at the largest cloud vendors like [Amazon AWS](https://substack.com/redirect/7136faaa-477d-4a5a-902c-08621b08c6f9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

That datapoint cuts directly against the bear case argued by market shorts like Michael Burry, that AI GPUs are short-lived assets whose useful lives are overstated on the accounting books. The third-party market is voting the other way right now: four-year-old silicon is repricing UP, not down, as global demand for training and inference collide. To be fair to the bears, that is a shortage market talking, not a permanent re-rating. But the current trend lines are what they are. For the chip and cloud/neocloud [vendors like CoreWeave](https://substack.com/redirect/40ef390d-6828-4c7d-88bd-dd741513be19?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in particular.

The sellers of AI Compute are cashing in. The Information’s Briefing by Martin Peers tells that side in [“Nebius, CoreWeave Are Cashing In on Soaring AI Compute Prices”](https://substack.com/redirect/e7814b6d-e212-4735-b80a-c4db4a7ae55c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), on the heels of both neocloud earnings calls this week.

CoreWeave, which I profiled early as [Nvidia’s rocket fuel propulsion of CoreWeave](https://substack.com/redirect/40ef390d-6828-4c7d-88bd-dd741513be19?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (RTZ #657), reported Tuesday evening: topped estimates, raised guidance, and another volatile week for the stock, this time to the upside, up 19% Wednesday. CEO Michael Intrator on the call:

> “Our near-term capacity remains effectively sold out... [that] is translating into signed commitments on increasingly favorable terms from a broadening set of customers.”[](https://substack.com/redirect/ab1792eb-40aa-4206-b034-82adc6f50429?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Pricing and margins for its newest Blackwell and Vera Rubin chips are

> “setting new highs, while pricing for prior-generation [chips] is at or above where it was years ago.” CoreWeave raised prices 25% in July, per CFO Nitin Agrawal: “We are more confident than ever in the long-term ROI of our product.”

Nebius, one of the [‘Neoclouds’](https://substack.com/redirect/80e0aad8-fac6-455f-92c7-bb4e8b7d4b0b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I flagged back in RTZ #558, grew revenue 454% to $582 million last quarter, and held its first ever capacity AUCTION, clearing Blackwell prices “15% above the highest price we ever charged before” per CEO Arkady Volozh. The stock soared 34%.

Even SpaceXAI, which pioneered the short-term premium rentals to Anthropic and Google I covered in part 1, jumped 9.7% Wednesday to $146.15, up 35% from last week. BNP Paribas notes Nebius’s short-term pricing is roughly equivalent to the economics of SpaceXAI’s recent deals. All of it under the wing of [Kingmaker Nvidia, now ‘Uber AI Investor & Banker’](https://substack.com/redirect/1187b7b1-d1ac-488b-8e0d-070b9acc88d3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (AI-RTZ #1171).

Even the biggest clouds are overloaded. The Information’s [“AWS Is Overloaded. These Cloud Startups Are Picking Up the Slack.”](https://substack.com/redirect/1fc0270a-ae48-44ef-aea2-5d8e8291d975?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) by Catherine Perloff reports a growing number of startups saying AWS no longer meets their needs. Arcee CEO Mark McQuade puts it bluntly:

> “The problem with the large hyperscalers like AWS is availability and pricing. They don’t have anything, and if they do, the pricing is insane.”

Some 75% of Nebius’s business is startups that maxed out capacity at the big clouds. Consultants describe clients paying to run extra servers just in case: ‘a lot of defensive buying’.

The other side of the trade deserves stating. Duckbill’s chief cloud economist Corey Quinn asks the right question: “At some point, the supply shortage is going to resolve itself, at which point you can get the GPU that you need from any provider you care to name, why would you pick a neo-cloud?” And Peers notes the premiums are specifically for short-term, time-bounded needs. Multi-year deals are not paying them, and nobody pays a premium for 2029 capacity while the industry spends hundreds of billions expanding supply.

My take: this is the ground level confirmation of the view I have laid out in parts 1 and 2, and for months.

The collision between global training and inference demand is pushing AI Compute pricing UP in the short term, even for older chips in third-party markets, with the pain concentrated on the youngest AI startups and the pricing power concentrated in [the neoclouds](https://substack.com/redirect/80e0aad8-fac6-455f-92c7-bb4e8b7d4b0b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and their Kingmaker. Consumers are paying their own version of this bill via [‘RAMageddon’](https://substack.com/redirect/ca33e64b-086e-480f-9c89-17c0b46b3d58?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (Google just added $100 to every Pixel 11). A few years out, as those hundreds of billions of data center buildout land as live capacity, I expect the pressure to temper.

That is the subject of the coming part 4 soon, back up at the macro level of the AI Compute economy: the supply and the demand together.

For how the model-side leaders are navigating the same crunch, see yesterday’s [‘KK’ piece on Google](https://substack.com/redirect/2d2431e9-e096-4beb-964b-999db182c7b2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (AI-RTZ #1177) and the [Anthropic mega-AI IPO piece](https://substack.com/redirect/f649989a-24d7-450a-8833-f1ef48c736d9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (AI-RTZ #1176).

A supply/demand impact of the [AI Tech Wave](https://substack.com/redirect/d5e0711d-d339-4b88-9d0a-46246a49f8d6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) noteworthy in its deep ebbs and flows. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/f52cf0d3-2c0a-4d3e-b881-78bde221a1a0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).)
