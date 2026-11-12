"""Part F: measured wheel-energy effect of physics beyond VECTO (candidates, NOT changes).

Base case: VECTO's own 1 Hz speed trace of the E2 ReferenceLoad runs (Regional, Urban) -> force_engine (unchanged) -> wheel power.
All variants live in reference_copy.py. Effects are WHEEL-level (kWh at the wheel, and % of the positive wheel energy);
the translation to battery energy is the job of the later drivetrain review.

Run:  python run_part_f.py
"""
import math

from _common import *
import reference_copy as RC

CYCLES = ["RegionalDelivery", "UrbanDelivery"]


def base_case(cyc, load="ReferenceLoad"):
    veh = Vehicle(cyc, load)
    cols = load_vmod_run(cyc, load)
    r = vmod_rows(cols)
    vs, ac = trace_for_engine(r, "acc")
    k = RC.force_engine(G, veh.crr_eff(), vs, ac, r["dt"], r["grad"], veh.r_dyn, veh.theta_red)
    cd = cdxa_interp(k[4], veh.cdxa_table())
    return veh, r, vs, ac, k, cd


def wheel(veh, k, cd, rho=RHO_VECTO, f_roll=1.0, roll_override=None, rho_row=None):
    k_lin, k_roll, k_rot, L, v_avg = k
    m = veh.mass
    rho = rho if rho_row is None else rho_row
    P_roll = f_roll * m ** BETA * k_roll if roll_override is None else roll_override
    P_air = rho * cd * L
    P = m * k_lin + P_roll + k_rot + P_air
    return dict(P=P, P_roll=P_roll, P_air=P_air)


def en(P, dt):
    return energy_kwh(P, dt)


