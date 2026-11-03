"""Part D — compare the code-of-record driver model against VECTO 5.1.6-RC .vmod.

Uses the VECTO generic-E2 reference vehicle reconstructed from harness v1.7
(_vecto_vehicle.py) and the real .vmod files in docs/research/vecto/. The HDEV
driver is run on the SAME .vdri cycle and reference mass VECTO used, then compared
row by resampled distance.

Metrics per cycle:
  1. speed vs distance every 10 m: mean difference and RMS
  2. time shares by mode (VECTO DriverAction -> HDEV mode, review Q12)
  3. seconds above target and above 85 km/h; max overspeed
  4. standing time and trip time
  5. coast/overspeed summary

Run: python docs/research/driver-model-review-2026-11/measure_part_d.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model.reference_copy import driver_model
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM


# which .vmod corresponds to which .vdri cycle + whether it is reference load
RUN_TO_CYCLE = {
    "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz": ("RegionalDelivery", "reference"),
    "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz": ("UrbanDelivery", "reference"),
    "BEV_E2_LongHaul_ReferenceLoad_1Hz": ("LongHaul", "reference"),
    "BEV_E2_RegionalDelivery_LowLoading_1Hz": ("RegionalDelivery", "low"),
    "BEV_E2_UrbanDelivery_LowLoading_1Hz": ("UrbanDelivery", "low"),
    "BEV_E2_LongHaul_LowLoading_1Hz": ("LongHaul", "low"),
}

VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()


def mode_shares(M):
    return {m: float((np.asarray(M) == m).mean()) * 100 for m in range(5)}


def vecto_mode_shares(cols):
    da = VM.col(cols, "DriverAction").astype(int)
    modes = np.array([VM.VECTO_ACTION_TO_MODE.get(int(x), -1) for x in da])
    return {m: float((modes == m).mean()) * 100 for m in range(5)}, da


def resample_speed_rms(S_hdev, V_hdev, dist_v, v_v, step=10.0):
    """RMS and mean speed difference (km/h) on a common 10 m distance grid."""
    s_max = min(S_hdev[-1], dist_v[-1])
    grid = np.arange(0, s_max, step)
    vh = np.interp(grid, S_hdev, V_hdev) * 3.6
    vv = np.interp(grid, dist_v, v_v)   # vmod v_act already km/h
    diff = vh - vv
    return float(np.mean(diff)), float(np.sqrt(np.mean(diff ** 2)))


def main():
    runs = VM.run_files()
    print("Part D — HDEV code of record vs VECTO 5.1.6-RC (generic E2, harness v1.7 vehicle)\n")
    for run, (cyc_name, load) in RUN_TO_CYCLE.items():
        if run not in runs:
            print(f"  [missing] {run}")
            continue
        cols = VM.load_vmod(runs[run])
        dist_v = VM.col(cols, "dist")
        v_v = VM.col(cols, "v_act")
        vtarg_v = VM.col(cols, "v_targ")
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc_name])

        # reference-load mass only (low-loading mass differs; see Part E note)
        T, S, V, A, gr, M = driver_model(
            s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC,
            **VV.driver_kwargs())

        mean_d, rms_d = resample_speed_rms(S, V, dist_v, v_v)
        hv = mode_shares(M)
        vv_sh, da = vecto_mode_shares(cols)

        # seconds above 85 km/h
        hdev_over85 = int((V * 3.6 > 85.0).sum())
        vecto_over85 = int((v_v > 85.0).sum())
        # seconds above target (above 50 km/h, allowing +2.5)
        hdev_over_t = int(np.sum((V * 3.6 - np.interp(S, s, v)) > 2.6))
        # standing: HDEV mode 0 rows; VECTO DriverAction Halt rows
        hdev_stand = int((M == 0).sum())
        vecto_stand = int((da == 0).sum())

        print(f"=== {run}  ({load} load) ===")
        print(f"  speed vs dist @10 m:  mean {mean_d:+.3f} km/h   RMS {rms_d:.3f} km/h")
        print(f"  mode % (stop/acc/cruise/coast/brake)")
        print(f"     HDEV : {hv[0]:.1f}/{hv[1]:.1f}/{hv[2]:.1f}/{hv[3]:.1f}/{hv[4]:.1f}")
        print(f"     VECTO: {vv_sh[0]:.1f}/{vv_sh[1]:.1f}/{vv_sh[2]:.1f}/{vv_sh[3]:.1f}/{vv_sh[4]:.1f}  (Roll+Coast folded into coast)")
        print(f"  coast share   HDEV {hv[3]:.2f} %   VECTO {vv_sh[3]:.2f} %")
        print(f"  secs >85 km/h HDEV {hdev_over85}   VECTO {vecto_over85}")
        print(f"  standing rows HDEV {hdev_stand}   VECTO {vecto_stand}   (trip time HDEV {T[-1]+1:.0f}s, VECTO {dist_v.size}s)")
        # raw VECTO action breakdown
        uniq = {VM.VECTO_ACTION_NAME.get(int(a), a): int((da == a).sum()) for a in sorted(set(da.astype(int)))}
        print(f"  VECTO raw actions: {uniq}")
        print()


if __name__ == "__main__":
    main()
