import json, sys, yaml
sys.path.insert(0,'/root/research-watchlist/scripts/screens')
from company_notes import NOTES
w=yaml.safe_load(open('config/watchlist.yaml'))
B={e['ticker'].upper() for e in w['tier_1_bctk'] if isinstance(e,dict) and e.get('ticker')}
R=json.load(open('scripts/screens/ai_forward_ranking.json'))
def tier(s):
    return ("1 — the model IS the product" if s>=85 else
            "2 — model-native, weaker proof" if s>=70 else
            "3 — strong corpus, real overlay" if s>=60 else
            "4 — AI real but not load-bearing" if s>=45 else
            "5 — thin")
L=[]
L.append("# AI application layer — ranked most to least AI-forward\n")
L.append("2026-08-20. 60 names, ranked by **thesis score**: model centrality (delete the model —")
L.append("does the product still exist and sell?) times whether there is a named product doing the")
L.append("work at a price. Evidence from five EDGAR/GitHub/blog screens adjusts by at most +8 and")
L.append("is shown per name; it confirms or contradicts a thesis, it never sets one.\n")
L.append("**BCTK holdings are marked [BCTK].** Everything else carries a two-sentence note on what")
L.append("the company does and why it qualifies — or, where the case is weak, why it does not.\n")
cur=None
for i,r in enumerate(R,1):
    t=tier(r['score'])
    if t!=cur:
        cur=t; L.append("\n## Tier %s\n" % t)
    tk=r['ticker']; held=" **[BCTK]**" if tk in B else ""
    flag=" · ⚠ %s" % r['contradiction'] if r['contradiction'] else ""
    L.append("**%d. %s** — %s%s  ·  centrality %d/5, product %d/3  ·  _%s_%s" % (
        i, tk, r['score'], held, r['centrality'], r['product'], r['evidence'], flag))
    if tk in NOTES:
        L.append("")
        L.append(NOTES[tk])
    L.append("")
L.append("\n---\n")
L.append("## Method notes\n")
L.append("- **Ranking is centrality, not evidence volume.** An earlier build folded evidence into")
L.append("  the denominator and penalised names measured on more dimensions — FactSet cleared all")
L.append("  three filing screens and fell to 45th while HeartFlow scored 100 partly by being")
L.append("  measured on fewer. Corrected.")
L.append("- **Practitioner evidence applies only to developer-facing firms.** Scoring iRhythm on")
L.append("  GitHub stars would measure that it is a medical device company, not that it is less")
L.append("  AI-central. The cost: top-tier diagnostics names rest on judgment plus reimbursement,")
L.append("  with no independent corroboration layer. That is the weakest link in tier 1.")
L.append("- **⚠ claims > traction** marks names loud in filings and silent where practitioners")
L.append("  would notice. For FDS this is a known false positive — its MCP server is real but not")
L.append("  on public GitHub. For MORN it is not: 21 stars, 338 days since last push.")
L.append("- Regenerate: `python3 scripts/screens/rank_ai_forward.py`\n")
open('docs/ai-forward-ranking-20260820.md','w').write("\n".join(L))
print("wrote docs/ai-forward-ranking-20260820.md")
