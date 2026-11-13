"""Part C: row-level reproduction of VECTO with VECTO's OWN rows.

Feeds each E2 .vmod (speed, acceleration, grade, dt, gear, mode) into the real force_engine (13 Nov) and into the engine variants.
Purpose: prove the ASSEMBLY LOGIC separately from the EFFICIENCY ASSUMPTIONS.

  C2  "VECTO efficiencies": per-row efficiencies computed from the .vmod power columns of each component (axle+gearbox, motor map incl. inverter),
      per-row regen limit = P_E2-em_gen_max, VECTO's own aux rows.  Whatever is left over is a LOGIC difference.
  C3  "HDEV placeholders": 0.95 / 0.95 / 0.98, regen 0.884 (harness v1.7 lines 50-51), v_no_regen 5 km/h (line 52), nominal aux.
  C4  tables per file and column, flagged rows explained.
  C5  causes isolated one at a time (switches of consumption_engine_v_split_eff).

Sign conventions (checked in the .vmod, Part A): VECTO P_wheel_in, P_axle_in, P_gbx_in: + = driving.  P_E2-em_mech_map, P_E2-em_el:
- = motor drives / draws electricity.  P_REESS_T: - = battery discharges.  In this script everything is converted to the HDEV convention
(+ = driving / drawn from battery) before it is compared.

Run: python partC_vecto_rows.py   (deterministic)
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _e2 as E  # noqa: E402
import reference_copy as RC  # noqa: E402
from _common import BETA, write_csv  # noqa: E402

CASES = [(c, l) for c in ("RegionalDelivery", "UrbanDelivery", "LongHaul") for l in ("ReferenceLoad", "LowLoading")]
SMALL_W, REL = 100.0, 0.01


def per_row_eta(v):
    """Per-row efficiencies that VECTO actually had, from the .vmod columns (all W).  HDEV sign: + driving."""
    wheelEnd, gbx = v["P_wheelEnd_in"], v["P_gbx_in"]
    # axle+gearbox: driving rows eta = wheelEnd / gbx_in ; regen rows eta = gbx_in / wheelEnd.
    # The ratio is SIGNED: at small regen power the constant (no-load) loss of axle + gearbox is larger than the power, the motor has to PUSH
    # (gbx_in > 0 while the wheel power is < 0).  A negative "efficiency" is the only way the single multiply can reproduce such a row.
    big = np.abs(wheelEnd) > 1.0
    eta_gb = np.ones_like(wheelEnd)
    d_, r_ = big & (wheelEnd > 0), big & (wheelEnd < 0)
    eta_gb[d_] = wheelEnd[d_] / np.where(np.abs(gbx[d_]) > 1e-9, gbx[d_], 1e-9)
    eta_gb[r_] = gbx[r_] / wheelEnd[r_]
    mech, el = -v["P_E2-em_mech_map"], -v["P_E2-em_el"]            # HDEV sign: + = motor drives / draws
    a, b = np.abs(mech), np.abs(el)
    on = (a > 1.0) & (b > 1.0)
    drive = on & (mech > 0)
    regen = on & (mech < 0)
    eta_m = np.ones_like(mech)
    eta_m[drive] = (mech[drive] / el[drive])                       # mech out / electric in
    eta_m[regen] = (el[regen] / mech[regen])                       # electric out / mech in (NEGATIVE when the motor still draws power while generating)
    return eta_gb, eta_m, int(((eta_gb < 0) | (eta_m < 0)).sum())


def stats(name, h, v, dt):
    Eh, Ev = h * dt / 3.6e6, v * dt / 3.6e6
    d = h - v
    flag = (np.abs(d) > SMALL_W) & (np.abs(d) > REL * np.abs(v))
    i = int(np.argmax(np.abs(d)))
    pct = lambda a, b: (a / b - 1) * 100 if abs(b) > 1e-9 else np.nan
    return dict(column=name, vecto_net=Ev.sum(), vecto_pos=Ev[Ev > 0].sum(), vecto_neg=Ev[Ev < 0].sum(),
                hdev_net=Eh.sum(), hdev_pos=Eh[Eh > 0].sum(), hdev_neg=Eh[Eh < 0].sum(),
                d_net_kWh=Eh.sum() - Ev.sum(), d_net_pct=pct(Eh.sum(), Ev.sum()),
                d_pos_pct=pct(Eh[Eh > 0].sum(), Ev[Ev > 0].sum()), d_neg_pct=pct(Eh[Eh < 0].sum(), Ev[Ev < 0].sum()),
                rms_W=float(np.sqrt(np.mean(d ** 2))), max_abs_W=float(abs(d[i])), max_at_row=i, n_flagged=int(flag.sum()), n_rows=len(d))


def build(case, zero_gear_to=0):
    cycle, loading = case
    rw = E.vecto_rows(cycle, loading)
    veh = rw["veh"]
    ratio = E.i_total_from_gear(rw["gear"], zero_gear_to)
    fe = E.forces(veh, rw["V"], rw["A"], rw["dt"], rw["grade"], E.J_ROTOR_TOTAL, ratio)
    n_wp = 2
    wp_s = np.array([0.0, rw["S"][-1] + 1.0])
    payload = np.array([veh.m_payload, np.nan])
    v = rw["vecto"]
    on = rw["V"] > 0
    nominal = dict(ES=float(v["P_aux_ES_el"].max()), PS=float(v["P_aux_PS_el"].max()), HVAC=float(v["P_aux_AC_el"].max()),
                   SP=float(v["P_aux_STP_el"][on].mean()) if on.any() else 0.0, cond=float(v["P_aux_COND_el"].max()), PTO_always_on=0.0)
    return rw, veh, fe, wp_s, payload, nominal


def run_case(case, out_rows, cause_rows, flag_rows):
    rw, veh, fe, wp_s, payload, nominal = build(case)
    v = rw["vecto"]
    cycle, loading = case
    dt = rw["dt"]
    eta_gb, eta_m, _ = per_row_eta(v)
    cap = np.maximum(v["P_E2-em_gen_max"], 0.0)
    # ----- pieces to compare, HDEV sign
    VEC = {"wheel": v["P_wheel_in"], "gearbox_in": v["P_gbx_in"], "motor_mech(map)": -v["P_E2-em_mech_map"], "motor_el": -v["P_E2-em_el"],
           "aux": v["P_aux_el"], "battery_terminal": -v["P_REESS_T"]}
    km = rw["S"][-1] / 1000.0
    pto = E.no_pto(2)

    def args(**kw):
        base = E.engine_args(veh, rw["T"], rw["S"], rw["V"], rw["M"], dt, fe, wp_s, payload, nominal, pto,
                             dict(gearbox_eff=eta_gb, motor_eff=eta_m, inverter_eff=1.0), P_regen_max=cap, v_no_regen=E.V_NO_REGEN_10)
        base.update(kw)
        return base

    def go(label, a, **sw):
        r = RC.consumption_engine_v_split_eff(**a, **sw)
        return label, r

    runs = {}
    # C2 logic test: VECTO efficiencies, VECTO aux rows, VECTO regen cap, 10 km/h (the E2 AMT value)
    runs["C2 VECTO eff, split sign, rotor at motor, VECTO aux"] = RC.consumption_engine_v_split_eff(
        **args(), aux_row_override=v["P_aux_el"])
    # C2b: same but Appendix-1-style: one sign, no rotor, 5 km/h, no cap  (= how the code of record would behave with VECTO's efficiencies)
    runs["C2b VECTO eff, Appendix-1 logic (one sign, no rotor, 5 km/h, no cap)"] = RC.consumption_engine_v_split_eff(
        **args(P_regen_max=None, v_no_regen=E.V_NO_REGEN_5), split_sign=False, rotor_at_motor=False, aux_row_override=v["P_aux_el"])
    # C3 placeholders
    ph = dict(gearbox_eff=E.GEARBOX_EFF, motor_eff=E.MOTOR_EFF, inverter_eff=E.INVERTER_EFF)
    runs["C3 placeholders, proposed logic, nominal aux"] = RC.consumption_engine_v_split_eff(**args(**ph, P_regen_max=None, v_no_regen=E.V_NO_REGEN_10))
    runs["C3b placeholders, proposed logic, VECTO aux rows"] = RC.consumption_engine_v_split_eff(**args(**ph, P_regen_max=None, v_no_regen=E.V_NO_REGEN_10),
                                                                                                aux_row_override=v["P_aux_el"])
    # the REAL notebook function with placeholders (code of record, as is)
    old = E.NS["consumption_engine"](**E.to_old_args(args(**ph, P_regen_max=None, v_no_regen=E.V_NO_REGEN_5)),)
    runs["C3c code of record (13 Nov), placeholders, nominal aux"] = dict(P_wheel=old[0], P_shaft=np.full(len(dt), np.nan), P_motor=np.full(len(dt), np.nan),
                                                                          P_trac=old[1], P_aux_row=old[2], P_battery=old[3], E_battery=old[4])
    # the REAL notebook function with VECTO's per-row efficiencies (single sign, no rotor, no cap)
    a_old = args(P_regen_max=None, v_no_regen=E.V_NO_REGEN_5)
    old_arg = E.to_old_args(a_old)
    old_arg["regen_effeiciency"] = eta_gb * eta_m
    old_arg["inverter_eff"] = 1.0
    old2 = E.NS["consumption_engine"](**old_arg)
    runs["C2c code of record (13 Nov), VECTO per-row eff, nominal aux"] = dict(P_wheel=old2[0], P_shaft=np.full(len(dt), np.nan), P_motor=np.full(len(dt), np.nan),
                                                                              P_trac=old2[1], P_aux_row=old2[2], P_battery=old2[3], E_battery=old2[4])

    HDEV_COL = {"wheel": "P_wheel", "gearbox_in": "P_shaft", "motor_mech(map)": "P_motor", "motor_el": "P_trac", "aux": "P_aux_row",
                "battery_terminal": "P_battery"}
    for label, r in runs.items():
        for col, vv in VEC.items():
            h = np.asarray(r[HDEV_COL[col]], dtype=float)
            if np.all(np.isnan(h)):
                continue
            s = stats(col, h, vv, dt)
            s.update(cycle=cycle, loading=loading, variant=label, kWh_km_hdev=s["hdev_net"] / km, kWh_km_vecto=s["vecto_net"] / km)
            out_rows.append(s)

    # ----- C5 causes isolated, one at a time from the C2 logic test (everything else as C2)
    ref = runs["C2 VECTO eff, split sign, rotor at motor, VECTO aux"]
    ev = lambda r: float(np.sum(r["P_battery"] * dt) / 3.6e6)
    e_vecto = float(np.sum(VEC["battery_terminal"] * dt) / 3.6e6)

    def cause(name, **kw):
        a = args()
        a.update({k: kw.pop(k) for k in list(kw) if k in a})
        kw.setdefault("aux_row_override", v["P_aux_el"])
        r = RC.consumption_engine_v_split_eff(**a, **kw)
        cause_rows.append(dict(cycle=cycle, loading=loading, cause=name, E_kWh=ev(r), vecto_kWh=e_vecto, d_vs_vecto_kWh=ev(r) - e_vecto,
                               d_vs_vecto_pct=(ev(r) / e_vecto - 1) * 100, d_vs_C2_kWh=ev(r) - ev(ref),
                               rms_W_battery=float(np.sqrt(np.mean((r["P_battery"] - VEC["battery_terminal"]) ** 2)))))
    cause("0  all switches at proposal (C2)")
    cause("a  one sign decision at the wheel (Appendix 1) instead of per component", split_sign=False)
    cause("b  rotor inertia dropped (Appendix 1 has no k_rot_rotor)", rotor_at_motor=False)
    cause("c  regen speed limit 5 km/h instead of 10 km/h", v_no_regen=E.V_NO_REGEN_5)
    cause("c2 no low-speed braking rule at all", low_speed_rule=False)
    cause("d  no regen cap (P_regen_max = None)", P_regen_max=None)
    cause("f  coasting not forced to zero traction", coast_zero=False)
    # (e) aux rule: use nominal aux with HDEV rules instead of VECTO's aux rows
    for rule, mr in (("moving", "start_speed"), ("em_on", "start_speed")):
        a = args()
        r = RC.consumption_engine_v_split_eff(**a, cond_rule=rule)
        cause_rows.append(dict(cycle=cycle, loading=loading, cause=f"e  nominal aux, Cond rule = {rule}", E_kWh=ev(r), vecto_kWh=e_vecto,
                               d_vs_vecto_kWh=ev(r) - e_vecto, d_vs_vecto_pct=(ev(r) / e_vecto - 1) * 100, d_vs_C2_kWh=ev(r) - ev(ref),
                               rms_W_battery=float(np.sqrt(np.mean((r["P_battery"] - VEC["battery_terminal"]) ** 2)))))

    # ----- flagged rows of the C2 logic test, classified (battery terminal)
    d = ref["P_battery"] - VEC["battery_terminal"]
    fl = (np.abs(d) > SMALL_W) & (np.abs(d) > REL * np.abs(VEC["battery_terminal"]))
    em_mixed = (v["EM_off"] > 0.001) & (v["EM_off"] < 0.999)
    act = rw["action"]
    act_prev, act_next = np.r_[act[0], act[:-1]], np.r_[act[1:], act[-1]]
    change = (act != act_prev) | (act != act_next)
    low_brake = (rw["M"] == 4) & (rw["V"] <= E.V_NO_REGEN_10)
    capb = (VEC["wheel"] < 0) & (v["P_brake_loss"] > 100)
    cls = np.where(em_mixed, "1 motor on only part of the 1 s row (EM_off between 0 and 1)",
          np.where(change, "2 driver action changes inside +-1 row (1 Hz averaging of ~0.5 s steps)",
          np.where(low_brake, "3 low-speed braking row",
          np.where(capb, "4 friction brake used (regen cap)", "5 other"))))
    for c in sorted(set(cls[fl])) if fl.any() else []:
        m = fl & (cls == c)
        flag_rows.append(dict(cycle=cycle, loading=loading, cause_class=c, n_rows=int(m.sum()), share_of_flagged_pct=100 * m.sum() / fl.sum(),
                              abs_diff_kWh=float(np.abs(d[m]).sum() / 3.6e6), net_diff_kWh=float(d[m].sum() / 3.6e6), max_abs_W=float(np.abs(d[m]).max())))
    flag_rows.append(dict(cycle=cycle, loading=loading, cause_class="ALL flagged (>0.1 kW and >1 % of the VECTO value)", n_rows=int(fl.sum()),
                          share_of_flagged_pct=100.0, abs_diff_kWh=float(np.abs(d[fl]).sum() / 3.6e6), net_diff_kWh=float(d[fl].sum() / 3.6e6),
                          max_abs_W=float(np.abs(d[fl]).max()) if fl.any() else 0.0))
    # extra bookkeeping used in the report
    return dict(cycle=cycle, loading=loading, km=km, rows=len(dt), brake_loss_kWh=float(np.sum(v["P_brake_loss"] * dt) / 3.6e6),
                gen_cap_rows=int(((VEC["wheel"] < 0) & (v["P_brake_loss"] > 100)).sum()))


def main():
    out_rows, cause_rows, flag_rows, extra = [], [], [], []
    for c in CASES:
        extra.append(run_case(c, out_rows, cause_rows, flag_rows))
    write_csv("partC_columns.csv", out_rows)
    write_csv("partC_causes.csv", cause_rows)
    write_csv("partC_flagged_rows.csv", flag_rows)
    write_csv("partC_extra.csv", extra)
    df = pd.DataFrame(out_rows)
    t = df[(df.column == "battery_terminal")][["cycle", "loading", "variant", "vecto_net", "hdev_net", "d_net_kWh", "d_net_pct", "d_pos_pct", "d_neg_pct", "rms_W"]]
    pd.set_option("display.width", 250, "display.max_colwidth", 70)
    print(t.round(3).to_string(index=False))
    print(pd.DataFrame(cause_rows)[["cycle", "loading", "cause", "d_vs_vecto_pct", "d_vs_C2_kWh"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
