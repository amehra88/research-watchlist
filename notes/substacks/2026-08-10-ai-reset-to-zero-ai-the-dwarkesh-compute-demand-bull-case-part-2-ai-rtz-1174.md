---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260810050256.3.2c2e93bd3b3169f6@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-dwarkesh-compute-demand-bull
source_date: '2026-08-10'
subscription_tier: free
tickers:
- NVDA
- MSFT
- GOOGL
- SPCX
themes:
- ai_infrastructure_capex
- inference_compute_economics
- foundation_model_economics
- model_efficiency_evolution
- frontier_model_competition
- datacenter_buildout_pacing
- silicon_architecture_competition
- model_commoditization
- ai_compute_topology
- foundry_capacity
- china_ai_infrastructure_demand
ingestion_date: '2026-08-15'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: The ‘Dwarkesh’ Compute Demand Bull Case (part 2). AI-RTZ #1174](https://substack.com/app-link/post?publication_id=684161&post_id=210379241&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMDM3OTI0MSwiaWF0IjoxNzg2MzM4NTQ3LCJleHAiOjE3ODg5MzA1NDcsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.KzRyHQn6JkPuKGU5_ZvhlOxXfWegsx3hEII6_nc--gU)

### ...compute 10x pricier? The mega-bull case laid out, and my ten brakes on tempered prices.

