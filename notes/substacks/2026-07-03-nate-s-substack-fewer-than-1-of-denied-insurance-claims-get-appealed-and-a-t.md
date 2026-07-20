---
doc_type: substack_post
source: substack
publication: Nate's Substack
publication_url: https://natesnewsletter.substack.com/
source_email: <20260703130355.3.a7f901a662094d08@mg-d0.substack.com>
source_sender: Nate from Nate’s Substack <natesnewsletter@substack.com>
source_url: https://open.substack.com/pub/natesnewsletter/p/reusable-ai-agent
source_date: '2026-07-03'
subscription_tier: free_plus_paid
tickers: []
themes:
- ai_agent_monetization
- enterprise_ai_adoption
- vertical_ai_applications
ingestion_date: '2026-07-13'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Fewer than 1% of denied insurance claims get appealed, and a third to half of appeals win. Build the AI rig that t…

Get the full post and max your AI career leverage, plus connect with tens of thousands of paid subscribers in Nate’s Substack chat.

# [Fewer than 1% of denied insurance claims get appealed, and a third to half of appeals win. Build the AI rig that turns your denial and tax pile into cited packets — it drafts, never sends.](https://substack.com/app-link/post?publication_id=1373231&post_id=204778530&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNDc3ODUzMCwiaWF0IjoxNzgzMDg4MDU3LCJleHAiOjE3ODU2ODAwNTcsImlzcyI6InB1Yi0xMzczMjMxIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.1cWARVxpXQYA3aN9vTedQVFet4YxdOF5Xrz-RWv8w3I)

### Anywhere you have sensitive, unorganized documents and a decision that matters, this pattern works: structure the pile, cite everything, export a reviewable packet, stop before sending.

Your unopened tax folder and your unappealed insurance denial are the same problem wearing different paperwork. The other side has structure — policy language, denial codes, forms, deadlines — and you have a pile.

KFF, an independent health-policy research nonprofit, has the clearest picture of how lopsided the fight is. Of roughly 85 million denied in-network claims in Affordable Care Act marketplace plans in 2024, consumers appealed fewer than one percent. When people do appeal, they win far more often than the silence suggests. Insurers reverse about a third of internal denials on their own, and if you push past them to an independent external reviewer, the number climbs toward half. In prior authorization it runs past eighty percent.

Most denials stick because almost nobody files, not because insurers are usually right. And the insurer’s side of the fight is increasingly automated. A 2024 Senate Permanent Subcommittee on Investigations report found the largest Medicare Advantage insurers leaned on algorithmic tools as their post-acute-care denial rates climbed. UnitedHealthcare’s rate more than doubled in two years. Structure plus automation, against a pile.

You already use AI every day, and it still hasn’t touched this. Almost everyone stops at the email agent. It works, it feels good, and the next real problem looks like starting from scratch: new tool, new setup, new trust questions. So the ambition dies in the inbox while the folders that cost real money stay closed.

The fix is a different standard for what you build. Every agent you build should make your next agent cheaper to build. If that is not happening, you are not building a system. You are collecting chores that happen to run on AI, and each one will rot on its own schedule.

This piece builds the alternative: one reusable rig — the working setup you assemble once, tune with use, and point at job after job — aimed at three problems in sequence: a scheduling thread, a denied insurance claim, and a year of tax prep. The rig runs the same nine stages every time, from deciding what the agent is allowed to read to the hard stop where it hands the work back to you. Between one build and the next, only the nouns change: what goes into the context pack, and what the packet at the end looks like. Everything else transfers. By the third build, the setup takes a fraction of the effort of the first, and that ratio keeps improving, because every component gets sharper with use.

Insurance and taxes are the proof runs, not the limits. Once you have watched the rig run three times, you will recognize the same shape in a dozen other problems: anywhere life hands you sensitive documents, no structure, and a decision that matters. I will come back to that list near the end, because it is the real payoff of building this way.

One rule governs everything that follows. The agent drafts and organizes only. It never sends, files, submits, pays, or signs. That boundary is the reason the system can be pointed at money and health at all, not a legal disclaimer bolted onto a capable system. By the end of this piece, you will see why the builds get more valuable, not less, because of it.

Here’s what’s inside:

- The rig, stage by stage. Nine steps with the reasoning behind each, including why this build deliberately skips vector search, and the legal detail about denial letters that makes deterministic retrieval the right call.

- Three builds, one rig. Email and calendar as the training run, then the insurance appeal packet, then the tax-year packet, with the context packs and export templates for each.

- The flywheel mechanics. Exactly which components transfer between builds, which get sharper with use, and why the third build costs a fraction of the first.

- Two agents plus the skills they run on. The Healthcare Claim Appeals Agent and the Tax Prep Organizer Agent, with the Context Engineering and Runbooks Open Skills underneath, each ready to copy with its own setup prompt.

The rig gets assembled once on email, where nothing goes wrong, and from there the exact same machinery takes on the denial and the tax year. What you walk away with is the copy-paste version: two finished agents and the skills under them, ready for whatever pile is costing you the most.

## Watch with a 7-day free trial

Subscribe to Nate’s Substack to watch this video and get 7 days of free access to the full post archives.

### A subscription gets you:
