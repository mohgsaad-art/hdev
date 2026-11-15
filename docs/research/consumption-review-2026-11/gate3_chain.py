"""Gate 3: does the REAL chain driver_model -> force_engine -> pto_engine -> P_aux -> consumption_engine run?

Expected (Appendix 1 vs Appendix 2): NO.  This script
  1. runs the real producers on E2 Regional, Urban and MunicipalUtility (refuse),
  2. tries three natural ways to hand their outputs to the 13 Nov consumption_engine and records the exact exception,
  3. runs the minimal adapter consumption_engine_v_signature_only (rename only) and checks that it gives the old function's numbers
     when k_rot_rotor = 0 and PTO is off (and with the stop PTO of the refuse cycle).
Writes gate3_chain.csv.   Run: python gate3_chain.py   (deterministic)
"""
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _e2 as E  # noqa: E402
import _rows as R  # noqa: E402
import reference_copy as RC  # noqa: E402
from _common import BETA, G  # noqa: E402

LOADING = "ReferenceLoad"
VPTO_T, VPTO_W = R.__dict__.get("VPTOEL_T"), None
from _scenarios import VPTOEL_T, VPTOEL_W, VPTOEL_KWH  # noqa: E402

AUX_NOMINAL = {"RegionalDelivery": (1000.0, 200.0, 250.0), "UrbanDelivery": (1000.0, 162.0, 187.5), "MunicipalUtility": (1000.0, 162.0, 187.5)}
# ^ ES, PS, HVAC electric W read from the E2 .vmod columns (P_aux_ES_el, P_aux_PS_el, P_aux_AC_el); Municipal has no group-2 .vmod -> Urban values [ASSUMPTION]


def build(cycle):
    cy = R.read_vdri(cycle)
    pto_flag = cy["pto"] == 1
    pto_dur = len(VPTOEL_T) - 1 if cycle == "MunicipalUtility" else 0
    stop_final = cy["stop"].copy()
    if cycle == "MunicipalUtility":
        stop_final[pto_flag] += pto_dur
    T, S, V, A, Gr, M = R.run_driver_e2(cy, LOADING, stop_override=stop_final)
    veh = E.veh_for("RegionalDelivery" if cycle == "MunicipalUtility" else cycle, LOADING)
    dt = np.diff(T, append=T[-1] + 1.0)
    fe = E.forces(veh, V, A, dt, Gr, E.J_ROTOR_TOTAL, E.I_TOTAL[2])
    payload = E.payload_engine(cy["stop"], "constant", veh.m_payload)
    es, ps, hv = AUX_NOMINAL[cycle]
    aux6 = E.P_aux(es, ps, hv, 20.0, 600.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    pto_out = E.pto_engine(stop_final, pto_flag.astype(float), VPTOEL_T if cycle == "MunicipalUtility" else [0.0],
                           VPTOEL_W if cycle == "MunicipalUtility" else [0.0], [0.0], [0.0], 1.0, 1.0)
    return dict(cy=cy, T=T, S=S, V=V, A=A, Gr=Gr, M=M, veh=veh, dt=dt, fe=fe, payload=payload, aux6=aux6, pto_out=pto_out,
                stop_final=stop_final, n_pto=int(pto_flag.sum()))


def attempt(label, fn):
    try:
        res = fn()
        return dict(attempt=label, outcome="RAN", detail=f"E_battery={float(res[-1]):.4f} kWh")
    except Exception as e:  # noqa: BLE001
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return dict(attempt=label, outcome="FAILED", detail=f"{type(e).__name__}: {str(e)[:160]}")


def main():
    rows = []
    for cycle in ("RegionalDelivery", "UrbanDelivery", "MunicipalUtility"):
        b = build(cycle)
        veh, fe = b["veh"], b["fe"]
        NH = int(b["T"][-1] // 3600) + 2
        is_on, pto_start, stop_1s, drive_1s = b["pto_out"]
        ES, PS, HVAC, SP, cond, PTO_a = b["aux6"]
        common = dict(m_vehicle=veh.m_empty, wp_s=b["cy"]["s"], payload_wp=b["payload"], beta=BETA, t_start=0.0,
                      T_amb_h=np.full(NH, E.T_K_VECTO - 273.15), W1=np.tile(E.crosswind_tables(veh)[0], (NH, 1)),
                      W2=np.tile(E.crosswind_tables(veh)[1], (NH, 1)), cdxa_v=E.CDXA_V, CdxA0=veh.cdxa0, p_air=E.P_AIR, R_air=E.R_AIR,
                      ES=ES, PS=PS, HVAC=HVAC, SP=SP, cond=cond, PTO_always_on=PTO_a,
                      motor_eff=E.MOTOR_EFF, inverter_eff=E.INVERTER_EFF, gearbox_eff=E.GEARBOX_EFF,
                      regen_effeiciency=E.REGEN_EFF_HARNESS, v_no_regen=E.V_NO_REGEN_5)
        ce = E.NS["consumption_engine"]
        # N1: positional hand-over, force_engine returns 6 values, the function expects 5 -> everything shifts by one
        rows.append(dict(cycle=cycle, **attempt("N1 positional: consumption_engine(T,S,V,M,dt, *force_engine_out, m_vehicle, ...)",
                         lambda: ce(b["T"], b["S"], b["V"], b["M"], b["dt"], *fe, common["m_vehicle"], common["wp_s"], common["payload_wp"],
                                    BETA, 0.0, common["T_amb_h"], common["W1"], common["W2"], common["cdxa_v"], common["CdxA0"], E.P_AIR,
                                    E.R_AIR, ES, PS, HVAC, SP, cond, PTO_a, stop_1s, is_on, pto_start, E.MOTOR_EFF, E.INVERTER_EFF,
                                    E.GEARBOX_EFF, E.REGEN_EFF_HARNESS, E.V_NO_REGEN_5))))
        # N2: by name, new force_engine names
        rows.append(dict(cycle=cycle, **attempt("N2 keyword: k_rot_wheel=..., k_rot_rotor=...",
                         lambda: ce(T=b["T"], S=b["S"], V=b["V"], M=b["M"], dt=b["dt"], k_lin=fe[0], k_roll=fe[1], k_rot_wheel=fe[2],
                                    k_rot_rotor=fe[3], L=fe[4], v_avg=fe[5], pto_1s=stop_1s, pto_on_col=is_on, pto_start_col=pto_start,
                                    **common))))
        # N3: force names fixed by hand (k_rot_wheel -> k_rot, rotor dropped), pto_engine outputs handed over IN ITS RETURN ORDER
        #     pto_engine returns (is_on, pto_start, stop_1s, drive_1s); the function wants (pto_1s, pto_on_col, pto_start_col)
        rows.append(dict(cycle=cycle, **attempt("N3 pto_engine outputs in return order -> (pto_1s, pto_on_col, pto_start_col)",
                         lambda: ce(T=b["T"], S=b["S"], V=b["V"], M=b["M"], dt=b["dt"], k_lin=fe[0], k_roll=fe[1], k_rot=fe[2], L=fe[4],
                                    v_avg=fe[5], pto_1s=is_on, pto_on_col=pto_start, pto_start_col=stop_1s, **common))))
        # adapter, rotor 0 and PTO off  == old function
        zero_rotor = np.zeros_like(fe[3])
        no_pto = (np.zeros(len(b["cy"]["s"])), np.full(len(b["cy"]["s"]), np.nan), np.zeros(0), np.zeros(0))
        old = ce(T=b["T"], S=b["S"], V=b["V"], M=b["M"], dt=b["dt"], k_lin=fe[0], k_roll=fe[1], k_rot=fe[2], L=fe[4], v_avg=fe[5],
                 pto_1s=np.zeros(0), pto_on_col=no_pto[0], pto_start_col=no_pto[1], **common)
        ad = RC.consumption_engine_v_signature_only(b["T"], b["S"], b["V"], b["M"], b["dt"], fe[0], fe[1], fe[2], zero_rotor, fe[4], fe[5],
                                                    common["m_vehicle"], common["wp_s"], common["payload_wp"], BETA, 0.0, common["T_amb_h"],
                                                    common["W1"], common["W2"], common["cdxa_v"], common["CdxA0"], E.P_AIR, E.R_AIR,
                                                    ES, PS, HVAC, SP, cond, PTO_a, no_pto[0], no_pto[1], no_pto[2], no_pto[3],
                                                    E.MOTOR_EFF, E.INVERTER_EFF, E.GEARBOX_EFF, E.REGEN_EFF_HARNESS, E.V_NO_REGEN_5)
        same = all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(old, ad))
        km = b["S"][-1] / 1000
        rows.append(dict(cycle=cycle, attempt="ADAPTER (rename only), k_rot_rotor=0, PTO off, vs old function", outcome="IDENTICAL" if same else "DIFFERENT",
                         detail=f"E_battery={ad[-1]:.4f} kWh ({ad[-1] / km:.4f} kWh/km); all 5 outputs bit-identical: {same}"))
        # adapter refuses what it cannot carry
        try:
            RC.consumption_engine_v_signature_only(b["T"], b["S"], b["V"], b["M"], b["dt"], fe[0], fe[1], fe[2], fe[3], fe[4], fe[5],
                                                   common["m_vehicle"], common["wp_s"], common["payload_wp"], BETA, 0.0, common["T_amb_h"],
                                                   common["W1"], common["W2"], common["cdxa_v"], common["CdxA0"], E.P_AIR, E.R_AIR,
                                                   ES, PS, HVAC, SP, cond, PTO_a, no_pto[0], no_pto[1], no_pto[2], no_pto[3],
                                                   E.MOTOR_EFF, E.INVERTER_EFF, E.GEARBOX_EFF, E.REGEN_EFF_HARNESS, E.V_NO_REGEN_5)
            msg = "ran"
        except ValueError as e:
            msg = f"refused: {e}"
        rows.append(dict(cycle=cycle, attempt="ADAPTER with real k_rot_rotor (rotor would be lost)", outcome="REFUSED" if "refused" in msg else "RAN",
                         detail=msg))
        # refuse cycle with its stop PTO through the adapter
        if cycle == "MunicipalUtility":
            ad2 = RC.consumption_engine_v_signature_only(b["T"], b["S"], b["V"], b["M"], b["dt"], fe[0], fe[1], fe[2], zero_rotor, fe[4], fe[5],
                                                         common["m_vehicle"], common["wp_s"], common["payload_wp"], BETA, 0.0, common["T_amb_h"],
                                                         common["W1"], common["W2"], common["cdxa_v"], common["CdxA0"], E.P_AIR, E.R_AIR,
                                                         ES, PS, HVAC, SP, cond, PTO_a, is_on, pto_start, stop_1s, drive_1s,
                                                         E.MOTOR_EFF, E.INVERTER_EFF, E.GEARBOX_EFF, E.REGEN_EFF_HARNESS, E.V_NO_REGEN_5)
            pto_kwh = float(ad2[2].sum() - ad[2].sum()) / 3.6e6
            rows.append(dict(cycle=cycle, attempt="ADAPTER with stop PTO on (96 stops expected)", outcome="RAN",
                             detail=f"PTO + Cond-extension energy = {pto_kwh:.3f} kWh; stops with PTO = {b['n_pto']}; "
                                    f"96 x {VPTOEL_KWH:.5f} = {96 * VPTOEL_KWH:.3f} kWh (Cond 600 W x PTO rows is included in the first number)"))
    df = pd.DataFrame(rows)[["cycle", "attempt", "outcome", "detail"]]
    p = os.path.join(HERE, "gate3_chain.csv")
    df.to_csv(p, index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 140)
    print(df.to_string(index=False))
    print("wrote", os.path.relpath(p, E.REPO))


if __name__ == "__main__":
    main()
