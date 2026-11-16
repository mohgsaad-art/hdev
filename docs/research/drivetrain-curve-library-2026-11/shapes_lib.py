"""Shape building blocks (Part A). Drives VECTO's generic vehicles over the VECTO declaration
cycles with Bob's notebook driver, then pushes the wheel power through `drivetrain` (Appendix A,
verbatim in reference_copy.py) with VECTO's own maps, and bins the result by load fraction.

Nothing here edits Bob's engine. The driver / force engine are the notebook copies used by the
v2 harness (hdev_test_module).
"""
import os
import sys

import numpy as np

import harness as HN               # sets sys.path for v2 modules, VECTO_SRC
import reference_copy as R

H = HN.H
REPO = R.REPO
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "docs", "research", "drag-default-test-2026-11"))
from tests.driver_model import _vecto_vehicle as VV      # noqa: E402  (3 Nov reference vehicle module)
import _e2_drag as E2DRAG                                 # noqa: E402  (3 Nov E2 drag table builder)

G = 9.80665          # DeclarationData.cs:72
RHO = 1.188          # DeclarationData.cs:74
V_NO_REGEN = 5.0 / 3.6
CYCLE_DIR = os.path.join(R.VECTO_SRC, "VectoCore", "VectoCore", "Resources", "Declaration", "MissionCycles")
CYCLES = {"Regional": "RegionalDelivery.vdri", "Urban": "UrbanDelivery.vdri", "LongHaul": "LongHaul.vdri",
          "Municipal": "MunicipalUtility.vdri", "Construction": "Construction.vdri"}
LOADINGS = {"reference": VV.PAYLOAD_REF, "low": 603.9176}      # low loading: 3 Nov close-out (E2 vsum 'Loading')
M_EMPTY = VV.M_VEHICLE


def load_cycle(name):
    s, v, g, stop = [], [], [], []
    with open(os.path.join(CYCLE_DIR, CYCLES[name])) as fh:
        for i, ln in enumerate(fh):
            if i == 0:
                continue
            p = ln.strip().split(",")
            if len(p) < 4:
                continue
            s.append(float(p[0])); v.append(float(p[1])); g.append(float(p[2])); stop.append(float(p[3]))
    return s, v, g, stop


def load_vacc():
    vv, aa, dd = [], [], []
    with open(os.path.join(R.E2_DIR, "Truck.vacc"), encoding="latin-1") as fh:
        next(fh)
        for ln in fh:
            p = ln.strip().split(",")
            if len(p) >= 3:
                vv.append(float(p[0])); aa.append(float(p[1])); dd.append(float(p[2]))
    return vv, aa, dd


def e2_vehicle_rows(cycle, load):
    """Wheel-power rows of the VECTO generic E2 truck (6570 kg + loading) on one declaration cycle.
    Same calls as the v2 gate (gate_e2.run): driver_model + force_engine, E2 drag table, crosswind CdxA."""
    mass = M_EMPTY + LOADINGS[load]
    crr = VV.crr_total_vecto(mass)
    s, v, g, stop = load_cycle(cycle)
    vv, va, vd = load_vacc()
    v_kmh, F, _ = E2DRAG.build_drag_table(130.0)
    T, S, V, A, grade, M = H.driver_model(s, v, stop, g, vv, va, vd, coast_mass=mass,
                                          m_red_wheels=VV.M_RED_WHEELS, cdxa_v=list(VV.CDXA_V),
                                          cdxa=list(VV.CDXA_REF), Crr=crr, rho=RHO, g=G,
                                          drag_v=v_kmh / 3.6, drag_F=F, P_max=None)
    dt = np.ones(len(T))
    k_lin, k_roll, k_rot, L, v_avg = H.force_engine(G, crr, V, A, dt, grade, VV.R_DYN, 0.0)
    cdxa_row = np.interp(v_avg * 3.6, VV.CDXA_V, VV.CDXA_REF)
    P_wheel = mass * k_lin + mass * k_roll + k_rot + RHO * cdxa_row * L
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    return dict(P_wheel=P_wheel, v_avg=v_avg, V=np.asarray(V, float), M=np.asarray(M), use=use, dt=dt,
                mass=mass, km=S[-1] / 1000.0, cycle=cycle, load=load, r_dyn=VV.R_DYN)


