# Sourcing filings and calls for non-EDGAR companies (China / India / Taiwan)

Researched 2026-08-10 in response to: *"I want the filings from the local Chinese companies
and their earnings calls. Can we source that? China has an EDGAR-like system."*

Answer: **yes for filings, partly for calls.** Everything below was tested from the droplet,
not assumed.

## Verified identifiers

`FactSet_EntityReference(data_type='entity_reference')` resolves all of them. The suffix
convention is country-based, not exchange-based — this is the thing that trips you up.

| registry id | FactSet id | fsymId | listing |
|---|---|---|---|
| `innolight.cn` | `300308-CN` | 08M33V-E | 300308.SZ Shenzhen |
| `eoptolink.cn` | `300502-CN` | 0C3XFT-E | 300502.SZ Shenzhen |
| `accelink.cn` | `002281-CN` | 081TS2-E | 002281.SZ Shenzhen |
| `hgtech.cn` | `000988-CN` | 0626CY-E | 000988.SZ Shenzhen |
| `mtar.in` | `MTARTECH-IND` | 06ZFQV-E | BSE 543270 / NSE MTARTECH |
| `kaori.tw` | `8996-TW` | 06RF7H-E | 8996 Taiwan |

Formats that DO NOT work: `300308-SZ`, `MTAR-IN`, `MTARTECH-IN`, `MTARTECH-NS`,
`MTARTECH-BO`. India resolves as `-IND` (or the BSE numeric `543270-IN`), China as `-CN`
regardless of Shenzhen/Shanghai.

## Route 1 — CNINFO (巨潮资讯网), China's EDGAR analogue

The CSRC-designated national disclosure platform, covering both Shenzhen and Shanghai.
Reachable from the droplet (HTTP 200). No key required.

**Step 1 — resolve code to orgId:**
```
POST http://www.cninfo.com.cn/new/information/topSearch/query
     keyWord=300308&maxNum=5
  -> [{"code":"300308","orgId":"9900022016","zwjc":"中际旭创",...}]
```

**Step 2 — list announcements:**
```
POST http://www.cninfo.com.cn/new/hisAnnouncement/query
     stock=300308,9900022016     <- MUST be "code,orgId"; code alone returns 0 results
     tabName=fulltext  column=szse  pageSize=30  pageNum=1
     category=category_ndbg_szsh          <- 年度报告 (annual); see codes below
     seDate=2024-01-01~2026-08-10
```

**Step 3 — fetch the PDF:** `http://static.cninfo.com.cn/` + `adjunctUrl`
Verified: Innolight FY2025 annual report = 229-page, 6.1 MB PDF, downloaded successfully.

Useful category codes: `category_ndbg_szsh` 年度报告 (annual) · `category_bndbg_szsh` 半年度报告
(interim) · `category_yjdbg_szsh` 一季报 (Q1) · `category_sjdbg_szsh` 三季报 (Q3) ·
`category_yjygjxz_szsh` 业绩预告 (pre-announcement).

**Caveats:** documents are Chinese-language PDFs (claude -p reads Chinese natively, so this
is a PDF-extraction problem, not a translation one). `www.szse.cn` itself timed out from the
droplet; CNINFO covers Shenzhen disclosure anyway. Rate-limit politely — there is no
published cap and no equivalent of EDGAR's stated 10 req/s.

## Route 2 — FactSet StreetAccount (the higher-value route, already connected)

`FactSet_UnstructuredContent(sources=['ALL_NEWS'], ids=['300308-CN'])` returns Chinese
A-share results **against FactSet consensus**, in English, already structured. Sampled:

- Zhongji Innolight Q1'26: revenue **CNY19.50B vs consensus CNY14.71B** [4 est] — a 33% beat
- Zhongji Innolight H1'25: revenue CNY14.79B +37% y/y; EBIT CNY4.88B **+79%**
- Zhongji Innolight Q3'25: revenue CNY10.22B vs consensus CNY10.75B [5 est]
- Eoptolink H1'25: revenue **CNY10.44B vs CNY2.73B year-ago** (~4x)
- Eoptolink Q3'25: revenue CNY6.07B vs consensus CNY7.41B [2 est]

**These names carry sell-side consensus**, which means beats/misses are measurable — the same
Store B guidance-vs-actual treatment already applied to US names could extend here.

**Why this matters to the thesis:** Chinese transceiver makers growing ~4x y/y and beating
consensus by a third is direct evidence against COHR's `supply_tightness` assumption. That
evidence was reachable from an already-connected tool the whole time.

## Route 3 — earnings calls

**Chinese A-shares: NOT available.** `sources=['ALL_TRANSCRIPTS']` with the correct
`300308-CN` / `300502-CN` identifiers returns zero. This is not an identifier problem — A-share
companies do not hold US-style calls. They hold 业绩说明会 (results briefings), published on
CNINFO's investor-relations platform (`irm.cninfo.com.cn`, reachable) and 上证e互动 for
Shanghai. Sourcing those means scraping those platforms, not FactSet.

