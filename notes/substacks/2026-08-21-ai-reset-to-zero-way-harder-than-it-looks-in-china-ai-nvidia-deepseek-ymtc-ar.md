---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260821180843.3.fadac55cac739d1a@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-ramblings-daily@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/way-harder-than-it-looks-in-china
source_date: '2026-08-21'
subscription_tier: free
tickers:
- NVDA
- MU
- AAPL
- SPCX
themes:
- china_export_controls
- china_us_tensions
- china_ai_infrastructure_demand
- inference_compute_economics
- frontier_model_competition
- model_efficiency_evolution
- hbm_competitive_landscape
- nand_demand_cycle
- silicon_architecture_competition
- space_economy
ingestion_date: '2026-08-22'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [‘Way Harder than it Looks’ in China AI. Nvidia, DeepSeek & YMTC. ARD #146](https://substack.com/app-link/post?publication_id=684161&post_id=212184354&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMjE4NDM1NCwiaWF0IjoxNzg3MzM1ODQwLCJleHAiOjE3ODk5Mjc4NDAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.o7FqXKhIkWa_9muaAsvuAe7MEdFpYGBNd2t4-0cq1Ss)

### ...Nvidia’s China comeback chip, DeepSeek’s next frontier push, & China memory company YMTC’s IPO plans after CXMT debut.

‘Way Harder than it Looks.’ China continues to have a busy AI week. Today’s ARD is about what success actually costs in the world’s second largest AI market: New reports on Nvidia engineering a Groq Inference chip it can legally sell in China and denying the plan the day it leaks, DeepSeek shipping a model nipping at the American frontier while rationing compute, and China’s number two memory maker filing a five billion dollar IPO that US policy will likely also not let American companies touch as with CXMT.

Three stories, one lesson, in this [AI Tech Wave](https://substack.com/redirect/6270afc3-af17-42bd-b246-d007b5f6e168?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): everyone in this market is threading a needle while smiling for the cameras. My takes below, as discussed on the show.

## (1) Nvidia’s Denied-but-Reported China Comeback Chip

The Information reports Nvidia plans small-batch shipments of a China-tailored AI chip by year-end, with several Chinese customers already placing orders. The chip is a variant of Nvidia’s LPU, the inference accelerator from its $20 billion Groq licensing and team acqui-hire, which speeds up an AI chatbot’s responses working alongside GPUs. It already complies with US export rules; Nvidia reworked the software so it pairs with processors available in China instead of the banned Vera Rubin systems. The open question is whether Beijing allows the orders, after blocking the H20 and flip-flopping on the H200. And hours after publication, Nvidia flatly denied the story: no LPU sales in China today, no China-specific LPU on the roadmap. Reuters reported a similar plan in March; Jensen Huang denied that one too.

The prize is China’s white hot inference chip market. Moonshot, one of the Six AI Tigers, halted new customer signups after its Kimi K3 release overwhelmed capacity. DeepSeek raised its developer prices this month. Huawei’s Ascend 950DT inference chip ships in volume later this year, and China’s giants have locked up domestic chip production into next year. Even so, unmet demand leaves Nvidia a window, if both governments allow it. Meanwhile the blockade stays porous: banned H200s and gaming chips keep reaching China through resellers.

My take: Nvidia has put up extraordinary results for quarters without its traditional share of China, a market normally worth tens of billions of dollars a year to them, in a country supplying over half the world’s AI talent. Jensen keeps threading the needle between two hostile governments, and publicly cannot raise hopes until the opening is real; US analysts would build it into their models. The deny-while-reported dance is itself part of how hard this market has become, with another round of the geopolitical chess game ahead when the two presidents meet next month. None of it is as easy as it should be. Way harder than it looks. For now.

Sources:

- [The Information: “Nvidia Plots China Comeback With New AI Chip”](https://substack.com/redirect/a2d087de-411e-4996-bf08-e2ca1c4e4bf1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the year-end plan and existing orders; the Groq-based LPU and the China software rework; the H200 flip-flop; the porous-blockade detail.

- [Tom’s Hardware: “Nvidia denies report it will ship Groq-based LPUs to China by year-end”](https://substack.com/redirect/03b1f5c3-25d4-45ed-8840-ac4b005d6dcc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the same-day denial, and the March Reuters echo.

For longtime readers:

- [AI-RTZ #735: Nvidia reigns on DESPITE China hits](https://substack.com/redirect/adc1aff6-50d2-4b15-aca4-6580f699b819?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ, 2024: No Nvidia (or Apple) without China](https://substack.com/redirect/2c073500-5c19-475d-8a84-9af40edcd9f5?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1085: Nvidia’s Jensen rides Air Force One to China after all](https://substack.com/redirect/fd66db93-17a5-4be4-95f5-4c06ab126a4a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (2) DeepSeek’s Next Best AI Model

DeepSeek unveiled an experimental multimodal version of its flagship text-only V4 Flash model, saying it comes close to Anthropic’s Opus 4.8 on tests of multimodal agentic capability, where a model analyzes images and screenshots and takes action without constant prompting. It matches V4 Flash on text, agents and reasoning, it is open weight, and it is live through DeepSeek’s API today. DeepSeek has shipped vision models before, but this is the first time the multimodal push lands in its most cutting-edge series.

My take: DeepSeek remains the iconic Chinese AI company since it burst onto the world scene in January of last year, and what they ship is a flagship event for every peer in China. Having raised $7.4 billion at a $50 billion valuation, with talk of more capital and an IPO, they fully intend to play in the ‘super-scale’ league: models with trillions of parameters, trained at massive cost, with as much technical efficiency as they can carve out given restricted access to the latest US chips. Note the connective tissue to item one: this same company raised its developer prices this month because inference compute is scarce. Harder than it looks, and they are executing away.

Sources:

- [Bloomberg: “DeepSeek Unveils Test Model to Rival Anthropic’s Opus 4.8”](https://substack.com/redirect/0d152e3b-5353-4654-8cf3-d75936021f7e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the V4-Flash-Vision-Exp release; the multimodal agentic comparison; the fraction-of-the-price framing.

For longtime readers:

- [AI-RTZ #1121: China’s DeepSeek raises $7.4 Billion at $50 Billion](https://substack.com/redirect/b1f2540d-7d09-4d6a-a75e-7866dd7e368e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #127: Closer Than They Appear. China’s AI Founders, Robots & Talent](https://substack.com/redirect/5cce95a4-7d04-47b3-a66c-f643513d6b78?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## (3) China’s #2 Memory Maker YMTC Files Its IPO

Flash-memory champion Yangtze Memory Technologies, YMTC, had its Shanghai listing application accepted on Friday: a planned 33 billion yuan, about $4.9 billion, raise on the STAR Market, which would rank among that market’s biggest offerings ever. It follows CXMT’s roughly 450% debut that carried it past Tencent as China’s largest market cap, and China’s leading robotic company Unitree’s white hot listing we covered Thursday. China’s champions are being fed by white hot public markets at home.

The other side of the memory story, via CNBC: Micron’s $50 billion Boise buildout is remaking its hometown into a boomtown, with rising housing prices, packed restaurants and jewelry sales, because the stock is up more than tenfold since the end of 2024, past a $1 trillion market cap. Two new fabs, more than 17,000 new area jobs, a $10 billion research lab commitment, and the first US front-end fab for leading-edge memory coming in 2027, all riding the AI memory shortage as high-bandwidth memory gobbles the world’s DRAM supply and lifts prices on everything down to MacBooks and iPads.

My take: I have long discussed the need for the US to lift the restrictions keeping US companies from accessing memory supply in China via CXMT and YMTC, versus depending solely on the oligopoly of the two Korean mega-memory companies SK Hynix and Samsung, plus the US based Micron. All three are enjoying a bounty of short-term riches at both ends of the ‘mainframe AI’ and ‘local AI’ spectrum in this era of ‘RAMageddon’. Apple in particular could use the relief valve, while Micron lobbies DC to keep the China supply unavailable. I understand the policy choices are way harder than they look. But it is about picking the least worst of two unappealing options.

Sources:

- [Reuters: “Chinese flash-memory chipmaker YMTC plans to raise $4.9 billion in Shanghai IPO”](https://substack.com/redirect/2378af8a-75db-4663-a7e4-347c4ff2baf9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the accepted STAR Market application; the CXMT and Unitree listing lineage.

- [CNBC: “How Micron’s $50 billion Boise buildout is reshaping its hometown”](https://substack.com/redirect/ce298c95-ea92-4e74-b416-e4999cfa80dc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the tenfold stock and trillion-dollar cap; the fabs and jobs; the HBM shortage economics; the 1999 cautionary echo.

For longtime readers:

- [AI-RTZ #1128: US hamstrung on Memory Chip Supply via China](https://substack.com/redirect/28621105-00c3-491b-9826-547c2080d16f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1175: ‘RAMageddon’ lobbies DC and Apple vies for China CXMT](https://substack.com/redirect/e48caa60-b128-47ae-99c7-859d153e7961?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

My overall take: all three of today’s events highlight the extraordinary entrepreneurship and innovation energy driving China in AI technologies, and we ignore it at our long-term peril. It is relatively easy to dismiss China as ‘copycats’ and ‘distillers’; the reality is very different, from ByteDance’s TikTok to Temu, Shein and Tencent’s super-apps, with more for our technology industry to learn from them than we give credit for, for a change. US crown jewels like Apple and Nvidia, and frankly Google, Microsoft and Amazon too, have much of their bread buttered in China: markets, products, and above all a tech/AI talent pool growing faster than ours in sheer numbers and quality. And China’s companies execute through geopolitically challenged environments that make everything way harder than it looks.

## Gadget AI: China’s Commercial Space Surge

Two stories here. Private startup LandSpace landed the first stage of its Zhuque-3 rocket in Gansu province, the first reusable-rocket landing by a private Chinese company, weeks after a state entity caught a booster at sea with nets on a boat. And Beijing cleared Geespace, the commercial space arm of EV giant Geely, for a two-year satellite Internet of Things trial, the first such approval for a private Chinese company: 64 satellites up, a constellation of over 5,600 planned, trials in more than 20 countries, going straight at US market leader Iridium. SpaceX first landed a Falcon 9 booster in 2015 and now does it almost daily, with Starlink’s ten thousand plus satellites making up about two thirds of everything active in orbit; China’s rival constellations have about 400 between them. A decade behind, with the key economics unlock now in hand.

My take: China is emulating most current US efforts in space as well, with a lot more companies focused on it than the two we discuss most here, SpaceX and Amazon with Blue Origin.

A key distinction is their efforts are more pragmatic than the ‘[AGI/Superintelligence’](https://substack.com/redirect/e073d6dc-17b3-42e8-8c3a-cb2d9ddc14ba?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) pilled AI debates here. They’re focused on what works in the near-term. While the [US pines for ‘God-AIs’.](https://substack.com/redirect/079b5f25-f560-4668-a4b6-d3298a593188?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) With far less [existential AI Doomerism](https://substack.com/redirect/08ab1e14-c878-4567-9770-bde374f122b7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) debates to boot.

The state playbook is the one that worked in every other technology sector: foster the growth of dozens if not hundreds of companies, encourage them with subsidies, let them compete viciously, and a few winners emerge. The Unitree of robotics, the DJI of drones, the DeepSeek of AI. And unlike the US, China’s ambitions in space and AI are far more pragmatic and closer to the ground in terms of near-term achievability: an EV company running satellites for trucks, fisheries and pipelines is not chasing Mars, it is chasing AI/Tech revenue in mundane, everyday industries.

Sources:

- [NYT: “Chinese Start-Up Lands Reusable Rocket for the First Time”](https://substack.com/redirect/30d163a4-85ca-4e21-93e3-6925e18ae946?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the Zhuque-3 landing; the Falcon 9 decade gap; the ‘alternative Starlink’ Huawei analogy.

- [SCMP: “China clears Geely for landmark satellite IoT test to spur commercial space sector”](https://substack.com/redirect/f6bfcecf-e3e0-498a-a241-14b59bccc4b8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the MIIT trial, first for a private firm; the Iridium comparison; the satellite IoT market numbers.

For longtime readers:

- [AI-RTZ #1066: SpaceX/xAI IPO filing outlines Elon’s boundless AI Ambitions](https://substack.com/redirect/8c038875-ecf3-4737-a13e-66f0d6e84b65?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1057: Amazon Leo buys Globalstar Satellites for $12 billion](https://substack.com/redirect/aa2e4cd0-3201-4862-b1b5-83a35d9b19b4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1034: Elon Musk boosts SpaceX/xAI pre-IPO story with ‘Terafab’](https://substack.com/redirect/ec883c8a-b314-43e3-9a74-8c3e6f14def0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Q&A

Q1: What is the one space based infrastructure that gets most taken for granted today? ANSWER: It is GPS of course. Designed for military applications decades ago, but now a mainstream reality for billions of users, from navigation to deliveries and mobility and everything in between. Almost as fundamental as electricity, and we do not give it a second thought.

Q2: What is still a bit more of a ways away than currently appreciated in space innovations? ANSWER: Likely AI Data Centers and ‘Terafabs’ in space. The creators, deployers and investors of the technology are anticipating these at volume in less than five years; because of the science difficulties, the reality is likely a decade or more out. Very exciting science projects for now, and still a lot harder than they look.

Today’s companion AI-RTZ, #1185, is on the global state of open source AI models, part 2 of the open source arc this week: [AI: The Global State of Open Source AI Models (part 2). AI-RTZ #1185](https://substack.com/redirect/67d845e2-140b-4f3d-9a17-ec16ab2e2453?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Full Source Reading

### Nvidia and China

- [The Information: Nvidia plots China comeback with new AI chip](https://substack.com/redirect/a2d087de-411e-4996-bf08-e2ca1c4e4bf1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Tom’s Hardware: Nvidia denies the LPU-to-China report](https://substack.com/redirect/03b1f5c3-25d4-45ed-8840-ac4b005d6dcc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1085: Jensen rides Air Force One to China after all](https://substack.com/redirect/fd66db93-17a5-4be4-95f5-4c06ab126a4a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### DeepSeek

- [Bloomberg: DeepSeek unveils test model to rival Anthropic’s Opus 4.8](https://substack.com/redirect/0d152e3b-5353-4654-8cf3-d75936021f7e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1121: DeepSeek raises $7.4 billion at $50 billion](https://substack.com/redirect/b1f2540d-7d09-4d6a-a75e-7866dd7e368e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### YMTC and memory

- [Reuters: YMTC plans $4.9 billion Shanghai IPO](https://substack.com/redirect/2378af8a-75db-4663-a7e4-347c4ff2baf9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [CNBC: Micron’s $50 billion Boise buildout](https://substack.com/redirect/ce298c95-ea92-4e74-b416-e4999cfa80dc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1175: ‘RAMageddon’ lobbies DC](https://substack.com/redirect/e48caa60-b128-47ae-99c7-859d153e7961?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

### Gadget AI: China commercial space

- [NYT: Chinese start-up lands reusable rocket for the first time](https://substack.com/redirect/30d163a4-85ca-4e21-93e3-6925e18ae946?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [SCMP: China clears Geely’s Geespace for satellite IoT trial](https://substack.com/redirect/f6bfcecf-e3e0-498a-a241-14b59bccc4b8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1034: Elon’s ‘Terafab’ story](https://substack.com/redirect/ec883c8a-b314-43e3-9a74-8c3e6f14def0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

## Clips from today

### Nvidia’s China Comeback Chip

### Jensen’s Multi-Trillion Chip Boom

### China’s Reusable Rocket Moment

### AI Data Centers in Space: Not Yet

An impact of the [AI Tech Wave](https://substack.com/redirect/6270afc3-af17-42bd-b246-d007b5f6e168?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) worth tracking. Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
