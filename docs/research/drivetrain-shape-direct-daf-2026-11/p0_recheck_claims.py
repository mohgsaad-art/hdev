"""Re-check of the statements Claude made on 16 Nov about PR #38 (do not trust blindly). Output: p0_recheck_claims.csv"""
import csv
import os
from collections import Counter, defaultdict

import numpy as np

import lib_eval as E
import lib_g5 as L

HERE = L.HERE
DT = {"C": {"eta", "regen", "F0", "eta_d", "eta_r", "F0_N"}, "L4b": {"a_W", "b_perW", "c_W_per_mps"}}


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    fits = [r for r in L.read(os.path.join(L.LIB, "g5_fits.csv"))]
    rows = []

    def add(claim, found, ok):
        rows.append(dict(item=claim, found_in_this_run=found, stated_on_16_nov=ok))
        print("%-5s %s | %s" % (ok, claim, found))
    for tag in ("C", "L4b"):
        f = [r for r in fits if r["method"] == tag]
        hits = [r for r in f if set(r["at_bound"].split(";")) - {"", "cdxa_declared"}]
        add("%s: fits with a drivetrain value at a bound" % tag, "%d/%d" % (len(hits), len(f)), "C 90/254 and L4b 166/254 claimed")
    c = [r for r in fits if r["method"] == "C"]
    l = [r for r in fits if r["method"] == "L4b"]
    add("C: F0 = 0 on 87 fits", str(sum(float(r["F0_N"]) <= 1e-6 * 3000 for r in c)), "")
    add("L4b: c = 0 on 160 fits", str(sum(float(r["c_W_per_mps"]) <= 1e-6 for r in l)), "")
    # CdxA position inside range
    from cdxa_ranges import CDXA_RANGES
    for tag, f in (("C", c), ("L4b", l)):
        meas = [r for r in f if r["cdxa_declared_m2"]]
        up = sum(1 for r in meas if abs(float(r["cdxa_declared_m2"]) - (CDXA_RANGES[r["cdxa_range"]][1] - 1e-6)) < 1e-3 * (CDXA_RANGES[r["cdxa_range"]][1] - CDXA_RANGES[r["cdxa_range"]][0]) + 1e-9)
        lo = sum(1 for r in meas if abs(float(r["cdxa_declared_m2"]) - CDXA_RANGES[r["cdxa_range"]][0]) < 1e-3 * (CDXA_RANGES[r["cdxa_range"]][1] - CDXA_RANGES[r["cdxa_range"]][0]) + 1e-9)
        add("%s: CdxA at upper / lower range edge (measured configs %d)" % (tag, len(meas)), "upper %d, lower %d" % (up, lo), "C upper 124; L4b lower 121 of 146 claimed")
    # architecture and gears
    g = Counter((r["make"], r["gears"]) for r in c)
    add("gear count nearly equals make: 12-gear = Volvo 84 + Renault 30; 3-gear = DAF only", "; ".join("%s g%s x%d" % (k[0], k[1], v) for k, v in sorted(g.items()) if k[1] in ("12", "3")), "")
    add("all group 5 configs are E-IEPC in the harness", str(Counter(r["architecture"] for r in c)), "")
    # raw EEA PEV architecture for group 5 vehicles
    arch = Counter()
    with open(os.path.join(L.HN.JOIN, "vehicles_xev.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["VehicleGroup"] == "5" and r["is_zev"] in ("True", "true"):
                arch[r["PEVArchitecture"] or "(blank)"] += 1
    add("EEA PEVArchitecture of group 5 ZEV vehicles in the join file (claimed 201 BEV configs E-IEPC, 26 blank)", str(dict(arch)), "vehicle level, not config level")
    # worst held-out models
    ft = L.fits_c_l4b()
    for tag in ("C", "L4b"):
        F = E.from_pr38(tag, ft)
        rr = E.holdout_models(F, by, ids)
        by_mean = sorted(rr, key=lambda r: r["mean_err"])
        by_worst = sorted(rr, key=lambda r: -r["worst_abs"])
        add("%s: four worst held-out models by mean error are all DAF" % tag, "; ".join("%s %s %.1f%%" % (r["target_make"], r["target_model"].strip(), r["mean_err_pct"]) for r in by_mean[:5]),
            "claimed G0200A -27, G0100A -12, XD 350 -12, XF 350 -9")
        add("%s: five largest single-result errors by model" % tag, "; ".join("%s %s %.1f%%" % (r["target_make"], r["target_model"].strip(), r["worst_abs_err_pct"]) for r in by_worst[:5]), "")
        s = L.summarize_models(rr)
        add("%s: held-out class P50 width / worst model" % tag, "%.2f pp / worst single %.2f%%" % (s["width_p90_minus_p10_pp"], s["worst_single_result_abs_err_pct"]), "claimed about 16 pp, 36-38 %")
        # drop fits with a drivetrain bound hit (donors and targets)
        okc = [cid for cid in ids if not (set(ft[tag][cid]["row"]["at_bound"].split(";")) - {"", "cdxa_declared"})]
        rr2 = E.holdout_models(F, by, okc)
        s2 = L.summarize_models(rr2)
        add("%s: held-out class P50 width without the fits with a drivetrain bound hit (%d configs, %d models)" % (tag, len(okc), s2["n_models"]),
            "%.2f pp" % s2["width_p90_minus_p10_pp"], "claimed 15.6 (C) / 15.5 (L4b)")
        # drop bound-hit fits from the donors only
        res = []
        for tgt in sorted(set(F.model[c_] for c_ in ids)):
            tc = [c_ for c_ in ids if F.model[c_] == tgt]
            donors = [c_ for c_ in okc if F.model[c_] != tgt]
            vals = E.class_p50(F, donors)
            es = np.concatenate([F.errors(c_, by[c_], vals) for c_ in tc])
            res.append(dict(mean_err=float(es.mean()), worst_abs=float(np.abs(es).max()), n=len(es), n_low=int((es < 0).sum())))
        s3 = L.summarize_models(res)
        add("%s: same, bound-hit fits removed from the donors only (all 38 models are targets)" % tag, "%.2f pp" % s3["width_p90_minus_p10_pp"], "")
    L.write(os.path.join(HERE, "p0_recheck_claims.csv"), rows)


if __name__ == "__main__":
    main()
