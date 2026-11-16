"""Part 1.3: does the Fuso eCanter (C0059, group 1) show the DAF pattern?

DAF pattern = two C fits, F0 ~1,600 N with eta_d 0.87-0.89 (standard-values IEPC, certification E1*85R00/11*4203*00) or F0 = 0 with
eta_d ~0.92 (measured IEPC). eCanter: 4 certified results (Regional, Urban x 2 payloads), IEPC certified with standard values
(EEA iepc_cert_method). Refit C with F0 free (PR #37 form), F0 = 0 and F0 = 1600 N (value copied from the DAF fits, not a source).
Also report the certified Regional/Urban ratio and the wheel-energy ratio (physics side, no drivetrain loss).
Outputs: p1_ecanter.csv, p1_ecanter_ratio.csv
"""
import os

import numpy as np

import lib_g5 as L
import p1_daf_refits as R

HN, ML = L.HN, L.ML
HERE = L.HERE
TEN = L.P3.TEN


def ten_records():
    recs, skipped = HN.load_or_build(TEN, "ten", processes=8)
    by = {}
    for r in recs:
        by.setdefault(r["config_id"], []).append(r)
    for v in by.values():
        v.sort(key=lambda r: (r["mission"], r["payload"]))
    return by, skipped


def main():
    L.setup()
    by, skipped = ten_records()
    rr = by["C0059"]
    cfg = HN._state()["cfgs"]["C0059"]
    rows = []
    for variant in ("V0", "V1", "V2"):
        m = R.make(variant, rr[0])
        th, rms = ML.fit_v2(m, rr)
        err = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
        d = R.name_val(m, th)
        row = dict(config_id="C0059", variant=variant, n_results=len(rr), n_fitted=len(th), at_bound=R.at_bound(m, th, rr[0]),
                   eta_d=round(d["eta_d"], 4), eta_r=round(d["eta_r"], 4), F0_N=round(d.get("F0_N", {"V1": 0.0, "V2": R.F_HIGH}.get(variant, 0)), 1),
                   mean_abs_err_pct=round(100 * float(np.mean(np.abs(err))), 2), worst_abs_err_pct=round(100 * float(np.max(np.abs(err))), 2))
        for i, r in enumerate(rr):
            row["err_%s_%d_kg_pct" % (r["mission"].replace(" ", "_"), round(r["payload"]))] = round(100 * float(err[i]), 2)
        rows.append(row)
    L.write(os.path.join(HERE, "p1_ecanter.csv"), rows)
    # ratio signature
    out = []
    for name, recs in (("eCanter C0059", rr),):
        d = {(r["mission"], round(r["payload"])): r for r in recs}
        for p in sorted(set(k[1] for k in d)):
            if ("Regional Delivery", p) in d and ("Urban Delivery", p) in d:
                a, b = d[("Regional Delivery", p)], d[("Urban Delivery", p)]
                wa = float(np.sum(a["P_wheel"])) / 3.6e6 / a["km"]; wb = float(np.sum(b["P_wheel"])) / 3.6e6 / b["km"]
                out.append(dict(truck=name, payload_kg=p, certified_regional_over_urban=round(a["cert"] / b["cert"], 3),
                                wheel_energy_regional_over_urban_no_loss=round(wa / wb, 3),
                                harness_V_A_regional_over_urban=round(a["E_A"] / b["E_A"], 3)))
    # DAF groups for comparison, group 5 (2600 kg both missions)
    ids, cfgs = L.g5_config_ids()
    g5 = L.records()
    ft = L.fits_c_l4b()["C"]
    for label, sel in (("DAF HIGH_F0 (F0>=800)", lambda c: cfgs[c]["Make_clean"] == "DAF" and ft[c]["values"][2] >= R.THRESH),
                       ("DAF LOW_F0", lambda c: cfgs[c]["Make_clean"] == "DAF" and ft[c]["values"][2] < R.THRESH),
                       ("all other group 5", lambda c: cfgs[c]["Make_clean"] != "DAF")):
        c1, w1, v1 = [], [], []
        for c in ids:
            if not sel(c):
                continue
            d = {(r["mission"], round(r["payload"])): r for r in g5[c]}
            if ("Regional Delivery", 2600) in d and ("Urban Delivery", 2600) in d:
                a, b = d[("Regional Delivery", 2600)], d[("Urban Delivery", 2600)]
                c1.append(a["cert"] / b["cert"])
                w1.append((float(np.sum(a["P_wheel"])) / a["km"]) / (float(np.sum(b["P_wheel"])) / b["km"]))
                v1.append(a["E_A"] / b["E_A"])
        out.append(dict(truck=label, payload_kg=2600, certified_regional_over_urban=round(float(np.mean(c1)), 3),
                        wheel_energy_regional_over_urban_no_loss=round(float(np.mean(w1)), 3),
                        harness_V_A_regional_over_urban=round(float(np.mean(v1)), 3), n_configs=len(c1)))
    L.write(os.path.join(HERE, "p1_ecanter_ratio.csv"), out)
    for r in rows + out:
        print(r)


if __name__ == "__main__":
    main()
