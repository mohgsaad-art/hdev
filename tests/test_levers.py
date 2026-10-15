# STATUS: NEW (PR 1). Tests for LEVERS (user §3.2) - exact keys, options, min/max.
from src.registry import LEVERS, allowed_lever_keys, FLEET_SIZE_MAX_FROM_PROJECT


def test_exactly_five_lever_keys():
    assert set(LEVERS) == {
        "fleet_size",
        "charging_priority",
        "electricity_price",
        "weather_year",
        "ownership_years",
    }
    assert set(allowed_lever_keys()) == set(LEVERS)


def test_fleet_size_spec():
    assert LEVERS["fleet_size"] == {"type": "int", "min": 1, "max": FLEET_SIZE_MAX_FROM_PROJECT}
    assert FLEET_SIZE_MAX_FROM_PROJECT == "from project"


def test_charging_priority_uses_only_client_facing_names():
    assert LEVERS["charging_priority"]["type"] == "enum"
    assert LEVERS["charging_priority"]["options"] == ["lowest_cost", "grid_friendly", "ready_earliest"]


def test_electricity_price_options():
    assert LEVERS["electricity_price"]["options"] == ["low", "expected", "high"]


def test_weather_year_options():
    assert LEVERS["weather_year"]["options"] == ["normal", "cold_winter"]


def test_ownership_years_options():
    assert LEVERS["ownership_years"]["options"] == [8, 10, 12]
