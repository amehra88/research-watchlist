---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260910050300.3.c1d22ca8d24bb071@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-rtz@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-coding-has-a-compiler-coworking
source_date: '2026-09-10'
subscription_tier: free
tickers: []
themes:
- model_efficiency_evolution
- frontier_model_competition
- enterprise_ai_adoption
- ai_agent_monetization
- model_commoditization
ingestion_date: '2026-09-11'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Coding has a Compiler. Coworking has None. AI-RTZ #1205](https://substack.com/app-link/post?publication_id=684161&post_id=214787037&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNDc4NzAzNywiaWF0IjoxNzg5MDE2ODU0LCJleHAiOjE3OTE2MDg4NTQsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.txDGw3sGePrtgHuf5b0piSm6FyJSuBtXsdE4G6i606o)

### ...the bigger half of the AI Coworking market cannot measure what it buys. METR and Anthropic’s data show why.

Every model launch this year has arrived with a benchmark chart. Very few of them tell you whether the model will be better at your job. All as the globally [white-hot AI Coding](https://substack.com/redirect/df3f89bc-c982-4c03-966f-8897f444bafb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) market zips along.

That is not a marketing problem. It is a measurement problem, and it splits the AI market cleanly in two.

On one side sits AI Coding, where the work checks itself. On the other sits everything else, which I will call AI Coworking. It is the far larger market, and it has no speed test.

It’s how billions around the world will use AI products in their daily work and personal lives. Bill Gates used to call it ‘[knowledge workers](https://substack.com/redirect/8541cc2d-83d3-4a05-8e38-2a2dfb532a06?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’ and the PC industry called it ‘[productivity software](https://substack.com/redirect/384ddaf9-8ed6-4923-a41d-c2e4097a48c2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’. Steve Jobs of course called the computers and the software ‘[bicycles for the mind](https://substack.com/redirect/ecdc5886-60e6-4231-bd2b-8c15a07e75b4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’.

Like I said, a far bigger market than AI Coding for tens of millions of developers today. Driving two trillion-dollar-plus mega-AI IPOs. Collectively ‘earning’ over $150 billion in revenues this year, and likely over $300 billion next.

Perhaps half of that revenue is AI Coding today, from a few tens of millions of developers. The rest is the AI Coworking bucket above, hundreds of millions of users now, billions to come. Both growing fast. Only one of them has a ceiling.

Why this matters for the [AI Tech Wave](https://substack.com/redirect/7dd57355-cc60-4055-8dc5-363b7ef682be?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in my words:

> The industry’s entire public scoreboard is built on the part that can be measured, and sold to the bigger part that cannot.

It is also the ground floor of a three-part series of posts going into this weekend.

Tomorrow and Sunday go to the other end of the AI World, where the people building these models are writing essays about losing control of them, and in one case this week, quitting the industry over it.

Hold this piece next to those. The gap between the two is the misunderstood reality of AI in 2026. Up and down the [AI roadmap](https://substack.com/redirect/8aa7027c-00ae-4854-9fb3-cc5852f6dcfc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

The sharpest version of this came from a professor, not from a lab

Angela Aristidou, a professor at University College London, laid it out in MIT Technology Review, in [AI benchmarks are broken. Here’s what we need instead.](https://substack.com/redirect/a21789f4-7e90-48a1-87e4-a81222aae521?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “AI is almost never used in the way it is benchmarked. (Angela Aristidou, professor at University College London, in [AI benchmarks are broken. Here’s what we need instead.](https://substack.com/redirect/a21789f4-7e90-48a1-87e4-a81222aae521?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), MIT Technology Review, March 31, 2026)”

Her example is medical imaging. Models cleared at 98% accuracy on the benchmark, then introduced delays once they were inside a hospital, because the benchmark never modeled how a multidisciplinary team actually reaches a decision.

She has a name for what follows. An AI graveyard. Systems that scored well and got abandoned anyway.

The evals question is an old thread here, discussed at length, and it has never been solved.

> “So then there is also the urgent need to measure how well these models work WITH each other. In other words, their ‘interoperability’. ([AI-RTZ #582, Scaling AI Evaluations](https://substack.com/redirect/de8d0f89-5dbf-41cc-90a7-e586f0bb7a42?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), December 2024)”

AI Coding has a compiler, and that is the entire advantage

Code compiles or it does not. Tests pass or they fail. The build breaks in ten seconds, and it breaks in front of you. It is binary. Zeroes and ones. It adds up or it does not.

An AI Coder gets a verdict on every turn. Free, immediate, and not a matter of taste.

That is why AI Coding went first. Not because it is the most valuable work in the world.

Because it is the most measurable work in the world. Checkable, in other words.

The advantage has almost nothing to do with the skill of the people using it. It is a property of the work at hand.

Everything else is far harder to measure with any precision

Consider what most other purchases of goods or services in the economy hand you.

Consumer goods carry labels and standards.

Broadband has a speed test, so you can catch a provider throttling the bandwidth you paid for.

Healthcare has the hardest measure there is, which is whether the patient improves.

Now consider a memo. A market analysis. A research summary.

A plan for the week. For work or for fun.

Two models produce two versions. Both are plausible. Both read well. Both cite things.

There is no compiler. There is no speed test. There is no patient.

What is left is a feeling. And the next section is about how much feelings are worth here.

Even the coders’ own numbers do not say what coders think

[METR (Model Evaluation and Threat Research)](https://substack.com/redirect/751517bf-506b-4b82-aac6-6e5446421f26?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) ran a randomized trial with sixteen experienced open-source developers, working real issues in repositories they already knew well.

> “When developers are allowed to use AI tools, they take 19% longer to complete issues. ([Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://substack.com/redirect/c93f5400-3b37-40ab-a82a-c03385a8b873?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), METR, July 10, 2025)”

Beforehand, those developers predicted AI would make them 24% faster.

Afterward, having actually been slower, they still believed it had made them 20% faster.

Read the gap again. Roughly forty points between what was measured and what was felt. In the one domain where measuring is easy.

METR is careful about the limits, and so am I.

Sixteen developers. Mature repositories. Around fifty hours of prior experience with the tool. This is not the final word on AI Coding productivity, and it has been argued about all year.

But it is a hard result for the rest of us to walk past. If people holding a stopwatch and a test suite can be off by that much, the rest of us are not going to do better on intuition.

The market that cannot measure is the bigger one

Anthropic publishes research on who uses Claude and for what.

> “Computer and Mathematical occupations are the most heavily over-represented, making up roughly 30% of survey respondents. ([Anthropic Economic Index report, Cadences](https://substack.com/redirect/7adb6c69-2f07-41e5-91ea-0b51a7c96ec4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Anthropic, June 26, 2026)”

Those occupations are roughly 4% of US employment. On Claude, the most developer-weighted of the major assistants, they run at about seven times their share of the workforce.

And they are still under a third of the respondents.

Which means roughly seven in ten users, on the most coder-heavy assistant in the market, are doing work with nothing attached that can grade it.

Then widen the lens past the two US frontier labs.

Open weight models from China and elsewhere are chasing those same users, at prices an order of magnitude below the top tier.

Every one of those companies, closed and open, US and Chinese, is selling into a market that cannot grade the product.

I wrote about that fork earlier this year, from inside it.

> “Mainstream folk worldwide, are at a fork in the road. Being inundated with all things AI every day, and trying to figure out IF and HOW to make it a part of daily life and work. While the coders and VCs seem to be having all the fun. ([AI-RTZ #1054, Working out daily with AI and AI Agents](https://substack.com/redirect/b2f2052d-0edb-4932-bf85-63e3e5f852db?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), April 2026)”

When you cannot verify, price becomes the signal

Economists have a name for a good whose quality the buyer cannot judge before purchase, during use, or afterward.

A [Credence Good](https://substack.com/redirect/fe4318f6-4b0f-433b-8fff-479426b58c3b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Faced with one, a careful buyer does the only rational thing left. Read price as the quality signal. If the top tier is affordable, buy the top tier.

That is not a consumer error. It is what you do when verification is unavailable and the cost of being wrong is invisible.

I do it myself, and I have said so in print, running the top subscriptions across several of these systems.

> “Today’s discussion is about what AI models cost in this [AI Tech Wave](https://substack.com/redirect/7dd57355-cc60-4055-8dc5-363b7ef682be?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and about two opposite things being true at the same time. The pricing spectrum for AI globally is widening at both ends. ([AI-RTZ #1169, The ‘Race to Zero’ that really Isn’t](https://substack.com/redirect/d9ae899d-3591-4b4b-a049-8e3bba19267d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), August 2026)”

Here is the part worth absorbing in all these AI debates on cost vs worth.

The segment that cannot verify is the segment least likely to ever trade down. Trading down would require evidence, and the evidence does not exist.

That is a durable pricing position. Both mega-AI IPO candidates walk into their filings holding it, and neither prospectus will describe it that way.

Which existential risk are we actually discussing

This connects to the essays I have been working through this week.

The frontier lab essays frame risk in general terms, as though capability arrives everywhere at once.

Look at where the concrete, near-term versions actually live and they cluster in the quantitative domains. AI Coding and cybersecurity, where capability is checkable, consequences arrive fast, and an error executes rather than merely reading badly.

Everywhere else, the pace will be slower than the essays imply. Not because the models are weak. Because adoption is gated on verification, and verification does not exist yet.

An organization cannot safely hand over work it has no way to grade. That is a governor on deployment, and it is a stronger one than most of the risk writing accounts for.

Put that next to this week’s AI news.

An Anthropic researcher [told the Wall Street Journal](https://substack.com/redirect/3b10f76b-de1d-49a0-85b0-dfb63e9aae84?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on Tuesday that he is leaving the industry because he expects self-improving systems to be out of control by the end of next year.

More than a thousand researchers, including the chief scientist of OpenAI and the CEO of Anthropic, have signed a call for governments to build a brake pedal.

I take the sincerity at face value. But read this piece first, then read theirs. The models those fears describe are improving themselves inside a lab, on compute nobody else has.

A small example from my own desk this week. I was working with the most expensive tier of Anthropic’s Claude, in its Cowork mode. Anthropic being one of the two US frontier labs. Over $200 a month.

Sold as the best AI in the world.

I asked it to quote five short passages from a public essay, with full attribution and links.

Standard practice for every scholar, journalist and writer since printing.

It declined. Not because it could not. Because a rule sitting on top of the model told it not to, and the rule cannot tell a footnoted quotation from a copyright violation.

Meanwhile the founders and chief scientists of these same labs warn, in essay after essay, that this class of system will soon be breaking into critical infrastructure around the world.

Both of those things are true at once.

The governance gate that exists today is aimed at the person writing a memo.

The capability the essays fear lives in a lab, behind no such gate. That is the whole AI Coworking problem in miniature.

A finite rule, written for a real risk, firing on the wrong case, with no way to appeal it, and no way for me, the customer, to measure what was lost. Or what I thought I had bought in the first place, when I signed up for the top subscription to the ‘best model’.

No fine print anywhere saying the most basic thing a writer does was off the table.

And the models the rest of us use cannot yet tell us whether the memo they wrote is any good. The distance between that and the essays’ scenarios is measured in years of ordinary engineering, the kind every prior tech wave needed, and got.

> “There is no single switch to flip. Thousands of models, used by billions of people, soon generating multiple billions of AI agents. Open and closed, across every border and vendor. ([AI-RTZ #1183, Not one Skynet, but Billions of AI Agents](https://substack.com/redirect/2df7bd64-b7f9-40d4-9476-fef61d68d2b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), August 2026)”

My Take

AI Researchers live in the future, with ‘God-like’ AI Compute. The rest of us live as humans, not Gods. With ordinary AI Compute. With arbitrary rules that restrict their use at the whims of the AI Gods.

The benchmark critique itself is not underreported. Researchers have been making it for two years, and [MIT Technology Review ran it as an opinion essay this spring](https://substack.com/redirect/a21789f4-7e90-48a1-87e4-a81222aae521?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

What gets less attention is the connection between three things that are usually discussed apart.

Verification is easy in one domain and absent in the others. The domain where it is absent is the bigger market. And in that market, price is doing the job that proof cannot.

Put those together and the industry’s scoreboard looks different.

It measures the smallest, most checkable slice of the work, and the results are sold to everyone else as though they transferred.

I want to be careful about what I am not saying.

I am not saying the models have stopped improving, and I am not saying the top tier is not worth its price. I cannot demonstrate either claim, and neither can anyone selling to me.

That is the actual finding.

In my own daily production work I have no instrument, so I have started building one. Not a benchmark. A checklist that runs, on my own output, and returns numbers instead of impressions.

That is the practical move available to anyone in the seven in ten. Decide what “better” means for your own week, write it down, and measure it. Once you can measure it, the price question answers itself.

Until AI Coworking gets its own compiler, price will keep standing in for proof in much of the [AI Tech Wave](https://substack.com/redirect/7dd57355-cc60-4055-8dc5-363b7ef682be?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). That’s the reality gap we need to adjust for going forward. Stay tuned.

## Sources and further reading

Primary

- [AI benchmarks are broken. Here’s what we need instead.](https://substack.com/redirect/a21789f4-7e90-48a1-87e4-a81222aae521?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Angela Aristidou, MIT Technology Review, March 31, 2026

- [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://substack.com/redirect/c93f5400-3b37-40ab-a82a-c03385a8b873?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), METR, July 10, 2025

- [Anthropic Economic Index report: Cadences](https://substack.com/redirect/7adb6c69-2f07-41e5-91ea-0b51a7c96ec4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Anthropic, June 26, 2026

- [Anthropic Researcher Quits Over ‘Out-of-Control’ AI Fears, Amrith Ramkumar, The Wall Street Journal, September 8, 2026](https://substack.com/redirect/3b10f76b-de1d-49a0-85b0-dfb63e9aae84?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Quoted above, from these pages

- [AI-RTZ #582: Scaling AI Evaluations (‘Evals’)](https://substack.com/redirect/de8d0f89-5dbf-41cc-90a7-e586f0bb7a42?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1054: Working out daily with AI and AI Agents](https://substack.com/redirect/b2f2052d-0edb-4932-bf85-63e3e5f852db?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1169: The ‘Race to Zero’ that really Isn’t](https://substack.com/redirect/d9ae899d-3591-4b4b-a049-8e3bba19267d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1183: Not one Skynet, but Billions of AI Agents](https://substack.com/redirect/2df7bd64-b7f9-40d4-9476-fef61d68d2b6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers

- [AI-RTZ #351: Evaluating AIs](https://substack.com/redirect/4aca601d-be5b-4a6b-a47d-a457c1f38832?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1167: ‘Forever Problems’ like Prompt Injections still being ‘Solved’](https://substack.com/redirect/dcf5f921-102e-48cd-83ba-f1c118274f4f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #847: Microsoft and Salesforce Sweating Enterprise AI Adoption](https://substack.com/redirect/bbf2cdd9-ac33-4d60-967a-d0c203558810?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #156: ‘Lots More Apples and Oranges’ in AI](https://substack.com/redirect/3a2869f8-61c1-4e39-ac9f-e15c26f0c0cf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #996: Resurgent AI Fears from AI Researchers](https://substack.com/redirect/7a07365b-3823-47bb-aed1-530ba95fcd92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
