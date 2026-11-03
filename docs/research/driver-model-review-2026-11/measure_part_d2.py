"""Part D2/D8 — decisive drag test with the CORRECTED VECTO drivetrain drag (F4 redo).

Correction: on Coast/Roll rows, -P_wheel_in/v = P_gbx_in (motor drag through the box)
+ P_gbx_loss + P_axle_loss = ~1.43-2.05 kN. The earlier D2 table (0.79-0.95 kN) omitted
P_gbx_in and was ~2x too small. Drag table rebuilt per 10 km/h band from -P_wheel_in/v.

Runs D1/D2/D3/D5/D8 for Regional and Urban at reference AND low load. Reports: coast
share split into look-ahead vs overspeed roll, secs>85 km/h, speed RMS @10 m, wheel
traction/braking energy. Also reports VECTO's in-driving-mode Coast/Roll share for a
fair overspeed-roll comparison (NOT assumed to be a classification difference).

Run: python docs/research/driver-model-review-2026-11/measure_part_d2.py
"""
import os
import sys
import bisect

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model.reference_copy import driver_model
from tests.driver_model.driver_model_v_dragtable import driver_model_dragtable
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM
from src.engine.force_engine import force_engine

VACC = D.load_vacc()

# CORRECTED drag table: -P_wheel_in/v = P_gbx_in + P_gbx_loss + P_axle_loss, per band.
D2_V = [0.0, 45.0, 55.0, 65.0, 75.0, 85.0, 130.0]
D2_F = [1431.0, 1431.0, 1534.0, 1635.0, 1935.0, 2055.0, 2055.0]
D3_V = [0.0, 50.0, 90.0, 130.0]
D3_F = [630.0, 630.0, 850.0, 850.0]

RUN_LOADS = [("RegionalDelivery", "reference"), ("RegionalDelivery", "low"),
             ("UrbanDelivery", "reference"), ("UrbanDelivery", "low")]
VDRI = {"RegionalDelivery": "RegionalDelivery.vdri", "UrbanDelivery": "UrbanDelivery.vdri"}
LOADING = {("RegionalDelivery", "reference"): 3019.5882, ("RegionalDelivery", "low"): 603.9176,
           ("UrbanDelivery", "reference"): 3019.5882, ("UrbanDelivery", "low"): 603.9176}
RUNFILE = {("RegionalDelivery", "reference"): "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
           ("RegionalDelivery", "low"): "BEV_E2_RegionalDelivery_LowLoading_1Hz",
           ("UrbanDelivery", "reference"): "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz",
           ("UrbanDelivery", "low"): "BEV_E2_UrbanDelivery_LowLoading_1Hz"}


def seg_targets(s, v):
    v_wp = [float(x) / 3.6 for x in v]
    s_wp = [float(x) for x in s]
    seg = [0.0] * len(v_wp)
    nxt = 0.0
    for i in range(len(v_wp) - 1, -1, -1):
        seg[i] = v_wp[i] if v_wp[i] > 0 else nxt
        if v_wp[i] > 0:
            nxt = v_wp[i]
    return s_wp, seg


def coast_split(S, V, M, s_wp, seg):
    tgt = np.array([seg[max(0, min(bisect.bisect_right(s_wp, float(d)) - 1, len(seg) - 1))] for d in S])
    c3 = (M == 3)
    n = len(M)
    la = int((c3 & (V < tgt - 0.01)).sum())
    osr = int((c3 & (V >= tgt - 0.01)).sum())
    return c3.sum() / n * 100, la / n * 100, osr / n * 100


def over85(V):
    return int((np.asarray(V) * 3.6 > 85).sum())


def rms_vs_vecto(S, V, cols):
    dist_v = VM.col(cols, "dist"); v_v = VM.col(cols, "v_act")
    s_max = min(S[-1], dist_v[-1]); grid = np.arange(0, s_max, 10.0)
    diff = np.interp(grid, S, V) * 3.6 - np.interp(grid, dist_v, v_v)
    return float(np.sqrt(np.mean(diff ** 2)))


