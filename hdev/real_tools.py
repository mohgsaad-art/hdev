# STATUS: NEW (PR 10, Bob to review). the §4.2 TOOL DISPATCHER for the real-mode assistant (Step 10).
#
# the LLM's ONLY power is to CHOOSE one of the seven §4.2 tools and fill its arguments. it NEVER
# executes anything itself. this module is the server-side executor: it validates every tool call and
# routes it to the existing pure chokepoint, then hands the structured result back to the conversation
# loop (hdev/real_chat.py) to feed into the next model turn. this is the "Python executes and
# validates and feeds the result back" half of §4.2.
#
# the seven tools -> chokepoints:
#   run_scenario(levers)   -> hdev.run_api.build_run_payload(mode, {levers})          (validate_lever each)
#   compare_runs(run_ids)  -> hdev.scenarios_api.build_scenarios_payload(mode,'compare',{run_ids})
#   save_scenario(name)    -> hdev.scenarios_api.build_scenarios_payload(mode,'save',{name,results})
#   build_report(format)   -> hdev.report_api.build_report_response(mode, format, {results})
#   set_inputs(patch)      -> src.validate.validate_patch(patch) then persist via project_store
#   ask_missing(fields)    -> derive the missing-classified fields from hdev.intake_api / the registry
#   apply_standard(fields) -> mark those fields standard_approved (registry/intake mechanism)
#
# server-side validation (the HARD line): an unknown tool name never reaches here (ai.parse_tool_reply
# rejects it against ALLOWED_TOOL_NAMES before the loop); a bad lever is rejected via validate_lever; a
# bad patch via validate_patch; an unknown field name is rejected against the registry. a tool whose
# args fail validation returns an {ok: False, error: <plain msg>} result the loop feeds back so the
# model can recover - it is NEVER executed with bad args.
#
# §8: every tool result handed back is already client-safe (the chokepoints enforce §8) and no result
# leaks maps_to / collapsed / hidden names. the dispatcher adds no numbers of its own.
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ai import ALLOWED_TOOL_NAMES


def _err(message: str) -> Dict[str, Any]:
    # a uniform plain-language failure result fed back to the model (never raises; the loop keeps going
    # so the model can pick a different tool / fix its args).
    return {"ok": False, "error": message}


def _ok(payload: Mapping[str, Any]) -> Dict[str, Any]:
    out = {"ok": True}
    out.update(dict(payload))
    return out


