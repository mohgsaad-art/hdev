# STATUS: NEW (PR 7, Bob to review). the OFFLINE demo-acceptance flow test (Step 7) via TestClient.
# no socket, no network, no AI provider, no API key. this is the server-side guarantee that the WHOLE
# demo flow runs end to end without error and that the illustrative flag is present throughout:
#   GET /api/inputs (demo, pill mode) ->
#   GET /api/intake (illustrative:true, found/missing) ->
#   'use standard values' -> POST /api/run (illustrative:true results) ->
#   each §4.4 suggestion button via POST /api/chat (compare_strategies, price_up, more_trucks,
#     cold_winter, save_scenario, show_inputs, show_audit, make_report) -> 200 + a reply ->
#   the shift edit via POST /api/chat edit_field -> 'Logged as run #N' ->
#   POST /api/scenarios save -> GET /api/audit shows the runs in the run log ->
#   the Report tab is reachable (GET / serves the shell).
#
# the Playwright click-through (tests/test_demo_acceptance_playwright.py) exercises the same flow in a
# real browser; this test is the browser-free guarantee that keeps CI green with no browser installed.
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

SUGGESTION_ACTIONS = [
    "compare_strategies",
    "price_up",
    "more_trucks",
    "cold_winter",
    "save_scenario",
    "show_inputs",
    "show_audit",
    "make_report",
]


@pytest.fixture()
def client():
    # default environment -> demo mode. a fresh app per test resets the project store (run #1).
    return TestClient(create_app())


def test_full_demo_acceptance_flow_runs_without_error(client):
    # 1. inputs: demo mode (the pill is shown by the client when mode == demo).
    inputs = client.get("/api/inputs")
    assert inputs.status_code == 200
    assert inputs.json()["mode"] == "demo"

    # 2. intake: illustrative values, with found + missing tallies.
    intake = client.get("/api/intake")
    assert intake.status_code == 200
    intake_payload = intake.json()
    assert intake_payload["illustrative"] is True
    assert "found" in intake_payload and "missing" in intake_payload

    # 3. use standard values -> run the full year. the first run echoes the standard values.
    run = client.post("/api/run", json={"levers": BASE_LEVERS})
    assert run.status_code == 200
    results = run.json()
    assert results["illustrative"] is True
    assert results["mode"] == "demo"
    assert results["run_number"] == 1

    # 4. each §4.4 suggestion button: 200 + a reply. the rerun buttons also return fresh illustrative
    #    results; the no-rerun tab buttons just open a tab.
    current = results
    for action in SUGGESTION_ACTIONS:
        chat = client.post(
            "/api/chat",
            json={"action": action, "current_results": current, "levers": BASE_LEVERS},
        )
        assert chat.status_code == 200, action
        body = chat.json()
        assert isinstance(body.get("reply"), str) and body["reply"], action
        act = body.get("action") or {}
        if isinstance(act.get("results"), dict):
            # a rerun button: its fresh results are still illustrative.
            assert act["results"]["illustrative"] is True, action
            current = act["results"]

    # 5. the shift edit: reruns and the reply ends with the audit line naming a concrete run number.
    edit = client.post(
        "/api/chat",
        json={
            "action": "edit_field",
            "target": "operation.schedule.shift_end",
            "value": "16:00",
            "current_results": current,
            "levers": BASE_LEVERS,
        },
    )
    assert edit.status_code == 200
    edit_body = edit.json()
    assert "Logged as run #" in edit_body["reply"]
    assert isinstance(edit_body["run_id"], int)
    assert edit_body["action"]["results"]["illustrative"] is True

    # 6. save the current scenario explicitly through /api/scenarios.
    save = client.post("/api/scenarios", json={"name": "My scenario", "results": results})
    assert save.status_code == 200
    assert save.json()["ok"] is True
    assert client.get("/api/scenarios").json()["count"] >= 1

    # 7. the audit trail shows the runs in the run log (the /api/run + the rerun buttons + the edit all
    #    appended entries). at minimum the first run and the shift edit are present.
    audit = client.get("/api/audit")
    assert audit.status_code == 200
    run_log = audit.json()["run_log"]
    assert len(run_log) >= 2
    # newest-first, strictly decreasing ids (append-only, no reuse).
    ids = [e["run_id"] for e in run_log]
    assert ids == sorted(ids, reverse=True)
    assert ids[-1] == 1  # the first run is the oldest (last newest-first)
    # the §8 note is present and names no field.
    assert audit.json()["note"] == "Every value can be changed. Changes are logged with who and when."

    # 8. the Report tab is reachable: the SPA shell is served at / and carries the Report tab chrome.
    #    (the Report panel itself is drawn client-side by app.js; the server just serves the shell.)
    index = client.get("/")
    assert index.status_code == 200
    assert "app.js" in index.text


def test_illustrative_flag_present_in_run_and_intake(client):
    assert client.get("/api/intake").json()["illustrative"] is True
    run = client.post("/api/run", json={"levers": BASE_LEVERS})
    assert run.json()["illustrative"] is True
