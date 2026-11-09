"""Drivetrain variants V-A..V-D for the EEA truck validation (Job 3), v2 rebuild. TEST-ONLY.

v2 fixes over v1 (see report R1,R5,R6,R7,R8):
  - imports the 3 Nov sourced loss/map builders instead of re-implementing them
    (docs/research/drivetrain-inputs-fallbacks-2026-11/_stdval.py and
     docs/research/drag-default-test-2026-11/_chain.py, _e2_drag.py);
  - NO NearestND fill: points outside a map/loss domain are counted as out-of-map and
    returned as NaN (R8). Nothing is silently clamped;
  - no assumed n_rated=3000 (R7): the rated point needs a declared full-load curve; when EEA
    cannot supply it the variant returns the "cannot run from EEA data" signal;
  - std axle is the truck value 70+20*i (Annex VII App.3), not the bus 52.5+15*i.

Nothing in src/ or the notebook is touched.
"""
import csv
import math
import os
import sys

import numpy as np
from scipy.interpolate import LinearNDInterpolator

RPM = 60 / (2 * math.pi)
VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")

# import the 3 Nov sourced modules (reuse, do not rebuild) -----------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "drivetrain-inputs-fallbacks-2026-11"))
sys.path.insert(0, os.path.join(_ROOT, "drag-default-test-2026-11"))
import _stdval as STD          # std_gearbox, std_axle_reg70, std_axle_vecto, std_motor, Drivetrain
import _chain as CHAIN         # make_chain('S'/'E'), electric_power, E2 geometry
import _e2_drag as E2DRAG      # build_drag_table (E2 coasting drag)

# V-A constant efficiencies. Source: 3 Nov drivetrain matrix
# (claude/results-drag-and-drivetrain-matrix-360km-2026-11-03.md; the notebook consumption_engine
# call has no values, so the 3 Nov matrix values are used and stated in the report).
VA_MOTOR, VA_INV, VA_GBX, VA_REGEN = 0.95, 0.95, 0.98, 0.95  # [3 Nov matrix]


# ---------------- map wrappers: LINEAR ONLY, out-of-domain -> NaN (R8) ----------------
class _EMapLinear:
    """Electric-machine map (n_rpm, T_Nm) -> P_el [W]. Linear interpolation only; points
    outside the convex hull of the map return NaN (NO nearest fill). R8."""
    def __init__(self, m):
        self.lin = LinearNDInterpolator(m[:, :2], m[:, 2])
        self._n_lo, self._n_hi = m[:, 0].min(), m[:, 0].max()
        self._t_lo, self._t_hi = m[:, 1].min(), m[:, 1].max()

    def __call__(self, n, T):
        return self.lin(n, T)  # NaN where outside

    def out_of_box(self, n, T):
        return (n < self._n_lo) | (n > self._n_hi) | (T < self._t_lo) | (T > self._t_hi)


class _LossLinear:
    """Transmission torque-loss map keyed (n_in, T_in - loss) -> loss. Linear only; NaN
    outside the hull (R8). input_side converts an output (n_out,T_out) to the input side."""
    def __init__(self, m_input_side, ratio):
        self.ratio = ratio
        pts = np.c_[m_input_side[:, 0], m_input_side[:, 1] - m_input_side[:, 2]]
        self.lin = LinearNDInterpolator(pts, m_input_side[:, 2])

    def input_side(self, n_out_rpm, T_out):
        n_in, T = n_out_rpm * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T)  # NaN outside
        return n_in, T + loss, loss


# ---------------- drivetrain spec ----------------
class DrivetrainSpec:
    def __init__(self, arch, axle_ratio, iepc_ratio, iepc_gears, n_gears, n_motors,
                 machine_type, rated_kw_total, max_cont_kw_total, r_dyn, wheel_motor,
                 diff_included):
        self.arch = arch
        self.axle_ratio = axle_ratio
        self.iepc_ratio = iepc_ratio
        self.iepc_gears = iepc_gears
        self.n_gears = n_gears
        self.n_motors = max(1, int(n_motors or 1))
        self.machine_type = (machine_type or "ASM").upper()
        self.rated_kw_total = rated_kw_total
        self.max_cont_kw_total = max_cont_kw_total
        self.r_dyn = r_dyn
        self.wheel_motor = wheel_motor
        self.diff_included = diff_included
        if arch == "E-IEPC":
            self.total_ratio = iepc_ratio if iepc_ratio else None
        else:
            self.total_ratio = axle_ratio if axle_ratio else None
        self.p_rated_per = (rated_kw_total * 1000.0 / self.n_motors) if rated_kw_total else None


# ---------------- V-A: via consumption_engine (handled in run_hdev; kept for reference) --
def traction_power_VA(P_wheel, M, V, v_no_regen):
    eff = VA_MOTOR * VA_INV * VA_GBX
    P = np.where(P_wheel > 0, P_wheel / eff, P_wheel * VA_REGEN)
    P = np.where(M == 3, 0.0, P)
    P = np.where((M == 4) & (V <= v_no_regen), 0.0, P)
    return P


# ---------------- V-C bus-generic motor map (de-normalised) ----------------
BUSMAP = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "GenericBusData")


def _read_num_csv(path, ncol=3, enc="latin-1"):
    rows = []
    with open(path, encoding=enc) as fh:
        for r in csv.reader(fh):
            cleaned = [c.strip().strip('"').strip() for c in r[:ncol]]
            try:
                rows.append([float(x) for x in cleaned])
            except (ValueError, IndexError):
                continue
    return np.array(rows)


def bus_generic_motor(machine_type, t_rated, n_rated, p_rated):
    """De-normalise the completed-bus normalised map for PSM or ASM.
    GenericBusElectricMotorData.cs / GenericBusEMBase.cs; maps
    EfficiencyMap_PSM_normalized.vmap / _ASM_normalized.vmap de-normalised
    n*=Nrated, T*=Trated, Pel*=Prated. R8: linear only, NaN outside."""
    mt = (machine_type or "ASM").upper()
    fname = "EfficiencyMap_PSM_normalized.vmap" if mt == "PSM" else "EfficiencyMap_ASM_normalized.vmap"
    norm = _read_num_csv(os.path.join(BUSMAP, fname), ncol=3)
    n = norm[:, 0] * n_rated
    T = norm[:, 1] * t_rated
    P_el = norm[:, 2] * p_rated
    return _EMapLinear(np.c_[n, T, P_el])


# ---------------- generic single-total-ratio chain, out-of-map aware (R8) ----------------
def map_chain_single_ratio(v_avg, P_wheel, use, r_dyn, total_ratio, n_motors, emap, adc_eff):
    """wheel -> single total ratio -> motor map. Returns (P_el[W], out_of_map_bool).
    out_of_map True where the demanded (n,T) is outside the motor map (NaN). R8: no fill."""
    n = len(v_avg)
    P_el = np.full(n, np.nan)
    out = np.zeros(n, dtype=bool)
    w = v_avg / r_dyn
    on = use & (w > 1e-3) & (P_wheel != 0)
    if not on.any():
        P_el[~on] = 0.0
        return P_el, out
    n_em = (w[on] * RPM) * total_ratio
    T_wheel = P_wheel[on] / w[on]
    T_em = T_wheel / total_ratio / n_motors
    pe = emap(n_em, T_em) * n_motors
    box = emap.out_of_box(n_em, T_em)
    nan = np.isnan(pe)
    bad = box | nan
    # mechanical ADC/transmission efficiency on the valid points
    pe_eff = np.where(pe > 0, pe / adc_eff, pe * adc_eff)
    idx = np.where(on)[0]
    P_el[idx] = pe_eff
    out[idx] = bad
    P_el[~on] = 0.0
    return P_el, out


def rated_point_from_fullload(fld_n, fld_T):
    """Rated point from a declared full-load curve: rated power = max(T*w). Returns
    (n_rated, t_rated, p_rated). EEA supplies no full-load curve -> caller passes None (R7)."""
    if fld_n is None:
        return None
    w = np.asarray(fld_n) / RPM
    P = np.asarray(fld_T) * w
    i = int(np.argmax(P))
    return float(fld_n[i]), float(fld_T[i]), float(P[i])
