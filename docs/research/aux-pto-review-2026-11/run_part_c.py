"""Part C: aux timing vs VECTO, row by row.

C1  what VECTO does, per driving state (from the six E2 .vmod files)
C2  HDEV's current rules (Appendix 1.4) applied to the SAME VECTO rows (driver not involved)
C3  rule variants (a)-(d), one at a time
C4  HDEV's own driver rows (notebook driver_model, E2 reference set-up, thresholds in m/s)

Run:  python run_part_c.py     (VECTO_SRC defaults to /projects/sandbox/vecto-src)
Deterministic; writes CSVs and one graph into this folder.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _rows import read_vmod, read_vdri, run_driver_e2, DRIVER_ACTION, REPO  # noqa: E402
import reference_copy as RC  # noqa: E402

CASES = [("RegionalDelivery", "ReferenceLoad"), ("RegionalDelivery", "LowLoading"),
         ("UrbanDelivery", "ReferenceLoad"), ("UrbanDelivery", "LowLoading"),
         ("LongHaul", "ReferenceLoad"), ("LongHaul", "LowLoading")]
AUXCOLS = {"ES": "P_aux_ES_el [kW]", "HVAC": "P_aux_AC_el [kW]", "PS": "P_aux_PS_el [kW]",
           "SP": "P_aux_STP_el [kW]", "COND": "P_aux_COND_el [kW]"}
V_NO_REGEN = 5 / 3.6          # Constants.cs 323 (5 km/h) as used by the notebook consumption_engine
WRITTEN = []


def out(name, df, **kw):
    p = os.path.join(HERE, name)
    df.to_csv(p, index=False, float_format="%.6f", **kw)
    WRITTEN.append(p)
    return p


def state_of(d):
    """VECTO driving state per row from DriverAction (Driver.cs 51-58) + acc."""
    da = d["DriverAction"].to_numpy()
    acc = d["acc [m/s^2]"].to_numpy()
    st = np.full(len(d), "other", dtype=object)
    st[da == 0] = "standing (Halt)"
    st[(da == 6) & (acc > 0.1)] = "accelerating (Accelerate, a>0.1)"
    st[(da == 6) & (np.abs(acc) <= 0.1)] = "cruising (Accelerate, |a|<=0.1)"
    st[(da == 6) & (acc < -0.1)] = "decelerating under power (Accelerate, a<-0.1)"
    st[da == 4] = "coasting (Coast)"
    st[da == 2] = "rolling (Roll)"
    st[da == -5] = "braking (Brake)"
    return st


def start_speed(d):
    """speed at the START of each 1 s row [m/s], reconstructed from the 1 Hz row average and acc (v_avg - a*dt/2).
    HDEV's V is the speed at the start of the step (force_engine docstring); VECTO's VehicleStopped uses PreviousState.Velocity."""
    v_avg = d["v_act [km/h]"].to_numpy() / 3.6
    acc = d["acc [m/s^2]"].to_numpy()
    v0 = np.maximum(v_avg - 0.5 * acc * d["dt [s]"].to_numpy(), 0.0)
    v0[v0 < 1e-6] = 0.0
    return v0


def hdev_mode_proxy(d, v0):
    """HDEV driver mode M (0 stop, 1 accelerate, 2 cruise, 3 coast, 4 brake) from VECTO DriverAction -- proxy only."""
    da = d["DriverAction"].to_numpy()
    acc = d["acc [m/s^2]"].to_numpy()
    M = np.zeros(len(d), dtype=int)
    M[(da == 6) & (acc > 0.1)] = 1
    M[(da == 6) & (acc <= 0.1)] = 2
    M[(da == 4) | (da == 2)] = 3
    M[da == -5] = 4
    return M


def kwh(w):
    return float(np.sum(w) / 3.6e6)


def part_c1_c2_c3():
    r1, r2, r2s, r3, r3m = [], [], [], [], []
    for cyc, load in CASES:
        d = read_vmod(cyc, load)
        n = len(d)
        st = state_of(d)
        w = {k: d[c].to_numpy() * 1000.0 for k, c in AUXCOLS.items()}          # W per row
        lvl = {k: float(np.max(w[k])) for k in w}
        em_off = d["EM_E2_off"].to_numpy()
        v0 = start_speed(d)
        M = hdev_mode_proxy(d, v0)
        # ---- C1: VECTO per state ----
        for s in sorted(set(st)):
            m = st == s
            row = dict(cycle=cyc, loading=load, state=s, seconds=int(m.sum()), EM_off_fraction=float(em_off[m].mean()))
            for k in ("SP", "COND"):
                row[f"{k}_on_fraction"] = float(w[k][m].mean() / lvl[k]) if lvl[k] > 0 else 0.0
                row[f"{k}_kWh"] = kwh(w[k][m])
            r1.append(row)
        # ---- C2: HDEV current rule on VECTO rows ----
        ES, PS, HV, SP, CD = lvl["ES"], lvl["PS"], lvl["HVAC"], lvl["SP"], lvl["COND"]
        zero = np.zeros(n)
        cur = RC.aux_row_variant("current", v0, np.zeros(n, bool), ES, PS, HV, SP, CD, 0.0, zero)
        parts = {
            "ES": np.full(n, ES), "HVAC": np.full(n, HV), "PS": np.full(n, PS),
            "SP": SP * (v0 > 0), "COND": CD * (v0 > 0),
        }
        for k in AUXCOLS:
            e_v, e_h = kwh(w[k]), kwh(parts[k])
            r2.append(dict(cycle=cyc, loading=load, aux=k, level_W=lvl[k], vecto_kWh=e_v, hdev_current_kWh=e_h,
                           diff_kWh=e_h - e_v, diff_pct=(e_h / e_v - 1) * 100 if e_v else np.nan))
            for s in sorted(set(st)):
                m = st == s
                dk = kwh(parts[k][m]) - kwh(w[k][m])
                if abs(dk) > 1e-9:
                    r2s.append(dict(cycle=cyc, loading=load, aux=k, state=s, seconds=int(m.sum()), diff_kWh=dk))
        e_v_tot = kwh(d["P_aux_el [kW]"].to_numpy() * 1000)
        r2.append(dict(cycle=cyc, loading=load, aux="TOTAL", level_W=np.nan, vecto_kWh=e_v_tot, hdev_current_kWh=kwh(cur),
                       diff_kWh=kwh(cur) - e_v_tot, diff_pct=(kwh(cur) / e_v_tot - 1) * 100))
        # ---- C3: variants; motor-off proxies ----
        proxies = {
            "P0_VECTO_EM_off_column_(fraction)": em_off,
            "P1_M in {0,3}": ((M == 0) | (M == 3)).astype(float),
            "P2_M in {0,3} or (M==4 and V<=v_no_regen)": ((M == 0) | (M == 3) | ((M == 4) & (v0 <= V_NO_REGEN))).astype(float),
            "P3_standing only (M==0)": (M == 0).astype(float),
        }
        for pn, po in proxies.items():
            r3m.append(dict(cycle=cyc, loading=load, proxy=pn, motor_off_seconds=float(po.sum()),
                            VECTO_EM_off_seconds=float(em_off.sum()), abs_second_by_second_mismatch_s=float(np.abs(po - em_off).sum()),
                            COND_kWh_if_used=kwh(CD * (1 - po)), COND_kWh_VECTO=kwh(w["COND"]),
                            COND_diff_kWh=kwh(CD * (1 - po)) - kwh(w["COND"])))
        best = "P2_M in {0,3} or (M==4 and V<=v_no_regen)"
        mo = proxies[best].astype(bool)
        variants = {
            "current (code of record)": dict(rule="current"),
            "(a) SP on when V>0.01 m/s": dict(rule="a", v_eps=0.01),
            f"(b) Cond only when motor not off [proxy {best}]": dict(rule="b", motor_off=mo),
            "(c) Cond also during stop PTO: no PTO in E2 runs, identical to (b)": dict(rule="c", motor_off=mo),
            "(a)+(b)+(c) together": dict(rule="a+b+c", motor_off=mo, v_eps=0.01),
            "(d) SP and Cond always on (conservative bound)": dict(rule="d"),
        }
        sp_v, cd_v, tot_v = kwh(w["SP"]), kwh(w["COND"]), e_v_tot
        for vn, kw in variants.items():
            tot = RC.aux_row_variant(kw["rule"], v0, np.zeros(n, bool), ES, PS, HV, SP, CD, 0.0, zero,
                                     motor_off=kw.get("motor_off"), v_eps=kw.get("v_eps", 0.01))
            sp_on = (v0 > kw.get("v_eps", 0.0)) if kw["rule"] in ("a", "a+b+c") else (v0 > 0)
            if kw["rule"] == "d":
                sp_on = np.ones(n, bool)
            cd_on = ((~kw["motor_off"]) if kw.get("motor_off") is not None else (v0 > 0))
            if kw["rule"] == "d":
                cd_on = np.ones(n, bool)
            r3.append(dict(cycle=cyc, loading=load, variant=vn, SP_kWh=kwh(SP * sp_on), COND_kWh=kwh(CD * cd_on),
                           total_aux_kWh=kwh(tot), VECTO_SP_kWh=sp_v, VECTO_COND_kWh=cd_v, VECTO_total_aux_kWh=tot_v,
                           SP_diff_kWh=kwh(SP * sp_on) - sp_v, COND_diff_kWh=kwh(CD * cd_on) - cd_v,
                           total_diff_kWh=kwh(tot) - tot_v, total_diff_pct=(kwh(tot) / tot_v - 1) * 100,
                           side=("conservative (>= VECTO)" if kwh(tot) >= tot_v - 1e-9 else "UNDER VECTO")))
    out("partC1_vmod_aux_by_state.csv", pd.DataFrame(r1))
    out("partC2_hdev_rules_on_vmod_rows.csv", pd.DataFrame(r2))
    out("partC2_diff_by_state.csv", pd.DataFrame(r2s))
    out("partC3_rule_variants.csv", pd.DataFrame(r3))
    out("partC3_motor_off_proxies.csv", pd.DataFrame(r3m))
    return pd.DataFrame(r2), pd.DataFrame(r3), pd.DataFrame(r3m)


def part_c4():
    rows = []
    for cyc, load in CASES:
        if cyc == "LongHaul":
            rows.append(dict(cycle=cyc, loading=load, status="BLOCKED: LongHaul is truck + trailer; trailer axle data, trailer mass and "
                             "trailer CdxA are not set up for the notebook driver (running it with the truck only is a named pitfall)"))
            continue
        d = read_vmod(cyc, load)
        cy = read_vdri(cyc)
        T, S, V, A, G, M = run_driver_e2(cy, load)
        n = len(T)
        aux_lv = {k: float(d[c].max() * 1000) for k, c in AUXCOLS.items()}
        ES, PS, HV, SP, CD = (aux_lv[k] for k in ("ES", "PS", "HVAC", "SP", "COND"))
        zero = np.zeros(n)
        tot = RC.aux_row_variant("current", V, np.zeros(n, bool), ES, PS, HV, SP, CD, 0.0, zero)
        parts = {"ES": np.full(n, ES), "HVAC": np.full(n, HV), "PS": np.full(n, PS), "SP": SP * (V > 0), "COND": CD * (V > 0)}
        for k in AUXCOLS:
            e_v = kwh(d[AUXCOLS[k]].to_numpy() * 1000)
            rows.append(dict(cycle=cyc, loading=load, status="ok", aux=k, hdev_rows=n, vecto_rows=len(d),
                             hdev_driver_time_s=float(T[-1] + 1), vecto_time_s=float(d["time [s]"].iloc[-1]),
                             vecto_kWh=e_v, hdev_driver_kWh=kwh(parts[k]), diff_kWh=kwh(parts[k]) - e_v,
                             diff_pct=(kwh(parts[k]) / e_v - 1) * 100 if e_v else np.nan))
        e_v = kwh(d["P_aux_el [kW]"].to_numpy() * 1000)
        rows.append(dict(cycle=cyc, loading=load, status="ok", aux="TOTAL", hdev_rows=n, vecto_rows=len(d),
                         hdev_driver_time_s=float(T[-1] + 1), vecto_time_s=float(d["time [s]"].iloc[-1]),
                         vecto_kWh=e_v, hdev_driver_kWh=kwh(tot), diff_kWh=kwh(tot) - e_v, diff_pct=(kwh(tot) / e_v - 1) * 100))
        # same, but with the variant rules that were found closest to VECTO: need a motor-off proxy from HDEV's own M
        mo = (M == 0) | (M == 3) | ((M == 4) & (V <= V_NO_REGEN))
        tot_v = RC.aux_row_variant("a+b+c", V, np.zeros(n, bool), ES, PS, HV, SP, CD, 0.0, zero, motor_off=mo)
        rows.append(dict(cycle=cyc, loading=load, status="ok", aux="TOTAL (rules a+b+c, motor-off proxy P2 on HDEV M)", hdev_rows=n,
                         vecto_rows=len(d), hdev_driver_time_s=float(T[-1] + 1), vecto_time_s=float(d["time [s]"].iloc[-1]),
                         vecto_kWh=e_v, hdev_driver_kWh=kwh(tot_v), diff_kWh=kwh(tot_v) - e_v, diff_pct=(kwh(tot_v) / e_v - 1) * 100))
    df = pd.DataFrame(rows)
    out("partC4_hdev_driver_rows.csv", df)
    return df


def graph(r3):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sub = r3[r3["cycle"].isin(["RegionalDelivery", "UrbanDelivery"]) & (r3["loading"] == "ReferenceLoad")]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    labels = list(dict.fromkeys(sub["variant"]))
    x = np.arange(len(labels))
    w = 0.38
    for i, cyc in enumerate(["RegionalDelivery", "UrbanDelivery"]):
        s = sub[sub["cycle"] == cyc].set_index("variant").loc[labels]
        ax.bar(x + (i - 0.5) * w, s["total_diff_pct"], w, label=cyc)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([l[:34] for l in labels], rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("total aux energy vs VECTO [%]")
    ax.set_title("Part C3: aux total vs VECTO on the SAME VECTO rows (ReferenceLoad)")
    ax.legend()
    fig.tight_layout()
    p = os.path.join(HERE, "graph_partC_rule_variants.png")
    fig.savefig(p, dpi=110)
    WRITTEN.append(p)


if __name__ == "__main__":
    r2, r3, r3m = part_c1_c2_c3()
    print("\nC2: HDEV current rules on VECTO rows (diff vs VECTO)")
    print(r2[r2.aux.isin(["SP", "COND", "TOTAL"])][["cycle", "loading", "aux", "vecto_kWh", "hdev_current_kWh", "diff_kWh", "diff_pct"]].to_string(index=False))
    print("\nC3: variants (total aux)")
    print(r3[["cycle", "loading", "variant", "SP_kWh", "COND_kWh", "total_diff_kWh", "total_diff_pct", "side"]].to_string(index=False))
    print("\nC3: motor-off proxies vs VECTO EM_off column")
    print(r3m[["cycle", "loading", "proxy", "motor_off_seconds", "VECTO_EM_off_seconds", "abs_second_by_second_mismatch_s", "COND_diff_kWh"]].to_string(index=False))
    c4 = part_c4()
    print("\nC4: HDEV own driver rows")
    print(c4[c4.get("aux").isin(["TOTAL", "SP", "COND"]) if "aux" in c4 else c4.index][[ "cycle", "loading", "aux", "hdev_driver_time_s", "vecto_time_s", "vecto_kWh", "hdev_driver_kWh", "diff_pct"]].to_string(index=False))
    graph(r3)
    print("\nfiles written:")
    for p in WRITTEN:
        print("  ", os.path.relpath(p, REPO))
