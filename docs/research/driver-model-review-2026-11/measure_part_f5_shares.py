"""F5 — time shares using VECTO's OWN definitions.

VECTO (ModalDataContainerExtensions.cs, stable v5.1.3; same rules the prompt cites on
IEPC-experiments ~60-112 / 528-566), ALL time-weighted by dt:
  acceleration: a > 0.125 m/s^2
  deceleration: a < -0.125
  cruise:       v >= 0.1 km/h AND -0.125 <= a <= 0.125
  stop:         v < 0.1 km/h
  coasting/braking: by DrivingBehavior enum (NOT the acc threshold, NOT DriverAction)

These are SEPARATE classifications, not a partition — accel/decel/cruise overlap with
coasting/braking, so they do not sum to 100 as a clean split.

This script applies the acc-threshold rules to the HDEV rows and puts them next to the
.vsum values. For the coasting/braking (DrivingBehavior) shares we use VECTO's .vsum
values directly and HDEV modes 3/4 as the closest HDEV equivalent, clearly labelled.

Run: python docs/research/driver-model-review-2026-11/measure_part_f5_shares.py
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

RUNS = {
    "RegionalDelivery": ("RegionalDelivery.vdri", 3019.5882, "reference"),
    "UrbanDelivery": ("UrbanDelivery.vdri", 3019.5882, "reference"),
    "LongHaul": ("LongHaul.vdri", 9841.1765, "reference"),
}

VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()


def hdev_vecto_shares(T, S, V, A, M, dt=1.0):
    """Apply VECTO's threshold rules to HDEV rows (fixed dt)."""
    a = np.asarray(A)
    v = np.asarray(V)  # m/s
    vmin = 0.1 / 3.6
    dur = len(a) * dt
    acc = float((a > 0.125).sum()) * dt / dur * 100
    dec = float((a < -0.125).sum()) * dt / dur * 100
    cruise = float(((v >= vmin) & (a >= -0.125) & (a <= 0.125)).sum()) * dt / dur * 100
    stop = float((v < vmin).sum()) * dt / dur * 100
    # HDEV mode-based coast/brake (closest equivalent to VECTO DrivingBehavior)
    coast = float((np.asarray(M) == 3).sum()) * dt / dur * 100
    brake = float((np.asarray(M) == 4).sum()) * dt / dur * 100
    return dict(acc=acc, dec=dec, cruise=cruise, stop=stop, coast=coast, brake=brake)


def main():
    print("F5 — time shares, VECTO's own definitions (acc-threshold; coast/brake by DrivingBehavior)\n")
    for cyc, (vdri, loading, load) in RUNS.items():
        vs = VM.vsum_row(vdri, loading)
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
        kw = VV.cycle_driver_kwargs(cyc, load)
        T, S, V, A, gr, M = driver_model(s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, **kw)
        h = hdev_vecto_shares(T, S, V, A, M)
        print(f"=== {cyc} (reference) ===")
        print(f"  {'share':12s} {'HDEV':>8s} {'VECTO .vsum':>12s}")
        for key, vskey in [("acc", "AccelerationTimeShare"), ("dec", "DecelerationTimeShare"),
                           ("cruise", "CruiseTimeShare"), ("stop", "StopTimeShare"),
                           ("coast", "CoastingTimeShare"), ("brake", "BrakingTimeShare")]:
            vsv = vs.get(vskey) if vs else None
            tag = "  (DrivingBehavior)" if key in ("coast", "brake") else ""
            print(f"  {key:12s} {h[key]:8.2f} {('%.2f' % vsv) if vsv is not None else 'n/a':>12s}{tag}")
        tot_h = h['acc'] + h['dec'] + h['cruise'] + h['stop']
        print(f"  (acc+dec+cruise+stop HDEV = {tot_h:.1f} %; not a partition with coast/brake)")
        print()


if __name__ == "__main__":
    main()
