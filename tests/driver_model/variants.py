"""Experimental variants of the code-of-record helpers / driver model.

Kiro is forbidden to edit Bob's engine, so every proposed change is prototyped
here beside the reference copy, clearly named, and reported as a before/after
snippet with its measured effect. These variants are NOT used by the engine.

Variants:
  coast_distance_v_atan   — Part D4 hypothesis: apply math.atan to grad in the
                            rolling term. Source check (Q3): VECTO does NOT do
                            this (Vehicle.cs RollingResistance uses cos of the raw
                            rise/run radian). So this variant DEVIATES from VECTO;
                            it exists only to measure the size of the change.
  coast_acc_v_avgdrag     — Part D6 hypothesis: use the step-average air-drag form
                            (as VECTO / the HDEV force engine) instead of the
                            instantaneous rho/2*CdA*v^2 in coast_acc.
"""
import math

import numpy as np

from tests.driver_model.reference_copy import interp1


def coast_distance_v_atan(v, v_target, h_now, h_target, s_now, s_target,
                          coast_mass, m_red_wheels, cdxa_v, cdxa, Crr, rho, g, P_drag_loss,
                          df_offset, df_scaling, df_vtarget, df_vdrop):
    """Code of record with math.atan applied to grad in F_roll (D4 hypothesis)."""
    m_eff = coast_mass + m_red_wheels
    dE = m_eff * g * (h_now - h_target) + m_eff * (v ** 2 - v_target ** 2) / 2
    v_avg = (v + v_target) / 2
    cda = interp1(v_avg, cdxa_v, cdxa)
    F_air = rho / 8 * cda * (v + v_target) * (v ** 2 + v_target ** 2) / v_avg
    grad = (h_target - h_now) / (s_target - s_now)
    F_roll = math.cos(math.atan(grad)) * coast_mass * g * Crr   # <-- atan added
    F_loss = P_drag_loss / v
    f_vt = interp1(v_target * 3.6, df_vtarget[0], df_vtarget[1])
    f_vd = interp1((v - v_target) * 3.6, df_vdrop[0], df_vdrop[1])
    DF = df_offset - df_scaling * f_vt * f_vd
    return dE / (DF * (F_air + F_roll + F_loss))


def coast_acc_avgdrag(v, v_prev, cv, cc, coast_mass, m_red_wheels, Crr, rho, g,
                      grade_pct, P_drag_loss):
    """Step-average air-drag coast acceleration (D6 hypothesis).

    Uses the VECTO / force-engine average 0.5*v^3 ~ (v1+v2)(v1^2+v2^2)/8 over the
    step instead of the instantaneous rho/2*CdA*v^2. Needs the previous-step speed
    v_prev; here we approximate the step with (v_prev, v)."""
    m_eff = coast_mass + m_red_wheels
    th = math.atan(grade_pct / 100)
    v_avg = (v + v_prev) / 2 if (v + v_prev) > 0 else v
    cda = interp1(v_avg, cv, cc)
    L = (v + v_prev) * (v ** 2 + v_prev ** 2) / 8 if (v + v_prev) > 0 else v ** 3 / 2
    F_air = rho * cda * L / v_avg if v_avg > 0 else 0.0   # force = power/v_avg
    F = (F_air
         + coast_mass * g * Crr * math.cos(th)
         + coast_mass * g * math.sin(th)
         + (P_drag_loss / v if v > 0 else 0.0))
    return -F / m_eff


# ---------------------------------------------------------------------------
# D2 — drivetrain coasting-drag TABLE (drag force vs speed) in coast_acc and
# coast_distance, instead of the scalar P_drag_loss. (F4)
#
# The table is the VECTO example drivetrain drag at the wheels, built from the
# .vmod component-loss columns on Coast/Roll rows (gearbox + axle + motor losses
# + inertias)/v, median per 10 km/h band (see measure_part_d2.py). It is a drag
# FORCE [N] vs speed [km/h]; it is ADDED to the existing air + rolling + slope.
# ---------------------------------------------------------------------------
import numpy as _np
from tests.driver_model.reference_copy import driver_model as _driver_model


# The runnable D2 variant is tests/driver_model/driver_model_v_dragtable.py — a
# faithful copy of the code of record whose coast_acc / coast_distance use a drag
# FORCE table F(v) [N] in place of the scalar P_drag_loss. It is proven byte-identical
# to the code of record with a zero table by tests/driver_model/test_dragtable_identity.py.
# measure_part_d2.py drives it for D2/D3/D5/D8.

# VECTO example drivetrain drag table (wheel side), from the .vmod component-loss
# columns on Coast/Roll rows, Reg+Urban+LongHaul reference (measure_part_d2.py). [VECTO][TEST]
VECTO_DRIVETRAIN_DRAG_V_KMH = [0.0, 45.0, 55.0, 65.0, 75.0, 85.0, 130.0]
VECTO_DRIVETRAIN_DRAG_N = [793.0, 793.0, 804.0, 888.0, 914.0, 949.0, 949.0]