def wheel_energy(T, S, V, A, grade, cyc, load):
    ep = VV.cycle_energy_params(cyc, load)
    dt = np.diff(T, append=T[-1] + 1.0)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(VV.G, ep["Crr"], V, A, dt, grade, ep["r_dyn"], 0.0)
    cdxa = np.interp(v_avg * 3.6, ep["cdxa_v"], ep["cdxa"])
    P = ep["mass"] * k_lin + ep["mass"] * k_roll + k_rot + ep["rho"] * cdxa * L
    E = P * dt
    return E[E > 0].sum() / 3.6e6, E[E < 0].sum() / 3.6e6


def run(cyc, load, variant, drag=None, g=None):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
    kw = VV.cycle_driver_kwargs(cyc, load)
    if g is not None:
        kw = dict(kw); kw["g"] = g
    if variant == "ref":
        return driver_model(s, v, stop, grad, *VACC, P_drag_loss=0.0, **kw)
    dv, df = drag
    return driver_model_dragtable(s, v, stop, grad, *VACC, drag_v_kmh=dv, drag_f=df, **kw)


def vecto_metrics(cols, s, v):
    da = VM.col(cols, "DriverAction").astype(int)
    vv = VM.col(cols, "v_act")
    dist = VM.col(cols, "dist")
    n = len(da)
    coast_roll = float(((da == 4) | (da == 2)).mean()) * 100
    # VECTO Coast/Roll rows that are INSIDE driving mode = overspeed roll: speed >= local
    # target (at/above target). Approximate with target interpolated from the cycle.
    s_wp, seg = seg_targets(s, v)
    tgt = np.array([seg[max(0, min(bisect.bisect_right(s_wp, float(d)) - 1, len(seg) - 1))] * 3.6 for d in dist])
    cr = (da == 4) | (da == 2)
    os_roll = float((cr & (vv >= tgt - 0.5)).mean()) * 100
    la = float((cr & (vv < tgt - 0.5)).mean()) * 100
    return coast_roll, la, os_roll, int((vv > 85).sum())


def main():
    runs = VM.run_files()
    print("Part D2/D8 — CORRECTED VECTO drivetrain drag (1.43-2.05 kN). F4 redo.\n")
    for cyc, load in RUN_LOADS:
        rf = RUNFILE[(cyc, load)]
        cols = VM.load_vmod(runs[rf]) if rf in runs else None
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
        s_wp, seg = seg_targets(s, v)
        vcoast, vla, vosr, vover = vecto_metrics(cols, s, v) if cols is not None else (0, 0, 0, -1)
        pw = VM.col(cols, "P_wheel_in"); dtv = VM.col(cols, "dt")
        vE = pw * dtv / 3600.0
        vEpos = float(vE[vE > 0].sum())

        cases = {
            "D1 (no drag)": run(cyc, load, "ref"),
            "D2 (VECTO drag)": run(cyc, load, "tbl", drag=(D2_V, D2_F)),
            "D3 (EU std)": run(cyc, load, "tbl", drag=(D3_V, D3_F)),
            "D5 (g=9.80665)": run(cyc, load, "ref", g=9.80665),
            "D8 (D2+D5)": run(cyc, load, "tbl", drag=(D2_V, D2_F), g=9.80665),
        }
        print(f"=== {cyc} {load} ===")
        print(f"  VECTO: Coast+Roll {vcoast:.2f}% (look-ahead {vla:.2f}% + overspeed-roll {vosr:.2f}%), "
              f"secs>85 {vover}, E_trac {vEpos:.1f} kWh")
        print(f"  {'case':16s} {'coast%':>7s} {'LA%':>6s} {'OSroll%':>7s} {'>85':>5s} {'RMS':>6s} {'Etrac':>6s} {'Ebrk':>7s}")
        for name, (T, S, V, A, gr, M) in cases.items():
            tot, la, osr = coast_split(S, V, M, s_wp, seg)
            rms = rms_vs_vecto(S, V, cols) if cols is not None else float("nan")
            Ep, En = wheel_energy(T, S, V, A, gr, cyc, load)
            print(f"  {name:16s} {tot:7.2f} {la:6.2f} {osr:7.2f} {over85(V):5d} {rms:6.2f} {Ep:6.1f} {En:7.1f}")
        print()


if __name__ == "__main__":
    main()
