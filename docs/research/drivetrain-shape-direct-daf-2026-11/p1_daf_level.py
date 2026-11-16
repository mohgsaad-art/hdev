"""Part 1.2/1.5: the level of the certified energy against the harness physics, by IEPC certification method and make.

ratio = certified kWh/km / E_A, E_A = the v2 harness result with a FIXED drivetrain (0.95 x 0.95 x 0.98, regen 0.95); same cycle, mass, payload,
tyres, aux and CdxA (range middle) for every config. A ratio near 1 = the fixed chain describes the certified energy; 1.47 = 47 % more energy than modelled.
Outputs: p1_daf_level_by_config.csv, p1_level_by_make_and_iepc_method.csv, p1_level_by_mission_daf.csv
"""
import csv
import os
from collections import defaultdict

import numpy as np

import lib_g5 as L

HERE = L.HERE
RESEARCH = os.path.abspath(os.path.join(L.LIB, ".."))


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    ft = L.fits_c_l4b()["C"]
    ie = {}
    for r in csv.DictReader(open(os.path.join(RESEARCH, "hdv_2024_iepc.csv"), encoding="utf-8-sig")):
        ie.setdefault(r["Vehicle_id"], r)
    rows, lev, msn = [], defaultdict(list), defaultdict(list)
    for c in ids:
        rr = by[c]
        vid = rr[0]["vehicle_id"]
        i = ie.get(vid, {})
        method = i.get("CertificationMethod", "?")
        cn = i.get("CertificationNumber", "")
        kind = "R85 number" if "85R" in cn.upper() else ("2017/2400 number" if "2017/2400" in cn else ("none" if not cn else "other"))
        for r in rr:
            if round(r["payload"]) == 2600 and r["mission"] in ("Regional Delivery", "Urban Delivery", "Long Haul", "Construction"):
                lev[(cfg[c]["Make_clean"], method, kind)].append((r["cert"], r["E_A"], r["mass"], r["rated_kw"] or 0, ft[c]["values"][0], ft[c]["values"][2]))
                if cfg[c]["Make_clean"] == "DAF":
                    msn[(("SV/R85" if method == "StandardValues" else "measured/2017-2400"), r["mission"])].append((r["cert"], r["E_A"], r["mass"]))
        if cfg[c]["Make_clean"] == "DAF":
            d = {r["mission"]: r["cert"] / r["E_A"] for r in rr if round(r["payload"]) == 2600}
            rows.append(dict(config_id=c, model=cfg[c]["Model"], iepc_method_vehicle_level=method, iepc_certification_number=cn,
                             iepc_digest_first8=i.get("DigestValue", "")[:8], sim_tool_version_min=cfg[c]["vecto_version_min"],
                             C_F0_N=round(ft[c]["values"][2], 1), C_eta_d=round(ft[c]["values"][0], 4),
                             **{"cert_over_VA_" + k.replace(" ", "_"): round(v, 3) for k, v in sorted(d.items())},
                             mean_cert_over_VA=round(float(np.mean(list(d.values()))), 3)))
    L.write(os.path.join(HERE, "p1_daf_level_by_config.csv"), rows)
    out = []
    for k, v in sorted(lev.items()):
        v = np.array(v)
        out.append(dict(make=k[0], iepc_method=k[1], iepc_certificate_kind=k[2], n_results=len(v), mean_certified_kwh_km=round(float(v[:, 0].mean()), 3),
                        mean_E_A_kwh_km=round(float(v[:, 1].mean()), 3), mean_ratio_cert_over_VA=round(float((v[:, 0] / v[:, 1]).mean()), 3),
                        min_ratio=round(float((v[:, 0] / v[:, 1]).min()), 3), max_ratio=round(float((v[:, 0] / v[:, 1]).max()), 3),
                        mean_test_mass_kg=round(float(v[:, 2].mean())), mean_iepc_rated_kW=round(float(v[:, 3].mean())),
                        C_eta_d_mean=round(float(v[:, 4].mean()), 3), C_F0_N_mean=round(float(v[:, 5].mean()))))
    L.write(os.path.join(HERE, "p1_level_by_make_and_iepc_method.csv"), out)
    m = []
    for k, v in sorted(msn.items()):
        v = np.array(v)
        m.append(dict(daf_group=k[0], mission=k[1], n=len(v), mean_certified_kwh_km=round(float(v[:, 0].mean()), 3), mean_E_A_kwh_km=round(float(v[:, 1].mean()), 3),
                      mean_test_mass_kg=round(float(v[:, 2].mean())), ratio=round(float((v[:, 0] / v[:, 1]).mean()), 3)))
    for ms in sorted(set(x["mission"] for x in m)):
        a = next(x for x in m if x["mission"] == ms and x["daf_group"].startswith("SV"))
        b = next(x for x in m if x["mission"] == ms and x["daf_group"].startswith("measured"))
        m.append(dict(daf_group="difference SV minus measured", mission=ms, n="", mean_certified_kwh_km=round(a["mean_certified_kwh_km"] - b["mean_certified_kwh_km"], 3),
                      mean_E_A_kwh_km=round(a["mean_E_A_kwh_km"] - b["mean_E_A_kwh_km"], 3), mean_test_mass_kg=round(a["mean_test_mass_kg"] - b["mean_test_mass_kg"]),
                      ratio=round(a["mean_certified_kwh_km"] / b["mean_certified_kwh_km"], 3)))
    L.write(os.path.join(HERE, "p1_level_by_mission_daf.csv"), m)
    for r in out + m:
        print(r)
    for r in rows:
        print(r["config_id"], r["iepc_method_vehicle_level"], r["iepc_certification_number"][:14], r["iepc_digest_first8"], r["C_F0_N"], r["mean_cert_over_VA"])


if __name__ == "__main__":
    main()
