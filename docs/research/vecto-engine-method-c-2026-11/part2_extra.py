"""Part 2/3 supporting runs (all with the same VECTO jobs and the same cache):
 1. engine decomposition at FIXED method C values: VECTO(theta) vs HDEV(theta) for theta = HDEV full fit and theta = VECTO full fit, per result
 2. F0 construction sensitivity: the same theta with F0 inside the IEPC map instead of the separate axle loss map
 3. size of battery loss and charging-efficiency effect: EC_el_final / terminal energy at the VECTO full-fit values
 4. relaxed-bound diagnostic (eCanter): how large would eta_r have to be (HDEV engine and VECTO engine)?
Outputs: p2_engine_at_fixed_theta.csv, p2_f0_construction.csv, p2_final_vs_terminal.csv, p2_relaxed_etar.csv
"""
import csv
import json
import os
import sys

import numpy as np

import engines as E
import fit_vecto as FV

HERE = E.HERE
ATTR = E.TI.ATTR
RES = os.path.join(HERE, "results")


def write(name, rows):
    with open(os.path.join(HERE, name), "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader(); w.writerows(rows)
    print("wrote", name)


def thetas(cid):
    h = json.load(open(os.path.join(HERE, "hdev_reference.json")))[cid]["theta"]
    v = json.load(open(os.path.join(RES, "%s_axle_full.json" % cid)))["theta"]
    return {"theta_HDEV_fit": np.array(h), "theta_VECTO_fit": np.array(v)}


def main(step):
    E.setup()
    E.prewarm()
    os.environ["VECTO_DEADLINE"] = str(__import__("time").time() + float(os.environ.get("VECTO_BUDGET_S", "540")))
    rows1, rows2, rows3 = [], [], []
    for cid in E.TI.TRUCKS:
        rr = E.records(cid)
        cert = E.certified(cid)
        lo, hi, _ = E.bounds(cid)
        for name, th in thetas(cid).items():
            th = np.clip(th, lo, hi)
            h = E.hdev_predict(cid, th)
            if step in ("1", "all"):
                v = E.vecto_run(cid, tuple(th), "axle")
                for r, hh, vv, c in zip(rr, h, v["term"], cert):
                    rows1.append(dict(truck=cid, theta_set=name, theta=";".join("%.5g" % x for x in th), mission=r["mission"], payload_kg=round(r["payload"]),
                                      certified=round(c, 4), HDEV_engine=round(hh, 4), VECTO_engine=round(vv, 4), VECTO_minus_HDEV_pct=round(100 * (vv / hh - 1), 2),
                                      HDEV_err_pct=round(100 * (hh / c - 1), 2), VECTO_err_pct=round(100 * (vv / c - 1), 2)))
            if step in ("2", "all"):
                va = E.vecto_run(cid, tuple(th), "axle")
                vi = E.vecto_run(cid, tuple(th), "iepc")
                for r, a, b, c in zip(rr, va["term"], vi["term"], cert):
                    rows2.append(dict(truck=cid, theta_set=name, mission=r["mission"], payload_kg=round(r["payload"]), certified=round(c, 4),
                                      F0_in_axle_loss_map=round(a, 4), F0_in_IEPC_map=round(b, 4), difference_pct=round(100 * (b / a - 1), 2)))
            if step in ("3", "all") and name == "theta_VECTO_fit":
                va = E.vecto_run(cid, tuple(th), "axle")
                for r, a, f, c in zip(rr, va["term"], va["final"], cert):
                    rows3.append(dict(truck=cid, mission=r["mission"], payload_kg=round(r["payload"]), certified=round(c, 4), terminal_over_0p995=round(a, 4),
                                      EC_el_final_over_0p995_generic_battery=round(f, 4), final_over_terminal_pct=round(100 * (f / a - 1), 2),
                                      err_terminal_pct=round(100 * (a / c - 1), 2), err_final_pct=round(100 * (f / c - 1), 2)))
    if rows1:
        write("p2_engine_at_fixed_theta.csv", rows1)
    if rows2:
        write("p2_f0_construction.csv", rows2)
    if rows3:
        write("p2_final_vs_terminal.csv", rows3)


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "all")
        print("DONE")
    except E.DeadlineExceeded:
        print("RESUME")
        sys.exit(3)
