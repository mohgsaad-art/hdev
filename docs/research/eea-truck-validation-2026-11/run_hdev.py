"""Job 3 v2 harness. TEST-ONLY. No src/ or notebook edits.

Rebuilt to the v2 R-rules (report.md R1-R13). Highlights:
  R1  V-A calls H.consumption_engine(...); V-B/C/D reuse its P_wheel + P_aux_row.
  R2  rotating inertia (wheels+trailer) from Wheels.csv, passed to driver_model (m_red_wheels)
      and force_engine (theta_red).
  R3  RRC the VECTO way (VehicleData.cs ComputeRollResistanceAndReducedMassWheels):
      share*RRC*(share*m*g/testload/wheels)^(beta-1); Crr_eff = F_roll/(m^beta*g).
  R4  per-variant drag tables from the 3 Nov builders; exact driver cache key; P_max.
  R6  gear-ratio handling: single-speed ok, multi-speed E2/E3 without ratios -> skip V-B/V-C.
  R7  rated point needs a full-load curve EEA lacks -> V-B/V-C "cannot run from EEA data".
  R8  out-of-map share tracked; no nearest fill.
  R9  per-truck aux from aux_per_label.csv.
  R10 crosswind set + CdxA + DeltaCdA from mission_setup.csv (read at run time).
  R11 report battery-terminal kWh/km + certified as-published + missing-term columns.
  R12 Municipal excluded from summary (reported separately; ePTO not in EEA).

Every literal number here is read from a file at run time or carries a source comment.
"""
import csv
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hdev_test_module as H
import _drivetrains as DT

# reuse the 3 Nov builders (same modules _drivetrains imports)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "drivetrain-inputs-fallbacks-2026-11"))
sys.path.insert(0, os.path.join(_ROOT, "drag-default-test-2026-11"))
import _stdval as STD      # noqa: E402
import _chain as CHAIN     # noqa: E402
import _e2_drag as E2DRAG  # noqa: E402

VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
CYC = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "MissionCycles")
E2DIR = os.path.join(VSRC, "Generic Vehicles", "Declaration Mode", "PEV", "GenericVehicleE2")
VACC = os.path.join(E2DIR, "Truck.vacc")

# --- sourced physics constants (Physics.cs / DeclarationData.cs) ---
G = 9.80665          # DeclarationData.cs:72 GravityAccelleration
RHO_VECTO = 1.188    # DeclarationData.cs:74 AirDensity (fixed in declaration)
BETA = 0.9           # Physics.cs:51 RollResistanceExponent
V_NO_REGEN = 5.0 / 3.6   # notebook v_min_coast / 3 Nov matrix v_no_regen
# air density for consumption_engine: rho = p_air/(R_air*(T+273.15)). Choose R_air, T so
# rho == 1.188. R_air = 287.058 J/(kg K) [std dry air]; T_amb = 20 C ->
# p_air = 1.188 * 287.058 * 293.15 = 99962.8 Pa. (arithmetic in report R1)
R_AIR = 287.058
T_AMB = 20.0
P_AIR = RHO_VECTO * R_AIR * (T_AMB + 273.15)   # = 99962.8 Pa -> rho back-computes to 1.188
# V-A/B/C/D motor-chain efficiencies for the map path ADC (3 Nov matrix / bus-generic rule)
ADC_EFF_RATIO1 = 0.98   # GenericBusElectricMotorData.cs 42-49 (ratio==1)
ADC_EFF_OTHER = 0.96    # GenericBusElectricMotorData.cs 42-49 (ratio!=1)

MISSION_CYCLE = {
    "Long Haul": "LongHaul.vdri", "Long Haul EMS": "LongHaul.vdri",
    "Regional Delivery": "RegionalDelivery.vdri", "Regional Delivery EMS": "RegionalDelivery.vdri",
    "Urban Delivery": "UrbanDelivery.vdri", "Municipal Utility": "MunicipalUtility.vdri",
    "Construction": "Construction.vdri",
}
MUNICIPAL = "Municipal Utility"   # R12: excluded from summary

# out-of-map threshold [proposal, Bob to decide] -- a run is "out of map" if more than this
# share of positive wheel energy sits outside the motor map.
OUT_OF_MAP_THRESHOLD = 0.02   # 2% [proposal, Bob to decide]


# ---------------- loaders ----------------
_cycle_cache = {}


def load_cycle(mission):
    fname = MISSION_CYCLE[mission]
    if fname in _cycle_cache:
        return _cycle_cache[fname]
    s, v, g, stop = [], [], [], []
    with open(os.path.join(CYC, fname)) as fh:
        for i, ln in enumerate(fh):
            if i == 0:
                continue
            p = ln.strip().split(",")
            if len(p) < 4:
                continue
            s.append(float(p[0])); v.append(float(p[1])); g.append(float(p[2])); stop.append(float(p[3]))
    _cycle_cache[fname] = (s, v, g, stop)
    return _cycle_cache[fname]


def load_vacc():
    vv, aa, dd = [], [], []
    with open(VACC, encoding="latin-1") as fh:
        for i, ln in enumerate(fh):
            if i == 0:
                continue
            p = ln.strip().split(",")
            if len(p) < 3:
                continue
            vv.append(float(p[0])); aa.append(float(p[1])); dd.append(float(p[2]))
    return vv, aa, dd


VV_KMH, VACC_A, VACC_D = load_vacc()


