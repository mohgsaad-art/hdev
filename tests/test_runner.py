# STATUS: NEW (Step 9, item 15 / M4.1, Bob to review). Tests for runner.run orchestration.
#
# These assert design §4C behaviour: change-set application (recording provided_by, empty = no-op),
# earliest-stage selection, refusal on an incomplete entry contract naming the missing fields, and the
# §3.3-shaped real results with mode='real' and nulls where stages are stubbed/blocked. A §8 guard
# asserts no engine-internal term appears in the real results JSON string.
#
# IMPORT PURITY: importing src.server.runner must not force numpy/gym. This file imports runner at the
# top; the fact the suite collects without numpy proves the module-level import is clean.
import json

import pytest

from src.server import runner


# a minimal "full project" that satisfies the consumption entry contract.
FULL_PROJECT = {
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


def test_apply_change_sets_empty_is_noop():
    out = runner.apply_change_sets(FULL_PROJECT, None)
    # same slots as the base (plus an empty provenance map), deep-copied (not the same object).
    assert out["vehicles"] == FULL_PROJECT["vehicles"]
    assert out is not FULL_PROJECT
    assert out.get("provenance") == {}
    out2 = runner.apply_change_sets(FULL_PROJECT, [])
    assert out2.get("provenance") == {}


def test_apply_change_sets_records_provided_by():
    changes = [{"key": "charger.rated_kW", "slot": 120, "provided_by": "CPO"}]
    out = runner.apply_change_sets(FULL_PROJECT, changes)
    assert out["charger.rated_kW"] == 120
    assert out["provenance"]["charger.rated_kW"]["provided_by"] == "CPO"
    # the base is untouched (deep copy).
    assert "charger.rated_kW" not in FULL_PROJECT


def test_apply_change_sets_accepts_plain_mapping():
    out = runner.apply_change_sets(FULL_PROJECT, {"fleet_size": 8})
    assert out["fleet_size"] == 8
    assert out["provenance"]["fleet_size"]["provided_by"] == "client"


def test_select_start_stage_consumption_for_full_project():
    assert runner.select_start_stage(FULL_PROJECT) == "consumption"


def test_select_start_stage_charging_for_session_list_only():
    # only a session list given -> consumption is not satisfiable, charging is the earliest that is.
    project = {"sessions": [{"arrival": "2026-01-01T18:00", "departure": "2026-01-02T06:00",
                             "energy_need_kWh": 100.0, "arrival_SOC": 0.2}]}
    assert runner.select_start_stage(project) == "charging"


def test_select_start_stage_tco_standalone():
    project = {"annual_energy_kWh": 500000.0, "peak_power_kW": 300.0}
    assert runner.select_start_stage(project) == "tco"


def test_run_refuses_incomplete_contract_naming_missing():
    # a project with none of the stage inputs -> refuse, naming consumption's missing fields.
    with pytest.raises(runner.RefusalError) as ei:
        runner.run({"fleet_size": 6})
    err = ei.value
    assert err.stage == "consumption"
    assert set(err.missing) == {"vehicles", "routes", "calendar_environment"}
    # the message names what is missing, in plain words.
    msg = str(err)
    assert "vehicles" in msg and "routes" in msg and "calendar_environment" in msg


def test_run_returns_real_shape_with_nulls():
    r = runner.run(FULL_PROJECT)
    # §3.3 landmark keys present.
    for key in ("energy", "kpis", "charging", "grid", "tco", "co2", "settings", "verdict", "provenance"):
        assert key in r
    assert r["mode"] == "real"
    assert r["illustrative"] is False
    # stubbed/blocked stages are null.
    assert r["energy"]["avg_day_kwh"] is None
    assert r["energy"]["monthly_avg_kwh"] is None
    assert r["charging"]["soc_profile"] is None
    assert r["grid"]["load_24h_kw"] is None
    assert r["co2"]["diesel_t_per_year"] is None
    assert r["kpis"]["break_even_year"] is None
    assert r["verdict"]["can_electrify"] is None
    # the TCO block still carries the six client-facing category names (data model), with null totals.
    assert [c["name"] for c in r["tco"]["categories"]] == [
        "Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate",
    ]
    for c in r["tco"]["categories"]:
        assert c["diesel"] is None and c["electric"] is None
    # settings echoed back with the client-facing keys.
    assert r["settings"]["fleet_size"] == 6
    assert r["settings"]["charging_priority"] == "lowest_cost"


def test_run_provenance_reports_start_stage():
    r = runner.run(FULL_PROJECT)
    assert r["provenance"]["stages"]["start_stage"] == "consumption"
    assert r["provenance"]["stages"]["simulated"] == ["consumption", "charging", "flexibility", "tco"]


def test_run_change_set_provenance_surfaces():
    r = runner.run(FULL_PROJECT, [{"key": "charger.rated_kW", "slot": 90, "provided_by": "CPO"}])
    assert r["provenance"]["slots"]["charger.rated_kW"]["provided_by"] == "CPO"


def test_section8_no_banned_internal_term_in_real_results():
    # §8 METHOD-HIDING guard: no engine-internal term appears anywhere in the real results JSON string.
    r = runner.run(FULL_PROJECT, [{"key": "charger.rated_kW", "slot": 90, "provided_by": "CPO"}])
    blob = json.dumps(r)
    banned = [
        "ASAP", "JIT", "EDF", "ES-Tech", "cost-based",
        "k_lin", "k_roll", "k_rot", "CdxA", "P_wheel", "P_aux", "VECTO", "rho",
        "eta_drive", "eta_regen", "OCV",
    ]
    for term in banned:
        assert term not in blob, "banned internal term leaked: %r" % term
