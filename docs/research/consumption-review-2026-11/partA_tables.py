"""Part A tables (deterministic): numbers behind the answers to Q1-Q12 and the audit lists.

  partA_hardcoded_numbers.csv     every numeric literal in consumption_engine (AST scan of the notebook cell) with its class
  partA_unit_conversions.csv      unit conversions inside the function (rule 7: there should be none)
  partA_raises.csv                every raise, and whether the parser can check it before the driver model runs
  partA_q2_sign_decisions.csv     rows where the sign at the wheel differs from the sign at the gearbox / the motor map (VECTO .vmod)
  partA_q3_rotor_size.csv         size of the rotor inertia term per mission
  partA_q4_regen_rules.csv        regen speed limit evidence, generator limit vs battery limit, friction brake rows
  partA_q6_modes.csv              driver action vs motor on/off in VECTO
  partA_q8_sp_cond_rows.csv       SP and Cond activity: HDEV rules vs VECTO rows
  partA_q11_energy_columns.csv    which VECTO column is which energy
Sign conventions of every VECTO column used are in the header of partC_vecto_rows.py.
"""
import ast
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _e2 as E  # noqa: E402
from _common import write_csv  # noqa: E402
from _load_notebook import cell_sources  # noqa: E402
from partC_vecto_rows import CASES, per_row_eta  # noqa: E402
from tests.driver_model import _vmod as VM  # noqa: E402


def literals():
    src = [s for i, s in cell_sources() if "def consumption_engine" in s][0]
    lines = src.splitlines()
    tree = ast.parse(src.replace("\n  ", "\n ", 0))
    out, convs, raises = [], [], []
    klass = {
        3600: ("unit definition", "seconds per hour (hour index)"),
        273.15: ("unit definition", "0 deg C in kelvin: a unit conversion inside the engine (rule 7) -> goes (13 Nov decision 15)"),
        3.6: ("unit definition", "m/s -> km/h: a unit conversion inside the engine (rule 7) -> goes (13 Nov decision 15)"),
        3.6e6: ("unit definition", "J per kWh"),
        1e-3: ("HDEV choice", "tolerance [m] to find the rows of a stop; TIME = distance noise; not a VECTO constant"),
        0.0: ("neutral value", "no traction power"),
        1: ("index/shape", "searchsorted -1, 1 - w, +1 cell"),
        2: ("index/shape", "len(cdxa_v) - 2"),
        3: ("HDEV choice (mode code)", "driver mode M == 3 coasting (driver_model contract)"),
        4: ("HDEV choice (mode code)", "driver mode M == 4 braking (driver_model contract)"),
    }
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            ln = node.lineno
            key = (node.value, ln)
            if key in seen:
                continue
            seen.add(key)
            k, why = klass.get(node.value, ("?", ""))
            out.append(dict(line_in_cell=ln, value=node.value, class_=k, comment=why, code=lines[ln - 1].strip()[:110]))
        if isinstance(node, ast.Raise):
            raises.append(dict(line_in_cell=node.lineno, code=lines[node.lineno - 1].strip()[:110]))
    return out, raises


RAISE_NOTES = {
    "no standing rows found": ("needs driver rows (do the driver rows contain a standing run at this waypoint?)", "POST-DRIVER check; the parser can only check that the stop time > 0"),
    "PTO does not fit": ("stop length vs PTO length is known BEFORE the driver (stop_wp and pto_dur)", "PARSER check (parser extends the stop: standing = stop + PTO, VECTO DistanceBasedDrivingCycle.cs 218-220)"),
}


