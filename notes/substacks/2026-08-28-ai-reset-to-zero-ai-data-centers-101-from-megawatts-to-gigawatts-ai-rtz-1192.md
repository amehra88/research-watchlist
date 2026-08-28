---
doc_type: substack_post
source: substack
publication: 'AI: Reset to Zero'
publication_url: https://michaelparekh.substack.com/
source_email: <20260828050236.3.04078d2791b27dea@mg2.substack.com>
source_sender: Michael Parekh <michaelparekh@substack.com>
source_url: https://open.substack.com/pub/michaelparekh/p/ai-data-centers-101-from-megawatts
source_date: '2026-08-28'
subscription_tier: free
tickers:
- NVDA
themes:
- ai_infrastructure_capex
- datacenter_buildout_pacing
- data_center_deployment_constraints
- thermal_management_cooling
- nuclear_energy_buildout
- hyperscaler_capex_buildout
ingestion_date: '2026-08-28'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [AI: Data Centers 101, from Megawatts to Gigawatts. AI-RTZ #1192](https://substack.com/app-link/post?publication_id=684161&post_id=212251482&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMjI1MTQ4MiwiaWF0IjoxNzg3ODkzNzIwLCJleHAiOjE3OTA0ODU3MjAsImlzcyI6InB1Yi02ODQxNjEiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.c8NKyr_6NUZQnzPIusFW2vO_i0Ee0yMBLOgIgASOMaI)

### ...Part 2: how AI data centers work, the $50B+ gigawatt era, & decades of buildout being redone at trillions.

Yesterday’s [Part 1](https://substack.com/redirect/6f6df03e-0ee4-480a-9942-188d8639c9ec?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) covered how AI data centers became the political football of the November midterms. Today, Part 2 steps back for the primer: what these facilities actually are, how they work at a high level, and why this generation is different from every one before it, in this [AI Tech Wave](https://substack.com/redirect/336d137f-1d11-48ed-90d7-dea6d82e6151?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Consider it a reference piece we will point back to in the months ahead.

Axios lays it out in [“Data center fight heating up: How they work and how much power they use”](https://substack.com/redirect/a56ac1b5-6454-4ecf-bd36-4ec7c9b568fe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): America has roughly 4,000 data centers today, with some 3,000 more under construction or planned. At bottom they are warehouses of computers, racks of servers storing our photos, streaming our shows, and running our apps. Data centers used about 1.5% of global electricity in 2024, headed for roughly 3% by 2030; in the US, estimates run from 9.5% to as much as 15.3% of American electricity by then. A large facility can draw millions of gallons of water a day for cooling, though Axios’s own chart offers useful context: cattle ranching and conventional power plants each consume far more water nationally than data centers do.

What makes the AI generation different is concentrated in one word: power. The classic data center of the last three decades was measured in single or double-digit megawatts, sipping from the local grid. AI data centers are built around dense racks of GPUs, liquid-cooled because air can no longer carry the heat away, and measured in gigawatts, each one drawing on the order of a nuclear plant’s output. That is why the fights of Part 1 are about electric bills and water, and why the developers increasingly bring their own generation, from gas turbines to nuclear deals, to the site.

Some personal history explains the arc. In a prior career at Goldman Sachs, I helped take the first generation of these companies public in the late nineties: Exodus Communications and Equinix among them, the original internet data center landlords. Exodus did not survive the dot-com bust, its assets absorbed into other entities over the years. [Equinix](https://substack.com/redirect/bd40beb7-bcd8-4f5f-9091-1fc4bc77f31c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is still very much with us, a hundred-plus billion dollar company built on those same foundations. Same buildout, opposite corporate fates, and the infrastructure itself kept compounding value through both. Worth remembering as the current cycle’s critics and cheerleaders both make their cases.

Regular readers have watched this generation’s ladder get built rung by rung here. Two years ago it was [going up from 100,000 GPU data centers](https://substack.com/redirect/d7a46c2e-b6a3-4774-ae5d-0303c6fbcb50?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); then gigawatt-scale facilities became [the new AI table stakes](https://substack.com/redirect/ee6da216-2599-4601-8e3a-eb2aba242e86?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA); then [the power plays began to build gigawatt data centers](https://substack.com/redirect/94b533c5-de01-458b-b97a-6bc2b0c8e566?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in earnest. The 101 of today was visible in the trade press of last year; it just kept getting bigger.

The scale of the transition is the headline number. The world spent the last two to three decades building multi-hundred-billions of dollars worth of traditional data centers; that entire installed base is now being redone, rapidly, into gigawatt-class AI facilities at investments measured in the trillions. A single gigawatt campus runs $50 billion plus all-in, the number we have used here consistently across Stargate, Colossus and their peers. Nvidia’s Jensen Huang put the industry’s own frame on it at Davos, [per Fox Business](https://substack.com/redirect/962b7bf1-fb75-4a9a-a604-f1d0058febf7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), calling it “the largest infrastructure buildout in human history”, with estimates he cited of some $85 trillion in related spending over the next fifteen years, and jobs across construction, electrical and network trades all along the way.

For the fuller economics behind the primer, [our four-part AI supply and demand series](https://substack.com/redirect/dc4269b8-42de-41b0-9017-563addf710be?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is the companion read: [the supply ambitions](https://substack.com/redirect/4c46323b-f77d-40b2-a01d-2ebdaf7d27c8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), [the demand bull case](https://substack.com/redirect/7ba572a2-c10d-4579-8545-adfec59cb193?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [the compute crunch at ground level](https://substack.com/redirect/a06a3594-faed-4865-9c18-3e257fe60bfe?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), with the grid mechanics covered from [the AI power grab](https://substack.com/redirect/5252048f-6ab3-4a7f-affa-8b6234618c62?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [power ramps and bad harmonics](https://substack.com/redirect/cc10bd8b-e732-4add-bdea-e7be61b30757?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

My take: the most useful thing a mainstream reader can hold onto is that a data center is not a mystery box; it is real estate plus computers plus power, and only the third ingredient has fundamentally changed. The first generation was a real estate business with servers in it. This generation is an energy business with GPUs in it, which is why the politics of Part 1 run through utility bills and water tables rather than zoning hearings alone. And the Exodus and Equinix story is the honest precedent: some of today’s builders will not survive their own capital cycle, but the facilities, the fiber and the power infrastructure will compound value for decades regardless of whose logo ends up on the door.

The trillions in AI Infrastructure get built any which way this [AI Tech Wave](https://substack.com/redirect/336d137f-1d11-48ed-90d7-dea6d82e6151?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Stay tuned.

(NOTE: The discussions here are for information purposes only, and not meant as investment advice at any time. Thanks for joining us here.)