[Yesterday’s Bigger Picture, part 1 of this pair](https://substack.com/redirect/9b878224-ca65-4118-b371-250b478f9d37?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), was the supply side of the compute trade: the ‘Gigawatt Gold Rush’, and who actually pays [Elon’s prices](https://substack.com/redirect/db3033bb-495e-40c3-b59a-86bc98bc8572?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)for AI compute. Today, part 2, the demand side: the bull case that compute prices go UP from here, way up. It deserves a fair hearing, because it is the smartest version of the argument in circulation. And then it deserves the brakes that could slow it down.

### The ‘Dwarkesh Patel’ compute bull case, fairly stated

[Dwarkesh Patel argued this week that compute might get 10x more expensive](https://substack.com/redirect/ea836467-9d53-474c-b3d7-cb04d806c76f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and the piece has drawn prominent industry reactions and [close examinations](https://substack.com/redirect/f23b22ad-3cc3-4156-b6f5-c8742b2fc195?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for a reason. His math is as follows:

Frontier lab revenue is compounding at roughly 10x a year (particularly frontier AI lab Anthropic for now). Compute supply grows about 3x a year, decomposed as roughly 1.4x from Moore’s Law, 1.2x from new fabs, and 1.8x from wafer reallocation toward AI. If revenue compounds at 10x while capacity compounds at 3x, something has to c[lear the gap](https://substack.com/redirect/1e9d871b-c0e0-4164-bdce-a4b7754c2112?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and price is the obvious release valve.

His pointiest version of the claim: compute that can do human-level software engineering should command something like human-level economics. On that logic an H100 [could justify around 250 thousand dollars a year in rent, roughly 15x today’s spot price](https://substack.com/redirect/228a8481-69d3-4c05-8fd5-ad7c06c82d02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

And he points to evidence already on the tape: GPU spot prices up 40 percent plus since February. Google reportedly paying about twice spot on its SpaceX rentals. Anthropic’s inference margins going from about 40 percent to above 80 in a year. Buyers locking multi-year capacity now, which is what you do when you expect prices to rise. Plus the wall behind it all: AI taking about 86 percent of advanced node wafer capacity by late 2027.

And the economics under it are named, not vibes. He leans on the economist-driven [lump of labor fallacy](https://substack.com/redirect/44ef8a85-0c91-408b-b251-8984cb672b09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to argue that a flood of AI software engineers does not crater the value of engineering, the way economists argue high-skilled immigration does not depress wages over time. He invokes the economic [Alchian-Allen effect](https://substack.com/redirect/0d9fb0d8-fe60-4af9-aca4-9f73c1265fbf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to argue that scarcity shifts demand TOWARD the premium frontier models, not away from them. And he flags the academic [Simon-Ehrlich wager](https://substack.com/redirect/5b95e410-bd7f-436a-8b46-c70206c9780a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) himself, conceding up front that his case pattern-matches the historical scarcity calls that lost. More on that concession in the brakes discussion below.

Here is his bull case ‘thought experiment’/argument in a visual ‘AI Compute Flywheel’ nutshell, along with my commentary with the dotted lines.

One more note on the source of this bullishness from a personal dynamics perspective, because it is a story in itself. This bull case comes, quite literally, out of one San Francisco house: Dwarkesh Patel and SemiAnalysis’s Dylan Patel ([his analysis discussed in Part 1](https://substack.com/redirect/9b878224-ca65-4118-b371-250b478f9d37?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)), no relation, [are housemates](https://substack.com/redirect/30bf9fc0-305e-4bf4-b8e2-d39914ac2985?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Which makes yesterday’s Bigger Picture and today’s post back-to-back replies to the two housemates’ back-to-back anchor pieces.

Dwarkesh is also close to Leopold Aschenbrenner, whose ‘Situational Awareness’ mega fund rode the same maximal bull thesis with 4x leverage to a 45 billion dollar peak, [was forced to unwind most of it days ago](https://substack.com/redirect/b0cef45c-a8b4-48e7-9b00-9ce4dc7b87ab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [is already back raising fresh capital](https://substack.com/redirect/ceb26d25-e4e8-4681-9e20-6a814ba4e6cc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

None of that makes the arguments wrong. But the loudest compute-scarcity math in circulation is coming from one tightly connected, VERY bullish corner of the AI world, marking its own beliefs to market. Worth knowing as we weigh it all.

That is the bull case, and it is a well-told, contrarian story. Now the brakes as I see them, and I count to ten.

### The market brakes

- Look at who pays these prices, and why. [As I wrote yesterday](https://substack.com/redirect/9b878224-ca65-4118-b371-250b478f9d37?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), today’s premiums are desperation prices, paid by OpenAI and Anthropic in their mega-AI IPO windows, [especially compute-throttled Anthropic](https://substack.com/redirect/1e9d871b-c0e0-4164-bdce-a4b7754c2112?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Windows close. Post-IPO, the same buyers get price-disciplined.

- Price umbrellas invite supply. [As I have written](https://substack.com/redirect/6bc088ce-77c4-4236-acb0-f673e58c809d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), 30 to 50 million dollars per megawatt-year summons every builder with a balance sheet. Elon is first, not last.

- Per-token deflation never stops. Every model generation and silicon generation cuts the cost of producing a token. ‘Renting an H100’ is the wrong unit of account over any multi-year horizon, and Dwarkesh’s own examiners [make the same distinction](https://substack.com/redirect/f23b22ad-3cc3-4156-b6f5-c8742b2fc195?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): token prices can fall while frontier compute stays tight. Both things happen.

- Customer silicon compounds. TPUs, Trainium, Maia, and now [Anthropic’s own chips](https://substack.com/redirect/0c29de99-a16e-4902-9e42-0426984d79f6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The ‘Frenemies’ build their own exits from spot pricing, every year.

- The revealed preference. [Google and Anthropic rent Elon’s racks on 90-day cancellation clauses](https://substack.com/redirect/573bb0f9-bff4-4c90-be1b-7ef136f302d0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Nobody betting on decade-long scarcity signs a 90-day out.

- History and China. Dwarkesh concedes it himself: bets on permanent scarcity usually lose to ingenuity, the Simon-Ehrlich lesson. And the Chinese open-weight models keep pressing from below. Yes, [DeepSeek just raised prices](https://substack.com/redirect/fe3ee07c-a2da-4896-bf99-b381f01e0684?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), which helps his case short-term. But the larger frame, as I argued in the Race to Zero piece, is a WIDENING pricing spectrum, not a curve that moves 10x in either direction. [](https://substack.com/redirect/4fb2ad9e-18d4-4c09-8f26-6c97af5ac6d7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- The labor peg is wobbly. The 250 thousand dollar H100 assumes AI labor prices at human labor rates. Competition among a dozen labs selling the same capability is precisely what breaks that peg. Monopoly rents require a monopoly.

- This is not all ‘Mainframe AI’. Dwarkesh’s math treats essentially all inference as data center load. But as I have argued since [the earliest days of this newsletter](https://substack.com/redirect/ce116993-d6fa-4fc9-aac3-a461593d8632?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), this wave adds a ‘Local AI’ compute stage alongside the ‘Mainframe AI’ stage, and unlike the mainframe-to-PC-to-smartphone transitions that took decades, this one is being measured in years. [Nvidia and Microsoft are already building the local AI computers](https://substack.com/redirect/2f54652f-c97e-4471-aaaf-ec46c457ea2d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Yes, [‘RAMageddon’ and the memory shortages](https://substack.com/redirect/1a06bf87-223f-4d2f-8861-3f9b1611dbee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) temper the pace, as I wrote this past week about Rubin Ultra. But the direction is real, and every inference workload that moves onto a device EXITS the data center pricing equation entirely.

- The winner-take-all assumption. The bull case quietly assumes the frontier models take most of the world’s compute load at their desired prices, because customers ‘go with the best’ for everything. That is exactly what [Microsoft is now arguing against, picking a side against the frontier labs](https://substack.com/redirect/61f694da-f561-4184-888f-a2d9db8f1691?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and what [Palantir and the enterprise camp have been shouting](https://substack.com/redirect/40944290-ac97-4c28-aa93-8c7b904615e4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), as I covered in the ‘Us vs Them’ pieces. Enterprises in law, medicine, finance and every domain beyond tech are waking up to the pattern: hand the frontier labs your data and your business IP, and watch them build their own Microsoft Excel to your Lotus 1-2-3, their own Word to your WordPerfect. In your domain. The rational response is to pick sides, split workloads, and keep leverage. A fragmented buyer base does not pay monopoly prices for compute. Winner-take-all pricing requires winner-take-all customers, and the customers are actively organizing against being taken.

- The 10x ARR growth is history, not a promise. Every step of the bull math compounds off frontier lab revenue growing roughly 10x a year. But listen to how Dario Amodei himself talks about that number. He [cites the 10-fold annual growth as what HAS happened, and names the fragility in the same breath](https://substack.com/redirect/05459f5d-2627-48b1-9296-3dd4f2ab6633?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): “If I’m just off by a year in that rate of growth, or if the growth rate is 5x a year instead of 10x a year, then you go bankrupt.” Even the [‘crazy’ 80x quarter and the 30 billion dollar run rate](https://substack.com/redirect/b7771794-c67f-4481-ac38-e9852a54723a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) are descriptions of the rear-view mirror. Nobody at scale in tech history has sustained 10x annual revenue growth for long, arguably three to five periods at most before the law of large numbers bends every curve. It always has. [](https://substack.com/redirect/2aa81eb2-cc07-4f21-905a-f4955473f6dd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

And consider where today’s load actually sits: much of the current revenue surge is AI coding, Anthropic Claude Code/CoWork and its imitators, a category that did not exist over a year ago. With OpenAI and everyone else feverishly racing to catch up.

Meanwhile this weekend brought reports that [ByteDance is training a 10 trillion parameter frontier model](https://substack.com/redirect/a5e1217c-5c21-42af-af51-a8f7890482d2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [MiniMax plans to open-source a 2.7 trillion parameter model this quarter](https://substack.com/redirect/8a3be63a-2df7-40f6-811e-879ed606cff5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). More super-scale competition pressing on prices, not less. A growth rate that is one part new-category surge and one part temporary lead is not a rate to hang decade-long compute price forecasts on.

### My Take

Prices stay firm through the IPO window and into the 2027 wafer crunch. The bulls are right about the next 18-24 months of tightness, and Dwarkesh has done everyone a service by putting some numbers on it.

But past the window, the spectrum widens rather than the whole curve lifting 10 to 15x. Supply answers the umbrella. Tokens keep deflating. Silicon alternatives compound. Local AI siphons inference off the mainframe. And the buyers refuse to consolidate behind the frontier labs, for reasons that have nothing to do with price and everything to do with survival.

And a closing word on thought experiments, from experience. I made exactly this point [on Ram Ahluwalia’s Lumida podcast last week](https://substack.com/redirect/ab150f9f-2f93-4d6b-b66d-3015a4aac337?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), talking about the Leopold-style long-term bull cases: the big-theme calls are the relatively easy part, and the people making them can be entirely right on the themes.

I wrote about the coming AI-driven memory shortage three years ago, and the shortage came. But HOW it came was nearly unknowable in advance: roughly 80 percent of the world’s memory capacity swung wholesale to HBM in about two years, on the same fabs, and the ‘Mainframe AI’ wave utterly disrupted the supply of ‘Local AI’ chips and memory in the short run, measured in the next three to four years. You knew the direction, but not the amplitude of the waves.

The 10x compute bull case by Dwarkesh Patel is a provocative thought experiment on the possible metric growth. Likely right on direction, and still liable to be upended, or at least interrupted, by variables not priced in today.

Both stages of this [AI Tech Wave](https://substack.com/redirect/d71e4385-b243-4a35-8979-cc2bd0fecf07?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) get built, Mainframe and Local, over the next 3-5+ years. Not the decades it took for the mainframe to PCs to Internet to Mobile to now AI waves.

The AI Compute demand gold rush is directionally right over the longer term. Unknown are the short term twists and turns that temper that speed of growth.

And there is a part 3 brewing in a future post on AI-RTZ: the economics that sits under both sides of this trade, supply and demand together, and why the economists always arrive after the engineers. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