def q2_q3_q4_q6_q8():
    q2, q3, q4, q6, q8 = [], [], [], [], []
    for cyc, ld in CASES:
        rw = E.vecto_rows(cyc, ld)
        v, dt = rw["vecto"], rw["dt"]
        km = rw["S"][-1] / 1000
        wheel = v["P_wheel_in"]; wend = v["P_wheelEnd_in"]; gbx = v["P_gbx_in"]; mm = -v["P_E2-em_mech_map"]; el = -v["P_E2-em_el"]
        k = lambda x: float(np.sum(x * dt) / 3.6e6)
        on = (np.abs(el) > 1.0)
        # sign at wheel vs sign at gearbox input vs sign at motor map vs sign of electric power (rows with the motor on)
        s = lambda x: np.sign(np.where(np.abs(x) < 1.0, 0, x))
        a = on & (s(wend) != 0) & (s(wend) != s(gbx))
        b = on & (s(gbx) != 0) & (s(gbx) != s(mm))
        c = on & (s(mm) != 0) & (s(mm) != s(el))
        d = on & (s(wend) != 0) & (s(wend) != s(el))
        for lab, m in (("wheel-end sign != gearbox-in sign", a), ("gearbox-in sign != motor map sign (rotor term)", b),
                       ("motor map sign != electric sign (motor loss > power)", c), ("wheel sign != electric sign (all effects)", d)):
            q2.append(dict(cycle=cyc, loading=ld, rows_motor_on=int(on.sum()), test=lab, n_rows=int(m.sum()), share_pct=100 * m.sum() / on.sum(),
                           electric_kWh_on_these_rows=k(el * m), example_rows=str(np.where(m)[0][:4].tolist())))
        # Q3 rotor size
        rot = v["P_E2-em_inertia_loss"]
        q3.append(dict(cycle=cyc, loading=ld, rotor_abs_kWh=k(np.abs(rot)), rotor_net_kWh=k(rot), rotor_peak_kW=float(np.abs(rot).max() / 1000),
                       wheel_pos_kWh=k(np.maximum(wheel, 0)), rotor_abs_pct_of_wheel_pos=100 * k(np.abs(rot)) / k(np.maximum(wheel, 0)),
                       rotor_net_pct_of_terminal=100 * k(rot) / k(-v["P_REESS_T"])))
        # Q4
        brake_rows = (rw["action"] == -5) & (rw["A"] < -0.2)
        v1 = rw["V"] * 3.6
        emon = v["EM_off"] == 0
        emoff = v["EM_off"] == 1
        genmax = v["P_E2-em_gen_max"]
        regen_el = np.maximum(-el * 0 + (el * -1) * 0, 0)          # placeholder to keep arrays aligned
        regen_mech = np.maximum(-mm, 0)                           # generating mech power at the map
        q4.append(dict(cycle=cyc, loading=ld, braking_rows=int(brake_rows.sum()),
                       min_start_speed_kmh_EM_on_braking=float(v1[brake_rows & emon].min()), max_start_speed_kmh_EM_off_braking=float(v1[brake_rows & emoff].max()),
                       EM_off_braking_rows_start_speed_over_10=int((brake_rows & emoff & (v1 > 10)).sum()),
                       EM_off_braking_rows_start_speed_5_to_10=int((brake_rows & emoff & (v1 > 5) & (v1 <= 10)).sum()),
                       EM_on_braking_rows_start_speed_below_10=int((brake_rows & emon & (v1 < 10)).sum()),
                       regen_rows=int((mm < -1.0).sum() * 0 + (-mm > 1.0).sum()),
                       max_regen_mech_kW=float(np.maximum(-mm, 0).max() / 1000), min_gen_limit_kW_when_regen=float(genmax[(-mm) > 1.0].min() / 1000),
                       rows_regen_within_2pct_of_gen_limit=int(((-mm) > 0.98 * genmax)[genmax > 0].sum()),
                       battery_charge_limit_kW=float(v["P_wheel_in"].max() * 0 + VM.col(rw["cols"], "P_REESS_charge_max").max()),
                       max_regen_electric_kW=float(np.maximum(-el, 0).max() / 1000), friction_brake_kWh=k(v["P_brake_loss"]),
                       friction_brake_rows=int((v["P_brake_loss"] > 100).sum())))
        # Q6: VECTO action vs motor
        for act, name in ((0, "Halt"), (2, "Roll"), (4, "Coast"), (6, "Accelerate"), (-5, "Brake")):
            m = rw["action"] == act
            if m.any():
                q6.append(dict(cycle=cyc, loading=ld, DriverAction=act, name=name, hdev_mode=E.MODE_FROM_ACTION[act], rows=int(m.sum()),
                               EM_off_mean=float(v["EM_off"][m].mean()), rows_EM_fully_off=int((v["EM_off"][m] == 1).sum()),
                               rows_EM_fully_on=int((v["EM_off"][m] == 0).sum()), electric_kWh=k(el * m)))
        # Q8
        on_hdev = rw["V"] > 0
        sp_vecto = v["P_aux_STP_el"] > 0
        c_hdev_moving = on_hdev
        cond_vecto = v["P_aux_COND_el"] > 0
        em_on_rule = (rw["M"] != 0) & (rw["M"] != 3)
        q8.append(dict(cycle=cyc, loading=ld, rows=len(dt),
                       SP_hdev_V_gt_0=int(on_hdev.sum()), SP_vecto_rows_on=int(sp_vecto.sum()), SP_rows_differ=int((on_hdev != sp_vecto).sum()),
                       Cond_hdev_moving=int(c_hdev_moving.sum()), Cond_vecto_rows_on=int(cond_vecto.sum()), Cond_rows_differ_moving_rule=int((c_hdev_moving != cond_vecto).sum()),
                       Cond_rows_differ_motor_on_rule=int((em_on_rule != cond_vecto).sum()),
                       Cond_HDEV_on_VECTO_off=int((c_hdev_moving & ~cond_vecto).sum()), Cond_HDEV_off_VECTO_on=int((~c_hdev_moving & cond_vecto).sum()),
                       COND_vecto_kWh=k(v["P_aux_COND_el"]), SP_vecto_kWh=k(v["P_aux_STP_el"])))
    return q2, q3, q4, q6, q8


def q11():
    import csv
    r = list(csv.reader(open(os.path.join(E.REPO, "docs", "research", "vecto", "BEV_E2.vsum"), encoding="utf-8-sig")))
    h = r[1]
    col = lambda n: h.index(n)
    rows = []
    for rr in r[2:]:
        if len(rr) < len(h) - 1 or rr[0].startswith('#'):
            continue
        rows.append(dict(job=rr[0], cycle=rr[2], loading_kg=rr[col("Loading [kg]")], km=rr[col("distance [km]")],
                         EC_el_SoC=rr[col("EC_el_SoC [kWh]")], EC_el_SoC_corr=rr[col("EC_el_SoC_corr [kWh]")], EC_el_final=rr[col("EC_el_final [kWh]")],
                         EC_el_final_kWh_km=rr[col("EC_el_final [kWh/km]")], E_REESS_T_dischg=rr[col("E_REESS_T_dischg [kWh]")],
                         E_REESS_T_chg=rr[col("E_REESS_T_chg [kWh]")], E_REESS_int_dischg=rr[col("E_REESS_int_dischg [kWh]")],
                         E_REESS_int_chg=rr[col("E_REESS_int_chg [kWh]")], E_REESS_loss=rr[col("E_REESS_loss [kWh]")], dE_REESS=rr[col("ΔE_REESS [kWh]")],
                         E_aux_sum_el=rr[col("E_aux_sum_el [kWh]")]))
    return rows


def q7():
    """Q7: battery terminal power = motor electric power - aux power (aux straight to the HV battery, DC/DC efficiency 1.0)."""
    rows = []
    for cyc, ld in CASES:
        rw = E.vecto_rows(cyc, ld)
        v = rw["vecto"]
        res = v["P_REESS_T"] - (v["P_E2-em_el"] - v["P_aux_el"])
        dcdc_in = VM.col(rw["cols"], "P_DC/DC_In") * 1000.0
        dcdc_out = VM.col(rw["cols"], "P_DC/DC_Out") * 1000.0
        rows.append(dict(cycle=cyc, loading=ld, max_abs_W_P_REESS_T_minus_em_el_plus_aux=float(np.abs(res).max()),
                         rms_W=float(np.sqrt(np.mean(res ** 2))), max_abs_W_DCDC_in_minus_out=float(np.abs(dcdc_in - dcdc_out).max()),
                         max_abs_W_DCDC_out_minus_P_aux_el=float(np.abs(dcdc_out - v["P_aux_el"]).max()),
                         vmod_rounding_W=0.1))
    return rows


def main():
    lit, rs = literals()
    write_csv("partA_q7_battery_identity.csv", q7())
    write_csv("partA_hardcoded_numbers.csv", lit)
    conv = [x for x in lit if x["value"] in (273.15, 3.6)]
    write_csv("partA_unit_conversions.csv", conv)
    raws = []
    for r in rs:
        note = next((v for k_, v in RAISE_NOTES.items() if k_ in r["code"] or k_ in "no standing rows found" and "no standing" in r["code"]), None)
        r2 = dict(r)
        if "no standing" in r["code"]:
            note = RAISE_NOTES["no standing rows found"]
        elif "does not fit" in r["code"]:
            note = RAISE_NOTES["PTO does not fit"]
        r2["can_parser_check_before_driver"] = note[0] if note else ""
        r2["where_the_check_belongs"] = note[1] if note else ""
        raws.append(r2)
    write_csv("partA_raises.csv", raws)
    q2, q3, q4, q6, q8 = q2_q3_q4_q6_q8()
    write_csv("partA_q2_sign_decisions.csv", q2)
    write_csv("partA_q3_rotor_size.csv", q3)
    write_csv("partA_q4_regen_rules.csv", q4)
    write_csv("partA_q6_modes.csv", q6)
    write_csv("partA_q8_sp_cond_rows.csv", q8)
    write_csv("partA_q11_energy_columns.csv", q11())


if __name__ == "__main__":
    main()
