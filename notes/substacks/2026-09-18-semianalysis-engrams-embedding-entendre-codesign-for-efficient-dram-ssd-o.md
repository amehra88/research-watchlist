---
doc_type: substack_post
source: substack
publication: SemiAnalysis
publication_url: https://newsletter.semianalysis.com/
source_email: <20260918143421.3.145e56649b6f3694@mg2.substack.com>
source_sender: SemiAnalysis <semianalysis@substack.com>
source_url: https://open.substack.com/pub/semianalysis/p/engrams-embedding-entendre-codesign
source_date: '2026-09-18'
subscription_tier: paid
tickers:
- NVDA
- AMD
themes:
- hbm_competitive_landscape
- inference_compute_economics
- ai_compute_topology
- model_efficiency_evolution
- silicon_architecture_competition
ingestion_date: '2026-09-19'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# [Engrams Embedding Entendre: Codesign for Efficient DRAM/SSD Offloading](https://substack.com/app-link/post?publication_id=6349492&post_id=215939732&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxNTkzOTczMiwiaWF0IjoxNzg5NzQyMjQxLCJleHAiOjE3OTIzMzQyNDEsImlzcyI6InB1Yi02MzQ5NDkyIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9._YCdha7nW5lWiUi6H8hmfkXXUSqGFm4kohAcnbbC6yU)

### New Model Architecture Implications for TAM of DRAM/NVMe, DeepSeek V4.1 Flash, AgentX, InferenceX, NVMe experiments

Engram extends standard token embeddings with learned multi-token lookups. Recurring local patterns retrieve vectors directly, reducing the need to reconstruct them through attention and feed-forward layers.

