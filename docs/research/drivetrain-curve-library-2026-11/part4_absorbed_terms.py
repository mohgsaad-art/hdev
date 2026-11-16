"""PART 4 -- what the certified kWh/km contains that a drivetrain fit absorbs, sized on the VECTO E2 .vmod runs
(docs/research/vecto/BEV_E2_*_1Hz.vmod, VECTO 5.1.6-RC, generic E2 vehicle), plus the remaining HDEV-vs-VECTO
differences of the vehicle physics on the same cycles.

Terms (all from .vmod columns, 1 s rows):
  battery internal loss       P_REESS_loss            (VECTO REESS Ri model)
  junction box / cable loss   P_REESS_JB_Cables_loss
  electric aux                P_aux_el
  charging                    certified = SoC-corrected energy / eta_charge, eta 0.995 (v2 report 2.1)
  motor-off rows              EM_E2_off > 0: VECTO switches the motor off (coasting / rolling, braking at low speed,
                              BatteryElectricMotorController.cs 34-47, 62-70); HDEV (consumption_engine) instead
                              regenerates on braking rows above v_no_regen and sets coasting rows to 0.
  HDEV on those rows: (a) Method A rule P_wheel * 0.95 on negative rows; (b) `drivetrain` (Appendix A, VECTO maps,
  vecto_loss_map reader) on the same rows.

Outputs: part4_absorbed_terms.csv, part4_motor_off.csv, part4_physics_vs_vecto.csv
"""
import csv
import os

import numpy as np

import reference_copy as R
import shapes_lib as SL

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [(m, l) for m in ("RegionalDelivery", "UrbanDelivery", "LongHaul") for l in ("ReferenceLoad", "LowLoading")]
ETA_CHARGE = 0.995
V_NO_REGEN = 5.0 / 3.6
HDEV_CYCLE = {"RegionalDelivery": "Regional", "UrbanDelivery": "Urban", "LongHaul": "LongHaul"}
HDEV_LOAD = {"ReferenceLoad": "reference", "LowLoading": "low"}


