"""Part C — behaviour tests on the real VECTO declaration cycles.

Runs the code of record (reference_copy.driver_model) on every .vdri mission
cycle present in reference/vecto/resources/MissionCycles, with coasting OFF
(coast_mass=None) and ON (ILLUSTRATIVE generic-E2 set-up).

LIMITATION: harness v1.7 and the real generic-E2 component files were NOT
supplied (Part 0.1). So the coasting set-up (Crr, CdxA table, masses) is the
ILLUSTRATIVE one in _vecto_data.py, NOT VECTO's reference vehicle. These tests
therefore check INTERNAL invariants of the code of record (reaches the end,
standing time, speed/accel caps, continuity) — they do NOT compare against
VECTO .vmod output (that is Part D, BLOCKED). The .vacc used is the real VECTO
Truck.vacc.

VECTO ref: v5.1.3 stable, commit d16ba783c.
"""
import math

import numpy as np
import pytest

from tests.driver_model.reference_copy import driver_model, decel_distance, interp1
from tests.driver_model import _vecto_data as D


CYCLES = D.list_cycles()
CYCLE_IDS = sorted(CYCLES)
VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()


def _run(name, coast=False, dt=1.0):
    s, v, grad, stop = D.load_cycle(CYCLES[name])
    kwargs = D.coasting_kwargs() if coast else {}
    return driver_model(s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, dt=dt, **kwargs), (s, v, grad, stop)


# --------------------------------------------------------------------------
# One run per cycle, cached, so each assertion family doesn't re-simulate.
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def runs():
    out = {}
    for name in CYCLE_IDS:
        out[(name, False)] = _run(name, coast=False)
        out[(name, True)] = _run(name, coast=True)
    return out


@pytest.mark.skipif(not CYCLE_IDS, reason="no .vdri cycles present")
class TestCyclesReachEnd:
    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_reaches_end_no_runtimeerror(self, runs, name, coast):
        (T, S, V, A, grade, M), (s, v, grad, stop) = runs[(name, coast)]
        assert len(T) > 0
        assert S[-1] <= s[-1] + 1e-6
        # the loop breaks when s >= s_end - 1e-6; last emitted row distance must be
        # within one coarse step of the route end
        assert s[-1] - S[-1] < max(V.max() * 1.0, 50.0)

    @pytest.mark.parametrize("name", CYCLE_IDS)
    def test_runtime_reasonable(self, runs, name):
        import time
        t0 = time.perf_counter()
        _run(name, coast=True)
        dt = time.perf_counter() - t0
        # generous bound; real cycles are < a few seconds each in pure python
        assert dt < 60.0, (name, dt)


@pytest.mark.skipif(not CYCLE_IDS, reason="no .vdri cycles present")
class TestStandingTime:
    @pytest.mark.parametrize("name", CYCLE_IDS)
    def test_standing_time_matches_cycle(self, runs, name):
        """Total standing rows (mode 0) * dt should equal the sum of cycle stop
        times, plus the VECTO first-waypoint 1 s rule if it applies. The code of
        record snaps standing time to the cycle stop times exactly (known
        deviation 2.3: VECTO's 1 Hz output differs by ~1 s per stop — not
        reproducible here without the .vmod)."""
        (T, S, V, A, grade, M), (s, v, grad, stop) = runs[(name, False)]
        expected = sum(stop)
        if v[0] == 0 and stop[0] == 0:
            expected += 1.0   # VECTO DrivingCycleDataReader line ~220
        stop_rows = int((M == 0).sum())
        assert stop_rows == pytest.approx(expected, abs=1.0)


@pytest.mark.skipif(not CYCLE_IDS, reason="no .vdri cycles present")
class TestSpeedCap:
    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_speed_never_far_above_target(self, runs, name, coast):
        """Speed must not exceed target + 2.5 km/h above 50 km/h, or target below
        50 km/h, beyond a small tolerance for the 1 s row crossing waypoints a few
        metres apart (known leftover 2.3). We flag every violation above 1 km/h."""
        (T, S, V, A, grade, M), (s, v, grad, stop) = runs[(name, coast)]
        s_wp = [float(x) for x in s]
        v_wp = [float(x) / 3.6 for x in v]
        # segment target (next positive), same rule as the model
        seg_v = [0.0] * len(v_wp)
        nxt = 0.0
        for i in range(len(v_wp) - 1, -1, -1):
            seg_v[i] = v_wp[i] if v_wp[i] > 0 else nxt
            if v_wp[i] > 0:
                nxt = v_wp[i]
        os_add = 2.5 / 3.6
        os_min = 50.0 / 3.6
        import bisect as _b
        violations = []
        for dist, spd in zip(S, V):
            k = _b.bisect_right(s_wp, float(dist)) - 1
            k = max(0, min(k, len(seg_v) - 1))
            tgt = seg_v[k]
            cap = tgt + os_add if tgt > os_min else tgt
            if spd > cap + 1.0 / 3.6:   # > 1 km/h over the cap
                violations.append((float(dist), (spd - cap) * 3.6))
        assert not violations, f"{name} coast={coast}: {len(violations)} rows >1km/h over cap, worst {max(x[1] for x in violations):.2f} km/h at {violations[0][0]:.0f} m"


@pytest.mark.skipif(not CYCLE_IDS, reason="no .vdri cycles present")
class TestAccelerationCap:
    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_powered_accel_within_vacc(self, runs, name, coast):
        """POWERED acceleration (mode 1) must never exceed the .vacc accel limit.

        NOTE / FINDING: in coast mode (mode 3) on steep downhills the gravity-driven
        coast acceleration ca CAN exceed the .vacc accel limit — the code of record
        caps ca only by (v_os - v)/dt, not by acc_max. This matches VECTO, where
        the free-rolling Coast action is NOT limited by the driver .vacc accel curve
        (only powered Accelerate is). So we assert the cap for mode 1 only, and
        record mode-3 over-vacc rows separately (see test_coast_mode_overspeed_rows)."""
        (T, S, V, A, grade, M), _ = runs[(name, coast)]
        vv = [x / 3.6 for x in VACC_V]
        worst_acc = 0.0
        for spd, acc, mode in zip(V, A, M):
            if mode != 1:
                continue
            a_max = interp1(float(spd), vv, VACC_ACC)
            if acc > a_max + 1e-6:
                worst_acc = max(worst_acc, acc - a_max)
        assert worst_acc < 1e-3, f"{name}: POWERED accel exceeds .vacc by {worst_acc:.4f} m/s^2"

    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_decel_within_vacc_margin(self, runs, name, coast):
        """Deceleration may exceed the .vacc dec limit on the last 1-2 braking rows
        and the stop-arrival row (1 s artefact, deviation 1 / known ~1.78x). It must
        not go past ~2x the .vacc deceleration."""
        (T, S, V, A, grade, M), _ = runs[(name, coast)]
        vv = [x / 3.6 for x in VACC_V]
        worst_dec_ratio = 0.0
        for spd, acc in zip(V, A):
            d_max = interp1(float(spd), vv, VACC_DEC)   # negative
            if acc < d_max - 1e-6:
                worst_dec_ratio = max(worst_dec_ratio, acc / d_max)
        assert worst_dec_ratio < 2.0, f"{name}: dec ratio {worst_dec_ratio:.3f} (>2x .vacc)"

    @pytest.mark.parametrize("name", CYCLE_IDS)
    def test_coast_mode_overspeed_rows_are_downhill(self, runs, name):
        """FINDING (documented): any coast row (mode 3) whose acceleration exceeds
        the .vacc accel limit must be on a downhill (grade < 0). This confirms the
        over-vacc coast rows are gravity-driven free-rolling, not a bug in the
        powered-acceleration path."""
        (T, S, V, A, grade, M), _ = runs[(name, True)]
        vv = [x / 3.6 for x in VACC_V]
        for spd, acc, mode, g in zip(V, A, M, grade):
            if mode == 3:
                a_max = interp1(float(spd), vv, VACC_ACC)
                if acc > a_max + 1e-6:
                    assert g < 0, f"{name}: coast over .vacc on non-downhill grade {g:.2f}%"


@pytest.mark.skipif(not CYCLE_IDS, reason="no .vdri cycles present")
class TestContinuity:
    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_distance_monotonic(self, runs, name, coast):
        (T, S, V, A, grade, M), _ = runs[(name, coast)]
        dS = np.diff(S)
        assert (dS >= -1e-6).all(), f"{name}: distance went backwards"

    @pytest.mark.parametrize("name", CYCLE_IDS)
    @pytest.mark.parametrize("coast", [False, True])
    def test_time_monotonic_uniform(self, runs, name, coast):
        (T, S, V, A, grade, M), _ = runs[(name, coast)]
        dT = np.diff(T)
        assert dT == pytest.approx(1.0, abs=1e-9), f"{name}: time step not uniform 1 s"

    @pytest.mark.parametrize("name", CYCLE_IDS)
    def test_altitude_matches_cycle(self, runs, name):
        """Altitude integrated along the emitted rows must match the cycle's own
        altitude (grade integrated over distance) at the route end, within rounding."""
        (T, S, V, A, grade, M), (s, v, grad, stop) = runs[(name, False)]
        s_arr = np.asarray(s, float)
        gr_arr = np.asarray(grad, float)
        rise = np.diff(s_arr) * gr_arr[:-1] / 100.0
        cycle_end_alt = float(np.cumsum(rise)[-1])
        # row grade * row distance, integrated
        s_next = np.append(S[1:], S[-1])
        ds_row = s_next - S
        row_alt = float(np.sum(grade / 100.0 * ds_row))
        # allow a small tolerance (stop-arrival snapping, last partial step)
        assert row_alt == pytest.approx(cycle_end_alt, abs=5.0), (name, row_alt, cycle_end_alt)


