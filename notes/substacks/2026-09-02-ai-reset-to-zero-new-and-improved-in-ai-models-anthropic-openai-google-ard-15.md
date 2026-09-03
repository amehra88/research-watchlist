---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260902200238.3.5325d7c672168f23@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/new-and-improved-in-ai-models-anthropic
source_date: '2026-09-02'
subscription_tier: free
tickers:
- NVDA
- AMD
- GOOGL
- PANW
- CSCO
themes:
- frontier_model_competition
- model_efficiency_evolution
- ai_regulation
- cybersecurity_competitive_landscape
- ai_inference_margin_compression
- humanoid_robotics_competition
ingestion_date: '2026-09-03'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [‘New and Improved’ in AI Models, Anthropic, OpenAI & Google. ARD #154](https://substack.com/app-link/post?publication_id=684161&post_id=213824368&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMzgyNDM2OCwiaWF0IjoxNzg4Mzc5NTkzLCJleHAiOjE3OTA5NzE1OTMsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.-SWHuzcC6zy2hT-hF5jI1TGoq7_IqTYaBfm2VFbe5-A)

### ...Fable 5.1’s fine print. Astra tips out on cyber. Gemini narrows the gap. World models level up.

‘New and Improved’, yes, again already. With caveats and asterisks.

All three big American AI labs are shipping or teasing upgrades this week, and every single one comes wrapped in safety gates, restricted access, or a smaller model than promised. On this [AI Tech Wave](https://substack.com/redirect/9ab1d2c7-0d8d-408f-92fc-aaf7a53e6a8e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), the fine print is where today’s tale needs to be told.

Today: Anthropic’s Fable and Mythos 5.1, OpenAI tip-toeing out Astra, its first ‘critical’ cyber model, and Google inching back into the frontier race. Plus a Gadget AI on World Labs’ new Atlas world model. My takes below, as discussed on the show.

## (1) Anthropic’s Fable and Mythos 5.1 Arrive, Wrapped in Caveats

First up. Anthropic released Claude Fable 5.1 and Mythos 5.1. Same model, two wrappers. Fable is the generally available version, with full safeguards. Mythos is the same frontier model with looser restraints, available only to vetted cybersecurity and life-science organizations, in programs built with the US government. I covered the original recast of this two-tier structure in [#1114](https://substack.com/redirect/2d9e8c7b-560e-462c-a325-6abb710515c6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) back in June.

The ‘improved’ seems real. Anthropic claims big jumps in agentic coding, science work and long-running tasks. More than doubling its predecessor on an agentic science benchmark. Testimonials about finding bugs that stumped engineers for years, and 38-hour unattended runs.

And the price cut is the headline for businesses. Cache reads, where the model re-reads context it has already processed, drop 75%, to 25 cents per million tokens. Anthropic says that cuts typical workload costs about 25%, and up to about 45% for heavy agentic work. Per VentureBeat, citing earlier FT reporting, the premium Fable 5 had only captured about 11% of Anthropic model spending across some 70,000 companies in Ramp’s data. This is Anthropic sharpening the pencil.

My take: the caveats ARE the product now. Read the label on this launch. A data-retention reversal after enterprise pushback, per CNBC, with a new ‘Enterprise Frontier Safeguards’ system that keeps monitoring data on the customer’s own cloud. Invisible watermarks on every output, per PCWorld, required under the EU AI Act. Cyber safeguards re-tuned to flag 60% fewer false positives, while still routing the dangerous stuff to older, safer models. And the whole release lands weeks after Anthropic disclosed that earlier models, in permissive test setups, escaped their sandboxes and touched real systems.

That context matters. This is what a maturing industry looks like on the way to the mega AI IPOs. The frontier labs are learning what consumer-products companies learned decades ago: past a certain scale, the label, the safety seal and the price point sell the product as much as what’s inside the box. ‘New and improved.’ Asterisk included, and on purpose.

Sources:

- [Anthropic: Introducing Claude Fable 5.1 and Claude Mythos 5.1](https://substack.com/redirect/9276eb55-cea4-4982-8b72-38aac9e7bdd6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [VentureBeat: Claude Fable 5.1 and Mythos 5.1 arrive with a 75% cost reduction for Fable cache reads](https://substack.com/redirect/6137e842-c360-485c-bdff-7c64c5301618?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: Anthropic Says New Fable AI Model Is Cheaper, Better at Coding](https://substack.com/redirect/628aebaa-cb90-4a0b-bdf2-3623496d3dc2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [CNBC: Anthropic changes data retention policy after pushback from customers](https://substack.com/redirect/cf7931c3-a9ef-4dbb-855d-45917797d63c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [PCWorld: Claude’s updated Fable and Mythos models watermark their replies](https://substack.com/redirect/de18a519-23ad-4bd1-b838-7d935cfab9b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1114: Anthropic recasts Mythos as Fable 5, with safety & pricing gates](https://substack.com/redirect/2d9e8c7b-560e-462c-a325-6abb710515c6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) OpenAI Tip-Toes Out Astra, Its First ‘Critical’ Cyber Model

Story two. OpenAI says its next model, Astra, is the first to cross its own ‘critical’ cybersecurity threshold. Meaning it can find previously unknown software flaws, build ways to exploit them, and chain those exploits together. Without a person guiding each step. During testing, per Axios, Astra discovered and chained two zero-day vulnerabilities, which OpenAI is now disclosing to the software’s maintainers.

So the rollout is on tip-toe. The broad version is ‘coming soon’, with the sharpest cyber capabilities held back. Early access goes to defenders first, per Wired: infrastructure companies in OpenAI’s ‘Daybreak Blue’ program, names like Cisco, Cloudflare and Palo Alto Networks, so they can harden systems before anything comparable spreads. A new misalignment monitor watches the model’s actions, and OpenAI itself warns it may flag legitimate work by mistake. Even work that has nothing to do with cybersecurity.

This follows the summer’s cautionary tales. OpenAI’s July disclosure that models in a test environment escaped the sandbox and hacked a real platform. Anthropic and the UK’s AI Security Institute disclosed similar incidents. The whole industry has been reminded that capable agents explore paths their operators didn’t anticipate.

My take: watch the release pattern here, it’s new. The most aggressive lab in the business is voluntarily slowing its own launch, pausing frontier training to harden the containment, and giving defense a head start over offense. Some of that is the [safety pose](https://substack.com/redirect/ca25c5a7-8f46-466c-9923-c7cd72aeb5b2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I described in ARD #144, struck partly for regulators and enterprise buyers ahead of the IPO parade. But some of it is a real capability threshold being crossed. Both can be true. The asterisk on Astra isn’t just marketing copy. It’s the fine print doing the work beyond the headline.

And as I covered in [#1166](https://substack.com/redirect/a1728c12-75b6-439f-96e0-e3aee98d7883?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), these long-running agents are exactly where the leverage, and the risk, compound together.

Sources:

- [Axios: OpenAI to limit access to Astra’s most powerful cyber tools](https://substack.com/redirect/db7c5e7f-26fc-4d6b-a8db-7510083357ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Wired: OpenAI Is About to Release Its First AI Model With ‘Critical’ Cyber Abilities](https://substack.com/redirect/407b230f-5236-43e1-b801-807484c512c1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #144: Strike a Pose: OpenAI, Anthropic & Apple](https://substack.com/redirect/ca25c5a7-8f46-466c-9923-c7cd72aeb5b2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1166: The Meter’s Running on Long AI Agents](https://substack.com/redirect/a1728c12-75b6-439f-96e0-e3aee98d7883?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) Google’s Gemini Inches Back Toward the Frontier

Story three. Google is set to release Gemini 3.8 Flash, possibly this week, per the WSJ. The claim that matters: in head-to-head testing inside Google’s own internal coding tool, Google engineers preferred it to Anthropic’s Opus. That’s a real benchmark of sorts, engineers voting with their fingers and eating their own dog food.

Now the asterisks, and there are several. It’s a Flash model, the smaller, cheaper, faster line, not the frontier ‘Pro’ tier. The new Pro is months behind schedule. Internal 3.5 Pro candidates were scrapped for not being better enough. Gemini 4 is still in post-training. And the leadership backdrop: a co-founder stepping aside last month, marquee researchers departing, and a new lab chief pushing pace, with a high-profile post-training hire brought in to sharpen reinforcement learning.

I covered Google [falling back in the AI coding race](https://substack.com/redirect/f11c37cb-f6e4-4575-81fe-cd482b5c6aa4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in ARD #121, after covering its developer push with [Gemini CLI](https://substack.com/redirect/163bf117-a3fa-4c68-bbe7-bf1a4f03ef02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in #763. This is the pendulum swinging back.

My take: small models are how you iterate fast, and Google is focused on it. Flash models are ‘good enough’, cheap to modify, so multiple teams can run experiments at once.

While changing a giant Pro model means corralling the whole company’s compute. Google is using the Flash line as its fast lane back into the coding race, while the heavyweight models take their time in the shop. ‘New and improved’, in deliberately small steps. The asterisk here isn’t safety. It’s size. And it’s a solid choice on the way back in AI Coding. Speed with ‘good enough’ and reliable results.

Sources:

- [WSJ: New Google AI Model Said to Narrow Gap on Coding Ability](https://substack.com/redirect/10df80cb-63e4-47e3-b0da-8d6fbd25f747?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #121: The Many AI Twists and Turns Accelerate](https://substack.com/redirect/f11c37cb-f6e4-4575-81fe-cd482b5c6aa4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #763: Google ups its Game for AI Developers with Gemini CLI](https://substack.com/redirect/163bf117-a3fa-4c68-bbe7-bf1a4f03ef02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: three labs, three tip-toes forward. Anthropic is selling trust and economics as hard as intelligence. OpenAI is metering out its most dangerous capabilities on its own clock. And Google is winding its way back into the AI coding leadership ranks. Although it has a much bigger opportunity, and more work to do, in bringing Gemini apps and services to the masses globally. But it should be able to walk and chew gum at the same time.

‘New and Improved.’ The oldest phrase in consumer marketing. It used to sell detergent and toothpaste.

Now it ships frontier AI models. Quarterly, sometimes faster. When the front of the box says ‘new and improved’, turn the box over and read the label. All three of the big American AI labs are shipping or teasing upgrades, and every single one comes with caveats and asterisks. Safety gates. Restricted access. A smaller model than promised. This week on the [AI Tech Wave](https://substack.com/redirect/9ab1d2c7-0d8d-408f-92fc-aaf7a53e6a8e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), the fine print is where the story is.

## Gadget AI: World Labs Levels Up the ‘World Model’

Today’s Gadget AI is a model for worlds, not words. World Labs, the spatial intelligence startup led by AI Guru Fei-Fei Li, widely called the godmother of AI, released Atlas, its next-generation world model.

What it does, per the announcement: give it a photo or a few, and it builds a coherent, explorable 3D scene. Camera control down to the pixel, up to a minute of video at 1440p. It reconstructs real spaces from a handful of phone snapshots, outputs actual 3D geometry, and runs ‘real-to-sim’ simulations for robots.

The WSJ’s recent column on world models frames the ambition: text is a lossy description of reality, and robots need models trained on worlds, not words. One investor’s honest caveat in that piece: this generation of world models is roughly where language models were at GPT-2. The money is real though: World Labs has raised about $1.23 billion, from Nvidia, AMD, Autodesk, Fidelity and others.

My take: this is a promising area for AI models, and a fitting one. It could bring Nvidia’s history, which started in gaming chips, full circle to user-created virtual worlds with significant gaming elements. Kind of what services like Roblox and Minecraft already hint at today. It’s also the same ‘Physical AI’ thread I mapped in [#1195](https://substack.com/redirect/d2f5b2f5-6397-42b4-a59b-195e6c27bae6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) this weekend, and in [‘Beyond LLM AIs to World Models’](https://substack.com/redirect/266a54aa-3207-4a4d-8c71-7ac38b7fba7f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in #909, well before it was fashionable. A lot of ‘new and improved’ still required from here to there. But this is one label where I’d underline the ‘new’ before the asterisk.

Sources:

- [World Labs: Atlas, A World Model for Spatial Intelligence](https://substack.com/redirect/86f58283-23d1-47cc-b10f-e5b8ca26f8a5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [WSJ: AI’s Next Big Leap Is Into the Real World](https://substack.com/redirect/39fa2020-87d5-4262-bbf4-53532efce056?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Crypto Briefing: World Labs unveils Atlas, an omni world model for spatial intelligence](https://substack.com/redirect/dc9b3c91-9ece-4a82-a50a-8bd94450a109?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Reuters via Yahoo Finance: AI pioneer Fei-Fei Li’s World Labs raises $1 billion in funding](https://substack.com/redirect/c9713cdb-dc8a-4314-9d21-7404fae8cf1a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #909: Beyond LLM AIs to World Models](https://substack.com/redirect/266a54aa-3207-4a4d-8c71-7ac38b7fba7f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1195: Physical AI w/ Nvidia’s Long Game in Robots, Cars & More](https://substack.com/redirect/d2f5b2f5-6397-42b4-a59b-195e6c27bae6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Q&A

Q1: What’s the most intriguing aspect of World Models for MP?

ANSWER: the prospect of user-defined games and simulated environments. Think worlds with the depth of GTA V or Red Dead Redemption 2, games that take years and enormous work to make today, delivering extraordinary simulated experiences to hundreds of millions. Imagine that done on a much shorter schedule. It seems possible technically, but the path from here to there looks long and arduous. Years of ‘new and improved’, version by version.

Q2: What’s the least appealing aspect of World Models?

ANSWER: the potential loss of truly shared global experiences. A GTA V or an RDR2 is a common world, shared by millions of players at once. That shared culture is part of the magic. GTA 6 lands November 19 and tens of millions will experience it the same day, yours truly included. A billion personal worlds could fragment that, the way the broader media environment has already fragmented. Something to watch as this category grows up.

Today’s [AI-RTZ #1197](https://substack.com/redirect/f9eb86d3-1e28-4029-a669-f9dfbefa9797?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) went out this morning: Nvidia’s $3.5 billion MediaTek bet, up and down the AI stack.

Tomorrow, we’re back with ARD 155 and AI-RTZ #1198. Keep reading the fine print on this [AI Tech Wave](https://substack.com/redirect/9ab1d2c7-0d8d-408f-92fc-aaf7a53e6a8e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). It’s all ‘new and improved’, asterisks and all. Thanks for joining us, AI Curious Folk. Stay tuned.

## Full Source Reading

Everything cited today, in one place.

### Anthropic’s Fable and Mythos 5.1

- [Anthropic: Introducing Claude Fable 5.1 and Claude Mythos 5.1](https://substack.com/redirect/9276eb55-cea4-4982-8b72-38aac9e7bdd6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [VentureBeat: 75% cost reduction for Fable cache reads](https://substack.com/redirect/6137e842-c360-485c-bdff-7c64c5301618?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: Anthropic Says New Fable AI Model Is Cheaper, Better at Coding](https://substack.com/redirect/628aebaa-cb90-4a0b-bdf2-3623496d3dc2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [CNBC: Anthropic changes data retention policy after pushback from customers](https://substack.com/redirect/cf7931c3-a9ef-4dbb-855d-45917797d63c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [PCWorld: Claude’s updated Fable and Mythos models watermark their replies](https://substack.com/redirect/de18a519-23ad-4bd1-b838-7d935cfab9b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1114: Anthropic recasts Mythos as Fable 5](https://substack.com/redirect/2d9e8c7b-560e-462c-a325-6abb710515c6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### OpenAI’s Astra

- [Axios: OpenAI to limit access to Astra’s most powerful cyber tools](https://substack.com/redirect/db7c5e7f-26fc-4d6b-a8db-7510083357ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Wired: OpenAI’s first AI model with ‘critical’ cyber abilities](https://substack.com/redirect/407b230f-5236-43e1-b801-807484c512c1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #144: Strike a Pose: OpenAI, Anthropic & Apple](https://substack.com/redirect/ca25c5a7-8f46-466c-9923-c7cd72aeb5b2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1166: The Meter’s Running on Long AI Agents](https://substack.com/redirect/a1728c12-75b6-439f-96e0-e3aee98d7883?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Google’s Gemini 3.8 Flash

- [WSJ: New Google AI Model Said to Narrow Gap on Coding Ability](https://substack.com/redirect/10df80cb-63e4-47e3-b0da-8d6fbd25f747?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #121: The Many AI Twists and Turns Accelerate](https://substack.com/redirect/f11c37cb-f6e4-4575-81fe-cd482b5c6aa4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #763: Google ups its Game for AI Developers with Gemini CLI](https://substack.com/redirect/163bf117-a3fa-4c68-bbe7-bf1a4f03ef02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: World Labs’ Atlas

- [World Labs: Atlas, A World Model for Spatial Intelligence](https://substack.com/redirect/86f58283-23d1-47cc-b10f-e5b8ca26f8a5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [WSJ: AI’s Next Big Leap Is Into the Real World](https://substack.com/redirect/39fa2020-87d5-4262-bbf4-53532efce056?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Crypto Briefing: World Labs unveils Atlas](https://substack.com/redirect/dc9b3c91-9ece-4a82-a50a-8bd94450a109?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Reuters via Yahoo Finance: World Labs raises $1 billion in funding](https://substack.com/redirect/c9713cdb-dc8a-4314-9d21-7404fae8cf1a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #909: Beyond LLM AIs to World Models](https://substack.com/redirect/266a54aa-3207-4a4d-8c71-7ac38b7fba7f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1195: Physical AI w/ Nvidia’s Long Game](https://substack.com/redirect/d2f5b2f5-6397-42b4-a59b-195e6c27bae6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### AI Labs: New & Improved, But Caveats Apply

### Google’s Gemini 3.8 Flash: A Step Forward

### World Models: Gaming’s Next Frontier?

### AI Gaming: Faster, Shorter, Less Common

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
