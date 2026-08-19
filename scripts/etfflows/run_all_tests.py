#!/usr/bin/env python3
"""
Run every etfflows test module in one shot and summarise.

There is no pytest in this env, so this is the suite runner:
    python3 scripts/etfflows/run_all_tests.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = ["test_metrics", "test_triggers", "test_factset_flows",
           "test_fear_greed", "test_render", "test_build", "test_lookthrough"]


def main() -> int:
    failed = []
    for mod in MODULES:
        path = os.path.join(HERE, f"{mod}.py")
        r = subprocess.run([sys.executable, path], capture_output=True, text=True)
        last = [ln for ln in (r.stdout or "").strip().splitlines() if ln.strip()]
        summary = last[-1] if last else "(no output)"
        status = "PASS" if r.returncode == 0 else "FAIL"
        print(f"{status}  {mod:<22} {summary}")
        if r.returncode != 0:
            failed.append(mod)
            print((r.stdout or "")[-2000:])
            print((r.stderr or "")[-1000:])
    print("-" * 60)
    if failed:
        print(f"FAILED MODULES: {', '.join(failed)}")
        return 1
    print(f"All {len(MODULES)} modules passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
