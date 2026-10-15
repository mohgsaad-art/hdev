# STATUS: NEW (Step 9 item 4-8). numpy-based unit tests for the core physics row pipeline:
#   driver_model (audit regression), weather_for_rows, power_step, p_aux, consumption.
# conftest.py puts repo root on sys.path so imports resolve as src.engine.* / src.resolver.*.
# Every expected number is either a captured VECTO reference (p_aux 2938.9/2537/1937 W; force simple-K)
# or a hand-checked case with the arithmetic written out in the test.

import math

import numpy as np
import pytest

from src.engine.driver_model import DriverModel
from src.engine.weather_for_rows import weather_for_rows, CDXA_SPEED_MIN_KMH, CDXA_SPEED_MAX_KMH
from src.engine.power_step import power_step
from src.engine.p_aux import p_aux
from src.engine.consumption import consumption, PLACEHOLDER_MESSAGE
from src.resolver.waypoint_parser import Waypoint, VaccPoint


# ---------------------------------------------------------------------------
# ITEM 4 - driver_model audit regression
# ---------------------------------------------------------------------------

def _vacc():
  # a tiny accel/decel curve: 1 m/s^2 accel, -1 m/s^2 decel across the speed range.
  return [VaccPoint(0.0, 1.0, -1.0), VaccPoint(25.0, 1.0, -1.0),
          VaccPoint(60.0, 1.0, -1.0), VaccPoint(120.0, 1.0, -1.0)]


def test_driver_model_runs_tiny_cycle_and_emits_payload():
  # 3 waypoints: depot stop 3 s, drive to 100 m at 36 km/h, then a 2 s stop at the end.
  wps = [
    Waypoint(distance=0.0, speed=0.0, grade_pct=1.0, stop=3.0),
    Waypoint(distance=100.0, speed=36.0, grade_pct=1.0, stop=0.0),
    Waypoint(distance=140.0, speed=36.0, grade_pct=2.0, stop=2.0),
  ]
  rows = DriverModel(wps).driver_model(_vacc(), dt_s=1.0)

  # the first-waypoint stop emits exactly 3 standstill rows (t_elapsed 0,1,2 < 3).
  first_stop_rows = [r for r in rows if r["time"] < 3.0]
  assert len(first_stop_rows) == 3
  assert all(r["speed"] == 0.0 and r["accel"] == 0.0 for r in first_stop_rows)

  # the final 2 s stop emits 2 standstill rows at distance 140.
  end_stop_rows = [r for r in rows if r["distance"] == 140.0 and r["speed"] == 0.0]
  assert len(end_stop_rows) == 2

  # F5 audit fix: every row now carries a 'payload' column (default 0.0 when unset).
  assert all("payload" in r for r in rows)
  assert all(r["payload"] == 0.0 for r in rows)

  # grade handling (M0.12) unchanged: rows copy the FLAT waypoint grade_pct, no interpolation.
  assert first_stop_rows[0]["grade"] == 1.0
  assert end_stop_rows[0]["grade"] == 2.0

  # the truck actually reaches the final waypoint (no infinite loop; F3/F4 guards hold).
  assert rows[-1]["distance"] == 140.0


def test_driver_model_payload_copied_like_grade():
  # attach payload to the waypoints (fill_payload would do this); driver copies it onto every row.
  wps = [
    Waypoint(distance=0.0, speed=0.0, grade_pct=0.0, stop=2.0),
    Waypoint(distance=80.0, speed=36.0, grade_pct=0.0, stop=2.0),
  ]
  wps[0].payload = 1000.0
  wps[1].payload = 2000.0
  rows = DriverModel(wps).driver_model(_vacc(), dt_s=1.0)
  # first-waypoint stop rows carry waypoint[0].payload
  assert rows[0]["payload"] == 1000.0
  # the end stop rows carry target.payload
  end_stop = [r for r in rows if r["distance"] == 80.0 and r["speed"] == 0.0]
  assert end_stop and all(r["payload"] == 2000.0 for r in end_stop)


def test_driver_model_momentary_stop_does_not_hang():
  # F3/F4 regression: a waypoint with speed 0 and no dwell (momentary stop) must TERMINATE
  # (no infinite loop). It reaches the momentary stop at 100 m and pulls away again. Full
  # completion of the final stretch is NOT asserted: that is known bug #2 (momentary stop,
  # left unfixed per the audit) - here we only prove the loop ends and makes forward progress.
  wps = [
    Waypoint(distance=0.0, speed=36.0, grade_pct=0.0, stop=0.0),
    Waypoint(distance=100.0, speed=0.0, grade_pct=0.0, stop=0.0),
    Waypoint(distance=200.0, speed=36.0, grade_pct=0.0, stop=0.0),
  ]
  rows = DriverModel(wps).driver_model(_vacc(), dt_s=1.0)
  # the truck passed through the momentary stop at 100 m (speed hit 0 there) ...
  assert any(r["distance"] >= 100.0 and r["speed"] == 0.0 for r in rows)
  # ... and then pulled away past it (forward progress; no hang).
  assert rows[-1]["distance"] > 100.0


