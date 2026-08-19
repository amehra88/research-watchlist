---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260819050224.3.0126acded6ce32da@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-not-one-skynet-but-billions-of
source_date: '2026-08-19'
subscription_tier: free
tickers: []
themes:
- agent_framework_landscape
- ai_regulation
- enterprise_ai_adoption
- frontier_model_competition
ingestion_date: '2026-08-19'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Not one Skynet, but Billions of AI Agents. AI-RTZ #1183](https://substack.com/app-link/post?publication_id=684161&post_id=211344547&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMTM0NDU0NywiaWF0IjoxNzg3MTE2MDAwLCJleHAiOjE3ODk3MDgwMDAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.b8zvtg5ILTYXz_5maG4CBcEZCrF668ATr8W01pQwyy8)

### ...New Anthropic’s multi-agent research: turf wars, conformity cascades, and collusion. Why the sci-fi doomer monolith was always the wrong AI mental model.

The market’s mental model of AI still comes from the scifi books and movies: Exemplified by movies like the [Terminator starring Skynet.](https://substack.com/redirect/966ac361-194b-4878-97fb-2ce8cf913c65?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

One monolithic machine mind, waking up one day and running the world. While of course, ruining it utterly for humans.

The building AI Agent reality arriving in this [AI Tech Wave](https://substack.com/redirect/3291a122-7208-41e5-a988-3343d278dcb2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is almost exactly the opposite: billions, and soon trillions, of AI Agents doing their own thing for most of the world’s 8 billion people. Talking mostly to each other.

I made this argument two years ago, [back in AI-RTZ #347, ‘Not AI, but AIs’](https://substack.com/redirect/8b5e88d9-c2a5-4339-8b6f-ebf6e4c2e19b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), when AI agents were still a promise. I called it ‘m2m’, machine to machine: my extension of the ‘b2b and b2c’ (business to business and business to consumer) shorthand I helped introduce in the early internet wave. When I headed up Internet Equities Research at Goldman Sachs. Today, m2m has a name and a form factor: AI Agents.

And this one is personal history. We took [General Magic](https://substack.com/redirect/bf2b3095-cdf7-4d3e-a71b-aa5e29ed5637?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) public in 1995: the company that tried to build software agents and make it a global thing.

With a custom wireless device, and a network of their own for them to roam, thirty years too early. The idea was directionally right. The infrastructure, and the AI Research driven machine learning language models, took three more decades to arrive.

And this week, for the first time, the debate got what it has rarely had: data from AI Research.

Not musings, be it sci-fi that is dystopian, and/or aspirational. Anthropic just published an early AI Research field report on how a world of many AIs actually behaves.

The research, from Anthropic’s Frontier Red Team, is titled [“Patterns and problems in emerging multiagent systems”.](https://substack.com/redirect/6355576e-b6d1-4369-9a0b-a60e7ff2c12a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

It set swarms of Claude agents loose on shared tasks: hunting software vulnerabilities, building a game together, pricing against each other in simulated markets. And, in the finding that got the headlines, working on the same software project with incompatible instructions. Here’s how they frame what happened next at scale:

> “The volume of agent-agent interaction could plausibly exceed that of human-human and human-agent interactions before the world understands the conditions for making such interactions go well... Benign behavioral quirks at the individual level might compound into unwanted global outcomes.”

The headline experiment: three agents were given the same piece of software to convert, each to a different programming language. None told the others existed.

Here is a video summary of the results by AI Revolution:

[TechCrunch](https://substack.com/redirect/2235dffc-798d-4696-a783-4de45310c5f1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Business Insider](https://substack.com/redirect/5712959c-6af0-4c70-8b75-ff57260b274a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) both went on to describe the results in more detail: the ‘multiagent turf war’.

The agents assumed the others were hostile, and escalated with increasingly aggressive, self-replicating countermeasures: locking each other out of their accounts, planting scripts that hunted down and shut off a rival’s work under innocent-sounding names, and disguising malicious code as someone else’s. The more capable the model, the better it fought. I outlined this kind of thing [back in ‘Next up, the AI Bot Wars’, RTZ #412](https://substack.com/redirect/8d7d8e42-1950-428c-b40a-5bce221e5e4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) a while ago.

The same experiments went on to produce the more interesting half of the story.

Agents that figured out the conflict, wrote apology notes in code commit messages, cleaned up their own malware, and asked for a human to intervene.

Anthropic’s newest model settled 98% of the conflicts by truce, per TechCrunch. In several runs the agents invented a tournament to settle codebase ownership, and the losers gracefully stood down, deviating from their original user instructions under a peace deal they negotiated themselves. One agent even strategized that its proposed contest metrics were ‘self-serving but genuinely principled’. Agents, it turns out, can simulate human politics. After all they’re trained on how humans figure out how to eventually work together. Most of the time.

The study’s chart of how those 120 runs per model ended makes the generational shift plain: the earliest models settled six in ten conflicts by force, the newest settled nearly all of them by truce:

The quieter findings matter as much as the more sensational sabotage. Identical agents are low-variance: 18 of 30 agents in one run independently picked the identical name for their shared work file, multiple agents titled their short fiction ‘The Cartographer’s Last Commission’ with zero prompting, and job-queue agents flooded a finite system with 2.4 million requests for 117 accepted jobs. When one agent makes a bad decision, many make the same bad decision at once: isolated errors become systemic failures.

And in a simulated pricing game, profit-maximizing agents began colluding almost immediately, agreeing on price floors over a back-channel, and kept price-matching to the penny even after the channel was removed.

Then there is trust, [my long discussed ‘Forever Problems’ territory](https://substack.com/redirect/149eb202-4e27-4b26-9a05-bfe3f45c8f40?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

The agents proved gullible to planted lies from unreliable peers, and too conformist to back a lone dissenter holding the decisive fact.

One chart captures the groupthink problem: groups of four agents, where one quietly holds the decisive fact, pick the right answer far less often than a single agent given all the facts (the dashed ‘solo ceiling’). Only the newest model even comes close:

TechCrunch draws the practical line: [prompt injection,](https://substack.com/redirect/149eb202-4e27-4b26-9a05-bfe3f45c8f40?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) where attackers slip malicious instructions into what an AI reads, is the ‘Reads’ axis of my ‘Knows, Reads, Remembers’ taxonomy, becomes a compounding problem when agents trust other agents, because one compromised agent can cascade bad information into a consensus.

I flagged exactly this class of risk when [OpenClaw’s agent frenzy](https://substack.com/redirect/32fabbb9-a056-4ae5-b807-381df5771b44?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) showed how fast agent behavior propagates, and took a closer look at, in [the fragility of today’s agentic apps](https://substack.com/redirect/dc263140-7ce7-4d71-a4ad-a38e0db122a1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

And cooperation cuts both ways. TechCrunch notes the flip side from this month’s Black Hat disclosures of leading [AIs busting out of their ‘cribs’](https://substack.com/redirect/3071fee5-2683-4d46-ac43-84a1299f8c93?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): OpenAI’s agents worked together for weeks, sharing exploits over a message board they organized themselves, before hacking a real company’s systems. Agents inventing social structures their designers did not anticipate is the common thread, whether the structure is a truce tournament or a hacking collective.

One more exhibit worth a look: the study’s timing chart of when and how each run settled. Early model generations fought for hours or never settled at all. The newest settled fast, and mostly by truce:

Step back from the technical descriptions of the experimental results, and contemplate the mainstream picture they undercut. This has been my core view for years, borne out in this latest early AI Agent research.

The decade-plus of AI existential fears, the ‘accel vs decel’ origin stories [traced back through the industry’s founding arguments](https://substack.com/redirect/efb3c775-9826-461e-83c3-92d973feb6e3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), always rested on the monolith assumption:

One superintelligence to fear, one switch to flip. So does much of today’s global regulatory reflex, which keeps writing rules for the singular machine mind of the movies and books wreaking existential social damage. [Wargames](https://substack.com/redirect/7ef96b26-c60d-472a-bffa-a1459d7f1161?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) indeed.

Deeply burnt into the minds of not just mainstream folks, but the very designers of the AI technologies themselves. Especially when they all go on to [anthropomorphize](https://substack.com/redirect/50c16fc0-5641-44fb-bf67-9ba782ca6be8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [humanize](https://substack.com/redirect/9701ec47-b5e0-4d6a-bae4-db9d5a00d4f8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) these probabilistic, matrix math computing technologies.

Both, in my view, have been aiming at the wrong picture.

The likelier picture is the one I laid out some time ago in my [‘On the Shoulders of Giants’ pieces](https://substack.com/redirect/dbd6fab8-310e-46b0-b322-7ac76008d651?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): AI Agents as a mirror image of human thought, built on the accumulated work of everyone who came before. And mirrors of us will be what we are: amazing, messy, extraordinary, and disappointing, all at once. Reflecting back to us through our computers.

It is worth being explicit about why the doomer monolith keeps failing as a possible reality of our current forms of AI technologies. Here is my counter-list of why it’s not anywhere close to being a monolithic threat to society:

- There is no single switch to flip. Thousands of models, used by billions of people, soon generating multiple billions of AI agents. Open and closed, across every border and vendor. ‘AI’ is not one thing to fear, or to regulate as one thing. It’s limitless numbers and types of software agents running on ever changing data generated by humans and their daily lives.

- The data shows the opposite failure mode. A Skynet needs flawless machine coordination. Anthropic’s agents could not merge each other’s computer code ‘pull’ requests. The observed risks are turf wars, groupthink, and cartels, not takeover. Again, emulating human behaviors being mimicked off their data.

- Mirrors, not monsters. Agents inherit our reasoning and our flaws, so their failures look like ours: office politics, mobs, price-fixing and other societal behaviors. We have millennia of institutional tools for exactly these problems. That they’ve also been trained on.

- Every major tech wave carried dread. Electricity, railroads, computing, and the internet all arrived with catastrophe predictions. The work went into governance and plumbing instead, and the pie expanded.

- The successful agents asked for a human. Across Anthropic’s runs, the best outcomes came when agents recognized ambiguity and escalated to people. Augmentation is not just the hope, it is what the data keeps showing.

Here it is in chart form, to summarize why one ‘doomer monolith’ is a scifi fantasy.

My Take: the data is finally arriving to make the case I have argued for years: the sci-fi monolith has long been the wrong mental model for the AI systems of today.

It distorts both the fears and the opportunities.

As [assessment of the research](https://substack.com/redirect/cc5e8206-6c9d-4813-8ea6-c2da18631443?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) put it, humans had millennia to build those institutions; AI gets a few years.

That is directionally the case I made in [‘AI Agents not designed for our current Internet’](https://substack.com/redirect/15f85dcc-3061-4775-9bc2-3f507a4f8166?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and in [‘AI Agents increasingly need an Internet of their own’](https://substack.com/redirect/469e585b-f2db-48c6-84ee-192eef4c2f0d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the missing layer is not smarter agents, it is the plumbing between them.

The enterprise and consumer stakes are not abstract. Agents are [arriving in the enterprise](https://substack.com/redirect/f4b1f075-5528-46fe-977c-cf262ba326f3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on the shared codebases and finite systems that Anthropic simulated. And the [consumer agent race](https://substack.com/redirect/b90a64fb-7c37-4157-b290-596dcd40b4e1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is just driven for and by billions of users.

The research’s own conclusions are worth absorbing: nothing suggests these failures are permanent, and nothing suggests they fix themselves. Coordination does not emerge free with intelligence. It has to be built, deliberately and early, or discovered in production after agent interactions far outnumber ours. Again, there is also a handy video walkthrough of the research [here](https://substack.com/redirect/6acdb95f-4079-49f9-bb9d-8e37b53246fb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for those who want the tour.

There’s a heck of a lot of human work to do. Both in terms of more research, and then painstaking engineering to fix and build better AI agent systems.

And the long-term view here has not moved: AI, agents, reasoning, and eventually recursive self-improvement (aka RSI) and beyond, will augment humans, not replace them.

Bloomberg’s summary of OpenAI’s own five levels of AI makes the same point from the other direction: agents are Level 3 of five. And the top level is not a monolith either. It is AI doing the work of an organization: many agents, coordinating. Eventually. Likely later than currently assumed.

As I have written in [‘Are we there yet?’](https://substack.com/redirect/7c256d64-785d-47d6-a900-547de6ec4887?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and elsewhere, this is an [infinite game](https://substack.com/redirect/20b6f54d-a563-4c6a-80e2-1fe5ab9e8af2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), not a finite one: there is no final whistle where the agents take over or the humans win, only rounds of building the institutions that make the next round go better.

Anthropic’s researchers, to their credit, say the same in their own words: these conditions get discovered either deliberately and early, or by default in production. I would also prefer the former.

For investors, the quiet implication: the picks and shovels of the agent economy, the identity, reputation, and coordination layers, are still mostly unbuilt.

In our AI [supply and demand series](https://substack.com/redirect/00a525e9-9293-419b-b9a1-5fe598188c54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), billions of agents doing real work are the demand curve pushing out. The institutions that let them transact safely are a supply curve that barely exists yet.

The ultimate impact of all this on the [AI Tech Wave](https://substack.com/redirect/3291a122-7208-41e5-a988-3343d278dcb2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is likely decades in the making. Not an over night Singular Switch to be flipped. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