def vecto_map(a):  # same as reference_copy.vecto_loss_map
    """VECTO builds its transmission loss triangulation on (in-speed, IN-torque minus LOSS) =
    OUTPUT torque in input units: TransmissionLossMap.cs 76-77. `drivetrain` (Appendix A) uses the
    file's input-torque column. This converter gives `drivetrain` the VECTO coordinates (A4)."""
    b = np.array(a, float)
    b[:, 1] = a[:, 1] - a[:, 2]
    return b


def rotor_power(V, w_em_fn_ratio, inertia_total, dt):
    """Rotor inertia power [W] = I (w1^2 - w0^2) / 2 / dt  (VECTO Formulas.InertiaPower).
    V: speed per row (end of step) [m/s]; w_em_fn_ratio: speed ratio w_em / v [1/m]."""
    w = np.asarray(V) * w_em_fn_ratio
    w0 = np.concatenate(([0.0], w[:-1]))
    return inertia_total * (w ** 2 - w0 ** 2) / 2.0 / dt


# ----------------------------------------------------------------------------------------
# Chain S1 : VECTO generic E2  (2 motors + ADC 2.0 + 2-speed AMT + axle)
# ----------------------------------------------------------------------------------------
class ChainE2:
    P_rated_W = 250e3          # 2 x 125 kW  [VECTO GenericEMotor_125kW_485Nm.vemp max torque*speed; vmod P_E2-em_drive_max 250 kW]

    def __init__(self, fixed_maps=True, em_map=None, eta_adc=1.0, name="S1_E2"):
        self.name = name
        self.eta_adc = eta_adc
        e2 = R.load_e2()
        if em_map is not None:
            e2["em_map"] = em_map
        if fixed_maps:
            e2["axle_map"] = vecto_map(e2["axle_map"])
            e2["gear_maps"] = [vecto_map(m) for m in e2["gear_maps"]]
        self.e2 = e2
        self.n_gears = 2
        self.max_w = e2["em_limits"][0][0].max()

    def run_gear(self, rows, g):
        e2 = self.e2
        w_wheel = rows["v_avg"] / rows["r_dyn"]
        on_g = np.where(rows["use"], g, 0)
        ratio_total = e2["i_axle"] * e2["i_gears"][g - 1] * e2["i_adc"]
        P_rot = rotor_power(rows["V"], ratio_total / rows["r_dyn"], e2["n_em"] * e2["rotor_inertia"], rows["dt"])
        out = R.run_e2_drivetrain(e2, rows["P_wheel"], w_wheel, on_g, P_rot, eta_adc=self.eta_adc)
        w_em = w_wheel * ratio_total
        return out, w_em

    def evaluate(self, rows):
        """Gear rule: highest gear the motor can manage (Appendix A note). Returns dict of per-row arrays."""
        n = len(rows["P_wheel"])
        best = np.zeros(n, int)
        res = {}
        for g in range(self.n_gears, 0, -1):               # highest gear first (gear 2 = lowest ratio)
            out, w_em = self.run_gear(rows, g)
            ok = rows["use"] & (w_em <= self.max_w * (1 + 1e-9)) & ~out[7]
            take = ok & (best == 0)
            best[take] = g
            res[g] = (out, w_em)
        # rows where no gear is ok: take the gear with the lowest motor speed that is still allowed to be driven
        none = rows["use"] & (best == 0)
        best[none] = self.n_gears
        P_el = np.zeros(n); parts = np.zeros((4, n)); brakes = np.zeros(n); ext = np.zeros(n, bool); over = np.zeros(n, bool)
        w_em_sel = np.zeros(n)
        for g in range(1, self.n_gears + 1):
            sel = best == g
            out, w_em = res[g]
            P_el[sel] = out[0][sel]
            for k in range(4):
                parts[k][sel] = out[1 + k][sel] if k < 4 else 0
            brakes[sel] = out[5][sel]
            ext[sel] = out[6][sel]; over[sel] = out[7][sel]
            w_em_sel[sel] = w_em[sel]
        return dict(P_el=P_el, P_axle_loss=parts[0], P_gbx_loss=parts[1], P_adc_loss=parts[2], P_em_loss=parts[3],
                    P_to_brakes=brakes, extrapolated=ext, over_limit=over, gear=best, w_em=w_em_sel,
                    no_gear_ok=none)


