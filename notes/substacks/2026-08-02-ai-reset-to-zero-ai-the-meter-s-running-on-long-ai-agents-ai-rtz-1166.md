---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260802050208.3.d1f7d97644f29054@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-meters-running-on-long-ai
source_date: '2026-08-02'
subscription_tier: free
tickers:
- AAPL
- GOOGL
- META
themes:
- ai_agent_monetization
- inference_compute_economics
- foundation_model_economics
- frontier_model_competition
- agent_framework_landscape
- enterprise_ai_adoption
- model_efficiency_evolution
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: ‘The Meter’s Running’ on Long AI Agents. AI-RTZ #1166](https://substack.com/app-link/post?publication_id=684161&post_id=209350340&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwOTM1MDM0MCwiaWF0IjoxNzg1NjQ3MTY3LCJleHAiOjE3ODgyMzkxNjcsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.O9w5yjAOxI4L_KnKiP6woHDleKG3GyVG9gUo0YZDxgY)

### ...OpenAI’s Astra, Anthropic Opus 5, and other rising token bills.

The Bigger Picture, Sunday, August 2, 2026

The next thing the frontier AI labs are selling is time.

Not smarter answers in a second. Longer runs. Agents that keep working for hours, then days, then weeks, even months. OpenAI previewed a model family called Astra, built for exactly that this week. Anthropic is already describing runs measured in weeks with its newest models in the Mythos/Fable/Opus 5 families. All focused on the AI Coding, Enterprise, and broad professional productivity spaces. It is the clearest shared direction across the labs since reasoning models, and it is worth a ‘[Bigger Picture’](https://substack.com/redirect/9d9b38fe-3a67-4860-a714-2ba2dd58c602?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) this [AI Tech Wave](https://substack.com/redirect/477f8bb2-1e6f-424b-9fbf-7e206217742e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) Sunday.

But there is a second thing that gets longer when the AI Agent run gets longer. The bill.

That is the part I want to unpack today.

Start with what was announced.

The Information reported Friday in [“Exclusive: OpenAI Previews ‘Astra’ AI Model in DC”:](https://substack.com/redirect/9ddfd75a-dfa3-4c84-923b-d21d89ad876e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “OpenAI is preparing to release a new model family, tentatively using the name ‘Astra,’ with improved abilities to complete long-running tasks, according to three people briefed on the plans.”

Founder/CEO Sam Altman demonstrated it to policymakers and regulators in Washington DC this week. The pitch was not a benchmark score.

> “OpenAI touted its abilities to have multiple agents work together over a long period of time to solve particularly hard problems, which could be applied to a project or advanced math problem.”

Astra would sit alongside Sol, Terra and Luna as a new class. OpenAI has not settled on whether it is GPT 6 or another entry in the GPT 5 series. And the models are intended to be the first to go through the administration’s planned pre-release review framework, which is a story of its own for another day.

OpenAI followed that on Saturday with [an official publication of its own](https://substack.com/redirect/4312207a-abeb-4354-95e5-5979e00fb547?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and it is the most useful thing anyone put out on this all week. Ten problems in mathematics and theoretical computer science that had seen no progress on the main result for at least a decade, and in most cases far longer.

> “The results were achieved by an internal version of Astra, our next major model. The total number of tokens needed to find solutions to these problems would cost roughly $2,000 at Sol API rates.”

Two thousand dollars. Expensive and a bargain at once, and that is the dimension long-running metered AI Agents have to be measured against.

As a return on compute it is remarkable. Decade-old problems in sphere packing, group theory and lattice cryptography, for the price of senior technical talent for a spot.

And it is also, unmistakably, a meter reading. A frontier lab publishing a research result and volunteering what the tokens cost is a new thing. That is not a benchmark score. That is an invoice worth judging against relative value. Every time.

Anthropic is describing the same shape from the other side.

Boris Cherny, who leads Anthropic’s ‘white hot’ global AI Coding sensation Claude Code, [described Opus 5 in a Y Combinator interview](https://substack.com/redirect/3f12742f-65a6-47e6-8fcc-46c38b97871f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) published July 27.

He laid it out as a model that runs for a very long period of time, and can go for days, weeks, or months at a time. He described a Swift rewriting project that had been running for two weeks, spawning thousands and then tens of thousands of agents underneath it.

He put a number on the change in a [written Q&A with Platformer](https://substack.com/redirect/7dae7efc-8466-4927-aac1-72f08707e712?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) back in May, and it is the clearest measure of the long running AI Agent shift I’m discussing:

> “A year and a half ago, Claude Code could run maybe 30 seconds before going off the rails. Now every night I have hundreds, sometimes thousands of agents running 5, 10, 20 hours.”

Thirty seconds to twenty hours, in eighteen months. That is the curve the labs are extrapolating from. That’s another form of ‘AI Scaling’ not contemplating by most AI Researchers a couple of years ago. The ‘scaling’ discussion then had been limited to data and compute.

And his advice for getting there was refreshingly candid. Give the model the task. Give it a way to verify its own output.

So the direction is not in dispute. Both leading labs are pointing at the same thing, from the model side and from the tools side. Long-horizon, multi-agent, self-verifying work.

Now the part that gets less attention and discussion.

Every one of those hours is AI inference. Needs AI Compute at various tiers of pricing. Sometimes across AI models of various types, closed to open.

Every sub-agent running reinforcement, reasoning, learning loops to answer the user prompt with millions of compute cycles, is its own token stream. Every verification loop is a second pass over work that was already paid for once. Reinforcement learning made the models better at long tasks by teaching them to try, check, and try again. That is a capability gain and a cost structure at the same time.

This is the thing that keeps making AI unlike the software business that came before it. In classic software, you built it once and the marginal cost of the next customer rounded to zero. That is what made the margins.

In AI, the marginal cost of the next hour is real, it is metered, and with agents it does not stop when the human walks away.

One other item to address. The variable cost of AI compute is often discussed in general discussions as being similar to electricity when it started to change the world. And is of course critical to the world today.

But electricity does not vary at the end user points in price and quality. The electricity running your toaster is the same as the current running your computer.

AI compute tokens are intricately mapped by AI coders and businesses.

Every AI model comes in dozens of setting combinations. Model X and low, medium, high and sometimes super-high settings. All at different prices, and rate limits on subscription plans. All have to be watched closely by the user.

So as not to get [‘Tokenmaxxing’](https://substack.com/redirect/b4607c73-cfef-4418-aa82-5043dd29a1f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) shocks way off the Token budgets. Call it ‘Combinatorial Compute’. Against the one price, one type electricity powering our work and home lives. I got into the cognitive load it creates back in [ARD #117](https://substack.com/redirect/e7099f4f-d99f-477e-93c1-c2923fef44d1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

I’ve been calling this the [a la carte problem](https://substack.com/redirect/b4607c73-cfef-4418-aa82-5043dd29a1f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for a while now, and businesses hit it first. Consumers will be next soon as they really start to use AI Agents. I [discussed yesterday](https://substack.com/redirect/488355d2-5212-4426-b798-441fb8663676?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) how Meta’s [Mark Zuckerberg is laser-focused](https://substack.com/redirect/adabfcb3-5b5e-4229-a8ea-1a911106e8d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)on that step to [use his burgeoning Nvidia powered AI Compute](https://substack.com/redirect/5257814b-2afe-4956-9559-4a06b48d53e4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) data centers.

Back in May, [Axios](https://substack.com/redirect/2deef44e-0979-4a54-93a2-4ec0551460e3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) laid out the corporate version of it. An AI consultant described a client that spent half a billion dollars in a single month after failing to put usage limits on Claude licenses for employees. Microsoft cancelled most of its Claude Code licenses, in part over cost. [Uber’s COO said AI costs](https://substack.com/redirect/3270e5ec-d6f8-45d4-bf3c-2f3d7dd788fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) were getting harder to justify. And one line from that piece has aged particularly well:

> “Enterprise AI plans are not truly ‘all you can eat,’ and even simple chatbot queries can carry heavy token costs.”

That was written about employees checking the weather with a frontier model. It was not written about an agent that runs unattended for two weeks.

I’ve walked through the vendor side of this in [Velvet Rope AI](https://substack.com/redirect/f6aaef21-1dbd-4daa-b8db-88f24c74813a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), in [AI Price Umbrellas](https://substack.com/redirect/a91dafd8-acbf-4db8-a6d2-c0c0826ef305?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and in the [all-you-can-eat agent pricing](https://substack.com/redirect/fdc1affb-0bc2-4790-96f3-bbd52b2c8d99?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) piece before that. The pattern across all of them is the same. Flat pricing is a promise made before anyone knew what the usage would look like.

And now it is arriving for consumers as well.

This is the newer development, and it happened quietly this summer while everyone watched earnings.

[Apple’s](https://substack.com/redirect/ebbcbb1e-445a-4773-bc2c-93721b7a2b55?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) [own June announcement](https://substack.com/redirect/d99ad5e0-9b29-4006-ac3c-5415c6e73374?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) at [WWDC 2026](https://substack.com/redirect/3ee6ed77-05ac-4a1c-a115-b684e9d29464?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) said it plainly. Some Apple Intelligence and upcoming Siri AI features have daily usage limits because they lean on server models. And increased access comes with most iCloud+ plans. That is metering, shipped, in the most consumer product there is. Across Apple’s unique platform surface serving Siri AI and Apple Intelligence to billions soon.

Tim Cook then said the quiet part on the [earnings call Thursday](https://substack.com/redirect/b6161ce5-4354-4397-ae8a-587ed0f10e8f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), in his last one as CEO for fifteen extraordinary years. Asked about the compute cost of the new Siri:

> “We do believe there will be people that want to use it a lot.”

And on how that gets paid for, he pointed at upgrade possibilities on iCloud+ where people can buy up the stack. He was also candid that this is not finished thinking:

> “It’s obviously early going for us, and so I don’t want to say that we have a complete plan for that.”

[Google moved first](https://substack.com/redirect/c1d6c3d5-a722-4dd3-b250-fa9ddd0b5331?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and moved further. In May it told Google One subscribers it was moving from daily prompt limits to a compute-used model, with top-up credits you can buy when you run through your allowance. [Anthropic now sells usage bundles](https://substack.com/redirect/de59e44c-7240-4db7-8f42-d09bc7500376?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to individual Pro and Max subscribers. [OpenAI has credits](https://substack.com/redirect/fd0d8427-0218-4d74-ba04-2ef28f5ec08e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on its consumer tiers for the heavier features.

None of these were announced as price increases. All of them are the same move. The unit of AI pricing is drifting from the seat to the meter.

There is a fair objection to all of this, and it belongs on the table.

Per-unit AI prices are falling, not rising. OpenAI [cut prices on two of its GPT-5.6 models](https://substack.com/redirect/b95b7142-4275-4aa4-b8e3-4fac579d2f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on Thursday, just three weeks after launching them. Luna, the fastest and cheapest, came down roughly 80%. Terra, the mid-range, 20%. It [cut ChatGPT prices for consumers too](https://substack.com/redirect/14bc0ea5-e136-40ab-9415-330fc9478799?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), with Sam Altman citing customer cost concerns.

But look at which one did not move. Sol, the most powerful version, held its price. That is the tier long-running agents actually run on.

And falling unit prices and rising total bills are not in conflict. They are the same story. Cheaper tokens are exactly what makes it reasonable to let an agent run for two weeks instead of two minutes. The bill is price times volume, and it is the volume that is moving by orders of magnitude. I’ve called it [‘making it up in volume’](https://substack.com/redirect/57ab915f-4a02-4154-8bfb-e0bc8a86080f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) before.

> “OpenAI and Anthropic have both adjusted pricing, rate limits and other usage policies as newer reasoning models consume far more tokens during longer-running agentic tasks.”

That is [Axios on Thursday](https://substack.com/redirect/b95b7142-4275-4aa4-b8e3-4fac579d2f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Which brings me to the part that I think is least appreciated.

The people telling us most confidently that AI will soon do all the jobs are, almost without exception, people who do not personally see a meter.

I’m referring in particular to the AI Researchers and engineers at the frontier lab companies, and their biggest customers/partners.

They all live in the near future. Not our present.

The way they talk about how great AI is about to be is based on their ability to ‘live in the future’ with the latest unrestricted models. With near-unlimited amounts of compute and token budgets at their fingertips and voice commands.

It has a bit of ‘[Let them eat Cake’](https://substack.com/redirect/c076bcd0-e596-4247-aef6-49502856959e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) sheen when they talk about the AI future coming soon for mainstream mortals. With humbler budgets.

That is not a character flaw and I don’t mean it as one.

Frontier researchers and the coders closest to them work inside effectively unmetered compute budgets. It is the correct thing for their employers to do. You do not want your best people rationing tokens.

But it does mean their lived experience of AI is a different product than the one the rest of the world is being sold. When you can spawn tens of thousands of agents to rewrite a codebase over two weeks and never think about what that cost, the question “will this replace a job” looks purely technical.

For everyone outside that budget, it is a technical question and a price question, and the price question is the one that decides. And will likely take decades to be available to most at scale. As the [multi trillion dollar compute](https://substack.com/redirect/68e8b901-d126-4e6f-80da-d231c3bdf116?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) gets built through this decade and beyond. Goldman Sachs Research puts that at a combined $5.3 trillion of capital spending from 2025 through 2030, from the big technology companies leading the buildout alone.

AI Coding is the one place where the math already works. That was true [when I wrote about it in May](https://substack.com/redirect/b4607c73-cfef-4418-aa82-5043dd29a1f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and it is still true. The value of a senior engineer’s hour is high enough that a lot of tokens fit underneath it. That is why coding is where the coveted ‘product-market-fit’ gold was found first, and it is also why coding is a poor guide to everything else.

The interesting question for the next few years is not whether agents can run for weeks. Astra and Opus 5 suggest they can, or nearly can. It is which tasks are worth a week of metered compute, and who is holding the bill when the answer turns out to be no.

So where does all this come down

I’d put it probabilistically, the way I try to with anything blending technology and finance driven decisions.

Over a multi-year horizon, I think it is more likely than not that AI pricing settles into something closer to utilities and cloud than to seats and software. Some base allowance. Metered usage above it. Tiers that exist because the underlying cost is real, not because the vendor is being greedy. Apple, Google and Anthropic have all moved that way within the last three months without saying so out loud.

I’d also expect the first genuine consumer backlash of this era to be about a bill rather than about safety. People forgive a lot from a product. They do not forgive a surprise invoice.

And I’d expect the labs to keep pushing on long runs anyway, because it is the right technical direction and because the demos are extraordinary.

Both things are true. The agents are getting longer times to run. So is the meter with variable pricing for tiers and capabilities. And confusing cognitive loads for users to sort out daily in their work and personal lives.

That is a ‘[Bigger Picture](https://substack.com/redirect/9d9b38fe-3a67-4860-a714-2ba2dd58c602?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’ worth absorbing this weekend, in this [AI Tech Wave](https://substack.com/redirect/477f8bb2-1e6f-424b-9fbf-7e206217742e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Stay tuned.

## SOURCES

Primary, this post:

- The Information, Erin Woo, Leo Schwartz and Stephanie Palazzolo, July 31, 2026 — [Exclusive: OpenAI Previews ‘Astra’ AI Model in DC](https://substack.com/redirect/9ddfd75a-dfa3-4c84-923b-d21d89ad876e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- OpenAI, August 1, 2026 — [Ten advances in mathematics and theoretical computer science](https://substack.com/redirect/4312207a-abeb-4354-95e5-5979e00fb547?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) — the official Astra publication, with the token cost

- Y Combinator, Boris Cherny interview, published July 27, 2026 — [YouTube](https://substack.com/redirect/e1d96276-9406-4cb9-b626-c56349889af6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · [show page](https://substack.com/redirect/1d4e9be2-9838-47cb-a6a7-0d324d1a4fac?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Apple Q3 FY26 earnings call, July 30, 2026 — [full transcript, Six Colors](https://substack.com/redirect/b6161ce5-4354-4397-ae8a-587ed0f10e8f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) · [Axios writeup](https://substack.com/redirect/20f7e75e-5a21-4352-a59c-890672ff50bf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Apple Newsroom, June 8, 2026 — [next generation of Apple Intelligence and Siri](https://substack.com/redirect/d99ad5e0-9b29-4006-ac3c-5415c6e73374?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Google, Shimrit Ben-Yair, May 19, 2026 — [Google AI subscriptions moving to a compute-used model](https://substack.com/redirect/c1d6c3d5-a722-4dd3-b250-fa9ddd0b5331?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Anthropic, updated May 18, 2026 — [usage bundles for Pro and Max](https://substack.com/redirect/de59e44c-7240-4db7-8f42-d09bc7500376?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- OpenAI — [credits for flexible usage on consumer plans](https://substack.com/redirect/fd0d8427-0218-4d74-ba04-2ef28f5ec08e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Axios, Ina Fried, July 30, 2026 — [OpenAI cuts GPT-5.6 prices](https://substack.com/redirect/b95b7142-4275-4aa4-b8e3-4fac579d2f20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- WSJ, July 2026 — [OpenAI Cuts ChatGPT Prices as Sam Altman Cites Customer Cost Concerns](https://substack.com/redirect/14bc0ea5-e136-40ab-9415-330fc9478799?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- Goldman Sachs, June 12, 2026 — [Private Markets Are Expected to Have a Growing Role in Data Center Financing](https://substack.com/redirect/68e8b901-d126-4e6f-80da-d231c3bdf116?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) ($5.3 trillion hyperscaler capex, 2025–2030)

For more curious AI readers, MP’s own ‘prior discussed’ threads on this topic:

- [AI: Customers asking ‘how much’ for AI tokenmaxxing. AI-RTZ #1103](https://substack.com/redirect/b4607c73-cfef-4418-aa82-5043dd29a1f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) — the a la carte piece, May 31, 2026

- [AI: Anthropic & OpenAI’s ‘Velvet Rope AI’ upgrade Drift. RTZ #1064](https://substack.com/redirect/f6aaef21-1dbd-4daa-b8db-88f24c74813a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI Price Umbrellas Getting Larger. ARD #114](https://substack.com/redirect/a91dafd8-acbf-4db8-a6d2-c0c0826ef305?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Meta’s ‘Good Enough’ AI, and new ‘All-You-Can-Eat’ AI Agents Pricing](https://substack.com/redirect/fdc1affb-0bc2-4790-96f3-bbd52b2c8d99?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: It’s Business and Personal in OpenAI/Anthropic pricing](https://substack.com/redirect/2b98cd5f-ecf3-48f5-a97c-85dc8025bf6a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Long road ahead for AI Agents for enterprises and consumers. RTZ #494](https://substack.com/redirect/6cc0286a-be5d-45aa-8e87-72f2755ffe50?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Fragility of today’s Claude Cowork type AI Agent Apps](https://substack.com/redirect/3e44ff27-87fb-4550-a673-6a66121adcdd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: AI Agents increasingly need an Internet of their own](https://substack.com/redirect/1e38310c-2f1f-4222-beb8-7ba4d7fc8f15?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: US frees OpenAI 5.6 vs Anthropic Claude Fable 5. AI-RTZ #1142](https://substack.com/redirect/40a0fd9e-9b22-4bf7-9174-66912f19bba3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Anthropic recasts Mythos as Fable 5, with safety & pricing gates. AI-RTZ #1114](https://substack.com/redirect/bd0b7846-6907-4f4a-bee4-6a9e9e249013?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Too Much of a Bad Thing is a new thing in AI. ARD #117](https://substack.com/redirect/e7099f4f-d99f-477e-93c1-c2923fef44d1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) — the ‘Combinatorial Compute’ math, July 13, 2026

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/8fd45c69-3169-4cba-8c54-1363f292277d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))
