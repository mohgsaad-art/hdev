# STATUS: NEW (PR 3, Bob to review). offline tests for the Step 3 demo intake flow (/api/intake).
# all via fastapi.testclient.TestClient - no socket, no network, no AI provider.
#
# what these assert (all registry/fixture-derived, NEVER literals - no hard-coded missing count):
#   - GET /api/intake in demo mode returns 200 and the documented shape.
#   - every fixture field id exists in the registry and every source is valid (round-trip).
#   - from_data + standard + missing tallies are registry/fixture-derived and sum to total_inputs,
#     and total_inputs equals /api/inputs total_inputs (open+collapsed).
#   - §8: the serialized payload leaks NO maps_to, NO collapsed/hidden field id/label, NO collapsed
#     value; OPEN field ids + labels DO appear.
#   - the `illustrative` flag is present.
#   - the N/M/K numbers in the found-line assistant string match the computed tallies.
#   - real mode does not expose the demo fixture (404 / available:false).
import json

import pytest
from fastapi.testclient import TestClient

from hdev.intake_api import OPENING_LINE, _load_fixture, build_intake_payload
from hdev.server import create_app
from src.registry import (
    fields_in_section,
    get_field,
    is_valid_source,
    listable_fields,
    visibility_counts,
)
from src.registry.registry import FIELDS, SECTIONS


@pytest.fixture()
def client():
    # default environment -> demo mode. fresh app per test.
    return TestClient(create_app())


# ---- helpers: recompute the expected tallies from the registry + fixture (no literals) ----

def _expected_tallies():
    # classify every open+collapsed registry field by the fixture's source and tally the three classes.
    # this mirrors the endpoint but is computed independently in the test, so the test is not asserting
    # a literal missing count - it derives it from the registry + fixture.
    fixture = _load_fixture()
    slots = fixture["fields"]
    from_data = standard = missing = 0
    for f in FIELDS:
        if f.visibility == "hidden":
            continue
        slot = slots.get(f.id)
        src = slot["source"] if slot else None
        if src is None or src == "missing":
            missing += 1
        elif src == "standard":
            standard += 1
        elif src == "message" or src.startswith("file:"):
            from_data += 1
        else:
            missing += 1
    return {"from_data": from_data, "standard": standard, "missing": missing}


def test_intake_ok_and_shape(client):
    resp = client.get("/api/intake")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    p = resp.json()
    assert p["available"] is True
    assert p["mode"] == "demo"
    # documented top-level keys present.
    for key in (
        "illustrative",
        "note",
        "tool_name",
        "total_inputs",
        "found",
        "missing",
        "totals",
        "assistant",
        "sections",
        "sample_files",
        "message_text",
    ):
        assert key in p, key
    # sections are in registry order.
    assert [s["id"] for s in p["sections"]] == [s.id for s in SECTIONS]


def test_fixture_round_trips_to_registry_and_valid_sources():
    # every fixture field id is a real registry id and every source is valid (is_valid_source).
    fixture = _load_fixture()
    assert fixture.get("illustrative") is True
    for fid, slot in fixture["fields"].items():
        assert get_field(fid) is not None, fid
        assert is_valid_source(slot["source"]), slot["source"]


def test_tallies_are_registry_derived_and_sum_to_total(client):
    # the test does NOT hard-code the missing count: it recomputes all three tallies from the registry
    # + fixture and compares to the endpoint, then checks they sum to total_inputs.
    expected = _expected_tallies()
    p = client.get("/api/intake").json()
    assert p["totals"]["from_data"] == expected["from_data"]
    assert p["totals"]["standard"] == expected["standard"]
    assert p["totals"]["missing"] == expected["missing"]
    # explicitly: the missing count is derived, never a literal in this test.
    assert p["missing"] == expected["missing"]
    assert p["found"] == expected["from_data"] + expected["standard"]
    assert (
        p["totals"]["from_data"] + p["totals"]["standard"] + p["totals"]["missing"]
        == p["total_inputs"]
    )