# ----------------------------------------------------------------------------------------
# Chains S2 / S3 : IEPC (map in OUTPUT shaft coordinates) + axle
# ----------------------------------------------------------------------------------------
IEPC_DIR = os.path.join(R.PEV_DIR, "GenericIEPC")


def _read_fld(path):
    a = R._read_csv_numeric(path)
    return a[:, 0], a[:, 1], a[:, 2]          # n_out rpm, T_drive_out, T_recup_out (negative)


def _read_viepco(path):
    a = R._read_csv_numeric(path)
    a[:, 0] /= R.RPM
    a[:, 2] *= 1000.0
    return a


_ZERO_LOSS = np.array([[0.0, -1e6, 0.0], [0.0, 1e6, 0.0], [1e4, -1e6, 0.0], [1e4, 1e6, 0.0]])


def rated_point_vecto(n_rpm, T_drive):
    """VECTO GenericRatedPointHelper.GetRatedPointOfFullLoadCurveAtEM + ElectricMotorRatedSpeedHelper:
    rated speed = last speed before the power gradient departs by >20 % from the first gradient
    (Constants.cs 429 RatedSpeedGradientDelta = 0.2); rated torque = max drive torque; P = n*T."""
    w = np.asarray(n_rpm) / R.RPM
    P = w * np.asarray(T_drive)
    grad = np.diff(P) / np.diff(w)
    n_rated = None
    for i in range(1, len(w)):
        g_i = (P[i] - P[i - 1]) / (w[i] - w[i - 1])
        if abs(g_i / grad[0] - 1.0) > 0.2:
            n_rated = w[i - 1]
            break
    if n_rated is None:
        raise ValueError("Rated speed not found")
    t_rated = float(np.max(T_drive))
    return n_rated, t_rated, n_rated * t_rated


class ChainIEPC:
    """VECTO GenericIEPC example (folder IEPC_Gbx1Speed or IEPC_Gbx3Speed) behind the generic 4x2 axle.
    The .viepco maps are in OUTPUT shaft speed/torque of each gear (GenericBusIEPCData / IEPCMapReader),
    so the axle loss map is the only separate loss step; the IEPC map holds IEPC gear + motor + inverter."""

    def __init__(self, folder, name, maps, ratios, fld_file, axle_ratio, fixed_maps=True, iepc_map_override=None):
        d = os.path.join(IEPC_DIR, folder)
        self.name = name
        self.ratios = ratios
        self.axle_ratio = axle_ratio
        axle = R.read_vtlm(os.path.join(d, "Axle_4x2_Tractor.vtlm"))
        self.axle_map = vecto_map(axle) if fixed_maps else axle
        self.maps = iepc_map_override if iepc_map_override else [_read_viepco(os.path.join(d, m)) for m in maps]
        n_rpm, Td, Tg = _read_fld(os.path.join(d, fld_file))
        # FLD is given at the measurement gear = gear with ratio closest to 1 (GenericBusIEPCData.GetGearRatioAtMeasurement)
        self.g_meas = int(np.argmin([abs(r - 1.0) for r in ratios]))
        r_m = ratios[self.g_meas]
        self.fld_motor = (n_rpm / R.RPM * r_m, Td / r_m, Tg / r_m)   # motor speed [rad/s], T drive, T recup (IEPCFullLoadCurveReader)
        self.n_rated_motor, self.t_rated_motor, self.P_rated_W = rated_point_vecto(n_rpm * r_m, Td / r_m)
        self.P_rated_W = float(np.max(self.fld_motor[0] * self.fld_motor[1]))   # peak drive power of the FLD (for x)
        self.inertia = 0.5               # GenericIEPC_*.viepc Inertia (0.5 kg m2, file value)
        self.n_gears = len(ratios)

    def fld_for_gear(self, g):
        r = self.ratios[g - 1]
        w_m, Td, Tg = self.fld_motor
        w_out = w_m / r
        return (w_out, Td * r), (w_out, Tg * r)

    def run_gear(self, rows, g):
        w_wheel = rows["v_avg"] / rows["r_dyn"]
        on_g = np.where(rows["use"], 1, 0)
        r = self.ratios[g - 1]
        w_out = w_wheel * self.axle_ratio
        P_rot = rotor_power(rows["V"], self.axle_ratio * r / rows["r_dyn"], self.inertia, rows["dt"])
        drive, gen = self.fld_for_gear(g)
        out = R.drivetrain(rows["P_wheel"], w_wheel, on_g, self.axle_ratio, self.axle_map, [1.0], [_ZERO_LOSS],
                           1.0, 1.0, 1, self.maps[g - 1], drive, gen, P_rot, 0.0)
        w_motor = w_out * r
        return out, w_motor

    def evaluate(self, rows):
        n = len(rows["P_wheel"])
        best = np.zeros(n, int)
        res = {}
        max_w = self.fld_motor[0].max()
        for g in range(self.n_gears, 0, -1) if self.ratios[0] > self.ratios[-1] else range(1, self.n_gears + 1):
            pass
        # gears ordered by ratio: highest gear = smallest ratio
        order = sorted(range(1, self.n_gears + 1), key=lambda g: self.ratios[g - 1])
        for g in order:
            out, w_motor = self.run_gear(rows, g)
            ok = rows["use"] & (w_motor <= max_w * (1 + 1e-9)) & ~out[7]
            take = ok & (best == 0)
            best[take] = g
            res[g] = (out, w_motor)
        none = rows["use"] & (best == 0)
        best[none] = order[0]
        P_el = np.zeros(n); parts = np.zeros((4, n)); brakes = np.zeros(n); ext = np.zeros(n, bool); over = np.zeros(n, bool)
        for g in range(1, self.n_gears + 1):
            sel = best == g
            out, _ = res[g]
            P_el[sel] = out[0][sel]
            for k in range(4):
                parts[k][sel] = out[1 + k][sel]
            brakes[sel] = out[5][sel]; ext[sel] = out[6][sel]; over[sel] = out[7][sel]
        return dict(P_el=P_el, P_axle_loss=parts[0], P_gbx_loss=parts[1], P_adc_loss=parts[2], P_em_loss=parts[3],
                    P_to_brakes=brakes, extrapolated=ext, over_limit=over, gear=best, no_gear_ok=none)


def iepc_gbx1():
    return ChainIEPC("IEPC_Gbx1Speed", "S3a_IEPC_1speed", ["IEPC_Gbx1.viepco"], [4.65],
                     "IEPC_Gbx1_FLD_max.viepcp", 2.64)


def iepc_gbx3():
    return ChainIEPC("IEPC_Gbx3Speed", "S3b_IEPC_3speed", ["IEPC_Gbx3_1.viepco", "IEPC_Gbx3_2.viepco", "IEPC_Gbx3_3.viepco"],
                     [8.31, 4.65, 2.74], "IEPC_Gbx3_FLD_max.viepcp", 2.64)


# ----------------------------------------------------------------------------------------
# binning
# ----------------------------------------------------------------------------------------
# Bin edges of x = |P_wheel| / P_rated. Fine at low load where the efficiency changes fast and where
# trucks spend most of their time (city/regional); coarse near full load. State: shares of energy per bin
# are written next to the curve so a reader can see which bins matter.
EDGES = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50,
                  0.60, 0.80, 1.00, 1.50])


def chain_rows_table(chain, rows):
    """Per-row table for one vehicle/cycle run: x, side, wheel power, el power, losses per part."""
    ev = chain.evaluate(rows)
    Pw = rows["P_wheel"]
    use = rows["use"] & (np.abs(Pw) > 1.0)
    x = np.abs(Pw) / chain.P_rated_W
    drive = use & (Pw > 0)
    regen = use & (Pw < 0)
    return dict(x=x, drive=drive, regen=regen, P_wheel=Pw, P_el=ev["P_el"], ev=ev, dt=rows["dt"])


