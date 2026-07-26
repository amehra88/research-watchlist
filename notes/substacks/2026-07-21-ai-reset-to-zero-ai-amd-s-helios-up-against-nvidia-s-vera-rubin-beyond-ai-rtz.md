---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260721050305.3.cc693cdb05fad20c@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-amds-helios-up-against-nvidias
source_date: '2026-07-21'
subscription_tier: free
tickers:
- AMD
- NVDA
- MSFT
- META
themes:
- silicon_architecture_competition
- ai_compute_topology
- inference_compute_economics
- hyperscaler_capex_buildout
- chip_design_competition
ingestion_date: '2026-07-26'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: AMD's Helios up against Nvidia's Vera Rubin & beyond. AI-RTZ #1154](https://substack.com/app-link/post?publication_id=684161&post_id=207671404&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNzY3MTQwNCwiaWF0IjoxNzg0NjEwMzQ1LCJleHAiOjE3ODcyMDIzNDUsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.E_Jbn5MmC4D2HMk2VHSV2mSKhyOyYp0Znx4_TLWOiks)

### ...a competitive offering vs a globally dominant AI Compute vendor

It’s appropriate of course that Nvidia and AMD who have long competed with each other on chip share in local computer desktop and laptops, are now meeting each in the AI Cloud infrastructure market.

