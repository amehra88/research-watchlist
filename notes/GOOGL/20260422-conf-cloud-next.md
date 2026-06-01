---
doc_type: conference_transcript
primary_ticker: "GOOGL"
subject_tickers:
  - "GOOGL"
event_date: "2026-04-22"
year: 2026
conference_name: "Google Cloud Next 2026"
ingestion_date: "2026-06-01"
source_origin: youtube_ingest
source_url: "https://www.youtube.com/watch?v=11PBno-cJ1g"
extraction_model: "gemini-2.5-pro"
language: en
---

# GOOGL — Google Cloud Next 2026 (2026-04-22)

_Ingested from YouTube via Gemini 2.5 Pro on 2026-06-01. Source: https://www.youtube.com/watch?v=11PBno-cJ1g_

## 1. Headline read

Google Cloud is aggressively positioning itself as the unified, end-to-end platform for the "Agentic Enterprise." The core announcements center on a massive infrastructure build-out, highlighted by a staggering $175-185B 2026 CapEx forecast from Sundar Pichai, with over half of ML compute allocated to Cloud. The launch of the Gemini Enterprise Agent Platform provides the software layer to manage AI agents at scale, while the new 8th-gen TPUs (8t for training, 8i for inference) and Axion ARM-based CPUs signal a continued push for custom silicon to optimize performance and cost against competitors like NVIDIA. A landmark partnership with Apple to power "Apple Intelligence" with Gemini and a strategic acquisition of security firm Wiz were major leading signals of market penetration and competitive positioning.

## 2. Speakers

- Thomas Kurian — CEO, Google Cloud
- Sundar Pichai — CEO, Google and Alphabet
- Nirmal Saverimuttu — CEO, Virgin Voyages (video)
- Billy Bohan Chinique — VP, Marketing & Digital Innovation, Virgin Voyages (video)
- Sarah Kennedy — VP, Google Cloud (video)
- Michael Santoro — Engineer, Google Cloud (video)
- Katherine Litinsky — Engineer, Google Cloud (video)
- Shaun White — 3x Olympic Gold Medalist & Founder, The Snow League (guest)
- Jason Davenport — Technical Lead, Google Cloud
- Amin Vahdat — SVP, Chief Technologist AI and Infrastructure, Google
- Josh Woods — Chief Technology Officer, Citadel Securities (video)
- Haris Nair — Research Platform Engineering Lead, Citadel Securities (video)
- Kieran Shanahan — EVP & COO, Walmart U.S. (video)
- Angie Brown — EVP and CIO, The Home Depot (video - *Note: The video testimonial was from The Home Depot, but the on-screen customer logo was for Walmart*)
- Leandro Barreto — Chief Marketing Officer, Unilever Beauty & Wellbeing (video)
- Sam Kini — Chief Digital & Technology Officer, Unilever (video)
- Daphne Coates — Global AI Strategy Lead, Unilever (video)
- Erica Chuong — Manager, Applied AI Forward Deployed Engineering, Google Cloud
- Yasmeen Ahmad — Managing Director, Product Management, Data & AI Cloud, Google Cloud
- Francis deSouza — COO, Google Cloud and President, Security Products, Google Cloud
- Yinon Costica — Co-Founder & VP of Product, Wiz
- Carrie Tharp — GTM COO & VP of Customer Experience, Google Cloud
- Patrick Marlow — Senior Product Manager, Applied AI, Google Cloud
- Yulie Kwon Kim — VP of Product, Google Workspace, Google Cloud
- Karthik Narain — Chief Product & Business Officer, Google Cloud

## 3. Product announcements

### Gemini Enterprise Agent Platform
- **Specs/claims:** An end-to-end system for the agentic era. Includes a Low-Code Agent Studio, Agent Registry, Skills and Tools Registry, Agent Gateway for policy management, Agent Observability for tracing, and an Agent Marketplace.
- **Availability:** Not explicitly stated, but components are in Preview or GA.
- **Said by:** Sundar Pichai, Thomas Kurian
- **Strategic framing:** "Mission control for the agentic enterprise." Designed to "build, scale, govern, and optimize" enterprise agents with a full-stack, secure, connective tissue.

