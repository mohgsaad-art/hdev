# STATUS: NEW (PR 7, Bob to review). the §3.4 RUN-LOG entry builder + thin listing helpers (Step 7).
#
# audit/ owns the §8-SAFE SHAPE of a run-log entry; hdev.project_store owns PERSISTENCE. this module
# builds one §3.4 entry from a §3.3 results dict and delegates append/list to the store.
#
# §3.4 entry shape (binding):
#   {run_id, timestamp, settings_summary, changed_from_previous:[...], key_result_summary, mode,
#    engine_version}
#
# §8 method-hiding: settings_summary, changed_from_previous and key_result_summary use CLIENT-FACING
# names and plain words ONLY (trucks, charging approach label, electricity price, weather, years kept,
# shift end; battery, depot peak, TCO saving, CO2 saved). NO internal lever key (cost/grid/early) and
# NO physics/parameter/formula name ever appears here. engine_version is the DEMO CONSTANT 'demo' (a
# stub; the real engine version lands in Step 9).
#
# purity: build_run_entry is a pure function of (run_id, results, previous_entry). no network, no AI
# provider. append/list helpers touch only the local project store (a JSON file).
from typing import Any, Dict, List, Mapping, Optional

from hdev import project_store

# engine_version is a stub constant for the demo. the real engine (§6/Step 9) will supply a real
# version string; until then every demo run is logged as 'demo'.
ENGINE_VERSION_DEMO = "demo"

# the three CLIENT-FACING charging-approach labels (§8). the results settings already carry the
# client-facing key (lowest_cost/grid_friendly/ready_earliest); this maps it to the human label.
_PRIORITY_LABEL = {
    "lowest_cost": "Lowest cost",
    "grid_friendly": "Grid-friendly",
    "ready_earliest": "Ready earliest",
}

# plain-word labels for the electricity-price and weather enums.
_PRICE_LABEL = {"low": "Low", "expected": "Expected", "high": "High"}
_WEATHER_LABEL = {"normal": "Normal year", "cold_winter": "Cold winter"}


def _priority_label(value: Any) -> str:
    return _PRIORITY_LABEL.get(value, "the chosen approach")


def _price_label(value: Any) -> str:
    return _PRICE_LABEL.get(value, str(value))


def _weather_label(value: Any) -> str:
    return _WEATHER_LABEL.get(value, str(value))


def settings_summary(results: Mapping[str, Any]) -> Dict[str, Any]:
    # a plain-word, client-facing snapshot of the run's settings. keys are human-readable labels; values
    # are the figures/labels a client would recognise. NEVER an internal lever key.
    settings = results.get("settings")
    settings = settings if isinstance(settings, Mapping) else {}
    return {
        "trucks": settings.get("fleet_size"),
        "charging_approach": _priority_label(settings.get("charging_priority")),
        "electricity_price": _price_label(settings.get("electricity_price")),
        "weather": _weather_label(settings.get("weather_year")),
        "years_kept": settings.get("ownership_years"),
        "shift_end": settings.get("shift_end"),
    }


def key_result_summary(results: Mapping[str, Any]) -> Dict[str, Any]:
    # the four §5.6 scenario "key results" KPIs in plain words: battery, depot peak, TCO saving, CO2
    # saved. every number is read straight from the results KPIs (no maths here).
    kpis = results.get("kpis")
    kpis = kpis if isinstance(kpis, Mapping) else {}
    return {
        "battery_kwh": kpis.get("battery_kwh"),
        "depot_peak_kw": kpis.get("grid_peak_kw"),
        "tco_saving_dkk": kpis.get("tco_diff_dkk"),
        "co2_saved_t_per_year": kpis.get("co2_saved_t_per_year"),
    }


# the plain-word labels used for the changed_from_previous diff (one per settings_summary key).
_CHANGE_LABEL = {
    "trucks": "Trucks",
    "charging_approach": "Charging approach",
    "electricity_price": "Electricity price",
    "weather": "Weather",
    "years_kept": "Years kept",
    "shift_end": "Shift end",
}
# the stable order the diff is reported in (matches the scenario-bar control order).
_CHANGE_ORDER = ("trucks", "charging_approach", "electricity_price", "weather", "years_kept", "shift_end")


def changed_from_previous(
    current: Mapping[str, Any],
    previous_entry: Optional[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    # a plain-word diff of this run's settings_summary vs the PREVIOUS run entry's settings_summary.
    # empty list for the first run (no previous). each change is {field, from, to} in client-facing
    # words so the audit trail reads like a sentence a client understands.
    if not isinstance(previous_entry, Mapping):
        return []
    prev = previous_entry.get("settings_summary")
    prev = prev if isinstance(prev, Mapping) else {}
    changes: List[Dict[str, Any]] = []
    for key in _CHANGE_ORDER:
        old = prev.get(key)
        new = current.get(key)
        if old != new:
            changes.append({"field": _CHANGE_LABEL[key], "from": old, "to": new})
    return changes


def build_run_entry(
    run_id: Any,
    results: Mapping[str, Any],
    previous_entry: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    # build ONE §3.4 run-log entry from a §3.3 results dict. `run_id` is the numeric run number the
    # store allocated. `previous_entry` is the store's latest run entry (or None for the first run),
    # used to compute the plain-word changed_from_previous diff. timestamp is taken from the results
    # (demo_engine emits a deterministic ISO timestamp) so repeated identical runs stay deterministic.
    current_settings = settings_summary(results)
    return {
        "run_id": run_id,
        "timestamp": results.get("timestamp"),
        "settings_summary": current_settings,
        "changed_from_previous": changed_from_previous(current_settings, previous_entry),
        "key_result_summary": key_result_summary(results),
        "mode": results.get("mode", "demo"),
        "engine_version": ENGINE_VERSION_DEMO,
    }


# ---------------------------------------------------------------------------
# thin persistence helpers delegating to the project store.
# ---------------------------------------------------------------------------
def append_entry(entry: Mapping[str, Any]) -> None:
    # append a built §3.4 entry to the project store's append-only run log.
    project_store.get_store().append_run(entry)


def list_entries() -> List[Dict[str, Any]]:
    # the run log NEWEST-FIRST (the store reverses the on-disk append-only list).
    return project_store.get_store().list_runs()


def latest_entry() -> Optional[Dict[str, Any]]:
    # the most recent run entry (newest) or None, used as the diff baseline for the next run.
    return project_store.get_store().latest_run()
