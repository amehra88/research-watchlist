---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260916050246.3.c3f722601881f38d@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-the-ai-security-dilemma-hidden
source_date: '2026-09-16'
subscription_tier: free
tickers: []
themes:
- frontier_model_competition
- model_efficiency_evolution
- ai_inference_margin_compression
- foundation_model_economics
- ai_regulation
ingestion_date: '2026-09-16'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: The AI ‘Security Dilemma’. Hidden Reasoning & Mega-IPOs. AI-RTZ #1211 (Part 1)](https://substack.com/app-link/post?publication_id=684161&post_id=215177743&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNTE3Nzc0MywiaWF0IjoxNzg5NTM1MjY0LCJleHAiOjE3OTIxMjcyNjQsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.XzeJ_U18Ee9NQjsOe7YEAZh88qgeXH29yJAEFdvM0TM)

### ...OpenAI’s Astra thinks in ‘neuralese’. Closed labs show less of it. Fewer tokens, better margins, ahead of the mega-IPOs.

There is an old idea in international relations called the [security dilemma.](https://substack.com/redirect/658c22fb-7a17-4594-a5ca-8e77a3c720a9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) One country arms itself to feel safe. Its rivals see the buildup and arm too, because they fear falling behind.

The issue comes to mind reading Bloomberg’s “[Altman’s Opaque AI Is Creating a New Security Dilemma](https://substack.com/redirect/202f9f47-d1d8-44d3-b641-eb3867142088?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”.

> “Artificial-intelligence researchers have been exploring the idea that AI models could be more powerful and cheaper to run if they disclosed less about how they worked, but this trade-off could make it harder for humans to check the systems aren’t doing anything harmful.”“The use of recurrent depth and other methods that limit insight into AI decision-making has raised concerns about safety and the potential for AI systems to be used in harmful ways, with some researchers warning that the industry is engaged in a dangerous arms race.”

The trigger was OpenAI’s new GPT-6 Astra model, and a technique called ‘recurrent depth’ that lets a model reason without writing its reasoning down in words we can read.

It is a timely reminder. And it lands on something I have been tracking in this [AI Tech Wave](https://substack.com/redirect/4a1f5beb-8859-4f8f-95da-92adbd162cdf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for three years: the industry’s steady walk from open research to closed AI products and services, as the industry pursues commercial opportunities at global scale.

Only now the thing being potentially closed is not the code, or the weights, or the training data. It is the model’s thinking itself.

Not just for hiding progress from competitors. But for sound technical reasons as well. A new dilemma indeed.

I’ve been highlighting these threads in a number of pieces of late. Last Thursday’s [AI Coding has a compiler, AI Coworking has none](https://substack.com/redirect/f5937509-9cdb-4d0b-8ca7-d82fd77f3e64?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and the two-parter on OpenAI’s ‘[Alien Mind’](https://substack.com/redirect/d4ff0ac3-28fa-41f4-a0c3-9ca653793380?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) essay, [Part 1 on Friday](https://substack.com/redirect/9f234bd1-e675-4b94-a3c2-d316f050f055?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Part 2 on Sunday](https://substack.com/redirect/6ca91f3e-634a-4eff-8dff-2cb4a9dba2df?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Those were about what the labs say they fear.

This one is about what they are increasingly choosing not to show. For a range of reasons.

One framing note before the details. Bloomberg tells this as an arms race between safety and profit. I read it more plainly.

This is the transition from academic research to commercial products.

I have watched that transition in every technology wave since the Internet in the 1990s. Research that starts out shared becomes product that is protected, once the money gets serious.

AI is doing the same thing. The difference this time is the size of the stakes, now in the trillions, and what is being protected. Not just the code. The reasoning.

## What OpenAI says about its own model

This is not a critic’s inference. OpenAI’s [safety overview for GPT-6 Astra](https://substack.com/redirect/0bc341fe-1f11-4fcf-b9c4-8e6ae13784af?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), published September 3, says it plainly.

> “Astra’s monitorability has decreased relative to the prior model, GPT-5.6 Sol. The model is more capable of controlling its own chain of thought, and less likely to include incriminating information in it.”

In adversarial tests, where OpenAI pushes the model to evade its monitors, Astra can sometimes stay undetected while deliberately underperforming, or while asked to perform sabotage tasks. OpenAI still calls a readable chain of thought a core research goal, and says auditing now needs to go beyond reading it.

Two more facts from the same page. Astra is the first OpenAI model to reach the Critical tier for cybersecurity under its Preparedness Framework. And OpenAI has added misalignment monitoring to all of Astra’s tool use in deployment, at what it calls significant compute cost.

In other words, the company is now paying, in GPU time, to watch a model it can read less of.

Sam Altman, [on X](https://substack.com/redirect/ac538889-0354-4cbd-8417-5a33b733ef13?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) two days before launch, said the company has been sprinting on safety priorities and slowing things as needed for the models after Astra.

## What recurrent depth does

Recurrent depth loops information through the same neural network layers over and over, instead of spelling each step out as text. The model ‘thinks’ in its own numerical representations, a vernacular researchers named ‘neuralese’ back in 2017. Bloomberg shows what that looks like next to a chain of thought a person can read.

## Words you can read. Numbers you cannot.

Some will say this is a solved problem. Computers have always run on numbers. We built programming languages, compilers and decompilers precisely to move between what people mean and what machines execute.

The subtle difference is that ‘Neuralese’ is not code. Binary has a dictionary, because humans wrote it.

A hidden state in ‘Neuralese’ is an ‘[AI matrix math](https://substack.com/redirect/98ecb7d2-ab13-4662-adb6-93654d34aefe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’ vector of thousands of numbers that nobody designed, learned in training, different for every input, every pass through the loop, and every new model.

That is the change regular AI users have been living through since [ChatGPT three years ago](https://substack.com/redirect/b7b35b82-3bb1-4b15-9b24-a7fb08dd1303?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), mostly without a name for it.

Seventy years of computing was deterministic. A person wrote every line, the same input gave the same output, and when it broke you could find the line.

This [AI Tech Wave](https://substack.com/redirect/4a1f5beb-8859-4f8f-95da-92adbd162cdf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) runs on probabilistic machines grown from data, where the same question can get two answers by design.

The reasoning trace was the bridge. For two years, regular AI users could watch the probabilistic machine work in plain English, a habit Perplexity in particular made mainstream, and DeepSeek took to its limit by showing the whole trace. Recurrent depth moves part of that thinking back into numbers.

Recurrent depth is one more loop, this time inside the model, and every turn of every loop is quadrillions of unreadable calculations.

## Who published it, and who productized it

The technique has an open academic lineage, and that matters, because the lineage is open and the product is not.

The research has been public all along. Meta published a version in late 2024, a university team in early 2025, and in October 2025 came [Ouro](https://substack.com/redirect/7a35eb6b-6821-4d70-815f-e5f9dc417101?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), the most prominent open-weight looped model to date, from ByteDance’s Seed team and university collaborators, with ‘AI Godfather’ Yoshua Bengio among the authors. Weights public, paper public.

The efficiency case is real. [Technical coverage](https://substack.com/redirect/9c8eb1d1-eb82-4322-b542-63fbb9239f60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) cites six to eighteen percent less training compute for the same result, and claims of up to fifty to ninety percent less compute at inference. The range is wide. The direction is not.

So the sequence is this. A Chinese-led team published the technique, weights attached. An American lab productized it and, by its own account, can now read less of what comes out.

Here’s how I’d summarize it all in how we got here.

## Why the safety researchers objected

In July 2025, forty-one researchers from OpenAI, Anthropic, Google DeepMind and government safety institutes published a [position paper](https://substack.com/redirect/1fd225ad-3a6c-4492-bdb1-7c7dec9babae?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) arguing that a readable [chain of thought (aka CoT)](https://substack.com/redirect/1f9de4ef-9dc6-47db-b5a8-05015caa440f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is a new and fragile opportunity for AI safety. Fragile because the moment reasoning moves into latent space, the window closes.

Fourteen months later, one of the signatory companies shipped a model that its own [system card](https://substack.com/redirect/0bc341fe-1f11-4fcf-b9c4-8e6ae13784af?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) says is harder to monitor.

The reaction, per [TechCrunch](https://substack.com/redirect/55b4972f-a457-4efc-80db-340575cd7a53?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Fortune](https://substack.com/redirect/66a28969-55e2-4f0d-9af2-05ed2bff388d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), came from safety researchers at Redwood Research and elsewhere. Scaling the technique could remove chain-of-thought monitoring outright. And the second-order worry: others will follow. The Information reported that Anthropic and Google DeepMind were already discussing it.

OpenAI’s chief scientist responded on X that legible chains of thought remain a core goal, that Astra’s use of recurrent depth is limited, and that monitoring may get harder for reasons unrelated to architecture. He did not say how much of Astra’s processing is visible and how much is not.

Both things are true. OpenAI has done more work on chain-of-thought monitoring than any lab. And it is the first to bring the trade-off to market.

## From academia to commerce, at trillion-dollar stakes

The business reasons are the same walk I have tracked for decades. Only the stakes changed.

Two years ago this month I wrote [The other AI ‘open to close’ battle](https://substack.com/redirect/f2895702-beff-4661-bc38-854cdb5e8394?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), when OpenAI first hid the raw reasoning of its o1 models from users and showed a summary instead. The company cited safety and monitoring. It also said, in the same breath, ‘competitive advantage’.

My read then was that the industry was moving from academia’s culture of sharing to product companies protecting their homework. Less copying others’ AI homework, less drafting in their wake.

Hard to remember, but only two years ago, OpenAI was a $150 billion private company. It is now heading toward a $1 trillion+ IPO by next year at the latest. And Anthropic is [days from filing its own](https://substack.com/redirect/fe4fabc3-809f-496c-97a5-13174934f039?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), as I laid out [yesterday](https://substack.com/redirect/730dae21-81c3-4845-aba3-82a4c469c93b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

I laid out the [compute commitments on both sides](https://substack.com/redirect/db9317a9-e6ca-4f6e-aa52-46897370dad9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) last week, about $750 billion against $517 billion. Every dollar of that is training and inference cost that a more efficient architecture reduces.

Which is why recurrent depth is not mainly a safety story. It is increasingly a business strategy story.

Fewer tokens per answer is a price cut that never shows up on the price list, as I wrote in last [Thursday’s ARD](https://substack.com/redirect/d0321516-f5ef-4d23-aa2f-e4155a9741aa?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). OpenAI’s CFO Sarah Friar told Goldman’s conference last week that Astra gets comparable results with sixty-eight percent fewer output tokens than Anthropic’s newest model.

It is hard not to connect that number to a model that does some of its thinking in ‘neuralese’ loops instead of words humans can read.

Part of the motivation is also to slow down distillation efforts to ‘learn’ from the models. Especially from China, which showed the world it could do exactly that with a visible chain of thought when [DeepSeek landed](https://substack.com/redirect/948516da-386a-447e-8b88-ef717cf1b727?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in January 2025.

It took a [commercial-versus-academia war for researchers](https://substack.com/redirect/3f172050-b082-4ea9-8038-0d92d59c7692?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that the companies won, a public market that pays for margin, and a technique that improves the financial metrics while reducing visibility.

The security dilemma is the mechanism. The mega-IPO calendar is the accelerant.

## My take

Two points today. The third, and the one I think matters most, comes tomorrow in Part 2.

One. This is the ‘open to close’ battle I flagged in September 2024, running along the [AI roadmap to AGI](https://substack.com/redirect/0c43080e-acd0-4990-a515-b4db6266e946?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from chatbots to reasoning to agents and beyond.

Two years further along and at a hundred times the stakes. It went code, then weights, then training data, then the reasoning shown to users, and now the reasoning available to the lab’s own monitors.

Each step had a safety rationale and a commercial one. The commercial one is the constant.

Two. The security dilemma is real, but the arms are not weapons, they are margins. The mega-IPO calendar, the compute bill in the hundreds of billions, and the price war I covered last Thursday all push the same way: fewer tokens, less visible reasoning, better unit economics.

OpenAI just happened to be first. But others are not far behind. Anthropic and Google are discussing the technique as well.

Tomorrow, Part 2: China’s open weights and the inspection alternative, where Nvidia sits, the technical counter-case, and why hidden reasoning belongs in my ‘Forever Problems’ file.

An impact of the AI Tech Wave worth tracking. Stay tuned.

## Sources

- [Altman’s Opaque AI Is Creating a New Security Dilemma, Parmy Olson, Bloomberg Opinion, September 4, 2026](https://substack.com/redirect/202f9f47-d1d8-44d3-b641-eb3867142088?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Safety overview: GPT-6 Astra, OpenAI, September 3, 2026](https://substack.com/redirect/0bc341fe-1f11-4fcf-b9c4-8e6ae13784af?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Sam Altman on X, September 1, 2026](https://substack.com/redirect/ac538889-0354-4cbd-8417-5a33b733ef13?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Quoted above

- [OpenAI’s new reasoning technique alarms AI safety experts, TechCrunch, September 2, 2026](https://substack.com/redirect/55b4972f-a457-4efc-80db-340575cd7a53?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Why are AI safety experts alarmed by reports OpenAI’s Astra model uses ‘recurrent depth’?, Fortune, September 3, 2026](https://substack.com/redirect/66a28969-55e2-4f0d-9af2-05ed2bff388d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [GPT-6 Astra, Looped Transformers, and Hidden Reasoning, Sebastian Raschka](https://substack.com/redirect/9c8eb1d1-eb82-4322-b542-63fbb9239f60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety, July 2025](https://substack.com/redirect/1fd225ad-3a6c-4492-bdb1-7c7dec9babae?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Scaling Latent Reasoning via Looped Language Models (Ouro), October 2025](https://substack.com/redirect/7a35eb6b-6821-4d70-815f-e5f9dc417101?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Training Large Language Models to Reason in a Continuous Latent Space (COCONUT), Meta, December 2024](https://substack.com/redirect/7db5852c-68bf-4d85-80c1-bf348f876826?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach (Huginn), February 2025](https://substack.com/redirect/438af3fb-9237-49ef-afbf-e4ae5c8ce34d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Translating Neuralese, Andreas et al., 2017](https://substack.com/redirect/55bf1c9f-05fc-4088-a383-c596830ffec3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers

- [RTZ #483: The other AI ‘open to close’ battle (September 2024)](https://substack.com/redirect/f2895702-beff-4661-bc38-854cdb5e8394?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1205: Coding has a Compiler. Coworking has None.](https://substack.com/redirect/f5937509-9cdb-4d0b-8ca7-d82fd77f3e64?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1206: OpenAI’s ‘Alien Mind’ Essay, & Asimov’s Three Laws (Part 1)](https://substack.com/redirect/9f234bd1-e675-4b94-a3c2-d316f050f055?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1208: The AI Existential Risk Essays, US vs China (Part 2)](https://substack.com/redirect/6ca91f3e-634a-4eff-8dff-2cb4a9dba2df?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #160: ‘Not So Fast’ in AI. OpenAI, Anthropic & the AI Economy](https://substack.com/redirect/d0321516-f5ef-4d23-aa2f-e4155a9741aa?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1204: Anthropic’s $517B vs OpenAI’s $750B Compute Race](https://substack.com/redirect/db9317a9-e6ca-4f6e-aa52-46897370dad9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1188: Anthropic’s mega-IPO Aims Past SpaceXAI & OpenAI](https://substack.com/redirect/fe4fabc3-809f-496c-97a5-13174934f039?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #845: The Commercial vs Academia war for AI Researchers](https://substack.com/redirect/3f172050-b082-4ea9-8038-0d92d59c7692?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #615: Deepest Lessons from DeepSeek](https://substack.com/redirect/948516da-386a-447e-8b88-ef717cf1b727?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1201: My 7 Major AI Tech Wave Takes, 1,200+ Days in](https://substack.com/redirect/f6fbb701-25d6-4732-bda8-07d06c6b7521?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
