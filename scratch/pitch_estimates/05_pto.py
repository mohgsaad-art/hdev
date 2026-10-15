"""Item O (slide 4 on-board consumers): refuse body / PTO energy per stop and
per round, from VECTO's generic electric-PTO activation cycle.

Source: reference/vecto/resources/MissionCycles/MunicipalUtility_PTO_generic.vptoel
  columns <t>[s], <P_PTO_el>[kW]  (07-pto-all.md: P_PTO_el is kW electrical, drawn
  directly from the battery as an aux consumer, DC/DC = 1.0).
Number of PTO-active stops per round from MunicipalUtility.vdri <PTO> column.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/05_pto.py
"""
import os

import numpy as np

from vecto_data import MISSIONS_DIR, read_vdri, V1


def read_vptoel(path):
    t, p = [], []
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip().lstrip("\ufeff")
            if not line or line.startswith("<"):
                continue
            parts = [x.strip() for x in line.split(",")]
            t.append(float(parts[0])); p.append(float(parts[1]))
    return np.array(t), np.array(p)   # s, kW


def main():
    path = os.path.join(MISSIONS_DIR, "MunicipalUtility_PTO_generic.vptoel")
    t, p_kw = read_vptoel(path)
    # energy of one activation cycle = integral P dt. 1 Hz samples, trapezoid.
    dur = t[-1] - t[0]
    # VECTO holds LeftSample over each 1 s step (07): sum P over [0..22] * 1 s,
    # i.e. energy = sum of P at each second it is held. Use trapezoid as a check.
    e_step_kWh = p_kw[:-1].sum() * 1.0 / 3600.0    # left-sample hold, 1 s steps
    e_trap_kWh = np.trapz(p_kw, t) / 3600.0 if hasattr(np, "trapz") else \
        np.trapezoid(p_kw, t) / 3600.0
    print("O  Electric PTO (refuse body) energy")
    print(f"  activation cycle: {len(t)} rows, duration {dur:.0f} s, "
          f"P range {p_kw.min():.2f}-{p_kw.max():.2f} kW")
    print(f"  energy per activation (left-sample hold) = {e_step_kWh*1000:.1f} Wh "
          f"= {e_step_kWh:.4f} kWh")
    print(f"  energy per activation (trapezoid check)   = {e_trap_kWh*1000:.1f} Wh")

    cyc = read_vdri(V1["cycle"])
    pto = cyc["flag"]
    both = (cyc["stop_s"] > 0) & (pto > 0)
    both[0] = False
    n_pto_stops = int(both.sum())
    e_round_kWh = e_step_kWh * n_pto_stops
    print(f"\n  PTO-active stops per round (MunicipalUtility <PTO>): {n_pto_stops}")
    print(f"  PTO energy per round = {e_step_kWh*1000:.1f} Wh x {n_pto_stops} "
          f"= {e_round_kWh:.2f} kWh")

    round_km = cyc["s"].max() / 1000.0
    day_km = 70.0
    n_rounds = day_km / round_km
    print(f"\n  scaled to a <70 km day ({n_rounds:.2f} rounds): "
          f"{e_round_kWh*n_rounds:.1f} kWh of PTO energy")
    print("\n  NOTE: this is the generic VECTO electric-PTO profile, not a specific"
          "\n  compactor. It is drawn straight from the battery (DC/DC=1.0).")

    # ---- P_aux (constant electric aux) for a Group-4 MunicipalUtility BEV ----
    # Values from docs/decisions/2026-10-08_session-closeout-paux.md (VECTO traced):
    #   ES  group 4 MU: table 1428.5714 W x 0.7 = 1000 W           (paux doc 4.1)
    #   HVAC group 4 MU Default: 300 W x 1.25   = 375 W            (paux doc 4.2)
    #   PS  'Vacuum pump + elec. driven' MU     = 162 W            (paux doc 4.3)
    #   SP  = 0 W while stopped (STP standstill filter)            (paux doc 4.4)
    #   Cond group lorry MU                      = 550 W (motor on) (paux doc 4.5)
    # ASSUMPTION: motor-on share + moving share not modelled here; we take the
    # "stopped, motor-on" constant set (ES+HVAC+PS+Cond) as a floor and ignore SP.
    print("\n" + "=" * 70)
    print("  P_aux floor (VECTO-traced constants, Group-4 MunicipalUtility BEV)")
    print("=" * 70)
    es, hvac, ps, cond = 1000.0, 375.0, 162.0, 550.0   # W
    aux_floor_W = es + hvac + ps + cond
    print(f"  ES {es:.0f} + HVAC {hvac:.0f} + PS {ps:.0f} + Cond {cond:.0f} "
          f"= {aux_floor_W:.0f} W continuous (motor on)")
    # time per round: moving time + dwell time
    move_dwell_s = _round_time_s(cyc)
    e_aux_round = aux_floor_W * move_dwell_s / 3.6e6
    print(f"  round active time ~= {move_dwell_s/60:.1f} min "
          f"-> aux energy/round ~= {e_aux_round:.2f} kWh")
    print(f"  scaled to a {day_km:.0f} km day: ~= {e_aux_round*n_rounds:.1f} kWh")
    print("  (HVAC here is A/C compressor only; VECTO has NO cabin heating -> a real"
          "\n   Danish winter adds an unmodelled heating load on top.)")


def _round_time_s(cyc):
    """Approx round active time = moving time (sum ds/v_avg) + total dwell (stop)."""
    s = cyc["s"]; v = cyc["v_kmh"] / 3.6
    ds = np.diff(s); vavg = (v[:-1] + v[1:]) / 2.0
    drive = (ds > 0) & (vavg > 1e-6)
    move = (ds[drive] / vavg[drive]).sum()
    dwell = cyc["stop_s"][1:].sum()
    return move + dwell


if __name__ == "__main__":
    main()
