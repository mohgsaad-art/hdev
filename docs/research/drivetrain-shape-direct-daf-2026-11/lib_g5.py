"""Shared helpers for the 16 Nov 2026 shape / DAF / baseline job.

Uses the PR #37/#38 harness unchanged (docs/research/drivetrain-curve-library-2026-11): same bounds
(P3.set_bounds), HN.AIRDRAG_MODE = "range_mid", same cached records (records_g5_NN_range_mid.npz, git-ignored).
Nothing in the harness, the notebook or src/ is edited.
"""
import csv
import glob
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.abspath(os.path.join(HERE, "..", "drivetrain-curve-library-2026-11"))
sys.path.insert(0, LIB)

import harness as HN          # noqa: E402
import part3_loo as P3        # noqa: E402
import methods_lib as ML      # noqa: E402

ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
PARAMS = {"C": ("eta_d", "eta_r", "F0_N"), "L4b": ("a_W", "b_perW", "c_W_per_mps")}
BATCH = 30


def setup():
    P3.set_bounds()
    HN.AIRDRAG_MODE = "range_mid"


def read(path):
    return list(csv.DictReader(ln for ln in open(path) if not ln.startswith("#")))


def write(path, rows, attr=True):
    with open(path, "w", newline="") as fh:
        if attr:
            fh.write(ATTR + "\n")
        fields = list(dict.fromkeys(k for r in rows for k in r)) if rows else ["empty"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("wrote", path)
    return path


def records():
    """All 2,958 group 5 records (cached npz from PR #38), sorted per config by (mission, payload)."""
    by = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(HN.CACHE, "records_g5_??_range_mid.npz"))):
        rr, _ = HN._load_npz(p)
        for r in rr:
            by[r["config_id"]].append(r)
    for v in by.values():
        v.sort(key=lambda r: (r["mission"], r["payload"]))
    return by


def g5_config_ids():
    cfg = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HN.V2_DIR, "truck_configs.csv")))}
    return [c for c, r in cfg.items() if r["VehicleGroup"] == "5"], cfg


def fits_c_l4b():
    """PR #38 g5_fits.csv -> {method: {config_id: dict(values, cdxa, model, make)}}."""
    out = defaultdict(dict)
    for r in read(os.path.join(LIB, "g5_fits.csv")):
        out[r["method"]][r["config_id"]] = dict(
            values=tuple(float(r[p]) for p in PARAMS[r["method"]]),
            cdxa=float(r["cdxa_declared_m2"]) if r["cdxa_declared_m2"] else None,
            model=r["model"], make=r["make"], row=r)
    return out


def theta_with_cdxa(rec, method_name, drivetrain, cdxa):
    m = P3.make(method_name, rec)
    return m, tuple(drivetrain) + ((cdxa,) if rec["airdrag_measured"] else ())


def pctl(x, q):
    return float(np.percentile(np.asarray(x, float), q))


def summarize_models(model_rows):
    """model_rows: list of dict(mean_err, worst_abs, n, n_low, abs_mean) one per held-out model.
    Same definitions as PR #38 g5_holdout_model_summary.csv, plus share too low and worst model mean error."""
    e = np.array([r["mean_err"] for r in model_rows]) * 100
    w = np.array([r["worst_abs"] for r in model_rows]) * 100
    n = np.array([r["n"] for r in model_rows])
    nl = np.array([r["n_low"] for r in model_rows])
    return dict(n_models=len(e), mean_of_model_mean_err_pct=round(float(e.mean()), 3),
                p10_pct=round(pctl(e, 10), 3), p50_pct=round(pctl(e, 50), 3), p90_pct=round(pctl(e, 90), 3),
                width_p90_minus_p10_pp=round(pctl(e, 90) - pctl(e, 10), 3),
                worst_model_mean_abs_err_pct=round(float(np.abs(e).max()), 3),
                worst_single_result_abs_err_pct=round(float(w.max()), 3),
                share_results_too_low=round(float(nl.sum() / n.sum()), 3), n_results=int(n.sum()))
