"""Job 1: build the clean truck test set, config table, mission table and make mapping.

TEST-ONLY. Reads the per-vehicle join files on `main`
(docs/research/eea-hdv-2024-join/) and applies Bob's rules (section 2 of the task).
Nothing in src/ is touched.

Outputs (written next to this script):
  truck_vehicles.csv   one row per in-scope vehicle, cleaned, with complete flag + missing_fields
  truck_configs.csv    exact duplicates collapsed on the full config key
  truck_missions.csv   per config x mission x payload: min/median/max certified kWh/km and range
  make_mapping.csv      every Make-string change applied

Scope (rule 1): ZEV-flag N2/N3 trucks WITH a battery record. Hybrids and the
battery-less ZEV trucks (VECTO 3.3.x placeholders) are dropped.
Rule 2: zeros are missing. Rule 3: completeness is architecture-aware.
Rule 4: collapse only exact duplicates of the full config key.
Rule 5: curb mass kept as min/max in the library; validation uses each vehicle's own mass.
Rule 6: clean Make strings without changing meaning; list every mapping.
"""
import csv
import os
import statistics
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
JOIN = os.path.join(HERE, "..", "eea-hdv-2024-join")
RESEARCH = os.path.join(HERE, "..")

VEH = os.path.join(JOIN, "vehicles_xev.csv")
MIS = os.path.join(JOIN, "missions_xev.csv")
IEPC = os.path.join(RESEARCH, "hdv_2024_iepc.csv")

TRUCK_MISSIONS = {
    "Long Haul", "Long Haul EMS", "Regional Delivery", "Regional Delivery EMS",
    "Urban Delivery", "Municipal Utility", "Construction",
}

# ---- rule 6: Make-string cleaning (meaning unchanged) ----
# key = raw EEA Make string ; value = (clean name, note)
MAKE_MAP = {
    "Mercedes Benz": ("Mercedes-Benz", "hyphen restored; same marque"),
    "DAF Trucks N.V.": ("DAF", "legal-entity suffix removed"),
    "MITSUBISHI FUSO or FUSO": ("Fuso", "case normalised; 'or FUSO' alias removed"),
    "IVECO": ("Iveco", "case normalised"),
    "DESIGNWERK": ("Designwerk", "case normalised"),
}
# flagged makes (rule 6): kept in counts, flagged, excluded from OEM comparison
FLAG_MAKES = {"##VEHICLE_MAKE##", "added", ""}


def truthy(x):
    return str(x).strip().lower() in ("true", "1", "yes")


def is_missing(x):
    """rule 2: empty or a zero value counts as missing."""
    s = str(x).strip()
    if s == "":
        return True
    try:
        return float(s) == 0.0
    except ValueError:
        return False


def clean_make(raw):
    raw = (raw or "").strip()
    if raw in MAKE_MAP:
        return MAKE_MAP[raw][0], False
    if raw in FLAG_MAKES:
        return (raw if raw else "(empty)"), True
    return raw, False


