"""Part D: consumption_step6_v_pto1nov (reference_copy.py).  Numbers marked ILLUSTRATIVE are test values."""
import numpy as np
import pytest

import reference_copy as RC
from _load_notebook import NS
from _scenarios import build_route, VPTOEL_T, VPTOEL_W, VPTOEL_KWH

pto = NS["pto_engine"]
NONE = ([0.0], [0.0])


def place(r, on, stop=(VPTOEL_T, VPTOEL_W), drive=NONE, stop_const=0.0, drive_const=0.0, se=1.0, de=1.0, use_M=True):
    is_on, ps, s1, d1 = pto(r["stop_wp"], on, stop[0], stop[1], drive[0], drive[1], se, de)
    return RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on, ps, s1, d1, stop_const_W=stop_const,
                                          drive_const_W=drive_const, stop_eff=se, drive_eff=de, M=r["M"] if use_M else None)


def test_stop_profile_energy_and_centering():
    r = build_route([1000, 1000], [10, 25, 10])
    row, sa, da, ev = place(r, [0, 1, 0.0])
    assert row.sum() / 3.6e6 == pytest.approx(VPTOEL_KWH)
    first = np.where((r["M"] == 0) & (np.abs(r["S"] - 1000) < 1e-3))[0][0]
    assert ev[0]["k0"] - first == 1 and sa.sum() == 23                                  # 1 s idle before, PTO 23 s, 1 s idle after


def test_stop_constant_uses_standing_rows_only_and_divides_by_eff():
    r = build_route([1000, 1000], [10, 25, 10])
    row, sa, da, ev = place(r, [0, 1, 0.0], stop=NONE, stop_const=3000.0, se=0.8)
    assert sa.sum() == 25 and row.max() == pytest.approx(3750.0)
    assert row.sum() / 3.6e6 == pytest.approx(3750 * 25 / 3.6e6)


def test_off_by_one_if_standing_rows_are_found_by_V0_only():
    """With the notebook driver layout the first accelerating row also has V == 0: V==0 alone gives stop+1 rows (+4 % for a 25 s stop)."""
    r = build_route([1000, 1000], [10, 25, 10])
    row_v, sa_v, _, _ = place(r, [0, 1, 0.0], stop=NONE, stop_const=3000.0, use_M=False)
    row_m, sa_m, _, _ = place(r, [0, 1, 0.0], stop=NONE, stop_const=3000.0, use_M=True)
    assert sa_v.sum() == 26 and sa_m.sum() == 25


def test_sweeper_drive_constant_from_marker_to_next_stop():
    r = build_route([1000] * 5, [10, 0, 30, 0, 30, 10])
    row, sa, da, ev = place(r, [0, 1, 0, 0, 0, 0.0], stop=NONE, drive_const=6000.0, de=0.9)
    assert da.sum() == 100 and row.max() == pytest.approx(6000 / 0.9)                   # 1000 m at 10 m/s from the marker to wp2's first standing row
    assert ev[0]["kind"] == "drive_const"


def test_drive_const_starts_after_a_real_stop_and_ends_at_next_stop():
    r = build_route([1000, 1000, 1000], [10, 30, 30, 10])
    row, sa, da, ev = place(r, [0, 1, 0, 0.0], stop=NONE, drive_const=2000.0)
    first_stop2 = np.where((r["M"] == 0) & (np.abs(r["S"] - 2000) < 1e-3))[0][0]
    assert ev[0]["k1"] == first_stop2 and row[:ev[0]["k0"]].sum() == 0 and row[first_stop2:].sum() == 0


def test_mixed_refuse_stop_profile_plus_drive_profile():
    r = build_route([1000, 1000, 1000, 1000], [10, 0, 25, 0, 25])
    row, sa, da, ev = place(r, [0, 0, 1, 0, 1.0], drive=([0, 60], [4000, 0]))
    assert row.sum() / 3.6e6 == pytest.approx(2 * VPTOEL_KWH + 0 * 1) or True
    kinds = [e["kind"] for e in ev]
    assert kinds.count("stop_profile") == 2 and kinds.count("drive_profile") == 1       # the 2nd stop is the last waypoint: no rows after it
    assert row.sum() / 3.6e6 == pytest.approx(2 * VPTOEL_KWH + 4000 * 60 / 3.6e6)


def test_drive_profile_keeps_running_through_the_next_stop():
    r = build_route([100, 100, 1000], [10, 20, 20, 10])
    row, sa, da, ev = place(r, [0, 1, 0, 0.0], stop=NONE, drive=([0, 60], [4000, 0]))
    nxt = np.where((r["M"] == 0) & (np.abs(r["S"] - 200) < 1e-3))[0][0]                  # first standing row of wp2
    assert ev[0]["runs_past_next_stop"] and da[nxt:nxt + 20].all() and row.sum() / 3.6e6 == pytest.approx(4000 * 60 / 3.6e6)


def test_overlapping_drive_profiles_raise_like_vecto():
    r = build_route([100, 100, 1000], [10, 20, 20, 10])
    with pytest.raises(ValueError, match="still runs"):
        place(r, [0, 1, 1, 0.0], stop=NONE, drive=([0, 60], [4000, 0]))


def test_drive_profile_longer_than_route_is_truncated_and_flagged():
    r = build_route([100], [10, 20])
    r2 = build_route([1000, 100], [10, 20, 0])
    row, sa, da, ev = place(r2, [0, 1, 0.0], stop=NONE, drive=([0, 600], [3000, 0]))
    assert ev[0]["truncated"] and row.sum() / 3.6e6 < 3000 * 600 / 3.6e6


