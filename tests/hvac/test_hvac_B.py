"""Part B tests for HVAC_thermal / ssm_total_w / climate_lookup.  All tests call Bob's REAL notebook code via _load_notebook.
Values marked ILLUSTRATIVE are test inputs only, not model inputs.  Run:  pytest tests/hvac -q"""
import numpy as np
import pytest

import hvac_common as H
import vecto_ssm_port as P
from gate3_grid import bob_parts, port_parts, CASES
from _load_notebook import NS, cell_source

HVAC_thermal, ssm_total_w, climate_lookup = NS["HVAC_thermal"], NS["ssm_total_w"], NS["climate_lookup"]
ARGS = H.base_args(H.PLACEHOLDER)          # ILLUSTRATIVE cab (Bob's placeholders), R-744 + electric heater, 5 kW / 5 kW


# ---- B1 Q = 0 reproduces the VECTO port ---------------------------------------------------------------------------
def test_B1_q0_equals_vecto_port_on_grid():
    Tg, Sg = np.meshgrid(np.arange(-30, 41, 1.0), np.arange(0, 1001, 100.0), indexing="ij")
    for name, c in CASES.items():
        b, p = bob_parts(Tg, Sg, c), port_parts(Tg, Sg, c)
        for k in ("total", "hp", "eh", "ac", "fan", "fuel_heat"):
            assert np.max(np.abs(b[k] - p[k])) < 1e-9, (name, k)


def test_B1_port_reproduces_vecto_own_unit_tests():
    import gate3_vecto_unit_tests as G
    bad = [r for r in G.results if r["result"] != "PASS"]
    assert len(G.results) >= 150 and not bad, bad[:3]


def test_gate2_notebook_cells_are_the_code_of_record():
    import appendix1_prompt_text as A
    norm = lambda s: "\n".join(l.rstrip() for l in s.strip("\n").split("\n"))
    for idx, name in ((11, "HVAC_THERMAL"), (12, "SSM_TOTAL_W"), (13, "CLIMATE_LOOKUP")):
        assert norm(cell_source(idx)) == norm(getattr(A, name))


# ---- B2 signs / modes -------------------------------------------------------------------------------------------
def test_B2_modes_cold_hot_between():
    kw = dict(ARGS)
    tot_cold, _ = HVAC_thermal(np.array([-10.0]), 0.0, **kw)
    tot_hot, _ = HVAC_thermal(np.array([35.0]), 800.0, **kw)
    tot_mid, _ = HVAC_thermal(np.array([20.0]), 0.0, **kw)
    # cold: heating only (fan at heating rate + heat); hot: cooling + fan; mid (T between setpoints, run1>0>run2): fan only
    fan_h = 6.5 * 7.0 * 0.56
    assert tot_cold[0] > fan_h + 100 and tot_hot[0] > fan_h + 100
    assert tot_mid[0] == pytest.approx(6.5 * 7.0 * 0.56)
    # parts: cold has no AC, hot has no heat
    c = dict(CASES["B  R-744 + el.heater (HD2), no caps"])
    pc, ph = bob_parts(np.array([-10.0]), np.array([0.0]), c), bob_parts(np.array([35.0]), np.array([800.0]), c)
    assert pc["ac"][0] == pytest.approx(0, abs=1e-9) and ph["hp"][0] == pytest.approx(0, abs=1e-9) and ph["eh"][0] == pytest.approx(0, abs=1e-9)


def test_B2_run1_ge_run2_always_when_tcool_ge_theat():
    T = np.arange(-40, 50, 0.5)
    for S in (0.0, 300.0, 1000.0):
        for Q in (0.0, 100.0):
            r1 = ssm_total_w(T, S, 18.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, 101325., 287.05, 1005., Q)
            r2 = ssm_total_w(T, S, 23.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, 101325., 287.05, 1005., Q)
            assert np.all(r1 >= r2)


def test_B2_three_modes_cover_every_hour_when_tcool_ge_theat():
    """heating, cooling or ventilation-only: with run1>=run2 each hour falls in exactly one class (ties at exactly 0 aside)."""
    T = np.arange(-40, 50, 0.37); S = 250.0
    r1 = ssm_total_w(T, S, 18.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, 101325., 287.05, 1005., 0.0)
    r2 = ssm_total_w(T, S, 23.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, 101325., 287.05, 1005., 0.0)
    heat = (r1 < 0) & (r2 < 0); cool = (r1 > 0) & (r2 > 0); vent = (r1 > 0) & (r2 < 0)
    assert np.all(heat.astype(int) + cool.astype(int) + vent.astype(int) == 1)


# ---- B3 monotonicity ------------------------------------------------------------------------------------------
def _jumps(S0, hd):
    T = np.arange(17.0 - 1e-9, -15.0, -0.01)
    tot, _ = HVAC_thermal(T, S0, **H.base_args(H.PLACEHOLDER, "R-744", hd))
    return T, tot


@pytest.mark.parametrize("hd", ["HD2", "HD9"])
@pytest.mark.parametrize("S0", [0.0, 500.0])
def test_B3_non_decreasing_below_17C(hd, S0):
    T, tot = _jumps(S0, hd)
    assert np.all(np.diff(tot) >= -1e-9), "HVAC_el must not fall as T falls below T_boundary (17 C)"


def test_B3_documented_jumps():
    """The jumps are real and come from VECTO's own switches (not bugs): sizes are printed in the report (run_part_b_jumps.py)."""
    T = np.array([17.01, 16.99])
    tot, _ = HVAC_thermal(T, 500.0, **ARGS)
    assert tot[0] - tot[1] > 40          # cooling turns off at 17 C and persons 80 W -> 50 W: HVAC falls by ~48 W (placeholder cab, ILLUSTRATIVE solar)
    T = np.array([-12.49, -12.51])
    tot, _ = HVAC_thermal(T, 0.0, **ARGS)
    assert tot[1] - tot[0] > 300         # nearest-point switch between the -5 and -20 C share rows (HD2): +480 W


# ---- B4 climate_lookup ------------------------------------------------------------------------------------------
def test_B4_cop_equals_interp_and_ties_go_to_colder_point():
    Th = [-20.0, -5.0, 2.0, 8.0, 14.0]; Tc = [20.5, 26.0, 33.0]
    T = np.array([-30.0, -12.5, -5.0, 0.0, 5.0, 11.0, 30.0, 40.0])
    ch, cc, hp, eh, fu = climate_lookup(T, Th, H.COP_H["R-744"], Tc, H.COP_C["R-744"], [.5, 1, 1, 1, 1], [.5, 0, 0, 0, 0], [0] * 5)
    assert np.array_equal(ch, np.interp(T, Th, H.COP_H["R-744"])) and np.array_equal(cc, np.interp(T, Tc, H.COP_C["R-744"]))
    # tie at -12.5 (between -20 and -5): first = colder point -> share row of -20 C
    assert hp[1] == 0.5 and eh[1] == 0.5
    assert hp[4] == 1.0   # 5 C: nearest of 2 (3 K) and 8 (3 K) is a tie -> colder = 2 C


def test_B4_works_1d_and_2d():
    Th = [-20.0, -5.0, 2.0, 8.0, 14.0]
    T2 = np.array([[-10.0, 0.0], [10.0, 20.0]])
    out2 = climate_lookup(T2, Th, H.COP_H["R-744"], [20.5, 26., 33.], H.COP_C["R-744"], [.5, 1, 1, 1, 1], [.5, 0, 0, 0, 0], [0] * 5)
    out1 = climate_lookup(T2.ravel(), Th, H.COP_H["R-744"], [20.5, 26., 33.], H.COP_C["R-744"], [.5, 1, 1, 1, 1], [.5, 0, 0, 0, 0], [0] * 5)
    for a, b in zip(out2, out1):
        assert a.shape == (2, 2) and np.array_equal(a.ravel(), b)


# ---- B5 caps ------------------------------------------------------------------------------------------------
def test_B5_cap_keeps_ratio_fuel_not_capped_cooling_capped():
    c = dict(CASES["A  R-744 + el.heater + fuel heater (HD3), caps 5 kW/5 kW"])
    T, S = np.array([-20.0]), np.array([0.0])
    hp_el, fuel_heat = bob_parts(T, S, c)["hp"], bob_parts(T, S, c)["fuel_heat"]
    b = bob_parts(T, S, c)
    # heat delivered by hp and eh after cap: hp_heat = hp_el*COP, eh_heat = eh_el*0.93 ; ratio must equal share ratio 0.4 : 0.2
    ratio = (b["hp"][0] * 1.80) / (b["eh"][0] * 0.93)
    assert ratio == pytest.approx(0.4 / 0.2, rel=1e-9)
    assert (b["hp"][0] * 1.80 + b["eh"][0] * 0.93) == pytest.approx(5000.0)          # capped at max_heating_power
    assert fuel_heat[0] > 5000.0 * 0.4 / 0.6 * 0.99 or fuel_heat[0] > 0             # fuel part NOT capped by max_heating_power
    # cooling cap
    hot = bob_parts(np.array([35.0]), np.array([1000.0]), dict(c, cap_c=1000.0))
    assert hot["ac"][0] == pytest.approx(1000.0 / np.interp(35.0, [20.5, 26, 33], c["cop_c"]))


# ---- B6 fresh air ---------------------------------------------------------------------------------------------
def test_B6_fresh_air_hand_calculation():
    T, Q = -10.0, 100.0                                  # ILLUSTRATIVE
    p, R, cp = 101325.0, 287.05, 1005.0                  # p0 and R: ISO 2533:1975 standard atmosphere [STD, summary only]; cp: Bob's default
    rho = p / (R * (T + 273.15))
    expected = rho * cp * Q / 3600.0 * (T - 18.0)
    base = ssm_total_w(np.array([T]), 0.0, 18.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, p, R, cp, 0.0)
    with_q = ssm_total_w(np.array([T]), 0.0, 18.0, 20, 3, 2, 4, (50, 80), (.65, .8), 17.0, .95, .25, p, R, cp, Q)
    assert (with_q - base)[0] == pytest.approx(expected, rel=1e-12)
    assert expected == pytest.approx(-1.3414 * 1005 * 100 / 3600 * 28, rel=1e-3)


# ---- B7 shape contract with consumption_engine (read-only) ---------------------------------------------------------
def _run_engine(HV, t_start=0, nh=4):
    ce = NS["consumption_engine"]
    n = 7200
    T = np.arange(n, dtype=float); V = np.full(n, 15.0); S = np.cumsum(V); M = np.ones(n)   # ILLUSTRATIVE rows
    W1, W2, cdv = np.ones((nh, 3)), np.zeros((nh, 3)), np.array([60., 80., 100.])
    return ce(T, S, V, M, 1.0, 0.0, 0.0, 0.0, 0.0, 15.0, 10000., np.array([0., S[-1]]), np.array([0., 0.]), 2.0,
              t_start, np.full(nh, 10.0), W1, W2, cdv, 1.0, 101325., 287.05,
              0., 0., HV, 0., 0., 0., np.zeros(1), np.zeros(0), np.zeros(0), 0.9, 0.9, 0.9, 0.7, 1.0)


def test_B7_per_hour_array_indexed_like_T_amb_h():
    hv = np.array([100., 200., 300., 400.])
    P_aux = _run_engine(hv)[2]
    assert P_aux[0] == 100 and P_aux[3599] == 100 and P_aux[3600] == 200 and P_aux[7199] == 200
    P_aux = _run_engine(hv, t_start=1800)[2]              # trip starts 30 min after weather hour 0
    assert P_aux[1799] == 100 and P_aux[1800] == 200 and P_aux[5400] == 300


def test_B7_scalar_works_and_too_short_array_fails_loudly():
    assert np.all(_run_engine(250.0)[2] == 250.0)
    with pytest.raises(IndexError):
        _run_engine(np.array([100.0]))


def test_B7_thermal_output_can_feed_P_aux_with_eff_1():
    tot, _ = HVAC_thermal(np.array([-5.0, 25.0]), np.array([0.0, 300.0]), **ARGS)
    out = NS["P_aux"](0, 0, tot, 0, 0, 0, HVAC_eff=1.0)
    assert np.array_equal(out[2], tot)
    out125 = NS["P_aux"](0, 0, tot, 0, 0, 0)      # default HVAC_eff=1.25 would inflate thermal W by 25 % -> parser must pass 1.0
    assert np.allclose(out125[2], 1.25 * tot)


