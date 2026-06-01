# OpenAI — private driver profile

- **pvt_id:** `openai.pvt`
- **Display name:** OpenAI
- **Aliases:** OpenAI · OpenAI Foundation · OpenAI OpCo, LLC
- **Added:** 2026-05-10
- **Type:** Standing profile (not an earnings note). Privates have no public filings;
  this dir holds blog/news/conference synthesis and read-through notes.

> Synthesized from existing config only (watchlist `private_drivers`, `web_sources`,
> and `supply-chain-manual.yaml`). No external facts added.

## Why it's tracked

Hyperscaler-equivalent capex behavior. Largest AI inference and training compute
consumer. Custom XPU partnership with AVGO; primary NVDA GPU customer; MSFT Azure
deployment partner; competitive pressure on GOOGL and META.

## Read-through to public names (`affects`)

AVGO · NVDA · MSFT · GOOGL · META

## Supply-chain edges referencing OpenAI

(from `config/supply-chain-manual.yaml`; `source → openai.pvt`)

| Source | Kind | Significance | Note |
|--------|------|-------------|------|
| AVGO | customer | high | Custom inference XPU + networking partnership (announced 2025); multi-year, multi-GW commitment. Read-through to AVGO custom-silicon franchise. |
| NVDA | customer | high | Major GPU customer; direct purchases plus indirect via MSFT; analyst-known beyond 10-K. |
| MSFT | customer | high | OpenAI's primary cloud host; Azure largest committed compute relationship. Partnership exclusivity loosening per 2025 disclosures. |
| GOOGL | customer | medium | Signed Google Cloud capacity (2025) to diversify beyond Azure; notable given GOOGL/OpenAI search + model overlap. |
| DDOG | customer | high | Public case-study customer; analyst-known, not disclosed in 10-K. |

## Web sources

- OpenAI Blog — https://openai.com/blog/ — company_blog, weekly. Product launches,
  model updates. (`affects:` AVGO, NVDA, MSFT, GOOGL, META)