I’ve had a lot of positive things to say about Nvidia’s multi-year AI Compute system roadmap in these pages. And its founder/CEO [Jensen Huang](https://substack.com/redirect/1a71b710-d8f0-449d-b471-a2cd99acefbe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of course in terms how he’s [executed thus far](https://substack.com/redirect/7ee6599c-01f3-4fcd-ad3b-5692db3897ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)over [three decades](https://substack.com/redirect/1f25b554-b70e-48a0-b4fb-1bc4f30f69e9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

A dominant share of the global AI Infrastructure market in this [AI Tech Wave](https://substack.com/redirect/c448b0ea-fc4d-4974-a328-5674ab9a5d57?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), that is measured north of 90% or more. But in a globally supply constrained market at least through the end of the decade, and an AI market that is growing leaps and bounds, that doesn’t mean there aren’t growth opportunities for competitors.

[AMD](https://substack.com/redirect/285d0a2a-b697-4b56-9e4c-adc17a575aab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is of course, one of those competitors. They’re out with a competitive offering called [Helios](https://substack.com/redirect/d50ddddd-1651-451b-9ee9-73239858c3b4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that needs it time under the spotlight. Along with some new options for some key customers discussed below.

CNBC lays it out in “AMD launches Helios, its first rack AI system to rival Nvidia, adding Microsoft as newest buyer”:

> “Microsoft announced Monday it will deploy AMD Helios racks in its Azure data centers, joining other early customers Meta, OpenAI and Oracle.”“Helios is AMD’s first rack-scale system for AI and its most competitive move against Nvidia yet. It will ship later this year.”“CNBC got an exclusive first detailed look inside AMD’s new system at the Texas lab where it’s being developed and tested.”“After a decade-long comeback, chip giant [Advanced Micro Devices](https://substack.com/redirect/9f0b5bd7-bef6-493b-b48a-9d6cd16d39f4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is preparing to ship its first rack-scale system for [artificial intelligence](https://substack.com/redirect/e67f2202-8698-4916-b4f9-13f2febc2bf1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), called Helios, to a growing list of customers that now includes [Microsoft](https://substack.com/redirect/0ae6e16c-ce17-43a7-816e-b50f934d77ac?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).”

Strategy of course is led by [AMD CEO Lisa Su,](https://substack.com/redirect/6d5a2643-4bbf-4e14-aa55-8843ace179b8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) a [distant cousin](https://substack.com/redirect/b96a914d-bf65-4792-9c39-8299ace1a2ca?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of Jensen Huang.

> “It’s the first rival to [Nvidia](https://substack.com/redirect/8fbb616f-6cc3-4791-a16c-a1c888cd1968?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’s wildly popular Grace Blackwell and [Vera Rubin systems](https://substack.com/redirect/844722b0-f893-4eeb-a751-b864913d1280?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and is aiming to give the world’s most valuable chipmaker its first real competition in years.”“Microsoft announced Monday it will use the Helios system in its data centers, joining [Meta](https://substack.com/redirect/a194a876-1f18-4ffb-93f1-b5411cf7f6dd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [OpenAI](https://substack.com/redirect/5a4c2295-02b4-4dd2-8897-18f3cc357a51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [Oracle](https://substack.com/redirect/a59ace2d-a4a8-4158-b70e-be7b5a17b9ea?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and others in a race to grab as much compute as possible.”“AMD will begin shipping to customers, including Microsoft, later this year. Shares of AMD climbed more than 4% on Monday. Microsoft stock climbed more than 1%.”

It was a well orchestrated rollout of course with Microsoft, from the very top.

> “We are expanding the Azure infrastructure portfolio with AMD Helios to give customers the performance, scale and choice they need to build and run the next generation of AI applications,” Microsoft CEO [Satya Nadella](https://substack.com/redirect/376d29f9-00f4-4257-8655-a37a4071ba06?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) wrote in a press release.”

These systems are skewed more to [AI Inference than training](https://substack.com/redirect/6c8c521c-278c-4606-b036-bd4d37804be6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), which is viewed as the largest, and the fastest growing AI computer market this this point.

> “The new Helios system will power frontier model inference for Microsoft, its AI customers and support Azure AI services. Microsoft will also add two new computing instances run on AMD’s latest “Venice” central processing units, or CPUs, one for agentic AI and data pipelines, and another for semiconductor design.”

The ‘Venice’ CPU units of course go against the ‘Vera’ in Nvidia’s Vera Rubin AI systems.

Names matter in the AI world of course, and they tend to like Greek origins.

> “Named for an ancient Greek god who pulls the sun across the sky with the help of four horses, Helios brings together four things AMD does in-house: GPUs, CPUs, networking and software.”“We’re very focused on providing the best total cost of ownership, the lowest cost per token, all in,” data center head Forrest Norrod told CNBC about AMD’s first-generation system. “And our customers are telling us that we’re achieving that.”In May, AMD CEO Lisa Su told CNBC’s Jim Cramer that Helios has “significant benefits” over Nvidia’s rack-scale systems, “when you’re talking about inference and when you’re talking about memory bandwidth and memory capabilities.”

Pricing looks comparable to [Nvidia](https://substack.com/redirect/12989c41-a697-42d4-9ac9-25c7cc587857?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), ahead of the inevitable customization and ‘bells and whistles’ that take these systems into the millions and beyond.

> “While AMD wouldn’t comment on cost, the Futurum Group estimates Helios will cost between $5 million and $5.5 million. That’s compared with Futurum estimates of $3.5 million to $4 million for Nvidia’s second-generation rack-scale system, Vera Rubin.”“At up to 7,000 pounds, Helios is also wider and heavier than Nvidia’s Vera Rubin.”

There’s a daunting hill to climb from a competition perspective.

> “Nvidia controls more than 95% of the data center GPU market, according to the Futurum Group. AMD only holds some 4.5% of the market, but Helios could change that.”“I think there’s a serious case in which AMD does great and can get to 20% and 25%. And by the way, this is hundreds of billions of dollars of revenue,” said Daniel Newman, analyst and CEO of the Futurum Group.”

Perhaps. On a long road ahead. But the expectations are being set for the markets.

> “In the first quarter of 2026, data centers made up the majority of AMD’s revenue, up 57% year over year. AMD told CNBC that it plans to book tens of billions in data center AI revenue starting in 2027, the majority coming from Helios.”“In data center CPU market share, [Intel](https://substack.com/redirect/cfb0f62e-5d6c-4e8a-a020-af9fb384dc3b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) remains the clear leader, but AMD has steadily been gaining ground. This CPU leadership sets AMD apart from Nvidia, which launched its first server CPU in 2021 and shifted strategies to [renew focus](https://substack.com/redirect/3d482ad4-41c7-4ee3-a9ac-7f927617abe9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on the chips this year.”

A lot of the current product line was put together through acquisitions:

> “Each Helios tray also has up to 12 networking chips made with technology AMD acquired when it [bought Pensando](https://substack.com/redirect/066a83c2-6878-4d3d-9e80-0fc83f792b84?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in 2022.”“It was one of several acquisitions that has helped enable Helios development in the last few years.”“AMD’s largest purchase to date was programmable chip company [Xilinx](https://substack.com/redirect/9cf3cddc-b2d3-4b1c-a148-7b12a57e5a3d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for nearly $50 billion in 2022. AMD also acquired server maker [ZT systems](https://substack.com/redirect/c1a6027d-6062-4488-a8d4-7d7cda537937?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for nearly $5 billion in 2025, and a series of software companies that helped it develop ROCm, its open-source alternative to Nvidia’s widely adopted CUDA software ecosystem.”“Counterpoint Research analyst Neil Shah said AMD’s Helios chips are “on par” with Nvidia GPUs and CPUs, but the “secret sauce is in the software and optimization.”

The key [Nvidia software moat](https://substack.com/redirect/4931b8ef-057d-412e-9c39-dcb88bba6748?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)to compete with is of course its [open source](https://substack.com/redirect/d47727e3-ea88-4ce6-88f0-effb6e2d56f7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)CUDA frameworks, developed patiently by Nvidia for over a decade.

> “With CUDA, I think Nvidia has a bigger ecosystem, and it’s quite ahead versus AMD,” he said.”“With Helios, AMD has the opportunity to make substantial strides, depending on how well early deployments fare.”“The question is going to be: Is AMD winning because they are technologically superior? Or does AMD win because there’s just such a constraint on capacity that if they can build it, someone will buy it?” Newman said.”

The [whole piece](https://substack.com/redirect/f523a51d-09bd-494b-9677-f54faad65733?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is worth a full read for additional details. There is also a 17 minute YouTube video that is worth a watch for interviews from some key people at AMD.

But the broader point is that Nvidia has some needed competition. With some marquee customers trying out their wares. And that is a step forward in [AI Tech Wave](https://substack.com/redirect/c448b0ea-fc4d-4974-a328-5674ab9a5d57?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/b3ad8c63-2ecc-49d1-b74a-1d374f75c2e2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))
