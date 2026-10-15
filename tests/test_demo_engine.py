# STATUS: NEW (PR 4, Bob to review). offline, pure tests for demo/demo_engine.run_scenario (Step 4).
# no TestClient, no socket, no network - run_scenario is a pure function of (project, levers).
#
# what these assert:
#   - SHAPE: all §3.3 top-level + nested keys; illustrative True / mode "demo"; array lengths
#     (monthly 12, load/flex 24, soc 49 pairs of length 2, tco.categories 6 in the exact order,
#     per_vehicle == fleet_size).
#   - §8 LEAK GUARD: the internal priority keys cost/grid/early never appear as priority values;
#     settings.charging_priority and every strategies[].priority are client-facing names; no technical
#     strategy name (ASAP/JIT/EDF/ES/cost-based) appears in verdict/plan/headline text.
#   - DIRECTION-OF-CHANGE: one test per lever, moving results in the same direction as the mock-up.
import json

import pytest

from demo.demo_engine import run_scenario

# client-facing priority names only (the internal cost/grid/early keys must never leak).
CLIENT_PRIORITIES = {"lowest_cost", "grid_friendly", "ready_earliest"}
# technical strategy names that must never appear in any client-facing string (§8).
FORBIDDEN_TECH_NAMES = ("ASAP", "JIT", "EDF", "ES", "cost-based")

TCO_ORDER = ["Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate"]


def _base_levers(**overrides):
    levers = {
        "fleet_size": 6,
        "charging_priority": "lowest_cost",
        "electricity_price": "expected",
        "weather_year": "normal",
        "ownership_years": 10,
    }
    levers.update(overrides)
    return levers


def _run(**overrides):
    return run_scenario({}, _base_levers(**overrides))


# ---------------------------------------------------------------------------
# shape
# ---------------------------------------------------------------------------
def test_top_level_keys_present():
    r = _run()
    for key in (
        "run_id", "timestamp", "mode", "illustrative", "settings", "verdict", "kpis",
        "energy", "charging", "grid", "tco", "co2", "plan", "inputs_summary",
    ):
        assert key in r, key


def test_mode_and_illustrative_flags():
    r = _run()
    assert r["mode"] == "demo"
    assert r["illustrative"] is True


def test_nested_keys_present():
    r = _run()
    assert set(r["energy"]) >= {"monthly_avg_kwh", "avg_day_kwh", "hardest_day_kwh", "per_vehicle"}
    assert set(r["charging"]) >= {"soc_profile", "strategies"}
    assert set(r["grid"]) >= {"load_24h_kw", "limit_kw", "flex_24h_kw", "flex_mwh_per_day"}
    assert set(r["tco"]) >= {"years", "categories", "cumulative"}
    assert set(r["co2"]) >= {"diesel_t_per_year", "electric_t_per_year", "cumulative_saved_t"}
    assert set(r["kpis"]) >= {
        "battery_kwh", "charger_kw", "charger_count", "ready_by", "grid_peak_kw",
        "grid_limit_kw", "grid_fits", "tco_diff_dkk", "break_even_year", "co2_saved_t_per_year",
    }
    assert set(r["verdict"]) >= {"can_electrify", "headline", "reason"}


def test_array_lengths():
    r = _run()
    assert len(r["energy"]["monthly_avg_kwh"]) == 12
    assert len(r["grid"]["load_24h_kw"]) == 24
    assert len(r["grid"]["flex_24h_kw"]) == 24
    # soc profile: 0..24 inclusive in 0.5 steps -> 49 points, each a [hour, pct] pair.
    assert len(r["charging"]["soc_profile"]) == 49
    for pair in r["charging"]["soc_profile"]:
        assert len(pair) == 2


def test_tco_categories_order_and_count():
    r = _run()
    cats = r["tco"]["categories"]
    assert len(cats) == 6
    assert [c["name"] for c in cats] == TCO_ORDER
    for c in cats:
        assert set(c) >= {"name", "diesel", "electric"}


def test_per_vehicle_matches_fleet_size():
    r = _run(fleet_size=9)
    assert len(r["energy"]["per_vehicle"]) == 9
    for v in r["energy"]["per_vehicle"]:
        assert set(v) >= {"id", "avg", "hardest"}


def test_per_vehicle_cycles_factor_list_beyond_twelve():
    # the per-truck factor list is 12 long; it cycles for a fleet larger than 12 (documented choice).
    r = _run(fleet_size=15)
    assert len(r["energy"]["per_vehicle"]) == 15
    assert r["energy"]["per_vehicle"][-1]["id"] == "T15"


def test_cumulative_length_is_years_plus_one():
    r = _run(ownership_years=10)
    assert len(r["tco"]["cumulative"]["diesel"]) == 11
    assert len(r["tco"]["cumulative"]["electric"]) == 11
    assert len(r["co2"]["cumulative_saved_t"]) == 11


def test_working_days_and_truck_days_simulated_present():
    # additive §3.3 fields (FEAT-002): working_days is the illustrative 250 the maths already uses, and
    # truck_days_simulated == fleet_size * working_days. check at least two fleet sizes.
    for fleet in (3, 6, 12):
        r = _run(fleet_size=fleet)
        assert r["working_days"] == 250
        assert r["truck_days_simulated"] == fleet * r["working_days"]
        assert r["truck_days_simulated"] == fleet * 250


