#!/usr/bin/env python3
"""Practitioner-audience proof: is LLM use CENTRAL, or written for the screens?

Operator's point (2026-08-20) and the sharpest critique of the EDGAR screens:
once a language screen is known, IR writes to it. A 10-K sentence is a claim
aimed at investors and algorithms. An engineering blog post is aimed at
engineers -- including the company's own, and the ones it wants to hire -- who
notice when a claim is hollow.

So this checks a DIFFERENT audience's artifacts and asks a harder question:
not "does the company mention LLMs" but "does it write like an organization
that actually operates them?"

TWO TIERS OF EVIDENCE, and the distinction is the whole point:

  MARKETING register  -- "AI-powered", "transforming", "revolutionize",
                         "harness the power of". Says nothing. Scores 0.
  OPERATOR register   -- eval harness, latency/token budgets, retrieval, RAG,
                         fine-tuning specifics, hallucination mitigation,
                         prompt regression, inference batching, guardrails,
                         context window management, distillation.

Only an organization actually running models in production writes about eval
sets, token budgets, and regression suites -- because those are the problems
you only have once it is real. That vocabulary is the signal.

STATUS: feed list in config/eng_blogs.yaml is SEEDED, NOT COMPLETE. Each entry
carries `verified`. Unverified/404 feeds are reported as UNRESOLVED, never as a
negative -- same asymmetry as the MCP screen: presence is strong evidence,
absence is weak.
"""
import json, os, re, sys, time, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
UA = "Mozilla/5.0 (research-watchlist; ashimmehra@gmail.com)"

# Feeds smaller than this carry headlines, not article bodies. A 0 from such a
# feed is an artifact of the feed format, not a finding about the company.
MIN_FEED_BYTES = 20000

# Operator register: problems you only have once models are in production.
OPERATOR = [
    "eval harness", "eval set", "evaluation harness", "golden set", "regression suite",
    "prompt regression", "token budget", "tokens per", "context window",
    "retrieval-augmented", "retrieval augmented", " rag ", "vector index", "embedding model",
    "fine-tun", "distill", "quantiz", "inference latency", "p95 latency",
    "hallucinat", "guardrail", "prompt injection", "chain-of-thought",
    "batch inference", "kv cache", "tool calling", "function calling",
    "model context protocol", "mcp server", "agent harness", "human-in-the-loop",
]
# Marketing register: scores nothing, but counted so the ratio can be shown.
MARKETING = [
    "ai-powered", "ai powered", "harness the power", "revolutioniz", "transforming the",
    "cutting-edge", "game-chang", "unlock the power", "next-generation ai", "ai-driven future",
]


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore"), r.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, 0


def strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).lower()


def load_feeds():
    try:
        import yaml
        d = yaml.safe_load(open(os.path.join(REPO, "config", "eng_blogs.yaml"))) or {}
        return d.get("feeds", {})
    except Exception as e:
        print("cannot read config/eng_blogs.yaml: %s" % e, file=sys.stderr)
        return {}


def main():
    feeds = load_feeds()
    if not feeds:
        print("No feeds configured.", file=sys.stderr)
        return
    rows, unresolved = [], []
    for ticker, meta in sorted(feeds.items()):
        url = meta.get("url") if isinstance(meta, dict) else meta
        if not url:
            continue
        body, status = fetch(url)
        time.sleep(1.0)
        if not body:
            unresolved.append("%s (HTTP %s)" % (ticker, status))
            print("%-6s UNRESOLVED http=%s %s" % (ticker, status, url), file=sys.stderr)
            continue
        text = strip_html(body)
        # SAMPLE-SIZE GUARD. A title-only feed scores 0 no matter how good the
        # engineering is -- that is a measurement artifact, not evidence.
        # Spotify's feed is ~6KB (titles only) while Shopify's is ~240KB, so a
        # zero means completely different things for the two. Below the floor we
        # report INSUFFICIENT rather than a score.
        nbytes = len(body)
        op = sorted({x.strip() for x in OPERATOR if x in text})
        mk = sorted({x.strip() for x in MARKETING if x in text})
        thin = nbytes < MIN_FEED_BYTES and not op
        rows.append({"ticker": ticker, "url": url, "feed_bytes": nbytes,
                     "operator_terms": op, "marketing_terms": mk,
                     "score": len(op), "insufficient_sample": thin})
        print("%-6s operator=%-3d marketing=%-3d bytes=%-7d%s %s" % (
            ticker, len(op), len(mk), nbytes, "  INSUFFICIENT" if thin else "", url),
              file=sys.stderr)

    rows.sort(key=lambda r: -r["score"])
    stamp = os.environ.get("SCREEN_STAMP") or datetime.date.today().strftime("%Y%m%d")
    outdir = os.environ.get("SCREEN_OUTDIR", HERE)
    dest = os.path.join(outdir, "eng_blog_proof_%s.json" % stamp)
    json.dump({"rows": rows, "unresolved": unresolved}, open(dest, "w"), indent=1)
    print("wrote " + dest, file=sys.stderr)

    print("## Practitioner proof — engineering-blog register\n")
    print("A filing sentence is written for investors and, increasingly, for screens.")
    print("An engineering post is written for engineers. **Operator terms** (eval harness,")
    print("token budget, retrieval, hallucination mitigation) are problems you only have")
    print("once models are actually in production. **Marketing terms** score nothing.\n")
    scored = [r for r in rows if not r["insufficient_sample"]]
    thin = [r for r in rows if r["insufficient_sample"]]
    if scored:
        print("| Operator terms | Ticker | Marketing terms | Evidence |")
        print("|---|---|---|---|")
        for r in scored:
            ev = ", ".join(r["operator_terms"][:6]) or "—"
            print("| %d | %s | %d | %s |" % (
                r["score"], r["ticker"], len(r["marketing_terms"]), ev))
        print()
    if thin:
        print("_Insufficient sample — feed carries headlines only, so a zero here says")
        print("nothing about the company: "
              + ", ".join("%s (%dKB)" % (r["ticker"], r["feed_bytes"] // 1024) for r in thin)
              + ". Fix by fetching full post bodies._\n")
    if unresolved:
        print("_Unresolved feeds (NOT a negative — the feed URL needs fixing): "
              + ", ".join(unresolved) + "_\n")


if __name__ == "__main__":
    main()
