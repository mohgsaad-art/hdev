"""Part F numbers from the E2 .vmod files: regen share, battery Ri loss, aux while standing, rows without gear.  Deterministic.
Sign: HDEV convention in this script (+ = drawn from the battery)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import _e2 as E
from _common import write_csv
rows = []
for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
    for ld in ("ReferenceLoad", "LowLoading"):
        rw = E.vecto_rows(cyc, ld); v = rw["vecto"]; dt = rw["dt"]; km = rw["S"][-1] / 1000
        k = lambda x: float(np.sum(x * dt) / 3.6e6)
        wheel_brake = k(np.minimum(v["P_wheel_in"], 0))                       # kWh, negative
        regen_batt = k(np.minimum(-v["P_E2-em_el"], 0))                       # kWh at the motor terminals, negative
        loss = k(v["P_REESS_int"] * 0 + (-v["P_REESS_int"]) - (-v["P_REESS_T"]))   # internal minus terminal energy [kWh]
        stand = rw["V"] == 0
        stand_true = rw["M"] == 0
        rows.append(dict(cycle=cyc, loading=ld, km=km, wheel_braking_kWh=wheel_brake, regen_at_motor_kWh=regen_batt,
                         regen_share_of_wheel_braking_pct=100 * regen_batt / wheel_brake,
                         friction_brake_kWh=k(v["P_brake_loss"]),
                         E_terminal_kWh=k(-v["P_REESS_T"]), E_internal_kWh=k(-v["P_REESS_int"]),
                         Ri_loss_kWh_signed=k(-v["P_REESS_int"]) - k(-v["P_REESS_T"]), Ri_loss_pct_of_terminal=100 * (k(-v["P_REESS_int"]) / k(-v["P_REESS_T"]) - 1),
                         aux_standing_kWh=k(np.where(stand_true, v["P_aux_el"], 0)), aux_total_kWh=k(v["P_aux_el"]),
                         aux_standing_pct_of_terminal=100 * k(np.where(stand_true, v["P_aux_el"], 0)) / k(-v["P_REESS_T"]),
                         standing_rows=int(stand_true.sum()), standing_h=float(stand_true.sum() / 3600),
                         gear0_moving_rows=int(((rw["gear"] == 0) & (rw["V"] > 0.5)).sum()),
                         gear0_moving_wheel_kWh=k(np.where((rw["gear"] == 0) & (rw["V"] > 0.5), v["P_wheel_in"], 0))))
write_csv("partF_vmod_numbers.csv", rows)
for r in rows: print({k_: (round(x, 3) if isinstance(x, float) else x) for k_, x in r.items()})
