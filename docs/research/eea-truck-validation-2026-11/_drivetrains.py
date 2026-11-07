"""Drivetrain variants V-A..V-D for the EEA truck validation (Job 3). TEST-ONLY.

Turns a per-row wheel-power trace (from HDEV force_engine + the driver model) into
battery-terminal traction power [W], for four drivetrain options. These are the same
four fallbacks tested on 3 Nov on VECTO example vehicles
(docs/research/drivetrain-inputs-fallbacks-2026-11, drag-default-test-2026-11); here
they are parameterised per real certified truck.

Nothing in src/ or the notebook is touched. Each formula carries a source tag.

Sources (opened, not from memory):
  Gearbox std loss  : Reg. 2017/2400 Annex VI App. 8 (AMT): Td0=Td1000=0.005*Tmax_in;
                      fT 0.04 indirect / 0.01 direct.  [_stdval.py / _chain.py, 3 Nov]
  Axle std loss     : VECTO generic axle GenericTransmissionComponentData.cs 24-127 +
                      Constants.GenericLossMapSettings (T0=52.5, T1=15, Td_n=150, eta 0.98).
  Motor std map     : Reg. Annex Xb App. 8 steps 6-7 (k_mn ASM table, x0.96, drag curve).
  Bus generic map   : VECTO GenericBusElectricMotorData.cs + GenericBusEMBase.cs; two
                      normalised maps EfficiencyMap_ASM_normalized.vmap /
                      _PSM_normalized.vmap, de-normalised n*=Nrated, T*=Trated, Pel*=Prated;
                      ADC eff 0.98 (ratio==1) else 0.96.
  E2 example        : Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2 (.vveh/.vgbx/
                      .vemo/.vemp): 2x 125kW/485Nm ASM, ADC 2.0, gears 3.86/1.93, axle 2.59,
                      CdA 4.83, MassMax 11.99 t, battery ~243 kWh.
"""
import csv
import math
import os

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

RPM = 60 / (2 * math.pi)
VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
E2 = os.path.join(VSRC, "Generic Vehicles", "Declaration Mode", "PEV", "GenericVehicleE2")
BUSMAP = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "GenericBusData")

# V-A constant efficiencies (the 3 Nov matrix values; the notebook consumption_engine call
# uses constant motor*inverter*gearbox). Stated in the report.
VA_MOTOR, VA_INV, VA_GBX, VA_REGEN = 0.95, 0.95, 0.98, 0.95


# ---------------- generic numeric helpers ----------------
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


class _Loss:
    """VECTO torque-loss map: points (n_in, T_in - loss) -> loss. input_side converts an
    output-shaft (n_out, T_out) to the input side. [TransmissionLossMap style, _chain.py]"""
    def __init__(self, m_input_side, ratio):
        self.ratio = ratio
        pts = np.c_[m_input_side[:, 0], m_input_side[:, 1] - m_input_side[:, 2]]
        self.lin = LinearNDInterpolator(pts, m_input_side[:, 2])
        self.near = NearestNDInterpolator(pts, m_input_side[:, 2])

    def input_side(self, n_out_rpm, T_out):
        n_in, T = n_out_rpm * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T)
        bad = np.isnan(loss)
        if bad.any():
            loss[bad] = self.near(n_in[bad], T[bad])
        return n_in, T + loss, loss


class _EMap:
    """Electric-machine map: (n_rpm, T_Nm) -> P_el [W] per machine."""
    def __init__(self, m):
        self.lin = LinearNDInterpolator(m[:, :2], m[:, 2])
        self.near = NearestNDInterpolator(m[:, :2], m[:, 2])

    def __call__(self, n, T):
        p = self.lin(n, T)
        bad = np.isnan(p)
        if bad.any():
            p[bad] = self.near(n[bad], T[bad])
        return p