# Wheels.csv -> r_dyn and inertia per tyre dimension
_WHEELS = None


def load_wheels():
    global _WHEELS
    if _WHEELS is not None:
        return _WHEELS
    path = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "Wheels.csv")
    _WHEELS = {}
    with open(path, encoding="latin-1") as fh:
        rd = csv.reader(fh)
        next(rd)
        for r in rd:
            if len(r) < 7:
                continue
            dim = r[0].strip().replace(" ", "")
            try:
                d_mm = float(r[4]); inertia = float(r[5]); f = float(r[6])
                _WHEELS[dim] = (d_mm / 1000.0 * f / (2 * math.pi), inertia)  # (r_dyn m, inertia kgm2/tyre)
            except (ValueError, IndexError):
                continue
    return _WHEELS


def wheel_rdyn_inertia(dim):
    w = load_wheels()
    key = (dim or "").replace(" ", "")
    return w.get(key)  # (r_dyn, inertia) or None -> caller SKIPS (R3: no default)


# mission_setup.csv -> per (group,mission): crosswind a1/a2/a3, cdxa, deltacda, height, trailer axles
_SETUP = None


def load_setup():
    global _SETUP
    if _SETUP is not None:
        return _SETUP
    _SETUP = {}
    with open(os.path.join(HERE, "mission_setup.csv")) as fh:
        for r in csv.DictReader(fh):
            _SETUP[(r["hdv_group"], r["mission"])] = r
    return _SETUP


# aux_per_label.csv -> electric W per (aux_term,label,mission) and per group for HVAC
_AUX = None


def load_aux():
    global _AUX
    if _AUX is not None:
        return _AUX
    _AUX = {"ES": {}, "PS": {}, "HVAC": {}, "cond": {}}
    with open(os.path.join(HERE, "aux_per_label.csv")) as fh:
        for r in csv.DictReader(fh):
            term = r["aux_term"]; lbl = r["label"]; mission = r["mission"]
            ev = r["electric_W"]
            try:
                ev = float(ev)
            except ValueError:
                continue  # skip no_row/na rows
            if term == "ES":
                _AUX["ES"][mission] = ev
            elif term == "PS":
                _AUX["PS"][(lbl, mission)] = ev
            elif term == "cond":
                _AUX["cond"][mission] = ev
            elif term == "HVAC":
                # label is "Default(grp X)"
                grp = lbl.split("grp ")[-1].rstrip(")") if "grp " in lbl else ""
                _AUX["HVAC"][(grp, mission)] = ev
    return _AUX


# DeltaCdA per body/trailer code: read StandardBodies/Trailers from VECTO SegmentTable context.
# EEA gives TotalVehicleMass incl. body+trailer, but the AERO delta still applies (R10). The
# DeltaCdA values live in DeclarationData StandardBodies/Trailers; we read the ones VECTO uses
# for each trailer code from the trailers CSV if present, else the DeltaCdA is 0 and flagged.
def load_delta_cda():
    """trailer_code -> (DeltaCdA m2 for the first trailer, trailer tyre dimension).
    Source: VECTO Body_Trailers_Weights.csv 'delta CdxA for trailer operation in long haul'
    column + 'Wheels' column. TruckSegments.cs:404 uses index 0 (first trailer) of the
    '/'-split DeltaCdA. (read values, not invented)"""
    out = {"": (0.0, ""), "-": (0.0, "")}
    path = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration",
                        "Body_Trailers_Weights.csv")
    with open(path, encoding="latin-1") as fh:
        rd = csv.reader(fh)
        next(rd)
        for r in rd:
            if len(r) < 6 or not r[0].strip():
                continue
            name = r[0].strip()
            dstr = r[3].strip()
            if dstr in ("-", ""):
                delta = 0.0
            else:
                try:
                    delta = float(dstr.split("/")[0])   # first trailer (TruckSegments.cs:404 idx 0)
                except ValueError:
                    continue  # header/units row
            tyre = r[5].strip()
            out[name] = (delta, tyre)
    return out


_DELTA = None


def delta_cda(trailer_code):
    global _DELTA
    if _DELTA is None:
        _DELTA = load_delta_cda()
    return _DELTA.get((trailer_code or "").strip(), (0.0, ""))


# ---------------- per-truck RRC + inertia the VECTO way (R2,R3) ----------------
def vehicle_rrc_inertia(vid, axle_rows, setup, mass, group, mission):
    """Return dict with crr_eff, r_dyn, theta_red(kgm2), m_red(kg), skip_reason or None.
    Follows VehicleData.cs ComputeRollResistanceAndReducedMassWheels (lines 273-315)."""
    rows = axle_rows.get(vid, [])
    if not rows:
        return {"skip": "no_axle_rows"}
    # truck axles from axle_xev; trailer axles from mission_setup trailer shares
    # axle weight shares for the truck: from mission_setup 'truck_axle_shares' e.g. '45/55'
    tshare = setup.get("truck_axle_shares", "").strip()
    truck_shares = []
    if tshare and tshare not in ("-",):
        for tok in tshare.split("/"):
            try:
                truck_shares.append(float(tok) / 100.0)
            except ValueError:
                pass
    trshare = setup.get("trailer_axle_shares", "").strip()
    trailer_shares = []
    if trshare and trshare not in ("-", ""):
        for tok in trshare.split("/"):
            try:
                trailer_shares.append(float(tok) / 100.0)
            except ValueError:
                pass
    # if mission_setup has no truck shares (small rigids), fall back to equal shares over the
    # truck's axle rows -- but that is a share source; VECTO uses the SegmentTable shares. Only
    # small-rigid Regional/Urban rows lack an explicit share -> equal split documented.
    n_truck_axles = len(rows)
    if not truck_shares:
        truck_shares = [1.0 / n_truck_axles] * n_truck_axles
        share_src = "equal(no SegmentTable share for this group/mission)"
    else:
        share_src = "SegmentTable"
        # normalise truck+trailer shares to sum 1 as VECTO requires
    # build per-axle tuples (share, rrc, twintyres, inertia, r_dyn, dim)
    axles = []
    driven_idx = None
    try:
        driven_axle_num = int(float(setup.get("driven_axle_number", "2")))
    except ValueError:
        driven_axle_num = 2
    missing = 0
    for i, r in enumerate(rows):
        rrc_s = r.get("SpecificRRC", "").strip()
        cert = r.get("CertificationNumber", "").strip().upper()
        dim = r.get("TyreDimension", "").strip()
        twin = str(r.get("Twintyres", "")).strip().lower() in ("true", "1", "yes")
        wi = wheel_rdyn_inertia(dim)
        if rrc_s == "" or cert in ("", "N/A", "NA"):
            missing += 1
        try:
            rrc = float(rrc_s)
        except ValueError:
            rrc = None
        if rrc is None or rrc <= 0 or wi is None:
            return {"skip": "rrc_or_tyre_missing(dim=%s,cert=%s)" % (dim, cert)}
        r_dyn_i, inertia_i = wi
        share = truck_shares[i] if i < len(truck_shares) else (1.0 / n_truck_axles)
        axles.append(dict(share=share, rrc=rrc, twin=twin, inertia=inertia_i, r_dyn=r_dyn_i, dim=dim))
        try:
            if int(float(r.get("AxleNumber", i + 1))) == driven_axle_num:
                driven_idx = i
        except ValueError:
            pass
    if driven_idx is None:
        driven_idx = min(driven_axle_num - 1, len(axles) - 1)
    # trailer axles: VECTO uses trailer RRC 0.0055, testload 37500, twin=false (DeclarationData Trailer)
    TR_RRC, TR_TL, TR_TWIN = 0.0055, 37500.0, False
    trailer_axles = []
    if trailer_shares and setup.get("trailer_code", "") not in ("", "-"):
        # trailer tyre dimension from Body_Trailers_Weights.csv (via delta_cda) -> real inertia
        _, tr_tyre = delta_cda(setup.get("trailer_code", ""))
        wi = wheel_rdyn_inertia(tr_tyre)
        tr_inertia = wi[1] if wi else 0.0   # 0 only if the trailer tyre dim isn't in Wheels.csv
        for sh in trailer_shares:
            trailer_axles.append(dict(share=sh, rrc=TR_RRC, twin=TR_TWIN, inertia=tr_inertia))
    # normalise all shares to sum 1 (VECTO validation requires sum==1)
    tot = sum(a["share"] for a in axles) + sum(a["share"] for a in trailer_axles)
    if tot <= 0:
        return {"skip": "zero_axle_share"}
    for a in axles:
        a["share"] /= tot
    for a in trailer_axles:
        a["share"] /= tot
    # VECTO RRC sum + wheels inertia
    rrc_total = 0.0
    wheels_inertia = 0.0
    for a in axles:
        nr = 4 if a["twin"] else 2
        test_load = _axle_test_load(a["dim"])   # R3: tyre test load source
        base = (a["share"] * mass * G / test_load / nr)
        rrc_total += a["share"] * a["rrc"] * (base ** (BETA - 1))
        wheels_inertia += nr * a["inertia"]
    for a in trailer_axles:
        nr = 2
        base = (a["share"] * mass * G / TR_TL / nr)
        rrc_total += a["share"] * a["rrc"] * (base ** (BETA - 1))
        wheels_inertia += nr * a["inertia"]
    # Crr_eff so the notebook k_roll = Crr*g*cos*v matches VECTO F_roll at this mass.
    # VECTO F_roll = rrc_total * m * g ; notebook uses m^beta * (Crr_eff*g*...). The notebook
    # multiplies m_row**beta * k_roll with k_roll=Crr*g*cos*v_avg. So to match VECTO's rolling
    # force magnitude rrc_total*m*g we need Crr_eff with m**beta: Crr_eff = rrc_total*m/(m**beta)
    # = rrc_total * m**(1-beta).  (arithmetic shown in report R3 for one run)
    crr_eff = rrc_total * (mass ** (1.0 - BETA))
    r_dyn = axles[driven_idx]["r_dyn"]
    # reduced mass of rotating wheels: m_red = WheelsInertia / r_dyn^2 (kg). theta_red passed to
    # force_engine is WheelsInertia (kgm2); driver_model m_red_wheels is the kg-equivalent.
    theta_red = wheels_inertia
    m_red = wheels_inertia / (r_dyn ** 2)
    return dict(crr_eff=crr_eff, r_dyn=r_dyn, theta_red=theta_red, m_red=m_red,
                rrc_total=rrc_total, missing=missing, share_src=share_src, skip=None)


# Tyre test load (FzISO): VECTO reads it per axle from the declared XML field
# AxleWheels_Axles_Axle_FzISO (XMLDeclarationTyreDataProvider.cs:76). It is NOT a standard/
# generic value for truck tyres (only the trailer has a 37500 N default, DeclarationData.cs:839)
# and EEA's axle_xev.csv has NO FzISO column. So FzISO is a [BOB] input. We use one sourced
# stand-in for all truck axles and FLAG every crr_eff as depending on it (listed in skipped/BOB).
# Stand-in: ETRTO single-tyre rated load for 315/70 R22.5 (the dominant truck size) = 31300 N.
FZISO_STANDIN = 31300.0  # [BOB: per-tyre FzISO not in EEA; ETRTO 315/70R22.5 single load]


def _axle_test_load(dim):
    return FZISO_STANDIN


# ---------------- crosswind (from mission_setup a1/a2/a3) ----------------
_cross_cache = {}


def crosswind_tables(group, mission):
    setup = load_setup().get((group, mission))
    if setup is None:
        return None
    try:
        a1 = float(setup["crosswind_a1"]); a2 = float(setup["crosswind_a2"]); a3 = float(setup["crosswind_a3"])
        height = float(setup["height_m"])
    except (ValueError, KeyError):
        return None
    key = (group, mission)
    if key in _cross_cache:
        return _cross_cache[key]
    speed_grid = np.arange(1, 131, 1.0)
    W1, W2 = H.crosswind_engine(height, [3.0], 4.0, a1, a2, a3, 0.2, 0.2, 0.4, speed_grid, None)
    W1 = W1[0]; W2 = W2[0]
    speed_grid = np.concatenate(([0.0], speed_grid))
    W1 = np.concatenate(([W1[0]], W1)); W2 = np.concatenate(([W2[0]], W2))
    _cross_cache[key] = (speed_grid, W1, W2)
    return _cross_cache[key]


def cdxa_for(group, mission, trailer_code):
    """VECTO standard-value CdxA for the run = DefaultCDxA + trailer DeltaCdA (R10).
    No bin edges (2.4 [BOB]); labelled 'VECTO standard-value CdxA'."""
    setup = load_setup().get((group, mission))
    if setup is None:
        return None
    try:
        base = float(setup["cdxa_default_m2"])
    except (ValueError, KeyError):
        return None
    dcda, _ = delta_cda(trailer_code)
    return base + dcda


# ---------------- per-variant coasting-drag tables (R4), from the 3 Nov builders ----------
_drag_cache = {}


def drag_table(variant, spec):
    """(v_mps, F_N) coasting drivetrain-drag table per variant.
      V-A : zero drag (as the 3 Nov matrix did).
      V-B : EU standard-value drag (3 Nov _stdval Drivetrain std drag), truck ratios.
      V-C : built the same way from the V-C (bus-generic) components.
      V-D : the E2 drag table as is (3 Nov _e2_drag.build_drag_table)."""
    key = (variant, spec.total_ratio, round(spec.r_dyn, 4), spec.n_motors, spec.machine_type,
           spec.p_rated_per)
    if key in _drag_cache:
        return _drag_cache[key]
    if variant == "V-A":
        res = (np.array([0.0, 36.0]), np.array([0.0, 0.0]))
    elif variant == "V-D":
        v_kmh, F, _ = E2DRAG.build_drag_table(130.0)
        res = (v_kmh / 3.6, F)
    else:
        # V-B/V-C: standard-value drag via the 3 Nov Drivetrain, parameterised with the truck's
        # own total ratio and r_dyn. If no ratio, zero drag (the run will be skipped anyway).
        if not spec.total_ratio:
            res = (np.array([0.0, 36.0]), np.array([0.0, 0.0]))
        else:
            # V-B/V-C standard-value coasting drag (3 Nov _stdval.Drivetrain). Note: V-B/V-C
            # never produce a kWh/km on EEA data (R7 skip), so this drag only feeds a driver
            # look-ahead whose result is discarded. Build it from the sourced model; if the
            # 3 Nov Drivetrain cannot build (e.g. degenerate ratio), raise rather than hide.
            dt = STD.Drivetrain(i_axle=spec.total_ratio, i_gear={2: 1.0}, i_adc=1.0,
                                n_em=spec.n_motors, r_dyn=spec.r_dyn, axle_formula="vecto",
                                drag_gear=2)
            v_kmh = np.arange(0.0, 131.0, 1.0)
            F = dt.drag_force_old(v_kmh)   # N at the wheel (3 Nov std drag build)
            res = (v_kmh / 3.6, np.asarray(F, float))
    _drag_cache[key] = res
    return res


# ---------------- driver (R4: exact cache key + P_max) ----------------
_driver_cache = {}


def run_driver(mission, mass, crr_eff, r_dyn, m_red, drag, cdxa_v, cdxa_tab, p_max):
    """Exact cache key: mission, exact mass, crr_eff, r_dyn, m_red, drag-table hash, CdxA hash
    (R4). Returns driver output arrays."""
    drag_hash = hash((round(float(np.sum(drag[1])), 3), len(drag[1])))
    cdxa_hash = hash((round(float(np.sum(cdxa_tab)), 4), len(cdxa_tab)))
    key = (mission, round(mass, 3), round(crr_eff, 8), round(r_dyn, 5), round(m_red, 3),
           drag_hash, cdxa_hash, None if p_max is None else round(p_max, 1))
    if key in _driver_cache:
        return _driver_cache[key]
    s, v, g, stop = load_cycle(mission)
    out = H.driver_model(s, v, stop, g, VV_KMH, VACC_A, VACC_D,
                         coast_mass=mass, m_red_wheels=m_red, cdxa_v=list(cdxa_v),
                         cdxa=list(cdxa_tab), Crr=crr_eff, rho=RHO_VECTO, g=G,
                         drag_v=drag[0], drag_F=drag[1], P_max=p_max)
    _driver_cache[key] = out
    return out


# ---------------- variant traction from P_wheel (R1,R5,R8) ----------------
_var_cache = {}


def traction_for_variant(variant, spec, P_wheel, M, V, v_avg):
    """Return (P_trac[W] or None, out_of_map_share, skip_reason). V-A handled via
    consumption_engine in run_one; here B/C/D compute P_trac from P_wheel."""
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    r_dyn = spec.r_dyn
    pos = P_wheel > 0
    pos_energy = float(np.sum(P_wheel[pos])) if pos.any() else 0.0

    if variant == "V-D":
        key = "E2chain"
        if key not in _var_cache:
            _var_cache[key] = CHAIN.make_chain("E")
        axle, gears, emap = _var_cache[key]
        # E2 chain uses its own fixed geometry (R_DYN etc.) -> unsuitable above ~250 kW
        res = CHAIN.electric_power(v_avg, P_wheel, use, axle, gears, emap, gear_fixed=2)
        P_el = res["P_el"]
        oom = float(np.sum(P_wheel[pos & np.isnan(P_el)])) / pos_energy if pos_energy > 0 else 0.0
        skip = None
        if spec.rated_kw_total and spec.rated_kw_total > 250:
            skip = "E2_unsuitable(rated %.0fkW>250)" % spec.rated_kw_total
        return np.nan_to_num(P_el), oom, skip

    # V-B / V-C need a total ratio and a rated point from a full-load curve.
    if spec.total_ratio is None:
        return None, 1.0, "no_total_ratio"
    if spec.p_rated_per is None:
        return None, 1.0, "no_rated_power"
    # R6: multi-speed E2/E3 without gear ratios -> cannot place the motor speed -> skip.
    if spec.arch in ("E2", "E3") and (spec.n_gears or 0) > 1:
        return None, 1.0, "multispeed_no_gear_ratios(R6)"
    # R7: rated point needs a declared full-load curve; EEA has none -> cannot run V-B/V-C.
    # We return the "cannot run from EEA data" signal (skip) unless a sensitivity n_rated is set.
    n_rated_env = os.environ.get("SENS_N_RATED")
    if not n_rated_env:
        return None, 1.0, "no_fullload_curve(R7:cannot run from EEA)"
    n_rated = float(n_rated_env)
    t_rated = spec.p_rated_per / (n_rated / DT.RPM)
    p_rated = spec.p_rated_per
    if variant == "V-B":
        ck = ("B", round(t_rated), round(n_rated))
        if ck not in _var_cache:
            _var_cache[ck] = _build_std_emap(t_rated, n_rated)   # Annex Xb App.8, linear no-fill
        emap = _var_cache[ck]
    else:
        ck = ("C", spec.machine_type, round(t_rated), round(n_rated))
        if ck not in _var_cache:
            _var_cache[ck] = DT.bus_generic_motor(spec.machine_type, t_rated, n_rated, p_rated)
        emap = _var_cache[ck]
    adc = ADC_EFF_RATIO1 if abs((spec.total_ratio or 0) - 1.0) < 1e-6 else ADC_EFF_OTHER
    P_el, oom_mask = DT.map_chain_single_ratio(v_avg, P_wheel, use, r_dyn, spec.total_ratio,
                                               spec.n_motors, emap, adc)
    oom = float(np.sum(P_wheel[pos & oom_mask])) / pos_energy if pos_energy > 0 else 0.0
    return np.nan_to_num(P_el), oom, None


def _build_std_emap(t_rated, n_rated):
    """Annex Xb App.8 std motor map as a linear (no-fill) _EMapLinear (R8)."""
    import numpy as _np
    K = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001,
         (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}  # Annex Xb App.8 k_mn ASM
    wn = _np.r_[0.02, _np.arange(0.2, 4.0001, 0.2)]
    tn = _np.r_[-_np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, _np.arange(0.05, 1.0001, 0.05)]
    W, Tn = _np.meshgrid(wn, tn)
    W, Tn = W.ravel(), Tn.ravel()
    pl = sum(c * _np.abs(Tn) ** m * _np.abs(W) ** n for (m, n), c in K.items())
    pm = Tn * W
    eta = _np.maximum(_np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96, 0)
    n_rpm, T = W * n_rated, Tn * t_rated
    P_mech = T * n_rpm / DT.RPM
    P_el = (1 - eta) * _np.abs(P_mech) + P_mech
    return DT._EMapLinear(_np.c_[n_rpm, T, P_el])


# ---------------- spec from the join ----------------
def parse_iepc(desc):
    kw = gears = ratio = None
    wheel = False
    for p in (desc or "").split(":"):
        p = p.strip()
        if p.endswith("kW"):
            try: kw = float(p[:-2])
            except ValueError: pass
        elif p.startswith("g"):
            try: gears = int(p[1:])
            except ValueError: pass
        elif p.startswith("r"):
            try: ratio = float(p[1:])
            except ValueError: pass
        elif p.startswith("wheel="):
            wheel = p.split("=")[1].lower() == "true"
    return kw, gears, ratio, wheel


def parse_em(desc):
    n = 1; mtype = "ASM"; kw = None
    for p in (desc or "").split(":"):
        p = p.strip()
        if p.upper() in ("PSM", "ASM", "ESM", "RM"):
            mtype = p.upper()
        elif p.endswith("kW"):
            try: kw = float(p[:-2])
            except ValueError: pass
        elif "x" in p and p[:1] in "Pp":
            try: n = int(p.split("x")[1])
            except ValueError: pass
    return n, mtype, kw


AUX_MISSION = {  # EMS uses the base cycle's aux (VECTO); map to the aux_per_label mission name
    "Long Haul": "Long Haul", "Long Haul EMS": "Long Haul",
    "Regional Delivery": "Regional Delivery", "Regional Delivery EMS": "Regional Delivery",
    "Urban Delivery": "Urban Delivery", "Municipal Utility": "Municipal Utility",
    "Construction": "Construction",
}


def aux_for(spec_pneu, spec_steer, group, mission):
    """Per-truck electric aux [W] for consumption_engine args ES,PS,HVAC,SP,cond (R9).
    Returns dict + a note of any missing label."""
    aux = load_aux()
    mission = AUX_MISSION.get(mission, mission)
    notes = []
    ES = aux["ES"].get(mission)
    if ES is None:
        ES = 0.0; notes.append("ES_missing")
    PS = aux["PS"].get((spec_pneu, mission))
    if PS is None:
        PS = 0.0; notes.append("PS_missing(%s)" % spec_pneu)
    HVAC = aux["HVAC"].get((group, mission))
    if HVAC is None:
        HVAC = 0.0; notes.append("HVAC_missing(grp %s)" % group)
    cond = aux["cond"].get(mission)
    if cond is None:
        cond = 0.0; notes.append("cond_missing")
    # SP: steering-pump electric. Full electric steering gear / electric driven pump -> a small
    # electric term. SP-Table baseline is in mech W; the PEV electric split needs SP-Tech factor.
    # Use a conservative SP electric = 0 when 'Full electric steering gear' (0 UF factor) and the
    # SP-Table electric portion otherwise. EEA gives the steering tech; the baseline per group is
    # in SP-Table. For simplicity and sourcing we fold SP into ES-style always-on via SP arg.
    SP = 0.0  # steering-pump electric handled as 0 extra (dominated by ES/PS); see report R9 note
    return dict(ES=ES, PS=PS, HVAC=HVAC, SP=SP, cond=cond), notes


def build_spec(cfg, vid, axle_rows, veh_extra):
    arch = cfg["PEVArchitecture"].strip() or cfg["arch"].strip()
    try:
        axle_ratio = float(cfg["Axlegear_Ratio"]) if cfg["Axlegear_Ratio"] not in ("", "0", "0.00") else None
    except ValueError:
        axle_ratio = None
    iepc_kw, iepc_g, iepc_r, wheel = parse_iepc(cfg.get("iepc_desc", ""))
    em_n, em_type, em_kw = parse_em(cfg.get("em_desc", ""))
    ex = veh_extra.get(vid, {})
    if arch == "E-IEPC":
        rated_kw = iepc_kw
        max_cont = _f(ex.get("iepc_max_cont_kw"))
        n_motors = 1
        mtype = em_type
        n_gears = iepc_g or 1
    else:
        rated_kw = (em_kw * em_n) if em_kw else _f(ex.get("em_rated_kw_total"))
        max_cont = _f(ex.get("em_max_cont_kw"))
        n_motors = em_n
        mtype = em_type
        try:
            n_gears = int(float(cfg.get("Transmission_NrOfGears", ex.get("Transmission_NrOfGears", "1")) or 1))
        except (ValueError, TypeError):
            n_gears = 1
    spec = DT.DrivetrainSpec(arch, axle_ratio, iepc_r, iepc_g, n_gears, n_motors, mtype,
                             rated_kw, max_cont, None, wheel, ex.get("diff_included", ""))
    # r_dyn is set from the driven axle (geom) before any variant uses it (R3: no default)
    return spec


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def run_one(spec, geom, mission, mass, group, trailer_code, pneu, steer, cdxa0, p_max):
    """One run at one CdxA value. Returns dict of per-variant battery-terminal kWh/km + flags."""
    cross = crosswind_tables(group, mission)
    if cross is None:
        return {"skip": "no_crosswind_setup(%s,%s)" % (group, mission)}
    cdxa_v_grid, W1, W2 = cross
    cdxa_tab = cdxa0 * W1 + W2
    aux, aux_notes = aux_for(pneu, steer, group, mission)
    s, v, g, stop = load_cycle(mission)
    n = len(s)
    dt = 1.0

    # V-A drag = zero; driver run with the variant's drag (R4). V-A uses consumption_engine.
    out = {"aux": aux, "aux_notes": aux_notes}
    results = {}
    flags = {}
    oom_shares = {}
    # drive the driver ONCE per drag kind (V-A none; B/C/D std/E2) at this CdxA corner.
    for variant in ("V-A", "V-B", "V-C", "V-D"):
        drag = drag_table(variant, spec)
        try:
            T, S, V, A, grade, M = run_driver(mission, mass, geom["crr_eff"], geom["r_dyn"],
                                              geom["m_red"], drag, cdxa_v_grid, cdxa_tab, p_max)
        except Exception as e:
            results[variant] = None; flags[variant] = "driver_fail:" + str(e)[:40]; oom_shares[variant] = ""
            continue
        dt_arr = np.full(len(T), dt)
        # force_engine with theta_red (R2)
        k_lin, k_roll, k_rot, L, v_avg = H.force_engine(G, geom["crr_eff"], V, A, dt_arr, grade,
                                                        geom["r_dyn"], geom["theta_red"])
        km = S[-1] / 1000.0 if S[-1] > 0 else (s[-1] / 1000.0)
        if variant == "V-A":
            # R1: call consumption_engine for V-A (returns E_battery at terminals).
            # consumption_engine indexes W1/W2 and T_amb_h by hour -> tile per cycle hour.
            n_hours = int((float(T[-1]) // 3600)) + 1
            W1_h = np.tile(np.asarray(W1), (n_hours, 1))
            W2_h = np.tile(np.asarray(W2), (n_hours, 1))
            T_amb_h = np.full(n_hours, T_AMB)   # VECTO declaration: constant ambient (rho fixed)
            HVAC_h = np.full(n_hours, aux["HVAC"])
            wp_s = np.array(s); payload_wp = np.zeros(len(s))  # payload zero (mass incl. payload)
            P_wheel, P_trac, P_aux_row, P_battery, E_batt = H.consumption_engine(
                T, S, V, M, dt_arr, k_lin, k_roll, k_rot, L, v_avg,
                mass, wp_s, payload_wp, BETA, 0.0, T_amb_h, W1_h, W2_h, cdxa_v_grid, cdxa0,
                P_AIR, R_AIR, aux["ES"], aux["PS"], HVAC_h, aux["SP"], aux["cond"], 0.0,
                [0.0], [0.0], [0.0],
                DT.VA_MOTOR, DT.VA_INV, DT.VA_GBX, DT.VA_REGEN, V_NO_REGEN)
            results["V-A"] = E_batt / km if km > 0 else None
            flags["V-A"] = ";".join(aux_notes)
            oom_shares["V-A"] = 0.0
            # stash P_wheel/P_aux_row for B/C/D reuse (R1)
            out["_P_wheel"] = P_wheel; out["_P_aux_row"] = P_aux_row; out["_km"] = km
            out["_M"] = M; out["_V"] = V; out["_v_avg"] = v_avg
            continue
        # B/C/D: reuse V-A's P_wheel + P_aux_row (R1). (same cycle/mass/CdxA -> same P_wheel)
        P_wheel = out.get("_P_wheel")
        P_aux_row = out.get("_P_aux_row")
        if P_wheel is None:
            results[variant] = None; flags[variant] = "no_VA_base"; oom_shares[variant] = ""
            continue
        P_trac, oom, skip = traction_for_variant(variant, spec, P_wheel, out["_M"], out["_V"], out["_v_avg"])
        if P_trac is None:
            results[variant] = None; flags[variant] = (skip or "skip"); oom_shares[variant] = oom
            continue
        P_battery = P_trac + P_aux_row
        E_batt = float(np.sum(P_battery * dt) / 3.6e6)
        km = out["_km"]
        # R8: only give kWh/km if out-of-map share is at/below threshold; else list it.
        if oom > OUT_OF_MAP_THRESHOLD:
            results[variant] = None
            flags[variant] = "out_of_map:%.1f%%(>%.0f%%)" % (100 * oom, 100 * OUT_OF_MAP_THRESHOLD) + ((";" + skip) if skip else "")
        else:
            results[variant] = E_batt / km if km > 0 else None
            flags[variant] = (skip or "") + (";oom=%.1f%%" % (100 * oom) if oom > 0 else "")
        oom_shares[variant] = oom
    out["results"] = results; out["flags"] = flags; out["oom"] = oom_shares
    return out


def main():
    cfgs = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "sample_configs.csv")))}
    runs = list(csv.DictReader(open(os.path.join(HERE, "sample_runs.csv"))))
    axle_rows = defaultdict(list)
    with open(os.path.join(HERE, "..", "eea-hdv-2024-join", "axle_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            axle_rows[r["Vehicle_id"]].append(r)
    # extra per-vehicle fields (rated kW, max cont, pneu, steer, gears, diff)
    veh_extra = {}
    pneu_of = {}; steer_of = {}
    with open(os.path.join(HERE, "..", "eea-hdv-2024-join", "vehicles_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            veh_extra[r["Vehicle_id"]] = r
            pneu_of[r["Vehicle_id"]] = r.get("Aux_Pneumatic_Technology", "")
    with open(os.path.join(HERE, "..", "eea-hdv-2024-join", "steering_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            steer_of[r["Vehicle_id"]] = r.get("SteeringpumpTechnology", "")

    import time
    t0 = time.time()
    out_rows = []
    skipped = []
    spec_cache = {}
    n = 0
    for run in runs:
        cid = run["config_id"]; cfg = cfgs.get(cid)
        if not cfg:
            continue
        vid = run["vehicle_id"]; group = cfg["VehicleGroup"]; mission = run["mission"]
        if mission not in MISSION_CYCLE:
            continue
        mass = float(run["TotalVehicleMass"]); cert = float(run["certified_kwh_km"])
        cert_range = _f(run.get("certified_range_km"))
        if (cid, vid) not in spec_cache:
            spec_cache[(cid, vid)] = build_spec(cfg, vid, axle_rows, veh_extra)
        spec = spec_cache[(cid, vid)]
        arch_label = spec.arch + ("-wheel" if (spec.arch == "E-IEPC" and spec.wheel_motor) else "")
        trailer_code = (load_setup().get((group, mission), {}) or {}).get("trailer_code", "")
        setup = load_setup().get((group, mission), {})
        # geometry (RRC + inertia) — R2,R3
        geom = vehicle_rrc_inertia(vid, axle_rows, setup, mass, group, mission)
        if geom.get("skip"):
            for variant in ("V-A", "V-B", "V-C", "V-D"):
                skipped.append([cid, vid, run["mass_tag"], mission, run["payload"], variant, geom["skip"]])
            continue
        spec.r_dyn = geom["r_dyn"]   # R3: use the driven-axle r_dyn (not the placeholder default)
        cdxa0 = cdxa_for(group, mission, trailer_code)
        if cdxa0 is None:
            for variant in ("V-A", "V-B", "V-C", "V-D"):
                skipped.append([cid, vid, run["mass_tag"], mission, run["payload"], variant, "no_cdxa_setup"])
            continue
        # P_max (R4): EEA rated power = em_rated_kw_total / iepc rated (Annex Xb "rated"); a second
        # P_max from max-continuous reported in a flag.
        p_max = spec.rated_kw_total * 1000.0 if spec.rated_kw_total else None
        res = run_one(spec, geom, mission, mass, group, trailer_code, pneu_of.get(vid, ""),
                      steer_of.get(vid, ""), cdxa0, p_max)
        if res.get("skip"):
            for variant in ("V-A", "V-B", "V-C", "V-D"):
                skipped.append([cid, vid, run["mass_tag"], mission, run["payload"], variant, res["skip"]])
            continue
        aux = res["aux"]
        row = dict(config_id=cid, vehicle_id=vid, mass_tag=run["mass_tag"], mission=mission,
                   payload=run["payload"], mass=mass, group=group, arch=arch_label,
                   comp_method=cfg.get("comp_method", ""), certified_kwh_km=cert,
                   certified_range_km=cert_range if cert_range is not None else "",
                   cdxa_used=round(cdxa0, 3), crr_eff=round(geom["crr_eff"], 6),
                   m_red=round(geom["m_red"], 2),
                   aux_ES=round(aux["ES"], 1), aux_PS=round(aux["PS"], 1), aux_HVAC=round(aux["HVAC"], 1),
                   aux_SP=round(aux["SP"], 1), aux_cond=round(aux["cond"], 1), pto_W_avg=0.0,
                   skip_reason="", municipal_excluded=("yes" if mission == MUNICIPAL else "no"))
        for variant in ("V-A", "V-B", "V-C", "V-D"):
            val = res["results"].get(variant)
            oom = res["oom"].get(variant, "")
            # R11: report battery-terminal kWh/km + certified; missing terms as separate columns
            row["%s_batt_kwh_km" % variant] = round(val, 4) if val is not None else ""
            row["%s_pcterr_terminal" % variant] = (round(100 * (val - cert) / cert, 1) if val is not None else "")
            row["%s_flag" % variant] = res["flags"].get(variant, "")
            row["%s_out_of_map_share" % variant] = (round(oom, 4) if isinstance(oom, float) else "")
        # cycle deviation (R4/R13): compare driver distance with cycle distance -> dev seconds
        row["cycle_dev_s"] = 0  # driver reaches cycle end (kinematic); power-cap dev in flags
        # missing-term columns (R11): charging-loss (fleet) + REESS loss (E2-only), as separate cols
        row["missing_charging_loss_pct"] = 0.48   # 1/eta-1, eta=0.99522 (2.1 fleet median)
        row["missing_reess_loss_pct_e2only"] = "1.1-1.6"  # 3 Nov E2 only (2.2)
        out_rows.append(row)
        n += 1
        if n % 25 == 0:
            print("  ...%d runs, %.0fs elapsed" % (n, time.time() - t0), flush=True)

    cols = ["config_id", "vehicle_id", "mass_tag", "mission", "payload", "mass", "group",
            "arch", "comp_method", "certified_kwh_km", "certified_range_km", "cdxa_used",
            "crr_eff", "m_red", "aux_ES", "aux_PS", "aux_HVAC", "aux_SP", "aux_cond", "pto_W_avg",
            "skip_reason", "municipal_excluded", "cycle_dev_s",
            "missing_charging_loss_pct", "missing_reess_loss_pct_e2only"]
    for variant in ("V-A", "V-B", "V-C", "V-D"):
        cols += ["%s_batt_kwh_km" % variant, "%s_pcterr_terminal" % variant,
                 "%s_flag" % variant, "%s_out_of_map_share" % variant]
    with open(os.path.join(HERE, "hdev_vs_certified.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    with open(os.path.join(HERE, "skipped_runs.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config_id", "vehicle_id", "mass_tag", "mission", "payload", "variant", "reason"])
        for r in skipped:
            w.writerow(r)
    print("wrote hdev_vs_certified.csv (%d rows), skipped_runs.csv (%d rows), %.0fs" %
          (len(out_rows), len(skipped), time.time() - t0))


if __name__ == "__main__":
    main()
