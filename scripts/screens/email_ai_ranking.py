#!/usr/bin/env python3
"""Email the AI application-layer top 50 with a long write-up per name.

Operator asked for 3-5 sentences per company covering why it is on the list AND
what its AI capability actually is. Those live in company_notes_long.py; this
script joins them to the ranking and sends.

Brevo pattern mirrored from scripts/newsdigest/email_send.py (credentials from
/root/podcasts/.env). Sends HTML -- a 50-name annotated list is not readable as
plain text -- with a text fallback for clients that refuse it.

  python3 scripts/screens/email_ai_ranking.py            # dry run, writes /tmp preview
  python3 scripts/screens/email_ai_ranking.py --send     # actually send
"""
import json, os, sys, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from company_notes_long import LONG                      # noqa: E402

TO = "amehra@baroncapitalgroup.com"
BREVO = "https://api.brevo.com/v3/smtp/email"
SUBJECT = "AI application layer — top 50, ranked most to least AI-forward"

BCTK = set()
try:
    import yaml
    w = yaml.safe_load(open(os.path.join(HERE, "..", "..", "config", "watchlist.yaml")))
    BCTK = {e["ticker"].upper() for e in w["tier_1_bctk"]
            if isinstance(e, dict) and e.get("ticker")}
except Exception:
    pass

R = json.load(open(os.path.join(HERE, "ai_forward_ranking.json")))
FLOOR = 60.0


def band(s):
    return ("The model IS the product" if s >= 85 else
            "Model-native, weaker proof" if s >= 70 else
            "Strong corpus, real overlay" if s >= 60 else
            "Below the discrimination floor — classified, not ranked")


def flags(r):
    out = []
    if r.get("contradiction"):
        out.append(r["contradiction"])
    if r.get("credibility"):
        out.append("credibility discount")
    if r.get("flywheel"):
        out.append("label flywheel")
    if r.get("churn"):
        out.append("leadership churn")
    if r.get("lab_risk", 1) >= 2:
        out.append("lab-encroachment %d/3" % r["lab_risk"])
    if r.get("disqualifier"):
        out.append(r["disqualifier"])
    return out


# ------------------------------------------------------------------ HTML
P = []
P.append("""<!doctype html><html><head><meta charset="utf-8">
<style>
 body{font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
      color:#1a1a1a;max-width:760px;margin:0 auto;padding:22px}
 h1{font-size:20px;margin:0 0 4px}
 h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#666;
    border-bottom:1px solid #ddd;padding-bottom:5px;margin:30px 0 14px}
 .lede{color:#444;font-size:14px;margin:0 0 6px}
 .row{margin:0 0 20px}
 .hd{font-weight:600;font-size:15px}
 .tk{font-weight:700}
 .sc{color:#888;font-weight:400;font-size:13px}
 .bctk{background:#1a1a1a;color:#fff;font-size:10px;padding:1px 5px;border-radius:3px;
       letter-spacing:.05em;margin-left:5px;vertical-align:1px}
 .ax{color:#777;font-size:12px;margin:2px 0 5px}
 .fl{color:#a33;font-size:12px;margin:2px 0 5px}
 .bd{margin:0;color:#222}
 .note{background:#f6f6f4;padding:12px 14px;border-radius:5px;font-size:13px;color:#444;
       margin:14px 0 6px}
</style></head><body>""")
P.append("<h1>AI application layer — top 50</h1>")
P.append('<p class="lede">Ranked most to least AI-forward. The ranking test is '
         '<b>delete the model — does the product still exist and sell?</b> '
         'Scores combine model centrality (0–5), whether a named product does the work '
         'at a price (0–3), and whether it is modern learned ML rather than a classical '
         'algorithm (0–3). Evidence from six EDGAR, GitHub and engineering-blog screens '
         'adjusts by at most ±8 — it confirms or contradicts a thesis, it never sets one. '
         'BCTK holdings are marked.</p>')
