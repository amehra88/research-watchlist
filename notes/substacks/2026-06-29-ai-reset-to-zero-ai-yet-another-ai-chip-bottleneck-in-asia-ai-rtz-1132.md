---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260629050248.3.3c02344e0c952af9@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-yet-another-ai-chip-bottleneck
source_date: '2026-06-29'
subscription_tier: free
tickers:
- TSM
- NVDA
themes:
- advanced_materials_ai_infra
- ai_infrastructure_capex
- datacenter_buildout_pacing
- silicon_architecture_competition
- foundry_capacity
- hbm_competitive_landscape
ingestion_date: '2026-06-29'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Yet another AI Chip Bottleneck in Asia. AI-RTZ #1132](https://substack.com/app-link/post?publication_id=684161&post_id=203866693&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwMzg2NjY5MywiaWF0IjoxNzgyNzA5NjQ2LCJleHAiOjE3ODUzMDE2NDYsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.K95nKFabHjrtSqwkgtJHLS_jpT7F-qpBYyh7EOEDXmQ)

### ...Chips on Wafer on Substrate (CoWoS) packaging tech as critical as AI GPUs & memory.

If it was just like packaging Lay’s potato chips.

Regulars here at AI-RTZ and ARD podcast know of the l[ong litany](https://substack.com/redirect/f52bd7ec-c9b0-4fff-864c-b94e3ef0d62a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of AI bottlenecks this [AI Tech Wave](https://substack.com/redirect/2e03f606-c8d4-487a-ab1f-5badeeb85d92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)through the end of this decade at least. To the [AI GPUs](https://substack.com/redirect/e7ff6d15-cfb7-4d97-850d-b885d270271d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), AI [memory,](https://substack.com/redirect/c7bedee1-a6be-4993-8ab1-0e4b907cd2c1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) [AI Data Centers](https://substack.com/redirect/586a2fef-46cb-45b5-bce7-4fedeed60855?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Power](https://substack.com/redirect/fd710095-ae18-4fd7-bf72-b3be83b04243?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [AI Talent](https://substack.com/redirect/7fd6c23e-59bf-4e02-ac08-e7c347add5d2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)and others, add chip packaging technologies, aka CoWoS, explained below.

Especially as we move into a plethora of [AI devices, gadgets and local compute](https://substack.com/redirect/fe68ce09-524e-4f6a-9e1e-9c4e22de7c25?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that will be essential to take AI from ‘Search, Ask and Do’ functions of LLM AIs to AI doing things for us in the physical world. Be they [AI devices](https://substack.com/redirect/7c255ef3-d6fa-49a4-a3cf-d2cbdc2dfa16?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [smart glasses](https://substack.com/redirect/b528d761-bb1a-4e79-9b70-ed8eeaa4b402?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [robots, robotaxies,](https://substack.com/redirect/5f68d492-98bb-4976-a1b4-9345b65a4887?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) drones and so many more things not yet invented.

The NY Times outlines this well in[“How a Niche Technology became a Choke Point for AI”:](https://substack.com/redirect/c44c94f2-e91c-4be9-a207-fbf7c664088a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “Advanced chip packaging, which boosts computing power for artificial intelligence, has made the United States more reliant on Taiwan than ever.”“Chips don’t work without packaging. The process, also called assembly, typically wraps bare pieces of silicon in protective plastic with connectors to pass signals to other chips on a circuit board.”“These days, chips are frequently placed on an intermediary layer called a substrate, which is typically made of plastic and glass fiber and embedded copper wiring.”

These were technologies developed in the US, specifically at places like IBM, then sub-contracted to Asia, to do the then low cost, low margin work of assembling the substrates to acts as communication bridges between the chips themselves.

And the company that ran with the ball, why [Taiwan Semiconductor, aka TSMC](https://substack.com/redirect/e2635f98-053c-4f29-8e6e-a24d1c0eabec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)of course, in Taiwan. Yes, the one I’ve [been calling the ‘Fed’](https://substack.com/redirect/8a0412bd-5676-4c2b-8590-21feeea54d1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of the [AI Tech Wave](https://substack.com/redirect/2e03f606-c8d4-487a-ab1f-5badeeb85d92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

With a fair bit of help from [Nvidia along the way](https://substack.com/redirect/3fed8f56-ad12-4bf5-b6fc-d80ac6c8ea09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

> “TSMC offers advanced packaging called CoWoS, short for chip on wafer on substrate. Nvidia’s new Rubin processor, for example, uses CoWoS to bundle two large A.I. chips with eight stacks of high-speed memory that each contain 12 chips, amassing 336 billion transistors in one package. By 2029, TSMC predicts a 48-fold boost in computing transistors per package compared with 2024.”

And it’s the new bottleneck in AI systems of all types, be they for Nvidia, or the entire universe of big tech companies needing AI chips and systems for all sorts of things going forward.

> “[Taiwan Semiconductor Manufacturing Company](https://substack.com/redirect/fba6b060-034c-4a6a-a841-d45ae5b27121?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), which makes cutting-edge chips for Nvidia and other A.I. leaders, also packages nearly all of them. Its key suppliers and partners are mainly in Taiwan, too, facing the same threat from China that caused U.S. policymakers to funnel billions of dollars into boosting domestic chip fabrication.”[](https://substack.com/redirect/6857c565-0fc2-4086-828f-c125d5adfa96?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)“TSMC is already struggling to catch up with A.I.-driven orders. Its CoWoS production is about 30 percent short of demand, estimated Handel Jones, an analyst at International Business Strategies, who said TSMC accounted for about 95 percent of all advanced packaging.”“You can’t make them without advanced packaging,” said Mark Gardner, an Intel vice president and general manager for packaging and testing. “We’d be in a very different place in the A.I. world without it.”““All I see is demand continuing to go higher and higher,” said Kevin Zhang, a TSMC senior vice president. “It is certainly going to cause a lot of constraints.”[](https://substack.com/redirect/aee54e83-27f8-4404-90da-91e753123aca?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)“And costs remain high. An advanced chip package may cost $500, said Jan Vardaman, president of the research firm TechSearch International. Simpler packages may cost closer to $40, industry executives said.”“Some chip start-ups are deliberately avoiding designs relying on CoWoS, which can require months to design the required interposer.”“The packaging bottleneck has become a hot topic in Silicon Valley as TSMC has struggled to keep up with demand.”

The [whole piece](https://substack.com/redirect/c44c94f2-e91c-4be9-a207-fbf7c664088a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is worth a full read, particularly on the historical ins and outs of how the US lost its opportunity to build these technologies here vs [Asia.](https://substack.com/redirect/5c05be27-e1e1-4d06-9175-e5a1d106ce16?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) And how it’s still behind the curve on that front.

So add CoWoS bottlenecks this [AI Tech Wave](https://substack.com/redirect/2e03f606-c8d4-487a-ab1f-5badeeb85d92?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)to why computers and other gadgets will [continue to go up in price](https://substack.com/redirect/ac1e5071-fe94-4707-bf22-6bdd2df0dec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for the forseeable future. And it’s not just [RAMageddon](https://substack.com/redirect/ac1e5071-fe94-4707-bf22-6bdd2df0dec1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for Apple and others.

And it’s far tougher than packaging Lay’s potato chips. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/cd0660eb-4483-4465-8859-5ef04d6e73fd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))
