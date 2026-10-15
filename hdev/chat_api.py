# STATUS: NEW (PR 6, Bob to review). the pure chokepoint behind POST /api/chat (Step 6, demo assistant).
#
# this is the ONE place that turns an assistant turn (mode + body of {message?/action?/levers?/
# current_results?}) into a reply payload. it mirrors hdev/run_api.py and hdev/intake_api.py: a pure
# function of the RESOLVED mode (demo|real) so it is unit-testable without a socket. §0: all logic
# lives in Python; the browser is a dumb client that POSTs raw text / an action id and renders the
# strings this returns - it does NO maths, NO reply-text generation and NO keyword matching.
#
# behaviour by mode:
#   - real mode (Step 10): delegate to hdev/real_chat.build_real_chat_payload, imported LAZILY inside
#     the real branch so the DEMO path below never imports an AI provider. the DEMO path and all its
#     helpers stay byte-for-byte unchanged and provider-free (the demo tests assert this module imports
#     no provider on the demo path). the real path owns the data guard + the §4.2 tool loop + the
#     §4.3/§8 output guards.
#   - demo mode: scripted, offline. three input shapes, all answered by explain/ templates:
#       (1) SUGGESTION BUTTONS (body.action): the eight §4.4 buttons. four of them change a lever and
#           RERUN through the SAME run path as /api/run (hdev.run_api.build_run_payload) so the reply's
#           numbers come from a fresh §3.3 results dict; four are no-rerun tab actions.
#       (2) TYPED-QUESTION KEYWORD ROUTER (body.message): lower-case substring match, server-side.
#           method/how/why questions deflect; anything unmatched returns the exact fallback line.
#       (3) the SHIFT-END FIELD EDIT (body.action == 'edit_field' on operation.schedule.shift_end):
#           validate the new value, rerun, assign a server-side run number N, reply ends with
#           'Logged as run #N in the audit trail.'.
#
# EVERY reply is passed through the §4.3 number-check (explain.number_check) before returning: a reply
# that contains a number not present in the current results/registry is BLOCKED and replaced by the
# safe fallback template. the UI never sees a drifting number.
#
# the handler returns (status_code, payload) so the thin server route in hdev/server.py only wraps it
# in a JSONResponse - the HTTP mapping stays in one place while the logic stays pure.
from typing import Any, Dict, Mapping, Optional, Tuple

import explain
from src.validate import validate_lever
from .project_store import get_store

# the shift-end edit target: the open + editable_in_demo registry field (an 'HH:MM' value). its plain
# label is read from the registry so the reply never hard-codes a field name.
_SHIFT_END_FIELD = "operation.schedule.shift_end"

# default levers for the base scenario, used when the caller gives no current_results and no levers so
# a reply always has a results source to quote from (documented in build_chat_payload). these match the
# demo_engine defaults / the sample case (a 6-truck municipal refuse fleet).
_DEFAULT_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}

# ---------------------------------------------------------------------------
# RUN COUNTER (Step 7 unification).
# the run number for 'Logged as run #N' is now the PROJECT-SCOPED monotonic counter owned by
# hdev.run_api.build_run_payload: every successful demo run (scenario-bar /api/run, the assistant
# rerun buttons, and the shift-end edit below) allocates exactly one N and appends exactly one §3.4
# run-log entry THERE. this module no longer owns a counter; the shift-edit path simply READS BACK the
# 'run_number' the run returned. this guarantees one monotonic sequence across the whole audit trail
# and no double-counting (the module-level itertools.count that used to live here is gone).
# ---------------------------------------------------------------------------

# the human labels for the tabs the UI opens (ids match the §5.6 workspace tabs the UI already renders).
_TAB_CHARGING = "charging"
_TAB_TCO = "tco"
_TAB_GRIDFLEX = "gridflex"
_TAB_ENERGY = "energy"
_TAB_SCENARIOS = "scenarios"
_TAB_INPUTS = "inputs"
_TAB_AUDIT = "audit"
_TAB_REPORT = "report"


def _rerun(levers: Mapping[str, Any], project: Mapping[str, Any], log_run: bool = True) -> Tuple[int, Dict[str, Any]]:
    # rerun through the SAME chokepoint as /api/run so the assistant and the scenario bar share one
    # path and one validation. returns (status, results-or-error-payload). `log_run` controls the Step
    # 7 run-counter side effect: a genuine rerun (a button / the shift-edit) logs and counts; a
    # quote-only rerun (to read a number for a no-rerun reply) passes log_run=False so it does not.
    from .run_api import build_run_payload

    return build_run_payload("demo", {"levers": dict(levers), "project": dict(project)}, log_run=log_run)


def _base_results(body: Mapping[str, Any]) -> Dict[str, Any]:
    # resolve a results dict to quote from for the NO-RERUN replies. prefer the caller's
    # current_results; else run a default scenario so a reply always has a source (§4.3: numbers must
    # come from a results dict, so one is always produced). this is a QUOTE-ONLY rerun - log_run=False
    # so it never consumes a run number or appends a run-log entry (no-rerun replies are not runs).
    current = body.get("current_results")
    if isinstance(current, Mapping) and current.get("kpis"):
        return dict(current)
    levers = body.get("levers")
    if not isinstance(levers, Mapping):
        levers = _DEFAULT_LEVERS
    project = body.get("project") if isinstance(body.get("project"), Mapping) else {}
    status, payload = _rerun(levers, project, log_run=False)
    return payload if status == 200 else {}


def _current_levers(body: Mapping[str, Any]) -> Dict[str, Any]:
    # the levers to start a rerun from: the caller's levers if given, else those on current_results'
    # settings, else the demo defaults. settings are already client-facing so they drop straight back
    # in as levers.
    levers = body.get("levers")
    if isinstance(levers, Mapping) and levers:
        return dict(levers)
    current = body.get("current_results")
    if isinstance(current, Mapping) and isinstance(current.get("settings"), Mapping):
        s = current["settings"]
        return {
            "fleet_size": s.get("fleet_size"),
            "charging_priority": s.get("charging_priority"),
            "electricity_price": s.get("electricity_price"),
            "weather_year": s.get("weather_year"),
            "ownership_years": s.get("ownership_years"),
            "operation.schedule.shift_end": s.get("shift_end"),
        }
    return dict(_DEFAULT_LEVERS)


def _guard(reply: str, results: Mapping[str, Any]) -> str:
    # apply the §4.3 number-check to EVERY reply before returning. a reply with a number not in the
    # current results/registry is replaced by the safe fallback template.
    ok, safe = explain.number_check(reply, results)
    return reply if ok else safe


# ---------------------------------------------------------------------------
# main chokepoint
# ---------------------------------------------------------------------------
def build_chat_payload(mode: str, body: Optional[Mapping[str, Any]]) -> Tuple[int, Dict[str, Any]]:
    # pure chokepoint. `mode` is already resolved (demo|real). `body` is the parsed JSON request body.
    body = body or {}

    if mode != "demo":
        # REAL MODE (Step 10): delegate to the real-mode conversation loop. the import is LAZY (inside
        # this branch) so the DEMO path below never imports an AI provider - this module stays
        # provider-free on the demo path, which the demo tests assert. the real path resolves the
        # config + provider, runs the data guard BEFORE any outbound call, drives the §4.2 tool loop,
        # and runs the §4.3 number-check + §8 denylist on the model output.
        from .real_chat import build_real_chat_payload

        return build_real_chat_payload(body)

    action = body.get("action")
    message = body.get("message")

    if isinstance(action, str) and action:
        return _handle_action(action, body)
    if isinstance(message, str):
        return _handle_message(message, body)

    # neither an action nor a message: nothing to answer. return the fallback line (no action).
    results = _base_results(body)
    return 200, {"reply": _guard(explain.unmatched_fallback_line(), results)}


# ---------------------------------------------------------------------------
# (1) suggestion-button actions + (3) the shift-end field edit
# ---------------------------------------------------------------------------
def _handle_action(action: str, body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # the four RERUN buttons: change one lever and rerun through the /api/run path, then quote the
    # fresh results.
    if action in ("price_up", "more_trucks", "cold_winter"):
        return _rerun_button(action, body)
    if action == "compare_strategies":
        return _compare_button(body)
    if action in ("save_scenario", "show_inputs", "show_audit", "make_report"):
        return _tab_button(action, body)
    if action == "edit_field":
        return _edit_field(body)
    # an unknown action id: treat like an unmatched turn.
    results = _base_results(body)
    return 200, {"reply": _guard(explain.unmatched_fallback_line(), results)}


def _rerun_button(action: str, body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # map the button to the lever change + the tab it opens + the reply template.
    levers = _current_levers(body)
    project = body.get("project") if isinstance(body.get("project"), Mapping) else {}

    if action == "price_up":
        levers["electricity_price"] = "high"
        open_tab = _TAB_TCO
        lever_patch = {"electricity_price": "high"}
        template = explain.price_up_reply
    elif action == "more_trucks":
        base_fleet = levers.get("fleet_size")
        if not isinstance(base_fleet, int) or isinstance(base_fleet, bool):
            base_fleet = _DEFAULT_LEVERS["fleet_size"]
        levers["fleet_size"] = base_fleet + 4
        open_tab = _TAB_GRIDFLEX
        lever_patch = {"fleet_size": levers["fleet_size"]}
        template = explain.more_trucks_reply
    else:  # cold_winter
        levers["weather_year"] = "cold_winter"
        open_tab = _TAB_ENERGY
        lever_patch = {"weather_year": "cold_winter"}
        template = explain.cold_winter_reply

    status, results = _rerun(levers, project)
    if status != 200:
        # a rejected lever: surface the plain-language error, no action.
        return status, {"reply": results.get("error", "That change could not be applied."), "ok": False}

    reply = _guard(template(results), results)
    return 200, {
        "reply": reply,
        "action": {"open_tab": open_tab, "lever": lever_patch, "results": results},
    }


def _compare_button(body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # compare the three charging approaches - NO rerun, opens the Charging tab.
    results = _base_results(body)
    reply = _guard(explain.compare_strategies_reply(results), results)
    return 200, {"reply": reply, "action": {"open_tab": _TAB_CHARGING}}


def _tab_button(action: str, body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # the no-rerun tab buttons. each opens a tab and says a short plain line; later steps fill them in.
    results = _base_results(body)
    if action == "save_scenario":
        # persist the CURRENT run as a saved scenario via the scenarios chokepoint (the single owner of
        # the project store write), then open the Scenarios tab. the client refreshes the table off the
        # action.saved_scenario flag. the reply names only the saved scenario (plain words, §4.3/§8-safe
        # - no result number is quoted). the scenario name is a plain UI label, not a result figure.
        from .scenarios_api import build_scenarios_payload

        name = body.get("scenario_name")
        if not isinstance(name, str) or not name.strip():
            store_count = len(get_store().list_scenarios())
            name = "Scenario " + str(store_count + 1)
        build_scenarios_payload("demo", "save", {"name": name, "results": results})
        # the reply names no number (a scenario name like "Scenario 2" would be read as a figure by the
        # §4.3 number-check and blocked); it points the client at the Scenarios tab instead.
        reply = "I have added this to your scenarios list. You can see it on the Scenarios tab."
        act: Dict[str, Any] = {"open_tab": _TAB_SCENARIOS, "saved_scenario": True}
    elif action == "show_inputs":
        reply = "Here are the inputs. I have opened the Operation section for you."
        act = {"open_tab": _TAB_INPUTS, "expand_section": "operation"}
    elif action == "show_audit":
        reply = "Here is the audit trail. The full source list arrives in a later step."
        act = {"open_tab": _TAB_AUDIT}
    else:  # make_report
        reply = "Here is the report. Exporting it to a file lands in a later step."
        act = {"open_tab": _TAB_REPORT}
    return 200, {"reply": _guard(reply, results), "action": act}


def _edit_field(body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    # the §4.4 shift-end field edit. only the open+editable operation.schedule.shift_end is accepted.
    target = body.get("target")
    new_value = body.get("value")
    project = body.get("project") if isinstance(body.get("project"), Mapping) else {}

    if target != _SHIFT_END_FIELD:
        return 400, {"ok": False, "reply": "That field cannot be changed here."}

    # validate the new value through the SAME validator the run path uses (§3.2 open+editable field).
    result = validate_lever(target, new_value, project)
    if not result:
        return 400, {"ok": False, "reply": result.error}

    levers = _current_levers(body)
    old_value = levers.get(target)
    levers[target] = new_value

    status, results = _rerun(levers, project)
    if status != 200:
        return status, {"ok": False, "reply": results.get("error", "That change could not be applied.")}

    # read back the run number the SHARED run path allocated and logged (Step 7). build_run_payload
    # owns allocation + §3.4 run-log append for every demo run, so the shift-edit must NOT allocate its
    # own N - it quotes the one the rerun returned. this keeps a single monotonic sequence and avoids
    # double-counting.
    run_number = results.get("run_number")
    changed_label = _field_label(target)
    reply = explain.shift_edit_reply(results, run_number, changed_label, old_value, new_value)
    reply = _guard(reply, results)

    return 200, {
        "reply": reply,
        "run_id": run_number,
        "action": {
            "open_tab": _TAB_AUDIT,
            "lever": {target: new_value},
            "results": results,
            "run_id": run_number,
        },
    }


def _field_label(field_id: str) -> str:
    # the plain client-facing label for a registry field, used so the reply names the change in human
    # words. imported lazily to keep this module's import graph small.
    try:
        from src.registry import get_field

        field = get_field(field_id)
        if field is not None:
            return field.label
    except Exception:
        pass
    return "the shift end"


# ---------------------------------------------------------------------------
# (2) typed-question keyword router (server-side, deterministic precedence)
# ---------------------------------------------------------------------------
# keyword precedence (first match wins), documented so it is deterministic:
#   1. method/how/why  -> method deflection (checked FIRST so "why is it more expensive" deflects
#                         rather than being read as a price question).
#   2. strategy/compare/charg -> compare the three approaches (open Charging, no rerun).
#   3. price/cost/expens      -> higher price (rerun, open Costs/tco).
#   4. truck/add/more         -> more trucks (rerun, open Grid & flexibility).
#   5. cold/winter/weather    -> cold winter (rerun, open Energy).
#   6. anything else          -> the exact unmatched fallback line, no action.
_METHOD_KEYWORDS = ("how ", "why", "which parameter", "parameter", "formula", "method", "calculat")
_STRATEGY_KEYWORDS = ("strategy", "compare", "charg")
_PRICE_KEYWORDS = ("price", "cost", "expens")
_TRUCK_KEYWORDS = ("truck", "add", "more")
_WINTER_KEYWORDS = ("cold", "winter", "weather")


def _handle_message(message: str, body: Mapping[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = message.lower()

    # 1. method/how/why deflection - checked first.
    if any(kw in text for kw in _METHOD_KEYWORDS):
        results = _base_results(body)
        return 200, {"reply": _guard(explain.method_deflection_line(), results)}

    # 2. strategies (same behaviour as the compare_strategies button).
    if any(kw in text for kw in _STRATEGY_KEYWORDS):
        return _compare_button(body)

    # 3. price (same behaviour as the price_up button).
    if any(kw in text for kw in _PRICE_KEYWORDS):
        return _rerun_button("price_up", body)

    # 4. more trucks.
    if any(kw in text for kw in _TRUCK_KEYWORDS):
        return _rerun_button("more_trucks", body)

    # 5. cold winter.
    if any(kw in text for kw in _WINTER_KEYWORDS):
        return _rerun_button("cold_winter", body)

    # 6. unmatched: the EXACT fallback line, no action.
    results = _base_results(body)
    return 200, {"reply": _guard(explain.unmatched_fallback_line(), results)}
