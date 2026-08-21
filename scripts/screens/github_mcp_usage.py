#!/usr/bin/env python3
"""MCP USAGE (not just existence) via GitHub, plus a practitioner-audience check.

Operator's point (2026-08-20), which is the sharpest critique of the EDGAR
screens: filing language is written for investors and, increasingly, FOR SCREENS
LIKE THIS ONE. Once a phrase is known to be screened, IR will write it. So a
filing hit is a claim, not evidence.

This script looks at artifacts produced for a PRACTITIONER audience, where
fakery gets noticed:

  - Does the company actually ship an MCP server, in public, under its own org?
  - Is anyone using it?      -> stars, forks
  - Is it maintained?        -> days since last push, open issues
  - Is it real engineering?  -> repo count, not one abandoned demo

A company can write "Model Context Protocol" into a 10-K in an afternoon. It
cannot fake 3,000 stars and eighteen months of commits.

SCORING (traction, 0-10):
  stars/forks capped and log-scaled so a 30k-star repo does not drown a 300-star
  one that is genuinely used; recency weighted heavily because an abandoned MCP
  server is evidence AGAINST centrality.

LIMITATION: only sees PUBLIC GitHub under a known org. A company shipping MCP
behind a customer portal, on GitLab, or under a product-specific org will be
missed or undercounted. Absence is weak evidence; presence is strong evidence.
That asymmetry is the point -- use this to CONFIRM, never to reject.

Unauthenticated GitHub search allows ~10 req/min. Set GITHUB_TOKEN to go faster.
"""
import json, os, sys, time, math, datetime, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
TODAY = datetime.date.today()


def gh(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "research-watchlist"},
    )
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):          # secondary rate limit
                time.sleep(20 * (attempt + 1))
                continue
            return None
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None


def load_orgs():
    path = os.path.join(REPO, "config", "github_orgs.yaml")
    try:
        import yaml
        d = yaml.safe_load(open(path)) or {}
        return d.get("orgs", {})
    except Exception as e:
        print("cannot read %s: %s" % (path, e), file=sys.stderr)
        return {}


def traction(repos):
    """0-10. Rewards real use and active maintenance; punishes abandonment."""
    if not repos:
        return 0.0, {}
    stars = sum(r["stargazers_count"] for r in repos)
    forks = sum(r["forks_count"] for r in repos)
    freshest = min((TODAY - r["_pushed"]).days for r in repos)
    use = min(5.0, math.log10(stars + 1) * 2.5)          # 100 stars ~ 5.0
    fork = min(2.0, math.log10(forks + 1) * 1.3)
    if freshest <= 30:
        recency = 2.0
    elif freshest <= 90:
        recency = 1.5
    elif freshest <= 365:
        recency = 0.75
    else:
        recency = 0.0                                     # abandoned: no credit
    breadth = min(1.0, len(repos) / 3.0)
    raw = use + fork + recency + breadth
    # ADOPTION GATE. Recency measures MAINTENANCE, not usage -- and the operator
    # asked about usage. Without this, a 1-star repo pushed yesterday outscores a
    # genuinely-used 300-star project, which is backwards. Below 25 stars we cap
    # the total so activity alone cannot manufacture a high score.
    gated = min(raw, 4.0) if stars < 25 else raw
    return round(min(10.0, gated), 1), {
        "repos": len(repos), "stars": stars, "forks": forks,
        "days_since_push": freshest,
        "low_adoption": stars < 25,
    }


def main():
    orgs = load_orgs()
    if not orgs:
        print("No orgs configured. Populate config/github_orgs.yaml.", file=sys.stderr)
        return
    out = []
    for ticker, org in sorted(orgs.items()):
        q = urllib.parse.quote("mcp in:name,description,readme org:%s" % org)
        d = gh("/search/repositories?q=%s&sort=stars&order=desc&per_page=20" % q)
        time.sleep(1.0 if TOKEN else 7.0)                 # respect search limits
        if d is None:
            print("%-6s %-22s QUERY FAILED" % (ticker, org), file=sys.stderr)
            continue
        repos = []
        for r in d.get("items", []):
            blob = " ".join(filter(None, [r.get("name", ""), r.get("description", "")])).lower()
            # require a real MCP signal, not an incidental "mcp" substring
            if "mcp" not in blob and "model context protocol" not in blob:
                continue
            try:
                r["_pushed"] = datetime.datetime.strptime(
                    r["pushed_at"][:10], "%Y-%m-%d").date()
            except Exception:
                continue
            repos.append(r)
        score, stats = traction(repos)
        top = sorted(repos, key=lambda r: -r["stargazers_count"])[:3]
        out.append({
            "ticker": ticker, "org": org, "traction": score, **stats,
            "top_repos": [{"name": r["full_name"], "stars": r["stargazers_count"],
                           "pushed": r["pushed_at"][:10]} for r in top],
        })
        print("%-6s %-22s traction=%-5s %s" % (ticker, org, score, stats), file=sys.stderr)

    out.sort(key=lambda r: -r["traction"])
    stamp = os.environ.get("SCREEN_STAMP") or TODAY.strftime("%Y%m%d")
    outdir = os.environ.get("SCREEN_OUTDIR", HERE)
    dest = os.path.join(outdir, "github_mcp_usage_%s.json" % stamp)
    json.dump(out, open(dest, "w"), indent=1)
    print("wrote " + dest, file=sys.stderr)

    print("## MCP usage — public GitHub traction\n")
    print("Filing language is a *claim*; a used, maintained public repo is *evidence*.")
    print("Traction 0-10: use (stars) + forks + recency + breadth. An abandoned")
    print("server scores 0 on recency — that is deliberate.\n")
    print("| Traction | Ticker | Repos | Stars | Forks | Days since push | Top repo |")
    print("|---|---|---|---|---|---|---|")
    for r in out:
        if not r.get("repos"):
            continue
        top = r["top_repos"][0]["name"] if r["top_repos"] else ""
        print("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["traction"], r["ticker"], r["repos"], r["stars"], r["forks"],
            r.get("days_since_push", ""), top))
    none = [r["ticker"] for r in out if not r.get("repos")]
    if none:
        print("\n_No public MCP repo found under the configured org "
              "(weak evidence only — may be private, elsewhere, or a different org): "
              + ", ".join(none) + "_\n")


if __name__ == "__main__":
    main()
