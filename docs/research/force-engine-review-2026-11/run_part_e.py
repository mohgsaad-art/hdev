"""Part E: time step. Driver at dt = 1.0, 0.5, 0.25 on Regional and Urban (E2 reference vehicle, coasting on),
pushed through force_engine + P_wheel. Energy terms only (no driver-behaviour metrics).

Run:  python run_part_e.py
"""
import time

from _common import *

DTS = [1.0, 0.5, 0.25]


def main():
    rows = []
    res_ = {}
    for cyc in ("RegionalDelivery", "UrbanDelivery"):
        res = {}
        for dt in DTS:
            t0 = time.perf_counter()
            (T, S, V, A, gr, M), veh = run_driver(cyc, "ReferenceLoad", coast=True, dt=dt)
            t_drv = time.perf_counter() - t0
            t0 = time.perf_counter()
            k_lin, k_roll, k_rot, L, v_avg = force_engine(G, veh.crr_eff(), V, A, dt, gr, veh.r_dyn, veh.theta_red)
            cd = cdxa_interp(v_avg, veh.cdxa_table())
            m = veh.mass
            P = dict(P_roll=m ** BETA * k_roll, P_air=RHO_VECTO * cd * L, P_slope=m * G * np.sin(np.arctan(gr / 100)) * v_avg,
                     P_veh_inertia=m * A * v_avg, P_wheel_inertia=k_rot)
            P["P_wheel"] = sum(P.values())
            t_frc = time.perf_counter() - t0
            res[dt] = dict(P=P, n=len(T), t_drv=t_drv, t_frc=t_frc, T_end=float(T[-1] + dt), S_end=float(S[-1]), coast=float(np.mean(M == 3) * 100))
        res_[cyc] = res
        ref = res[0.25]
        for dt in DTS:
            r = res[dt]
            for term, P in r["P"].items():
                E = lambda x, d=dt: energy_kwh(x, np.full(len(x), d))
                e, e0 = E(P), energy_kwh(ref["P"][term], np.full(len(ref["P"][term]), 0.25))
                rows.append(dict(cycle=cyc, dt=dt, term=term, rows=r["n"], net_kWh=e["net"], pos_kWh=e["pos"], neg_kWh=e["neg"],
                                 pos_vs_dt0p25_pct=(e["pos"] / e0["pos"] - 1) * 100 if e0["pos"] > 1e-9 else float("nan"),
                                 net_vs_dt0p25_kWh=e["net"] - e0["net"],
                                 trip_time_s=r["T_end"], route_end_m=r["S_end"], coast_pct=r["coast"]))
    write_csv("partE_timestep_energy.csv", rows)
    # runtimes are machine dependent -> separate file (not part of the deterministic outputs)
    rt = [dict(cycle=c, dt=d, rows=res_[c][d]["n"], driver_seconds=res_[c][d]["t_drv"], force_seconds=res_[c][d]["t_frc"]) for c in res_ for d in DTS]
    write_csv("partE_runtime_machine_dependent.csv", rt)


if __name__ == "__main__":
    main()
