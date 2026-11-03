"""Part D metric 7 + hypothesis h1: wheel energy and measured VECTO coasting drag.

From the real VECTO .vmod: sum positive/negative wheel power, and measure the
coasting resistance force VECTO actually applies during its Coast/Roll rows
(from P_air + P_roll + P_slope + component losses). Compares against the EU
standard-value drag (0.63-0.85 kN) and the earlier HDEV-measured 1.43-2.05 kN.

Run: python docs/research/driver-model-review-2026-11/measure_part_d_energy.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model import _vmod as VM

RUNS = [
    "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
    "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz",
    "BEV_E2_LongHaul_ReferenceLoad_1Hz",
]


def main():
    runs = VM.run_files()
    print("Part D metric 7 + h1 — VECTO wheel energy and measured coasting drag\n")
    for run in RUNS:
        if run not in runs:
            print(f"  [missing] {run}")
            continue
        c = VM.load_vmod(runs[run])
        dt = VM.col(c, "dt")
        v = VM.col(c, "v_act") / 3.6
        da = VM.col(c, "DriverAction").astype(int)
        p_wheel = VM.col(c, "P_wheel_in")        # kW at the wheels (traction demand)
        # wheel energy split
        E = p_wheel * dt / 3600.0                # kWh per row
        E_pos = E[E > 0].sum()
        E_neg = E[E < 0].sum()
        # VECTO brake energy (from P_brake_in, loss) if present
        try:
            p_brake = VM.col(c, "P_brake_in")
            E_brake = (p_brake * dt / 3600.0).sum()
        except KeyError:
            E_brake = float("nan")
        # coasting drag force during Coast/Roll rows: resistance = (P_air+P_roll+P_slope... )/v
        # use P_air + P_roll (+ gearbox/axle/EM loss if present) over v
        p_air = VM.col(c, "P_air")
        p_roll = VM.col(c, "P_roll")
        try:
            p_gbx = VM.col(c, "P_gbx_loss")
            p_axl = VM.col(c, "P_axle_loss")
        except KeyError:
            p_gbx = np.zeros_like(p_air)
            p_axl = np.zeros_like(p_air)
        coast_mask = (da == 4) | (da == 2)       # Coast or Roll
        band = {}
        for lo, hi in [(40, 50), (60, 70), (80, 90)]:
            m = coast_mask & (v * 3.6 >= lo) & (v * 3.6 < hi) & (v > 1)
            if m.sum() == 0:
                band[(lo, hi)] = None
                continue
            # resistance force [kN] = (P_air+P_roll+P_gbx+P_axl)[kW] / v[m/s]
            F = (p_air[m] + p_roll[m] + np.abs(p_gbx[m]) + np.abs(p_axl[m])) / v[m]
            band[(lo, hi)] = float(np.nanmean(F))
        print(f"=== {run} ===")
        print(f"  VECTO wheel energy: +{E_pos:.2f} kWh traction, {E_neg:.2f} kWh (neg at wheel)")
        print(f"  VECTO brake energy (P_brake_in): {E_brake:.2f} kWh")
        print(f"  VECTO coasting resistance force (air+roll+gbx+axle)/v, by speed band:")
        for (lo, hi), f in band.items():
            print(f"     {lo}-{hi} km/h: {'n/a' if f is None else f'{f:.2f} kN'}")
        print()


if __name__ == "__main__":
    main()
