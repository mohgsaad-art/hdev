"""Part D7: drag table IN the driver model, compared to VECTO .vmod.

Reruns the PR-#21 Part-D comparison (coast %, seconds > 85 km/h, speed RMS over
distance, wheel traction/braking energy) with the CORRECTED standard-value drag table
(D2) fed into a TEST-ONLY copy of the driver model that has the agreed edits
(drag_v/drag_F defaults, interp1(v,drag_v,drag_F), g=9.80665, inputs in m/s).

No engine file is touched. Run:
  cd docs/research/drivetrain-inputs-fallbacks-2026-11
  VECTO_SRC=/path/to/VECTO python run_d7.py
"""
import csv
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM

import _stdval as S
import _driver_dragtable as DM

OUT = _HERE
RUNS = {
    "RegionalDelivery": "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
    "UrbanDelivery": "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz",
    "LongHaul": "BEV_E2_LongHaul_ReferenceLoad_1Hz",
}


def hdev_run(cycle, drag=None):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cycle])
    vacc_v, vacc_acc, vacc_dec = D.load_vacc()
    kw = dict(
        coast_mass=VV.M_REF, m_red_wheels=VV.M_RED_WHEELS,
        cdxa_v=list(VV.CDXA_V), cdxa=list(VV.CDXA_REF),
        Crr=VV.crr_total_vecto(VV.M_REF), rho=VV.RHO_VECTO, g=VV.G,
    )
    if drag is not None:
        kw["drag_v"] = list(drag[0])
        kw["drag_F"] = list(drag[1])
    return DM.driver_model(s, v, stop, grad, vacc_v, vacc_acc, vacc_dec, **kw)


def coast_pct(M):
    return float(np.mean(M == 3) * 100)


def secs_over(V, kmh=85.0):
    return int(np.sum(V * 3.6 > kmh))


def rms_speed_vs_distance(S_h, V_h, c_vmod):
    """RMS speed difference every 10 m along the route."""
    v_vecto = VM.col(c_vmod, "v_act") / 3.6
    s_vecto = VM.col(c_vmod, "dist")          # cumulative distance [m]
    grid = np.arange(0, min(S_h[-1], s_vecto[-1]), 10.0)
    vh = np.interp(grid, S_h, V_h) * 3.6
    vv = np.interp(grid, s_vecto, v_vecto) * 3.6
    return float(np.sqrt(np.mean((vh - vv) ** 2)))


def _has(c, name):
    try:
        VM.col(c, name)
        return True
    except KeyError:
        return False


def vecto_metrics(c):
    v = VM.col(c, "v_act") / 3.6
    da = VM.col(c, "DriverAction").astype(int)
    dt = VM.col(c, "dt")
    coast = float(np.mean((da == 4) | (da == 2)) * 100)
    over = int(np.sum((v * 3.6 > 85.0)))
    p_wheel = VM.col(c, "P_wheel_in")
    E = p_wheel * dt / 3600.0
    return coast, over, E[E > 0].sum(), E[E < 0].sum()


def main():
    dt_obj = S.Drivetrain(axle_formula="vecto")
    v_fix, f_fix = dt_obj.drag_table("fixed")
    v_old, f_old = dt_obj.drag_table("old")
    runs = VM.run_files()
    rows = []
    print("Part D7 — drag table in the driver model vs VECTO .vmod\n")
    for cycle, label in RUNS.items():
        if cycle not in D.list_cycles():
            print(f"  [missing cycle] {cycle}")
            continue
        # HDEV runs: no drag, old drag (22 Oct), fixed drag (D2)
        out_nod = hdev_run(cycle, drag=None)
        out_old = hdev_run(cycle, drag=(v_old, f_old))
        out_fix = hdev_run(cycle, drag=(v_fix, f_fix))
        row = dict(cycle=cycle)
        for tag, out in [("nodrag", out_nod), ("olddrag", out_old), ("fixeddrag", out_fix)]:
            T, Sh, Vh, Ah, gr, Mh = out
            row[f"coast_{tag}"] = round(coast_pct(Mh), 2)
            row[f"secs85_{tag}"] = secs_over(Vh)
        # VECTO reference
        if label in runs:
            c = VM.load_vmod(runs[label])
            cv, ov, Epos, Eneg = vecto_metrics(c)
            row["coast_vecto"] = round(cv, 2)
            row["secs85_vecto"] = ov
            row["rms_fixeddrag_vs_vecto"] = round(
                rms_speed_vs_distance(out_fix[1], out_fix[2], c), 3)
            row["rms_nodrag_vs_vecto"] = round(
                rms_speed_vs_distance(out_nod[1], out_nod[2], c), 3)
        else:
            row["coast_vecto"] = row["secs85_vecto"] = "n/a"
        rows.append(row)
        print(f"=== {cycle} ===")
        print(f"  coast %:  no-drag {row['coast_nodrag']:5.2f}  old {row['coast_olddrag']:5.2f}  "
              f"FIXED {row['coast_fixeddrag']:5.2f}   VECTO {row.get('coast_vecto')}")
        print(f"  secs>85:  no-drag {row['secs85_nodrag']:4d}  old {row['secs85_olddrag']:4d}  "
              f"FIXED {row['secs85_fixeddrag']:4d}   VECTO {row.get('secs85_vecto')}")
        print(f"  speed RMS vs VECTO (km/h): no-drag {row.get('rms_nodrag_vs_vecto')}  "
              f"FIXED {row.get('rms_fixeddrag_vs_vecto')}")
        print()

    fields = sorted({k for r in rows for k in r})
    with open(os.path.join(OUT, "D7_driver_drag_vs_vecto.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["cycle"] + [f for f in fields if f != "cycle"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("CSV written:", os.path.join(OUT, "D7_driver_drag_vs_vecto.csv"))


if __name__ == "__main__":
    main()
