"""Builds the markdown tables of the report from the CSV outputs (no number is typed by hand). Output: report_tables.json"""
import json
import os

import lib_g5 as L

HERE = L.HERE


def md(rows, cols, heads=None):
    heads = heads or cols
    out = ["| " + " | ".join(heads) + " |", "|" + "|".join("---:" if i else "---" for i in range(len(cols))) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def rd(name):
    return L.read(os.path.join(HERE, name))


def f(x, n=1, sign=False):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    return (("%+." if sign else "%.") + str(n) + "f") % v


def main():
    T = {}
    summ = {r["method"]: r for r in rd("p2_g5_summary.csv")}
    boot = {(r["universe"], r["method"]): r for r in rd("final_bootstrap.csv")}
    order = ["C", "L4b", "L1[S3b_IEPC_3speed]", "L1b[S3b_IEPC_3speed]", "L1[arch]", "L1b[arch]", "L1[S3a_IEPC_1speed]", "L1b[S3a_IEPC_1speed]",
             "L1[S2_busIEPC_PSM]", "L1b[S2_busIEPC_PSM]", "L1[S2_busIEPC_ASM]", "L1b[S2_busIEPC_ASM]"]
    rows = []
    for m in order:
        s = summ[m]
        b = boot[("all 38 models", m + " [CdxA own]")]
        rows.append(dict(method=m, k=s["n_fitted_drivetrain_values"], ins=f(s["insample_mean_abs_err_pct"], 2), insw=f(s["insample_worst_abs_err_pct"], 1),
                         cb=f(s["class_p50_width_config_pp"], 1), mean=f(s["holdout_mean_of_model_mean_err_pct"], 2, True), p10=f(s["holdout_p10_pct"], 1, True),
                         p50=f(s["holdout_p50_pct"], 1, True), p90=f(s["holdout_p90_pct"], 1, True), w=f(s["holdout_width_pp"], 1),
                         ci="%s to %s" % (f(b["width_ci95_lo"], 1), f(b["width_ci95_hi"], 1)), wm=f(s["worst_model_mean_abs_err_pct"], 1),
                         wr=f(s["worst_single_result_abs_err_pct"], 1), low=f(100 * float(s["share_results_too_low"]), 0) + " %"))
    T["T1"] = md(rows, ["method", "k", "ins", "insw", "cb", "mean", "p10", "p50", "p90", "w", "ci", "wm", "wr", "low"],
                 ["method", "fitted values", "in-sample mean abs err %", "in-sample worst %", "class-P50 config width pp", "held-out mean %", "P10 %", "P50 %", "P90 %",
                  "**P90-P10 pp**", "95 % interval of width (bootstrap over models)", "worst model mean |err| %", "worst single result %", "results too low"])
    # without DAF
    sn = {r["method"]: r for r in rd("p2_g5_summary_without_daf.csv")}
    rows = []
    for m in ["C", "L4b", "L1[S3b_IEPC_3speed]", "L1b[S3b_IEPC_3speed]", "L1[arch]", "L1[S3a_IEPC_1speed]", "L1[S2_busIEPC_PSM]", "L1[S2_busIEPC_ASM]"]:
        a, b = summ[m], sn[m]
        rows.append(dict(method=m, cb_all=f(a["class_p50_width_config_pp"], 1), cb_no=f(b["class_p50_width_config_pp"], 1), w_all=f(a["holdout_width_pp"], 1),
                         w_no=f(b["holdout_width_pp"], 1), wm_all=f(a["worst_model_mean_abs_err_pct"], 1), wm_no=f(b["worst_model_mean_abs_err_pct"], 1),
                         wr_all=f(a["worst_single_result_abs_err_pct"], 1), wr_no=f(b["worst_single_result_abs_err_pct"], 1)))
    T["T3"] = md(rows, ["method", "cb_all", "cb_no", "w_all", "w_no", "wm_all", "wm_no", "wr_all", "wr_no"],
                 ["method", "class-P50 width, all 254 configs", "without DAF (231)", "held-out width, 38 models", "without DAF (32 models)", "worst model |mean err| %, all", "without DAF",
                  "worst single result %, all", "without DAF"])
    # PR #38 reproduction + DAF
    wd = rd("p1_without_daf.csv")
    T["T3b"] = md([dict(method=r["method"], case=r["case"], n=r["n_configs"], nm=r["n_models"], cb=f(r["class_band_width_pp"], 2), hw=f(r["holdout_width_pp"], 2),
                        wm=f(r["worst_model_mean_abs_pct"], 1), wr=f(r["worst_single_result_abs_pct"], 1)) for r in wd],
                  ["method", "case", "n", "nm", "cb", "hw", "wm", "wr"],
                  ["method", "case", "configs", "models", "class-band width pp (P90-P10 of config mean error)", "held-out-model width pp", "worst model mean |err| %", "worst single result %"])
    # Part 3 table
    p3 = rd("p3_summary.csv")
    rows = []
    for u in ("all 38 models", "without DAF (32 models)"):
        for r in p3:
            if r["universe"] != u:
                continue
            nm = r["method"]
            if nm.startswith("class-P50") and ("L1b" in nm or "L4b" in nm):
                continue
            key = (u, nm + (" [CdxA own]" if r["cdxa_for_target"].startswith("own") else (" (CdxA mid)" if r["cdxa_for_target"].startswith("middle") else "")))
            if u.startswith("all") and nm.startswith("class-P50"):
                bk = (u, nm.replace("class-P50 ", "") + " [CdxA own]") if r["cdxa_for_target"].startswith("own") else (u, nm + " (CdxA mid)")
            else:
                bk = key
            b = boot.get(bk) or boot.get((u, nm))
            ci = "%s to %s" % (f(b["width_ci95_lo"], 1), f(b["width_ci95_hi"], 1)) if b else ""
            rows.append(dict(u=u.replace(" models", "").replace("without DAF (32)", "no DAF (32)"), m=nm, c=r["cdxa_for_target"], w=f(r["width_p90_minus_p10_pp"], 1), ci=ci,
                             mean=f(r["mean_of_model_mean_err_pct"], 1, True), wm=f(r["worst_model_mean_abs_err_pct"], 1), wr=f(r["worst_single_result_abs_err_pct"], 1),
                             low=f(100 * float(r["share_results_too_low"]), 0) + " %"))
    T["T4"] = md(rows, ["u", "m", "c", "w", "ci", "mean", "wm", "wr", "low"],
                 ["models", "method", "CdxA of the target", "**P90-P10 pp**", "95 % interval", "mean of model mean err %", "worst model mean |err| %", "worst single result %", "results too low"])
    # ten trucks
    ten = rd("p2_ten_summary.csv")
    T["T5"] = md([dict(m=r["method"], k=r["n_fitted"], t=r["trucks_all_within_5pct"], w5=f(100 * float(r["share_within_5pct"]), 0) + " %", low=f(100 * float(r["share_too_low"]), 0) + " %",
                       mu=f(r["largest_under_pct"], 1, True), mo=f(r["largest_over_pct"], 1, True), med=f(r["median_abs_err_pct"], 2), wt=f(r["worst_truck_abs_err_pct"], 1),
                       mw=f(r["median_of_truck_worst_abs_err_pct"], 1)) for r in ten],
                  ["m", "k", "t", "w5", "low", "mu", "mo", "med", "wt", "mw"],
                  ["method (leave-one-result-out)", "fitted values", "trucks all within 5 %", "predictions within 5 %", "too low", "largest under %", "largest over %", "median abs err %", "worst truck %", "median of truck worst %"])
    # per make
    pm = rd("final_by_make_best_shape.csv")
    T["T6"] = md([dict(mk=r["make"], k=r["method"], nm=r["n_models"], nc=r["n_configs"], a=f(r["insample_MAE_S3a_IEPC_1speed"], 2), b=f(r["insample_MAE_S3b_IEPC_3speed"], 2),
                       p=f(r["insample_MAE_S2_busIEPC_PSM"], 2), s=f(r["insample_MAE_S2_busIEPC_ASM"], 2), bi=r["best_by_insample"], ha=f(r["holdout_absmean_S3a_IEPC_1speed"], 1),
                       hb=f(r["holdout_absmean_S3b_IEPC_3speed"], 1), hp=f(r["holdout_absmean_S2_busIEPC_PSM"], 1), hs=f(r["holdout_absmean_S2_busIEPC_ASM"], 1), bh=r["best_by_holdout"]) for r in pm],
                  ["mk", "k", "nm", "nc", "a", "b", "p", "s", "bi", "ha", "hb", "hp", "hs", "bh"],
                  ["make", "method", "models", "configs", "in-sample MAE % S3a", "S3b", "S2 PSM", "S2 ASM", "lowest in-sample", "held-out mean abs model err % S3a", "S3b", "S2 PSM", "S2 ASM", "lowest held-out"])
    # DAF tables
    lv = rd("p1_level_by_make_and_iepc_method.csv")
    T["T7"] = md([dict(mk=r["make"], me=r["iepc_method"], ck=r["iepc_certificate_kind"], n=r["n_results"], c=r["mean_certified_kwh_km"], e=r["mean_E_A_kwh_km"], ra=r["mean_ratio_cert_over_VA"],
                       rg="%s to %s" % (r["min_ratio"], r["max_ratio"]), m=r["mean_test_mass_kg"], eta=r["C_eta_d_mean"], f0=r["C_F0_N_mean"]) for r in lv],
                  ["mk", "me", "ck", "n", "c", "e", "ra", "rg", "m", "eta", "f0"],
                  ["make", "IEPC method (EEA)", "certificate", "results", "certified kWh/km", "harness E_A kWh/km", "certified / E_A", "range", "test mass kg", "C eta_d (mean)", "C F0 N (mean)"])
    dl = rd("p1_level_by_mission_daf.csv")
    T["T8"] = md([dict(g=r["daf_group"], m=r["mission"], n=r["n"], c=r["mean_certified_kwh_km"], e=r["mean_E_A_kwh_km"], ma=r["mean_test_mass_kg"], ra=r["ratio"]) for r in dl],
                 ["g", "m", "n", "c", "e", "ma", "ra"], ["DAF group", "mission (2,600 kg payload)", "results", "certified kWh/km", "E_A kWh/km", "test mass kg", "certified / E_A (or ratio SV / measured)"])
    dc = rd("p1_daf_level_by_config.csv")
    T["T9"] = md([dict(c=r["config_id"], mo=r["model"].strip(), me=r["iepc_method_vehicle_level"], dg=r["iepc_digest_first8"], v=r["sim_tool_version_min"], f0=r["C_F0_N"], e=r["C_eta_d"], ra=r["mean_cert_over_VA"])
                  for r in sorted(dc, key=lambda r: (r["iepc_method_vehicle_level"], r["iepc_digest_first8"], r["config_id"]))],
                 ["c", "mo", "me", "dg", "v", "f0", "e", "ra"], ["config", "model", "IEPC method", "IEPC digest (first 8)", "VECTO version", "C F0 N", "C eta_d", "certified / E_A"])
    me = rd("p1_daf_mission_error.csv")
    T["T10"] = md([dict(cl=r["cluster"], v={"V0": "free F0 (PR #38)", "V1": "F0 = 0", "V2": "F0 = 1600 N", "V3": "free F0, no Construction rows"}[r["variant"]], m=r["mission"], n=r["n_results"],
                        me=f(r["mean_err_pct"], 1, True), ma=f(r["mean_abs_err_pct"], 1), w=f(r["worst_abs_err_pct"], 1)) for r in me if r["variant"] in ("V0", "V1", "V2")],
                  ["cl", "v", "m", "n", "me", "ma", "w"], ["cluster", "C fit", "mission", "results", "mean err %", "mean abs err %", "worst abs err %"])
    ec = rd("p1_ecanter.csv")
    T["T11"] = md([dict(v={"V0": "free F0", "V1": "F0 = 0", "V2": "F0 = 1600 N"}[r["variant"]], e=r["eta_d"], f0=r["F0_N"], b=r["at_bound"], ma=r["mean_abs_err_pct"], w=r["worst_abs_err_pct"],
                        r1=r["err_Regional_Delivery_333_kg_pct"], r2=r["err_Regional_Delivery_1664_kg_pct"], u1=r["err_Urban_Delivery_333_kg_pct"], u2=r["err_Urban_Delivery_1664_kg_pct"]) for r in ec],
                  ["v", "e", "f0", "b", "ma", "w", "r1", "r2", "u1", "u2"], ["C fit of C0059", "eta_d", "F0 N", "at bound", "mean abs err %", "worst %", "Regional 333 kg %", "Regional 1664 kg %", "Urban 333 kg %", "Urban 1664 kg %"])
    dd = rd("final_daf_shape_diagnostic.csv")
    T["T12"] = md([dict(g=r["group"], n=r["n_configs"], m=r["method"], e=f(r["in_sample_mean_abs_err_pct"], 2)) for r in dd], ["g", "n", "m", "e"], ["DAF group", "configs", "method", "in-sample mean abs err %"])
    cd = rd("p1_construction_drop_all.csv")
    import numpy as np
    mk = {}
    for r in cd:
        mk.setdefault(r["make"], []).append(r)
    T["T13"] = md([dict(mk=k, n=len(v), a=f(np.median([float(x["F0_with"]) for x in v]), 0), b=f(np.median([float(x["F0_without"]) for x in v]), 0),
                        s=sum(float(x["F0_without"]) >= 800 for x in v)) for k, v in sorted(mk.items())], ["mk", "n", "a", "b", "s"],
                  ["make", "configs with Construction", "median F0 N, all missions", "median F0 N, Construction rows dropped", "configs with F0 >= 800 N after dropping"])
    json.dump(T, open(os.path.join(HERE, "report_tables.json"), "w"), indent=1)
    for k, v in T.items():
        print("=====", k)
        print(v)


if __name__ == "__main__":
    main()
