---
doc_type: substack_post
source: substack
publication: Vik's Newsletter
publication_url: https://www.viksnewsletter.com/
source_email: <20260722131445.3.5c1bf6287b2c6efb@mg-d1.substack.com>
source_sender: Vik's Newsletter <viksnewsletter@substack.com>
source_url: https://open.substack.com/pub/viksnewsletter/p/lasers-for-cponpo-part-2-lumentums-tech-and-moat
source_date: '2026-07-22'
subscription_tier: free_plus_paid
tickers:
- LITE
themes:
- ai_compute_topology
- networking_competitive_landscape
ingestion_date: '2026-07-27'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Lasers for CPO/NPO: Part 2 – Lumentum’s Technology and Moat](https://substack.com/app-link/post?publication_id=2065897&post_id=208019065&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwODAxOTA2NSwiaWF0IjoxNzg0NzI2NjM0LCJleHAiOjE3ODczMTg2MzQsImlzcyI6InB1Yi0yMDY1ODk3Iiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.x8KJSnUgcjM9bU3pzuCAtj2DrG7HdYzniweYqvjLV4w)

### How JDSU/Lumentum engineered their UHP laser, where the competition stands, and how it's all about "is it good enough?"

In this series on UHP lasers for CPO/NPO, our purpose is to carefully dissect the technology to understand how it works, where the engineering difficulty lies, what architectural options exist, and deeply understand where the technology differentiation and moat actually lies for key industry players. If you want to understand why these external lasers are needed, see this earlier post.

In Part 1 of this series, we built up the fundamental physics of ultra high power (UHP) lasers. We concluded by identifying the four walls that make it challenging to implement a UHP laser: managing heat, maintaining narrow linewidth, getting light out, and catastrophic optical damage.

In Part 2, we will explore exactly how Lumentum overcame these challenges via their [2007 paper as JDS Uniphase](https://substack.com/redirect/e710b348-b420-438d-a05c-49c49efe759d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and via their later [2022 CLEO paper](https://substack.com/redirect/f60cf776-ada4-42ec-ba8b-b559c93d5638?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on UHP lasers. We will touch on reliability and single mode operation, and dig into how defensible their UHP laser platform is, including what it means for the competition.

Contents:

- Suppressing Re-Broadening for sub-MHz Linewidth: How to choose the key design parameter that makes UHP lasers work

- Precisely Engineering the Cavity Length: Are longer lasers necessarily worse? How do laser designers choose the laser cavity length?

- Pros and Cons for Longer Cavity Length: What does cavity length help with, and what it means for reliability and mode-stability

- The Moat isn’t the UHP Laser design: The engineering mindset is to out-design the competition in UHP lasers, but reality is different: is it good enough?

By reading this post, you agree to the [terms and conditions](https://substack.com/redirect/e5275273-9862-4405-9d5a-5dab7c3b5d56?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Also see the [full ethics statement](https://substack.com/redirect/590e55de-bbb7-4a47-99f3-b1397a33b7a9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

If you’re new, check out the [About page](https://substack.com/redirect/96879240-d805-4685-abe5-a9062fbae903?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). A lot of readers expense the subscription to this newsletter as it helps their professional work. Group subscriptions (3+) are 20% off. If you have any questions, reply to this email and let me know!

If you are not a paid subscriber, you can purchase just this article using the button below. You can find the whole catalog of articles for purchase [at this link](https://substack.com/redirect/56cc3244-a3b1-40d4-acfe-3907fa5d265a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

[Buy the ebook](https://substack.com/redirect/be842a4f-44e5-40d7-9b33-356c3c07ce59?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Also check out the [Semi Doped podcast](https://substack.com/redirect/caf295cc-9632-4cdc-a2be-ded5c3e919c2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) with [Austin Lyons](https://open.substack.com/users/8066776-austin-lyons?utm_source=mentions) and myself, and [our daily free newsletter](https://substack.com/redirect/f4356114-6468-4598-92d8-824afe9e6360?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) with latest semi news.

If you would like to engage independent research services for your project or need expert calls, check out my boutique consulting practice at [SemiExponent](https://substack.com/redirect/724dd8e5-362a-469a-8b03-048877e40a43?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

### Suppressing Re-Broadening for sub-MHz Linewidth

Even in 2007, Lumentum (then JDSU) realized that increasing the output power of a DFB past a few 10s of milliwatts resulted in the laser linewidth getting broader than 1 MHz even if the “Schawlow-Townes-Henry” equation predicts that it should get narrower as the laser power is increased (explained in part 1). Good lasers should have narrow linewidth because the transmission of an optical pulse on an optical fiber broadens the pulse anyway; no need to have that problem at the source.

Pulse broadens as power gets higher. Source: Gemini, for conceptual purposes only.

They explain that there were two things causing this:

- With so much optical power in the laser, photons are not distributed uniformly in the physical structure under the DFB grating. We explained this effect as spatial hole burning in part 1. This non-uniformity also causes a non-uniform refractive index, which in turn makes the linewidth broaden.

- Within the InP multiple quantum well (MQW, where electricity is converted to light), there are random charge recombinations always occurring. This added to the “phase noise” of the system and also caused linewidth to broaden.

The former mechanism was more dominant, but the latter is significant enough to not be ignored. It was already known through other published work at the time that the easiest way to avoid re-broadening is to make the cavity length (L) longer. This generally helps distribute the photons in the cavity more evenly and keep the refractive index as even as possible under the DFB grating.

But it is not quite as simple as just increasing length because how evenly the photons are distributed depends on the DFB grating design. In part 1, we explained how there is a quantity κ – the grating’s reflection strength per unit length – combined with the length of cavity L, determines how evenly the photons are distributed.

As a recap from part 1:

> κL is the key knob that decides how light is distributed along the chip.If the κL is too low, then light spreads out and leaks towards the ends. Insufficient feedback to hold the light in the channel evenly, and wavelength selection is weak.If κL is too high, then light gets trapped and piles up in the middle of the chip and causes spatial hole burning.

Engineering the right UHP laser now came down to picking the right cavity length L, for a given grating reflection strength κ set by the grating design. There is a goldilocks range for κL where the photon field was the flattest – which JDSU determined to be 0.7. Look at the pink lines in the graphs below, for different phases of the optical signal. κL=0.7 provides a flatness over nearly 200 degrees of phase – much better than κL=0.5 or κL=1.

### Precisely Engineering the Cavity Length

Now that κL is set, the crux of the problem is that both κ and L are design parameters that can be chosen to keep κL=0.7. How do we choose?...

## Continue reading this post for free in the Substack app