# ---------------------------------------------------------------------------
# individual tool handlers. each takes (mode, arguments, store) and returns a plain result dict.
# ---------------------------------------------------------------------------
def _tool_run_scenario(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # run_scenario(levers): validate every submitted lever server-side, then run through the SAME
    # chokepoint as /api/run. the model only names the levers; Python validates + runs.
    from src.validate import validate_lever
    from hdev.run_api import build_run_payload

    levers = args.get("levers")
    if not isinstance(levers, Mapping) or not levers:
        return _err("run_scenario needs a 'levers' object.")

    project = args.get("project") if isinstance(args.get("project"), Mapping) else {}
    for key, value in levers.items():
        result = validate_lever(key, value, project)
        if not result:
            # a bad lever is rejected with the validator's plain-language message (§8 safe).
            return _err(result.error)

    status, payload = build_run_payload(mode, {"levers": dict(levers), "project": dict(project)})
    if status != 200:
        return _err(payload.get("error", "That scenario could not be run."))
    return _ok({"results": payload})


def _tool_compare_runs(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # compare_runs(run_ids): line up saved scenarios by their run ids (or names) via the scenarios
    # chokepoint's 'compare' operation.
    from hdev.scenarios_api import build_scenarios_payload

    body: Dict[str, Any] = {}
    if isinstance(args.get("run_ids"), list):
        body["run_ids"] = args["run_ids"]
    if isinstance(args.get("names"), list):
        body["names"] = args["names"]
    status, payload = build_scenarios_payload(mode, "compare", body)
    if status != 200:
        return _err(payload.get("error", payload.get("reason", "The comparison could not be built.")))
    return _ok({"comparison": payload})


def _tool_save_scenario(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # save_scenario(name): persist the current results under a name via the scenarios 'save' operation.
    from hdev.scenarios_api import build_scenarios_payload

    name = args.get("name")
    if not isinstance(name, str) or not name.strip():
        return _err("save_scenario needs a non-empty 'name'.")
    body: Dict[str, Any] = {"name": name.strip()}
    if isinstance(args.get("results"), Mapping):
        body["results"] = args["results"]
    status, payload = build_scenarios_payload(mode, "save", body)
    if status != 200:
        return _err(payload.get("error", payload.get("reason", "The scenario could not be saved.")))
    return _ok({"saved": payload})


def _tool_build_report(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # build_report(format): render the report in the requested format via the report chokepoint. the
    # raw bytes are NOT fed back to the model (they are not text it should rephrase); the result just
    # confirms the format + size so the model can tell Bob the report is ready.
    from hdev.report_api import build_report_response

    fmt = args.get("format")
    body: Dict[str, Any] = {}
    if isinstance(args.get("results"), Mapping):
        body["results"] = args["results"]
    status, data, media_type, filename = build_report_response(mode, fmt, body)
    if status != 200 or data is None:
        return _err("Unknown report format. Use 'pdf' or 'excel'.")
    return _ok({"report": {"format": fmt, "filename": filename, "media_type": media_type, "bytes": len(data)}})


def _tool_set_inputs(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # set_inputs(patch): validate the patch server-side (field exists, lock flag, physical sanity) via
    # src.validate.validate_patch, then persist a minimal snapshot through the project store. the model
    # only proposes the patch; Python validates + writes.
    from src.validate import validate_patch

    patch = args.get("patch")
    if not isinstance(patch, Mapping) or not patch:
        return _err("set_inputs needs a 'patch' object with a 'field' and a 'value'.")

    result = validate_patch(patch)
    if not result:
        # a bad patch (unknown field, locked slot, out-of-range) is rejected with the plain message.
        return _err(result.error)

    # persist a minimal snapshot keyed by field id. the store keeps inputs small in demo; this is the
    # single documented write path for an assistant-driven input change.
    field_id = patch.get("field")
    value = patch.get("value")
    if store is not None:
        current = {}
        try:
            current = dict(store.load().get("inputs") or {})
        except Exception:
            current = {}
        current[field_id] = value
        store.set_inputs(current)
    return _ok({"updated": {"field": field_id}})


def _tool_ask_missing(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # ask_missing(fields): derive the MISSING-classified fields from the intake chokepoint (demo) or
    # the registry, so the assistant can ask Bob for exactly what is still needed. only OPEN fields are
    # named (§8); collapsed/hidden fields are never surfaced. a 'fields' hint narrows the list to those
    # ids, but the server is the source of truth for which are actually missing.
    missing = _missing_open_fields(mode)
    wanted = args.get("fields")
    if isinstance(wanted, list) and wanted:
        wanted_set = {str(w) for w in wanted}
        missing = [m for m in missing if m["id"] in wanted_set]
    return _ok({"missing_fields": missing})


def _tool_apply_standard(mode: str, args: Mapping[str, Any], store) -> Dict[str, Any]:
    # apply_standard(fields): mark the named fields as standard_approved. the fields must be real OPEN
    # registry fields; an unknown field id is rejected. in this build the approval is recorded in the
    # project store's inputs snapshot (source marker), the single server-side write path - the real
    # defaults table is the locked M1.1 item, so the VALUE stays a standard stand-in.
    from src.registry import get_field

    fields = args.get("fields")
    if not isinstance(fields, list) or not fields:
        return _err("apply_standard needs a non-empty 'fields' list.")

    approved: List[str] = []
    for fid in fields:
        field = get_field(str(fid))
        if field is None:
            return _err("One of the fields is not one the tool recognises.")
        if getattr(field, "visibility", None) != "open":
            # §8: only open fields may be named/acted on by the assistant.
            return _err("One of the fields cannot be set here.")
        approved.append(field.id)

    if store is not None:
        current = {}
        try:
            current = dict(store.load().get("inputs") or {})
        except Exception:
            current = {}
        for fid in approved:
            # record the approval marker; the stand-in value itself is the locked M1.1 defaults item.
            current[fid] = {"source": "standard_approved"}
        store.set_inputs(current)
    return _ok({"standard_approved": approved})


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _missing_open_fields(mode: str) -> List[Dict[str, Any]]:
    # the OPEN fields classified 'missing' by the demo intake payload (id + label only, §8 safe). in
    # real mode there is no fixture, so fall back to the registry's open fields (all treated as needing
    # a value until a real intake lands). never names a collapsed/hidden field.
    out: List[Dict[str, Any]] = []
    if mode == "demo":
        try:
            from hdev.intake_api import build_intake_payload

            payload = build_intake_payload("demo")
            for section in payload.get("sections", []):
                for field in section.get("fields", []):
                    if field.get("class") == "missing":
                        out.append({"id": field.get("id"), "label": field.get("label")})
            return out
        except Exception:
            pass
    # real-mode fallback (or if the demo fixture is unavailable): list open registry fields.
    try:
        from src.registry import FIELDS

        for field in FIELDS:
            if getattr(field, "visibility", None) == "open":
                out.append({"id": field.id, "label": field.label})
    except Exception:
        pass
    return out


_DISPATCH = {
    "run_scenario": _tool_run_scenario,
    "compare_runs": _tool_compare_runs,
    "save_scenario": _tool_save_scenario,
    "build_report": _tool_build_report,
    "set_inputs": _tool_set_inputs,
    "ask_missing": _tool_ask_missing,
    "apply_standard": _tool_apply_standard,
}


def tool_names() -> Tuple[str, ...]:
    # the authoritative seven §4.2 tool names the loop offers the model. kept identical to
    # ai.ALLOWED_TOOL_NAMES so the parser's allow-list and the dispatcher's table never drift.
    return tuple(ALLOWED_TOOL_NAMES)


def dispatch_tool(name: str, arguments: Mapping[str, Any], mode: str, store=None) -> Dict[str, Any]:
    # execute ONE validated tool call and return a plain result dict. an unknown tool name is rejected
    # here too (defence in depth - the parser already rejects it against the allow-list), so a tool the
    # server did not wire can never run.
    handler = _DISPATCH.get(name)
    if handler is None:
        return _err("The requested tool is not available.")
    arguments = arguments if isinstance(arguments, Mapping) else {}
    return handler(mode, arguments, store)