### TPU 8t and TPU 8i
- **Specs/claims:** 8th generation TPUs. First dual-chip approach with specialized architectures: TPU 8t for training, TPU 8i for inference.
- **TPU 8t:** "3x performance per pod" over previous generations. "121 exaFLOPS of FP4 compute per pod." Scales to 9,600 TPUs in a 3D torus topology. "2 PB of shared bandwidth memory" in a single superpod. Uses TPUDirect Storage.
- **TPU 8i:** Optimized for inference and reinforcement learning. Integrates a "Collectives Acceleration Engine" (CAE) which reduces latency by an additional 5x. On-silicon memory cache "broke the memory wall". Scales to 1,152 TPUs per pod with "Boardfly Topology".
- **Availability:** Not explicitly stated.
- **Said by:** Amin Vahdat
- **Strategic framing:** A purpose-built foundation for the agentic era, creating an "AI Hypercomputer" where "Compute is the entire datacenter."

### Google Cloud Axion
- **Specs/claims:** Custom-designed ARM-based CPU. "2x price-performance vs x86 instances." "80% better performance per watt than comparable x86 instances."
- **Availability:** Not explicitly stated.
- **Said by:** Amin Vahdat
- **Strategic framing:** Leadership in general-purpose workloads, delivering sustained continuous operation and eliminating cold starts for "always on" agents.

### NVIDIA Vera Rubin NVL72 on Google Cloud
- **Specs/claims:** "Massive exaFLOPS of inference performance per rack."
- **Availability:** Coming Soon.
- **Said by:** Amin Vahdat
- **Strategic framing:** Google will be "among the first" to offer the new NVIDIA platform, reinforcing its role as a key partner and customer for NVIDIA.

### Virgo Network
- **Specs/claims:** Doubles connectivity beyond the superpod. Links 134,000 TPUs with up to 47,000,000 gigabits of non-blocking bandwidth per second, delivering 1.7 exaFLOPS of compute. Scales to 1 million+ TPUs in a single training cluster. "4x the bandwidth per accelerator" over the previous generation.
- **Availability:** Coming Soon. Also announced to be available on NVIDIA Vera Rubin NVL72, supporting up to 960,000 GPUs.
- **Said by:** Amin Vahdat

### Agentic Data Cloud (suite of products/framing)
- **Products:** Knowledge Catalog (Preview), Smart Storage (Coming Soon), Lightning Engine for Apache Spark (GA), Cross-Cloud Lakehouse (Preview).
- **Specs/claims:**
    - **Knowledge Catalog:** "Universal context engine for your enterprise."
    - **Lightning Engine:** "Up to 2x price-performance over the previous market leader" for Apache Spark.
    - **Managed Lustre:** Now supports up to 10TB/s throughput.
- **Availability:** Stated per product.
- **Said by:** Karthik Narain
- **Strategic framing:** "Reasoning without context is just a guess." The Agentic Data Cloud is the engine that provides agents with trusted business context, creating a "truly borderless foundation" where data lives everywhere.

### Gemini Enterprise for Customer Experience (and Workspace Intelligence)
- **Products:** Gemini Enterprise for Customer Experience, Workspace Intelligence (GA).
- **Specs/claims:**
    - **Workspace Intelligence:** A "unified intelligence layer" that connects dots across Workspace apps.
    - **Rapid Enterprise Migration:** "Move to Workspace up to 5x faster" from Microsoft 365.
- **Availability:** Workspace Intelligence is GA.
- **Said by:** Carrie Tharp, Yulie Kwon Kim
- **Strategic framing:** Creating a "coordinated Agentic Taskforce" of specialized agents that operate alongside employees to expand reach, deepen engagement, and personalize service at scale.

## 4. Named customers and partners

