# STATUS: NEW (PR 1, revised). Tests for the input registry structure (user §3.1 / §5.4).
# the registry is the single source of truth: the §5.4 mock-up numbers (a 112 total, per-subgroup counts)
# were PLACEHOLDERS, not requirements. these tests therefore assert that (a) every field carries a
# non-empty internal maps_to, (b) a field with no maps_to cannot be constructed, and (c) all counts are
# COMPUTED from the registry and internally consistent - never against a hard-coded count.
import pytest

from src.registry import (
    Section,
    SECTIONS,
    FIELDS,
    SUBGROUPS,
    FIELD_TYPES,
    VISIBILITY_VALUES,
    Field,
    fields_in_section,
    fields_in_subgroup,
    listable_fields,
    visibility_counts,
)
from src.registry.registry import section_counts

# the 8 §5.4 sections (a real structural fact) and their ordered subgroup NAMES. names (not counts) are
# allowed expectations; the registry is still the source of truth for how many fields each one holds.
EXPECTED_SECTIONS = {
    "operation": ("schedule", "routes"),
    "vehicles": ("body", "drivetrain", "battery", "wheels", "equipment"),
    "depot_grid": ("site", "connection", "building_load", "chargers_on_site"),
    "charging": ("strategy", "charger_types", "time_windows"),
    "energy_prices": ("electricity", "grid_tariffs", "diesel", "trends"),
    "weather": ("location", "daily_records", "seasons"),
    "costs_finance": ("purchase", "leasing", "maintenance", "finance"),
    "policy_taxes": ("taxes", "subsidies"),
}

# sections that may hold "open" fields per §3.1 (Operation and Energy prices only).
MAY_BE_OPEN = {"operation", "energy_prices"}


def test_eight_sections():
    assert len(SECTIONS) == 8
    assert {s.id for s in SECTIONS} == set(EXPECTED_SECTIONS)


def test_every_field_has_maps_to():
    # every retained field names the engine input / pipeline step / source doc it feeds (internal only).
    for f in FIELDS:
        assert f.maps_to and f.maps_to.strip(), f.id


def test_field_requires_maps_to():
    # constructing a Field with an empty/blank maps_to must fail loudly.
    for bad in ("", "   "):
        with pytest.raises(ValueError):
            Field(
                id="operation.schedule.bogus", section="operation", subgroup="schedule",
                label="Bogus", type="number", unit=None, visibility="open",
                editable_in_demo=True, maps_to=bad,
            )


def test_total_count_is_registry_derived():
    # the total is whatever the registry holds (no magic literal): sum of per-section counts == len(FIELDS).
    assert sum(len(fields_in_section(s.id)) for s in SECTIONS) == len(FIELDS)


def test_section_and_subgroup_counts_are_internally_consistent():
    # for each section, the sum of its subgroup field counts equals the section's own field count,
    # and every field lands in a declared subgroup. all counts are computed from FIELDS.
    for section in SECTIONS:
        in_section = fields_in_section(section.id)
        subgroup_sum = sum(len(fields_in_subgroup(section.id, name)) for name in section.subgroups)
        assert subgroup_sum == len(in_section), section.id
        assert {f.subgroup for f in in_section} == set(section.subgroups), section.id


def test_section_counts_helper_is_registry_derived():
    counts = section_counts()
    # per-section n matches fields_in_section, and the sum over sections equals the whole registry.
    assert sum(counts[s.id]["n"] for s in SECTIONS) == len(FIELDS)
    for section in SECTIONS:
        assert counts[section.id]["n"] == len(fields_in_section(section.id))
        for name in section.subgroups:
            assert counts[section.id]["subgroups"][name] == len(fields_in_subgroup(section.id, name))


def test_section_total_property_matches_fields():
    for section in SECTIONS:
        assert section.total == len(fields_in_section(section.id))


def test_subgroup_names_come_from_the_registry():
    # the registry's own SUBGROUPS keys per section are exactly the section's declared subgroup names.
    for section in SECTIONS:
        assert set(SUBGROUPS[section.id].keys()) == set(section.subgroups), section.id
        assert set(section.subgroups) == set(EXPECTED_SECTIONS[section.id]), section.id


def test_every_field_has_valid_metadata():
    for f in FIELDS:
        assert f.label and f.label.strip(), f.id
        assert f.type in FIELD_TYPES, f.id
        assert f.visibility in VISIBILITY_VALUES, f.id


def test_no_duplicate_field_ids():
    ids = [f.id for f in FIELDS]
    assert len(ids) == len(set(ids))


def test_visibility_default_rule():
    # §3.1: vehicles / weather / charging / depot_grid are ALL collapsed; no open fields there.
    for section_id in ("vehicles", "weather", "charging", "depot_grid"):
        for f in fields_in_section(section_id):
            assert f.visibility == "collapsed", f.id
    # only Operation and Energy prices may contain open fields.
    for f in listable_fields():
        assert f.section in MAY_BE_OPEN, f.id


def test_no_hidden_fields_leak_into_counts():
    # every field in this PR is open or collapsed; none hidden. (hidden would not be counted.)
    counts = visibility_counts()
    assert counts["hidden"] == 0
    assert counts["open"] + counts["collapsed"] == len(FIELDS)
