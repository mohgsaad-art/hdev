"""Part 3.4: model-by-model comparison of physics and baselines (absolute mean error of each held-out model).
Output: p3_pairwise.csv. Physics rows use 'CdxA mid' (no use of the target's certified results), 'own' is PR #38's rule."""
import os
from collections import defaultdict

import numpy as np

import lib_g5 as L

HERE = L.HERE


def main():
    d = defaultdict(lambda: defaultdict(dict))
    for r in L.read(os.path.join(HERE, "p3_holdout_models.csv")):
        d[r["universe"]][r["method"]][r["target_model"]] = abs(float(r["mean_err_pct"]))
    out = []
    for u, ms in d.items():
        bases = [m for m in ms if m.startswith("B")]
        phys = [m for m in ms if m.startswith("class-P50") and ("(CdxA mid)" in m or "(CdxA own)" in m) and "L1b" not in m]
        for p in sorted(phys):
            for b in sorted(bases):
                models = sorted(ms[p])
                a = np.array([ms[p][m] for m in models])
                c = np.array([ms[b][m] for m in models])
                out.append(dict(universe=u, physics=p, baseline=b, n_models=len(models), physics_median_abs_model_err_pct=round(float(np.median(a)), 2),
                                baseline_median_abs_model_err_pct=round(float(np.median(c)), 2), physics_mean_abs_model_err_pct=round(float(a.mean()), 2),
                                baseline_mean_abs_model_err_pct=round(float(c.mean()), 2), models_where_physics_is_closer=int((a < c).sum()),
                                models_where_baseline_is_closer=int((a > c).sum())))
    L.write(os.path.join(HERE, "p3_pairwise.csv"), out)
    for r in out:
        if "mid" in r["physics"] or "own" in r["physics"]:
            print(r["universe"][:6], r["physics"][:44].ljust(44), r["baseline"][:30].ljust(30), r["physics_median_abs_model_err_pct"], r["baseline_median_abs_model_err_pct"],
                  r["physics_mean_abs_model_err_pct"], r["baseline_mean_abs_model_err_pct"], r["models_where_physics_is_closer"], "/", r["n_models"])


if __name__ == "__main__":
    main()
