"""Final tables: bootstrap intervals for the hold-out widths, paired differences, per-make shape table (post hoc), DAF diagnostic.

Bootstrap: resample the held-out MODELS (each model = one observation, as in the width definition) with replacement, 5,000 draws,
fixed seed 20261116; width = P90 - P10 of the model mean errors. Paired differences use the same resampled model indices.
Outputs: final_bootstrap.csv, final_by_make_best_shape.csv, final_daf_shape_diagnostic.csv, final_tables.md
"""
import csv
import os
from collections import defaultdict

import numpy as np

import lib_g5 as L

HERE = L.HERE
SEED, NB = 20261116, 5000


def models_table(path, key):
    d = defaultdict(dict)
    for r in L.read(path):
        d[(r.get("universe", ""), r["method"])][r["target_model"]] = (float(r["mean_err_pct"]), r["target_make"] if "target_make" in r else "")
    return d


def widths(e, idx):
    x = e[idx]
    return np.percentile(x, 90, axis=1) - np.percentile(x, 10, axis=1)


def main():
    rng = np.random.default_rng(SEED)
    p2 = defaultdict(dict)                                   # all 38 models, PR #38 CdxA rule, every method of Part 2
    for r in L.read(os.path.join(HERE, "p2_g5_holdout_models.csv")):
        p2[r["method"]][r["target_model"]] = float(r["mean_err_pct"])
    p3 = defaultdict(lambda: defaultdict(dict))              # universe -> method -> model -> mean err (baselines and physics with own / mid CdxA)
    make_of = {}
    for r in L.read(os.path.join(HERE, "p3_holdout_models.csv")):
        p3[r["universe"]][r["method"]][r["target_model"]] = float(r["mean_err_pct"])
        make_of[r["target_model"]] = r["target_make"]
    models = sorted(p2["C"])
    nodaf = [m for m in models if make_of[m] != "DAF"]
    series = {"all 38 models": {}, "without DAF (32 models)": {}}
    for m, d in p2.items():
        series["all 38 models"]["%s [CdxA own]" % m] = d
    for u, ms in p3.items():
        for m, d in ms.items():
            if m.startswith("B") :
                series[u][m] = d
            elif m.endswith("(CdxA mid)"):
                series[u][m] = d
    for u, ms in p3.items():
        if u.startswith("without"):
            for m, d in ms.items():
                if m.endswith("(CdxA own)"):
                    series[u][m.replace("(CdxA own)", "[CdxA own]")] = d
    rows = []
    for universe, mods in (("all 38 models", models), ("without DAF (32 models)", nodaf)):
        idx = rng.integers(0, len(mods), size=(NB, len(mods)))
        W = {}
        for name, d in series[universe].items():
            e = np.array([d[m] for m in mods])
            W[name] = (e, widths(e, idx))
        refs = [n for n in W if n.startswith("C [") or n.startswith("class-P50 C [")]
        for name, (e, w) in sorted(W.items()):
            rows.append(dict(universe=universe, method=name, n_models=len(mods), width_pp=round(float(np.percentile(e, 90) - np.percentile(e, 10)), 2),
                             width_ci95_lo=round(float(np.percentile(w, 2.5)), 2), width_ci95_hi=round(float(np.percentile(w, 97.5)), 2)))
        for ref_name in refs:
            for name, (e, w) in sorted(W.items()):
                if name == ref_name:
                    continue
                dwid = w - W[ref_name][1]
                d0 = (np.percentile(e, 90) - np.percentile(e, 10)) - (np.percentile(W[ref_name][0], 90) - np.percentile(W[ref_name][0], 10))
                rows.append(dict(universe=universe, method="DIFF %s minus %s" % (name, ref_name), n_models=len(mods), width_pp=round(float(d0), 2),
                                 width_ci95_lo=round(float(np.percentile(dwid, 2.5)), 2), width_ci95_hi=round(float(np.percentile(dwid, 97.5)), 2)))
    L.write(os.path.join(HERE, "final_bootstrap.csv"), rows)

    # --- per-make best shape (post hoc), four requested fixed shapes
    bm = L.read(os.path.join(HERE, "p2_g5_by_make.csv"))
    shapes = ["S3a_IEPC_1speed", "S3b_IEPC_3speed", "S2_busIEPC_PSM", "S2_busIEPC_ASM"]
    out = []
    for mk in sorted(set(r["make"] for r in bm)):
        for kind in ("L1", "L1b"):
            cand = {s: next(r for r in bm if r["make"] == mk and r["method"] == "%s[%s]" % (kind, s)) for s in shapes}
            bi = min(shapes, key=lambda s: float(cand[s]["insample_mean_abs_err_pct"]))
            bh = min(shapes, key=lambda s: float(cand[s]["holdout_mean_abs_of_model_mean_err_pct"]))
            out.append(dict(make=mk, method=kind, n_models=cand[shapes[0]]["n_models"], n_configs=cand[shapes[0]]["n_configs"],
                            **{"insample_MAE_" + s: cand[s]["insample_mean_abs_err_pct"] for s in shapes}, best_by_insample=bi,
                            **{"holdout_absmean_" + s: cand[s]["holdout_mean_abs_of_model_mean_err_pct"] for s in shapes}, best_by_holdout=bh,
                            spread_insample_pp=round(max(float(cand[s]["insample_mean_abs_err_pct"]) for s in shapes) - min(float(cand[s]["insample_mean_abs_err_pct"]) for s in shapes), 3)))
    L.write(os.path.join(HERE, "final_by_make_best_shape.csv"), out)

    # --- DAF: standard-values IEPC (EEA iepc_cert_method) vs measured, in-sample MAE per method (diagnostic, shape S4 = standard values)
    import p1_daf_refits  # noqa: F401  (for THRESH)
    cfgs = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(L.HN.V2_DIR, "truck_configs.csv")))}
    ft = L.fits_c_l4b()
    ie = {}
    for r in csv.DictReader(open(os.path.join(HERE, "..", "hdv_2024_iepc.csv"), encoding="utf-8-sig")):
        ie.setdefault(r["Vehicle_id"], r)
    by = L.records()
    diag = []
    daf = [c for c in cfgs if cfgs[c]["VehicleGroup"] == "5" and cfgs[c]["Make_clean"] == "DAF"]
    grp = {c: ("R85 standard-values IEPC" if "85R" in ie[by[c][0]["vehicle_id"]]["CertificationNumber"].upper() else "VECTO-certified IEPC (2017/2400)") for c in daf}
    meth = {"C": {c: float(ft["C"][c]["row"]["in_sample_mean_abs_err_pct"]) for c in daf}, "L4b": {c: float(ft["L4b"][c]["row"]["in_sample_mean_abs_err_pct"]) for c in daf}}
    for kind in ("L1", "L1b"):
        for s in ("S3b_IEPC_3speed", "S4_std_ASM"):
            rr = L.read(os.path.join(HERE, "p2_fits_%s_%s.csv" % (kind, s)))
            meth["%s[%s]" % (kind, s)] = {r["config_id"]: float(r["in_sample_mean_abs_err_pct"]) for r in rr if r["config_id"] in daf}
    for g in sorted(set(grp.values())):
        cs = [c for c in daf if grp[c] == g]
        for m, d in meth.items():
            diag.append(dict(group=g, n_configs=len(cs), method=m, in_sample_mean_abs_err_pct=round(float(np.mean([d[c] for c in cs])), 3)))
    L.write(os.path.join(HERE, "final_daf_shape_diagnostic.csv"), diag)
    for r in rows[:60]:
        print(r)


if __name__ == "__main__":
    main()
