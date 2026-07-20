---
doc_type: substack_post
source: substack
publication: Vik's Newsletter
publication_url: https://www.viksnewsletter.com/
source_email: <20260715173318.3.57909d8efb404e42@mg-d1.substack.com>
source_sender: Vik's Newsletter <viksnewsletter@substack.com>
source_url: https://open.substack.com/pub/viksnewsletter/p/lasers-for-cponpo-part-1-the-inp
source_date: '2026-07-15'
subscription_tier: free_plus_paid
tickers:
- LITE
themes:
- advanced_materials_ai_infra
- ai_compute_topology
- networking_competitive_landscape
ingestion_date: '2026-07-16'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Lasers for CPO/NPO: Part 1 – The InP DFB Laser](https://substack.com/app-link/post?publication_id=2065897&post_id=207183819&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNzE4MzgxOSwiaWF0IjoxNzg0MTM2OTY4LCJleHAiOjE3ODY3Mjg5NjgsImlzcyI6InB1Yi0yMDY1ODk3Iiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.WzvBuiph88bcKhgYzjdkQ_8Fe2MfOeeqeBUb9J0WOhk)

### How an InP DFB laser works, and the four physical walls that make high power hard.

There is a lot of FUD in the market about ultra high power (UHP) lasers for CPO and who the leading provider is in this segment. Everybody I’ve asked about UHP lasers unequivocally says Lumentum is in the lead, but few are able to discuss the engineering challenges in making UHP lasers, where the Lumentum advantage lies (if it even exists), and what the real alligator-filled moat is that keeps competitors out.

The goal of this article series is not to dethrone Lumentum or advocate for an alternative provider in any way. It is to understand the true difficulty of making UHP lasers for CPO from first principles, so that the reader is well informed enough to cut through the noise and think for themselves.

Instead of examining generic laser architectures, we will directly address the one that Lumentum says their structure is most similar to, in their [CLEO 2022 paper](https://substack.com/redirect/4aa7d2c0-427a-470a-8d15-99978f1a28cb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

In their CLEO 2022 paper, it seems interesting that Lumentum would quote a paper from 2007 as the basis for their high power laser design. These authors at the time were affiliated with JDS Uniphase, which spun off in 2015 to become the publicly traded, and well loved company that we know as Lumentum today.

Interestingly, none of those authors work at Lumentum any more. Another important takeaway is that Lumentum has been working on UHP lasers since before they were Lumentum. As it turns out, 20 years later, this precise laser architecture is what the world wants for CPO and Lumentum just happens to have a ton of experience with it.

This 2007 paper describes a 1310 nm InGaAsP/InP DFB doing 600 mW on-chip and 350 mW ex-fiber with sub-500 kHz linewidth, and is spec-for-spec the ancestor of the UHP laser Lumentum sells for CPO today. We’ll use this as a case study to understand UHP lasers and how its related challenges were solved, but is still by no means an endorsement for investments in Lumentum. Do your own research.

To understand how to make a good UHP laser requires a background in how these devices work. This first part is groundwork: how an InP DFB laser works and the physical walls that make high power hard. Where Lumentum’s advantage actually lies, and how deep the moat runs, needs this physics first, so that verdict waits for Part 2.

Contents:

- InP laser diode fundamentalsMultiple Quantum Well structureL-I curve, spontaneous vs stimulated emission

- Distributed Feedback (DFB) grating designMode-hoppingHow to space gratingsHow DFB worksRefractive index changesReflection strength and length

- Laser Linewidth and DFB Cavity LengthCalculating linewidth: Schawlow-Townes-Henry equationImpact of power, mirror loss and dependence on length

- Low Power DFB Lasers for Telecom/EMLDirect modulated lasers (DML)CW lasers and EMLs

- High Power DFB Lasers for CPOHow to increase output powerThe 4 walls of UHP lasersHeatLinewidth wideningGetting light outCatastrophic optical damage

By reading this post, you agree to the [terms and conditions](https://substack.com/redirect/481620fc-8097-479e-8fcb-1263859956dc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Also see the [full ethics statement](https://substack.com/redirect/b1582d57-aa74-47b6-9f5a-8446ffa2b4db?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

If you are not a paid subscriber, you can purchase just this article using the button below. You can find the whole catalog of articles for purchase [at this link](https://substack.com/redirect/9e59d57b-aea9-44d6-91ec-d212ae21812e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

[Buy the report](https://substack.com/redirect/eb1e1c8f-b518-4b5d-aee2-1f7f3082d0e0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

If you would like to engage boutique research services for your project, reach out to us.

[Contact SemiExponent](https://substack.com/redirect/68f6bc76-c3b5-40d6-a65f-9b9ccefa9666?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

The Indium Phosphine (InP) Distributed Feedback (DFB) laser is the fundamental component of optics today, so it is best we understand how it works. It consists of two basic parts built on the same piece of material: The InP laser diode and DFB grating.

### The InP laser diode

This is often called the gain section and its job is to convert electrical current into optical power. The light is generated by Multiple Quantum Wells (MQW) in an “active region” which are essentially alternating layers of InGaAsP (Indium-Galium-Arsenic-Phosporus) sandwiched together. The alternating layers have slightly different compositions of these fundamental elements, so that they have slightly different energy levels. The purpose of this structure is to trap electrons in a low-energy layer between two high energy layers so that the electrons are trapped in a “well” and can’t get out. Multiple wells means more electrons, which means stronger laser output.

Source: Effects of multiple quantum well width on InGaAs/InP laser diode, doi:10.1088/1742-6596/2937/1/012007. ([link](https://substack.com/redirect/1c02c163-95eb-43d5-8238-bd7ea97f7984?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA))

If you want to understand more about what energy levels in a semiconductor mean, I have several articles on this.

To generate light, current is applied to the laser diode by applying a voltage across the anode and cathode. When the current applied is low, the emission of light is a messy stream of light waves out of phase with each other, each one behaving independent of the other. This is called spontaneous emission, and is not a focused beam of light; it is much like LED light. If photons were people, they would just wander around in a park without purpose.

Beyond a threshold of current, stimulated emission kicks in. The photons generated in the presence of a highly concentrated “well” of electrons kick up more photons themselves resulting in an avalanche of more photons. These photons now march in step with their phases correlated to each other. Now the photons are on a military parade in complete lockstep while being highly directional and focused.

Source: Wide-Band and Scalable Equivalent Circuit Model for Multiple Quantum Well Laser Diodes, Jae Hong Kim, PhD Thesis, Georgia Tech 2005.

This relationship between light and applied current is represented by the L-I diagram shown below. The threshold of current needed to make photons march together depends on the temperature; higher temperatures need more drive current. This is an important observation that will later drive a lot of our understanding of UHP lasers.

Source: Wide-Band and Scalable Equivalent Circuit Model for Multiple Quantum Well Laser Diodes, Jae Hong Kim, PhD Thesis, Georgia Tech 2005...

## Subscribe to Vik's Newsletter to unlock the rest.

Become a paying subscriber of Vik's Newsletter to get access to this post and other subscriber-only content.

### A subscription gets you:
