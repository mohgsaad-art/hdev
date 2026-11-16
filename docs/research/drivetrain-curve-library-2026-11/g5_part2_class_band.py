"""Part 2: group 5 class P10/P50/P90 parameter bands, model-weighted and config-weighted.

For each method, P10/P50/P90 is taken component-wise across full-fit parameters. Model-weighted means each
model's configs are averaged first, so each distinct model name carries one weight. At application, every config
uses its OWN fitted declared CdxA (where measured), exactly as the requested cross-check; only drivetrain
parameters are swapped. This deliberately tests transfer of drivetrain values, not published-air-drag uncertainty.

Usage: python g5_part2_class_band.py
Outputs: g5_class_parameters.csv, g5_class_band.csv, g5_class_band_summary.csv, g5_swap.csv, g5_class_band_hist.png
"""
import csv
import glob
import os
from collections import defaultdict

import numpy as np

import harness as HN
import part3_loo as P3

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
PARAMS = {"C": ("eta_d", "eta_r", "F0_N"), "L4b": ("a_W", "b_perW", "c_W_per_mps")}


def write(path, rows):
    with open(path, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        fields = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print("wrote", path)


def read(path):
    return list(csv.DictReader(ln for ln in open(path) if not ln.startswith("#")))


def records():
    by = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(HN.CACHE, "records_g5_??_range_mid.npz"))):
        rr, sk = HN._load_npz(p)
        for r in rr: by[r["config_id"]].append(r)
    for v in by.values(): v.sort(key=lambda r: (r["mission"], r["payload"]))
    return by


def fitted():
    out = defaultdict(dict)
    for r in read(os.path.join(HERE, "g5_fits.csv")):
        vals = tuple(float(r[p]) for p in PARAMS[r["method"]])
        cdxa = float(r["cdxa_declared_m2"]) if r["cdxa_declared_m2"] else None
        out[r["method"]][r["config_id"]] = dict(values=vals, cdxa=cdxa, model=r["model"], make=r["make"])
    return out


def theta_for(rec, method_name, drivetrain, cdxa):
    """P3.make makes +CdxA only if the TARGET config is measured. It must get the target's own CdxA."""
    m = P3.make(method_name, rec)
    return m, tuple(drivetrain) + ((cdxa,) if rec["airdrag_measured"] else ())


def main():
    P3.set_bounds(); HN.AIRDRAG_MODE = "range_mid"
    by, ft = records(), fitted()
    params_rows, band, summary, swaps = [], [], [], []
    all_sets = {}
    for method in ("C", "L4b"):
        pnames = PARAMS[method]
        raw = ft[method]
        for weighting in ("config_unweighted", "model_weighted"):
            if weighting == "config_unweighted":
                values = np.array([x["values"] for x in raw.values()])
                n_models = len(set(x["model"] for x in raw.values()))
            else:
                mm = defaultdict(list)
                for x in raw.values(): mm[x["model"]].append(x["values"])
                values = np.array([np.mean(v, axis=0) for v in mm.values()])
                n_models = len(mm)
            qs = {q: np.percentile(values, q, axis=0) for q in (10, 50, 90)}
            for q, v in qs.items():
                params_rows.append(dict(method=method, weighting=weighting, percentile="P%d" % q, n_configs=len(raw), n_models=n_models,
                                        **{p: round(x, 9) for p, x in zip(pnames, v)}))
            all_sets[(method, weighting)] = qs
            # apply each parameter set to all configs, target own fitted CdxA
            for q, vals in qs.items():
                config_err = []
                for cid, rr in by.items():
                    own = raw[cid]
                    m, th = theta_for(rr[0], method, vals, own["cdxa"])
                    e = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
                    config_err.append(float(np.mean(e)))
                    band.append(dict(config_id=cid, make=own["make"], model=own["model"], method=method, weighting=weighting,
                                     percentile="P%d" % q, n_results=len(rr), own_cdxa_m2=(round(own["cdxa"], 5) if own["cdxa"] else ""),
                                     mean_err_pct=round(100 * float(np.mean(e)), 3), mean_abs_err_pct=round(100 * float(np.mean(abs(e))), 3),
                                     worst_abs_err_pct=round(100 * float(max(abs(e))), 3)))
                config_err = np.array(config_err) * 100
                summary.append(dict(method=method, weighting=weighting, percentile="P%d" % q, n_configs=len(config_err),
                                    mean_of_config_mean_err_pct=round(float(np.mean(config_err)), 3),
                                    p10_config_mean_err_pct=round(float(np.percentile(config_err, 10)), 3),
                                    p50_config_mean_err_pct=round(float(np.percentile(config_err, 50)), 3),
                                    p90_config_mean_err_pct=round(float(np.percentile(config_err, 90)), 3),
                                    width_p90_minus_p10_pp=round(float(np.percentile(config_err, 90)-np.percentile(config_err,10)), 3),
                                    worst_config_mean_err_pct=round(float(max(abs(config_err))), 3)))
        # swaps: each target gets every other config's drivetrain params, its own CdxA
        for cid, rr in by.items():
            means = []
            own = raw[cid]
            for source, src in raw.items():
                if source == cid: continue
                m, th = theta_for(rr[0], method, src["values"], own["cdxa"])
                e = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
                means.append(float(np.mean(e)) * 100)
            swaps.append(dict(config_id=cid, model=own["model"], method=method, n_donor_configs=len(means),
                              min_mean_err_pct=round(float(min(means)), 3), p10_mean_err_pct=round(float(np.percentile(means,10)),3),
                              p50_mean_err_pct=round(float(np.median(means)),3), p90_mean_err_pct=round(float(np.percentile(means,90)),3),
                              max_mean_err_pct=round(float(max(means)),3), width_min_to_max_pp=round(float(max(means)-min(means)),3)))
    write(os.path.join(HERE, "g5_class_parameters.csv"), params_rows)
    write(os.path.join(HERE, "g5_class_band.csv"), band)
    write(os.path.join(HERE, "g5_class_band_summary.csv"), summary)
    write(os.path.join(HERE, "g5_swap.csv"), swaps)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for j, method in enumerate(("C", "L4b")):
        for i, weighting in enumerate(("config_unweighted", "model_weighted")):
            a = axs[i, j]
            d = [r["mean_err_pct"] for r in band if r["method"] == method and r["weighting"] == weighting and r["percentile"] == "P50"]
            a.hist(d, bins=20, color="tab:blue", alpha=.75); a.axvline(0,color="k",lw=.8); a.axvline(5,color="k",ls=":"); a.axvline(-5,color="k",ls=":")
            a.set_title("%s, %s P50" % (method, weighting.replace("_", " "))); a.set_ylabel("configs")
    for a in axs[-1]: a.set_xlabel("mean error vs certified [%]")
    fig.tight_layout(); f=os.path.join(HERE,"g5_class_band_hist.png"); fig.savefig(f,dpi=110); print("wrote",f)


if __name__ == "__main__":
    main()
