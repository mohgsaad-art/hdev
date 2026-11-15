"""E2 test bench for the consumption review: builds every input of consumption_engine for the VECTO generic E2 truck,
either from VECTO's OWN rows (a .vmod file, Part C) or from HDEV's driver rows (Gate 3, Part D).

Review glue only.  Engine functions are called from the notebook (through _load_notebook / _common).  Each constant has a source tag.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _common import (NS, Vehicle, load_vmod_run, vmod_rows, trace_for_engine, CDXA_V, G, RHO_VECTO, BETA,  # noqa: E402
                     write_csv, out, REPO)
from tests.driver_model import _vmod as VM  # noqa: E402

force_engine = NS["force_engine"]
crosswind_engine = NS["crosswind_engine"]
payload_engine = NS["payload_engine"]
driver_model = NS["driver_model"]
pto_engine = NS["pto_engine"]
P_aux = NS["P_aux"]

# ---- E2 powertrain data -------------------------------------------------------------------------------------------
# [VECTO] GenericVehicleE2/AMT.vgbx: axle ratio 2.59, gear 1 = 3.86, gear 2 = 1.93; BatteryElectricVehicle.vveh: ElectricMotors Count 2, Ratio (ADC) 2.0
# [VECTO] GenericEMotor_125kW_485Nm.vem Inertia 0.225 per motor; ElectricMachinesDataAdapter.cs:124 Inertia = motorData.Inertia * count
I_AXLE, I_GEAR, I_ADC = 2.59, {1: 3.86, 2: 1.93}, 2.0
J_ROTOR_TOTAL = 0.225 * 2                        # kg m2, both motors; [TEST] fitted from .vmod P_E2-em_inertia_loss: median 0.4500
I_TOTAL = {g: I_AXLE * r * I_ADC for g, r in I_GEAR.items()}     # wheel -> motor shaft
P_AIR, R_AIR = 101325.0, 287.058                 # [STD] ISO 2533:1975 sea-level pressure; specific gas constant of dry air (ISO 2533 Table 1, 287.053 J/(kg K); 287.058 CODATA-rounded) -> ILLUSTRATIVE precision
T_K_VECTO = P_AIR / (R_AIR * RHO_VECTO)          # [CALC] temperature that gives VECTO's fixed 1.188 kg/m3 at 101325 Pa
V_NO_REGEN_5 = 5 / 3.6                           # [VECTO] Constants.cs 323 (AT gearbox value, what Appendix 1 cites)
V_NO_REGEN_10 = 10 / 3.6                         # [VECTO] Constants.cs 321 + GearboxData.cs 90-99 (clutch value, applies to an AMT)
MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF = 0.95, 0.95, 0.98     # HDEV placeholders (harness v1.7 line 50), flagged
REGEN_EFF_HARNESS = MOTOR_EFF * INVERTER_EFF * GEARBOX_EFF  # harness v1.7 line 51
MODE_FROM_ACTION = {0: 0, 2: 3, 4: 3, 6: 1, -5: 4}           # tests/driver_model/_vmod.py VECTO_ACTION_TO_MODE (VECTO Driver.cs 51-58)

NO_STOP = ([0.0], [0.0])         # "no profile" = single point: np.diff -> empty


def veh_for(cycle, loading):
    return Vehicle("RegionalDelivery" if cycle != "LongHaul" else "LongHaul", loading) if cycle != "UrbanDelivery" \
        else Vehicle("UrbanDelivery", loading)


def crosswind_tables(veh):
    """W1, W2 (1 weather hour x speed grid) from Bob's crosswind_engine at the declaration wind (VECTO Physics.cs 56-66)."""
    a1, a2, a3 = veh.a123
    W1, W2 = crosswind_engine(3.75, np.array([3.0]), 4.0, a1, a2, a3, 0.2, 3.75 / 10, 10, CDXA_V, None)
    return np.asarray(W1), np.asarray(W2)


def vecto_rows(cycle, loading):
    """VECTO's own rows from a .vmod, as HDEV engine inputs, plus VECTO's columns [W] for comparison.
    Sign conventions of the .vmod (checked in Part A): P_wheel_in, P_axle_in, P_gbx_in positive = driving;
    P_E2-em_mech_map / P_E2-em_el: negative = motor drives / draws electricity, positive = generates / charges;
    P_REESS_T: NEGATIVE = battery discharges (terminal), positive = charging."""
    cols = load_vmod_run(cycle, loading)
    r = vmod_rows(cols)
    veh = veh_for(cycle, loading)
    v1, acc = trace_for_engine(r, "acc")
    c = lambda n: VM.col(cols, n)
    kW = lambda n: c(n) * 1000.0
    action = c("DriverAction").astype(int)
    M = np.array([MODE_FROM_ACTION[a] for a in action])
    gear = c("Gear").astype(int)
    n = len(v1)
    return dict(veh=veh, cols=cols, r=r, n=n, T=np.arange(n, dtype=float), S=r["dist"], V=v1, A=acc, grade=r["grad"], M=M,
                dt=r["dt"], gear=gear, action=action,
                vecto={k: kW(k) for k in ("P_wheel_in", "P_wheelEnd_in", "P_axle_in", "P_gbx_in", "P_E2-em_mech", "P_E2-em_mech_map",
                                          "P_E2-em_inertia_loss", "P_E2-em_el", "P_aux_el", "P_REESS_T", "P_REESS_int", "P_brake_loss",
                                          "P_E2-em_gen_max", "P_aux_COND_el", "P_aux_STP_el", "P_aux_ES_el", "P_aux_AC_el", "P_aux_PS_el")}
                | dict(EM_off=c("EM_E2_off"), v_act=r["v_act"], cdxa=c("CdxA_eff")))


def i_total_from_gear(gear, zero_gear_to=0):
    """Per-row wheel->motor ratio.  Gear 0 (no gear engaged): VECTO ignores motor inertia there (ElectricMotor.cs 271-276)."""
    tab = {0: zero_gear_to and I_TOTAL[zero_gear_to] or 0.0, 1: I_TOTAL[1], 2: I_TOTAL[2]}
    return np.array([tab[int(g)] for g in gear])


def forces(veh, v1, acc, dt, grade, J_rotor, i_total):
    """The real notebook force_engine (13 Nov, 6 outputs)."""
    return force_engine(G, veh.crr_eff(BETA), v1, acc, dt, grade, veh.r_dyn, veh.theta_red, J_rotor, i_total)


def engine_args(veh, T, S, V, M, dt, fe, wp_s, payload, aux, pto, drivetrain, T_K=None, P_regen_max=None, v_no_regen=V_NO_REGEN_5,
                drive_pto_mechanical=False, hours=2):
    """Argument dict for consumption_engine_v_split_eff / consumption_engine_v_proposed (new names, SI).
    fe = force_engine outputs (k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg)."""
    k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg = fe
    W1, W2 = crosswind_tables(veh)
    T_K = T_K_VECTO if T_K is None else T_K
    nh = max(hours, int(T[-1] // 3600) + 2)
    return dict(T=T, S=S, V=V, M=M, dt=dt, k_lin=k_lin, k_roll=k_roll, k_rot_wheel=k_rot_wheel, k_rot_rotor=k_rot_rotor, L=L, v_avg=v_avg,
                m_vehicle=veh.m_empty, wp_s=wp_s, payload_wp=payload, beta=BETA,
                t_start=0.0, T_amb_h=np.full(nh, T_K), W1=np.tile(W1, (nh, 1)), W2=np.tile(W2, (nh, 1)),
                cdxa_v=CDXA_V / 3.6, CdxA0=veh.cdxa0, p_air=P_AIR, R_air=R_AIR,
                **aux, **pto, **drivetrain, v_no_regen=v_no_regen, P_regen_max=P_regen_max,
                drive_pto_mechanical=drive_pto_mechanical)


NO_PTO = dict(wp_stop=None, is_on=None, pto_start=None, stop_1s=np.zeros(0), drive_1s=np.zeros(0), stop_const_W=0.0, drive_const_W=0.0)


def no_pto(n_wp):
    return dict(wp_stop=np.zeros(n_wp), is_on=np.zeros(n_wp), pto_start=np.full(n_wp, np.nan), stop_1s=np.zeros(0), drive_1s=np.zeros(0),
                stop_const_W=0.0, drive_const_W=0.0)


def to_old_args(a):
    """new SI argument dict -> arguments of the 13 Nov notebook consumption_engine (kelvin -> deg C, m/s -> km/h).  PTO off."""
    n_wp = len(a["wp_s"])
    old = dict(T=a["T"], S=a["S"], V=a["V"], M=a["M"], dt=a["dt"], k_lin=a["k_lin"], k_roll=a["k_roll"], k_rot=a["k_rot_wheel"], L=a["L"],
               v_avg=a["v_avg"], m_vehicle=a["m_vehicle"], wp_s=a["wp_s"], payload_wp=a["payload_wp"], beta=a["beta"], t_start=a["t_start"],
               T_amb_h=a["T_amb_h"] - 273.15, W1=a["W1"], W2=a["W2"], cdxa_v=a["cdxa_v"] * 3.6, CdxA0=a["CdxA0"], p_air=a["p_air"],
               R_air=a["R_air"], ES=a["ES"], PS=a["PS"], HVAC=a["HVAC"], SP=a["SP"], cond=a["cond"], PTO_always_on=a["PTO_always_on"],
               pto_1s=np.zeros(0), pto_on_col=np.zeros(n_wp), pto_start_col=np.full(n_wp, np.nan),
               motor_eff=a["motor_eff"], inverter_eff=a["inverter_eff"], gearbox_eff=a["gearbox_eff"],
               regen_effeiciency=a.get("regen_effeiciency", a["motor_eff"] * a["inverter_eff"] * a["gearbox_eff"]),
               v_no_regen=a["v_no_regen"], P_regen_max=a["P_regen_max"])
    return old