def main():
    rows = []
    for cyc in CYCLES:
        veh, r, vs, ac, k, cd = base_case(cyc)
        dt = r["dt"]
        b = wheel(veh, k, cd)
        eb = en(b["P"], dt)
        e_roll0, e_air0 = en(b["P_roll"], dt)["net"], en(b["P_air"], dt)["net"]

        def add(item, scenario, P_new, source, tag, note=""):
            e = en(P_new, dt)
            rows.append(dict(item=item, cycle=cyc, scenario=scenario, E_wheel_pos_kWh=e["pos"], dE_pos_kWh=e["pos"] - eb["pos"],
                             dE_pos_pct=(e["pos"] / eb["pos"] - 1) * 100, dE_net_kWh=e["net"] - eb["net"], base_pos_kWh=eb["pos"],
                             E_roll_base_kWh=e_roll0, E_air_base_kWh=e_air0, source=source, tag=tag, note=note))

        # ---------- F1 cold rolling resistance (hourly factor from ambient T)
        for T in (-10, 0, 10, 25):
            f = float(RC.f_roll_linear_between_sourced_points(T))
            add("F1 tyre temperature", f"T={T} C, f_roll={f:.2f}", wheel(veh, k, cd, f_roll=f)["P"],
                "Ramesh Babu et al. 2025 (full text): Crr 0.007 @20C -> 0.014 @-20C", "[SOURCE]+[ASSUMPTION linear between the two points]",
                "factor applies to the WHOLE trip (no warm-up); conservative (more energy)")

        # ---------- F2/F3 winter surface + speed dependence: Askerdal et al. 2025 fit on scraped ice at -12 C (measured, 9 t BEV truck, <= 50 km/h)
        c1, c2, c3 = 9.3e-3, 9.0e-4, -3.1e-5                    # Askerdal et al. 2025, Vehicle System Dynamics 63(6), section 4.1 (full text read)
        v_fit = np.clip(k[4], 0.0, 50 / 3.6)                     # fit is valid up to ~50 km/h; held above [ASSUMPTION]
        Crr_ice = c1 + c2 * v_fit + c3 * v_fit ** 2
        m = veh.mass
        P_ice = Crr_ice * m * G * np.cos(np.arctan(r["grad"] / 100)) * k[4]            # their form is linear in mass
        add("F2/F3 scraped-ice winter Crr(v)", "Crr(v)=c1+c2 v+c3 v^2 at -12 C, scraped ice", wheel(veh, k, cd, roll_override=P_ice)["P"],
            "Askerdal et al. 2025 (full text); different truck and tyres -> ILLUSTRATIVE size only", "[SOURCE]+[ILLUSTRATIVE]",
            "mean Crr over moving rows = %.4f vs E2 declaration Crr_eff-equivalent %.4f" % (float(np.mean(Crr_ice[k[4] > 0.5])), float(veh.crr_total_vecto())))

        # ---------- F4 air density: replace the VECTO 1.188 by weather-dependent values
        for T in (-10, 0, 10, 20, 30):
            for RH in (0.0, 0.5, 1.0):
                rho = float(RC.rho_cipm2007(T, 101325.0, RH))
                add("F4 density (CIPM-2007)", f"T={T} C, RH={int(RH*100)} %, p=101325 Pa", wheel(veh, k, cd, rho=rho)["P"],
                    "CIPM-2007 (Picard 2008) full text; validity 15-27 C, outside = extrapolation", "[SOURCE]+[CALC]", f"rho={rho:.4f} kg/m3 vs VECTO 1.188 ({(rho/RHO_VECTO-1)*100:+.1f} %)")
        for T in (-10, 15):
            for h in (0, 1000, 2000):
                p = float(RC.p_standard_atmosphere(h))
                rho = float(RC.rho_cipm2007(T, p, 0.5))
                add("F4 density vs altitude", f"T={T} C, RH=50 %, h={h} m (p={p:.0f} Pa, ISO 2533 barometric formula)", wheel(veh, k, cd, rho=rho)["P"],
                    "ISO 2533 barometric formula (constants not re-read: OPEN) + CIPM-2007", "[CALC]+[OPEN]", f"rho={rho:.4f}")
        for dp in (-3000.0, 3000.0):
            rho = float(RC.rho_cipm2007(10, 101325.0 + dp, 0.5))
            add("F4 station pressure", f"T=10 C, RH=50 %, p=101325{dp:+.0f} Pa", wheel(veh, k, cd, rho=rho)["P"], "CIPM-2007", "[CALC]", f"rho={rho:.4f}")

        # ---------- F5 motor rotor inertia, wheel-side equivalent (gear per row from .vmod)
        J = 0.225 * 2
        cols = load_vmod_run(cyc, "ReferenceLoad")
        gear = VM.col(cols, "Gear").astype(int)
        i_row = 2.0 * 2.59 * np.array([{0: 1.93, 1: 3.86, 2: 1.93}[g] for g in gear])
        th = RC.theta_red_with_rotor(veh.theta_red, J, i_row)
        k2 = RC.force_engine_v_rotor(G, veh.crr_eff(), vs, ac, dt, r["grad"], veh.r_dyn, th)
        add("F5 rotor inertia", "J_rotor=0.45 kg m2 (2 x 0.225), E2 ratios, wheel-side equivalent", wheel(veh, k2, cd)["P"],
            "[VECTO] GenericEMotor_125kW_485Nm.vem, AMT.vgbx, .vveh (commit b8d6126)", "[VECTO]+[CALC]", "VECTO applies it at the motor shaft, not at the wheel (Q5)")

        # ---------- F7 grade noise: ILLUSTRATIVE altitude noise on the VECTO altitude profile, with and without smoothing
        alt = r["altitude"]
        ds = np.maximum(np.diff(r["dist"], prepend=0.0), 1e-9)
        rng = np.random.default_rng(12345)
        for sigma in (0.5, 1.0, 2.0):
            noisy = alt + rng.normal(0.0, sigma, len(alt))
            for win_m, label in ((0.0, "raw"), (200.0, "moving average over ~200 m")):
                if win_m > 0:
                    # moving average along distance (centred, window in rows set from mean row spacing)
                    n = max(int(round(win_m / max(np.mean(ds[ds > 0.5]), 1.0))), 1) | 1
                    ker = np.ones(n) / n
                    sm = np.convolve(np.pad(noisy, n // 2, mode="edge"), ker, mode="valid")
                else:
                    sm = noisy
                dalt = np.diff(sm, prepend=sm[0])
                gr_noisy = np.where(ds > 0.5, dalt / ds * 100, 0.0)
                gr_noisy = np.clip(gr_noisy, -30.0, 30.0)         # a parser would clamp absurd grades; clamp at +-30 % [ASSUMPTION for this illustration]
                kn = RC.force_engine(G, veh.crr_eff(), vs, ac, dt, gr_noisy, veh.r_dyn, veh.theta_red)
                add("F7 grade noise (ILLUSTRATIVE)", f"altitude noise sigma={sigma} m, {label}", wheel(veh, kn, cd)["P"],
                    "no sourced sigma; NREL/ORNL grade-smoothing papers not readable here (abstract only)", "[ILLUSTRATIVE]",
                    f"mean |grade| noisy={np.mean(np.abs(gr_noisy)):.2f} % vs original {np.mean(np.abs(r['grad'])):.2f} %")

        # ---------- F8 coast-down mapping: fit F0+F1 v+F2 v^2 to HDEV's own road load, map back to Crr and CdxA, measure the loss
        v = np.linspace(5.0, 90.0, 200) / 3.6
        cd_v = np.interp(v * 3.6, CDXA_V, veh.cdxa_table())
        F_true = veh.crr_eff() * G * veh.mass ** BETA + 0.5 * RHO_VECTO * cd_v * v ** 2
        F2_, F1_, F0_ = np.polyfit(v, F_true, 2)
        Crr_eq = F0_ / (veh.mass * G)
        CdxA_eq = 2 * F2_ / RHO_VECTO
        k_lin, k_roll, k_rot, L, v_avg = k
        P_fit_road = (F0_ + F1_ * v_avg) * (v_avg > 0) * 1.0 * v_avg + 0.0
        # air part via L-form with an equivalent constant CdxA; F1 term acts like extra speed-proportional drag
        P_cd = RHO_VECTO * CdxA_eq * L
        P_new = veh.mass * k[0] + (F0_ * np.cos(np.arctan(r["grad"] / 100)) * v_avg) + F1_ * v_avg * v_avg + k[2] + P_cd
        add("F8 coast-down mapping", f"quadratic fit 5-90 km/h: F0={F0_:.0f} N, F1={F1_:.2f} N s/m, F2={F2_:.3f} N s2/m2 -> Crr_eq={Crr_eq:.5f}, CdxA_eq={CdxA_eq:.3f}",
            P_new, "[CALC] from HDEV's own E2 road load", "[CALC]", f"max |F_fit-F_true| = {np.max(np.abs(np.polyval([F2_, F1_, F0_], v) - F_true)):.1f} N over 5-90 km/h")
    write_csv("partF_effects_wheel_energy.csv", rows)

    # ---------- air density scenario table independent of the vehicle
    dens = []
    for T in (-20, -10, 0, 10, 15, 20, 25, 30):
        for RH in (0.0, 0.5, 1.0):
            dens.append(dict(T_C=T, RH=RH, p_Pa=101325.0, rho_ideal_dry_HDEV=float(RC.rho_ideal_dry(T)), rho_cipm2007=float(RC.rho_cipm2007(T, 101325.0, RH)),
                             rho_vs_vecto_1p188_pct=(float(RC.rho_cipm2007(T, 101325.0, RH)) / RHO_VECTO - 1) * 100,
                             hdev_dry_vs_cipm_pct=(float(RC.rho_ideal_dry(T)) / float(RC.rho_cipm2007(T, 101325.0, RH)) - 1) * 100,
                             in_cipm_validity_15_27C=bool(15 <= T <= 27)))
    write_csv("partF_air_density_table.csv", dens)
    T_eq = 101325.0 / (287.05 * RHO_VECTO) - 273.15
    write_csv("partF_vecto_density_equivalent_T.csv", [dict(note="dry ideal-gas T giving VECTO's rho=1.188 at 101325 Pa with R=287.05", T_C=T_eq)])


if __name__ == "__main__":
    main()