def main():
    nz = np.nan_to_num
    e2 = R.load_e2()
    e2["axle_map"] = R.vecto_loss_map(e2["axle_map"])
    e2["gear_maps"] = [R.vecto_loss_map(m) for m in e2["gear_maps"]]
    terms, off_rows, phys = [], [], []
    for mis, load in RUNS:
        m = R.read_vmod(os.path.join(R.VMOD_DIR, "BEV_E2_%s_%s_1Hz.vmod" % (mis, load)))
        dt = m["dt"]
        km = (np.nanmax(m["dist"]) - np.nanmin(m["dist"])) / 1000.0
        kwh = lambda col: float(np.sum(nz(m[col]) * dt) / 3600.0)
        E_term = -kwh("P_REESS_T")                       # energy drawn at the battery terminals (VECTO sign: discharge < 0)
        E_int = -kwh("P_REESS_int")
        loss_ri = kwh("P_REESS_loss"); loss_jb = kwh("P_REESS_JB_Cables_loss"); aux = kwh("P_aux_el")
        em_el = -kwh("P_E2-em_el")
        E_grid = E_int / ETA_CHARGE
        terms.append(dict(run="%s %s" % (mis, load), km=round(km, 3), E_internal_kwh=round(E_int, 3), E_terminal_kwh=round(E_term, 3),
                          battery_Ri_loss_kwh=round(loss_ri, 3), battery_Ri_loss_pct_of_internal=round(100 * loss_ri / E_int, 2),
                          jb_cable_loss_kwh=round(loss_jb, 3), aux_el_kwh=round(aux, 3), aux_pct_of_internal=round(100 * aux / E_int, 2),
                          motor_el_kwh=round(em_el, 3), charging_kwh=round(E_grid - E_int, 3), charging_pct=round(100 * (1 / ETA_CHARGE - 1), 3),
                          internal_kwh_per_km=round(E_int / km, 4), grid_kwh_per_km=round(E_grid / km, 4)))
        # motor-off rows
        off = nz(m["EM_E2_off"]) > 0
        Pw = nz(m["P_wheelEnd_in"]) * 1000.0
        brake = off & (Pw < 0)
        v = nz(m["v_act"]) / 3.6
        vecto_off = float(np.sum((-nz(m["P_E2-em_el"]) * 1000.0)[off] * dt[off]) / 3.6e6)
        hdev_A = np.where(brake & (v > V_NO_REGEN), Pw * 0.95, 0.0)
        ww = m["n_gbx_out_avg"] / R.RPM / e2["i_axle"]
        gear = nz(m["Gear"]).astype(int)
        gear_off = np.where(brake & (v > V_NO_REGEN), np.where(gear > 0, gear, 2), 0)    # HDEV keeps a gear in
        Prot = (nz(m["P_E2-em_mech"]) - nz(m["P_E2-em_mech_map"])) * 1000.0
        out = R.run_e2_drivetrain(e2, np.where(gear_off > 0, Pw, 0.0), nz(ww), gear_off, Prot * 0, eta_adc=1.0)
        hdev_dt = float(np.sum(out[0] * dt) / 3.6e6)
        off_rows.append(dict(run="%s %s" % (mis, load), rows_off_any=int(off.sum()), rows_off_full=int((nz(m["EM_E2_off"]) >= 1).sum()),
                             rows_off_braking=int(brake.sum()), wheel_brake_energy_on_off_rows_kwh=round(float(-np.sum(Pw[brake] * dt[brake]) / 3.6e6), 3),
                             vecto_el_on_off_rows_kwh=round(vecto_off, 4),
                             hdev_methodA_el_on_off_rows_kwh=round(float(np.sum(hdev_A * dt) / 3.6e6), 3),
                             hdev_drivetrain_el_on_off_rows_kwh=round(hdev_dt, 3),
                             diff_methodA_pct_of_motor_el=round(100 * (float(np.sum(hdev_A * dt) / 3.6e6) - vecto_off) / em_el, 2),
                             diff_drivetrain_pct_of_motor_el=round(100 * (hdev_dt - vecto_off) / em_el, 2)))
        # vehicle physics: HDEV (v2 driver + force engine) vs VECTO on the same cycle and mass
        rows = SL.e2_vehicle_rows(HDEV_CYCLE[mis], HDEV_LOAD[load])
        Ph = rows["P_wheel"]
        Pv = nz(m["P_wheel_in"]) * 1000.0
        phys.append(dict(run="%s %s" % (mis, load), hdev_mass_kg=round(rows["mass"], 1),
                         vecto_km=round(km, 3), hdev_km=round(rows["km"], 3),
                         vecto_time_s=int(len(dt)), hdev_time_s=int(len(Ph)),
                         vecto_wheel_pos_kwh=round(float(np.sum(np.clip(Pv, 0, None) * dt) / 3.6e6), 3),
                         hdev_wheel_pos_kwh=round(float(np.sum(np.clip(Ph, 0, None)) / 3.6e6), 3),
                         vecto_wheel_neg_kwh=round(float(np.sum(np.clip(Pv, None, 0) * dt) / 3.6e6), 3),
                         hdev_wheel_neg_kwh=round(float(np.sum(np.clip(Ph, None, 0)) / 3.6e6), 3),
                         diff_pos_pct=round(100 * (np.sum(np.clip(Ph, 0, None)) / np.sum(np.clip(Pv, 0, None) * dt) - 1), 2),
                         diff_neg_pct=round(100 * (np.sum(np.clip(Ph, None, 0)) / np.sum(np.clip(Pv, None, 0) * dt) - 1), 2),
                         note=("BLOCKED: VECTO LongHaul E2 run has a trailer (vsum Total vehicle mass 11273.9 / 19811.2 kg, CdxA 6.13 m2); "
                               "the HDEV E2 set-up used here (shapes_lib.e2_vehicle_rows) has no trailer -> not comparable")
                         if mis == "LongHaul" else ""))
    files = []
    for name, rows in (("part4_absorbed_terms.csv", terms), ("part4_motor_off.csv", off_rows), ("part4_physics_vs_vecto.csv", phys)):
        f = os.path.join(HERE, name)
        with open(f, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        files.append(f)
    for f in files:
        print("wrote", f)


if __name__ == "__main__":
    main()
