---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260809050237.3.d250f79821a7c7a0@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-elons-mega-ai-data-center-supply
source_date: '2026-08-09'
subscription_tier: free
tickers:
- SPCX
- NVDA
- META
- MSFT
- AMZN
- GOOGL
themes:
- ai_infrastructure_capex
- hyperscaler_capex_buildout
- datacenter_buildout_pacing
- data_center_deployment_constraints
- inference_compute_economics
- foundation_model_economics
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Elon’s Mega AI Data Center Supply Ambitions (part 1). AI-RTZ #1173](https://substack.com/app-link/post?publication_id=684161&post_id=210189152&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMDE4OTE1MiwiaWF0IjoxNzg2MjUxOTQ0LCJleHAiOjE3ODg4NDM5NDQsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.ioeC2fUksUbcnet80PRyDlpwhpCAC5VDY2FiMQcv-PE)

### ...the ‘Gigawatt AI Gold Rush’, with frontier labs paying Elon ~2x compute market prices, for now.

The Bigger Picture, Sunday, August 9, 2026

We have argued for a while now that this [AI Tech Wave](https://substack.com/redirect/629ba54e-61ab-4ac0-8900-f31f6f28fd1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) has a unit of account besides compute tokens: Gigawatts. Power and mostly Nvidia Compute, at a current going rate of $50+ billion per Gigawatt of Power. For now, regardless of their use for AI training or inference.

This Sunday’s [Bigger Picture](https://substack.com/redirect/1a57aee2-cd0d-4352-9af6-b0a6798b8d83?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is about the industry’s mega ambitions for Gigawatts of AI data centers, who is being most aggressive about building them, who actually pays the prices that make the math kinda work, and the unprecedented bills that comes with the builds. And we’re using Elon Musk as a prime driver and example, in the current gigawatt supply trends.

### Elon’s 10+ gigawatt sprint

Start with the most aggressive plan on the board. SemiAnalysis published a piece this week with a title that says it plainly: “[SpaceX 10GW in 2027, Why It’s Real](https://substack.com/redirect/fabf41e9-74c0-488c-98b4-703797f78bff?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”.

On SpaceXAI’s first earnings call as a public company, [which I covered on ARD 134](https://substack.com/redirect/5f84a069-d6f3-4d16-aec0-b52965c8f0c0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) last week, Elon Musk said the company ‘conservatively’ aims to build and deliver an incremental 6 to 8 gigawatts of AI compute in 2027 alone. With potential well above 10 gigawatts. At roughly 50 billion dollars per gigawatt, that is 300 to 500 billion dollars of capex in a single year. On par with what analysts expect from AWS and Google combined, from a company with a fraction of their profits.

The floor of that range, $300 billion in 2026 dollars, is what it cost the US and NASA to send a total of 12 men to the moon from 1960 to 1973.

> “We see SpaceX on track to build about 10GW by year-end 2027... Elon bypasses typical datacenter construction constraints.”

The details on speed are real, and I have covered them as they landed. [Colossus 1 in Memphis](https://substack.com/redirect/a92ea410-2a7d-47c7-838c-481690cc042d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): 300 megawatts erected in 122 days. The Southaven power plant across the Mississippi border: 27 turbines in February, 69 turbines and 1.7 gigawatts by July. The new ‘MiniHard’ build: roughly half a gigawatt in five months.

The playbook is not better construction. It is creative, ‘out of the box’ construction. Transformers backlogged two years? Buy power modules from China and re-architect around medium voltage. Gas turbines backlogged five years at the usual names? There are 30 plus other gas generation suppliers if you will work with new ones. Labor constrained? Parallelize, pre-assemble, and run the site with a third of the industry-standard headcount.

### The bull supply case: gigawatts as current cash cows

Here is what makes the whole industry lean forward on this trade. Particularly Meta, also led by [AI-pilled founder/CEO Mark Zuckerberg](https://substack.com/redirect/8957b4a9-39e1-406f-acfa-0f0a2f27c814?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

As per SemiAnalysis’s tokenomics work: a gigawatt of frontier compute serving API inference can generate on the order of 100 billion dollars a year in revenue, against roughly 12 billion dollars a year of rental cost. Frontier inference margins run north of 60 percent, and for the very top models, higher still.

That is why Elon reintroduced something the AI compute market had not yet seen at scale: top-dollar pricing, at a reported 30 to 50 million dollars per megawatt-year, with 3 to 5 month delivery times nobody else has yet matched. At those rates the capex pays back in under a year.

The AI market bulls do not stop there. Industry analyst [Dwarkesh Patel argued this week that compute might get 10x more expensive](https://substack.com/redirect/9c81b7f4-74ad-4164-be84-d2ca7b424f7c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from here. By his own admission, he did it as a provocative, ‘against the consensus’ thought experiment.

His math: frontier lab revenue is compounding at roughly 10x a year while compute supply grows about 3x. And price is the release valve by his argument. AI compute from frontier models at current spot prices are already up 40 percent plus since February. And cites Google paying roughly twice spot in its SpaceX rental deal.

### My more tempered take: look at WHO pays these prices, and WHY

I agree with the short term directionality of these trends.

But this is where I part ways with the longer-term bullishness of these arguments, SemiAnalysis’s included.

The current ‘money math’ is not a market price. It is a desperation price, paid by a very specific set of buyers in a very specific market window.

The buyers paying up are Anthropic and OpenAI. Both are in their [mega-AI IPO windows](https://substack.com/redirect/f78769ce-4150-486a-a1ef-c844b04ea70d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), where the story requires growth unconstrained by compute. And both have severe near-term compute shortages, [especially Anthropic, whose compute constraints have visibly throttled its growth](https://substack.com/redirect/c5d9dadd-df6f-41e0-8f28-4483e6285ded?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), as I wrote in May.

For them, 3 to 5 month delivery at top-dollar prices is not extravagance. It is the price of the IPO narrative. That is precisely the window Elon is building into, and I would argue [Meta’s parallel mega-builds](https://substack.com/redirect/e2cb491b-e4dd-49d3-9ef5-4b77fbb0e4ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that I have covered are aimed at adjacent urgency.

The other prospective customers are a different species.

Microsoft, Google and Amazon own fleets, own silicon in TPUs, Trainium and Maia, and operate on decade horizons. [Google and Anthropic already rent Elon’s racks](https://substack.com/redirect/7a93af22-9cc8-4fa9-8d28-9ae9c21edae1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), but note the terms: 90-day cancellation clauses.

That is tenants keeping optionality, not committing decades at 50 billion dollars per gigawatt-year. SemiAnalysis sees Microsoft as the natural largest offtaker of Elon’s 2027 capacity. Maybe. On some of the deliverables that Microsoft owes OpenAI under its current supply deals.

My read is the hyperscalers will be prudent and pragmatic on price, because they can afford to be. The desperate cannot, and the desperate are in a short supply-constrained window, not necessarily a permanent market.

And remember what widening [price umbrellas](https://substack.com/redirect/1d97e77f-6aec-448d-b64f-c94832029689?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) do, as I have written: they invite supply. Even [OpenAI is playing that card](https://substack.com/redirect/b8a03ea4-2f95-4971-8c27-9cd91cbb7c1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) against Anthropic with its slightly less capable frontier models in the GPT 5.6 family.

Per-token compute costs keep falling with every model and silicon generation. Customer silicon keeps expanding the alternatives. The desperation premium ends the way all scarcity premiums end, with more supply and calmer, pragmatic buyers.

Dwarkesh himself concedes the history: bets on permanent scarcity usually lose.

The financing side carries the same asterisk. Nvidia vendor financing is likely the quiet reason Elon declared SpaceX ‘Nvidia exclusive’ on that earnings call. [The Kingmaker, now Uber AI investor and banker](https://substack.com/redirect/2ca994fb-7380-417d-be02-a9829c7a2bed?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), one row deeper into the stack, as I wrote Friday.

Bookings become buildings become billings, IF the tenants stay. And SemiAnalysis’s 300 billion dollar ARR path for SpaceX deserves my standing caution from the earnings coverage: ARR is one month multiplied by twelve, not recorded revenue.

### Also, the ‘net zero’ Climate Collision

Now the other costs that come with the build. The NY Times reports [Amazon is investing in an on-site gas plant in Pecos County, Texas](https://substack.com/redirect/1a329a45-5978-4130-b8bf-7dea67b615df?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): 35 natural gas turbines, up to 7.65 gigawatts, feeding a single data center campus.

> “The new gas-burning plant, if built to specifications, would be permitted to release 33 million tons of carbon dioxide a year... more planet-warming gases than any other power plant in the country.”

The current record holder is a coal plant at about 16 million tons. Amazon co-founded the Climate Pledge, net zero by 2040. Its emissions have risen every year of the AI boom. The company says the commitment has not changed. The permits say the near-term direction has.

This is the collision I covered in [Haste Makes Waste](https://substack.com/redirect/e2cb491b-e4dd-49d3-9ef5-4b77fbb0e4ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on the Memphis air-quality fights, and in [Damn the Torpedoes](https://substack.com/redirect/d150d5fb-617c-4cfc-bf4f-833c1eb16f54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the giants are building through the headwinds, not around them. Off-grid gas is the fastest path to gigawatts, so off-grid gas is what gets built. Expect an explosion of these projects, and an equal explosion of local resistance, town by town, permit by permit, turbine by turbine.

### The bigger picture

Goldman Sachs has sized the AI infrastructure buildout at [roughly $7.6 trillion through 2031](https://substack.com/redirect/cf87dbd7-c924-4c62-8458-3e2b7487c157?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). I have been writing about the [multi-trillion dollar compute builds](https://substack.com/redirect/1b84c9e8-e067-4355-a1ac-3440a21910d3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) since they were a one-to-nine-trillion argument. The abstraction is over. The trillions now have street addresses: Olive Branch, Mississippi. Southaven. Pampa, Texas. Pecos County.

So hold the [Bigger Picture](https://substack.com/redirect/1a57aee2-cd0d-4352-9af6-b0a6798b8d83?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in mind.

The ambitions are real, and Elon’s are the most aggressive of the lot, because his speed advantage is provable and his urgent customers’ margins can carry his prices for now. The circularity is real: Nvidia finances the builder, the builder rents to the labs, the labs’ IPO stories justify the prices. And the physical bill is real, and will be litigated in public.

Elon, typically, has already priced in the endgame: if earth pushes back hard enough, his answer is [Terafabs](https://substack.com/redirect/ae5266ae-f875-428c-8890-f7fcfeee53cc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [AI data centers in space](https://substack.com/redirect/b4301583-d177-41e5-9981-1853a3725219?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Out there? Sure. But so was 10 gigawatts in a year, [not so long ago.](https://substack.com/redirect/9bd0d55d-e457-4349-b295-7634b9a963df?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Gigawatts are the new standard in AI data centers. And the ‘gold rush’ is on.

Just remember what gold rushes are actually famous for: who ends up holding the pans, and who sold them.

More tomorrow in ‘Part 2’, on the demand side bull case for AI compute prices from here.

And the reasons I think the curve runs tamer. An impact of the [AI Tech Wave](https://substack.com/redirect/629ba54e-61ab-4ac0-8900-f31f6f28fd1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) worth tracking. Stay tuned.

(A programming note: this is part 1 of a pair. Today was the supply side of the compute trade: who is building the Gigawatts, and who actually pays the prices. Tomorrow’s part 2 takes up the demand side, the strongest version of the other side of the trade: the ‘Dwarkesh Patel’ compute ‘thought experiment’ bull case. The short and longer term economic implications.

The case that compute prices go UP from here, way up, and the ten brakes on it from my perspective. Stay tuned.)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
