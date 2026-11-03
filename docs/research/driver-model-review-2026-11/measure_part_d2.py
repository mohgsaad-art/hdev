"""Part D2 (+ D3, D5, D6, D8) — the decisive drag test (F4).

Uses driver_model_v_dragtable (faithful copy of the code of record, proven identical
with a zero table by test_dragtable_identity) with the drag FORCE table applied in BOTH
coast_acc and coast_distance. One change at a time.

Drag tables (wheel-side force vs speed), from the .vmod analysis (measure_part_d_energy):
  D2 = VECTO example drivetrain drag (component losses gbx+axle+motor+inertias)/v
  D3 = EU standard value 0.63-0.85 kN

Metrics vs VECTO: coast share (and the look-ahead-only sub-share), secs>85 km/h, speed
RMS @10 m, wheel traction/braking energy. One change at a time: D5 (g), D6 (step-avg
air drag note), D8 (D2+D5 together).

Run: python docs/research/driver-model-review-2026-11/measure_part_d2.py
"""
import os
import sys

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

D2_V = [0.0, 45.0, 55.0, 65.0, 75.0, 85.0, 130.0]
D2_F = [793.0, 793.0, 804.0, 888.0, 914.0, 949.0, 949.0]   # VECTO drivetrain drag [N]
D3_V = [0.0, 50.0, 90.0, 130.0]
D3_F = [630.0, 630.0, 850.0, 850.0]                         # EU standard value [N]


def coast_share(M):
    return float((np.asarray(M) == 3).mean()) * 100


def over85(V):
    return int((np.asarray(V) * 3.6 > 85).sum())


def rms_vs_vecto(S, V, cols):
    dist_v = VM.col(cols, "dist")
    v_v = VM.col(cols, "v_act")
    s_max = min(S[-1], dist_v[-1])
    grid = np.arange(0, s_max, 10.0)
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


def main():
    runs = VM.run_files()
    print("Part D2/D3/D5/D8 — drag table in coast_acc AND coast_distance (F4)\n")
    for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
        run_name = f"BEV_E2_{cyc}_ReferenceLoad_1Hz"
        cols = VM.load_vmod(runs[run_name]) if run_name in runs else None
        da = VM.col(cols, "DriverAction").astype(int) if cols is not None else None
        vecto_coast = float(((da == 4) | (da == 2)).mean()) * 100 if da is not None else float("nan")
        vecto_over = int((VM.col(cols, "v_act") > 85).sum()) if cols is not None else -1
        pw = VM.col(cols, "P_wheel_in") if cols is not None else None
        dtv = VM.col(cols, "dt") if cols is not None else None
        vE = (pw * dtv / 3600.0) if cols is not None else None
        vEpos = float(vE[vE > 0].sum()) if cols is not None else float("nan")

        cases = {
            "D1 (no drag)": run(cyc, "reference", "ref"),
            "D2 (VECTO drag)": run(cyc, "reference", "tbl", drag=(D2_V, D2_F)),
            "D3 (EU std drag)": run(cyc, "reference", "tbl", drag=(D3_V, D3_F)),
            "D5 (g=9.80665)": run(cyc, "reference", "ref", g=9.80665),
            "D8 (D2+D5)": run(cyc, "reference", "tbl", drag=(D2_V, D2_F), g=9.80665),
        }
        print(f"=== {cyc} (reference) — VECTO: coast {vecto_coast:.2f} %, secs>85 {vecto_over}, "
              f"E_trac {vEpos:.1f} kWh ===")
        print(f"  {'case':18s} {'coast%':>7s} {'secs>85':>8s} {'RMS kmh':>8s} {'E_trac':>7s} {'E_brake':>8s}")
        for name, (T, S, V, A, gr, M) in cases.items():
            rms = rms_vs_vecto(S, V, cols) if cols is not None else float("nan")
            Ep, En = wheel_energy(T, S, V, A, gr, cyc, "reference")
            print(f"  {name:18s} {coast_share(M):7.2f} {over85(V):8d} {rms:8.2f} {Ep:7.1f} {En:8.1f}")
        print()


if __name__ == "__main__":
    main()
