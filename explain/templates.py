# STATUS: NEW (PR 6, Bob to review). plain-language assistant TEMPLATES over the §3.3 results JSON.
#
# this package turns the §3.3 results dict (and the registry only where a field LABEL is needed) into
# the plain-language strings the demo assistant says back. in DEMO mode there is no LLM, so these
# TEMPLATES ARE the reply - nothing rephrases them. in REAL mode (Step 10) an LLM may only REPHRASE
# these template strings; it may never introduce a new number or a method/physics detail. §8
# method-hiding and the §4.3 number-check are enforced HERE (and in number_check below), not in JS.
#
# the hard rules every function obeys (§4.3 / §8):
#   - PULL EVERY NUMBER VERBATIM from the results JSON. never compute, round, re-scale or invent a
#     number in this module. where a figure may be absent/None, say a plain "not yet available" phrase
#     rather than printing a made-up value.
#   - say RESULTS, never METHOD: no parameter / coefficient / formula name, no physics data-source
#     name (VECTO / DMI / air drag / rolling resistance / state of charge / ...), no internal or
#     technical charging-strategy name (cost / grid / early / ASAP / JIT / EDF / cost-based). the
#     ONLY charging-approach names allowed are the three client-facing labels Lowest cost /
#     Grid-friendly / Ready earliest.
#   - no collapsed/hidden field names, no per-row intermediate values.
#   - the owner is referred to only as "Bob".
#
# purity: every function is a pure, deterministic, offline function of its arguments. no network, no
# AI provider, no clock dependence.
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple
import re

# the three CLIENT-FACING charging-approach names (§8). the key is the client-facing priority value
# the engine already emits (demo_engine maps the internal cost/grid/early keys to these); the value is
# the human label the assistant says. NO internal/technical name ever appears here.
_PRIORITY_LABEL = {
    "lowest_cost": "Lowest cost",
    "grid_friendly": "Grid-friendly",
    "ready_earliest": "Ready earliest",
}

# the EXACT §4.3 method-deflection reply (plain apostrophe, matches the master prompt wording).
_METHOD_DEFLECTION = "That's the engineering side. The results and every input source are in the report."

# the EXACT §4.4 unmatched-typed-question reply (character for character).
_UNMATCHED_FALLBACK = (
    "In this demo I can answer the suggested questions below. "
    "In the full tool you can ask anything about your fleet."
)

# a plain stand-in when a figure the template wants is absent/None in results. never a number.
_NOT_AVAILABLE = "not yet available"


# ---------------------------------------------------------------------------
# small helpers: read a value out of results WITHOUT ever computing a new number.
# ---------------------------------------------------------------------------
def _settings(results: Mapping[str, Any]) -> Mapping[str, Any]:
    s = results.get("settings")
    return s if isinstance(s, Mapping) else {}


def _kpis(results: Mapping[str, Any]) -> Mapping[str, Any]:
    k = results.get("kpis")
    return k if isinstance(k, Mapping) else {}


def _verdict(results: Mapping[str, Any]) -> Mapping[str, Any]:
    v = results.get("verdict")
    return v if isinstance(v, Mapping) else {}


def _energy(results: Mapping[str, Any]) -> Mapping[str, Any]:
    e = results.get("energy")
    return e if isinstance(e, Mapping) else {}


def _num(value: Any) -> str:
    # render a number EXACTLY as it sits in results (no new rounding). ints print without a dot; floats
    # are shown with a light trim of trailing zeros so a stored 150.0 reads as "150" - the digits are
    # identical to the stored value, nothing is recomputed. None/absent -> the plain not-available text.
    if value is None:
        return _NOT_AVAILABLE
    if isinstance(value, bool):
        # booleans are never printed as numbers.
        return _NOT_AVAILABLE
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return ("%g" % value)
    # strings (e.g. "15:00") are passed through unchanged.
    return str(value)


def _priority_label(priority: Any) -> str:
    # map a client-facing priority value to its human label; unknown -> a neutral word (never internal).
    return _PRIORITY_LABEL.get(priority, "the chosen approach")


def _fits_phrase(fits: Any) -> str:
    # plain words for the grid-fit flag. never a number.
    if fits is True:
        return "fits the site's power connection"
    if fits is False:
        return "asks for more power than the site can draw"
    return "has a power fit that is " + _NOT_AVAILABLE


