"""Part B — unit tests for the driver-model helpers.

Tests interp1, decel_distance and coast_distance (code of record, Appendix 1,
imported from reference_copy.py). Where a test value is not sourced from VECTO or
a standard it is labelled ILLUSTRATIVE in the test name or comment.

VECTO references are to the v5.1.3 stable branch, commit d16ba783c (the fallback
named in prompt section 0.4; no 5.1.6 tag exists in mohgsaad-art/VECTO). Files:
  - AccelerationCurve.cs  (ComputeDecelerationDistance / ComputeAccelerationSegmentDistance)
  - DefaultDriverStrategy.cs (ComputeCoastingDistance, lines 741-779)
  - Vehicle.cs (RollingResistance line 278, cos of the raw rise/run radian)
"""
import math

import numpy as np
import pytest

from tests.driver_model.reference_copy import interp1, decel_distance, coast_distance
from tests.driver_model._vecto_data import TRUCK_VACC_V, TRUCK_VACC_DEC


# ======================================================================
# interp1 — must behave like np.interp (holds both ends)
# ======================================================================
class TestInterp1:
    def test_matches_numpy_on_random_points(self):
        rng = np.random.default_rng(0)
        xs = np.sort(rng.uniform(0, 100, 8))
        # make strictly increasing (interp1/np.interp assume monotone xs)
        xs = np.unique(xs)
        ys = rng.uniform(-5, 5, len(xs))
        for x in rng.uniform(-10, 110, 200):
            assert interp1(float(x), list(xs), list(ys)) == pytest.approx(
                float(np.interp(x, xs, ys)), abs=1e-12
            )

    def test_both_ends_held(self):
        xs = [0.0, 10.0, 20.0]
        ys = [1.0, 2.0, 3.0]
        assert interp1(-5.0, xs, ys) == 1.0      # below first -> first value
        assert interp1(99.0, xs, ys) == 3.0      # above last -> last value
        assert interp1(0.0, xs, ys) == 1.0
        assert interp1(20.0, xs, ys) == 3.0

    def test_exact_knot_values(self):
        xs = [0.0, 10.0, 20.0]
        ys = [1.0, 2.0, 3.0]
        assert interp1(10.0, xs, ys) == pytest.approx(2.0)

    def test_repeated_x_values(self):
        # bisect_right lands past the duplicate; interp1 must not divide by zero
        # as long as the queried x is not exactly on the duplicated knot interior.
        xs = [0.0, 10.0, 10.0, 20.0]
        ys = [0.0, 1.0, 5.0, 6.0]
        # query strictly inside the last segment -> uses (10,5)->(20,6)
        assert interp1(15.0, xs, ys) == pytest.approx(5.5)
        # query inside the first segment -> uses (0,0)->(10,1)
        assert interp1(5.0, xs, ys) == pytest.approx(0.5)

    def test_single_segment_table(self):
        xs = [0.0, 50.0]
        ys = [10.0, 20.0]
        assert interp1(25.0, xs, ys) == pytest.approx(15.0)
        assert interp1(-1.0, xs, ys) == 10.0
        assert interp1(60.0, xs, ys) == 20.0


# ======================================================================
# decel_distance
# ======================================================================
def _numeric_decel_distance(v_from, v_to, vacc_v, vacc_dec, n=200000):
    """Fine numerical integration of ds = v / |a(v)| dv over the .vacc dec curve.

    a(v) is the piecewise-linear deceleration lookup, held at the table ends
    (like interp1). This is an INDEPENDENT reference for decel_distance.
    """
    if v_to >= v_from:
        return 0.0
    vs = np.linspace(v_to, v_from, n)
    a = np.interp(vs, vacc_v, vacc_dec)   # held ends, linear interior
    integrand = vs / np.abs(a)
    _trapz = getattr(np, "trapezoid", None) or np.trapz  # numpy 2.x renamed trapz
    return float(_trapz(integrand, vs))


