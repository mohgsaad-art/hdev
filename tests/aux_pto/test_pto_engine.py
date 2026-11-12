"""Part B.4: notebook pto_engine (cell 14), unchanged."""
import warnings

import numpy as np
import pytest

from _load_notebook import NS
import reference_copy as RC
from _scenarios import VPTOEL_T, VPTOEL_W, VPTOEL_KWH

pto = NS["pto_engine"]
NONE = ([0.0], [0.0])


def run(stop, on, st=VPTOEL_T, sw=VPTOEL_W, dt=NONE[0], dw=NONE[1], se=1.0, de=1.0):
    return pto(stop, on, st, sw, dt, dw, se, de)


def test_vecto_refuse_profile_from_the_file():
    """Reads the real .vptoel (kW) and converts to W the way the parser will."""
    import os, csv
    from _load_notebook import REPO
    p = os.path.join(REPO, "reference", "vecto", "resources", "MissionCycles", "MunicipalUtility_PTO_generic.vptoel")
    rows = [l.split(",") for l in open(p).read().splitlines()[1:] if l.strip()]
    t = [float(r[0]) for r in rows]
    w = [float(r[1]) * 1000.0 for r in rows]
    is_on, start, stop_1s, drive_1s = run([0, 25], [0, 1], t, w)
    assert len(stop_1s) == 23                                            # t = 0..23 -> 23 steps of 1 s
    assert stop_1s.sum() / 3.6e6 == pytest.approx(0.14993, abs=5e-6)     # 5*8.42 + 4*33.69 + 14*25.92 kJ = 539.74 kJ
    assert stop_1s.sum() / 3.6e6 == pytest.approx(VPTOEL_KWH)
    assert len(drive_1s) == 0 and start[1] == 1


@pytest.mark.parametrize("stop,expect", [(23, 0), (24, 0), (25, 1), (26, 1), (27, 2), (30, 3), (45, 11)])
def test_centering_even_odd_exact(stop, expect):
    assert run([0, stop], [0, 1])[1][1] == expect                         # floor((stop - 23) / 2)


def test_stop_exactly_equal_to_profile_starts_at_zero():
    assert run([0, 23], [0, 1])[1][1] == 0


def test_stop_one_second_short_raises():
    with pytest.raises(ValueError, match="longer than the stop"):
        run([0, 22], [0, 1])


def test_is_on_first_forced_zero_and_input_not_mutated():
    on = [1, 1]
    out = run([30, 30], on)
    assert out[0][0] == 0 and on == [1, 1]
    assert np.isnan(out[1][0])


def test_is_on_length_mismatch_raises_unclear_numpy_error():
    with pytest.raises(ValueError, match="broadcast"):
        run([0, 30, 30], [0, 1])


def test_BUG_is_on_values_other_than_0_1_are_accepted():
    """is_on = 2 or 0.5 is accepted: stop_on uses `> 0`, but the consumption engine uses `== 1`, so 0.5/2 silently do nothing there."""
    assert run([0, 30], [0, 2])[1][1] == 3 and run([0, 30], [0, 0.5])[1][1] == 3
    with pytest.raises(ValueError):
        RC.parser_check_pto([0, 30], [0, 2])


def test_BUG_fractional_profile_times_truncate_energy_silently():
    """t = [0, 1.5, 3]: np.diff = [1.5, 1.5] -> astype(int) = [1, 1].  True energy 1000*1.5 + 2000*1.5 = 4500 Ws; engine gives 3000 Ws (-33 %)."""
    out = run([0, 30], [0, 1], [0, 1.5, 3.0], [1000, 2000, 3000])
    true_Ws = 1000 * 1.5 + 2000 * 1.5
    got_Ws = out[2].sum()
    assert len(out[2]) == 2 and got_Ws == 3000 and got_Ws / true_Ws - 1 == pytest.approx(-1 / 3)
    with pytest.raises(ValueError, match="whole seconds"):
        RC.parser_check_pto([0, 30], [0, 1], [0, 1.5, 3.0], [1000, 2000, 3000])