def test_pto_on_last_waypoint_has_no_drive_rows():
    r = build_route([1000, 1000], [10, 25, 25])
    row, sa, da, ev = place(r, [0, 0, 1.0], drive=([0, 60], [4000, 0]))
    assert da.sum() == 0 and row.sum() / 3.6e6 == pytest.approx(VPTOEL_KWH)


def test_marker_with_stop_profile_configured_places_only_the_drive_part():
    r = build_route([1000, 1000], [10, 0, 25])
    row, sa, da, ev = place(r, [0, 1, 0.0], drive=([0, 60], [4000, 0]))
    assert sa.sum() == 0 and da.sum() == 60


def test_is_on_depot_is_ignored():
    r = build_route([1000], [10, 25])
    row, sa, da, ev = place(r, [1, 0.0])
    assert row.sum() == 0


def test_two_stops_same_distance_rejected():
    r = build_route([1000, 1000], [10, 25, 25])
    r["wp_s"] = np.array([0.0, 1000.0, 1000.0])
    with pytest.raises(ValueError, match="same distance"):
        place(r, [0, 1, 1.0])
    with pytest.raises(ValueError, match="same distance"):
        RC.parser_check_pto(r["stop_wp"], [0, 1, 1.0], wp_s=r["wp_s"])


@pytest.mark.parametrize("drift,ok", [(0.0, True), (5e-4, True), (9e-4, True), (2e-3, False)])
def test_float_drift_in_distance(drift, ok):
    r = build_route([1000, 1000], [10, 25, 10])
    r["wp_s"] = r["wp_s"] + np.array([0, drift, 0])
    if ok:
        assert place(r, [0, 1, 0.0])[0].sum() > 0
    else:
        with pytest.raises(ValueError, match="no standing rows"):
            place(r, [0, 1, 0.0])


def test_profile_and_constant_together_rejected():
    r = build_route([1000, 1000], [10, 25, 10])
    is_on, ps, s1, d1 = pto(r["stop_wp"], [0, 1, 0.0], VPTOEL_T, VPTOEL_W, NONE[0], NONE[1], 1.0, 1.0)
    with pytest.raises(ValueError, match="OR a constant"):
        RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on, ps, s1, d1, stop_const_W=1000.0, M=r["M"])


def test_fast_and_slow_row_matching_give_identical_results():
    r = build_route([1000, 1000, 1000], [10, 25, 30, 10])
    is_on, ps, s1, d1 = pto(r["stop_wp"], [0, 1, 1, 0.0], VPTOEL_T, VPTOEL_W, NONE[0], NONE[1], 1.0, 1.0)
    a = RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on, ps, s1, d1, M=r["M"], fast=True)[0]
    b = RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on, ps, s1, d1, M=r["M"], fast=False)[0]
    assert np.array_equal(a, b)


def test_municipal_utility_96_stops_energy_and_standing_time():
    """MunicipalUtility.vdri + VECTO refuse profile on every stop the vdri flags (PTO column == 1).  Driver rows from the notebook driver_model."""
    from _rows import read_vdri, run_driver_e2
    cy = read_vdri("MunicipalUtility")
    flag = cy["pto"] == 1
    assert flag.sum() == 96
    stop_final = cy["stop"].copy()
    stop_final[flag] += 23
    is_on, ps, s1, d1 = pto(stop_final, flag.astype(float), VPTOEL_T, VPTOEL_W, NONE[0], NONE[1], 1.0, 1.0)
    T, S, V, A, G, M = run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)
    row, sa, da, ev = RC.consumption_step6_v_pto1nov(S, V, cy["s"], stop_final, is_on, ps, s1, d1, M=M)
    assert row.sum() / 3.6e6 == pytest.approx(96 * 0.14993, abs=5e-4)
    assert row.sum() / 3.6e6 == pytest.approx(96 * VPTOEL_KWH, abs=1e-9)
    assert len(ev) == 96
    for e in ev:
        i = e["wp"]
        rows = np.where((M == 0) & (V == 0) & (np.abs(S - cy["s"][i]) <= 1e-3))[0]
        assert len(rows) == 25                                                         # 2 s stop + 23 s PTO
        assert e["k0"] - rows[0] == 1 and rows[-1] + 1 - e["k1"] == 1                  # centred: 1 s idle each side (VECTO 3-phase: StoppingTime/2)


def test_municipal_utility_time_without_pto_extension_is_much_shorter():
    from _rows import read_vdri, run_driver_e2
    cy = read_vdri("MunicipalUtility")
    flag = cy["pto"] == 1
    t0 = run_driver_e2(cy, "ReferenceLoad")[0][-1]
    stop_final = cy["stop"].copy()
    stop_final[flag] += 23
    t1 = run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)[0][-1]
    assert t1 - t0 == pytest.approx(96 * 23, abs=3)                                     # forgetting the 23 s extension loses 2208 s of standing time


def test_cond_rule_during_stop_pto_current_notebook_rule_has_cond_on():
    """Notebook rule: cond * (moving | pto_active) -> Cond runs during the stop PTO (VECTO: EPTOOn keeps Cond on, Conditioning.cs 86)."""
    r = build_route([1000, 1000], [10, 25, 10])
    row, sa, da, ev = place(r, [0, 1, 0.0])
    on = RC.aux_row_variant("current", r["V"], sa | da, 0, 0, 0, 0, 550.0, 0, row)
    standing = (r["M"] == 0) & (np.abs(r["S"] - 1000) < 1e-3)
    assert (on[sa] == 550.0 + row[sa]).all() and (on[standing & ~sa] == 0).all()
