"""Part K: speed of the code of record, the step-6 fix and consumption_engine_v_proposed.  MachineDependent: the CSV is NOT byte-identical
between runs (timings).  Mean of 5 runs.  Cases: the refuse cycle (96 PTO stops, 4389 rows) because step 6 is the only part that scales with
the number of stops.

  day            one call, one route
  year, loop     250 calls (one per operating date)
  year, one array 250 days stacked into one array (1.1 M rows, 24 000 PTO stops)

Run: python partK_performance.py [--skip-old-long]   (the old loop on the long array takes minutes)
"""
import os
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _e2 as E  # noqa: E402
import _rows as R  # noqa: E402
import reference_copy as RC  # noqa: E402
from _common import BETA  # noqa: E402
from _scenarios import VPTOEL_T, VPTOEL_W  # noqa: E402

DAYS, REPEATS = 250, 5


def cpu():
    try:
        return [l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0] + f" ({os.cpu_count()} logical CPUs)"
    except Exception:  # noqa: BLE001
        return platform.processor()


def municipal_day():
    cy = R.read_vdri("MunicipalUtility")
    flag = cy["pto"] == 1
    stop_final = cy["stop"].copy(); stop_final[flag] += len(VPTOEL_T) - 1
    T, S, V, A, G_, M = R.run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)
    veh = E.veh_for("RegionalDelivery", "ReferenceLoad")
    dt = np.diff(T, append=T[-1] + 1.0)
    fe = E.forces(veh, V, A, dt, G_, E.J_ROTOR_TOTAL, E.I_TOTAL[2])
    is_on, ps, s1, d1 = E.pto_engine(stop_final, flag.astype(float), VPTOEL_T, VPTOEL_W, [0.0], [0.0], 1.0, 1.0)
    return dict(cy=cy, T=T, S=S, V=V, M=M, dt=dt, fe=fe, veh=veh, is_on=is_on, ps=ps, s1=s1, stop_final=stop_final)


def build_args(d, days=1):
    veh, fe = d["veh"], d["fe"]
    n, nwp = len(d["T"]), len(d["cy"]["s"])
    total_s = d["S"][-1] + 10.0
    rep = lambda x: np.tile(np.asarray(x), days)
    T = np.concatenate([d["T"] + k * 86400.0 for k in range(days)])
    S = np.concatenate([d["S"] + k * total_s for k in range(days)])
    wp_s = np.concatenate([d["cy"]["s"] + k * total_s for k in range(days)])
    payload = np.concatenate([np.r_[veh.m_payload, np.full(nwp - 1, np.nan)] for _ in range(days)])
    nh = days * 24 + 2
    W1, W2 = E.crosswind_tables(veh)
    new = dict(T=T, S=S, V=rep(d["V"]), M=rep(d["M"]), dt=rep(d["dt"]), k_lin=rep(d["fe"][0]), k_roll=rep(d["fe"][1]), k_rot_wheel=rep(d["fe"][2]),
               k_rot_rotor=rep(d["fe"][3]), L=rep(d["fe"][4]), v_avg=rep(d["fe"][5]), m_vehicle=veh.m_empty, wp_s=wp_s, payload_wp=payload, beta=BETA,
               t_start=0.0, T_amb_h=np.full(nh, 288.15), W1=np.tile(W1, (nh, 1)), W2=np.tile(W2, (nh, 1)), cdxa_v=E.CDXA_V / 3.6, CdxA0=veh.cdxa0,
               p_air=E.P_AIR, R_air=E.R_AIR, ES=1000.0, PS=162.0, HVAC=187.5, SP=20.0, cond=600.0, PTO_always_on=0.0,
               wp_stop=rep(d["stop_final"]), is_on=rep(d["is_on"]), pto_start=rep(d["ps"]), stop_1s=d["s1"], drive_1s=np.zeros(0), stop_const_W=0.0,
               drive_const_W=0.0, drive_pto_mechanical=False, gearbox_eff=0.98, motor_eff=0.95, inverter_eff=0.95, v_no_regen=E.V_NO_REGEN_5,
               P_regen_max=None)
    old = E.to_old_args(new)
    old.update(pto_1s=d["s1"], pto_on_col=rep(d["is_on"]), pto_start_col=rep(d["ps"]))
    return new, old


