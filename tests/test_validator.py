# STATUS: NEW (PR 1). Tests for the validator: lever rejection, patch rejection, lock enforcement,
# and physical/logical sanity checks only (requirements §9.6).
from src.registry.fields import Field
from src.validate import validate_lever, validate_patch, validate_range
from src.validate import validator as _validator


# ---- lever validation (user §3.2) -----------------------------------------
def test_rejects_unknown_lever():
    r = validate_lever("made_up_lever", 5)
    assert not r.ok
    assert r.error


def test_rejects_out_of_range_lever_value():
    assert not validate_lever("fleet_size", 0)          # below min
    assert not validate_lever("charging_priority", "cheapest")  # not an option
    assert not validate_lever("ownership_years", 9)     # not an allowed option


def test_accepts_valid_lever():
    assert validate_lever("fleet_size", 10)
    assert validate_lever("charging_priority", "grid_friendly")
    assert validate_lever("ownership_years", 12)


def test_fleet_size_max_from_project():
    # with a project cap, going above it is rejected; within it is accepted.
    assert not validate_lever("fleet_size", 50, project={"fleet_size": 20})
    assert validate_lever("fleet_size", 15, project={"fleet_size": 20})
    # without a project, only min + int-ness are enforced.
    assert validate_lever("fleet_size", 9999)


def test_open_editable_field_is_a_lever_target():
    # operation.schedule.shift_end is open + editable_in_demo (an enum/dropdown), so it is a valid lever.
    assert validate_lever("operation.schedule.shift_end", "18:00")


# ---- patch validation (user §3.1) ------------------------------------------
def test_rejects_patch_to_unknown_field():
    r = validate_patch({"field": "nope.not.here", "value": 1})
    assert not r.ok
    assert r.error


def test_rejects_patch_to_locked_slot():
    # §9.4 / M6.14: a write to a locked slot is rejected.
    r = validate_patch({"field": "vehicles.battery.usable_capacity", "value": 300, "locked": True})
    assert not r.ok
    assert r.error


def test_rejects_wrong_type_value():
    # usable_capacity is a number; a string must be rejected.
    assert not validate_patch({"field": "vehicles.battery.usable_capacity", "value": "lots"})
    # a bool field must get a bool.
    assert not validate_patch({"field": "operation.routes.return_to_depot", "value": "yes"})


def test_accepts_valid_patch():
    assert validate_patch({"field": "vehicles.battery.usable_capacity", "value": 250})
    assert validate_patch({"field": "operation.routes.return_to_depot", "value": True})


# ---- physical / logical sanity only (requirements §9.6) --------------------
def test_rejects_negative_where_physical():
    # a distance cannot be negative.
    assert not validate_patch({"field": "operation.routes.daily_distance", "value": -5})
    # a capacity cannot be negative.
    assert not validate_patch({"field": "vehicles.battery.usable_capacity", "value": -1})


def test_accepts_unusual_but_physical_value():
    # §9.6: no invented plausibility ranges. a huge-but-physical capacity is ACCEPTED.
    assert validate_patch({"field": "vehicles.battery.usable_capacity", "value": 100000})
    # a very long daily distance is physical and accepted.
    assert validate_patch({"field": "operation.routes.daily_distance", "value": 5000})


def test_accepts_negative_where_physical_allows_it():
    # a temperature can be negative; §9.6 must not reject it.
    assert validate_patch({"field": "weather.daily_records.min_temperature", "value": -30})
    # a price trend can be negative (prices can fall).
    assert validate_patch({"field": "energy_prices.trends.electricity_trend", "value": -2})


def test_fraction_field_bounded_0_to_1():
    # a share/fraction must stay within 0..1 (§9.6). exercised with a synthetic fraction field so the
    # SoC>1 rejection is covered regardless of which registry fields are fractions.
    frac = Field(
        id="vehicles.battery.state_of_charge", section="vehicles", subgroup="battery",
        label="Battery charge level", type="number", unit=None, visibility="collapsed",
        editable_in_demo=False,
    )
    assert not _validator._sanity_number(frac, 1.5)   # SoC > 1 rejected
    assert not _validator._sanity_number(frac, -0.1)  # SoC < 0 rejected
    assert _validator._sanity_number(frac, 0.5)       # within range accepted


def test_validate_range_min_le_max():
    assert validate_range(1, 5)
    assert not validate_range(5, 1)
