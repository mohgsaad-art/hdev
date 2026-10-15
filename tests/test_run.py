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


# a real-mode base project that satisfies the consumption entry contract (design §4B). real mode runs
# the real pipeline and returns the §3.3 shape with nulls where stages are stubbed/blocked.
REAL_BODY = {
    "project": {
        "vehicles": [{"id": "T1"}],
        "routes": [{"id": "R1"}],
        "calendar_environment": {"days": []},
        "fleet_size": 6,
        "charging_priority": "lowest_cost",
        "electricity_price": "expected",
        "weather_year": "normal",
        "ownership_years": 10,
        "shift_end": "15:00",
    }
}


def test_real_mode_returns_real_results_with_nulls(monkeypatch):
    # NEW CONTRACT (Step 9): real mode returns 200 with a §3.3-shaped results dict, mode='real', and
    # NULLS where stages are stubbed/blocked (consumption energy, charging, grid, tco metrics, co2).
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    resp = c.post("/api/run", json=REAL_BODY)
    assert resp.status_code == 200
    r = resp.json()
    assert r["mode"] == "real"
    assert r.get("illustrative") in (False, None)
    # the §3.3 landmark keys exist (same client-facing shape as demo).
    for key in ("energy", "kpis", "charging", "grid", "tco", "co2", "settings"):
        assert key in r
    # stubbed/blocked fields are null -> UI shows "Not yet available".
    assert r["energy"]["avg_day_kwh"] is None
    assert r["charging"]["soc_profile"] is None
    assert r["grid"]["load_24h_kw"] is None
    assert r["co2"]["diesel_t_per_year"] is None
    assert r["kpis"]["break_even_year"] is None
    # the TCO data model still carries the six client-facing category names, with null totals.
    assert [cat["name"] for cat in r["tco"]["categories"]] == [
        "Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate",
    ]


def test_real_mode_refuses_incomplete_contract(monkeypatch):
    # a real body that satisfies NO stage entry contract -> 400 refusal naming the missing fields.
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    resp = c.post("/api/run", json={"project": {"fleet_size": 6}})
    assert resp.status_code == 400
    r = resp.json()
    assert r["ok"] is False
    assert "vehicles" in r["error"]
    assert set(r["missing"]) == {"vehicles", "routes", "calendar_environment"}


def test_real_results_no_banned_internal_term(monkeypatch):
    # §8 guard end-to-end: no engine-internal term appears in the real results JSON string.
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    blob = c.post("/api/run", json=REAL_BODY).text
    for term in ("ASAP", "JIT", "EDF", "k_lin", "CdxA", "VECTO", "P_wheel", "P_aux", "eta_drive"):
        assert term not in blob, "banned internal term leaked: %r" % term


def test_real_mode_does_not_call_demo_engine(monkeypatch):
    # prove demo_engine.run_scenario is NOT called in real mode by making it blow up if invoked. the
    # status is now the NEW 200/real contract (not the old 404), but the never-call intent is kept.
    import demo.demo_engine as engine

    def _boom(*a, **k):
        raise AssertionError("demo_engine.run_scenario must not be called in real mode")

    monkeypatch.setenv("HDEV_MODE", "real")
    monkeypatch.setattr(engine, "run_scenario", _boom)
    c = TestClient(create_app())
    resp = c.post("/api/run", json=REAL_BODY)
    assert resp.status_code == 200
    assert resp.json()["mode"] == "real"
