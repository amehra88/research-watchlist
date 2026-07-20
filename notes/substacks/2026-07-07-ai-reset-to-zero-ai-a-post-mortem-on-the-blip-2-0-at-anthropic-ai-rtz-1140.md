---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260707050205.3.c9c3c49e2376fcfc@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-a-post-mortem-on-the-blip-20-at
source_date: '2026-07-07'
subscription_tier: free
tickers: []
themes:
- ai_regulation
- frontier_model_competition
- china_us_tensions
ingestion_date: '2026-07-13'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: A post-mortem on 'The Blip 2.0' at Anthropic. AI-RTZ #1140](https://substack.com/app-link/post?publication_id=684161&post_id=205574076&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNTU3NDA3NiwiaWF0IjoxNzgzNDAwODg0LCJleHAiOjE3ODU5OTI4ODQsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.dPMz7AaMhURh3aX1lTv_TZYjx44teI0ahwVayfpKwsY)

### ...paused for now by the US Government, but not yet 'over'.

It’s now officially three weeks since the lifting of [Anthropic’s June 12 ‘Blip 2.0’](https://substack.com/redirect/adf638e9-8132-44d9-bc72-c9487130c2d3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)last week by the US Government. Named as such by me after ‘[the Blip 1.0](https://substack.com/redirect/ab61fa5e-1736-495a-a10f-2432a1ed1563?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)’ three years ago, when OpenAI’s non-profit board [fired and re-hired](https://substack.com/redirect/23526668-053c-4b3a-b02c-582dcfc4baf2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)founder/CEO [Sam Altman](https://substack.com/redirect/3a08c713-c563-4d76-9956-99f6ddfcaa29?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) over a globally stressful [weekend.](https://substack.com/redirect/0c80ada9-126e-4334-9d86-3845412f5753?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Both times an interruption in the [AI Tech Wave](https://substack.com/redirect/f5eeb94f-eec9-4db0-bfbb-10e6c121b971?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that was startlingly searing. With lots of unintended consequences still being felt today from the Blip 1.0.

And as I discussed last week, this second one is not yet completely behind us. Especially with the [US government still gating both Anthropic and OpenAI](https://substack.com/redirect/37cefb68-e044-4858-9fc4-f7d317c03e95?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)on its latest next-generations of frontier ai models. Specifically Mythos from Anthropic and GPT 5.6 from OpenAI.

So it’s helpful to see what the latest post-mortem analysis on how it all went down reveals.

Axios goes through it all in “[How the world’s top AI models were revived”](https://substack.com/redirect/5b7cbcf5-c455-4f40-b806-9ea1287cc151?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

> “The fight that scrubbed the world’s most powerful AI models from the internet featured personality clashes, industry confusion and international backlash.” [](https://substack.com/redirect/4604b651-deaf-4a6a-a8f5-998d6d4e4b69?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)“Why it matters: Anthropic’s models are back online, but the impact of its 20-day showdown with the Trump administration will be long lasting.”“Behind the scenes: It began when Amazon, Anthropic’s partner and investor, sounded an alarm that was later disputed by cybersecurity experts.”“It warned about a “jailbreaking” issue it found with the AI lab’s latest models, Mythos and Fable — meaning a technical flaw that could have caused a failure of their guardrails.”“Amazon flagged its concerns to the administration, [triggering sweeping export controls](https://substack.com/redirect/7f7d0d59-4bc3-4de6-9bc0-68b8183d951d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). A U.S. official said the government conducted its own tests once it became apparent that the issue needed to be addressed.”“Cybersecurity experts, however, [later wrote](https://substack.com/redirect/5c4275ed-36d2-4048-afc6-f43ef923a470?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in an open letter to the administration that other leading AI models have the same issue Amazon warned about with Anthropic.”

Then the Friday evening events that set if all off with a call from Lutnick:

> “On June 12, Commerce Secretary Howard Lutnick, at the direction of President Trump, called Anthropic CEO Dario Amodei.”“Lutnick made clear to Amodei the issue needed to be resolved fast and alerted the CEO that the company would be receiving a letter imposing sweeping export controls, the U.S. official said.”“Amodei called Lutnick back that night after receiving the letter, realizing it effectively meant the models would have to be taken offline — to which Lutnick responded that was indeed the goal.”

So clarity at last at that point on the near-term objective. Regardless of broader consequences for the [US ‘AI Race’ vs China.](https://substack.com/redirect/becbfd0f-5154-47d1-b7e9-ca5b39025905?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “That decision led to a three-week, multi-agency crash course in AI safety.”“Anthropic [deployed engineers](https://substack.com/redirect/388b00b7-da5e-4da9-88ba-04aa62ffdcbd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to Washington D.C. According to a U.S. official, the company wanted to prove everything was already resolved and further changes were being fine tuned.”“But the federal Center for AI Standards and Innovation and the National Security Agency said those changes weren’t good enough, prompting further fixes, according to the U.S. official.”“Gradually, various agency heads approved of the changes, and on July 1 the models were released, the official said.”

Gears of the Government hard at work indeed.

> “Out of all of the administration officials Amazon’s Andy Jassy could have called, it was Treasury Secretary Scott Bessent who first heard about the jailbreaking issue found in the company report, according to a separate source familiar.”“Bessent was early to sound the alarm on Mythos, work with White House chief of staff Susie Wiles to [reengage the embattled company](https://substack.com/redirect/c60aea79-73a1-4856-983d-f2af47411d54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and help get a [cybersecurity executive order](https://substack.com/redirect/028c06b1-515d-45c8-b804-84ab00302a81?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) across the finish line.”“While technical discussions to address the jailbreaking issue took place in D.C., it was Bessent who stood next to Trump during the G7, where allies called for global cooperation on safety standards.”

Nature abhores a vacuum as they say. And the departure of ‘[AI and Crypto Czar’ David Sacks](https://substack.com/redirect/8adcbbec-bb7c-4275-b13a-1a78e70937dd?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in recent days, left Secretary Lutnick at the AI helm, steering the US ship.

> “At the center of the showdown was [Lutnick](https://substack.com/redirect/53e3aa2b-fc14-40aa-bd59-5469ad2ddd7c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), who also flanked Trump at the G7 meeting while his department’s teams led technical discussions.”“National cyber director Sean Cairncross, the White House Office of Science and Technology Policy, Treasury Department chief information officer Sam Corcos and the NSA also all participated in technical discussions, according to various sources.”“Washington mobilized faster to hold scores of meetings and pulled in far more agencies than one would expect for a single technical issue, one source said.”

Then it all guilt from there, continuing over to the G7 meeting in Europe, with Anthropic founder/CEO Dario Amodei in attendance. And [meeting briefly with President Trump.](https://substack.com/redirect/9903bb09-6ab5-45b1-86e6-a034b1513383?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

> “The tension spiraled amid [personality clashes](https://substack.com/redirect/f6603605-689f-484f-ab27-4d88def3bda2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and poor communication.”“Anthropic eventually understood that in order to be successful, it needed to be on the same side as the government, the U.S. official said.”“As discussions turned more technical, Anthropic policy chief Sarah Heck and co-founder Tom Brown got more involved. Brown also had multiple conversations with Lutnick and Cairncross the weekend of June 12.”“There was never a moment when Dario stepped offstage and someone else replaced him, one source said, adding that Brown’s technical expertise allowed him to sit in a room with government specialists and go line by line through how models behave under stress.”

There are still a lot of details to be worked out across the board. With the latest US AI frontier models by either company, still [out of reach](https://substack.com/redirect/3094261b-293e-4725-b665-456917418264?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for most.

> “Between the lines: It remains uncertain when and how Anthropic’s models will be released to ally countries around the world — which proponents say is key to beating China — or how other labs from OpenAI to Google will release their latest models.”“OpenAI, whose latest model GPT-5.6 is on hold, did not have visibility into discussions between Anthropic and the White House and is engaged in daily technical discussions on the release of its own model, a source said.”“The bottom line: There’s a lot of work left to be done on a framework for approving future models with a clear inclusive process that has transparency standards and timelines, sources familiar said.”

So after all, much still remains unclear, and to be resolved. WIth the US government firmly steering the US AI ship in multiple directions. At various speeds.

That’s where we are at the moment this [AI Tech Wave](https://substack.com/redirect/f5eeb94f-eec9-4db0-bfbb-10e6c121b971?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), post the seeming pause in the ‘[Blip 2.0’](https://substack.com/redirect/37cefb68-e044-4858-9fc4-f7d317c03e95?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for [joining us here](https://substack.com/redirect/21c44504-def7-4358-807a-056600caeea1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))
