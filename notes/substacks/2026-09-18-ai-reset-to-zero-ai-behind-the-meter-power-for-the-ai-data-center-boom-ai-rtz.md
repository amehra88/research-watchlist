---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260918050242.3.4be4dcca0825770a@mg-d1.substack.com>
source_sender: Michael Parekh <michaelparekh+ai-rtz@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-behind-the-meter-power-for-the
source_date: '2026-09-18'
subscription_tier: free
tickers:
- BE
- GOOG
- META
- SPCX
themes:
- ai_infrastructure_capex
- capacity_supply_tightness
- china_ai_infrastructure_demand
- data_center_deployment_constraints
- datacenter_buildout_pacing
- energy_storage_buildout
- hyperscaler_capex_buildout
- nuclear_energy_buildout
ingestion_date: '2026-09-18'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: ‘Behind the Meter’ Power for the AI Data Center Boom. AI-RTZ #1213](https://substack.com/app-link/post?publication_id=684161&post_id=215182382&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNTE4MjM4MiwiaWF0IjoxNzg5NzA4MTc0LCJleHAiOjE3OTIzMDAxNzQsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.BEGeonbYbpZ1vo3x9rDDbjo2h84eV3Jdx0KG9EexR28)

### ...Big Tech puts the power plant next to the GPUs. Gas, turbines, fuel cells, batteries. China’s head start on electrons.

