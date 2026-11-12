"""Part J: performance of force_engine and consumption_engine steps 1-4 (mean of 5 runs).

Weather and payload values are ILLUSTRATIVE (timing only). Steps 1-4 are timed on a verbatim copy
(reference_copy.wheel_power_steps_1_to_4); the full notebook consumption_engine is timed as well.

Run:  python run_part_j.py     (timings differ between machines; the CSV records the CPU)
"""
import platform
import resource
import time

from _common import *
import reference_copy as RC


def cpu_name():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def timeit(f, n=5):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        out = f()
        ts.append(time.perf_counter() - t0)
    return float(np.mean(ts)), float(np.std(ts)), out


def main():
    (T, S, V, A, gr, M), veh = run_driver("RegionalDelivery", "ReferenceLoad", coast=True)
    n = len(T)
    s_wp, v_kmh, g_wp, stop = D.load_cycle(D.list_cycles()["RegionalDelivery"])
    stop = np.asarray(stop, float)
    pl = payload_engine(stop, "constant", 3019.5882)
    nh = 24 * 365
    rng = np.random.default_rng(0)                              # ILLUSTRATIVE weather, timing only
    T_amb = 8 + 10 * np.sin(np.arange(nh) / 24 * 2 * np.pi / 365) + rng.normal(0, 3, nh)
    wind = np.clip(rng.gamma(2.0, 2.0, nh), 0, 25)
    rows = []

    t, sd, k = timeit(lambda: force_engine(G, veh.crr_eff(), V, A, 1.0, gr, veh.r_dyn, veh.theta_red))
    rows.append(dict(item="force_engine, 1 Regional trip", rows=n, seconds_mean=t, seconds_std=sd))
    coef = k

    # crosswind table for the hours of ONE day (24 values) and for the whole year (chunked to bound memory)
    a1, a2, a3 = veh.a123
    t, sd, wt = timeit(lambda: crosswind_engine(HEIGHT, wind[:24], H_DECL, a1, a2, a3, HELLMANN, HEIGHT / 10, 10, CDXA_V, 10.0))
    rows.append(dict(item="crosswind_engine, 24 hourly wind speeds", rows=24, seconds_mean=t, seconds_std=sd))
    t0 = time.perf_counter()
    W1 = np.empty((nh, len(CDXA_V)))
    W2 = np.empty((nh, len(CDXA_V)))
    ru0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for i in range(0, nh, 500):
        w1, w2 = crosswind_engine(HEIGHT, wind[i:i + 500], H_DECL, a1, a2, a3, HELLMANN, HEIGHT / 10, 10, CDXA_V, 10.0)
        W1[i:i + 500], W2[i:i + 500] = w1, w2
    rows.append(dict(item="crosswind_engine, 8760 hourly wind speeds (chunks of 500)", rows=nh, seconds_mean=time.perf_counter() - t0, seconds_std=0.0,
                     note=f"peak RSS after {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB (chunk 500 h: temporaries ~ {500 * len(CDXA_V) * 36 * 10 * 8 / 1e6:.0f} MB each)"))
    W1d, W2d = W1[:24], W2[:24]

    # steps 1-4 once (one day, one payload)
    def one():
        return RC.wheel_power_steps_1_to_4(T, S, V, *coef, veh.mass - 3019.5882, np.asarray(s_wp, float), pl, BETA, 8 * 3600.0,
                                           T_amb[:48], W1[:48], W2[:48], CDXA_V, veh.cdxa0, 101325.0, 287.05)
    t, sd, _ = timeit(one)
    rows.append(dict(item="steps 1-4 (copy), 1 trip", rows=n, seconds_mean=t, seconds_std=sd))
    one_t = t

    def full():
        return consumption_engine(T, S, V, M, 1.0, *coef, veh.mass - 3019.5882, np.asarray(s_wp, float), pl, BETA, 8 * 3600.0, T_amb[:48], W1[:48], W2[:48],
                                  CDXA_V, veh.cdxa0, 101325.0, 287.05, 1000.0, 200.0, 250.0, 20.0, 500.0, 0.0,
                                  np.zeros(0), np.zeros(len(s_wp)), np.zeros(len(s_wp)), 0.95, 0.95, 0.98, 0.9, 5 / 3.6)
    t, sd, _ = timeit(full)
    rows.append(dict(item="full consumption_engine (steps 1-7), 1 trip", rows=n, seconds_mean=t, seconds_std=sd))

    # 365 days x 3 payloads, steps 1-4 only, loop over cases
    payloads = [603.9176, 3019.5882, 6000.0]                    # low / reference / ILLUSTRATIVE full
    plist = [payload_engine(stop, "constant", p) for p in payloads]

    def year():
        acc = 0.0
        for d in range(365):
            for p in plist:
                P = RC.wheel_power_steps_1_to_4(T, S, V, *coef, veh.mass - 3019.5882, np.asarray(s_wp, float), p, BETA, d * 86400.0 + 8 * 3600.0,
                                                T_amb, W1, W2, CDXA_V, veh.cdxa0, 101325.0, 287.05)
                acc += P.sum()
        return acc
    t, sd, _ = timeit(year, n=2)
    rows.append(dict(item="365 days x 3 payloads, steps 1-4 (loop)", rows=n * 365 * 3, seconds_mean=t, seconds_std=sd, note="n=2 runs; weather arrays are 8760 h"))

    # memory of the coefficient arrays
    mem = sum(np.asarray(c).nbytes for c in coef)
    rows.append(dict(item="coefficient arrays (5 x float64), 1 Regional trip", rows=n, seconds_mean=0.0, seconds_std=0.0, note=f"{mem / 1e3:.0f} kB"))
    rows.append(dict(item="all 1095 P_wheel arrays kept in memory", rows=n * 1095, seconds_mean=0.0, seconds_std=0.0, note=f"{n * 1095 * 8 / 1e6:.0f} MB"))
    rows.append(dict(item="cpu", rows=0, seconds_mean=0.0, seconds_std=0.0, note=f"{cpu_name()} ; python {platform.python_version()} ; numpy {np.__version__}"))
    for r in rows:
        r.setdefault("note", "")
    write_csv("partJ_performance.csv", rows)


if __name__ == "__main__":
    main()
