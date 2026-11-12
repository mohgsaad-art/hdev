"""Part B.3: notebook SP_power_helper (cell 10), unchanged."""
import numpy as np
import pytest

from _load_notebook import NS
import reference_copy as RC

SP = NS["SP_power_helper"]
BASE = [290, 30, 20]                     # SP-Table.csv group 2 Regional delivery, in W (the cell is 290/30/20)
FULL_EL = [0.0, 0.143, 1.429]            # SP-Tech.csv "Full electric steering gear"
ELEC_PUMP = [0.857, 0.857, 0.857]        # SP-Tech.csv "Electric driven pump"
AX = [[100, 100, 100], [100, 70, 70], [100, 50, 50], [100, 50, 50]]   # SP-Axles.csv rows 1..4


def test_one_axle_e2_regional_is_32_87():
    assert SP(BASE, AX[:1], [FULL_EL]) == pytest.approx(32.87, abs=1e-9)        # x0.7 in P_aux = 23.009 W; .vmod 23.0 W


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_1_to_4_axles_hand_calc(n):
    shares = np.array(AX[:n], dtype=float)
    facs = np.array([ELEC_PUMP] * n)
    expect = float(np.sum(np.array(BASE) * shares.sum(axis=0) / 100 * facs.mean(axis=0)))
    assert SP(BASE, AX[:n], [ELEC_PUMP] * n) == pytest.approx(expect)


def test_five_axles_accepted_but_VECTO_has_no_row_5():
    """VECTO SP-Axles.csv has rows 1..4; the 5th steered axle is a lookup error in VECTO (SteeringPump.cs 80).  The notebook helper
    happily computes it (shares given by the caller).  The MAX is a parser check (table-driven)."""
    out = SP(BASE, AX + [[100, 50, 50]], [ELEC_PUMP] * 5)
    assert out > SP(BASE, AX, [ELEC_PUMP] * 4)


def test_tech_rows_must_match_axle_rows():
    with pytest.raises(ValueError, match="technology"):
        SP(BASE, AX[:2], [FULL_EL])


@pytest.mark.parametrize("shares", [[], [[]], [100, 100, 100], [[100, 100]], [[100, 100, 100, 100]]])
def test_bad_share_shapes_raise(shares):
    with pytest.raises(ValueError):
        SP(BASE, shares, [FULL_EL])


def test_empty_arrays_raise_clear_error():
    with pytest.raises(ValueError, match="steered axle"):
        SP(BASE, np.empty((0, 3)), np.empty((0, 3)))


@pytest.mark.parametrize("base", [[290, 30], [290, 30, 20, 5]])
def test_wrong_baseline_length_raises_numpy_error(base):
    with pytest.raises(ValueError):
        SP(base, AX[:1], [FULL_EL])


def test_BUG_scalar_baseline_is_broadcast_silently():
    """BUG-ish: SP_baseline=290 (scalar) is broadcast to (290, 290, 290) -> 870 W; no shape check on the baseline."""
    assert SP(290, AX[:1], [[1, 1, 1]]) == pytest.approx(870.0)
    with pytest.raises(ValueError):
        RC.SP_power_helper_v_checks(290, AX[:1], [[1, 1, 1]])


def test_BUG_2d_baseline_is_accepted():
    assert SP([[290, 30, 20]], AX[:1], [[1, 1, 1]]) == pytest.approx(340.0)
    with pytest.raises(ValueError):
        RC.SP_power_helper_v_checks([[290, 30, 20]], AX[:1], [[1, 1, 1]])


def test_BUG_nan_negative_and_oversize_values_are_accepted():
    assert np.isnan(SP([290, np.nan, 20], AX[:1], [[1, 1, 1]]))
    assert SP([-290, 30, 20], AX[:1], [[1, 1, 1]]) < 0
    assert SP(BASE, [[300, 300, 300]], [[1, 1, 1]]) == pytest.approx(3 * 340.0)             # share 300 % accepted
    for bad in (([290, np.nan, 20], AX[:1], [[1, 1, 1]]), ([-1, 30, 20], AX[:1], [[1, 1, 1]]), (BASE, [[300] * 3], [[1, 1, 1]]),
                (BASE, AX[:1], [[-1, 1, 1]])):
        with pytest.raises(ValueError):
            RC.SP_power_helper_v_checks(*bad)


def test_checks_variant_equals_notebook_on_valid_input():
    assert RC.SP_power_helper_v_checks(BASE, AX[:2], [FULL_EL, ELEC_PUMP]) == SP(BASE, AX[:2], [FULL_EL, ELEC_PUMP])
