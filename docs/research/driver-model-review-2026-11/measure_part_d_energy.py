"""Part D metric 7 + F3/F6 — VECTO wheel energy, coasting DRIVETRAIN drag, brake split.

F3 fix: the coasting DRIVETRAIN drag at the wheels is -P_wheel_in/v on Coast/Roll
rows (what the powertrain pulls back), NOT (P_air+P_roll+...)/v (that double-counts
air+roll). Cross-checked against the component columns:
  gearbox + axle + motor side (P_gbx_loss, P_axle_loss, P_E2-em_mech, P_E2-em_loss,
  P_E2-em_inertia_loss, P_gbx_inertia).

F6: P_brake_loss * dt sums to the .vsum E_brake (friction-brake energy); P_brake_in
is the power flowing INTO the brake component, not braking energy. Reports VECTO's
split of negative wheel energy into regen and friction braking.

Run: python docs/research/driver-model-review-2026-11/measure_part_d_energy.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model import _vmod as VM

RUNS = {
    "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz": ("RegionalDelivery.vdri", 3019.5882),
    "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz": ("UrbanDelivery.vdri", 3019.5882),
    "BEV_E2_LongHaul_ReferenceLoad_1Hz": ("LongHaul.vdri", 9841.1765),
}

BANDS = [(40, 50), (50, 60), (60, 70), (70, 80), (80, 90)]


def getcol(c, *names):
    try:
        return VM.col(c, *names)
    except KeyError:
        return None


def main():
    runs = VM.run_files()
    print("Part D metric 7 + F3/F6 — VECTO drivetrain coasting drag and brake split\n")
    for run, (vdri, loading) in RUNS.items():
        if run not in runs:
            print(f"  [missing] {run}")
            continue
        c = VM.load_vmod(runs[run])
        dt = VM.col(c, "dt")
        v = VM.col(c, "v_act") / 3.6
        da = VM.col(c, "DriverAction").astype(int)
        p_wheel = VM.col(c, "P_wheel_in")        # kW at the wheels
        E = p_wheel * dt / 3600.0
        E_pos = E[E > 0].sum()
        E_neg = E[E < 0].sum()

        # F6: brake split
        p_brake_loss = getcol(c, "P_brake_loss")
        E_brake_fric = float((p_brake_loss * dt / 3600.0).sum()) if p_brake_loss is not None else float("nan")
        vs = VM.vsum_row(vdri, loading)
        vsum_ebrake = vs.get("E_brake") if vs else None
        # regen = negative wheel energy recovered through the driveline (approx -E_neg minus friction)
        regen = -E_neg - E_brake_fric if np.isfinite(E_brake_fric) else float("nan")

        # F3: drivetrain drag at wheels on Coast/Roll rows = -P_wheel_in / v  (median per band)
        coast_mask = ((da == 4) | (da == 2)) & (v > 1)
        # component cross-check columns
        p_gbx_in = getcol(c, "P_gbx_in")   # motor drag flowing INTO the gearbox at zero torque
        p_gbx = getcol(c, "P_gbx_loss")
        p_axl = getcol(c, "P_axle_loss")
        p_em_mech = getcol(c, "P_E2-em_mech")
        p_em_loss = getcol(c, "P_E2-em_loss")
        p_em_inert = getcol(c, "P_E2-em_inertia_loss")
        p_gbx_inert = getcol(c, "P_gbx_inertia")

        print(f"=== {run} ===")
        print(f"  wheel energy: +{E_pos:.2f} kWh (traction), {E_neg:.2f} kWh (negative at wheel)")
        print(f"  F6 brake split: friction (Sum P_brake_loss*dt) = {E_brake_fric:.4f} kWh"
              f"  | .vsum E_brake = {vsum_ebrake}  | regen (approx) = {regen:.2f} kWh")
        print(f"  F3 drivetrain drag at wheels (-P_wheel_in/v) on Coast/Roll rows, median [kN] (n):")
        for lo, hi in BANDS:
            m = coast_mask & (v * 3.6 >= lo) & (v * 3.6 < hi)
            n = int(m.sum())
            if n == 0:
                print(f"     {lo}-{hi}: - (n 0)")
                continue
            F_wheel = -p_wheel[m] / v[m]          # kN (kW / (m/s))
            med = float(np.median(F_wheel))
            # CORRECT component-sum cross-check: P_gbx_in (motor drag through the box)
            # + P_gbx_loss + P_axle_loss, all /v. This equals -P_wheel_in/v.
            comp = np.zeros(n)
            for pc in (p_gbx_in, p_gbx, p_axl):
                if pc is not None:
                    comp = comp + np.abs(pc[m])
            comp_F = float(np.median(comp / v[m])) if comp.any() else float("nan")
            print(f"     {lo}-{hi}: {med:.2f} kN (n {n})   (|P_gbx_in|+|P_gbx_loss|+|P_axle_loss|)/v {comp_F:.2f} kN")
        print()


if __name__ == "__main__":
    main()
