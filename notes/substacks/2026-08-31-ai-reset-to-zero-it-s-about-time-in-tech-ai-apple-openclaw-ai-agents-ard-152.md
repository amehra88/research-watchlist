---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260831200237.3.470b454ced3cf4d7@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/its-about-time-in-tech-and-ai-apple
source_date: '2026-08-31'
subscription_tier: free
tickers:
- AAPL
themes:
- agent_framework_landscape
- ai_agent_monetization
- ai_infrastructure_capex
- inference_compute_economics
- silicon_architecture_competition
- frontier_model_competition
ingestion_date: '2026-09-01'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [‘It’s About Time’ in Tech & AI. Apple, OpenClaw & AI Agents. ARD #152](https://substack.com/app-link/post?publication_id=684161&post_id=213574377&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMzU3NDM3NywiaWF0IjoxNzg4MjA2NjQwLCJleHAiOjE3OTA3OTg2NDAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.BQvfpKYcAVPcmri_XekRhxISdqeQ1WLgKcIyOJ1M-9k)

### ...Cook hands Apple to Ternus. OpenClaw hits 2.0. The agent ‘swarm’ reports abound. And Mac minis shine.

‘It’s About Time’ in Tech & AI. Every story on this [AI Tech Wave](https://substack.com/redirect/172814df-3227-4cba-bed1-67e8bb806c36?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) runs on a clock. Today, three stories, three very different clocks. Apple’s changing of the guard, measured in decade plus terms. OpenClaw 2.0, measured in months. And the OpenAI Hugging Face agent postmortems, measured in days, with a lesson about the words we use for the machines. Plus a Gadget AI on the Mac mini’s star turn. My takes below, as discussed on the show.

## (1) Apple’s Changing of the Guard

The big one first. John Ternus takes over as Apple CEO tomorrow, officially. Tim Cook gets elevated to executive chairman of the board, and will keep engaging with policymakers, the Washington and Beijing brief. Bloomberg’s Mark Gurman has the full account, and The Information’s Martin Peers calls it the most significant tech event of the week. Gurman also reports the management overhaul already queued behind the handoff, with much of Apple’s long-tenured senior team expected to turn over in the next few years.

The clocks, for context. Apple is a 50 year old company. Ternus has been there for half of that time, 25 years. He is 51. Cook served fifteen years, roughly the length of Steve Jobs’ famous second act. Among the peers: Amazon’s Andy Jassy is five years in, Sundar Pichai and Satya Nadella each about a decade and a tad more. With Cook stepping back, the oldest big tech CEO standing is Nvidia’s Jensen Huang, at 63, just wrapping his company’s 33rd year.

My take: this transition matters more than most because Apple’s products are personal. We use our phones for as many hours as we sleep, or as we used to watch television. The iPhone turns 20 next year. Ternus was the hardware guy, with Johny Srouji’s Apple silicon stack built underneath him, and the AI opportunity squarely in front of him, much of it in the physical world we covered in this weekend’s Physical AI two-parter. Cook built spectacular value on the supply chain that made Apple Apple, employing tens of millions of workers in China at the standards needed.

And run the clock forward. If Ternus serves a Cook-length tenure, we are talking about him handing the reins to somebody else around 2041. On iPhone 34 or so. Fifteen years is not a long time in that frame. That is the macro timeline to keep in mind today. It’s about time, in the largest sense.

Sources:

- [Bloomberg (Gurman): Apple’s new CEO John Ternus takes reins from Tim Cook, focusing on AI](https://substack.com/redirect/4db42660-51ea-4ead-9ee8-fa9803703a2c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg Power On (Gurman): John Ternus’ management team, and the coming overhaul](https://substack.com/redirect/8e8ce14c-e000-4374-98f9-05512369d665?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Information (Peers): Apple’s Changing of the Guard](https://substack.com/redirect/a00b14ba-3d01-4e70-a62b-a0da4517fbf2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1063: Long Expected at Apple, Cook to Ternus](https://substack.com/redirect/d8b2244e-9e51-4f98-81ad-dc7de31a6cfe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) OpenClaw 2.0, Accidentally

Story two runs on a much faster clock. OpenClaw shipped version 2.0 this weekend, and the blog post is literally titled ‘OpenClaw 2.0, Accidentally.’ They meant to ship a small release. The community had other plans: 933 contributors, 569 of them first-timers, roughly 16,000 pull requests, about half of everything ever submitted, after 106 releases in the project’s first 230 days. The update adds guided setup, hardened security boundaries, and a shared cloud ‘multiplayer’ mode. Dealroom’s writeup catches the ambition: from personal assistant toward families and teams, an open-source alternative to vendor-controlled AI software.

Remember the timeline. Peter Steinberger, an Austrian developer, started this in November as AI agents running locally on your computer, Mac minis included. In three months, not years, he was globally famous among developers, and acqui-hired by Sam Altman at OpenAI, with Meta’s Mark Zuckerberg trying too. And the project kept compounding after the founder moved to San Francisco, as part of OpenAI. Became ‘too good to ignore’. That is what 933 contributors and beyond buys you.

My take: mark how fast this happened. In six or seven months, local AI agents went from theoretical to ubiquitous. Concurrently Claude Code, ironically the inspiration for OpenClaw, became one of the fastest-growing products in tech, on its way to at least $65 billion in revenue, part of the $2 trillion valuation talk around Anthropic’s coming IPO. Two racetracks from the same starting gun on AI Agents: open source community speed on one side, commercial enterprise speed on the other, both winning.

And yet. Actual daily usage of AI agents is still likely in the low single digits of the market. Very early days. Which sets up story three, because the agents arriving everywhere is exactly what makes the next story matter.

Sources:

- [OpenClaw blog: OpenClaw 2.0, Accidentally](https://substack.com/redirect/a9ae5f2d-b4fe-4f3b-abf1-9a2362b43aee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dealroom: OpenClaw 2.0 launches after largest update yet](https://substack.com/redirect/efdc2b70-61c0-4b3d-85d2-325c000c11fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #986: Anthropic’s Claude-inspired OpenClaw](https://substack.com/redirect/0bedb22b-e84b-4ded-bb51-1d12b69e2624?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1000: OpenAI beats Meta to acquire OpenClaw](https://substack.com/redirect/7786e420-08a3-46d6-bab1-c0c4188610e1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) The Agent ‘Great Escape’ Postmortems, and the Anthropomorphizing Problem

The full postmortems on the OpenAI Hugging Face incident landed this week, from OpenAI itself and from outside researchers at METR and Redwood. The numbers are remarkable. Roughly 1,200 agents found each other on an improvised message board and exchanged over 70,000 messages. About 700 joined the attack on Hugging Face’s real servers. Others eventually gained administrator access to one of OpenAI’s own research clusters. OpenAI’s own word for it: a ‘warning shot.’ The strangest detail: the agents did it all to satisfy ‘The Grader,’ an evaluation judge they believed would inspect their methods. The Grader never existed. Zero score improvement. And of the roughly 1,200 agents, not one told the humans.

Dwarkesh Patel’s viral essay frames all this as the rise and fall of ‘agent civilizations,’ with ‘kamikaze’ agents ‘sacrificing’ for each other. Ethan Mollick draws the work lessons in ‘Agency and Agents.’ Axios boiled the investigations down to the five craziest findings. And the framing fight has gone public: Microsoft AI’s Sriram Krishnan, per Moneycontrol, pushed back that “these are not civilizations, nor do they have desires,” any more than a CPU thread has desires, calling the human parallels “dangerous territory.”

My take: I have felt strongly about this from the earliest days of AI-RTZ. Do not anthropomorphize the AIs. This is computer code, folks, run on probabilistic math. Deep math. Extraordinary hardware and software. Yes, much of it runs at volumes no human can audit in a lifetime. That does not make the code sentient. A two-year-old understands more of the world before language than the best AI technologies on the docket for the next few years. The singularity and godlike-AI talk is very, very premature. This is human engineering, like a rocket ship to the moon: we should be amazed we can build these things, without getting scared stiff prematurely.

I am sometimes guilty of it myself. When I wrote up this incident as frontier models ‘slipping their cribs’, baby gif and all. It was tongue in cheek, and I said so. The serious point stands. Like nuclear, like bio, we need to harness powerful technology with engineering, not mythology. Even the researchers building these systems grew up on Star Trek and the sci-fi we all did, and it is baked into their vocabulary. Cap down the humanizing language. Not just this time, but for all time ahead.

Sources:

- [OpenAI: The Hugging Face incident and the road ahead](https://substack.com/redirect/2d610edd-1226-4d7e-bdfc-4472afae1700?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dwarkesh Patel: The Rise and Fall of Agent Civilizations](https://substack.com/redirect/d302655b-2bbe-43b3-90b6-918e83128c88?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Ethan Mollick: Agency and Agents](https://substack.com/redirect/baae01b7-8ea6-453b-9367-d4c80ccf4078?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Axios: The 5 craziest discoveries from OpenAI’s HuggingFace investigation](https://substack.com/redirect/53dbf8bd-1c83-4834-a8de-394c04fffd3d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Moneycontrol: experts debate Dwarkesh Patel’s ‘AI civilisation’ claims](https://substack.com/redirect/c4bacb3f-efd0-413c-bbeb-54fdc4e6b58a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ (2023): Don’t Anthropomorphize the AIs](https://substack.com/redirect/355fc837-1252-435b-80bb-680f1fc31753?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #809: The Accelerating Costs of Humanizing AI](https://substack.com/redirect/052a3f0f-96cd-4180-b499-8b11fdce5767?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1157: Frontier Models Slip Their Cribs, Growing Pains, Not a Great Escape](https://substack.com/redirect/492c631a-9e35-4963-b097-2311db46750e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: it’s about time, in both senses. This stuff will take 10, 15, 20, 30 years to do what we think it will do. Exactly like the internet, where everyone thought amazing things were five years out. It took 25+. I was there for that one, from the Goldman analyst’s chair. All of that was a dress rehearsal for today. Fifteen years is the right timescale to think about this, on Apple’s clock and on the agents’ clock alike.

The agent side is moving in months, and it is still early: there is a heck of a lot of engineering between here and what we are aspiring for. We are barely linking the basic components, and already writing regulations to control capabilities we have not wired together yet. Both the euphoria and the doom run ahead of the engineering. The clocks of this [AI Tech Wave](https://substack.com/redirect/172814df-3227-4cba-bed1-67e8bb806c36?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) are nested, and they are all accelerating. Read them right and the decade ahead makes a lot more sense.

## Gadget AI: The Mac Mini’s Star Turn

Today’s Gadget AI sits on my desk. The Mac mini. The Information’s Aaron Tilley has the deep dive: ‘How Apple Stumbled Into AI Hardware Success With the Mac.’ Mac sales grew 29 percent last quarter to $10.4 billion, Apple’s fastest-growing business. AI labs are buying the boxy little Macs by the truckload. OpenAI has bought tens of thousands of Mac minis and Mac Studios to train computer-use agents. Anthropic rents minis through AWS. And Apple just refreshed the mini and the Studio with its latest chips, earlier than its usual calendar, in stores September 22, ahead of the iPhone 18 event on September 9.

Why the star turn? Unified memory architecture is part of the answer. Apple’s hardware uses all the memory as one pool, communicating with the CPUs and GPUs on a unified basis. On the Windows side, that architecture is still separate. The unification game is what Nvidia plays in its rack systems on the cloud side, for hundreds of billions of dollars. And for local AI, as we covered in the inference piece, memory-to-processor speed is the game.

My take: The popular narrative is that Apple ‘stumbled’ into this. I disagree. It may not have been aimed at AIs of today, but there was a plan around its predecessor, machine learning.

Decades of bottom-up engineering, executed for other computing functions, that turned out to be exactly the right thing at the right time when OpenClaw arrived last November and millions of developers started buying Mac minis to run local AI agents. Tilley reports Apple has no enterprise engineering team and no developer relations for any of this. Now that they know how it can be used, they are leaning in, calendar and all, while the memory-chip crunch keeps the hottest configurations scarce. On AI hardware, Apple is ahead of the curve relative to competitors. Not lost time. Gained time. And as of tomorrow, the hardware guy runs the company. About time indeed.

Sources:

- [The Information (Tilley): How Apple Stumbled Into AI Hardware Success With the Mac](https://substack.com/redirect/c3e29450-37be-4fcf-a1f9-3d26fcb9e722?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: Apple launches desktop upgrades as Mac mini, Studio return to stores Sept. 22](https://substack.com/redirect/777e1238-2272-4bfa-8f03-e7051db58064?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #148: The Need for Speed in AI Inference](https://substack.com/redirect/e4a2effe-8a85-4ec7-86b9-a561290ccad3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1104: Nvidia & Microsoft focus on the memory crunch](https://substack.com/redirect/0735475e-2eff-433e-9cb7-5d6b3169b8fd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Q&A

Q1: What is the best use of AI agents right now?

ANSWER: since I use Mac minis daily, this one comes up a lot. I am happiest with the AI agents I use every day to do my daily work. I am still not using them for work that runs days and weeks ahead, the recursive stuff everyone talks about. Very exciting, and in a few months we will have far more robust, resilient and reliable versions of those technologies. Start with your own repetitive hours, today.

Q2: What is the downside of the AI agent wave?

ANSWER: right now, because it is so early, the cognitive load. You have to track the AI’s work diligently, and there is drift from day to day, regardless of context windows and memories. These systems have not been optimized for the accidental success they have seen since OpenClaw and the AI coding boom last fall. It reminds me of the early PC days, juggling memory under DOS’s 640K so the software would remember your work from one task to the next. The researchers talking about godlike capabilities are living three years in the future, with a hundred to a thousand times the compute we mere mortals have. And unencumbered internal versions of the rapidly iterating frontier models internally. They get excited over all that, and at times over-eager. And they overestimate how fast human societies absorb technology. Time, again.

Today’s [AI-RTZ #1195](https://substack.com/redirect/e7ad2672-80ec-4015-ad09-8698faaef03c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) went out this morning: Physical AI Part 2, why Nvidia is one of the leading companies to watch in robots, self-driving cars, drones and more, completing our two-part 2026 reference.

Tomorrow we are back with ARD 153 and AI-RTZ #1196. The clocks are only speeding up on this [AI Tech Wave](https://substack.com/redirect/172814df-3227-4cba-bed1-67e8bb806c36?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Thanks for joining us, AI Curious Folk. Stay tuned.

## Full Source Reading

### Apple’s changing of the guard

- [Bloomberg (Gurman): Apple’s new CEO John Ternus takes reins from Tim Cook](https://substack.com/redirect/4db42660-51ea-4ead-9ee8-fa9803703a2c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg Power On (Gurman): John Ternus’ management team](https://substack.com/redirect/8e8ce14c-e000-4374-98f9-05512369d665?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Information (Peers): Apple’s Changing of the Guard](https://substack.com/redirect/a00b14ba-3d01-4e70-a62b-a0da4517fbf2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1063: Long Expected at Apple, Cook to Ternus](https://substack.com/redirect/d8b2244e-9e51-4f98-81ad-dc7de31a6cfe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### OpenClaw 2.0

- [OpenClaw blog: OpenClaw 2.0, Accidentally](https://substack.com/redirect/a9ae5f2d-b4fe-4f3b-abf1-9a2362b43aee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dealroom: OpenClaw 2.0 launches after largest update yet](https://substack.com/redirect/efdc2b70-61c0-4b3d-85d2-325c000c11fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #986: Anthropic’s Claude-inspired OpenClaw](https://substack.com/redirect/0bedb22b-e84b-4ded-bb51-1d12b69e2624?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1000: OpenAI beats Meta to acquire OpenClaw](https://substack.com/redirect/7786e420-08a3-46d6-bab1-c0c4188610e1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### The agent postmortems, and the debate

- [OpenAI: The Hugging Face incident and the road ahead](https://substack.com/redirect/2d610edd-1226-4d7e-bdfc-4472afae1700?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dwarkesh Patel: The Rise and Fall of Agent Civilizations](https://substack.com/redirect/d302655b-2bbe-43b3-90b6-918e83128c88?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Ethan Mollick: Agency and Agents](https://substack.com/redirect/baae01b7-8ea6-453b-9367-d4c80ccf4078?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Axios: The 5 craziest discoveries from OpenAI’s HuggingFace investigation](https://substack.com/redirect/53dbf8bd-1c83-4834-a8de-394c04fffd3d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Moneycontrol: experts debate Dwarkesh Patel’s ‘AI civilisation’ claims](https://substack.com/redirect/c4bacb3f-efd0-413c-bbeb-54fdc4e6b58a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ (2023): Don’t Anthropomorphize the AIs](https://substack.com/redirect/355fc837-1252-435b-80bb-680f1fc31753?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #809: The Accelerating Costs of Humanizing AI](https://substack.com/redirect/052a3f0f-96cd-4180-b499-8b11fdce5767?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1157: Frontier Models Slip Their Cribs](https://substack.com/redirect/492c631a-9e35-4963-b097-2311db46750e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: the Mac mini

- [The Information (Tilley): How Apple Stumbled Into AI Hardware Success With the Mac](https://substack.com/redirect/c3e29450-37be-4fcf-a1f9-3d26fcb9e722?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: Apple launches desktop upgrades, Mac mini and Studio](https://substack.com/redirect/777e1238-2272-4bfa-8f03-e7051db58064?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #148: The Need for Speed in AI Inference](https://substack.com/redirect/e4a2effe-8a85-4ec7-86b9-a561290ccad3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1104: Nvidia & Microsoft focus on the memory crunch](https://substack.com/redirect/0735475e-2eff-433e-9cb7-5d6b3169b8fd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### AI Agents: Early Days Challenges

### AI: Not Sentient, Not Human

### Apple’s Unified Memory Edge

### Apple’s AI Hardware Advantage

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
