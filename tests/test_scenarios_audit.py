# STATUS: NEW (PR 7, Bob to review). offline tests for the Step 7 scenarios + audit endpoints via
# TestClient. no socket, no network, no AI provider. follows tests/test_run.py / test_chat.py patterns.
#
# what these assert:
#   - POST /api/scenarios save then GET /api/scenarios lists the scenario with the §5.6 mock-up columns
#     and CLIENT-FACING names (Lowest cost / Normal year / Expected ...), never an internal lever key.
#   - POST /api/scenarios/compare of >=2 saved scenarios returns a side-by-side diff table.
#   - GET /api/audit is COUNTS-ONLY (§8): NO registry field id and NO registry field label appears
#     anywhere in the audit payload; a total row is present; the EXACT note string is present.
#   - the run log is append-only and newest-first (two runs -> newest first; run_ids monotonic).
#   - run numbers are shared/monotonic across /api/run and the chat shift-edit (one increasing sequence
#     with no gaps/reuse).
#   - real mode -> 404 available:false for both endpoints.
import json

import pytest
from fastapi.testclient import TestClient

from hdev.server import create_app
from src.registry import FIELDS

BASE_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}


@pytest.fixture()
def client():
    # default environment -> demo mode. a fresh app per test resets the project store (run #1).
    return TestClient(create_app())


def _run(client, **overrides):
    levers = dict(BASE_LEVERS)
    levers.update(overrides)
    resp = client.post("/api/run", json={"levers": levers})
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# scenarios: save -> list with the mock-up columns + client-facing names
# ---------------------------------------------------------------------------
def test_save_then_list_has_mockup_columns_and_client_facing_names(client):
    results = _run(client)
    save = client.post("/api/scenarios", json={"name": "Baseline", "results": results})
    assert save.status_code == 200
    assert save.json()["ok"] is True

    listing = client.get("/api/scenarios")
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["count"] == 1
    row = payload["scenarios"][0]

    # the §5.6 mock-up columns are all present.
    assert row["name"] == "Baseline"
    for key in ("battery_kwh", "depot_peak_kw", "tco_saving_dkk", "co2_saved_t_per_year"):
        assert key in row
    settings = row["settings"]
    for key in ("trucks", "charging_approach", "electricity_price", "weather"):
        assert key in settings

    # CLIENT-FACING names only - never an internal lever key.
    assert settings["charging_approach"] == "Lowest cost"
    assert settings["electricity_price"] == "Expected"
    assert settings["weather"] == "Normal year"
    assert settings["trucks"] == 6
    blob = json.dumps(payload)
    for leaked in ("lowest_cost", "grid_friendly", "ready_earliest", "weather_year", "charging_priority"):
        assert leaked not in blob


def test_empty_list_reports_zero_count(client):
    listing = client.get("/api/scenarios")
    assert listing.status_code == 200
    assert listing.json()["count"] == 0
    assert listing.json()["scenarios"] == []


# ---------------------------------------------------------------------------
# compare of >=2 scenarios returns a diff table
# ---------------------------------------------------------------------------
def test_compare_of_two_scenarios_returns_diff_table(client):
    base = _run(client)
    client.post("/api/scenarios", json={"name": "Base", "results": base})
    pricey = _run(client, electricity_price="high")
    client.post("/api/scenarios", json={"name": "Pricey", "results": pricey})

    compare = client.post("/api/scenarios/compare", json={})
    assert compare.status_code == 200
    payload = compare.json()
    assert payload["count"] == 2
    assert len(payload["scenarios"]) == 2

    diff = payload["diff"]
    assert isinstance(diff, list) and diff
    # every diff row carries a field label, a value per scenario and a 'same' flag.
    for row in diff:
        assert "field" in row
        assert len(row["values"]) == 2
        assert isinstance(row["same"], bool)
    # the electricity-price row differs (Expected vs High) so at least one row is NOT the same.
    price_rows = [r for r in diff if r["field"] == "Electricity price"]
    assert price_rows and price_rows[0]["same"] is False


def test_compare_specific_names(client):
    base = _run(client)
    client.post("/api/scenarios", json={"name": "Base", "results": base})
    more = _run(client, fleet_size=10)
    client.post("/api/scenarios", json={"name": "More", "results": more})

    compare = client.post("/api/scenarios/compare", json={"names": ["Base", "More"]})
    assert compare.status_code == 200
    names = [s["name"] for s in compare.json()["scenarios"]]
    assert names == ["Base", "More"]


# ---------------------------------------------------------------------------
# audit: COUNTS-ONLY (§8) - no field id/label anywhere; total + exact note present
# ---------------------------------------------------------------------------
def test_audit_is_counts_only_no_field_id_or_label(client):
    # make a run so the run log is non-empty too.
    _run(client)
    audit = client.get("/api/audit")
    assert audit.status_code == 200
    payload = audit.json()

    # the EXACT §5.6 note string.
    assert payload["note"] == "Every value can be changed. Changes are logged with who and when."

    # a total row (count) is present on the source table.
    source_table = payload["source_table"]
    assert "total" in source_table
    assert isinstance(source_table["total"], int)
    assert source_table["rows"]

    # §8: NO registry field id and NO registry field label appears ANYWHERE in the audit payload.
    blob = json.dumps(payload, ensure_ascii=False)
    for field in FIELDS:
        assert field.id not in blob, "field id leaked into audit payload: " + field.id
        label = getattr(field, "label", None)
        if label:
            assert label not in blob, "field label leaked into audit payload: " + label


