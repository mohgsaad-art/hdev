"""Part A robustness + Part B unit/analytic tests for force_engine and consumption_engine steps 1-4.

Everything is run against Bob's code of record (12 Nov 2026 notebook) loaded by
docs/research/force-engine-review-2026-11/_load_notebook.py. Nothing in src/ or the notebook is changed.

Labels:  ILLUSTRATIVE = test value with no source.   BUG / LIMITATION = documented behaviour of Bob's code that
the test pins down (the test passes while the behaviour exists; it will fail if Bob changes it, which is the point).

Run:   pytest tests/force_engine -q
"""
import math
import os
import sys
import warnings

import numpy as np
import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REV = os.path.join(_REPO, "docs", "research", "force-engine-review-2026-11")
for p in (_REPO, _REV):
    if p not in sys.path:
        sys.path.insert(0, p)

import _common as C                                       # noqa: E402
from _common import (G, CDXA_V, Vehicle, force_engine, consumption_engine, payload_engine, run_driver)  # noqa: E402

CRR = 0.0055  # ILLUSTRATIVE (also the value used in the 8 Oct hand tests)


# ============================================================== B1 neutral defaults + 8 Oct hand tests
def test_hand_test_1_v20_flat_g980665():
    """8 Oct test 1 recomputed with g = 9.80665 (8 Oct used ~9.81 -> 1.0791). ILLUSTRATIVE inputs."""
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR, [20.0], [0.0], [1.0], [0.0], 0.0, 0.0)
    assert k_lin[0] == pytest.approx(0.0)
    assert k_roll[0] == pytest.approx(0.0055 * 9.80665 * 20.0)        # 1.078732 (was 1.0791 with g=9.81)
    assert float(k_roll[0]) == pytest.approx(1.07873, abs=1e-5)
    assert k_rot[0] == 0.0
    assert L[0] == pytest.approx(4000.0)
    assert v_avg[0] == pytest.approx(20.0)


def test_hand_test_2_v10_a1_g980665():
    """8 Oct test 2 recomputed with g = 9.80665 (8 Oct: 0.56653 with g~9.81)."""
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR, [10.0], [1.0], [1.0], [0.0], 0.0, 0.0)
    assert k_lin[0] == pytest.approx(10.5)
    assert k_roll[0] == pytest.approx(0.0055 * 9.80665 * 10.5)        # 0.566337
    assert float(k_roll[0]) == pytest.approx(0.56634, abs=1e-5)
    assert L[0] == pytest.approx(580.125)
    assert v_avg[0] == pytest.approx(10.5)


def test_neutral_defaults_equal_simple_road_load():
    rng = np.random.default_rng(1)                                    # ILLUSTRATIVE random rows
    v = rng.uniform(0, 25, 200)
    a = rng.uniform(-1, 1, 200)
    a = np.maximum(a, -v)                                             # no clamp
    gr = rng.uniform(-8, 8, 200)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR, v, a, 1.0, gr, 0.4, 0.0)
    th = np.arctan(gr / 100)
    K = (CRR * G * np.cos(th) + G * np.sin(th) + a) * v_avg           # the commented 'K' line in Bob's code
    assert np.allclose(k_lin + k_roll, K, rtol=1e-12, atol=1e-12)
    assert np.all(k_rot == 0)


# ============================================================== B2 L = exact mean of 0.5 v^3
@pytest.mark.parametrize("seed", range(5))
def test_L_equals_numeric_integral(seed):
    rng = np.random.default_rng(seed)
    v1 = rng.uniform(0, 30, 50)
    a = rng.uniform(-2, 2, 50)
    # include steps that end exactly at v2 = 0 and steps that start at 0
    a[:10] = -v1[:10]
    v1[10:15] = 0.0
    a[10:15] = np.abs(a[10:15])
    dt = 1.0
    _, _, _, L, _ = force_engine(G, 0, v1, a, dt, 0 * v1, 0, 0)
    t = np.linspace(0, dt, 20001)
    v2 = np.maximum(v1 + a * dt, 0.0)
    for i in range(len(v1)):
        ai = (v2[i] - v1[i]) / dt                                     # acceleration as force_engine implies after the clamp
        vt = v1[i] + ai * t
        num = np.trapezoid(0.5 * vt ** 3, t) / dt
        assert L[i] == pytest.approx(num, rel=1e-6, abs=1e-6)