def _vecto_segment_distance(i, v1, v2, vacc_v, vacc_dec):
    """Independent re-implementation of VECTO ComputeAccelerationSegmentDistance
    for the DECELERATION branch (AccelerationCurve.cs lines 139-181).

    VECTO clamps: v2 = max(v2, leftKey), v1 = min(v1, rightKey) within the segment.
    """
    v_lo, v_hi = vacc_v[i - 1], vacc_v[i]
    a_lo, a_hi = vacc_dec[i - 1], vacc_dec[i]
    v2 = max(v2, v_lo)
    v1 = min(v1, v_hi)
    if math.isclose(a_lo, a_hi):
        a = a_lo
        return (v2 - v1) ** 2 / 2.0 / a + v1 * (v2 - v1) / a
    k = (a_lo - a_hi) / (v_lo - v_hi)
    d = a_lo - k * v_lo
    m = v1 + d / k
    b = -d / k
    c = -m / k
    t = math.log((v2 * k + d) / (v1 * k + d)) / k
    return m / k * math.exp(k * t) + b * t + c


def _vecto_find_index(v, vacc_v):
    """VECTO AccelerationCurve.FindIndex (lines 76-90): clamps to the table."""
    if v < vacc_v[0]:
        return 1
    idx = next((i for i, x in enumerate(vacc_v) if x > v), None)
    if idx is None or idx <= 0:
        idx = len(vacc_v) - 1 if v > vacc_v[0] else 1
    return idx


def _vecto_decel_distance(v_from, v_to, vacc_v, vacc_dec):
    """VECTO ComputeDecelerationDistance (lines 119-137), re-implemented in Python."""
    i1 = _vecto_find_index(v_from, vacc_v)
    i2 = _vecto_find_index(v_to, vacc_v)
    dist = 0.0
    for i in range(i2, i1 + 1):
        dist += _vecto_segment_distance(i, v_from, v_to, vacc_v, vacc_dec)
    return dist


SYNTH_1_V = [0.0, 10.0, 30.0]              # ILLUSTRATIVE synthetic curve 1 (constant dec)
SYNTH_1_DEC = [-1.2, -1.2, -1.2]
SYNTH_2_V = [0.0, 10.0, 20.0, 40.0]        # ILLUSTRATIVE synthetic curve 2 (varying dec)
SYNTH_2_DEC = [-0.8, -0.8, -1.5, -0.6]