**MTAR (India): fully available.** FactSet CallStreet has complete transcripts with Q&A —
Q1 FY26 (2025-08-06), Q2 FY26 (2025-11-06), Q4 FY26 (2026-05-13). Directly on-thesis content
sampled from them:

- *"you've indicated multiple capacity expansions on the hot boxes side ... is the number
  going to be significantly higher than the previously mentioned number of boxes?"*
- *"what will be the peak revenue once we ramp up our hotboxes capacity to 20,000 per annum?"*
- an analyst question built entirely on **Bloom's own** presentation and its 750 TWh
  US power-demand projection

This is the supplier read-through the `mtar.in` registry entry predicted: MTAR's order book and
capacity commentary is an independent window on BE demand that BE's own filings do not provide.

**Kaori (Taiwan):** entity resolves; transcript coverage not yet tested.

## Recommended order of work

1. **FactSet StreetAccount for the six verified T4 names.** No new infrastructure, English,
   structured, and it carries consensus. Highest value per unit of effort by a wide margin.
2. **MTAR transcripts via FactSet** into the corpus as `doc_type='earnings_transcript'` — the
   existing chunker already handles transcripts, including the Q&A speaker/answerer treatment.
3. **CNINFO filing fetcher** — a real build (PDF extraction, Chinese text, no CIK-equivalent
   watermarking). Do it only if 1 and 2 leave a gap worth the effort.
4. **业绩说明会 scraping** — lowest priority, highest effort, least structured.

## Open

- Kaori transcript coverage untested.
- Whether FactSet Fundamentals/Estimates endpoints cover these fsymIds (likely, untested) —
  that would be a cleaner route than parsing CNINFO PDFs for financials.
- Hisense Broadband and Source Photonics remain unverifiable by construction: one is an
  unlisted subsidiary, the other private. Neither will ever have primary disclosure.

---

## PROVEN 2026-08-10: Chinese PDF -> English claims, end to end

Answering *"streetaccount is very surface level ... why don't we use both"* and *"can we get
it in English or translate it"*.

**Use both — they are different instruments.** StreetAccount gives structured results against
consensus (a beat/miss number). CNINFO gives the operating detail behind it. Neither
substitutes for the other.

**No translation step is required.** The CNINFO PDF is TEXT-BASED, not scanned — `pypdf`
pulled 208,079 chars from Innolight's 229-page FY2025 annual report with no OCR. `claude -p`
reads the Chinese directly and emits English, preserving the Chinese source phrase for audit.
CNINFO has no working English portal (`en.cninfo.com.cn` does not resolve), and it does not
matter.

Measured: one 12,000-char slice of the MD&A -> **11 thesis-linked claims for $0.1478**.

### What the depth route surfaced that StreetAccount cannot

| claim (from the Chinese original) | bears on |
|---|---|
| Capacity **+34% YoY to 28.06M units**; production +55% to 23.76M; sales +44% to 21.09M (`产能 2,806万只`) | COHR `supply_tightness` — CHALLENGES |
| Revenue RMB 37.46B **+64%**, gross margin **expanding 34.65% -> 42.61%** | COHR `supply_tightness` — CHALLENGES harder: scaling without buying share on price |
| 1.6T uses a **dual platform: EML AND silicon photonics**; silicon photonics also offered at 800G as an EML alternative | LITE `eml_laser_supply_position` — CHALLENGES |
| First in industry to launch 1.6T-DR8 OSFP224 LPO | COHR `supply_tightness` — CHALLENGES |
| Raw materials are **externally sourced** optical components and IC chips; **no in-house chip/laser claim** | COHR `vertical_integration_moat` — CONFIRMS |
| No major capex expansion projects separately disclosed (`重大投资项目建设情况 不适用`) | COHR `supply_tightness` — mild confirm |

**The methodological point:** one document CHALLENGED one COHR assumption and CONFIRMED
another, in opposite directions, while also hitting LITE. A single "Innolight is a threat"
verdict would have destroyed both signals. This is the payoff from decomposing a score into
separate testable assumptions (docs/thesis-assumptions-draft.md).

**Verification status:** extraction is faithful to the quoted Chinese phrases, which are
carried through for audit. The figures have NOT been independently checked against the
audited statements, and this is a single document from a single year. Treat as a strong lead
to verify, not as established fact.

### Recommended shape

- **StreetAccount** (already connected, no build): quarterly results vs consensus for the six
  verified T4 names. Cheap, structured, English, and these names carry sell-side estimates.
- **CNINFO annual/interim reports** (small build): MD&A + capacity/product sections only, not
  whole documents. ~$0.15 per slice, a handful of slices per report.
- Route the output through `entity_mentions` so claims land beside the US-filing claims and
  carry the same `affects` mapping.

### Still open

- HKEX (`www1.hkexnews.hk`, reachable): Innolight's 2026 Hong Kong listing should produce
  BILINGUAL filings under HKEX rules — English originals, no extraction from Chinese needed.
  Worth checking before building a CNINFO fetcher, since it may supersede it for Innolight.
- Kaori transcript coverage untested.
- FactSet Fundamentals/Estimates coverage for these fsymIds untested — likely a cleaner route
  to financials than parsing PDFs.
