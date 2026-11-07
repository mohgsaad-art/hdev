"""Job 3 sample selection: pick 40-60 complete configs spread across make,
architecture, vehicle group, component certification method and battery size.

Writes:
  sample_configs.csv   the chosen configs with the pick reason
  sample_runs.csv      one row per (config, mission, payload, vehicle-at-mass) to run
  sample_selection.md   the human-readable rationale (Job 3 deliverable)

TEST-ONLY. Reads truck_configs.csv / truck_vehicles.csv / truck_missions.csv and
the per-vehicle mission masses from the join. No src/ touched.
"""
import csv
import os
import statistics
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
JOIN = os.path.join(HERE, "..", "eea-hdv-2024-join")


def arch_of(r):
    a = r["PEVArchitecture"]
    if a == "E-IEPC":
        return "E-IEPC-wheel" if "wheel=true" in r["iepc_desc"] else "E-IEPC"
    return a


def bat_bucket(kwh):
    kwh = float(kwh)
    if kwh < 150:
        return "small(<150)"
    if kwh < 400:
        return "mid(150-400)"
    if kwh < 700:
        return "large(400-700)"
    return "xl(>=700)"


def comp_method(r):
    # one label per config for the measured-vs-standard split
    # prefer the drivetrain/motor method; batteries are mostly standard
    for k in ("iepc_cert_method", "em_cert_method"):
        if r[k] == "Measured":
            return "measured"
    for k in ("iepc_cert_method", "em_cert_method", "bat_cert_method"):
        if "Standard" in r[k]:
            return "standard"
    return r["bat_cert_method"].lower() or "unknown"


def main():
    cfg = [r for r in csv.DictReader(open(os.path.join(HERE, "truck_configs.csv")))
           if r["complete"] == "yes" and r["make_flagged"] == "no"]
    for r in cfg:
        r["arch"] = arch_of(r)
        r["bat_bucket"] = bat_bucket(r["bat_installed_kwh"])
        r["comp_method"] = comp_method(r)

    # stratified greedy pick: make sure every (make) and every (arch) appears,
    # and spread across group / bat bucket / cert method. Prefer configs with more
    # vehicles (more real registrations behind them).
    cfg.sort(key=lambda r: -int(r["vehicle_count"]))
    picked = []
    seen_make = Counter()
    seen_arch = Counter()
    seen_grp = Counter()
    seen_bat = Counter()
    seen_cm = Counter()

    def want(r):
        # score how much this config adds to coverage
        s = 0
        if seen_make[r["Make_clean"]] == 0:
            s += 100
        if seen_arch[r["arch"]] == 0:
            s += 100
        if seen_grp[r["VehicleGroup"]] == 0:
            s += 20
        if seen_bat[r["bat_bucket"]] == 0:
            s += 20
        if seen_cm[r["comp_method"]] == 0:
            s += 20
        # soft caps so no single stratum dominates
        s -= 3 * seen_make[r["Make_clean"]]
        s -= 2 * seen_arch[r["arch"]]
        return s

    TARGET = 52
    remaining = cfg[:]
    while remaining and len(picked) < TARGET:
        remaining.sort(key=lambda r: (-want(r), -int(r["vehicle_count"])))
        r = remaining.pop(0)
        reasons = []
        if seen_make[r["Make_clean"]] == 0:
            reasons.append("first config for make " + r["Make_clean"])
        if seen_arch[r["arch"]] == 0:
            reasons.append("first config for architecture " + r["arch"])
        if seen_grp[r["VehicleGroup"]] == 0:
            reasons.append("first config for group " + r["VehicleGroup"])
        if seen_bat[r["bat_bucket"]] == 0:
            reasons.append("first config in battery bucket " + r["bat_bucket"])
        if seen_cm[r["comp_method"]] == 0:
            reasons.append("first config with " + r["comp_method"] + " components")
        if not reasons:
            reasons.append("fills spread; " + r["vehicle_count"] + " vehicles behind it")
        r["pick_reason"] = "; ".join(reasons)
        picked.append(r)
        seen_make[r["Make_clean"]] += 1
        seen_arch[r["arch"]] += 1
        seen_grp[r["VehicleGroup"]] += 1
        seen_bat[r["bat_bucket"]] += 1
        seen_cm[r["comp_method"]] += 1

    # --- write sample_configs.csv ---
    cols = ["config_id", "Make_clean", "Model", "VehicleGroup", "arch", "PEVArchitecture",
            "Axlegear_Ratio", "iepc_desc", "em_desc", "bat_installed_kwh", "bat_usable_sim_kwh",
            "bat_nominal_v", "bat_bucket", "AirDrag_CdxA_range", "AxleConfiguration",
            "comp_method", "bat_cert_method", "em_cert_method", "iepc_cert_method",
            "Aux_Pneumatic_Technology", "vehicle_count", "registrations",
            "curb_mass_min", "curb_mass_max", "pick_reason"]
    with open(os.path.join(HERE, "sample_configs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in picked:
            w.writerow(r)
    print("picked", len(picked), "configs")
    print("by arch:", dict(Counter(r["arch"] for r in picked)))
    print("by make:", dict(Counter(r["Make_clean"] for r in picked)))
    print("by comp_method:", dict(Counter(r["comp_method"] for r in picked)))
    print("by bat_bucket:", dict(Counter(r["bat_bucket"] for r in picked)))

    # --- build sample_runs.csv: per config x mission x payload x (median/min/max mass vehicle) ---
    picked_ids = {r["config_id"] for r in picked}
    # map config -> its vehicle ids (from truck_vehicles via config membership)
    # rebuild config membership using the same key as build_test_set
    from build_test_set import CONFIG_KEY_FIELDS, is_missing  # reuse
    vehrows = list(csv.DictReader(open(os.path.join(HERE, "truck_vehicles.csv"))))
    # recompute config_id mapping identically: we need the config_id order from truck_configs
    # Simpler: truck_configs stores vehicle_ids (first 50). Use those.
    cfg_veh = {}
    for r in csv.DictReader(open(os.path.join(HERE, "truck_configs.csv"))):
        cfg_veh[r["config_id"]] = r["vehicle_ids"].split(";") if r["vehicle_ids"] else []

    # per-vehicle per-mission mass + certified kwh from missions_xev
    TRUCK_MISSIONS = {"Long Haul", "Long Haul EMS", "Regional Delivery",
                      "Regional Delivery EMS", "Urban Delivery", "Municipal Utility", "Construction"}
    want_vids = set()
    for cid in picked_ids:
        want_vids.update(cfg_veh.get(cid, []))
    mdata = defaultdict(list)  # (vid, mission) -> list of (payload, mass, kwh, range)
    with open(os.path.join(JOIN, "missions_xev.csv"), newline="") as fh:
        for row in csv.DictReader(fh):
            if row["Vehicle_id"] not in want_vids:
                continue
            if row["Mission"] not in TRUCK_MISSIONS:
                continue
            if is_missing(row["ElectricEnergy_kwh_km"]):
                continue
            mdata[(row["Vehicle_id"], row["Mission"])].append(
                (row["Payload"], row["TotalVehicleMass"], row["ElectricEnergy_kwh_km"],
                 row["ActualChargeDepletingRange"]))

    vid_to_cfg = {}
    for cid in picked_ids:
        for v in cfg_veh.get(cid, []):
            vid_to_cfg[v] = cid

    runs = []
    for cid in picked_ids:
        vids = cfg_veh.get(cid, [])
        if not vids:
            continue
        # pick representative vehicles by TotalVehicleMass on a reference mission (Regional Delivery if present)
        ref_mass = {}
        for v in vids:
            for miss in ("Regional Delivery", "Urban Delivery", "Long Haul", "Construction", "Municipal Utility"):
                rows = mdata.get((v, miss))
                if rows:
                    ref_mass[v] = statistics.mean(float(x[1]) for x in rows)
                    break
        vids_m = [v for v in vids if v in ref_mass]
        if not vids_m:
            continue
        vids_m.sort(key=lambda v: ref_mass[v])
        chosen = {vids_m[len(vids_m) // 2]: "median-mass"}
        chosen[vids_m[0]] = "min-mass" if vids_m[0] not in chosen else chosen[vids_m[0]]
        chosen[vids_m[-1]] = "max-mass" if vids_m[-1] not in chosen else chosen[vids_m[-1]]
        for v, tag in chosen.items():
            for (vv, miss), rows in mdata.items():
                if vv != v:
                    continue
                for payload, mass, kwh, rng in rows:
                    runs.append(dict(config_id=cid, vehicle_id=v, mass_tag=tag, mission=miss,
                                     payload=payload, TotalVehicleMass=mass,
                                     certified_kwh_km=kwh, certified_range_km=rng))

    with open(os.path.join(HERE, "sample_runs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["config_id", "vehicle_id", "mass_tag", "mission",
                                           "payload", "TotalVehicleMass", "certified_kwh_km",
                                           "certified_range_km"])
        w.writeheader()
        for r in runs:
            w.writerow(r)
    print("sample_runs rows:", len(runs))
    return picked, runs


if __name__ == "__main__":
    main()
