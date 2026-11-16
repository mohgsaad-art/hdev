"""Part 3: physics-free baselines on group 5, hold-out-model, and the same table for class-P50 physics.

B0   held-out model, mission m, payload p:  median over the OTHER models of (mean certified kWh/km of that model's configs at (m, p)).
     No physics, no parameter, no CdxA. Each model weighs one.
B1   same but the median of the k nearest OTHER models that have a certified value at (m, p). Distance = Euclidean on z-scores of
     (reference test mass, IEPC rated kW) over the models in the universe; reference test mass = TotalVehicleMass at
     Regional Delivery, 12,900 kg payload (all 254 configs have it), median over the model's configs. k = 5 headline, k = 3 shown.
     [ASSUMPTION: Claude's proposal; k and distance fixed before the run, not tuned.]
Physics rows (C, L4b, L1[S3b], L1b[S3b]) use PR #38's hold-out: class P50 of the other models' fitted values, applied to the held-out model with
     (own) its own fitted declared CdxA, as in PR #38, which uses the held-out truck's certified results to fit CdxA. A truck that is truly unseen has no such fit,
     so the table also gives (mid) the middle of the published CdxA range.
Run for all 38 models and without DAF (32 models).
Outputs: p3_summary.csv, p3_holdout_models.csv, p3_baseline_inputs.csv
"""
import os
from collections import defaultdict

import numpy as np

import lib_eval as E
import lib_g5 as L
import p2_eval_g5 as P2

HERE = L.HERE
REF = ("Regional Delivery", 12900)


def model_tables(by, ids, model_of):
    cert = defaultdict(lambda: defaultdict(list))     # model -> (mission, payload) -> [certified of its configs]
    mass, kw = defaultdict(list), defaultdict(list)
    for c in ids:
        for r in by[c]:
            cert[model_of[c]][(r["mission"], round(r["payload"]))].append(r["cert"])
            if (r["mission"], round(r["payload"])) == REF:
                mass[model_of[c]].append(r["mass"])
        kw[model_of[c]].append(by[c][0]["rated_kw"])
    mcert = {m: {k: float(np.mean(v)) for k, v in d.items()} for m, d in cert.items()}
    feat = {m: (float(np.median(mass[m])), float(np.median(kw[m]))) for m in mcert}
    return mcert, feat


def baseline(by, ids, model_of, make_of, k):
    """k = None -> B0 (all other models); else B1 with k nearest. Returns per-model rows."""
    mcert, feat = model_tables(by, ids, model_of)
    models = sorted(mcert)
    F = np.array([feat[m] for m in models])
    z = (F - F.mean(0)) / F.std(0)
    zi = dict(zip(models, z))
    rows = []
    for tgt in models:
        order = sorted((m for m in models if m != tgt), key=lambda m: float(np.linalg.norm(zi[m] - zi[tgt])))
        errs, ndon = [], []
        for c in [c for c in ids if model_of[c] == tgt]:
            for r in by[c]:
                key = (r["mission"], round(r["payload"]))
                pool = [m for m in order if key in mcert[m]]
                if k:
                    pool = pool[:k]
                if not pool:
                    continue
                pred = float(np.median([mcert[m][key] for m in pool]))
                errs.append(pred / r["cert"] - 1)
                ndon.append(len(pool))
        e = np.array(errs)
        rows.append(dict(target_model=tgt, target_make=make_of[[c for c in ids if model_of[c] == tgt][0]], n=len(e), n_low=int((e < 0).sum()),
                         mean_err=float(e.mean()), worst_abs=float(np.abs(e).max()), mean_err_pct=round(100 * float(e.mean()), 3),
                         worst_abs_err_pct=round(100 * float(np.abs(e).max()), 3), mean_donors=round(float(np.mean(ndon)), 1)))
    return rows, feat, order


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    ft = L.fits_c_l4b()
    model_of = {c: cfg[c]["Model"] for c in ids}
    make_of = {c: cfg[c]["Make_clean"] for c in ids}
    methods = {F.tag: F for F in P2.all_methods() if F.tag in ("C", "L4b", "L1[S3b_IEPC_3speed]", "L1b[S3b_IEPC_3speed]")}
    summ, hold, inputs = [], [], []
    for universe_name, uni in (("all 38 models", ids), ("without DAF (32 models)", [c for c in ids if make_of[c] != "DAF"])):
        for label, k in (("B0 median of all other models", None), ("B1 median of 5 nearest models (mass, kW)", 5), ("B1 median of 3 nearest models (mass, kW)", 3)):
            rows, feat, _ = baseline(by, uni, model_of, make_of, k)
            s = L.summarize_models(rows)
            summ.append(dict(universe=universe_name, method=label, cdxa_for_target="n/a", **{k_: v for k_, v in s.items()}))
            hold += [dict(universe=universe_name, method=label, **{k_: r[k_] for k_ in ("target_model", "target_make", "n", "mean_err_pct", "worst_abs_err_pct", "mean_donors")}) for r in rows]
            if k is None and universe_name.startswith("all"):
                inputs += [dict(model=m, reference_test_mass_kg=round(v[0], 1), iepc_rated_kW=v[1]) for m, v in sorted(feat.items())]
        for tag, F in methods.items():
            for mode in ("own", "mid"):
                rows = E.holdout_models(F, by, uni, mode)
                s = L.summarize_models(rows)
                summ.append(dict(universe=universe_name, method="class-P50 " + tag, cdxa_for_target={"own": "own fitted CdxA (PR #38)", "mid": "middle of published range"}[mode], **s))
                hold += [dict(universe=universe_name, method="class-P50 %s (CdxA %s)" % (tag, mode), **{k_: r[k_] for k_ in ("target_model", "target_make", "n", "mean_err_pct", "worst_abs_err_pct")}) for r in rows]
    L.write(os.path.join(HERE, "p3_summary.csv"), summ)
    L.write(os.path.join(HERE, "p3_holdout_models.csv"), hold)
    L.write(os.path.join(HERE, "p3_baseline_inputs.csv"), inputs)
    for s in summ:
        print("%-26s %-44s %-28s width %6.2f  mean %+6.2f  worst model %5.1f  worst result %5.1f  low %.2f" % (
            s["universe"], s["method"], s["cdxa_for_target"], s["width_p90_minus_p10_pp"], s["mean_of_model_mean_err_pct"],
            s["worst_model_mean_abs_err_pct"], s["worst_single_result_abs_err_pct"], s["share_results_too_low"]))


if __name__ == "__main__":
    main()
