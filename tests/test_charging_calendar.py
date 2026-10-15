# STATUS: NEW (Step 9 items 9-14). Hand-checked unit tests for the calendar/sizing/charging/AI-adapter
#   block. conftest.py puts repo root on sys.path so imports resolve as src.resolver.* / src.charging.*.
# Every expected number is a hand-checked case with the arithmetic written out in the test. None of these
# modules may import gym at load (the thesis env ev_charging_env.py imports gym; the pure path must not).

import datetime as dt

import pytest


# ---------------------------------------------------------------------------
# ITEM 9 - calendar expand (pattern -> dated operating days, Danish holidays)
# ---------------------------------------------------------------------------

from src.resolver.calendar import (
    build_calendar,
    standard_danish_holidays,
    easter_sunday,
)


def _two_weeks_weather():
    # Dec 14 2026 (Mon) .. Dec 27 2026 (Sun): 14 consecutive dates with trivial weather supplied.
    return {dt.date(2026, 12, d): {"T": 2.0, "wind": 5.0} for d in range(14, 28)}


def test_build_calendar_expands_two_week_weekday_pattern():
    # 2026-12-14 (Mon) .. 2026-12-27 (Sun) is exactly two calendar weeks = 14 dates.
    # weekdays pattern -> 10 Mon-Fri dates, but 2026-12-25 (Fri, Christmas Day) is a holiday.
    # So operating days = 10 - 1 = 9. Hand-counted:
    #   wk1 Mon14 Tue15 Wed16 Thu17 Fri18          -> 5
    #   wk2 Mon21 Tue22 Wed23 Thu24 (Fri25 holiday) -> 4
    #   total 9.
    holidays = {dt.date(2026, 12, 25), dt.date(2026, 12, 26)}
    cal = build_calendar(
        dt.date(2026, 12, 14), dt.date(2026, 12, 27),
        "weekdays", _two_weeks_weather(), holidays,
    )
    assert len(cal["rows"]) == 14
    assert cal["operating_days"] == 9

    # the known Danish holiday 2026-12-25 is non-operating
    row_dec25 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 25))
    assert row_dec25["operating"] is False
    assert row_dec25["day_type"] is None

    # a normal operating weekday carries the day-type and the supplied weather
    row_dec14 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 14))
    assert row_dec14["operating"] is True
    assert row_dec14["day_type"] == "default"
    assert row_dec14["T"] == 2.0 and row_dec14["wind"] == 5.0

    # weekend dates are non-operating under the weekdays pattern
    row_dec19 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 19))  # Saturday
    assert row_dec19["operating"] is False

    # the holiday-set assumption is surfaced, not applied silently
    assert any("HOLIDAY SET ASSUMPTION" in a for a in cal["assumptions"])


def test_easter_based_holidays_and_great_prayer_day_rule():
    # Easter Sunday 2026 is 2026-04-05 (hand/reference checked).
    assert easter_sunday(2026) == dt.date(2026, 4, 5)
    # Great Prayer Day = 4th Friday after Easter = Easter + 26 days.
    gpd_2023 = easter_sunday(2023) + dt.timedelta(days=26)
    gpd_2026 = easter_sunday(2026) + dt.timedelta(days=26)
    # statutory in 2023, abolished from 2024 -> present in 2023 set, absent in 2026 set (default rule).
    assert gpd_2023 in standard_danish_holidays(2023)
    assert gpd_2026 not in standard_danish_holidays(2026)
    # forcing it on brings it back for 2026
    assert gpd_2026 in standard_danish_holidays(2026, include_great_prayer_day=True)
    # contested days OFF by default, ON when switched
    assert dt.date(2026, 6, 5) not in standard_danish_holidays(2026)
    assert dt.date(2026, 6, 5) in standard_danish_holidays(2026, include_constitution_day=True)


def test_build_calendar_raises_on_operating_date_without_weather():
    # an operating date with no weather entry must raise (weather is never invented).
    with pytest.raises(ValueError):
        build_calendar(
            dt.date(2026, 1, 5), dt.date(2026, 1, 5),  # a Monday
            "weekdays", {}, set(),
        )


def test_build_calendar_rejects_bad_date_order_and_unknown_pattern():
    with pytest.raises(ValueError):
        build_calendar(dt.date(2026, 1, 2), dt.date(2026, 1, 1), "weekdays", {}, set())
    with pytest.raises(ValueError):
        build_calendar(
            dt.date(2026, 1, 5), dt.date(2026, 1, 5),
            "every-third-tuesday", _two_weeks_weather(), set(),
        )


