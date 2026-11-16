"""Part 2.3 and 2.5: group 5 in-sample, class-P50 cross-check and hold-out-model for C, L4b (PR #38) and L1, L1b (this PR).

Definitions are PR #38's (lib_eval.py): hold-out-model = the other models' median of per-model mean parameters, applied to every
config of the held-out model with its own fitted CdxA; summary over 38 models. Per make table for question 2.5 (post hoc, labelled).
Outputs: p2_g5_summary.csv, p2_g5_summary_without_daf.csv, p2_g5_holdout_models.csv, p2_g5_by_make.csv
"""
import os

import numpy as np

import lib_eval as E
import lib_g5 as L
import p2_methods as PM

HERE = L.HERE
SHAPES = ["arch", "S3a_IEPC_1speed", "S3b_IEPC_3speed", "S2_busIEPC_PSM", "S2_busIEPC_ASM", "S4_std_ASM"]


def from_csv(kind, shape_key):
    rows = L.read(os.path.join(HERE, "p2_fits_%s_%s.csv" % (kind, shape_key)))
    cols = ("s",) if kind == "L1" else ("s_drive", "s_regen")
    return E.Fitted(PM.label(kind, shape_key), lambda rec, k=kind, s=shape_key: PM.make(k, s, rec),
                    {r["config_id"]: tuple(float(r[c]) for c in cols) for r in rows},
                    {r["config_id"]: (float(r["cdxa_declared_m2"]) if r["cdxa_declared_m2"] else None) for r in rows},
                    {r["config_id"]: r["model"] for r in rows}, {r["config_id"]: r["make"] for r in rows}, len(cols))


def all_methods():
    ft = L.fits_c_l4b()
    out = [E.from_pr38("C", ft), E.from_pr38("L4b", ft)]
    for s in SHAPES:
        out.append(from_csv("L1", s))
        out.append(from_csv("L1b", s))
    return out


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    summ, summ_nd, hold_all, make_rows = [], [], [], []
    for F in all_methods():
        nodaf = [c for c in ids if F.make_name[c] != "DAF"]
        for universe, store in ((ids, summ), (nodaf, summ_nd)):
            band, _ = E.class_band(F, by, universe, universe)
            ins = E.insample(F, by, universe)
            hrows = E.holdout_models(F, by, universe)
            store.append(E.summary_row(F.tag, hrows, band, ins, F.n_params if F.tag not in ("C", "L4b") else 3))
            if universe is ids:
                hold_all += [{k: v for k, v in r.items() if k in ("method", "target_model", "target_make", "n_target_configs", "n_predictions", "mean_err_pct", "worst_abs_err_pct", "share_too_low", "params")} for r in hrows]
                for mk in sorted(set(r["target_make"] for r in hrows)):
                    x = [r for r in hrows if r["target_make"] == mk]
                    e = np.array([r["mean_err_pct"] for r in x])
                    cids = [c for c in ids if F.make_name[c] == mk]
                    ins_mk = E.insample(F, by, cids)
                    make_rows.append(dict(method=F.tag, make=mk, n_models=len(x), n_configs=len(cids), holdout_mean_of_model_mean_err_pct=round(float(e.mean()), 3),
                                          holdout_mean_abs_of_model_mean_err_pct=round(float(np.abs(e).mean()), 3), holdout_min_pct=round(float(e.min()), 3),
                                          holdout_max_pct=round(float(e.max()), 3), worst_single_result_abs_err_pct=max(r["worst_abs_err_pct"] for r in x),
                                          share_too_low=round(sum(r["n_low"] for r in x) / sum(r["n"] for r in x), 3),
                                          insample_mean_abs_err_pct=ins_mk["mean_of_config_mae_pct"]))
        print(summ[-1]["method"], summ[-1]["holdout_width_pp"], summ_nd[-1]["holdout_width_pp"])
    L.write(os.path.join(HERE, "p2_g5_summary.csv"), summ)
    L.write(os.path.join(HERE, "p2_g5_summary_without_daf.csv"), summ_nd)
    L.write(os.path.join(HERE, "p2_g5_holdout_models.csv"), hold_all)
    L.write(os.path.join(HERE, "p2_g5_by_make.csv"), make_rows)


if __name__ == "__main__":
    main()
