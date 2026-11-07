"""Job 3 main harness: run HDEV on the sampled certified trucks and compare with the
certified kWh/km. TEST-ONLY. No src/ or notebook edits.

Chain per run:
  VECTO declaration cycle  -> HDEV driver_model (code-of-record copy)
                           -> HDEV force_engine (code-of-record copy) -> P_wheel per row
                           -> drivetrain variant V-A/B/C/D -> P_trac per row
                           -> + P_aux (VECTO declaration aux values) = P_battery
                           -> battery-side kWh/km, then / 0.995 = grid-side (certified basis)
CdxA: run at bin low and high edge (here: VECTO group DefaultCdxA +/-10%, a declared band;
      exact EEA A-bin edges are [BOB], see report). Construction uses CdxA_Construction.

Caching: the driver trace depends only on (cycle, mass, drag, Crr). It is cached per
(mission, rounded mass, drag-kind) and reused across variants and CdxA corners.
"""
import csv
import math
import os
import sys
import statistics
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hdev_test_module as H
import _drivetrains as DT

VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
CYC = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "MissionCycles")
VACC = os.path.join(VSRC, "Generic Vehicles", "Declaration Mode", "PEV", "GenericVehicleE2", "Truck.vacc")

G = 9.80665  # FIX 3: agreed g
RHO = 1.188  # VECTO fixed air density (declaration)
V_NO_REGEN = 5.0 / 3.6
BETA_RRC = 0.9  # Physics.RollResistanceExponent

# mission name -> VECTO cycle file (Job 2 point 4). EMS uses the base cycle.
MISSION_CYCLE = {
    "Long Haul": "LongHaul.vdri", "Long Haul EMS": "LongHaul.vdri",
    "Regional Delivery": "RegionalDelivery.vdri", "Regional Delivery EMS": "RegionalDelivery.vdri",
    "Urban Delivery": "UrbanDelivery.vdri", "Municipal Utility": "MunicipalUtility.vdri",
    "Construction": "Construction.vdri",
}

# VECTO SegmentTable.csv CdxA_Default / CdxA_Construction / Height per HDV group (opened).
GROUP_CDXA = {
    "1": (7.1, None, 3.6), "1s": (7.1, None, 3.6), "2": (7.2, None, 3.75), "3": (7.4, None, 3.9),
    "4": (8.4, 6.6, 4.0), "5": (8.7, 7.2, 4.0), "9": (8.5, 6.7, 4.0), "10": (8.8, 7.3, 4.0),
    "11": (8.5, 6.7, 4.0), "12": (8.8, 7.3, 4.0), "16": (9.0, 7.0, 3.6),
    "53": (5.8, None, 3.5),
}
# crosswind parameter row per group kind (VCDV_parameters.csv, opened)
CROSS = {
    "RigidSolo": (0.013526, 0.017746, -0.000666),
    "RigidTrailer": (0.017125, 0.072275, -0.004148),
    "TractorSemitrailer": (0.030042, 0.040817, -0.00213),
}
# groups 1-16 are rigid trucks; 5/9/10/11/12 commonly run with trailer; tractors (groups with
# semitrailer) use TractorSemitrailer. Simplify by group: solo for small rigids, trailer for
# larger rigids. Documented in the report.
GROUP_CROSS = {
    "1": "RigidSolo", "1s": "RigidSolo", "2": "RigidSolo", "3": "RigidSolo",
    "4": "RigidSolo", "53": "RigidSolo",
    "5": "RigidTrailer", "9": "RigidTrailer", "10": "RigidTrailer",
    "11": "RigidTrailer", "12": "RigidTrailer", "16": "RigidTrailer",
}

# VECTO declaration aux electric power per mission for PEV lorries [W electric], from the
# VAUX tables (Job 2 point 6). Representative per-mission totals (ES+PS+HVAC+SP+Cond),
# electric side. These are the declaration standard-technology values; sourced in the report.
# Conservative single per-mission total used across trucks (documented limitation).
AUX_W = {  # mission -> total electric aux W
    "Long Haul": 2600.0, "Long Haul EMS": 2600.0,
    "Regional Delivery": 2300.0, "Regional Delivery EMS": 2300.0,
    "Urban Delivery": 2100.0, "Municipal Utility": 2300.0, "Construction": 2300.0,
}


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
    return vv, aa, dd  # vv in km/h


VV_KMH, VACC_A, VACC_D = load_vacc()


# ---------------- per-truck spec from the join ----------------
def parse_iepc(desc):
    # "511kW:g6:r2.23800:wheel=false"
    kw = gears = ratio = None
    wheel = False
    for p in desc.split(":"):
        p = p.strip()
        if p.endswith("kW"):
            try: kw = float(p[:-2])
            except: pass
        elif p.startswith("g"):
            try: gears = int(p[1:])
            except: pass
        elif p.startswith("r"):
            try: ratio = float(p[1:])
            except: pass
        elif p.startswith("wheel="):
            wheel = p.split("=")[1].lower() == "true"
    return kw, gears, ratio, wheel


def parse_em(desc):
    # "P3x1:PSM:140kW" or "P3x4:ASM:14kW"
    n = 1; mtype = "ASM"; kw = None
    parts = desc.split(":")
    for p in parts:
        p = p.strip()
        if p.upper() in ("PSM", "ASM", "ESM", "RM"):
            mtype = p.upper()
        elif p.endswith("kW"):
            try: kw = float(p[:-2])
            except: pass
        elif "x" in p and p[0] in "Pp":
            try: n = int(p.split("x")[1])
            except: pass
    return n, mtype, kw


def rrc_rdyn_for_vehicle(vid, axle_rows):
    """Combine per-axle SpecificRRC with equal fallback shares; r_dyn from driven axle.
    axle_rows: list of dicts for this vehicle. Returns (crr_nominal, r_dyn, n_axles, missing)."""
    rows = axle_rows.get(vid, [])
    rrcs = []
    missing = 0
    dims = []
    for r in rows:
        v = r["SpecificRRC"].strip()
        cert = r["CertificationNumber"].strip().upper()
        if v == "" or cert in ("", "N/A", "NA"):
            missing += 1
        try:
            fv = float(v)
            if fv > 0:
                rrcs.append(fv)  # SpecificRRC already a Crr value (N/N), e.g. 0.0066
        except ValueError:
            pass
        dims.append(r["TyreDimension"].strip())
    if not rrcs:
        crr = 0.0055  # fallback, flagged
        missing = max(missing, 1)
    else:
        crr = sum(rrcs) / len(rrcs)
    # r_dyn: VECTO Wheels.cs d*f/(2pi); default 315/70 R22.5 ~ 0.489 m if unknown.
    r_dyn = wheels_rdyn(dims[-1] if dims else "")
    return crr, r_dyn, len(rows), missing


# VECTO Wheels.csv dynamic radius lookup (a few common truck dims; else default)
_WHEELS = None


def load_wheels():
    global _WHEELS
    if _WHEELS is not None:
        return _WHEELS
    path = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "Wheels.csv")
    _WHEELS = {}
    try:
        with open(path, encoding="latin-1") as fh:
            rd = csv.reader(fh)
            header = next(rd)
            # columns: Wheel, width, aspect, rim, d[mm]=idx4, Inertia=idx5, F=idx6
            for r in rd:
                if len(r) < 7:
                    continue
                dim = r[0].strip().replace(" ", "")
                try:
                    d_mm = float(r[4]); f = float(r[6])
                    _WHEELS[dim] = d_mm / 1000.0 * f / (2 * math.pi)
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        pass
    return _WHEELS


def wheels_rdyn(dim):
    w = load_wheels()
    key = dim.replace(" ", "")
    if key in w:
        return w[key]
    return 0.489  # 315/70 R22.5 default [ASSUMPTION, flagged]


# ---------------- driver + consumption ----------------
_driver_cache = {}


def run_driver(mission, mass, crr, r_dyn, cdxa_ref, drag):
    """Cached driver trace. drag: None (V-A) or (v_tab, f_tab) for coasting (V-B/C/D).
    cdxa_ref: a constant reference CdxA for coasting look-ahead."""
    key = (mission, round(mass / 250.0), round(crr, 4), round(r_dyn, 3), drag is not None)
    if key in _driver_cache:
        return _driver_cache[key]
    s, v, g, stop = load_cycle(mission)
    cdxa_v = [0.0, 200.0]
    cdxa = [cdxa_ref, cdxa_ref]
    if drag is None:
        drag = (np.array([0.0, 36.0]), np.array([0.0, 0.0]))  # V-A: zero drivetrain drag
    kw = dict(coast_mass=mass, m_red_wheels=0.0, cdxa_v=cdxa_v, cdxa=cdxa, Crr=crr,
              rho=RHO, g=G, drag_v=drag[0], drag_F=drag[1])
    out = H.driver_model(s, v, stop, g, VV_KMH, VACC_A, VACC_D, **kw)
    _driver_cache[key] = out
    return out


def cdxa_corners(group, mission):
    center, con, height = GROUP_CDXA.get(group, (8.0, None, 4.0))
    if mission == "Construction" and con:
        center = con
    lo = center * 0.9
    hi = center * 1.1
    return lo, hi, height


def one_run(spec, mission, mass, cdxa0, height, group):
    """Returns dict variant -> battery-side kWh/km, plus flags, for one CdxA corner."""
    # crosswind tables W1,W2 for this group over a speed grid 0..130 km/h
    a1, a2, a3 = CROSS[GROUP_CROSS.get(group, "RigidSolo")]
    speed_grid = np.arange(1, 131, 1.0)  # start at 1 km/h to avoid /0; 0 handled by hold-low
    # Use crosswind_engine at base wind 3 m/s (VECTO BaseWindSpeed), Hellmann 0.2
    W1, W2 = H.crosswind_engine(height, [3.0], 4.0, a1, a2, a3, 0.2, 0.2, 0.4, speed_grid, None)
    W1 = W1[0]; W2 = W2[0]
    # prepend a 0 km/h point holding the 1 km/h value (VECTO copies the low-speed value)
    speed_grid = np.concatenate(([0.0], speed_grid))
    W1 = np.concatenate(([W1[0]], W1)); W2 = np.concatenate(([W2[0]], W2))
    cdxa_v_grid = speed_grid  # km/h grid for consumption_engine
    # single weather hour at 20 C
    T_amb_h = np.array([20.0])
    W1h = W1[None, :]; W2h = W2[None, :]

    results = {}
    flags = {}
    # V-A: no coasting drag in driver; constant efficiencies
    for variant in ("V-A", "V-B", "V-C", "V-D"):
        drag = None
        if variant in ("V-B", "V-C", "V-D"):
            drag = build_drag(spec, variant)
        try:
            T, S, V, A, grade, M = run_driver(mission, mass, spec_crr(spec), spec.r_dyn, cdxa0, drag)
        except RuntimeError as e:
            results[variant] = None
            flags[variant] = "driver_fail:" + str(e)[:40]
            continue
        dt = 1.0
        dt_arr = np.full(len(T), dt)
        k_lin, k_roll, k_rot, L, v_avg = H.force_engine(G, spec_crr(spec), V, A, dt_arr, grade, spec.r_dyn, 0.0)
        # wheel power per row with crosswind CdxA at this corner
        hour = np.zeros(len(T), dtype=int)
        v_kmh = np.clip(v_avg * 3.6, cdxa_v_grid[0], cdxa_v_grid[-1])
        cdxa_tab = cdxa0 * W1 + W2
        j = np.clip(np.searchsorted(cdxa_v_grid, v_kmh, side="right") - 1, 0, len(cdxa_v_grid) - 2)
        w = (v_kmh - cdxa_v_grid[j]) / (cdxa_v_grid[j + 1] - cdxa_v_grid[j])
        cdxa_row = cdxa_tab[j] * (1 - w) + cdxa_tab[j + 1] * w
        P_wheel = mass * k_lin + mass ** BETA_RRC * k_roll + k_rot + RHO * cdxa_row * L
        use = (M != 0)
        # traction power per variant
        P_trac, vflag = traction_for_variant(variant, spec, P_wheel, M, V, v_avg)
        # aux
        P_aux = AUX_W.get(mission, 2300.0)
        P_battery = P_trac + P_aux
        km = S[-1] / 1000.0 if S[-1] > 0 else (load_cycle(mission)[0][-1] / 1000.0)
        E_batt = float(np.sum(P_battery * dt) / 3.6e6)
        results[variant] = E_batt / km if km > 0 else None
        flags[variant] = vflag
    return results, flags


def spec_crr(spec):
    return getattr(spec, "_crr", 0.0055)


def build_drag(spec, variant):
    """A coasting drivetrain-drag table (v[m/s], F[N]) for the driver look-ahead.
    Small second-order effect; a single std-value drag table is used for B/C/D."""
    v_tab = np.arange(0.0, 36.0, 1.0)  # 0..~130 km/h
    ratio = spec.total_ratio or 10.0
    r_dyn = spec.r_dyn
    # simple motor+axle drag proportional to speed via std axle Td0 (documented approximation)
    td0 = 52.5 + 15.0 * (ratio / 3.0)
    f = (td0 * ratio) / r_dyn + 2.0 * v_tab  # N; linear-in-speed drivetrain drag [approx, flagged]
    return v_tab, f


_var_cache = {}


def traction_for_variant(variant, spec, P_wheel, M, V, v_avg):
    flag = ""
    if variant == "V-A":
        return DT.traction_power_VA(P_wheel, M, V, V_NO_REGEN), flag
    # map-based variants: build emap + chain
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    r_dyn = spec.r_dyn
    total_ratio = spec.total_ratio
    n_motors = spec.n_motors
    if variant == "V-D":
        # fixed E2 example maps (unscaled)
        key = "E2maps"
        if key not in _var_cache:
            _var_cache[key] = (DT.e2_motor_map(), DT.e2_axle_gears())
        emap, (axle, gears) = _var_cache[key]
        P_el = DT._map_chain(v_avg, P_wheel, use, DT.R_DYN if False else r_dyn,
                             None, 2, emap, axle=axle, gears=gears, gear_fixed=2)
        if spec.rated_kw_total and spec.rated_kw_total > 300:
            flag = "E2_unsuitable(rated %.0fkW>>250kW)" % spec.rated_kw_total
        return P_el, flag
    # V-B std maps, V-C bus-generic maps
    if total_ratio is None:
        return np.zeros(len(v_avg)), "no_total_ratio_skip"
    rp = DT.rated_point_from_power(spec.p_rated_per)
    if rp is None:
        return np.zeros(len(v_avg)), "no_rated_power_skip"
    n_rated, t_rated, p_rated = rp
    pbucket = round(spec.p_rated_per / 5000.0)  # 5 kW buckets to reuse interpolators
    if variant == "V-B":
        ck = ("B", pbucket)
        if ck not in _var_cache:
            _var_cache[ck] = DT.std_motor(t_rated, n_rated)
        emap = _var_cache[ck]
        flag = "std_motor n_rated=3000[ASSUMP]"
    else:  # V-C
        ck = ("C", spec.machine_type, pbucket)
        if ck not in _var_cache:
            _var_cache[ck] = DT.bus_generic_motor(spec.machine_type, t_rated, n_rated, p_rated)
        emap = _var_cache[ck]
        flag = "bus_generic %s n_rated=3000[ASSUMP]" % spec.machine_type
    P_el = DT._map_chain(v_avg, P_wheel, use, r_dyn, total_ratio, n_motors, emap,
                         axle=None, gears=None, adc_eff=0.96)
    return P_el, flag


# ---------------- main ----------------
def build_spec(cfg_row, vid, axle_rows):
    arch = cfg_row["PEVArchitecture"]
    axle_ratio = None
    try:
        axle_ratio = float(cfg_row["Axlegear_Ratio"]) if cfg_row["Axlegear_Ratio"] not in ("", "0", "0.00") else None
    except ValueError:
        pass
    iepc_kw, iepc_g, iepc_r, wheel = parse_iepc(cfg_row["iepc_desc"]) if cfg_row["iepc_desc"] else (None, None, None, False)
    em_n, em_type, em_kw = parse_em(cfg_row["em_desc"]) if cfg_row["em_desc"] else (1, "ASM", None)
    if arch == "E-IEPC":
        rated_kw = iepc_kw
        n_motors = 1
        mtype = em_type
    else:
        rated_kw = (em_kw * em_n) if em_kw else None
        n_motors = em_n
        mtype = em_type
    crr, r_dyn, n_ax, missing = rrc_rdyn_for_vehicle(vid, axle_rows)
    spec = DT.DrivetrainSpec(arch, axle_ratio, iepc_r, iepc_g, n_motors, mtype, rated_kw, r_dyn, wheel)
    spec._crr = crr
    spec._rrc_missing = missing
    return spec


def main():
    cfgs = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "sample_configs.csv")))}
    runs = list(csv.DictReader(open(os.path.join(HERE, "sample_runs.csv"))))
    # axle rows per vehicle
    axle_rows = defaultdict(list)
    with open(os.path.join(HERE, "..", "eea-hdv-2024-join", "axle_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            axle_rows[r["Vehicle_id"]].append(r)

    # group per config from truck_vehicles (VehicleGroup is in sample_configs)
    out_rows = []
    spec_cache = {}
    n = 0
    for run in runs:
        cid = run["config_id"]
        cfg = cfgs.get(cid)
        if not cfg:
            continue
        vid = run["vehicle_id"]
        group = cfg["VehicleGroup"]
        mission = run["mission"]
        if mission not in MISSION_CYCLE:
            continue
        mass = float(run["TotalVehicleMass"])
        cert = float(run["certified_kwh_km"])
        speckey = (cid, vid)
        if speckey not in spec_cache:
            spec_cache[speckey] = build_spec(cfg, vid, axle_rows)
        spec = spec_cache[speckey]
        lo, hi, height = cdxa_corners(group, mission)
        row = dict(config_id=cid, vehicle_id=vid, mass_tag=run["mass_tag"], mission=mission,
                   payload=run["payload"], mass=mass, group=group, arch=spec.arch,
                   comp_method=cfg["comp_method"], certified_kwh_km=cert,
                   rrc_missing=spec._rrc_missing)
        for corner, c0 in (("lo", lo), ("hi", hi)):
            res, flags = one_run(spec, mission, mass, c0, height, group)
            for variant in ("V-A", "V-B", "V-C", "V-D"):
                val = res.get(variant)
                # grid-side correction: HDEV battery-side / 0.995
                grid = (val / 0.995) if val is not None else None
                row["%s_%s_batt" % (variant, corner)] = round(val, 4) if val is not None else ""
                row["%s_%s_grid" % (variant, corner)] = round(grid, 4) if grid is not None else ""
                row["%s_%s_pcterr" % (variant, corner)] = (
                    round(100 * (grid - cert) / cert, 1) if grid is not None else "")
                row["%s_%s_flag" % (variant, corner)] = flags.get(variant, "")
        out_rows.append(row)
        n += 1
        if n % 50 == 0:
            print("  ...%d runs done" % n, flush=True)

    # write
    cols = ["config_id", "vehicle_id", "mass_tag", "mission", "payload", "mass", "group",
            "arch", "comp_method", "certified_kwh_km", "rrc_missing"]
    for variant in ("V-A", "V-B", "V-C", "V-D"):
        for corner in ("lo", "hi"):
            cols += ["%s_%s_batt" % (variant, corner), "%s_%s_grid" % (variant, corner),
                     "%s_%s_pcterr" % (variant, corner), "%s_%s_flag" % (variant, corner)]
    with open(os.path.join(HERE, "hdev_vs_certified.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print("wrote hdev_vs_certified.csv with", len(out_rows), "runs")


if __name__ == "__main__":
    main()
