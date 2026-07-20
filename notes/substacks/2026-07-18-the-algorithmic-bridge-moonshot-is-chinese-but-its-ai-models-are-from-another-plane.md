---
doc_type: substack_post
source: substack
publication: The Algorithmic Bridge
publication_url: https://www.thealgorithmicbridge.com/
source_email: <20260718193215.3.f97a781eaf1babb0@mg2.substack.com>
source_sender: Alberto Romero from The Algorithmic Bridge <thealgorithmicbridge@substack.com>
source_url: https://open.substack.com/pub/thealgorithmicbridge/p/moonshot-is-chinese-but-its-ai-models
source_date: '2026-07-18'
subscription_tier: free_plus_paid
tickers: []
themes:
- frontier_model_competition
- model_efficiency_evolution
- model_commoditization
- foundation_model_economics
- china_export_controls
- china_us_tensions
- ai_regulation
ingestion_date: '2026-07-20'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Moonshot is Chinese But Its AI Models Are From Another Planet

Thank you for being a free subscriber. You can [upgrade here](https://substack.com/redirect/00791b93-3166-45bb-8be5-0a3991f097b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# [Moonshot is Chinese But Its AI Models Are From Another Planet](https://substack.com/app-link/post?publication_id=883883&post_id=207563221&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNzU2MzIyMSwiaWF0IjoxNzg0NDAzMjA4LCJleHAiOjE3ODY5OTUyMDgsImlzcyI6InB1Yi04ODM4ODMiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.CyrM0p6-xapko47RidNjFoWmTLaDjkEsqoCb_AbDAGA)

### OpenAI, Anthropic, and America are in deep trouble

Hey, Alberto here! 👋 Each week, I publish long-form AI analysis covering culture, philosophy, and business. Paid subscribers get Monday how-to guides and Friday news commentary. If you’d like to become a paid subscriber, here’s a button for that:

I’m on vacation this week but made time to write this deep-dive on Moonshot’s Kimi K3, the first Chinese AI model at the level of America’s frontier models. And it’s open.

Moonshot’s [Kimi K3](https://substack.com/redirect/a903586e-fa8d-4e67-91fb-f5052730be98?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is the first Chinese open-source model to reach the level of the best American frontier models. In some areas, it’s on par with Anthropic’s [Mythos/Fable](https://substack.com/redirect/942f3a89-e590-4ef0-b43b-388bdfb787d7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and OpenAI’s [GPT-5.6](https://substack.com/redirect/0913b617-a9a6-4ca3-b94b-65eb41190ac4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). For those of you who remember DeepSeek’s ascent to notoriety in January 2025, this is Moonshot’s “[DeepSeek moment](https://substack.com/redirect/bb48dec3-270d-4d73-89f1-8d2e873f9f8e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA),” except more serious: Experts used to calculate that China was only six to nine months behind the top Western AI models.

Well, make it zero months, zero weeks, and zero days now.¹

DeepSeek proved that China can make an open model much more efficient than American AI labs without a large performance penalty even under severe hardware restrictions. Moonshot builds on that to prove that China can exploit those efficiency-gains-under-constraints to make an open model at the intelligence level of the best American AI labs. Expect, as the main consequence of this, for the geopolitical discourse around AI to increase in both intensity and urgency (at least after Moonshot publishes the model weights on July 27th). If the US government considered Mythos dangerous enough to withdraw from Western allies, what will it think about China having a Mythos-level equivalent? A bad regulatory move could push the entire world ahead of the US.

But before getting into the interesting analysis, let’s do a quick objective review of the model’s capabilities and its relative position inside the frontier AI ecosystem: Why is it making a fuss? Is this a new “DeepSeek moment”? Is it really as good as the best American models in general or only on less relevant benchmarks? All these questions can be summed up with this one: How good is Kimi K3?

### I. HOW GOOD IS KIMI K3?

The first place we have to look is, naturally, [the self-reported performance scores](https://substack.com/redirect/f6ed6e23-c294-4cc3-a82a-bcf240643551?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Capability-wise, K3 lands first, second, or third across benchmarks and displays a superior score-cost ratio across coding and agentic evals. It is essentially one rung above Opus-4.8 and GPT-5.5, and almost on par with Mythos/Fable and GPT-5.6. This means that one mistake by Anthropic or OpenAI will lead China to become the main AI superpower in the world (barring a clear inferiority in terms of chips and fabs, which is the hardware basis of AI models; more on that later).

This is what Moonshot itself says, though, which has an obvious incentive to pump its numbers. However, independent analysts agree for the most part. It’s not just Moonshot glazing its own model but the general sentiment. Here’s a short compilation of Kimi K3 being really good.

[Artificial Analysis](https://substack.com/redirect/d73c8b0b-f4f7-4d90-9eb4-6d0d594a93cb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a benchmarking firm, on how Kimi K3 compares to Anthropic and OpenAI’s top models (blue, brown, and black respectively):

The jump in capabilities and intelligence from Kimi K2.6 is huge. K3 falls only slightly behind Fable and GPT-5.6, both released recently—and at the price range of GPT (Claude is more expensive): “Cost per task ($0.94) is similar to GPT-5.6 Sol ($1.04), ~1/2 the price of Opus 4.8 ($1.80).” Kimi K3 is an appealing model for API users according to Artificial Analysis’ indices (it’s the only model in the frontier of capabilities that falls inside Artificial Analysis “most attractive quadrant”).

All in all, K3 will be an interesting compromise in the enterprise sector, as it lies comfortably between the cheapness of worse open models and the expense of closed ones at around its level.

Arena, another benchmarking firm, reports that Kimi K3 is considerably better than Fable on [frontend coding](https://substack.com/redirect/0a275c8f-0ea6-4542-9c91-3188b8465a19?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). This was the first result to go viral on K3’s capabilities, but I think it was extremely over-hyped in the sense that one benchmark on Arena means essentially nothing. It adds to all the other benchmarks that put K3 at a really, really good level—it’s just that “much better than Fable” is an unrealistic exaggeration. (The x-axis on the chart below that went viral is truncated at 1,450 to make the difference seem larger.)

I mean, we can be excited about the technological competition or worried about China “getting ahead,” but once you take a look at the amount of green in the chart below on “US vs China advantage,” you will calm down. Let’s not let excitement blur our judgment into a bad analysis.

Indeed, K3 falls considerably lower on Arena’s [overall text](https://substack.com/redirect/25628b8f-c0bd-43cc-b563-85bad473de9d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) ranking.

More great results from K3 here. It is also [#1 on creative writing](https://substack.com/redirect/7a3dd898-6d1d-48d1-8ca0-f8eda27d1abf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [#1 on Vercel’s Next.js agentic benchmark](https://substack.com/redirect/201b6b43-a45c-406f-86a3-f8aee0eded87?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [#3 on deepSWE](https://substack.com/redirect/deee9403-3a34-4d32-8be3-6efd85588948?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a long-horizon software engineering benchmark.

The overall impression I get from the benchmarks—as well as the reviews I’ve read, which, although anecdotal, add to the vibes—is that Moonshot’s portrayal of the model is accurate. It’s evidently a frontier model; there’s no denying that, and China has caught up to the US, but the top labs—Anthropic and OpenAI—remain slightly ahead. The bottom line is that there’s no comforting gap between the frontier and China for American labs to enjoy anymore.²

The question of “how good is Kimi K3?” which we have just answered with a resounding “really good,” leads us directly into our second question:

How is Kimi K3 so good?

### II. HOW IS KIMI K3 SO GOOD?

This is the million-dollar question. How on Earth did a smaller, resource-constrained Chinese open-source lab get to compete toe-to-toe with the extremely wealthy, extremely resourceful, extremely-spoiled-by-the-government American labs? To answer what seems to be a much harder question and also a more unexpected one, we need to consider several factors: size, training efficiency, algorithmic advances, and hardware limitations. There are also some far less pleasant possibilities: when it comes to Chinese AI, unlike in the US, everyone is guilty until proven innocent. Has Moonshot distilled from existing American models? Have they gamed the benchmarks or benchmaxxed the models? Have industry secrets leaked or diffused?

Let’s take a look.

A sneak peek at the positive response, which amounts to “Moonshot, like DeepSeek before them, seem clearly cut from a different cloth,” can be summed up this way: constraints breed creativity. Contrary to what it might seem, K3 is great because of Moonshot’s limitations as a small Chinese lab rather than despite them.

There are plenty of technical details in the [blog post on Kimi K3](https://substack.com/redirect/f6ed6e23-c294-4cc3-a82a-bcf240643551?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (thank you, open source). I don’t want to bother you with too much jargon, but a bit of it is always necessary to understand what’s going on. The first detail, and a rather surprising one, is that K3 is huge. The habit of using parameter count as a proxy for model capability faded away with the increasing closeness of the top labs in recent years. (Do you remember the GPT-4 circle vs GPT-3 circle viral image?) But open models don’t have time for secrecy, only progress and transparency. So we know K3 is 2.8 trillion parameters. According to Moonshot, it’s the first open model in the world in the 3T range. (Top models from OpenAI and Anthropic are thought to be in that or slightly higher range.)

Here’s a chart of the size increases of open models over time and a comparison between K3 and OpenAI’s open-source model (everyone went crazy that OpenAI would open a model, which is in itself funny when written down, and it gets only funnier when you look at the size comparison):

One reason not to get too excited about the number itself is that size is and isn’t a proxy for capability. You can have a smaller model that’s better than a bigger one, no problem. But, if done well, a large pre-train will naturally be better than a small one. So, although it’s a significant factor in capability, depending on who says “mine is bigger,” you can or can’t trust it to be a reliable heuristic for quality. (I won’t say here who I trust and who I don’t, but my reliability ranking is quite… broad.)

Another reason is sparsity.

Kimi K3 is extremely sparse, meaning that even if there are 2.8 trillion parameters in the model, the active ones at any given time are a tiny fraction of that. To be precise, K3 is a mixture of experts with almost 900 experts (specialized groups of parameters that are called on only when they are useful for the current task). Only 16 are active at a time, which means the model can draw on a very large pool of capabilities without using all of them for every request.

Combined with additional custom changes to how data moves through the model (Kimi Delta Attention and Attention Residuals—you don’t need to know what those are except in the sense that they enable two-digit efficiency gains at negligible cost increases), as well as improvements on the training process (INT4-native quantization), inference (expert parallelism) and data quality, Kimi K3 is roughly 2.5 times more scale-efficient—efficient at turning energy into intelligence—than Kimi K2. In short: Moonshot engineers are masters of turning scraps into gold.

In case you’re interested, here’s a snapshot of Kimi K3’s architecture:

There’s one common thread that should not go unnoticed here. Moonshot and DeepSeek are alike to the same degree that American labs are to one another, but not for the same reasons.

The reason why Anthropic and OpenAI have pursued the same goals (e.g., recursive self-improvement) and keep a similar pace of progress despite algorithmic advances and efficiency improvements often being unplannable eureka moments is that AI talent moves around a lot in the Bay Area. They all know each other and, naturally, the secrets of one lab are passed to the other without even the possibility of enforcing NDAs or IP claims. The trade secrets of the AI industry are kept from the world but not from one another.

However, the reason Moonshot and DeepSeek are alike is that they’re born out of the same ecosystem—an open and severely constrained ecosystem that needs to grow around scarcity, not abundance. They’re heavily incentivized by hardware shortages to keep everything in the open to benefit from other labs’ discoveries and grow together as well as to keep a razor-sharp focus on finding alternative paths that account for resource limits. This means that they don’t need to share DNA as OpenAI and Anthropic do so much as share a vision: let’s do more with less.

The idea that “constraints breed creativity” is mostly a slogan, but it’s also been seriously studied. A [cross-disciplinary integrative review](https://substack.com/redirect/e55dfb12-57f5-4f2f-aae4-c16aec88d507?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) found that creativity responds to a U-shaped relationship with constraints. Too few and you will wander. Too many and you will stall. As I see it, OpenAI and Anthropic are in one extreme of the U, being too wealthy to be forced to bother much about efficiency and stuff except when business pressures ask for it (instead, they will reset limits as if that’s equivalent to making the model as cheap as it can be). xAI is perhaps [the clearest example of this](https://substack.com/redirect/3c77209b-1d27-4961-ae4c-094b804f0161?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in the American AI ecosystem: huge datacenters, zero focus.

Chinese startups inhabit, instead, the middle of the U: constrained hardware-wise but capable of compensating for it with technical prowess and incredibly talented teams that will never scale a model by brute force but by ensuring first that the corresponding efficiency gains are in place. (Don’t get me wrong: American labs also have incredibly talented teams, but they might not be as motivated to direct that talent fully to overcome non-existent constraints.)

As a Google DeepMind researcher, Anika, [said](https://substack.com/redirect/ac04a59b-f975-453b-8fea-842ce711024b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): Moonshot demonstrates that “training is efficiency-compressible . . . a small lab with taste can compress the compute needed to make a frontier model, even if it can’t afford to serve one. the frontier is no longer something money can buy.”

But being creative also means hacks.

There are many cheap tricks a small AI team can deploy to benefit from the closed advances. This alternative path to greatness leads me to reassess Kimi K3’s capabilities: are all these advances on efficiency and intelligence legit, or has China copied America once again?

This has been the usual explanation for the question of “how has China caught up to American AI efforts so quickly?” Anthropic CEO Dario Amodei has stated Anthropic has detected several “industrial-scale campaigns” from Chinese actors—including but not limited to Moonshot—distilling Claude models. Although Amodei’s hawkishness against China has often been the target of mockery, this is not a minor issue. Quoting from [Anthropic’s blog post](https://substack.com/redirect/2d1e0ef8-97ec-4121-8905-9d9bf1bc3daf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in February:

> Distillation attacks undermine [chip export] controls by allowing foreign labs, including those subject to the control of the Chinese Communist Party, to close the competitive advantage that export controls are designed to preserve through other means.

The first problem is of a business nature. The labs doing distillation can obtain huge capability gains for their own models at a fraction of the time and the cost. The second problem is geopolitical. This makes export control measures moot. Insofar as Nvidia sells its chips to American labs from which the corresponding capabilities are later distilled, Chinese labs don’t need those chips themselves.

To conduct a distillation attack, external labs create fraudulent accounts and proxy services to make a massive number of exchanges with the best models to grab chat information—and even extract the reasoning traces—and use them to post-train worse models into higher benchmark performances. A sort of teacher-student symbiotic relationship (rather parasitic in this case because Anthropic doesn’t benefit). This is what Anthropic said about Moonshot specifically, whose attack scale is estimated at 3.4 million exchanges across agentic, code, and computer use tasks:

> Moonshot (Kimi models) employed hundreds of fraudulent accounts spanning multiple access pathways. Varied account types made the campaign harder to detect as a coordinated operation. We attributed the campaign through request metadata, which matched the public profiles of senior Moonshot staff. In a later phase, Moonshot used a more targeted approach, attempting to extract and reconstruct Claude’s reasoning traces.

Given that this was published in February, it’s perfectly possible that this particular campaign was used to post-train Kimi K2.6 (released April 2026), and even Kimi K3.

I find this explanation of China’s quick improvement to be generally believable but weak to explain every single performance increase from a Chinese model. In the case of Kimi K3, the evidence suggests against it (or, at least, it’s insufficient to explain the full capability increase): in several benchmarks, K3 is better than the best public models from Anthropic and OpenAI; you can hardly distill a teacher model into a superior student.

Analysis from the Western ecosystem broadly agrees with this view. Here’s an [OpenAI researcher](https://substack.com/redirect/24615054-2fb2-4631-b219-91d6a021912e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

Here’s another [OpenAI researcher](https://substack.com/redirect/b8e96d36-3f80-4100-86e9-dfdbe6a7275f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

Here’s [Amjad Masad](https://substack.com/redirect/6833783f-5c01-485d-bf16-252e96a67722?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Replit CEO:

[Nathan Lambert](https://substack.com/redirect/d9976b73-3245-44ff-9093-d76a176005c0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), an important voice on both open source AI and Chinese AI (he has [a great post](https://substack.com/redirect/fd5dd8c2-8111-47b8-812a-e0190470c669?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from May 2026 with notes on his trip to meet the Chinese labs), said this:

In his May post, he enumerated the differences he found most notable between America and China regarding how they approach AI. Among them: willing to do grunt work to improve the model (vs. obsessive individualism more common in the Western world), less ego, and fresher minds unburdened from prior ideas and ready to embrace new techniques and methods.

So, how do we square these extremely positive traits that Lambert attributes to the Chinese people with Anthropic’s claims of distillation? Easily: why not both? Chinese AI labs can be distilling from American AI labs and also be really great themselves at building this technology.

What I’m trying to say is this: it is unfair to dismiss Chinese talent, hard work, and achievement solely on the basis of Anthropic’s claims. Three-point-four million exchanges is enough to matter—and potentially enough for a strong, targeted post-training run—but it is not enough to conclude that Claude explains Kimi K3’s overall capabilities. And, at the same time, it’s also unfair to dismiss Anthropic’s worries about distillation as if it has never actually played a role in China catching up.

Two truths emerge here:

You don’t close the gap with the frontier by doing hacks.

No one playing at that level is a saint.

Now, if “how is Kimi K3 so good?” is the one-million-dollar question, then “what does it mean for the West’s AI efforts that a Chinese open model is so good?” is the one-trillion-dollar question—and quite literally so, given that the aggregate market size of the AI industry is around $1T.

### III. IS KIMI K3 THE DAWN OF AN AMERICAN AI CRISIS?

Yes. And now let's elaborate...

## Keep reading with a 7-day free trial

Subscribe to The Algorithmic Bridge to keep reading this post and get 7 days of free access to the full post archives.

### A subscription gets you:
