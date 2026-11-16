"""Part 1.1 and 1.2 (cluster comparison): every input of every DAF group 5 config, per mission, next to the VECTO
declaration data (file + line in mohgsaad-art/VECTO, branch IEPC-experiments, commit b8d6126).

Outputs
  p1_daf_inputs_per_mission.csv   one row per certified result (config x mission x payload): all inputs the harness used
  p1_daf_inputs_per_config.csv    one row per config: component data, labels, fit values, cluster
  p1_daf_vecto_refs.csv           input -> VECTO file + line (checked by reading the line) + value used
  p1_daf_cluster_compare.csv      every input variable: values in HIGH-F0 vs LOW-F0, does it separate the two clusters
  p1_daf_iepc_component.csv       IEPC certification number / digest per config vs F0, eta_d (the variable that separates)
"""
import csv
import os
from collections import Counter, defaultdict

import numpy as np

import lib_g5 as L

HN, RH = L.HN, L.HN.RH
HERE = L.HERE
VSRC = os.environ["VECTO_SRC"]
DECL = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration")
CORE = os.path.join(VSRC, "VectoCore", "VectoCore")
JOIN = HN.JOIN
RESEARCH = os.path.abspath(os.path.join(L.LIB, ".."))
THRESH = 800.0


def line_of(path, needle, nth=1, enc="latin-1"):
    """1-based line number of the nth line containing needle (read by opening the file)."""
    k = 0
    with open(path, encoding=enc, errors="replace") as fh:
        for i, ln in enumerate(fh, 1):
            if needle in ln:
                k += 1
                if k == nth:
                    return i, ln.strip()
    raise SystemExit("BLOCKED: %r not found in %s" % (needle, path))


def rel(p):
    return os.path.relpath(p, VSRC)


