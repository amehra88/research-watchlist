---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260907200241.3.b5cb2d91c6cd7e37@mg-d0.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/miles-to-go-before-we-sleep-in-ai
source_date: '2026-09-07'
subscription_tier: free
tickers:
- TSLA
- MSFT
- NVDA
- AMD
- AAPL
- BIDU
themes:
- autonomous_vehicle_competition
- ai_regulation
- agent_framework_landscape
- inference_compute_economics
- ai_infrastructure_capex
- pc_demand
- silicon_architecture_competition
- foundation_model_economics
- ai_agent_monetization
ingestion_date: '2026-09-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [‘Miles to Go Before We Sleep’ in AI. Tesla, Microsoft, Anthropic. ARD #157](https://substack.com/app-link/post?publication_id=684161&post_id=214213731&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNDIxMzczMSwiaWF0IjoxNzg4ODExNTcyLCJleHAiOjE3OTE0MDM1NzIsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.SPEuyJ1EDO6PTmTn9h4xr7KjSe9Bqb-0NokC8gOcCmA)

### ...Feds slow Tesla’s Cybercab. Windows goes local AI. Anthropic builds its own billing. Military turns off ad trackers.

‘Miles to go before we sleep’, one of my favorites from Robert Frost, a line I last leaned on for [OpenAI in early 2025](https://substack.com/redirect/9cd75e16-e463-4e0d-b457-445380ed181e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and it applies to three events today and so much more going on in this AI wave. Three events, around Tesla, Microsoft and Anthropic, and they share one shape. In each, the AI is ready before the infrastructure is. The road is not ready for a car without a steering wheel. The PC is not ready to run an AI agent locally without a memory upgrade. And the payment rails are not ready for a company charging billions of dollars by the token.

All three are relevant in the context of how much more we have to do for AI infrastructure, far beyond the models and robots and agents we talk about day in and day out. Plus a Gadget AI on the US military turning off the ad trackers on its phones and computers, and why your TV is next. My takes below, as discussed on the show, on this Labor Day.

## (1) The Feds Slow Tesla’s Cybercab. Not So Fast.

First up. Tesla started offering rides in its two-seater Cybercab on Thursday, in limited areas of Austin, a car with no steering wheel and no pedals. On Friday morning, hours later, the federal safety regulator opened an investigation, per TechCrunch and Reuters.

The mechanics matter here. Federal vehicle safety standards still require manual controls, brake pedals included. Tesla told NHTSA it self-certified the Cybercab as compliant, which is how automakers normally do it. The agency’s audit query will examine ‘the process and technical data on which Tesla relied’, and specifically whether Tesla decided certain federal standards simply do not apply to a car with no wheel. NHTSA’s administrator: ‘we need to ensure that all of our laws are followed.’ The Department of Transportation has proposed removing the manual-control requirements for vehicles designed to drive themselves. Until that work is done, in the agency’s words, ‘existing standards remain in force.’

There is a precedent, and it took years. Amazon’s Zoox self-certified its wheel-less robotaxi in 2022. NHTSA issued a special order, then an audit query, the same process now aimed at Tesla. Zoox went the formal exemption route, got a demonstration exemption in 2025, and received final approval to charge for rides only in July of this year, capped at 2,500 vehicles a year for two years. Four years, gate to gate. It now charges fares in Las Vegas.

The scoreboard, per Reuters and Texas records: Tesla has 420 autonomous vehicles registered in Texas, 45 of them Cybercabs. Waymo has 988. Tesla has no permit in California to run a robotaxi service or even test without a safety driver. Musk skipped Thursday’s Austin event. Pricing was described as dynamic, ‘a first-class experience at coach price’, with no date for charging fares. And the July 2025 promise, robotaxis available to half the US population by the end of last year, did not pan out. Cybercab production began in April; Musk said it would be ‘very slow’.

My take: the regulator is basically saying not so fast, and that is what regulators are for. Anything without steering wheels and pedals needs to go through a regulatory process, and Tesla being Tesla, and Elon being Elon, did not slow down for that speed bump. Now there is a case number. And this stuff is very early. I have long said that self-driving cars are going to take a lot longer than we think. I called full self-driving the ‘canary in the AI coal mine’ back in [October 2023](https://substack.com/redirect/6945a527-f9e9-4e3a-a10c-0343da18769d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a dozen-plus years and over $200 billion into the industry’s effort, and in [#515](https://substack.com/redirect/195330eb-db41-4e89-8044-38bd31b16e02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I argued it was easier to catch a rocket with chopsticks than to execute unsupervised self-driving cars. That still holds.

Tesla is not as well positioned here as the market value suggests. Waymo is ahead on every operational number, with lidar and radar that work in weather, [a $110 billion valuation](https://substack.com/redirect/3a3d743b-e993-402e-b770-3d5e7f1ee733?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and Uber and Lyft handling the demand funnel. And China is further ahead still. It is not a race, it is a long wave, as I have said for a long time. But China has the advantage of a top-down regulatory framework and a huge manufacturing base, with dozens of car companies focused on self-driving, most of them using lidar a lot more than Tesla does. [Baidu is past 14 million rides](https://substack.com/redirect/1ccd3741-0c85-4364-9014-e9a167afcc65?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and expanding into Europe, Asia and the Middle East. We are years earlier in robotaxis than the headlines suggest.

Tesla’s market value, $1.4 trillion per Reuters, far above any other automaker, rests on the autonomy story: the robotaxis on one side, the Optimus humanoid robots on the other, with investors also excited about Elon’s ambitions across SpaceX, AI, data centers in space and terafabs for chips. That is the [‘vibe coasting’](https://substack.com/redirect/bd342a40-52f4-4d9f-a452-e02c20e99812?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I wrote about when the Austin pilot launched last June with a safety monitor in the passenger seat: the market rewarding the promise ahead of the reality. It is easy to get carried away when one rides a Waymo or a Cybercab; it feels like living several years in the future. And that is all terrific, and we will all get there. It is going to take a little longer than we think. The regulatory plumbing has to be built too, and it needs to be addressed head on. Miles to go, literally.

Sources:

- [TechCrunch: Feds launch investigation into Tesla’s Cybercab deployment](https://substack.com/redirect/07a5a3da-8e6f-46c5-9ed5-2adec1644769?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Reuters: Tesla starts Cybercab rides in Austin, drawing US safety agency interest](https://substack.com/redirect/7ce98503-4c14-49ca-ac52-42e44d1581ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [Bumpier Roads for Self-Driving Cars, October 2023](https://substack.com/redirect/6945a527-f9e9-4e3a-a10c-0343da18769d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #515: Catching Rockets vs Unsupervised self driving cars & robots](https://substack.com/redirect/195330eb-db41-4e89-8044-38bd31b16e02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #761: Tesla ‘Vibe Coasts’ on AI Robotaxis](https://substack.com/redirect/bd342a40-52f4-4d9f-a452-e02c20e99812?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #985: Latest on Google Waymo’s funding and expansion strategy](https://substack.com/redirect/3a3d743b-e993-402e-b770-3d5e7f1ee733?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #901: Update on AI driven cars in China vs the US](https://substack.com/redirect/1ccd3741-0c85-4364-9014-e9a167afcc65?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) Microsoft’s Project Zenith: A Windows for Local AI

Story two, speaking of plumbing. Microsoft gave its developer-optimized Windows a name this week, Project Zenith, and a floor: devices with 64 gigabytes or more of unified memory, per The Verge. The first Zenith device is a miniature PC from AMD on its Ryzen AI Halo chips, announced on stage at IFA. More devices on other silicon come ‘in the coming months.’

The pitch, from Microsoft’s Windows platform chief: on these machines developers ‘can run 30B+ parameter models locally and unmetered, accelerating experimentation while helping reduce reliance on metered cloud tokens.’ Unmetered is the word to hold onto. The rest is a curated Windows: Visual Studio Code, GitHub Copilot, PowerToys and Windows Dev Skills preinstalled, File Explorer showing extensions and full paths, the Start menu tips and account nags turned off, the command palette on by default. Microsoft says it is ‘the result of listening to developers about what they need from Windows today, and where they want the platform to go next.’

Note the convergence. Nvidia’s RTX Spark N1X, the PC chip I covered in [#1104](https://substack.com/redirect/5ec2c9ae-5045-429a-8442-a0402771ab95?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) when Nvidia and Microsoft went local, launches in October for laptops and desktops with up to 128 gigabytes of unified memory, per Tom’s Hardware. Apple’s new Mac mini on the M6 starts at $899, unified memory on Apple Silicon since day one, and ‘good luck getting your hands on one’, as I noted on [ARD #148](https://substack.com/redirect/ed4fce85-ef41-45cc-8652-8b0b167faabc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Now Microsoft draws the same line: unified memory, 64 gigabytes and up, is the new floor for a computer that runs AI locally.

My take: I have written a lot about Microsoft working with Nvidia and others on local devices with huge GPU processing and no meter running for AI agents. For that you actually have to rework a lot of the software. I have argued that we are going to need a whole parallel internet, alongside the one we built over the last thirty years for humans, just for AI agents: in [#702](https://substack.com/redirect/936fc86f-5ceb-478c-acc4-50430349b65a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that AI agents were not designed for our current internet, and in [#1023](https://substack.com/redirect/14969c34-306e-4a23-b35b-e8948a961471?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that they increasingly need an internet of their own. It is not going to be scrapped and rebuilt. It is going to be built around, and the scaffolding is going to go up. Project Zenith is part of that scaffolding: a Windows platform designed for the machines, running local models of thirty billion parameters or higher, almost unattended. In other words, humans will have additional computers, for themselves and for their machines.

We are already seeing that with the boom in Mac minis, a success Apple has on its hands, intended or not. Apple’s superpower there has been its unified memory architecture, and the reports are that Zenith builds around a unified memory architecture for Windows, with Nvidia likely alongside with its Spark RTX machines. The device is the other half of the miles-to-go story for local AI, which will help consumers and businesses, small, medium and large, deploy AIs of all types, open and closed, on the cloud and on their local devices, often beefed up. Machines worth tens of thousands of dollars with today’s [RAMageddon](https://substack.com/redirect/ba5d3575-13d6-4c9b-9cef-fd7a2b67863f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) pricing, with 64 gigabytes and up the most expensive component on the board.

I live this every day. In [#1061](https://substack.com/redirect/b32919fc-7705-4b94-a529-9553c3dfa7b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) this April I compared today’s AI agent apps to the early 1980s PC days, when 640 kilobytes was the memory limit computers lived with for most of that decade. Today’s generation forgets all that, or was not around for it. We have the same memory juggling going on with AI, and it is not going to be solved in a matter of months. It will take years, with three phases roughly five years apart: usable but flaky through 2027, reliable for serious users by 2028 to 2030, invisible infrastructure in the early 2030s. A new form of Windows then has to be deployed in millions of local PCs optimized for AI agents, and every company from Nvidia to AMD is focused on it. That is the long and slow road, again, not so fast. Zenith is Microsoft building for phase one. It is the right move and it is early.

Sources:

- [The Verge: Microsoft’s Project Zenith is a ‘distraction-free Windows experience’ for developers](https://substack.com/redirect/dbb4de68-cf90-49e4-a67d-e7353a2560d2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Tom’s Hardware: Nvidia’s RTX Spark N1X launches in October for laptops and desktops](https://substack.com/redirect/50bbe403-90b6-4f1a-ad63-62eac538692c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [AI-RTZ #1104: Nvidia & Microsoft focus on local AI computers](https://substack.com/redirect/5ec2c9ae-5045-429a-8442-a0402771ab95?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #148: The ‘Need for Speed’ in AI Inference](https://substack.com/redirect/ed4fce85-ef41-45cc-8652-8b0b167faabc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #702: AI Agents not designed for our current Internet](https://substack.com/redirect/936fc86f-5ceb-478c-acc4-50430349b65a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #1023: AI Agents increasingly need an Internet of their own](https://substack.com/redirect/14969c34-306e-4a23-b35b-e8948a961471?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1061: Fragility of today’s Claude Cowork type AI Agent Apps](https://substack.com/redirect/b32919fc-7705-4b94-a529-9553c3dfa7b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1145: ‘RAMageddon’ really here to stay](https://substack.com/redirect/ba5d3575-13d6-4c9b-9cef-fd7a2b67863f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) Anthropic Builds Its Own Payments Plumbing, Chipping Away at Stripe

Story three. Anthropic is looking to build more billing, fraud detection and other financial infrastructure in-house, per its own job postings, The Information reports. The tell is a line in one posting: Anthropic’s ‘business is scaling faster than the processes and systems that support it.’ Annualized revenue rose nearly five-fold to almost $45 billion in the five months through May, per the piece, and complex token-based pricing makes collecting the money harder than selling the product.

The roles spell it out. One overhauls order management, provisioning, billing and invoicing. A staff billing engineer would decide where to build on outside platforms and ‘where to build our own primitives around them’, with ‘opinions on where they fall short.’ A fraud role builds real-time payment risk systems and tools against people gaming subscriptions and free credits. And a treasury role describes ‘the production-grade financial applications that no vendor has built for us yet.’ Anthropic says Stripe ‘has been a strong partner for years’ and it continues to work with them across the business.

The context is an industry pattern. OpenAI added Adyen as a second payment processor last month, and earlier this year moved where it stores customer card data to an intermediary, so it can work with multiple providers. Shopify added PayPal two years ago and is collecting state money-transmitter licenses. Stripe’s answer has been to move up the stack: the [$7.5 billion OpenRouter deal](https://substack.com/redirect/e7e4a6f0-74a1-453b-afda-e609f115a9ab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), which charges the buyers of AI rather than the sellers, and the $1 billion Metronome purchase in January for usage-based billing. Adyen bought Orb for the same reason. Stripe’s core take, 2.9% plus a fixed fee, less for the biggest customers, adds up fast for a company collecting from a very large number of small developers.

My take: this is one of the fastest growing revenue companies in the history of the planet, from nothing in AI coding tools with Claude Code and Cowork a year ago to a run rate well north of $60 billion this year, on my math likely past $100 billion by year end and $200 billion next year, the basis for the $2 trillion-plus valuation being targeted for the mega AI IPO to be filed in the coming weeks. So they are now looking to build more of their own billing, fraud detection and other financial infrastructure, which to date they have relied on companies like Stripe for. I covered Stripe and its OpenRouter deal on [ARD #142](https://substack.com/redirect/044e186b-1262-482f-9078-2eac2728fd76?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [ARD #145](https://substack.com/redirect/e7e4a6f0-74a1-453b-afda-e609f115a9ab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), with the standing disclosure that I am an early Stripe investor. Stripe has been one of the early providers of billing infrastructure to Anthropic, OpenAI and a who’s who of Silicon Valley.

Anthropic is doing what all the hyperscalers and frontier labs do: building their own chips in addition to Nvidia’s, in a frenemies kind of way, and now building billing separate from Stripe. It does not mean they replace it overnight. It is complementary, and it will take months and years to build. But ‘no vendor has built for us yet’ is the phrase to underline. What this story says is that the payment rails for the AI token economy are not built yet, even for the company at the front of the line.

The bigger point is that we are going into a world of super micro-billing for AI services, all of them super variable. Remember, the internet itself in its earliest days was never designed for micropayments. There was ambition to build it in; the reserved status code, HTTP 402 ‘payment required’, for the techies among you, never got built out in the early 1990s when I was heading Goldman’s internet research. It was a missing piece I talked about a lot then. The internet was commercialized for the next thirty years without it, and we made do with Amazon’s one-click and everything from PayPal to Venmo as workarounds. Now we are reinventing it again, with Anthropic rethinking billing in a world where tokens have to be priced on a variable basis by the trillions. The m2m version is bigger still: billions of AI agents transacting with each other, in fractions of a cent, at machine speed. Google’s [Agent Payments Protocol](https://substack.com/redirect/968d8b94-c9d6-48ed-9b64-8ddfacdfc97b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), Stripe’s stablecoin bets, OpenRouter’s routing, Anthropic’s primitives: all of it is the plumbing being laid, pipe by pipe. That is why Stripe paid up for the tollbooth, and why Anthropic is building its own meter. Miles to go on the rails, too.

Sources:

- [The Information: Anthropic’s In-House Payments Tech Push Could Chip Away at Stripe](https://substack.com/redirect/5151374b-edec-4174-91c8-bbccfef84256?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [ARD #142: ‘Hidden Figures’ in AI. Big Tech, Stripe & Anthropic](https://substack.com/redirect/044e186b-1262-482f-9078-2eac2728fd76?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #145: ‘Wheels within Wheels’ in AI. Stripe, Nvidia & Unitree](https://substack.com/redirect/e7e4a6f0-74a1-453b-afda-e609f115a9ab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1186: Mega-IPO Preps, Stripe M&A, Open Source Steam, & More](https://substack.com/redirect/c32362ba-a62c-433a-bfcc-fa0824e06e5c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #848: Google’s new AI ‘Agent Payments Protocol’ (AP2)](https://substack.com/redirect/968d8b94-c9d6-48ed-9b64-8ddfacdfc97b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1166: ‘The Meter’s Running’ on Long AI Agents](https://substack.com/redirect/f6cbc315-0c39-458d-a383-aaf5da45c94f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: three stories, one infrastructure gap. On the road, a car that drives itself has to be compatible with rules written for human drivers over the last hundred years, and that takes time because we want them as safe as human drivers, if not safer. On the device, a model that runs itself is running today on computers and smartphones designed for humans, and that has to be reinvented from the operating system up, whether Windows, macOS or Android, a parallel one optimized for agents, for huge amounts of unified memory, for running tools. On the rails, a company billing by the token is running on payment plumbing built for subscriptions, in a world of super micro-billing that the internet never had.

All three are the infrastructure for the AI agent and m2m internet I keep writing about, the one for billions of AIs, not one. On our computers, and on the road. The AI keeps arriving ahead of the roads, devices and rails it needs. That is not a knock on the technology. It is where we are in year four of this [AI Tech Wave](https://substack.com/redirect/3b8656f3-d684-4e9c-8a8c-2b3c50e5aff4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the layers below the models get built after the models prove they are worth building for.

Every prior wave worked this way. The PC arrived before the software, the internet before the broadband, the smartphone before the app economy. The regulator, the memory chip and the billing system are the unglamorous work, and the unglamorous work is what takes the years. It is the underlying stuff, far beyond the chatbots and models and agents and all the dramatic things we read about every day, that has yet to be built on all of these vectors. Miles to go before we sleep. Thank you, Robert Frost. Something to consider this Labor Day.

## Gadget AI: The US Military Turns Off the Ad Trackers

Today’s Gadget AI is a setting on the phone in your pocket. US military officials say they have disabled advertising trackers on a range of phones and computers, per a Reuters exclusive, after reports that commercially available location data had been used to target American forces in the Middle East.

The details, from letters released by Senator Ron Wyden: the Air Force disabled advertising identifiers on computers and mobile phones two months ago. Special Operations Command ‘recently’ did so on its Windows devices. The Army says advertising IDs have been blocked on Windows computers since before 2021, but on Android and Apple phones only ‘since at least February 2026.’ Mobile advertising IDs are the unique device identifiers the ad industry uses to track activity across apps and pinpoint location, and data brokers resell them. In July, Reuters reported some deployed personnel could be ordered to surrender their phones outright because their videos were helping Iran target US bases. Wyden and Representative Pat Harrigan have now asked the Pentagon to investigate whether the safeguards work. Harrigan’s line: US enemies ‘should not be able to pull out a credit card and buy information that helps them track American troops.’ A privacy ad-tech founder’s caution: turning off the ID removes you from bulk data sales, but you can still be tracked by triangulating device details with network data.

My take: the military is addressing the fact that most of the equipment it uses was designed for consumers: our phones, our TVs, our computers, with tracking technologies built in. This is the business of dual-use technology. For fifty-plus years the military had the luxury of technology built for its own purposes. In the last twenty or thirty years it has been adopting consumer technologies, and consumer technologies have a monetization angle. Tracking is one of them. What is good on the consumer side is not good on the military side, and it took a conflict to make the Pentagon flip a switch that has been in the settings menu for years. I wrote about the military’s own AI journey in [#344](https://substack.com/redirect/1bd6f4d3-b26f-43ca-9dd0-ed9f23a39095?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [#348](https://substack.com/redirect/277b663d-6d72-4f29-ac3b-a2f2be980513?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) back in 2024, from ‘pumping the brakes on generative AI’ to a planned fleet of a thousand unmanned warplanes. Two years on, the harder problem is not the AI in the jet. It is the phone in the pocket.

And it is not just the phone. Every TV we buy today essentially tracks you out of the box. You can turn it off; it is tedious, but doable. I did a Gadget AI in July, on [ARD #112](https://substack.com/redirect/396ad192-bf63-495b-8b74-6d4075ad3be1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), on the $400 Walmart Vizio set that The Verge found is one of the very few you can actually run as a ‘dumb TV’, and even that takes the better part of half an hour to switch off. Walmart bought Vizio to monetize that viewing data at the Walmart level; that is why the screens keep getting bigger and cheaper at Costco and Walmart. Now picture the same set in a barracks or a ship’s wardroom. Same dual use. This business of plumbing coming in the way, exposing vulnerabilities for the military on technologies it is using, is an oversight issue now finally being focused on.

It is relevant well beyond the military, as we quickly go into a world where our smart glasses track everything through their cameras, our pendants listen, and our AirPods get cameras too. It is relevant for consumers, who have been used to being the product for advertising-driven search and social media. It is relevant for companies, in how their employees are tracked, and how they use that data to train future AIs. And it is relevant for the military, whose assets and people are trackable by the bad guys in a conflict. The [data exhaust](https://substack.com/redirect/abc4f057-da1a-42e5-a6bd-0562586b97b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I wrote about in 2023 becomes the data trail. The military just told us what the default setting should be. Miles to go on that, too, and not so fast.

Sources:

- [Reuters: US military turns off ad trackers on devices amid Middle East targeting reports](https://substack.com/redirect/3d19cd6f-7782-4908-8c5f-307461ae75b9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: Vizio accidentally made the best dumb TV on the market](https://substack.com/redirect/27d53795-2845-4703-8e32-935cf3b60056?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers:

- [RTZ #344: ‘Shall We Play a Game’?](https://substack.com/redirect/1bd6f4d3-b26f-43ca-9dd0-ed9f23a39095?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #348: On Land, Sea, and Air](https://substack.com/redirect/277b663d-6d72-4f29-ac3b-a2f2be980513?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #112: AI Chips: Not As Easy As It Looks (Gadget AI: the Walmart Vizio ‘dumb TV’)](https://substack.com/redirect/396ad192-bf63-495b-8b74-6d4075ad3be1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Our Data Exhaust, August 2023](https://substack.com/redirect/abc4f057-da1a-42e5-a6bd-0562586b97b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Q&A

Q1: Should consumers do what the military just did, and turn off their ad IDs?

ANSWER: absolutely. But most of us will not. We live in a world of convenience as opposed to a world of doing what is good for us, and for the most part a majority of us will not do some of these things. But for those of us who care, we should be thoughtful about how this stuff is a trade: our convenience relative to our privacy. On the device it is a two-tap setting on iPhone and Android, and the cost is ads that know you a little less well. The bigger point is what it does not fix; the founder Reuters quotes says it plainly, you fall out of the bulk data sales, but network data and device fingerprints can still place you. And this issue is going to explode, not recede into the distance.

Q2: Does this change the story for AI devices, the glasses and rings and agents on our phones?

ANSWER: this is one of the crucial questions over the next two or three years, especially in [RAMageddon](https://substack.com/redirect/ba5d3575-13d6-4c9b-9cef-fd7a2b67863f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), as these devices head toward doubling in price. I think there is a lot more headwind for all of the companies, whether they are doing smart glasses or rings or pendants, small, medium or large. They will have to address the social creepiness issues I have talked a lot about. Apple is front and center with its new devices rolling out on September 9, and AirPods with sensors and cameras on the way over the next year. We will see how it goes. But a lot of infrastructure will have to be built and rebuilt to accommodate these AIs and the monetization models around them. Every one of these devices is a sensor package, and an AI agent that acts for you needs to know where you are and what you see. That is the utility. It is also the exhaust.

Today’s [AI-RTZ #1202](https://substack.com/redirect/e612a675-91d0-43cd-922c-ce850634bbf6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) went out this morning: Nvidia buys Hugging Face, the ‘home shelf’ of open AI models, for $13 billion, bolstering its open source platform around Nemotron and beyond, and why open and closed AI co-exist. Do take a look.

Tomorrow we’re back with ARD 158 and AI-RTZ #1203. The woods are lovely, dark and deep. I hope you all enjoy the Labor Day weekend. We have promises to keep, as they say, and miles to go before we sleep, on this [AI Tech Wave](https://substack.com/redirect/3b8656f3-d684-4e9c-8a8c-2b3c50e5aff4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Thanks for joining us, AI Curious Folk. Stay tuned.

## Full Source Reading

Everything cited today, in one place.

### Tesla’s Cybercab and the regulators

- [TechCrunch: Feds launch investigation into Tesla’s Cybercab deployment](https://substack.com/redirect/07a5a3da-8e6f-46c5-9ed5-2adec1644769?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Reuters: Tesla starts Cybercab rides in Austin, drawing US safety agency interest](https://substack.com/redirect/7ce98503-4c14-49ca-ac52-42e44d1581ce?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Bumpier Roads for Self-Driving Cars, October 2023](https://substack.com/redirect/6945a527-f9e9-4e3a-a10c-0343da18769d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #515: Catching Rockets vs Unsupervised self driving cars & robots](https://substack.com/redirect/195330eb-db41-4e89-8044-38bd31b16e02?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #761: Tesla ‘Vibe Coasts’ on AI Robotaxis](https://substack.com/redirect/bd342a40-52f4-4d9f-a452-e02c20e99812?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #985: Latest on Google Waymo’s funding and expansion strategy](https://substack.com/redirect/3a3d743b-e993-402e-b770-3d5e7f1ee733?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #901: Update on AI driven cars in China vs the US](https://substack.com/redirect/1ccd3741-0c85-4364-9014-e9a167afcc65?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Microsoft’s Project Zenith and local AI

- [The Verge: Microsoft’s Project Zenith is a ‘distraction-free Windows experience’ for developers](https://substack.com/redirect/dbb4de68-cf90-49e4-a67d-e7353a2560d2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Tom’s Hardware: Nvidia’s RTX Spark N1X launches in October for laptops and desktops](https://substack.com/redirect/50bbe403-90b6-4f1a-ad63-62eac538692c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1104: Nvidia & Microsoft focus on local AI computers](https://substack.com/redirect/5ec2c9ae-5045-429a-8442-a0402771ab95?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #148: The ‘Need for Speed’ in AI Inference](https://substack.com/redirect/ed4fce85-ef41-45cc-8652-8b0b167faabc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #702: AI Agents not designed for our current Internet](https://substack.com/redirect/936fc86f-5ceb-478c-acc4-50430349b65a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #1023: AI Agents increasingly need an Internet of their own](https://substack.com/redirect/14969c34-306e-4a23-b35b-e8948a961471?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1061: Fragility of today’s Claude Cowork type AI Agent Apps](https://substack.com/redirect/b32919fc-7705-4b94-a529-9553c3dfa7b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1145: ‘RAMageddon’ really here to stay](https://substack.com/redirect/ba5d3575-13d6-4c9b-9cef-fd7a2b67863f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Anthropic, Stripe and the payment rails

- [The Information: Anthropic’s In-House Payments Tech Push Could Chip Away at Stripe](https://substack.com/redirect/5151374b-edec-4174-91c8-bbccfef84256?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #142: ‘Hidden Figures’ in AI. Big Tech, Stripe & Anthropic](https://substack.com/redirect/044e186b-1262-482f-9078-2eac2728fd76?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #145: ‘Wheels within Wheels’ in AI. Stripe, Nvidia & Unitree](https://substack.com/redirect/e7e4a6f0-74a1-453b-afda-e609f115a9ab?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1186: Mega-IPO Preps, Stripe M&A, Open Source Steam, & More](https://substack.com/redirect/c32362ba-a62c-433a-bfcc-fa0824e06e5c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #848: Google’s new AI ‘Agent Payments Protocol’ (AP2)](https://substack.com/redirect/968d8b94-c9d6-48ed-9b64-8ddfacdfc97b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1166: ‘The Meter’s Running’ on Long AI Agents](https://substack.com/redirect/f6cbc315-0c39-458d-a383-aaf5da45c94f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: the military and the ad trackers

- [Reuters: US military turns off ad trackers on devices amid Middle East targeting reports](https://substack.com/redirect/3d19cd6f-7782-4908-8c5f-307461ae75b9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [The Verge: Vizio accidentally made the best dumb TV on the market](https://substack.com/redirect/27d53795-2845-4703-8e32-935cf3b60056?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #344: ‘Shall We Play a Game’?](https://substack.com/redirect/1bd6f4d3-b26f-43ca-9dd0-ed9f23a39095?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #348: On Land, Sea, and Air](https://substack.com/redirect/277b663d-6d72-4f29-ac3b-a2f2be980513?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #112: AI Chips: Not As Easy As It Looks](https://substack.com/redirect/396ad192-bf63-495b-8b74-6d4075ad3be1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Our Data Exhaust, August 2023](https://substack.com/redirect/abc4f057-da1a-42e5-a6bd-0562586b97b3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #628: OpenAI, ‘Miles to go before I sleep’](https://substack.com/redirect/9cd75e16-e463-4e0d-b457-445380ed181e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1202: Nvidia Buys the ‘Home Shelf’ of Open AI, Hugging Face](https://substack.com/redirect/e612a675-91d0-43cd-922c-ce850634bbf6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### Microsoft’s Zenith: Windows for Local AI

### AI Devices: The Social Creepiness Challenge

### Dual Use: The Military Turns Off Ad Trackers

### Smart Glasses & AirPods: Tracking Comes Next

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
