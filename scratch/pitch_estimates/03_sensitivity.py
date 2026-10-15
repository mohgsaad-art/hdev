"""Item T (slide 7): sensitivity of the refuse truck's daily energy to +/-10% in
each input (air temperature is +/-10 K, not %). Rank largest first.

Baseline: V1 refuse on MunicipalUtility, good-day density, no wind, full regen,
BATTERY-level net energy per round (one round; a day is several rounds but the %
sensitivities are identical, so one round is a valid proxy for "daily energy").

To keep every case on ONE consistent code path, this script carries its own small
battery-net function (same physics as cycle_engine.cycle_energy, built on Bob's
force_engine) that also accepts a 'kin_scale' factor for the stop-count case.
A stop-count check against cycle_engine at kin_scale=1 is asserted below.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/03_sensitivity.py
"""
import numpy as np

from cycle_engine import cycle_energy
from vecto_data import (V1, read_vdri, v1_rrc_simple, air_density, RHO_VECTO,
                        ETA_CHAIN, G, force_engine)

CHASSIS = 11000.0            # ASSUMPTION chassis curb (middle of the sweep)
BODY = V1["body_curb_kg"]    # 6000 kg MU4
PAYLOAD = V1["payload_ref_kg"]  # 3000 kg reference


def batt_net(cyc, mass, cdxa, crr, rho, eta, kin_scale=1.0):
    """Battery-level net kWh/round. Same balance as cycle_engine.cycle_energy
    (theta_red=0, beta=1, full regen). 'kin_scale' multiplies ONLY the start-stop
    kinetic (accel) wheel power -> proxy for scaling the number of stops."""
    s = cyc["s"]; v = cyc["v_kmh"] / 3.6; grad = cyc["grad_pct"]
    ds = np.diff(s); v1 = v[:-1]; v2 = v[1:]; gr = grad[:-1]
    drive = ds > 0
    ds = ds[drive]; v1 = v1[drive]; v2 = v2[drive]; gr = gr[drive]
    vavg = (v1 + v2) / 2.0; safe = vavg > 1e-6
    a = np.zeros_like(ds); a[safe] = (v2[safe] ** 2 - v1[safe] ** 2) / (2 * ds[safe])
    dt = np.zeros_like(ds); dt[safe] = ds[safe] / vavg[safe]
    k_lin, k_roll, k_rot, L, vo = force_engine(G, crr, v1, a, dt, gr, 0.507, 0.0)
    grade_rad = np.arctan(gr / 100.0)
    P_roll = mass * crr * G * np.cos(grade_rad) * vo
    P_air = rho * cdxa * L
    P_grade = mass * G * np.sin(grade_rad) * vo
    P_acc = mass * a * vo * kin_scale
    E = (P_roll + P_air + P_grade + P_acc) * dt            # signed J per segment
    E_drive = E[E > 0].sum(); E_brake = -E[E < 0].sum()
    E_batt = E_drive / eta - E_brake * eta                 # regen fraction = 1
    return E_batt / 3.6e6


def main():
    cyc = read_vdri(V1["cycle"])
    m0 = CHASSIS + BODY + PAYLOAD
    cdxa0 = V1["cdxa_m2"]; crr0 = v1_rrc_simple(); rho0 = RHO_VECTO; eta0 = ETA_CHAIN

    # consistency check: our local batt_net must match cycle_engine at kin_scale=1
    ref = cycle_energy(cyc, m0, cdxa0, crr0, 0.507, rho=rho0)["E_batt_net_kWh"]
    loc = batt_net(cyc, m0, cdxa0, crr0, rho0, eta0, 1.0)
    assert abs(ref - loc) < 1e-6, f"path mismatch {ref} vs {loc}"
    base = loc
    print(f"Baseline (battery net/round): {base:.3f} kWh  (matches cycle_engine)")
    print(f"  [chassis {CHASSIS:.0f} ASSUMPTION, body {BODY:.0f}, payload {PAYLOAD:.0f}]\n")

    results = []

    def record(name, lo, hi, lo_lbl, hi_lbl):
        results.append([name, lo, hi, (lo / base - 1) * 100, (hi / base - 1) * 100,
                        lo_lbl, hi_lbl])

    # payload +/-10%
    record("payload",
           batt_net(cyc, CHASSIS + BODY + 0.9 * PAYLOAD, cdxa0, crr0, rho0, eta0),
           batt_net(cyc, CHASSIS + BODY + 1.1 * PAYLOAD, cdxa0, crr0, rho0, eta0),
           "-10%", "+10%")
    # curb mass (chassis+body) +/-10%
    record("curb mass (chassis+body)",
           batt_net(cyc, 0.9 * (CHASSIS + BODY) + PAYLOAD, cdxa0, crr0, rho0, eta0),
           batt_net(cyc, 1.1 * (CHASSIS + BODY) + PAYLOAD, cdxa0, crr0, rho0, eta0),
           "-10%", "+10%")
    # Crr +/-10%
    record("tyre rolling resistance (Crr)",
           batt_net(cyc, m0, cdxa0, 0.9 * crr0, rho0, eta0),
           batt_net(cyc, m0, cdxa0, 1.1 * crr0, rho0, eta0), "-10%", "+10%")
    # CdxA +/-10%
    record("CdxA",
           batt_net(cyc, m0, 0.9 * cdxa0, crr0, rho0, eta0),
           batt_net(cyc, m0, 1.1 * cdxa0, crr0, rho0, eta0), "-10%", "+10%")
    # air temperature +/-10 K via density. VECTO 1.188 ~ T0 at sea level.
    T0 = 101325.0 / (287.05 * RHO_VECTO) - 273.15
    record(f"air temperature (+/-10 K, base {T0:.0f}C)",
           batt_net(cyc, m0, cdxa0, crr0, air_density(T0 - 10), eta0),   # colder->denser->MORE
           batt_net(cyc, m0, cdxa0, crr0, air_density(T0 + 10), eta0),   # warmer->thinner->LESS
           "-10 K", "+10 K")
    # drivetrain efficiency product +/-10% (relative). Higher eta -> less energy.
    record("drivetrain efficiency product",
           batt_net(cyc, m0, cdxa0, crr0, rho0, min(eta0 * 1.1, 0.999)),  # +10% eta
           batt_net(cyc, m0, cdxa0, crr0, rho0, eta0 * 0.9),              # -10% eta
           "+10% eta", "-10% eta")
    # stop count +/-10% via kinetic-throughput proxy
    record("stop count (kinetic throughput)",
           batt_net(cyc, m0, cdxa0, crr0, rho0, eta0, kin_scale=0.9),
           batt_net(cyc, m0, cdxa0, crr0, rho0, eta0, kin_scale=1.1),
           "-10%", "+10%")

    results.sort(key=lambda r: max(abs(r[3]), abs(r[4])), reverse=True)
    print(f"{'rank input':34s} {'-case kWh':>10s} {'+case kWh':>10s} {'-%':>9s} {'+%':>9s}")
    print("-" * 76)
    for i, (name, lo, hi, plo, phi, llbl, hlbl) in enumerate(results, 1):
        print(f"{i:2d}. {name:30.30s} {lo:10.3f} {hi:10.3f} {plo:+8.1f}% {phi:+8.1f}%")
    print("\nNotes: air temperature '-10 K' is colder = denser air = MORE energy.")
    print("'drivetrain efficiency' '+10% eta' = more efficient = LESS energy.")
    print("stop count scales start-stop kinetic throughput only (road-load unchanged).")


if __name__ == "__main__":
    main()