| Customer/Partner | Product/Use Case | Speaker | Verbatim notes |
|---|---|---|---|
| ~75% of Google Cloud customers | Google Cloud AI products | Thomas Kurian | "~75% of Google Cloud customers leverage our AI products." |
| Databricks, JetBrains, Replit, Emergent, Figma, monday.com, Shopify | Gemini 3.1 Pro | Thomas Kurian | "Chosen by industry-leading companies." |
| Anthropic | Models on Vertex AI (Claude Opus 4.7) | Thomas Kurian | "We support all the leading models from Anthropic... today we're adding support for Anthropic's Claude Opus 4.7." |
| Apple (AAPL) | Preferred cloud provider for Apple Foundation Models based on Gemini | Thomas Kurian | "We're collaborating with Apple as their preferred cloud provider to develop the next generation of Apple Foundation models... will help power future Apple Intelligence features including a more personalized Siri." |
| Citi Wealth (C) | Gemini Enterprise, DeepMind | Thomas Kurian | Launching "Citi Sky," an "always-on AI-powered member of the Citi Wealth team." |
| Honeywell (HON) | Gemini Enterprise | Thomas Kurian | "Generates 2B actionable insights... by training digital twins on over a million product specifications." |
| Liverpool (retailer) | AI Shopping Assistant | Thomas Kurian | "Projecting a 10x ROI for Liverpool's new AI shopping assistant." |
| NASA | Gemini Enterprise Agents | Thomas Kurian | "...to power flight readiness and astronaut safety for Artemis II." |
| Atlassian, Box, Lovable, Oracle, ServiceNow, Workday | Agent Marketplace in Gemini Enterprise | Thomas Kurian | Listed as partners available in the new marketplace. |
| Virgin Voyages | Gemini Enterprise, Google Distributed Cloud Edge | Nirmal Saverimuttu, Billy Bohan Chinique | Building "Project Rovey" personal concierge. "60% reduction in production timeline" and "28% increase month on month for a record sales quarter." |
| Team USA | Google Cloud AI & Google DeepMind | Sarah Kennedy, Shaun White | Using computer vision and 3D models to analyze athlete performance in snowboarding and skiing for the Winter Olympics. |
| Citadel Securities | TPU 8, TPU Ironwood | Josh Woods, Haris Nair | Using TPUs for research workloads. "Able to run workloads 2-to-4x as fast with a 30% lower cost with TPUs." |
| Walmart (WMT) | Gemini Enterprise, Pixel Fold | Kieran Shanahan | Rolling out Gemini Enterprise on Pixel Fold devices to store and supply chain leaders. |
| The Home Depot (HD) | Gemini Enterprise for Customer Experience | Angie Brown, Jordan Broggi | Powering the "Magic Apron" shopping assistant. "10% increase in comparable sales leveraging digital platforms YOY." |
| Unilever | Gemini Enterprise, ADK (Agent Development Kit) | Leandro Barreto, Sam Kini | Using an "Agentic foundation" for a competitive buying multi-agent solution to make "smarter sourcing decisions." |
| Signal Iduna | Gemini Enterprise | Thomas Kurian | "80% adoption company-wide within weeks." 400% increase in weekly active users. "Providing customers with answers 37% faster." |
| Bosch | Gemini Enterprise | Thomas Kurian | Adopting globally from finance to engineering. |
| KPMG | Gemini Enterprise | Thomas Kurian | "90% adoption of Gemini Enterprise in the first month" with over 100 agents. |
| ASCO | Gemini Enterprise | Thomas Kurian | Providing access to trusted cancer expertise for 50k+ oncology professionals. |
| Merck (MRK) | Gemini Enterprise | Thomas Kurian | Empowering 75k employees worldwide. |
| Wiz | Acquired by Google Cloud | Francis deSouza, Yinon Costica | Integrating with Google Cloud Security to create "Agentic Defense." |
| LADWP | Google Cloud & Wiz | Francis deSouza | "Securing utilities for 4 million residents & businesses in Los Angeles" ahead of LA 2028 games. |
| CSIT Singapore | Google Cloud & Wiz | Francis deSouza | "Enabling proactive defense against advanced digital threats to Singapore." |
| DBS | Google Cloud & Wiz | Francis deSouza | Strengthening security with multi-layered, cloud-native protection. |
| Morgan Stanley (MS) | Google Cloud & Wiz | Francis deSouza | "Extending visibility, control, and security across cloud environments." |
| AXIA Energia | TPU Clusters | Amin Vahdat | Running advanced weather modeling to prevent power outages for 60 million people; reported 15% YoY improvement in extreme weather accuracy. |
| Thinking Machine Labs | NVIDIA-based infrastructure on GCP | Amin Vahdat | Using infrastructure to power "Tinker," an open platform for RL and fine-tuning. |
| Woven by Toyota | Google Cloud AI | Amin Vahdat | Achieved "42% faster visual-language model training to predict complex traffic events." |
| US Department of Energy | Google Cloud | Amin Vahdat | Powering "AI co-scientists across all 17 national labs." |
| Boston Dynamics | AI Hypercomputer | Amin Vahdat | "Training the future of robotics on AI Hypercomputer." |
| Virgin Media O2 | Knowledge Catalog | Karthik Narain | Documented 20k+ data assets with Knowledge Catalog. |
| Palantir, Salesforce, SAP, ServiceNow, Workday | Zero-copy partners | Karthik Narain | Listed as partners for zero-copy data access. |
| Flipkart, Lowe's, Meesho | Lightning Engine for Apache Spark | Karthik Narain | "Accelerating data science workloads with Lightning Engine." |
| Papa Johns | Gemini Enterprise for Customer Experience (Food Ordering Agent) | Carrie Tharp | Building a hyper-personalized ordering system. |
| Best Buy (BBY) | Gemini Enterprise for Customer Experience | Carrie Tharp | "Bringing technical expertise online with Gemini Enterprise for Customer Experience." |
| YouTube TV | Gemini Enterprise for Customer Experience (Voice Agent) | Patrick Marlow | Live voice agent handling customer support for NFL Sunday Ticket and YouTube TV plans. |
| Colgate-Palmolive (CL) | Google Workspace | Yulie Kwon Kim | Rolled out to 34,000 employees. Using AI agents to develop new product concepts "in minutes, not months." |
| Natura | Google Workspace (Gemini Gems) | Yulie Kwon Kim | "10x faster reporting with Gemini Gems." |
| Korean Air | Google Workspace | Yulie Kwon Kim | "22k employees assisted with complex tasks" using AI agents and tools. |
| Compass (COMP) | Google Workspace | Yulie Kwon Kim | "28k+ hours back in 2026 to serve clients" via task management. |
| Reliance | Gemini Enterprise for Customer Experience | Carrie Tharp | Shopping agent driving "7% increase in revenue per session." Analyzes "40M images in minutes." |

## 5. Quantified guidance and TAM claims

- **~$175-185B** — Sundar Pichai — Alphabet's total CapEx forecast for 2026.
- **"nearly 6x increase in just four years"** — Sundar Pichai — Describing CapEx growth from $31B in 2022 to the 2026 forecast.
- **"over half of our machine learning compute is expected to go towards the cloud business"** — Sundar Pichai — Allocation of 2026 ML compute CapEx.
- **~75%** — Thomas Kurian — "of Google Cloud customers leverage our AI products."
- **~75%** — Sundar Pichai — "of all new code at Google is AI generated and approved by engineers," up from 50% last fall.
- **6x** — Sundar Pichai — "We completed the migration 6x faster" (internal code migration using agents).
- **70%** — Sundar Pichai — "70% faster turnaround" for internal marketing campaigns using AI vs non-AI workflows.
- **20%** — Sundar Pichai — "20% increase in conversion" for internal marketing campaigns using AI.
- **90%** — Sundar Pichai — "reduced threat mitigation time by over 90%" for internal security teams using AI.
- **3x** — Amin Vahdat — "3x performance per pod" for the new TPU 8t.
- **9,600** — Amin Vahdat — "scaling up to 9,600 TPUs" per TPU 8t pod.
- **2 PB** — Amin Vahdat — "2 PB of shared bandwidth memory" for TPU 8t.
- **1 million+** — Amin Vahdat — Number of TPUs that can be connected in a single training cluster with the Virgo Network.
- **10x** — Thomas Kurian — "ROI projected for Liverpool's new AI shopping assistant."
- **2B** — Thomas Kurian — Actionable insights generated by Honeywell using Gemini Enterprise.
- **80%** — Thomas Kurian — Adoption of Gemini Enterprise at Signal Iduna "company-wide within weeks."
- **400%** — Thomas Kurian — Increase in weekly active users at Signal Iduna with Gemini Enterprise.
- **37%** — Thomas Kurian — "Signal Iduna is providing customers with answers 37% faster."
- **90%** — Thomas Kurian — Adoption of Gemini Enterprise at KPMG in the first month.
- **10TB/s** — Karthik Narain — Throughput now supported by Google Cloud Managed Lustre.
- **2x** — Karthik Narain — "Up to 2x price-performance" of Lightning Engine for Apache Spark over the market leader.
- **$15 million** — Yasmeen Ahmad — Forecasted revenue for the "Midnight Swirl" product launch, derived in under 5 minutes.
- **-7 days** — Francis deSouza — "The meantime to exploit a vulnerability has dropped to -7 days."
- **22 seconds** — Francis deSouza — The handoff time between initial access and a secondary threat group has dropped from 8 hours to 22 seconds.
- **98%** — Francis deSouza — Accuracy of Dark Web Intelligence in identifying external threats.

## 6. Strategic positioning statements

- "The era of the pilot is over, the era of the agent is here." — Thomas Kurian
- "You cannot deliver AI by piecing together a puzzle piece of fragmented silicon and disconnected models. The answer is a unified stack." — Thomas Kurian
- "AI must be open. While others want to lock you into a walled garden that owns your models, your data, and your agents, we offer you an integrated stack but the freedom to choose." — Thomas Kurian
- "We are firmly in the agentic Gemini era." — Sundar Pichai
- "We are making big investments now and for the future." — Sundar Pichai
- "A big focus for us is to always be customer zero for our own technologies." — Sundar Pichai
- "In the agentic era, compute is no longer defined by a chip. Compute is the entire datacenter." — Amin Vahdat
- "Reasoning without context is just a guess. And when you expect your AI to make decisions and your agents to take actions, you cannot afford to guess." — Karthik Narain
- "We didn't just want to build another platform you have to learn. Instead, the Data Agent Kit integrates... directly into your workflows that you already use." — Karthik Narain
- "Your old Lakehouse expected the analytical engines and the data storage to reside in the same cloud. This approach is broken." — Karthik Narain
- "No more moving data, no more vendor lock-in, just freedom." — Karthik Narain (on Cross-Cloud Lakehouse)
- "You need a cloud that drives itself." — Amin Vahdat

## 7. Cross-ticker implications

- **NVDA (NVIDIA):** Google continues to be a major customer, announcing it will be "among the first" to offer NVIDIA's next-gen Vera Rubin NVL72 platform. This is a positive demand signal. However, Google is also escalating its direct competition with the launch of its 8th-gen TPU 8t (training) and 8i (inference), claiming 3x performance per pod on the 8t. This dual-source strategy (buy and build) keeps NVIDIA on its toes and gives Google negotiating leverage.

- **AMZN (Amazon) / MSFT (Microsoft):** Google's "Agentic Enterprise" narrative and the "Gemini Enterprise Agent Platform" are a direct strategic challenge to Microsoft's Copilot ecosystem and Amazon's Bedrock/agent offerings. The announcement of a "Cross-Cloud Lakehouse" that can reason over data in AWS and Azure without moving it is a significant competitive move aimed at reducing multi-cloud friction and vendor lock-in, potentially making it easier for enterprises to shift workloads to GCP.

- **AAPL (Apple):** The named partnership is a massive strategic win for Google Cloud. Google being the "preferred cloud provider" to power "Apple Intelligence features" with its Gemini models signals deep integration and a significant new revenue stream. This validates Gemini's capabilities at the highest enterprise level and is a major reputational blow to competitors who were likely vying for the same deal.

- **WIZ:** The acquisition and integration of Wiz into Google Cloud Security, forming the "Agentic Defense" pillar, dramatically accelerates Google's security roadmap. It positions them more strongly against Microsoft's Defender and other cloud security platforms, turning Wiz's multi-cloud security context into a competitive advantage for GCP.

- **CRM (Salesforce), NOW (ServiceNow), WDAY (Workday), PLTR (Palantir), SAP:** These companies were named as "zero-copy partners" for the Agentic Data Cloud and as available in the Agent Marketplace. This is a positive signal, indicating Google is pursuing an ecosystem strategy rather than a purely competitive one, aiming to integrate with existing enterprise systems of record. This reduces friction for enterprise adoption of Google's AI agents.

- **SNOW (Snowflake), DDOG (Datadog):** Google's "Agentic Data Cloud" and features like Cross-Cloud Lakehouse, Lightning Engine, and Agent Observability represent a concerted effort to build a more powerful, integrated, and cost-effective native data and observability stack. This intensifies competition for third-party vendors by offering a compelling "good enough" or even superior alternative that is deeply integrated into the core cloud platform.

## 8. Drift signals vs prior coverage

Unable to assess drift — no prior baseline in this ingest context.
