"""Part F measurement: the 1 s step — convergence with dt.

Runs the code of record at dt = 1.0, 0.5, 0.25 on the cycles present (coasting
ON, ILLUSTRATIVE E2) and reports how the main metrics move as the step shrinks:
trip time, standing time, coast share, wheel traction/braking energy, worst
deceleration ratio vs .vacc (the 1 s braking-peak artefact), and count of rows
above target+2.5 km/h.

No VECTO comparison here (BLOCKED). The point is convergence of the HDEV model
to its own dt->0 limit, which bounds the 1 s discretisation error.

Run: python docs/research/driver-model-review-2026-11/measure_part_f.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model.reference_copy import driver_model, interp1
from tests.driver_model import _vecto_data as D
from src.engine.force_engine import force_engine

G = 9.81
R_DYN = 0.5


def metrics(out, mass, Crr, vv, vacc_dec):
    T, S, V, A, grade, M = out
    dt = float(np.diff(T)[0]) if len(T) > 1 else 1.0
    dts = np.diff(T, append=T[-1] + dt)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, Crr, V, A, dts, grade, R_DYN, 0.0)
    rho, cdxa = 1.188, 4.83
    P = mass * k_lin + mass * k_roll + k_rot + rho * cdxa * L
    E = P * dts
    # worst deceleration ratio vs .vacc
    worst = 0.0
    for spd, acc in zip(V, A):
        dmax = interp1(float(spd), vv, vacc_dec)
        if acc < dmax - 1e-6:
            worst = max(worst, acc / dmax)
    return {
        "trip_time_s": float(T[-1] + dt),
        "stand_s": float((M == 0).sum()) * dt,
        "coast_pct": float((M == 3).mean()) * 100,
        "E_trac_kWh": float(E[E > 0].sum()) / 3.6e6,
        "E_brake_kWh": float(E[E < 0].sum()) / 3.6e6,
        "worst_dec_ratio": worst,
        "n_rows": len(T),
    }


def main():
    cycles = D.list_cycles()
    targets = [c for c in ("RegionalDelivery", "UrbanDelivery") if c in cycles]
    VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()
    vv = [x / 3.6 for x in VACC_V]
    m = D.E2_REF_MASS
    print("Part F — dt convergence (coasting ON, ILLUSTRATIVE E2 reference mass)\n")
    for name in targets:
        s, v, grad, stop = D.load_cycle(cycles[name])
        print(f"=== {name} ===")
        base = None
        for dt in (1.0, 0.5, 0.25):
            out = driver_model(s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC,
                               dt=dt, **D.coasting_kwargs(coast_mass=m))
            mt = metrics(out, m, D.E2_CRR, vv, VACC_DEC)
            if base is None:
                base = mt
            dtrac = (mt["E_trac_kWh"] - base["E_trac_kWh"]) / base["E_trac_kWh"] * 100 if base["E_trac_kWh"] else 0
            dbrake = (mt["E_brake_kWh"] - base["E_brake_kWh"]) / base["E_brake_kWh"] * 100 if base["E_brake_kWh"] else 0
            print(f"  dt={dt:4.2f}: rows={mt['n_rows']:6d} time={mt['trip_time_s']:8.1f}s "
                  f"stand={mt['stand_s']:6.1f}s coast%={mt['coast_pct']:5.2f} "
                  f"Etrac={mt['E_trac_kWh']:7.2f}({dtrac:+5.2f}%) "
                  f"Ebrake={mt['E_brake_kWh']:7.2f}({dbrake:+5.2f}%) "
                  f"worstDecRatio={mt['worst_dec_ratio']:.3f}")
        print()


if __name__ == "__main__":
    main()
