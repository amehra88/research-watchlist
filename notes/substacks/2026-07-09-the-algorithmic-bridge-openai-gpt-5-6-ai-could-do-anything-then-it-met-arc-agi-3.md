---
doc_type: substack_post
source: substack
publication: The Algorithmic Bridge
publication_url: https://www.thealgorithmicbridge.com/
source_email: <20260709204603.3.0a7f6146a5303a58@mg-d1.substack.com>
source_sender: Alberto Romero from The Algorithmic Bridge <thealgorithmicbridge@substack.com>
source_url: https://open.substack.com/pub/thealgorithmicbridge/p/openai-gpt-56-ai-could-do-anything
source_date: '2026-07-09'
subscription_tier: free_plus_paid
tickers: []
themes:
- frontier_model_competition
- model_efficiency_evolution
ingestion_date: '2026-07-13'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# OpenAI GPT-5.6: AI Could Do Anything, Then It Met ARC-AGI-3

Thank you for being a free subscriber. You can [upgrade here](https://substack.com/redirect/b9411c9a-03f2-4cc2-bb5a-71298e0b6c70?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# [OpenAI GPT-5.6: AI Could Do Anything, Then It Met ARC-AGI-3](https://substack.com/app-link/post?publication_id=883883&post_id=206353207&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNjM1MzIwNywiaWF0IjoxNzgzNjMwMDA2LCJleHAiOjE3ODYyMjIwMDYsImlzcyI6InB1Yi04ODM4ODMiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.d6dFcwkFaWyau6RNBzjkOFJvKo-6pTGvxnadqqHKVnU)

### GPT-5.6’s ARC-AGI-3 score is scandalously bad and scandalously good

Hey, Alberto here! 👋 Each week, I publish long-form AI analysis covering culture, philosophy, and business. Paid subscribers get Monday how-to guides and Friday news commentary. If you’d like to become a paid subscriber, here’s a button for that:

[GPT-5.6 is here](https://substack.com/redirect/584e89a5-e247-439f-ba98-be3d789312d8?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) and OpenAI’s cheerleaders have already treated us to their recitals about how incredible it is. I believe them: every new model from Anthropic and OpenAI is incredible at this point. Refuting an Erdős conjecture—and soon, perhaps, hopefully, solving a Millennium Prize Problem—is a piece of cake to them. There are some gaps when it comes to the reliability of this technology, but on agentic tasks and code, these models are fantastic. (Read GPT-5.6’s system card [here](https://substack.com/redirect/5de85917-aaf6-4373-9ede-4eb9776590c9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).)

I’m here today to reframe this undeniable fact with a result that usually goes unnoticed by the faithful chorus. One that is, at the same time, incredible for being good and incredible for being bad.

I’m referring to GPT-5.6’s score on the benchmark known as ARC-AGI-3—a personal favorite of mine—which amounts to [the scandalous figure of 7.8%](https://substack.com/redirect/c39db953-f5a9-4b62-9f4d-3a643e42a30c?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). (From here on, I only refer to GPT-5.6 Sol, the biggest of the three versions of this model, which include Terra and Luna; Read the full blog post on ARC-AGI-3 [here](https://substack.com/redirect/126d6106-59ce-4b5b-9a89-a1e16bdf0816?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA).)

It’s scandalous for three reasons.

First, because it is not, in fact, scandalous at all. ARC-AGI-3 is a benchmark designed to look easy to the human eye while requiring a type of intelligence—”fluid, not crystallized,” as its creator, François Chollet, likes to put it—that AI struggles with. If you try it yourself, it might take a little while to get the hang of it, but soon enough you start to grasp the idea of each game, the patterns of colors and movements, etc. That’s why 7.8% is terribly low; humans reliably score >90%.

How is it possible that an AI model capable of training another AI by itself—[OpenAI said in its livestream](https://substack.com/redirect/5aa31617-a0d2-43ab-8a33-22a3f8152773?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that GPT-5.6 Sol “autonomously post-trained” GPT-5.6 Luna—and playing around with Erdős problems, solves fewer than 1 in 10 games that you and I could beat with reasonable ease?

Second, because relative to every other general-purpose language model in existence—from any company, of any size and condition—it is a scandalously high grade. To give you an idea, the score of GPT-5.5, which came out three months ago, [was 0.43%](https://substack.com/redirect/77ea13d5-3b8e-4830-b780-a861085cd6d9?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA). Yes, I didn’t slip a decimal. Less than half a percentage point. GPT-5.6 is 20 times better than its predecessor, which was, at the time, [the highest score ever recorded](https://substack.com/redirect/059243b7-4c66-45cf-a1c8-177acfd1894a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)! (Opus 4.8 eventually [got a 1.5%](https://substack.com/redirect/f7294e20-a43c-4fa4-a2ec-ac6336fa68c7?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), surpassing it.)

If we extend the line on the chart the way the AI guys like to do, ARC-AGI-3 will be saturated by the end of the year, just like the previous versions eventually were. GPT-5.6 scores 90%+ on both ARC-AGI-1 and ARC-AGI-2 at a negligible cost per task, setting a new Pareto frontier of efficiency: it’s the best model in the performance-efficiency ladder.

I still remember how, in the old days of a year and a half ago, ARC-AGI-2 seemed so hard compared to ARC-AGI-1, and now these two charts below look like they are the same chart. One can have some reservations on AI progress and call out gaps and flaws, but sometimes it is simply beautiful to witness and impossible to disregard. (Note the x-axis is logarithmic.)

And third, because it is scandalous how incredibly interesting ARC-AGI-3 is as a benchmark when the best model in the world (Anthropic’s Fable pending testing) gets a score that is at once so high and so low depending on whether you compare it against AIs or against humans.

Rather than ask what GPT-5.6 has that makes it so special, I may as well ask what this ARC-AGI benchmark has that makes it so special? Am I being blinded by the millenarian instinct to think this moment is special at all and these results are actually just a fleeting artifact that will go down in history as a footnote once AI models develop a better memory or a greater capacity to understand games whose rules they don’t know? But if the test is actually robust, then what about ARC-AGI-4 (the ARC Prize team is already working on it)—will it reset the scoreboard to 0.XX% once again? If so, how many more iterations of ARC-AGI can be created? Can we speak of AGI while there is still some ARC-AGI left to be designed that is “easy” for humans and impossible for AI? What is it about this simple game test that trips super smart models over and over again? Why can I just log in, play around, and figure everything out in a few minutes, and they might solve three Erdős problems in that time but will struggle with this? So many questions, and none of them answered.

AI companies have become obsessed with software and agents, and it’s understandable: that’s where the enterprise money awaits them. That’s also why they decided to modify the definition of AGI into one that is economically relevant, like “doing 80% of the work of an average office worker,” or “reaching $200 billion in revenue,” or something along those lines. Even Sam Altman, OpenAI’s CEO, went as far as saying that AGI had actually been achieved already and it was time for the next milestone. But if what interests you is intelligence—after all, that is what truly sets us humans apart; any construction crane can do “economically relevant” work—then you’re in luck, because there is no AGI until ARC-AGI, in all its versions, is saturated. And even then, we may have to wait.

I don’t want to wander into philosophical thickets I won’t know how to get out of, so let me return to GPT-5.6’s performance on ARC-AGI.

The team has highlighted more than the score or the efficiency (not exactly dazzling, truth be told—the full evaluation at max reasoning effort cost close to $20,000): they’ve highlighted GPT-5.6’s problem-solving idiosyncrasy, the qualitative differences in its modus operandi compared to models close in time and in score on other benchmarks, like Opus 4.8.

The first thing that [caught my eye](https://substack.com/redirect/126d6106-59ce-4b5b-9a89-a1e16bdf0816?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) is this: it is the first verified frontier model to solve an ARC-AGI-3 game and for a good reason: “Sol is able to perform on ARC-AGI not because it executes better, but because it correctly orients itself in a new environment first.”

The magnitude of this can’t be grasped from that sentence alone unless you already know what it’s revealing: the main difference between fluid intelligence and crystallized intelligence—which I mentioned earlier but didn’t define—is that the fluid kind consists of solving problems you don’t know, that you’ve never faced, with a required set of skills you ignore or perhaps don’t even have, on the fly and efficiently. Humans do this constantly because our mental model of the world is finer than that of AIs trained on language alone (this idea that AI needs a better “world model,” by the way, is what separates Google’s current trajectory from OpenAI’s and Anthropic’s; I have a deep dive in the works explaining the main differences).

Let me give you an example of something that could pass for a test of fluid intelligence: you’re driving down a poorly lit road in Ontario; it has snowed, and the windows are fogging up. Suddenly you see a large shape in the middle of the road. You’ve never been to Ontario before. You’ve never driven in this much snow. And still, you brake and turn around. Or maybe, if there’s room, you carefully steer around the shape and get out of there. Is it a fallen tree? A dead moose? A hibernating bear? You don’t know, and it doesn’t matter, because the name of the thing is irrelevant to solving the situation; what matters is operating under uncertainty in a scenario that doesn’t exist in your “training data.” For you, that shape exists “out of distribution.” AI is incredibly adept at solving problems in-distribution, but the ones outside—those it struggles with.

Well, saying that GPT-5.6 is the best model at “orienting itself in novel situations” is exactly a compliment of that caliber. I’ve played the public demo of ARC-AGI-3 myself, and it is not exactly intuitive at first. You know nothing about the rules or the goals. The full game is basically a list of “problems you’ve never seen before.” The 7.8% score, which I mocked in the beginning, is a qualitative milestone, however quantitative it looks. It’s no mocking matter. I don’t know if we can call this a “[move 37](https://substack.com/redirect/c47117fa-0202-4981-a850-5296ca6f8f88?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)” for ARC-AGI—perhaps too premature—but it’s approaching fast.

Another incredible thing about GPT-5.6 is [this](https://substack.com/redirect/85b8661b-fdcd-496f-9e9b-be00ce937550?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA):

> Sol’s distinguishing capability is scene comprehensionIt almost always figures out what the core game mechanics actually are (unlike other models)Sol discovers a complicated mechanic in LP85 where game pieces must be held or parked until they are needed:“The horizontal tracks are independent. Park the lower color-11 tile one step right, then the vertical loop can move the upper tile without disturbing it. ACTION6 48 37”When it loses, it loses downstream (planning/execution), never at the perception stage

Solving perception is a matter of intelligence, whereas solving execution—at least at this level of complexity—is more a matter of memory and planning. If you manage to teach the model to recall the plan, it apparently has the intelligence to solve it. This is akin to humans solving the game of the disappearing numbers (limited-hold memory test). We are smart enough to count, but our short-term memory can’t hold more than a few chunks of information at a time. And then you’ll see chimps beating this game barely looking at the screen, while eating, with much lower intelligence. To me, the report on GPT-5.6’s skill gaps means that climbing to 50% is no longer a question of higher smarts but of scaffolding: “What breaks down is Sol’s reasoning on top: as the required chain of inference gets deeper, the model can’t compose what it’s learned into a working plan.”

People will laugh, as I did, at the 7.8% score being state-of-the-art. That’s precisely why I wanted to reframe what looks like a terribly low score with a more nuanced perspective. As I see it—maybe because I’m a writer and not a coder—we are still quite far from AGI. But I’m nevertheless happy to see GPT-5.6 start to see through the fog of my favorite challenge.