# ---------------- standard-value component builders (parameterised) ----------------
def std_gearbox(ratio, tmax_in, direct=False):
    td = 0.005 * tmax_in
    fT = 0.01 if direct else 0.04
    n = np.array([0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000], float)
    T = np.linspace(-1.1 * tmax_in, 1.1 * tmax_in, 45)
    N, TT = np.meshgrid(n, T)
    N, TT = N.ravel(), TT.ravel()
    return _Loss(np.c_[N, TT, td + td * N / 1000 + fT * np.abs(TT)], ratio)


def vecto_axle(ratio, T0=52.5, T1=15.0, td_n=150.0, eta=0.98):
    """VECTO generic axle [GenericTransmissionComponentData.cs]; also used by V-C."""
    td0 = T0 + T1 * ratio
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out)
    N, TT = N.ravel(), TT.ravel()
    calc_n = np.where(N == 0, 50.0, N)
    lo = td0 * 0.5 + td0 * 0.5 * calc_n / td_n + np.abs(TT) / eta - np.abs(TT)
    return _Loss(np.c_[N * ratio, (TT + lo) / ratio, lo / ratio], ratio)


# Annex Xb App. 8 k_mn ASM coefficients
_K_ASM = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001,
          (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}


def std_motor(t_max, n_rated):
    """Annex Xb App. 8 step 6 standard motor efficiency map, per machine, P_el [W]."""
    wn = np.r_[0.02, np.arange(0.2, 4.0001, 0.2)]
    tn = np.r_[-np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, np.arange(0.05, 1.0001, 0.05)]
    W, Tn = np.meshgrid(wn, tn)
    W, Tn = W.ravel(), Tn.ravel()
    pl = sum(c * np.abs(Tn) ** m * np.abs(W) ** n for (m, n), c in _K_ASM.items())
    pm = Tn * W
    eta = np.maximum(np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96, 0)
    n_rpm, T = W * n_rated, Tn * t_max
    P_mech = T * n_rpm / RPM
    P_el = (1 - eta) * np.abs(P_mech) + P_mech
    return _EMap(np.c_[n_rpm, T, P_el])


# ---------------- VECTO completed-bus generic motor map (V-C) ----------------
def bus_generic_motor(machine_type, t_rated, n_rated, p_rated):
    """De-normalise the completed-bus normalised map for PSM or ASM.
    machine_type PSM -> PSM map; ASM/ESM/RM -> ASM map [GenericBusEMBase.cs 22-35]."""
    mt = (machine_type or "ASM").upper()
    fname = "EfficiencyMap_PSM_normalized.vmap" if mt == "PSM" else "EfficiencyMap_ASM_normalized.vmap"
    norm = _read_num_csv(os.path.join(BUSMAP, fname), ncol=3)
    n = norm[:, 0] * n_rated
    T = norm[:, 1] * t_rated
    P_el = norm[:, 2] * p_rated
    return _EMap(np.c_[n, T, P_el])


# ---------------- E2 example maps (V-D) ----------------
def e2_motor_map():
    em = _read_num_csv(os.path.join(E2, "GenericMap_125kW_485Nm.vemo"), ncol=3)  # n, T, P_el kW
    return _EMap(np.c_[em[:, :2], em[:, 2] * 1000.0])


def e2_axle_gears():
    axle = _Loss_from_vtlm(os.path.join(E2, "Axle_4x2_Tractor.vtlm"), 2.59)
    gears = {1: _Loss_from_vtlm(os.path.join(E2, "Gear_1.vtlm"), 3.86),
             2: _Loss_from_vtlm(os.path.join(E2, "Gear_2.vtlm"), 1.93)}
    return axle, gears


def _Loss_from_vtlm(path, ratio):
    # .vtlm is already an INPUT-side map: columns Input Speed[rpm], Input Torque[Nm],
    # Torque Loss[Nm]. _Loss keys on (n_in, T_in - loss) -> loss, and its input_side()
    # converts an output (n_out,T_out) to the input side with `ratio`.
    m = _read_num_csv(path, ncol=3)  # n_in, T_in, loss
    return _Loss(m, ratio)


