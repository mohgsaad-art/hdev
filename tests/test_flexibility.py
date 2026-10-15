# STATUS: NEW (Step 9, item 16, Bob to review). Hand-checked tests for the pure flexibility wrapper.
#
# src/charging/flexibility.py re-expresses the import/export heads of
# src/charging/flexibility_setpoints.refresh_feasibility over plain arrays (no gym, no env) and rolls
# them into per-hour up/down headroom. These tests pin the arithmetic with numbers worked out by hand
# and assert the §8 plain-word output (no strategy name).
import json

import numpy as np
import pytest

from src.charging.flexibility import feasible_heads, flexibility_per_hour


def test_feasible_import_head_capped_by_site():
    # two present EVs each need 100 kWh over dt=1h -> each wants 100 kW, charger cap 60 kW -> 60+60=120,
    # but the site is capped at 100 kW, so Pmax = 100. no V2G args -> Pmin = 0.
    present = [True, True]
    need = [100.0, 100.0]
    pmin, pmax = feasible_heads(present, need, max_charging_rate_kw=60.0,
                                max_station_capacity_kw=100.0, dt_h=1.0)
    assert pmax == 100.0
    assert pmin == 0.0


def test_feasible_import_head_capped_by_charger_and_need():
    # one present EV needs 30 kWh over dt=1h -> wants 30 kW; charger 60, site 400 -> head = 30. an absent
    # EV contributes nothing.
    present = [True, False]
    need = [30.0, 999.0]
    pmin, pmax = feasible_heads(present, need, max_charging_rate_kw=60.0,
                                max_station_capacity_kw=400.0, dt_h=1.0)
    assert pmax == 30.0
    assert pmin == 0.0


def test_feasible_export_head_v2g():
    # one V2G EV at SoC 0.8, min_soc_v2g 0.5, battery 100 kWh -> head (0.8-0.5)*100 = 30 kWh over dt=1h
    # -> 30 kW; charger 60, site 400 -> Pmin = -30.
    present = [True]
    need = [10.0]
    pmin, pmax = feasible_heads(present, need, max_charging_rate_kw=60.0,
                                max_station_capacity_kw=400.0, dt_h=1.0,
                                v2g_capable=[True], soc_current=[0.8],
                                min_soc_v2g=0.5, battery_capacity_kwh=100.0)
    assert pmax == 10.0
    assert pmin == pytest.approx(-30.0)


def test_flexibility_per_hour_up_down():
    # load 50 kW, import head 120 kW, export head -20 kW over a single hour.
    # up = 120 - 50 = 70; down = 50 - (-20) = 70. energy versions equal (dt=1h).
    out = flexibility_per_hour([50.0], feasible_import_kw=120.0, feasible_export_kw=-20.0, dt_h=1.0)
    assert out["up_kw"] == [70.0]
    assert out["down_kw"] == [70.0]
    assert out["up_kwh"] == [70.0]
    assert out["down_kwh"] == [70.0]


def test_flexibility_per_hour_clamps_at_zero():
    # if the load already sits at the import head there is no upward headroom; down is bounded >= 0.
    out = flexibility_per_hour([120.0, 0.0], feasible_import_kw=[120.0, 120.0],
                               feasible_export_kw=[0.0, 0.0], dt_h=1.0)
    assert out["up_kw"] == [0.0, 120.0]
    assert out["down_kw"] == [120.0, 0.0]


def test_flexibility_output_is_plain_worded():
    # §8: no internal strategy name leaks into the output.
    out = flexibility_per_hour([10.0], feasible_import_kw=50.0, feasible_export_kw=0.0)
    blob = json.dumps(out).lower()
    for banned in ("asap", "jit", "edf", " es ", "cost-based", "setpoint"):
        assert banned not in blob
