"""Step 1 check: E2-file drag table vs the .vmod Coast/Roll rows, per 10 km/h band.

Writes step1_drag_table.csv (the 0-130 km/h table) and step1_band_check.csv (band
medians: E2-file build vs .vmod -P_wheel_in/v, Regional + Urban reference).
Stops with a loud message if any band is off by > 10 %.

Run:
  cd docs/research/drag-default-test-2026-11
  VECTO_SRC=/path/to/VECTO python step1_drag_check.py
"""
import collections
import csv
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tests.driver_model import _vmod as VM
import _e2_drag as E2

BANDS = [(40, 50), (50, 60), (60, 70), (70, 80), (80, 90)]
RUNS = ["BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
        "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz"]


def vmod_band_drag():
    """Median -P_wheel_in/v on Coast/Roll rows per band, and the component-sum identity."""
    runs = VM.run_files()
    pw = collections.defaultdict(list)
    comp = collections.defaultdict(list)
    per_run = {}
    for run in RUNS:
        if run not in runs:
            continue
        c = VM.load_vmod(runs[run])
        v = VM.col(c, "v_act") / 3.6
        da = VM.col(c, "DriverAction").astype(int)
        p_wheel = VM.col(c, "P_wheel_in")

        def g(n):
            try:
                return VM.col(c, n)
            except KeyError:
                return np.zeros_like(v)
        csum = np.abs(g("P_gbx_in")) + np.abs(g("P_gbx_loss")) + np.abs(g("P_axle_loss"))
        m = ((da == 4) | (da == 2)) & (v > 1)
        rp = collections.defaultdict(list)
        for vv, fw, fc in zip(v[m] * 3.6, -p_wheel[m] / v[m], csum[m] / v[m]):
            lo = int(vv // 10) * 10
            pw[lo].append(fw * 1000)      # kW/(m/s) -> N  (P in kW, so *1000)
            comp[lo].append(fc * 1000)
            rp[lo].append(fw * 1000)
        per_run[run] = rp
        # also confirm the gear on Coast/Roll rows is gear 2
    return pw, comp, per_run


def gear_on_coast():
    runs = VM.run_files()
    out = {}
    for run in RUNS:
        if run not in runs:
            continue
        c = VM.load_vmod(runs[run])
        da = VM.col(c, "DriverAction").astype(int)
        gear = VM.col(c, "Gear")
        m = (da == 4) | (da == 2)
        g = gear[m]
        g = g[~np.isnan(g)]
        vals, counts = np.unique(g.astype(int), return_counts=True)
        out[run] = dict(zip(vals.tolist(), counts.tolist()))
    return out


def main():
    v_kmh, F, comp = E2.build_drag_table()
    # write the full table
    with open(os.path.join(_HERE, "step1_drag_table.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["v_kmh", "F_drag_N", "motor_N", "gearbox_N", "axle_N"])
        for i, vk in enumerate(v_kmh):
            w.writerow([f"{vk:.0f}", f"{F[i]:.1f}", f"{comp['motor'][i]:.1f}",
                        f"{comp['gearbox'][i]:.1f}", f"{comp['axle'][i]:.1f}"])

    pw, compv, per_run = vmod_band_drag()

    print("Step 1 — E2-file coasting-drag table vs the .vmod (Regional+Urban ref)\n")
    print("  gear on Coast/Roll rows (confirm gear 2):")
    for run, g in gear_on_coast().items():
        print(f"    {run}: {g}")
    print()
    print(f"  {'band':9s} {'E2 files':>10s} {'.vmod -Pw/v':>12s} {'.vmod compsum':>14s} {'diff %':>8s}")
    worst = 0.0
    band_rows = []
    for lo, hi in BANDS:
        vk = (lo + hi) / 2
        f_e2 = float(np.interp(vk, v_kmh, F))
        f_vmod = float(np.median(pw[lo])) if pw.get(lo) else float("nan")
        f_comp = float(np.median(compv[lo])) if compv.get(lo) else float("nan")
        diff = (f_e2 / f_vmod - 1) * 100 if f_vmod == f_vmod and f_vmod else float("nan")
        if diff == diff:
            worst = max(worst, abs(diff))
        band_rows.append(dict(band=f"{lo}-{hi}", v_kmh=vk, E2_N=round(f_e2, 1),
                              vmod_Pw_N=round(f_vmod, 1), vmod_compsum_N=round(f_comp, 1),
                              diff_pct=round(diff, 1)))
        print(f"  {lo}-{hi:<4d} {f_e2:10.1f} {f_vmod:12.1f} {f_comp:14.1f} {diff:8.1f}")
    with open(os.path.join(_HERE, "step1_band_check.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(band_rows[0]))
        w.writeheader()
        w.writerows(band_rows)
    print(f"\n  worst band difference: {worst:.1f} %")
    if worst > 10.0:
        print("  *** STOP: a band is off by more than 10 %. Investigate before Step 2. ***")
    else:
        print("  OK: every band within 10 % -> reuse the 18940ab .vmod driver results (Step 2).")
    print("\nCSVs written to", _HERE)


if __name__ == "__main__":
    main()
