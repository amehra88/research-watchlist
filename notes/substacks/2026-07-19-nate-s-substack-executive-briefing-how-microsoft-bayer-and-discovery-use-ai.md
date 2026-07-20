---
doc_type: substack_post
source: substack
publication: Nate's Substack
publication_url: https://natesnewsletter.substack.com/
source_email: <20260719150306.3.e0543bf60578c6d1@mg-d0.substack.com>
source_sender: Nate from Nate’s Substack <natesnewsletter@substack.com>
source_url: https://open.substack.com/pub/natesnewsletter/p/run-ai-offline-private-files
source_date: '2026-07-19'
subscription_tier: free_plus_paid
tickers:
- MSFT
themes:
- enterprise_ai_adoption
- vertical_ai_applications
- model_efficiency_evolution
ingestion_date: '2026-07-20'
extraction_source: v3 substack ingest pipeline (substacks.py), claude-extracted tickers/themes
---

# Executive Briefing: How Microsoft, Bayer, and Discovery Use AI on the Data You
 Can't Upload

Get the full post and max your AI career leverage, plus connect with tens of thousands of paid subscribers in Nate’s Substack chat.

# [Executive Briefing: How Microsoft, Bayer, and Discovery Use AI on the Data You Can't Upload](https://substack.com/app-link/post?publication_id=1373231&post_id=207571099&utm_source=post-email-title&utm_campaign=email-post-title&isFreemail=true&r=8ne7oq&token=eyJ1c2VyX2lkIjo1MjMwMjM3MjIsInBvc3RfaWQiOjIwNzU3MTA5OSwiaWF0IjoxNzg0NDc3NTc4LCJleHAiOjE3ODcwNjk1NzgsImlzcyI6InB1Yi0xMzczMjMxIiwic3ViIjoicG9zdC1yZWFjdGlvbiJ9.Cc1cLPNXoaNk8k8WODiVk2jb0-eyLMdPRq4QgUCsle0)

### Bayer and Discovery Bank are teaching smaller models their private rules. LM Studio lets you test the first useful step on a laptop, and shows where the laptop stops being enough.

You have a file you would never paste into a chatbot. We all do: a contract, a board deck, a client record. AI could obviously help, but you also know you can’t send it to a model provider, so the work stays manual, or it doesn’t happen at all.

Big companies are spending real money to escape that exact trade-off.

At Bayer, complex crop-protection questions that used to take an agronomic adviser days or weeks to resolve now come back in less than thirty seconds.

These are not general farming questions. Answering them can require working through crop-protection labels that run past a hundred pages. Product, crop, location, and use all matter. A fluent summary can still be wrong if it misses the exception that changes the recommendation.

Bayer fine-tuned a small Microsoft Phi model on proprietary product-label data, regulatory rules, and expert-written questions and answers.

Discovery Bank made the same choice for different work. It fine-tuned five variants across two smaller Azure OpenAI models, 4o-mini and 4.1-mini. The variants were trained for work that included understanding the bank’s financial language, producing SQL in the format its systems expected, and following the response templates attached to specific workflows. Discovery says average response time fell from five or six seconds to between one and a half and two.

Both companies supplied what a public model could not know: their terminology, rules, examples, and standard for an acceptable answer. Microsoft says the customers’ prompts, training files, outputs, and fine-tuned models are not used to improve the general foundation model without permission. The fine-tuned model remains exclusive to the customer.

That is the big-company version of a decision that now fits on one laptop: instead of sending a sensitive file to a model provider, bring a downloaded model to the file.

With LM Studio, one person can open a synthetic or authorized document on the same machine as the model and disconnect the computer from the internet while it works. The laptop is not suddenly compliant, and the model has not learned the company’s rules. It can still flag possible sensitive material, compare versions, extract terms, summarize a private file, or prepare a proposed redacted copy for a person to check without sending the text to a model provider.

Start with one document. A local test shows which jobs fit on a laptop and where shared use, regulation, volume, or operational importance require an enterprise system. If the test becomes a recurring job, people will begin correcting the answers and teaching the system which exceptions matter. At that point the company owns more than the original files, and a board should know whether the job it has taught the system will survive a change of model or provider.

This briefing covers:

- The offline setup. The exact LM Studio config that reads a sensitive document with the network switched off.

- The Grok Build leak. The model obeyed “don’t open these files,” and the product uploaded the whole repo anyway.

- Where the laptop stops. What one machine handles, and the point the job moves to enterprise infrastructure.

- Microsoft’s lock-in move. How your corrections and permissions become the dependency, and the one question that tests “model independent.”

- The guide and skill. The full walkthrough plus the red/amber/green sensitivity router, to download and run on your own files.

Bring the one file you’ve been avoiding. I’ll show you exactly how to work on it.

## Upgrade your subscription to Nate’s Substack to unlock the rest.

Become a AI Executive Circle of Nate’s Substack to get access to this post.

### A subscription gets you:

### A subscription gets you:
