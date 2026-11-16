"""Part 2: method C fitted on ALL certified results with VECTO in the loop, then the hide-one-result test.

Usage: python part2_fit.py <truck> full [f0_mode]       # full fits from two starts, keeps the lower cost
       python part2_fit.py <truck> loro [f0_mode]       # one fit per hidden result (parallel folds), fixed Jacobian from the full fit, then gradient check
Results: results/<truck>_<f0_mode>_full.json, results/<truck>_<f0_mode>_loro.json. Every VECTO job is cached in cache/ (parameter set -> result).
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import engines as E
import fit_vecto as FV

HERE = E.HERE
RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
T0 = time.time()


def log(*a):
    print("[%6.0f s]" % (time.time() - T0), *a, flush=True)


def hdev_ref(cid):
    return json.load(open(os.path.join(HERE, "hdev_reference.json")))[cid]


def full(cid, f0_mode):
    P = FV.Problem(cid, f0_mode, log=log)
    ref = hdev_ref(cid)
    starts = [np.array(ref["theta"], float)]
    s_c = E.starts(cid)                      # PR #37 starts of method C (+ CdxA range middle)
    starts.append(np.array(s_c[2], float))   # the third PR #37 start (0.95, 0.95, 0 [, CdxA mid]), unrelated to the HDEV optimum
    best = None
    runs = []
    for i, s in enumerate(starts):
        log("full fit", cid, f0_mode, "start", i, np.round(s, 4))
        sol = P.fit(s, jac="broyden", max_nfev=14)
        log("  -> theta", np.round(sol["theta"], 5), "cost %.6g nfev %d status %d" % (sol["cost"], sol["nfev"], sol["status"]), sol["at_bound"])
        runs.append(dict(start=list(s), theta=list(sol["theta"]), cost=sol["cost"], nfev=sol["nfev"], status=sol["status"], at_bound=sol["at_bound"]))
        if best is None or sol["cost"] < best["cost"] - 1e-12:
            best = sol
    gnorm, J = FV.grad_check(P, best["theta"], P.used)
    log("projected gradient norm at the best solution (fresh finite differences): %.3g" % gnorm)
    out = dict(cid=cid, f0_mode=f0_mode, names=list(P.names), theta=list(best["theta"]), cost=best["cost"], rms=float(np.sqrt(np.mean(best["resid_all"] ** 2))),
               resid_all=list(best["resid_all"]), at_bound=best["at_bound"], runs=runs, grad_norm=gnorm, J_all=J.tolist(),
               pred=list((best["resid_all"] + 1.0) * P.cert), wall_s=time.time() - T0, njobs=P.nfun)
    json.dump(out, open(os.path.join(RES, "%s_%s_full.json" % (cid, f0_mode)), "w"), indent=1)
    return out


def check_folds(cid, f0_mode, which):
    """Fresh finite-difference gradient (4 jobs) at the fixed-Jacobian solution of selected folds."""
    res = json.load(open(os.path.join(RES, "%s_%s_loro.json" % (cid, f0_mode))))
    out = res.setdefault("checks", {})
    n = len(E.certified(cid))
    for i in which:
        if str(i) in out:
            continue
        f = res["folds"][i]
        P = FV.Problem(cid, f0_mode, used=[j for j in range(n) if j != i])
        g, _ = FV.grad_check(P, np.array(f["theta"]), P.used)
        out[str(i)] = g
        log("fold", i, "fresh-gradient norm %.3g (full-fit gradient was reported in the full json)" % g)
        json.dump(res, open(os.path.join(RES, "%s_%s_loro.json" % (cid, f0_mode)), "w"), indent=1)


def loro(cid, f0_mode):
    fullres = json.load(open(os.path.join(RES, "%s_%s_full.json" % (cid, f0_mode))))
    J_all = np.array(fullres["J_all"])
    theta_full = np.array(fullres["theta"])
    E.prewarm()
    n = len(E.certified(cid))

    def fold(i):
        used = [j for j in range(n) if j != i]
        P = FV.Problem(cid, f0_mode, used=used, log=lambda *a: None)
        sol = P.fit(theta_full, jac="fixed", J_all=J_all, max_nfev=10)
        g, refined = float("nan"), False        # gradient check on selected folds only (check_folds), it costs 4 extra jobs per fold
        pred = (sol["resid_all"][i] + 1.0) * P.cert[i]
        log("fold", i, "theta", np.round(sol["theta"], 4), "held-out err %+.2f %%" % (100 * sol["resid_all"][i]), "grad %.2g refined %s" % (g, refined))
        return dict(i=i, theta=list(sol["theta"]), pred=pred, err=float(sol["resid_all"][i]), grad_norm=g, refined=refined, nfev=sol["nfev"], at_bound=sol["at_bound"],
                    train_rms=float(np.sqrt(np.mean(sol["resid_used"] ** 2))), resid_all=list(sol["resid_all"]))
    # folds run in parallel, each fold's jobs are queued on its own Problem pool (WORKERS threads each) -> limit folds
    with ThreadPoolExecutor(int(os.environ.get("VECTO_FOLDS", "4"))) as ex:
        folds = list(ex.map(fold, range(n)))
    json.dump(dict(cid=cid, f0_mode=f0_mode, folds=folds, wall_s=time.time() - T0), open(os.path.join(RES, "%s_%s_loro.json" % (cid, f0_mode)), "w"), indent=1)
    os.environ["VECTO_DEADLINE"] = str(time.time() + float(os.environ.get("VECTO_BUDGET_S", "540")))
    errs = np.array([f["err"] for f in folds])
    log("LORO mean abs %.2f %% worst %.2f %%" % (100 * np.mean(np.abs(errs)), 100 * np.max(np.abs(errs))))


if __name__ == "__main__":
    cid, what = sys.argv[1], sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "axle"
    budget = float(os.environ.get("VECTO_BUDGET_S", "540"))
    os.environ["VECTO_DEADLINE"] = str(time.time() + budget)
    E.setup()
    try:
        if what == "check":
            check_folds(cid, mode, [int(x) for x in sys.argv[4].split(",")])
        else:
            (full if what == "full" else loro)(cid, mode)
        print("DONE")
    except E.DeadlineExceeded:
        print("RESUME: time budget used; run the same command again (all finished VECTO jobs are cached)")
        sys.exit(3)
