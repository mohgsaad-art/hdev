"""Items H (slide 6 cross-check) and B (slide 4 braking tile).

H: energy per working day for the refuse truck, compared to Frederiksberg's
   real-world figure (175 kWh truck, under 70 km, ended at 15% SoC -> ~149 kWh
   used IF started full and 15% is of the rated 175 kWh -- Bob's assumption).
   We scale one MunicipalUtility round (11.24 km) up to the day's distance.

B: % of traction (drive) energy recovered on the refuse cycle, and how much a
   model WITHOUT recovery would overstate the energy.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/04_crosscheck_braking.py
"""
import numpy as np

from cycle_engine import cycle_energy
from vecto_data import V1, read_vdri, v1_rrc_simple, RHO_VECTO

BODY = V1["body_curb_kg"]
PAYLOAD = V1["payload_ref_kg"]
ROUND_KM = None  # filled from the cycle


def main():
    cyc = read_vdri(V1["cycle"])
    crr = v1_rrc_simple(); cdxa = V1["cdxa_m2"]

    print("=" * 70)
    print("B  Braking energy recovered on the refuse cycle (MunicipalUtility)")
    print("=" * 70)
    for chassis in V1["chassis_curb_assumptions_kg"]:
        mass = chassis + BODY + PAYLOAD
        r = cycle_energy(cyc, mass, cdxa, crr, 0.507, rho=RHO_VECTO)
        drive = r["E_drive_wheel_kWh"]; brake = r["E_brake_wheel_kWh"]
        recov_pct = brake / drive * 100
        # a no-recovery model would report E_drive (wheel) vs the net E_drive-brake
        net = drive - brake
        overstate = (drive / net - 1) * 100
        print(f"\n  chassis {chassis:.0f} kg -> mass {mass:.0f} kg, dist {r['dist_km']:.2f} km")
        print(f"    wheel drive  = {drive:7.2f} kWh")
        print(f"    wheel brake  = {brake:7.2f} kWh  (regen-eligible)")
        print(f"    recovered    = {recov_pct:5.1f}% of traction (if 100% capture at wheel)")
        print(f"    net (wheel)  = {net:7.2f} kWh")
        print(f"    a NO-recovery model overstates net by {overstate:+.1f}%")

    print("\n" + "=" * 70)
    print("H  Energy per working day vs Frederiksberg real-world (~149 kWh used)")
    print("=" * 70)
    # one round distance
    round_km = cycle_energy(cyc, 1.0, cdxa, crr, 0.507)["dist_km"]
    day_km = 70.0            # Bob's prompt: "a day of under 70 km"
    n_rounds = day_km / round_km
    print(f"\n  one MunicipalUtility round = {round_km:.2f} km; "
          f"a <70 km day ~= {n_rounds:.2f} rounds")
    print(f"\n  {'chassis kg':>10s} {'mass kg':>8s} {'wheel/day':>10s} {'batt/day':>10s} "
          f"{'vs 149':>8s}")
    for chassis in V1["chassis_curb_assumptions_kg"]:
        mass = chassis + BODY + PAYLOAD
        r = cycle_energy(cyc, mass, cdxa, crr, 0.507, rho=RHO_VECTO)
        wheel_day = r["E_wheel_net_recover_kWh"] * n_rounds
        batt_day = r["E_batt_net_kWh"] * n_rounds
        vs149 = (batt_day / 149.0 - 1) * 100
        print(f"  {chassis:10.0f} {mass:8.0f} {wheel_day:9.1f}  {batt_day:9.1f}  {vs149:+7.1f}%")
    print("\n  (battery/day = traction side only: motor+inverter+gearbox placeholder,"
          "\n   full regen. NO P_aux, NO PTO/compactor, NO cabin heating -> physics is a"
          "\n   LOWER bound; the real 149 kWh includes all of those.)")


if __name__ == "__main__":
    main()