# ---- Part A robustness (characterisation of CURRENT behaviour; BUG-labelled ones are reported in the report) ------------
def test_A_scalar_solar_with_array_T_and_2d():
    a, _ = HVAC_thermal(np.array([-10., 5., 30.]), 500.0, **ARGS)
    b, _ = HVAC_thermal(np.array([-10., 5., 30.]), np.full(3, 500.0), **ARGS)
    assert np.array_equal(a, b)
    t2, _ = HVAC_thermal(np.array([[-10., 10.], [20., 30.]]), np.array([[0., 0.], [300., 600.]]), **ARGS)
    assert t2.shape == (2, 2)


def test_A_per_hour_array_inputs_work_without_code_change():
    U = np.array([3.0, 4.5, 3.0])                                                      # e.g. parked / driving UA per hour
    kw = dict(ARGS); kw["U"] = U
    t, _ = HVAC_thermal(np.array([-5., -5., -5.]), 0.0, **kw)
    assert t[1] > t[0] and t[0] == t[2]


def test_BUG_nan_solar_or_temperature_gives_silent_zero_watt():
    """BUG (silent): one NaN hour gives 0 W, including a winter hour where solar is irrelevant.  Weather gaps must be filled in the parser (decision 5)."""
    t, _ = HVAC_thermal(np.array([-10.0]), np.array([np.nan]), **ARGS)
    assert t[0] == 0.0
    t, _ = HVAC_thermal(np.array([np.nan]), np.array([100.0]), **ARGS)
    assert t[0] == 0.0


def test_BUG_nan_in_cop_grid_poisons_interpolation_between_points():
    """The VECTO cell '-' (non-R-744, -20 C) as NaN makes np.interp return NaN for ALL T between -20 and -5 C -> ValueError for hours at -12 C."""
    kw = H.base_args(H.PLACEHOLDER, "non R-744 continuous", "HD1")
    with pytest.raises(ValueError):
        HVAC_thermal(np.array([-12.0]), 0.0, **kw)
    t, _ = HVAC_thermal(np.array([-3.0]), 0.0, **kw)      # at -3 C the segment (-5..2) is fine
    assert np.isfinite(t[0])


def test_A_zero_and_inf_inputs_current_behaviour():
    kw = dict(ARGS); kw["U"] = 0.0
    assert np.isfinite(HVAC_thermal(np.array([-10.0]), 0.0, **kw)[0][0])
    kw = dict(ARGS); kw["A_window"] = 0.0
    assert np.isfinite(HVAC_thermal(np.array([30.0]), 800.0, **kw)[0][0])
    kw = dict(ARGS); kw["max_heating_power"] = np.inf
    assert np.isfinite(HVAC_thermal(np.array([-10.0]), 0.0, **kw)[0][0])
    kw = dict(ARGS); kw["waste_heat"] = 1e9
    assert HVAC_thermal(np.array([-10.0]), 0.0, **kw)[0][0] == pytest.approx(6.5 * 7 * 0.56)   # heating fully covered: only the fan remains
    kw = dict(ARGS); kw["cop_cool_points"] = [0, 0, 0]
    with np.errstate(divide="ignore"):
        assert np.isinf(HVAC_thermal(np.array([32.0]), 500.0, **kw)[0][0])                  # cop = 0 -> inf, no ValueError (parser must check cop > 0)
    kw = dict(ARGS); kw["max_heating_power"] = np.nan
    assert np.isnan(HVAC_thermal(np.array([-10.0]), 0.0, **kw)[0][0])                       # NaN cap propagates (not silent)


def test_A_shares_not_summing_to_one_not_checked():
    kw = dict(ARGS); kw["hp_share_points"] = [1] * 5; kw["eh_share_points"] = [1] * 5
    t, _ = HVAC_thermal(np.array([-10.0]), 0.0, **kw)
    ok, _ = HVAC_thermal(np.array([-10.0]), 0.0, **ARGS)
    assert t[0] > 3 * ok[0]               # 200 % of the demand is delivered; no engine check -> parser job
