"""Shared harness for the drivetrain-inputs fallback tests (3 Nov 2026). TEST-ONLY.

Runs the code-of-record driver_model on the VECTO mission cycles at the real E2
reference vehicle (from tests/driver_model/_vecto_vehicle.py), then turns the wheel
trace into battery kWh/km with the standard-value drivetrain (_stdval.Drivetrain).

No engine file is touched. The driver model's drag is fed through P_drag_loss as a
callable-via-float object (the 22 Oct DragPower trick) so coast_acc / coast_distance
get a real drag FORCE(v) without editing the engine. A separate path (drag_v/drag_F
table on a TEST-ONLY copy of the driver model) is used for Part D7.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tests.driver_model.reference_copy import driver_model
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from src.engine.force_engine import force_engine

import _stdval as S

CYCLES = ["RegionalDelivery", "UrbanDelivery", "MunicipalUtility"]
V_NO_REGEN = 5.0 / 3.6          # below this, regen off (consumption-engine rule)
P_AUX = 0.0                     # auxiliaries out of scope for this study (focus: drivetrain)


class DragPower(float):
    """A float whose plain value is the drag power at 70 km/h, but whose division by a
    speed v returns the drag FORCE at v (coast_acc does P_drag_loss / v). This lets the
    unmodified code-of-record driver model consume a full drag table. [TEST 22 Oct]"""
    def __new__(cls, v_tab, f_tab):
        obj = float.__new__(cls, float(np.interp(70 / 3.6, v_tab, f_tab) * 70 / 3.6))
        obj._v = v_tab
        obj._f = f_tab
        return obj

    def __truediv__(self, v):
        return float(np.interp(float(v), self._v, self._f))


def load_vacc():
    return D.load_vacc()


def run_driver(cycle_name, coast_mass=None, drag=None, r_dyn=None,
               cdxa_v=None, cdxa=None, Crr=None):
    """Run the code-of-record driver model at the reference vehicle with optional drag.

    drag: None (no drivetrain drag) or (v_tab, f_tab) drag table -> DragPower.
    Returns driver arrays (T, S, V, A, grade, M)."""
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cycle_name])
    vacc_v, vacc_acc, vacc_dec = load_vacc()
    kw = VV.driver_kwargs(coast_mass=VV.M_REF if coast_mass is None else coast_mass)
    if cdxa_v is not None:
        kw["cdxa_v"] = cdxa_v
    if cdxa is not None:
        kw["cdxa"] = cdxa
    if Crr is not None:
        kw["Crr"] = Crr
    if drag is not None:
        kw["P_drag_loss"] = DragPower(drag[0], drag[1])
    return driver_model(s, v, stop, grad, vacc_v, vacc_acc, vacc_dec, **kw)


def wheel_power(T, S_, V, A, grade, mass, Crr, r_dyn):
    """P_wheel per row [W] at the real reference CdxA table."""
    dt = np.diff(T, append=T[-1] + 1.0)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(VV.G, Crr, V, A, dt, grade, r_dyn, 0.0)
    cdxa = np.interp(v_avg * 3.6, VV.CDXA_V, VV.CDXA_REF)
    P = mass * k_lin + mass * k_roll + k_rot + VV.RHO_VECTO * cdxa * L
    return P, v_avg, dt


def battery_kwh_per_km(cycle_name, dt_obj, coast_mass=None, drag=None):
    """Full chain: driver -> wheel power -> battery electric energy via the
    standard-value drivetrain dt_obj (an _stdval.Drivetrain). Returns a dict of results."""
    mass = VV.M_REF if coast_mass is None else coast_mass
    Crr = VV.crr_total_vecto(mass)
    r_dyn = dt_obj.r_dyn
    out = run_driver(cycle_name, coast_mass=mass, drag=drag)
    T, Sr, V, A, grade, M = out
    P_wheel, v_avg, dt = wheel_power(T, Sr, V, A, grade, mass, Crr, r_dyn)
    # consumption on/off rule (same as the 22 Oct add-on / consumption engine):
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    P_use = np.where(use, P_wheel, 0.0)
    P_el, parts, gear = dt_obj.electric_power(v_avg, P_use, use, v_no_regen=V_NO_REGEN)
    km = Sr[-1] / 1000.0
    E_batt = float(np.sum(P_el * dt) / 3.6e6) + P_AUX
    E_regen = -float(np.sum(np.minimum(P_el, 0) * dt) / 3.6e6)
    return dict(
        cycle=cycle_name, km=km, kwh_km=E_batt / km, E_batt=E_batt, E_regen=E_regen,
        coast_pct=float(np.mean(M == 3) * 100), trip_s=len(M),
        E_loss_axle=float(np.sum(parts["axle"] * dt) / 3.6e6),
        E_loss_gearbox=float(np.sum(parts["gearbox"] * dt) / 3.6e6),
        E_loss_motor=float(np.sum(parts["motor"] * dt) / 3.6e6),
        gear1_s=int(np.sum(gear == 1)),
    )
