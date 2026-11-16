"""Part 1.2 / 1.3 / 1.4a: DAF refits.

For every DAF group 5 config (23) fit method C (PR #38 form, same bounds, range_mid) four ways:
  V0  C as in PR #38 (eta_d, eta_r, F0, CdxA in range)                     -> must reproduce g5_fits.csv
  V1  F0 fixed at 0 N          (eta_d, eta_r, CdxA fitted)
  V2  F0 fixed at 1600 N       (eta_d, eta_r, CdxA fitted). 1600 N is read off the PR #38 DAF fits (median F0 of the
                               DAF fits with F0 > 800 N), it is NOT from a source.   [CALC]
  V3  C fitted without the Construction rows (only configs that have Construction): does F0 jump?
And the V3 test on all 254 group 5 configs, to see whether it is DAF-specific.

Cluster definition (ASSUMPTION): HIGH-F0 = PR #38 C fit F0 >= 800 N (half of 1600 N); LOW-F0 otherwise.

Outputs: p1_daf_refits.csv, p1_daf_mission_error.csv, p1_construction_drop_all.csv
"""
import os
import sys
from collections import defaultdict

import numpy as np

import lib_g5 as L

HN, ML, P3 = L.HN, L.ML, L.P3
HERE = L.HERE
F_HIGH = 1600.0
THRESH = 800.0
MISSIONS = HN.MISSIONS_BASE


class CFixed(ML.MethodCv2):
    """Method C with F0 held at a constant: free eta_d, eta_r."""
    names = ("eta", "regen")

    def __init__(self, F0):
        self.F0 = float(F0)
        self.name = "C[F0=%g]" % F0
        self.bounds = ((ML.BND_ETA[0], ML.BND_REGEN[0]), (ML.BND_ETA[1], ML.BND_REGEN[1]))

    def starts_for(self, rec):
        return [(0.9, 0.8), (0.7, 0.6), (0.95, 0.95)]

    def bounds_for(self, rec):
        return self.bounds

    def predict(self, rec, theta):
        eta, reg = theta
        return ML.kwh_per_km(rec, ML.traction_power(rec, eta, reg, F0=self.F0))


def make(variant, rec):
    base = {"V0": ML.MethodCv2(), "V1": CFixed(0.0), "V2": CFixed(F_HIGH), "V3": ML.MethodCv2()}[variant]
    return ML.WithCdxARange(base) if rec["airdrag_measured"] else base


def at_bound(m, th, rec):
    lo, hi = m.bounds_for(rec)
    return ";".join(n for n, v, a, b in zip(m.names, th, lo, hi) if min(abs(v - a), abs(b - v)) <= 1e-3 * (b - a))


def fit_one(variant, rr):
    m = make(variant, rr[0])
    use = [r for r in rr if not (variant == "V3" and r["mission"] == "Construction")]
    th, rms = ML.fit_v2(m, use)
    err = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
    return m, th, err, use


def name_val(m, th):
    d = {}
    for n, v in zip(m.names, th):
        d[{"eta": "eta_d", "regen": "eta_r", "F0": "F0_N", "cdxa_declared": "cdxa_declared_m2"}[n]] = v
    return d


