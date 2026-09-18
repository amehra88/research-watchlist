---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260917050237.3.e36649acda693b6e@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-ai-security-dilemma-chinas
source_date: '2026-09-17'
subscription_tier: free
tickers:
- NVDA
- AAPL
themes:
- frontier_model_competition
- china_ai_infrastructure_demand
- china_us_tensions
- model_efficiency_evolution
- ai_regulation
- china_export_controls
ingestion_date: '2026-09-17'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: The AI ‘Security Dilemma’. China’s Open Weights & Nvidia. AI-RTZ #1212 (Part 2)](https://substack.com/app-link/post?publication_id=684161&post_id=215618385&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNTYxODM4NSwiaWF0IjoxNzg5NjIxNTQ4LCJleHAiOjE3OTIyMTM1NDgsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0._Qp2HbaQ1xHyqpIlAkb45hElHeobXnhfk_PLu8AqbHA)

### ...China ships weights you can inspect. Nvidia owns the open shelf. The counter-case, and the fourth ‘Forever Problem’.

Yesterday, in [Part 1](https://substack.com/redirect/1f4e67ea-c98f-42eb-b38f-01033556c71f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), I laid out the security dilemma in AI reasoning: OpenAI’s GPT-6 Astra does some of its thinking in ‘neuralese’ loops that its own monitors can read less of, the technique came out of open research, and the reason it shipped now is margins, ahead of the mega-IPOs.

Today, the other side of the ledger. Who you can still inspect, where Nvidia sits, the technical counter-case, and why hidden reasoning belongs in my ‘Forever Problems’ file, in this [AI Tech Wave](https://substack.com/redirect/d90efd32-af48-4086-b0af-fbfc4fd96d1b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

## China, open weights and the inspection alternative

The obvious question is whether this is a closed-lab problem or an everyone problem. The technique is everyone’s. The opacity is part of the new business model.

China’s labs work on latent reasoning too. [Ouro](https://substack.com/redirect/aa876a95-50ef-4a50-8da0-f616cbe76a41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), the open-weight looped model from ByteDance’s Seed team and academic collaborators that I described in [Part 1](https://substack.com/redirect/1f4e67ea-c98f-42eb-b38f-01033556c71f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), is the proof. But they publish. The weights ship. Anyone can download the model, loop it, probe it, and fine-tune it inside their own network.

Bloomberg made the related case in a second column, “[You Don’t Have to Trust Chinese AI](https://substack.com/redirect/1e7dce04-4199-4775-babd-26f420339d50?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”. The argument is that national origin is a poor proxy for reliability. What matters is whether a model can be independently scrutinized.

The evidence. Sweden’s defence research agency found no technical backdoors in DeepSeek beyond the boilerplate on Chinese foreign policy. Cognition, the AI coding company valued near $47 billion, built a flagship model on Moonshot’s open-weight Kimi K2.7 and found it in line with leading US offerings.

> “Trust in a technology this consequential should depend on systems that can be inspected, tested and contained, giving users evidence instead of assurances.” ([Bloomberg Opinion](https://substack.com/redirect/1e7dce04-4199-4775-babd-26f420339d50?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))

And the irony the column lands on: trust is becoming an American AI problem. Edelman’s survey last fall had eighty-seven percent of respondents in China trusting AI, against thirty-two percent in the US.

I have written about [China leading the US in open source models](https://substack.com/redirect/c6118b17-b80f-43fa-856b-d2017e26f5ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for years now, and about the [global state of open source AI](https://substack.com/redirect/57d2104b-7eee-4e98-834c-714b97909c17?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in August.

Put the two Bloomberg columns side by side and the picture is uncomfortable for the US labs.

The country the regulators are told to fear is the one shipping models you can open up.

The companies the regulators are told to trust are the ones telling you, in their own system cards, that they can see less of what their models are doing.

Whether Beijing keeps supporting open weights if they threaten its control of information is a fair question. For now, the inspection model is the more durable one.

## Where Nvidia sits

Nvidia has not said a word about recurrent depth, and would not. Its posture is structural, and it is on the inspection side.

Late last month it agreed to buy Hugging Face for about $13 billion, with Jensen Huang committing that the platform stays open to the whole ecosystem. I wrote it up as [Nvidia buying the home shelf of open AI](https://substack.com/redirect/0ca9068e-bf50-455c-8c92-0a0451959bef?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Nvidia was already the largest contributor of open models to that shelf, with the reasoning data published alongside the weights.

The reason is not sentiment. Every open model, from every country, runs on Nvidia silicon, and inspectable models are what enterprises deploy inside their own walls. Hence the [open, secure AI alliance](https://substack.com/redirect/e52956a7-b52a-4b40-a655-b4be875eb5f0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) Nvidia assembled in July, and my case in May that [Nvidia and Apple could be the US open-source champions against China](https://substack.com/redirect/9899dcc0-0035-45a5-bb43-625da512878a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

If the closed frontier labs go quieter, the open shelf gets more valuable, not less. Nvidia owns the shelf. And is the US champion for it.

## The other side of the argument

Fairness requires the counter-case, and it is a good one technically.

Shorter reasoning traces correlate with capability. More capable models need fewer steps written out. A shorter trace is not the same as a hidden one, and OpenAI says Astra’s recurrent depth is limited precisely so its chains of thought stay legible.

Anthropic’s own research last year, [Reasoning models don’t always say what they think](https://substack.com/redirect/08c18f29-0ed4-4f19-95f4-2da4a64e0b64?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), showed that even a fully readable chain of thought is not a faithful account of why a model did what it did. The window was always partly frosted.

So the fair version is not that OpenAI blinded itself. The industry’s best window into its models was already narrowing. Technical and commercial imperatives accelerated the trend.

## My take

The third point, after yesterday’s two, and then the one I think matters most.

Three. The dividing line is not US versus China, or closed versus open source in the abstract. It is inspectable versus not.

China’s labs for now are doing latent reasoning research in the open, with weights attached. The US frontier labs are doing it in product, with system cards attached. A regulator who wants evidence instead of assurances currently gets more of it from Hangzhou than from San Francisco. That should concern Washington.

Now the part that belongs in my [‘Forever Problems’](https://substack.com/redirect/b0875476-a1a7-4690-879c-baddfc92bb09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) file.

I have mapped the problems that never close out on three axes: what a model [Knows](https://substack.com/redirect/5ef2493a-597d-45d0-8d15-1f02c7f3deec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (AI Hallucinations), what it [Reads](https://substack.com/redirect/b05b5801-aae8-4645-aaa4-8cfd34c0434f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (Prompt Injections), and what it [Remembers](https://substack.com/redirect/b0875476-a1a7-4690-879c-baddfc92bb09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (Memory Poisoning). Each gets ‘solved’ every few months and then returns.

Hidden reasoning is the fourth axis, and it was there from the start. I wrote [Can’t see how it works](https://substack.com/redirect/7030dfce-586b-47dc-aef4-b8cb37352957?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in July 2023, [Opacity to Transparency](https://substack.com/redirect/18b2234a-18da-4cf1-af8a-5fe30bf80ffc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that October, and [Into the ‘mind’ of an LLM AI](https://substack.com/redirect/6baf86b1-b6ab-4b44-b362-193018b4be2a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) when Anthropic first mapped features inside a model in 2024.

Call it what the model Shows. Readable chains of thought were the one recent improvement on that axis. Recurrent depth takes some of it back, for a good commercial reason, at the worst possible moment for the trust argument.

What makes this a Forever Problem rather than a scandal is that nobody can stop at the technique. If a numerical loop is cheaper and more efficient than a sentence in a human language, the loop wins, in every lab, in every country.

The only durable answer is the one the open-weights world already runs on: let the customer inspect the model, inside their own network, and demand evidence rather than assurances from anyone who will not allow it.

That is a market structure question, not a safety one. And it is where the money is going to be made and lost as these companies go public in this [AI Tech Wave](https://substack.com/redirect/d90efd32-af48-4086-b0af-fbfc4fd96d1b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

On Saturday the labs themselves took a version of that position. Dario Amodei’s essay, [We Must Pace the Frontier](https://substack.com/redirect/9d6255bc-c4f0-4e0a-92bb-33e299043d92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), commits Anthropic to seating outside evaluators inside the company, with employee-level access to training pipelines and the right to publish what they find.

By Saturday night Sam Altman, Elon Musk and Demis Hassabis had said yes. Evidence instead of assurances, offered by the labs most associated with assurances. Hugging Face asked to be the first evaluator in the door. I am calling the whole turn The Blip 3.0, and it was [Monday’s ARD 162](https://substack.com/redirect/fd43cd66-91ac-46fc-8009-eb3cd769d142?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

As I added to [Sunday’s piece](https://substack.com/redirect/9e741100-cdba-4ecf-b0ec-3678cd6b3cc9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), I am with [Jensen Huang](https://substack.com/redirect/40d552bc-a48a-4636-a994-dc56a818e3fc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on the call to action itself. The one part that is real is those outside evaluators, third-party safety teams seated inside the labs with badges, laptops and the right to publish.

We have always had machines that translate between human language and machine numbers. Neither compilers nor decompilers apply here, because neuralese is not code. It is the probabilistic machine thinking in its native form, and the reasoning trace was the one place regular AI users could read it.

The arithmetic behind all of this, from a gigawatt to a GPU to the quadrillions of calculations in a page of AI output, and a glossary of the numbers, get their own post next week: AI Loops 101, the next part of the AI data center ‘Explainer’ series here at AI-RTZ.

Tomorrow, the power side of the same build: ‘Behind the Meter’ power for the AI data center boom, and China’s head start on electrons.

It’s all a bit technical on the surface, but the high-level takeaways are critical in understanding the risk-reward dynamics of this [AI Tech Wave](https://substack.com/redirect/d90efd32-af48-4086-b0af-fbfc4fd96d1b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) relative to prior tech waves to date.

[Monday’s ARD 162](https://substack.com/redirect/fd43cd66-91ac-46fc-8009-eb3cd769d142?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), on [The Blip 3.0](https://substack.com/redirect/fd43cd66-91ac-46fc-8009-eb3cd769d142?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), tied Saturday’s, Sunday’s and both parts of this piece together. [Tuesday’s #1210](https://substack.com/redirect/0ae95950-4ac6-41e3-a244-761470b205b9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) followed the money to Anthropic’s mega-AI IPO to come soon.

Yesterday and today, we tackled the increasing dilemmas on AI models getting more opaque due to both technical and business reasons. Where the stakes are increasing into the trillions.

It all makes for an [AI Tech Wave](https://substack.com/redirect/d90efd32-af48-4086-b0af-fbfc4fd96d1b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) very different from all the preceding ones over decades past. Stay tuned.

## Sources

- [We Must Pace the Frontier, Dario Amodei, September 2026](https://substack.com/redirect/9d6255bc-c4f0-4e0a-92bb-33e299043d92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [You Don’t Have to Trust Chinese AI, Catherine Thorbecke, Bloomberg Opinion, September 7, 2026](https://substack.com/redirect/1e7dce04-4199-4775-babd-26f420339d50?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Quoted above

- [Reasoning models don’t always say what they think, Anthropic, April 2025](https://substack.com/redirect/08c18f29-0ed4-4f19-95f4-2da4a64e0b64?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Nvidia’s Hugging Face deal is a bet on open models, SiliconANGLE, September 3, 2026](https://substack.com/redirect/57d6d73d-59d4-4b5c-adee-4cf48db616eb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers

- [AI-RTZ #1211: The AI ‘Security Dilemma’. Hidden Reasoning & Mega-IPOs (Part 1)](https://substack.com/redirect/1f4e67ea-c98f-42eb-b38f-01033556c71f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #483: The other AI ‘open to close’ battle (September 2024)](https://substack.com/redirect/ba18747e-8f22-46dd-8964-c00a1422b263?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1167: ‘Forever Problems’ like Prompt Injections still being ‘Solved’](https://substack.com/redirect/b0875476-a1a7-4690-879c-baddfc92bb09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1111: ‘Prompt Injections’, the other ‘Forever Problem’ beyond ‘AI Hallucinations’](https://substack.com/redirect/b05b5801-aae8-4645-aaa4-8cfd34c0434f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #741: AI Hallucinations the ‘Forever Problem’](https://substack.com/redirect/5ef2493a-597d-45d0-8d15-1f02c7f3deec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Can’t see how it works (July 2023)](https://substack.com/redirect/7030dfce-586b-47dc-aef4-b8cb37352957?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI: Opacity to Transparency (October 2023)](https://substack.com/redirect/18b2234a-18da-4cf1-af8a-5fe30bf80ffc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #366: Into the ‘mind’ of an LLM AI](https://substack.com/redirect/6baf86b1-b6ab-4b44-b362-193018b4be2a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #744: China leads US in open source LLM AIs](https://substack.com/redirect/c6118b17-b80f-43fa-856b-d2017e26f5ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1185: The Global State of Open Source AI Models (part 2)](https://substack.com/redirect/57d2104b-7eee-4e98-834c-714b97909c17?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1156: Anthropic & OpenAI now against China open source AI](https://substack.com/redirect/75cff558-c5a3-467a-a770-08bdd6f5562c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1202: Nvidia Buys the ‘Home Shelf’ of Open AI, Hugging Face](https://substack.com/redirect/0ca9068e-bf50-455c-8c92-0a0451959bef?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1161: Nvidia Assembles AI ‘Avengers’, Open Secure AI Alliance](https://substack.com/redirect/e52956a7-b52a-4b40-a655-b4be875eb5f0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1089: How Nvidia & Apple can be the Global, US Open Source AI Champions vs China](https://substack.com/redirect/9899dcc0-0035-45a5-bb43-625da512878a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1183: Not one Skynet, but Billions of AI Agents](https://substack.com/redirect/79496a67-5dc9-4391-bcb0-0be07e050fc7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1201: My 7 Major AI Tech Wave Takes, 1,200+ Days in](https://substack.com/redirect/814646bb-886b-46c7-b841-b4f641b1700d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
