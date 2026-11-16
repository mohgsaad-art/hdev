"""GATE 1 -- run the v2 harness gate (gate_e2.py, branch eea-truck-validation-2026-11, commit 73990f0) UNCHANGED
and check the four E2 numbers against the v2 report (report.md table, "v2 harness" column) within 0.1 %.

Writes gate1.csv. Exit code 1 if a number is off by more than 0.1 %.
"""
import csv
import os
import sys

import harness as HN                       # puts the v2 folder on sys.path and sets VECTO_SRC

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HN.V2_DIR)
import gate_e2                             # noqa: E402  (v2 gate, not edited)

# v2 report.md, table under "GATE: PASSED" ("v2 harness" column). Copied from the report text, not from code.
V2_REPORT = {("RegionalDelivery", "reference"): 1.0471, ("RegionalDelivery", "low"): 0.9887,
             ("UrbanDelivery", "reference"): 0.8267, ("UrbanDelivery", "low"): 0.7376}


def main():
    rows, ok = [], True
    for (mission, load), rep in V2_REPORT.items():
        val = gate_e2.run(mission, load)
        diff = 100 * (val - rep) / rep
        ok &= abs(diff) <= 0.1
        rows.append([mission, load, round(val, 4), rep, round(diff, 3)])
        print("%-17s %-9s run %.4f  v2 report %.4f  diff %+.3f %%" % (mission, load, val, rep, diff))
    # the v2 gate's own pass rule against the 3 Nov numbers (threshold 1 %)
    own = gate_e2.main()
    out = os.path.join(HERE, "gate1.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cycle", "load", "run_now_kwh_km", "v2_report_kwh_km", "diff_pct"])
        w.writerows(rows)
        w.writerow(["GATE1", "PASS" if (ok and own) else "FAIL", "tolerance_pct", 0.1, ""])
    print("GATE 1:", "PASS" if (ok and own) else "FAIL")
    print("wrote", out)
    return 0 if (ok and own) else 1


if __name__ == "__main__":
    sys.exit(main())