def main():
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    ft = L.fits_c_l4b()["C"]
    daf = [c for c in ids if cfg[c]["Make_clean"] == "DAF"]
    rows, mrows = [], []
    for cid in daf:
        rr = by[cid]
        has_con = any(r["mission"] == "Construction" for r in rr)
        pr38 = ft[cid]["values"][2]
        cluster = "HIGH_F0" if pr38 >= THRESH else "LOW_F0"
        for variant in ("V0", "V1", "V2", "V3"):
            if variant == "V3" and not has_con:
                continue
            m, th, err, use = fit_one(variant, rr)
            d = name_val(m, th)
            row = dict(config_id=cid, model=cfg[cid]["Model"], cluster=cluster, has_construction=has_con, variant=variant,
                       n_fit_results=len(use), at_bound=at_bound(m, th, rr[0]),
                       eta_d=d.get("eta_d", ""), eta_r=d.get("eta_r", ""),
                       F0_N=d.get("F0_N", {"V1": 0.0, "V2": F_HIGH}.get(variant, "")),
                       cdxa_declared_m2=d.get("cdxa_declared_m2", ""),
                       mean_abs_err_pct_all_results=round(100 * float(np.mean(np.abs(err))), 3),
                       worst_abs_err_pct_all_results=round(100 * float(np.max(np.abs(err))), 3),
                       mean_err_pct_all_results=round(100 * float(np.mean(err)), 3))
            for ms in MISSIONS:
                sel = [i for i, r in enumerate(rr) if r["mission"] == ms]
                row["err_" + ms.replace(" ", "_")] = round(100 * float(np.mean(err[sel])), 3) if sel else ""
            rows.append(row)
            for i, r in enumerate(rr):
                mrows.append(dict(config_id=cid, cluster=cluster, variant=variant, mission=r["mission"], payload_kg=round(r["payload"]),
                                  err_pct=round(100 * float(err[i]), 3), in_fit=bool(r in use)))
    # reproduction check of V0 against PR #38
    mx = 0.0
    for r in rows:
        if r["variant"] == "V0":
            f = ft[r["config_id"]]["values"]
            mx = max(mx, abs(float(r["F0_N"]) - f[2]), abs(float(r["eta_d"]) - f[0]) * 1000)
    print("V0 vs PR #38 g5_fits.csv: max |dF0| or 1000*|d eta_d| = %.5f" % mx)
    L.write(os.path.join(HERE, "p1_daf_refits.csv"), rows)

    # --- per-mission error by cluster and variant (mean error, mean absolute error)
    agg = defaultdict(list)
    for r in mrows:
        agg[(r["cluster"], r["variant"], r["mission"])].append(r["err_pct"])
    out = []
    for (cl, v, ms), e in sorted(agg.items()):
        e = np.array(e)
        out.append(dict(cluster=cl, variant=v, mission=ms, n_results=len(e), mean_err_pct=round(float(e.mean()), 3),
                        mean_abs_err_pct=round(float(np.abs(e).mean()), 3), worst_abs_err_pct=round(float(np.abs(e).max()), 3)))
    L.write(os.path.join(HERE, "p1_daf_mission_error.csv"), out)
    L.write(os.path.join(HERE, "p1_daf_mission_error_by_result.csv"), mrows)

    # --- V3 on all 254 configs: does dropping Construction send F0 high, and for whom?
    allrows = []
    for cid in ids:
        rr = by[cid]
        if not any(r["mission"] == "Construction" for r in rr):
            continue
        m0, th0, e0, _ = fit_one("V0", rr)
        m3, th3, e3, _ = fit_one("V3", rr)
        d0, d3 = name_val(m0, th0), name_val(m3, th3)
        allrows.append(dict(config_id=cid, make=cfg[cid]["Make_clean"], model=cfg[cid]["Model"],
                            sim_version_min=cfg[cid]["vecto_version_min"],
                            F0_with=round(d0["F0_N"], 2), F0_without=round(d3["F0_N"], 2),
                            eta_d_with=round(d0["eta_d"], 4), eta_d_without=round(d3["eta_d"], 4),
                            cdxa_with=round(d0.get("cdxa_declared_m2", float("nan")), 4),
                            cdxa_without=round(d3.get("cdxa_declared_m2", float("nan")), 4),
                            err_construction_pct_when_dropped=round(100 * float(np.mean([e3[i] for i, r in enumerate(rr) if r["mission"] == "Construction"])), 3)))
    L.write(os.path.join(HERE, "p1_construction_drop_all.csv"), allrows)
    by_make = defaultdict(list)
    for r in allrows:
        by_make[r["make"]].append(r)
    for mk, x in sorted(by_make.items()):
        a = np.array([r["F0_with"] for r in x]); b = np.array([r["F0_without"] for r in x])
        print("%-14s n=%3d  F0 with Constr median %7.1f | without median %7.1f | share F0>=800 without: %.2f | mean Constr err when dropped %+.1f%%" % (
            mk, len(x), np.median(a), np.median(b), np.mean(b >= THRESH), np.mean([r["err_construction_pct_when_dropped"] for r in x])))


if __name__ == "__main__":
    main()
