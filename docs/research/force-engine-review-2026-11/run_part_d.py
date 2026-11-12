"""Part D: consistency between the driver's force model (coast_acc / coast_distance) and force_engine,
plus the driver-vs-force split of the 22 Oct error (driver rows -> force_engine vs VECTO .vmod).

Run:  python run_part_d.py
"""
from _common import *

DRV_CYCLES = ["RegionalDelivery", "UrbanDelivery", "LongHaul"]


def interp1(x, xs, ys):
    return NS["interp1"](x, xs, ys)


def force_rows(veh, V, A, dt, gr, mass, tab, rho=RHO_VECTO, beta=BETA):
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, veh.crr_eff(beta), V, A, dt, gr, veh.r_dyn, veh.theta_red)
    cd = cdxa_interp(v_avg, tab)
    P = dict(P_roll=mass ** beta * k_roll, P_air=rho * cd * L, P_slope=mass * G * np.sin(np.arctan(gr / 100)) * v_avg,
             P_veh_inertia=mass * A * v_avg, P_wheel_inertia=k_rot)
    P["P_wheel"] = P["P_roll"] + P["P_air"] + P["P_slope"] + P["P_veh_inertia"] + P["P_wheel_inertia"]
    return P, v_avg, L, cd


def main():
    resid_rows, snap_rows, split_rows, mode0_rows = [], [], [], []
    for cyc in DRV_CYCLES:
        (T, S, V, A, gr, M), veh = run_driver(cyc, "ReferenceLoad", coast=True)
        dt = 1.0
        tab = veh.cdxa_table()
        dv, dF = e2_drag_table()
        P, v_avg, L, cd = force_rows(veh, V, A, dt, gr, veh.mass, tab)

        # -------- standing rows: every coefficient exactly zero
        k = force_engine(G, veh.crr_eff(), V, A, dt, gr, veh.r_dyn, veh.theta_red)
        m0 = M == 0
        mode0_rows.append(dict(cycle=cyc, n_standing_rows=int(m0.sum()), max_abs_coeff_standing=float(max(np.abs(np.asarray(c)[m0]).max() for c in k)) if m0.any() else 0.0,
                               n_rows_V0_but_mode_not_0=int(np.sum((V == 0) & ~m0))))

        # -------- coast rows (mode 3): residual = P_wheel + F_drag(v1) * v_avg
        c3 = M == 3
        F_drag = np.array([interp1(v, [x / 3.6 for x in dv], dF) for v in V])
        resid = P["P_wheel"] + F_drag * v_avg
        # analytic split of the residual
        v1 = V
        v2 = np.maximum(V + A * dt, 0.0)
        cd_v1 = cdxa_interp(v1, tab)
        F_air_inst = RHO_VECTO / 2 * cd_v1 * v1 ** 2           # what coast_acc uses (CdxA at the START speed, instantaneous v^2)
        P_air_inst_x_vavg = F_air_inst * v_avg                 # instantaneous force times average speed
        d_form = RHO_VECTO / 2 * cd * v1 ** 2 * v_avg          # same CdxA(v_avg), instantaneous v1^2
        part_form = P["P_air"] - d_form                        # step-average vs instantaneous speed in v^2
        part_cdxa = d_form - P_air_inst_x_vavg                 # CdxA looked up at v_avg vs at v1
        other = resid - (part_form + part_cdxa)
        # same residual but with the driver's own grade (waypoint-segment grade at the row start, gr_l[k] in coast_acc)
        s_wp, _v, g_wp, _st = D.load_cycle(D.list_cycles()[cyc])
        k_seg = np.searchsorted(np.asarray(s_wp), S, side="right") - 1
        gr_seg = np.asarray(g_wp)[np.clip(k_seg, 0, len(g_wp) - 1)]
        P_seg, _, _, _ = force_rows(veh, V, A, dt, gr_seg, veh.mass, tab)
        other_seg = P_seg["P_wheel"] + F_drag * v_avg - (part_form + part_cdxa)
        grade_differs = np.abs(gr_seg - gr) > 1e-9
        E = lambda x, m=c3: float(np.sum(x[m]) * dt / 3.6e6)
        resid_rows.append(dict(cycle=cyc, n_coast_rows=int(c3.sum()), E_coast_wheel_kWh=E(P["P_wheel"]), E_drag_kWh=E(-F_drag * v_avg),
                               E_residual_kWh=E(resid), E_air_avg_vs_inst_kWh=E(part_form), E_cdxa_lookup_start_vs_avg_kWh=E(part_cdxa),
                               E_other_kWh=E(other), max_abs_other_W=float(np.abs(other[c3]).max()) if c3.any() else 0.0,
                               n_coast_rows_grade_secant_ne_segment=int((c3 & grade_differs).sum()),
                               E_other_gross_abs_kWh=float(np.sum(np.abs(other[c3])) * dt / 3.6e6),
                               max_abs_other_W_with_driver_segment_grade=float(np.abs(other_seg[c3]).max()) if c3.any() else 0.0,
                               E_other_with_driver_segment_grade_kWh=E(other_seg),
                               E_total_positive_wheel_kWh=float(np.sum(np.maximum(P["P_wheel"], 0)) * dt / 3.6e6),
                               E_total_negative_wheel_kWh=float(np.sum(np.minimum(P["P_wheel"], 0)) * dt / 3.6e6),
                               E_air_trip_kWh=float(np.sum(P["P_air"]) * dt / 3.6e6),
                               residual_pct_of_positive_wheel=E(resid) / (np.sum(np.maximum(P["P_wheel"], 0)) * dt / 3.6e6) * 100))

        # -------- stop-arrival rows: distance error and energy effect
        ds = np.append(np.diff(S), 0.0)
        ds[-1] = v_avg[-1] * dt             # last row has no successor; no error assumed
        err = v_avg * dt - ds
        bad = np.abs(err) > 1e-6
        P_ds, _, _, _ = force_rows(veh, V, A, dt, gr, veh.mass, tab)
        # energy if the row speed were ds/dt instead of v_avg in the speed-linear terms (roll, slope, inertia)
        speed_scale = np.where(v_avg > 0, ds / np.where(v_avg > 0, v_avg, 1) / dt, 1.0)
        d_roll = np.sum(P["P_roll"] * (speed_scale - 1)) * dt / 3.6e6
        d_slope = np.sum(P["P_slope"] * (speed_scale - 1)) * dt / 3.6e6
        snap_rows.append(dict(cycle=cyc, rows_with_distance_mismatch=int(bad.sum()), total_distance_error_m=float(err.sum()),
                              max_row_error_m=float(np.abs(err).max()), route_length_m=float(S[-1]),
                              total_error_pct_of_route=float(err.sum() / S[-1] * 100),
                              dE_roll_kWh_if_speed_were_ds_over_dt=float(d_roll), E_roll_trip_kWh=float(np.sum(P["P_roll"]) * dt / 3.6e6),
                              dE_slope_kWh_if_speed_were_ds_over_dt=float(d_slope)))

        # -------- driver share: HDEV driver rows through force_engine vs VECTO .vmod, per loading
        for load in ("ReferenceLoad", "LowLoading"):
            vh = Vehicle(cyc, load)
            cols = load_vmod_run(cyc, load)
            vt = vecto_terms(cols)
            dtv = VM.col(cols, "dt")
            Pd, _, _, _ = force_rows(vh, V, A, dt, gr, vh.mass, vh.cdxa_table())
            # VECTO trace through force_engine (Part C baseline)
            r = vmod_rows(cols)
            vs, ac = trace_for_engine(r, "acc")
            Hc = hdev_terms(vh, vs, ac, dtv, r["grad"], tab=vh.cdxa_table())
            for t in ("P_roll", "P_air", "P_slope", "P_wheel_inertia", "P_wheel"):
                vtt = vt["P_wheel_in"] if t == "P_wheel" else vt[t]
                e_v = energy_kwh(vtt, dtv)
                e_d = energy_kwh(Pd[t], np.full(len(Pd[t]), dt))
                e_c = energy_kwh(Hc[t], dtv)
                for part in ("net", "pos"):
                    split_rows.append(dict(cycle=cyc, load=load, term=t, part=part, vecto_kWh=e_v[part], hdev_driver_force_kWh=e_d[part],
                                           hdev_vectotrace_force_kWh=e_c[part],
                                           err_total_pct=(e_d[part] / e_v[part] - 1) * 100 if abs(e_v[part]) > 1e-6 else float("nan"),
                                           err_force_only_pct=(e_c[part] / e_v[part] - 1) * 100 if abs(e_v[part]) > 1e-6 else float("nan"),
                                           driver_share_kWh=e_d[part] - e_c[part],
                                           driver_share_pct_of_vecto=(e_d[part] - e_c[part]) / e_v[part] * 100 if abs(e_v[part]) > 1e-6 else float("nan"),
                                           coast_mass_kg=veh.mass, force_mass_kg=vh.mass))

    write_csv("partD_coast_rows_residual.csv", resid_rows)
    write_csv("partD_standing_rows.csv", mode0_rows)
    write_csv("partD_stop_arrival_rows.csv", snap_rows)
    write_csv("partD_driver_vs_force_split.csv", split_rows)


if __name__ == "__main__":
    main()
