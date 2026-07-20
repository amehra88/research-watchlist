---
doc_type: substack_post
source: substack
publication: The Algorithmic Bridge
publication_url: https://www.thealgorithmicbridge.com/
source_email: <20260701194007.3.804b3802b43dc3d3@mg2.substack.com>
source_sender: Alberto Romero from The Algorithmic Bridge <thealgorithmicbridge@substack.com>
source_url: https://open.substack.com/pub/thealgorithmicbridge/p/fable-is-back-this-safeguard-has
source_date: '2026-07-01'
subscription_tier: free_plus_paid
tickers: []
themes:
- ai_regulation
- frontier_model_competition
- model_efficiency_evolution
ingestion_date: '2026-07-13'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Fable is Back: This Safeguard Has Some AI in It!

Thank you for being a free subscriber. You can [upgrade here](https://substack.com/redirect/13f58a03-db67-4505-a900-01e5c34d73e3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# [Fable is Back: This Safeguard Has Some AI in It!](https://substack.com/app-link/post?publication_id=883883&post_id=204501128&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNDUwMTEyOCwiaWF0IjoxNzgyOTM0OTA5LCJleHAiOjE3ODU1MjY5MDksImlzcyI6InB1Yi04ODM4ODMiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.RkT8oH9Rg2xuWJmC1LX53Las0LOW6LSZC4iHB1zypM0)

### Let's analyze Anthropic and the US government's comms

Hey, Alberto here! 👋 Each week, I publish long-form AI analysis covering culture, philosophy, and business. Paid subscribers get Monday how-to guides and Friday news commentary. If you’d like to become a paid subscriber, here’s a button for that:

Will keep you updated on the events surrounding Fable until the situation normalizes.

Today, July 1, Anthropic’s Fable 5 is back.

But there’s some fine print attached to the redeployment, and I want to comment on that. I will quote excerpts from [Anthropic’s blog post](https://substack.com/redirect/047a3e5d-efda-4052-b9b9-005f6f5c34ec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [Commerce Secretary Lutnick’s letter](https://substack.com/redirect/aa9b7a80-83a5-4019-b8ef-b35ecb32593d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). To see where the AI industry’s heading, we just need to read between the lines of what they say in public.

Here’s [Anthropic’s blog post](https://substack.com/redirect/047a3e5d-efda-4052-b9b9-005f6f5c34ec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

> Fable 5 will be available starting tomorrow, Wednesday, July 1, to users globally on the Claude Platform, Claude.ai, Claude Code, and Claude Cowork. For Pro, Max, Team, and select Enterprise plans,1 Fable 5 will be included for up to 50% of weekly usage limits through July 7, after which it will be available via [usage credits](https://substack.com/redirect/aa64c9fe-e67a-4071-ba50-91a2d2dbd8cd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

This is more or less what we had [before the export restriction](https://substack.com/redirect/0b6de909-0dba-44ac-862f-7f0227c9b45c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), except for two things: 1) you have one week of Fable under your paid subscription instead of two weeks (and then it moves to a pay-as-you-go credit system, that doesn’t change) and 2) only up to 50% of the tokens can go to Fable instead of 100%. (No Mythos either way, as expected.) I find it interesting that they chose the 50% limit. It’s bad optics in the sense that it’s not clean and it also feels unnecessary. It’s probably necessary though, or they wouldn’t do it—which can only mean that they don’t have the compute.

> The export control directive on June 12 came after the government became aware of a report in which Amazon researchers had found a method of bypassing Fable 5’s safeguards: prompting it so that it identified a number of software vulnerabilities. . . . Our testing confirmed that many less capable models—including Claude Opus 4.8, GPT-5.5, and Kimi K2.7—could identify the same vulnerabilities as Fable 5 did in the [Amazon] report.

This jailbreak that sparked the withdrawal of the model. Anthropic is restating what they had already told the government (the gov didn’t like this), prompting the export control restriction: the jailbreak is not an issue because it does not bear on Fable’s broader capabilities relative to other models. It is a known, lower-priority jailbreak that poses little actual danger and is found everywhere.

This reads like a defense but, together with the whole “the industry needs a consistent way to assess and fix potential ‘jailbreaks’ of AI models,” it’s also a jab at those players not targeted by the government (particularly open-source models).

> . . . there are some tasks that are unlikely to be dangerous but are nonetheless blocked by the safeguards out of an abundance of caution. . . .

Tighter safeguards mean lower capabilities and thus greater unreliability for the user. An “abundance of caution” is their way of saying the new Fable 5 will be more crippled than the previous version, which was already a downgrade from Mythos. Anthropic tends to err on the side of caution, but this was the government’s doing; take this as a sign of what’s coming with future models.

As stated, this is not a “that bad” (who doesn’t want that bad things don’t happen, right?) The problem comes with what “abundance” and “caution” mean here, about which we have no say whatsoever, nor apparently does Anthropic.

> Working closely with the government, we trained an improved safety classifier that targets and blocks the behavior described in the report. Users will be notified if a request to Fable 5 is blocked, and the request will instead be sent to Opus 4.8.

Ok, so no invisible re-routing at all, which is great. “Improved” here presumably means fewer false positives, but it can also mean less permission and thus less risk.

> The new classifier also comes at the cost of flagging benign requests more often during routine coding and debugging tasks. As with all our safeguards, we’ll continue to refine this to better distinguish genuine misuse from legitimate requests and reduce false positives. . . . This “safety margin” approach means that a request has to look very clearly safe to avoid triggering the classifier (see row A in the diagram below). Users experience the safety margin as a model refusing to respond to some reasonable, non-harmful requests. For Fable 5, we made this safety margin much larger than in any prior launch (row B), meaning that many more benign requests would be blocked.

Alright, there you go. This is the one clearly backward move. [Fable 5 was criticized initially](https://substack.com/redirect/0b6de909-0dba-44ac-862f-7f0227c9b45c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) due to an exaggerated sensitivity to standard prompts. If this new version will flag “benign requests more often” precisely for coding tasks (even if not all)—which is the main use case for Fable or any other frontier model—then I wonder whether the effective AI capability frontier is actually capped at Opus 4.8/GPT-5.5 moving forward (presumably, better models will have to fall back to the same level of capabilities).

So the question is: Can they train the classifier that separates dangerous tasks from non-dangerous ones in a way that allows users to conduct complex experiments at the frontier of intelligence? They will “continue to refine” it, but given the stakes and the sensitivity of AI models to different forms of jailbreak, I don’t think, under this regime, that we will ever see a “non-capped” model again.

“Very clearly safe” is more or less equivalent to “you can’t do shit.” (I will be excited to read testimonies by people working at the frontier and I hope to be wrong.)

> We understood that these kinds of false positives would be frustrating for users, but made this tradeoff in the interest of making the model’s other capabilities widely available.

In practice, the eventual compromise will keep the government happy and users scratching their heads because the opposite is untenable. Users provide money/data, which is important, and might be annoyed, but the government has the power to shut you down. AI companies and the US government will be increasingly interwoven to 1) prevent this kind of problem from repeating and 2) pave the way toward a full-scale Manhattan Project for AI. If anything, this will happen in the medium-term (will be absolutely undeniable by 2028), but again, this is the first step toward that and [the last step of the AI industry as we knew it](https://substack.com/redirect/7901f436-e0cc-47e4-8f83-aeeab3045684?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

> As we noted [when we launched Fable 5](https://substack.com/redirect/451b9025-040e-49f4-9451-8fe9031a7d4e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), it is probably impossible to make any AI model fully robust (that is, impervious) to jailbreaks. We expect that some jailbreaks will be found for our models, and that they will vary in severity . . .

They can’t allow a jailbreak to happen, so they will indeed err on the side of caution, as they do. To ensure a 99% jailbreak avoidance, they will never be able to escape overly conservative restrictions. The problem is that jailbreaks can’t be fully solved in code due to the infinite scope of language as the interface between human and AI—AI models are grown, not designed—and sometimes that’s a blessing and sometimes a curse. This is the latter.

It’s simply the case that we’re at a point in the AI trajectory that “frontier capabilities” and “abundance of caution” can hardly go hand-in-hand anymore. So, this looks like an effective redefinition of what “the frontier of AI capability” means for the rest of us.

Finally, the explicit role of the government moving forward.

> . . . Anthropic has worked closely with the US government . . . Our engagement spanned the Office of the National Cyber Director, the Office of Science and Technology Policy, the Department of the Treasury, the Department of Commerce (including CAISI), and relevant national security agencies.We are committed to continuing that work, building on nearly two years of pre-existing collaborations with US government partners on pre-deployment testing and evaluation. The commitments below reflect both that pre-existing work and our new proposals to scale up our government collaboration as the above framework is finalized:Pre‑release government access and evaluation. For models that materially advance the capability frontier in areas relevant to national security, we will provide designated government partners with expanded early access to both the models and the safeguards that accompany them. . . .Dedicated resources for joint research. We are substantially scaling up joint work with government partners on AI security. We will stand up dedicated Anthropic teams to work on shared government priorities, provide a significant compute allocation to support government testing and research . . .

This is basically the US government at the helm of the world’s top AI companies. (It will apply to OpenAI and Google all the same.) They will have preferential access, veto power beyond just cybersecurity, and dedicated resources (talent and compute).

To me, it’s clear who’s in charge.

Ok, so now moving onto [Lutnick’s letter](https://substack.com/redirect/aa9b7a80-83a5-4019-b8ef-b35ecb32593d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

> . . . Anthropic has agreed to proactively detect and address security risks associated with the models; to work diligently with the U.S. government on protocols and standards and releases for Mythos, Fable, and future models. . . .

This is the same thing Anthropic said except for one important detail: “future models.” They are crystal clear that this will be the standard release procedure moving forward. Essentially, the government is now a gatekeeper of some undisclosed kind with some undisclosed power between AI companies and us, users.

> Commerce reserves the right to reevaluate the decisions made in this letter and the necessity of reimposing a license requirement, should circumstances change or should Anthropic fail to adhere to its commitments.

If “circumstances change”—essentially a description of AI as a technology—the government can “reevaluate the decisions.” What are those circumstances? We don’t know, but given that the premise of the AI industry is that emergent capabilities can be achieved by scaling compute and data, it’s fair to assume that anything that happens at any point is subject to be deemed a change in circumstance.

There’s nothing super weird about the state being in charge (state > industry, at least for now), but realize where the trajectory points to: better models will display better capabilities, which will entail more safeguards for us and tighter control of the industry by the state.

“This is the worst AI will ever be.”

Yes, and this is also the freest AI will ever be.

Let me summarize what we just read.

A problem reproducible in lesser models—Anthropic shakes off responsibility—has cascaded into a full-blown protocol: stricter classifier to re-route prompts, undisclosed government audit of safeguards, dedicated compute and staff handed to the state, a signed commitment about every model to come, and a clear asymmetry between them: whereas Anthropic concedes everything, the government retains the power to tighten the restrictions and redefine the industry at some point by some reason.

You don’t build all of this over a minor bug (there could have been confusion at first about jailbreak types and whatever, but at this point, the government knows exactly what it’s doing). So it was never about the bug.

If the jailbreak is really the cause, why didn’t this happen at any point during the last few years, while the capability frontier was not as scary but this kind of issue was already well-known? Why did it happen now? Because only now can it be sold to us as an acceptable compromise: on the one hand, “Even the government says Mythos is scary”; and on the other, “Go have fun with the restored capabilities.” And because Anthropic has been the underdog for years and only in 2026 did they take the lead.

How can we say no to this? Everything Anthropic presents as a safety choice—the wider margin, the coding requests that now bounce down to Opus 4.8, the compromise for users—is also lending permanent control to the government.

Anthropic asked for this. They say the arrangement has to be durable; an orderly and lasting process for government involvement in releases that includes them and everyone else. Anthropic engineered its own subordination and would do it again, because, to them, a chained frontier beats an open race.