def test_total_inputs_matches_api_inputs(client):
    # total_inputs is the registry open+collapsed total and equals /api/inputs total_inputs.
    totals = visibility_counts()
    expected_total = totals["open"] + totals["collapsed"]
    intake = client.get("/api/intake").json()
    inputs = client.get("/api/inputs").json()
    assert intake["total_inputs"] == expected_total
    assert intake["total_inputs"] == inputs["total_inputs"]


def test_per_section_tallies_sum_to_section_total(client):
    # each section's from_data+standard+missing equals its open+collapsed field count (registry-derived).
    p = client.get("/api/intake").json()
    by_id = {s["id"]: s for s in p["sections"]}
    for section in SECTIONS:
        s = by_id[section.id]
        vis = visibility_counts(section.id)
        assert s["total"] == vis["open"] + vis["collapsed"]
        assert s["from_data"] + s["standard"] + s["missing"] == s["total"]


def test_no_maps_to_leaks(client):
    blob = json.dumps(client.get("/api/intake").json())
    assert "maps_to" not in blob
    for f in FIELDS:
        assert f.maps_to not in blob, f.id


def test_no_collapsed_or_hidden_names_or_values_leak(client):
    # §8: collapsed fields are COUNTED only; their id/label/value must never appear. same for hidden.
    p = client.get("/api/intake").json()
    blob = json.dumps(p)
    fixture = _load_fixture()
    slots = fixture["fields"]
    for f in FIELDS:
        if f.visibility in ("collapsed", "hidden"):
            assert f.id not in blob, f.id
            assert f.label not in blob, f.label
            # the fixture value of a collapsed field must not leak either.
            slot = slots.get(f.id)
            if slot is not None and slot.get("value") is not None:
                assert json.dumps(slot["value"]) not in blob, f.id


def test_open_field_ids_and_labels_present(client):
    # every OPEN field exposes id + label in the payload.
    blob = json.dumps(client.get("/api/intake").json())
    assert listable_fields()
    for f in listable_fields():
        assert f.id in blob, f.id
        assert f.label in blob, f.label


def test_illustrative_flag_present(client):
    p = client.get("/api/intake").json()
    assert p["illustrative"] is True
    # every open field is flagged illustrative too.
    for s in p["sections"]:
        for field in s["fields"]:
            assert field["illustrative"] is True


def test_assistant_strings_numbers_match_tallies(client):
    # the N/M/K in the found-line must equal the computed found / total / missing (server numbers).
    p = client.get("/api/intake").json()
    found = p["found"]
    total = p["total_inputs"]
    missing = p["missing"]
    expected_line = f"I found {found} of {total} inputs… {missing} are missing"
    assert p["assistant"]["found_line"] == expected_line
    # the opening line is the EXACT §4 string.
    assert p["assistant"]["opening"] == OPENING_LINE
    assert p["assistant"]["reading"] == "Reading…"


def test_real_mode_does_not_expose_fixture(monkeypatch):
    # §7/§8: in real mode the demo sample case must not leak. endpoint returns 404 + available:false.
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    resp = c.get("/api/intake")
    assert resp.status_code == 404
    p = resp.json()
    assert p["available"] is False
    blob = json.dumps(p)
    # none of the fixture's open field ids/labels leak in real mode.
    for f in listable_fields():
        assert f.id not in blob, f.id


def test_build_intake_payload_real_mode_pure():
    # the pure chokepoint returns an unavailable payload in real mode without reading the fixture.
    p = build_intake_payload("real")
    assert p["available"] is False
    assert "sections" not in p


def test_section_open_fields_only_contain_open_ids(client):
    # defensive: the `fields` list of each section must contain ONLY open field ids of that section.
    p = client.get("/api/intake").json()
    by_id = {s["id"]: s for s in p["sections"]}
    for section in SECTIONS:
        open_ids = {f.id for f in fields_in_section(section.id) if f.visibility == "open"}
        got_ids = {f["id"] for f in by_id[section.id]["fields"]}
        assert got_ids == open_ids, section.id