def vecto_refs():
    rows = []

    def add(inp, path, needle, used, nth=1):
        i, txt = line_of(path, needle, nth)
        rows.append(dict(input=inp, vecto_file=rel(path), line=i, vecto_text=" ".join(txt.split())[:170], used_in_harness_as=used))
    seg = os.path.join(DECL, "SegmentTable.csv")
    # group 5, Tractor, 4x2, Vocational 0 (HDV group, Vocational, Valid, Category, Axle Conf.)
    with open(seg, encoding="latin-1") as fh:
        for i, ln in enumerate(fh, 1):
            p = [x.strip() for x in ln.split(",")]
            if len(p) > 5 and p[0] == "5" and p[1] == "0" and p[3] == "Tractor" and p[4] == "4x2":
                rows.append(dict(input="segment (payload pairs, trailer, axle shares, CdxA default, height)", vecto_file=rel(seg), line=i,
                                 vecto_text=" ".join(ln.split())[:170], used_in_harness_as="mission_setup.csv rows (hdv_group 5, Tractor, 4x2)"))
                break
    wh = os.path.join(DECL, "Wheels.csv")
    for dim in ("315/70 R22.5", "385/55 R22.5", "315/80 R22.5", "385/65 R22.5"):
        add("tyre dimension %s (r_dyn, inertia)" % dim, wh, dim, "run_hdev.load_wheels (d, inertia, f)")
    bt = os.path.join(DECL, "Body_Trailers_Weights.csv")
    for code, what in (("ST1    ", "semitrailer ST1: delta CdxA 0/2.1, trailer tyre 385/65 R22.5"), ("STT1   ", "construction semitrailer STT1: 0/0"), ("T2     ", "EMS second trailer T2 1.5/1.5")):
        add("trailer " + code.strip(), bt, code, what)
    add("electric system ES (Standard technology)", os.path.join(DECL, "VAUX", "ES-Tech.csv"), "Standard technology", "aux_per_label.csv ES x AlternatorEfficiency 0.7")
    add("pneumatic system PS 'Large Supply + AMS + elec. driven'", os.path.join(DECL, "VAUX", "PS-Table.csv"), "Large Supply + AMS + elec. driven", "aux_per_label.csv PS (the *_el columns)")
    add("HVAC Default, group 5", os.path.join(DECL, "VAUX", "HVAC-Table.csv"), "Default    , 5 ", "aux_per_label.csv HVAC / 0.8")
    add("condenser (Lorry)", os.path.join(DECL, "VAUX", "Cond-Table.csv"), "Lorry", "aux_per_label.csv cond")
    dd = os.path.join(CORE, "Models", "Declaration", "DeclarationData.cs")
    add("g", dd, "GravityAccelleration =", "9.80665")
    add("air density", dd, "AirDensity =", "1.188")
    add("alternator efficiency", dd, "AlternatorEfficiency =", "0.7")
    add("HVAC electric efficiency factor", dd, "HVACElectricEfficiencyFactor =", "0.8")
    add("trailer rolling resistance coefficient", dd, "RollResistanceCoefficient = 0.0055", "0.0055")
    add("trailer tyre test load", dd, "TyreTestLoad = 37500", "37500 N")
    ad = os.path.join(CORE, "InputData", "Reader", "DataObjectAdapter", "SimulationComponents", "AirdragDataAdapter.cs")
    add("declared CdxA replaced by default on Construction", ad, "mission.MissionType == MissionType.Construction", "uses_declared = measured and mission != Construction")
    add("CdxA + trailer DeltaCdA", ad, "retVal.DeclaredAirdragArea + mission.Trailer.Sum", "cdxa0 = base + delta")
    add("tyre test load FzISO is a declared input (not in EEA)", os.path.join(CORE, "InputData", "FileIO", "XML", "Declaration", "DataProvider", "XMLDeclarationTyreDataProvider.cs"),
        "TyreTestLoad =>", "NO SOURCE in EEA; harness stand-in 31300 N")
    add("rolling resistance and wheel inertia of the vehicle", os.path.join(CORE, "Models", "SimulationComponent", "Data", "VehicleData.cs"),
        "ComputeRollResistanceAndReducedMassWheels()", "run_hdev.vehicle_rrc_inertia")
    ts = os.path.join(CORE, "Models", "Declaration", "TruckSegments.cs")
    add("trailers per mission", ts, "GetTrailers", "harness.vecto_trailers")
    add("default CdxA / construction CdxA", ts, "DefaultCDxA = ReadDefaultAirDragValue", "harness.vecto_cdxa default")
    for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul", "Construction"):
        rows.append(dict(input="cycle %s" % cyc, vecto_file=rel(os.path.join(DECL, "MissionCycles", cyc + ".vdri")), line=1,
                         vecto_text="first line is the header; data from line 2", used_in_harness_as="run_hdev.load_cycle"))
    ch = os.path.join(VSRC, "CHANGES.md")
    add("VECTO 4.1.0 added missing mission profiles (Construction for non-vocational)", ch, "CodeEU-577", "explains why 4.0.x results have no Construction mission")
    rows.append(dict(input="IEPC loss map of the DAF component (certification R00/11*4203*00, 379*I*00743*00)", vecto_file="NO SOURCE", line="",
                     vecto_text="EEA gives certification number, digest, rated power, gears, lowest ratio only", used_in_harness_as="not used: C and L4b fit the losses"))
    return rows


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    ft = L.fits_c_l4b()
    daf = [c for c in ids if cfg[c]["Make_clean"] == "DAF"]
    st = HN._state()
    veh_extra, steer_of = st["veh_extra"], st["steer_of"]
    ie = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(RESEARCH, "hdv_2024_iepc.csv"), encoding="utf-8-sig")):
        ie[r["Vehicle_id"]].append(r)
    setup = RH.load_setup()
    from cdxa_ranges import CDXA_RANGES

    cfg_rows, rec_rows, comp_rows = [], [], []
    for cid in daf:
        rr = by[cid]
        c = cfg[cid]
        vid = rr[0]["vehicle_id"]
        ve = veh_extra[vid]
        axles = st["axle_rows"][vid]
        iepc = ie[vid][0] if ie.get(vid) else {}
        fc, fl = ft["C"][cid], ft["L4b"][cid]
        cluster = "HIGH_F0" if fc["values"][2] >= THRESH else "LOW_F0"
        ms = Counter(r["mission"] for r in rr)
        rng = CDXA_RANGES[c["AirDrag_CdxA_range"].strip()]
        tyre = " | ".join("axle%s %s RRC=%s twin=%s" % (a["AxleNumber"], a["TyreDimension"], a["SpecificRRC"], a["Twintyres"] or "false") for a in axles)
        cfg_rows.append(dict(
            config_id=cid, cluster=cluster, make=c["Make_clean"], model=c["Model"], n_vehicles_in_config=len(c["vehicle_ids"].split(";")),
            vehicle_id_used=vid[:14] + "...", sim_tool_version_min=c["vecto_version_min"], sim_tool_version_max=c["vecto_version_max"],
            sim_date_min=c["sim_date_min"], axle_config=c["AxleConfiguration"], vehicle_category=ve.get("VehicleCategory", ""),
            sleeper_cab=ve.get("SleeperCab", ""), iepc_desc=c["iepc_desc"], iepc_rated_kW=fc["row"]["iepc_rated_kW"],
            iepc_max_cont_kW=ve.get("iepc_max_cont_kw", ""), n_gears=rr[0]["n_gears"], lowest_total_ratio=iepc.get("LowestTotalTransmissionRatio", ""),
            axlegear_ratio_eea=c["Axlegear_Ratio"], axlegear_cert_method=c["Axlegear_CertificationMethod"],
            iepc_cert_method=c["iepc_cert_method"], iepc_certification_number=iepc.get("CertificationNumber", ""),
            iepc_digest=iepc.get("DigestValue", ""), differential_included=iepc.get("DifferentialIncluded", ""),
            airdrag_method=c["AirDrag_CertificationMethod"], cdxa_range=c["AirDrag_CdxA_range"], cdxa_range_lo=rng[0], cdxa_range_hi=rng[1],
            cdxa_fit_C=round(fc["cdxa"], 4), cdxa_fit_L4b=round(fl["cdxa"], 4), tyres=tyre,
            fziso_N="NO SOURCE (EEA has no FzISO); harness stand-in %.0f" % RH.FZISO_STANDIN,
            aux_pneumatic=ve.get("Aux_Pneumatic_Technology", ""), aux_hvac_system=ve.get("Aux_HVAC_SystemConfiguration", ""),
            aux_steering=steer_of.get(vid, ""), battery_installed_kwh=c["bat_installed_kwh"], battery_usable_sim_kwh=c["bat_usable_sim_kwh"],
            tpmlm_kg=c["tpmlm_kg"], curb_mass_min=c["curb_mass_min"], curb_mass_max=c["curb_mass_max"], n_results=len(rr),
            missions=";".join("%s:%d" % (k, v) for k, v in sorted(ms.items())), has_construction=("Construction" in ms),
            C_eta_d=round(fc["values"][0], 4), C_eta_r=round(fc["values"][1], 4), C_F0_N=round(fc["values"][2], 1), C_at_bound=fc["row"]["at_bound"],
            C_mean_abs_err_pct=fc["row"]["in_sample_mean_abs_err_pct"], L4b_a_W=round(fl["values"][0], 1), L4b_b_perW=fl["values"][1],
            L4b_c_W_per_mps=round(fl["values"][2], 1), L4b_at_bound=fl["row"]["at_bound"]))
        comp_rows.append(dict(config_id=cid, cluster=cluster, iepc_certification_number=iepc.get("CertificationNumber", ""),
                              iepc_digest_first8=iepc.get("DigestValue", "")[:8], iepc_rated_kW=fc["row"]["iepc_rated_kW"],
                              lowest_total_ratio=iepc.get("LowestTotalTransmissionRatio", ""), sim_tool_version_min=c["vecto_version_min"],
                              has_construction=("Construction" in ms), C_F0_N=round(fc["values"][2], 1), C_eta_d=round(fc["values"][0], 4),
                              C_eta_r=round(fc["values"][1], 4), L4b_a_W=round(fl["values"][0], 1), L4b_c_W_per_mps=round(fl["values"][2], 1)))
        for r in rr:
            ms_name = r["mission"]
            aux, notes = RH.aux_for(r["aux_pneu"], steer_of.get(vid, ""), r["group"], ms_name)
            su = setup.get((r["group"], ms_name), {})
            declared_used = r["cdxa_hi"] > r["cdxa_lo"]
            rec = dict(config_id=cid, cluster=cluster, mission=ms_name, cycle_file=RH.MISSION_CYCLE.get(ms_name, "") if hasattr(RH, "MISSION_CYCLE") else "",
                       payload_kg=round(r["payload"]), total_mass_kg=round(r["mass"], 1), certified_kwh_km=round(r["cert"], 4),
                       cycle_km=round(r["km"], 3), trailer_codes=r["cdxa_trailers"], delta_cdxa_trailer_m2=r["cdxa_delta"],
                       cdxa_declared_used_this_mission=declared_used, cdxa_lo_incl_delta_m2=round(r["cdxa_lo"], 4), cdxa_hi_incl_delta_m2=round(r["cdxa_hi"], 4),
                       cdxa0_start_m2=round(r["cdxa0"], 4), cdxa_fit_C_incl_delta_m2=round(fc["cdxa"] + r["cdxa_delta"], 4) if declared_used else round(r["cdxa0"], 4),
                       cdxa_fit_L4b_incl_delta_m2=round(fl["cdxa"] + r["cdxa_delta"], 4) if declared_used else round(r["cdxa0"], 4),
                       crr_eff_total=round(r["crr_eff"], 6), m_red_wheels_kg=round(r["m_red"], 1), r_dyn_m=round(r["r_dyn"], 4),
                       aux_ES_W=aux["ES"], aux_PS_W=aux["PS"], aux_HVAC_W=aux["HVAC"], aux_cond_W=aux["cond"],
                       aux_share_of_certified_pct=round(100 * r["E_aux_Ws"] / 3.6e6 / r["km"] / HN.CHARGING_ETA / r["cert"], 2),
                       aux_notes=";".join(notes), truck_axle_shares=su.get("truck_axle_shares", ""), trailer_axle_shares=su.get("trailer_axle_shares", ""),
                       n_gears=r["n_gears"], iepc_rated_kW=r["rated_kw"], axlegear_ratio_eea=c["Axlegear_Ratio"], harness_E_A_kwh_km=round(r["E_A"], 4),
                       harness_wheel_kwh_km_no_loss=round(float(np.sum(r["P_wheel"])) / 3.6e6 / r["km"], 4),
                       segment_table_ref="SegmentTable.csv line 17 (group 5 Tractor 4x2, Vocational 0)", tyre_ref="Wheels.csv lines 41/50 (315/70, 385/55), 42, 51")
            rec_rows.append(rec)
    L.write(os.path.join(HERE, "p1_daf_inputs_per_config.csv"), cfg_rows)
    L.write(os.path.join(HERE, "p1_daf_inputs_per_mission.csv"), rec_rows)
    L.write(os.path.join(HERE, "p1_daf_iepc_component.csv"), comp_rows)
    L.write(os.path.join(HERE, "p1_daf_vecto_refs.csv"), vecto_refs())

    # ---- cluster comparison on every input variable
    hi = [r for r in cfg_rows if r["cluster"] == "HIGH_F0"]
    lo = [r for r in cfg_rows if r["cluster"] == "LOW_F0"]

    def fam(v):
        return ".".join(str(v).split(".")[:3])
    cand = {
        "sim_tool_version (major.minor.patch)": lambda r: fam(r["sim_tool_version_min"]),
        "sim_tool_version_min (full)": lambda r: r["sim_tool_version_min"],
        "has_construction": lambda r: r["has_construction"],
        "iepc_certification_number": lambda r: r["iepc_certification_number"],
        "iepc_digest": lambda r: r["iepc_digest"][:8],
        "iepc_rated_kW": lambda r: r["iepc_rated_kW"],
        "lowest_total_ratio": lambda r: r["lowest_total_ratio"],
        "n_gears": lambda r: r["n_gears"], "axle_config": lambda r: r["axle_config"],
        "axlegear_ratio_eea": lambda r: r["axlegear_ratio_eea"], "cdxa_range": lambda r: r["cdxa_range"],
        "airdrag_method": lambda r: r["airdrag_method"], "model": lambda r: r["model"].split()[0],
        "aux_pneumatic": lambda r: r["aux_pneumatic"], "aux_hvac_system": lambda r: r["aux_hvac_system"], "aux_steering": lambda r: r["aux_steering"],
        "sleeper_cab": lambda r: r["sleeper_cab"], "battery_installed_kwh": lambda r: r["battery_installed_kwh"],
        "tpmlm_kg": lambda r: r["tpmlm_kg"], "tyre dims (axle1;axle2)": lambda r: ";".join(sorted(t.split()[1] + t.split()[2] for t in r["tyres"].split(" | "))),
        "n_vehicles_in_config": lambda r: r["n_vehicles_in_config"],
    }
    out = []
    for name, f in cand.items():
        vh, vl = Counter(str(f(r)) for r in hi), Counter(str(f(r)) for r in lo)
        sep = not (set(vh) & set(vl))
        out.append(dict(variable=name, values_in_HIGH_F0="; ".join("%s x%d" % kv for kv in sorted(vh.items())),
                        values_in_LOW_F0="; ".join("%s x%d" % kv for kv in sorted(vl.items())), separates_perfectly=sep))
    # per-mission numeric inputs: HIGH vs LOW medians
    for key in ("total_mass_kg", "crr_eff_total", "m_red_wheels_kg", "r_dyn_m", "aux_ES_W", "aux_PS_W", "aux_HVAC_W", "aux_cond_W",
                "cdxa0_start_m2", "delta_cdxa_trailer_m2", "aux_share_of_certified_pct", "harness_wheel_kwh_km_no_loss"):
        for ms in ("Regional Delivery", "Long Haul", "Urban Delivery"):
            a = [float(r[key]) for r in rec_rows if r["cluster"] == "HIGH_F0" and r["mission"] == ms]
            b = [float(r[key]) for r in rec_rows if r["cluster"] == "LOW_F0" and r["mission"] == ms]
            if not a or not b:
                continue
            ov = max(min(a), min(b)) <= min(max(a), max(b))
            out.append(dict(variable="%s [%s]" % (key, ms), values_in_HIGH_F0="min %.4g median %.4g max %.4g" % (min(a), np.median(a), max(a)),
                            values_in_LOW_F0="min %.4g median %.4g max %.4g" % (min(b), np.median(b), max(b)), separates_perfectly=(not ov)))
    # certified level and shape: Regional/Urban at the same payload (group 5: both 2600 kg)
    for cl in ("HIGH_F0", "LOW_F0"):
        rat = []
        for cid in daf:
            if any(r["cluster"] == cl and r["config_id"] == cid for r in cfg_rows):
                d = {(r["mission"], round(r["payload"])): r["cert"] for r in by[cid]}
                if ("Regional Delivery", 2600) in d and ("Urban Delivery", 2600) in d and ("Long Haul", 2600) in d:
                    rat.append((d[("Regional Delivery", 2600)] / d[("Urban Delivery", 2600)], d[("Long Haul", 2600)] / d[("Urban Delivery", 2600)]))
        a = np.array(rat)
        out.append(dict(variable="certified Regional/Urban and LongHaul/Urban at 2600 kg", values_in_HIGH_F0="", values_in_LOW_F0="",
                        separates_perfectly="", note="%s: Regional/Urban %.3f (%.3f-%.3f), LongHaul/Urban %.3f (%.3f-%.3f), n=%d" % (
                            cl, a[:, 0].mean(), a[:, 0].min(), a[:, 0].max(), a[:, 1].mean(), a[:, 1].min(), a[:, 1].max(), len(a))))
    L.write(os.path.join(HERE, "p1_daf_cluster_compare.csv"), out)
    for r in out:
        if r.get("separates_perfectly") is True or r["variable"].startswith("certified"):
            print("SEPARATES" if r["separates_perfectly"] is True else "info", r["variable"], r.get("note", ""))


if __name__ == "__main__":
    main()