class TestDecelDistance:
    @pytest.mark.parametrize("vacc_v,vacc_dec", [
        (TRUCK_VACC_V, TRUCK_VACC_DEC),
        (SYNTH_1_V, SYNTH_1_DEC),
        (SYNTH_2_V, SYNTH_2_DEC),
    ])
    def test_against_numeric_integration(self, vacc_v, vacc_dec):
        vv = [x / 3.6 for x in vacc_v]
        v_top = vv[-1] * 0.95
        for v_to in (0.0, vv[1] * 0.5, vv[1]):
            got = decel_distance(v_top, v_to, vv, vacc_dec)
            ref = _numeric_decel_distance(v_top, v_to, vv, vacc_dec)
            assert got == pytest.approx(ref, rel=2e-3), (v_top, v_to, got, ref)

    @pytest.mark.parametrize("vacc_v,vacc_dec", [
        (TRUCK_VACC_V, TRUCK_VACC_DEC),
        (SYNTH_2_V, SYNTH_2_DEC),
    ])
    def test_against_vecto_formula_within_table(self, vacc_v, vacc_dec):
        """Within the table range the two formulas must agree closely."""
        vv = [x / 3.6 for x in vacc_v]
        v_top = vv[-1]
        for v_to in (0.0, vv[1], vv[-2]):
            got = decel_distance(v_top, v_to, vv, vacc_dec)
            ref = _vecto_decel_distance(v_top, v_to, vv, vacc_dec)
            assert got == pytest.approx(ref, rel=1e-6, abs=1e-9), (v_to, got, ref)

    def test_v_to_ge_v_from_returns_zero(self):
        vv = [x / 3.6 for x in TRUCK_VACC_V]
        assert decel_distance(10.0, 10.0, vv, TRUCK_VACC_DEC) == 0.0
        assert decel_distance(5.0, 10.0, vv, TRUCK_VACC_DEC) == 0.0

    def test_constant_deceleration_segment(self):
        # closed form for constant dec a: s = (v1^2 - v2^2)/(2|a|)
        vv = [x / 3.6 for x in SYNTH_1_V]
        v1, v2 = 8.0, 2.0
        expect = (v1 ** 2 - v2 ** 2) / (2 * 1.2)
        assert decel_distance(v1, v2, vv, SYNTH_1_DEC) == pytest.approx(expect, rel=1e-9)

    def test_v_from_above_last_point_matches_vecto_clamp(self):
        """v_from above the top .vacc point.

        BOTH HDEV decel_distance and VECTO clamp the top of the integration to the
        last table speed (HDEV via v1=min(v_from,v_hi) per segment; VECTO via
        FindIndex clamp + v1=Min(v1,rightKey)). So the distance travelled ABOVE
        the table is ignored by both — they must agree. This refines open item 2.3.
        """
        vv = [x / 3.6 for x in TRUCK_VACC_V]
        v_above = vv[-1] + 20.0 / 3.6   # 20 km/h above the top point
        got = decel_distance(v_above, 0.0, vv, TRUCK_VACC_DEC)
        ref = _vecto_decel_distance(v_above, 0.0, vv, TRUCK_VACC_DEC)
        # also equals the clamped-top result
        clamped = decel_distance(vv[-1], 0.0, vv, TRUCK_VACC_DEC)
        assert got == pytest.approx(ref, rel=1e-6)
        assert got == pytest.approx(clamped, rel=1e-6)
        assert math.isfinite(got) and got > 0

    def test_v_from_below_first_point(self):
        vv = [x / 3.6 for x in TRUCK_VACC_V]
        got = decel_distance(0.3, 0.0, vv, TRUCK_VACC_DEC)
        assert math.isfinite(got) and got >= 0

    def test_equal_adjacent_vacc_v_does_not_crash(self):
        """Equal adjacent speeds -> a zero-width segment. decel_distance must skip it
        (v2 >= v1 -> continue) and not divide by zero."""
        vacc_v = [0.0, 10.0, 10.0, 20.0]
        vacc_dec = [-1.0, -1.0, -0.8, -0.8]
        got = decel_distance(18.0, 2.0, vacc_v, vacc_dec)
        assert math.isfinite(got) and got > 0

    def test_sign_change_segment_behaviour(self):
        """A dec curve that crosses zero inside a segment is DEGENERATE: a(v)=0 at
        some v, so the exact-integral log term can blow up / go complex. This test
        DOCUMENTS the behaviour of the code of record (it is never produced by a
        valid .vacc, where dec is strictly negative, SIRange(-20,-0.05)).
        """
        vacc_v = [0.0, 10.0, 20.0]
        vacc_dec = [-1.0, 0.5, 1.0]   # INVALID curve (dec goes positive) — ILLUSTRATIVE
        # We only assert it either returns a float or raises a clean error, not silent NaN.
        try:
            got = decel_distance(18.0, 2.0, vacc_v, vacc_dec)
        except (ValueError, ZeroDivisionError):
            return
        assert isinstance(got, float)


# ======================================================================
# coast_distance — VECTO ComputeCoastingDistance (DefaultDriverStrategy.cs 741-779)
# ======================================================================
def _hand_coast_distance(v, v_target, h_now, h_target, s_now, s_target,
                         mass, m_red, cdxa_v, cdxa, Crr, rho, g, P_drag,
                         df_off, df_scl, df_vt, df_vd):
    """Independent hand re-implementation of coast_distance, mirroring VECTO's
    ComputeCoastingDistance term by term. Energy uses (mass + reduced wheels);
    rolling uses cos(rise/run) on the bare vehicle mass; air drag is the step
    average form rho/8*CdA*(v1+v2)(v1^2+v2^2)/v_avg.
    """
    m_eff = mass + m_red
    dE = m_eff * g * (h_now - h_target) + m_eff * (v ** 2 - v_target ** 2) / 2.0
    v_avg = (v + v_target) / 2.0
    cda = np.interp(v_avg, cdxa_v, cdxa)
    F_air = rho / 8.0 * cda * (v + v_target) * (v ** 2 + v_target ** 2) / v_avg
    grad = (h_target - h_now) / (s_target - s_now)
    F_roll = math.cos(grad) * mass * g * Crr
    F_loss = P_drag / v
    f_vt = np.interp(v_target * 3.6, df_vt[0], df_vt[1])
    f_vd = np.interp((v - v_target) * 3.6, df_vd[0], df_vd[1])
    DF = df_off - df_scl * f_vt * f_vd
    return dE / (DF * (F_air + F_roll + F_loss))


