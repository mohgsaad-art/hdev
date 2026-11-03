"""Part D — compare the code-of-record driver model against VECTO 5.1.6-RC .vmod.

CORRECTED (F1/F2): each cycle+load uses its OWN VECTO vehicle and mass:
  - Regional/Urban: RigidSolo, reference 9589.6 kg / low 7173.9 kg
  - LongHaul: truck+trailer (RigidTrailer, CdxA 6.13), reference 19811.2 / low 11273.9 kg
All masses, total RRC and CdxA source are from BEV_E2.vsum / SegmentTable (see
_vecto_vehicle.py). The HDEV driver is run on the same .vdri cycle at the same mass.

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


# run label -> (cycle, load). LongHaul now uses its own vehicle.
RUN_TO_CYCLE = {
    "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz": ("RegionalDelivery", "reference"),
    "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz": ("UrbanDelivery", "reference"),
    "BEV_E2_LongHaul_ReferenceLoad_1Hz": ("LongHaul", "reference"),
    "BEV_E2_RegionalDelivery_LowLoading_1Hz": ("RegionalDelivery", "low"),
    "BEV_E2_UrbanDelivery_LowLoading_1Hz": ("UrbanDelivery", "low"),
    "BEV_E2_LongHaul_LowLoading_1Hz": ("LongHaul", "low"),
}
CYCLE_VDRI = {"RegionalDelivery": "RegionalDelivery.vdri",
              "UrbanDelivery": "UrbanDelivery.vdri", "LongHaul": "LongHaul.vdri"}

VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()


def mode_shares(M):
    return {m: float((np.asarray(M) == m).mean()) * 100 for m in range(5)}


def resample_speed_rms(S_hdev, V_hdev, dist_v, v_v, step=10.0):
    s_max = min(S_hdev[-1], dist_v[-1])
    grid = np.arange(0, s_max, step)
    vh = np.interp(grid, S_hdev, V_hdev) * 3.6
    vv = np.interp(grid, dist_v, v_v)
    diff = vh - vv
    return float(np.mean(diff)), float(np.sqrt(np.mean(diff ** 2)))


def main():
    runs = VM.run_files()
    print("Part D — HDEV code of record vs VECTO 5.1.6-RC (per-cycle vehicle, F1/F2 fixed)\n")
    for run, (cyc_name, load) in RUN_TO_CYCLE.items():
        if run not in runs:
            print(f"  [missing] {run}")
            continue
        cols = VM.load_vmod(runs[run])
        dist_v = VM.col(cols, "dist")
        v_v = VM.col(cols, "v_act")
        da = VM.col(cols, "DriverAction").astype(int)
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc_name])

        kw = VV.cycle_driver_kwargs(cyc_name, load)
        T, S, V, A, gr, M = driver_model(s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, **kw)

        mean_d, rms_d = resample_speed_rms(S, V, dist_v, v_v)
        hv = mode_shares(M)
        hdev_over85 = int((V * 3.6 > 85.0).sum())
        vecto_over85 = int((v_v > 85.0).sum())
        hdev_stand = int((M == 0).sum())
        vecto_stand = int((da == 0).sum())
        vecto_coast = float(((da == 4) | (da == 2)).mean()) * 100

        print(f"=== {run}  ({load} load, mass {kw['coast_mass']:.0f} kg, CdxA0 "
              f"{'6.13' if cyc_name=='LongHaul' else '4.83'}) ===")
        print(f"  speed vs dist @10 m:  mean {mean_d:+.3f} km/h   RMS {rms_d:.3f} km/h")
        print(f"  coast %  HDEV {hv[3]:.2f}   VECTO(Coast+Roll) {vecto_coast:.2f}")
        print(f"  secs >85 km/h  HDEV {hdev_over85}   VECTO {vecto_over85}")
        print(f"  standing rows  HDEV {hdev_stand}   VECTO {vecto_stand}")
        print(f"  trip time  HDEV {T[-1]+1:.0f} s   VECTO {dist_v.size} s")
        uniq = {VM.VECTO_ACTION_NAME.get(int(a), a): int((da == a).sum()) for a in sorted(set(da.astype(int)))}
        print(f"  VECTO raw actions: {uniq}")
        print()


if __name__ == "__main__":
    main()
