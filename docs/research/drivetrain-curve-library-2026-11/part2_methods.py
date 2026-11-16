"""PART 2 -- the methods C, L4a, L4b: bounds for the L4 coefficients from VECTO's generic maps, and one-truck timing.

L4 bounds are expressed as fractions of the rated power so they scale to each truck:
  a_max = a_frac * P_rated      a_frac = largest no-load electric power / P_rated of any VECTO generic chain at any
                                cycle speed (zero wheel torque, gear in, wheels turning)
  c_max = c_frac * P_rated      c_frac = largest slope of that no-load power against vehicle speed (least squares
                                P_noload = a0 + c0 * v over all cycle rows) / P_rated
  b_max = b_frac / P_rated      b_frac = largest electric loss per unit wheel power k_d = 1/eta - 1 in the top
                                driving load bins (x >= 0.6) of any VECTO shape (partA_shapes.csv); at x = 1,
                                b * P_rated^2 = k * P_rated (a = 0 taken, so this is an upper bound)
VECTO chains: S1 E2, S2 bus-generic IEPC (PSM/ASM), S3a/b/c GenericIEPC examples, S4 standard-value ASM
(shapes_lib.py / partA_shapes.py; all VECTO fork b8d6126 files).

Outputs: part2_L4_bounds.csv, part2_noload_by_chain.csv, part2_timing_one_truck.csv
"""
import csv
import os
import time

import numpy as np

import harness as HN
import methods_lib as ML
import shapes_lib as SL
import partA_shapes as PA

HERE = os.path.dirname(os.path.abspath(__file__))


def noload_by_chain():
    rows = []
    for ch in PA.all_chains():
        P, V = [], []
        for c in PA.CYCLES:
            vr = SL.e2_vehicle_rows(c, "reference")
            r0 = dict(vr)
            r0["P_wheel"] = np.where(vr["use"], 1e-3, 0.0)
            ev = ch.evaluate(r0)
            m = vr["use"] & (vr["v_avg"] > 0.5)
            P.append(ev["P_el"][m]); V.append(vr["v_avg"][m])
        P, V = np.concatenate(P), np.concatenate(V)
        A = np.c_[np.ones_like(V), V]
        a0, c0 = np.linalg.lstsq(A, P, rcond=None)[0]
        rows.append(dict(chain=ch.name, P_rated_kW=round(ch.P_rated_W / 1e3, 2),
                         noload_mean_frac=round(float(P.mean() / ch.P_rated_W), 5),
                         noload_max_frac=round(float(P.max() / ch.P_rated_W), 5),
                         fit_a0_frac=round(float(a0 / ch.P_rated_W), 5),
                         fit_c0_frac_per_mps=round(float(c0 / ch.P_rated_W), 6)))
    return rows


def top_load_k():
    out = {}
    for r in csv.DictReader(open(os.path.join(HERE, "partA_shapes.csv"))):
        if r["side"] == "drive" and float(r["x_lo"]) >= 0.6:
            k = 1.0 / float(r["eta"]) - 1.0
            out[r["shape"]] = max(out.get(r["shape"], 0.0), k)
    return out


def main():
    files = []
    nl = noload_by_chain()
    kt = top_load_k()
    for r in nl:
        r["top_load_k_drive"] = round(kt.get(r["chain"], float("nan")), 5)
    f = os.path.join(HERE, "part2_noload_by_chain.csv")
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(nl[0].keys())); w.writeheader(); w.writerows(nl)
    files.append(f)
    a_frac = max(r["noload_max_frac"] for r in nl)
    c_frac = max(r["fit_c0_frac_per_mps"] for r in nl)
    b_frac = max(kt.values())
    bounds = [dict(coef="a", unit="W", upper_bound="%.5f * P_rated" % a_frac, value_frac=a_frac,
                   source="max no-load P_el / P_rated over VECTO generic chains (part2_noload_by_chain.csv)"),
              dict(coef="b", unit="1/W", upper_bound="%.5f / P_rated" % b_frac, value_frac=b_frac,
                   source="max k_d = 1/eta-1 at x >= 0.6 over VECTO shapes (partA_shapes.csv)"),
              dict(coef="c", unit="W per m/s", upper_bound="%.6f * P_rated" % c_frac, value_frac=c_frac,
                   source="max slope of no-load P_el vs vehicle speed / P_rated over VECTO generic chains"),
              dict(coef="eta_d (C)", unit="-", upper_bound="0.5 .. 1.0", value_frac="", source="ASSUMPTION: job prompt bounds"),
              dict(coef="eta_r (C)", unit="-", upper_bound="0.3 .. 1.0", value_frac="", source="ASSUMPTION: job prompt bounds"),
              dict(coef="F0 (C)", unit="N", upper_bound="0 .. 3000", value_frac="", source="ASSUMPTION: job prompt bounds"),
              dict(coef="CdxA declared", unit="m2", upper_bound="[min, max) of the EEA range", value_frac="",
                   source="REG 2018/956 Annex I Part C; measured air drag only")]
    f = os.path.join(HERE, "part2_L4_bounds.csv")
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(bounds[0].keys())); w.writeheader(); w.writerows(bounds)
    files.append(f)
    # one-truck timing (rule 1: time one truck before the full loop)
    ML.set_l4_bounds(a_frac, b_frac, c_frac)
    HN.AIRDRAG_MODE = "range_mid"
    recs, _ = HN.load_or_build(["C0059", "C0091", "C0371", "C0116", "C0153", "C0218", "C0712", "C0206", "C0070", "C0001"], "ten", processes=8)
    rr = [r for r in recs if r["config_id"] == "C0116"]
    tim = []
    for m in (ML.MethodCv2(), ML.MethodL4a(), ML.MethodL4b()):
        m = ML.WithCdxARange(m)
        t0 = time.process_time()
        ML.loo_v2(m, rr)
        dt = time.process_time() - t0
        tim.append(dict(method=m.name, truck="C0116", results=len(rr), loo_cpu_s=round(dt, 2),
                        extrapolated_10_trucks_x2_views_cpu_s=round(dt * 10 * 2, 1)))
        print("timing %s on C0116 (%d results): %.2f s CPU leave-one-out" % (m.name, len(rr), dt))
    f = os.path.join(HERE, "part2_timing_one_truck.csv")
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tim[0].keys())); w.writeheader(); w.writerows(tim)
    files.append(f)
    print("L4 bounds: a <= %.4f P_rated, b <= %.4f / P_rated, c <= %.6f P_rated per m/s" % (a_frac, b_frac, c_frac))
    for f in files:
        print("wrote", f)


if __name__ == "__main__":
    main()
