"""Builds ../vecto-engine-method-c-2026-11.md from the CSV/JSON results in this folder (no new VECTO run)."""
import csv
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def rd(n):
    return list(csv.DictReader(l for l in open(os.path.join(HERE, n), encoding="utf-8") if not l.startswith("#")))


def md(rows, cols, heads):
    o = ["| " + " | ".join(heads) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(cols))) + "|"]
    for r in rows:
        o.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(o)


def sg(x, n=1):
    return (("%+." + str(n) + "f") % float(x))


def main():
    T = {}
    p0 = rd("part0_e2_reproduction.csv")
    T["P0"] = md([dict(c=r["cycle"], l=r["loading"], t=r["terminal_kwh_km"], f=r["EC_el_final_kwh_km"], b=r["bob_22_oct_kwh_km"] or "", d=(sg(r["diff_pct"], 2) + " %") if r["diff_pct"] else "") for r in p0],
                 ["c", "l", "t", "f", "b", "d"], ["cycle", "loading", "terminal kWh/km (VECTO fork 4.3.4-DEV)", "EC_el_final kWh/km", "Bob 22 Oct (5.1.6-RC)", "difference"])
    tm = rd("part0_timing.csv")
    T["TIM"] = md(tm, ["mode", "command", "runs", "wall_s", "cpu_s"], ["mode", "command", "runs", "wall s", "CPU s"])
    inp = rd("p1_inputs_table.csv")
    T["INP"] = md(inp, ["truck", "input", "value", "source", "tag"], ["truck", "input", "value", "source", "tag"])
    refs = rd("p1_vecto_refs.csv")
    T["REFS"] = md(refs, ["rule", "file", "line", "use_in_this_study"], ["rule", "VECTO file (fork b8d6126)", "line", "use here"])
    bal = rd("p1_balance.csv")
    T["BAL"] = md([dict(t=r["truck"], m=r["mission"], p=r["payload_kg"], term=r["vsum_terminal_kwh_km"], res=r["balance_residual_kwh_km"],
                        ie=r["vmod_E_IEPC_el"], wi=r["vmod_E_wheel_in"], dl=r["lossless_residual_IEPC_el_minus_wheel_in"], br=r["vmod_E_brake_loss"],
                        au=r["vmod_E_aux"], ha=r["harness_E_aux"]) for r in bal],
                  ["t", "m", "p", "term", "res", "ie", "wi", "dl", "br", "au", "ha"],
                  ["truck", "mission", "payload kg", "terminal kWh/km (vsum)", "terminal - (IEPC el + aux + cables)", "IEPC electric", "wheel in", "IEPC el - wheel in", "mechanical brake loss", "aux VECTO", "aux harness"])
    # engine difference at the wheel (eta = 1, F0 = 0)
    g = {}
    for r in bal:
        k = (r["truck"], r["mission"].split()[0])
        g.setdefault(k, []).append((float(r["vmod_E_wheel_in"]) / float(r["harness_E_wheel_net"]) - 1, float(r["vmod_E_wheel_drive"]) / float(r["harness_E_wheel_drive"]) - 1,
                                    float(r["vmod_E_wheel_regen_side"]) / float(r["harness_E_wheel_regen_side"]) - 1))
    T["WHEEL"] = md([dict(t=k[0], m=k[1], n=len(v), net=sg(100 * np.mean([x[0] for x in v])), lo=sg(100 * min(x[0] for x in v)), hi=sg(100 * max(x[0] for x in v)),
                          dr=sg(100 * np.mean([x[1] for x in v])), rg=sg(100 * np.mean([x[2] for x in v]))) for k, v in sorted(g.items())],
                    ["t", "m", "n", "net", "lo", "hi", "dr", "rg"], ["truck", "mission", "results", "net wheel energy VECTO vs HDEV, mean %", "min %", "max %", "drive side %", "regen side (magnitude) %"])
    fv = rd("p2_fitted_values.csv")
    T["FIT"] = md([dict(t=r["truck"] + " " + r["name"], e=r["engine"], k=r["n_fitted"], ed=r["eta_d"], er=r["eta_r"], f0=r["F0_N"], cd=r.get("cdxa_declared_m2", "") or "-", rms=r["rms_pct"], b=r["at_bound"] or "none") for r in fv],
                  ["t", "e", "k", "ed", "er", "f0", "cd", "rms", "b"], ["truck", "engine", "values fitted", "eta_d", "eta_r", "F0 N", "CdxA m2", "rms error on all results %", "at a bound"])
    pr = rd("p2_per_result.csv")
    T["PER"] = md([dict(t=r["truck"], m=r["mission"], p=r["payload_kg"], c=r["certified"], hp=r["HDEV_hide_one"], he=sg(r["HDEV_hide_one_err_pct"], 2), vp=r["VECTO_hide_one"], ve=sg(r["VECTO_hide_one_err_pct"], 2),
                        hfe=sg(r["HDEV_fit_all_err_pct"], 2), vfe=sg(r["VECTO_fit_all_err_pct"], 2)) for r in pr],
                  ["t", "m", "p", "c", "hp", "he", "vp", "ve", "hfe", "vfe"],
                  ["truck", "mission", "payload kg", "certified kWh/km", "HDEV hide-one pred", "HDEV err %", "VECTO hide-one pred", "VECTO err %", "HDEV err % (fit on all)", "VECTO err % (fit on all)"])
    sm = rd("p3_summary.csv")
    T["SUM"] = md([dict(t=r["truck"], v=r["view"], e=r["engine"], me=sg(r["mean_err_pct"], 2), ma=r["mean_abs_err_pct"], w=r["worst_abs_err_pct"], ua=r["urban_mean_abs_err_pct"], uw=r["urban_worst_abs_err_pct"],
                        w5=int(round(100 * float(r["share_within_5pct"]))), lo=int(round(100 * float(r["share_too_low"])))) for r in sm],
                  ["t", "v", "e", "me", "ma", "w", "ua", "uw", "w5", "lo"],
                  ["truck", "test", "engine", "mean error %", "mean abs %", "worst abs %", "Urban mean abs %", "Urban worst abs %", "within 5 % (share %)", "too low (share %)"])
    sh = rd("p3_share_removed_by_vecto_engine.csv")
    T["SHARE"] = md([dict(t=r["truck"], v=r["view"], m=r["metric"], a=r["HDEV_engine_pct"], b=r["VECTO_engine_pct"], s=r["share_that_disappears_pct"]) for r in sh],
                    ["t", "v", "m", "a", "b", "s"], ["truck", "test", "metric", "HDEV engine %", "VECTO engine %", "share that disappears %"])
    fx = rd("p2_engine_at_fixed_theta.csv")
    rows = []
    for ts in ("theta_HDEV_fit", "theta_VECTO_fit"):
        for t in ("C0091", "C0059"):
            for ms in ("Urban", "Regional", "Long", "Constr", "ALL"):
                y = [float(r["VECTO_minus_HDEV_pct"]) for r in fx if r["theta_set"] == ts and r["truck"] == t and (ms == "ALL" or r["mission"].startswith(ms))]
                if y:
                    rows.append(dict(ts=ts.replace("theta_", "").replace("_fit", " fit values"), t=t, m=ms if ms != "ALL" else "all results", n=len(y), mean=sg(np.mean(y), 2), lo=sg(min(y), 2), hi=sg(max(y), 2)))
    T["FIXED"] = md(rows, ["ts", "t", "m", "n", "mean", "lo", "hi"], ["method C values", "truck", "missions", "results", "VECTO minus HDEV, mean %", "min %", "max %"])
    cl = rd("p3_certified_vs_lossless.csv")
    T["LL"] = md([dict(t=r["truck"], m=r["mission"], p=r["payload_kg"], c=r["certified"], l=r["VECTO_lossless_wheel_plus_aux"], ra=r["certified_over_lossless"], ex=r["extra_kwh_km"], v=r["avg_speed_kmh"],
                       pe=r["extra_power_kW_at_avg_speed"], er=sg(r["VECTO_fit_err_pct"], 2)) for r in cl],
                 ["t", "m", "p", "c", "l", "ra", "ex", "v", "pe", "er"],
                 ["truck", "mission", "payload kg", "certified kWh/km", "VECTO lossless (eta 1, F0 0) kWh/km", "certified / lossless", "extra kWh/km", "average speed km/h", "extra x speed kW", "VECTO C fit error %"])
    rl = rd("p3_relaxed_etar.csv")
    T["RELAX"] = md([dict(e=r["engine"], ed=r["eta_d"], er=r["eta_r"], f0=r["F0_N"], rms=r.get("rms_pct", ""), er2=r["errors_pct"]) for r in rl], ["e", "ed", "er", "f0", "rms", "er2"],
                    ["engine / run", "eta_d", "eta_r", "F0 N", "rms %", "errors on the 4 results % (Reg 333, Reg 1664, Urb 333, Urb 1664)"])
    f0 = rd("p2_f0_construction.csv")
    rows = []
    for t in ("C0091", "C0059"):
        for ts in ("theta_HDEV_fit", "theta_VECTO_fit"):
            y = [float(r["difference_pct"]) for r in f0 if r["truck"] == t and r["theta_set"] == ts]
            rows.append(dict(t=t, ts=ts.replace("theta_", "").replace("_fit", " fit values"), mean=sg(np.mean(y), 2), lo=sg(min(y), 2), hi=sg(max(y), 2)))
    T["F0"] = md(rows, ["t", "ts", "mean", "lo", "hi"], ["truck", "method C values", "F0 inside the IEPC map vs F0 in the axle loss map, mean %", "min %", "max %"])
    fn = rd("p2_final_vs_terminal.csv")
    T["FINAL"] = md([dict(t=r["truck"], m=r["mission"], p=r["payload_kg"], c=r["certified"], te=r["terminal_over_0p995"], fi=r["EC_el_final_over_0p995_generic_battery"], d=sg(r["final_over_terminal_pct"]),
                          et=sg(r["err_terminal_pct"], 2), ef=sg(r["err_final_pct"], 2)) for r in fn],
                    ["t", "m", "p", "c", "te", "fi", "d", "et", "ef"],
                    ["truck", "mission", "payload kg", "certified kWh/km", "terminal / 0.995", "EC_el_final / 0.995 (generic battery)", "final vs terminal %", "error terminal basis %", "error final basis %"])
    s = open(os.path.join(HERE, "report_template.md"), encoding="utf-8").read()
    for k, v in T.items():
        s = s.replace("{{%s}}" % k, v)
    assert "{{" not in s, s[s.index("{{"):s.index("{{") + 40]
    out = os.path.abspath(os.path.join(HERE, "..", "vecto-engine-method-c-2026-11.md"))
    open(out, "w", encoding="utf-8").write(s)
    print("wrote", out, len(s.splitlines()), "lines")


if __name__ == "__main__":
    main()
