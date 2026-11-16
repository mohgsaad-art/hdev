"""Diagnostic (eCanter C0059): method C with eta_r allowed up to 3 (not physical), HDEV engine; plus the VECTO response to eta_r > 1. Shows what the data ask for when the
regeneration efficiency is not held at 1. Output: p3_relaxed_etar.csv. VECTO part resumes from cache like the other fits."""
import csv, json, os, sys, time
import numpy as np
import engines as E
import fit_vecto as FV

HERE = E.HERE

def main():
    E.setup(); E.prewarm()
    os.environ["VECTO_DEADLINE"] = str(time.time() + float(os.environ.get("VECTO_BUDGET_S", "540")))
    cid = "C0059"
    rr = E.records(cid); m = E.method(cid)
    lo, hi, names = E.bounds(cid)
    lo2, hi2 = lo.copy(), hi.copy(); hi2[1] = 3.0
    rows = []
    # HDEV engine: same least squares as PR #37 (fit_v2) with the relaxed upper bound
    from scipy.optimize import least_squares
    cert = E.certified(cid)
    scale = np.where(hi2 > 0, hi2, 1.0)
    best = None
    for s in E.starts(cid):
        sol = least_squares(lambda z: E.hdev_predict(cid, z * scale) / cert - 1, np.clip(np.array(s) / scale, lo2 / scale + 1e-9, hi2 / scale - 1e-9),
                            bounds=(lo2 / scale, hi2 / scale), xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=300)
        if best is None or sol.cost < best.cost:
            best = sol
    th = best.x * scale
    e = E.hdev_predict(cid, th) / cert - 1
    rows.append(dict(engine="HDEV", eta_d=round(th[0], 4), eta_r=round(th[1], 4), F0_N=round(th[2], 1), rms_pct=round(100 * float(np.sqrt(np.mean(e ** 2))), 3),
                     mean_abs_err_pct=round(100 * float(np.mean(np.abs(e))), 3), worst_abs_err_pct=round(100 * float(np.max(np.abs(e))), 3),
                     errors_pct=";".join("%+.2f" % (100 * x) for x in e)))
    # VECTO engine: a map with eta_r > 1 (more electric power out than mechanical power in) is not represented correctly by VECTO's map reader
    # (loss values are treated as magnitudes); show the response of the 4 results to eta_r = 0.999 and 1.029 at otherwise equal values
    for er in (0.999, 1.029):
        v = E.vecto_run(cid, (0.652, er, 0.5), "axle")
        rows.append(dict(engine="VECTO at fixed eta_d 0.652, F0 0.5 N", eta_d=0.652, eta_r=er, F0_N=0.5, rms_pct="", mean_abs_err_pct="",
                         worst_abs_err_pct="", errors_pct=";".join("%+.2f" % (100 * (x / c - 1)) for x, c in zip(v["term"], cert)),
                         predicted_kwh_km=";".join("%.4f" % x for x in v["term"])))
    with open(os.path.join(HERE, "p3_relaxed_etar.csv"), "w", newline="") as fh:
        fh.write(E.TI.ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in rows for k in r))); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)

if __name__ == "__main__":
    try:
        main(); print("DONE")
    except E.DeadlineExceeded:
        print("RESUME"); sys.exit(3)
