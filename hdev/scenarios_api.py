# STATUS: NEW (PR 7, Bob to review). the pure chokepoint behind the /api/scenarios endpoints (Step 7).
#
# this is the ONE place that turns a scenarios request (mode + method + body) into a payload. it mirrors
# hdev/run_api.py and hdev/intake_api.py: a pure function of the RESOLVED mode (demo|real) returning
# (status_code, payload) so the thin server routes only wrap it in a JSONResponse. §0: all logic lives
# in Python; the browser is a dumb client that draws the saved-scenario rows / the compare table.
#
# three operations (the server routes pick the method+path and pass it in):
#   - method 'save'    (POST /api/scenarios): snapshot the CURRENT run under a given name. the body may
#                       carry a 'results' dict (the §3.3 payload to snapshot) and/or a 'run_id' (a
#                       numeric run number already in the run log); if neither is given, a default
#                       scenario is run so a save always has a source. the stored scenario holds the
#                       NAME + the client-facing settings_summary + key_result_summary (§8-safe).
#   - method 'list'    (GET /api/scenarios): the saved-scenarios table with the §5.6 mock-up columns -
#                       name, settings {trucks, charging approach, electricity price, weather}, battery,
#                       depot peak, TCO saving, CO2 saved - all client-facing names/plain words pulled
#                       from each saved scenario's summary.
#   - method 'compare' (POST /api/scenarios/compare): given run_ids/scenario names, return the §4.2
#                       compare_runs diff-table: the chosen scenarios side by side + a per-row diff.
#
# §8: scenarios use CLIENT-FACING lever names + plain words only (the summaries come from
# audit.run_log, which already enforces this). NEVER an internal lever key.
#
# real mode: {available:false, mode, reason} with 404, exactly like run_api/intake_api (running and the
# scenarios that depend on it are demo-only in this build; the real pipeline is Step 9/10).
from typing import Any, Dict, List, Mapping, Optional, Tuple

import audit.run_log as run_log_mod
from hdev.project_store import get_store

# the demo default levers for a save/compare when the caller supplies no results and no run_id (mirrors
# chat_api's defaults: the 6-truck municipal refuse sample case).
_DEFAULT_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}

_NOT_AVAILABLE_REAL = {
    "available": False,
    "reason": "Scenarios are only available in demo mode in this build.",
}


def _real_not_available(mode: str) -> Tuple[int, Dict[str, Any]]:
    payload = dict(_NOT_AVAILABLE_REAL)
    payload["mode"] = mode
    return 404, payload


def _default_results() -> Dict[str, Any]:
    # run the default demo scenario (quote-only; does NOT consume a run number) so a save/compare
    # always has a results source even when the caller sends neither results nor a run_id.
    from hdev.run_api import build_run_payload

    status, payload = build_run_payload("demo", {"levers": dict(_DEFAULT_LEVERS)}, log_run=False)
    return payload if status == 200 else {}


def _scenario_from_results(name: str, results: Mapping[str, Any], run_id: Any) -> Dict[str, Any]:
    # build the §8-safe saved-scenario record from a §3.3 results dict: name + client-facing
    # settings_summary + key_result_summary (both from audit.run_log). the run_id (numeric run number)
    # is kept so the scenario can be matched back to its run-log entry.
    return {
        "name": name,
        "run_id": run_id,
        "settings_summary": run_log_mod.settings_summary(results),
        "key_result_summary": run_log_mod.key_result_summary(results),
    }


def _scenario_row(scenario: Mapping[str, Any]) -> Dict[str, Any]:
    # one row of the §5.6 Scenarios table: name + the four settings columns + the four key-result
    # columns, all client-facing. pulled straight from the saved scenario's summaries.
    settings = scenario.get("settings_summary") or {}
    kpis = scenario.get("key_result_summary") or {}
    return {
        "name": scenario.get("name"),
        "run_id": scenario.get("run_id"),
        "settings": {
            "trucks": settings.get("trucks"),
            "charging_approach": settings.get("charging_approach"),
            "electricity_price": settings.get("electricity_price"),
            "weather": settings.get("weather"),
        },
        "battery_kwh": kpis.get("battery_kwh"),
        "depot_peak_kw": kpis.get("depot_peak_kw"),
        "tco_saving_dkk": kpis.get("tco_saving_dkk"),
        "co2_saved_t_per_year": kpis.get("co2_saved_t_per_year"),
    }