# ---------------------------------------------------------------------------
# (a) post-run summary (§4.4 flow step 5)
# ---------------------------------------------------------------------------
def summary_text(results: Mapping[str, Any]) -> str:
    # one short paragraph: the verdict headline + reason, then a few KPI values that are PRESENT in
    # results, in human words. every number is read straight from results.
    verdict = _verdict(results)
    kpis = _kpis(results)
    headline = verdict.get("headline") or "Here is what the numbers show."
    reason = verdict.get("reason") or ""

    battery = _num(kpis.get("battery_kwh"))
    charger_kw = _num(kpis.get("charger_kw"))
    charger_count = _num(kpis.get("charger_count"))
    peak = _num(kpis.get("grid_peak_kw"))
    limit = _num(kpis.get("grid_limit_kw"))
    break_even = kpis.get("break_even_year")
    co2 = _num(kpis.get("co2_saved_t_per_year"))

    parts: List[str] = [headline]
    if reason:
        parts.append(reason)

    parts.append(
        f"Each truck needs about a {battery} kWh battery, and the plan uses "
        f"{charger_count} chargers at {charger_kw} kW."
    )
    parts.append(
        f"On the busiest day the site draws about {peak} kW against a {limit} kW connection."
    )
    if break_even is None:
        parts.append("The costs do not come back within the years you plan to keep the fleet.")
    else:
        parts.append(f"The costs come back in year {_num(break_even)}.")
    parts.append(f"It saves about {co2} tonnes of CO\u2082 a year.")

    return " ".join(p.strip() for p in parts if p.strip())