def timeit(fn, repeats=REPEATS):
    fn()                                                                  # warm-up
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
    return float(np.mean(ts)), float(np.min(ts)), float(np.max(ts))


def main(skip_old_long=False):
    d = municipal_day()
    new1, old1 = build_args(d, 1)
    rows = []
    cpu_s = cpu()

    def rec(case, variant, fn, repeats=REPEATS, calls=1):
        m, lo, hi = timeit(fn, repeats)
        rows.append(dict(case=case, variant=variant, rows_per_call=len(new1["T"]) if "day" in case or "loop" in case else None, calls=calls,
                         mean_s=m * 1, min_s=lo, max_s=hi, repeats=repeats, cpu=cpu_s, numpy=np.__version__, python=platform.python_version()))
        print(f"{case:32s} {variant:40s} mean {m:9.4f} s  (min {lo:.4f}, max {hi:.4f})")

    ce = E.NS["consumption_engine"]
    rec("day (4389 rows, 96 PTO stops)", "code of record (Appendix 1 loop)", lambda: ce(**old1))
    rec("day (4389 rows, 96 PTO stops)", "step 6 searchsorted only", lambda: RC.consumption_engine_v_step6_searchsorted(**old1))
    rec("day (4389 rows, 96 PTO stops)", "consumption_engine_v_proposed", lambda: RC.consumption_engine_v_proposed(**new1))
    # year as 250 calls
    rec("year = 250 calls (one per date)", "code of record (Appendix 1 loop)", lambda: [ce(**old1) for _ in range(DAYS)], repeats=3, calls=DAYS)
    rec("year = 250 calls (one per date)", "step 6 searchsorted only", lambda: [RC.consumption_engine_v_step6_searchsorted(**old1) for _ in range(DAYS)], repeats=3, calls=DAYS)
    rec("year = 250 calls (one per date)", "consumption_engine_v_proposed", lambda: [RC.consumption_engine_v_proposed(**new1) for _ in range(DAYS)], repeats=3, calls=DAYS)
    # year as one long array
    newL, oldL = build_args(d, DAYS)
    print("long array rows:", len(newL["T"]), " PTO stops:", int((newL["is_on"] == 1).sum()))
    rec("year = one array (1.1 M rows)", "step 6 searchsorted only", lambda: RC.consumption_engine_v_step6_searchsorted(**oldL), repeats=3)
    rec("year = one array (1.1 M rows)", "consumption_engine_v_proposed", lambda: RC.consumption_engine_v_proposed(**newL), repeats=3)
    if not skip_old_long:
        t0 = time.perf_counter(); ce(**oldL); dt_ = time.perf_counter() - t0
        rows.append(dict(case="year = one array (1.1 M rows)", variant="code of record (Appendix 1 loop), ONE run", rows_per_call=None, calls=1, mean_s=dt_, min_s=dt_, max_s=dt_,
                         repeats=1, cpu=cpu_s, numpy=np.__version__, python=platform.python_version()))
        print(f"{'year = one array':32s} {'code of record, one run':40s} {dt_:9.2f} s")
    # same numbers?
    a = ce(**old1); b = RC.consumption_engine_v_step6_searchsorted(**old1)
    same = all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(a, b))
    print("step-6 searchsorted variant bit-identical to the code of record on the refuse day:", same)
    rows.append(dict(case="check", variant="step6 searchsorted == code of record (bit identical, refuse day)", mean_s=float(same)))
    df = pd.DataFrame(rows)
    p = os.path.join(HERE, "partK_runtime_machine_dependent.csv")
    df.to_csv(p, index=False)
    print("wrote", os.path.relpath(p, E.REPO))


if __name__ == "__main__":
    main("--skip-old-long" in sys.argv)
