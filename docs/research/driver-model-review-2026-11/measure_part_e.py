"""Part E measurement: how much does the fixed reference coasting mass matter?

Runs the code of record with coast_mass = empty / reference / full for the
ILLUSTRATIVE generic-E2 set-up on the cycles present, then uses the repo's
force_engine to compute wheel energy (traction and braking) for each trace at
the ACTUAL mass. The "wrong-mass trace" error is: driver trace built at the
reference mass, but energy evaluated at empty/full mass, compared with the trace
built AND evaluated at that mass.

LIMITATION: the vehicle set-up (Crr, CdxA, masses) is ILLUSTRATIVE (harness v1.7
and the E2 component files were not supplied). The MAGNITUDES below are therefore
indicative of the mechanism, not certified E2 numbers. No VECTO comparison here.

Run: python docs/research/driver-model-review-2026-11/measure_part_e.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model.reference_copy import driver_model
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from src.engine.force_engine import force_engine


from tests.driver_model import _vecto_vehicle as VV

G = VV.G
R_DYN = VV.R_DYN   # [VECTO] real E2 dynamic wheel radius ~0.4209 m
CDXA_V = VV.CDXA_V
CDXA_REF = VV.CDXA_REF


def wheel_energy(T, S, V, A, grade, mass, Crr):
    """Positive (traction) and negative (braking) wheel energy [kWh] for a trace
    evaluated at `mass`, using the repo force_engine P_wheel at theta_red=0.

    CdxA is the real VECTO reference table interpolated at v_avg (not flat)."""
    dt = np.diff(T, append=T[-1] + 1.0)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(
        G, Crr, V, A, dt, grade, R_DYN, 0.0)
    rho = VV.RHO_VECTO
    cdxa = np.interp(v_avg * 3.6, CDXA_V, CDXA_REF)   # km/h lookup, VECTO ref table
    P = mass * k_lin + mass * k_roll + k_rot + rho * cdxa * L
    E = P * dt            # J per row
    E_pos = E[E > 0].sum() / 3.6e6
    E_neg = E[E < 0].sum() / 3.6e6
    return E_pos, E_neg


def coast_share(M):
    return float((M == 3).mean()) * 100.0


def main():
    cycles = D.list_cycles()
    targets = [c for c in ("RegionalDelivery", "UrbanDelivery", "LongHaul") if c in cycles]
    # real VECTO masses: empty = vehicle only; reference = +ref payload; full = TPMLM
    masses = {
        "empty": VV.M_VEHICLE,
        "reference": VV.M_REF,
        "full": VV.TPMLM,
    }
    VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()

    print("Part E — fixed reference coasting mass (VECTO E2 vehicle, harness v1.7 values)\n")
    for name in targets:
        s, v, grad, stop = D.load_cycle(cycles[name])
        print(f"=== {name} ===")
        # trace built at each mass (driver + energy both at that mass)
        traces = {}
        for mlabel, m in masses.items():
            crr_m = VV.crr_total_vecto(m)
            out = driver_model(s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC,
                               **VV.driver_kwargs(coast_mass=m))
            traces[mlabel] = (out, crr_m)
            T, S, V, A, gr, Mo = out
            Ep, En = wheel_energy(T, S, V, A, gr, m, crr_m)
            print(f"  mass={mlabel:9s} ({m:7.0f} kg): coast%={coast_share(Mo):5.2f}  "
                  f"E_traction={Ep:7.2f} kWh  E_braking={En:7.2f} kWh")
        # wrong-mass trace error: driver trace at REFERENCE mass, energy at empty/full
        (Tr, Sr, Vr, Ar, grr, Mor), _ = traces["reference"]
        print("  --- wrong-mass trace error (driver@reference, energy@actual) ---")
        for mlabel in ("empty", "full"):
            m = masses[mlabel]
            crr_m = VV.crr_total_vecto(m)
            # right: driver AND energy at this mass
            (Tc, Sc, Vc, Ac, grc, Moc), _ = traces[mlabel]
            Ep_right, En_right = wheel_energy(Tc, Sc, Vc, Ac, grc, m, crr_m)
            # wrong: driver at reference, energy at this mass
            Ep_wrong, En_wrong = wheel_energy(Tr, Sr, Vr, Ar, grr, m, crr_m)
            err_trac = (Ep_wrong - Ep_right) / Ep_right * 100 if Ep_right else 0.0
            err_brake = (En_wrong - En_right) / En_right * 100 if En_right else 0.0
            print(f"    {mlabel:6s}: traction err {err_trac:+6.2f} %   braking err {err_brake:+6.2f} %")
        print()


if __name__ == "__main__":
    main()
