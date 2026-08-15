---
doc_type: substack_post
source: substack
publication: The Algorithmic Bridge
publication_url: https://www.thealgorithmicbridge.com/
source_email: <20260812124050.3.8b1ff25f11876db2@mg2.substack.com>
source_sender: Alberto Romero from The Algorithmic Bridge <thealgorithmicbridge@substack.com>
source_url: https://open.substack.com/pub/thealgorithmicbridge/p/on-substack-pangram-partnership-its
source_date: '2026-08-12'
subscription_tier: free_plus_paid
tickers: []
themes:
- ai_generated_content
- ai_regulation
ingestion_date: '2026-08-15'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# On Substack-Pangram Partnership: It's About Sending a Message

Thank you for being a free subscriber. You can [upgrade here](https://substack.com/redirect/1fd44971-491f-4200-be28-144fcf71a1ac?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)

# [On Substack-Pangram Partnership: It's About Sending a Message](https://substack.com/app-link/post?publication_id=883883&post_id=210885751&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIxMDg4NTc1MSwiaWF0IjoxNzg2NTM4NTY5LCJleHAiOjE3ODkxMzA1NjksImlzcyI6InB1Yi04ODM4ODMiLCJzdWIiOiJwb3N0LXJlYWN0aW9uIn0.OcRvQK9mIiFJvRaAAGuBEtDO5v4qGZ1isvIwLlH3GrU)

### A bunch of false positives for a slop-free internet? Yeah, you can count me in

Hey, Alberto here! 👋 I publish long-form AI analysis covering culture, philosophy, and business. Paid subscribers get Monday how-to guides and Friday news commentary. If you’d like to become a paid subscriber, here’s a button for that:

Sorry guys, I’m not really following the schedule due to vacation. I’ll be back to the normal pace soon. Today, some delayed thoughts on the Substack-Pangram partnership (it’s been a month, but I believe I can add to this important conversation).

## I.

It’s the easiest time in history to do great work. It’s the hardest time in history to prove it's yours.

News is that Substack [has partnered with Pangram](https://open.substack.com/pub/post/p/against-claudefishing), the top AI detection company, in an attempt to free the platform of AI writing (or, failing that, discourage those who outsource their writing to AI from doing it further; fear of public shame is a strong disincentive). The news is not news anymore, though. A month has passed since the announcement. I wanted to wait before commenting to avoid the noise of posts fervently in favor and fervently against it because this is sort of neither. Now that the fog has dissipated, here’s what I think.

Let me start with the elephant in the room: I don’t think witch hunting is the best approach to fight anything*.* But if back in the seventeenth century in Salem or Scotland, witches had actually been killing people with potions, ointments, and sorcery, then hunting them would’ve been strictly a good thing. To the extent that this partnership can be labeled a “witch hunt,” I see it as the lesser evil. I would, of course, rather have people who disguise themselves as writers not use AI to plague the web with slop in the first place but, alas, it’s not in my hand to overhaul the human condition: they are doing it—like actual witches, they cast their prompts and spread the malaise—and so we must be unremorsefully inquisitorial.

The problem is, as others have pointed out, that some of the accused will not be guilty.

Every detection system is imperfect—witch hunters were so to the utmost degree, for witchcraft is a mix of superstition and fear and misogyny, and thus thoroughly made up—but even modern technology falls short of this impossible task. As we will see, Pangram is no panacea.

So, in the face of a “[tragedy of the commons](https://substack.com/redirect/c3d482c7-b544-4096-b1bb-1c1cdaba42a2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA)” that I’m not willing to withstand—AI slop everywhere for the gain of a few—I will accept a tragedy of the unlucky. If in exchange for a clean Substack, some innocent souls targeted by the AI detector have to be unfairly punished, then so be it. And I say more: if I myself have to pay that price in the form of accusatory fingers and a dent in my revenue and reputation just to get actual grifters to be afraid of grifting, then I’ll gladly do so. We’re not casualties of a platform-wide cleansing but martyrs for a digital golden age.

That’s my main point: The Substack-Pangram partnership is mostly good, not so much for what it is but for what it can be. In leading by example, Substack is sending a message to the entire world: let’s make writing human again.

If this were just about Substack, then I’d have reservations—Medium, the other writing app, [has rejected the use of AI detectors](https://substack.com/redirect/60434f4d-2f4d-42fc-9293-3d8b42b4f3c2?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in favor of other approaches—but this is bigger than either of them. This is bigger than Pangram. Or AI. This is bigger than writing itself. Our society is at stake—our humanity is at stake. To borrow Lincoln’s words, “the occasion is piled high with difficulty, and we must rise with the occasion.” You can’t escape history.

Ok, so now that we’ve considered the worst possible outcome—that good, normal people like you and me pay the price of a safe society—I must say that the likely outcome is much less dramatic: most of you will not be incorrectly flagged as AI.

## II.

Pangram has worked really hard to push the rate of false positive (FP) cases—those where the detection tool flags a human-written piece of text as AI—down to the theoretical minimum. They estimate the FP rate of the last version of the tool ([Pangram 4.0](https://substack.com/redirect/1516f518-9af9-4e64-a8c7-f661585db810?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA), launched recently) at 0.0041%, or 1 for every 24,000 instances.¹ The minimum is above zero, yes, but negligibly so.²

Pangram is not perfect, but it’s close to being as good as a detector can be.

Back in December 2022, three days after OpenAI released ChatGPT, [I predicted](https://substack.com/redirect/edf9535e-a17c-4f1b-adb6-d88d25c3dd51?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that AI writing would have what I called a styleme (probably a Hispanicism):

> Human writing has characteristics that can, using the right tools, reveal authorship. As LMs become masters of prose, they may develop some kind of writing idiosyncrasy . . . Maybe we could find the AI’s styleme (like a fingerprint hidden in language) not simply to distinguish ChatGPT from a human, but to distinguish its style from all others.

I knew the problem of detecting AI would be big, and I thought: if humans leave traces and cues in their writing—this fact is used in stylometry to attribute authorship to anonymous or disputed texts—why wouldn’t AI? That’s what Pangram is trained to detect: AI’s stylistic fingerprints.

It doesn’t matter whether your writing went into ChatGPT’s training corpus, because it’s the aggregate of everything it swallowed—plus the subsequent conditioning during the “post-training” phase—that gives AI models their distinctively annoying style. You, a mere human, can tell AI writing apart from human writing if you train enough. (I believe I’m better than Pangram, although I have no evidence to support this claim.)

So I’m not at all surprised that it’s possible to do what Pangram does. However, as I stated in [a piece on Pangram’s virtues](https://substack.com/redirect/13b33db2-ca76-4006-b79e-0b85a98793f4?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (that I published before this partnership), a detector should focus on securing a minimal rate of false positives at the expense of a higher rate of false negatives. I wrote:

> [Pangram’s is] the better approach: do everything in your power to avoid punishing those who try to play fair in a world giving them every reason to be corrupt.

AI detection is therefore subject to Voltaire’s adage: Perfect is the enemy of good. This trade-off entails that everything flagged as AI will almost always be AI (1 for every 24,000 documents is extremely low), whereas not everything flagged as human will always be human (0.34%—1 for every 300 documents—is not an acceptable rate at scale).

But even with an uncompromising focus on reducing false positives, the FP rate is not zero, and I’m not fond of being hand-wavy on this matter: one innocent in jail is still a failure. As William Blackstone said in 1765: it’s better for 10 guilty people to escape than for 1 innocent person to suffer. I still stand by that—society must be unfailingly exemplary.

Thankfully, this is not such a case.

## III.

Substack is not actually trying to catch AI sloppers; the mechanism they’ve enabled isn’t binding. If you’re flagged as AI, it doesn’t result in a lifetime ban from the platform. (You can even turn off Pangram completely.) They’re not actually sending one innocent person to digital jail for every ten people accused of being guilty. The goal behind this partnership is, instead, to give people the ability to know what’s going on. Pangram acts as a sort of “externally enforceable disclosure.”³

If Mr. X writes with AI and you don’t want to read AI, you can now find out and decide accordingly. This is the correct approach to the AI;DR trend (it’s AI, so I don’t read it). This partnership acts, first and foremost, as a deterrent not limited to Substack: if this initiative succeeds, then it’s a matter of institutional will for it to spread like wildfire to all other platforms, social media, magazines, newspapers, universities, etc.

Actually, if it succeeds, the rest of the world will have no choice but to follow suit, for there will be no excuses whatsoever not to kill slop.

This could be the dawn of an AI slop-free world. And for that, given the level of rot, murkiness, and illiteracy that we’ve reached as a species, a couple of mistakes here and there seem to me an acceptable price—practically a bargain. I’ve been a target of false positives myself and I know it sucks and yet I consider that a reasonable price to pay in exchange for going back to a pre-ChatGPT internet. Would I prefer AI had never been deployed into the world and used to create piles of slop? Sure. But that’s wistfulness. This, in turn, is real.

Maybe you don’t agree with me. Maybe you think society should be exemplary even at the cost of society itself; a sort of “being tolerant even with the intolerant.” If people want to use AI to write—for whatever reason—then let them be even if they kill the commons in the process. Just write your stuff yourself and stop minding other people’s business. But I’m quite [Popperian](https://substack.com/redirect/37dadf11-1bf6-4294-b66c-42ce241a8e01?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) in this regard: there’s nothing worse in modern society—modern understood as the kind that has more or less figured out things for harmonic coexistence—than someone who is not civic: Someone who, by virtue of living in a safe and stable society he didn’t build, is willing to be selfish in exchange for a collective sacrifice.⁴

The students who cheated in Serrano’s exam at Brown ([I covered this story](https://substack.com/redirect/91aa950a-e1e8-474a-aed5-8831faed6140?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) that went viral recently, and it’s a good real-world example of what I mean) thought they were inflicting just an infinitesimal amount of harm into the educational system, but because most of them thought the same thing, the harm compounded to the point of forcing Serrano’s hand into an in-person final exam, a further nation-wide coverage of the events, and the subsequent lost of trust in what is otherwise a well-respected faculty. Substack—no, the internet—is that faculty. Who will come here to read people’s real stuff at the risk of encountering so much fake slop? I, for one, wouldn’t. If I were a newcomer and found out slop inhabits Substack like mold inhabits the shower plate of a middle-aged unmarried man, I wouldn’t come back. The risk of polluting my feeds is greater than the benefit of reading one good essay.

This rationale also works, to be sure, with human-made slop. But what can be done about that except making the web totally undemocratic? (If you make slop, you’re out, as decided by the anti-slop elite.) Better to let everyone in than to arbitrarily select who can stay. Pangram makes for a fine, granular solution where something rougher wouldn’t suffice. With AI, we don’t have to resort to age or race or socioeconomic status. It’s a matter of how much of your writing is surrendered to the machine. Pangram can trace that line quite closely to ground truth. It can quarantine AI slop, so how is the fact that human slop exists a counterargument in any sense?

If we could define in a measurable and objective manner what counts as human slop and what doesn’t—the term is subjective by definition, for it pertains to the taste of the beholder—then I’d also be in favor of killing human slop. If you think this is elitist, I encourage you to work hard to stay on the correct side of history.

## IV.

What worries me about this collaboration more than anything else is that the social dynamics that emerge from what seems, at all lights, like a good idea are never as neat as they seem on paper. A witch hunt, even when witches exist and non-witches are mostly safe, is still governed by the mob. And the mob, more so than any other agent involved here, is stupid.

If you’re a writer who hates AI—and you were unfamiliar with Pangram before the Substack partnership announcement—then you’re at risk of becoming part of the mob. Don’t be the mob.

If you didn’t know about the asymmetry between false positives and false negatives or Pangram’s stylometric focus, or the fact that it gets almost perfect scores on pre-ChatGPT texts, or that it’s trained like ChatGPT is and so it doesn’t rely on naive heuristics like “if you’re in the corpus, you will be flagged”—if you didn’t know about any of those things, that’s fine, but now you should learn them. Indeed, Pangram isn’t perfect and the shape of imperfection it displays is worth knowing. The fewer words a text has, the more brittle the tool; it processes text in chunks, which produces weird results (like a full human-written text being flagged as 100% human but parts of it as 100% AI), etc.

If you want writers and readers to see this partnership favorably, what remains for you is to not become the mob. This is a duty that, in my opinion, is a little ask in exchange for a sane platform: don’t overlook the details. Don’t be as lazy in understanding how AI works as others are in understanding how writing works. Don’t go hunting without knowing the limits of the tool you wield. If you do, you witch-hunters and the witches you hunt are hardly distinguishable in your contribution to this mess.

Substack was careful about this. They wrote that “Pangram can only detect whether AI was used to make the text, not whether great human care went into creating it, nor whether AI tools were used as a source.”

But the mob is the enemy of nuance. What this disclaimer means in practice is that people will make absolute accusations about relative crimes, without taking into account why, how, and to what extent AI was used. There are many ways to use AI in the multi-step process of writing an essay or a news article. I’m not going to judge whether it’s better to outsource the brainstorming or editing or research. Each should decide where to draw the line and stick to that. But wielding a unidimensional tool to judge a multidimensional activity, many will unwittingly forget this limitation the moment the open the page, without realizing that it’s he who wields a tool that’s responsible for how it’s used: If Pangram can’t tell you the details of how a text was made, then don’t use it to delegate your judgement just like you dislike when others delegate their writing.

The inverse problem exists as well.

It might be that “great human care,” as Substack writes, went into an article that Pangram scores as 74% AI, but just how much care exactly? The remaining 26%? Or is it infinite insofar as it’s unmeasurable? The mob is unfair to you, but how unfair are you to the mob?

Those using AI to write [are hiding](https://open.substack.com/pub/emmaklint/p/i-use-ai-to-write-everything-i-publish) behind an unknown amount of care they ensure was put into their work. An amount that, in the eyes of the world, Pangram mercilessly collapses into nothing. But they’re abusing their status as cyborgs; human kernels inside a bot, however pure their core. When readers reject their AI writing, it’s not because they know how little care was put into it, but because they don’t know how much. All the intent, enthusiasm, and love you devoted to it that Pangram ignored will always be less than the amount devoted by those who did write the entire thing.

Just like it’s unfair for readers to make absolute accusations from relative crimes, it’s also unfair that you mount absolute defenses on relative alibis. A 74% AI score is less damning as total evidence of lazy writing than it is of relative carelessness compared with the 0% scores.

I’m happy that you outsourced some things and not others—and that you cared some indeterminate amount about me—but this guy over here cared everything about me. And because my time and attention are finite, his pristine Pangram score tells me that I’m better off paying him back for his pristine care than you.

The good news is that you can turn up your care to a level where your AI writing is no longer actually AI writing. When Substack says that you can scan your drafts to check whether they pass the “Pangram test,” they’re not saying “adhere to the ruling of the AI detector” but “if you’re worried you didn’t do enough to cover your footprints, just check your score.” Reading that as “Oh, no, I’m going to lose my idiosyncrasy because Pangram will steer me into a goop-shaped literary convergence,” makes you sound rather hyperbolic.

In any case, if you do write your stuff yourself, then don’t use Pangram at all. He is as much a prisoner of AI who delegates intent and voice as he who distorts them to escape its mistaken condemnation. My advice here is simple: learn to be as weird on the page as you are in your life, and you’ll be ok, whatever Pangram says. You can’t deny the usefulness of Pangram just because its scores are wrong at times and then use those scores as an argument that it’s oppressive. If you ignore them for one reason, ignore them for the other.

The real you exists “out of slop,” and to the extent that you could be flagged as machine-like, it’s probably because you read too much machine prose.

Lucky for you, this was written by a human.

Now, should you trust Pangram, the company, on its self-assessed reliability scores of Pangram, the tool? Surely not. There are also [independent third-party assessments](https://substack.com/redirect/e6772f01-643d-4738-a582-3c76ecd3c94a?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) of its accuracy. I don’t think it is as good as they claim it to be, but again, the main edge cases that take place in the real world but not in the lab—like AI-human mixed authorship—are being addressed already. AI slop only gets worse because we get lazier; AI detection tools only get better.

This is not a post on Pangram’s specs, so I will cite here what matters to us from the new [Pangram 4.0](https://substack.com/redirect/1516f518-9af9-4e64-a8c7-f661585db810?j=eyJ1IjoiOG5lN29xIn0.bqmJ9TjykdtTXCviJ3jD2X5vxhprRGd5tpCaC89FQIA) (awaiting further independent reviews):

> To our knowledge, Pangram 4 is the first AI detection model that is able to differentiate AI-edited writing from interspersed human-AI content simultaneously in a single pass. It is robust against humanizers and adversarial prompting, identifying AI involvement in humanized output 98.83% of the time across 13 popular commercial tools. It generalizes across frontier models: every model family is detected with an FNR below 0.7%, with no significant correlation between a model’s release date and its detectability.

If true, most of the usual complaints—humanizers break detectors or detectors can’t discern mixed authorship—don’t apply to Pangram. The question is not perfection but rather what level of imperfection is acceptable. I think Pangram clears that bar.

Substack has always championed a rather laissez-faire approach to writing that I prefer to over-moralizing and cancel culture, so I suspect its attitude toward Pangram results will be the same. I don’t think they will do anything whatsoever contingent on the level of AI slop in your posts. If they did, they might even be violating some [data privacy laws](https://open.substack.com/pub/careylening/p/one-weird-trick-for-opting-out-of). (If you want to opt out, [you can](https://substack.com/@privacat1/note/c-308544221).) They trust that people will exercise their preferences and manually block or unsubscribe from those who outsource their creativity to AI if they so wish.

When I read someone go on at length about how awful it is to call people out for using AI to write, I can only think one thing: it’s telling that you think the allegation is worse than the offense. The truth is that the offense is a destructive mechanism, whereas the allegation is a corrective one.