def load_iepc_differential():
    """Vehicle_id -> DifferentialIncluded (str) from hdv_2024_iepc.csv (rule 3)."""
    out = {}
    with open(IEPC, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            out[row["Vehicle_id"]] = row.get("DifferentialIncluded", "").strip()
    return out


def architecture_complete(r, diff_incl):
    """rule 3: architecture-aware completeness. Returns (complete_bool, [missing_fields])."""
    missing = []
    arch = r["PEVArchitecture"].strip()
    axle_missing = is_missing(r["Axlegear_Ratio"])
    iepc_desc = r["iepc_desc"].strip()
    wheel_motor = "wheel=true" in iepc_desc

    if arch in ("E2", "E3"):
        if axle_missing:
            missing.append("axle_ratio")
    elif arch == "E-IEPC":
        # IEPC ratio: parse from iepc_desc "...:rX.XXXXX:..."
        iepc_ratio_ok = any(p.startswith("r") and not is_missing(p[1:])
                            for p in iepc_desc.split(":"))
        if not iepc_ratio_ok:
            missing.append("iepc_ratio")
        if wheel_motor:
            pass  # DesignTypeWheelMotor=true -> no separate axle gear (not a gap)
        else:
            # non-wheel-motor IEPC: axle ratio needed only if IEPC excludes the differential
            diff = (diff_incl or "").strip().lower()
            if diff in ("true", "1", "yes"):
                pass  # differential inside the IEPC -> no separate axle gear
            elif diff in ("false", "0", "no"):
                if axle_missing:
                    missing.append("axle_ratio")
            else:
                # DifferentialIncluded unknown -> cannot confirm; keep out, flag BOB
                if axle_missing:
                    missing.append("axle_ratio[BOB:DifferentialIncluded unknown]")
    else:
        missing.append("unknown_architecture")

    # battery, motor/iepc power, CdxA bin, pneumatic are required for all
    if is_missing(r["bat_installed_kwh"]):
        missing.append("bat_installed_kwh")
    if r["AirDrag_CdxA_range"].strip() == "":
        missing.append("cdxa_bin")
    if r["em_desc"].strip() == "" and iepc_desc == "":
        missing.append("emachine_or_iepc")
    return (len(missing) == 0), missing


# config key = all component/config fields (rule 4)
CONFIG_KEY_FIELDS = [
    "Make_clean", "Model", "VehicleGroup", "AxleConfiguration", "PEVArchitecture",
    "Axlegear_Ratio", "Transmission_NrOfGears", "AirDrag_CdxA_range",
    "bat_packs_inst_use", "bat_installed_kwh", "bat_usable_sim_kwh", "bat_nominal_v",
    "em_desc", "iepc_desc", "Aux_Pneumatic_Technology", "Aux_HVAC_SystemConfiguration",
    "Transmission_PowerTakeOff", "tpmlm_kg",
]


def main():
    diff_map = load_iepc_differential()
    with open(VEH, newline="") as fh:
        allrows = list(csv.DictReader(fh))

    tb = [r for r in allrows
          if truthy(r["is_zev"]) and r["VehicleCategory"] in ("N2", "N3")
          and not is_missing(r["bat_installed_kwh"])]
    print("in-scope truck vehicles:", len(tb))

    # --- clean + completeness ---
    make_changes = Counter()
    for r in tb:
        clean, flagged = clean_make(r["Make"])
        r["Make_clean"] = clean
        r["make_flagged"] = "yes" if flagged else "no"
        if r["Make"].strip() != clean and not flagged:
            make_changes[(r["Make"].strip(), clean)] += 1
        comp, missing = architecture_complete(r, diff_map.get(r["Vehicle_id"], ""))
        r["complete"] = "yes" if comp else "no"
        r["missing_fields"] = ";".join(missing)

    # ---- make_mapping.csv ----
    with open(os.path.join(HERE, "make_mapping.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["raw_make", "clean_make", "note", "vehicle_count", "flagged"])
        for raw, (clean, note) in MAKE_MAP.items():
            cnt = sum(1 for r in tb if r["Make"].strip() == raw)
            if cnt:
                w.writerow([raw, clean, note, cnt, "no"])
        for raw in FLAG_MAKES:
            cnt = sum(1 for r in tb if r["Make"].strip() == raw)
            if cnt:
                w.writerow([raw if raw else "(empty)", raw if raw else "(empty)",
                            "flagged: excluded from OEM comparison", cnt, "yes"])

    # ---- truck_vehicles.csv ----
    out_cols = (["Vehicle_id", "Make", "Make_clean", "make_flagged", "Model",
                 "VehicleCategory", "VehicleGroup", "AxleConfiguration", "PEVArchitecture",
                 "CorrectedActualMass", "tpmlm_kg", "Axlegear_Ratio",
                 "Transmission_NrOfGears", "AirDrag_CdxA_range", "AirDrag_CertificationMethod",
                 "Axlegear_CertificationMethod",
                 "bat_packs_inst_use", "bat_installed_kwh", "bat_usable_sim_kwh",
                 "bat_nominal_v", "bat_cert_method", "em_desc", "em_rated_kw_total",
                 "em_cert_method", "iepc_desc", "iepc_max_cont_kw", "iepc_cert_method",
                 "Aux_Pneumatic_Technology", "Aux_HVAC_SystemConfiguration",
                 "Transmission_PowerTakeOff", "cap_capacitance_f",
                 "reg_count", "reg_dk", "reg_countries", "reg_first", "reg_last",
                 "SimulationToolVersion", "SimulationDate",
                 "complete", "missing_fields"])
    with open(os.path.join(HERE, "truck_vehicles.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=out_cols, extrasaction="ignore")
        w.writeheader()
        for r in tb:
            w.writerow(r)

    # ---- truck_configs.csv (rule 4: collapse exact dupes on config key) ----
    groups = defaultdict(list)
    for r in tb:
        key = tuple(r.get(f, "") for f in CONFIG_KEY_FIELDS)
        groups[key].append(r)

    cfg_cols = CONFIG_KEY_FIELDS + [
        "config_id", "vehicle_count", "vehicle_ids", "registrations", "dk_registrations",
        "curb_mass_min", "curb_mass_max", "complete",
        "bat_cert_method", "em_cert_method", "iepc_cert_method",
        "Axlegear_CertificationMethod", "AirDrag_CertificationMethod",
        "vecto_version_min", "vecto_version_max", "sim_date_min", "sim_date_max",
        "make_flagged",
    ]
    vid_to_cfg = {}
    with open(os.path.join(HERE, "truck_configs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cfg_cols, extrasaction="ignore")
        w.writeheader()
        for i, (key, rs) in enumerate(sorted(groups.items())):
            cid = "C%04d" % i
            for r in rs:
                vid_to_cfg[r["Vehicle_id"]] = cid
            masses = [float(r["CorrectedActualMass"]) for r in rs
                      if not is_missing(r["CorrectedActualMass"])]
            regs = sum(int(float(r["reg_count"] or 0)) for r in rs)
            dk = sum(int(float(r["reg_dk"] or 0)) for r in rs)
            versions = sorted({r["SimulationToolVersion"].strip() for r in rs if r["SimulationToolVersion"].strip()})
            dates = sorted({r["SimulationDate"].strip() for r in rs if r["SimulationDate"].strip()})
            d = {f: rs[0].get(f, "") for f in CONFIG_KEY_FIELDS}
            d.update(dict(
                config_id=cid, vehicle_count=len(rs),
                vehicle_ids=";".join(r["Vehicle_id"] for r in rs[:50]),
                registrations=regs, dk_registrations=dk,
                curb_mass_min=min(masses) if masses else "", curb_mass_max=max(masses) if masses else "",
                complete=rs[0]["complete"],
                bat_cert_method=rs[0]["bat_cert_method"], em_cert_method=rs[0]["em_cert_method"],
                iepc_cert_method=rs[0]["iepc_cert_method"],
                Axlegear_CertificationMethod=rs[0]["Axlegear_CertificationMethod"],
                AirDrag_CertificationMethod=rs[0]["AirDrag_CertificationMethod"],
                vecto_version_min=versions[0] if versions else "",
                vecto_version_max=versions[-1] if versions else "",
                sim_date_min=dates[0] if dates else "", sim_date_max=dates[-1] if dates else "",
                make_flagged=rs[0]["make_flagged"],
            ))
            w.writerow(d)
    print("configs (exact-duplicate collapsed):", len(groups))

    # ---- truck_missions.csv ----
    vids_in_scope = {r["Vehicle_id"] for r in tb}
    # gather mission rows for in-scope trucks only, truck missions only
    mrows = defaultdict(list)  # (config_id, mission, payload) -> list of (kwh_km, range, vid)
    with open(MIS, newline="") as fh:
        for row in csv.DictReader(fh):
            vid = row["Vehicle_id"]
            if vid not in vids_in_scope:
                continue
            if row["Mission"] not in TRUCK_MISSIONS:
                continue
            kwh = row["ElectricEnergy_kwh_km"].strip()
            if is_missing(kwh):
                continue
            cid = vid_to_cfg.get(vid)
            if cid is None:
                continue
            rng = row["ActualChargeDepletingRange"].strip()
            payload = row["Payload"].strip()
            mrows[(cid, row["Mission"], payload)].append(
                (float(kwh), float(rng) if rng and not is_missing(rng) else None, vid,
                 row.get("Mode", ""), row.get("ResultType", "")))

    mcols = ["config_id", "mission", "payload", "vehicle_count",
             "kwh_km_min", "kwh_km_median", "kwh_km_max",
             "range_km_min", "range_km_median", "range_km_max",
             "mode", "result_type"]
    with open(os.path.join(HERE, "truck_missions.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(mcols)
        for (cid, mission, payload), vals in sorted(mrows.items()):
            kwhs = [v[0] for v in vals]
            rngs = [v[1] for v in vals if v[1] is not None]
            modes = ";".join(sorted({v[3] for v in vals}))
            rts = ";".join(sorted({v[4] for v in vals}))
            w.writerow([cid, mission, payload, len(vals),
                        round(min(kwhs), 4), round(statistics.median(kwhs), 4), round(max(kwhs), 4),
                        round(min(rngs), 1) if rngs else "",
                        round(statistics.median(rngs), 1) if rngs else "",
                        round(max(rngs), 1) if rngs else "",
                        modes, rts])
    print("mission (config x mission x payload) rows:", len(mrows))

    # ---- summary counts to stdout + counts file ----
    comp = [r for r in tb if r["complete"] == "yes"]
    print("complete vehicles:", len(comp), "incomplete:", len(tb) - len(comp))
    print("by make:", dict(Counter(r["Make_clean"] for r in tb)))
    print("by architecture:", dict(Counter(r["PEVArchitecture"] for r in tb)))
    complete_cfgs = sum(1 for key, rs in groups.items() if rs[0]["complete"] == "yes")
    print("complete configs:", complete_cfgs, "of", len(groups))


if __name__ == "__main__":
    main()