# ---------------------------------------------------------------------------
# the three operations
# ---------------------------------------------------------------------------
def _save(body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    name = body.get("name")
    if not isinstance(name, str) or not name.strip():
        return 400, {"ok": False, "error": "A scenario needs a name."}
    name = name.strip()

    store = get_store()

    # resolve the results to snapshot: an explicit 'results' body, else the run-log entry for a given
    # 'run_id', else a freshly run default scenario.
    results = body.get("results")
    run_id = body.get("run_id")
    if isinstance(results, Mapping) and results.get("kpis"):
        snapshot = dict(results)
        run_id = snapshot.get("run_number", run_id)
        scenario = _scenario_from_results(name, snapshot, run_id)
    elif run_id is not None and store.get_run(run_id) is not None:
        # reuse the run-log entry's already-§8-safe summaries directly.
        entry = store.get_run(run_id)
        scenario = {
            "name": name,
            "run_id": run_id,
            "settings_summary": entry.get("settings_summary", {}),
            "key_result_summary": entry.get("key_result_summary", {}),
        }
    else:
        snapshot = _default_results()
        scenario = _scenario_from_results(name, snapshot, snapshot.get("run_number"))

    stored = store.save_scenario(scenario)
    return 200, {"ok": True, "scenario": _scenario_row(stored)}


def _list() -> Tuple[int, Dict[str, Any]]:
    rows = [_scenario_row(s) for s in get_store().list_scenarios()]
    return 200, {"scenarios": rows, "count": len(rows)}


def _compare(body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # §4.2 compare: given scenario NAMES or numeric run_ids, line the chosen saved scenarios up side by
    # side and emit a per-row diff (the §5.6 columns that differ across the chosen scenarios). when no
    # ids/names are given, compare ALL saved scenarios.
    store = get_store()
    saved = store.list_scenarios()

    wanted_names = body.get("names")
    wanted_ids = body.get("run_ids")

    chosen: List[Mapping[str, Any]] = []
    if isinstance(wanted_names, list) and wanted_names:
        by_name = {s.get("name"): s for s in saved}
        chosen = [by_name[n] for n in wanted_names if n in by_name]
    elif isinstance(wanted_ids, list) and wanted_ids:
        by_id = {s.get("run_id"): s for s in saved}
        chosen = [by_id[i] for i in wanted_ids if i in by_id]
    else:
        chosen = list(saved)

    columns = [_scenario_row(s) for s in chosen]

    # per-row diff: for each §5.6 field, the value in each chosen scenario and whether they all agree.
    def _field_values(getter):
        return [getter(c) for c in columns]

    def _row(label, values):
        return {"field": label, "values": values, "same": len(set(_hashable(v) for v in values)) <= 1}

    diff: List[Dict[str, Any]] = [
        _row("Trucks", _field_values(lambda c: c["settings"]["trucks"])),
        _row("Charging approach", _field_values(lambda c: c["settings"]["charging_approach"])),
        _row("Electricity price", _field_values(lambda c: c["settings"]["electricity_price"])),
        _row("Weather", _field_values(lambda c: c["settings"]["weather"])),
        _row("Battery (kWh)", _field_values(lambda c: c["battery_kwh"])),
        _row("Depot peak (kW)", _field_values(lambda c: c["depot_peak_kw"])),
        _row("TCO saving (DKK)", _field_values(lambda c: c["tco_saving_dkk"])),
        _row("CO\u2082 saved (t/year)", _field_values(lambda c: c["co2_saved_t_per_year"])),
    ]

    return 200, {"scenarios": columns, "diff": diff, "count": len(columns)}


def _hashable(value: Any) -> Any:
    # make a value hashable for the "all the same?" set check (dict/list -> a stable string form).
    if isinstance(value, (dict, list)):
        import json

        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return value


# ---------------------------------------------------------------------------
# main chokepoint
# ---------------------------------------------------------------------------
def build_scenarios_payload(
    mode: str,
    method: str,
    body: Optional[Mapping[str, Any]] = None,
) -> Tuple[int, Dict[str, Any]]:
    # pure chokepoint. `mode` is already resolved (demo|real); `method` is 'save' | 'list' | 'compare'.
    if mode != "demo":
        return _real_not_available(mode)

    body = body or {}
    if method == "save":
        return _save(body)
    if method == "list":
        return _list()
    if method == "compare":
        return _compare(body)
    return 400, {"ok": False, "error": f"Unknown scenarios operation: {method!r}"}
