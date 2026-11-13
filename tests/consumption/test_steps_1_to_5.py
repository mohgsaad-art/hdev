"""Part B tests 1, 3, 4, 5(part), 7(part): energy bookkeeping, step 5 signs, payload, weather, shapes.
All calls go to the notebook function (old_call) or to a named variant in reference_copy.py.  Numbers are ILLUSTRATIVE."""
import numpy as np
import pytest

import _e2 as E
import reference_copy as RC
from _load_notebook import NS
from _synth import base_args, old_call, rows

NOTEBOOK = NS["consumption_engine"]


# ---------------------------------------------------------------- 1. energy bookkeeping
def test_energy_equals_wheel_work_when_everything_is_ideal():
    """[TEST] all efficiencies 1, no regen limit, no aux, rows without M 3/4-low-speed rules: E_battery == sum(P_wheel*dt)."""
    r = rows()
    a = base_args(r, v_no_regen=-1.0)
    P_wheel, P_trac, P_aux, P_bat, E_kwh = old_call(a, regen_effeiciency=1.0, v_no_regen=-1.0)
    assert np.allclose(P_trac, np.where(r["M"] == 3, 0.0, P_wheel))
    assert E_kwh == pytest.approx(np.sum(P_wheel * r["dt"]) / 3.6e6, rel=1e-12)
    assert np.all(P_aux == 0)


def test_rotor_term_is_in_the_proposal_and_not_in_the_old_function():
    """[TEST] with J_rotor > 0 the old function has no place for k_rot_rotor (signature_only refuses); the proposal adds it at the motor shaft."""
    a = base_args(J_rotor=0.45, i_total=10.0, v_no_regen=-1.0)
    with pytest.raises(ValueError):
        RC.consumption_engine_v_signature_only(**{k: a[k] for k in ("T", "S", "V", "M", "dt")}, k_lin=a["k_lin"], k_roll=a["k_roll"],
                                               k_rot_wheel=a["k_rot_wheel"], k_rot_rotor=a["k_rot_rotor"], L=a["L"], v_avg=a["v_avg"],
                                               m_vehicle=a["m_vehicle"], wp_s=a["wp_s"], payload_wp=a["payload_wp"], beta=a["beta"], t_start=0.0,
                                               T_amb_h=a["T_amb_h"] - 273.15, W1=a["W1"], W2=a["W2"], cdxa_v=a["cdxa_v"] * 3.6, CdxA0=a["CdxA0"],
                                               p_air=a["p_air"], R_air=a["R_air"], ES=0, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0,
                                               is_on=np.zeros(2), pto_start=np.full(2, np.nan), stop_1s=np.zeros(0), drive_1s=np.zeros(0),
                                               motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0)
    out = RC.consumption_engine_v_proposed(**a)
    wheel_work = np.sum(out["P_wheel"] * a["dt"]) / 3.6e6
    rotor_work = np.sum(a["k_rot_rotor"] * a["dt"]) / 3.6e6
    # everything ideal: energy = wheel work + rotor work (coasting rows M 3 do not occur in these rows; M 4 rows are above v_no_regen = -1)
    assert out["E_battery"] == pytest.approx(wheel_work + rotor_work, rel=1e-12)
    assert abs(rotor_work) < 1e-9 * abs(wheel_work) + 1e-6      # rotor inertia is conservative: it nets to ~0 over a stop-to-stop trip


# ---------------------------------------------------------------- 3. step-5 signs
def test_sign_table_old_function():
    """[TEST] positive wheel power -> /eta, negative -> *regen, zero -> zero, coasting -> 0, braking below v_no_regen -> 0, above -> regen."""
    r = rows()
    eta, reg = 0.8, 0.7
    a = base_args(r, eff=(1.0, eta, 1.0), v_no_regen=5 / 3.6)
    P_wheel, P_trac, *_ = old_call(a, regen_effeiciency=reg, gearbox_eff=1.0, motor_eff=eta, inverter_eff=1.0)
    M, V = r["M"], r["V"]
    for k in range(len(M)):
        if M[k] == 3:
            assert P_trac[k] == 0
        elif M[k] == 4 and V[k] <= 5 / 3.6:
            assert P_trac[k] == 0
        elif P_wheel[k] > 0:
            assert P_trac[k] == pytest.approx(P_wheel[k] / eta)
        else:
            assert P_trac[k] == pytest.approx(P_wheel[k] * reg)
    assert (P_wheel > 0).any() and (P_wheel < 0).any() and (M == 4).any()


def test_coasting_rows_are_zero_even_if_wheel_power_is_large():
    r = rows()
    r["M"] = np.full(r["n"], 3)
    P_wheel, P_trac, *_ = old_call(base_args(r), regen_effeiciency=1.0)
    assert np.all(P_trac == 0) and np.abs(P_wheel).max() > 0


def test_regen_cap_binds_and_the_rest_is_friction_brake():
    a = base_args(cap=None, v_no_regen=-1.0)
    _, P_free, *_ = old_call(a, regen_effeiciency=1.0)
    cap = 0.5 * (-P_free.min())
    _, P_cap, *_ = old_call(a, regen_effeiciency=1.0, P_regen_max=cap)
    assert P_cap.min() == pytest.approx(-cap)
    assert np.all(P_cap >= -cap - 1e-9)


def test_rotor_term_can_flip_the_sign_at_the_motor():
    """[TEST] a row with small NEGATIVE wheel power but a larger POSITIVE rotor term (accelerating on a small downhill):
    Appendix 1 decides on the wheel sign and calls it regen; the proposal decides at the motor and calls it driving.  Q2."""
    a = base_args(v_no_regen=-1.0)
    n = len(a["V"])
    for key in ("k_lin", "k_roll", "k_rot_wheel", "k_rot_rotor", "L", "v_avg"):
        a[key] = np.zeros(n)
    a["k_lin"] = np.full(n, -0.001)            # P_wheel = m * k_lin = 9000+1000 kg * -0.001 = -10 W... ILLUSTRATIVE
    a["k_rot_rotor"] = np.full(n, 30.0)        # +30 W at the motor shaft
    a["m_vehicle"], a["payload_wp"] = 1000.0, np.array([0.0, np.nan])
    old = old_call(a, regen_effeiciency=0.8, gearbox_eff=1.0, motor_eff=1.0, inverter_eff=1.0)
    new = RC.consumption_engine_v_proposed(**{**a, "M": np.full(n, 2)})
    assert np.all(old[0] < 0) and np.all(old[1] < 0)             # old: regen
    assert np.all(new["P_motor"] > 0) and np.all(new["P_trac"] > 0)   # proposal: drive (+20 W)


def test_mechanical_drive_pto_flips_the_sign_at_the_motor():
    """[TEST] same idea with a mechanical drive PTO: the PTO power is added at the motor shaft BEFORE motor x inverter efficiency."""
    r = rows()
    a = base_args(r, eff=(1.0, 0.9, 1.0), v_no_regen=-1.0)
    n = r["n"]
    for key in ("k_lin", "k_roll", "k_rot_wheel", "k_rot_rotor", "L", "v_avg"):
        a[key] = np.zeros(n)
    a["M"] = np.full(n, 2)
    a["T"], a["S"], a["V"] = np.arange(n, dtype=float), np.linspace(0, 100, n), np.full(n, 5.0)
    a["wp_s"] = np.array([0.0, 1.0]); a["wp_stop"] = np.array([0.0, 0.0]); a["is_on"] = np.array([0.0, 1.0])
    # a wheel-side downhill of -1000 W and a drive PTO of +4000 W (constant) -> motor shaft +3000 W
    a["k_lin"] = np.full(n, -1000.0 / 10000.0)
    a["m_vehicle"], a["payload_wp"] = 10000.0, np.array([0.0, np.nan])
    a["drive_const_W"] = 4000.0
    mech = RC.consumption_engine_v_proposed(**{**a, "drive_pto_mechanical": True})
    elec = RC.consumption_engine_v_proposed(**{**a, "drive_pto_mechanical": False})
    # mechanical: (-1000 + 4000)/0.9 = 3333 W traction ; electric: -1000*0.9 = -900 W traction and +4000 W aux
    assert mech["P_trac"][5] == pytest.approx(3000.0 / 0.9)
    assert elec["P_trac"][5] == pytest.approx(-900.0)
    assert mech["P_aux_row"][5] == pytest.approx(0.0)
    assert elec["P_aux_row"][5] == pytest.approx(4000.0)


# ---------------------------------------------------------------- 4. payload
def _mass_only(wp_s, payload_wp, S, m_vehicle=1000.0):
    """Reproduce step 1 of the notebook function through its P_wheel (k_lin=1, others 0): P_wheel = m_row."""
    n = len(S)
    z = np.zeros(n)
    o = dict(T=np.arange(n, dtype=float), S=np.asarray(S, float), V=z + 1, M=z + 2, dt=z + 1, k_lin=z + 1, k_roll=z, k_rot=z, L=z, v_avg=z + 1,
             m_vehicle=m_vehicle, wp_s=wp_s, payload_wp=payload_wp, beta=1.0, t_start=0.0, T_amb_h=np.array([15.0]), W1=np.ones((1, 3)),
             W2=np.zeros((1, 3)), cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0, p_air=101325.0, R_air=287.058, ES=0, PS=0, HVAC=0, SP=0,
             cond=0, PTO_always_on=0, pto_1s=np.zeros(0), pto_on_col=np.zeros(len(wp_s)), pto_start_col=np.full(len(wp_s), np.nan),
             motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0, P_regen_max=None)
    return NOTEBOOK(**o)[0]          # P_wheel = m_row (+ tiny air term, CdxA * L = 0)


def test_payload_forward_fill_and_exact_stop_row():
    wp_s = [0.0, 100.0, 200.0]
    pay = [500.0, 300.0, 100.0]
    m = _mass_only(wp_s, pay, [0, 50, 99.999, 100.0, 150, 200.0, 250])
    # a row exactly AT a stop waypoint already carries the payload written there (side='right')
    assert list(m) == [1500, 1500, 1500, 1300, 1300, 1100, 1100]


def test_payload_row_a_hair_before_first_waypoint_BUG2_and_fix():
    """[TEST] BUG-2 (PR #30): S a hair before wp_s[0] -> searchsorted-1 = -1 -> LAST payload.  The proposal clips to 0 -> FIRST payload."""
    wp_s = [0.0, 100.0, 200.0]
    pay = [500.0, 300.0, 100.0]
    m = _mass_only(wp_s, pay, [-1e-9, 10.0])
    assert m[0] == 1100.0                 # BUG: last payload (100 kg) instead of the start payload (500 kg)
    k = np.clip(np.searchsorted(np.array(wp_s), np.array([-1e-9, 10.0]), side="right") - 1, 0, None)
    assert np.array(pay)[k][0] == 500.0   # fix


def test_payload_engine_shapes_constant_linear_custom_and_no_stops():
    pe = NS["payload_engine"]
    stop = [0, 30, 0, 30, 0]
    assert np.allclose(pe(stop, "constant", 700)[[0, 1, 3]], 700) and np.isnan(pe(stop, "constant", 700)[2])
    lin = pe(stop, "linear", 900, 300)
    assert lin[0] == 900 and lin[1] == 600 and lin[3] == 300
    assert list(pe(stop, "custom", 0, payload_custom=[900, 500, 100])[[0, 1, 3]]) == [900, 500, 100]
    nostop = pe([0, 0, 0], "constant", 500)
    assert nostop[0] == 500 and np.isnan(nostop[1:]).all()
    with pytest.raises(ValueError):
        pe([0, 0, 0], "linear", 500, 100)
    # route with no stops through the engine: single payload value, all rows get it
    m = _mass_only([0.0, 100.0, 200.0], nostop, [0, 50, 150, 250])
    assert np.all(m == 1500.0)


# ---------------------------------------------------------------- 5. weather
def _hour_probe(t_start, T, nh):
    """P_wheel = rho * CdxA * L with L=1: with a different temperature per hour the hour index is visible in the result."""
    n = len(T)
    z = np.zeros(n)
    temps_c = np.arange(nh) * 10.0                                  # 0, 10, 20 ... deg C, ILLUSTRATIVE
    o = dict(T=np.asarray(T, float), S=np.linspace(0, 10, n), V=z + 1, M=z + 2, dt=z + 1, k_lin=z, k_roll=z, k_rot=z, L=z + 1, v_avg=z + 10,
             m_vehicle=1.0, wp_s=[0.0, 20.0], payload_wp=[0.0, np.nan], beta=1.0, t_start=t_start, T_amb_h=temps_c, W1=np.ones((nh, 3)),
             W2=np.zeros((nh, 3)), cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0, p_air=101325.0, R_air=287.058, ES=0, PS=0, HVAC=0, SP=0,
             cond=0, PTO_always_on=0, pto_1s=np.zeros(0), pto_on_col=np.zeros(2), pto_start_col=np.full(2, np.nan),
             motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0, P_regen_max=None)
    return NOTEBOOK(**o)[0], temps_c


