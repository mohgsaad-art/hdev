# STATUS: NEW (PR 1). Tests for the input registry structure (user §3.1 / §5.4).
from src.registry import (
    SECTIONS,
    FIELDS,
    SUBGROUPS,
    FIELD_TYPES,
    VISIBILITY_VALUES,
    fields_in_section,
    fields_in_subgroup,
    listable_fields,
    visibility_counts,
)
from src.registry.registry import section_counts

# the §5.4 table, verbatim, as the single expectation these tests check against.
EXPECTED = {
    "operation": {"schedule": 5, "routes": 5},
    "vehicles": {"body": 6, "drivetrain": 5, "battery": 4, "wheels": 3, "equipment": 6},
    "depot_grid": {"site": 4, "connection": 5, "building_load": 4, "chargers_on_site": 5},
    "charging": {"strategy": 3, "charger_types": 4, "time_windows": 4},
    "energy_prices": {"electricity": 5, "grid_tariffs": 3, "diesel": 2, "trends": 2},
    "weather": {"location": 2, "daily_records": 4, "seasons": 3},
    "costs_finance": {"purchase": 5, "leasing": 4, "maintenance": 5, "finance": 6},
    "policy_taxes": {"taxes": 4, "subsidies": 4},
}

# sections that may hold "open" fields per §3.1 (Operation and Energy prices only).
MAY_BE_OPEN = {"operation", "energy_prices"}


def test_eight_sections():
    assert len(SECTIONS) == 8
    assert {s.id for s in SECTIONS} == set(EXPECTED)


def test_exactly_112_fields():
    assert len(FIELDS) == 112
    assert sum(sum(sg.values()) for sg in EXPECTED.values()) == 112


def test_section_and_subgroup_counts_match_5_4():
    for section_id, subgroups in EXPECTED.items():
        assert len(fields_in_section(section_id)) == sum(subgroups.values())
        for subgroup, count in subgroups.items():
            assert len(fields_in_subgroup(section_id, subgroup)) == count, (section_id, subgroup)


def test_section_counts_helper_agrees():
    counts = section_counts()
    for section_id, subgroups in EXPECTED.items():
        total = sum(subgroups.values())
        assert counts[section_id]["n"] == total
        assert counts[section_id]["total"] == total


def test_subgroup_names_match_5_4():
    for section_id, subgroups in EXPECTED.items():
        assert set(SUBGROUPS[section_id].keys()) == set(subgroups)


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
    # all 112 fields are open or collapsed in this PR; none hidden. (hidden would not be counted.)
    counts = visibility_counts()
    assert counts["hidden"] == 0
    assert counts["open"] + counts["collapsed"] == 112
