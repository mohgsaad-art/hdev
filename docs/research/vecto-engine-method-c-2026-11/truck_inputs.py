"""Inputs of the two trucks (C0091 IVECO S-eWay, C0059 Fuso eCanter) for the VECTO job files.

Everything comes from the same places as the PR #37 harness (docs/research/drivetrain-curve-library-2026-11/harness.py, which uses the v2 EEA
harness at commit 73990f0 unchanged), so both engines get the same inputs:
  vehicle, axles, tyres, RRC     EEA axle_xev.csv (TyreDimension, SpecificRRC, Twintyres) of the median-mass vehicle of the config
  CurbWeight                     EEA vehicles_xev.csv CorrectedActualMass of that vehicle
  rated power, total ratio       EEA vehicles_xev.csv iepc_desc  "<kW>kW:g<gears>:r<lowest total ratio>:wheel=false"
  wheel inertia, r_dyn           VECTO Wheels.csv (file read by the harness, run_hdev.load_wheels)
  FzISO                          NO SOURCE in EEA; harness stand-in 31,300 N (run_hdev.FZISO_STANDIN)  [ASSUMPTION]
  CdxA start                     middle of the Reg. (EU) 2018/956 Annex I Part C range (harness AIRDRAG_MODE = range_mid)  [ASSUMPTION]
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.abspath(os.path.join(HERE, "..", "drivetrain-curve-library-2026-11"))
sys.path.insert(0, LIB)

import harness as HN       # noqa: E402
import part3_loo as P3     # noqa: E402

ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
TRUCKS = ("C0091", "C0059")
RH = HN.RH


def vehicle_inputs(cid):
    st = HN._state()
    cfg = st["cfgs"][cid]
    vid, rows = HN.config_runs(cid)
    ve = st["veh_extra"][vid]
    spec = RH.build_spec(cfg, vid, st["axle_rows"], st["veh_extra"])
    axles = sorted(st["axle_rows"][vid], key=lambda a: int(float(a["AxleNumber"])))
    tp = float(ve["TechnicalPermissibleMaximumLadenMass"])
    out = dict(config_id=cid, vehicle_id=vid, group=cfg["VehicleGroup"], category=ve["VehicleCategory"], axle_config=cfg["AxleConfiguration"],
               make=cfg["Make_clean"], model=cfg["Model"], tpmlm_t=tp / 1000.0 if tp > 1000 else tp,
               curb_mass_kg=float(ve["CorrectedActualMass"]), rated_kw=spec.rated_kw_total, total_ratio=spec.total_ratio, n_gears=spec.n_gears,
               iepc_cert_method=cfg["iepc_cert_method"], airdrag_method=cfg["AirDrag_CertificationMethod"], cdxa_range=cfg["AirDrag_CdxA_range"].strip(),
               pneu=ve["Aux_Pneumatic_Technology"], steering=st["steer_of"].get(vid, ""), bat_kwh=float(cfg["bat_installed_kwh"]), bat_v=float(cfg["bat_nominal_v"]),
               axles=[dict(number=int(float(a["AxleNumber"])), dim=a["TyreDimension"].strip(), rrc=float(a["SpecificRRC"]),
                           twin=str(a["Twintyres"]).lower() in ("true", "1"), inertia_per_tyre=RH.wheel_rdyn_inertia(a["TyreDimension"])[1],
                           r_dyn=RH.wheel_rdyn_inertia(a["TyreDimension"])[0]) for a in axles],
               fziso_N=RH.FZISO_STANDIN, results=rows)
    return out


def table_rows():
    """Part 1.1 table: every input, value, source."""
    rows = []
    for cid in TRUCKS:
        v = vehicle_inputs(cid)

        def add(inp, val, src, tag):
            rows.append(dict(truck=cid, input=inp, value=val, source=src, tag=tag))
        add("vehicle", "%s %s, group %s, %s %s" % (v["make"], v["model"], v["group"], v["category"], v["axle_config"]),
            "EEA vehicles_xev.csv Make, Model, VehicleGroup, VehicleCategory, AxleConfiguration", "[DATA]")
        add("median-mass vehicle id", v["vehicle_id"][:18] + "...", "harness.config_runs (PR #37 rule: one vehicle per exact config)", "[ASSUMPTION]")
        add("CurbWeight [kg]", v["curb_mass_kg"], "EEA vehicles_xev.csv CorrectedActualMass of that vehicle", "[DATA]")
        add("MassMax / TPMLM [t]", v["tpmlm_t"], "EEA vehicles_xev.csv TechnicalPermissibleMaximumLadenMass", "[DATA]")
        add("IEPC rated power [kW]", v["rated_kw"], "EEA vehicles_xev.csv iepc_desc (RatedPower)", "[DATA]")
        add("IEPC gears / lowest total ratio", "%s / %s" % (v["n_gears"], v["total_ratio"]),
            "EEA iepc_desc; differential included (hdv_2024_iepc.csv DifferentialIncluded = true)", "[DATA]")
        add("IEPC certification method (EEA)", v["iepc_cert_method"], "EEA configs: iepc_cert_method", "[DATA]")
        for a in v["axles"]:
            add("axle %d tyre / RRC / twin" % a["number"], "%s / %.4f / %s" % (a["dim"], a["rrc"], a["twin"]),
                "EEA axle_xev.csv TyreDimension, SpecificRRC, Twintyres", "[DATA]")
            add("axle %d wheel inertia per tyre [kgm2] / r_dyn [m]" % a["number"], "%.1f / %.4f" % (a["inertia_per_tyre"], a["r_dyn"]),
                "VECTO Resources/Declaration/Wheels.csv (same file the harness reads)", "[VECTO]")
        add("FzISO [N]", v["fziso_N"], "NO SOURCE (EEA has no FzISO); harness stand-in", "[ASSUMPTION]")
        add("air drag", "%s, range %s" % (v["airdrag_method"], v["cdxa_range"]),
            "EEA AirDrag_CertificationMethod, AirDrag_CdxA_range; Reg. 2018/956 Annex I Part C via cdxa_ranges.py", "[DATA]/[REG]")
        add("auxiliaries", "ES Standard technology; PS '%s'; HVAC Default; steering: %s" % (v["pneu"], v["steering"] or "(none in EEA)"),
            "EEA Aux_Pneumatic_Technology; VECTO VAUX tables (same as harness aux_per_label.csv)", "[DATA]/[VECTO]")
        add("battery", "installed %.0f kWh, nominal %.0f V" % (v["bat_kwh"], v["bat_v"]),
            "EEA bat_installed_kwh, bat_nominal_v; the terminal energy does not depend on it", "[DATA]/[ASSUMPTION]")
    return rows


if __name__ == "__main__":
    rows = table_rows()
    with open(os.path.join(HERE, "p1_inputs_table.csv"), "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)
