# AI application-layer screen — 2026-08-20

Automated quarterly run over **every US filer** via EDGAR full-text search — not just the
159 tickers in `config/watchlist.yaml`. Rows marked *tracked* are already on the watchlist.

Interpret with `skills/ai-application-layer-screen/SKILL.md`: apply a size filter and check
for phrase collisions before treating any row as a candidate. The screens deliberately do not
filter — that judgment step is the point.

## Cross-signal — companies clearing more than one screen

Any one screen is weak alone: language can be IR polish, a title can be a
defensive hire, an MCP server can be a side project. Two or three independent
thresholds is a costly, consistent public bet. **Read this section first.**

62 companies clear 2+ screens.

| # | Ticker | Name | Screens cleared | |
|---|---|---|---|---|
| 3 | FDS | FACTSET RESEARCH SYSTEMS INC | MCP / agent-addressable (12); senior AI officer (8); revenue/data language (4) |  |
| 3 | RXRX | RECURSION PHARMACEUTICALS, INC. | senior AI officer (8); revenue/data language (5); MCP / agent-addressable (2) |  |
| 3 | AI | C3.ai, Inc. | senior AI officer (4); revenue/data language (1); MCP / agent-addressable (1) |  |
| 2 | TEAM | Atlassian Corp | MCP / agent-addressable (18); senior AI officer (7) | *tracked* |
| 2 | MORN | Morningstar, Inc. | MCP / agent-addressable (22); senior AI officer (3) |  |
| 2 | SPGI | S&P Global Inc. | senior AI officer (12); MCP / agent-addressable (11) |  |
| 2 | FIG | Figma, Inc. | MCP / agent-addressable (15); revenue/data language (3) |  |
| 2 | MQ | Marqeta, Inc. | MCP / agent-addressable (10); senior AI officer (8) |  |
| 2 | PD | PagerDuty, Inc. | MCP / agent-addressable (15); revenue/data language (1) |  |
| 2 | FSLY | Fastly, Inc. | MCP / agent-addressable (10); revenue/data language (4) |  |
| 2 | UPWK | UPWORK, INC | MCP / agent-addressable (10); senior AI officer (4) |  |
| 2 | NOTE | FiscalNote Holdings, Inc. | MCP / agent-addressable (10); senior AI officer (4) |  |
| 2 | FUSE | Fusemachines Inc. | senior AI officer (8); revenue/data language (5) |  |
| 2 | STGW | Stagwell Inc | senior AI officer (8); revenue/data language (5) |  |
| 2 | INFA | Informatica Inc. | MCP / agent-addressable (11); revenue/data language (2) |  |
| 2 | CRWD | CrowdStrike Holdings, Inc. | MCP / agent-addressable (11); revenue/data language (2) | *tracked* |
| 2 | DOCU | DOCUSIGN, INC. | MCP / agent-addressable (10); revenue/data language (2) |  |
| 2 | CRM | Salesforce, Inc. | MCP / agent-addressable (10); revenue/data language (2) |  |
| 2 | ABSI | Absci Corp | senior AI officer (8); revenue/data language (3) |  |
| 2 | MDB | MongoDB, Inc. | MCP / agent-addressable (10); revenue/data language (1) | *tracked* |
| 2 | CRTO | Criteo S.A. | MCP / agent-addressable (10); revenue/data language (1) |  |
| 2 | AMPL | Amplitude, Inc. | MCP / agent-addressable (10); revenue/data language (1) |  |
| 2 | BRZE | Braze, Inc. | MCP / agent-addressable (10); revenue/data language (1) |  |
| 2 | NTSK | Netskope Inc | MCP / agent-addressable (6); revenue/data language (4) |  |
| 2 | AIOT | Powerfleet, Inc. | senior AI officer (8); revenue/data language (1) |  |
| 2 | CTEV | Claritev Corp | senior AI officer (8); MCP / agent-addressable (1) |  |
| 2 | EXLS | ExlService Holdings, Inc. | senior AI officer (7); MCP / agent-addressable (2) |  |
| 2 | BIGC | Commerce.com, Inc. | MCP / agent-addressable (5); senior AI officer (4) |  |
| 2 | WLY | JOHN WILEY & SONS, INC. | revenue/data language (5); senior AI officer (3) |  |
| 2 | PUBM | PubMatic, Inc. | MCP / agent-addressable (6); revenue/data language (2) |  |
| 2 | S | SentinelOne, Inc. | MCP / agent-addressable (7); revenue/data language (1) |  |
| 2 | NVDA | NVIDIA CORP | revenue/data language (6); MCP / agent-addressable (1) | *tracked* |
| 2 | INOD | INNODATA INC | revenue/data language (6); MCP / agent-addressable (1) |  |
| 2 | ZSQR | Z Squared Inc. | revenue/data language (5); MCP / agent-addressable (2) |  |
| 2 | GEN | Gen Digital Inc. | senior AI officer (4); revenue/data language (3) |  |
| 2 | CLVT | CLARIVATE PLC | MCP / agent-addressable (5); revenue/data language (2) |  |
| 2 | ASAN | Asana, Inc. | MCP / agent-addressable (5); revenue/data language (2) |  |
| 2 | OKTA | Okta, Inc. | MCP / agent-addressable (5); revenue/data language (2) |  |
| 2 | RXT | Rackspace Technology, Inc. | revenue/data language (5); MCP / agent-addressable (1) |  |
| 2 | MIGI | Mawson Infrastructure Group Inc. | senior AI officer (4); revenue/data language (2) |  |
| 2 | SHOP | SHOPIFY INC. | senior AI officer (4); revenue/data language (2) | *tracked* |
| 2 | BLIN | Bridgeline Digital, Inc. | MCP / agent-addressable (5); revenue/data language (1) |  |
| 2 | TRU | TransUnion | MCP / agent-addressable (5); revenue/data language (1) |  |
| 2 | WAY | Waystar Holding Corp. | senior AI officer (3); revenue/data language (2) |  |
| 2 | BLZE | Backblaze, Inc. | senior AI officer (4); MCP / agent-addressable (1) |  |
| 2 | EPAM | EPAM Systems, Inc. | senior AI officer (4); MCP / agent-addressable (1) |  |
| 2 | ZS | Zscaler, Inc. | senior AI officer (4); MCP / agent-addressable (1) | *tracked* |
| 2 | MARA | MARA Holdings, Inc. | senior AI officer (3); MCP / agent-addressable (2) |  |
| 2 | WDAY | Workday, Inc. | senior AI officer (3); MCP / agent-addressable (2) |  |
| 2 | BFRG | BullFrog AI Holdings, Inc. | revenue/data language (2); MCP / agent-addressable (2) |  |


