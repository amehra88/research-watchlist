---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260825195939.3.a55a5a5b2069f2a5@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/the-need-for-speed-in-ai-inference
source_date: '2026-08-25'
subscription_tier: free
tickers:
- AAPL
- AVGO
- NVDA
themes:
- agent_framework_landscape
- ai_compute_topology
- ai_infrastructure_capex
- chip_design_competition
- foundation_model_economics
- inference_compute_economics
- model_commoditization
- model_efficiency_evolution
- silicon_architecture_competition
ingestion_date: '2026-08-26'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [The ’Need for Speed’ in AI Inference. OpenAI, Nvidia & Apple. ARD #148](https://substack.com/app-link/post?publication_id=684161&post_id=212749720&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMjc0OTcyMCwiaWF0IjoxNzg3Njg3OTg3LCJleHAiOjE3OTAyNzk5ODcsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.ezeYLF9iHvMxnnxfQuba3OeG5lxPifJ3IO85LrWEFgQ)

### ...OpenAI’s Jalapeño beats Blackwell, Perplexity goes local with Nvidia, AI routing booms, & Apple’s M6 Mac mini.

‘The Need for Speed.’ For AI inference, especially locally. Yesterday we put the whole AI world on Nvidia’s shoulders; today is about what everyone is actually racing FOR: more AI inference computing capacity, in the cloud and on our desks, as fast as possible. Speed, in tokens per second, tokens per watt, tokens per dollar, is the currency of this [AI Tech Wave](https://substack.com/redirect/d98f6704-fe9f-4fd1-a8af-1b1681e80350?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) going into the second half of 2026, and into the two US mega-AI IPOs ahead. Four stories today, all the same physics from different altitudes. My takes below, as discussed on the show.

## (1) OpenAI Leans In on its ‘Jalapeño’ Inference Chips

OpenAI took the wraps off Jalapeño, its self-designed AI inference chip, at the Hot Chips conference, and the early reviews are pretty positive. Semianalysis, one of the widely followed chip analysts in the business, was invited into OpenAI’s labs to benchmark it themselves, and their headline says it plainly: “better than Nvidia Blackwell.” Their numbers: Jalapeño beat every Nvidia, AMD and Google chip they have tested on top open source models, on the metric that matters most, tokens per megawatt. Over 700 tokens per second per user on DeepSeek R1, around 1,400 on GPT-OSS, all without the ‘speculative-decoding’ tricks other chips lean on. The Verge adds OpenAI’s own framing: 1.5 to 1.9 times more AI work per watt, and 1.7 to 3.6 times lower latency, than Nvidia’s GB200-class systems, with hardware VP Richard Ho calling it the best of both worlds since chips normally trade latency against throughput.

The backstory is notable for its speed of development, along with the benchmarks. Built with Broadcom from a blank sheet: design team hired mid-2024, tape-out in about 16 months, silicon back for only 3 months, and already posting these results, with a B0 stepping in the fab carrying roughly 25% better performance per watt. The chip uses HBM4 memory ahead of most of the industry, runs at 700 watts against Rubin’s 900-plus, and OpenAI’s own Codex wrote most of the kernels. Now the caveats, and there are real ones: the numbers were provided by OpenAI, verified in-lab but on the friendlier benchmarks; production only ramps through 2027; and OpenAI itself says this supplements Nvidia rather than replaces it. Why the hurry? The same day, OpenAI restored the five-hour usage caps on Codex for ChatGPT Plus users to smooth the load on its compute. Demand is so hot they are rationing it.

And zoom out with the Dwarkesh Patel and Dylan Patel conversation this week, a useful macro frame on all of this. Dylan’s math: world compute in gigawatts roughly doubles every year, but frontier lab compute triples. Anthropic and OpenAI alone are on track to take roughly 45% of the world’s incremental compute next year, and half of all new compute by late 2027, because they monetize tokens better than most, and can generally outbid everyone. As Dylan puts it, “every force is screeching towards centralization.”

My take: the AI supply-demand race accelerates, exactly along the lines of our four-part supply and demand series. Jalapeño is not about replacing Nvidia in the near term. It supplements it. The overall supply picture stays tight for the foreseeable future, and the frontier labs are pressing on the gas for every alternative path to compute: their own chips, other people’s chips, and other people’s data centers. It is currently a two-horse race between OpenAI and Anthropic to capture the maximum share of the world’s AI compute, and Anthropic is now standing up its own ASIC team, with some Jalapeño alumni on it, to run the same play. I called the tension years ago in ‘Nvidia vs its Top Customers’ and the ‘Frenemies’ piece. The frenemies era is now shipping silicon. The need for speed compounds from here.

Sources:

- [Semianalysis: OpenAI Jalapeño, better than Nvidia Blackwell](https://substack.com/redirect/e73dc555-2cb7-41da-960c-9a1c493b5d2d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: OpenAI says its Jalapeño chip can power faster AI responses than the competition](https://substack.com/redirect/f0779ff7-d22d-4249-8a89-c70846caa46d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [9to5Mac: OpenAI restores 5-hour Codex and Work limits for ChatGPT Plus users](https://substack.com/redirect/238bd80c-7be7-4d50-a5aa-bc9c4398de41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dwarkesh Patel podcast: Anthropic & OpenAI will have most of the world’s compute by 2028, with Dylan Patel](https://substack.com/redirect/6dd95fd4-5fbf-4514-ac0c-017a255e6a87?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #554: Nvidia vs its Top Customers for AI GPUs](https://substack.com/redirect/83c97e95-097b-4c09-a87a-f644904d211f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #806: The ‘Frenemies’ nature of the AI Coding space](https://substack.com/redirect/07243be5-9d70-46df-aea4-1189152e3b2a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1180: AI Supply and Demand Together (part 4)](https://substack.com/redirect/b99167d4-504d-42da-9152-c0b1f1e55c9a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ: The Dwarkesh compute demand bull case (part 2)](https://substack.com/redirect/04e62e90-c873-4d22-bc2a-f6846b93ce67?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) Perplexity and Nvidia Ship the ‘Portable Computer’

The local leg of the need for speed. One day after the report of Nvidia discussing a $30 billion-plus investment in Perplexity, the two companies shipped a product together: Portable Computer, a version of Perplexity’s agentic ‘Computer’ platform that runs entirely on hardware you already own. Nvidia’s DGX Spark desktop supercomputer, any Linux machine with an RTX GPU carrying 24 gigabytes of video memory, or the other Nvidia/Microsoft AI computers being rolled out by OEMs that I wrote about recently, with supplemental cloud compute off various tiers of Perplexity subscriptions. The headline feature, per VentureBeat: zero token costs. The models, your files, and the work all stay on the machine; in the demo, an agent chewed through a folder of 1099s and investment documents while the cloud-credit counter sat parked at zero. Every task starts on-device by default, and the system asks permission before escalating any step to a frontier model in the cloud, running a privacy classifier over what would leave the box first. The hybrid economics are the tell: on a hard coding benchmark, the local model alone scored about 60% at essentially zero cost; letting it consult a cloud frontier model as an advisor recovered most of the remaining gap at two-thirds of the frontier-only cost.

My take: the two companies are not waiting after their deal news to expand AI compute options across multiple models, local and cloud together. A smart move by both. For Nvidia, it is the killer app its DGX Spark desktop has been waiting for, and another lean into open source models to supplement its close frontier-lab relationships. For Perplexity, it is a product whose economics do not depend on metering every token, and a wedge into the privacy-sensitive enterprises in law, healthcare and finance. One conspicuous absence on the roadmap: Apple silicon. Hold that thought for the Gadget section, because the local speed race is very much multi-front.

Sources:

- [VentureBeat: Perplexity partners with Nvidia to launch Portable Computer, a fully local AI agent with zero token costs](https://substack.com/redirect/a8dc8ca4-f0f6-4efc-8b48-ed628084af9b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1104: Nvidia and Microsoft focus on local AI computers](https://substack.com/redirect/b78d24b9-2d0a-4532-9c7d-283151eaa4c9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #147: yesterday’s Nvidia/Perplexity $30B investment discussion](https://substack.com/redirect/ce4f251b-d6e8-45fc-b918-2995739885f2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) AI Model Routing Companies in Demand, post the Stripe/OpenRouter Buy

Model routing is booming, per Axios’ aptly titled piece, routing is coming for the frontier AI labs. The scoreboard: Stripe agreed to buy OpenRouter for north of $8 billion, up from the roughly $7 billion first reported when we covered it at ARD 142. OpenRouter had 8 million users and 400 models on the platform as of May. Meta is reportedly building its own OpenRouter competitor, called Switchboard, partly to lower its own AI bills. Even the frontier labs now ship model pickers of their own. And the tell inside the numbers: the five most popular models on OpenRouter are all open weight or open source. OpenAI and Google place just one model each in the top ten. Anthropic places none. Average token costs have plummeted since their mid-May peak as the labs cut prices to win back share, and there is a sovereignty current running underneath too: enterprises that do not want their IP flowing to the frontier labs, the same shield instinct we covered in the FDE wars.

My take: this trend was underway well before the Stripe deal, as we wrote in the ‘open to close’ battle piece back in the day. But now it gets turbocharged across the industry. Routing turns models from destinations into interchangeable commodities, which is exactly why the frontier labs are keenly aware, and why I expect them to keep their a la carte pricing efforts relatively muted ahead of their mega-AI IPOs. Nobody pitching a $2 trillion valuation wants to headline a price war. The router is the buyer’s answer to the need for speed at the right price, every query, every time.

Sources:

- [Axios: Routing is coming for the frontier AI labs](https://substack.com/redirect/596d584d-256f-4cfb-baf3-f1c474e92b54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #142: Stripe’s OpenRouter Buy, in ‘Hidden Figures’](https://substack.com/redirect/8da6a037-01df-43e6-9168-731aefc75477?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #483: The other AI open to close battle](https://substack.com/redirect/a702eb07-a72d-4017-ae9c-922ad914e346?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: notice the two opposite directions the need for speed is pulling, at the same time. Up and in: Dylan Patel’s math has OpenAI and Anthropic absorbing half the world’s new compute by late next year, building their own chips, and outbidding everyone for the rest. Down and out: routers, open models, and zero-token local agents pushing usable intelligence onto desks and into devices, at marginal costs approaching zero. Same scarcity, opposite responses. The centralization pays for the frontier; the diffusion is how the rest of the world routes around its price. My long-held thesis of AI ‘mainframe’ computing on cloud infrastructure, supplemented by local AI computing on premises, is coming together, despite the headwinds of [‘RAMageddon’](https://substack.com/redirect/3d652366-51aa-43d3-8f08-ea9f909ed132?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). That is the supply and demand story of our four-part series, now running at full speed on both rails. Speed, measured in tokens per second, per watt, and per dollar, is the scoreboard for all of it.

## Gadget AI: Apple Refreshes the Mac mini and Mac Studio, in ‘RAMageddon’

The Gadget AI today is the humble hero of local AI: Apple refreshed the Mac mini and Mac Studio with its latest M5 and M6 chips. And pithily put by the WSJ, ‘good luck getting your hands on one’. The news: a new Mac mini with the all-new M6 chip at $899, or an M5 Pro at $1,699, both $100 more than the outgoing models. The Mac Studio moves to the M5 Max at $2,499 and the M5 Ultra at $5,499, up $200. Apple claims at least 4x faster AI performance generation over generation. The M6 is Apple’s first 2-nanometer chip, per the Verge, with a dual 16-core Neural Engine and a neural accelerator in every GPU core; the M5 Ultra fuses four dies into Apple’s most powerful chip yet, supporting 512 gigabytes of unified memory. Preorders are open, shipping September 22. Avid developers will likely spec out the top configurations at $10-20k per unit. With max chips, RAM and storage. A relative bargain vs rising a la carte AI compute prices for top inference models.

Why the price hikes and the scarcity: ‘RAMageddon.’ The global memory-chip shortage plus the AI agent craze made the outgoing Minis and Studios sleeper hits that vanished from shelves; the Mini is normally about 3% of Apple’s US Mac sales, then OpenClaw and the on-device agent wave hit, as we covered at the time. Apple’s unified memory architecture, where CPU and GPU share one pool, happens to be exactly what local AI models want.

My take: this is Apple’s signal that it takes the local AI compute opportunity seriously. They shipped these ahead of Siri AI and the updated iPhones September 9 next month, and ahead of the September 1 transition to the new Apple CEO, John Ternus, the ex-hardware chief, which tells you what kind of company Apple intends to be under him. A positive, proactive lean into this [AI Tech Wave](https://substack.com/redirect/d98f6704-fe9f-4fd1-a8af-1b1681e80350?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from Apple, meeting the near-term need for speed in local computing for millions of developers running custom and private AI agent workflows. Note the shape of the race: Perplexity and Nvidia left Apple silicon conspicuously off their local roadmap this morning, while Apple sells out of its best-selling local AI boxes. The local front has more than one army of computers.

Sources:

- [WSJ: There’s a New Mac Mini and Mac Studio. Good Luck Getting Your Hands on One](https://substack.com/redirect/96b795b8-00fe-4061-95a2-ea481ed2d57f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Apple Newsroom: Apple unveils a more powerful Mac mini, featuring the all-new M6 and M5 Pro](https://substack.com/redirect/ec63490d-eec7-461b-b4b7-c9ba16376209?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Apple Newsroom: Apple introduces new Mac Studio with M5 Max and M5 Ultra](https://substack.com/redirect/9e4f6339-2af6-4734-a4db-06dec7dac756?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: Apple’s new M6 chip gets more cores and more AI compute](https://substack.com/redirect/603ccb60-4a68-4ca3-8a42-823be2980aab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1016: Apple’s Mac mini popularity with OpenAI’s OpenClaw, in China and beyond](https://substack.com/redirect/da65a563-1003-4294-81ab-9d95a5dadeb3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Q&A

Q1: What’s MP’s take on the Mac mini?

ANSWER: The best Apple computer I have ever used, across decades of using them. Especially for AI tasks with frontier models. No muss, no fuss. It sits there, it runs the agents, it gets out of the way. The unified memory is the quiet superpower: the models just fit.

Q2: Any ways they could be better?

ANSWER: They sometimes get overly hot with sustained AI computing. Long agent runs will make that little aluminum box work. So better cooling perhaps, especially as always-on agentic workloads become the default use. A small ask against what it delivers.

The need for speed in AI inference, up and in toward the frontier labs, down and out onto our desks, is the current running under every story in this [AI Tech Wave](https://substack.com/redirect/d98f6704-fe9f-4fd1-a8af-1b1681e80350?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). And tomorrow brings Nvidia’s quarter, the next weigh-in for all of it. Stay tuned.

## Full Source Reading

### OpenAI’s Jalapeño chip, and the compute race

- [Semianalysis: OpenAI Jalapeño, better than Nvidia Blackwell](https://substack.com/redirect/e73dc555-2cb7-41da-960c-9a1c493b5d2d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: OpenAI’s Jalapeño chip benchmarks](https://substack.com/redirect/f0779ff7-d22d-4249-8a89-c70846caa46d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [9to5Mac: OpenAI restores 5-hour Codex limits](https://substack.com/redirect/238bd80c-7be7-4d50-a5aa-bc9c4398de41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dwarkesh Patel podcast, with Dylan Patel](https://substack.com/redirect/6dd95fd4-5fbf-4514-ac0c-017a255e6a87?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #554: Nvidia vs its Top Customers](https://substack.com/redirect/83c97e95-097b-4c09-a87a-f644904d211f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #806: The ‘Frenemies’ nature of the AI Coding space](https://substack.com/redirect/07243be5-9d70-46df-aea4-1189152e3b2a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1180: AI Supply and Demand Together (part 4)](https://substack.com/redirect/b99167d4-504d-42da-9152-c0b1f1e55c9a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ: The Dwarkesh compute demand bull case (part 2)](https://substack.com/redirect/04e62e90-c873-4d22-bc2a-f6846b93ce67?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Perplexity and Nvidia’s Portable Computer

- [VentureBeat: Perplexity partners with Nvidia to launch Portable Computer](https://substack.com/redirect/a8dc8ca4-f0f6-4efc-8b48-ed628084af9b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1104: Nvidia and Microsoft focus on local AI computers](https://substack.com/redirect/b78d24b9-2d0a-4532-9c7d-283151eaa4c9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #147: The World on its Shoulders](https://substack.com/redirect/ce4f251b-d6e8-45fc-b918-2995739885f2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Routing

- [Axios: Routing is coming for the frontier AI labs](https://substack.com/redirect/596d584d-256f-4cfb-baf3-f1c474e92b54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #142: Stripe’s OpenRouter Buy, in ‘Hidden Figures’](https://substack.com/redirect/8da6a037-01df-43e6-9168-731aefc75477?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #483: The other AI open to close battle](https://substack.com/redirect/a702eb07-a72d-4017-ae9c-922ad914e346?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: the new Mac minis and Studios

- [WSJ: There’s a New Mac Mini and Mac Studio](https://substack.com/redirect/96b795b8-00fe-4061-95a2-ea481ed2d57f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Apple Newsroom: the new Mac mini](https://substack.com/redirect/ec63490d-eec7-461b-b4b7-c9ba16376209?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Apple Newsroom: the new Mac Studio](https://substack.com/redirect/9e4f6339-2af6-4734-a4db-06dec7dac756?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: Apple’s M6 chip](https://substack.com/redirect/603ccb60-4a68-4ca3-8a42-823be2980aab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1145: ‘RAMageddon’ really here to stay](https://substack.com/redirect/3d652366-51aa-43d3-8f08-ea9f909ed132?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1016: OpenClaw and the Mac mini run](https://substack.com/redirect/da65a563-1003-4294-81ab-9d95a5dadeb3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### OpenAI’s Jalapeño Inference Chip

### The OpenAI vs Anthropic Compute Race

### Apple’s Mac minis, Ahead of iPhones

### New Mac minis, Despite RAMageddon

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
