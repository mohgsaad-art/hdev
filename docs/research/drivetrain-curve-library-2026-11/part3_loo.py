"""PART 3 -- leave-one-out on the 10 trucks: Method A (reference), C, L4a, L4b.

Physics: v2 harness through harness.py with the Part 1 air-drag rule (AIRDRAG_MODE = "range_mid").
Fitted per truck: C (eta_d, eta_r, F0), L4a (a, b), L4b (a, b, c); + declared CdxA inside its EEA range when
air drag was measured (WithCdxARange). Bounds: part2_L4_bounds.csv.
Results used: the median-mass vehicle of each config, every certified mission except Municipal; EMS kept.

Views:  LORO = leave one result out;  LOMO = leave one mission out (all payloads of that mission hidden).
Extra:  Municipal Utility WITHOUT PTO (driving only; never certified as such, never fitted) for trucks whose group
        has that mission, with the EEA Municipal payload -> how far C and L4 drift apart on an unseen cycle.

Outputs: part3_predictions.csv, part3_worst_per_truck.csv, part3_summary.csv, part3_fitted_values.csv,
         part3_plausibility.csv, part3_unseen_mission.csv, part3_*.png
"""
import csv
import os
import time
import multiprocessing as mp

import numpy as np

import harness as HN
import methods_lib as ML

HERE = os.path.dirname(os.path.abspath(__file__))
TEN = ["C0059", "C0091", "C0371", "C0116", "C0153", "C0218", "C0712", "C0206", "C0070", "C0001"]
NAMES = {"C0059": "Fuso eCanter", "C0091": "IVECO S-eWay", "C0371": "Scania R 400E", "C0116": "MAN eTGX",
         "C0153": "Mercedes eActros 600", "C0218": "Renault D", "C0712": "Volvo FM", "C0206": "Mercedes Econic",
         "C0070": "IVECO eDaily", "C0001": "DAF XB"}
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
METHODS = ("A", "C", "L4a", "L4b")
TARGET = 0.05
X_POINTS = (0.1, 0.25, 0.5, 1.0)


def set_bounds():
    b = {r["coef"]: r for r in csv.DictReader(open(os.path.join(HERE, "part2_L4_bounds.csv")))}
    ML.set_l4_bounds(float(b["a"]["value_frac"]), float(b["b"]["value_frac"]), float(b["c"]["value_frac"]))


def make(name, rec):
    m = {"A": ML.MethodA, "C": ML.MethodCv2, "L4a": ML.MethodL4a, "L4b": ML.MethodL4b}[name]()
    if name != "A" and rec["airdrag_measured"]:
        m = ML.WithCdxARange(m)
    return m


_G = {}


def _job(args):
    cid, mname, view = args
    recs = _G["by"][cid]
    m = make(mname, recs[0])
    t0 = time.process_time()
    if mname == "A":
        res = [dict(pred=m.predict(r), err=m.predict(r) / r["cert"] - 1, theta=()) for r in recs]
    else:
        res = ML.loo_v2(m, recs, None if view == "LORO" else [r["mission"] for r in recs])
    return cid, mname, view, m.name, len(m.names), res, time.process_time() - t0


def _full(args):
    cid, mname = args
    recs = _G["by"][cid]
    m = make(mname, recs[0])
    th, rms = ML.fit_v2(m, recs) if m.names else ((), 0.0)
    return cid, mname, m.name, th, rms


def write(path, rows, attr=True):
    with open(path, "w", newline="") as fh:
        if attr:
            fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return path


