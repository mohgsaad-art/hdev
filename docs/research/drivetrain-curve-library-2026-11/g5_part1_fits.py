"""Part 1: per-config full fits for Group 5 only, run in config batches after g5_build_records.py.

Usage:
    python g5_part1_fits.py 0       # fit cached batch 0
    python g5_part1_fits.py combine # combine batch CSVs to g5_fits.csv and g5_skipped.csv

Settings are exactly Part 3 of PR #37: P3.set_bounds(), HN.AIRDRAG_MODE='range_mid', P3.make() and fit_v2().
"""
import csv
import glob
import os
import sys
import time
from collections import Counter

import numpy as np

import harness as HN
import part3_loo as P3
import methods_lib as ML

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")


def cfgs():
    return {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HN.V2_DIR, "truck_configs.csv"))) if r["VehicleGroup"] == "5"}


def parse_kw(desc):
    for p in (desc or "").split(":"):
        if p.endswith("kW"):
            return float(p[:-2])
    return None


def bounds_hit(m, th, rec):
    if not th:
        return ""
    lo, hi = m.bounds_for(rec)
    return ";".join(n for n, v, a, b in zip(m.names, th, lo, hi)
                    if min(abs(v - a), abs(b - v)) <= 1e-3 * (b - a))


def write(path, rows):
    with open(path, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["config_id", "reason"])
        w.writeheader(); w.writerows(rows)


def fit_batch(i):
    P3.set_bounds(); HN.AIRDRAG_MODE = "range_mid"
    cfg = cfgs()
    ids = [r["config_id"] for r in cfg.values()]
    batch_ids = ids[i * 30:(i + 1) * 30]
    path = os.path.join(HN.CACHE, "records_g5_%02d_range_mid.npz" % i)
    if not os.path.exists(path):
        raise SystemExit("BLOCKED: cache missing; run g5_build_records.py %d" % i)
    recs, skipped = HN._load_npz(path)
    by = {}
    for r in recs:
        by.setdefault(r["config_id"], []).append(r)
    out, sk = [], [dict(config_id=a, mission=b, payload_kg=c, reason=d) for a, b, c, d in skipped]
    t0 = time.monotonic()
    for cid in batch_ids:
        rr = sorted(by.get(cid, []), key=lambda r: (r["mission"], r["payload"]))
        if len(rr) < 4:
            sk.append(dict(config_id=cid, mission="", payload_kg="", reason="BLOCKED: %d results < 4" % len(rr)))
            continue
        c = cfg[cid]
        for tag, ctor in (("C", ML.MethodCv2), ("L4b", ML.MethodL4b)):
            m = P3.make(tag, rr[0])
            th, rms = ML.fit_v2(m, rr)
            e = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
            kw = parse_kw(c["iepc_desc"])
            vals = {"eta_d": "", "eta_r": "", "F0_N": "", "a_W": "", "b_perW": "", "c_W_per_mps": "", "cdxa_declared_m2": ""}
            for n, v in zip(m.names, th):
                vals[{"eta": "eta_d", "regen": "eta_r", "F0": "F0_N", "a_W": "a_W", "b_perW": "b_perW",
                      "c_W_per_mps": "c_W_per_mps", "cdxa_declared": "cdxa_declared_m2"}[n]] = round(v, 8)
            out.append(dict(config_id=cid, make=c["Make_clean"], model=c["Model"], architecture=rr[0]["arch"],
                            gears=rr[0]["n_gears"], iepc_rated_kW=kw, battery_installed_kwh=c["bat_installed_kwh"],
                            airdrag_method=c["AirDrag_CertificationMethod"], cdxa_range=c["AirDrag_CdxA_range"],
                            method=tag, n_results=len(rr), n_fitted=len(th), dof=len(rr)-len(th),
                            at_bound=bounds_hit(m, th, rr[0]), in_sample_mean_abs_err_pct=round(100 * np.mean(np.abs(e)), 3),
                            in_sample_worst_abs_err_pct=round(100 * np.max(np.abs(e)), 3), in_sample_mean_err_pct=round(100 * np.mean(e), 3),
                            **vals))
    elapsed = time.monotonic() - t0
    write(os.path.join(HERE, "g5_fits_batch_%02d.csv" % i), out)
    write(os.path.join(HERE, "g5_fits_batch_%02d_skipped.csv" % i), sk)
    print("fit batch %d: %d config-method fits, %d skipped, %.1f s" % (i, len(out), len(sk), elapsed))
    print("wrote", os.path.join(HERE, "g5_fits_batch_%02d.csv" % i))
    print("wrote", os.path.join(HERE, "g5_fits_batch_%02d_skipped.csv" % i))
    if elapsed > 600:
        raise SystemExit("BLOCKED: batch exceeded 10 minutes")


def read(path):
    return list(csv.DictReader(ln for ln in open(path) if not ln.startswith("#")))


def combine():
    fits = sum((read(p) for p in sorted(glob.glob(os.path.join(HERE, "g5_fits_batch_??.csv")))), [])
    sk = sum((read(p) for p in sorted(glob.glob(os.path.join(HERE, "g5_fits_batch_??_skipped.csv")))), [])
    write(os.path.join(HERE, "g5_fits.csv"), fits)
    write(os.path.join(HERE, "g5_skipped.csv"), sk)
    print("fits: %d rows / %d configs; skipped %d (%s)" % (len(fits), len(set(r["config_id"] for r in fits)), len(sk), dict(Counter(r["reason"] for r in sk))))
    print("bound hits:", dict(Counter(r["method"] for r in fits if r["at_bound"])))
    print("wrote", os.path.join(HERE, "g5_fits.csv")); print("wrote", os.path.join(HERE, "g5_skipped.csv"))


if __name__ == "__main__":
    if sys.argv[1] == "combine": combine()
    else: fit_batch(int(sys.argv[1]))