def test_inputs_summary_is_registry_derived():
    # inputs_summary must equal the intake tallies (not a literal). import the same source.
    from hdev.intake_api import build_intake_payload

    totals = build_intake_payload("demo")["totals"]
    r = _run()
    assert r["inputs_summary"] == {
        "from_data": totals["from_data"],
        "standard": totals["standard"],
        "missing": totals["missing"],
        "total": totals["total"],
    }


def test_deterministic():
    # pure/deterministic: same inputs -> identical output (including run_id and timestamp).
    assert _run() == _run()


# ---------------------------------------------------------------------------
# §8 leak guard
# ---------------------------------------------------------------------------
def test_settings_priority_is_client_facing():
    for prio in CLIENT_PRIORITIES:
        r = _run(charging_priority=prio)
        assert r["settings"]["charging_priority"] == prio


def test_strategy_priorities_are_client_facing():
    r = _run()
    prios = [s["priority"] for s in r["charging"]["strategies"]]
    assert set(prios) == CLIENT_PRIORITIES
    for p in prios:
        assert p in CLIENT_PRIORITIES


def test_internal_priority_keys_never_leak_as_values():
    # serialize the whole results JSON and assert the internal keys never appear as a priority value.
    r = _run()
    for s in r["charging"]["strategies"]:
        assert s["priority"] not in ("cost", "grid", "early")
    assert r["settings"]["charging_priority"] not in ("cost", "grid", "early")


def test_no_technical_strategy_name_in_client_strings():
    # verdict/plan/headline text uses PLAIN words only - no technical strategy name.
    r = _run()
    client_strings = [
        r["verdict"]["headline"],
        r["verdict"]["reason"],
    ] + [p["text"] for p in r["plan"]] + [p["when"] for p in r["plan"]]
    blob = " ".join(client_strings)
    for name in FORBIDDEN_TECH_NAMES:
        # match as a whole token to avoid false hits inside ordinary words.
        tokens = blob.replace(".", " ").replace(",", " ").split()
        assert name not in tokens, name


# ---------------------------------------------------------------------------
# direction-of-change, one test per lever
# ---------------------------------------------------------------------------
def test_electricity_price_up_raises_running_electric_and_tco_diff():
    low = _run(electricity_price="low")
    high = _run(electricity_price="high")
    low_running = low["tco"]["categories"][1]["electric"]   # Running is index 1
    high_running = high["tco"]["categories"][1]["electric"]
    assert high_running > low_running
    # a higher electric total pushes the electric-minus-diesel difference up too.
    assert high["kpis"]["tco_diff_dkk"] > low["kpis"]["tco_diff_dkk"]
    # the final electric cumulative point also rises.
    assert high["tco"]["cumulative"]["electric"][-1] > low["tco"]["cumulative"]["electric"][-1]


def test_cold_winter_raises_hardest_day_battery_and_a_month():
    normal = _run(weather_year="normal")
    cold = _run(weather_year="cold_winter")
    assert cold["energy"]["hardest_day_kwh"] > normal["energy"]["hardest_day_kwh"]
    assert cold["kpis"]["battery_kwh"] >= normal["kpis"]["battery_kwh"]
    # at least one monthly value is higher (the winter months are raised).
    assert any(c > n for c, n in zip(cold["energy"]["monthly_avg_kwh"], normal["energy"]["monthly_avg_kwh"]))


def test_more_fleet_raises_grid_peak():
    small = _run(fleet_size=3)
    big = _run(fleet_size=12)
    assert big["kpis"]["grid_peak_kw"] > small["kpis"]["grid_peak_kw"]


def test_priority_changes_charger_peak_and_ready_by():
    cost = _run(charging_priority="lowest_cost")
    early = _run(charging_priority="ready_earliest")
    # a different approach yields a different charger size and/or site peak, and a different ready time.
    assert (cost["kpis"]["charger_kw"] != early["kpis"]["charger_kw"]) or (
        cost["kpis"]["grid_peak_kw"] != early["kpis"]["grid_peak_kw"]
    )
    assert cost["kpis"]["ready_by"] != early["kpis"]["ready_by"]


def test_longer_ownership_scales_totals():
    short = _run(ownership_years=8)
    long = _run(ownership_years=12)
    # Running is a Y-scaled total, so it grows with more years.
    assert long["tco"]["categories"][1]["electric"] > short["tco"]["categories"][1]["electric"]
    assert long["tco"]["categories"][1]["diesel"] > short["tco"]["categories"][1]["diesel"]
    # the cumulative curves are Y+1 long.
    assert len(long["tco"]["cumulative"]["diesel"]) == 13
    assert len(short["tco"]["cumulative"]["diesel"]) == 9


def test_later_shift_end_shortens_grid_window_and_changes_grid_strategy():
    early_end = _run()                  # default shift end 15
    late_end = run_scenario({"shift_end": "18:00"}, _base_levers())
    # the grid-friendly charging window is (30 - se) - 2 hours; a later shift end shortens it, which
    # forces a different (larger) charger and/or a different site peak for the grid-friendly strategy.
    def grid_strat(r):
        return next(s for s in r["charging"]["strategies"] if s["priority"] == "grid_friendly")

    g_early = grid_strat(early_end)
    g_late = grid_strat(late_end)
    assert (g_late["charger_kw"] != g_early["charger_kw"]) or (g_late["peak_kw"] != g_early["peak_kw"])