P.append('<p class="note"><b>Read the bottom of the list differently.</b> Below a score of '
         '60 the ranking stops discriminating — five names tie at exactly 52.7 with '
         'identical scoring vectors, so their order is a tie-break artifact. Those names are '
         'not weak versions of the top of the list; they fail the thesis for different and '
         'non-comparable reasons, so each carries a classification instead.</p>')

cur = None
for i, r in enumerate(R, 1):
    b = band(r["score"])
    if b != cur:
        cur = b
        P.append("<h2>%s</h2>" % html.escape(b))
    tk = r["ticker"]
    held = '<span class="bctk">BCTK</span>' if tk in BCTK else ""
    P.append('<div class="row">')
    P.append('<div class="hd">%d. <span class="tk">%s</span>%s '
             '<span class="sc">— %s</span></div>' % (i, html.escape(tk), held, r["score"]))
    P.append('<div class="ax">centrality %d/5 · named product %d/3 · modern ML %d/3 · %s</div>'
             % (r["centrality"], r["product"], r["ml"], html.escape(r["evidence"])))
    fl = flags(r)
    if fl:
        P.append('<div class="fl">⚠ %s</div>' % html.escape(" · ".join(fl)))
    P.append('<p class="bd">%s</p>' % html.escape(LONG.get(tk, "")))
    P.append("</div>")

P.append('<h2>Method</h2>')
P.append('<p class="bd" style="font-size:13px;color:#444">'
         'Screens run over <b>every US filer</b>, not just names under coverage. They are '
         'weighted by disclosure cost: "artificial intelligence" appears in 4,194 10-Ks and '
         'carries no information, while "AI revenue" appears in five. The rare, '
         'expensive-to-fake tail is the signal. Two known blind spots: the officer screen '
         'sees only Section 16 officers, so senior AI hires below that line are invisible; '
         'and a GitHub-traction flag cannot distinguish absent adoption from adoption on '
         'private infrastructure, which is why FactSet\'s flag is a false positive.</p>')
P.append("</body></html>")
HTML = "\n".join(P)

# ------------------------------------------------------------------ text
T = ["AI APPLICATION LAYER - TOP 50", "=" * 60, "",
     "Ranked most to least AI-forward. Test: delete the model -- does the",
     "product still exist and sell? Below a score of 60 the ranking stops",
     "discriminating; those names carry a classification instead.", ""]
cur = None
for i, r in enumerate(R, 1):
    b = band(r["score"])
    if b != cur:
        cur = b
        T += ["", b.upper(), "-" * len(b)]
    tk = r["ticker"]
    T.append("")
    T.append("%d. %s - %s%s" % (i, tk, r["score"], "  [BCTK]" if tk in BCTK else ""))
    T.append("   centrality %d/5 | product %d/3 | modern ML %d/3 | %s"
             % (r["centrality"], r["product"], r["ml"], r["evidence"]))
    fl = flags(r)
    if fl:
        T.append("   ! " + " | ".join(fl))
    T.append("   " + LONG.get(tk, ""))
TEXT = "\n".join(T)


def send():
    sender = os.environ.get("SMTP_USER", "")
    key = os.environ.get("SMTP_PASSWORD", "")
    if not sender or not key:
        raise RuntimeError("SMTP_USER / SMTP_PASSWORD not set (source /root/podcasts/.env)")
    payload = json.dumps({
        "sender": {"name": "Research Screens", "email": sender},
        "to": [{"email": TO}],
        "subject": SUBJECT,
        "htmlContent": HTML,
        "textContent": TEXT,
    }).encode()
    req = urllib.request.Request(BREVO, data=payload, method="POST", headers={
        "accept": "application/json", "api-key": key, "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.status, resp.read().decode()[:200]


if __name__ == "__main__":
    prev = os.environ.get("PREVIEW_PATH", "/tmp/ai_ranking_email.html")
    open(prev, "w").write(HTML)
    print("names: %d | html %d bytes | text %d bytes" % (len(R), len(HTML), len(TEXT)))
    print("preview: %s" % prev)
    if "--send" in sys.argv:
        st, body = send()
        print("sent -> %s  HTTP %s  %s" % (TO, st, body))
    else:
        print("dry run (pass --send to deliver)")
