"""Numbers for Part A (Q1 grade table, hand tests) and Part B (energy closure, v2 clamp, stop snapping).

Run:  python run_part_a_b_numbers.py
"""
import math
from _common import *


def main():
    # ---- Q1: sin(atan(G)) vs asin(G) vs G
    rows = []
    for gp in (2, 6, 10, 20):
        Gr = gp / 100
        rows.append(dict(grade_pct=gp, sin_atan_G=math.sin(math.atan(Gr)), sin_of_asin_G=math.sin(math.asin(Gr)), G_direct=Gr,
                         asin_G_rad=math.asin(Gr), atan_G_rad=math.atan(Gr),
                         sin_atan_minus_G_pct_of_G=(math.sin(math.atan(Gr)) / Gr - 1) * 100,
                         cos_atan_G=math.cos(math.atan(Gr)), cos_asin_G=math.sqrt(1 - Gr ** 2),
                         cos_atan_minus_1_pct=(math.cos(math.atan(Gr)) - 1) * 100,
                         cos_asin_minus_1_pct=(math.sqrt(1 - Gr ** 2) - 1) * 100,
                         sin_atan_minus_sin_asin_pct=(math.sin(math.atan(Gr)) / Gr - 1) * 100))
    write_csv("partA_q1_grade_conversions.csv", rows)

    # ---- hand tests recomputed with g = 9.80665
    rows = []
    for label, v, a in (("test1 v=20 a=0", 20.0, 0.0), ("test2 v=10 a=1", 10.0, 1.0)):
        for g_ in (9.81, G):
            k = force_engine(g_, 0.0055, [v], [a], [1.0], [0.0], 0.0, 0.0)
            rows.append(dict(test=label, g=g_, k_lin=float(k[0][0]), k_roll=float(k[1][0]), k_rot=float(k[2][0]), L=float(k[3][0]), v_avg=float(k[4][0])))
    write_csv("partB_hand_tests_recomputed.csv", rows)

    # ---- closure + gap split on the driver rows (E2 reference mass)
    rows = []
    for cyc in ("RegionalDelivery", "UrbanDelivery"):
        (T, S, V, A, gr, M), veh = run_driver(cyc, "ReferenceLoad", coast=True)
        m = veh.mass
        k_lin, k_roll, k_rot, L, v_avg = force_engine(G, veh.crr_eff(), V, A, 1.0, gr, veh.r_dyn, veh.theta_red)
        Gr = gr / 100
        ds = np.append(np.diff(S), 0.0)
        dh = np.sum(Gr * ds)
        E_in = np.sum(m * A * v_avg) / 3.6e6
        v_end = max(V[-1] + A[-1], 0.0)
        E_ke = 0.5 * m * (v_end ** 2 - V[0] ** 2) / 3.6e6
        E_slope = np.sum(m * G * np.sin(np.arctan(Gr)) * v_avg) / 3.6e6
        E_pot = m * G * dh / 3.6e6
        gap_i = np.sum(m * G * (np.sin(np.arctan(Gr)) - Gr) * v_avg) / 3.6e6
        gap_ii = np.sum(m * G * Gr * (v_avg - ds)) / 3.6e6
        E_pos_slope = np.sum(np.maximum(m * G * np.sin(np.arctan(Gr)) * v_avg, 0)) / 3.6e6
        rows.append(dict(cycle=cyc, mass_kg=m, rows=len(T), E_inertia_kWh=E_in, E_kinetic_kWh=E_ke, closure_residual_kWh=E_in - E_ke,
                         E_slope_kWh=E_slope, E_potential_m_g_dh_kWh=E_pot, gap_total_kWh=E_slope - E_pot,
                         gap_i_sin_atan_vs_G_kWh=gap_i, gap_ii_distance_ne_vavg_dt_kWh=gap_ii, gap_residual_kWh=E_slope - E_pot - gap_i - gap_ii,
                         E_slope_positive_part_kWh=E_pos_slope,
                         sum_k_rot_J_per_kg_s=float(np.sum(k_rot)), total_row_distance_error_m=float(np.sum(v_avg) - np.sum(ds)),
                         max_row_distance_error_m=float(np.max(np.abs(v_avg - ds))), n_rows_distance_error_gt_1mm=int(np.sum(np.abs(v_avg - ds) > 1e-3))))
    write_csv("partB_energy_closure.csv", rows)

    # ---- the v2 clamp
    v, a, dt = 2.0, -4.0, 1.0
    k = force_engine(G, 0, [v], [a], [dt], [0.0], 0, 0)
    write_csv("partB_v2_clamp.csv", [dict(note="ILLUSTRATIVE v=2 m/s a=-4 m/s2 dt=1 s", v2_unclamped=v + a * dt, v2_clamped=0.0,
                                         inertia_J_per_kg_engine=float(k[0][0] * dt), kinetic_J_per_kg=-0.5 * v * v, ratio=float(k[0][0] * dt / (-0.5 * v * v)))])
    rows = []
    for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul", "MunicipalUtility", "Construction"):
        for coast in (True, False):
            (T, S, V, A, gr, M), veh = run_driver(cyc, "ReferenceLoad", coast=coast)
            slack = V + A * 1.0
            rows.append(dict(cycle=cyc, coast=coast, rows=len(T), min_v_plus_a_dt=float(slack.min()), rows_clamped=int(np.sum(slack < -1e-9))))
    write_csv("partB_v2_clamp_driver_scan.csv", rows)


def q10():
    """Q10: other columns in the .vmod (wheel-end saving, friction-brake loss, gearbox/rotor inertia)."""
    rows = []
    for key in LOADING:
        cols = load_vmod_run(*key)
        dt = VM.col(cols, "dt")
        f = lambda n: float(np.nansum(VM.col(cols, n) * dt) / 3600)
        rows.append(dict(cycle=key[0], load=key[1], E_wheelEnd_saving_kWh=f("P_wheelEnd_saving"), E_brake_loss_kWh=f("P_brake_loss"),
                         E_gbx_inertia_kWh=f("P_gbx_inertia"), E_rotor_inertia_net_kWh=f("P_E2-em_inertia_loss"), E_wheel_in_net_kWh=f("P_wheel_in"),
                         E_wheel_in_pos_kWh=float(np.sum(np.maximum(VM.col(cols, "P_wheel_in"), 0) * dt) / 3600),
                         E_trac_pos=float(np.sum(np.maximum(VM.col(cols, "P_trac"), 0) * dt) / 3600)))
    write_csv("partA_q10_other_terms.csv", rows)


if __name__ == "__main__":
    main()
    q10()
