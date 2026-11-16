"""GATE 2 -- `drivetrain` (Appendix A, verbatim) fed the VECTO .vmod rows of the E2 example (reference load).

Inputs per row (all from the .vmod):
    power at axle output   = P_wheelEnd_in [kW]
    wheel speed            = n_gbx_out_avg / axle ratio 2.59 (rpm -> rad/s)
    gear                   = Gear
    rotor inertia power    = P_E2-em_mech - P_E2-em_mech_map  (VECTO: map torque = shaft torque + inertia torque)
Electric power compared:  -P_E2-em_el  (VECTO writes motoring electric power negative).
eta_adc = 1.0 (VECTO declaration ignores the .vveh MechanicalEfficiency, DeclarationData.cs 114).

Row rule (found in this job): rows where VECTO switched the motor OFF (vmod column EM_E2_off > 0) are left
out. VECTO switches the machine off while coasting / rolling and when braking at low speed
(BatteryElectricMotorController.cs 34-47, 62-70); the motor then only drags, which `drivetrain` is not built
for (HDEV sets those rows to zero electric power, consumption_engine line 531). With ALL rows the deviation is
larger; both are written.

Target (job prompt 2.1): -0.35 / -0.56 / -0.41 % for Regional / Urban / LongHaul, tolerance 0.05 percentage points.
"""
import csv
import os
import sys

import numpy as np

import reference_copy as R

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = {"RegionalDelivery": -0.35, "UrbanDelivery": -0.56, "LongHaul": -0.41}
TOL_PP = 0.05


def run(mission, e2=None, vecto_coords=False, load="ReferenceLoad"):
    import shapes_lib as SL
    e2 = dict(e2 or R.load_e2())
    if vecto_coords:
        e2["axle_map"] = SL.vecto_map(e2["axle_map"])
        e2["gear_maps"] = [SL.vecto_map(m) for m in e2["gear_maps"]]
    m = R.read_vmod(os.path.join(R.VMOD_DIR, "BEV_E2_%s_%s_1Hz.vmod" % (mission, load)))
    nz = np.nan_to_num
    Pw = nz(m["P_wheelEnd_in"]) * 1000.0
    ww = m["n_gbx_out_avg"] / R.RPM / e2["i_axle"]
    gear = nz(m["Gear"]).astype(int)
    Prot = (nz(m["P_E2-em_mech"]) - nz(m["P_E2-em_mech_map"])) * 1000.0
    out = R.run_e2_drivetrain(e2, Pw, ww, gear, Prot, eta_adc=1.0)
    Pel = out[0]
    vel = -nz(m["P_E2-em_el"]) * 1000.0
    on = nz(m["EM_E2_off"]) == 0
    dt = m["dt"]
    res = dict(
        mission=mission,
        dev_on_rows_pct=100 * (Pel[on].sum() / vel[on].sum() - 1),
        dev_all_rows_pct=100 * (Pel.sum() / vel.sum() - 1),
        gbx_loss_dev_pct=100 * ((out[2] * dt)[on].sum() / (nz(m["P_gbx_loss"]) * 1000 * dt)[on].sum() - 1),
        axle_loss_dev_pct=100 * ((out[1] * dt)[on].sum() / (nz(m["P_axle_loss"]) * 1000 * dt)[on].sum() - 1),
        vecto_el_kwh_on_rows=float((vel * dt)[on].sum() / 3.6e6),
        n_rows=len(Pw), n_rows_on=int(on.sum()), extrapolated=int(out[6].sum()), over_limit=int(out[7].sum()))
    return res


def main():
    rows, ok = [], True
    for mis, tgt in TARGET.items():
        r = run(mis)
        r["target_pct"] = tgt
        r["diff_pp"] = r["dev_on_rows_pct"] - tgt
        r["pass"] = abs(r["diff_pp"]) <= TOL_PP
        ok &= r["pass"]
        rows.append(r)
        print("%-17s on-rows %+.3f %% (target %+.2f, diff %+.3f pp)  all-rows %+.3f %%  gearbox loss %+.2f %%  axle loss %+.2f %%  -> %s" % (
            mis, r["dev_on_rows_pct"], tgt, r["diff_pp"], r["dev_all_rows_pct"], r["gbx_loss_dev_pct"],
            r["axle_loss_dev_pct"], "PASS" if r["pass"] else "FAIL"))
    out = os.path.join(HERE, "gate2_drivetrain.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("GATE 2:", "PASS" if ok else "FAIL")
    print("wrote", out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