def test_hour_index_across_midnight_is_one_continuous_array():
    t_start = 23 * 3600 + 1800                           # 23:30
    T = np.array([0, 1799, 1800, 3000])                  # 23:30, 23:59:59, 00:00, 00:20 next day
    # hour index = (t_start + T)//3600 = 23, 23, 24, 24 -> the weather array must be one continuous array with at least 25 hours
    P, temps = _hour_probe(t_start, T, nh=25)
    rho = lambda tc: 101325.0 / (287.058 * (tc + 273.15))
    assert P[0] == pytest.approx(rho(temps[23])) and P[1] == pytest.approx(rho(temps[23]))
    assert P[2] == pytest.approx(rho(temps[24])) and P[3] == pytest.approx(rho(temps[24]))


def test_weather_array_too_short_is_a_loud_IndexError():
    with pytest.raises(IndexError):
        _hour_probe(0.0, np.array([0.0, 7200.0]), nh=2)      # needs hour index 2


def test_hvac_scalar_vs_per_hour_and_pto_always_on_per_hour_is_NOT_hour_indexed():
    """[TEST] HVAC scalar or one value per weather hour works.  PTO_always_on as an hourly array is added as-is: it is NOT indexed by hour."""
    r = rows()
    a = base_args(r, nh=3)
    base = old_call(a)[2]
    hv = np.array([100.0, 200.0, 300.0])
    assert np.allclose(old_call({**a, "HVAC": hv})[2], base + hv[0])      # all rows are in hour 0
    assert np.allclose(old_call({**a, "HVAC": 100.0})[2], base + 100.0)
    # PTO_always_on array of hours (len 3) with rows (len n): broadcasting error or wrong numbers -> BUG, parser must give a scalar
    with pytest.raises(ValueError):
        old_call({**a, "PTO_always_on": hv})
    # the proposal indexes it by hour
    out = RC.consumption_engine_v_proposed(**{**a, "PTO_always_on": hv})
    assert np.allclose(out["P_aux_row"], hv[0])


def test_w1_w2_one_row_per_weather_hour():
    r = rows()
    a = base_args(r, nh=3)
    base = old_call(a)[0]
    W1 = np.ones((3, 3)); W1[1:] = 2.0
    W2 = np.zeros((3, 3))
    assert np.allclose(old_call({**a, "W1": W1, "W2": W2})[0], base)        # rows are in hour 0 only
    r2 = dict(r); r2["T"] = r["T"] + 3600.0                                  # now in hour 1: twice the air term
    a2 = base_args(r2, nh=3)
    assert old_call({**a2, "W1": W1, "W2": W2})[0].sum() > old_call(a2)[0].sum()


# ---------------------------------------------------------------- 7. shapes, types, NaN
def test_scalars_arrays_and_integers_for_power_inputs():
    a = base_args(aux=(1000, 200, 250, 20, 600, 0))              # integers
    P1 = old_call(a)[2]
    P2 = old_call({**a, "ES": np.float64(1000.0), "HVAC": np.array(250.0)})[2]
    assert np.allclose(P1, P2)
    assert P1.shape == a["V"].shape


def test_empty_route_returns_zero_energy_silently():
    """[TEST] BUG-like: an empty route gives E_battery = 0.0 and empty arrays, no error.  PARSER JOB: reject an empty route."""
    a = base_args()
    for k in ("T", "S", "V", "M", "dt", "k_lin", "k_roll", "k_rot_wheel", "k_rot_rotor", "L", "v_avg"):
        a[k] = a[k][:0]
    out = old_call(a)
    assert out[-1] == 0.0 and len(out[3]) == 0


def test_nan_in_an_input_propagates_silently_so_the_parser_must_stop_it():
    """[TEST] NaN in k_lin -> E_battery is NaN, no error.  PARSER JOB: no NaN may reach the engine."""
    a = base_args()
    a["k_lin"] = a["k_lin"].copy(); a["k_lin"][7] = np.nan
    out = old_call(a)
    assert np.isnan(out[-1])
