"""Item W (slide 3): bad-weather day vs good day, same truck/route/load.

Weather enters ONLY through air drag here (density + crosswind). Cabin heating,
battery temperature and P_aux are NOT modelled -> every weather % is a LOWER
bound for winter (stated in the report).

Good day : VECTO density 1.188 kg/m^3, no wind.
Other days: ideal-gas density at the scenario temperature, + crosswind via
            crosswind_engine (direction-averaged, VECTO method), with Bob's 10 deg
            yaw clamp. We also print the no-clamp value next to it.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/02_weather.py
"""
import numpy as np

from vecto_data import (V1, V2, read_vdri, v1_rrc_simple, v2_rrc_simple,
                        air_density, RHO_VECTO, WEATHER)
from cycle_engine import cycle_energy


def run_vehicle(label, cyc, mass, cdxa0, crr, coeff_set, veh_h, v_steady_kmh):
    print("\n" + "=" * 70 + f"\n{label}\n" + "=" * 70)
    c = read_vdri(cyc)

    def energy(rho, v_ref, clamp, key="E_wheel_net_recover_kWh"):
        return cycle_energy(c, mass, cdxa0, crr, 0.507, rho=rho,
                            cdxa_wind=(v_ref > 0), v_ref_mps=v_ref,
                            coeff_set=coeff_set, veh_h=veh_h,
                            beta_clamp=clamp)[key]

    good = energy(RHO_VECTO, 0.0, 10.0)
    good_b = energy(RHO_VECTO, 0.0, 10.0, "E_batt_net_kWh")
    print(f"  good day (rho=1.188, no wind): {good:.2f} kWh net/round (wheel), "
          f"{good_b:.2f} kWh (battery)\n")
    print(f"  {'scenario':30s} {'rho':>6s} {'kWh':>8s} {'vs good':>9s} {'(no-clamp)':>12s}")
    rows = []
    for name in ["typical", "bad", "severe"]:
        tC, wind, note = WEATHER[name]
        rho = air_density(tC)
        e_clamp = energy(rho, wind, 10.0)
        e_noclamp = energy(rho, wind, None)
        e_clamp_b = energy(rho, wind, 10.0, "E_batt_net_kWh")
        pct = (e_clamp / good - 1) * 100
        pct_nc = (e_noclamp / good - 1) * 100
        pct_b = (e_clamp_b / good_b - 1) * 100
        print(f"  {name+' '+note:30.30s} {rho:6.3f} {e_clamp:8.2f} {pct:+8.1f}% "
              f"{pct_nc:+11.1f}%  (batt {pct_b:+.1f}%)")
        rows.append((name, rho, e_clamp, pct, e_noclamp, pct_nc, note))
    return good, rows


def main():
    v2_mass = V2["tractor_curb_kg"] + V2["trailer_curb_kg"] + V2["payload_ref_kg"]
    v1_mass = V1["chassis_curb_assumptions_kg"][1] + V1["body_curb_kg"] + V1["payload_ref_kg"]

    run_vehicle("W  V2 Group-5 tractor-semitrailer on RegionalDelivery "
                f"(mass {v2_mass:.0f} kg)",
                V2["cycle"], v2_mass, V2["cdxa_combo_m2"], v2_rrc_simple(),
                V2["crosswind_set"], V2["height_m"], 80.0)

    run_vehicle("W  V1 refuse truck on MunicipalUtility "
                f"(mass {v1_mass:.0f} kg, 11000 chassis ASSUMPTION)",
                V1["cycle"], v1_mass, V1["cdxa_m2"], v1_rrc_simple(),
                V1["crosswind_set"], V1["height_m"], 30.0)

    print("\nNOTE: weather here = air drag only (density + wind). Cabin heating,"
          "\nbattery derating and P_aux are NOT included -> these are LOWER bounds"
          "\nfor a real winter day.")


if __name__ == "__main__":
    main()