def unseen_records():
    """Municipal Utility (no PTO) records for trucks whose group has that mission in mission_setup.csv."""
    out = {}
    setup = HN.RH.load_setup()
    cfgs = HN._state()["cfgs"]
    for cid in TEN:
        vid, rows = HN.config_runs(cid)
        group = cfgs[cid]["VehicleGroup"]
        mun = [r for r in rows if r["mission"] == "Municipal Utility"]
        if (group, "Municipal Utility") not in setup or not mun:
            out[cid] = "BLOCKED: no Municipal Utility mission/payload for group %s in VECTO SegmentTable/EEA" % group
            continue
        recs = []
        for r in mun:
            rec = HN.build_record(cid, vid, "Municipal Utility", r["payload"], r["mass"], r["cert"])
            if "skip" in rec:
                out[cid] = "BLOCKED: " + rec["skip"]; break
            recs.append(HN.compact(rec))
        else:
            out[cid] = recs
    return out


def main():
    t_all = time.time()
    set_bounds()
    HN.AIRDRAG_MODE = "range_mid"
    recs, skipped = HN.load_or_build(TEN, "ten", processes=8)
    by = {}
    for r in recs:
        by.setdefault(r["config_id"], []).append(r)
    for cid in by:
        by[cid].sort(key=lambda r: (r["mission"], r["payload"]))
    _G["by"] = by
    jobs = [(c, m, v) for c in TEN for m in METHODS for v in ("LORO", "LOMO")]
    with mp.get_context("fork").Pool(8) as pool:
        out = pool.map(_job, jobs, chunksize=1)
        full = pool.map(_full, [(c, m) for c in TEN for m in METHODS], chunksize=1)
    t_fit = time.time() - t_all
    files = []

    # ---- predictions, per-truck worst, summary
    preds, worst, summ = [], [], []
    store = {}
    for cid, mname, view, full_name, k, res, cpu in out:
        rr = by[cid]; n = len(rr)
        n_train = n - 1 if view == "LORO" else None
        e = np.array([x["err"] for x in res])
        store[(cid, mname, view)] = res
        for x, r in zip(res, rr):
            nm = sum(1 for q in rr if q["mission"] == r["mission"])
            ntr = n - 1 if view == "LORO" else n - nm
            preds.append(dict(config_id=cid, truck=NAMES[cid], view=view, method=mname, method_full=full_name,
                              mission=r["mission"], payload_kg=round(r["payload"]), certified_kwh_km=round(r["cert"], 4),
                              predicted_kwh_km=round(x["pred"], 4), err_pct=round(100 * x["err"], 2),
                              n_results=n, n_fitted=k, dof_train=ntr - k,
                              underdetermined=bool(k > 0 and ntr - k < 1)))
        worst.append(dict(config_id=cid, truck=NAMES[cid], view=view, method=mname, method_full=full_name,
                          worst_abs_err_pct=round(100 * float(np.max(np.abs(e))), 2),
                          largest_under_pct=round(100 * float(min(0.0, e.min())), 2),
                          all_within_5pct=bool(np.max(np.abs(e)) <= TARGET), n_results=n, n_fitted=k, dof_full=n - k,
                          cpu_s=round(cpu, 2)))
    for view in ("LORO", "LOMO"):
        for mname in METHODS:
            w = [x for x in worst if x["view"] == view and x["method"] == mname]
            e = np.array([p["err_pct"] for p in preds if p["view"] == view and p["method"] == mname]) / 100
            eu = np.array([p["err_pct"] for p in preds if p["view"] == view and p["method"] == mname and p["mission"] == "Urban Delivery"]) / 100
            summ.append(dict(view=view, method=mname, trucks_all_within_5pct=sum(x["all_within_5pct"] for x in w),
                             predictions=len(e), share_within_5pct=round(float(np.mean(np.abs(e) <= TARGET)), 3),
                             share_too_low=round(float(np.mean(e < 0)), 3), largest_under_pct=round(100 * float(e.min()), 2),
                             largest_over_pct=round(100 * float(e.max()), 2), median_abs_err_pct=round(100 * float(np.median(np.abs(e))), 2),
                             mean_abs_err_urban_pct=round(100 * float(np.mean(np.abs(eu))), 2) if len(eu) else "",
                             worst_truck_pct=max(x["worst_abs_err_pct"] for x in w),
                             dof_min=min(x["dof_full"] for x in w)))
    # LOMO restricted to folds whose training set has at least one more result than fitted values
    for mname in METHODS:
        pp = [p for p in preds if p["view"] == "LOMO" and p["method"] == mname and not p["underdetermined"]]
        e = np.array([p["err_pct"] for p in pp]) / 100
        trucks = sorted(set(p["config_id"] for p in pp))
        ok = sum(1 for c in trucks if max(abs(p["err_pct"]) for p in pp if p["config_id"] == c) <= 100 * TARGET)
        summ.append(dict(view="LOMO_dof>=1", method=mname, trucks_all_within_5pct=ok, predictions=len(e),
                         share_within_5pct=round(float(np.mean(np.abs(e) <= TARGET)), 3), share_too_low=round(float(np.mean(e < 0)), 3),
                         largest_under_pct=round(100 * float(e.min()), 2), largest_over_pct=round(100 * float(e.max()), 2),
                         median_abs_err_pct=round(100 * float(np.median(np.abs(e))), 2), mean_abs_err_urban_pct="",
                         worst_truck_pct=round(100 * float(np.max(np.abs(e))), 2), dof_min=""))
    # ---- difference between methods per prediction (|C - L4| in % of certified)
    diffs = []
    for view in ("LORO", "LOMO"):
        for cid in TEN:
            rr = by[cid]
            for i, r in enumerate(rr):
                pc = store[(cid, "C", view)][i]["pred"]
                for lm in ("L4a", "L4b"):
                    pl = store[(cid, lm, view)][i]["pred"]
                    diffs.append(dict(view=view, config_id=cid, mission=r["mission"], payload_kg=round(r["payload"]), pair="C-" + lm,
                                      abs_diff_pct_of_cert=round(100 * abs(pc - pl) / r["cert"], 2)))
    for view in ("LORO", "LOMO"):
        for pair in ("C-L4a", "C-L4b"):
            d = np.array([x["abs_diff_pct_of_cert"] for x in diffs if x["view"] == view and x["pair"] == pair])
            for s in summ:
                if s["view"] == view and s["method"] == pair.split("-")[1]:
                    s["median_abs_diff_vs_C_pct"] = round(float(np.median(d)), 2)
                    s["max_abs_diff_vs_C_pct"] = round(float(np.max(d)), 2)
    for s in summ:
        s.setdefault("median_abs_diff_vs_C_pct", ""); s.setdefault("max_abs_diff_vs_C_pct", "")

    # ---- full fits, plausibility
    fitted, plaus = [], []
    noload = {r["chain"]: r for r in csv.DictReader(open(os.path.join(HERE, "part2_noload_by_chain.csv")))}
    nl_mean = [float(r["noload_mean_frac"]) for r in noload.values()]
    thetas = {}
    for cid, mname, full_name, th, rms in full:
        rr = by[cid]; thetas[(cid, mname)] = th
        k = len(th)
        row = dict(config_id=cid, truck=NAMES[cid], method=full_name, n_results=len(rr), n_fitted=k, dof=len(rr) - k,
                   fit_rms_pct=round(100 * rms, 3), values=";".join("%s=%.5g" % (n, v) for n, v in zip(make(mname, rr[0]).names, th)))
        if k:
            lo, hi = make(mname, rr[0]).bounds_for(rr[0])
            hits = [n for n, v, l, h in zip(make(mname, rr[0]).names, th, lo, hi)
                    if min(abs(v - l), abs(h - v)) <= 1e-3 * (h - l)]          # within 0.1 % of the bound width
        else:
            hits = []
        row["at_bound"] = ";".join(hits)
        fitted.append(row)
        if mname in ("L4a", "L4b"):
            P_r = rr[0]["rated_kw"] * 1000.0
            a, b = th[0], th[1]
            c = th[2] if mname == "L4b" else 0.0
            v_mean = float(np.mean(np.concatenate([r["v_avg"][r["engaged"]] for r in rr])))
            p = dict(config_id=cid, truck=NAMES[cid], method=mname, rated_kW=P_r / 1e3, a_over_Prated=round(a / P_r, 4),
                     vecto_noload_mean_frac_range="%.3f-%.3f" % (min(nl_mean), max(nl_mean)), b_times_Prated=round(b * P_r, 4),
                     c_over_Prated_per_mps=round(c / P_r, 6), v_mean_mps=round(v_mean, 2))
            for x in X_POINTS:
                P = x * P_r
                p["eta_drive_x%.2f" % x] = round(P / (P + a + c * v_mean + b * P * P), 4)
                p["eta_regen_x%.2f" % x] = round((P - a - c * v_mean - b * P * P) / P, 4)
            if rr[0]["airdrag_measured"]:
                p["cdxa_declared_fit"] = round(th[-1], 3); p["cdxa_range"] = rr[0]["cdxa_range"]
            else:
                p["cdxa_declared_fit"] = ""; p["cdxa_range"] = rr[0]["cdxa_range"] + " (standard)"
            plaus.append(p)
        elif mname == "C":
            P_r = rr[0]["rated_kw"] * 1000.0
            plaus.append(dict(config_id=cid, truck=NAMES[cid], method="C", rated_kW=P_r / 1e3, a_over_Prated="",
                              vecto_noload_mean_frac_range="", b_times_Prated="", c_over_Prated_per_mps="", v_mean_mps="",
                              **{"eta_drive_x%.2f" % x: round(th[0], 4) for x in X_POINTS},
                              **{"eta_regen_x%.2f" % x: round(th[1], 4) for x in X_POINTS},
                              cdxa_declared_fit=(round(th[-1], 3) if rr[0]["airdrag_measured"] else ""),
                              cdxa_range=rr[0]["cdxa_range"] + ("" if rr[0]["airdrag_measured"] else " (standard)")))
    # ---- unseen mission (Municipal without PTO), full-data fits
    unseen = []
    ur = unseen_records()
    for cid in TEN:
        u = ur[cid]
        if isinstance(u, str):
            unseen.append(dict(config_id=cid, truck=NAMES[cid], mission="Municipal Utility (no PTO)", payload_kg="",
                               A_kwh_km="", C_kwh_km="", L4a_kwh_km="", L4b_kwh_km="", C_vs_L4a_pct="", C_vs_L4b_pct="", note=u))
            continue
        for r in u:
            vals = {m: make(m, by[cid][0]).predict(r, thetas[(cid, m)]) for m in METHODS}
            unseen.append(dict(config_id=cid, truck=NAMES[cid], mission="Municipal Utility (no PTO)", payload_kg=round(r["payload"]),
                               A_kwh_km=round(vals["A"], 4), C_kwh_km=round(vals["C"], 4), L4a_kwh_km=round(vals["L4a"], 4),
                               L4b_kwh_km=round(vals["L4b"], 4), C_vs_L4a_pct=round(100 * (vals["L4a"] / vals["C"] - 1), 2),
                               C_vs_L4b_pct=round(100 * (vals["L4b"] / vals["C"] - 1), 2),
                               note="certified Municipal (with PTO) = %.3f, not comparable" % r["cert"]))
    files += [write(os.path.join(HERE, "part3_predictions.csv"), preds),
              write(os.path.join(HERE, "part3_worst_per_truck.csv"), worst),
              write(os.path.join(HERE, "part3_summary.csv"), summ),
              write(os.path.join(HERE, "part3_method_differences.csv"), diffs),
              write(os.path.join(HERE, "part3_fitted_values.csv"), fitted),
              write(os.path.join(HERE, "part3_plausibility.csv"), plaus),
              write(os.path.join(HERE, "part3_unseen_mission.csv"), unseen),
              write(os.path.join(HERE, "part3_missions_per_truck.csv"),
                    [dict(config_id=c, truck=NAMES[c], missions="; ".join("%s %d kg" % (r["mission"], round(r["payload"])) for r in by[c]))
                     for c in TEN])]
    files += plots(preds, worst)
    for s in summ:
        print("%-4s %-4s trucks ok %d/10  within5 %.2f  too low %.2f  worst under %+.1f%%  worst truck %.1f%%  |C-L| median %s max %s" % (
            s["view"], s["method"], s["trucks_all_within_5pct"], s["share_within_5pct"], s["share_too_low"],
            s["largest_under_pct"], s["worst_truck_pct"], s["median_abs_diff_vs_C_pct"], s["max_abs_diff_vs_C_pct"]))
    for f in files:
        print("wrote", f)
    print("fits wall %.0f s, total %.0f s" % (t_fit, time.time() - t_all))


