"""Step 3 consumption chains S (EU standard values) and E (E2 component maps).

TEST-ONLY. Faithful port of the sourced chains in docs/research/inputs/
hdev_maps_test_v1.py (Chain E) and hdev_maps_test_v2.py (Chain S). Nothing in Bob's
engine is touched. Every ratio/constant carries a source tag in the two input scripts.

wheel power -> axle -> gearbox -> motor map -> battery electric power, per row.
Gear rule: gear 2 (VECTO uses gear 2 > 99 % of driving; 22 Oct close-out; confirmed on
Coast/Roll rows in Step 1). Regen cap from the motor generating-torque curve. No motor
power when coasting/stopped; no regen below 5 km/h.
"""
import csv
import math
import os

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

RPM = 60 / (2 * math.pi)

# E2 geometry [VECTO b8d6126: AMT.vgbx, BatteryElectricVehicle.vveh, Wheels.cs]
I_AXLE, I_GEAR, I_ADC, N_EM = 2.59, {1: 3.86, 2: 1.93}, 2.0, 2
R_DYN = 0.867 * 3.05 / (2 * math.pi)
V_NO_REGEN = 5 / 3.6
T_EM_MAX, N_RATED = 485.0, 2461.158914          # .vemp, per motor
TMAX_IN = N_EM * T_EM_MAX * I_ADC               # 1940 Nm [ASSUMPTION]

_VECTO = os.environ.get("VECTO_SRC", "/projects/sandbox/vecto-src")
E2 = os.path.join(_VECTO, "Generic Vehicles", "Declaration Mode", "PEV", "GenericVehicleE2")


def _csv(fname):
    path = os.path.join(E2, fname)
    rows = []
    with open(path, encoding="latin-1") as fh:
        for r in csv.reader(fh):
            try:
                rows.append([float(x) for x in r[:3]])
            except (ValueError, IndexError):
                continue
    return np.array(rows)


class _Loss:
    """VECTO loss map: points (n_in, T_in - loss) -> loss [TransmissionLossMap.cs:77,94]."""
    def __init__(self, m, ratio):
        self.ratio = ratio
        pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2])
        self.near = NearestNDInterpolator(pts, m[:, 2])

    def input_side(self, n_out_rpm, T_out):
        n_in, T = n_out_rpm * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T)
        bad = np.isnan(loss)
        if bad.any():
            loss[bad] = self.near(n_in[bad], T[bad])
        return n_in, T + loss, loss


class _EMap:
    def __init__(self, m):          # m: n, T (+drive), P_el [W] (+drawn)
        self.lin = LinearNDInterpolator(m[:, :2], m[:, 2])
        self.near = NearestNDInterpolator(m[:, :2], m[:, 2])

    def __call__(self, n, T):
        p = self.lin(n, T)
        bad = np.isnan(p)
        if bad.any():
            p[bad] = self.near(n[bad], T[bad])
        return p


# ---------- E2 example components (Chain E) ----------
def _em_example():
    em = _csv("GenericMap_125kW_485Nm.vemo")        # n, T, P_el kW
    return _EMap(np.c_[em[:, :2], em[:, 2] * 1000])


# ---------- EU standard-value components (Chain S) ----------
def _std_gearbox(ratio, tmax_in, direct=False):
    """Annex VI App. 8 AMT: Td0 = Td1000 = 0.005*Tmax_in; fT 0.01 direct / 0.04 indirect."""
    td = 0.005 * tmax_in
    fT = 0.01 if direct else 0.04
    n = np.array([0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000], float)
    T = np.linspace(-1.1 * tmax_in, 1.1 * tmax_in, 45)
    N, TT = np.meshgrid(n, T)
    N, TT = N.ravel(), TT.ravel()
    return _Loss(np.c_[N, TT, td + td * N / 1000 + fT * np.abs(TT)], ratio)


def _std_axle(ratio, T0=70.0, T1=20.0, eta=0.98):
    """Annex VII App. 3 single reduction: Td0 = 70 + 20*i WHEEL SIDE, eta 0.98.
    Output loss = Td0 + |T_out|/eta - |T_out|; moved to the input side as VECTO stores it.
    This is the corrected (wheel-side) build; the truck standard value, not the bus
    generic 52.5 + 15*i. [REG Annex VII App. 3 Table 1, consolidated 01.01.2026 p.306]"""
    td0 = T0 + T1 * ratio
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out)
    N, TT = N.ravel(), TT.ravel()
    loss_out = td0 + np.abs(TT) / eta - np.abs(TT)
    return _Loss(np.c_[N * ratio, (TT + loss_out) / ratio, loss_out / ratio], ratio)


def _std_motor(t_max, n_rated):
    """Annex Xb App. 8 step 6 k_mn (ASM/ESM/RM), eta x 0.96; per motor, P_el in W."""
    k = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001,
         (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}
    wn = np.r_[0.02, np.arange(0.2, 4.0001, 0.2)]
    tn = np.r_[-np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, np.arange(0.05, 1.0001, 0.05)]
    W, Tn = np.meshgrid(wn, tn)
    W, Tn = W.ravel(), Tn.ravel()
    pl = sum(c * np.abs(Tn) ** m * np.abs(W) ** n for (m, n), c in k.items())
    pm = Tn * W
    eta = np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96
    eta = np.maximum(eta, 0)
    n_rpm, T = W * n_rated, Tn * t_max
    P_mech = T * n_rpm / RPM
    P_el = (1 - eta) * np.abs(P_mech) + P_mech
    return _EMap(np.c_[n_rpm, T, P_el])


# regen cap from the generating-torque curve (per motor)
def _t_gen_max():
    fld = _csv("GenericEMotor_125kW_485Nm.vemp")
    fld = fld[np.argsort(fld[:, 0])]
    return lambda n: np.interp(n, fld[:, 0], np.abs(fld[:, 2]))


_T_GEN_MAX = _t_gen_max()


def make_chain(kind):
    """kind='S' standard values, 'E' E2 example maps. Returns (axle, gears, emap)."""
    if kind == "E":
        axle = _Loss(_csv("Axle_4x2_Tractor.vtlm"), I_AXLE)
        gears = {g: _Loss(_csv(f"Gear_{g}.vtlm"), I_GEAR[g]) for g in (1, 2)}
        emap = _em_example()
    elif kind == "S":
        axle = _std_axle(I_AXLE)
        gears = {g: _std_gearbox(I_GEAR[g], TMAX_IN) for g in (1, 2)}
        emap = _std_motor(T_EM_MAX, N_RATED)
    else:
        raise ValueError(kind)
    return axle, gears, emap


def electric_power(v_avg, P_wheel, use, axle, gears, emap, gear_fixed=2):
    """Battery electric power per row [W] from wheel power. gear 2 fixed by default."""
    n = len(v_avg)
    out = {k: np.zeros(n) for k in ("axle_loss", "gbx_loss", "em_loss", "P_el")}
    w = v_avg / R_DYN
    on = use & (w > 1e-3) & (P_wheel != 0)
    if not on.any():
        return out
    n_ax, T_ax, l_ax = axle.input_side(w[on] * RPM, P_wheel[on] / w[on])
    n_gb, T_gb, l_gb = gears[gear_fixed].input_side(n_ax, T_ax)
    n_em = n_gb * I_ADC
    T_em = T_gb / I_ADC / N_EM
    cap = -_T_GEN_MAX(n_em)
    T_em = np.maximum(T_em, cap)                # regen torque cap
    P_el = emap(n_em, T_em) * N_EM
    P_mech = T_em * N_EM * n_em / RPM
    out["axle_loss"][on] = l_ax * n_ax / RPM
    out["gbx_loss"][on] = l_gb * n_gb / RPM
    out["em_loss"][on] = P_el - P_mech
    out["P_el"][on] = P_el
    return out