# ============================================================== B3 energy closure on driver rows
def _rows(cycle, coast=True):
    (T, S, V, A, gr, M), veh = run_driver(cycle, "ReferenceLoad", coast=coast)
    return T, S, V, A, gr, M, veh


@pytest.mark.parametrize("cycle", ["RegionalDelivery", "UrbanDelivery"])
def test_inertia_energy_telescopes_to_kinetic_energy(cycle):
    """Sum m*a*v_avg*dt == 0.5*m*(v_end^2 - v_start^2) to machine precision (VECTO routes, ILLUSTRATIVE vehicle mass)."""
    T, S, V, A, gr, M, veh = _rows(cycle)
    m = 10000.0                                                       # ILLUSTRATIVE
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR, V, A, 1.0, gr, 0.4, 0.0)
    E_in = np.sum(m * A * v_avg * 1.0)
    v_end = max(V[-1] + A[-1], 0.0)
    expect = 0.5 * m * (v_end ** 2 - V[0] ** 2)
    assert E_in == pytest.approx(expect, abs=1e-6 * m)


@pytest.mark.parametrize("cycle", ["RegionalDelivery", "UrbanDelivery"])
def test_slope_energy_vs_potential_energy_gap_is_explained(cycle):
    """sum m g sin(theta) v_avg dt vs m g (h_end - h_start): the gap = (i) sin(atan G) vs G + (ii) row distance != v_avg*dt."""
    T, S, V, A, gr, M, veh = _rows(cycle)
    m = 10000.0                                                       # ILLUSTRATIVE
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, 0.0, V, A, 1.0, gr, 0.4, 0.0)
    E_slope = np.sum(m * G * np.sin(np.arctan(gr / 100)) * v_avg)
    ds = np.append(np.diff(S), 0.0)                                   # row distance (last row: 0 - ends the route)
    dh = np.sum(gr / 100 * ds)                                        # altitude change by construction of the secant grade
    E_pot = m * G * dh
    Gr = gr / 100
    gap_i = np.sum(m * G * (np.sin(np.arctan(Gr)) - Gr) * v_avg)      # (i) angle conversion
    gap_ii = np.sum(m * G * Gr * (v_avg - ds))                        # (ii) distance snapping at stops (dt = 1)
    assert E_slope - E_pot == pytest.approx(gap_i + gap_ii, rel=1e-9, abs=1e-6)
    # sizes (printed with -s): both gaps are small relative to the potential energy scale
    scale = m * G * np.sum(np.abs(Gr) * ds)
    assert abs(gap_i) < 1e-3 * scale
    assert abs(gap_ii) < 5e-3 * scale


@pytest.mark.parametrize("cycle", ["RegionalDelivery", "UrbanDelivery"])
def test_wheel_inertia_energy_is_zero_stop_to_stop(cycle):
    T, S, V, A, gr, M, veh = _rows(cycle)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR, V, A, 1.0, gr, veh.r_dyn, veh.theta_red)
    assert abs(np.sum(k_rot)) < 1e-6 * veh.theta_red / veh.r_dyn ** 2 * 100        # sub-micro-joule per kg


# ============================================================== B4 the v2 clamp
def test_v2_clamp_inertia_vs_kinetic_energy():
    """Rows with v + a*dt < 0 (not produced by the driver): inertia energy over the row is NOT 0.5*(v2^2-v1^2).
    ILLUSTRATIVE: v = 2 m/s, a = -4 m/s^2, dt = 1 s -> v2 would be -2, clamp -> 0."""
    v, a, dt = 2.0, -4.0, 1.0
    k_lin, _, _, L, v_avg = force_engine(G, 0, [v], [a], [dt], [0.0], 0, 0)
    e_engine = k_lin[0] * dt                                           # per kg
    e_true = 0.5 * (0.0 ** 2 - v ** 2)                                 # -2 J/kg
    assert e_engine == pytest.approx(a * (v / 2) * dt)                 # a * v_avg * dt = -4 J/kg
    assert e_engine == pytest.approx(2 * e_true)                       # twice the kinetic energy: the clamp does not rescale a


def test_driver_never_produces_clamped_rows():
    for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul", "MunicipalUtility", "Construction"):
        for coast in (True, False):
            (T, S, V, A, gr, M), veh = run_driver(cyc, "ReferenceLoad", coast=coast)
            assert np.all(V + A * 1.0 >= -1e-9), (cyc, coast)


# ============================================================== B5 mass-free property
@pytest.mark.parametrize("beta", [1.0, 0.9])
def test_mass_free_property(beta):
    """P_wheel(m) from coefficients == direct force x speed, 5 masses (ILLUSTRATIVE masses)."""
    (T, S, V, A, gr, M), veh = run_driver("RegionalDelivery", "ReferenceLoad", coast=True)
    crr = veh.crr_eff(beta)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, crr, V, A, 1.0, gr, veh.r_dyn, veh.theta_red)
    tab = veh.cdxa_table()
    cd = np.interp(v_avg * 3.6, CDXA_V, tab)
    rho = 1.188
    v1 = V
    v2 = np.maximum(V + A, 0.0)
    th = np.arctan(gr / 100)
    for m in (5000.0, 7173.9, 9589.6, 15000.0, 40000.0):
        P_coef = m * k_lin + m ** beta * k_roll + k_rot + rho * cd * L
        F = m * A + m * G * np.sin(th) + crr * G * m ** beta * np.cos(th) + veh.theta_red / veh.r_dyn ** 2 * A
        with np.errstate(divide="ignore", invalid="ignore"):
            F_air = np.where(v_avg > 0, rho / 8 * cd * (v1 + v2) * (v1 ** 2 + v2 ** 2) / v_avg, 0.0)
        P_direct = (F + F_air) * v_avg
        assert np.allclose(P_coef, P_direct, rtol=1e-9, atol=1e-6)


# ============================================================== A robustness (documented behaviours)
def test_robust_theta_red_array_raises_LIMITATION():
    """LIMITATION: `if theta_red > 0` fails for an array theta_red (e.g. a per-row gear-dependent inertia)."""
    with pytest.raises(ValueError):
        force_engine(G, CRR, [10.0, 5.0], [1.0, 0.0], 1.0, [0.0, 0.0], 0.4, np.array([39.0, 39.0]))


