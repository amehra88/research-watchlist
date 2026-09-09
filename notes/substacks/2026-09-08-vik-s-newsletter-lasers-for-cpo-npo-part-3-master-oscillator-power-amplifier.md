---
doc_type: substack_post
source: substack
publication: Vik's Newsletter
publication_url: https://www.viksnewsletter.com/
source_email: <20260908031114.3.6d5d15823841200c@mg2.substack.com>
source_sender: Vik's Newsletter <viksnewsletter@substack.com>
source_url: https://open.substack.com/pub/viksnewsletter/p/lasers-for-cponpo-part-3-master-oscillator
source_date: '2026-09-08'
subscription_tier: free_plus_paid
tickers:
- LITE
themes:
- ai_compute_topology
- advanced_materials_ai_infra
ingestion_date: '2026-09-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Lasers for CPO/NPO: Part 3 – Master Oscillator, Power Amplifier](https://substack.com/app-link/post?publication_id=2065897&post_id=214666894&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNDY2Njg5NCwiaWF0IjoxNzg4ODM3MTAxLCJleHAiOjE3OTE0MjkxMDEsImlzcyI6InB1Yi0yMDY1ODk3Iiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.fC5_V84lPRVyV07VItIZ2672OzXn0zqfzbJKuPMpTkU)

### Ultra high power lasers for CPO can be built differently from Lumentum’s approach, but how good are they?

This is the third article in the series on UHP lasers for CPO/NPO. If you want to understand why these external UHP lasers are needed for CPO, see this post for background.

In Part 1 of this series, we built up the fundamental physics of ultra high power (UHP) lasers. We concluded by identifying the four walls that make it challenging to implement a UHP laser: managing heat, maintaining narrow linewidth, getting light out, and catastrophic optical damage.

In Part 2, we explored how Lumentum overcame these challenges via their [2007 paper as JDS Uniphase](https://substack.com/redirect/641486ae-3f40-4fb0-839f-245996a93a98?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and via their later [2022 CLEO paper](https://substack.com/redirect/3c24e7ed-63fe-43c1-8da1-e2302fcd1703?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on UHP lasers. We also looked at how defensible their high power laser platform is.

In Part 3, we will look at the use of a Semiconductor Optical Amplifier (SOA) in conjunction with a lower power laser (~100 mW) to generate UHP laser power levels of ~400 mW. This architecture is called the Master Oscillator (the laser diode), Power Amplifier (or the SOA) approach – aka, MOPA. We will contrast it to the single-cavity UHP laser approach to highlight the pros and cons of each.

Contents:

- The MOPA Concept (free)

- Integrated Semiconductor Optical Amplifiers (SOAs)Operating PrincipleAmplified Spontaneous Emission (ASE)Back Reflection into the SOA

- MOPA High Power LasersSumitomo’s SOA-Integrated DFB LaserNanjing University’s 12-Channel MOPA Array

- Single Cavity vs MOPA: Lumentum vs Sumitomo

- Who is Actually Shipping?

- Which Bet Wins

By reading this post, you agree to the [terms and conditions](https://substack.com/redirect/71204e6c-165a-42fd-85c9-f17c319be954?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Also see the [full ethics statement](https://substack.com/redirect/9d1919ba-4f32-4435-a535-da29cd83947f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

If you’re new, check out the [About page](https://substack.com/redirect/c95ad7d7-ab4b-4717-8fdc-d1c7a0afdc1f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). A lot of readers expense the subscription to this newsletter as it helps their professional work. Group subscriptions (3+) are 20% off. If you have any questions, reply to this email and let me know!

Check out the [Semi Doped podcast](https://substack.com/redirect/4e94aec1-12a1-43ec-9485-8d78e43a0643?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [our daily free newsletter](https://substack.com/redirect/04fa1953-e4ab-4c6e-bba7-df883689c3b0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) with latest semi news. Reach out for institutional research at [SemiExponent](https://substack.com/redirect/f2627b51-9acd-4597-8425-66af8d16ec31?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

# The MOPA Concept

The idea is simple: instead of making a single-cavity high power laser that is prone to issues like spatial hole burning and optical damage like we’ve discussed in previous articles, use a low power seed laser, and then put a power amplifier after it to boost up the power.

Source: Coherent

> Example: A MOPA UHP laser can run the MO at ~100 mW and have the PA multiply that power by a factor of 4x, or 6 dB, to produce a total of ~400 mW at the output.

It is far simpler to make a low power laser with good spectral qualities due to the photon field in the cavity being low. A lot of the issues we discussed earlier in making UHP lasers are greatly mitigated at low laser power. Most laser manufacturers can make them at high yield.

The challenge in MOPA lasers comes from designing a power amplifier (SOA) that is good enough to boost the power to the levels needed for CPO, without degrading the spectral properties of the signal. High power amplification, whether it is radio waves or light, is no laughing matter.

When amplifiers are driven to deliver high power, they unintentionally degrade the quality of light output unless they are designed well. Having two components instead of one introduces other problems: (1) the interface between the two matter, and (2) the combination of the MO and PA should work reliably at high yield over a range of temperatures.

The concept of MOPA amplifiers is not new as they have been widely used in precision cutting, lidar and medical imaging. Those systems use discrete laser and amplifier components, along with isolators, focusing lenses and mirrors. The isolator exists to prevent the reflected light from the input of the PA from affecting the operation of the MO. This is important to remember when we discuss integrated MOPA lasers. Fibers doped with rare earths like Erbium or Ytterbium perform the power amplification, which themselves require pumping with lasers to amplify light. Mirrors and lenses guide the light across the system.

Source: [em-smart.com](https://substack.com/redirect/df00a703-023c-4741-a9bd-4ff0f2dd4915?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Discrete MOPAs are too bulky for use as light sources for CPO. They will need to be integrated into the same InP substrate to deliver a compact light source. We will discuss integrated SOAs next...

## Subscribe to Vik's Newsletter to unlock the rest.

Become a paying subscriber of Vik's Newsletter to get access to this post and other subscriber-only content.

### A subscription gets you:
