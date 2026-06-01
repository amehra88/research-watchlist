# Anthropic — private driver profile

- **pvt_id:** `anthropic.pvt`
- **Display name:** Anthropic
- **Aliases:** Anthropic · Anthropic PBC
- **Added:** 2026-05-10
- **Type:** Standing profile (not an earnings note). Privates have no public filings;
  this dir holds blog/news/conference synthesis and read-through notes.

> Synthesized from existing config only (watchlist `private_drivers`, `web_sources`,
> and `supply-chain-manual.yaml`). No external facts added.

## Why it's tracked

Hyperscaler-equivalent capex behavior. Strategic AVGO custom-XPU customer; AMZN
Trainium primary deployer; GOOGL TPU competitive proxy.

## Read-through to public names (`affects`)

AVGO · AMZN · GOOGL

## Supply-chain edges referencing Anthropic

(from `config/supply-chain-manual.yaml`; `source → anthropic.pvt`)

| Source | Kind | Significance | Note |
|--------|------|-------------|------|
| AMZN | customer | high | Anthropic's primary cloud + custom-silicon partner; AWS Trainium deployer (Project Rainier). Backed by multi-billion AMZN investment. Read-through to AWS. |
| GOOGL | customer | high | Large Google Cloud TPU customer; Google also a strategic investor. Read-through to GCP + TPU validation. |
| AVGO | customer | medium | Custom-silicon / accelerator partner alongside hyperscaler cloud deals. Read-through to AVGO custom-silicon franchise. |

## Web sources

- Anthropic News — https://www.anthropic.com/news — company_blog, weekly. Product
  launches, capability updates. (`affects:` AVGO, AMZN, GOOGL)