> **Note on the language-screen diff below.** Cost-side phrases ("inference costs", "cost of
> AI") were removed from the screen this run. The 15 "dropped" names are a **methodology
> change, not a signal** — they qualified only on cost language. Worth knowing which ones:
> ALGN and TTAN were riding on it, which further weakens the ALGN case. Real quarter-over-
> quarter diffs begin with the 2026-11-01 run.

## edgar_ai_language_screen

`edgar_ai_language_screen_20260819.json` → `edgar_ai_language_screen_20260820.json`

209 → 194 filers | **0 new** | 0 increased | 15 dropped

### Dropped (15)

AGYS, ALGN, DOCS, IOT, LSCC, LVO, MOVE, MRVL, MSFT, PODC, POWI, SES, TDC, TTAN, VERI


## edgar_ai_officer_screen

`edgar_ai_officer_screen_20260819.json` → `edgar_ai_officer_screen_20260820.json`

115 → 115 filers | **0 new** | 0 increased | 0 dropped


## edgar_mcp_screen

First run (`edgar_mcp_screen_20260820.json`) — no baseline yet, so this is the current standing list, not a diff. 133 companies (137 filing rows).

| Score | Ticker | Name | Phrases | |
|---|---|---|---|---|
| 22 | MORN | Morningstar, Inc. | Model Context Protocol; MCP server; MCP servers |  |
| 22 | FROG | JFrog Ltd | Model Context Protocol; MCP server; MCP servers | *tracked* |
| 18 | TEAM | Atlassian Corp | Model Context Protocol; MCP server; our MCP | *tracked* |
| 15 | PD | PagerDuty, Inc. | Model Context Protocol; MCP server; our MCP |  |
| 15 | FIG | Figma, Inc. | Model Context Protocol; MCP server; our MCP |  |
| 15 | SST | System1, Inc. | Model Context Protocol; MCP server; MCP servers |  |
| 14 | UDMY | Udemy, Inc. | Model Context Protocol; MCP server; our MCP |  |
| 14 | V | VISA INC. | Model Context Protocol; MCP server; our MCP |  |
| 14 | KVYO | Klaviyo, Inc. | Model Context Protocol; MCP server; our MCP |  |
| 12 | FDS | FACTSET RESEARCH SYSTEMS INC | Model Context Protocol; MCP server; AI-ready data |  |
| 12 | NTAP | NetApp, Inc. | Model Context Protocol; MCP server; AI-ready data |  |
| 11 | INFA | Informatica Inc. | MCP server; agent-ready; AI-ready data |  |
| 11 | SPGI | S&P Global Inc. | MCP servers; agent-ready; AI-ready data |  |
| 11 | FITB | FIFTH THIRD BANCORP | Model Context Protocol; MCP server; agentic workflows |  |
| 11 | CRWD | CrowdStrike Holdings, Inc. | Model Context Protocol; MCP servers; agentic workflows | *tracked* |
| 11 | INUV | Inuvo, Inc. | Model Context Protocol; MCP server; agentic workflows |  |
| 10 | CRM | Salesforce, Inc. | Model Context Protocol; agent-ready; AI-ready data |  |
| 10 | TDC | TERADATA CORP /DE/ | MCP server; our MCP; agentic workflows |  |
| 10 | AMPL | Amplitude, Inc. | Model Context Protocol; MCP server |  |
| 10 | DOCU | DOCUSIGN, INC. | Model Context Protocol; MCP server |  |
| 10 | BOX | BOX INC | Model Context Protocol; MCP server |  |
| 10 | MQ | Marqeta, Inc. | Model Context Protocol; MCP servers |  |
| 10 | ADSK | Autodesk, Inc. | Model Context Protocol; MCP servers |  |
| 10 | NOTE | FiscalNote Holdings, Inc. | Model Context Protocol; MCP server |  |
| 10 | BRZE | Braze, Inc. | Model Context Protocol; MCP server |  |
| 10 | CRTO | Criteo S.A. | Model Context Protocol; MCP server |  |
| 10 | MRSH | MARSH & MCLENNAN COMPANIES, INC. | Model Context Protocol; MCP servers |  |
| 10 | DHX | DHI GROUP, INC. | Model Context Protocol; MCP server |  |
| 10 | SNOW | Snowflake Inc. | Model Context Protocol; MCP server | *tracked* |
| 10 | PSTG | Pure Storage, Inc. | Model Context Protocol; MCP servers |  |
| 10 | BKKT | Bakkt, Inc. | Model Context Protocol; MCP server |  |
| 10 | FSLY | Fastly, Inc. | Model Context Protocol; MCP server |  |
| 10 | SILO | Silo Pharma, Inc. | Model Context Protocol; MCP server |  |
| 10 | DT | Dynatrace, Inc. | Model Context Protocol; MCP server |  |
| 10 | UPWK | UPWORK, INC | Model Context Protocol; MCP server |  |
| 10 | MDB | MongoDB, Inc. | Model Context Protocol; MCP server | *tracked* |
| 10 | NABL | N-able, Inc. | Model Context Protocol; MCP server |  |
| 10 | YEXT | Yext, Inc. | Model Context Protocol; MCP servers |  |
| 9 | BAND | Bandwidth Inc. | Model Context Protocol; our MCP |  |
| 7 | S | SentinelOne, Inc. | Model Context Protocol; AI-ready data |  |

