---
doc_type: substack_post
source: substack
publication: Nate's Substack
publication_url: https://natesnewsletter.substack.com/
source_email: <20260803130113.3.daae12620860f132@mg2.substack.com>
source_sender: Nate from Nate’s Substack <natesnewsletter@substack.com>
source_url: https://open.substack.com/pub/natesnewsletter/p/ai-bet-leverage-timing
source_date: '2026-08-03'
subscription_tier: free_plus_paid
tickers:
- AAPL
- 000660.KS
themes:
- ai_infrastructure_capex
- hbm_competitive_landscape
- inference_compute_economics
- silicon_architecture_competition
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Your AI bet can be right and still run out of money. Grab the two-clock prompt: what has to be true, how long it r…

Thanks for supporting Nate’s Newsletter! This post is free and clear for all subscribers, just like the sky (but not in Seattle—it’s always cloudy here).

# [Your AI bet can be right and still run out of money. Grab the two-clock prompt: what has to be true, how long it really takes, who controls your runway, what pays today.](https://substack.com/app-link/post?publication_id=1373231&post_id=209549403&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwOTU0OTQwMywiaWF0IjoxNzg1NzY2MjgzLCJleHAiOjE3ODgzNTgyODMsImlzcyI6InB1Yi0xMzczMjMxIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.8LdRF1FEp47fsbGfNCD317Ud96jVe4nVyFIb4ucb3vs)

### Aschenbrenner read AI right and still had to sell. Apple has looked slow for two years and it doesn't matter. The forecast was never the problem.

On July 30, one of the most successful AI investors alive sold his stock portfolio to Ken Griffin because his lenders ran out of patience.

