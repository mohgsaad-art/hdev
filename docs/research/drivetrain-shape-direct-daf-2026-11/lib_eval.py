"""Evaluation functions shared by Part 1.4, Part 2 and Part 3. Same definitions as PR #38:

class band (g5_part2_class_band.py): model-weighted P50 parameters = median over models of each model's mean parameter
    vector; applied to every config with that config's OWN fitted declared CdxA; width = P90 - P10 of the config mean errors.
held-out model (g5_part4_holdout_models.py): for each model name, the other models' per-model mean parameter vectors, median,
    applied to every config of the held-out model with its own fitted CdxA; one row per model: mean error over all its results.
"""
from collections import defaultdict

import numpy as np

import lib_g5 as L

ML = L.ML


class Fitted:
    """One method's per-config full fits. params[cid] = tuple of drivetrain values (no CdxA); cdxa[cid] = fitted declared CdxA or None."""

    def __init__(self, tag, make_method, params, cdxa, model, make_name, n_params):
        self.tag, self.make_method, self.params, self.cdxa = tag, make_method, params, cdxa
        self.model, self.make_name, self.n_params = model, make_name, n_params

    def errors(self, cid, rr, drivetrain, cdxa_mode="own"):
        """cdxa_mode 'own': the target config's own fitted declared CdxA (PR #38). 'mid': the middle of its published range
        (what is known for an unseen model; no use of the target's certified results)."""
        m = self.make_method(rr[0])
        if cdxa_mode == "mid" and rr[0]["airdrag_measured"]:
            from cdxa_ranges import CDXA_RANGES
            lo, hi = CDXA_RANGES[rr[0]["cdxa_range"]]
            cd = 0.5 * (lo + hi)
        else:
            cd = self.cdxa[cid]
        th = tuple(drivetrain) + ((cd,) if rr[0]["airdrag_measured"] else ())
        return np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])


def from_pr38(tag, ft):
    d = ft[tag]
    return Fitted(tag, lambda rec, t=tag: L.P3.make(t, rec), {c: x["values"] for c, x in d.items()}, {c: x["cdxa"] for c, x in d.items()},
                  {c: x["model"] for c, x in d.items()}, {c: x["make"] for c, x in d.items()}, 3)


def model_vectors(F, donor_ids):
    mm = defaultdict(list)
    for c in donor_ids:
        mm[F.model[c]].append(F.params[c])
    return {m: np.mean(np.array(v), axis=0) for m, v in mm.items()}


def class_p50(F, donor_ids):
    mv = model_vectors(F, donor_ids)
    if not mv:
        return None
    return np.percentile(np.array(list(mv.values())), 50, axis=0)


def class_band(F, by, eval_ids, donor_ids):
    """PR #38 Part 2 model-weighted P50 application. Returns dict with the config-mean-error distribution."""
    vals = class_p50(F, donor_ids)
    e = []
    for c in eval_ids:
        e.append(100 * float(np.mean(F.errors(c, by[c], vals))))
    e = np.array(e)
    return dict(method=F.tag, n_configs=len(e), mean_of_config_mean_err_pct=round(float(e.mean()), 3), p10=round(L.pctl(e, 10), 3),
                p50=round(L.pctl(e, 50), 3), p90=round(L.pctl(e, 90), 3), width_p90_minus_p10_pp=round(L.pctl(e, 90) - L.pctl(e, 10), 3),
                worst_config_mean_abs_err_pct=round(float(np.abs(e).max()), 3), params_p50=";".join("%.6g" % v for v in vals)), e


def holdout_models(F, by, ids, cdxa_mode="own"):
    """PR #38 Part 4 class source. ids = configs of the universe (targets and donors)."""
    models = sorted(set(F.model[c] for c in ids))
    rows = []
    for tgt in models:
        tc = [c for c in ids if F.model[c] == tgt]
        donors = [c for c in ids if F.model[c] != tgt]
        vals = class_p50(F, donors)
        es = np.concatenate([F.errors(c, by[c], vals, cdxa_mode) for c in tc])
        rows.append(dict(method=F.tag, target_model=tgt, target_make=F.make_name[tc[0]], n_target_configs=len(tc), n_predictions=len(es),
                         mean_err=float(es.mean()), worst_abs=float(np.abs(es).max()), n=len(es), n_low=int((es < 0).sum()), mean_err_pct=round(100 * float(es.mean()), 3),
                         worst_abs_err_pct=round(100 * float(np.abs(es).max()), 3), share_too_low=round(float((es < 0).mean()), 3),
                         params=";".join("%.6g" % v for v in vals)))
    return rows


def insample(F, by, ids):
    """Own-fit errors per config (the numbers PR #38 g5_fits.csv reports)."""
    mae, worst = [], []
    for c in ids:
        e = F.errors(c, by[c], F.params[c])
        mae.append(100 * float(np.mean(np.abs(e))))
        worst.append(100 * float(np.abs(e).max()))
    return dict(mean_of_config_mae_pct=round(float(np.mean(mae)), 3), worst_config_abs_err_pct=round(float(max(worst)), 3))


def summary_row(label, hold_rows, band=None, ins=None, n_params=""):
    s = L.summarize_models(hold_rows)
    out = dict(method=label, n_fitted_drivetrain_values=n_params)
    if ins:
        out.update(insample_mean_abs_err_pct=ins["mean_of_config_mae_pct"], insample_worst_abs_err_pct=ins["worst_config_abs_err_pct"])
    if band:
        out.update(class_p50_width_config_pp=band["width_p90_minus_p10_pp"])
    out.update(holdout_mean_of_model_mean_err_pct=s["mean_of_model_mean_err_pct"], holdout_p10_pct=s["p10_pct"], holdout_p50_pct=s["p50_pct"],
               holdout_p90_pct=s["p90_pct"], holdout_width_pp=s["width_p90_minus_p10_pp"],
               worst_model_mean_abs_err_pct=s["worst_model_mean_abs_err_pct"], worst_single_result_abs_err_pct=s["worst_single_result_abs_err_pct"],
               share_results_too_low=s["share_results_too_low"], n_models=s["n_models"], n_results=s["n_results"])
    return out
