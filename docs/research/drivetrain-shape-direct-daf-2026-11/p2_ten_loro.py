"""Part 2.4: the 10 trucks of Appendix B (16 Nov v2 prompt), per-truck leave-one-RESULT-out (as PR #37 Part 3, LORO).

Methods: C, L4b (as PR #37), L1 and L1b with (a) the a-priori rule 'arch' (PR #37 ML.ARCH_SHAPE) and (b) each fixed shape S3a, S3b, S2_PSM, S2_ASM.
Each truck is fitted on its own other results only (certified results of the median-mass vehicle, every mission except Municipal, EMS kept).
Outputs: p2_ten_predictions.csv, p2_ten_summary.csv, p2_ten_worst_per_truck.csv, p2_ten_fits.csv
"""
import multiprocessing as mp
import os

import numpy as np

import lib_g5 as L
import p1_ecanter as PE
import p2_methods as PM

ML, P3 = L.ML, L.P3
HERE = L.HERE
TEN, NAMES = P3.TEN, P3.NAMES
FIXED = ["S3a_IEPC_1speed", "S3b_IEPC_3speed", "S2_busIEPC_PSM", "S2_busIEPC_ASM"]
_G = {}


def methods():
    out = [("C", lambda rec: P3.make("C", rec)), ("L4b", lambda rec: P3.make("L4b", rec))]
    for shape in ["arch"] + FIXED:
        for kind in ("L1", "L1b"):
            out.append((PM.label(kind, shape), lambda rec, k=kind, s=shape: PM.make(k, s, rec)))
    return out


def _job(args):
    cid, idx = args
    name, mk = methods()[idx]
    rr = _G["by"][cid]
    m = mk(rr[0])
    res = ML.loo_v2(m, rr, None)
    th, _ = ML.fit_v2(m, rr)
    return cid, name, len(m.names), res, th, m.names


def main():
    L.setup()
    by, _ = PE.ten_records()
    _G["by"] = by
    jobs = [(c, i) for c in TEN for i in range(len(methods()))]
    with mp.get_context("fork").Pool(8) as pool:
        out = pool.map(_job, jobs, chunksize=1)
    preds, worst, fits = [], [], []
    for cid, name, k, res, th, names in out:
        rr = by[cid]
        e = np.array([x["err"] for x in res])
        for x, r in zip(res, rr):
            preds.append(dict(config_id=cid, truck=NAMES[cid], method=name, mission=r["mission"], payload_kg=round(r["payload"]),
                              certified_kwh_km=round(r["cert"], 4), predicted_kwh_km=round(x["pred"], 4), err_pct=round(100 * x["err"], 2)))
        worst.append(dict(config_id=cid, truck=NAMES[cid], method=name, n_results=len(rr), n_fitted=k, dof=len(rr) - k,
                          worst_abs_err_pct=round(100 * float(np.abs(e).max()), 2), mean_abs_err_pct=round(100 * float(np.abs(e).mean()), 2),
                          largest_under_pct=round(100 * float(min(0.0, e.min())), 2), all_within_5pct=bool(np.abs(e).max() <= 0.05)))
        fits.append(dict(config_id=cid, truck=NAMES[cid], method=name, values=";".join("%s=%.5g" % (n, v) for n, v in zip(names, th))))
    summ = []
    for name, _ in methods():
        w = [x for x in worst if x["method"] == name]
        e = np.array([p["err_pct"] for p in preds if p["method"] == name]) / 100
        summ.append(dict(method=name, n_fitted=w[0]["n_fitted"], trucks_all_within_5pct=sum(x["all_within_5pct"] for x in w), predictions=len(e),
                         share_within_5pct=round(float(np.mean(np.abs(e) <= 0.05)), 3), share_too_low=round(float(np.mean(e < 0)), 3),
                         mean_err_pct=round(100 * float(e.mean()), 2), median_abs_err_pct=round(100 * float(np.median(np.abs(e))), 2),
                         largest_under_pct=round(100 * float(e.min()), 2), largest_over_pct=round(100 * float(e.max()), 2),
                         worst_truck_abs_err_pct=max(x["worst_abs_err_pct"] for x in w),
                         median_of_truck_worst_abs_err_pct=round(float(np.median([x["worst_abs_err_pct"] for x in w])), 2)))
    L.write(os.path.join(HERE, "p2_ten_predictions.csv"), preds)
    L.write(os.path.join(HERE, "p2_ten_worst_per_truck.csv"), worst)
    L.write(os.path.join(HERE, "p2_ten_summary.csv"), summ)
    L.write(os.path.join(HERE, "p2_ten_fits.csv"), fits)
    for s in summ:
        print(s)


if __name__ == "__main__":
    main()