# ---------------------------------------------------------------------------
# ITEM 5 - weather_for_rows
# ---------------------------------------------------------------------------

def _flat_cdxa_table(cdxa0=5.0):
  # a crosswind table where W1 = 1 and W2 = 0 at every speed -> CdxA_eff == CdxA(0) (no wind effect).
  speeds = np.array([60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0, 105.0])
  w1 = np.ones_like(speeds)
  w2 = np.zeros_like(speeds)
  return {"cdxa0": cdxa0, "speeds_kmh": speeds, "w1": w1, "w2": w2}


def test_weather_rho_matches_hand_value():
  # rho = P/(R*T). Hand case: P = 101325 Pa, R = 287.05 J/(kg*K), T = 288.15 K (15 degC).
  # rho = 101325 / (287.05 * 288.15) = 1.2250... kg/m^3.
  temps = np.full(24, 288.15)
  winds = np.zeros(24)
  v_avg = np.array([80.0 / 3.6, 80.0 / 3.6])   # 80 km/h in m/s, two rows
  rho, cdxa = weather_for_rows(v_avg, departure_time=8.0, temps_by_hour=temps,
                               winds_by_hour=winds, cdxa_table=_flat_cdxa_table(5.0),
                               P=101325.0, R=287.05, dt_s=1.0)
  expected_rho = 101325.0 / (287.05 * 288.15)
  assert np.allclose(rho, expected_rho)
  # W1=1, W2=0 -> CdxA_eff == CdxA(0) = 5.0
  assert np.allclose(cdxa, 5.0)


def test_weather_cdxa_clamps_below_60_and_interpolates_within():
  # a table whose CdxA_eff rises linearly with speed so interpolation is checkable.
  # cdxa0=1, W1 = speed/60 so CdxA_eff(speed) = speed/60; W2 = 0.
  speeds = np.array([60.0, 90.0, 105.0])
  w1 = speeds / 60.0
  w2 = np.zeros_like(speeds)
  table = {"cdxa0": 1.0, "speeds_kmh": speeds, "w1": w1, "w2": w2}
  temps = np.full(24, 288.15)
  winds = np.zeros(24)

  # row speeds: 30 km/h (below 60 -> use 60 value = 1.0), 75 km/h (interpolate 60..90).
  v_avg = np.array([30.0 / 3.6, 75.0 / 3.6])
  _, cdxa = weather_for_rows(v_avg, 8.0, temps, winds, table, P=101325.0, R=287.05)
  # below 60 -> clamp to 60 -> CdxA_eff = 60/60 = 1.0
  assert math.isclose(cdxa[0], 1.0, rel_tol=1e-9)
  # 75 km/h: interp between 60 (1.0) and 90 (1.5) -> 1.25
  assert math.isclose(cdxa[1], 1.25, rel_tol=1e-9)


def test_weather_raises_above_105():
  temps = np.full(24, 288.15)
  winds = np.zeros(24)
  v_avg = np.array([110.0 / 3.6])    # 110 km/h is above the 105 km/h lookup top
  with pytest.raises(ValueError):
    weather_for_rows(v_avg, 8.0, temps, winds, _flat_cdxa_table(), P=101325.0, R=287.05)


def test_weather_bounds_constants():
  assert CDXA_SPEED_MIN_KMH == 60.0 and CDXA_SPEED_MAX_KMH == 105.0


# ---------------------------------------------------------------------------
# ITEM 6 - power_step
# ---------------------------------------------------------------------------

def test_power_step_neutral_beta_equals_simple_K():
  # neutral beta=1, k_rot=0 -> P_wheel = m*(k_lin + k_roll) + rho*CdxA*L (the simple K).
  m = 20000.0
  k_lin = np.array([0.5, 1.0])
  k_roll = np.array([1.0791, 0.5])
  k_rot = np.array([0.0, 0.0])
  rho = np.array([1.225, 1.225])
  cdxa = np.array([5.0, 5.0])
  L = np.array([4000.0, 580.125])
  out = power_step(m, 1.0, k_lin, k_roll, k_rot, rho, cdxa, L)
  expected = m * (k_lin + k_roll) + rho * cdxa * L
  assert np.allclose(out, expected)


def test_power_step_matches_pure_python_loop_on_random_arrays():
  rng = np.random.default_rng(42)
  n = 50
  m = 18500.0
  beta = 0.9
  k_lin = rng.normal(size=n)
  k_roll = rng.uniform(0.1, 2.0, size=n)
  k_rot = rng.uniform(0.0, 0.5, size=n)
  rho = rng.uniform(1.1, 1.3, size=n)
  cdxa = rng.uniform(4.0, 9.0, size=n)
  L = rng.uniform(0.0, 5000.0, size=n)

  out = power_step(m, beta, k_lin, k_roll, k_rot, rho, cdxa, L)
  ref = np.array([
    m * k_lin[i] + m ** beta * k_roll[i] + k_rot[i] + rho[i] * cdxa[i] * L[i]
    for i in range(n)
  ])
  assert np.allclose(out, ref)


# ---------------------------------------------------------------------------
# ITEM 7 - p_aux
# ---------------------------------------------------------------------------

# Group 5 Regional Delivery BEV reference (paux close-out section 5):
#   ES=1000, HVAC=250, PS=687, SP=401.9, Cond=600.
P_ES, P_HVAC, P_PS, P_SP, P_COND = 1000.0, 250.0, 687.0, 401.9, 600.0


def test_p_aux_reproduces_three_reference_states():
  # per-row flags for the three documented states:
  #   row0 moving + motor on  -> 2938.9 W
  #   row1 stopped + motor on -> 2537.0 W
  #   row2 stopped + motor off-> 1937.0 W
  moving = np.array([True, False, False])
  motor_on = np.array([True, True, False])
  out = p_aux(P_ES, P_HVAC, P_PS, P_SP, P_COND, moving, motor_on)
  assert math.isclose(out[0], 2938.9, rel_tol=0, abs_tol=1e-6)
  assert math.isclose(out[1], 2537.0, rel_tol=0, abs_tol=1e-6)
  assert math.isclose(out[2], 1937.0, rel_tol=0, abs_tol=1e-6)


def test_p_aux_raises_on_blank_cell():
  # a None constant stands for a blank/'---' VECTO cell -> must raise (never silently 0 W).
  with pytest.raises(ValueError):
    p_aux(None, P_HVAC, P_PS, P_SP, P_COND, [True], [True])


def test_p_aux_weather_hook_raises_notimplemented():
  with pytest.raises(NotImplementedError):
    p_aux(P_ES, P_HVAC, P_PS, P_SP, P_COND, [True], [True],
          aux_weather_fn=lambda *a: 0.0)


# ---------------------------------------------------------------------------
# ITEM 8 - consumption
# ---------------------------------------------------------------------------

def test_consumption_sign_switch_at_zero():
  # hand case: traction row divides by eta_drive; regen row multiplies by eta_regen.
  P_wheel = np.array([1000.0, -1000.0, 0.0])
  out = consumption(P_wheel, eta_drive=0.95, eta_regen=0.95, eta_dcdc=0.98, P_aux=0.0, dt_s=1.0)
  P_batt = out["P_batt"]
  # P_wheel > 0 -> /eta_drive
  assert math.isclose(P_batt[0], 1000.0 / 0.95, rel_tol=1e-12)
  # P_wheel <= 0 -> *eta_regen  (both the negative and the exact-zero row)
  assert math.isclose(P_batt[1], -1000.0 * 0.95, rel_tol=1e-12)
  assert math.isclose(P_batt[2], 0.0, abs_tol=1e-12)


def test_consumption_carries_placeholder_flag():
  out = consumption(np.array([500.0]))
  assert out["placeholder_efficiencies"] is True
  assert out["message"] == PLACEHOLDER_MESSAGE
  assert out["efficiencies"] == {"eta_drive": 0.95, "eta_regen": 0.95, "eta_dcdc": 0.98}


def test_consumption_adds_aux_and_integrates_kwh():
  # two rows, 1 s each. P_wheel = [0, 0] so no traction; P_aux = 1960 W through eta_dcdc=0.98.
  # P_batt per row = 1960/0.98 = 2000 W. Energy = 2000 W * 2 s = 4000 J = 4000/3.6e6 kWh.
  out = consumption(np.array([0.0, 0.0]), eta_dcdc=0.98, P_aux=np.array([1960.0, 1960.0]), dt_s=1.0)
  assert np.allclose(out["P_batt"], 2000.0)
  assert math.isclose(out["kWh"], 4000.0 / 3.6e6, rel_tol=1e-12)


def test_consumption_matches_loop_reference():
  rng = np.random.default_rng(7)
  n = 100
  P_wheel = rng.normal(scale=5000.0, size=n)
  P_aux = rng.uniform(1500.0, 3000.0, size=n)
  ed, er, edc, dt = 0.93, 0.91, 0.97, 1.0
  out = consumption(P_wheel, eta_drive=ed, eta_regen=er, eta_dcdc=edc, P_aux=P_aux, dt_s=dt)

  ref_P = np.zeros(n)
  for i in range(n):
    trac = P_wheel[i] / ed if P_wheel[i] > 0 else P_wheel[i] * er
    ref_P[i] = trac + P_aux[i] / edc
  ref_kwh = float(np.sum(ref_P * dt)) / 3.6e6
  assert np.allclose(out["P_batt"], ref_P)
  assert math.isclose(out["kWh"], ref_kwh, rel_tol=1e-12)


def test_consumption_rejects_bad_efficiency():
  with pytest.raises(ValueError):
    consumption(np.array([100.0]), eta_drive=0.0)
