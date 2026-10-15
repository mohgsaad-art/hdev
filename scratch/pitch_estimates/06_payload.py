"""Items P1 and P2 (slide 4 payload tile + section 5).

P1: V2 (Group-5 tractor-semitrailer) on RegionalDelivery -- empty vs reference vs
    max payload, % energy.
P2: V1 (refuse) on MunicipalUtility with payload rising from empty at the start of
    collection to full at the end, built with Bob's payload_engine (shape='linear')
    + fill_payload. Compare:
      (i)   real varying payload
      (ii)  constant at the average
      (iii) constant full
      (iv)  constant empty
    Report energy per round and % of each vs (i).

For P2 the per-row payload multiplies the mass term row-by-row. We feed a per-row
mass array into a payload-aware cycle energy (same force_engine balance).

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/06_payload.py
"""
import numpy as np

from cycle_engine import cycle_energy
from vecto_data import (V1, V2, read_vdri, v1_rrc_simple, v2_rrc_simple,
                        RHO_VECTO, ETA_CHAIN, G, force_engine,
                        payload_engine, fill_payload)


def cycle_energy_varmass(cyc, mass_row, cdxa, crr, rho=RHO_VECTO):
    """Battery-level net kWh with a PER-ROW mass array (len = n rows). Mass of a
    segment = mass at its start row. Same balance as cycle_engine (full regen)."""
    s = cyc["s"]; v = cyc["v_kmh"] / 3.6; grad = cyc["grad_pct"]
    ds = np.diff(s); v1 = v[:-1]; v2 = v[1:]; gr = grad[:-1]
    m_seg = mass_row[:-1]
    drive = ds > 0
    ds = ds[drive]; v1 = v1[drive]; v2 = v2[drive]; gr = gr[drive]; m_seg = m_seg[drive]
    vavg = (v1 + v2) / 2.0; safe = vavg > 1e-6
    a = np.zeros_like(ds); a[safe] = (v2[safe] ** 2 - v1[safe] ** 2) / (2 * ds[safe])
    dt = np.zeros_like(ds); dt[safe] = ds[safe] / vavg[safe]
    k_lin, k_roll, k_rot, L, vo = force_engine(G, crr, v1, a, dt, gr, 0.507, 0.0)
    grade_rad = np.arctan(gr / 100.0)
    P = (m_seg * crr * G * np.cos(grade_rad) * vo
         + rho * cdxa * L
         + m_seg * G * np.sin(grade_rad) * vo
         + m_seg * a * vo)
    E = P * dt
    E_drive = E[E > 0].sum(); E_brake = -E[E < 0].sum()
    wheel_net = (E_drive - E_brake) / 3.6e6
    batt_net = (E_drive / ETA_CHAIN - E_brake * ETA_CHAIN) / 3.6e6
    return wheel_net, batt_net


def main():
    # ---------------- P1: V2 empty / reference / max ----------------
    print("=" * 70)
    print("P1  V2 Group-5 tractor-semitrailer on RegionalDelivery: payload sweep")
    print("=" * 70)
    base = V2["tractor_curb_kg"] + V2["trailer_curb_kg"]   # empty combination
    max_payload = V2["combo_gvm_kg"] - base                # cap at 40 t combo GVM
    cyc2 = read_vdri(V2["cycle"]); crr2 = v2_rrc_simple(); cdxa2 = V2["cdxa_combo_m2"]
    cases = [("empty", 0.0), ("reference", V2["payload_ref_kg"]),
             ("max (cap 40 t)", max_payload)]
    ref_e = None
    print(f"  empty combination curb = {base:.0f} kg; max payload = {max_payload:.0f} kg\n")
    print(f"  {'case':16s} {'payload kg':>10s} {'mass kg':>9s} {'wheel kWh':>10s} "
          f"{'batt kWh':>9s} {'vs ref':>8s}")
    for name, pl in cases:
        mass = base + pl
        r = cycle_energy(cyc2, mass, cdxa2, crr2, 0.507, rho=RHO_VECTO)
        if name == "reference":
            ref_e = r["E_wheel_net_recover_kWh"]
    for name, pl in cases:
        mass = base + pl
        r = cycle_energy(cyc2, mass, cdxa2, crr2, 0.507, rho=RHO_VECTO)
        w = r["E_wheel_net_recover_kWh"]; b = r["E_batt_net_kWh"]
        print(f"  {name:16s} {pl:10.0f} {mass:9.0f} {w:10.2f} {b:9.2f} "
              f"{(w/ref_e-1)*100:+7.1f}%")

    # ---------------- P2: V1 varying payload over the round ----------------
    print("\n" + "=" * 70)
    print("P2  V1 refuse: payload empty->full over the round (payload_engine linear)")
    print("=" * 70)
    cyc1 = read_vdri(V1["cycle"]); crr1 = v1_rrc_simple(); cdxa1 = V1["cdxa_m2"]
    chassis = V1["chassis_curb_assumptions_kg"][1]   # 11000 ASSUMPTION
    body = V1["body_curb_kg"]
    empty_pl, full_pl = 0.0, V1["payload_ref_kg"]    # 0 -> 3000 kg reference
    tare = chassis + body

    # Bob's payload_engine: write payload on row0 + stop rows, linear empty->full,
    # then fill_payload forward-fills to every row.
    stop = cyc1["stop_s"]
    payload_stops = payload_engine(stop, shape="linear",
                                   payload_start=empty_pl, payload_end=full_pl)
    payload_row = fill_payload(payload_stops)
    mass_row_var = tare + payload_row
    avg_pl = payload_row.mean()

    w_var, b_var = cycle_energy_varmass(cyc1, mass_row_var, cdxa1, crr1)
    w_avg, b_avg = cycle_energy_varmass(cyc1, np.full_like(mass_row_var, tare + avg_pl),
                                        cdxa1, crr1)
    w_full, b_full = cycle_energy_varmass(cyc1, np.full_like(mass_row_var, tare + full_pl),
                                          cdxa1, crr1)
    w_emp, b_emp = cycle_energy_varmass(cyc1, np.full_like(mass_row_var, tare + empty_pl),
                                        cdxa1, crr1)

    print(f"  tare (chassis 11000 ASSUMPTION + MU4 body) = {tare:.0f} kg; "
          f"payload 0 -> {full_pl:.0f} kg over {int((stop>0)[1:].sum())} stops")
    print(f"  average payload over the round = {avg_pl:.0f} kg\n")
    print(f"  {'case':28s} {'wheel kWh':>10s} {'batt kWh':>9s} {'vs (i)':>8s}")
    for lbl, w, b in [("(i) real varying payload", w_var, b_var),
                      ("(ii) constant at average", w_avg, b_avg),
                      ("(iii) constant full", w_full, b_full),
                      ("(iv) constant empty", w_emp, b_emp)]:
        print(f"  {lbl:28s} {w:10.3f} {b:9.3f} {(w/w_var-1)*100:+7.1f}%")

    print("\n  Observation: (i) real varying and (ii) constant-at-average are very"
          "\n  close because road-load energy is near-LINEAR in mass, so using the"
          "\n  mean mass reproduces the mean energy. Varying payload matters for WHEN"
          "\n  in the day energy is drawn (empty on the outbound legs, full near the"
          "\n  end) and for how much braking energy is available to recover.")


if __name__ == "__main__":
    main()
