"""Part D.4 runtime: the PTO loop of the code of record (np.where over ALL rows for each PTO stop) vs the variant (searchsorted).

Wall-clock times depend on the machine, so the CSV is called partD_runtime_machine_dependent.csv and is NOT expected to be
byte-identical between runs.  The row/stop counts and the speed-up ORDER OF MAGNITUDE are what matter.

Cases
  A  MunicipalUtility, all 96 PTO stops (one route)
  B  365 sequential days of that route (Option A of docs/design/year-and-day-simulation-problem.md: one T and wind per day)
  C  one array holding 365 days back to back (S continues; upper bound if a year were ever put in one array)
"""
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _rows import read_vdri, run_driver_e2, REPO  # noqa: E402
from _scenarios import VPTOEL_T, VPTOEL_W  # noqa: E402
import reference_copy as RC  # noqa: E402
from _load_notebook import NS  # noqa: E402

pto_engine = NS["pto_engine"]


def timeit(f, repeat=3):
    best = 1e9
    for _ in range(repeat):
        t0 = time.perf_counter()
        f()
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    cy = read_vdri("MunicipalUtility")
    pto = cy["pto"] == 1
    stop_final = cy["stop"].copy()
    stop_final[pto] += 23
    on = pto.astype(float)
    is_on, ps, s1, d1 = pto_engine(stop_final, on, VPTOEL_T, VPTOEL_W, [0.0], [0.0], 1.0, 1.0)
    T, S, V, A, G, M = run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)
    n = len(S)
    rows = []

    def slow():
        return RC.consumption_step6_current_loop(S, V, cy["s"], is_on, ps, s1)

    def fast():
        return RC.consumption_step6_v_pto1nov(S, V, cy["s"], stop_final, is_on, ps, s1, d1, M=M)

    a = slow()[0]
    b = fast()[0]
    same = bool(np.allclose(a, b))
    rows.append(dict(case="A: one MunicipalUtility route", rows=n, pto_stops=int(pto.sum()), seconds_current_loop=timeit(slow),
                     seconds_variant=timeit(fast), identical_pto_row=same))
    # B: 365 sequential days
    t_cur = timeit(lambda: [slow() for _ in range(365)], repeat=1)
    t_var = timeit(lambda: [fast() for _ in range(365)], repeat=1)
    rows.append(dict(case="B: 365 sequential days of that route", rows=n * 365, pto_stops=int(pto.sum()) * 365, seconds_current_loop=t_cur,
                     seconds_variant=t_var, identical_pto_row=same))
    # C: one array, 365 days back to back
    days = 365
    L = S[-1] + 100.0
    S_big = np.concatenate([S + d * L for d in range(days)])
    V_big = np.tile(V, days)
    M_big = np.tile(M, days)
    wp_big = np.concatenate([cy["s"] + d * L for d in range(days)])
    stop_big = np.tile(stop_final, days)
    on_big = np.tile(on, days)
    ps_big = np.tile(ps, days)
    is_on_big = np.tile(is_on, days)

    def fast_big():
        return RC.consumption_step6_v_pto1nov(S_big, V_big, wp_big, stop_big, is_on_big, ps_big, s1, d1, M=M_big)

    def slow_big():
        return RC.consumption_step6_current_loop(S_big, V_big, wp_big, is_on_big, ps_big, s1)

    t_fast = timeit(fast_big, repeat=1)
    # the current loop is O(rows x PTO stops): time a 5-day slice and extrapolate linearly in stops x rows (labelled)
    k = 5
    sl = len(S) * k
    ns = int(np.searchsorted(wp_big, S_big[sl - 1] + 1e-6, side="right"))
    t5 = timeit(lambda: RC.consumption_step6_current_loop(S_big[:sl], V_big[:sl], wp_big[:ns], is_on_big[:ns], ps_big[:ns], s1), repeat=1)
    est = t5 * (days / k) ** 2
    rows.append(dict(case="C: 365 days in ONE array (variant measured; current loop measured on 5 days, x(365/5)^2 extrapolated)",
                     rows=len(S_big), pto_stops=int(pto.sum()) * days, seconds_current_loop=est, seconds_variant=t_fast,
                     identical_pto_row=None))
    df = pd.DataFrame(rows)
    p = os.path.join(HERE, "partD_runtime_machine_dependent.csv")
    df.to_csv(p, index=False, float_format="%.5f")
    print(df.to_string(index=False))
    print("file written:", os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