# ---------------- drivetrain spec from the join ----------------
class DrivetrainSpec:
    """Per-truck geometry parsed from the EEA join row. r_dyn from the driven axle tyre."""
    def __init__(self, arch, axle_ratio, iepc_ratio, iepc_gears, n_motors,
                 machine_type, rated_kw_total, r_dyn, wheel_motor):
        self.arch = arch
        self.axle_ratio = axle_ratio       # E2/E3 final drive, or None
        self.iepc_ratio = iepc_ratio       # total IEPC ratio, or None
        self.iepc_gears = iepc_gears
        self.n_motors = max(1, int(n_motors or 1))
        self.machine_type = machine_type or "ASM"
        self.rated_kw_total = rated_kw_total
        self.r_dyn = r_dyn
        self.wheel_motor = wheel_motor
        # total ratio wheel->motor
        if arch == "E-IEPC":
            self.total_ratio = iepc_ratio if iepc_ratio else None
        else:
            self.total_ratio = axle_ratio if axle_ratio else None
        # rated point per machine (for std/bus maps). rated kW is combined; per machine:
        self.p_rated_per = (rated_kw_total * 1000.0 / self.n_motors) if rated_kw_total else None


def rated_point_from_power(p_rated_w, n_rated_rpm=None):
    """A simple rated (N,T) point from rated power. n_rated default 3000 rpm [ASSUMPTION,
    flagged]; T_rated = P/(2*pi*n/60). Used only to scale the normalised/std maps when the
    EEA data gives no full-load curve."""
    if p_rated_w is None:
        return None
    n_rated = n_rated_rpm or 3000.0
    t_rated = p_rated_w / (n_rated / RPM)
    return n_rated, t_rated, p_rated_w


# ---------------- the wheel-power -> battery traction power chains ----------------
def traction_power_VA(P_wheel, M, V, v_no_regen):
    """V-A: notebook consumption_engine constant efficiencies (0.95*0.95*0.98)."""
    eff = VA_MOTOR * VA_INV * VA_GBX
    P = np.where(P_wheel > 0, P_wheel / eff, P_wheel * VA_REGEN)
    P = np.where(M == 3, 0.0, P)
    P = np.where((M == 4) & (V <= v_no_regen), 0.0, P)
    return P


def _map_chain(v_avg, P_wheel, use, r_dyn, total_ratio, n_motors, emap, axle=None, gears=None,
               gear_fixed=2, adc_eff=1.0):
    """Generic map-based chain: wheel -> (axle,gearbox or single total ratio) -> motor map.
    If axle/gears given (E2 example), use them; else use a single total_ratio and only the
    motor map + adc_eff (used for IEPC and the bus-generic axle path handled by caller)."""
    n = len(v_avg)
    P_el = np.zeros(n)
    w = v_avg / r_dyn
    on = use & (w > 1e-3) & (P_wheel != 0)
    if not on.any():
        return P_el
    if axle is not None and gears is not None:
        n_ax, T_ax, _ = axle.input_side(w[on] * RPM, P_wheel[on] / w[on])
        n_gb, T_gb, _ = gears[gear_fixed].input_side(n_ax, T_ax)
        n_em = n_gb / 1.0
        T_em = T_gb / n_motors
    else:
        # single total ratio (wheel->motor). mechanical loss via adc_eff on driving.
        n_em = (w[on] * RPM) * total_ratio
        T_wheel = P_wheel[on] / w[on]
        T_em = T_wheel / total_ratio / n_motors
    pe = emap(n_em, T_em) * n_motors
    # apply a small mechanical transmission efficiency for the single-ratio path
    if axle is None:
        pe = np.where(pe > 0, pe / adc_eff, pe * adc_eff)
    P_el[on] = pe
    return P_el