def bin_shape(tables, edges=EDGES):
    """Energy-weighted efficiency per x-bin, separately for driving and regen, whole chain and per part.
    Returns list of dict rows."""
    rows = []
    for side in ("drive", "regen"):
        X = np.concatenate([t["x"][t[side]] for t in tables])
        Pw = np.concatenate([t["P_wheel"][t[side]] for t in tables])
        Pe = np.concatenate([t["P_el"][t[side]] for t in tables])
        ev = {k: np.concatenate([t["ev"][k][t[side]] for t in tables])
              for k in ("P_axle_loss", "P_gbx_loss", "P_adc_loss", "P_em_loss", "P_to_brakes")}
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (X >= lo) & (X < hi)
            if not m.any():
                continue
            ew = np.abs(Pw[m]).sum()                                       # wheel energy [W s] (1 s rows)
            if side == "drive":
                eta = Pw[m].sum() / Pe[m].sum()                            # wheel energy / electric energy
                row_eta = Pw[m] / np.where(Pe[m] > 0, Pe[m], np.nan)
            else:
                eta = -Pe[m].sum() / (-Pw[m].sum())                        # recovered electric / wheel energy (incl. brake overflow)
                row_eta = Pe[m] / Pw[m]
            rows.append(dict(
                side=side, x_lo=lo, x_hi=hi, x_mid=float(np.sum(X[m] * np.abs(Pw[m])) / ew),
                eta=float(eta), n_rows=int(m.sum()), wheel_kwh=float(ew / 3.6e6),
                eta_p10=float(np.nanpercentile(row_eta, 10)), eta_p90=float(np.nanpercentile(row_eta, 90)),
                loss_axle=float(ev["P_axle_loss"][m].sum() / ew), loss_gearbox=float(ev["P_gbx_loss"][m].sum() / ew),
                loss_adc=float(ev["P_adc_loss"][m].sum() / ew), loss_motor=float(ev["P_em_loss"][m].sum() / ew),
                brake_overflow=float(-ev["P_to_brakes"][m].sum() / ew)))
    return rows


# ----------------------------------------------------------------------------------------
# VECTO generic (normalised) maps, de-normalised the VECTO way
# ----------------------------------------------------------------------------------------
BUS_DIR = os.path.join(R.VECTO_SRC, "VectoCore", "VectoCore", "Resources", "Declaration", "GenericBusData")


def _read_norm(fname):
    rows = []
    with open(os.path.join(BUS_DIR, fname), encoding="latin-1") as fh:
        next(fh)
        for ln in fh:
            p = [x.strip().strip('"') for x in ln.strip().split(",")]
            if len(p) >= 3 and p[0]:
                rows.append([float(x) for x in p[:3]])
    return np.array(rows)


GENERIC_GEAR_EFF = 0.96      # GenericBusIEPCData.cs 18  GenericGearEfficiency


def em_standard_map(mtype, n_rated_rad, t_rated):
    """GenericBusElectricMotorData.DeNormalizeData (cs 202-215): n*=NRated, T*=TRated, Pel*=PRated.
    Returns rows (rad/s, Nm, W) for ONE motor. mtype 'ASM' or 'PSM' (VECTO normalised maps)."""
    f = "EfficiencyMap_PSM_normalized.vmap" if mtype == "PSM" else "EfficiencyMap_ASM_normalized.vmap"
    a = _read_norm(f)
    return np.c_[a[:, 0] * n_rated_rad, a[:, 1] * t_rated, a[:, 2] * n_rated_rad * t_rated]


def iepc_bus_maps(fld_file_dir, fld_file, ratios, mtype):
    """GenericBusIEPCData.DeNormalizeData (cs 138-160) with axleRatio = 1 and axleEfficiency = 1
    (DifferentialIncluded = false). Returns one map per gear in OUTPUT shaft coordinates (rad/s, Nm, W)."""
    n_rpm, Td, _ = _read_fld(os.path.join(IEPC_DIR, fld_file_dir, fld_file))
    g_meas = int(np.argmin([abs(r - 1.0) for r in ratios]))
    r_m = ratios[g_meas]
    w = n_rpm / R.RPM
    P = w * Td
    n_rated = None
    for i in range(1, len(w)):
        grad0 = (P[1] - P[0]) / (w[1] - w[0])
        gi = (P[i] - P[i - 1]) / (w[i] - w[i - 1])
        if abs(gi / grad0 - 1.0) > 0.2:
            n_rated = w[i - 1]
            break
    t_drive = float(np.max(Td))
    n_rated_at = n_rated * 1.0 * r_m                                  # GetNRatedAtIEPC
    t_rated_at = t_drive / r_m / GENERIC_GEAR_EFF / 1.0 / 1.0         # GetTRatedAtIEPC
    p_rated_at = n_rated_at * t_rated_at
    f = "EfficiencyMap_IEPC_PSM_normalized.vmap" if mtype == "PSM" else "EfficiencyMap_IEPC_ASM_normalized.vmap"
    a = _read_norm(f)
    maps = []
    for r in ratios:
        n_out = a[:, 0] * n_rated_at / r / 1.0
        T = a[:, 1] * t_rated_at * r * 1.0 * np.where(a[:, 1] > 0, GENERIC_GEAR_EFF * 1.0, 1.0 / (GENERIC_GEAR_EFF * 1.0))
        Pel = a[:, 2] * p_rated_at
        maps.append(np.c_[n_out, T, Pel])
    return maps, (n_rated_at, t_rated_at)


