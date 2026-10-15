"""Items M1 (steady state), R (realistic vs constant-average speed) and
G (grade vs flat).  Wheel-level unless noted.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/01_steady_realistic_grade.py
"""
import numpy as np

from vecto_data import V1, V2, read_vdri, v1_rrc_simple, v2_rrc_simple, RHO_VECTO
from cycle_engine import cycle_energy, steady_state_power_kW


def banner(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def main():
    # ---- M1: steady state ----
    banner("M1  Steady state (constant speed, flat, accel=0), VECTO rho=1.188")
    v2_mass = V2["tractor_curb_kg"] + V2["trailer_curb_kg"] + V2["payload_ref_kg"]
    print(f"V2 mass (tractor+ST1+ref payload) = {v2_mass:.0f} kg")
    for vk in [80.0]:
        r = steady_state_power_kW(v2_mass, V2["cdxa_combo_m2"], v2_rrc_simple(), vk)
        whkm = r["P_wheel_kW"] * 1000.0 / vk       # Wh/km = kW*1000 / (km/h)
        print(f"  V2 @ {vk:.0f} km/h: P={r['P_wheel_kW']:.1f} kW "
              f"(roll {r['P_roll_kW']:.1f}, air {r['P_air_kW']:.1f}) "
              f"-> {whkm:.0f} Wh/km (wheel)")

    v1_mass = V1["chassis_curb_assumptions_kg"][1] + V1["body_curb_kg"] + V1["payload_ref_kg"]
    print(f"V1 mass (11000 chassis ASSUMPTION + MU4 body + ref payload) = {v1_mass:.0f} kg")
    for vk in [30.0, 50.0]:
        r = steady_state_power_kW(v1_mass, V1["cdxa_m2"], v1_rrc_simple(), vk)
        whkm = r["P_wheel_kW"] * 1000.0 / vk
        print(f"  V1 @ {vk:.0f} km/h: P={r['P_wheel_kW']:.1f} kW "
              f"(roll {r['P_roll_kW']:.1f}, air {r['P_air_kW']:.1f}) "
              f"-> {whkm:.0f} Wh/km (wheel)")

    # ---- R: realistic trace vs constant average speed, same distance ----
    banner("R  Realistic cycle speed trace vs same distance at constant avg speed")
    for veh, cyc, mass, cdxa, crr in [
        ("V2 RegionalDelivery", V2["cycle"], v2_mass, V2["cdxa_combo_m2"], v2_rrc_simple()),
        ("V1 MunicipalUtility", V1["cycle"], v1_mass, V1["cdxa_m2"], v1_rrc_simple()),
    ]:
        c = read_vdri(cyc)
        real = cycle_energy(c, mass, cdxa, crr, 0.507)
        # average speed over the moving part (distance / moving time).
        # moving time approximated from the cycle: sum ds/v_avg per driving seg.
        s = c["s"]; v = c["v_kmh"] / 3.6
        ds = np.diff(s); v1_ = v[:-1]; v2_ = v[1:]
        vavg = (v1_ + v2_) / 2.0
        drive = (ds > 0) & (vavg > 1e-6)
        move_time = (ds[drive] / vavg[drive]).sum()
        dist = ds[drive].sum()
        v_const_kmh = dist / move_time * 3.6
        # constant-speed cycle: a flat trace at v_const over the same distance,
        # same grade profile. Build a 2-point-per-segment synthetic trace that
        # keeps grade but sets speed constant.
        c_const = dict(c)
        c_const = {k: c[k].copy() for k in c}
        c_const["v_kmh"] = np.where(c["v_kmh"] > 0, v_const_kmh, 0.0)
        const = cycle_energy(c_const, mass, cdxa, crr, 0.507)
        rd = real["E_wheel_net_recover_kWh"]
        cd = const["E_wheel_net_recover_kWh"]
        print(f"\n  {veh}: avg moving speed = {v_const_kmh:.1f} km/h, dist {real['dist_km']:.2f} km")
        print(f"    realistic trace : net {rd:7.2f} kWh (drive {real['E_drive_wheel_kWh']:.2f}, "
              f"brake {real['E_brake_wheel_kWh']:.2f})")
        print(f"    constant speed  : net {cd:7.2f} kWh")
        print(f"    realistic is {(rd/cd-1)*100:+.1f}% vs constant-average (wheel, full regen)")

    # ---- G: grade vs flat ----
    banner("G  Energy with the cycle's grade vs flat (grade set to 0)")
    print("  Reported both with FULL regen and NO regen. The declaration cycles are\n"
          "  near altitude-neutral (return to start), so with full regen grade nets\n"
          "  to ~0; the honest 'decisive across the border' story is the NO-regen\n"
          "  case (you cannot always recover a long descent: full battery, speed/brake\n"
          "  limits).")
    for veh, cyc, mass, cdxa, crr in [
        ("V2 RegionalDelivery", V2["cycle"], v2_mass, V2["cdxa_combo_m2"], v2_rrc_simple()),
        ("V1 MunicipalUtility", V1["cycle"], v1_mass, V1["cdxa_m2"], v1_rrc_simple()),
        ("V2 LongHaul (cross-border ref)", "LongHaul.vdri", v2_mass, V2["cdxa_combo_m2"], v2_rrc_simple()),
    ]:
        c = read_vdri(cyc)
        wg_full = cycle_energy(c, mass, cdxa, crr, 0.507)["E_wheel_net_recover_kWh"]
        wg_nore = cycle_energy(c, mass, cdxa, crr, 0.507,
                               regen_fraction=0.0)["E_wheel_net_recover_kWh"]
        c_flat = {k: c[k].copy() for k in c}
        c_flat["grad_pct"] = np.zeros_like(c["grad_pct"])
        fl_full = cycle_energy(c_flat, mass, cdxa, crr, 0.507)["E_wheel_net_recover_kWh"]
        fl_nore = cycle_energy(c_flat, mass, cdxa, crr, 0.507,
                               regen_fraction=0.0)["E_wheel_net_recover_kWh"]
        s = c["s"]; grad = c["grad_pct"]; ds = np.diff(s)
        alt = np.concatenate([[0], np.cumsum(ds * grad[:-1] / 100.0)])
        print(f"\n  {veh}: dist {ds[ds>0].sum()/1000:.2f} km, "
              f"alt {alt.min():.0f}..{alt.max():.0f} m, net end {alt[-1]:.0f} m")
        print(f"    FULL regen: with-grade {wg_full:7.2f} vs flat {fl_full:7.2f} kWh "
              f"-> grade effect {(wg_full/fl_full-1)*100:+.1f}%")
        print(f"    NO   regen: with-grade {wg_nore:7.2f} vs flat {fl_nore:7.2f} kWh "
              f"-> grade effect {(wg_nore/fl_nore-1)*100:+.1f}%")


if __name__ == "__main__":
    main()