[The Wall Street Journal](https://substack.com/redirect/87ebd538-10cd-4828-a0cb-802234d8a671?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) reported that Situational Awareness, the AI-focused hedge fund founded by former OpenAI researcher Leopold Aschenbrenner, sold the bulk of its public-stock portfolio to Citadel after steep losses. [Reuters](https://substack.com/redirect/70968fac-ce9e-4973-a3fe-32280e30825c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) described the purchase as most of the stock holdings. [Axios](https://substack.com/redirect/21148765-d8c1-414c-937f-43bf27f82f59?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) reported that the fund sold all of its public equities.

The accounts differ on the exact scope, but they agree on the important part: a concentrated, leveraged AI portfolio came under enough lender pressure that a large block of public stocks moved to Citadel. My interpretation is that the exposure moved to a buyer with more control over timing.

The Journal reported that Situational Awareness retained private-company positions, including Anthropic. The transaction was therefore a liquidity-driven sale from one part of the portfolio, not a neat verdict on every part of Aschenbrenner’s AI thesis.

The internet immediately supplied a more cinematic version. A Citadel Securities strategist argued for a surprise rate increase, AI stocks sold off, and Citadel’s investment business then bought the portfolio. Posts began treating the sequence as proof of coordination, a deliberately engineered collapse, a bargain purchase, and billions of dollars in instant profit.

The public evidence does not establish any of that.

Citadel and Citadel Securities describe themselves as [separate and distinct firms](https://substack.com/redirect/a5242bf1-1fc0-4e01-9255-b83577584ee6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). [Bloomberg reported the rate argument](https://substack.com/redirect/d8efa979-1f86-4c2e-9b64-bea4ef998bcc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on July 27. On July 29, [the Fed held its target range steady](https://substack.com/redirect/85b24daa-207d-4d13-937b-ffd589ed65d1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) at 3.5 to 3.75 percent, with three of twelve voting members preferring a quarter-point increase. The portfolio transaction followed, but chronology is not proof of coordination or profit. The deal terms are private. No regulator has commented publicly on the sequence, in either direction.

I’m not interested in laundering an online theory into a fact because it makes the story more fun. The confirmed facts support a harder lesson: Aschenbrenner had a powerful view of the future, but the structure around that view shortened how long he could wait for it.

Apple has almost the opposite problem. It has time, distribution, cash generation, and increasingly capable hardware. What it hasn’t proved is that it’ll turn those advantages into an AI product customers want.

Here’s what’s inside:

- The two clocks. One asks when the capability arrives. The other asks whether you’re still solvent when it does.

- What actually happened. The verified sequence, and the numbers that fall apart against the filings.

- Apple’s cash engine is the strategy — $117 billion generated in nine months, and a chip architecture that puts other people’s models to work on Apple hardware.

- Five questions to run against any AI bet you’re making or funding.

- What this means for what you’re building. Answer six questions and the prompt scores your own runway against your own timeline.

Every serious AI bet runs on two clocks. Let’s start with what Aschenbrenner actually believed.

## The thesis was more than a stock list

Aschenbrenner became famous for [Situational Awareness: The Decade Ahead](https://substack.com/redirect/a8bf9d26-1dac-4afb-9a5a-4ced7ce7e34c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a long 2024 essay that argued the scale-up in compute, power, data centers, and model capability made extraordinary AI progress visible in advance.

He then built an investment firm around that view.

The basic logic is understandable even if you disagree with his timelines. Frontier AI doesn’t arrive as software floating in the air. Training and serving powerful models requires chips, memory, power, networking, cooling, construction, and enormous amounts of capital. If you believe the labs will keep scaling, you can work backward through the physical supply chain and ask which companies benefit.

That thesis attracted enormous capital. The fund [raised a reported $225 million](https://substack.com/redirect/ce488737-2cc1-4859-9e15-08c94694bb80?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in July 2024 from the Collisons, Nat Friedman, and Daniel Gross. By June 8 it had [passed $20 billion in assets](https://substack.com/redirect/5f5cb3da-b2fe-41a5-a11e-6985a1d66516?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and counted Jane Street among its investors — a firm that mostly trades its own money, and rarely hands anyone else a mandate. CNBC reported [the peak at about $45 billion in assets](https://substack.com/redirect/ce488737-2cc1-4859-9e15-08c94694bb80?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) at the start of July. By July 30, Bloomberg [had it at roughly $10 billion](https://substack.com/redirect/6dc8371b-9853-4d3b-b508-5657a30f2664?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Worth pausing on the word assets. CNBC cited one source and never said net. The fund’s own [Form ADV](https://substack.com/redirect/e6668711-22da-4fbe-958f-c66b3a821a17?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) lists $9.3 billion in regulatory assets under management, its [first-quarter 13F](https://substack.com/redirect/e1d5c818-5a88-461e-8514-45b2c1947214?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) shows $3.86 billion in ordinary shares against $9.8 billion in options, and [SpotGamma](https://substack.com/redirect/2463057c-b712-440a-ab6b-f64359c885dc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) puts mid-2026 assets at $20 to $24 billion, with gross leverage on top of that. The collapse is real. The numbers on either end of it are measuring different things, and nobody outside the fund can tell you which one the $45 billion was.

The positions were leveraged. That’s what turned a few bad weeks into a deadline.

Leverage means borrowing to control more exposure than your own capital supports. It magnifies gains on the way up and hands someone else the timing on the way down.

An unleveraged investor who still believes the thesis can wait through a drawdown. A leveraged investor may have to raise capital, reduce positions, or sell while still believing the long-term argument. The market only has to move far enough, fast enough, to make the current financing intolerable. Proving the AI buildout is over is a much higher bar, and nobody has to clear it.

The selloff had a name. SK Hynix [listed in the US on July 10](https://substack.com/redirect/5e7e7173-06d8-49ac-9e8a-0f96cbe8e68b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and raised $26.5 billion, the largest first-time US share sale ever by a foreign company, past Alibaba’s $25 billion in 2014. The following Monday [the shares fell 15.4 percent in Seoul](https://substack.com/redirect/30e341bf-b828-416c-9994-3864cbed426b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), the sharpest one-day drop in the company’s history, and dragged the KOSPI down 9 percent with them. On July 29 it [reported record profit that still missed forecasts](https://substack.com/redirect/d2711708-2293-40e7-8f60-dbbdd6bbe2c4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The stock fell as much as 19 percent intraday before closing down 9.6 percent. SK Hynix was, [according to Fortune](https://substack.com/redirect/5ec70761-cc70-4467-8873-23fbd5550add?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), one of the fund’s largest holdings.

CNBC [reported leverage of up to 400 percent](https://substack.com/redirect/ce488737-2cc1-4859-9e15-08c94694bb80?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). I’m not going to hang the argument on that number, because it is reported rather than filed, and no public document establishes a clean ratio. What is solid is that the book carried substantial borrowed exposure. A quarterly 13F filing cannot solve that problem. It shows certain U.S.-listed long positions and options at a past date; it does not show the complete live portfolio, short positions, financing terms, or net exposure.

The safe conclusion is narrower and more useful: Situational Awareness had a large, leveraged public-stock book, suffered steep losses during the selloff, sought fresh capital, and sold much of or all of that public-equity exposure to Citadel.

The sequence shows something narrower than a failed thesis. Being directionally right about a long transition is a different skill from financing the path across it.

## The two clocks inside an AI bet

The first clock is technical. It asks when a model, chip, product, or cost curve becomes good enough. An agent may need to work for hours without losing the task. A useful model may need to run on hardware the customer already owns. For another product, the threshold could be inference cheap enough for thousands of calls, or a new interface reliable enough to replace an old habit. Most AI forecasts live on this clock because they estimate capability and adoption.

The second clock is financial. It asks whether the owner can keep funding the attempt until the technical change arrives. Debt may mature before then, a broker may demand collateral, or cash may leave faster than investors will replace it. The current product can fund the wait, or the whole thesis can depend on another financing round. What happens if the forecast is right two years later than expected?

Neither clock cares that you’re sincere.

A lab can sign long-term commitments for chips, power, and data centers because the technical plan requires them, then discover that the revenue curve moved more slowly. A builder can be early enough to be correct and too early to stay alive.

The financial clock is often hidden when things are going well. Borrowed money feels like confidence. A long contract feels like securing scarce supply. A high burn rate feels like speed. The real test appears when the path changes and someone else has the right to demand an answer.

Citadel won this by being the buyer when Situational Awareness needed liquidity. Forecasting had nothing to do with it.

A sophisticated buyer can price the block, hedge parts of the exposure, and require terms that compensate it for moving quickly. We don’t know the private terms, so I’m not going to claim that Citadel bought at a particular discount or made a specific amount. We know that one side needed to act and the other side had the capacity to choose.

That control over timing is the bridge to Apple.

## How Apple’s AI strategy buys time

Apple is easy to criticize in AI because the visible comparison isn’t flattering. OpenAI, Anthropic, and Google built the model brands. Their assistants set expectations and their releases define much of the conversation. Apple owns an enormous consumer platform, yet its AI story has often looked slower and less coherent than the position should allow.

Cash can’t repair a bad product instinct. Distribution can’t make customers love an assistant that disappoints them. A long runway becomes a liability if management uses it to postpone the hard decisions.

That’s the strongest case against Apple, and I take it seriously.

But I think the conventional comparison still misses what Apple owns.

I’ve made the longer case for Apple’s hardware and local-inference position in [my briefing on the AI cost curve](https://substack.com/redirect/7e0e535c-013f-4933-a019-5242eefb5cce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [my guide to owning personal AI compute](https://substack.com/redirect/06e74517-f120-45df-8dda-d8611d4ee8cc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [a video on what Apple could do with local compute](https://substack.com/redirect/b79e3890-de54-4dc9-8161-f2e63bd1bea0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). I’m returning to it here for a narrower reason. Apple’s structure gives the company multiple attempts while the current business funds the wait.

Apple sells the hardware on which a growing amount of AI can run. It designs the silicon, controls the operating system, has an installed base measured in billions of active devices, and earns money from products and services that customers already buy for reasons beyond generative AI.

The financial shape is very different from a concentrated leveraged trade.

On July 30, Apple reported $109.4 billion in quarterly revenue, up 16 percent from the prior year. Through the first nine months of its fiscal year, it generated roughly $117 billion in operating cash. At quarter end it held about $146.5 billion in cash and marketable securities — though that isn’t net cash, since Apple also carries roughly $84.3 billion in commercial paper and term debt. ([Apple Q3 results](https://substack.com/redirect/aa3fc3e0-1787-4370-bc72-5b45c6a27b51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [consolidated financial statements](https://substack.com/redirect/d6eb56e5-5f02-4653-8579-216a9416fe9f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))

The size of the pile matters less than its refill rate. The current business keeps producing cash while the AI strategy develops.

[Apple also announced that John Ternus, its longtime hardware engineering leader, will become CEO on September 1, with Tim Cook moving to executive chairman.](https://substack.com/redirect/7e278624-602a-40dc-bd42-8290a4e105a3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) It would be too neat to say the board selected a hardware engineer only because local AI is the strategy. Apple didn’t say that but the succession does put someone who has spent decades inside Apple’s hardware system in charge as silicon, memory, and on-device computation become more important to the AI experience.

Apple’s long investment in silicon is what creates the option value.

Apple’s chips use a unified memory architecture, which lets the CPU and GPU work from the same pool instead of constantly copying data between separate pools. Because model weights and a conversation’s growing cache consume so much memory, shared access matters for local inference. A base machine can’t run every large model. High-memory Macs aren’t cheap, but the architecture still makes them unusually practical for experimenting with and serving models locally.

Apple also built [MLX](https://substack.com/redirect/f348902c-c032-4537-a768-8af13788280b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), an open-source machine-learning framework designed for Apple silicon’s unified memory. MLX LM makes it easier to generate text and fine-tune language models on a Mac. At [WWDC26](https://substack.com/redirect/f96b2061-bf38-4c07-9482-9205161d52cb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Apple demonstrated distributed local inference across multiple Macs.

Then the outside ecosystem does work Apple didn’t have to fund. [The MLX Community on Hugging Face](https://substack.com/redirect/6e126b5a-3668-44f5-a347-0fd9ef5c1a09?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) contained more than 5,300 model repositories on July 31. Developers take open models from companies and research groups around the world, convert the weights into a format that runs well through MLX, reduce the memory required through quantization, test them, and publish the result. Current listings include multiple versions of Qwen, Kimi, and many other model families. Apple didn’t train those models. It benefits when people want to make them run on Apple hardware.

For a Mac owner, this creates choices. A cloud model may still be much more capable. A local model may be useful for private material, repetitive high-volume work, offline experiments, or a workflow whose economics don’t tolerate a frontier API call every time. A developer can mix them: local for one step, cloud for the difficult review, and an Apple device as the place where the work happens.

Every useful conversion gives the Mac another job, even though repository count isn’t the same as mainstream adoption.

Memory prices can rise, and local models can stay too weak for normal customers. Apple still has to expose the right capabilities to developers and turn its assets into a product people understand.

Apple can benefit from model progress without training the winning model. It can improve its own, pay for access to somebody else’s, let developers bring open models onto the hardware, or combine all three. The current business funds more than one attempt.

That’s what a long financial clock buys: options, not victory.

## Time only helps if you spend it

It’s tempting to turn this into a morality play. Aschenbrenner moved too fast, Apple moved slowly, patience wins. I don’t believe that.

Aschenbrenner identified a real economic consequence of AI: physical infrastructure matters. His fund’s rise showed how forcefully markets can reward that view, while the sale under lender pressure shows the danger of attaching too much short-term financial pressure to a volatile long-term thesis. His thesis and its financing deserve separate judgments.

Apple has had years and still hasn’t shipped an assistant people love. What it built instead is silicon, distribution, developer tools, and a cash engine. Those buy more attempts. Winning is a separate problem.

The real test is what the structure does when the forecast is early, the market turns, or the first product is wrong.

I’d examine any serious AI bet with five questions.

First, what has to become true for the thesis to pay off? Name the capability, cost, customer behavior, or infrastructure change. “AI will be huge” isn’t a thesis you can operate.

Second, how long might that honestly take? Use a range, including the version in which progress is uneven and adoption arrives later than the demo.

Third, who controls the clock before then? Look for lenders, brokers, cloud commitments, investor rights, supplier contracts, and burn. A five-year belief financed with a ninety-day runway isn’t made safer by conviction.

Fourth, what produces value now? Current customers, revenue, useful data, a distribution channel, or a smaller product can keep the company learning while the larger capability develops. Apple’s current hardware and services business is doing this on an enormous scale. A small builder needs a much smaller version of the same principle.

Fifth, which options improve while you wait? An ecosystem might make the product more useful. The infrastructure you own might become more valuable when other people innovate. You may be able to change models without rebuilding the company and still serve the same customer with today’s technology.

These questions test one thing. Does the way you financed the belief match the belief itself?

## Surviving the buildout is the whole test

Public markets are going to make this tension harder to ignore.

If OpenAI or Anthropic eventually becomes a public company, investors won’t judge only the quality of the models. They’ll judge spending, revenue, margins, commitments, dilution, competition, and the time between the next infrastructure bill and the payoff. A research program measured in years will meet a market that reprices the stock every day.

The financing structure becomes part of the technology strategy, whoever is holding the paper.

The same is true for builders. If your product depends on a model becoming reliable next year, you need a company that can still exist next year. If a platform launch can remove every reason to buy, you need deeper customer knowledge or a different business. If your cloud bill scales faster than customer value, the technical achievement won’t rescue the economics.

And it’s true for Apple. Its cash engine and hardware system buy time, but the company still has to use that time. The opportunity is to make Apple silicon, its device base, its operating systems, and the work of the open-model community add up to an AI experience that feels deliberate.

One sale doesn’t end an AI boom, and one balance sheet doesn’t win a race. What the two stories share is the clock nobody puts on a chart: how long the owner can keep paying for the attempt.

How long does your thesis need? And who else can end it before then?

## [LINK: [Grab the two-clock prompt](https://substack.com/redirect/63859e77-a075-474f-9169-2f84ec685b4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)]

Those five questions are easier to ask than to answer honestly about your own work. So I built the prompt version.

Paste it into your LLM of choice. It asks you six things: what the bet is, what has to become true for it to pay, how long that honestly takes, who controls your runway before then, what pays the bills today, and how long you could go with no new money. Then it scores both clocks, tells you whether your financing matches your belief, and names the one thing most likely to end the bet before it pays.

It is built to push back. Conviction gets treated as something to test rather than as evidence.

## Coming up

This week: the Anti-Slop Cannon. A practical guide on how to define your outputs well enough that the model stops guessing.

## Related reading

- [The largest IPO in history is engineered to spend your retirement savings](https://substack.com/redirect/bde00650-b655-4956-b0d9-1d74190e674b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Executive briefing: the bubble test for OpenAI](https://substack.com/redirect/5e34e639-2390-4a17-8e31-acebf49a1a26?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Executive briefing: your AI vendor contract isn’t built for a capacity crunch](https://substack.com/redirect/ddbfb4c2-226a-422e-b0c7-b3119d6df1b5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Executive briefing: your company is about to get cheap intelligence](https://substack.com/redirect/c53de6ca-071b-4983-86b2-847135e8ab6b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)
