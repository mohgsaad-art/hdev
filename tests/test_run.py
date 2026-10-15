# STATUS: NEW (PR 4, Bob to review). offline tests for POST /api/run (Step 4) via TestClient.
# no socket, no network, no AI provider. follows tests/test_server.py / tests/test_intake.py patterns.
#
# what these assert:
#   - demo mode: a valid levers body returns 200 and a §3.3 results JSON with illustrative:true,
#     mode:"demo".
#   - demo mode: an out-of-range or unknown lever returns a 4xx and NO results (the validator rejection
#     path, end-to-end).
#   - real mode: returns the not-yet-available payload (available:false) and does NOT call demo_engine
#     (no results fields present).
import json

import pytest
from fastapi.testclient import TestClient

from hdev.server import create_app

VALID_BODY = {
    "levers": {
        "fleet_size": 6,
        "charging_priority": "lowest_cost",
        "electricity_price": "expected",
        "weather_year": "normal",
        "ownership_years": 10,
    }
}


@pytest.fixture()
def client():
    # default environment -> demo mode. fresh app per test.
    return TestClient(create_app())


def test_demo_run_returns_results(client):
    resp = client.post("/api/run", json=VALID_BODY)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    r = resp.json()
    assert r["mode"] == "demo"
    assert r["illustrative"] is True
    # a couple of §3.3 landmarks so this is a real results JSON, not an error payload.
    assert len(r["energy"]["monthly_avg_kwh"]) == 12
    assert [c["name"] for c in r["tco"]["categories"]] == [
        "Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate",
    ]


def test_demo_run_exposes_working_days_and_truck_days_simulated(client):
    # additive §3.3 fields (FEAT-002): the run screen reads the real truck-days count from the server
    # rather than hard-coding 250. VALID_BODY uses fleet_size 6.
    r = client.post("/api/run", json=VALID_BODY).json()
    fleet_size = VALID_BODY["levers"]["fleet_size"]
    assert r["working_days"] == 250
    assert r["truck_days_simulated"] == fleet_size * r["working_days"]


def test_demo_run_accepts_levers_at_top_level(client):
    # convenience: the demo endpoint also accepts the levers at the top level of the body.
    resp = client.post("/api/run", json=VALID_BODY["levers"])
    assert resp.status_code == 200
    assert resp.json()["mode"] == "demo"


def test_demo_run_priority_names_are_client_facing(client):
    r = client.post("/api/run", json=VALID_BODY).json()
    blob = json.dumps(r)
    # §8: the internal keys must not leak as priority values.
    for s in r["charging"]["strategies"]:
        assert s["priority"] in {"lowest_cost", "grid_friendly", "ready_earliest"}
    assert r["settings"]["charging_priority"] in {"lowest_cost", "grid_friendly", "ready_earliest"}


def test_out_of_range_fleet_size_rejected(client):
    body = {"levers": dict(VALID_BODY["levers"], fleet_size=0)}
    resp = client.post("/api/run", json=body)
    assert resp.status_code == 400
    r = resp.json()
    # no results fields: the validator rejection path returns an error, not a scenario.
    assert "energy" not in r
    assert "kpis" not in r
    assert r.get("ok") is False
    assert r.get("error")


def test_unknown_lever_rejected(client):
    body = {"levers": dict(VALID_BODY["levers"], not_a_real_lever="whatever")}
    resp = client.post("/api/run", json=body)
    assert resp.status_code == 400
    r = resp.json()
    assert "energy" not in r
    assert r.get("ok") is False


def test_bad_enum_value_rejected(client):
    body = {"levers": dict(VALID_BODY["levers"], electricity_price="free")}
    resp = client.post("/api/run", json=body)
    assert resp.status_code == 400
    assert "kpis" not in resp.json()


def test_real_mode_not_available_and_no_results(monkeypatch):
    # real mode: the demo engine must not run. endpoint returns 404 + available:false, no results.
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    resp = c.post("/api/run", json=VALID_BODY)
    assert resp.status_code == 404
    r = resp.json()
    assert r["available"] is False
    assert r["mode"] == "real"
    # no results fields leaked.
    for key in ("energy", "kpis", "tco", "charging", "grid", "co2"):
        assert key not in r


def test_real_mode_does_not_call_demo_engine(monkeypatch):
    # prove demo_engine.run_scenario is NOT called in real mode by making it blow up if invoked.
    import demo.demo_engine as engine

    def _boom(*a, **k):
        raise AssertionError("demo_engine.run_scenario must not be called in real mode")

    monkeypatch.setenv("HDEV_MODE", "real")
    monkeypatch.setattr(engine, "run_scenario", _boom)
    c = TestClient(create_app())
    resp = c.post("/api/run", json=VALID_BODY)
    assert resp.status_code == 404
    assert resp.json()["available"] is False