Two years ago I called it [the AI power grab](https://substack.com/redirect/106d9d81-13ab-41e1-9ea5-9bfbc21edb54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Big Tech had discovered that the binding constraint on AI data centers was not chips, or money, or land. It was electricity, and the grid that delivers it.

Last week SemiAnalysis published the most detailed field report I have seen on how that constraint is actually being solved, in “[What is So Hard About Behind-The-Meter Power For Datacenters?](https://substack.com/redirect/0ff578a0-af99-4cbc-8d29-1b7b60330a4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)” It is intricate in the technical details behind the race to power today’s trillions in AI Data Center investments.

It is Part 3 of the AI data center series, and one of the [AI-RTZ Explainers](https://substack.com/redirect/164793f7-4627-4f30-9723-4f7f98f53727?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): the evergreen pieces behind the daily posts, written to stay useful long after the news cycle moves on, in numbers a regular reader can hold.

The high-level picture is what matters for this [AI Tech Wave](https://substack.com/redirect/6a72c661-956e-4320-9235-e2cb8bd27f51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and it is a big one.

> “Behind-the-meter [BTM] primary power solutions for [AI Data Centers], have been called all sorts of names, such as “[science experiments](https://substack.com/redirect/92742ab4-e724-475d-9462-8706b7d9977b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”, “[Dark Gigawatts](https://substack.com/redirect/92742ab4-e724-475d-9462-8706b7d9977b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”, and “[literally the dumbest thing that human beings have ever attempted to do](https://substack.com/redirect/057e82c6-5ba7-4d70-804b-aa705ed1e6b7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)”! “But the supply chain has witnessed a massive acceleration. Our [Energy Model](https://substack.com/redirect/f944e280-cacb-4301-b5c0-1bd3633cf7d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) now tracks 75GW of firm, binding orders in the supply chain only for behind-the-meter AI compute - of which ~20GW alone ordered in Q2 2026. What started as an Elon Musk experiment is now mainstream for every single AI Lab and hyperscaler.”

The [whole piece](https://substack.com/redirect/0ff578a0-af99-4cbc-8d29-1b7b60330a4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is worth a read.

But the short version. The US grid cannot connect gigawatt data centers fast enough, so the AI labs and hyperscalers are building their own power plants next to the GPUs.

And underneath all of it sits a frame I have been pressing for two years: China is behind on the best AI chips and the machines that make them, and ahead on the one input those chips cannot run without: POWER.

## What ‘behind the meter’ means

A meter sits where a project’s wires meet the grid’s wires. Everything on the grid side, the power plants, the substations, the pylons, is front of the meter. Everything on the project’s side is behind it.

Behind-the-meter power, or BTM, means the data center generates its own electricity on site, as primary power, not backup. The terms blur in practice: off-grid, islanded, co-located, microgrid. SemiAnalysis notes, drily, that many projects use ‘microgrid’ because it avoids saying ‘gas’.

I’ve [been discussing](https://substack.com/redirect/f676ea8f-8feb-4923-99f7-ef28822ca428?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) these BTM power [solutions like natural gas](https://substack.com/redirect/ba72bebb-9ed4-49ad-9b09-63bf5d300e12?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)and others, for a while now.

Most of these plants are built as a bridge. The campus runs on its own generation for the first years, and when the utility finally delivers a grid connection, the on-site plant shifts to backup or reserve. xAI’s first Colossus in Memphis has already made that transition.

Some will never connect. That is the new part.

## Why it went mainstream

The numbers SemiAnalysis tracks are the story. About 3 gigawatts of US AI data center capacity will be running behind the meter by the end of this year.

Those 75 gigawatts are OEM orders tied to specific projects, not the hundreds of speculative gigawatts in press releases.

For scale, the entire US grid added 53 gigawatts of generating capacity in 2025, per the [Energy Information Administration](https://substack.com/redirect/4d4cc1da-230c-4a12-be4f-2934e5a59e62?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Why the rush? SemiAnalysis frames it as AI economics. A power plant for a 1 gigawatt data center costs roughly $5 billion. Table stakes as the ante grows rapidly.

In today’s market, inference revenue on that gigawatt can reach $100 billion a year at high gross margins. Paying twice as much for power, or accepting lower efficiency, is a rounding error against getting the GPUs running a year earlier.

The other side of the ledger is the grid. Building new utility generation takes five years or more.

Interconnecting a large load takes years on its own.

In August, Texas Governor Abbott [paused new data center grid connections](https://substack.com/redirect/9c270717-8776-4afa-ac0e-dd25e653c7d9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for a statewide audit, after ERCOT’s queue swelled to about 474 gigawatts of requests, more than five times the state’s record peak demand, roughly 90 percent of them data centers.

> “Cheap GW-scale interconnections do not exist anymore.” ([SemiAnalysis](https://substack.com/redirect/0ff578a0-af99-4cbc-8d29-1b7b60330a4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))

SemiAnalysis reads the Texas pause as a positive for behind-the-meter, because a self-powered campus can promise a hyperscaler a timeline the grid cannot. I covered the political side of this last month in [Data Centers become the Midterms’ Political Football](https://substack.com/redirect/58d7ebda-3b60-478d-a1d5-75f6a920987f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The engineering side is now catching up to the politics.

## The menu: six ways to put electrons next to the GPUs

Here is the high-level map of what the big companies are actually doing, with the examples SemiAnalysis and public filings put on the record.

Gas reciprocating engines. Big truck and ship engines, from half a megawatt to twenty megawatts each, ganged together by the hundreds.

Utilities do not buy them at scale, so the AI labs get the factory slots.

OpenAI’s flagship 1.4 gigawatt campus in Shackelford County, Texas, built with Oracle, runs on more than five hundred Jenbacher engines and is about to start operating.

Anthropic and Meta have each signed several hundred megawatts with Enchanted Rock, whose gensets are built around a 22 liter V12 gas engine.

Order to power is about twenty months, against five years or more for a combined-cycle plant. The supplier count with multi-hundred-megawatt data center orders has gone from twelve to twenty-two in a year.

Gas turbines. Jet engines repackaged for power, in the 30 to 115 megawatt range, or utility-scale frames near 400 megawatts.

This is the Musk playbook. xAI’s Colossus 2 in Memphis draws its power from a plant across the state line in Southaven, Mississippi, where the state let the turbines run as ‘temporary’ units and then, in March, approved a 41 turbine, 1.2 gigawatt permanent plant.

Google, historically the most reluctant, is deploying 930 megawatts of off-grid aeroderivative turbines at a flagship campus, alongside more than a gigawatt of Mitsubishi J-class machines.

The catch is supply: turbine slots at the big manufacturers are sold out past 2030, and a secondary market now trades delivery slots at a real premium.

Fuel cells. Bloom Energy’s solid-oxide cells turn gas into electricity without a flame, which means far less nitrogen oxide and a much lighter air permit.

They have become the escape hatch when turbine permits get blocked. Oracle’s 2.45 gigawatt Project Jupiter in New Mexico abandoned its turbine design in April after 7,000 public comments and refiled on Bloom cells.

Google is putting 900 megawatts of them in Wyoming. Nebius switched its first US site to 328 megawatts of Bloom.

The open question is scale: nobody has run fuel cells at gigawatts, and they need supercapacitors to handle the load swings.

Batteries. Not the power, the shock absorber.

AI training load jitters by tens of megawatts several times a second, which shortens turbine shaft life and pushes combustion below its clean operating floor.

xAI learned this at Colossus 1 and installed 150 megawatts of Tesla Megapacks. Liberty Energy says batteries now average half of gas capacity across its data center clients.

A new class of medium-voltage UPS sits at the campus gate to ride through grid faults.

Solar and storage. No combustion, no pipeline, no air permit.

Crusoe and Redwood Materials have run a microgrid in Sparks, Nevada since June 2025 on 12 megawatts of solar and second-life EV batteries, at 99.2 percent uptime, now expanding to 20.

The catch is physics: an island of inverters struggles to clear its own short circuits, so a clean island has to buy grid-forming inverters and synchronous condensers.

SemiAnalysis thinks the long-run BTM campus becomes a true microgrid with a broad mix, and calls that a strong positive for solar and batteries. For now it is small.

Nuclear. The clean baseload everyone wants and nobody gets soon.

I covered the wave of deals when it broke in [Nuclear Power accelerated for AI data centers](https://substack.com/redirect/f676ea8f-8feb-4923-99f7-ef28822ca428?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): Microsoft and Constellation restarting Three Mile Island, Amazon and Talen at Susquehanna, Google and Kairos on small modular reactors, Meta’s nuclear tender.

Those are grid-connected contracts that land late this decade and into the 2030s. Fusion is the [stretch goal](https://substack.com/redirect/3ab341d5-df75-4b5e-b201-2b092049e4b1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). None of it powers a GPU in 2026.

## What is hard about it

SemiAnalysis lays out six gates a BTM project has to clear, and the report’s honest conclusion is that no single technology clears all six. Three of them decide most projects.

Money first. A grid interconnection used to cost a few million dollars and a letter of credit. A behind-the-meter plant costs billions before the first GPU arrives, and lenders want a signed offtaker, offtakers want a credible timeline, and the timeline depends on equipment deposits nobody has funded yet. The chicken and the egg.

Three models have broken the loop.

Vertical integration, the Musk way, equity-funded.

Full-scope developers who sell the data center with the power plant inside the price, which now commonly crosses $20 million a megawatt.

And a new class of ‘energy as a service’ vendors, the BTM utilities, companies like VoltaGrid that deliver power under long-term contracts and truck in compressed gas as a virtual pipeline while the real one gets built.

Permits second. Air permits turn on how many tons of nitrogen oxide a plant could emit running flat out.

Cross the federal line and you are into a full review that can add years.

So developers now choose jurisdictions as carefully as equipment. Colossus 2 sits in Tennessee; its power plant sits in Mississippi.

Texas, with cheap gas and a single pipeline regulator, is set to host more of the BTM fleet than any other state.

Everything related to Power for AI Data Centers is getting [super-sized](https://substack.com/redirect/9dc41c0e-a838-4e40-abdb-663df6afd823?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

People are the quieter gate. SemiAnalysis sizes the 2027 data center labor gap at 288,000 workers, and gas plants need boilermakers and pipe welders, an aging trade of 10,000 people nationally. Fuel cells need neither, which is part of why they keep winning orders.

Physics last. A grid gives a plant two things for free: inertia and fault current. An island has to make both. That is the least visible gate and, the report says, the least forgiving.

## My take

Three points.

One. The power problem is being solved, in the American way: fast, expensive, improvised, and mostly with gas.

I wrote in February that the [US AI data center boom is running on natural gas](https://substack.com/redirect/47932195-f62f-4284-a264-e5fa98fa69d6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and the numbers since have only confirmed it.

Seventy-five gigawatts of firm orders is not a science experiment. It is an industry.

The [$31 trillion PwC number](https://substack.com/redirect/6972160e-2e99-4216-9224-afa006fd1520?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) from last week for global AI data centers through 2050 assumes this build keeps going, and behind-the-meter is how the next three years of it get powered.

Two. The companies with the deepest pockets and the most patience will win the power race, not the ones with the best chips.

That has been my view since the [100,000 GPU table stakes](https://substack.com/redirect/34adbe4f-3f08-4d13-b211-4e30386b195b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in 2024.

OpenAI’s $150 billion of contracted Oracle capacity rests on off-grid gas. Anthropic’s flagship Texas campus is off-grid too, and its new Georgia site, [as I covered Tuesday](https://substack.com/redirect/deff4aa4-911c-4f5b-aaf8-4969e456c551?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), is still waiting on its 120 megawatts.

Meta’s Hyperion in Louisiana takes the utility route, with Entergy building the gas plants and the pipeline.

Every path costs billions per gigawatt before a single token is served, which is exactly the [compute race](https://substack.com/redirect/0625047e-431a-4ea8-9847-541c70fec5fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) I described last week in dollars.

Three. Elon went first, and the industry is now running his playbook with better lawyers. The Memphis turbines that drew lawsuits in 2025, which I covered in [Elon’s Mega AI Data Center Supply Ambitions](https://substack.com/redirect/b05b7974-db65-4e0b-9259-fa7c6df0ba10?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), taught everyone the state-line trick, the Megapack fix, and the bridge-to-grid model.

Haste made waste, as I said on the [ARD in July](https://substack.com/redirect/1ece595e-5948-4b2e-ad82-09eb5bab8812?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and then haste became the standard.

## China’s head start on electrons

Now the other frame, which is the one I think the US policy debate keeps missing.

China does not have Nvidia’s best chips. It does not have ASML’s best lithography machines. Its data center infrastructure is behind on the frontier. I have written that story for two years, from [China continues to lead in AI from behind](https://substack.com/redirect/4952352c-3306-45a2-9739-2db75972612b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [China focused on the AI Applications Prize](https://substack.com/redirect/ba9190d0-6594-4a98-83ac-73c2fde33d1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [A Tale of Two AI Races](https://substack.com/redirect/bc4a656f-ca0a-498d-9e6e-1c9e2137427a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

But on the input this entire piece is about, China is not behind. It is ahead by an order of magnitude.

In 2025 China added 543 gigawatts of generating capacity, per its National Energy Administration, 315 gigawatts of it solar. The United States added 53 gigawatts. Ten to one. Since 2021, China has added more capacity than the entire US grid contains.

China’s electricity demand reached 10,573 terawatt-hours last year, growing 5 percent, per [Ember’s Global Electricity Review](https://substack.com/redirect/5506c75b-57fc-4ef1-84b9-ff0b5530fd11?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). The US used 4,536 terawatt-hours, growing 3 percent. China’s increase alone, about 500 terawatt-hours in a single year, is roughly what the whole of Texas uses.

The point is not that China’s data centers are better. They are not.

The point is that the US is spending billions per gigawatt, and years of permitting, to build behind the meter what China builds in front of it as a matter of national routine.

When a Chinese lab wants a gigawatt, the constraint is chips. When an American lab wants a gigawatt, the constraint is the meter.

That asymmetry shapes the race in ways the chip debate does not capture. Export controls slow China’s access to the best compute. Nothing slows its access to power.

And the Chinese labs, as I wrote in [the global state of open source AI](https://substack.com/redirect/3c72cbf2-97c6-450f-bc22-f11a8627ccee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), have gotten very good at doing more with less compute. Cheap, abundant electricity is the other half of that equation.

## Where this goes

SemiAnalysis’s view, and mine, is that the grid will expand, but materially slower than AI needs. So the behind-the-meter campuses get bigger, not smaller, and they start mixing gas, batteries, solar and eventually nuclear into true microgrids.

Some of those 75 gigawatts of engines and turbines become backup when the grid arrives. Some get moved to the next site. Some never connect at all.

For the companies, the questions are the ones I have been tracking since the [braggawatt year-end update](https://substack.com/redirect/062b304f-209c-4b30-b4c8-e12ffcd94d22?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): who has firm gas, firm equipment, and firm permits, versus who has a press release. Those distinctions decide which gigawatts show up in 2027 and 2028.

For the country, the question is whether the US wants its AI build powered by a patchwork of private gas plants next to the GPUs, or by a grid that can actually connect them.

For now the answer is the patchwork, because the patchwork is the only thing that ships on time.

This week’s two-parter on [hidden reasoning](https://substack.com/redirect/e7b796ca-35fc-4af5-b060-014cd089ea8f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) was about what the models do with the compute. This is about how the compute gets its electrons. AI Loops 101, next week, ties the two together in numbers you can hold.

This is what is worth tracking this [AI Tech Wave](https://substack.com/redirect/6a72c661-956e-4320-9235-e2cb8bd27f51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to truly understand the AI Data Center power plays. Stay tuned.

## Sources

Primary

- [What is So Hard About Behind-The-Meter Power For Datacenters? Part 1, SemiAnalysis, September 10, 2026 (paid)](https://substack.com/redirect/0ff578a0-af99-4cbc-8d29-1b7b60330a4c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Quoted above

- [Facing an estimated 474 GW of interconnection requests, Texas hits pause on data centers, Utility Dive, August 5, 2026](https://substack.com/redirect/9c270717-8776-4afa-ac0e-dd25e653c7d9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [US electric capacity additions, EIA, February 20, 2026](https://substack.com/redirect/4d4cc1da-230c-4a12-be4f-2934e5a59e62?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [Global Electricity Review 2026, Ember](https://substack.com/redirect/5506c75b-57fc-4ef1-84b9-ff0b5530fd11?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [China added 543 gigawatts of new power capacity in 2025, OilPrice citing Bloomberg and the NEA](https://substack.com/redirect/f9ab9c5f-b19d-4dfd-84e2-0f4992f492bc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [China adds 315 GW of solar in 2025, pv magazine, January 28, 2026](https://substack.com/redirect/758464e2-f59b-4d1d-9255-216872277e82?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

For longtime readers

- [RTZ #407: The AI Power Grab (July 2024)](https://substack.com/redirect/106d9d81-13ab-41e1-9ea5-9bfbc21edb54?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #477: The ‘100,000 AI GPUs’ Table Stakes opening round](https://substack.com/redirect/34adbe4f-3f08-4d13-b211-4e30386b195b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #481: Power Plays begin to build Gigawatt AI data centers](https://substack.com/redirect/6e7cfdb4-1c5c-4066-b8ec-0e39bfac65ee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #512: Nuclear Power accelerated for AI data centers](https://substack.com/redirect/f676ea8f-8feb-4923-99f7-ef28822ca428?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #568: Exxon to the AI Energy Rescue?](https://substack.com/redirect/ba72bebb-9ed4-49ad-9b09-63bf5d300e12?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #584: AI Data Center Power ramps and ‘Bad Harmonics’](https://substack.com/redirect/e0342108-5489-467c-93f1-c2643c00facf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #609: OpenAI/Softbank’s Stargate for new AI destinations](https://substack.com/redirect/204683d2-529d-43e6-8fe9-263ecab7e767?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #860: OpenAI’s Intimidating AI Compute & Power Plans](https://substack.com/redirect/c6dff185-2561-4338-b358-9a440d4cf72c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #938: Year-end update on ‘Braggawatt’ powered AI Data Centers](https://substack.com/redirect/062b304f-209c-4b30-b4c8-e12ffcd94d22?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #940: Mapping the Power Hungry AI Data Center Race across 50 States](https://substack.com/redirect/dbe87fb6-d5f8-4e01-8b2b-0b1b73376fa3?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #984: US AI Data Center boom driven on natural gas power](https://substack.com/redirect/47932195-f62f-4284-a264-e5fa98fa69d6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #1035: Nuclear Fusion the next ‘stretch goal’ to Power AI](https://substack.com/redirect/3ab341d5-df75-4b5e-b201-2b092049e4b1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #1042: Update on ‘monster’ US AI Energy & Power needs](https://substack.com/redirect/4c5fb68b-a70f-4a1e-939f-4bc8fa3189e6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1173: Elon’s Mega AI Data Center Supply Ambitions (part 1)](https://substack.com/redirect/b05b7974-db65-4e0b-9259-fa7c6df0ba10?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1191: Data Centers become the Midterms’ Political Football](https://substack.com/redirect/58d7ebda-3b60-478d-a1d5-75f6a920987f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1192: Data Centers 101, from Megawatts to Gigawatts](https://substack.com/redirect/537919b8-b275-4453-bb9e-e49268a0b5b2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1204: Anthropic’s $517B vs OpenAI’s $750B Compute Race](https://substack.com/redirect/0625047e-431a-4ea8-9847-541c70fec5fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #122: Haste Makes Waste in Super-Sizing AI Data Centers](https://substack.com/redirect/1ece595e-5948-4b2e-ad82-09eb5bab8812?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [ARD #159: ‘Beyond the Moon’ in AI, PwC’s $31.6T](https://substack.com/redirect/6972160e-2e99-4216-9224-afa006fd1520?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #403: China continues to lead in AI from behind](https://substack.com/redirect/4952352c-3306-45a2-9739-2db75972612b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #832: China focused on the AI Applications Prize](https://substack.com/redirect/ba9190d0-6594-4a98-83ac-73c2fde33d1c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [RTZ #888: A Tale of Two AI Races, US vs China](https://substack.com/redirect/bc4a656f-ca0a-498d-9e6e-1c9e2137427a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

- [AI-RTZ #1185: The Global State of Open Source AI Models (part 2)](https://substack.com/redirect/3c72cbf2-97c6-450f-bc22-f11a8627ccee?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
