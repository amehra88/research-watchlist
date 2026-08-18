---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260817200230.3.c31b2c459c9a7362@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/hidden-figures-in-ai-big-tech-stripe
source_date: '2026-08-17'
subscription_tier: free
tickers:
- AAPL
- MU
- SPCX
themes:
- ai_infrastructure_capex
- ai_regulation
- agentic_commerce
- china_export_controls
- hyperscaler_capex_buildout
- foundation_model_economics
- agent_framework_landscape
- handset_competition
ingestion_date: '2026-08-18'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [‘Hidden Figures’ in AI. Big Tech, Stripe & Anthropic. ARD #142](https://substack.com/app-link/post?publication_id=684161&post_id=211585222&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMTU4NTIyMiwiaWF0IjoxNzg2OTk3MTI3LCJleHAiOjE3ODk1ODkxMjcsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.1fYfv_TILRqMqw8_gV248-QD2flRmNXcCW7BzHIZ_60)

### ...$3 trillion of AI capex off the books, watermarks inside Claude’s math, & Stripe’s $7bn OpenRouter buy.

‘Hidden Figures.’ One of my favorite movies, based on a great book: the story of the human, female, african-american ‘computers’ at NASA that made Apollo & more possible. The human mathematicians history almost left out, whose numbers actually got the rockets up and about. Note the double meaning, because it is today’s whole point: the hidden figures are the numbers, and they are also the people behind them. Not to mention the human ‘figuring’ that occurs around the computer generated math as well.

Today’s ARD is about the hidden figures in AI, in this [AI Tech Wave](https://substack.com/redirect/ef869543-b270-4d15-b2d8-8a9542b466a2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): three trillion dollars of AI spending that is not on Big Tech Co balance sheet, an Anthropic regulation mandated, AI watermark that hides inside the way Claude picks its words via matrix math, and a seven billion dollar acquisition Stripe where the price is the least interesting number. With my takes.

## (1) Big Tech’s ‘Off-Book’ AI Capex: $3 Trillion in the Footnotes

Investors are laser-focused on the headline AI capex numbers big tech publishes every quarter. Roughly $600 billion over the past reported year, and those numbers are enormous. But the ‘hidden figures’ are bigger. The Journal went through the footnotes of the securities filings and found some $3 trillion of off-balance-sheet commitments across nine top tech companies, mostly AI. That is about five times the published capex, roughly triple what these companies owe on all their leases and long-term borrowings combined, and it is growing faster than the capex line itself. ‘Circular’ financing or not, these obligations live in legal footnotes and financing partnerships with the biggest financial players in the world. I wrote the roadmap for this in my pieces on Meta’s mega financing deals and on AI data centers’ global financing needs. For now, the off-book numbers are going to lead the published numbers. Watch the footnotes across financial partners, not just the press releases by the mainstay companies.

Sources:

- [WSJ: “Why Big Tech’s AI Spending is $3 Trillion Higher than it Seems”](https://substack.com/redirect/04a5608d-dd56-4300-9e50-e2411d44d6c6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Stratechery: “The Capex Train keeps Rolling”](https://substack.com/redirect/f7f98410-a31e-4a2c-9a03-44dc239012d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #891: Meta’s mega financing deals show roadmap for peers](https://substack.com/redirect/9390d381-a9fa-424c-bb3f-cde214fe9616?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #777: AI Data Centers growing globally in financing needs](https://substack.com/redirect/4d6b486e-2e20-44e0-b06d-97dcfb10527d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) Anthropic’s AI Watermarks: the Hidden Math

Most folks hear ‘watermarking’ and think of a visible stamp that flags what is AI-made. That is not how this works at all in differentiating AI work from human work. Anthropic’s text watermark reaches into the fundamental way the model does its probabilistic math. When Claude picks its next word from a shortlist of likely candidates, a hidden key quietly tilts the dice: candidate words get dealt ‘green’ and ‘red’ by the key, fresh from the few words just before, not from any fixed list, and the finished text carries a statistical lean only the key-holder can detect. ‘Hidden Figures’ in a numberical sense indeed.

Google has quietly done a version of this with Gemini since 2024. Anthropic says there is no practical quality impact, nothing added to the text, and that this is EU AI Act compliance every major provider has signed up for. Maybe so. But those hidden-figure effects inside the sampling math are exactly where the consequences will live, and regulators do not yet grasp the downstream implications. Tech Guru and writer John Gruber calls it a ‘perversion of writing.’ We may be throwing out the AI baby with the bathwater in this early rush to separate AI content from human content. To separate the so-called ‘AI Slop’ from ‘human’ work. Not recognizing that one person’s AI Slop is another’s AI Gold. It is like highlighting every word autocorrect ever touched, in every document on the internet. On the assumption that most of it ‘bad’ because it was suggested by a machine. Overlooking that the statistics that drove the suggestions were using aggregated human behaviors across countless keystrokes. The ‘Hidden Figures’ here are just our cumulative reflections in the AI mirrors of human behaviors.

Sources:

- [Anthropic: “How Claude’s text watermarking works”](https://substack.com/redirect/0ffc71aa-daca-4b49-bbdd-2bed0c6cafd4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [declaude.org: “How AI text watermarking works: a visual guide”](https://substack.com/redirect/a08ce128-de28-4fef-bb54-337784104533?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Daring Fireball: “Anthropic’s ‘Watermark’ Text Adulteration in Claude is a Perversion of Writing”](https://substack.com/redirect/1582001c-8446-43db-b2f9-b2b75756a22a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1082: Limiting AI with human intelligence in the mirror](https://substack.com/redirect/634b07ca-0539-41db-8863-8e2fed0c4178?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) Stripe Buys OpenRouter, SpaceXAI Closes Cursor: the Hidden Strategy

Two acquisitions, and in both cases the sticker price is the least interesting number. Stripe finalized its deal for OpenRouter at over $7 billion, the 70-times-revenue math we crunched on ARD #129. OpenRouter routes developers across hundreds of AI models, matching workloads to the most efficient and affordable option.

Bolt that to Stripe’s payment rails and you have the metering and monetization layer for the machine-to-machine agent economy we have been writing about all week.

Ben Thompson of Stratechery frames it as an opportumity for Stripe to ‘flip’ OpenRouter’s current business model to aggregate AI. It’s good ‘Hidden Figuring’ of a strategy that’s work well for so many key big tech acquisitions. Like Google buying YouTube, and flipping its business model to allow for unlimited video uploads to this day. Charging on the other side to advertisers, not on the demand side. Same with Google Maps post the Keyhole satellite data acquisition decades ago. All ‘flipped’ models.

And Elon’s SpaceXAI just completed its $60 billion Cursor acquisition. The pattern to remember: the right acquirer changes what the acquired company can become. YouTube with Google became something YouTube alone never could. The hidden strategic ‘figuring’ spits out implications that are worth far more than the acquisition math.

Sources:

- [Bloomberg: “Stripe Clinches over $7 Billion deal to buy AI firm OpenRouter”](https://substack.com/redirect/5fd07ef6-b953-45b3-87fc-64c07f5b9bb4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Stratechery: “Stripe acquiring OpenRouter, Aggregating AI? Flipping the Business Model”](https://substack.com/redirect/a78de7df-cd9a-42d2-8854-5339e80042cb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: “SpaceXAI completes $60 billion acquisition of AI Startup Cursor”](https://substack.com/redirect/652526b7-2374-4884-adb3-cb8496266c97?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #129: Stripe may pay 70x revenue for OpenRouter](https://substack.com/redirect/c3e8ea36-d510-4389-b820-98cb2c5550d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #62: Elon’s $60 billion call on Cursor](https://substack.com/redirect/0abe67fe-186a-4184-880b-2717c70cac77?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1066: SpaceXAI IPO outlines Elon’s boundless AI ambitions](https://substack.com/redirect/c648ec8d-81a6-4d44-81b5-f9c60bfb2c17?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: all three events today are the same lesson wearing different clothes. The published number is the start of the analysis, not the end of it. Three trillion dollars of commitments living in footnotes. A watermark living inside the word-choice math. Acquisition prices that hide what the asset becomes in the right hands. The ‘hidden figures,’ both the numbers and the people behind them, are what make the major impact down the road in this [AI Tech Wave](https://substack.com/redirect/ef869543-b270-4d15-b2d8-8a9542b466a2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). That was true for the ‘Hidden Figures’ at NASA in 1962. It is true in AI in 2026.

## Gadget AI: US Leans on Apple over Chinese Memory Chips

Commerce Secretary Lutnick says out loud that the administration does not want Apple buying memory chips from China, where Apple has been testing CXMT and Yangtze Memory parts for devices sold in China. Not the result Apple wanted in the middle of ‘RAMageddon’ memory pricing. My read: this looks tactical ahead of the second Trump-Xi White House meeting on September 24.

The US side knows its memory options are three names: SK hynix, Samsung, and Micron. Micron is lobbying for more restrictions; Apple and its peers will lobby the other way. The ‘hidden figures’ of those costs will be presented to the policy makers in black and white.

This is a negotiating chip, in both senses. And the saving grace for phone buyers: over half of US consumer smartphones move on carrier-financed installment deals with trade-ins, before counting the ‘cash’ purchases that ride on credit cards, which spreads the sticker shock over monthly payments.

Sources:

- [WSJ exclusive: “US Urges Apple Not to Buy Chinese Memory Chips”](https://substack.com/redirect/e1c28935-21b8-453b-9652-eee9ef66cfd7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1145: ‘RAMageddon’ really here to stay](https://substack.com/redirect/72deffda-aa1d-467b-8513-79f7daa009af?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1128: US hamstrung on memory chip supply via China](https://substack.com/redirect/76060d20-f77b-422c-8cd1-c1325df26880?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1113: Apple Intelligence & Siri AI with ‘Google & Nvidia’ inside](https://substack.com/redirect/4c0a5dd4-3840-478f-91d6-286fa0d312f2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #130: the Apple leasing and Klarna installment angle](https://substack.com/redirect/80435d11-138f-4bfc-b629-707647c52c41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Today’s companion AI-RTZ, #1181, is on [Anthropic’s mega-IPO math banking on 2028 forecasts](https://substack.com/redirect/5bf21bce-543b-4474-aec4-4fd333603498?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Tomorrow it is ARD 143 and AI-RTZ #1182.

## Full Source Reading

### Big Tech off-book AI capex

- [WSJ: “Why Big Tech’s AI Spending is $3 Trillion Higher than it Seems”](https://substack.com/redirect/04a5608d-dd56-4300-9e50-e2411d44d6c6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Stratechery: “The Capex Train keeps Rolling”](https://substack.com/redirect/f7f98410-a31e-4a2c-9a03-44dc239012d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #891: Meta’s mega financing deals](https://substack.com/redirect/9390d381-a9fa-424c-bb3f-cde214fe9616?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #777: AI data centers’ global financing needs](https://substack.com/redirect/4d6b486e-2e20-44e0-b06d-97dcfb10527d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Anthropic AI watermarks

- [Anthropic: “How Claude’s text watermarking works”](https://substack.com/redirect/0ffc71aa-daca-4b49-bbdd-2bed0c6cafd4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [declaude.org: watermarking visual guide](https://substack.com/redirect/a08ce128-de28-4fef-bb54-337784104533?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Daring Fireball on the watermark](https://substack.com/redirect/1582001c-8446-43db-b2f9-b2b75756a22a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1082: Limiting AI with human intelligence in the mirror](https://substack.com/redirect/634b07ca-0539-41db-8863-8e2fed0c4178?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Stripe/OpenRouter and SpaceXAI/Cursor

- [Bloomberg: Stripe’s $7B+ OpenRouter deal](https://substack.com/redirect/5fd07ef6-b953-45b3-87fc-64c07f5b9bb4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Stratechery: Aggregating AI, flipping the business model](https://substack.com/redirect/a78de7df-cd9a-42d2-8854-5339e80042cb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bloomberg: SpaceXAI completes $60B Cursor deal](https://substack.com/redirect/652526b7-2374-4884-adb3-cb8496266c97?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #129: the 70x revenue discussion](https://substack.com/redirect/c3e8ea36-d510-4389-b820-98cb2c5550d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #62: Elon’s Cursor call](https://substack.com/redirect/0abe67fe-186a-4184-880b-2717c70cac77?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1066: SpaceXAI IPO ambitions](https://substack.com/redirect/c648ec8d-81a6-4d44-81b5-f9c60bfb2c17?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: Apple and Chinese memory

- [WSJ exclusive: US urges Apple off Chinese memory chips](https://substack.com/redirect/e1c28935-21b8-453b-9652-eee9ef66cfd7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1145: RAMageddon here to stay](https://substack.com/redirect/72deffda-aa1d-467b-8513-79f7daa009af?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1128: US hamstrung on memory supply](https://substack.com/redirect/76060d20-f77b-422c-8cd1-c1325df26880?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1113: Apple Intelligence inside](https://substack.com/redirect/4c0a5dd4-3840-478f-91d6-286fa0d312f2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #130: Apple leasing and Klarna](https://substack.com/redirect/80435d11-138f-4bfc-b629-707647c52c41?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### AI Watermarks: You Can’t Unmix the Stew

### RAMageddon’s Saving Grace: Carrier Financing

### US Tells Apple: No Chinese Memory Chips

### AI Isn’t a Race. It’s a Decades-Long Evolution

An impact of the [AI Tech Wave](https://substack.com/redirect/ef869543-b270-4d15-b2d8-8a9542b466a2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) worth tracking. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
