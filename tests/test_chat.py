# STATUS: NEW (PR 6, Bob to review). offline tests for POST /api/chat (Step 6 demo assistant) via
# TestClient. no socket, no network, no AI provider. follows tests/test_run.py patterns.
#
# what these assert:
#   - the typed-question keyword router sends each keyword to the right behaviour (compare -> Charging,
#     expensive -> price/tco, add a truck -> more_trucks/gridflex, cold winter -> energy); an unmatched
#     message returns EXACTLY the fallback line with no action; a how/why/method message deflects.
#   - each suggestion-button action changes the right lever and reruns (or opens the right tab with no
#     lever change for the no-rerun buttons).
#   - the shift-end field edit reruns, the reply NAMES the change and ends with the audit line with a
#     concrete N, and run_id is returned.
#   - real mode -> 404 available:false, and demo mode calls NO AI provider / hits no network.
import json

import pytest
from fastapi.testclient import TestClient

from hdev.server import create_app

BASE_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}


@pytest.fixture()
def client():
    # default environment -> demo mode. fresh app per test.
    return TestClient(create_app())


def _run(client):
    # a fresh base results dict to pass as current_results on no-rerun turns.
    resp = client.post("/api/run", json={"levers": BASE_LEVERS})
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# (a) typed-question keyword router
# ---------------------------------------------------------------------------
def test_keyword_compare_opens_charging_no_rerun(client):
    results = _run(client)
    resp = client.post("/api/chat", json={"message": "can you compare the options?", "current_results": results})
    assert resp.status_code == 200
    p = resp.json()
    assert p["action"]["open_tab"] == "charging"
    assert "lever" not in p["action"]  # no rerun -> no lever change
    assert "Lowest cost" in p["reply"]
    assert "Grid-friendly" in p["reply"]
    assert "Ready earliest" in p["reply"]


def test_keyword_expensive_sets_high_price_and_opens_tco(client):
    resp = client.post("/api/chat", json={"message": "will it be more expensive?", "levers": BASE_LEVERS})
    assert resp.status_code == 200
    p = resp.json()
    assert p["action"]["open_tab"] == "tco"
    assert p["action"]["lever"] == {"electricity_price": "high"}
    assert p["action"]["results"]["settings"]["electricity_price"] == "high"


def test_keyword_add_truck_bumps_fleet_and_opens_gridflex(client):
    resp = client.post("/api/chat", json={"message": "what if I add a truck?", "levers": BASE_LEVERS})
    assert resp.status_code == 200
    p = resp.json()
    assert p["action"]["open_tab"] == "gridflex"
    assert p["action"]["results"]["settings"]["fleet_size"] == BASE_LEVERS["fleet_size"] + 4
    assert p["action"]["lever"] == {"fleet_size": BASE_LEVERS["fleet_size"] + 4}


def test_keyword_cold_winter_sets_weather_and_opens_energy(client):
    resp = client.post("/api/chat", json={"message": "how about a cold winter?", "levers": BASE_LEVERS})
    # NOTE: "how" would normally deflect, but the message also contains "cold"/"winter"; method keywords
    # are checked FIRST, so this message deflects. use a message with no method word for the winter path.
    assert resp.status_code == 200
    assert resp.json()["reply"].startswith("That's the engineering side.")


def test_keyword_cold_winter_pure(client):
    resp = client.post("/api/chat", json={"message": "a cold winter year", "levers": BASE_LEVERS})
    assert resp.status_code == 200
    p = resp.json()
    assert p["action"]["open_tab"] == "energy"
    assert p["action"]["results"]["settings"]["weather_year"] == "cold_winter"
    assert p["action"]["lever"] == {"weather_year": "cold_winter"}


def test_unmatched_message_returns_exact_fallback_no_action(client):
    resp = client.post("/api/chat", json={"message": "tell me a joke", "levers": BASE_LEVERS})
    assert resp.status_code == 200
    p = resp.json()
    assert p["reply"] == (
        "In this demo I can answer the suggested questions below. "
        "In the full tool you can ask anything about your fleet."
    )
    assert "action" not in p


def test_method_question_deflects(client):
    for msg in ("how is the battery sized?", "why that number?", "which parameter drives this?"):
        resp = client.post("/api/chat", json={"message": msg, "levers": BASE_LEVERS})
        assert resp.status_code == 200
        p = resp.json()
        assert p["reply"] == "That's the engineering side. The results and every input source are in the report."
        assert "action" not in p


# ---------------------------------------------------------------------------
# (b) suggestion-button actions
# ---------------------------------------------------------------------------
def test_button_compare_strategies_no_lever_change(client):
    results = _run(client)
    resp = client.post("/api/chat", json={"action": "compare_strategies", "current_results": results})
    p = resp.json()
    assert p["action"]["open_tab"] == "charging"
    assert "lever" not in p["action"]
    assert "Lowest cost" in p["reply"]


def test_button_price_up_reruns_high(client):
    resp = client.post("/api/chat", json={"action": "price_up", "levers": BASE_LEVERS})
    p = resp.json()
    assert p["action"]["results"]["settings"]["electricity_price"] == "high"
    assert p["action"]["open_tab"] == "tco"


