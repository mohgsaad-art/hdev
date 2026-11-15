"""ILLUSTRATIVE synthetic rows for the unit tests.  Every number here is ILLUSTRATIVE (rule 2 of the prompt), none is a model input."""
import numpy as np

import _e2 as E
from _load_notebook import NS

force_engine = NS["force_engine"]


def rows(n_stand=5, n_acc=10, n_cruise=20, n_brake=10, v_cruise=10.0):
    """Illustrative 1 s rows: standing, accelerating (a = v/n), cruising, braking to a stop.  M: 0 standing, 1 acc, 2 cruise, 4 braking."""
    a_up, a_dn = v_cruise / n_acc, -v_cruise / n_brake
    V, A, M = [], [], []
    v = 0.0
    for _ in range(n_stand):
        V.append(0.0); A.append(0.0); M.append(0)
    for _ in range(n_acc):
        V.append(v); A.append(a_up); M.append(1); v += a_up
    for _ in range(n_cruise):
        V.append(v); A.append(0.0); M.append(2)
    for _ in range(n_brake):
        V.append(v); A.append(a_dn); M.append(4); v += a_dn
    V, A, M = np.array(V), np.array(A), np.array(M)
    n = len(V)
    S = np.concatenate(([0.0], np.cumsum((V + np.maximum(V + A, 0)) / 2)[:-1]))
    return dict(T=np.arange(n, dtype=float), S=S, V=V, A=A, M=M, dt=np.ones(n), n=n)


def base_args(r=None, aux=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0), eff=(1.0, 1.0, 1.0), v_no_regen=5 / 3.6, cap=None, J_rotor=0.0, i_total=10.0,
              mass=9000.0, payload=1000.0, nh=3, T_K=288.15, drive_mech=False):
    """Argument dict (new names, SI) for consumption_engine_v_proposed / _split_eff.  ILLUSTRATIVE vehicle:
    Crr 0.006, theta_red 40, r_dyn 0.42, CdxA 5 m2 flat, beta 0.9."""
    r = r or rows()
    fe = force_engine(9.80665, 0.006, r["V"], r["A"], r["dt"], np.zeros(r["n"]), 0.42, 40.0, J_rotor, i_total)
    ES, PS, HVAC, SP, cond, PTOa = aux
    wp_s = np.array([0.0, r["S"][-1] + 1.0])
    W1 = np.ones((nh, 3)); W2 = np.zeros((nh, 3))
    return dict(T=r["T"], S=r["S"], V=r["V"], M=r["M"], dt=r["dt"], k_lin=fe[0], k_roll=fe[1], k_rot_wheel=fe[2], k_rot_rotor=fe[3], L=fe[4],
                v_avg=fe[5], m_vehicle=mass, wp_s=wp_s, payload_wp=np.array([payload, np.nan]), beta=0.9, t_start=0.0,
                T_amb_h=np.full(nh, T_K), W1=W1, W2=W2, cdxa_v=np.array([0.0, 10.0, 40.0]), CdxA0=5.0, p_air=101325.0, R_air=287.058,
                ES=ES, PS=PS, HVAC=HVAC, SP=SP, cond=cond, PTO_always_on=PTOa, **E.no_pto(2),
                gearbox_eff=eff[0], motor_eff=eff[1], inverter_eff=eff[2], v_no_regen=v_no_regen, P_regen_max=cap, drive_pto_mechanical=drive_mech)


def old_call(a, **override):
    """Call the REAL notebook consumption_engine (kelvin -> deg C, m/s -> km/h done here, as the old function expects)."""
    o = E.to_old_args(a)
    o.update(override)
    return NS["consumption_engine"](**o)
