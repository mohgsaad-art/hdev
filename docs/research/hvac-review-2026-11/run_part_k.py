"""Part K: run time of HVAC_thermal (mean of 5 runs, after 1 warm-up).  ILLUSTRATIVE inputs are the real DMI year (weather/) -- the time does not depend on values.
Output: part_k_timing.csv"""
import csv, os, platform, time
import numpy as np
import hvac_common as H

HERE = os.path.dirname(os.path.abspath(__file__))
w = H.load_weather(verbose=False)
a = H.base_args(H.PLACEHOLDER)


def cpu():
    for l in open("/proc/cpuinfo"):
        if l.startswith("model name"):
            return l.split(":", 1)[1].strip()
    return platform.processor()


def t(fn, n=5):
    fn()
    ts = []
    for _ in range(n):
        t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
    return float(np.mean(ts)), float(np.min(ts))


cases = {"1 day (24 h)": (w["T"][:24], w["S"][:24]), "1 year (8760 h, 1-D)": (w["T"], w["S"]),
         "1 year as 2-D days x hours (365 x 24)": (w["T"].reshape(365, 24), w["S"].reshape(365, 24))}
rows = []
for k, (T, S) in cases.items():
    m, mn = t(lambda: H.HVAC_thermal(T, S, Q=100.0, **a))
    rows.append(dict(case=k, mean_ms=round(m * 1e3, 3), min_ms=round(mn * 1e3, 3), cpu=cpu(), python=platform.python_version(), numpy=np.__version__))
    print(rows[-1])
# 1000 trucks x 1 year, same cab: not 1000 evaluations -- cache key = (weather year/station hash, all cab inputs, Q, setpoints)
m1 = rows[1]["mean_ms"]
print(f"1000 different cabs x 1 year = {1000*m1/1000:.1f} s if not cached; identical (weather, cab inputs) -> 1 evaluation")
with open(os.path.join(HERE, "part_k_timing.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