def test_BUG_sub_second_profile_vanishes_completely():
    out = run([0, 30], [0, 1], [0, 0.5, 1.0], [1000, 2000, 3000])
    assert len(out[2]) == 0 and np.isnan(out[1][1])                        # -100 %, and no PTO start either


def test_non_increasing_times_raise_obscure_numpy_error_and_plateau_passes():
    with pytest.raises(ValueError, match="repeats"):
        run([0, 30], [0, 1], [0, 5, 3, 8], [1, 2, 3, 4])
    assert len(run([0, 30], [0, 1], [0, 5, 5, 8], [1, 2, 3, 4])[2]) == 8     # a 0 s step is dropped silently
    with pytest.raises(ValueError, match="increasing"):
        RC.parser_check_pto([0, 30], [0, 1], [0, 5, 5, 8], [1, 2, 3, 4])


def test_one_point_profile_gives_empty_stop_1s_and_no_pto_start():
    is_on, start, s1, d1 = run([0, 30], [0, 1], [0.0], [1000.0])
    assert len(s1) == 0 and np.isnan(start[1]) and is_on[1] == 1          # is_on stays 1 although nothing is placed


def test_two_point_zero_profile_is_a_one_second_profile_not_empty():
    """[0,1],[0,0] is a 1 s zero-power profile (pto_dur = 1), not 'no profile'.  'No profile' must be a 1-point or empty array."""
    out = run([0, 30], [0, 1], [0, 1], [0, 0])
    assert len(out[2]) == 1 and out[1][1] == 14


def test_zero_length_drive_profile():
    assert len(run([0, 30], [0, 1], dt=[0.0], dw=[0.0])[3]) == 0
    assert len(run([0, 30], [0, 1], dt=[], dw=[])[3]) == 0


def test_BUG_negative_power_accepted():
    assert run([0, 30], [0, 1], [0, 2, 4], [-1000, -2000, -3000])[2][0] == -1000
    with pytest.raises(ValueError, match="negative"):
        RC.parser_check_pto([0, 30], [0, 1], [0, 2, 4], [-1000, -2000, -3000])


def test_BUG_efficiency_zero_negative_and_above_one():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert np.isinf(run([0, 30], [0, 1], [0, 2, 4], [1000, 2000, 3000], se=0.0)[2][0])
        assert np.isinf(run([0, 30], [0, 1], dt=[0, 2, 4], dw=[1000, 2000, 3000], de=0.0)[3][0])
    assert any("divide by zero" in str(x.message) for x in w)
    assert run([0, 30], [0, 1], [0, 2, 4], [1000, 2000, 3000], se=-1.0)[2][0] == -1000
    assert run([0, 30], [0, 1], [0, 2, 4], [1000, 2000, 3000], se=2.0)[2][0] == 500          # eff 2 -> electric is HALF of shaft
    for bad in (0.0, -1.0, 2.0):
        with pytest.raises(ValueError, match="must be in"):
            RC.parser_check_pto([0, 30], [0, 1], stop_pto_eff=bad)


def test_pto_start_nan_on_non_pto_waypoints_and_downstream():
    """NaN is the 'no stop profile here' marker.  It is only dangerous if is_on == 1 there and a consumer does int(NaN)."""
    is_on, start, s1, d1 = run([0, 30, 0, 30], [0, 1, 1, 0])
    assert np.isnan(start[2]) and is_on[2] == 1                            # marker waypoint (stop 0) stays is_on == 1
    assert np.isnan(start[3])


def test_BUG_negative_or_nan_stop_is_silently_treated_as_no_stop():
    assert np.isnan(run([0, -5], [0, 1])[1][1]) and np.isnan(run([0, np.nan], [0, 1])[1][1])
    with pytest.raises(ValueError):
        RC.parser_check_pto([0, -5], [0, 1])


def test_BUG_time_not_starting_at_zero_start_offset_is_ignored():
    assert len(run([0, 30], [0, 1], [5, 10, 15], [1000, 2000, 3000])[2]) == 10


def test_profile_length_mismatch_raises():
    with pytest.raises(ValueError):
        run([0, 30], [0, 1], [0, 2, 4], [1000, 2000])
