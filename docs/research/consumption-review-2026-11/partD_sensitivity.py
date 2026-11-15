"""Part D: sensitivity of kWh/km, one input at a time, on HDEV's OWN driver rows (E2 Regional and Urban, reference load).

Baseline = consumption_engine_v_proposed with SCALAR efficiencies fitted to VECTO's energy (Q5: what one number per direction would
reproduce VECTO on average).  Each change is only run over a SOURCED range (VECTO files / VECTO runs); where there is no source the line is
written as NO SOURCE and skipped.  Also writes the scalar-efficiency fit (Q5) and a tornado chart.

Run: python partD_sensitivity.py  (deterministic)
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _e2 as E  # noqa: E402
import _rows as R  # noqa: E402
import reference_copy as RC  # noqa: E402
from _common import write_csv  # noqa: E402
from partC_vecto_rows import per_row_eta  # noqa: E402

VSUM_KWH_KM = {"RegionalDelivery": 1.050, "UrbanDelivery": 0.840}     # BEV_E2.vsum [kWh/km at the battery terminals], PR #23 close-out
LOAD = "ReferenceLoad"


def scalar_fit(cycle, loading):
    """Energy-weighted scalar factors from the VECTO run of this cycle: wheel -> motor shaft, motor -> battery, per direction."""
    rw = E.vecto_rows(cycle, loading)
    v, dt = rw["vecto"], rw["dt"]
    wheelEnd, gbx = v["P_wheelEnd_in"], v["P_gbx_in"]
    mech, el = -v["P_E2-em_mech_map"], -v["P_E2-em_el"]
    d, g = mech > 0, mech < 0
    out = dict(
        gb_drive=float((wheelEnd[wheelEnd > 0] * dt[wheelEnd > 0]).sum() / (gbx[wheelEnd > 0] * dt[wheelEnd > 0]).sum()),
        gb_regen=float((gbx[wheelEnd < 0] * dt[wheelEnd < 0]).sum() / (wheelEnd[wheelEnd < 0] * dt[wheelEnd < 0]).sum()),
        mot_drive=float((mech[d] * dt[d]).sum() / (el[d] * dt[d]).sum()),
        mot_regen=float((el[g] * dt[g]).sum() / (mech[g] * dt[g]).sum()),
    )
    # total wheel -> battery: driving rows and regen rows
    wd = v["P_wheel_in"] > 0
    out["total_drive"] = float((v["P_wheel_in"][wd] * dt[wd]).sum() / (el[wd] * dt[wd]).sum())
    wr = v["P_wheel_in"] < 0
    out["total_regen"] = float((el[wr] * dt[wr]).sum() / (v["P_wheel_in"][wr] * dt[wr]).sum())
    return out


def hdev_rows(cycle):
    cy = R.read_vdri(cycle)
    T, S, V, A, G_, M = R.run_driver_e2(cy, LOAD)
    veh = E.veh_for(cycle, LOAD)
    dt = np.diff(T, append=T[-1] + 1.0)
    return cy, veh, T, S, V, A, G_, M, dt


def run(cy, veh, T, S, V, A, G_, M, dt, vec, gear=2, **over):
    ratio = E.I_TOTAL[gear]
    fe = E.forces(veh, V, A, dt, G_, over.pop("J_rotor", E.J_ROTOR_TOTAL), ratio)
    wp_s = np.array([0.0, S[-1] + 1.0]); payload = np.array([veh.m_payload, np.nan])
    km = S[-1] / 1000.0
    aux = dict(ES=vec["ES"], PS=vec["PS"], HVAC=vec["HVAC"], SP=vec["SP"], cond=vec["cond"], PTO_always_on=0.0)
    drv = over.pop("drivetrain", dict(gearbox_eff=vec["gb"], motor_eff=vec["mot"], inverter_eff=1.0))
    a = E.engine_args(veh, T, S, V, M, dt, fe, wp_s, payload, aux, E.no_pto(2), drv, P_regen_max=over.pop("cap", None),
                      v_no_regen=over.pop("v_no_regen", E.V_NO_REGEN_10), drive_pto_mechanical=over.pop("mech", False))
    sw = over
    r = RC.consumption_engine_v_split_eff(**a, **sw)
    return r["E_battery"] / km, r


def main():
    fits, rows_, tornado = [], [], []
    for cycle in ("RegionalDelivery", "UrbanDelivery"):
        cy, veh, T, S, V, A, G_, M, dt = hdev_rows(cycle)
        # scalar fits from all six VECTO runs of this cycle family (sourced: BEV_E2 .vmod)
        f = {ld: scalar_fit(cycle, ld) for ld in ("ReferenceLoad", "LowLoading")}
        for ld, d in f.items():
            fits.append(dict(cycle=cycle, loading=ld, **d))
        fr = f["ReferenceLoad"]
        rw = E.vecto_rows(cycle, "ReferenceLoad")
        vv = rw["vecto"]
        mv = rw["V"] > 0
        vec = dict(ES=float(vv["P_aux_ES_el"].max()), PS=float(vv["P_aux_PS_el"].max()), HVAC=float(vv["P_aux_AC_el"].max()),
                   SP=float(vv["P_aux_STP_el"][mv].mean()), cond=float(vv["P_aux_COND_el"].max()),
                   gb=1.0, mot=1.0)
        # baseline: scalar efficiency = the VECTO energy-weighted drive value for both directions of each component (symmetric, as the proposal)
        gb0 = 0.5 * (fr["gb_drive"] + fr["gb_regen"]); mot0 = 0.5 * (fr["mot_drive"] + fr["mot_regen"])
        vec["gb"], vec["mot"] = gb0, mot0
        base, _ = run(cy, veh, T, S, V, A, G_, M, dt, vec)
        target = VSUM_KWH_KM[cycle]
        rows_.append(dict(cycle=cycle, item="BASELINE (scalar gearbox %.3f, motor %.3f, both directions)" % (gb0, mot0), setting="", kWh_km=base,
                          d_kWh_km=0.0, d_pct=0.0, vs_vecto_pct=(base / target - 1) * 100, source="VECTO E2 .vmod energy-weighted"))

        def add(item, setting, val, source, key=None):
            rows_.append(dict(cycle=cycle, item=item, setting=setting, kWh_km=val, d_kWh_km=val - base, d_pct=(val / base - 1) * 100,
                              vs_vecto_pct=(val / target - 1) * 100, source=source))
            tornado.append(dict(cycle=cycle, item=item, setting=setting, d_pct=(val / base - 1) * 100))

        # gearbox efficiency: sourced range = min / max over the VECTO runs of this cycle (drive-direction energy-weighted)
        gb_vals = [f[l][k] for l in f for k in ("gb_drive", "gb_regen")]
        mot_vals = [f[l][k] for l in f for k in ("mot_drive", "mot_regen")]
        for lab, g in (("low", min(gb_vals)), ("high", max(gb_vals))):
            add("gearbox_eff (axle+gearbox)", f"{lab} {g:.3f}", run(cy, veh, T, S, V, A, G_, M, dt, {**vec, "gb": g})[0], "[VECTO] .vmod range over the 2 loadings and 2 directions")
        for lab, m in (("low", min(mot_vals)), ("high", max(mot_vals))):
            add("motor_eff (motor map incl. inverter)", f"{lab} {m:.3f}", run(cy, veh, T, S, V, A, G_, M, dt, {**vec, "mot": m})[0], "[VECTO] .vmod range over the 2 loadings and 2 directions")
        # regen: separate regen multiplier = VECTO regen vs drive values (asymmetric)
        add("regen chain separate from drive chain (VECTO drive and regen values)", "gb %.3f/%.3f, motor %.3f/%.3f" % (fr["gb_drive"], fr["gb_regen"], fr["mot_drive"], fr["mot_regen"]),
            _asym(cy, veh, T, S, V, A, G_, M, dt, vec, fr), "[VECTO] .vmod")
        rows_.append(dict(cycle=cycle, item="inverter_eff separately", setting="skipped", kWh_km=np.nan, d_kWh_km=np.nan, d_pct=np.nan, vs_vecto_pct=np.nan,
                          source="NO SOURCE: the VECTO E2 efficiency map already contains the inverter; no separate sourced value"))
        # v_no_regen
        for lab, vn in (("5 km/h [Constants.cs 323]", E.V_NO_REGEN_5), ("10 km/h [Constants.cs 321, GearboxData.cs 90-99, AMT]", E.V_NO_REGEN_10)):
            add("v_no_regen", lab, run(cy, veh, T, S, V, A, G_, M, dt, vec, v_no_regen=vn)[0], "[VECTO]")
        # P_regen_max: VECTO gen_max at the row (sourced); a constant would need NO SOURCE
        cap_row = np.interp(S, rw["S"], np.maximum(vv["P_E2-em_gen_max"], 0.0))       # VECTO limit at the same distance
        add("P_regen_max", "VECTO motor generating limit (per row)", run(cy, veh, T, S, V, A, G_, M, dt, vec, cap=cap_row)[0], "[VECTO] .vmod P_E2-em_gen_max")
        rows_.append(dict(cycle=cycle, item="P_regen_max single constant", setting="skipped", kWh_km=np.nan, d_kWh_km=np.nan, d_pct=np.nan, vs_vecto_pct=np.nan,
                          source="NO SOURCE for one number: E2 limit is speed-dependent (min / max over the Regional run: %.0f / %.0f kW)" % (vv["P_E2-em_gen_max"][vv["P_E2-em_gen_max"] > 0].min() / 1e3, vv["P_E2-em_gen_max"].max() / 1e3)))
        # gear / J_rotor
        add("gear for k_rot_rotor (parser default = lowest gear)", "gear 1 (i_total %.2f)" % E.I_TOTAL[1], run(cy, veh, T, S, V, A, G_, M, dt, vec, gear=1)[0], "[VECTO] AMT.vgbx")
        add("gear for k_rot_rotor (VECTO uses gear 2 in >99 % of driving rows)", "gear 2 (i_total %.2f)" % E.I_TOTAL[2], run(cy, veh, T, S, V, A, G_, M, dt, vec, gear=2)[0], "[VECTO] AMT.vgbx, .vmod Gear")
        add("J_rotor = 0 (rotor inertia not modelled, Appendix 1)", "0", run(cy, veh, T, S, V, A, G_, M, dt, vec, rotor_at_motor=False)[0], "[VECTO] ElectricMotor.cs 186-188")
        # aux rules
        add("Cond rule", "V>0 or stop PTO (Appendix 1)", run(cy, veh, T, S, V, A, G_, M, dt, vec, cond_rule="moving")[0], "[VECTO] Conditioning.cs 83-91 says motor-on")
        add("Cond rule", "motor on or E-PTO (VECTO)", run(cy, veh, T, S, V, A, G_, M, dt, vec, cond_rule="em_on")[0], "[VECTO] Conditioning.cs 83-91")
        add("coasting rule", "M==3 traction not forced to 0", run(cy, veh, T, S, V, A, G_, M, dt, vec, coast_zero=False)[0], "[VECTO] BatteryElectricMotorController.cs 44-47")
        add("sign decision", "one sign decision at the wheel (Appendix 1)", run(cy, veh, T, S, V, A, G_, M, dt, vec, split_sign=False)[0], "[VECTO] ElectricMotor.cs 297 / TransmissionLossMap")
        # scalar placeholders
        add("PLACEHOLDERS 0.95/0.95/0.98 instead of fitted VECTO values", "0.95 / 0.95 / 0.98", run(cy, veh, T, S, V, A, G_, M, dt, vec,
            drivetrain=dict(gearbox_eff=0.98, motor_eff=0.95, inverter_eff=0.95))[0], "HDEV placeholder (harness v1.7 line 50), flagged")

    write_csv("partD_scalar_eta_fit.csv", fits)
    write_csv("partD_sensitivity.csv", rows_)
    df = pd.DataFrame(tornado)
    _tornado(df)
    pd.set_option("display.width", 220, "display.max_colwidth", 70)
    print(pd.DataFrame(rows_)[["cycle", "item", "setting", "kWh_km", "d_pct", "vs_vecto_pct"]].round(3).to_string(index=False))
    print(pd.DataFrame(fits).round(4).to_string(index=False))


def _asym(cy, veh, T, S, V, A, G_, M, dt, vec, fr):
    """Direction-dependent scalar efficiencies: needs per-row arrays; sign of the row decides which value is used.
    Build the arrays from the engine's own sign decisions (wheel sign, motor sign)."""
    ratio = E.I_TOTAL[2]
    fe = E.forces(veh, V, A, dt, G_, E.J_ROTOR_TOTAL, ratio)
    wp_s = np.array([0.0, S[-1] + 1.0]); payload = np.array([veh.m_payload, np.nan])
    aux = dict(ES=vec["ES"], PS=vec["PS"], HVAC=vec["HVAC"], SP=vec["SP"], cond=vec["cond"], PTO_always_on=0.0)
    # pass 1 to get the wheel sign
    a0 = E.engine_args(veh, T, S, V, M, dt, fe, wp_s, payload, aux, E.no_pto(2), dict(gearbox_eff=1.0, motor_eff=1.0, inverter_eff=1.0), v_no_regen=E.V_NO_REGEN_10)
    r0 = RC.consumption_engine_v_split_eff(**a0)
    gb = np.where(r0["P_wheel"] > 0, fr["gb_drive"], fr["gb_regen"])
    mot = np.where(r0["P_motor"] > 0, fr["mot_drive"], fr["mot_regen"])
    a = E.engine_args(veh, T, S, V, M, dt, fe, wp_s, payload, aux, E.no_pto(2), dict(gearbox_eff=gb, motor_eff=mot, inverter_eff=1.0), v_no_regen=E.V_NO_REGEN_10)
    return RC.consumption_engine_v_split_eff(**a)["E_battery"] / (S[-1] / 1000.0)


def _tornado(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)
    for ax, cyc in zip(axes, ("RegionalDelivery", "UrbanDelivery")):
        d = df[df.cycle == cyc].copy()
        d["label"] = d["item"].str.slice(0, 48) + " | " + d["setting"].str.slice(0, 24)
        d = d.reindex(d.d_pct.abs().sort_values().index)
        ax.barh(d["label"], d.d_pct, color=np.where(d.d_pct >= 0, "tab:red", "tab:blue"))
        ax.axvline(5, ls="--", c="grey"); ax.axvline(-5, ls="--", c="grey")
        ax.set_title(f"{cyc}: change of kWh/km vs baseline [%] (dashed = 5 % target)")
        ax.tick_params(axis="y", labelsize=7)
    plt.tight_layout()
    p = os.path.join(HERE, "graph_partD_tornado.png")
    plt.savefig(p, dpi=110)
    print("wrote", os.path.relpath(p, E.REPO))


if __name__ == "__main__":
    main()
