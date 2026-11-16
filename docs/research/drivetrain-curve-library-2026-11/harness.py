"""Bridge to the v2 EEA truck-validation harness (branch eea-truck-validation-2026-11, commit 73990f0).

The v2 harness is NOT edited or re-implemented. This module imports it, calls its own
`run_one` (which calls Bob's notebook copy `consumption_engine`, `driver_model`, `force_engine`),
and keeps the per-row arrays the drivetrain methods need:

    P_wheel [W]   wheel power from the physics (zero drivetrain drag, as in v2 variant V-A)
    P_aux   [W]   per-row electric auxiliary power (v2 aux_per_label.csv path)
    M, V, v_avg   driver mode, speed, step-average speed
    km            cycle distance
    E_A           the v2 V-A result (today's fixed 0.95*0.95*0.98 / regen 0.95), battery side, kWh/km

Where the v2 harness lives (it is on another branch, not on main):
    export V2_HARNESS_DIR=/path/to/docs/research/eea-truck-validation-2026-11
    export VECTO_SRC=/path/to/VECTO   (fork, branch IEPC-experiments, commit b8d6126)
Run `bash setup_v2_worktree.sh` once to create the worktree next to the repo.
"""
import csv
import os
import sys
import pickle
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JOIN = os.path.join(REPO, "docs", "research", "eea-hdv-2024-join")
CACHE = os.path.join(HERE, "cache")

V2_DIR = os.environ.get(
    "V2_HARNESS_DIR",
    os.path.abspath(os.path.join(REPO, "..", "hdev-v2", "docs", "research", "eea-truck-validation-2026-11")))
os.environ.setdefault("VECTO_SRC", os.path.abspath(os.path.join(REPO, "..", "VECTO")))

if not os.path.isfile(os.path.join(V2_DIR, "run_hdev.py")):
    raise SystemExit("BLOCKED: v2 harness not found at %s (set V2_HARNESS_DIR, see setup_v2_worktree.sh)" % V2_DIR)
sys.path.insert(0, V2_DIR)
import run_hdev as RH          # noqa: E402  (v2 harness, unchanged)
import hdev_test_module as H   # noqa: E402  (notebook copy used by v2, unchanged)

CHARGING_ETA = 0.995           # job prompt s.0/s.2: certified kWh/km is grid-side, energy / eta ~ 0.995
MISSIONS_BASE = ("Regional Delivery", "Urban Delivery", "Long Haul", "Construction",
                 "Regional Delivery EMS", "Long Haul EMS")      # Municipal excluded (v2 rule R12)


class _Cfg(dict):
    def __missing__(self, k):
        return ""


_STATE = {}


def _state():
    if _STATE:
        return _STATE
    cfgs = {}
    with open(os.path.join(V2_DIR, "truck_configs.csv")) as fh:
        for r in csv.DictReader(fh):
            cfgs[r["config_id"]] = _Cfg(r)
    axle_rows = defaultdict(list)
    with open(os.path.join(JOIN, "axle_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            axle_rows[r["Vehicle_id"]].append(r)
    veh_extra, pneu_of, steer_of = {}, {}, {}
    with open(os.path.join(JOIN, "vehicles_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            veh_extra[r["Vehicle_id"]] = r
            pneu_of[r["Vehicle_id"]] = r.get("Aux_Pneumatic_Technology", "")
    with open(os.path.join(JOIN, "steering_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            steer_of[r["Vehicle_id"]] = r.get("SteeringpumpTechnology", "")
    _STATE.update(cfgs=cfgs, axle_rows=axle_rows, veh_extra=veh_extra, pneu_of=pneu_of, steer_of=steer_of)
    return _STATE


def config_runs(config_id):
    """Certified results of the median-mass vehicle of one config (7 Nov rule: one vehicle per exact
    config; select_sample.py picks the median of the vehicles' mean TotalVehicleMass).
    Returns (vehicle_id, [dict(mission, payload, mass, cert)])."""
    st = _state()
    if "missions" not in st:
        mdata = defaultdict(list)
        with open(os.path.join(JOIN, "missions_xev.csv"), newline="") as fh:
            for row in csv.DictReader(fh):
                if row["Mission"] not in RH.MISSION_CYCLE:
                    continue
                if row["ElectricEnergy_kwh_km"] in ("", "NA", "nan"):
                    continue
                mdata[row["Vehicle_id"]].append(row)
        st["missions"] = mdata
    cfg = st["cfgs"][config_id]
    vids = [v for v in cfg["vehicle_ids"].split(";") if v in st["missions"]]
    if not vids:
        return None, []

    def refmass(v):
        for miss in ("Regional Delivery", "Urban Delivery", "Long Haul", "Construction", "Municipal Utility"):
            rows = [float(r["TotalVehicleMass"]) for r in st["missions"][v] if r["Mission"] == miss]
            if rows:
                return float(np.mean(rows))
        return None
    ms = [(refmass(v), v) for v in vids]
    ms = sorted([x for x in ms if x[0] is not None], key=lambda t: t[0])
    if not ms:
        return None, []
    vid = ms[len(ms) // 2][1]
    seen, out = set(), []
    for r in st["missions"][vid]:
        key = (r["Mission"], round(float(r["Payload"]), 1))
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(mission=r["Mission"], payload=float(r["Payload"]), mass=float(r["TotalVehicleMass"]),
                        cert=float(r["ElectricEnergy_kwh_km"])))
    return vid, out


def build_record(config_id, vid, mission, payload, mass, cert):
    """One physics run through the v2 harness. Returns a record dict with per-row arrays or
    dict(skip=reason)."""
    st = _state()
    cfg = st["cfgs"][config_id]
    group = cfg["VehicleGroup"]
    spec = RH.build_spec(cfg, vid, st["axle_rows"], st["veh_extra"])
    setup = RH.load_setup().get((group, mission), {})
    trailer_code = setup.get("trailer_code", "")
    geom = RH.vehicle_rrc_inertia(vid, st["axle_rows"], setup, mass, group, mission)
    if geom.get("skip"):
        return dict(skip=geom["skip"])
    spec.r_dyn = geom["r_dyn"]
    cdxa0 = RH.cdxa_for(group, mission, trailer_code)
    if cdxa0 is None:
        return dict(skip="no_cdxa_setup")
    p_max = spec.rated_kw_total * 1000.0 if spec.rated_kw_total else None
    res = RH.run_one(spec, geom, mission, mass, group, trailer_code, st["pneu_of"].get(vid, ""),
                     st["steer_of"].get(vid, ""), cdxa0, p_max)
    if res.get("skip"):
        return dict(skip=res["skip"])
    if "_P_wheel" not in res:
        return dict(skip="no_VA_base")
    arch = spec.arch + ("-wheel" if (spec.arch == "E-IEPC" and spec.wheel_motor) else "")
    # aero sensitivity dP/dCdxA0 [W/m2] = rho * L * W1(v_avg): P_wheel is linear in CdxA0 because
    # cdxa_row = CdxA0*W1(v) + W2(v)  (consumption_engine lines 521-527, run_one: cdxa_tab = cdxa0*W1 + W2)
    grid, W1, _W2 = RH.crosswind_tables(group, mission)
    v_avg = np.asarray(res["_v_avg"], float)
    v1 = np.asarray(res["_V"], float)
    v2 = 2.0 * v_avg - v1                                   # force_engine: v_avg = (v1 + v2) / 2
    L = (v1 + v2) * (v1 ** 2 + v2 ** 2) / 8.0               # force_engine
    aero_k = RH.RHO_VECTO * L * np.interp(np.clip(v_avg * 3.6, grid[0], grid[-1]), grid, W1)
    return dict(
        config_id=config_id, vehicle_id=vid, mission=mission, payload=payload, mass=mass, cert=cert,
        group=group, arch=arch, n_gears=spec.n_gears, rated_kw=spec.rated_kw_total, r_dyn=geom["r_dyn"],
        cdxa0=cdxa0, aero_k=aero_k, E_A=res["results"]["V-A"],
        P_wheel=np.asarray(res["_P_wheel"], float), P_aux=np.asarray(res["_P_aux_row"], float),
        M=np.asarray(res["_M"]), V=np.asarray(res["_V"], float), v_avg=np.asarray(res["_v_avg"], float),
        km=float(res["_km"]), aux_notes=";".join(res["aux_notes"]))


V_NO_REGEN = 5.0 / 3.6     # = RH.V_NO_REGEN (notebook v_min_coast)


def compact(rec):
    """Keep only what the drivetrain step needs, exactly following consumption_engine lines 530-532:
    rows where traction power is forced to zero (M == 3, or M == 4 at V <= v_no_regen) are dropped; rows that
    remain carry P_wheel, v_avg, aero_k and an 'engaged' flag (M != 0). P_aux only enters as a sum."""
    M, V, Pw = rec["M"], rec["V"], rec["P_wheel"]
    applied = ~((M == 3) | ((M == 4) & (V <= V_NO_REGEN)))
    keep = applied & ((M != 0) | (Pw != 0))
    out = {k: v for k, v in rec.items() if k not in ("P_wheel", "P_aux", "M", "V", "v_avg", "aero_k")}
    out["P_wheel"] = Pw[keep].astype(np.float64)
    out["v_avg"] = rec["v_avg"][keep].astype(np.float64)
    out["aero_k"] = rec["aero_k"][keep].astype(np.float64)
    out["engaged"] = (M[keep] != 0)
    out["E_aux_Ws"] = float(np.sum(rec["P_aux"]))
    return out


def build_config_records(config_id):
    vid, rows = config_runs(config_id)
    recs, skipped = [], []
    for r in rows:
        if r["mission"] not in MISSIONS_BASE:
            continue
        try:
            rec = build_record(config_id, vid, r["mission"], r["payload"], r["mass"], r["cert"])
        except Exception as e:                      # a crash is reported, not hidden (job rule 6)
            rec = dict(skip="BUG:%s:%s" % (type(e).__name__, str(e)[:80]))
        if "skip" in rec:
            skipped.append((config_id, r["mission"], r["payload"], rec["skip"]))
        else:
            recs.append(compact(rec))
    return recs, skipped


def _build_one(cid):
    import warnings
    warnings.filterwarnings("ignore")
    return build_config_records(cid)


def load_or_build(config_ids, tag, processes=1):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "records_%s.pkl" % tag)
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    recs, skipped = [], []
    if processes and processes > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(processes) as pool:
            results = pool.map(_build_one, list(config_ids), chunksize=4)     # map keeps input order
    else:
        results = [_build_one(cid) for cid in config_ids]
    for r, s_ in results:
        recs += r
        skipped += s_
    with open(path, "wb") as fh:
        pickle.dump((recs, skipped), fh)
    return recs, skipped
