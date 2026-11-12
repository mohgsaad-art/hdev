"""Minimal call of the notebook consumption_engine on a synthetic route (ILLUSTRATIVE numbers; traction forces are zero
so only the aux/PTO part of steps 6-7 contributes)."""
import numpy as np
from _load_notebook import NS


def call_ce(route, ES=0.0, PS=0.0, HVAC=0.0, SP=0.0, cond=0.0, PTO_always_on=0.0, pto_1s=(), pto_on_col=None, pto_start_col=None):
    n = len(route["S"])
    n_wp = len(route["wp_s"])
    z = np.zeros(n)
    payload = np.full(n_wp, np.nan)
    payload[0] = 0.0
    pto_on_col = np.zeros(n_wp) if pto_on_col is None else pto_on_col
    pto_start_col = np.full(n_wp, np.nan) if pto_start_col is None else pto_start_col
    return NS["consumption_engine"](
        T=route["T"], S=route["S"], V=route["V"], M=route["M"], dt=1.0,
        k_lin=z, k_roll=z, k_rot=z, L=z, v_avg=z,
        m_vehicle=1000.0, wp_s=route["wp_s"], payload_wp=payload, beta=1.0,
        t_start=0.0, T_amb_h=np.full(3, 20.0), W1=np.ones((3, 2)), W2=np.zeros((3, 2)), cdxa_v=np.array([60.0, 100.0]),
        CdxA0=1.0, p_air=101325.0, R_air=287.05,
        ES=ES, PS=PS, HVAC=HVAC, SP=SP, cond=cond, PTO_always_on=PTO_always_on,
        pto_1s=np.asarray(pto_1s, dtype=float), pto_on_col=pto_on_col, pto_start_col=pto_start_col,
        motor_eff=0.9, inverter_eff=0.95, gearbox_eff=0.97, regen_effeiciency=0.8, v_no_regen=5 / 3.6)