With Engram model architecture optimization, it allows for lower HBM capacity to be needed for models at the same quality. [This does not mean there won’t be an insane demand for HBM but it just means that model architecture will continue to innovate around constraints.](https://substack.com/redirect/57469d47-8e13-410e-ba8b-9ac7702488a9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

This model architecture design is naturally codesigned for parameter offloading: each token accesses a few embedding rows whose addresses depend on token IDs, not hidden states. The runtime can prefetch those rows from host DRAM while earlier layers compute, keeping the table outside HBM without transferring entire weight matrices. [Our Memory model contains our latest estimates of quarter by quarter HBM, DRAM, & NAND supply and demand.](https://substack.com/redirect/57469d47-8e13-410e-ba8b-9ac7702488a9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Offloading frees HBM for model weights and KV cache, potentially supporting larger batches or more concurrent sessions. When DRAM becomes the next constraint, NVMe offers another tier. Recommendation systems already cache frequently or recently accessed embedding rows in faster memory while backing colder rows with SSDs. [After NVIDIA roadmap had to change due to massively despec’ing Rubin Ultra from 1024GB to now ~200GB of HBM per chip](https://substack.com/redirect/60b7cbcb-3555-4930-b2d5-8eab08f9eb60?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), model architecture optimizations like emgram maybe helpful.

Our DeepSeek-V4.1-Flash configuration uses roughly 189 GiB of memory for Engram. We replace it with a memory-mapped (mmap) file and measure serving performance with offload to SSD.

Later on in our report, we will show our Engram offloading experiments along with [the official InferenceX agentic inference serving results on Engram models like DeepSeekv4.1 Flash across all 6 NVIDIA GPU SKUs along with MI355X.](https://substack.com/redirect/b7bbf934-a75a-43b8-abdf-4b7be0383eae?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) Unsurprisingly, the CUDA Moat is still mogging MI355X on the ultra popular DeepSeekV4.1 Flash model.

We also show how even on high capacity HBM SKUs, offloading emgrams to DRAM could result in even better performance for most of the pareto than keeping the emgram in HBM.

[Our benchmark has been widely reproduced, validated and/or supported by almost every major buyer](https://substack.com/redirect/8d5a6c23-2a5b-44b2-8aa0-f40aed7e13ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of compute from [Google Cloud](https://substack.com/redirect/956edee0-845f-490a-8cc6-da792ce64659?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [Microsoft Azure](https://substack.com/redirect/8fa876bc-85b8-4997-8f42-9ec60d4ceb2d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [Oracle,](https://substack.com/redirect/8d5a6c23-2a5b-44b2-8aa0-f40aed7e13ad?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [Meta](https://substack.com/redirect/badcfc97-0b64-4fcb-9cef-ef211e35eca1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and many more. Furthermore, it has the [support of the ML community including from vLLM, LMCache, SGLang, PyTorch, Huggingface](https://substack.com/redirect/badcfc97-0b64-4fcb-9cef-ef211e35eca1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and the support of [major labs like OpenAI, MiniMax, ZAI, Qwen, Moonshot Kimi, etc.](https://substack.com/redirect/badcfc97-0b64-4fcb-9cef-ef211e35eca1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

[Star the InferenceX GitHub repository if you find the open-source benchmark and data useful!](https://substack.com/redirect/8c7e4889-4983-43bb-b2de-80b6d0d14b01?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). InferenceX is the only inference benchmark in the world to have TPUv7, Jalapeño, Nvidia Rubin NVL72, AMD, and soon, SambaNova and Trainium. Due to how realistic AgentX scenario is to real world agentic inference workloads, AMD has committed to collaborating on MI455X UALoE72 too.

# Engram Benefits

DeepSeek did not release the original paper’s two trained Engram models. We replicated its setup on fineweb-edu using the released code and training hyperparameters, at an estimated 6E18 FLOPs per run. We observed the same U-shape scaling:

Engram improved performance over pure MoE baselines. We also reproduced DeepSeek’s results, where earlier-layer representations with Engram resembled those of later layers.

# What is Being Memorized?

Like the original Engram paper, it is possible to probe Engram’s gate scores to see what n-grams DeepSeek-V4.1-Flash makes the most use of. Our gate scan finds names, code fragments, relational phrasing, and boilerplate. These examples prioritize interesting-ness over gate strength.

One unexpected result was Wright : Ace Attorney.

These examples suggest learned memory optimizes the training objective, not a judgment of which facts deserve storage. Licenses, bibliography fragments, API scaffolding, and website furniture can provide prediction shortcuts, so the value of additional Engram capacity may depend on what survives data preparation. This does not show that table capacity is “wasted”: the evaluation-corpus scan establishes neither training exposure nor the capacity occupied by each category.

For offloading, strong gates do not identify cache-hot rows. Low gates do not automatically save reads either: computing the gate requires the retrieved key and undoes the performance gain of a fused kernel. Skipping reads would require a separate usefulness predictor before retrieval.

# Removing Engram

In the [original paper’s inference-time ablation](https://substack.com/redirect/42b46ff8-6e99-4342-b1fb-e120a352e66b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), factual-knowledge benchmarks retained just 29–44% of their original performance, while reading comprehension retained 81–93%. This is due to the training–inference mismatch. The resulting degradation therefore measures this trained model’s dependence on Engram, not the performance difference between models trained with and without it.

In our ablations, suppressing Engram worsens token likelihood across all evaluated domains, especially encyclopedia text and several code corpora. Surprisingly, GSM8K accuracy stays within measured run-to-run variation and removing Engram has no effect.

Engram is not a detachable dictionary beside an unchanged MoE. Removing it changes downstream features and expert selection.

We tested whether rerouting hurts or compensates by holding tokens fixed in a teacher-forced experiment on CRUXEval, a code-reasoning benchmark of small Python functions where the model predicts a function’s output from its code and an input, and scoring the reference answer.

Removing Engram raised answer loss from 0.2848 to 0.3093 bits/token. Forcing the ablated model to use the original Engram-on expert choices made it worse still, at 0.3375 bits/token.

Rerouting partially compensates for the missing memory. Memory features and expert selection work together, rather than following a clean “memory stores facts; experts reason” division.

On the same CRUXeval, removing Engram during either phase reduced accuracy and increased generated tokens; removing it throughout produced the largest changes.

Keeping Engram for prefill leads to more correct answers than keeping for decode likely due to semantically richer KV cache transferred to decode workers, allowing it to mitigate some of the performance loss.

# Agentic Inference Serving Performance

Engram’s table is large, but each lookup is small. DeepSeek-V4.1-Flash requests 24 rows at each of two Engram layers, about 12.4 KiB per processed token position across the model, or 3.1 KiB per GPU when split across four GPUs.

Currently as of Day 7 since Model Release, MI355X is still 2-4x worse performance per dollar compared to B200 even when normalized by Mi355X’s lower TCO. [Our full total cost of ownership breakdown comes from our AI Cloud TCO Model along with monthly market surveys of over 100+ gpu clouds & gpu cloud customers.](https://substack.com/redirect/3329b7e3-432e-4fec-8986-2243d1f13929?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

On the Day 0 release of DeepSeekv4.1 Flash, NVIDIA vLLM works out of the box with zero issues across all 6 SKUs: H100, H200, B200, B300, GB200, GB300! This was thanks to the amazing work by the NVIDIA & Interact teams! In comparison, AMD vLLM did not work on day 0 for DeepSeekv4.1 Flash.Source: SemiAnalysis InferenceX

AMD’s vLLM documentation points to using vllm/vllm-openai-rocm:deepseekv41-flash-0909, but from hour 0 of the model release to hour 23, AMD has not publicly released the image. AMD claims, “SPEED IS THE MOAT,” yet it has still not released it by the 23rd hour. We wish that, going forward, the AMD team has a better process for hour 0 model releases.

Eventually when they did publicly release for “day 0” image support, performance-wise, it is currently up to 14.8x worse perf per dollar than H200 and up to 42x worse perf per dollar than B200/B300.

The power of the CUDA MOAT is NVIDIA’s collaboration with its massive 6 million-developer community ecosystem including most of the vLLM & SGLang & Tokenspeed maintainers which means that CUDA is optimized on day 0.

Overall, AMD did make significant improvements but the performance per dollar is still currently 2-4x worse than B200.

## AgentX Engram DRAM Offloading Improving Performance

The HBM and DRAM offload use the same GPU kernel to select and dequantize rows. With HBM, it reads GPU memory; with Unified Virtual Addressing (UVA), it reads pinned host memory directly.

Both support full decode graphs. Moving the table into HBM accelerates only the sparse lookup, leaving decoder computation and communication unchanged, resulting in little overall benefit while consuming memory otherwise available to KV cache.

Another benefit of Engram offloaded to DRAM which means you can reduce the communication overhead by using less HBM GPUs per replica. For example, when enabling Engram offloading on B300, we are able to switch from TP4 to now TP2 which improves the pareto curve by up to 1.6x.

When iso-model quality, less HBM is required as the engrams could be offloaded to host DRAM. Thus HBM bandwidth matters way more than HBM capacity. For inference workloads where memory bandwidth matters the most, 4-hi HBM provides the best $/bandwidth and therefore lowest cost per token. If China continues to make more and more revolutionary model architecture innovations, soon it could potentially 0Hi HBM stacks.

#### [Long Live the Short King: Why 4-hi HBM Wins](https://substack.com/redirect/60327a00-47ac-42ad-a1d1-7cc4635dd22c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

Moreover, on B300 and week-0 stack, moving the Engram table back to HBM did not improve results and stay within run-to-run variance. This is a result of the work optimizing DRAM offload, such as async, and overlap.

## SSD Offloading

On B200, we created a unoptimized vLLM fork and stored the Engram tables in memory-mapped files on local SSDs. File backing lets the OS reclaim table pages when other applications need RAM. Pages already cached in memory can be served without reading the SSD again. Furthermore, note that we were unable to turn on GDS

The unoptimized SSD implementation changes how rows reach the GPU. It copies row IDs to the CPU, deduplicates them, gathers the requested rows into pinned buffers, copies those rows back to the GPU and dequantizes them. This work runs between segments of the GPU execution graph. Native UVA performs row selection and dequantization directly on the GPU, avoiding the CPU round trip.

A warm filesystem cache removes physical SSD reads, but leaves the coordination, row gathering and transfers. This is why a file already cached in RAM can still perform worse than a pinned DRAM table. The comparison measures the whole serving path; it does not separate the time spent on each of these operations.

B200 DRAM dominates both measured SSD serving curves in total tokens per dollar and P90 interactivity. Near 125 tokens/s/user, DRAM delivers 121 million total tokens per dollar versus 52 million for SSD.

For production serving, SSD offloading is likely not worth the tradeoff. On the B200 configurations we measured, SSD offloading loses on both measures: every observed SSD point has a DRAM alternative that delivers higher P90 interactivity and more total tokens per dollar. The only points where

Cheaper storage does not automatically produce a cheaper inference service. Moving Engram to SSD leaves the same four expensive GPUs and the rest of the server in place. Reclaiming RAM only creates an economic benefit if it enables a cheaper server configuration or additional useful capacity. The current unoptimized path provides neither benefit, and the filesystem cache still consumes RAM when table pages are resident.

# Mechanism

Next we will look at the mechanisms and specific implementation of ngrams from DeepSeekv4.1 Flash, LongCat, Qwen3.8 Flash Next...

## Subscribe to SemiAnalysis to unlock the rest.

Become a paying subscriber of SemiAnalysis to get access to this post and other subscriber-only content.

### A subscription gets you:
