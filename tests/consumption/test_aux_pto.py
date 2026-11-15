"""Part B tests 2 and 6: each aux alone; PTO placement with the final pto_engine outputs.  Numbers ILLUSTRATIVE unless marked."""
import numpy as np
import pytest

import _e2 as E
import reference_copy as RC
from _load_notebook import NS
from _scenarios import VPTOEL_KWH, VPTOEL_T, VPTOEL_W, build_route
from _synth import base_args, old_call, rows

pto_engine = NS["pto_engine"]
NOTEBOOK = NS["consumption_engine"]


# ---------------------------------------------------------------- 2. each aux alone
@pytest.mark.parametrize("idx,name", [(0, "ES"), (1, "PS"), (2, "HVAC"), (5, "PTO_always_on")])
def test_always_on_aux_alone(idx, name):
    r = rows()
    aux = [0.0] * 6
    aux[idx] = 123.0
    a = base_args(r, aux=tuple(aux))
    _, _, P_aux, _, _ = old_call(a)
    assert np.allclose(P_aux, 123.0)
    assert np.sum(P_aux * r["dt"]) / 3.6e6 == pytest.approx(123.0 * r["n"] / 3.6e6)


def test_sp_only_when_moving_and_cond_row_counts():
    """[TEST] SP on when V > 0 (speed at the START of the row).  Count rows by V and by driver mode M (Q8)."""
    r = rows()
    aux = (0, 0, 0, 40.0, 600.0, 0)
    a = base_args(r, aux=aux)
    P_aux = old_call(a)[2]
    n_moving_V = int((r["V"] > 0).sum())
    n_not_standing_M = int((r["M"] != 0).sum())
    assert np.sum(P_aux > 0) == n_moving_V
    assert np.sum(P_aux * r["dt"]) == pytest.approx((40.0 + 600.0) * n_moving_V)
    # the first accelerating row has V == 0 (speed at the start of the step) but M == 1: V>0 and M!=0 differ by exactly that row
    assert n_not_standing_M - n_moving_V == 1
    # VECTO ElectricAuxiliaries.cs 105-116 + Vehicle.cs 326: SP is off when |v at start| <= 0.01 m/s -> same rule as V > 0


def test_cond_rule_variants_count_rows():
    r = rows()
    r["M"] = r["M"].copy(); r["M"][20:25] = 3                      # five coasting rows inside the cruise
    a = base_args(r, aux=(0, 0, 0, 0, 600.0, 0), v_no_regen=-1.0)
    moving = RC.consumption_engine_v_split_eff(**a, cond_rule="moving")["P_aux_row"]
    em_on = RC.consumption_engine_v_split_eff(**a, cond_rule="em_on")["P_aux_row"]
    # 5 coasting rows: Cond on in HDEV, off in VECTO (Conditioning.cs 83-91).  The first accelerating row (V == 0, M == 1) is the opposite: off in HDEV, on in VECTO.
    assert (moving > 0).sum() - (em_on > 0).sum() == 5 - 1


# ---------------------------------------------------------------- 6. PTO with the final pto_engine outputs
def _route(stops=(0, 25, 0), legs=(100, 100), v=10.0):   # legs in m: 10 m/s -> 10 s per 100 m
    return build_route(list(legs), list(stops), v=v)


def _pto(stop_final, is_on, t=VPTOEL_T, w=VPTOEL_W, dt=None, dw=None, se=1.0, de=1.0):
    return pto_engine(stop_final, is_on, t, w, dt if dt is not None else [0.0], dw if dw is not None else [0.0], se, de)


def _stop_profile_const(W=1000.0, sec=10):
    return list(range(sec + 1)), [W] * sec + [W]


def test_stop_profile_energy_and_position():
    rt = _route(stops=(0, 25, 0))
    t, w = _stop_profile_const(1000.0, 10)
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0], t, w)
    stop_row, drive_row, sa, da = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, ps, s1, d1, 0.0, 0.0)
    assert stop_row.sum() == pytest.approx(10 * 1000.0)
    first = np.where(rt["M"] == 0)[0]
    first = first[first >= 0][0] if False else np.where((rt["M"] == 0) & (rt["S"] == rt["wp_s"][1]))[0][0]
    assert np.where(stop_row > 0)[0][0] == first + int(np.floor((25 - 10) / 2))        # centred, floor
    assert not drive_row.any()


def test_stop_constant_fills_all_standing_rows():
    rt = _route(stops=(0, 25, 0))
    is_on = np.array([0.0, 1.0, 0.0])
    stop_row, _, sa, _ = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, np.full(3, np.nan), np.zeros(0), np.zeros(0), 500.0, 0.0)
    n_stand = int(((rt["M"] == 0) & (rt["S"] == rt["wp_s"][1])).sum())
    assert n_stand == 25 and stop_row.sum() == pytest.approx(500.0 * 25) and sa.sum() == 25


def test_drive_profile_starts_after_the_stop_and_runs_past_the_next_stop():
    rt = _route(stops=(0, 20, 0, 20, 0), legs=(300, 300, 300, 300))
    t, w = list(range(0, 71)), [2000.0] * 71
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0, 0, 0], [0.0], [0.0], t, w)
    stop_row, drive_row, sa, da = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, ps, s1, d1, 0.0, 0.0)
    assert drive_row.sum() == pytest.approx(70 * 2000.0)
    k_stand2 = np.where((rt["M"] == 0) & (rt["S"] == rt["wp_s"][3]))[0]
    assert da[k_stand2].any()                                                # keeps running through the second stop (VECTO)


def test_drive_constant_sweeper_until_next_stop_and_second_part_overlap_error():
    rt = _route(stops=(0, 20, 0, 20, 0), legs=(100, 100, 100, 100))
    is_on = np.array([0.0, 1.0, 0.0, 0.0, 0.0])
    _, drive_row, _, da = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, np.full(5, np.nan), np.zeros(0), np.zeros(0), 0.0, 3000.0)
    k_next = np.where((rt["M"] == 0) & (rt["S"] == rt["wp_s"][3]))[0][0]
    k_leave = np.where((rt["M"] == 0) & (rt["S"] == rt["wp_s"][1]))[0][-1] + 1
    assert da[k_leave:k_next].all() and not da[:k_leave].any() and not da[k_next:].any()
    # a drive PROFILE that starts again while the previous one still runs: error (VECTO PTODriveAuxiliary.cs 25-27)
    t, w = list(range(0, 400)), [1000.0] * 400
    is_on2, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0, 1, 0], [0.0], [0.0], t, w)
    with pytest.raises(ValueError):
        RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on2, ps, s1, d1, 0.0, 0.0)


def test_marker_waypoint_with_zero_stop_and_only_a_drive_part():
    """[TEST] 0 s marker waypoint (stop = 0).  OLD step 6 raises 'no standing rows'; the variant starts the drive PTO at the marker."""
    rt = _route(stops=(0, 0, 0), legs=(500, 500))
    t, w = list(range(0, 31)), [1500.0] * 31
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0], [0.0], [0.0], t, w)
    _, drive_row, _, da = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, ps, s1, d1, 0.0, 0.0)
    assert drive_row.sum() == pytest.approx(30 * 1500.0)
    k0 = int(np.searchsorted(rt["S"], rt["wp_s"][1] - 1e-3))
    assert np.where(da)[0][0] == k0
    a = base_args(rows())
    with pytest.raises(ValueError, match="no standing rows"):
        a_old = E.to_old_args(a)
        a_old.update(pto_on_col=np.array([0.0, 1.0]), pto_start_col=np.array([np.nan, 0.0]), pto_1s=np.ones(5), wp_s=np.array([0.0, 50.0]))
        NOTEBOOK(**a_old)