def plots(preds, worst):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    files = []
    for view in ("LORO", "LOMO"):
        fig, ax = plt.subplots(figsize=(12, 4.8))
        wdt = 0.2
        for j, m in enumerate(METHODS):
            vals = [next(x["worst_abs_err_pct"] for x in worst if x["config_id"] == c and x["method"] == m and x["view"] == view) for c in TEN]
            ax.bar(np.arange(10) + j * wdt, vals, wdt, label=m)
        ax.axhline(5, color="k", ls="--", lw=1)
        ax.set_xticks(np.arange(10) + 0.3); ax.set_xticklabels([NAMES[c] for c in TEN], rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("worst |error| [%]"); ax.legend(); ax.grid(axis="y", alpha=0.3)
        ax.set_title("Worst %s error per truck (calibration on VECTO certified results, not validation)" % view)
        fig.tight_layout(); f = os.path.join(HERE, "part3_worst_per_truck_%s.png" % view); fig.savefig(f, dpi=110); plt.close(fig); files.append(f)
    fig, axs = plt.subplots(1, 4, figsize=(16, 4), sharex=True, sharey=True)
    for a, m in zip(axs, METHODS):
        rr = [p for p in preds if p["method"] == m and p["view"] == "LORO"]
        a.scatter([p["certified_kwh_km"] for p in rr], [p["predicted_kwh_km"] for p in rr], s=10,
                  c=["tab:red" if p["mission"] == "Urban Delivery" else "tab:blue" for p in rr])
        lim = [0.4, 2.4]; a.plot(lim, lim, "k-", lw=0.8); a.plot(lim, [l * 1.05 for l in lim], "k:"); a.plot(lim, [l * 0.95 for l in lim], "k:")
        a.set_title(m + " (LORO)"); a.set_xlabel("certified kWh/km"); a.grid(alpha=0.3)
    axs[0].set_ylabel("predicted kWh/km (red = Urban)")
    fig.tight_layout(); f = os.path.join(HERE, "part3_parity.png"); fig.savefig(f, dpi=110); plt.close(fig); files.append(f)
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ms = ["Urban Delivery", "Regional Delivery", "Long Haul", "Construction", "Regional Delivery EMS", "Long Haul EMS"]
    data, labels = [], []
    for m in METHODS:
        for s in ms:
            data.append([p["err_pct"] for p in preds if p["method"] == m and p["view"] == "LORO" and p["mission"] == s] or [np.nan])
            labels.append("%s\n%s" % (m, s.replace(" Delivery", "")))
    ax.boxplot(data, tick_labels=labels); ax.axhline(0, color="k", lw=0.8); ax.axhline(5, color="k", ls=":"); ax.axhline(-5, color="k", ls=":")
    ax.tick_params(axis="x", labelsize=6); ax.set_ylabel("LORO error [%]"); ax.set_title("Error by mission")
    fig.tight_layout(); f = os.path.join(HERE, "part3_error_by_mission.png"); fig.savefig(f, dpi=110); plt.close(fig); files.append(f)
    return files


if __name__ == "__main__":
    main()
