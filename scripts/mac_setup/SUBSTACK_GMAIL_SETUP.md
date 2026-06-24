# Substack → Gmail setup (one-time, operator-facing)

This wires Substack newsletters into the v3 ingestion pipeline. Newsletters land in
`ashimmehratranscripts@gmail.com`, a Gmail filter routes them to a **`Substack`
label** (and **skips the inbox**), and the droplet's daily `substacks.py` job
(06:00 ET) reads that label, synthesizes each post into `notes/substacks/`, and
ingests it into the pg corpus.

> **Why the label matters.** The existing transcript poller scans **INBOX `UNSEEN`**
> and marks everything Seen with no sender filter. If Substack mail hit the inbox it
> would be consumed before `substacks.py` saw it. **Skipping the inbox** (label only)
> keeps the two channels from colliding. This is non-negotiable — set "Skip the Inbox".

---

## 1. Log in
Open Gmail on the web as **ashimmehratranscripts@gmail.com**.

## 2. Create the label
Settings (gear) → **See all settings** → **Labels** → **Create new label** → name it
exactly **`Substack`** → Create.

## 3. Create the filter
Settings → **Filters and Blocked Addresses** → **Create a new filter**.

Most publications are Substack-hosted and send from `@substack.com` even when they
have a custom website domain — but a few send from their own domain (Stratechery via
Passport → `stratechery.com`; The Rundown AI via beehiiv → `therundown.ai`; Police
Briefing → `policebriefing.com`). So the filter matches a **list of sender domains**.

In the filter's **From** field, paste this exact string:

```
from:(substack.com OR stratechery.com OR therundown.ai OR policebriefing.com OR netinterest.co OR thediff.co OR notboring.co OR bitsaboutmoney.com OR generalist.com OR semianalysis.com OR viksnewsletter.com OR fabricatedknowledge.com OR ai-supremacy.com OR thealgorithmicbridge.com)
```

Click **Create filter**, then on the next panel check:
- ☑ **Skip the Inbox (Archive it)**  ← required (collision avoidance)
- ☑ **Apply the label:** `Substack`
- ☑ **Also apply filter to matching conversations** (catches anything already arrived)
- ☐ Mark as read — **leave UNchecked** (the pipeline doesn't use the read flag; keeping
  posts unread gives you a visual count of what's pending in the label)
- (optional) ☑ Mark as important

Click **Create filter**.

> **`substack.com` covers the majority** (any `<pub>@substack.com` sender). The extra
> domains are belt-and-suspenders for the self-hosted/custom-domain senders. If you
> later add a publication that sends from a brand-new domain, just **edit this filter**
> and add ` OR newdomain.com` inside the parentheses — no code change needed.

## 4. Verify
Two options:
- **Wait for the first delivery** — after you subscribe (step 5), the next newsletter
  should arrive already labeled `Substack` and NOT in the inbox. Open the `Substack`
  label in the left sidebar to confirm.
- **Self-test** — from another account, send a mail to the research Gmail with any
  `@substack.com` address in the From display, or temporarily add your own domain to
  the filter; confirm it lands under the label, not the inbox. Remove the test clause
  after.

If a publication you subscribed to is **not** getting labeled, check which address it
actually sends from (open the email → "show original" → `From:`) and add that domain
to the filter's From parentheses.

---

## 5. Subscriptions to set up (operator action)

Subscribe to each of these **using `ashimmehratranscripts@gmail.com`**. Source of
truth + per-publication metadata: `config/substack_subscriptions.yaml`.

| # | Publication | URL | Tier | Action |
|---|---|---|---|---|
| 1 | AI: Reset to Zero | michaelparekh.substack.com | free | subscribe |
| 2 | **Stratechery** | stratechery.com | paid | **DECISION** ↓ |
| 3 | **Sharp Tech** | stratechery.com/company/sharp-tech | paid | bundled w/ Stratechery ↓ |
| 4 | Net Interest | netinterest.co | free+paid | subscribe (free) |
| 5 | The Diff | thediff.co | free+paid | subscribe (free) |
| 6 | ~~Doomberg~~ | doomberg.substack.com | paid | **SKIP** (not subscribed) |
| 7 | Not Boring | notboring.co | free | subscribe |
| 8 | Bits about Money | bitsaboutmoney.com | free | subscribe |
| 9 | The Generalist | generalist.com | free+paid | subscribe (free) |
| 10 | **SemiAnalysis** | newsletter.semianalysis.com | paid $500/yr | **DECISION** ↓ |
| 11 | Fabricated Knowledge | fabricatedknowledge.com | free+paid | subscribe (free) |
| 12 | Nutty | nuttycld.substack.com | free+paid | subscribe (free) |
| 13 | Vik's Newsletter | viksnewsletter.com | free+paid | subscribe (free) |
| 14 | Elevator Pitches | elevatorpitches.substack.com | free+paid | subscribe (free) |
| 15 | ML Liebreich (Chairman Michael) | mliebreich.substack.com | free+paid | subscribe (free) |
| 16 | Nate's Substack | natesnewsletter.substack.com | free+paid | subscribe (free) |
| 17 | The Rundown AI | therundown.ai | free | subscribe |
| 18 | AI Supremacy | ai-supremacy.com | free+paid | subscribe (free) |
| 19 | The Algorithmic Bridge | thealgorithmicbridge.com | free+paid | subscribe (free) |
| 20 | Police Briefing | policebriefing.com | unknown | subscribe; confirm sender domain |

### Three decisions needed
- **#2/#3 Stratechery + Sharp Tech (paid, self-hosted via Passport, from `stratechery.com`).**
  You already pay under a different email. Pick one: (a) migrate the Stratechery
  account email to `ashimmehratranscripts@gmail.com`; (b) set up forwarding of
  Stratechery mail to it; or (c) use the limited free tier. Until then these two
  won't flow. (Sharp Tech is mostly a podcast — its email may be show-notes only.)
- **#10 SemiAnalysis (paid ~$500/yr).** Highest-signal semis source. Pay for full
  access, or subscribe free-tier-only? The pipeline works either way; paid = more posts.
- **#6 Doomberg — confirmed SKIP** (paid, not held). Left in config, not subscribed.

Everything else is free — subscribe with the research Gmail and you're done.