def test_button_more_trucks_reruns_plus_four(client):
    resp = client.post("/api/chat", json={"action": "more_trucks", "levers": BASE_LEVERS})
    p = resp.json()
    assert p["action"]["results"]["settings"]["fleet_size"] == BASE_LEVERS["fleet_size"] + 4
    assert p["action"]["open_tab"] == "gridflex"


def test_button_cold_winter_reruns(client):
    resp = client.post("/api/chat", json={"action": "cold_winter", "levers": BASE_LEVERS})
    p = resp.json()
    assert p["action"]["results"]["settings"]["weather_year"] == "cold_winter"
    assert p["action"]["open_tab"] == "energy"


def test_no_rerun_tab_buttons(client):
    results = _run(client)
    cases = {
        "save_scenario": {"open_tab": "scenarios"},
        "show_inputs": {"open_tab": "inputs", "expand_section": "operation"},
        "show_audit": {"open_tab": "audit"},
        "make_report": {"open_tab": "report"},
    }
    for action, expected in cases.items():
        resp = client.post("/api/chat", json={"action": action, "current_results": results})
        assert resp.status_code == 200
        p = resp.json()
        for k, v in expected.items():
            assert p["action"][k] == v
        assert "lever" not in p["action"]
        assert "results" not in p["action"]


# ---------------------------------------------------------------------------
# (c) shift-end field edit
# ---------------------------------------------------------------------------
def test_shift_end_edit_reruns_and_logs_run_number(client):
    resp = client.post(
        "/api/chat",
        json={
            "action": "edit_field",
            "target": "operation.schedule.shift_end",
            "value": "17:00",
            "levers": BASE_LEVERS,
        },
    )
    assert resp.status_code == 200
    p = resp.json()
    # names the change (plain field label + new value).
    assert "Shift end" in p["reply"]
    assert "17:00" in p["reply"]
    # ends with the exact audit line, with a concrete integer N.
    assert isinstance(p["run_id"], int)
    assert p["reply"].rstrip().endswith(f"Logged as run #{p['run_id']} in the audit trail.")
    assert p["action"]["results"]["settings"]["shift_end"] == "17:00"
    assert p["action"]["run_id"] == p["run_id"]


def test_shift_end_edit_run_number_increments(client):
    body = {"action": "edit_field", "target": "operation.schedule.shift_end", "value": "16:00", "levers": BASE_LEVERS}
    first = client.post("/api/chat", json=body).json()["run_id"]
    second = client.post("/api/chat", json=body).json()["run_id"]
    assert second == first + 1


def test_edit_field_wrong_target_rejected(client):
    resp = client.post(
        "/api/chat",
        json={"action": "edit_field", "target": "fleet_size", "value": 9, "levers": BASE_LEVERS},
    )
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


# ---------------------------------------------------------------------------
# (d) real mode: 404 available:false and NO AI provider / demo engine involvement
# ---------------------------------------------------------------------------
def test_real_mode_not_available(monkeypatch):
    monkeypatch.setenv("HDEV_MODE", "real")
    c = TestClient(create_app())
    resp = c.post("/api/chat", json={"message": "hi"})
    assert resp.status_code == 404
    p = resp.json()
    assert p["available"] is False
    assert p["mode"] == "real"
    assert "reply" not in p


def test_real_mode_does_not_call_demo_engine(monkeypatch):
    # prove demo_engine.run_scenario is NOT called in real mode (the assistant never reruns there).
    import demo.demo_engine as engine

    def _boom(*a, **k):
        raise AssertionError("demo_engine.run_scenario must not be called in real mode")

    monkeypatch.setenv("HDEV_MODE", "real")
    monkeypatch.setattr(engine, "run_scenario", _boom)
    c = TestClient(create_app())
    resp = c.post("/api/chat", json={"action": "price_up", "levers": BASE_LEVERS})
    assert resp.status_code == 404
    assert resp.json()["available"] is False


def test_chat_api_imports_no_ai_provider():
    # §0 / HARD CONSTRAINT: demo mode never calls any AI provider and chat_api imports none. there is
    # no ai/ package in Step 6; assert the module source does not import one.
    import inspect

    import hdev.chat_api as chat_api

    src = inspect.getsource(chat_api)
    for forbidden in ("import ai", "from ai", "openai", "anthropic", "gemini", "ollama", "requests", "httpx", "urllib.request"):
        assert forbidden not in src, f"chat_api must not reference {forbidden!r}"


def test_number_check_blocks_drift_at_endpoint(monkeypatch):
    # if a template ever drifted and produced a number not in results, the chokepoint must replace the
    # reply with the safe fallback. force a drifting template and confirm the endpoint returns the
    # fallback, not the drift.
    import hdev.chat_api as chat_api

    monkeypatch.setattr(
        chat_api.explain, "compare_strategies_reply", lambda results: "The answer is 424242 kW."
    )
    c = TestClient(create_app())
    results = c.post("/api/run", json={"levers": BASE_LEVERS}).json()
    resp = c.post("/api/chat", json={"action": "compare_strategies", "current_results": results})
    assert resp.status_code == 200
    reply = resp.json()["reply"]
    assert "424242" not in reply
    assert reply == (
        "In this demo I can answer the suggested questions below. "
        "In the full tool you can ask anything about your fleet."
    )
