# RIS4 Phase 0 — smoke test results (2026-09-15 evening ET)

Artifact: https://claude.ai/artifact/TbFXtHkVLWxLSdEGW9c24j (source `portal_build/smoke/`, gitignored).
Opened by the operator in the **iPhone Claude app** (UA `... iPhone OS 18_7 ... Claude/1.260909.19`), viewport 440×820, system light theme.

| probe | result |
|---|---|
| `window.claude` | present |
| capabilities | **db, assets, mcp, sample available**; artifact, downloads, room absent; `user` absent (expected — no per-viewer paths) |
| same-origin `fetch("probe.json")` | **works** (no JSONP fallback needed) |
| `<script src="probe.js">` | works |
| `mcp.listTools()` | 3 servers, display names **"FactSet AI-Ready Data", "InsiderScore", "Gmail"**; `fileArgs: no` → attachments must be inline base64 within the 1 MiB callTool input cap |
| FactSet_GlobalPrices (NVDA-US, 7d) | ok, 6 rows; NOTE the page's `last.price` read `?` — payload row shape differs from the session-side shape; log the raw payload in the real app before writing the formatter |
| InsiderScore get_company_info | ok — name/sector/price returned (use for the name backfill + cheap price header) |
| Gmail send_message | ok, message id returned; arrived in the transcripts INBOX from ashimwork88@gmail.com, subject `PORTAL smoke <ts>` |
| sample quick call | ok, "OK" in 4.4 s; limits: prompt 65,536 B, **tools 16**, images no |
| db set/get | ok (`smoke/latest`, read back from the session via ArtifactData) |
| assets upload (3.5 MB photo) | **unverified** — status stuck at "uploading", asset store empty afterwards; retest with a smaller photo / keep the page open |

## P0.2 — cloud routine + Artifact tool
One-shot routine `trig_013FCcZWhLm8c3g7dPYySz4Q` (Sonnet 5, no repo) ran 6 s and replied
`ARTIFACT_TOOL: available — 2 artifacts listed`. **Routines can publish artifacts.**
→ Daily auto-republish design: droplet builds `portal_build/` → pushes it to a private GitHub
branch/repo (`portal-bundle`) → 07:40 ET routine clones it, `Artifact read` the portal URL, then
publishes with `url=` + files map. No session needed for the daily refresh.

## Consequences for RIS4
- Keep `fetch` for data files; drop the JSONP fallback from the plan.
- Photo/PDF capture: inline base64 ≤ ~700 KB in the Gmail body/attachments; larger → assets (once the upload path is verified) + session pull.
- `sample` page tools: up to 16 per call — Ask-with-retrieval is feasible as designed.
- Operator still to do: Gmail filter `subject:PORTAL` → label `Portal`, skip Inbox (before slice 5).