def test_robust_r_dyn_zero_with_theta_BUG():
    """BUG (guard missing): r_dyn = 0 with theta_red > 0 -> ZeroDivisionError for Python floats; numpy floats give inf."""
    with pytest.raises(ZeroDivisionError):
        force_engine(G, CRR, [10.0], [1.0], 1.0, [0.0], 0.0, 39.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = force_engine(G, CRR, [10.0], [1.0], 1.0, [0.0], np.float64(0.0), 39.0)
    assert np.isinf(out[2][0])


@pytest.mark.parametrize("bad", [-39.0, float("nan")])
def test_robust_negative_or_nan_theta_silently_dropped_BUG(bad):
    """BUG (silent fallback, rule 3): negative or NaN theta_red is treated as 'no rotating mass' without any message."""
    out = force_engine(G, CRR, [10.0], [1.0], 1.0, [0.0], 0.4, bad)
    assert out[2][0] == 0.0


def test_robust_dt_scalar_vs_array_same():
    a = force_engine(G, CRR, [10.0, 5.0], [1.0, -1.0], 1.0, [2.0, -2.0], 0.4, 39.0)
    b = force_engine(G, CRR, [10.0, 5.0], [1.0, -1.0], np.array([1.0, 1.0]), [2.0, -2.0], 0.4, 39.0)
    for x, y in zip(a, b):
        assert np.array_equal(x, y)


def test_robust_nan_propagates_only_in_its_row():
    out = force_engine(G, CRR, [10.0, 5.0], [1.0, 0.0], 1.0, [np.nan, 0.0], 0.4, 39.0)
    assert np.isnan(out[0][0]) and np.isnan(out[1][0]) and np.isfinite(out[0][1])
    out = force_engine(G, CRR, [np.nan, 5.0], [1.0, 0.0], 1.0, [0.0, 0.0], 0.4, 39.0)
    assert all(np.isnan(o[0]) for o in out)


def test_robust_empty_arrays():
    out = force_engine(G, CRR, [], [], [], [], 0.4, 39.0)
    assert all(np.size(o) == 0 for o in out)


def test_robust_negative_speed_gives_negative_L_no_check():
    """No guard: speed < 0 gives negative L and negative v_avg (parser must check)."""
    _, _, _, L, v_avg = force_engine(G, CRR, [-5.0], [0.0], 1.0, [0.0], 0.4, 0.0)
    assert L[0] < 0 and v_avg[0] < 0


def test_robust_integer_inputs_ok():
    out = force_engine(9, 1, [10, 5], [1, 0], [1, 1], [2, 0], 1, 0)
    assert out[3][0] == pytest.approx(580.125)


def test_robust_shape_mismatch_raises():
    with pytest.raises(ValueError):
        force_engine(G, CRR, [10.0, 5.0], [1.0, 0.0, 0.0], 1.0, [0.0, 0.0], 0.4, 0.0)


# ============================================================== B6 consumption_engine steps 1-4
def _ce(T, S, V, M, dt, coef, m_vehicle, wp_s, payload_wp, beta, t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air=101325.0, R_air=287.05):
    n_wp = len(wp_s)
    out = consumption_engine(
        T, S, V, M, dt, *coef, m_vehicle, wp_s, payload_wp, beta, t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,                                  # ES PS HVAC SP cond PTO_always_on  (aux not under test)
        np.zeros(0), np.zeros(n_wp), np.zeros(n_wp),                   # pto_1s, pto_on_col, pto_start_col  (no PTO)
        1.0, 1.0, 1.0, 1.0, 0.0)                                       # efficiencies=1, v_no_regen=0 (steps 5-7 not under test)
    return out[0]                                                      # P_wheel


def _simple_case(n=20, v0=10.0):
    T = np.arange(n, dtype=float)
    V = np.full(n, v0)
    A = np.zeros(n)
    S = np.cumsum(V) - V[0]
    gr = np.zeros(n)
    coef = force_engine(G, CRR, V, A, 1.0, gr, 0.4, 0.0)
    M = np.full(n, 2)
    return T, S, V, A, M, coef


def test_step1_payload_constant_linear_custom():
    """Payload mapping by distance for the three payload_engine shapes (ILLUSTRATIVE route and payloads)."""
    wp_s = np.array([0.0, 50.0, 100.0, 150.0])
    stop = np.array([0.0, 10.0, 10.0, 0.0])
    T, S, V, A, M, coef = _simple_case(n=16, v0=10.0)
    S = np.arange(16) * 10.0                                           # rows at 0,10,...,150
    zero_m = 0.0
    k_roll = np.asarray(coef[1])
    for shape, kw, expect in (
        ("constant", dict(payload_start=1000.0), [1000.0] * 3),
        ("linear", dict(payload_start=1000.0, payload_end=0.0), [1000.0, 500.0, 0.0]),
        ("custom", dict(payload_start=1000.0, payload_custom=[1000.0, 700.0, 200.0]), [1000.0, 700.0, 200.0]),
    ):
        pl = payload_engine(stop, shape, **kw)
        Pw = _ce(T[:16], S, V[:16], M[:16], 1.0, [c[:16] for c in coef], 5000.0, wp_s, pl, 1.0, 0.0,
                 np.full(2, 15.0), np.ones((2, len(CDXA_V))), np.zeros((2, len(CDXA_V))), CDXA_V, 0.0)
        # air off (CdxA0 = 0, W2 = 0). With A = 0 and flat: P = m^beta * k_roll -> recover m per row
        m_row = Pw[:16] / k_roll[:16]
        for i, s in enumerate(S):
            seg = 0 if s < 50.0 else (1 if s < 100.0 else 2)           # last waypoint at or before the row; row at 50 -> after-stop-1 payload
            assert m_row[i] == pytest.approx(5000.0 + expect[seg]), (shape, i, s)


def test_step1_row_exactly_at_stop_distance_uses_new_payload():
    wp_s = np.array([0.0, 50.0, 100.0])
    pl = np.array([1000.0, 300.0, np.nan])
    T, S, V, A, M, coef = _simple_case(n=3)
    S = np.array([49.999, 50.0, 50.001])
    Pw = _ce(T[:3], S, V[:3], M[:3], 1.0, [c[:3] for c in coef], 5000.0, wp_s, pl, 1.0, 0.0,
             np.full(2, 15.0), np.ones((2, len(CDXA_V))), np.zeros((2, len(CDXA_V))), CDXA_V, 0.0)
    m_row = Pw / np.asarray(coef[1])[:3]
    assert m_row == pytest.approx([6000.0, 5300.0, 5300.0])            # side="right": the row AT the stop already has the new payload


def test_step1_row_before_first_waypoint_wraps_to_last_payload_BUG():
    """BUG (latent): a row with S a hair below wp_s[0] gives k_pl = -1 and picks the LAST payload.
    The driver starts exactly at wp_s[0], so this needs another source of S (GPS adapter, float error in the parser)."""
    wp_s = np.array([0.0, 50.0, 100.0])
    pl = np.array([1000.0, 300.0, 200.0])
    T, S, V, A, M, coef = _simple_case(n=2)
    S = np.array([-1e-9, 0.0])
    Pw = _ce(T[:2], S, V[:2], M[:2], 1.0, [c[:2] for c in coef], 5000.0, wp_s, pl, 1.0, 0.0,
             np.full(2, 15.0), np.ones((2, len(CDXA_V))), np.zeros((2, len(CDXA_V))), CDXA_V, 0.0)
    m_row = Pw / np.asarray(coef[1])[:2]
    assert m_row[1] == pytest.approx(6000.0)                           # correct (first payload)
    assert m_row[0] == pytest.approx(5200.0)                           # WRONG: last payload (200 kg) instead of 1000 kg


def test_step1_route_without_stops():
    wp_s = np.array([0.0, 500.0])
    stop = np.zeros(2)
    pl = payload_engine(stop, "constant", 1500.0)
    T, S, V, A, M, coef = _simple_case(n=10)
    Pw = _ce(T, S, V, M, 1.0, coef, 5000.0, wp_s, pl, 1.0, 0.0, np.full(2, 15.0),
             np.ones((2, len(CDXA_V))), np.zeros((2, len(CDXA_V))), CDXA_V, 0.0)
    assert (Pw / np.asarray(coef[1])) == pytest.approx(np.full(10, 6500.0))


def test_step2_hour_index_edge_cases():
    wp_s = np.array([0.0, 500.0])
    pl = np.array([0.0, np.nan])
    T, S, V, A, M, coef = _simple_case(n=10)
    ones = np.ones((2, len(CDXA_V)))
    # T_amb_h too short -> IndexError (loud, fine)
    T_long = T + 3600.0 * 2
    with pytest.raises(IndexError):
        _ce(T_long, S, V, M, 1.0, coef, 5000.0, wp_s, pl, 1.0, 0.0, np.full(2, 15.0), ones, 0 * ones, CDXA_V, 4.8)
    # trip crossing midnight with a continuous hourly array: hour index goes past 23, not wrapped (parser must supply a continuous array)
    t_start = 23 * 3600 + 3595.0
    Pw = _ce(T, S, V, M, 1.0, coef, 5000.0, wp_s, pl, 1.0, t_start, np.linspace(-5, 20, 26), np.ones((26, len(CDXA_V))), np.zeros((26, len(CDXA_V))), CDXA_V, 4.8)
    assert np.all(np.isfinite(Pw))
    # t_start not a whole hour: hour = floor((t_start + T)/3600)
    hour = ((1800.0 + np.array([0.0, 1799.0, 1800.0, 3599.0])) // 3600).astype(int)
    assert list(hour) == [0, 0, 1, 1]


def test_step3_cdxa_interpolation_equals_np_interp_per_hour():
    veh = Vehicle("RegionalDelivery", "ReferenceLoad")
    n = 40
    T = np.arange(n, dtype=float) + 3590.0                              # crosses an hour boundary
    rng = np.random.default_rng(0)
    V = rng.uniform(0, 30, n)
    A = np.zeros(n)
    S = np.cumsum(V) - V[0]
    coef = force_engine(G, 0.0, V, A, 1.0, np.zeros(n), 0.4, 0.0)       # only air + (zero) roll remains
    a1, a2, a3 = veh.a123
    vref = np.array([2.0, 7.0])                                         # ILLUSTRATIVE wind speed per hour
    W1, W2 = C.crosswind_engine(C.HEIGHT, vref, C.H_DECL, a1, a2, a3, C.HELLMANN, C.HEIGHT / 10, 10, CDXA_V, None)
    Pw = _ce(T, S, V, np.full(n, 2), 1.0, coef, 5000.0, np.array([0.0, 1e6]), np.array([0.0, np.nan]), 1.0, 0.0,
             np.array([15.0, 15.0]), W1, W2, CDXA_V, veh.cdxa0)
    rho = 101325.0 / (287.05 * (15.0 + 273.15))
    hour = (T // 3600).astype(int)
    tab = veh.cdxa0 * W1 + W2
    expect = np.array([rho * np.interp(coef[4][i] * 3.6, CDXA_V, tab[hour[i]]) * coef[3][i] for i in range(n)])
    assert Pw == pytest.approx(expect, rel=1e-12, abs=1e-9)
    assert set(hour) == {0, 1}                                          # the test really crosses an hour


def test_step3_below_60_and_above_130_held():
    veh = Vehicle("RegionalDelivery", "ReferenceLoad")
    tab = veh.cdxa_table()
    for v_kmh, expect in ((10.0, tab[0]), (59.9, tab[0] + (tab[1] - tab[0]) * 0), (140.0, tab[-1]), (200.0, tab[-1])):
        V = np.array([v_kmh / 3.6])
        coef = force_engine(G, 0.0, V, np.zeros(1), 1.0, np.zeros(1), 0.4, 0.0)
        W1, W2 = np.ones((1, len(CDXA_V))), np.zeros((1, len(CDXA_V)))
        Pw = _ce(np.zeros(1), np.zeros(1), V, np.full(1, 2), 1.0, coef, 5000.0, np.array([0.0, 1e6]), np.array([0.0, np.nan]), 1.0, 0.0,
                 np.array([15.0]), W1, W2, CDXA_V, veh.cdxa0)
        rho = 101325.0 / (287.05 * (15.0 + 273.15))
        assert Pw[0] == pytest.approx(rho * veh.cdxa0 * coef[3][0], rel=1e-12)   # W1 = 1, W2 = 0 -> CdxA0 flat
    # with a real table the held values are the end values
    W1, W2 = C.crosswind_engine(C.HEIGHT, np.array([3.0]), C.H_DECL, *veh.a123, C.HELLMANN, C.HEIGHT / 10, 10, CDXA_V, None)
    tab = veh.cdxa0 * W1 + W2
    for v_kmh, ref in ((10.0, tab[0, 0]), (150.0, tab[0, -1])):
        V = np.array([v_kmh / 3.6])
        coef = force_engine(G, 0.0, V, np.zeros(1), 1.0, np.zeros(1), 0.4, 0.0)
        Pw = _ce(np.zeros(1), np.zeros(1), V, np.full(1, 2), 1.0, coef, 5000.0, np.array([0.0, 1e6]), np.array([0.0, np.nan]), 1.0, 0.0,
                 np.array([15.0]), W1, W2, CDXA_V, veh.cdxa0)
        rho = 101325.0 / (287.05 * (15.0 + 273.15))
        assert Pw[0] == pytest.approx(rho * ref * coef[3][0], rel=1e-12)


def test_step3_cdxa_table_shape_contract():
    """W1, W2 must have one row per weather hour. One row for all hours -> IndexError for hour >= 1 (parser must tile)."""
    V = np.full(5, 20.0)
    coef = force_engine(G, 0.0, V, np.zeros(5), 1.0, np.zeros(5), 0.4, 0.0)
    T = np.array([0.0, 1.0, 3599.0, 3600.0, 3601.0])
    one_row = (np.ones((1, len(CDXA_V))), np.zeros((1, len(CDXA_V))))
    with pytest.raises(IndexError):
        _ce(T, np.zeros(5), V, np.full(5, 2), 1.0, coef, 5000.0, np.array([0.0, 1e6]), np.array([0.0, np.nan]), 1.0, 0.0,
            np.full(2, 15.0), *one_row, CDXA_V, 4.8)


def test_step3_rho_ideal_gas_vs_references():
    """rho = p/(R T). The only ISO 2533 sea-level anchor is 15 C -> 1.2250 kg/m3 (ISO 2533:1975, standard atmosphere).
    ISO 2533 has no table of sea-level density at -20/0/30 C (temperature there is fixed at 15 C at sea level): those
    points are checked against the ideal-gas law with ISO 2533's own R = 287.05287 J/(kg K) only (ratio test), see report [OPEN]."""
    p, R = 101325.0, 287.05                                             # HDEV values (harness P_AIR, R_AIR)
    rho15 = p / (R * (15 + 273.15))
    assert rho15 == pytest.approx(1.2250, abs=2e-4)
    R_iso = 287.05287
    for t in (-20, 0, 15, 30):
        assert p / (R * (t + 273.15)) == pytest.approx(p / (R_iso * (t + 273.15)), rel=2e-5)