def iepc_bus_chain(folder, name, fld_file, ratios, mtype):
    maps, _ = iepc_bus_maps(folder, fld_file, ratios, mtype)
    return ChainIEPC(folder, name, None, ratios, fld_file, 2.64, iepc_map_override=maps)


def e2_standard_motor_chain(mtype):
    """S4: EU standard-value / bus-generic normalised motor map on the E2 motor's own rated point
    (rated speed by the VECTO gradient rule on the E2 .vemp, rated torque = max drive torque)."""
    (w, Td), _ = R.read_vemp(os.path.join(R.E2_DIR, "GenericEMotor_125kW_485Nm.vemp"))
    n_r, t_r, _p = rated_point_vecto(w * R.RPM, Td)
    return ChainE2(em_map=em_standard_map(mtype, n_r, t_r), eta_adc=1.0, name="S4_std_motor_" + mtype), (n_r, t_r)


class ChainIEPCWheel:
    """VECTO GenericIEPC wheel-motor example (IEPC_Gbx1Speed-Whl1): one map per wheel unit in OUTPUT (wheel)
    coordinates, 2 units because NrOfDesignTypeWheelMotorMeasured = 1 (GenericBusIEPCData.cs 49:
    count = DesignTypeWheelMotor && NrOfDesignTypeWheelMotorMeasured == 1 ? 2 : 1). No axle gear."""

    def __init__(self):
        d = os.path.join(IEPC_DIR, "IEPC_Gbx1Speed-Whl1")
        self.name = "S3c_IEPC_wheel_1speed"
        self.map = _read_viepco(os.path.join(d, "IEPC_Gbx1Whl1.viepco"))
        n_rpm, Td, Tg = _read_fld(os.path.join(d, "IEPC_Gbx1Whl1_FLD_max.viepcp"))
        self.fld = ((n_rpm / R.RPM, Td), (n_rpm / R.RPM, Tg))
        self.n_units = 2
        self.ratio = 12.276                       # GenericIEPC_Gbx1Whl1.viepc Gears[0].Ratio
        self.inertia = 0.5 * 2                    # .viepc Inertia x count (GenericBusIEPCData.cs: Inertia * count)
        self.P_rated_W = float(self.n_units * np.max(self.fld[0][0] * self.fld[0][1]))
        self.n_gears = 1

    def evaluate(self, rows):
        w_wheel = rows["v_avg"] / rows["r_dyn"]
        on = np.where(rows["use"], 1, 0)
        P_rot = rotor_power(rows["V"], self.ratio / rows["r_dyn"], self.inertia, rows["dt"])
        # rotor inertia of the unit referred to the wheel side: map is in wheel coordinates, so add the
        # inertia power directly at map speed (the map speed is the wheel speed here)
        out = R.drivetrain(rows["P_wheel"], w_wheel, on, 1.0, _ZERO_LOSS, [1.0], [_ZERO_LOSS], 1.0, 1.0,
                           self.n_units, self.map, self.fld[0], self.fld[1], P_rot, 0.0)
        return dict(P_el=out[0], P_axle_loss=out[1], P_gbx_loss=out[2], P_adc_loss=out[3], P_em_loss=out[4],
                    P_to_brakes=out[5], extrapolated=out[6], over_limit=out[7], gear=on,
                    no_gear_ok=np.zeros(len(on), bool))
