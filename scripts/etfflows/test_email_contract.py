"""
Guards the seam between this repo and /root/daily — the one place a defect is invisible here
and silent there.

The bug this exists to prevent ALREADY HAPPENED once: do_report named its output for the FLOW
date (T-1, because FactSet flows lag a day) while combine_and_send.py formats every path with
date.today(). Every test in this repo passed, the digest ran fine, and the section simply
never appeared. Nothing failed loudly — the digest just logs "Report not found" and sends
without it.

So this test reads the ACTUAL REPORTS table out of /root/daily/combine_and_send.py and checks
that the paths it expects are the paths etf_flows.py writes. If /root/daily is absent (a
checkout elsewhere, CI) the test skips rather than failing — it is a deployment contract, not
a property of this repo alone.

Run:  python3 scripts/etfflows/test_email_contract.py
"""
import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILURES = []
SKIPPED = []
COMBINE = "/root/daily/combine_and_send.py"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def load_reports(path):
    """Pull the REPORTS list out of combine_and_send.py without importing it.

    Parsed rather than imported because importing pulls in Brevo config and network code.
    """
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "REPORTS":
                    return [tuple(ast.literal_eval(e)) for e in node.value.elts]
    return None


def report_paths_we_write(run_date):
    """Mirror of the two paths do_report writes. Read from the source, not re-typed."""
    src = open(os.path.join(REPO, "scripts", "etf_flows.py")).read()
    out = {}
    for key, pattern in (
        ("main", r'f"report_etfflows_\{run_date\}\.txt"'),
        ("table", r'f"report_etfflows_table_\{run_date\}\.txt"'),
    ):
        if not re.search(pattern, src):
            return None, f"etf_flows.py no longer builds a {key} filename from run_date"
        out[key] = os.path.join(REPO, "logs",
                                f"report_etfflows{'_table' if key == 'table' else ''}"
                                f"_{run_date}.txt")
    return out, ""


def test_digest_expects_the_filenames_we_write():
    if not os.path.exists(COMBINE):
        SKIPPED.append("no /root/daily checkout")
        print("  skip /root/daily not present — deployment contract not checkable here")
        return

    reports = load_reports(COMBINE)
    check("REPORTS table parsed", reports is not None)
    if not reports:
        return

    titles = [t for t, _ in reports]
    check("ETF FLOWS & CROWDING section is registered",
          "ETF FLOWS & CROWDING" in titles, f"got {titles}")
    check("ETF FLOW DETAIL section is registered",
          "ETF FLOW DETAIL" in titles, f"got {titles}")

    by_title = dict(reports)
    run_date = "2026-08-21"
    ours, err = report_paths_we_write(run_date)
    check("etf_flows.py still names files from the run date", ours is not None, err)
    if not ours:
        return

    expects_main = by_title.get("ETF FLOWS & CROWDING", "").format(date=run_date)
    expects_table = by_title.get("ETF FLOW DETAIL", "").format(date=run_date)

    # Compare FILENAMES, not full paths: this may run from a worktree, whose logs/ dir is
    # under .claude/worktrees/... The filename is what actually broke, and the directory is
    # fixed by deployment (the digest reads the canonical /root/research-watchlist/logs).
    check("digest looks for exactly the main report filename we write",
          os.path.basename(expects_main) == os.path.basename(ours["main"]),
          f"digest={os.path.basename(expects_main)} ours={os.path.basename(ours['main'])}")
    check("digest looks for exactly the table filename we write",
          os.path.basename(expects_table) == os.path.basename(ours["table"]),
          f"digest={os.path.basename(expects_table)} ours={os.path.basename(ours['table'])}")
    check("digest reads them from the canonical repo's logs/ dir",
          expects_main.startswith("/root/research-watchlist/logs/"), f"got {expects_main}")


def test_layout_order_is_the_operator_layout():
    """Flows directly after ETF UPDATE; the full table LAST."""
    if not os.path.exists(COMBINE):
        print("  skip /root/daily not present")
        return
    titles = [t for t, _ in (load_reports(COMBINE) or [])]
    if not titles:
        return
    check("flows section sits immediately after ETF UPDATE",
          titles.index("ETF FLOWS & CROWDING") == titles.index("ETF UPDATE") + 1,
          f"got {titles}")
    check("the detail table is the LAST section",
          titles[-1] == "ETF FLOW DETAIL", f"got {titles}")


def test_report_step_runs_before_the_combine():
    """run_daily.sh must render the report before combine_and_send.py reads for it."""
    path = "/root/daily/run_daily.sh"
    if not os.path.exists(path):
        print("  skip run_daily.sh not present")
        return
    src = open(path).read()
    check("run_daily.sh invokes the flows report", "etf_flows.py --report" in src)

    # Match the INVOCATION, not any mention. Comments in this file legitimately name
    # combine_and_send.py, and a naive substring search finds those first.
    lines = src.splitlines()

    def line_of(pred):
        return next((i for i, ln in enumerate(lines)
                     if not ln.lstrip().startswith("#") and pred(ln)), None)

    i_report = line_of(lambda ln: "etf_flows.py --report" in ln)
    i_combine = line_of(lambda ln: "combine_and_send.py" in ln)
    check("both steps are actually invoked",
          i_report is not None and i_combine is not None,
          f"report={i_report} combine={i_combine}")
    check("the report is rendered BEFORE the combine reads for it",
          i_report is not None and i_combine is not None and i_report < i_combine,
          f"report at line {i_report}, combine at line {i_combine} — a report written after "
          "the combine would always be a day stale")
    check("the flows step cannot break the digest",
          "etf_flows.py --report" in src and "|| true" in src)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        print(f"\n{fn.__name__}:")
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
        return 1
    print(f"All checks passed ({len(tests)} tests)"
          + (f" [{len(SKIPPED)} skipped: {', '.join(SKIPPED)}]" if SKIPPED else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