def test_audit_source_rows_have_type_count_status(client):
    audit = client.get("/api/audit").json()
    for row in audit["source_table"]["rows"]:
        assert set(("source_type", "count", "status")).issubset(row.keys())
        assert isinstance(row["count"], int)


# ---------------------------------------------------------------------------
# run log: append-only + newest-first; ids monotonic
# ---------------------------------------------------------------------------
def test_run_log_is_append_only_newest_first(client):
    _run(client)  # run #1
    _run(client, fleet_size=8)  # run #2

    audit = client.get("/api/audit").json()
    run_log = audit["run_log"]
    assert len(run_log) == 2
    # newest-first: the first entry is the most recent run.
    assert run_log[0]["run_id"] == 2
    assert run_log[1]["run_id"] == 1
    # ids are strictly increasing in append order (oldest-last here).
    ids_newest_first = [e["run_id"] for e in run_log]
    assert ids_newest_first == sorted(ids_newest_first, reverse=True)


def test_run_log_entry_has_section_3_4_shape(client):
    _run(client)
    entry = client.get("/api/audit").json()["run_log"][0]
    for key in (
        "run_id",
        "timestamp",
        "settings_summary",
        "changed_from_previous",
        "key_result_summary",
        "mode",
        "engine_version",
    ):
        assert key in entry
    assert entry["engine_version"] == "demo"
    # client-facing settings labels in the summary.
    assert entry["settings_summary"]["charging_approach"] == "Lowest cost"
    assert entry["changed_from_previous"] == []  # first run has no previous


# ---------------------------------------------------------------------------
# shared monotonic run numbers across /api/run and the chat shift-edit
# ---------------------------------------------------------------------------
def test_run_numbers_shared_and_monotonic_across_run_and_shift_edit(client):
    first = _run(client)
    assert first["run_number"] == 1

    # a scenario-bar style /api/run advances the counter to 2.
    second = _run(client, fleet_size=7)
    assert second["run_number"] == 2

    # a chat shift-edit reruns through the SAME run path and takes 3.
    edit = client.post(
        "/api/chat",
        json={
            "action": "edit_field",
            "target": "operation.schedule.shift_end",
            "value": "16:00",
            "current_results": second,
        },
    )
    assert edit.status_code == 200
    assert edit.json()["run_id"] == 3
    assert "Logged as run #3" in edit.json()["reply"]

    # a second shift-edit takes 4 - one increasing sequence, no gaps, no reuse.
    edit2 = client.post(
        "/api/chat",
        json={
            "action": "edit_field",
            "target": "operation.schedule.shift_end",
            "value": "17:00",
            "current_results": edit.json()["action"]["results"],
        },
    )
    assert edit2.json()["run_id"] == 4

    # the run log now holds exactly 4 entries with ids 4,3,2,1 newest-first (no double-counting).
    run_log = client.get("/api/audit").json()["run_log"]
    assert [e["run_id"] for e in run_log] == [4, 3, 2, 1]


def test_quote_only_chat_turn_does_not_consume_a_run_number(client):
    results = _run(client)  # run #1
    # a no-rerun compare turn quotes results but must NOT advance the counter or append a log entry.
    client.post("/api/chat", json={"action": "compare_strategies", "current_results": results})
    run_log = client.get("/api/audit").json()["run_log"]
    assert [e["run_id"] for e in run_log] == [1]
    # the next genuine run is #2 (the quote-only turn did not reserve a number).
    assert _run(client, fleet_size=9)["run_number"] == 2


# ---------------------------------------------------------------------------
# save-scenario via the chat action persists
# ---------------------------------------------------------------------------
def test_chat_save_scenario_action_persists(client):
    results = _run(client)
    before = client.get("/api/scenarios").json()["count"]
    chat = client.post("/api/chat", json={"action": "save_scenario", "current_results": results})
    assert chat.status_code == 200
    assert chat.json()["action"]["saved_scenario"] is True
    after = client.get("/api/scenarios").json()["count"]
    assert after == before + 1


# ---------------------------------------------------------------------------
# real mode degradation
# ---------------------------------------------------------------------------
def test_scenarios_and_audit_degrade_in_real_mode(monkeypatch):
    monkeypatch.setenv("HDEV_MODE", "real")
    client = TestClient(create_app())
    assert client.get("/api/scenarios").status_code == 404
    assert client.get("/api/scenarios").json()["available"] is False
    assert client.get("/api/audit").status_code == 404
    assert client.get("/api/audit").json()["available"] is False
