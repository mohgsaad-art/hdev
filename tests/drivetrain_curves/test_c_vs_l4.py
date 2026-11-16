"""Tests for the drivetrain C vs L4 job (docs/research/drivetrain-curve-library-2026-11).

All numbers in the synthetic record are ILLUSTRATIVE (test inputs only, not model inputs).
The test that checks Method A against the v2 harness result runs only when the record cache exists
(cache/records_ten_range_mid.npz, built by part1_airdrag.py); otherwise it is skipped.
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.abspath(os.path.join(HERE, "..", "..", "docs", "research", "drivetrain-curve-library-2026-11"))
sys.path.insert(0, JOB)

import methods_lib as ML          # noqa: E402
from cdxa_ranges import CDXA_RANGES  # noqa: E402

ML.set_l4_bounds(0.18482, 0.36145, 0.00626)     # values of part2_L4_bounds.csv


def _rec(seed=0, cert=1.2, measured=True, mission_uses_declared=True):
    """ILLUSTRATIVE synthetic record in the compact format of harness.compact."""
    rng = np.random.default_rng(seed)
    n = 3000
    v = np.clip(15 + 5 * np.sin(np.arange(n) / 50.0), 0, None)
    Pw = 60e3 * np.sin(np.arange(n) / 17.0) + 20e3
    lo, hi = CDXA_RANGES["A12"]
    mid = 0.5 * (lo + hi)
    return dict(P_wheel=Pw + rng.normal(0, 1e3, n), v_avg=v, aero_k=1.188 * v ** 3 * 1.05, engaged=np.ones(n, bool),
                E_aux_Ws=2e3 * n, km=float(v.sum() / 1000.0), rated_kw=300.0, cert=cert, mission="Regional Delivery",
                cdxa_range="A12", airdrag_measured=measured,
                cdxa_lo=lo if mission_uses_declared else mid, cdxa_hi=hi if mission_uses_declared else mid)


def test_l4_zero_coefficients_give_zero_loss():
    r = _rec()
    assert np.all(ML.l4_loss(r, 0.0, 0.0, 0.0) == 0.0)
    for m, th in ((ML.MethodL4a(), (0.0, 0.0)), (ML.MethodL4b(), (0.0, 0.0, 0.0))):
        expected = (r["P_wheel"].sum() + r["E_aux_Ws"]) / 3.6e6 / r["km"] / ML.CHARGING_ETA
        assert m.predict(r, th) == pytest.approx(expected, rel=1e-12)


def test_c_with_unit_efficiency_equals_wheel_energy_path_of_method_a():
    """C with eta_d = eta_r = 1, F0 = 0 must equal Method A's path (consumption_engine step 5 copy) with all
    efficiencies 1: battery energy = wheel energy + aux."""
    r = _rec()
    c = ML.MethodCv2().predict(r, (1.0, 1.0, 0.0))
    a_path = ML.kwh_per_km(r, ML.traction_power(r, 1.0, 1.0))
    assert c == pytest.approx(a_path, rel=1e-12)
    assert c == pytest.approx((r["P_wheel"].sum() + r["E_aux_Ws"]) / 3.6e6 / r["km"] / ML.CHARGING_ETA, rel=1e-12)


def _synthetic_truck():
    recs = [_rec(seed=s, cert=c) for s, c in zip(range(6), (1.10, 1.15, 1.22, 1.30, 1.05, 1.18))]
    recs.append(_rec(seed=9, cert=1.0, mission_uses_declared=False))   # e.g. Construction: default CdxA
    return recs


@pytest.mark.parametrize("base", [ML.MethodCv2, ML.MethodL4a, ML.MethodL4b])
def test_fits_are_deterministic(base):
    recs = _synthetic_truck()
    m = ML.WithCdxARange(base())
    t1, r1 = ML.fit_v2(m, recs)
    t2, r2 = ML.fit_v2(m, recs)
    assert t1 == t2 and r1 == r2
    l1 = ML.loo_v2(m, recs)
    l2 = ML.loo_v2(m, recs)
    assert [x["pred"] for x in l1] == [x["pred"] for x in l2]


@pytest.mark.parametrize("base", [ML.MethodCv2, ML.MethodL4a, ML.MethodL4b])
def test_cdxa_stays_inside_its_range(base):
    recs = _synthetic_truck()
    for cert_scale in (0.6, 1.0, 1.6):                        # push the fit both ways
        rr = [dict(r, cert=r["cert"] * cert_scale) for r in recs]
        th, _ = ML.fit_v2(ML.WithCdxARange(base()), rr)
        lo, hi = CDXA_RANGES["A12"]
        assert lo <= th[-1] < hi


def test_cdxa_not_moved_on_missions_using_default():
    r = _rec(mission_uses_declared=False)
    m = ML.WithCdxARange(ML.MethodCv2())
    assert m.predict(r, (0.9, 0.8, 0.0, 4.88)) == m.predict(r, (0.9, 0.8, 0.0, 5.11))


CACHE = os.path.join(JOB, "cache", "records_ten_range_mid.npz")


@pytest.mark.skipif(not os.path.isfile(CACHE), reason="record cache not built (run part1_airdrag.py)")
def test_method_a_equals_v2_harness_consumption_engine():
    sys.path.insert(0, JOB)
    import harness as HN
    recs, _ = HN._load_npz(CACHE)
    for r in recs:
        assert ML.MethodA().predict(r) == pytest.approx(r["E_A"] / ML.CHARGING_ETA, rel=1e-12)
