---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260724050213.3.90b58700c0eae7b3@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-frontier-ai-models-and-agents
source_date: '2026-07-24'
subscription_tier: free
tickers: []
themes:
- frontier_model_competition
- ai_regulation
- cybersecurity_competitive_landscape
- agent_framework_landscape
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Frontier AI models & Agents learn to break out. AI-RTZ #1157](https://substack.com/app-link/post?publication_id=684161&post_id=208101271&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwODEwMTI3MSwiaWF0IjoxNzg0ODY5NTMwLCJleHAiOjE3ODc0NjE1MzAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.REYUXjpboh7Dp5b0TScoNs-ahQziV2Wfoz6ZM85Jx7k)

### ...a familiar problem with early, growing software technologies

So now there is a ‘new’ big AI concern this [AI Tech Wave](https://substack.com/redirect/27576dbe-eab8-429a-8692-398ff12c1a7c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) . The [latest AI models seem to be figuring out](https://substack.com/redirect/4a2fbbb7-4671-4e84-bb52-16683ad01802?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)how to break out of their environments while being tested on safeguards. Babies slipping out of their cribs.

It’s a concern that’s been [building with AI models](https://substack.com/redirect/43239b8d-08fa-4487-b725-1191748d9102?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)for [years,](https://substack.com/redirect/ab703575-8580-4567-be03-54626ba1eded?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [discussed here](https://substack.com/redirect/4a2fbbb7-4671-4e84-bb52-16683ad01802?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)at AI-RTZ for a while. They’re now getting more urgent focus because the latest frontier AI models from [Anthropic, Mythos/Fable 5, and OpenAI’s GPT 5.6,](https://substack.com/redirect/43239b8d-08fa-4487-b725-1191748d9102?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) are now ‘grown up’ enough to potentially cause more concern out unsupervised in the wild.

Note that these issues are separate from the [AI ‘Forever’ problems I’ve discussed](https://substack.com/redirect/339ca1c4-99f7-4a66-89a1-e93928ee3c86?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)like [hallucinations](https://substack.com/redirect/cc6052e7-2d0b-42bb-a760-ebf7e38d82b7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)and [prompt injections](https://substack.com/redirect/2575c631-52fd-4bb4-885f-63464eba523e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Whole different kettle of fish.

Let’s discuss the latest breakouts of the young AI models.

Axios summarizes it well in [“AI’s alarming new skill: breaking out of the test lab”:](https://substack.com/redirect/e69eab20-1b2a-4b9d-965a-f0f935470f72?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “Frontier AI models are getting scary good at breaking rules in ways their creators didn’t anticipate.” [](https://substack.com/redirect/de93328e-aaab-481a-b11f-034bbe92b400?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)“Why it matters: Forget [AGI](https://substack.com/redirect/eb5cc775-ef4c-478b-bd27-115dd549b7f4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and superintelligence timelines. Today’s models are already slipping past guardrails, carrying out sophisticated, multistep cyberattacks and — in at least one case — compromising real-world infrastructure, sometimes before their creators know what happened.”“Case in point: OpenAI [said Tuesday](https://substack.com/redirect/3142675c-2748-4568-8753-8b29fd5de96e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that GPT-5.6 Sol and “an even more capable pre-release model” carried out last week’s [AI-led cyberattack](https://substack.com/redirect/0aab0dfc-e895-4178-ab8b-a0ebcf183b60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on Hugging Face.”“OpenAI says its models were asked to solve a hacking challenge during pre-deployment testing and went to extreme lengths to win.”“The models decided on their own to break out of their walled testing environment, inferring that Hugging Face — a popular platform for hosting AI models and datasets — might hold the test’s answers.”“The models used stolen credentials and additional vulnerabilities to gain access to part of Hugging Face’s production infrastructure.”

Of course, allowing nascent [AI models to hack through systems](https://substack.com/redirect/ab703575-8580-4567-be03-54626ba1eded?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)in sandboxed environments is a long-time practice in the tech industry. Red-Teams, and [simulated ‘war games’](https://substack.com/redirect/b4f83059-c73c-4e8e-9400-1f74e136f4d7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)and all.

But these models are showing new capabilities that are surprising the veternas.

> “What they’re saying: Clément Delangue, co-founder and CEO of Hugging Face, [called](https://substack.com/redirect/bd7a229e-2df3-4ecf-9e48-c15057701da5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) the incident an “attack unlike anything we’ve seen before” and praised OpenAI for its partnership as the companies investigate what happened.”“It’s quite mind-blowing that all of this happened autonomously,” he [added](https://substack.com/redirect/14302581-e9c6-4eb1-bc98-68b3b800730d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).”“Logan Graham, head of Anthropic’s frontier red team, said he [told](https://substack.com/redirect/1737fdff-d584-49bd-b4aa-a5416e6528b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) his team to “remember this moment as the first true AI safety incident.”

Of course the testing also includes [open souce AI models](https://substack.com/redirect/2ec250cd-07b8-4cdc-9881-790c9be75436?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from around the world, [including China.](https://substack.com/redirect/2e53a60b-6ffc-4490-9dc6-cc031b42c5e1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “The intrigue: Hugging Face used GLM 5.2, an open-weight model from Chinese AI company Z.ai, to analyze the attack after running into guardrails when using U.S. frontier models.”“Between the lines: OpenAI’s latest models aren’t the only ones finding ways to cheat evaluations.”“The U.K.’s AI Security Institute [said](https://substack.com/redirect/d68fccd9-ef83-4dd1-9662-394623588a70?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) Tuesday that every model it tested attempted to cheat at least some of the time on its cybersecurity evaluations.”“AISI defines cheating as taking an out-of-scope or explicitly prohibited action to achieve the task’s goal.”“GPT-5.6 Sol attempted to cheat in 12.6% of test runs, while Anthropic’s Claude Mythos Preview did so in 7.8%.”“Models often failed to admit they had cheated when questioned afterward and described their cheating as wrong less than half the time.”

And these issues are proliferating particularly with [AI Agents](https://substack.com/redirect/c3ae3dca-0af2-44f0-b7a3-85470a6a19a1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from all [sorts of models](https://substack.com/redirect/588ca80b-f191-4b54-a29e-e7f91ec8bc70?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

> “Zoom in: Xbow — whose autonomous AI agents probe clients’ systems for security holes, with permission — [said Wednesday](https://substack.com/redirect/4f281b21-550f-4e92-a606-65b55d864fc6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that it has seen its own agents do similar things in internal testing.”“Seven months ago, the company forgot to switch on its safety guardrails during a lab test. Its agent then broke into a system, stole credentials and used them to map the target’s Slack workspace and probe its AWS accounts.”

But these are still developments that the experts have ways to tackle and tame.

> “Threat level: It isn’t new for models to game their safety evaluations. But as models grow more powerful, the fallout from these shortcuts is getting more severe, Chris Canal, CEO and co-founder of third-party evaluation company EquiStamp, told Axios.”“Letting your model loose on the internet has a blast radius,” Canal said. “If anything goes wrong, it could be hugely impactful, maybe to people’s lives.”“Canal was speaking generally about internet-connected AI evaluations, not OpenAI’s specific incident.”

Overall, these situations when they occur gather attentiona and headlines. Just like a baby figuring out a way to get out of the crib.

> “The big picture: The most capable OpenAI model behind the Hugging Face breach isn’t even public yet, raising the question of how safety testing needs to adapt to keep pace.”“Canal said independent evaluators previously had about five weeks to test a pre-release model before launch. That window has shrunk to as little as five days as companies race to ship.”

Scary indeed at first glance.

But the problems diminish in scope as the models ‘grow up’ and are ready for the real world. Then of course the threats are more external forces like [the aforementioned](https://substack.com/redirect/339ca1c4-99f7-4a66-89a1-e93928ee3c86?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)‘prompt injections’ and the like.

> “Reality check: The versions of these models the public can use carry stronger safeguards designed to block Hugging Face-style attacks.”“OpenAI, like other companies, intentionally dialed back those cyber safeguards for GPT-5.6 Sol and its unreleased model inside the testing environment — making them far more capable hackers.”

For those who want the intricate technical details of what really happened here, this it a way to that rabbit hole.

Here’s the story of how OpenAI’s GPT 5.6 Sol and advanced preview model tasked by OpenAI internal AI Researchers to solve a performance benchmark. WHich led to it scrounging around Hugging Face, for additional data repositories to accomplish that task. [Watch this youtube video](https://substack.com/redirect/c90143aa-06e3-458c-ac3e-264e9d06baba?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)by Theo-t3.gg, for the blow by blow narrative.

Again, the OpenAI models were just trying to solve for the internal benchmark they had been tasked with solving.

And they determinedly got into Hugging Face’s data collections to fulfill that task. They were NOT trying to hack anything maliciously. They were just being super task-focused like a [faithful Rothweiler.](https://substack.com/redirect/9fbd1600-24fa-41b1-8dd2-85c3cb60bedd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) As [Peter Gostev memorably describes](https://substack.com/redirect/b173fa01-2d89-46f0-b686-584276c4aa41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)OpenAI GPT 5.6 Sol vs the ‘wise owl’ Anthropic Claude Fable 5.

It’s quite the technical rabbit-hole for those so inclined.

But for the broader mainstream audience, here is the bigger takeaway with these headlines.

Overall, this is a compelling story that is always entertaining AND alarming to read about at first glance. It’s just young software being software.

No matter how ‘rambunctious’ they may seem at first glance.

But these are just ‘growing pains’ in early technologies. Experienced for decades with traditional software

And these new AI matrix math driven software technologies this [AI Tech Wave](https://substack.com/redirect/27576dbe-eab8-429a-8692-398ff12c1a7c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) are not so different.

Just trying to test the limits of their surroundings vs their intrinsic objectives. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/5f783e25-f89f-4fe6-8f8b-3a9cf3105938?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))
