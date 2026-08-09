---
doc_type: substack_post
source: substack
publication: Vik's Newsletter
publication_url: https://www.viksnewsletter.com/
source_email: <20260804162850.3.ba8426f19dcdd1ad@mg-d0.substack.com>
source_sender: Vik's Newsletter <viksnewsletter@substack.com>
source_url: https://open.substack.com/pub/viksnewsletter/p/astera-labs-from-the-tray-to-the-rack
source_date: '2026-08-04'
subscription_tier: free_plus_paid
tickers:
- AMZN
- AVGO
- MRVL
- NVDA
themes:
- ai_compute_topology
- networking_competitive_landscape
- silicon_architecture_competition
- hyperscaler_revenue_concentration
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Astera Labs: From the Tray to the Rack, and What Comes After

Listen to [Semi Doped](https://substack.com/redirect/ae6de906-5558-4478-9b8e-e7207f6c35b8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), my podcast with Austin Lyons of [Chipstrat](https://substack.com/redirect/88570ce6-4463-4bd4-840b-b48a3e23a138?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), for a more casual take on the week in semiconductors. On every podcast app. Sign up for our [daily free newsletter](https://substack.com/redirect/83f4e47d-c89b-4099-bfc9-3741d378df23?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

# [Astera Labs: From the Tray to the Rack, and What Comes After](https://substack.com/app-link/post?publication_id=2065897&post_id=209778091&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwOTc3ODA5MSwiaWF0IjoxNzg1ODYwOTQ1LCJleHAiOjE3ODg0NTI5NDUsImlzcyI6InB1Yi0yMDY1ODk3Iiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.qVybJgdpMhHGHFBZfCSztipIIoPx3TqWFBfqB3k44kM)

### PCIe Switches, AWS Trainium, NVLink Fusion, and the UALink Future

Astera Labs’ expansion out of the tray, where they built the company using their Aries PCIe retimers for XPU-CPU-NIC connectivity, and into the rack via their Scorpio switches is their biggest near term growth move. From the 1Q2026 earnings call:

> “Given the size of the opportunity and the associated dollar content, we would expect to see that Scorpio will become our largest product line by the end of the year, which is strong performance for the product line that was only a small percent of total company revenue last year.”

In addition, Astera Labs explicitly pointed out in their last earnings calls that they expect their dollar content per accelerator to go up.

> “We do see our content continue to increase, and to that end we are expecting, and going forward with the design wins we have, over $1,000 worth of content per accelerator, and that is significant and growing rapidly for us.”

The consensus on Astera Labs is that Scorpio is the growth story and that part largely holds as Trainium 3 volumes ramp. What the consensus misses is that Scorpio X’s scale-up revenue has a narrow customer list, and a known end date when AWS moves Trainium 4 to NVLink Fusion. Astera Labs’ future hinges on their pivot to UALink in the next generation, and the potential to serve as NVLink Fusion connectivity partner to a broad cross-section of the AI accelerator industry.

In this post, we will focus on why Scorpio switches are the near term growth path, how AWS warrants plays in, and where NVLink Fusion and UALink land in Astera Labs’ future.

If you want to understand the history of Astera Labs from their early foray into retimers, check out our [deep dive podcast on Semi-Doped](https://substack.com/redirect/181773a2-9b2d-4e78-ab42-efd2f5dc6abf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on this. ALAB announces its 2Q2026 earnings call on August 4th 2026. We will publish an earnings review post as well.

Contents:

- Why it makes sense to go from PCIe retimers to switches

- What the choice of PCIe means as a protocol for scale-up

- Comparison of PCIe switches from Astera Labs, Broadcom, and Marvell

- How AWS warrants play into their relationship with Astera Labs

- What the move to NVLink Fusion in Trainium 4 means for Astera Labs

- Why UALink and its adoption defines the future of Astera Labs

By reading this post, you agree to the [terms and conditions](https://substack.com/redirect/7551b777-4122-4c9c-836d-a28b5ec8105c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Also see the [full ethics statement](https://substack.com/redirect/a2366ce4-58f6-42bf-ad17-8c8d33fa57d4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

If you’re new, check out the [About page](https://substack.com/redirect/fdf3fa3d-e72a-400a-a7b2-f344d7cbbff7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). A lot of readers expense the subscription to this newsletter as it helps their professional work. Group subscriptions (3+) are 20% off. If you have any questions, reply to this email and let me know!

If you are not a paid subscriber, you can purchase just this article using the button below. You can find the whole catalog of articles for purchase [at this link](https://substack.com/redirect/c1613dc6-979e-413c-8ccd-c604ec6808b1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

[Buy the article](https://substack.com/redirect/02d3f14e-a69a-4cf8-94a0-6ac2ea5c137f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Also check out the [Semi Doped podcast](https://substack.com/redirect/adc39b07-2b97-4fba-a04c-052fbefa488b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) with Austin Lyons and myself, and [our daily free newsletter](https://substack.com/redirect/83f4e47d-c89b-4099-bfc9-3741d378df23?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) with latest semi news.

If you would like to engage independent research services for your project or need expert calls, check out my boutique consulting practice at [SemiExponent](https://substack.com/redirect/e9c13104-4637-4a2a-93e2-cc2387154a49?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

### PCIe: From Retimers to Switches

Astera Labs’ current networking strategy is entirely built on PCI express (PCIe), with a future goal to upgrade to native UALink. Their Scorpio line of switches is built on PCIe, which is a natural extension of their IP from the Aries line of retimer products that are broadly used to fix signal integrity of PCIe links that connect the XPU to CPU, NIC or SSDs.

The Scorpio product line has two SKUs, for different use cases in the rack:

- Scorpio P-Series: PCIe 6 switching for scale-out networking — fanning GPUs, NICs, and storage out of head nodes. It has been shipping since Q2 2025 with design wins at three hyperscalers and two more starting late 2026. Has product variants from 32 to 320 lanes.

- Scorpio X-Series: the scale-up fabric — the merchant silicon switch, running memory-semantic traffic over PCIe.

Astera Labs states that Scorpio is a bestseller for them, with 10%+ revenue within two quarters of launch, and is expected to become the largest product line by the end of 2026.

### The Choice of PCIe

Regardless of their impending success with PCIe switches, it is interesting to ask why PCIe as a protocol of choice for scale up? PCIe has been the mainstay of connections of computer motherboards for decades, and what made Astera Labs a company with $1B ARR today is their prescient bet on PCIe in the AI era. Their massive design wins in the Hopper and Blackwell HGX boards within a server tray, was because of their first-to-market with a PCIe Gen5 retimer, which has become an incredibly sticky slot connecting XPU-CPU/NIC and is a big contributor to their success. The logical next move for Astera Labs is to move this IP up the stack into rack-scale.

PCIe itself is attractive as a protocol for one main reason: every device – XPU, CPU, NIC, SSD – already has a PCIe controller built in and natively speaks the same language. Because the protocol is designed to know the route directly to various devices, it routes by memory address and encodes destination in its upper bits. ESUN-T and UALink had to define specific transport layers to get the same thing. In addition, PCIe lanes run at a slower bit rate compared to Ethernet, which is useful for keeping scale-up in copper longer.

PCIe Gen5, for example, operates at 32 GT/s (giga-transfers-per-second), where the transfer refers to the movement of a bit. This relates to the modulation scheme as well: an NRZ modulated signal moves one bit per signal, while PAM4 moves two bits per symbol. The symbol modulation speed is measured in Baud: at 32 GT/s, it is 32 GBaud on NRZ, and 16 GBaud on PAM4. On a per-lane basis, the speeds of PCIe are slower than NVLink, ESUN (ethernet based) or UALink, which is oddly an advantage when it comes to interconnects for scale-up with copper (better reach). But, what PCIe lacks in per-lane speed, it must make up for in lane count.

The ultimate speed in Gbps of a PCIe link thus depends on: (1) speed in transfers/sec, (2) modulation format, and (3) number of lanes per link. Let’s work on a simple example to show this:

PCIe at 64 GT/s using PAM4 at 32 GBaud, and running four lanes in aggregate (x4) gives 64 GT/s x 4 / 8 bits = 32 GB/s unidirectional, or 64 GB/s of bidirectional bandwidth. The following table shows this calculation for several PCIe generations.

### ALAB Scorpio X, AVGO PEX, Marvell Structura S

It is instructive to compare the Scorpio switch against the big dog in the merchant silicon switch market – Broadcom. Broadcom also offers PCIe 6 switches in its PEX line of switches, alongside its flagship Tomahawk 6 (TH6). We’ll gloss over Marvell too...

## Continue reading this post for free in the Substack app