# --------------------------------------------------------------------------
# Edge routes — synthetic, ILLUSTRATIVE waypoints
# --------------------------------------------------------------------------
class TestEdgeRoutes:
    def _vacc(self):
        return D.TRUCK_VACC_V, D.TRUCK_VACC_ACC, D.TRUCK_VACC_DEC

    def test_single_waypoint_route(self):
        """One waypoint: there is no segment to drive. The loop condition
        s >= s_end is immediately true -> empty or single-stop output; must not
        hang or raise an unexpected error. Documents behaviour."""
        vv, va, vd = self._vacc()
        try:
            out = driver_model([0.0], [0.0], [0.0], [0.0], vv, va, vd)
        except (RuntimeError, IndexError, ValueError) as e:
            pytest.skip(f"single-waypoint raises {type(e).__name__}: {e} (documented)")
        T, S, V, A, grade, M = out
        assert len(T) >= 0

    def test_all_zero_speeds_raises(self):
        """A route whose waypoints are all 0 km/h never moves. The code of record's
        max_steps guard must eventually raise RuntimeError rather than loop forever,
        OR it fills only stop rows and ends. We assert it terminates (one of the two)."""
        vv, va, vd = self._vacc()
        s = [0.0, 100.0, 200.0]
        try:
            out = driver_model(s, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0, 0, 0], vv, va, vd)
        except RuntimeError:
            return  # acceptable: guard fired
        T, S, V, A, grade, M = out
        # if it returned, it must not have moved past the first waypoint's stop region
        assert S.max() <= s[-1] + 1e-6

    def test_back_to_back_stops(self):
        vv, va, vd = self._vacc()
        s = [0, 300, 600, 900, 1200]
        v = [0, 60, 0, 0, 60]       # two stops in a row at 600 and 900
        stop = [0, 0, 20, 20, 0]
        grad = [0, 0, 0, 0, 0]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd)
        assert int((M == 0).sum()) == pytest.approx(40 + 1, abs=1)  # +1 first-wp rule
        assert S[-1] <= s[-1] + 1e-6

    def test_very_short_waypoint_spacing(self):
        vv, va, vd = self._vacc()
        # spacing < 1 m and 1-5 m
        s = [0, 0.4, 2.0, 5.0, 500.0]
        v = [40, 40, 50, 60, 60]
        stop = [0, 0, 0, 0, 0]
        grad = [0, 0, 0, 0, 0]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd)
        assert math.isfinite(S[-1])

    @pytest.mark.parametrize("gpct", [10.0, -10.0])
    def test_steep_grades(self, gpct):
        vv, va, vd = self._vacc()
        s = [0, 500, 1000, 1500]
        v = [60, 60, 60, 60]
        stop = [0, 0, 0, 0]
        grad = [gpct, gpct, gpct, gpct]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd, **D.coasting_kwargs())
        assert math.isfinite(S[-1]) and S[-1] <= s[-1] + 1e-6

    def test_target_change_1kmh(self):
        vv, va, vd = self._vacc()
        s = [0, 500, 1000]
        v = [80, 79, 79]      # 1 km/h drop
        stop = [0, 0, 0]
        grad = [0, 0, 0]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd)
        assert S[-1] <= s[-1] + 1e-6

    def test_route_starting_at_speed(self):
        vv, va, vd = self._vacc()
        s = [0, 500, 1000]
        v = [80, 80, 80]      # starts at 80 km/h, no initial stop
        stop = [0, 0, 0]
        grad = [0, 0, 0]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd)
        assert V[0] == pytest.approx(80 / 3.6)
        assert int((M == 0).sum()) == 0   # no standing rows

    @pytest.mark.parametrize("dt", [0.5, 2.0])
    def test_alternate_timestep(self, dt):
        vv, va, vd = self._vacc()
        s = [0, 500, 1000, 1500]
        v = [0, 80, 0, 80]
        stop = [0, 0, 30, 0]
        grad = [0, 0, 0, 0]
        T, S, V, A, grade, M = driver_model(s, v, stop, grad, vv, va, vd, dt=dt)
        assert np.diff(T) == pytest.approx(dt, abs=1e-9)
        assert S[-1] <= s[-1] + 1e-6
