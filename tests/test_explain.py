# STATUS: NEW (PR 6, Bob to review). offline tests for the explain/ templates + the §4.3 number-check.
# pure functions, no socket, no network, no AI provider.
#
# what these assert:
#   - every template returns a non-empty string whose numbers all appear in the results JSON
#     (number_check returns ok=True for genuine replies).
#   - the number-check BLOCKS a deliberately drifting reply and returns the safe fallback.
#   - §8 GUARD: no technical/strategy/parameter/physics term appears in ANY explain output, and the
#     three client-facing priority labels are the ONLY charging-approach names shown.
import pytest

import explain
from demo.demo_engine import run_scenario

# a spread of scenarios so the §8 guard and the number-check see varied output (different priorities,
# weather, price and shift-end all exercise different branches of the templates).
_SCENARIOS = [
    {},
    {"charging_priority": "grid_friendly"},
    {"charging_priority": "ready_earliest"},
    {"electricity_price": "high"},
    {"weather_year": "cold_winter"},
    {"fleet_size": 10},
    {"operation.schedule.shift_end": "18:00"},
]


def _all_replies(results):
    # every template reply built from one results dict (the two fixed-string helpers + the field edit).
    return [
        explain.summary_text(results),
        explain.compare_strategies_reply(results),
        explain.price_up_reply(results),
        explain.more_trucks_reply(results),
        explain.cold_winter_reply(results),
        explain.shift_edit_reply(results, 7, "Shift end", "15:00", "17:00"),
        explain.method_deflection_line(),
        explain.unmatched_fallback_line(),
    ]


# ---------------------------------------------------------------------------
# (e) every template is non-empty and its numbers all come from results
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("levers", _SCENARIOS)
def test_templates_nonempty_and_numbers_sourced(levers):
    results = run_scenario({}, levers)
    for reply in _all_replies(results):
        assert isinstance(reply, str) and reply.strip(), "template returned an empty string"
        ok, safe = explain.number_check(reply, results)
        assert ok, f"a genuine reply contained an unsourced number:\n{reply}"


def test_shift_edit_reply_ends_with_audit_line():
    results = run_scenario({}, {})
    reply = explain.shift_edit_reply(results, 42, "Shift end", "15:00", "16:00")
    assert reply.rstrip().endswith("Logged as run #42 in the audit trail.")
    assert "Shift end" in reply
    assert "16:00" in reply


def test_exact_fixed_strings():
    assert explain.unmatched_fallback_line() == (
        "In this demo I can answer the suggested questions below. "
        "In the full tool you can ask anything about your fleet."
    )
    assert explain.method_deflection_line() == (
        "That's the engineering side. The results and every input source are in the report."
    )


# ---------------------------------------------------------------------------
# (f) the number-check BLOCKS a drifting reply
# ---------------------------------------------------------------------------
def test_number_check_blocks_hallucinated_number():
    results = run_scenario({}, {})
    genuine = explain.compare_strategies_reply(results)
    drifted = genuine + " Also it needs 424242 kW."
    ok, safe = explain.number_check(drifted, results)
    assert ok is False
    assert safe == explain.unmatched_fallback_line()


def test_number_check_custom_safe_reply():
    results = run_scenario({}, {})
    ok, safe = explain.number_check("A bogus 999999 figure.", results, safe_reply="BLOCKED")
    assert ok is False
    assert safe == "BLOCKED"


def test_number_check_allows_registry_numbers():
    # ownership-year options (8/10/12) and the fleet-size min (1) are registry numbers that may appear
    # even when not in the current results.
    results = run_scenario({}, {})
    ok, _ = explain.number_check("You can keep the fleet for 8, 10 or 12 years.", results)
    assert ok is True


def test_number_check_thousands_separator_not_blocked():
    # a correctly-formatted thousands-separated results number must NOT be falsely blocked.
    results = {"kpis": {"cost": 1250000}}
    ok, _ = explain.number_check("It costs about 1,250,000 DKK.", results, registry_values=[])
    assert ok is True


# ---------------------------------------------------------------------------
# (g) §8 guard over ALL explain output
# ---------------------------------------------------------------------------
_DENYLIST = [
    "cda", "crr", "ocv", "regen", "yaw", "vecto", "dmi",
    "coefficient", "parameter", "formula", "air drag", "rolling resistance",
    "asap", "jit", "edf", "cost-based", "state of charge",
    # the internal priority keys as standalone technical terms.
    "lowest_cost", "grid_friendly", "ready_earliest",
]


@pytest.mark.parametrize("levers", _SCENARIOS)
def test_no_forbidden_term_in_any_reply(levers):
    results = run_scenario({}, levers)
    for reply in _all_replies(results):
        low = reply.lower()
        for term in _DENYLIST:
            assert term not in low, f"§8-forbidden term {term!r} appeared in:\n{reply}"


@pytest.mark.parametrize("levers", _SCENARIOS)
def test_only_client_facing_priority_labels_appear(levers):
    # the three human labels are the ONLY charging-approach names that may appear. no internal key
    # (cost/grid/early) may appear as a standalone charging-approach token.
    results = run_scenario({}, levers)
    reply = explain.compare_strategies_reply(results)
    assert "Lowest cost" in reply
    assert "Grid-friendly" in reply
    assert "Ready earliest" in reply
    # the internal keys must not leak (checked as standalone words to avoid matching inside e.g. "cost").
    import re
    for internal in ("asap", "jit", "edf"):
        assert not re.search(rf"\b{internal}\b", reply.lower())
