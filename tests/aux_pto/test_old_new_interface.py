"""Part B.5: the notebook consumption_engine still takes the OLD pto_engine outputs (pto_1s, pto_on_col, pto_start_col).
Here the 1 Nov outputs (stop_1s, is_on, pto_start) are passed into those slots to show exactly what breaks.  ILLUSTRATIVE routes."""
import numpy as np
import pytest

from _load_notebook import NS
from _scenarios import build_route, VPTOEL_T, VPTOEL_W
from _ce import call_ce

pto = NS["pto_engine"]
NONE = ([0.0], [0.0])


def new_outputs(route, is_on, drive=NONE, stop=(VPTOEL_T, VPTOEL_W)):
    return pto(route["stop_wp"], is_on, stop[0], stop[1], drive[0], drive[1], 1.0, 1.0)


def test_normal_refuse_stop_works_through_old_slots():
    r = build_route([1000, 1000], [10, 25, 10])
    is_on, start, s1, d1 = new_outputs(r, [0, 1, 0.0])
    out = call_ce(r, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)
    assert out[4] == pytest.approx(23 * 0 + s1.sum() / 3.6e6, rel=1e-9)               # all traction forces are 0 -> E = PTO energy


def test_BREAKS_marker_waypoint_is_on_without_stop_raises_no_standing_rows():
    """is_on == 1 on a 0 s marker waypoint (the new design lets it start a drive part) -> old engine: 'no standing rows found'."""
    r = build_route([1000, 1000], [10, 0, 25])
    is_on, start, s1, d1 = new_outputs(r, [0, 1, 0.0], drive=([0, 60], [4000, 0]))
    assert is_on[1] == 1 and np.isnan(start[1])
    with pytest.raises(ValueError, match="no standing rows found"):
        call_ce(r, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)


def test_BREAKS_is_on_with_drive_part_only_at_a_real_stop_gives_int_nan_error():
    """Real stop, is_on == 1, but only a DRIVE profile (stop profile empty): pto_start is NaN -> int(NaN) in the old engine."""
    r = build_route([1000, 1000], [10, 25, 10])
    is_on, start, s1, d1 = new_outputs(r, [0, 1, 0.0], drive=([0, 60], [4000, 0]), stop=NONE)
    assert len(s1) == 0 and np.isnan(start[1])
    with pytest.raises(ValueError, match="cannot convert float NaN"):
        call_ce(r, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)


def test_BREAKS_drive_profile_is_silently_dropped():
    r = build_route([1000, 1000], [10, 25, 10])
    is_on, start, s1, d1 = new_outputs(r, [0, 1, 0.0], drive=([0, 60], [4000, 0]))
    out = call_ce(r, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)
    assert len(d1) == 60 and d1.sum() > 0
    assert out[4] == pytest.approx(s1.sum() / 3.6e6)                                    # drive energy (60 s x 4 kW = 0.0667 kWh) is missing


def test_BREAKS_no_slot_for_constants():
    """The signature has no argument for a stop constant or a drive constant."""
    import inspect
    params = inspect.signature(NS["consumption_engine"]).parameters
    assert not [p for p in params if "const" in p.lower() or "drive" in p.lower()]


def test_is_on_values_other_than_1_are_ignored_by_the_old_engine():
    r = build_route([1000, 1000], [10, 25, 10])
    is_on, start, s1, d1 = new_outputs(r, [0, 0.5, 0.0])
    assert start[1] == 1                                                               # pto_engine computed a start (is_on > 0): floor((25-23)/2)
    out = call_ce(r, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)
    assert out[4] == 0.0                                                               # consumption_engine tests == 1: nothing placed


def test_stop_profile_longer_than_standing_rows_raises():
    r = build_route([1000, 1000], [10, 25, 10])
    long_profile = np.ones(30) * 1000.0
    with pytest.raises(ValueError, match="does not fit"):
        call_ce(r, pto_1s=long_profile, pto_on_col=np.array([0, 1, 0.0]), pto_start_col=np.array([np.nan, 0, np.nan]))


def test_two_stops_at_the_same_distance_both_match_the_same_rows():
    """Two waypoints at one distance: the old engine matches BOTH to the same standing rows (PTO placed twice, overwritten, no error)."""
    r = build_route([1000, 1000], [10, 25, 10])
    r2 = dict(r)
    r2["wp_s"] = np.array([0.0, 1000.0, 1000.0])
    out = call_ce(r2, pto_1s=np.ones(23) * 1000, pto_on_col=np.array([0, 1, 1.0]), pto_start_col=np.array([np.nan, 1, 1]))
    assert out[4] == pytest.approx(23 * 1000 / 3.6e6)                                  # counted once because `=` overwrites, not `+=`


def test_BUG_PTO_always_on_per_hour_array_is_not_indexed_by_hour():
    """PTO_always_on as a per-hour array is ADDED to the rows without [hour]: wrong length -> numpy error; same length -> silently
    mis-indexed (hour 0 value goes to row 0, hour 1 value to row 1 ...)."""
    r = build_route([100, 100], [3, 3, 3])
    n = len(r["S"])
    with pytest.raises(ValueError, match="broadcast"):
        call_ce(r, PTO_always_on=np.array([100.0, 200.0, 300.0]))                      # 3 hours, n rows != 3
    arr = np.arange(n, dtype=float) * 10.0                                             # n values 'per hour' by accident -> accepted
    out = call_ce(r, PTO_always_on=arr)
    assert np.allclose(out[2], arr)                                                    # P_aux_row == the array itself: row-indexed, not hour-indexed
    # HVAC, by contrast, IS hour-indexed
    out2 = call_ce(r, HVAC=np.array([100.0, 200.0, 300.0]))
    assert np.allclose(out2[2], 100.0)                                                 # all rows are in hour 0
