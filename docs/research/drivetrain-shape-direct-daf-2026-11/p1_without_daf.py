"""Part 1.4: PR #38 class band and held-out-model band without DAF (C and L4b). Not a proposal to drop DAF.

A  all 254 configs, 38 models   (must reproduce PR #38: class band 14.71 / 14.73 pp, held-out 15.84 / 15.79 pp)
B  DAF removed from donors AND targets  (231 configs, 32 models)
C  DAF removed from donors only; DAF configs still evaluated (class band over 254 configs; held-out over the 6 DAF models
   against donors without DAF, plus the 32 other models as in B)
Outputs: p1_without_daf.csv, p1_without_daf_holdout.csv
"""
import os

import lib_eval as E
import lib_g5 as L

HERE = L.HERE


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    ft = L.fits_c_l4b()
    out, hrows = [], []
    for tag in ("C", "L4b"):
        F = E.from_pr38(tag, ft)
        nodaf = [c for c in ids if F.make_name[c] != "DAF"]
        daf = [c for c in ids if F.make_name[c] == "DAF"]
        for case, eval_ids, donor_ids in (("A all configs", ids, ids), ("B DAF removed (donors and targets)", nodaf, nodaf),
                                          ("C DAF removed from donors, DAF still evaluated", ids, nodaf)):
            band, _ = E.class_band(F, by, eval_ids, donor_ids)
            if case.startswith("C"):
                # held-out models of the whole universe, donors never DAF
                models = sorted(set(F.model[c] for c in ids))
                rows = []
                for tgt in models:
                    tc = [c for c in ids if F.model[c] == tgt]
                    donors = [c for c in nodaf if F.model[c] != tgt]
                    import numpy as np
                    vals = E.class_p50(F, donors)
                    es = np.concatenate([F.errors(c, by[c], vals) for c in tc])
                    rows.append(dict(method=tag, target_model=tgt, target_make=F.make_name[tc[0]], n=len(es), n_low=int((es < 0).sum()),
                                     mean_err=float(es.mean()), worst_abs=float(np.abs(es).max()), mean_err_pct=round(100 * float(es.mean()), 3),
                                     worst_abs_err_pct=round(100 * float(np.abs(es).max()), 3)))
            else:
                rows = E.holdout_models(F, by, eval_ids)
            s = L.summarize_models(rows)
            out.append(dict(method=tag, case=case, n_configs=band["n_configs"], n_models=s["n_models"],
                            class_band_width_pp=band["width_p90_minus_p10_pp"], class_band_p10=band["p10"], class_band_p50=band["p50"], class_band_p90=band["p90"],
                            class_band_worst_config_mean_pct=band["worst_config_mean_abs_err_pct"],
                            holdout_mean_pct=s["mean_of_model_mean_err_pct"], holdout_p10=s["p10_pct"], holdout_p50=s["p50_pct"], holdout_p90=s["p90_pct"],
                            holdout_width_pp=s["width_p90_minus_p10_pp"], worst_model_mean_abs_pct=s["worst_model_mean_abs_err_pct"],
                            worst_single_result_abs_pct=s["worst_single_result_abs_err_pct"], share_too_low=s["share_results_too_low"]))
            for r in rows:
                hrows.append(dict(case=case, **{k: r[k] for k in ("method", "target_model", "target_make", "n", "mean_err_pct", "worst_abs_err_pct")}))
            print(tag, case, out[-1]["class_band_width_pp"], out[-1]["holdout_width_pp"], out[-1]["worst_single_result_abs_pct"])
    L.write(os.path.join(HERE, "p1_without_daf.csv"), out)
    L.write(os.path.join(HERE, "p1_without_daf_holdout.csv"), hrows)


if __name__ == "__main__":
    main()
