"""Part 2.3 and Part 3: tables from the saved fits.
Outputs: p2_fitted_values.csv, p2_per_result.csv, p3_summary.csv, p3_ecanter_evidence.csv, p2_vecto_runs.csv (every VECTO job of this study)
"""
import csv
import glob
import json
import os

import numpy as np

import engines as E

HERE = E.HERE
RES = os.path.join(HERE, "results")
ATTR = E.TI.ATTR
NAMES = {"C0091": "IVECO S-eWay", "C0059": "Fuso eCanter"}


def write(name, rows):
    with open(os.path.join(HERE, name), "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader(); w.writerows(rows)
    print("wrote", name)


def main():
    E.setup()
    E.prewarm()
    href = json.load(open(os.path.join(HERE, "hdev_reference.json")))
    fitted, per, summ = [], [], []
    store = {}
    for cid in E.TI.TRUCKS:
        rr = E.records(cid)
        cert = E.certified(cid)
        h = href[cid]
        vf = json.load(open(os.path.join(RES, "%s_axle_full.json" % cid)))
        vl = json.load(open(os.path.join(RES, "%s_axle_loro.json" % cid)))
        names = h["names"]
        lo, hi, _ = E.bounds(cid)
        for engine, th, rms, ab in (("HDEV engine (PR #37)", h["theta"], h["rms"], None), ("VECTO engine", vf["theta"], float(np.sqrt(np.mean(np.array(vf["resid_all"]) ** 2))), vf["at_bound"])):
            th = np.array(th)
            hits = [n for n, v, a, b in zip(names, th, lo, hi) if min(abs(v - a), abs(b - v)) <= 1e-3 * (b - a)]
            d = dict(truck=cid, name=NAMES[cid], engine=engine, n_results=len(rr), n_fitted=len(th), rms_pct=round(100 * rms, 3), at_bound=";".join(hits))
            for n, v in zip(names, th):
                d[{"eta": "eta_d", "regen": "eta_r", "F0": "F0_N", "cdxa_declared": "cdxa_declared_m2"}[n]] = round(float(v), 5)
            fitted.append(d)
        pf_h = np.array(h["pred_full"]); pf_v = np.array(vf["pred"])
        lo_h = np.array(h["loro_pred"]); lo_v = np.array([f["pred"] for f in vl["folds"]])
        for i, r in enumerate(rr):
            per.append(dict(truck=cid, mission=r["mission"], payload_kg=round(r["payload"]), certified=round(cert[i], 4),
                            HDEV_fit_all=round(pf_h[i], 4), HDEV_fit_all_err_pct=round(100 * (pf_h[i] / cert[i] - 1), 2),
                            VECTO_fit_all=round(pf_v[i], 4), VECTO_fit_all_err_pct=round(100 * (pf_v[i] / cert[i] - 1), 2),
                            HDEV_hide_one=round(lo_h[i], 4), HDEV_hide_one_err_pct=round(100 * (lo_h[i] / cert[i] - 1), 2),
                            VECTO_hide_one=round(lo_v[i], 4), VECTO_hide_one_err_pct=round(100 * (lo_v[i] / cert[i] - 1), 2),
                            HDEV_hide_one_theta=";".join("%.4g" % x for x in h["loro_theta"][i]), VECTO_hide_one_theta=";".join("%.4g" % x for x in vl["folds"][i]["theta"])))
        urban = np.array([r["mission"] == "Urban Delivery" for r in rr])
        store[cid] = dict(cert=cert, pf=(pf_h, pf_v), lo=(lo_h, lo_v), urban=urban)
        for view, (a, b) in (("fit on all results", (pf_h, pf_v)), ("hide one result", (lo_h, lo_v))):
            for engine, p in (("HDEV engine (PR #37)", a), ("VECTO engine", b)):
                e = 100 * (p / cert - 1)
                summ.append(dict(truck=cid, view=view, engine=engine, n=len(e), mean_err_pct=round(float(e.mean()), 2), mean_abs_err_pct=round(float(np.abs(e).mean()), 2),
                                 worst_abs_err_pct=round(float(np.abs(e).max()), 2), urban_mean_abs_err_pct=round(float(np.abs(e[urban]).mean()), 2),
                                 urban_worst_abs_err_pct=round(float(np.abs(e[urban]).max()), 2), share_within_5pct=round(float(np.mean(np.abs(e) <= 5)), 2),
                                 share_too_low=round(float(np.mean(e < 0)), 2)))
    # share that disappears with VECTO's engine
    share = []
    for cid in list(E.TI.TRUCKS) + ["both"]:
        for view in ("fit on all results", "hide one result"):
            def get(engine, key):
                rows = [s for s in summ if s["view"] == view and s["engine"] == engine and (cid == "both" or s["truck"] == cid)]
                return rows
            if cid == "both":
                eh, ev, uh, uv = [], [], [], []
                for c in E.TI.TRUCKS:
                    d = store[c]; k = 0 if view.startswith("fit") else 1
                    eh += list(100 * (d[("pf" if k == 0 else "lo")][0] / d["cert"] - 1)); ev += list(100 * (d[("pf" if k == 0 else "lo")][1] / d["cert"] - 1))
                    uh += list(d["urban"]); uv += list(d["urban"])
                eh, ev, u = np.array(eh), np.array(ev), np.array(uh)
            else:
                d = store[cid]; k = "pf" if view.startswith("fit") else "lo"
                eh, ev, u = 100 * (d[k][0] / d["cert"] - 1), 100 * (d[k][1] / d["cert"] - 1), d["urban"]
            for metric, f in (("mean absolute error", lambda e: np.abs(e).mean()), ("worst absolute error", lambda e: np.abs(e).max()),
                              ("Urban mean absolute error", lambda e: np.abs(e[u]).mean()), ("Urban worst absolute error", lambda e: np.abs(e[u]).max())):
                a, b = float(f(eh)), float(f(ev))
                share.append(dict(truck=cid if cid != "both" else "both trucks (16 results)", view=view, metric=metric, HDEV_engine_pct=round(a, 2), VECTO_engine_pct=round(b, 2),
                                  share_that_disappears_pct=round(100 * (1 - b / a), 1), remains_pct_points=round(b, 2)))
    write("p2_fitted_values.csv", fitted)
    write("p2_per_result.csv", per)
    write("p3_summary.csv", summ)
    write("p3_share_removed_by_vecto_engine.csv", share)

    # ---- every VECTO job of this study
    runs = []
    for f in sorted(glob.glob(os.path.join(E.CACHE, "*.json"))):
        d = json.load(open(f))
        cid = os.path.basename(f).split("_")[0]
        keys = [(m["cycle"], m["loading"]) for m in d["meta"]]
        for (cyc, ld), t, fi in zip(keys, d["term"], d["final"]):
            runs.append(dict(truck=cid, f0_mode=d["f0_mode"], eta_d=d["theta"][0], eta_r=d["theta"][1], F0_N=d["theta"][2], cdxa=(d["theta"][3] if len(d["theta"]) > 3 else ""),
                             cycle=cyc, loading_kg=round(ld, 2), terminal_kwh_km_over_0p995=round(t, 5), EC_el_final_kwh_km_over_0p995=round(fi, 5), job_wall_s=round(d["wall_s"], 1)))
    write("p2_vecto_runs.csv", runs)
    print(len(runs), "result rows from", len(glob.glob(os.path.join(E.CACHE, "*.json"))), "VECTO jobs")

    # ---- eCanter evidence
    bal = {}
    for r in csv.DictReader(l for l in open(os.path.join(HERE, "p1_balance.csv")) if not l.startswith("#")):
        bal[(r["truck"], r["mission"], int(r["payload_kg"]))] = r
    ev = []
    import csv as _csv
    for cid in E.TI.TRUCKS:
        rr = E.records(cid)
        for i, r in enumerate(rr):
            b = bal[(cid, r["mission"], round(r["payload"]))]
            lossless = float(b["vsum_terminal_kwh_km"]) / E.CHARGING_ETA
            vmod_t = None
            cert = r["cert"]
            ev.append(dict(truck=cid, mission=r["mission"], payload_kg=round(r["payload"]), certified=round(cert, 4), VECTO_lossless_wheel_plus_aux=round(lossless, 4),
                           certified_over_lossless=round(cert / lossless, 3), extra_kwh_km=round(cert - lossless, 4),
                           avg_speed_kmh=b["avg_speed_kmh"], extra_power_kW_at_avg_speed=round((cert - lossless) * float(b["avg_speed_kmh"]), 2),
                           VECTO_wheel_drive_kwh_km=b["vmod_E_wheel_drive"], VECTO_wheel_regen_side_kwh_km=b["vmod_E_wheel_regen_side"],
                           HDEV_wheel_drive_kwh_km=b["harness_E_wheel_drive"], HDEV_wheel_regen_side_kwh_km=b["harness_E_wheel_regen_side"],
                           VECTO_fit_err_pct=per[[p["truck"] + p["mission"] + str(p["payload_kg"]) for p in per].index(cid + r["mission"] + str(round(r["payload"])))]["VECTO_fit_all_err_pct"]))
    write("p3_certified_vs_lossless.csv", ev)


if __name__ == "__main__":
    main()
