"""Part G numbers: what do the formula CONVENTIONS of other tools change, on identical inputs (VECTO's own E2 1 Hz trace)?

Conventions (all [CALC]; inputs identical, only the averaging convention differs; constants such as rho are NOT changed):
  HDEV        air = rho*CdxA(v_avg)*mean(0.5 v^3) ; roll/slope at v_avg
  FASTSim-3   air = 0.5*rho*CdxA*v_avg^3  (roadload.rs 28-63: t3..t0 expand 1/16*rho*CdA*(v+v0)^3)
  SUMO        roll, slope, air all evaluated at the END speed of the step (HelpersEnergy.cpp 59-81)
Run:  python run_part_g_conventions.py
"""
from _common import *


def main():
    rows = []
    for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
        for load in ("ReferenceLoad",):
            veh = Vehicle(cyc, load)
            cols = load_vmod_run(cyc, load)
            r = vmod_rows(cols)
            dt = r["dt"]
            vs, ac = trace_for_engine(r, "acc")
            H = hdev_terms(veh, vs, ac, dt, r["grad"], tab=veh.cdxa_table())
            v1 = vs
            v2 = np.maximum(vs + ac * dt, 0.0)
            vav = (v1 + v2) / 2
            cd = H["cdxa"]
            m = veh.mass
            th = np.arctan(r["grad"] / 100)
            base_rest = H["P_roll"] + H["P_slope"] + H["P_veh_inertia"] + H["P_wheel_inertia"]
            variants = {
                "HDEV (code of record)": H["P_wheel"],
                "FASTSim-3 air convention (v_avg^3)": base_rest + H["P_wheel_inertia"] * 0 + 0.5 * RHO_VECTO * cd * vav ** 3,
                "SUMO end-speed convention": (m ** BETA * veh.crr_eff() * G * np.cos(th) * v2 + m * G * np.sin(th) * v2 + m * ac * vav +
                                              H["P_wheel_inertia"] + 0.5 * RHO_VECTO * cd * v2 ** 3),
            }
            base = energy_kwh(variants["HDEV (code of record)"], dt)
            for name, P in variants.items():
                e = energy_kwh(P, dt)
                a = energy_kwh(0.5 * RHO_VECTO * cd * v2 ** 3 if "SUMO" in name else (0.5 * RHO_VECTO * cd * vav ** 3 if "FASTSim" in name else H["P_air"]), dt)
                rows.append(dict(cycle=cyc, load=load, convention=name, E_air_kWh=a["net"], E_wheel_pos_kWh=e["pos"], E_wheel_net_kWh=e["net"],
                                 d_pos_vs_HDEV_pct=(e["pos"] / base["pos"] - 1) * 100, d_air_vs_HDEV_pct=(a["net"] / energy_kwh(H["P_air"], dt)["net"] - 1) * 100))
    write_csv("partG_convention_effects.csv", rows)


if __name__ == "__main__":
    main()