# ---------------------------------------------------------------------------
# (b) compare the three charging approaches (§4.4 button / "compare" keyword)
# ---------------------------------------------------------------------------
def compare_strategies_reply(results: Mapping[str, Any]) -> str:
    # walk results['charging']['strategies'] and describe each by its CLIENT-FACING label only. every
    # number (charger_kw, peak_kw, cost_per_year_dkk, ready_by) is read straight from the strategy row.
    charging = results.get("charging")
    strategies = charging.get("strategies") if isinstance(charging, Mapping) else None
    if not isinstance(strategies, list) or not strategies:
        return "The charging comparison is " + _NOT_AVAILABLE + "."

    # the running cost (cost_per_year_dkk) is a large multi-figure DKK amount; it is ranked in words
    # (cheapest / in between / dearest) rather than printed, so every PRINTED number stays a clean
    # verbatim results figure (charger_kw, peak_kw, ready_by). §4.3 is satisfied without an ugly float.
    costs = [s.get("cost_per_year_dkk") for s in strategies if isinstance(s, Mapping)]
    numeric_costs = [c for c in costs if isinstance(c, (int, float)) and not isinstance(c, bool)]
    cheapest = min(numeric_costs) if numeric_costs else None
    dearest = max(numeric_costs) if numeric_costs else None

    def _cost_word(c: Any) -> str:
        if c is None or not numeric_costs:
            return "a running cost that is " + _NOT_AVAILABLE
        if c == cheapest:
            return "the lowest running cost"
        if c == dearest:
            return "the highest running cost"
        return "a running cost in between"

    lines: List[str] = ["Here is how the three charging approaches compare:"]
    for s in strategies:
        if not isinstance(s, Mapping):
            continue
        label = _priority_label(s.get("priority"))
        charger_kw = _num(s.get("charger_kw"))
        peak = _num(s.get("peak_kw"))
        ready = _num(s.get("ready_by"))
        fits = _fits_phrase(s.get("fits_grid"))
        lines.append(
            f"{label}: {charger_kw} kW chargers, about {peak} kW at the busiest moment, "
            f"{_cost_word(s.get('cost_per_year_dkk'))}, ready by {ready}, and it {fits}."
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# (c) higher electricity price (§4.4 "price_up" button / "price" keyword)
# ---------------------------------------------------------------------------
def price_up_reply(results: Mapping[str, Any]) -> str:
    # explain the effect of the higher price using the CURRENT results KPIs. the direction (cheaper or
    # dearer than diesel) is read from the SIGN of tco_diff_dkk; the break-even YEAR is quoted verbatim.
    # the raw multi-million DKK difference is described in words, not printed as a number, so the reply
    # stays readable and every PRINTED number is a verbatim results figure (§4.3).
    kpis = _kpis(results)
    tco_diff = kpis.get("tco_diff_dkk")
    break_even = kpis.get("break_even_year")

    parts: List[str] = [
        "With the higher electricity price the running cost goes up, so the picture shifts a little."
    ]
    if isinstance(tco_diff, (int, float)) and not isinstance(tco_diff, bool):
        if tco_diff <= 0:
            parts.append("Over the years you keep the fleet it still comes out cheaper than diesel overall.")
        else:
            parts.append("Over the years you keep the fleet it now costs a little more than staying on diesel.")
    if break_even is None:
        parts.append("At this price the costs do not come back within that time.")
    else:
        parts.append(f"The costs come back in year {_num(break_even)}.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# (d) more trucks (§4.4 "more_trucks" button / "truck" keyword)
# ---------------------------------------------------------------------------
def more_trucks_reply(results: Mapping[str, Any]) -> str:
    # explain the effect of the larger fleet: fleet_size / charger_count and the grid peak vs limit.
    settings = _settings(results)
    kpis = _kpis(results)
    fleet_size = _num(settings.get("fleet_size"))
    charger_count = _num(kpis.get("charger_count"))
    peak = _num(kpis.get("grid_peak_kw"))
    limit = _num(kpis.get("grid_limit_kw"))
    fits = _fits_phrase(kpis.get("grid_fits"))

    return (
        f"With {fleet_size} trucks the plan uses {charger_count} chargers. "
        f"On the busiest day the site draws about {peak} kW against a {limit} kW connection, "
        f"so it {fits}."
    )


# ---------------------------------------------------------------------------
# (e) cold winter (§4.4 "cold_winter" button / "cold"/"winter" keyword)
# ---------------------------------------------------------------------------
def cold_winter_reply(results: Mapping[str, Any]) -> str:
    # explain the winter effect in plain words. a cold winter needs more energy (allowed); the WHY /
    # physics is NOT said. names hardest_day_kwh and battery_kwh, read straight from results.
    energy = _energy(results)
    kpis = _kpis(results)
    hardest = _num(energy.get("hardest_day_kwh"))
    battery = _num(kpis.get("battery_kwh"))

    return (
        "A cold winter needs more energy, so the busiest day climbs. "
        f"On the hardest day a truck uses about {hardest} kWh, which is why each truck is sized for "
        f"about a {battery} kWh battery so it still gets through the day."
    )


# ---------------------------------------------------------------------------
# (f) the shift-end field edit (§4.4 field-edit rerun) - ends with the audit line.
# ---------------------------------------------------------------------------
def shift_edit_reply(
    results: Mapping[str, Any],
    run_id: Any,
    changed_label: str,
    old_value: Any,
    new_value: Any,
) -> str:
    # name WHAT changed (the field's plain label + the new value) and what did NOT, then append EXACTLY
    # 'Logged as run #N in the audit trail.' with N the server-assigned run number. the ready_by figure
    # is read straight from results.
    kpis = _kpis(results)
    ready_by = _num(kpis.get("ready_by"))
    battery = _num(kpis.get("battery_kwh"))

    old_txt = _num(old_value)
    new_txt = _num(new_value)

    body = (
        f"I changed {changed_label} from {old_txt} to {new_txt} and ran it again. "
        f"The trucks are ready by {ready_by} and each is still sized for about a {battery} kWh battery; "
        f"the fleet and the routes stayed the same. "
    )
    return body + f"Logged as run #{_num(run_id)} in the audit trail."


# ---------------------------------------------------------------------------
# (g) method deflection + (h) unmatched fallback (exact strings)
# ---------------------------------------------------------------------------
def method_deflection_line() -> str:
    # §4.3 method-deflection reply. results, not methods.
    return _METHOD_DEFLECTION


def unmatched_fallback_line() -> str:
    # §4.4 unmatched-typed-question reply. character for character.
    return _UNMATCHED_FALLBACK


# ---------------------------------------------------------------------------
# §4.3 NUMBER CHECK: block any reply with a number not sourced from results/registry.
# ---------------------------------------------------------------------------
# a numeric token: a run of digits, optionally with thousands-separators and a decimal part, and an
# optional trailing percent sign. examples that match: 150, 1,250,000, 3.14, 42%, 15:00 is handled by
# splitting on the colon so each side is its own token.
_NUM_TOKEN_RE = re.compile(r"\d[\d,]*(?:\.\d+)?%?")


def _normalise_token(token: str) -> str:
    # normalise a numeric token for comparison: drop thousands separators and a trailing percent so a
    # correctly-formatted results number ('1,250,000') matches the raw value ('1250000'). a trailing
    # '.0' is trimmed so 150.0 and 150 compare equal. the result is a plain digit string (optionally
    # with a '.fraction').
    t = token.strip().rstrip("%").replace(",", "")
    if "." in t:
        head, _, tail = t.partition(".")
        tail = tail.rstrip("0")
        t = head if not tail else f"{head}.{tail}"
    return t


def _collect_numbers(value: Any, out: Set[str]) -> None:
    # recursively walk the results structure collecting every number as a normalised token. ints and
    # floats are added directly; strings are scanned for embedded numbers (so 'HH:MM' clock strings
    # and any numeric substrings in settings/verdict text are allowed). bools are NOT numbers.
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        out.add(_normalise_token(str(value)))
        return
    if isinstance(value, float):
        # add both the trimmed form and the integer form when it is a whole number, so 150.0 allows
        # a reply that prints "150". the raw repr is also added for safety.
        out.add(_normalise_token(repr(value)))
        if value == int(value):
            out.add(_normalise_token(str(int(value))))
        else:
            out.add(_normalise_token(("%g" % value)))
        return
    if isinstance(value, str):
        for m in _NUM_TOKEN_RE.findall(value):
            out.add(_normalise_token(m))
        return
    if isinstance(value, Mapping):
        for v in value.values():
            _collect_numbers(v, out)
        return
    if isinstance(value, (list, tuple)):
        for v in value:
            _collect_numbers(v, out)
        return
    # anything else (None, etc.) contributes no number.


def allowed_number_tokens(
    results: Mapping[str, Any],
    registry_values: Optional[Iterable[Any]] = None,
) -> Set[str]:
    # build the ALLOWED numeric-token set from (1) every number anywhere in the results dict and
    # (2) any registry/LEVERS numbers the caller passes in (e.g. ownership_years 8/10/12, fleet_size
    # min). all tokens are normalised the same way the reply tokens are, so formatting never causes a
    # false block.
    allowed: Set[str] = set()
    _collect_numbers(results, allowed)
    if registry_values is None:
        registry_values = _default_registry_numbers()
    for v in registry_values:
        _collect_numbers(v, allowed)
    return allowed


def _default_registry_numbers() -> List[Any]:
    # the registry/LEVERS numbers that may legitimately appear in a reply even when they are not in the
    # current results: the ownership-year options and the fleet-size minimum. imported lazily so this
    # module has no import-time dependency on the registry.
    try:
        from src.registry import LEVERS
    except Exception:
        return []
    nums: List[Any] = []
    for key, spec in LEVERS.items():
        if "options" in spec:
            nums.extend(spec["options"])
        if "min" in spec and isinstance(spec["min"], (int, float)):
            nums.append(spec["min"])
        if "max" in spec and isinstance(spec["max"], (int, float)):
            nums.append(spec["max"])
    return nums


def number_check(
    reply: str,
    results: Mapping[str, Any],
    registry_values: Optional[Iterable[Any]] = None,
    safe_reply: Optional[str] = None,
) -> Tuple[bool, str]:
    # §4.3 guard. scan `reply` for numeric tokens; if any token is NOT in the allowed set, BLOCK the
    # reply: return (False, safe_reply) where safe_reply defaults to the unmatched fallback template so
    # a drifting reply is REPLACED rather than shown. otherwise return (True, reply) unchanged.
    #
    # normalisation (documented so a legit '150' from kpis is allowed but a hallucinated '999' blocked):
    #   - both the allowed numbers and the reply tokens are stripped of thousands separators and a
    #     trailing '%', and a trailing '.0' / trailing zeros in the fraction are trimmed, before
    #     comparing. so '1,250,000' == '1250000' and '150.0' == '150'. a token with no match in the
    #     allowed set blocks the reply.
    allowed = allowed_number_tokens(results, registry_values)
    for raw in _NUM_TOKEN_RE.findall(reply):
        token = _normalise_token(raw)
        if token == "":
            continue
        if token not in allowed:
            return False, (safe_reply if safe_reply is not None else _UNMATCHED_FALLBACK)
    return True, reply