# ---------------------------------------------------------------------------
# ITEM 10 - session hand-over object {arrival, departure, energy_need_kWh, arrival_SOC}
# ---------------------------------------------------------------------------

from dataclasses import fields as _dc_fields

from src.resolver.session_handover import ChargingSession, build_sessions


def test_session_handover_has_exactly_the_four_fields():
    names = {f.name for f in _dc_fields(ChargingSession)}
    assert names == {"arrival", "departure", "energy_need_kWh", "arrival_SOC"}
    # explicitly NOT departure_time (the separate 🔒 M2.7)
    assert "departure_time" not in names


def test_build_sessions_carries_soc_across_two_days():
    # two operating days, pack 100 kWh usable, start SOC 0.50.
    # day 1 uses 20 kWh -> session1 arrival_SOC = 0.50, need 20.
    #   carried SOC = 0.50 + 20/100 = 0.70.
    # day 2 uses 30 kWh -> session2 arrival_SOC = 0.70, need 30.
    rows = [
        {"arrival": dt.datetime(2026, 1, 5, 18, 0), "departure": dt.datetime(2026, 1, 6, 6, 0),
         "energy_used_kWh": 20.0},
        {"arrival": dt.datetime(2026, 1, 6, 18, 0), "departure": dt.datetime(2026, 1, 7, 6, 0),
         "energy_used_kWh": 30.0},
    ]
    out = build_sessions(rows, start_soc=0.50, usable_pack_kwh=100.0)
    s = out["sessions"]
    assert len(s) == 2
    assert s[0].arrival_SOC == pytest.approx(0.50)
    assert s[0].energy_need_kWh == pytest.approx(20.0)
    assert s[1].arrival_SOC == pytest.approx(0.70)
    assert s[1].energy_need_kWh == pytest.approx(30.0)


def test_build_sessions_fails_loudly():
    bad_order = [{"arrival": dt.datetime(2026, 1, 6, 6, 0),
                  "departure": dt.datetime(2026, 1, 5, 18, 0), "energy_used_kWh": 10.0}]
    with pytest.raises(ValueError):
        build_sessions(bad_order, start_soc=0.5, usable_pack_kwh=100.0)
    good = [{"arrival": dt.datetime(2026, 1, 5, 18, 0),
             "departure": dt.datetime(2026, 1, 6, 6, 0), "energy_used_kWh": 10.0}]
    with pytest.raises(ValueError):
        build_sessions(good, start_soc=1.5, usable_pack_kwh=100.0)   # SOC out of range
    with pytest.raises(ValueError):
        build_sessions(good, start_soc=0.5, usable_pack_kwh=0.0)     # bad pack


# ---------------------------------------------------------------------------
# ITEM 11 - battery sizing (mode A datasheet / mode B iterate)
# ---------------------------------------------------------------------------

from src.charging.sizing import size_battery_mode_a, size_battery_mode_b


def test_mode_a_returns_datasheet_value():
    # mode A is decided: the datasheet value is returned directly, no model.
    assert size_battery_mode_a(540.0) == pytest.approx(540.0)
    with pytest.raises(ValueError):
        size_battery_mode_a(0.0)
    with pytest.raises(ValueError):
        size_battery_mode_a(None)


def test_mode_b_fixpoint_converges_on_hand_case():
    # closed-form check of the fixpoint:
    #   base mass (no pack) = glider + payload = 10000 + 5000 = 15000 kg
    #   energy_need = 0.0001 kWh/km/kg * 300 km * M = 0.03 * M  (usable_fraction=1 -> nominal = need)
    #   pack_mass = nominal / 0.15 = (0.03*M)/0.15 = 0.2*M
    #   M = 15000 + 0.2*M  ->  0.8*M = 15000  ->  M = 18750 kg
    #   pack_mass = 3750 kg ; battery_kwh = 0.03 * 18750 = 562.5 kWh
    r = size_battery_mode_b(
        glider_mass_kg=10000.0, pack_kwh_per_kg=0.15, payload_kg=5000.0,
        energy_per_km_per_kg=0.0001, range_km=300.0,
    )
    assert r["battery_kwh"] == pytest.approx(562.5, rel=1e-6)
    assert r["pack_mass_kg"] == pytest.approx(3750.0, rel=1e-6)
    assert r["total_mass_kg"] == pytest.approx(18750.0, rel=1e-6)
    # the source flag for the locked (🔒 M3.2) glider-mass + kWh/kg inputs is surfaced
    assert any("M3.2" in a for a in r["assumptions"])


def test_mode_b_requires_the_locked_source_args_and_fails_loudly():
    # required args have no defaults -> omitting them is a TypeError
    with pytest.raises(TypeError):
        size_battery_mode_b(glider_mass_kg=10000.0, pack_kwh_per_kg=0.15)
    # a diverging design (each kg of pack needs >1 kg of pack) must raise, never guess
    with pytest.raises(ValueError):
        size_battery_mode_b(
            glider_mass_kg=10000.0, pack_kwh_per_kg=0.001, payload_kg=0.0,
            energy_per_km_per_kg=0.01, range_km=300.0,
        )


# ---------------------------------------------------------------------------
# ITEM 12 - AI waypoint adapter (interface + stub only, map provider not chosen)
# ---------------------------------------------------------------------------

from src.resolver.ai_waypoint_adapter import ai_waypoints_from_descriptions


def test_ai_waypoint_adapter_is_a_stub():
    with pytest.raises(NotImplementedError) as exc:
        ai_waypoints_from_descriptions([{"description": "depot"}])
    assert "map provider not chosen" in str(exc.value)


# ---------------------------------------------------------------------------
# ITEM 13 - charging sizing (P=E/t) + simulation (OCV + Ri), dt a required arg
# ---------------------------------------------------------------------------

from src.charging.battery_ocv_ri import (
    battery_step,
    solve_current_for_power,
    ocv_lookup,
)
from src.charging.charging_sim import (
    sizing_power,
    simulate_session,
    resolve_timestep_plan,
)


def test_sizing_power_is_energy_over_time():
    # P_min = E / t : 60 kWh over 10 h = 6 kW. Hand value.
    assert sizing_power(60.0, 10.0) == pytest.approx(6.0)
    with pytest.raises(ValueError):
        sizing_power(60.0, 0.0)


def test_ocv_and_current_solver_hand_values():
    # linear 2-point OCV table interpolates to the midpoint
    assert ocv_lookup([(0.0, 300.0), (1.0, 400.0)], 0.5) == pytest.approx(350.0)
    # table never extrapolates
    with pytest.raises(ValueError):
        ocv_lookup([(0.0, 300.0), (1.0, 400.0)], 1.5)
    # R = 0 -> I = P / U0 : 1000 W / 400 V = 2.5 A
    assert solve_current_for_power(1000.0, 400.0, 0.0) == pytest.approx(2.5)
    # R = 0.1 -> R*I^2 + U0*I - P = 0 solved for the +sign root
    import math as _m
    disc = 400.0 * 400.0 + 4 * 0.1 * 1000.0
    expected = (-400.0 + _m.sqrt(disc)) / (2 * 0.1)
    assert solve_current_for_power(1000.0, 400.0, 0.1) == pytest.approx(expected)


def test_battery_step_charges_and_reports_loss():
    # 10 A charge, R = 0.1 ohm -> loss = I^2 R = 10*10*0.1 = 10 W ; terminal = U0 + I*R.
    # choose a power that yields exactly 10 A at U0: solve on R=0 would be P=U0*I; with R the solver
    # finds I for the given P, so instead feed a known current by using R=0 and P = U0*I.
    out = battery_step(0.5, 350.0 * 10.0, 3600.0, [(0.0, 300.0), (1.0, 400.0)], 0.0,
                       capacity_as=3600000.0)
    assert out["current_a"] == pytest.approx(10.0, rel=1e-6)
    # SOC advance = I*dt/Q = 10*3600/3600000 = 0.01
    assert out["soc"] == pytest.approx(0.51, rel=1e-6)


def test_simulate_session_delivers_energy_over_window():
    # 1000 W for 3600 s = 1.0 kWh of terminal energy, R = 0 (no loss), dt 60 s -> 60 steps.
    r = simulate_session(0.5, 1000.0, 3600.0, 60.0, [(0.0, 300.0), (1.0, 400.0)], 0.0,
                         capacity_as=360000.0)
    assert r["delivered_kwh"] == pytest.approx(1.0, rel=1e-9)
    assert r["steps"] == 60
    assert r["soc_end"] > 0.5  # charged up


def test_simulate_session_requires_dt_no_default():
    # dt is REQUIRED (no default). Passing None raises loudly; it must never silently default.
    with pytest.raises(ValueError) as exc:
        simulate_session(0.5, 1000.0, 3600.0, None, [(0.0, 300.0), (1.0, 400.0)], 0.0,
                         capacity_as=360000.0)
    assert "dt" in str(exc.value)
    # it is also a positional/keyword arg with no default in the signature
    import inspect
    sig = inspect.signature(simulate_session)
    assert sig.parameters["dt"].default is inspect.Parameter.empty