def test_is_on_with_only_a_drive_profile_breaks_the_old_function_int_of_nan():
    """[TEST] is_on = 1 at a real stop, but only a DRIVE profile: pto_engine gives pto_start = NaN there; old step 6 does int(NaN)."""
    rt = _route(stops=(0, 25, 0))
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0], [0.0], [0.0], list(range(11)), [500.0] * 11)
    assert np.isnan(ps[1]) and len(s1) == 0
    n = len(rt["S"])
    z = np.zeros(n)
    kw = dict(T=rt["T"], S=rt["S"], V=rt["V"], M=rt["M"], dt=z + 1, k_lin=z, k_roll=z, k_rot=z, L=z, v_avg=z, m_vehicle=1.0, wp_s=rt["wp_s"],
              payload_wp=np.array([0.0, np.nan, np.nan]), beta=1.0, t_start=0.0, T_amb_h=np.array([15.0]), W1=np.ones((1, 3)), W2=np.zeros((1, 3)),
              cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0, p_air=101325.0, R_air=287.058, ES=0, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0,
              pto_1s=s1, pto_on_col=is_on, pto_start_col=ps, motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0)
    with pytest.raises(ValueError, match="NaN"):
        NOTEBOOK(**kw)


def test_standing_rows_M0_vs_V0_gives_one_extra_row():
    """[TEST] PR #31: the first accelerating row after a stop also has V == 0.  V==0 gives stop+1 rows, M==0 gives exactly the stop."""
    rt = _route(stops=(0, 25, 0))
    at = np.isclose(rt["S"], rt["wp_s"][1], rtol=0, atol=1e-3)
    assert int((at & (rt["V"] == 0)).sum()) == 26
    assert int((at & (rt["M"] == 0)).sum()) == 25
    # consequence: a 26 s stop profile in a 25 s stop is NOT refused by the old guard (it fits the 26 V==0 rows) -> 1 s of PTO on the accelerating row
    z = np.zeros(len(rt["S"]))
    t, w = _stop_profile_const(1000.0, 26)
    is_on, ps, s1, d1 = _pto(np.array([0.0, 26.0, 0.0]), [0, 1, 0], t, w)
    kw = dict(T=rt["T"], S=rt["S"], V=rt["V"], M=rt["M"], dt=z + 1, k_lin=z, k_roll=z, k_rot=z, L=z, v_avg=z, m_vehicle=1.0, wp_s=rt["wp_s"],
              payload_wp=np.array([0.0, np.nan, np.nan]), beta=1.0, t_start=0.0, T_amb_h=np.array([15.0]), W1=np.ones((1, 3)), W2=np.zeros((1, 3)),
              cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0, p_air=101325.0, R_air=287.058, ES=0, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0,
              pto_1s=s1, pto_on_col=is_on, pto_start_col=ps, motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0)
    P_aux = NOTEBOOK(**kw)[2]
    assert P_aux.sum() == pytest.approx(26 * 1000.0)                      # old function: accepted, 26 s of PTO inside a 25 s stop
    with pytest.raises(ValueError, match="does not fit"):
        RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], np.array([0.0, 25.0, 0.0]), is_on, ps, s1, d1, 0.0, 0.0)


def test_stop_at_the_last_waypoint():
    rt = _route(stops=(0, 0, 30), legs=(100, 100))
    t, w = _stop_profile_const(800.0, 10)
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 0, 1], t, w)
    stop_row, *_ = RC.pto_rows(rt["S"], rt["M"], rt["wp_s"], rt["stop_wp"], is_on, ps, s1, d1, 0.0, 0.0)
    assert stop_row.sum() == pytest.approx(10 * 800.0)


def test_two_stops_at_one_distance_are_silently_doubled_so_the_parser_must_reject():
    """[TEST] two stop waypoints at the SAME distance: both find the same standing rows and the PTO is laid twice.  PARSER JOB."""
    rt = _route(stops=(0, 25, 0), legs=(100, 100))
    wp_s = np.array([0.0, 100.0, 100.0, 200.0])
    stop_wp = np.array([0.0, 25.0, 25.0, 0.0])
    t, w = _stop_profile_const(1000.0, 10)
    is_on, ps, s1, d1 = _pto(stop_wp, [0, 1, 1, 0], t, w)
    stop_row, *_ = RC.pto_rows(rt["S"], rt["M"], wp_s, stop_wp, is_on, ps, s1, d1, 0.0, 0.0)
    assert stop_row.sum() == pytest.approx(2 * 10 * 1000.0)


def test_refuse_cycle_14_393_kwh_reproduced_exactly():
    """[TEST] MunicipalUtility.vdri, 96 PTO stops x one VECTO generic refuse profile (0.14993 kWh) = 14.393 kWh [VECTO .vptoel, CALC]."""
    import _rows as R
    cy = R.read_vdri("MunicipalUtility")
    flag = cy["pto"] == 1
    assert int(flag.sum()) == 96
    stop_final = cy["stop"].copy()
    stop_final[flag] += len(VPTOEL_T) - 1                                      # standing time = stop + PTO duration (VECTO DistanceBasedDrivingCycle.cs 218-220)
    is_on, ps, s1, d1 = _pto(stop_final, flag.astype(float))
    T, S, V, A, G_, M = R.run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)
    stop_row, _, sa, _ = RC.pto_rows(S, M, cy["s"], stop_final, is_on, ps, s1, d1, 0.0, 0.0)
    assert stop_row.sum() / 3.6e6 == pytest.approx(96 * VPTOEL_KWH, abs=1e-9)
    assert 96 * VPTOEL_KWH == pytest.approx(14.393, abs=5e-4)
    # the old function lays the same PTO energy (V==0 start row is the same first standing row)
    n = len(T)
    z = np.zeros(n)
    kw = dict(T=T, S=S, V=V, M=M, dt=z + 1, k_lin=z, k_roll=z, k_rot=z, L=z, v_avg=z, m_vehicle=1.0, wp_s=cy["s"], payload_wp=np.r_[0.0, np.full(len(cy["s"]) - 1, np.nan)],
              beta=1.0, t_start=0.0, T_amb_h=np.array([15.0] * 3), W1=np.ones((3, 3)), W2=np.zeros((3, 3)), cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0,
              p_air=101325.0, R_air=287.058, ES=0, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0, pto_1s=s1, pto_on_col=is_on, pto_start_col=ps,
              motor_eff=1, inverter_eff=1, gearbox_eff=1, regen_effeiciency=1, v_no_regen=-1.0)
    assert NOTEBOOK(**kw)[2].sum() / 3.6e6 == pytest.approx(96 * VPTOEL_KWH, abs=1e-9)


def test_step6_searchsorted_variant_gives_identical_numbers_to_the_old_loop():
    """[TEST] consumption_engine_v_step6_searchsorted == Appendix 1 on a route with several PTO stops."""
    rt = _route(stops=(0, 25, 0, 25, 0), legs=(100, 100, 100, 100))
    t, w = _stop_profile_const(1000.0, 10)
    is_on, ps, s1, d1 = _pto(rt["stop_wp"], [0, 1, 0, 1, 0], t, w)
    n = len(rt["S"]); z = np.zeros(n)
    kw = dict(T=rt["T"], S=rt["S"], V=rt["V"], M=rt["M"], dt=z + 1, k_lin=z + 0.1, k_roll=z, k_rot=z, L=z, v_avg=z, m_vehicle=1000.0, wp_s=rt["wp_s"],
              payload_wp=np.r_[0.0, np.full(4, np.nan)], beta=1.0, t_start=0.0, T_amb_h=np.array([15.0]), W1=np.ones((1, 3)), W2=np.zeros((1, 3)),
              cdxa_v=np.array([0.0, 36.0, 144.0]), CdxA0=1.0, p_air=101325.0, R_air=287.058, ES=100.0, PS=0, HVAC=0, SP=10.0, cond=300.0, PTO_always_on=0,
              pto_1s=s1, pto_on_col=is_on, pto_start_col=ps, motor_eff=0.9, inverter_eff=0.95, gearbox_eff=0.98, regen_effeiciency=0.85, v_no_regen=1.0)
    a = NOTEBOOK(**kw)
    b = RC.consumption_engine_v_step6_searchsorted(**kw)
    for x, y in zip(a, b):
        assert np.array_equal(np.asarray(x), np.asarray(y))
