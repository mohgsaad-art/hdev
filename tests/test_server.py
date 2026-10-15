# STATUS: NEW (PR 2, Bob to review). Tests for the Step 2 local UI server (hdev/) via TestClient.
# all offline: fastapi.testclient.TestClient drives the ASGI app in-process, no socket, no network.
#
# what these assert:
#   - GET / serves index.html (and carries the literal `[TOOL NAME]` placeholder).
#   - GET /api/inputs is registry-derived: sections / display_names / expandable / subgroups and all
#     counts match SECTIONS and section_counts()/visibility_counts() HELPERS, never a literal (no 112).
#   - §8 method-hiding: the serialized payload contains NO `maps_to`, NO collapsed-field id/label, and
#     NO hidden-field id/label; every OPEN field's id + label IS present.
#   - mode defaults to "demo" and switches to "real" with HDEV_MODE=real.
import json

import pytest
from fastapi.testclient import TestClient

from hdev.server import create_app
from src.registry import (
    SECTIONS,
    counted_only_fields,
    listable_fields,
    section_counts,
    visibility_counts,
)
from src.registry.registry import FIELDS


@pytest.fixture()
def client():
    # default environment -> demo mode. build a fresh app per test.
    return TestClient(create_app())


def test_root_serves_index_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    # the tool name shown in the UI is the literal placeholder string (never a brand).
    assert "[TOOL NAME]" in resp.text


def test_api_inputs_ok(client):
    resp = client.get("/api/inputs")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")


def test_sections_match_registry_exactly(client):
    payload = client.get("/api/inputs").json()
    got = payload["sections"]
    # same number and order of sections as the registry.
    assert [s["id"] for s in got] == [s.id for s in SECTIONS]
    by_id = {s["id"]: s for s in got}
    for section in SECTIONS:
        s = by_id[section.id]
        assert s["display_name"] == section.display_name
        assert s["expandable"] == section.expandable
        # subgroup names and order come straight from the registry.
        assert [g["name"] for g in s["subgroups"]] == list(section.subgroups)


def test_counts_are_registry_derived(client):
    # counts compared to the HELPERS, never to a hard-coded number (the §5.4 112 was a mock-up).
    payload = client.get("/api/inputs").json()
    counts = section_counts()
    by_id = {s["id"]: s for s in payload["sections"]}
    for section in SECTIONS:
        s = by_id[section.id]
        assert s["count"] == counts[section.id]["n"]
        sec_vis = visibility_counts(section.id)
        assert s["open_count"] == sec_vis["open"]
        assert s["collapsed_count"] == sec_vis["collapsed"]
        for g in s["subgroups"]:
            assert g["count"] == counts[section.id]["subgroups"][g["name"]]


def test_total_inputs_is_registry_derived(client):
    payload = client.get("/api/inputs").json()
    totals = visibility_counts()
    # open + collapsed, hidden excluded. asserted against the helper, not a literal.
    assert payload["total_inputs"] == totals["open"] + totals["collapsed"]
    assert payload["visibility_totals"] == {"open": totals["open"], "collapsed": totals["collapsed"]}


def test_no_maps_to_leaks(client):
    # §8: maps_to must never reach the client.
    blob = json.dumps(client.get("/api/inputs").json())
    assert "maps_to" not in blob
    # and no field's actual maps_to text appears either.
    for f in FIELDS:
        assert f.maps_to not in blob, f.id


def test_no_collapsed_field_names_leak(client):
    # §8: collapsed fields are COUNTED only; their id/label must never appear in the payload.
    blob = json.dumps(client.get("/api/inputs").json())
    for f in counted_only_fields():
        assert f.id not in blob, f.id
        assert f.label not in blob, f.label


def test_no_hidden_field_names_leak(client):
    # §8: hidden fields are neither counted nor shown. (the current registry has none, but assert anyway.)
    blob = json.dumps(client.get("/api/inputs").json())
    for f in FIELDS:
        if f.visibility == "hidden":
            assert f.id not in blob, f.id
            assert f.label not in blob, f.label


def test_open_fields_present(client):
    # every open field exposes id + label in the payload.
    blob = json.dumps(client.get("/api/inputs").json())
    assert listable_fields(), "expected at least one open field in the registry"
    for f in listable_fields():
        assert f.id in blob, f.id
        assert f.label in blob, f.label


def test_mode_defaults_to_demo(monkeypatch):
    monkeypatch.delenv("HDEV_MODE", raising=False)
    client = TestClient(create_app())
    assert client.get("/api/inputs").json()["mode"] == "demo"


def test_mode_switches_to_real(monkeypatch):
    monkeypatch.setenv("HDEV_MODE", "real")
    client = TestClient(create_app())
    assert client.get("/api/inputs").json()["mode"] == "real"


def test_unknown_mode_falls_back_to_demo(monkeypatch):
    monkeypatch.setenv("HDEV_MODE", "bananas")
    client = TestClient(create_app())
    assert client.get("/api/inputs").json()["mode"] == "demo"