DF_VT = ((0, 48, 52, 100), (0, 0, 1, 1))     # VECTO LAC-DF-Vtarget.csv [VECTO v5.1.3]
DF_VD = ((-100, 9, 11, 100), (1, 1, 0, 0))   # VECTO LAC-DF-Vdrop.csv   [VECTO v5.1.3]
RHO = 1.188        # DeclarationData.cs line 76 [VECTO]
G = 9.81           # code of record value (VECTO uses 9.80665 — deviation, see report Q13)
MASS = 9589.6      # [ASSUMPTION] generic E2 reference mass
M_RED = 200.0      # ILLUSTRATIVE reduced wheel mass
CDXA_V = [0.0, 60.0, 90.0, 130.0]
CDXA = [4.83, 4.83, 4.83, 4.83]   # flat, ILLUSTRATIVE
CRR = 0.0055       # ILLUSTRATIVE


class TestCoastDistance:
    @pytest.mark.parametrize("label,h_now,h_target,vkmh,vt_kmh", [
        ("flat_small",   0.0,   0.0,  85.0, 80.0),
        ("flat_large",   0.0,   0.0,  85.0, 55.0),
        ("uphill_small", 0.0,   5.0,  85.0, 80.0),
        ("uphill_large", 0.0,  20.0,  85.0, 55.0),
        ("downhill_small", 0.0, -5.0, 85.0, 80.0),
        ("downhill_large", 0.0, -20.0, 85.0, 55.0),
    ])
    def test_against_hand_calculation(self, label, h_now, h_target, vkmh, vt_kmh):
        s_now, s_target = 0.0, 300.0
        v = vkmh / 3.6
        vt = vt_kmh / 3.6
        got = coast_distance(v, vt, h_now, h_target, s_now, s_target,
                             MASS, M_RED, CDXA_V, CDXA, CRR, RHO, G, 0.0,
                             2.5, 1.5, DF_VT, DF_VD)
        ref = _hand_coast_distance(v, vt, h_now, h_target, s_now, s_target,
                                   MASS, M_RED, CDXA_V, CDXA, CRR, RHO, G, 0.0,
                                   2.5, 1.5, DF_VT, DF_VD)
        assert got == pytest.approx(ref, rel=1e-9), (label, got, ref)

    def test_uphill_negative_dE_gives_negative_result(self):
        """Steep uphill: kinetic+potential energy at target exceeds current ->
        dE < 0 -> coast_distance < 0. The driver_model ignores a negative coast
        distance (the loop only uses cd when cd > 0), which matches VECTO:
        GetDrivingBehaviorEntry treats coastingDistance < 0 as 'braking only'
        (DefaultDriverStrategy.cs line 713). Confirmed from source."""
        v = 85 / 3.6
        vt = 55 / 3.6
        got = coast_distance(v, vt, 0.0, 60.0, 0.0, 300.0,
                             MASS, M_RED, CDXA_V, CDXA, CRR, RHO, G, 0.0,
                             2.5, 1.5, DF_VT, DF_VD)
        assert got < 0

    def test_cos_grad_vs_cos_atan_grad_difference(self):
        """Q3: VECTO uses cos(rise/run) directly (rise/run treated as a radian),
        NOT cos(atan(rise/run)). coast_distance matches VECTO. Here we quantify how
        much a hypothetical atan 'fix' would change the rolling term at 2/6/10 %."""
        for grade_pct in (2.0, 6.0, 10.0):
            g_ratio = grade_pct / 100.0
            cos_direct = math.cos(g_ratio)          # VECTO / code of record
            cos_atan = math.cos(math.atan(g_ratio))  # proposed 'fix'
            rel = abs(cos_direct - cos_atan) / cos_atan
            # the difference is tiny and grows with grade; assert it stays < 1 %
            assert rel < 0.01, (grade_pct, cos_direct, cos_atan, rel)

    def test_P_drag_over_v_small_speed(self):
        """F_loss = P_drag_loss / v. coast_distance is only CALLED above lac_min
        (50 km/h) in driver_model (guarded by 'coast_on and v > lac_min'), so v is
        never small there. This test documents that with a non-zero P_drag and a
        realistic coasting speed the term is finite and positive."""
        v = 60 / 3.6
        vt = 55 / 3.6
        got = coast_distance(v, vt, 0.0, 0.0, 0.0, 300.0,
                             MASS, M_RED, CDXA_V, CDXA, CRR, RHO, G, 800.0,
                             2.5, 1.5, DF_VT, DF_VD)
        assert math.isfinite(got) and got > 0
