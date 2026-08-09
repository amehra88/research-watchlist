---
doc_type: substack_post
source: substack
publication: The Algorithmic Bridge
publication_url: https://www.thealgorithmicbridge.com/
source_email: <20260728185446.3.285e8746bb39bd93@mg-d1.substack.com>
source_sender: Alberto Romero from The Algorithmic Bridge <thealgorithmicbridge@substack.com>
source_url: https://open.substack.com/pub/thealgorithmicbridge/p/the-actual-reason-why-google-fell
source_date: '2026-07-28'
subscription_tier: free_plus_paid
tickers:
- GOOG
- GOOGL
themes:
- frontier_model_competition
- foundation_model_economics
- enterprise_ai_adoption
- agent_framework_landscape
- model_efficiency_evolution
- ai_regulation
ingestion_date: '2026-08-09'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# The Actual Reason Why Google “Fell Out” of the AI Race Changes Everything

Thank you for being a free subscriber. You can [upgrade here](https://substack.com/redirect/0b8d6e67-5180-4c9b-8e26-3bf05495af93?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# [The Actual Reason Why Google “Fell Out” of the AI Race Changes Everything](https://substack.com/app-link/post?publication_id=883883&post_id=208831378&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwODgzMTM3OCwiaWF0IjoxNzg1MjY1MTA2LCJleHAiOjE3ODc4NTcxMDYsImlzcyI6InB1Yi04ODM4ODMiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.edfThLOZiaoezmpgzvgtar3O7W56rKSA0bLIuogyl60)

### Hottest story of the year

Hey, Alberto here! 👋 Each week, I publish long-form AI analysis covering culture, philosophy, and business. Paid subscribers get Monday how-to guides and Friday news commentary. If you’d like to become a paid subscriber, here’s a button for that:

This is a long deep dive (~8,000 words) with a lot of information and many threads to pull on if you're interested. I’d appreciate it if you support this kind of deep research that takes more time and effort than usual.

What if I told you that Google is out of the AI race?

It didn’t happen because Google lost, though. Despite an [underwhelming I/O event](https://substack.com/redirect/3b3af0f0-9b85-4d43-9cc4-2fd326af1458?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) earlier this year, several [heavyweight departures](https://substack.com/redirect/8d3bd001-007f-470e-886c-f0ab25020888?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and a [slower model release pace](https://substack.com/redirect/bc1ff4bb-5f70-46c1-a600-39c3ef068474?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) than its competitors, Google is still alive. It is out of the race because it withdrew. Weird, right? Why would Google do that willingly?

To answer that, I’m going to tell you the story of why and how Google withdrew from the AI race that OpenAI and Anthropic are betting everything on.

Here’s my hypothesis, stated plainly: Google DeepMind CEO Demis Hassabis—a pioneer of AI as we understand it today—doesn’t think that automating AI research with coding agents (AI systems that can program better AI systems) is the correct approach to artificial general intelligence (AGI, the kind of AI that’s as good as humans at everything). Google DeepMind’s leadership sees OpenAI and Anthropic’s bet at best as an off-ramp, and at worst as a dead end.

Hassabis is betting on something else: world models. Models that can understand and simulate the real world, not just predict the next token.

And he’s steering Google accordingly. The AI race is actually a race between two theories of intelligence and also between two kinds of company: startups that need AI to become a business, and an incumbent whose existing business can subsidize AI for years. As we will see, Hassabis’s decision puts Google in a life-or-death situation. He could make Google the absolute leader or an irrelevant laggard.

That said, to write Google off the story would be a serious mistake. I’m going to explain why I think Google has a unique chance here.

You won’t see official confirmation about my hypothesis; as far as the executive is concerned, Google is still competing directly with OpenAI and Anthropic. I contend that’s not quite true anymore. Follow the breadcrumbs with me. I’ll put them together into a coherent picture. The evidence is public, but that doesn’t mean I’m right. This is informed speculation, so please, take it with a grain of salt.

If I manage to change your view of what the hell Google is doing, then I’ll be satisfied with my work.

### I. AS ANTHROPIC AND OPENAI RUSH FORWARD

The first piece of the puzzle is that Anthropic CEO Dario Amodei and OpenAI CEO Sam Altman think that AI models will soon be autonomously improving themselves—this is known as “recursive self-improvement” (RSI): model A makes a better model B that makes a better model C, etc.—and that this is the key to achieving AGI.

The best approach to pursue this goal is also the simplest: build datacenters and use brute force on algorithms that can be scaled that way, like learning and search. That’s the fundamental insight of [Richard Sutton’s Bitter Lesson](https://substack.com/redirect/a9d7d816-1ff0-4069-8b0a-ef16774ddee2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), which both OpenAI and Anthropic hold sacred. If new architectures or algorithms are needed, those better models, equipped with a lot of compute, will find them somehow.

That’s the theory. What does this creed look like inside the lab? We only need to read their testimonies.

You have engineering staff at both companies admitting that they [barely write any code](https://substack.com/redirect/74c5b259-6738-4b18-abe5-ca76575c0237?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) anymore. It is swarms of coding agents—Claude Code and Codex—that do. Employees have become [managers of agents](https://substack.com/redirect/836622ac-732d-4868-9a5b-01d17a12ee4b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) rather than developers and researchers. [Claude Code writes Claude Code](https://substack.com/redirect/140f891e-862a-4ad5-aebf-902c585e4f3c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and [wrote Claude Cowork](https://substack.com/redirect/e94da925-dbcb-4649-805e-395143a9be0c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). GPT-5.6 Sol “[autonomously post-trained](https://substack.com/redirect/1cbb5ad5-432c-4751-b447-d65a68d9322b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)” GPT-5.6 Luna. They say straight away that “[RSI is coming](https://substack.com/redirect/7296ba5f-8fcc-4ede-9dee-ef7ed25e918b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).” Human supervision is still required for many things—we’re in the final moments of the “human-in-the-loop” stage—but one prediction is that by 2028, there’s a [60% chance that RSI is achieved](https://substack.com/redirect/a647ba50-440e-4bae-afbf-117ed3572f6f?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). That’s what Anthropic co-founder Jack Clark wrote in a newsletter in May. [Others predict RSI even sooner](https://substack.com/redirect/15833420-64ea-4abb-b2ef-595649b790aa?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Things are going so fast that Anthropic is in favor of a coordinated slowdown: it’d be “[a good thing](https://substack.com/redirect/74c5b259-6738-4b18-abe5-ca76575c0237?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).” OpenAI staffers, even those who advocate for cautious progress over excessive fear-mongering, are [saying things like](https://substack.com/redirect/c76d4241-f1a9-47fc-8690-5791c9563c20?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): “if we could coordinate a global capabilities slowdown today i would likely press that magic button.”

So what we have here are the two top AI startups deeply convinced on one goal and one trajectory and pushing everything to get there. If I were Google, I’d have to be 100% convinced this isn’t the way. The rate of progress displayed by Anthropic and OpenAI is vertiginous for the world and rather unsettling for their competitors.

Another AI pioneer, [Andrej Karpathy’s decision to join Anthropic](https://substack.com/redirect/73a3f5f2-2043-4d60-9759-d53725695e45?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) earlier this quarter as a “member of technical staff” surprised everyone. “What did Karpathy see?” people asked. Well, he saw the exact same trajectory toward RSI that the labs were seeing. He [joined a team](https://substack.com/redirect/d001b88a-dfdd-478e-acf2-ab7d61027e0c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) tasked with teaching Claude to improve the pre-training phase of the next Claude version. This basically means: making AI’s foundations more robust so that the AI can make the next AI’s foundations more robust, and so on.

Karpathy knew RSI was possible. He had built a miniature version of RSI with his [autoresearch project](https://substack.com/redirect/d98a3467-0948-415c-871b-d9c2c9e6f9f0?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) himself: he discovered that AI agents could autonomously [improve the efficiency of his own code by ~10%](https://substack.com/redirect/6bd13482-64c6-49df-af1d-c2d6ddca2ffb?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). If only this could scale, he wrote, then they’d step into the next stage. Anthropic was a good place to try.

And so he joined Anthropic, a lab with a conviction bordering on religious devotion toward the scaling laws derived from Sutton’s bitter lesson. But what else do you do when you stand on the verge of the exponential, right? You can only embrace it, like one embraces the sublime of a huge mountain or an inexorable hurricane.

Being six years younger than OpenAI, Anthropic had one shot, and they hit the bull’s eye: An unbreakable focus on code + agents + enterprise secured a steady climb to the top. It’s been a crazy streak of successes, from [revenue](https://substack.com/redirect/6a1c5d9b-151c-43e3-97cc-ba1611ff536a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [valuation](https://substack.com/redirect/c53cac8e-cbf2-42bc-82a7-b5a58fffeecc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to [popularity](https://substack.com/redirect/2e642e57-624a-4c25-a9e9-056663b216e2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) to getting ahead of larger and older companies, passing through several [back-and-forths](https://substack.com/redirect/9541feb5-fdc3-49af-8ed7-8991a08a04f6?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) [with the US government](https://substack.com/redirect/02cbab8d-1580-47bd-9943-fe84b1a3d62e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

OpenAI is a different story.

It skyrocketed to fame with ChatGPT, and then it had to deal with the success disaster that followed: [too many expensive free users not willing to pay](https://substack.com/redirect/d70de87c-ab68-47b3-8b6f-ac72627f4abc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). At the time of writing, the revealed preferences of US households indicate that only 2.2% are willing to pay for an AI subscription. Despite that, OpenAI is not behind Anthropic in any relevant metric: they’re essentially tied on [revenue](https://substack.com/redirect/4a00102e-1dea-4370-a2f8-579ce40e8d99?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (run-rate revenue looks better for Anthropic, but it’s not the same as actual revenue), [reach](https://substack.com/redirect/46029ef3-64da-4af8-883f-e1847edd41b4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [ambition](https://substack.com/redirect/4cdb6ec6-bb23-4ed9-a243-b431ed45aea7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Perhaps most importantly, OpenAI fixed its main weakness: [over-diversification](https://substack.com/redirect/023bd007-26e7-49e4-a15c-355236782136?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Earlier this year, Altman cut secondary projects that were taking up invaluable compute resources and distracting from the path of RSI. [As I wrote back then](https://substack.com/redirect/d4198adc-68fa-43c9-b1fa-8674705d908b?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

> OpenAI spent 2025 announcing [Sora](https://substack.com/redirect/b03116bf-701c-4f7f-b514-6d8fa3aca291?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a video generator, [Atlas](https://substack.com/redirect/97ec6259-1407-4dfd-9c45-79c070432b51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), a web browser, a new [device](https://substack.com/redirect/bb81f2b7-35ec-4e49-9126-e99a93026930?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and [e-commerce features](https://substack.com/redirect/550489e2-d69a-49ba-8830-e89fbab943cf?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) for ChatGPT. Altman compared this to “[betting on a series of startups](https://substack.com/redirect/1bf6ef4c-9f98-49df-98aa-83a183f3fa2d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).” I called it “[risky](https://substack.com/redirect/023bd007-26e7-49e4-a15c-355236782136?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).” In March 2026, OpenAI’s CEO of applications, Fidji Simo, told staff they were in “[code red](https://substack.com/redirect/2a290046-b585-4944-8d12-b6f51edca30e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).” (A [second at that](https://substack.com/redirect/894f12b8-138d-4c59-bc97-e4fa96391465?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).) She described Anthropic’s enterprise gains as “[a wake-up call](https://substack.com/redirect/2a290046-b585-4944-8d12-b6f51edca30e?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)” and cancelled all “side quests.” Current and former employees described a period of strategic confusion: mixed teams, unstable compute allocation, a cascade of restructuring decisions...

This move by OpenAI was read by analysts as a push to catch up to [Anthropic’s unmatched revenue figures](https://substack.com/redirect/bee454af-c18a-47c3-91a8-c846adf7dcc1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) on the [enterprise market](https://substack.com/redirect/bce6fc97-3a8d-4149-92af-a93c32f4329a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), but my reading puts revenue in a secondary place. OpenAI will not worry about Anthropic having more revenue than them at any given point—they worry, if anything, about the trajectory.

OpenAI realized that Anthropic was starting to show the signs of acceleration consistent with proto-RSI. They care about money, sure, but Altman wouldn’t make a company-wide restructuring for a short-term trade. This was a full overhaul intended to be a long-term investment. OpenAI can afford to let Anthropic win the enterprise market, but it can’t afford someone else achieving RSI-enabled escape velocity.

OpenAI pivoted fast. It [doubled down on Codex, agents, enterprise](https://substack.com/redirect/a7c8b53b-6bf5-4bb1-84d6-98518e6b4f56?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and, ultimately, on the road to recursive self-improvement. OpenAI is doing so well now that insiders confidently claim that [Codex is actually better than Claude Code](https://substack.com/redirect/b4426519-de1d-4bc5-908a-d54b3a70373c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Codex actually grew well beyond expectations [after the release of ChatGPT Work](https://substack.com/redirect/4e36daeb-cfb7-4cde-9070-b487ef941988?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), and it’s up to 10 million users, as Bloomberg [last reported](https://substack.com/redirect/4e36daeb-cfb7-4cde-9070-b487ef941988?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).

Anthropic’s Fable 5 [is great](https://substack.com/redirect/e5010c1f-3176-4f3d-bf25-c64cea58b043?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) but too expensive—as is Opus 5, [just introduced](https://substack.com/redirect/42fd8420-b6f4-4c38-88ce-a0c589786960?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)—so in terms of cost-performance ratio, which is the most interesting metric right now, [GPT-5.6 Sol seems to be superior](https://substack.com/redirect/ec9b09c0-1599-4e42-a4b8-e43ef60585cc?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). (If you’re wondering what model to use for which task, I wrote [a simple guide for beginners](https://substack.com/redirect/33747b43-babd-45ed-bd68-19497c04d021?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).)

But then next month, people will confidently claim the exact opposite. “We’re so back”; “it’s so over.” Etc. Etc. So who’s winning? I don’t know, I’m not an oracle; I’m just a breadcrumb follower. And the bigger picture reveals that it doesn’t matter whether OpenAI or Anthropic is better off, because during the exponential climb, anything can happen, and what counts is not so much the point as the trajectory.

What I know is that those left out of the first stage of the exponential are out of the game. And as far as we can tell from public information, that would be Google.

Anthropic made this strong claim far back, [in April 2023](https://substack.com/redirect/0ad51a08-2bbf-413d-8a96-656c91b18d1d?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA): “We believe that companies that train the best 2025/26 models will be too far ahead for anyone to catch up in subsequent cycles.” This is what I mean when I say “escape velocity.” It’s the speed you need to escape the gravity field of the planet without falling back to the ground. Once you get there, your next model release is accelerated thanks to the previous model’s involvement in training and post-training. At the time of writing, everything Anthropic and OpenAI argued in 2023-2024 has become true.

All of the above happened—gradually then suddenly—in the first few months of 2026. Where’s Google in this entire story? Can you see them? Yeah, they have Gemini 3 point something. And Antigravity. And something called Omni—more on that later—but they’re essentially nowhere to be found at the frontier of the code + agents + enterprise + RSI race. [Google released its latest model](https://substack.com/redirect/5bea201d-c202-46e5-8a66-a3f01e55a8b1?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)—Gemini Flash 3.6—on July 21, 2026. Here’s where it landed in the [Artificial Analysis intelligence index](https://substack.com/redirect/9dfb331f-90d3-42bd-9d11-f06505cffbc9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

That is an unacceptable score for Google. Something very big must be happening inside the search giant for it to be giving up the good press and the extra revenue of achieving RSI. It can be as big as the corporation falling apart or that it’s setting its sights on a bigger prize.

What can be so big…?...

## Keep reading with a 7-day free trial

Subscribe to The Algorithmic Bridge to keep reading this post and get 7 days of free access to the full post archives.

### A subscription gets you:
