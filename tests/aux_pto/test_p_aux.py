"""Part B.1: notebook P_aux (cell 9), unchanged, loaded by _load_notebook.  Numbers marked ILLUSTRATIVE are test values."""
import warnings

import numpy as np
import pytest

from _load_notebook import NS
import reference_copy as RC

P_aux = NS["P_aux"]


def test_scalar_vecto_e2_regional():
    # VECTO E2 Regional table values (ES-Tech 1428.5714, PS-Table _el 200, HVAC-Table 200, SP 32.87 mech, Cond 600) -> .vmod W
    es, ps, hv, sp, cd, pto = P_aux(1428.5714, 200, 200, 32.87, 600, 0)
    assert es == pytest.approx(1000.0, abs=1e-3)
    assert ps == 200 and hv == 250 and cd == 600 and pto == 0
    assert sp == pytest.approx(23.009, abs=1e-3)           # .vmod shows 0.0230 kW (4-decimal kW print)


def test_lists_and_arrays_per_hour():
    out = P_aux([1000, 2000], [0, 0], [100, 200], [10, 20], [5, 6], [0, 100.0])      # ILLUSTRATIVE
    assert np.allclose(out[0], [700, 1400]) and np.allclose(out[2], [125, 250]) and np.allclose(out[5], [0, 100])


def test_always_on_pto_per_hour_array_works_in_p_aux():
    pto = np.array([0.0, 500.0, 1000.0])                                                  # ILLUSTRATIVE fridge per hour
    out = P_aux(0, 0, 0, 0, 0, pto, PTO_eff=0.5)
    assert np.allclose(out[5], [0, 1000, 2000])


def test_every_aux_zero():
    assert all(float(x) == 0.0 for x in P_aux(0, 0, 0, 0, 0, 0))


@pytest.mark.parametrize("pos", range(5))
def test_negative_aux_power_raises(pos):
    args = [1.0] * 5 + [0.0]
    args[pos] = -1.0
    with pytest.raises(ValueError, match="negative"):
        P_aux(*args)


def test_BUG_negative_always_on_pto_is_accepted_silently():
    """BUG (notebook): PTO_always_on < 0 is NOT checked (Bob's intended version checks it).  -100 W comes out as -100 W."""
    out = P_aux(1, 1, 1, 1, 1, -100.0)
    assert float(out[5]) == -100.0
    with pytest.raises(ValueError):
        RC.P_aux_v_bob_intended(1, 1, 1, 1, 1, -100.0)                                      # intended version raises


@pytest.mark.parametrize("name", ["ES_alteff", "PS_alteff", "HVAC_eff", "SP_alteff", "cond_eff"])
@pytest.mark.parametrize("val", [0.0, -1.0])
def test_bad_efficiency_raises(name, val):
    with pytest.raises(ValueError, match="efficiency"):
        P_aux(1, 1, 1, 1, 1, 0, **{name: val})


def test_BUG_PTO_eff_zero_gives_inf_with_warning_not_an_error():
    """BUG (notebook): PTO_eff is not checked.  0 -> inf (RuntimeWarning only); -1 -> negative power, silently."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = P_aux(1, 1, 1, 1, 1, 100.0, PTO_eff=0)
    assert np.isinf(out[5]) and any("divide by zero" in str(x.message) for x in w)
    assert float(P_aux(1, 1, 1, 1, 1, 100.0, PTO_eff=-1)[5]) == -100.0
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        assert np.isnan(P_aux(1, 1, 1, 1, 1, 0.0, PTO_eff=0)[5])                            # 0/0
    with pytest.raises(ValueError):
        RC.P_aux_v_bob_intended(1, 1, 1, 1, 1, 100.0, PTO_eff=0)


def test_BUG_nan_and_inf_pass_straight_through():
    """BUG (notebook): `np.any(p < 0)` is False for NaN, so NaN/inf are accepted; the output is NaN/inf."""
    assert np.isnan(P_aux(np.nan, 1, 1, 1, 1, 0)[0])
    assert np.isnan(P_aux(1, 1, 1, 1, 1, np.nan)[5])
    assert np.isinf(P_aux(np.inf, 1, 1, 1, 1, 0)[0])
    assert np.isnan(P_aux(1, 1, 1, 1, 1, 0, ES_alteff=float("nan"))[0])                    # NaN efficiency: `nan <= 0` is False
    with pytest.raises(ValueError):
        RC.P_aux_v_checks(np.nan, 1, 1, 1, 1, 0)
    with pytest.raises(ValueError):
        RC.P_aux_v_checks(1, 1, 1, 1, 1, 0, ES_alteff=float("nan"))


def test_mixed_shapes_scalar_and_array_broadcast():
    out = P_aux([1, 2, 3], 5, [1, 2, 3], 1, 1, 0)
    assert out[0].shape == (3,) and np.ndim(out[1]) == 0


def test_BUG_mismatched_array_lengths_are_not_rejected():
    """BUG (notebook): arrays of different length are returned as they are; the failure comes later (or never)."""
    out = P_aux([1, 2, 3], 5, [1, 2], 1, 1, 0)
    assert out[0].shape == (3,) and out[2].shape == (2,)
    with pytest.raises(ValueError):
        RC.P_aux_v_checks([1, 2, 3], 5, [1, 2], 1, 1, 0)


def test_PTO_eff_above_one_is_accepted():
    """PTO_eff 1.5 means electric < shaft power (impossible for a loss-making chain).  Notebook accepts it."""
    assert float(P_aux(0, 0, 0, 0, 0, 150.0, PTO_eff=1.5)[5]) == pytest.approx(100.0)
    with pytest.raises(ValueError):
        RC.P_aux_v_checks(0, 0, 0, 0, 0, 150.0, PTO_eff=1.5)


def test_array_efficiency_not_supported():
    """An hourly array of efficiencies (e.g. a COP) raises an unclear numpy error (`e <= 0` on an array)."""
    with pytest.raises(ValueError):
        P_aux(1, 1, 1, 1, 1, 0, ES_alteff=np.array([0.7, 0.8]))


def test_stale_comment_undo_the_multiply():
    """The comment on the PTO line says 'undo the multiply above, then divide'.  There is no multiply for PTO_always_on above:
    the line is a plain division.  Comment is stale (cosmetic)."""
    from _load_notebook import cell_source
    src = cell_source(9)
    assert "undo the multiply" in src
    assert "PTO_always_on = PTO_always_on / PTO_eff" in src
    assert "PTO_always_on * " not in src.split("PTO_always_on = np.asarray")[1].split("PTO_always_on = PTO_always_on / PTO_eff")[0]


def test_checks_variant_equals_notebook_on_valid_input():
    a = P_aux(1428.5714, 200, 200, 32.87, 600, 300.0, PTO_eff=0.9)
    b = RC.P_aux_v_checks(1428.5714, 200, 200, 32.87, 600, 300.0, PTO_eff=0.9)
    c = RC.P_aux_v_bob_intended(1428.5714, 200, 200, 32.87, 600, 300.0, PTO_eff=0.9)
    assert all(np.allclose(x, y) and np.allclose(x, z) for x, y, z in zip(a, b, c))