def test_timestep_plan_is_neutral_by_default():
    plan = resolve_timestep_plan(900.0)
    assert plan["neutral"] is True
    assert plan["dt_fine"] == plan["dt_base"] == 900.0
    assert plan["windows"] == []
    assert "Energinet" in plan["flag"]
    # a fine window makes it non-neutral
    plan2 = resolve_timestep_plan(900.0, dt_fine=300.0, windows=[(0, 3600)])
    assert plan2["neutral"] is False


# ---------------------------------------------------------------------------
# ITEM 14 - year-long depot charging run (SOC carry-over, shared chargers, site cap)
# ---------------------------------------------------------------------------

from src.charging.year_depot_run import run_year_depot
from src.resolver.session_handover import build_sessions as _build_sessions


def _battery_params():
    # a flat-ish OCV pack, R = 0 (lossless), big capacity so delivery is energy-faithful.
    return {
        "ocv_table": [(0.0, 350.0), (1.0, 370.0)],
        "r_internal": 0.0,
        "capacity_as": 1_000_000.0,
        "usable_pack_kwh": 100.0,
    }


def test_run_year_depot_carries_soc_across_two_sessions():
    # two overnight sessions, each 12 h dwell. JIT power = energy / dwell:
    #   session 1: 20 kWh / 12 h = 1.6667 kW (<= 50 kW charger / 50 kW site) -> delivers 20 kWh
    #   session 2: 30 kWh / 12 h = 2.5    kW                               -> delivers 30 kWh
    # The ending SOC of session 1 must become the arrival SOC of session 2 (REAL carry-over).
    rows = [
        {"arrival": dt.datetime(2026, 1, 5, 18, 0), "departure": dt.datetime(2026, 1, 6, 6, 0),
         "energy_used_kWh": 20.0},
        {"arrival": dt.datetime(2026, 1, 6, 18, 0), "departure": dt.datetime(2026, 1, 7, 6, 0),
         "energy_used_kWh": 30.0},
    ]
    sessions = _build_sessions(rows, start_soc=0.5, usable_pack_kwh=100.0)["sessions"]
    out = run_year_depot(sessions, chargers=[50.0], site_limit_kw=50.0, dt=300.0,
                         battery_params=_battery_params())
    r = out["results"]
    assert len(r) == 2
    # JIT power hand values
    assert r[0]["power_kw"] == pytest.approx(20.0 / 12.0, rel=1e-6)
    assert r[1]["power_kw"] == pytest.approx(30.0 / 12.0, rel=1e-6)
    # energy delivered meets the need (lossless, enough dwell)
    assert r[0]["delivered_kWh"] == pytest.approx(20.0, rel=1e-3)
    assert r[1]["delivered_kWh"] == pytest.approx(30.0, rel=1e-3)
    # SOC carry-over: session 2 arrival SOC == session 1 ending SOC (the REAL ending SOC, not the
    # neutral one build_sessions laid out) and rises from ~0.50 to ~0.70 then ~0.99.
    assert r[1]["arrival_SOC"] == pytest.approx(r[0]["ending_SOC"])
    assert r[0]["ending_SOC"] == pytest.approx(0.699, abs=0.01)
    assert out["ending_soc"] == pytest.approx(r[1]["ending_SOC"])
    assert out["ending_soc"] == pytest.approx(0.993, abs=0.01)


def test_run_year_depot_requires_dt_and_valid_site_cap():
    sessions = _build_sessions(
        [{"arrival": dt.datetime(2026, 1, 5, 18, 0), "departure": dt.datetime(2026, 1, 6, 6, 0),
          "energy_used_kWh": 10.0}],
        start_soc=0.5, usable_pack_kwh=100.0,
    )["sessions"]
    with pytest.raises(ValueError):
        run_year_depot(sessions, chargers=[50.0], site_limit_kw=50.0, dt=None,
                       battery_params=_battery_params())
    with pytest.raises(ValueError):
        run_year_depot(sessions, chargers=[], site_limit_kw=50.0, dt=300.0,
                       battery_params=_battery_params())
    with pytest.raises(ValueError):
        run_year_depot(sessions, chargers=[50.0], site_limit_kw=0.0, dt=300.0,
                       battery_params=_battery_params())


def test_year_depot_modules_do_not_import_gym():
    # the pure path must load without gym installed (gym is NOT in the venv).
    import sys
    assert "gym" not in sys.modules
    import importlib
    importlib.import_module("src.charging.year_depot_run")
    importlib.import_module("src.charging.charging_sim")
    importlib.import_module("src.resolver.calendar")
    assert "gym" not in sys.modules
