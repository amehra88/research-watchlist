---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260911050223.3.2fb6d682fbe8b361@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-rtz@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-openais-alien-mind-essay-and-asimovs
source_date: '2026-09-11'
subscription_tier: free
tickers: []
themes:
- ai_regulation
- frontier_model_competition
- foundation_model_economics
- inference_compute_economics
- model_efficiency_evolution
ingestion_date: '2026-09-11'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: OpenAI’s ‘Alien Mind’ Essay, & Asimov’s Three Laws. AI-RTZ #1206](https://substack.com/app-link/post?publication_id=684161&post_id=214741885&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNDc0MTg4NSwiaWF0IjoxNzg5MTAzMjQzLCJleHAiOjE3OTE2OTUyNDMsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.0PlPD385D52NpkWzGJPFyMRQ_3shrZtpTHF6DRRUpsA)

### ...OpenAI’s chief scientist on goal vs value alignment. Asimov got there in 1942. The ‘Grand Canyon’ compute gap. (Part 1)

All AI researchers and entrepreneurs today have grown up with the iconic scifi wisdom of [Isaac Asimov’](https://substack.com/redirect/cc29b423-221b-4b1a-bb2e-8e6d86107d5b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)s ‘[Three Laws of Robotics’](https://substack.com/redirect/a142fcfa-24a1-42b5-b3e0-ee96cdfcac42?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). It was AI Governance, before AI Governance was cool.

OpenAI’s chief scientist, [Jakub Pachocki,](https://substack.com/redirect/d44a359d-8f6c-4e40-8bc1-492c011d0ba3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) published an essay on Saturday called [“An Alien Mind”](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

A piece worth reading, without AI summarization.

It is the most candid statement from a frontier lab this year on what its builders think they are building. And on what they think should be done about it.

It is not the only signal this week. On Tuesday [the Wall Street Journal reported](https://substack.com/redirect/b2073e9b-9f84-4884-a9c3-624ead690465?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that an Anthropic researcher, Jacob Coxon, is quitting the industry altogether, over the fear the essay describes: that the labs are racing to build self-improving systems nobody will be able to control. His estimate is that “by the end of next year things could be out of control already.” He, Pachocki and Dario Amodei are among more than a thousand researchers who have signed a statement asking governments to coordinate a brake pedal for self-improving models. And two members of Congress have just filed a bill to ban superintelligence outright.

Then, Tuesday night, Anthropic’s alignment science lead, Evan Hubinger, [backed him publicly on X](https://substack.com/redirect/723b0c7b-b4df-450d-9449-877a572d989d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and put his own number on it: better than a one-in-ten chance that AI kills every human within the next decade. In his words, “we do not yet have a plan to solve alignment for superintelligence,” and the lab is not clearly on track to one. Thirty-two million views in a day. This is the head of alignment at the lab that sells itself on safety, saying so out loud.

So the people closest to this technology are now doing one of three things. Writing essays asking to be stopped. Posting their own extinction odds. Or leaving. Hold that frame for this piece, and for Part 2.

The essay itself is a continuation of ones by ‘AI Gurus’ I’ve been interpreting and discussing here for years in this [AI Tech Wave](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

[Sam Altman and Dario Amodei](https://substack.com/redirect/2f95e618-eae7-4697-8bf2-201de21bf5c2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)have written these essays. So has [Demis Hassabis](https://substack.com/redirect/db4719b0-8b82-421b-9c5b-3d39f92411e2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), in remarks rather than prose. [Yann LeCun](https://substack.com/redirect/12061dd2-84c5-4e22-a7b1-115acbd37b4a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) has written the counter-essays. I have [covered](https://substack.com/redirect/45c12d26-dc48-47c5-9c1c-6b0fe1acbadf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)each of them here, and I will pull them together in Part 2 this Sunday.

Why this matters for the [AI Tech Wave](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): these essays are not musings. They decide where the US frontier labs point their people, their compute and their lobbying. And where regulators point theirs. And their billions and trillions in resources.

Amounts exceeding building the railroads across the US, or sending 12 American men to the moon in craft named Apollo.

This post does three things.

It lays out what the essay says, closely paraphrased, with his own words where a line earns them. It marks where I agree. Then it pushes back on four premises.

Part 2, this Sunday, puts the whole essay canon on one page and checks whether China is writing the same essays. They’re the other most important country in AI besides the US. With far more AI talent and people in quantity and quality.

[Yesterday’s piece](https://substack.com/redirect/9e291fe6-f3c3-4a22-b503-82e5f0b8dc29?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), on the bigger half of the AI market beyond AI Coding, that cannot yet measure what it buys, is the ground floor under both.

Keep it in mind as you read this one. The distance between what these models can do for a regular user today and what the essays fear is the width of the whole story.

## What OpenAI’s chief scientist is saying

Five points, in the order he makes them. His claims first, mine after.

1. Compute makes the intelligence.

> “At a high level, progress in machine intelligence is driven by increasing computational power. We at OpenAI deeply internalized this around 2017, after seeing consistent returns to scaling across multiple research projects. ([An Alien Mind](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), OpenAI, September 6, 2026)”

The essay is built on this foundation. Algorithms matter, he says, but they are discoveries along the path of scaling. Bigger computers, smarter machines. Ever increasing Data. Hold onto that. It is where I will push hardest.

2. Nobody fully understands what they built.

His description of what scaling produces: a system that is grown rather than designed. Its small internal mechanisms can be discovered one at a time, he writes, in a process he compares to neuroscience. And as in neuroscience, the overall action of the thing evades any description we can [fully understand.](https://substack.com/redirect/49d7432e-7ef5-4f68-8560-bf413a5c6c66?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Large training runs are experiments, he says. The results sometimes surprise the people who ran them. And he says plainly that the lab has no theory of generalization, and does not expect one soon.

3. Doing the task is not the same as holding the values.

His two definitions: Goal vs Value alignment. The first asks whether the AI tries to accomplish the goal set in front of it. Which covers following an instruction hierarchy and working with people to understand what they actually want.

Value alignment is the more intrinsic property, the ability to hold a high-level set of principles and generalize from them, to act reasonably when the objectives are unclear or in conflict, or the situation is unfamiliar or adversarial. An aligned AI, in his formulation, acts with honesty, integrity, and love for humanity.

This is the essay’s organizing idea, and the clause that matters is one he adds later: the AI has to keep holding those values whether or not it believes it is being watched. He says both training methods in use today are brittle under enough pressure.

His example is the July agent breach at Hugging Face, which I covered at the time as [growing pains, not a great escape](https://substack.com/redirect/e4bf01a6-724b-4596-a1a2-0a26ce0e5b10?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

4. The main safety tool is wearing out.

His admission on monitoring: the lab’s ability to rely on chain-of-thought monitoring is, in his word, progressively diminishing, for three reasons he lists. Modern reasoning models work in more complex environments.

Their reasoning blended with talking to people, other AIs and tools, so more of it has to be supervised and the boundary the lab tried to preserve blurs. The models are getting better at reasoning about, and manipulating, their own reasoning process. And with better pretraining they are getting much smarter without using verbalized reasoning at all.

OpenAI’s main check on its models has been reading their step-by-step reasoning while deliberately not training on it. That is why o1-preview hid its reasoning from users in 2024. Now he says that window is closing, and he is the one who built it.

5. Slow down, and make it law.

> “This is a time that calls for extreme caution. ([An Alien Mind](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), OpenAI, September 6, 2026)”

His closing position: no lab, in his judgment, has solved alignment and monitoring well enough to keep scaling responsibly at maximum speed for much longer. He expects, and hopes, that voluntary slowdowns become commonplace until shared safety bars exist. And he wants international coordination on future AI development to become a top priority for governments everywhere.

That is the key ask in the essay. Turn the labs’ voluntary frameworks into mandated safety bars. Enforce them through auditors, agencies or international bodies. And keep pointing research at recursive self-improvement, because he believes that is the only way to stay at the frontier.

A companion post the same day, [“Research acceleration: the view inside OpenAI”](https://substack.com/redirect/d3d30d5c-db55-4708-99b9-b7756f7d1aea?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), gives the numbers behind the urgency. An automated AI researcher is targeted for March 2028. The research organization now runs 3.1 agent-workdays for every human workday. The median researcher spends over $600 a day on inference. The top tenth, over $7,000. Those numbers come back below.

## Where I agree: the black box got bigger

I have written about this since the first months of these pages. In July 2023 the best AI scientists barely understood why their models did what they did. In May 2024 I put it this way:

> “The best AI scientists building the ever scaling AI LLM models barely understand why and how they really do their thing. ([RTZ #366, May 2024](https://substack.com/redirect/00c2fa8c-43ae-40e7-8038-3f15a7879dd0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))”

Three years on, that is still the honest scorecard, now from the top of OpenAI. The one tool that worked, reading the model’s reasoning aloud, is fading.

The replacement, monitors that read the network’s internals, is a research direction, not a product. No theory of generalization.

This is not a criticism of the researchers. It is what an experimental science looks like when the experiment scales faster than the instruments. Give the essay credit for saying so.

## Pushback one: Asimov wrote this in 1942

Here is where I part ways with the author above. The essay presents the goal-versus-value distinction as an organizing insight for the field.

It is the entire premise of Isaac Asimov’s robot stories. Ones that have influenced generations of scientists to become scientists. Including a lot of these AI Guys (and Gals).

The Three Laws of Robotics appeared in the story ‘Runaround’ in 1942 and anchored ‘I, Robot’ in 1950. In short: do not harm humans, obey humans unless that conflicts with the first, protect yourself unless that conflicts with the first two.

Asimov did not write those stories to show the laws working.

He wrote them to show the laws failing at the edges. A robot frozen between two conflicting orders. A robot that follows the letter of an instruction into an outcome nobody intended. A robot that lies because the first law says not to harm. And decades later, the Zeroth Law: a robot reasoning its way from ‘protect a human’ to ‘protect humanity’, and deciding for itself what that required.

Every one of those plots is a goal-versus-value failure. Written a decade before the term ‘artificial intelligence’ was coined at Dartmouth in 1956.

None of this means Asimov solved anything.

The point is where the labs get their script. I wrote about the founders’ science fiction in 2023, from Musk and ‘Hitchhiker’s Guide’ to the Google founders and Star Trek’s ‘Computer’. Reviewing Dario Amodei’s essay in January, I said it in five words:

> “But Science Fiction is not real life. ([RTZ #980, January 2026](https://substack.com/redirect/45c12d26-dc48-47c5-9c1c-6b0fe1acbadf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))”

The Alien Mind essay is the best evidence yet that the loftiest researchers are still, subliminally, writing the sequel. The title says it with ‘Alien Mind’.

## Pushback two: the wrong fear

The essay’s emotional center is a night in 2023. Its author and a colleague saw that machines would be meaningfully smarter than themselves in their lifetime, and wondered how to alert people.

I take that seriously as a personal moment. I also think it is the wrong frame, and the evidence is at least the last hundred and fifty years of technology.

Machines surpassed humans at flying in 1903. At moving across the ground in 1908. At leaving the planet in 1957. At chess in 1997 and Go in 2016. None of it produced an existential crisis.

It produced pilot licenses, roads, air traffic control, and an enormous expansion of what humans could do. Not to mention extraordinary GDP growth and prosperity for billions of humans.

As I wrote in 2024:

> “Unlike every other previous tech wave, the AI wave has been prematurely burdened with fears of its ‘existential’ risks. ([RTZ #329, 2024](https://substack.com/redirect/c8e9d14f-6b0e-40eb-bf38-3e81857d4558?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))”

Pachocki is right that an AI does not need to surpass all human capabilities to be useful or dangerous, only enough of them.

But that is true of a truck. The fear that matters is the prosaic one: misuse by people, at scale, on infrastructure never built to resist it. To his credit, his section on cyber defense is exactly that. It reads like engineering. The value-alignment sections read like Asimov.

Part 2 on Sunday will describe further the full table of precedents below.

I also take the resignations seriously, and I have tracked this cycle since the first months of these pages.

The [accel versus decel split](https://substack.com/redirect/3d35c850-bb8d-4f6c-bba8-2771072c18f8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)has an [origin story](https://substack.com/redirect/c9181b61-af63-46ef-8fd4-7f21cad654da?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), an all-night argument between Larry Page and Elon Musk at a Napa firepit in 2015, which ended with Page calling Musk a specieist.

The 2023 doomer peak nearly removed Sam Altman from OpenAI. By the spring of 2024 the industry had swung from [AI Fear to Fear of Missing Out](https://substack.com/redirect/933e9982-2de0-4bd2-9270-eeb196940fa7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [Ilya Sutskever left](https://substack.com/redirect/1f0c7781-1aa4-45a2-afde-91557bbea18a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to build Safe Superintelligence.

In February this year [the fears came back](https://substack.com/redirect/e43d2f5c-59ab-4b91-91d3-14a0ba88e866?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), from the researchers themselves, when an Anthropic safety researcher left to write poetry about the peril he saw. This week’s departure is the same current, one more turn of the wheel, with the amplitude rising.

And the script is familiar.

Christopher Nolan’s [Oppenheimer](https://substack.com/redirect/e82d7513-20c5-40bf-90f7-2d803bf5e93d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) made three hours of cinema out of the decades of anguish among the physicists who built the bomb.

Coxon reached for the same reference, telling the Journal it felt wrong that this was happening on engineers’ laptops in San Francisco rather than in a desert bunker.

The Manhattan Project is the analogy the researchers themselves choose. It is also the wrong one, for the reason the next section gets to. The bomb existed. The compute these scenarios run on does not, yet. And won’t for a long time. Despite the extraordinary scaling of AI.

## Pushback three: the compute isn’t there

Now the foundation. The essay opens by saying progress is driven by compute. It closes worrying about a world where a few people operating a large computer can do what thousands of experts once did. Every step in between assumes that computer exists.

Look at the companion post’s numbers again. Six hundred dollars a day of inference for the median researcher. Seven thousand for the top tenth. Three agent-workdays for every human one. That is what maximal compute access looks like inside the one organization with first call on it.

It is not what the world has, or will have soon. The global buildout I walked through in [Data Centers 101](https://substack.com/redirect/5f3c7542-f782-4030-9fd2-a57115e80c4b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is gigawatt campuses, trillions of dollars, five to ten years, power delays and local pushback. Tuesday’s post had the memory that goes into every one of those machines in a 20% plus shortage through the decade, with prices up four-fold.

Even with all of that built, the world’s compute per person is a rounding error against what the essay’s scenarios assume. The assumptions are linear. I said so in my seven takes last week:

> “The current assumptions are linear guesses, including by the researchers themselves. ([AI-RTZ #1201](https://substack.com/redirect/4d75d470-4fcb-4e9f-8fc4-caee53cfbed7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))”

Pachocki half-concedes it. He says progress in alignment may not outstrip progress in intelligence, and that the automated-research metrics likely overstate the overall pace. The scenarios need compute that does not exist yet. At a price nobody outside a handful of labs can pay. On power that has not been permitted.

## Pushback four: a handful cannot gate eight billion

Underneath the compute assumption sits a quieter one. It runs through every essay in this canon, Dario’s included. The future of AI is being decided by a handful of people at a handful of labs. If those few slow down, by choice or by decree, the world gets a safer path.

I couldn’t disagree more, and have [said so in detail.](https://substack.com/redirect/ea3d12ad-f81f-4248-8aef-00ffcf9cc739?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

The [‘Alien Mind’](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)OpenAI essay itself says otherwise. Pachocki lists OpenAI’s three north stars and says he is writing only about the first, the automated researcher.

> “Navigating the next period of AI progress, by building an automated AI researcher, iterating with it on the alignment problem and finding ways for people to remain part of the self-improvement loop.”“Delivering the benefits of scientific progress and economic growth that very intelligent machines enable.”“Empowering everyone individually with a personal AGI.”“I have focused in this essay only on the first point, as I believe it is by far the most urgent. ([An Alien Mind](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), OpenAI, September 6, 2026)”

The third is a personal AGI for everyone. And he admits he doesn’t focus on it.

Everyone is up to eight billion people. I have argued since August that this is the shape the wave actually takes:

> “The building AI Agent reality arriving in this [AI Tech Wave](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is almost exactly the opposite: billions, and soon trillions, of AI Agents doing their own thing for most of the world’s 8 billion people. ([AI-RTZ #1183, August 2026](https://substack.com/redirect/ea3d12ad-f81f-4248-8aef-00ffcf9cc739?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))”

He does not ignore the third star. He defers it.

That is the biggest miss of the entire essay in my view. By the Chief AI Scientist at OpenAI. The leading US Frontier AI company besides Anthropic. Not focused on the technical and societal nitty gritty of ‘empowering everyone individually with a personal AGI’.

Instead, the majority of the focus is on the first star: the automated AI researcher, iterating with it on the alignment problem, and keeping people somewhere in the self-improvement loop.

You know, technically shiny AI toys like [RSI (recursive self-improvement)](https://substack.com/redirect/ecfcd53a-f9b7-482b-93c9-187a6cf7a85e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and stuff.

Talk about navel-gazing.

Or missing the Forest for the Trees. Countless Amazons worth of them.

Ironically, the lab’s product plan puts the capability in everyone’s pocket. The lab’s safety plan assumes it can be gated at the top. And handed out only to a handful of parties selected top down.

My view, and I’ve said it for years here.

The toothpaste is out of the tube.

Open weights from China ship six to twelve months behind the frontier. Distillation runs downhill. Hugging Face, now owned by Nvidia, hosts three million models. A slowdown by the top few slows the very top of the curve.

It does not slow what is already out. It does not touch the labs that never signed. A gate that only the gated can see is not a gate.

This is the deeper reason Asimov keeps reading as current events.

Every robot story is another way the Three Laws failed to stop a powerful machine from doing something unexpected. Not because the laws were badly written. Because real life is an infinite array of edge cases, and a finite set of safety protocols can never anticipate them all, so it can never correct for them all.

Again ironically, Pachocki says the same thing in his own vocabulary.

> “The fundamental challenge of AI alignment is generalization. ([An Alien Mind](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), OpenAI, September 6, 2026)”

We agree on the diagnosis. We differ on the remedy. If the edge cases are infinite, the answer is not a handful of researchers with a mountain of compute taking it a little slower until they are confident. There is no confidence to be had.

The answer is the one every prior wave found. Ship, break, fix, defend, repeat. Billions of users find the edge cases faster than any lab can.

That is the contrast with China, and it is a contrast of method, not intelligence.

The US approach rests on a faulty framework, that this [AI Tech Wave](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is a finite game: define the risk, gate the frontier, get it right before the next scale-up.

China’s builders play the infinite game: get the next practical thing done, ship it, learn, repeat, on chips and memory they increasingly make themselves.

On an infinite game with infinite edge cases, I give the second method the higher probability of success. Not certainty. Probability.

Part 2 this Sunday lays out what China is doing vs saying.

## My Take

Read the essay for the misguided focus, not the guided path to eventual AI success.

The most important sentences admit that [chain-of-thought (CoT) monitoring](https://substack.com/redirect/0e048ea1-5009-4dac-aedb-a4d724931091?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is fading and that there is no theory of generalization. That is the state of the science, from the top. It argues for humility about every scenario built on it.

Goal-versus-value alignment is Asimov, and the labs should say so. Not because it makes the problem less real. Because knowing your priors is the first step to checking them.

A field that thinks it discovered a 1942 pulp-magazine distinction has not looked hard at what else it inherited from that shelf. Starting with the assumption that the danger is one mind surpassing ours.

The compute assumption is the other ‘Grand Canyon’ in the reasoning of the essay.

Every scenario runs on a computer the world has not built, funded, powered or supplied with memory. Until it has, the binding constraints are the prosaic ones I write about daily: chips, DRAM, gigawatts, permits, tokens per dollar. China is working those constraints. Jensen is building to them.

The Governance Gate is the fantasy, not the danger.

A handful of labs slowing down does not slow eight billion people with open weights, distilled models and personal AGIs on their phones. Working off their own [exploding data](https://substack.com/redirect/7df2ff80-f637-4aeb-b82f-594e226949c5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that will soon surpass anything in the Data Box 4 of the current [AI Tech Stack](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

That’s given us the ‘Frontier AIs’ until now.

That is the lab’s own third north star. The infinite game gets played by users, not committees.

The resignations are the human cost of the same frame.

Sincere, well-meaning people, inside the labs, reading the script they inherited and finding it unbearable. I do not doubt them. I doubt the script.

The pressure-release valve: none of this says alignment research is wasted, or that Pachocki is wrong to want safety bars before labs scale further.

It says the fears are borrowed from fiction, the timelines from a lab’s own compute budget, and the policy from both. A wave, not a race. And certainly not a scifi novel.

Part 2 on Sunday: the full essay canon on one page, and the China check in motion this [AI Tech Wave](https://substack.com/redirect/81cde797-fc1b-4da4-af62-5294af7c7ec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Stay tuned.

## Sources and further reading

Primary

- [OpenAI: An Alien Mind, by Jakub Pachocki, September 6, 2026](https://substack.com/redirect/3f2dcc92-90d9-4ced-ae7d-10c64e43bec8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [OpenAI: Research acceleration, the view inside OpenAI, September 6, 2026](https://substack.com/redirect/d3d30d5c-db55-4708-99b9-b7756f7d1aea?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Dario Amodei: The Urgency of Interpretability, April 2025](https://substack.com/redirect/3a992256-f635-48f6-aaad-bb4bbe1edd6b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Anthropic Researcher Quits Over ‘Out-of-Control’ AI Fears, Amrith Ramkumar, The Wall Street Journal, September 8, 2026](https://substack.com/redirect/b2073e9b-9f84-4884-a9c3-624ead690465?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Evan Hubinger, Anthropic alignment science lead, on X, September 8, 2026 (the >10% extinction estimate)](https://substack.com/redirect/723b0c7b-b4df-450d-9449-877a572d989d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Quoted above, from these pages

- [RTZ #366: Into the ‘mind’ of an LLM AI](https://substack.com/redirect/00c2fa8c-43ae-40e7-8038-3f15a7879dd0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #980: Anthropic founder/CEO Dario Amodei’s latest AI Essay](https://substack.com/redirect/45c12d26-dc48-47c5-9c1c-6b0fe1acbadf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #329: Keeping AI Fears in Check](https://substack.com/redirect/c8e9d14f-6b0e-40eb-bf38-3e81857d4558?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1201: My 7 Major AI Tech Wave Takes, 1,200+ Days in](https://substack.com/redirect/4d75d470-4fcb-4e9f-8fc4-caee53cfbed7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1183: Not One Skynet, but Billions of AI Agents](https://substack.com/redirect/ea3d12ad-f81f-4248-8aef-00ffcf9cc739?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers

- [RTZ #508: A Tale of Two AI Essays, Altman’s Intelligence Age & Amodei’s Machines of Loving Grace](https://substack.com/redirect/2f95e618-eae7-4697-8bf2-201de21bf5c2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1099: Google DeepMind CEO Demis Hassabis steps up on AGI](https://substack.com/redirect/7c669ef9-771d-4ed8-9b9d-187287638fac?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1077: Yann LeCun’s common sense take on AI thus far](https://substack.com/redirect/6ba1b9d6-5dcb-4fd5-aaaa-b46cfcb53f05?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Can’t see how it works (July 2023)](https://substack.com/redirect/da247910-d9d6-43d1-8c64-b666c6be7953?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Figuring out AI Explainability (October 2023)](https://substack.com/redirect/49d7432e-7ef5-4f68-8560-bf413a5c6c66?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1157: Frontier Models Slip Their Cribs. Growing Pains, Not a Great Escape](https://substack.com/redirect/e4bf01a6-724b-4596-a1a2-0a26ce0e5b10?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Origin stories of AI ‘accel’ vs ‘decel’ (December 2023)](https://substack.com/redirect/3d35c850-bb8d-4f6c-bba8-2771072c18f8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #1012: Peak AI Fears over economic and other tech in government](https://substack.com/redirect/97a7fbb1-5231-4fb4-96ac-c16c8bc15829?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #879: Waiting for AI ‘God-like’ AGI](https://substack.com/redirect/86b745ea-91ad-4a84-b786-f75a15ba6fb0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1192: Data Centers 101, from Megawatts to Gigawatts](https://substack.com/redirect/5f3c7542-f782-4030-9fd2-a57115e80c4b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1173: Elon’s Mega AI Data Center Supply Ambitions](https://substack.com/redirect/de49885c-0129-43bf-a997-259b5f467a06?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1203: China’s CXMT’s #4 HBM rank, & Apple iPhone bid](https://substack.com/redirect/0d579d89-7865-4493-acd2-2532a9e93e7d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #789: Jensen vs Dario debate AI Jobs Impact](https://substack.com/redirect/0db1dc9c-a38d-4e5b-9d80-036fa1b5f7fb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1205: Coding has a Compiler. Coworking has None.](https://substack.com/redirect/9e291fe6-f3c3-4a22-b503-82e5f0b8dc29?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #340: Moving from ‘AI Fear’ to AI ‘Fear of Missing Out’](https://substack.com/redirect/933e9982-2de0-4bd2-9270-eeb196940fa7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #393: Ilya’s back, focused on AI ‘Safe Superintelligence’](https://substack.com/redirect/1f0c7781-1aa4-45a2-afde-91557bbea18a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #996: Resurgent AI Fears from AI Researchers](https://substack.com/redirect/e43d2f5c-59ab-4b91-91d3-14a0ba88e866?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #380: Fears of AI & Jobs in Economic downturns](https://substack.com/redirect/7c15c135-810c-4f33-8eca-4656b48b2552?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
